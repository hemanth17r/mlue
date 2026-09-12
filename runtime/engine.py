"""MLUE Phase 0.6 Core Engine

Deterministic computational engine evaluating spatial geometry, multi-entity composition,
external input signals, linear velocity time-integration (dt), environment boundary constraints,
pairwise relational collisions, collision-based event triggers, entity lifecycle management,
property mutations, and state variable conditions.
Completely decoupled from any rendering or platform display subsystem.
"""

import copy
import math
import re
from typing import List, Tuple, Dict, Any, Optional, Set, FrozenSet, Union
from collections import defaultdict
from .model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    CircleSize,
    BoxSize,
    SegmentSize,
    CapsuleSize,
    TextSize,
    Velocity,
    EvaluationResult,
    ComputedShape,
    ComputedConstraint,
    SimulationState,
    PointerState,
    Rule,
    Condition,
    Action,
    Constraint,
)
from .loader import parse_keypath
from .spatial import (
    SpatialHashGrid2D,
    Ray2D,
    RayHit,
    cast_ray_scene,
    hit_test_scene,
    hit_test_entity,
    get_anchor_origin,
    get_entity_effective_pos,
)

TEMPLATE_PATTERN = re.compile(r"\{([a-zA-Z0-9_\.\[\]]+)\}")

_SMALL_PAIRS = {
    k: tuple((i, j) for i in range(k) for j in range(i + 1, k))
    for k in range(2, 7)
}


def _analytical_point_to_segment(
    px: float, py: float, ax: float, ay: float, bx: float, by: float
) -> Tuple[float, float, float, float, float]:
    """Calculates closest point on segment AB to point P.
    Returns (qx, qy, dist, nx, ny) where (nx, ny) is unit normal pointing from Q to P."""
    vx = bx - ax
    vy = by - ay
    v_len_sq = vx * vx + vy * vy
    if v_len_sq <= 1e-12:
        t = 0.0
    else:
        t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / v_len_sq))
    qx = ax + t * vx
    qy = ay + t * vy
    dx = px - qx
    dy = py - qy
    dist = math.hypot(dx, dy)
    if dist > 1e-12:
        nx = dx / dist
        ny = dy / dist
    else:
        seg_len = math.hypot(vx, vy)
        if seg_len > 1e-12:
            nx = -vy / seg_len
            ny = vx / seg_len
        else:
            nx, ny = 1.0, 0.0
    return qx, qy, dist, nx, ny


def _analytical_segment_to_segment(
    p1x: float, p1y: float, p2x: float, p2y: float,
    q1x: float, q1y: float, q2x: float, q2y: float
) -> Tuple[float, float, float, float, float, float, float]:
    """Calculates closest points between segment P1P2 and segment Q1Q2.
    Returns (c1x, c1y, c2x, c2y, dist, nx, ny) where (nx, ny) points from C2 to C1."""
    ux = p2x - p1x
    uy = p2y - p1y
    vx = q2x - q1x
    vy = q2y - q1y
    wx = p1x - q1x
    wy = p1y - q1y

    a = ux * ux + uy * uy
    b = ux * vx + uy * vy
    c = vx * vx + vy * vy
    d = ux * wx + uy * wy
    e = vx * wx + vy * wy
    denom = a * c - b * b

    if denom <= 1e-12:
        best_dist = float("inf")
        c1x, c1y, c2x, c2y = p1x, p1y, q1x, q1y
        t1 = max(0.0, min(1.0, e / c)) if c > 1e-12 else 0.0
        qx1, qy1 = q1x + t1 * vx, q1y + t1 * vy
        d1 = math.hypot(p1x - qx1, p1y - qy1)
        if d1 < best_dist:
            best_dist, c1x, c1y, c2x, c2y = d1, p1x, p1y, qx1, qy1
        e2 = vx * (p2x - q1x) + vy * (p2y - q1y)
        t2 = max(0.0, min(1.0, e2 / c)) if c > 1e-12 else 0.0
        qx2, qy2 = q1x + t2 * vx, q1y + t2 * vy
        d2 = math.hypot(p2x - qx2, p2y - qy2)
        if d2 < best_dist:
            best_dist, c1x, c1y, c2x, c2y = d2, p2x, p2y, qx2, qy2
        s3 = max(0.0, min(1.0, -d / a)) if a > 1e-12 else 0.0
        px3, py3 = p1x + s3 * ux, p1y + s3 * uy
        d3 = math.hypot(px3 - q1x, py3 - q1y)
        if d3 < best_dist:
            best_dist, c1x, c1y, c2x, c2y = d3, px3, py3, q1x, q1y
        d4_val = ux * (q2x - p1x) + uy * (q2y - p1y)
        s4 = max(0.0, min(1.0, d4_val / a)) if a > 1e-12 else 0.0
        px4, py4 = p1x + s4 * ux, p1y + s4 * uy
        d4 = math.hypot(px4 - q2x, py4 - q2y)
        if d4 < best_dist:
            best_dist, c1x, c1y, c2x, c2y = d4, px4, py4, q2x, q2y
    else:
        s = max(0.0, min(1.0, (b * e - c * d) / denom))
        t = max(0.0, min(1.0, (b * s + e) / c)) if c > 1e-12 else 0.0
        if a > 1e-12:
            s = max(0.0, min(1.0, (b * t - d) / a))
        c1x = p1x + s * ux
        c1y = p1y + s * uy
        c2x = q1x + t * vx
        c2y = q1y + t * vy

    dx = c1x - c2x
    dy = c1y - c2y
    dist = math.hypot(dx, dy)
    if dist > 1e-12:
        nx = dx / dist
        ny = dy / dist
    else:
        nx, ny = 1.0, 0.0

    return c1x, c1y, c2x, c2y, dist, nx, ny


class MLUEEngine:
    """Deterministic computational engine for evaluating MLUE representations and simulations."""

    def _interpolate_template(
        self, template: Optional[str], state_vars: Optional[Dict[str, Any]]
    ) -> str:
        """Interpolates state variables into template string without regex recompilation."""
        if not template:
            return ""
        if "{" not in template or not state_vars:
            return template

        def repl(match):
            path = match.group(1).strip()
            val = self._get_path_value(state_vars, path)
            return str(val) if val is not None else ""

        return TEMPLATE_PATTERN.sub(repl, template)

    def _get_stack_dimension(self, child: Entity, is_vertical: bool) -> float:
        """Calculates child dimension along stacking axis."""
        if child.type == "box" and isinstance(child.size, BoxSize):
            return child.size.height if is_vertical else child.size.width
        if child.type == "capsule" and isinstance(child.size, CapsuleSize):
            return (child.size.radius * 2.0) if is_vertical else (child.size.length + child.size.radius * 2.0)
        if child.type == "circle" and isinstance(child.size, CircleSize):
            return child.size.radius * 2.0
        if child.type == "segment" and isinstance(child.size, SegmentSize):
            return child.size.thickness if is_vertical else abs(child.size.end_x - child.position.x)
        if child.type == "text" and isinstance(child.size, TextSize):
            return child.size.font_scale * 1.5 if is_vertical else 0.5
        return 0.05 if is_vertical else 0.1

    def _calculate_auto_stacking(
        self,
        entities: List[Entity],
        children_by_parent: Dict[str, List[Entity]],
        env: Optional[Environment] = None,
    ) -> Dict[str, Tuple[float, float]]:
        """Calculates normalized child positions for containers with auto-stacking layout."""
        stacked_offsets: Dict[str, Tuple[float, float]] = {}
        for container in entities:
            if not container.layout or container.id not in children_by_parent:
                continue
            layout = container.layout
            direction = layout.get("direction", "vertical")
            gap = float(layout.get("gap", 0.01))
            padding = float(layout.get("padding", 0.0))
            align_items = layout.get("align_items")
            if direction == "auto":
                if env is not None:
                    cw = container.size.width * env.width if isinstance(container.size, BoxSize) else float(env.width)
                    ch = container.size.height * env.height if isinstance(container.size, BoxSize) else float(env.height)
                    is_vertical = cw < ch
                elif isinstance(container.size, BoxSize):
                    is_vertical = container.size.width < container.size.height
                else:
                    is_vertical = True
            else:
                is_vertical = direction in ("vertical", "stack_y")
            cursor = padding if padding > 0.0 else gap
            children = children_by_parent[container.id]

            for child in children:
                dim = self._get_stack_dimension(child, is_vertical)
                if is_vertical:
                    rel_y = cursor + dim / 2.0
                    if align_items == "start":
                        rel_x = padding if padding > 0.0 else 0.05
                    elif align_items == "center":
                        rel_x = 0.5
                    elif align_items == "end":
                        rel_x = 1.0 - (padding if padding > 0.0 else 0.05)
                    else:
                        rel_x = child.position.x if child.position.x != 0.0 else (padding if padding > 0.0 else 0.5)
                    stacked_offsets[child.id] = (rel_x, rel_y)
                else:
                    rel_x = cursor + dim / 2.0
                    if align_items == "start":
                        rel_y = padding if padding > 0.0 else 0.05
                    elif align_items == "center":
                        rel_y = 0.5
                    elif align_items == "end":
                        rel_y = 1.0 - (padding if padding > 0.0 else 0.05)
                    else:
                        rel_y = child.position.y if child.position.y != 0.0 else (padding if padding > 0.0 else 0.5)
                    stacked_offsets[child.id] = (rel_x, rel_y)
                cursor += dim + gap

        return stacked_offsets

    def _compute_entity_geometry(
        self,
        entity: Entity,
        pw: float,
        ph: float,
        p_min: float,
        cx: float,
        cy: float,
        px0: float,
        py0: float,
        state_vars: Optional[Dict[str, Any]],
        is_stacked: bool = False,
    ) -> Tuple[Tuple[float, float, float, float], Optional[str]]:
        """Computes concrete bounding box and text content for a single entity."""
        etype = entity.type
        if etype == "circle" and isinstance(entity.size, CircleSize):
            r = entity.size.radius * p_min
            return (cx - r, cy - r, cx + r, cy + r), None
        if etype == "box" and isinstance(entity.size, BoxSize):
            hw = (entity.size.width / 2.0) * pw
            hh = (entity.size.height / 2.0) * ph
            return (cx - hw, cy - hh, cx + hw, cy + hh), None
        if etype == "segment" and isinstance(entity.size, SegmentSize):
            if is_stacked:
                sx1 = px0 + entity.position.x * pw
                sx2 = px0 + entity.size.end_x * pw
                sy1 = cy
                sy2 = cy
                cx = (sx1 + sx2) / 2.0
            else:
                sx1 = px0 + entity.position.x * pw
                sy1 = py0 + entity.position.y * ph
                sx2 = px0 + entity.size.end_x * pw
                sy2 = py0 + entity.size.end_y * ph
                cx = (sx1 + sx2) / 2.0
                cy = (sy1 + sy2) / 2.0
            th = (entity.size.thickness / 2.0) * p_min
            return (
                min(sx1, sx2) - th, min(sy1, sy2) - th,
                max(sx1, sx2) + th, max(sy1, sy2) + th,
            ), None
        if etype == "capsule" and isinstance(entity.size, CapsuleSize):
            text_content = self._interpolate_template(entity.template, state_vars) if entity.template else None
            r = entity.size.radius * p_min
            hl = (entity.size.length / 2.0) * p_min
            dx = hl * math.cos(entity.size.angle)
            dy = hl * math.sin(entity.size.angle)
            if is_stacked and (cx - dx - r) < (px0 + (0.01 * pw)):
                cx = cx + dx + r
            return (
                min(cx - dx, cx + dx) - r, min(cy - dy, cy + dy) - r,
                max(cx - dx, cx + dx) + r, max(cy - dy, cy + dy) + r,
            ), text_content
        if etype == "text" and isinstance(entity.size, TextSize):
            text_content = self._interpolate_template(entity.template, state_vars)
            fs = entity.size.font_scale * p_min
            t_len = len(text_content) if text_content else 0
            if entity.size.align == "center":
                return (cx - (t_len * fs * 0.3), cy - fs / 2.0, cx + (t_len * fs * 0.3), cy + fs / 2.0), text_content
            if entity.size.align == "right":
                return (cx - (t_len * fs * 0.6), cy - fs / 2.0, cx, cy + fs / 2.0), text_content
            return (cx, cy - fs / 2.0, cx + (t_len * fs * 0.6), cy + fs / 2.0), text_content
        return (cx, cy, cx, cy), None

    def _compute_flat_shapes(
        self,
        env: Environment,
        entities: List[Entity],
        state_vars: Optional[Dict[str, Any]],
    ) -> List[ComputedShape]:
        """Fast-path linear shape projection for standard flat scenes without parent hierarchy."""
        w = float(env.width)
        h = float(env.height)
        p_min = min(w, h)
        shapes: List[ComputedShape] = []
        for entity in entities:
            if not entity.active:
                continue
            ex, ey = get_entity_effective_pos(entity, env)
            cx = ex * w
            cy = ey * h
            bbox, text_content = self._compute_entity_geometry(
                entity, w, h, p_min, cx, cy, 0.0, 0.0, state_vars, False
            )
            ang = (
                float(entity.size.angle + entity.angle)
                if (entity.type == "capsule" and isinstance(entity.size, CapsuleSize))
                else float(entity.angle)
            )
            shapes.append(
                ComputedShape(
                    id=entity.id,
                    type=entity.type,
                    bbox=bbox,
                    center=(cx, cy),
                    color=entity.properties.get("color", "#FFFFFF"),
                    text=text_content,
                    theta=ang,
                )
            )
        return shapes

    def _compute_hierarchical_shapes(
        self,
        env: Environment,
        entities: List[Entity],
        state_vars: Optional[Dict[str, Any]],
    ) -> List[ComputedShape]:
        """Resolves nested layout trees, parent containers, and auto-stacking."""
        w = float(env.width)
        h = float(env.height)

        children_by_parent: Dict[str, List[Entity]] = defaultdict(list)
        for entity in entities:
            if entity.parent_id is not None:
                children_by_parent[entity.parent_id].append(entity)

        stacked_offsets = self._calculate_auto_stacking(entities, children_by_parent, env)

        resolved_bboxes: Dict[str, Tuple[float, float, float, float]] = {}
        shape_dict: Dict[str, ComputedShape] = {}
        entity_map = {e.id: e for e in entities}
        remaining = [e for e in entities if e.active]

        while remaining:
            progress = False
            next_remaining = []
            for entity in remaining:
                parent_id = entity.parent_id
                if parent_id is not None and parent_id not in resolved_bboxes and parent_id in entity_map:
                    next_remaining.append(entity)
                    continue

                progress = True
                if parent_id is not None and parent_id in resolved_bboxes:
                    px0, py0, px1, py1 = resolved_bboxes[parent_id]
                else:
                    px0, py0, px1, py1 = 0.0, 0.0, w, h

                pw = max(1.0, px1 - px0)
                ph = max(1.0, py1 - py0)
                p_min = min(pw, ph)

                is_stacked = entity.id in stacked_offsets
                if parent_id is None and not is_stacked:
                    rx, ry = get_entity_effective_pos(entity, env)
                else:
                    rx, ry = stacked_offsets.get(entity.id, (entity.position.x, entity.position.y))
                cx = px0 + rx * pw
                cy = py0 + ry * ph

                bbox, text_content = self._compute_entity_geometry(
                    entity, pw, ph, p_min, cx, cy, px0, py0, state_vars, is_stacked
                )

                if entity.clip_bounds and parent_id is not None and parent_id in resolved_bboxes:
                    bbox = (
                        max(px0, min(px1, bbox[0])),
                        max(py0, min(py1, bbox[1])),
                        max(px0, min(px1, bbox[2])),
                        max(py0, min(py1, bbox[3])),
                    )

                resolved_bboxes[entity.id] = bbox
                ang = (
                    float(entity.size.angle + entity.angle)
                    if (entity.type == "capsule" and isinstance(entity.size, CapsuleSize))
                    else float(entity.angle)
                )
                shape_dict[entity.id] = ComputedShape(
                    id=entity.id,
                    type=entity.type,
                    bbox=bbox,
                    center=(cx, cy),
                    color=entity.properties.get("color", "#FFFFFF"),
                    text=text_content,
                    theta=ang,
                )

            if not progress and remaining:
                for e in remaining:
                    resolved_bboxes[e.id] = (0.0, 0.0, w, h)
                break
            remaining = next_remaining

        return [shape_dict[e.id] for e in entities if e.id in shape_dict]

    def _compute_shapes(
        self,
        env: Environment,
        entities: List[Entity],
        state_vars: Optional[Dict[str, Any]] = None,
    ) -> List[ComputedShape]:
        """Resolves normalized entity coordinates, layout hierarchy, and sizes into concrete screen-space geometry."""
        for e in entities:
            if e.parent_id is not None or e.layout is not None:
                return self._compute_hierarchical_shapes(env, entities, state_vars)
        return self._compute_flat_shapes(env, entities, state_vars)

    def evaluate(self, doc: MLUEDocument) -> EvaluationResult:
        """Evaluates an MLUEDocument into resolved computational entity states (instantaneous snapshot)."""
        shapes = self._compute_shapes(doc.environment, doc.entities, doc.state_variables)
        computed_constraints: List[ComputedConstraint] = []
        if doc.constraints:
            w = float(doc.environment.width)
            h = float(doc.environment.height)
            entity_by_id = {e.id: e for e in doc.entities}
            for c in doc.constraints:
                if c.entity_a not in entity_by_id:
                    continue
                e_a = entity_by_id[c.entity_a]
                e_b = entity_by_id.get(c.entity_b) if c.entity_b else None
                p_ax, p_ay, _, _ = self._compute_anchor_world(e_a, c.anchor_a)
                if e_b is not None:
                    p_bx, p_by, _, _ = self._compute_anchor_world(e_b, c.anchor_b)
                else:
                    p_bx, p_by = c.anchor_b.x, c.anchor_b.y
                computed_constraints.append(
                    ComputedConstraint(
                        id=c.id,
                        type=c.type,
                        p1=(p_ax * w, p_ay * h),
                        p2=(p_bx * w, p_by * h),
                    )
                )
        return EvaluationResult(
            width=doc.environment.width,
            height=doc.environment.height,
            background=doc.environment.background,
            shapes=shapes,
            constraints=computed_constraints,
        )

    def init_simulation(self, doc: MLUEDocument) -> SimulationState:
        """Initializes a dynamic simulation state from an MLUEDocument."""
        result = self.evaluate(doc)
        return SimulationState(
            time=0.0,
            environment=doc.environment,
            entities=list(doc.entities),
            result=result,
            state_variables=dict(doc.state_variables),
            rules=list(doc.rules),
            pointer=PointerState(),
            constraints=list(doc.constraints),
        )

    def cast_ray(
        self,
        state: SimulationState,
        origin: Tuple[float, float],
        angle_rad: float,
        max_range: float = 1.0,
        ignore_ids: Optional[Set[str]] = None,
    ) -> RayHit:
        """Casts an analytical 2D ray from origin (x, y) at angle_rad, returning the closest RayHit."""
        ray = Ray2D.from_angle(origin[0], origin[1], angle_rad, max_range=max_range)
        return cast_ray_scene(state.entities, state.environment, ray, ignore_ids=ignore_ids)

    def cast_lidar(
        self,
        state: SimulationState,
        origin: Tuple[float, float],
        num_rays: int = 8,
        fov_rad: float = 2.0 * math.pi,
        start_angle_rad: float = 0.0,
        max_range: float = 1.0,
        ignore_ids: Optional[Set[str]] = None,
    ) -> List[float]:
        """Casts a multi-directional LiDAR sweep of analytical rays, returning a list of normalized hit distances."""
        if num_rays <= 0:
            return []

        is_full_circle = abs(fov_rad - (2.0 * math.pi)) < 1e-6
        angle_step = (fov_rad / num_rays) if is_full_circle else (fov_rad / max(1, num_rays - 1))

        distances: List[float] = []
        for i in range(num_rays):
            angle = start_angle_rad + i * angle_step
            ray = Ray2D.from_angle(origin[0], origin[1], angle, max_range=max_range)
            hit = cast_ray_scene(state.entities, state.environment, ray, ignore_ids=ignore_ids)
            distances.append(hit.distance)

        return distances

    def _get_entity_extents(self, entity: Entity, env: Environment) -> Tuple[float, float]:
        """Returns normalized half-extents (ex, ey) for an entity."""
        etype = entity.type
        esize = entity.size

        if etype == "circle":
            r = esize.radius
            if env.width == env.height:
                return (r, r)
            min_dim = min(env.width, env.height)
            return (r * (min_dim / env.width), r * (min_dim / env.height))
        elif etype == "box":
            hw = esize.width * 0.5
            hh = esize.height * 0.5
            ang = entity.angle
            if ang != 0.0:
                c = abs(math.cos(ang))
                s = abs(math.sin(ang))
                return (hw * c + hh * s, hw * s + hh * c)
            return (hw, hh)
        elif etype == "segment":
            w = env.width
            h = env.height
            min_dim = min(w, h)
            dx = abs(esize.end_x - entity.position.x) * 0.5
            dy = abs(esize.end_y - entity.position.y) * 0.5
            th_x = (esize.thickness * 0.5) * (min_dim / w)
            th_y = (esize.thickness * 0.5) * (min_dim / h)
            return (dx + th_x, dy + th_y)
        elif etype == "capsule":
            w = env.width
            h = env.height
            hl = esize.length * 0.5
            tot_ang = esize.angle + entity.angle
            dx = abs(hl * math.cos(tot_ang))
            dy = abs(hl * math.sin(tot_ang))
            r = esize.radius
            if w == h:
                return (dx + r, dy + r)
            min_dim = min(w, h)
            return (dx + r * (min_dim / w), dy + r * (min_dim / h))
        return 0.0, 0.0

    def _get_entity_inv_mass_inertia(self, entity: Entity) -> Tuple[float, float]:
        """Calculates (inv_mass, inv_inertia) for rigid-body impulse dynamics."""
        props = entity.properties
        if not props.get("solid", False) or "control" in props or props.get("static", False) or entity.type == "segment":
            return 0.0, 0.0

        mass = float(props.get("mass", 1.0))
        if mass <= 0.0 or math.isinf(mass) or math.isnan(mass):
            return 0.0, 0.0
        m_inv = 1.0 / mass

        if props.get("fixed_rotation", False):
            return m_inv, 0.0

        inertia = 1.0
        if entity.type == "circle" and isinstance(entity.size, CircleSize):
            r = entity.size.radius
            inertia = 0.5 * mass * (r * r)
        elif entity.type == "box" and isinstance(entity.size, BoxSize):
            w = entity.size.width
            h = entity.size.height
            inertia = (1.0 / 12.0) * mass * (w * w + h * h)
        elif entity.type == "capsule" and isinstance(entity.size, CapsuleSize):
            L = entity.size.length
            r = entity.size.radius
            inertia = mass * ((L * L) / 12.0 + 0.5 * (r * r))

        if inertia <= 1e-9 or math.isnan(inertia) or math.isinf(inertia):
            return m_inv, 0.0
        return m_inv, 1.0 / inertia

    def _apply_contact_impulse(
        self,
        e1: Entity,
        e2: Entity,
        cx: float,
        cy: float,
        nx: float,
        ny: float,
        e1_static: bool = False,
        e2_static: bool = False,
    ) -> Tuple[Velocity, Velocity]:
        """Applies 2D rigid-body linear and angular impulse with restitution and Coulomb surface friction."""
        m1_inv, i1_inv = (0.0, 0.0) if e1_static else self._get_entity_inv_mass_inertia(e1)
        m2_inv, i2_inv = (0.0, 0.0) if e2_static else self._get_entity_inv_mass_inertia(e2)

        w1 = getattr(e1.velocity, "omega", 0.0)
        w2 = getattr(e2.velocity, "omega", 0.0)

        r1x = cx - e1.position.x
        r1y = cy - e1.position.y
        r2x = cx - e2.position.x
        r2y = cy - e2.position.y

        v1x = e1.velocity.vx - w1 * r1y
        v1y = e1.velocity.vy + w1 * r1x
        v2x = e2.velocity.vx - w2 * r2y
        v2y = e2.velocity.vy + w2 * r2x

        rvx = v1x - v2x
        rvy = v1y - v2y

        vn = rvx * nx + rvy * ny
        if vn >= 0.0:
            return e1.velocity, e2.velocity

        if m1_inv == 0.0 and m2_inv == 0.0:
            rest = min(float(e1.properties.get("restitution", 1.0)), float(e2.properties.get("restitution", 1.0)))
            new_v1x = e1.velocity.vx - (1.0 + rest) * vn * nx
            new_v1y = e1.velocity.vy - (1.0 + rest) * vn * ny
            return Velocity(vx=new_v1x, vy=new_v1y, omega=w1), e2.velocity

        rn1 = r1x * ny - r1y * nx
        rn2 = r2x * ny - r2y * nx
        kn = m1_inv + m2_inv + (rn1 * rn1) * i1_inv + (rn2 * rn2) * i2_inv
        if kn <= 1e-12:
            return e1.velocity, e2.velocity

        rest1 = float(e1.properties.get("restitution", 1.0))
        rest2 = float(e2.properties.get("restitution", 1.0))
        e_coeff = min(rest1, rest2)
        jn = -(1.0 + e_coeff) * vn / kn

        tx = -ny
        ty = nx
        vt = rvx * tx + rvy * ty

        fric1 = float(e1.properties.get("friction", 0.0))
        fric2 = float(e2.properties.get("friction", 0.0))
        mu = math.sqrt(fric1 * fric2) if (fric1 > 0.0 and fric2 > 0.0) else max(fric1, fric2)

        jt = 0.0
        if mu > 0.0:
            rt1 = r1x * ty - r1y * tx
            rt2 = r2x * ty - r2y * tx
            kt = m1_inv + m2_inv + (rt1 * rt1) * i1_inv + (rt2 * rt2) * i2_inv
            if kt > 1e-12:
                desired_jt = -vt / kt
                max_fric = mu * jn
                jt = max(-max_fric, min(max_fric, desired_jt))

        jx = jn * nx + jt * tx
        jy = jn * ny + jt * ty

        new_v1x = e1.velocity.vx + m1_inv * jx
        new_v1y = e1.velocity.vy + m1_inv * jy
        new_w1 = w1 + i1_inv * (r1x * jy - r1y * jx)

        new_v2x = e2.velocity.vx - m2_inv * jx
        new_v2y = e2.velocity.vy - m2_inv * jy
        new_w2 = w2 - i2_inv * (r2x * jy - r2y * jx)

        return (
            Velocity(vx=new_v1x, vy=new_v1y, omega=new_w1),
            Velocity(vx=new_v2x, vy=new_v2y, omega=new_w2),
        )

    def _resolve_circle_box_collision(
        self, circle: Entity, box: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between a Circle and a Box with rotation support."""
        cx = circle.position.x
        cy = circle.position.y
        rx, ry = self._get_entity_extents(circle, env)

        bx = box.position.x
        by = box.position.y
        hw, hh = self._get_entity_extents(box, env)
        box_ang = box.angle

        if box_ang == 0.0:
            if abs(cx - bx) >= (rx + hw) or abs(cy - by) >= (ry + hh):
                return circle, box, False

        if abs(box_ang) > 1e-9:
            cos_b = math.cos(-box_ang)
            sin_b = math.sin(-box_ang)
            dx_rel = cx - bx
            dy_rel = cy - by
            local_cx = dx_rel * cos_b - dy_rel * sin_b
            local_cy = dx_rel * sin_b + dy_rel * cos_b

            local_px = max(-hw, min(local_cx, hw))
            local_py = max(-hh, min(local_cy, hh))

            cos_f = math.cos(box_ang)
            sin_f = math.sin(box_ang)
            px = bx + (local_px * cos_f - local_py * sin_f)
            py = by + (local_px * sin_f + local_py * cos_f)

            dx = cx - px
            dy = cy - py
        else:
            px = max(bx - hw, min(cx, bx + hw))
            py = max(by - hh, min(cy, by + hh))
            dx = cx - px
            dy = cy - py

        norm_dist_sq = (dx / rx) ** 2 + (dy / ry) ** 2 if (rx > 0 and ry > 0) else 0.0

        if norm_dist_sq < 1.0 or (dx == 0.0 and dy == 0.0):
            if dx == 0.0 and dy == 0.0:
                if abs(box_ang) > 1e-9:
                    d_left = local_cx - (-hw)
                    d_right = hw - local_cx
                    d_top = local_cy - (-hh)
                    d_bottom = hh - local_cy
                    min_d = min(d_left, d_right, d_top, d_bottom)
                    if min_d == d_left:
                        lnx, lny = -1.0, 0.0
                        local_new_cx = -hw - rx
                        local_new_cy = local_cy
                        local_px = -hw
                        local_py = local_cy
                    elif min_d == d_right:
                        lnx, lny = 1.0, 0.0
                        local_new_cx = hw + rx
                        local_new_cy = local_cy
                        local_px = hw
                        local_py = local_cy
                    elif min_d == d_top:
                        lnx, lny = 0.0, -1.0
                        local_new_cx = local_cx
                        local_new_cy = -hh - ry
                        local_px = local_cx
                        local_py = -hh
                    else:
                        lnx, lny = 0.0, 1.0
                        local_new_cx = local_cx
                        local_new_cy = hh + ry
                        local_px = local_cx
                        local_py = hh
                    nx = lnx * cos_f - lny * sin_f
                    ny = lnx * sin_f + lny * cos_f
                    new_cx = bx + (local_new_cx * cos_f - local_new_cy * sin_f)
                    new_cy = by + (local_new_cx * sin_f + local_new_cy * cos_f)
                    px = bx + (local_px * cos_f - local_py * sin_f)
                    py = by + (local_px * sin_f + local_py * cos_f)
                else:
                    dist_left = cx - (bx - hw)
                    dist_right = (bx + hw) - cx
                    dist_top = cy - (by - hh)
                    dist_bottom = (by + hh) - cy
                    min_d = min(dist_left, dist_right, dist_top, dist_bottom)
                    if min_d == dist_left:
                        nx, ny = -1.0, 0.0
                        new_cx = bx - hw - rx
                        new_cy = cy
                        px = bx - hw
                        py = cy
                    elif min_d == dist_right:
                        nx, ny = 1.0, 0.0
                        new_cx = bx + hw + rx
                        new_cy = cy
                        px = bx + hw
                        py = cy
                    elif min_d == dist_top:
                        nx, ny = 0.0, -1.0
                        new_cx = cx
                        new_cy = by - hh - ry
                        px = cx
                        py = by - hh
                    else:
                        nx, ny = 0.0, 1.0
                        new_cx = cx
                        new_cy = by + hh + ry
                        px = cx
                        py = by + hh
            else:
                dist = math.hypot(dx, dy)
                nx = dx / dist
                ny = dy / dist
                new_cx = px + nx * rx
                new_cy = py + ny * ry

            box_static = not box.properties.get("dynamic", False)
            new_cvel, new_bvel = self._apply_contact_impulse(
                circle, box, px, py, nx, ny, e2_static=box_static
            )

            updated_circle = Entity(
                id=circle.id,
                type=circle.type,
                position=Position(x=new_cx, y=new_cy),
                size=circle.size,
                velocity=new_cvel,
                properties=circle.properties,
                active=circle.active,
                parent_id=circle.parent_id,
                clip_bounds=circle.clip_bounds,
                layout=circle.layout,
                template=circle.template,
                angle=getattr(circle, "angle", 0.0),
            )
            updated_box = Entity(
                id=box.id,
                type=box.type,
                position=box.position,
                size=box.size,
                velocity=new_bvel,
                properties=box.properties,
                active=box.active,
                parent_id=box.parent_id,
                clip_bounds=box.clip_bounds,
                layout=box.layout,
                template=box.template,
                angle=box_ang,
            )
            return updated_circle, updated_box, True

        return circle, box, False

    def _resolve_circle_circle_collision(
        self, c1: Entity, c2: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between two Circles with impulse dynamics."""
        r1x, _ = self._get_entity_extents(c1, env)
        r2x, _ = self._get_entity_extents(c2, env)
        target_dist = r1x + r2x

        dx = c1.position.x - c2.position.x
        if abs(dx) >= target_dist:
            return c1, c2, False
        dy = c1.position.y - c2.position.y
        if abs(dy) >= target_dist:
            return c1, c2, False
        dist = math.hypot(dx, dy)

        if dist < target_dist:
            if dist > 1e-12:
                nx = dx / dist
                ny = dy / dist
            else:
                nx, ny = 1.0, 0.0

            overlap = target_dist - dist
            new_c1x = c1.position.x + nx * (overlap / 2.0)
            new_c1y = c1.position.y + ny * (overlap / 2.0)
            new_c2x = c2.position.x - nx * (overlap / 2.0)
            new_c2y = c2.position.y - ny * (overlap / 2.0)

            cx = new_c1x - nx * r1x
            cy = new_c1y - ny * r1x

            new_v1, new_v2 = self._apply_contact_impulse(c1, c2, cx, cy, nx, ny)

            u1 = Entity(
                id=c1.id,
                type=c1.type,
                position=Position(x=new_c1x, y=new_c1y),
                size=c1.size,
                velocity=new_v1,
                properties=c1.properties,
                active=c1.active,
                parent_id=c1.parent_id,
                clip_bounds=c1.clip_bounds,
                layout=c1.layout,
                template=c1.template,
                angle=getattr(c1, "angle", 0.0),
            )
            u2 = Entity(
                id=c2.id,
                type=c2.type,
                position=Position(x=new_c2x, y=new_c2y),
                size=c2.size,
                velocity=new_v2,
                properties=c2.properties,
                active=c2.active,
                parent_id=c2.parent_id,
                clip_bounds=c2.clip_bounds,
                layout=c2.layout,
                template=c2.template,
                angle=getattr(c2, "angle", 0.0),
            )
            return u1, u2, True

        return c1, c2, False

    def _resolve_box_box_collision(
        self, b1: Entity, b2: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between two Boxes with impulse dynamics."""
        hw1, hh1 = self._get_entity_extents(b1, env)
        hw2, hh2 = self._get_entity_extents(b2, env)

        dx = b1.position.x - b2.position.x
        overlap_x = (hw1 + hw2) - abs(dx)
        if overlap_x <= 0.0:
            return b1, b2, False

        dy = b1.position.y - b2.position.y
        overlap_y = (hh1 + hh2) - abs(dy)
        if overlap_y <= 0.0:
            return b1, b2, False

        if True:
            if overlap_x < overlap_y:
                nx = 1.0 if dx > 0.0 else -1.0
                ny = 0.0
                new_b1x = b1.position.x + nx * (overlap_x / 2.0)
                new_b1y = b1.position.y
                new_b2x = b2.position.x - nx * (overlap_x / 2.0)
                new_b2y = b2.position.y
            else:
                nx = 0.0
                ny = 1.0 if dy > 0.0 else -1.0
                new_b1x = b1.position.x
                new_b1y = b1.position.y + ny * (overlap_y / 2.0)
                new_b2x = b2.position.x
                new_b2y = b2.position.y - ny * (overlap_y / 2.0)

            cx = (new_b1x + new_b2x) / 2.0
            cy = (new_b1y + new_b2y) / 2.0

            new_v1, new_v2 = self._apply_contact_impulse(b1, b2, cx, cy, nx, ny)

            u1 = Entity(
                id=b1.id,
                type=b1.type,
                position=Position(x=new_b1x, y=new_b1y),
                size=b1.size,
                velocity=new_v1,
                properties=b1.properties,
                active=b1.active,
                parent_id=b1.parent_id,
                clip_bounds=b1.clip_bounds,
                layout=b1.layout,
                template=b1.template,
                angle=getattr(b1, "angle", 0.0),
            )
            u2 = Entity(
                id=b2.id,
                type=b2.type,
                position=Position(x=new_b2x, y=new_b2y),
                size=b2.size,
                velocity=new_v2,
                properties=b2.properties,
                active=b2.active,
                parent_id=b2.parent_id,
                clip_bounds=b2.clip_bounds,
                layout=b2.layout,
                template=b2.template,
                angle=getattr(b2, "angle", 0.0),
            )
            return u1, u2, True

        return b1, b2, False

    def _resolve_circle_segment_collision(
        self, circle: Entity, segment: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between a moving Circle and a static Segment boundary."""
        if not isinstance(circle.size, CircleSize) or not isinstance(segment.size, SegmentSize):
            return circle, segment, False

        w = float(env.width)
        h = float(env.height)
        min_dim = min(w, h)
        scale_x = w / min_dim
        scale_y = h / min_dim

        px = circle.position.x * scale_x
        py = circle.position.y * scale_y
        ax = segment.position.x * scale_x
        ay = segment.position.y * scale_y
        bx = segment.size.end_x * scale_x
        by = segment.size.end_y * scale_y

        r = circle.size.radius
        th = segment.size.thickness / 2.0
        target_dist = r + th

        qx, qy, dist, nx, ny = _analytical_point_to_segment(px, py, ax, ay, bx, by)

        if dist < target_dist and target_dist > 0.0:
            pen = target_dist - dist
            new_cx = circle.position.x + nx * (pen / scale_x)
            new_cy = circle.position.y + ny * (pen / scale_y)

            contact_x = qx / scale_x
            contact_y = qy / scale_y
            new_cvel, _ = self._apply_contact_impulse(circle, segment, contact_x, contact_y, nx, ny)

            updated_circle = Entity(
                id=circle.id,
                type=circle.type,
                position=Position(x=new_cx, y=new_cy),
                size=circle.size,
                velocity=new_cvel,
                properties=circle.properties,
                active=circle.active,
                parent_id=circle.parent_id,
                clip_bounds=circle.clip_bounds,
                layout=circle.layout,
                template=circle.template,
                angle=getattr(circle, "angle", 0.0),
            )
            return updated_circle, segment, True

        return circle, segment, False

    def _resolve_capsule_circle_collision(
        self, capsule: Entity, circle: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between a Capsule and a Circle."""
        if not isinstance(capsule.size, CapsuleSize) or not isinstance(circle.size, CircleSize):
            return capsule, circle, False

        w = float(env.width)
        h = float(env.height)
        min_dim = min(w, h)
        scale_x = w / min_dim
        scale_y = h / min_dim

        cx = capsule.position.x * scale_x
        cy = capsule.position.y * scale_y
        hl = capsule.size.length / 2.0
        total_ang = capsule.size.angle + getattr(capsule, "angle", 0.0)
        dx_core = hl * math.cos(total_ang)
        dy_core = hl * math.sin(total_ang)
        cax, cay = cx - dx_core, cy - dy_core
        cbx, cby = cx + dx_core, cy + dy_core

        px = circle.position.x * scale_x
        py = circle.position.y * scale_y

        target_dist = capsule.size.radius + circle.size.radius
        qx, qy, dist, nx, ny = _analytical_point_to_segment(px, py, cax, cay, cbx, cby)

        if dist < target_dist and target_dist > 0.0:
            pen = target_dist - dist
            new_circle_x = circle.position.x + nx * (pen * 0.5 / scale_x)
            new_circle_y = circle.position.y + ny * (pen * 0.5 / scale_y)
            new_cap_x = capsule.position.x - nx * (pen * 0.5 / scale_x)
            new_cap_y = capsule.position.y - ny * (pen * 0.5 / scale_y)

            contact_x = (new_circle_x + new_cap_x) / 2.0
            contact_y = (new_circle_y + new_cap_y) / 2.0

            new_circ_vel, new_cap_vel = self._apply_contact_impulse(circle, capsule, contact_x, contact_y, nx, ny)

            upd_circle = Entity(
                id=circle.id, type=circle.type, position=Position(x=new_circle_x, y=new_circle_y),
                size=circle.size, velocity=new_circ_vel,
                properties=circle.properties, active=circle.active,
                parent_id=circle.parent_id, clip_bounds=circle.clip_bounds,
                layout=circle.layout, template=circle.template,
                angle=getattr(circle, "angle", 0.0),
            )
            upd_cap = Entity(
                id=capsule.id, type=capsule.type, position=Position(x=new_cap_x, y=new_cap_y),
                size=capsule.size, velocity=new_cap_vel,
                properties=capsule.properties, active=capsule.active,
                parent_id=capsule.parent_id, clip_bounds=capsule.clip_bounds,
                layout=capsule.layout, template=capsule.template,
                angle=getattr(capsule, "angle", 0.0),
            )
            return upd_cap, upd_circle, True

        return capsule, circle, False

    def _resolve_capsule_segment_collision(
        self, capsule: Entity, segment: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between a moving Capsule and a static Segment."""
        if not isinstance(capsule.size, CapsuleSize) or not isinstance(segment.size, SegmentSize):
            return capsule, segment, False

        w = float(env.width)
        h = float(env.height)
        min_dim = min(w, h)
        scale_x = w / min_dim
        scale_y = h / min_dim

        cx = capsule.position.x * scale_x
        cy = capsule.position.y * scale_y
        hl = capsule.size.length / 2.0
        total_ang = capsule.size.angle + getattr(capsule, "angle", 0.0)
        dx_core = hl * math.cos(total_ang)
        dy_core = hl * math.sin(total_ang)
        cax, cay = cx - dx_core, cy - dy_core
        cbx, cby = cx + dx_core, cy + dy_core

        sax = segment.position.x * scale_x
        say = segment.position.y * scale_y
        sbx = segment.size.end_x * scale_x
        sby = segment.size.end_y * scale_y

        target_dist = capsule.size.radius + segment.size.thickness / 2.0
        c1x, c1y, c2x, c2y, dist, nx, ny = _analytical_segment_to_segment(
            cax, cay, cbx, cby, sax, say, sbx, sby
        )

        if dist < target_dist and target_dist > 0.0:
            pen = target_dist - dist
            new_cx = capsule.position.x + nx * (pen / scale_x)
            new_cy = capsule.position.y + ny * (pen / scale_y)

            contact_x = c2x / scale_x
            contact_y = c2y / scale_y
            new_cap_vel, _ = self._apply_contact_impulse(capsule, segment, contact_x, contact_y, nx, ny)

            upd_cap = Entity(
                id=capsule.id, type=capsule.type, position=Position(x=new_cx, y=new_cy),
                size=capsule.size, velocity=new_cap_vel,
                properties=capsule.properties, active=capsule.active,
                parent_id=capsule.parent_id, clip_bounds=capsule.clip_bounds,
                layout=capsule.layout, template=capsule.template,
                angle=getattr(capsule, "angle", 0.0),
            )
            return upd_cap, segment, True

        return capsule, segment, False

    def _resolve_capsule_capsule_collision(
        self, cap1: Entity, cap2: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between two dynamic Capsules."""
        if not isinstance(cap1.size, CapsuleSize) or not isinstance(cap2.size, CapsuleSize):
            return cap1, cap2, False

        w = float(env.width)
        h = float(env.height)
        min_dim = min(w, h)
        scale_x = w / min_dim
        scale_y = h / min_dim

        c1x = cap1.position.x * scale_x
        c1y = cap1.position.y * scale_y
        hl1 = cap1.size.length / 2.0
        ang1 = cap1.size.angle + getattr(cap1, "angle", 0.0)
        dx1 = hl1 * math.cos(ang1)
        dy1 = hl1 * math.sin(ang1)

        c2x = cap2.position.x * scale_x
        c2y = cap2.position.y * scale_y
        hl2 = cap2.size.length / 2.0
        ang2 = cap2.size.angle + getattr(cap2, "angle", 0.0)
        dx2 = hl2 * math.cos(ang2)
        dy2 = hl2 * math.sin(ang2)

        target_dist = cap1.size.radius + cap2.size.radius
        c1_cx, c1_cy, c2_cx, c2_cy, dist, nx, ny = _analytical_segment_to_segment(
            c1x - dx1, c1y - dy1, c1x + dx1, c1y + dy1,
            c2x - dx2, c2y - dy2, c2x + dx2, c2y + dy2,
        )

        if dist < target_dist and target_dist > 0.0:
            pen = target_dist - dist
            if dist <= 1e-12:
                cdx = cap1.position.x - cap2.position.x
                cdy = cap1.position.y - cap2.position.y
                c_dist = math.hypot(cdx, cdy)
                if c_dist > 1e-12:
                    nx, ny = cdx / c_dist, cdy / c_dist
                else:
                    nx, ny = -1.0, 0.0

            new_c1x = cap1.position.x + nx * (pen * 0.5 / scale_x)
            new_c1y = cap1.position.y + ny * (pen * 0.5 / scale_y)
            new_c2x = cap2.position.x - nx * (pen * 0.5 / scale_x)
            new_c2y = cap2.position.y - ny * (pen * 0.5 / scale_y)

            contact_x = (new_c1x + new_c2x) / 2.0
            contact_y = (new_c1y + new_c2y) / 2.0

            new_v1, new_v2 = self._apply_contact_impulse(cap1, cap2, contact_x, contact_y, nx, ny)

            u1 = Entity(
                id=cap1.id, type=cap1.type, position=Position(x=new_c1x, y=new_c1y),
                size=cap1.size, velocity=new_v1,
                properties=cap1.properties, active=cap1.active,
                parent_id=cap1.parent_id, clip_bounds=cap1.clip_bounds,
                layout=cap1.layout, template=cap1.template,
                angle=getattr(cap1, "angle", 0.0),
            )
            u2 = Entity(
                id=cap2.id, type=cap2.type, position=Position(x=new_c2x, y=new_c2y),
                size=cap2.size, velocity=new_v2,
                properties=cap2.properties, active=cap2.active,
                parent_id=cap2.parent_id, clip_bounds=cap2.clip_bounds,
                layout=cap2.layout, template=cap2.template,
                angle=getattr(cap2, "angle", 0.0),
            )
            return u1, u2, True

        return cap1, cap2, False

    def _resolve_capsule_box_collision(
        self, capsule: Entity, box: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between a Capsule and a Box."""
        if not isinstance(capsule.size, CapsuleSize) or not isinstance(box.size, BoxSize):
            return capsule, box, False

        w = float(env.width)
        h = float(env.height)
        min_dim = min(w, h)
        scale_x = w / min_dim
        scale_y = h / min_dim

        cx = capsule.position.x * scale_x
        cy = capsule.position.y * scale_y
        hl = capsule.size.length / 2.0
        total_ang = capsule.size.angle + getattr(capsule, "angle", 0.0)
        dx_core = hl * math.cos(total_ang)
        dy_core = hl * math.sin(total_ang)
        cax, cay = cx - dx_core, cy - dy_core
        cbx, cby = cx + dx_core, cy + dy_core

        bx = box.position.x * scale_x
        by = box.position.y * scale_y
        hw = (box.size.width / 2.0) * scale_x
        hh = (box.size.height / 2.0) * scale_y

        segments = [
            (bx - hw, by - hh, bx + hw, by - hh),
            (bx - hw, by + hh, bx + hw, by + hh),
            (bx - hw, by - hh, bx - hw, by + hh),
            (bx + hw, by - hh, bx + hw, by + hh),
        ]

        min_d = float("inf")
        best_nx, best_ny = 0.0, 0.0

        for sx1, sy1, sx2, sy2 in segments:
            _, _, _, _, dist, nx, ny = _analytical_segment_to_segment(
                cax, cay, cbx, cby, sx1, sy1, sx2, sy2
            )
            if dist < min_d:
                min_d = dist
                best_nx, best_ny = nx, ny

        target_dist = capsule.size.radius
        inside = (bx - hw <= cx <= bx + hw) and (by - hh <= cy <= by + hh)

        if min_d < target_dist or inside:
            pen = (target_dist - min_d) if not inside else (target_dist + min_d)
            nx, ny = best_nx, best_ny
            if nx == 0.0 and ny == 0.0:
                nx, ny = 0.0, -1.0

            new_cap_x = capsule.position.x + nx * (pen / scale_x)
            new_cap_y = capsule.position.y + ny * (pen / scale_y)

            contact_x = new_cap_x
            contact_y = new_cap_y
            box_static = not box.properties.get("dynamic", False)
            new_cap_vel, new_box_vel = self._apply_contact_impulse(
                capsule, box, contact_x, contact_y, nx, ny, e2_static=box_static
            )

            upd_cap = Entity(
                id=capsule.id, type=capsule.type, position=Position(x=new_cap_x, y=new_cap_y),
                size=capsule.size, velocity=new_cap_vel,
                properties=capsule.properties, active=capsule.active,
                parent_id=capsule.parent_id, clip_bounds=capsule.clip_bounds,
                layout=capsule.layout, template=capsule.template,
                angle=getattr(capsule, "angle", 0.0),
            )
            upd_box = Entity(
                id=box.id, type=box.type, position=box.position,
                size=box.size, velocity=new_box_vel,
                properties=box.properties, active=box.active,
                parent_id=box.parent_id, clip_bounds=box.clip_bounds,
                layout=box.layout, template=box.template,
                angle=getattr(box, "angle", 0.0),
            )
            return upd_cap, upd_box, True

        return capsule, box, False

    def _get_entity_property_value(self, entity: Entity, prop_path: str) -> float:
        """Extracts a numerical property from an Entity (e.g. 'position.x')."""
        if prop_path == "position.x":
            return entity.position.x
        elif prop_path == "position.y":
            return entity.position.y
        elif prop_path == "velocity.vx":
            return entity.velocity.vx
        elif prop_path == "velocity.vy":
            return entity.velocity.vy
        elif prop_path in ("velocity.omega", "angular_velocity"):
            return getattr(entity.velocity, "omega", 0.0)
        elif prop_path == "angle":
            return getattr(entity, "angle", 0.0)
        return 0.0

    def _integrate_entity_motion(
        self,
        entity: Entity,
        dt: float,
        input_map: Dict[str, float],
        env: Environment,
    ) -> Entity:
        """Applies input control modulation, time integration, and boundary constraints to a single entity."""
        if not entity.active or entity.type in ("segment", "text"):
            return entity

        ex, ey = self._get_entity_extents(entity, env)
        x, y = entity.position.x, entity.position.y
        vx, vy = entity.velocity.vx, entity.velocity.vy
        omega = entity.velocity.omega
        curr_angle = entity.angle
        is_controlled = False

        if "control" in entity.properties:
            ctrl = entity.properties["control"]
            channel = ctrl.get("channel")
            axis = ctrl.get("axis", "y")
            speed = ctrl.get("speed", 0.0)
            is_controlled = True

            if channel in input_map:
                signal = max(-1.0, min(1.0, float(input_map[channel])))
                if axis == "y":
                    vy = signal * speed
                elif axis == "x":
                    vx = signal * speed
                elif axis in ("omega", "angle", "rotation"):
                    omega = signal * speed
            else:
                if axis == "y":
                    vy = 0.0
                elif axis == "x":
                    vx = 0.0
                elif axis in ("omega", "angle", "rotation"):
                    omega = 0.0

        new_x = x + vx * dt
        new_y = y + vy * dt
        new_angle = (curr_angle + omega * dt) % 6.283185307179586 if omega != 0.0 else curr_angle
        new_vx, new_vy = vx, vy

        if is_controlled:
            if new_x - ex <= 0.0:
                new_x = ex
                new_vx = max(0.0, new_vx)
            elif new_x + ex >= 1.0:
                new_x = 1.0 - ex
                new_vx = min(0.0, new_vx)

            if new_y - ey <= 0.0:
                new_y = ey
                new_vy = max(0.0, new_vy)
            elif new_y + ey >= 1.0:
                new_y = 1.0 - ey
                new_vy = min(0.0, new_vy)
        else:
            if new_x - ex <= 0.0:
                new_x = ex
                if new_vx < 0.0:
                    e_rest = float(entity.properties.get("restitution", 1.0))
                    new_vx = -new_vx * e_rest
            elif new_x + ex >= 1.0:
                new_x = 1.0 - ex
                if new_vx > 0.0:
                    e_rest = float(entity.properties.get("restitution", 1.0))
                    new_vx = -new_vx * e_rest

            if new_y - ey <= 0.0:
                new_y = ey
                if new_vy < 0.0:
                    e_rest = float(entity.properties.get("restitution", 1.0))
                    new_vy = -new_vy * e_rest
            elif new_y + ey >= 1.0:
                new_y = 1.0 - ey
                if new_vy > 0.0:
                    e_rest = float(entity.properties.get("restitution", 1.0))
                    new_vy = -new_vy * e_rest

        return Entity(
            id=entity.id,
            type=entity.type,
            position=Position(x=new_x, y=new_y),
            size=entity.size,
            velocity=Velocity(vx=new_vx, vy=new_vy, omega=omega),
            properties=entity.properties,
            active=entity.active,
            parent_id=entity.parent_id,
            clip_bounds=entity.clip_bounds,
            layout=entity.layout,
            template=entity.template,
            angle=new_angle,
        )

    def _resolve_pair_collision(
        self, e1: Entity, e2: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Dispatches pairwise collision resolution across supported geometric types."""
        pair = (e1.type, e2.type)
        if pair == ("circle", "box"):
            return self._resolve_circle_box_collision(e1, e2, env)
        if pair == ("box", "circle"):
            r2, r1, hit = self._resolve_circle_box_collision(e2, e1, env)
            return r1, r2, hit
        if pair == ("circle", "circle"):
            return self._resolve_circle_circle_collision(e1, e2, env)
        if pair == ("box", "box"):
            return self._resolve_box_box_collision(e1, e2, env)
        if pair == ("circle", "segment"):
            return self._resolve_circle_segment_collision(e1, e2, env)
        if pair == ("segment", "circle"):
            r2, r1, hit = self._resolve_circle_segment_collision(e2, e1, env)
            return r1, r2, hit
        if pair == ("capsule", "circle"):
            return self._resolve_capsule_circle_collision(e1, e2, env)
        if pair == ("circle", "capsule"):
            r2, r1, hit = self._resolve_capsule_circle_collision(e2, e1, env)
            return r1, r2, hit
        if pair == ("capsule", "segment"):
            return self._resolve_capsule_segment_collision(e1, e2, env)
        if pair == ("segment", "capsule"):
            r2, r1, hit = self._resolve_capsule_segment_collision(e2, e1, env)
            return r1, r2, hit
        if pair == ("capsule", "capsule"):
            return self._resolve_capsule_capsule_collision(e1, e2, env)
        if pair == ("capsule", "box"):
            return self._resolve_capsule_box_collision(e1, e2, env)
        if pair == ("box", "capsule"):
            r2, r1, hit = self._resolve_capsule_box_collision(e2, e1, env)
            return r1, r2, hit
        return e1, e2, False

    def _resolve_pairwise_collisions(
        self, entities: List[Entity], env: Environment
    ) -> Tuple[List[Entity], Set[FrozenSet[str]]]:
        """Resolves pairwise relational collisions using broadphase spatial indexing and narrowphase physics."""
        collision_events: Set[FrozenSet[str]] = set()
        n = len(entities)
        if n < 2:
            return entities, collision_events

        # 1. Broadphase: Generate candidate collision pairs
        if n <= 6:
            candidate_pairs = _SMALL_PAIRS.get(n, ())
        else:
            grid = SpatialHashGrid2D()
            aabbs = grid.build(entities, env)
            candidate_pairs = grid.get_candidate_pairs(aabbs)

        # 2. Narrowphase: Exact impulse collision resolution
        for i, j in candidate_pairs:
            e1 = entities[i]
            e2 = entities[j]
            if not (e1.active and e2.active):
                continue

            if e1.properties.get("solid", False) and e2.properties.get("solid", False):
                e1_res, e2_res, has_collided = self._resolve_pair_collision(e1, e2, env)
                if has_collided:
                    entities[i], entities[j] = e1_res, e2_res
                    collision_events.add(frozenset([e1.id, e2.id]))

        return entities, collision_events

    def _resolve_path_parent(
        self, root: Dict[str, Any], path: str
    ) -> Tuple[Optional[Any], Optional[Union[str, int]]]:
        """Resolves keypath to its parent container (dict or list) and final token key/index."""
        tokens = parse_keypath(path)
        if not tokens:
            return None, None
        curr: Any = root
        for tok in tokens[:-1]:
            if isinstance(curr, dict) and isinstance(tok, str):
                curr = curr.get(tok)
            elif isinstance(curr, list) and isinstance(tok, int):
                if 0 <= tok < len(curr) or (tok < 0 and abs(tok) <= len(curr)):
                    curr = curr[tok]
                else:
                    return None, None
            else:
                return None, None
            if curr is None:
                return None, None
        return curr, tokens[-1]

    def _get_path_value(self, root: Dict[str, Any], path: str) -> Any:
        """Retrieves value addressed by keypath, supporting .length on lists."""
        tokens = parse_keypath(path)
        if not tokens:
            return None
        curr: Any = root
        for idx, tok in enumerate(tokens):
            if tok == "length" and idx == len(tokens) - 1 and isinstance(curr, list):
                return len(curr)
            if isinstance(curr, dict) and isinstance(tok, str):
                curr = curr.get(tok)
            elif isinstance(curr, list) and isinstance(tok, int):
                if 0 <= tok < len(curr) or (tok < 0 and abs(tok) <= len(curr)):
                    curr = curr[tok]
                else:
                    return None
            else:
                return None
            if curr is None:
                return None
        return curr

    def _set_path_value(self, root: Dict[str, Any], path: str, value: Any) -> None:
        """Assigns value to the location addressed by keypath."""
        parent, final_tok = self._resolve_path_parent(root, path)
        if parent is None or final_tok is None:
            return
        if isinstance(parent, dict) and isinstance(final_tok, str):
            parent[final_tok] = value
        elif isinstance(parent, list) and isinstance(final_tok, int):
            if 0 <= final_tok < len(parent) or (final_tok < 0 and abs(final_tok) <= len(parent)):
                parent[final_tok] = value

    def _increment_path_value(self, root: Dict[str, Any], path: str, amount: float) -> None:
        """Adds numeric delta to value addressed by keypath."""
        parent, final_tok = self._resolve_path_parent(root, path)
        if parent is None or final_tok is None:
            return
        if isinstance(parent, dict) and isinstance(final_tok, str):
            curr_val = parent.get(final_tok)
            if isinstance(curr_val, (int, float)):
                parent[final_tok] = curr_val + amount
        elif isinstance(parent, list) and isinstance(final_tok, int):
            if 0 <= final_tok < len(parent) or (final_tok < 0 and abs(final_tok) <= len(parent)):
                curr_val = parent[final_tok]
                if isinstance(curr_val, (int, float)):
                    parent[final_tok] = curr_val + amount

    def _push_path_value(self, root: Dict[str, Any], path: str, value: Any) -> None:
        """Appends value to array addressed by keypath."""
        target = self._get_path_value(root, path)
        if isinstance(target, list):
            target.append(value)

    def _pop_path_value(self, root: Dict[str, Any], path: str, index: int = -1) -> None:
        """Removes element from array addressed by keypath."""
        target = self._get_path_value(root, path)
        if isinstance(target, list):
            if 0 <= index < len(target) or (index < 0 and abs(index) <= len(target)):
                target.pop(index)

    def _delete_path_key(self, root: Dict[str, Any], path: str, key: Optional[str] = None) -> None:
        """Deletes key from dictionary addressed by keypath."""
        if key is not None:
            target = self._get_path_value(root, path)
            if isinstance(target, dict):
                target.pop(key, None)
        else:
            parent, final_tok = self._resolve_path_parent(root, path)
            if isinstance(parent, dict) and isinstance(final_tok, str):
                parent.pop(final_tok, None)

    def _evaluate_rule_condition(
        self,
        cond: Condition,
        entities: List[Entity],
        entity_map: Dict[str, int],
        state_variables: Dict[str, Any],
    ) -> bool:
        """Evaluates whether a single rule condition is satisfied."""
        if cond.state_path is not None:
            actual_val = self._get_path_value(state_variables, cond.state_path)
            threshold = cond.value
            if actual_val is None:
                return False
            try:
                if cond.op == "<=": return actual_val <= threshold
                if cond.op == ">=": return actual_val >= threshold
                if cond.op == "<":  return actual_val < threshold
                if cond.op == ">":  return actual_val > threshold
                if cond.op == "==": return actual_val == threshold
                if cond.op == "!=": return actual_val != threshold
            except TypeError:
                return False

        elif cond.state_variable is not None:
            actual_val = state_variables.get(cond.state_variable, 0)
            threshold = cond.value
            if cond.op == "<=": return actual_val <= threshold
            if cond.op == ">=": return actual_val >= threshold
            if cond.op == "<":  return actual_val < threshold
            if cond.op == ">":  return actual_val > threshold
            if cond.op == "==": return actual_val == threshold
            if cond.op == "!=": return actual_val != threshold

        elif cond.entity is not None:
            ent_idx = entity_map.get(cond.entity)
            if ent_idx is not None and entities[ent_idx].active:
                target_entity = entities[ent_idx]
                actual_val = self._get_entity_property_value(target_entity, cond.property or "position.x")
                threshold = float(cond.value)
                if cond.op == "<=": return actual_val <= threshold
                if cond.op == ">=": return actual_val >= threshold
                if cond.op == "<":  return actual_val < threshold
                if cond.op == ">":  return actual_val > threshold
                if cond.op == "==": return abs(actual_val - threshold) < 1e-6
                if cond.op == "!=": return abs(actual_val - threshold) >= 1e-6

        return False

    def _execute_rule_actions(
        self,
        actions: List[Action],
        entities: List[Entity],
        entity_map: Dict[str, int],
        state_variables: Dict[str, Any],
    ) -> Tuple[float, bool, bool]:
        """Executes a list of state mutation actions. Returns (delta_reward, is_terminated, is_truncated)."""
        delta_reward = 0.0
        is_terminated = False
        is_truncated = False
        for action in actions:
            if action.type == "reward":
                amt = float(action.amount) if action.amount is not None else 1.0
                delta_reward += amt
            elif action.type == "terminate":
                is_terminated = True
            elif action.type == "truncate":
                is_truncated = True
            elif action.type in ("destroy_entity", "deactivate_entity"):
                t_idx = entity_map.get(action.target)
                if t_idx is not None:
                    curr = entities[t_idx]
                    entities[t_idx] = Entity(
                        id=curr.id, type=curr.type, position=curr.position,
                        size=curr.size, velocity=curr.velocity, properties=curr.properties,
                        active=False,
                        parent_id=curr.parent_id,
                        clip_bounds=curr.clip_bounds,
                        layout=curr.layout,
                        template=curr.template,
                        angle=curr.angle,
                    )
            elif action.type == "set_property":
                t_idx = entity_map.get(action.target)
                if t_idx is not None and action.property is not None:
                    curr = entities[t_idx]
                    props = dict(curr.properties)
                    props[action.property] = action.value
                    entities[t_idx] = Entity(
                        id=curr.id, type=curr.type, position=curr.position,
                        size=curr.size, velocity=curr.velocity, properties=props,
                        active=curr.active,
                        parent_id=curr.parent_id,
                        clip_bounds=curr.clip_bounds,
                        layout=curr.layout,
                        template=curr.template,
                        angle=curr.angle,
                    )
            elif action.type == "increment" and action.target in state_variables:
                amt = action.amount if action.amount is not None else 1.0
                state_variables[action.target] = state_variables[action.target] + amt
            elif action.type == "set" and action.target in state_variables:
                state_variables[action.target] = action.value
            elif action.type == "set_path":
                self._set_path_value(state_variables, action.target, action.value)
            elif action.type == "increment_path":
                amt = action.amount if action.amount is not None else 1.0
                self._increment_path_value(state_variables, action.target, amt)
            elif action.type == "push":
                self._push_path_value(state_variables, action.target, action.value)
            elif action.type == "pop":
                idx = action.index if action.index is not None else -1
                self._pop_path_value(state_variables, action.target, idx)
            elif action.type == "delete_key":
                self._delete_path_key(state_variables, action.target, action.key)
            elif action.type == "reset_entity":
                reset_idx = entity_map.get(action.target)
                if reset_idx is not None:
                    curr = entities[reset_idx]
                    new_pos = action.position if action.position is not None else curr.position
                    new_vel = action.velocity if action.velocity is not None else curr.velocity
                    entities[reset_idx] = Entity(
                        id=curr.id, type=curr.type, position=new_pos,
                        size=curr.size, velocity=new_vel, properties=curr.properties,
                        active=True,
                        parent_id=curr.parent_id,
                        clip_bounds=curr.clip_bounds,
                        layout=curr.layout,
                        template=curr.template,
                        angle=curr.angle,
                    )
        return delta_reward, is_terminated, is_truncated

    def _clone_state_variables(self, state_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Ultra-fast deterministic deep cloning of hierarchical state variables without copy.deepcopy overhead."""
        res: Dict[str, Any] = {}
        for k, v in state_dict.items():
            if isinstance(v, dict):
                res[k] = self._clone_state_variables(v)
            elif isinstance(v, list):
                res[k] = [
                    self._clone_state_variables(item) if isinstance(item, dict)
                    else (list(item) if isinstance(item, list) else item)
                    for item in v
                ]
            else:
                res[k] = v
        return res

    def _process_pointer_input(
        self,
        state: SimulationState,
        input_map: Dict[str, Any],
        moved_entities: List[Entity],
        env: Environment,
    ) -> Tuple[PointerState, Dict[str, Optional[str]]]:
        """Resolves pointer state transitions and generates discrete interaction events."""
        old_ptr = state.pointer
        pointer_input = input_map.get("pointer")
        has_flat_pointer = "pointer_x" in input_map or "pointer_y" in input_map

        # Fast path: No pointer input and no active drag/hover state
        if pointer_input is None and not has_flat_pointer and not old_ptr.pressed and old_ptr.hovered_entity_id is None:
            return old_ptr, {}
        if isinstance(pointer_input, dict):
            new_px = float(pointer_input.get("x", old_ptr.x))
            new_py = float(pointer_input.get("y", old_ptr.y))
            new_pressed = bool(pointer_input.get("pressed", old_ptr.pressed))
        elif "pointer_x" in input_map or "pointer_y" in input_map:
            new_px = float(input_map.get("pointer_x", old_ptr.x))
            new_py = float(input_map.get("pointer_y", old_ptr.y))
            new_pressed = bool(input_map.get("pointer_pressed", old_ptr.pressed))
        else:
            new_px = old_ptr.x
            new_py = old_ptr.y
            new_pressed = old_ptr.pressed

        just_pressed = new_pressed and not old_ptr.pressed
        just_released = not new_pressed and old_ptr.pressed
        current_hovered = hit_test_scene(moved_entities, new_px, new_py, env)

        if just_pressed:
            new_pressed_id = current_hovered
        elif not new_pressed:
            new_pressed_id = None
        else:
            new_pressed_id = old_ptr.pressed_entity_id

        events = {
            "pointer_down": current_hovered if just_pressed else None,
            "pointer_up": current_hovered if just_released else None,
            "pointer_click": (
                current_hovered
                if (just_released and old_ptr.pressed_entity_id == current_hovered and current_hovered is not None)
                else None
            ),
            "pointer_hover_enter": (
                current_hovered
                if (current_hovered != old_ptr.hovered_entity_id and current_hovered is not None)
                else None
            ),
            "pointer_hover_exit": (
                old_ptr.hovered_entity_id
                if (current_hovered != old_ptr.hovered_entity_id and old_ptr.hovered_entity_id is not None)
                else None
            ),
        }

        new_pointer = PointerState(
            x=new_px,
            y=new_py,
            pressed=new_pressed,
            hovered_entity_id=current_hovered,
            pressed_entity_id=new_pressed_id,
        )
        return new_pointer, events

    def _is_rule_triggered(
        self,
        rule: Rule,
        collision_events: Set[FrozenSet[str]],
        pointer_events: Dict[str, Optional[str]],
        moved_entities: List[Entity],
        entity_map: Dict[str, int],
        state_variables: Dict[str, Any],
    ) -> bool:
        """Determines if a declarative rule is satisfied during the current time step."""
        if rule.event == "collision" and rule.entities:
            triggered = frozenset(rule.entities) in collision_events
        elif rule.event in pointer_events:
            target = pointer_events[rule.event]
            triggered = (target is not None and rule.entity == target)
        elif rule.condition is not None:
            triggered = self._evaluate_rule_condition(
                rule.condition, moved_entities, entity_map, state_variables
            )
        else:
            triggered = False

        if triggered and rule.event is not None and rule.condition is not None:
            triggered = self._evaluate_rule_condition(
                rule.condition, moved_entities, entity_map, state_variables
            )
        return triggered

    def _compute_anchor_world(self, entity: Entity, anchor: Position) -> Tuple[float, float, float, float]:
        """Returns (world_x, world_y, lever_rx, lever_ry) for an entity anchor."""
        ang = entity.angle
        ca = math.cos(ang)
        sa = math.sin(ang)
        rx = anchor.x * ca - anchor.y * sa
        ry = anchor.x * sa + anchor.y * ca
        return entity.position.x + rx, entity.position.y + ry, rx, ry

    def _update_entity_kinematics(
        self,
        e: Entity,
        x: float,
        y: float,
        vx: float,
        vy: float,
        omega: float,
        angle: float,
    ) -> Entity:
        """Constructs an updated Entity instance with modified kinematic state."""
        return Entity(
            id=e.id,
            type=e.type,
            position=Position(x=x, y=y),
            size=e.size,
            velocity=Velocity(vx=vx, vy=vy, omega=omega),
            properties=e.properties,
            active=e.active,
            parent_id=e.parent_id,
            clip_bounds=e.clip_bounds,
            layout=e.layout,
            template=e.template,
            angle=angle,
            anchor=e.anchor,
        )

    def _get_constraint_inv_mass_inertia(self, entity: Entity) -> Tuple[float, float]:
        """Calculates (inv_mass, inv_inertia) for constraint dynamics."""
        props = entity.properties
        if props.get("static", False) or entity.type == "segment" or "control" in props:
            return 0.0, 0.0
        mass = float(props.get("mass", 1.0))
        if mass <= 0.0 or math.isinf(mass) or math.isnan(mass):
            return 0.0, 0.0
        m_inv = 1.0 / mass
        if props.get("fixed_rotation", False):
            return m_inv, 0.0
        inertia = 1.0
        if entity.type == "circle" and isinstance(entity.size, CircleSize):
            r = entity.size.radius
            inertia = 0.5 * mass * (r * r)
        elif entity.type == "box" and isinstance(entity.size, BoxSize):
            w = entity.size.width
            h = entity.size.height
            inertia = (1.0 / 12.0) * mass * (w * w + h * h)
        elif entity.type == "capsule" and isinstance(entity.size, CapsuleSize):
            L = entity.size.length
            r = entity.size.radius
            inertia = mass * ((L * L) / 12.0 + 0.5 * (r * r))
        if inertia <= 1e-9 or math.isnan(inertia) or math.isinf(inertia):
            return m_inv, 0.0
        return m_inv, 1.0 / inertia

    def _solve_spring_constraint(
        self,
        e_a: Entity,
        e_b: Optional[Entity],
        constraint: Constraint,
        dt: float,
    ) -> Tuple[Entity, Optional[Entity]]:
        """Applies Hookean and damping impulses between entity A and entity B (or world)."""
        if dt <= 0.0:
            return e_a, e_b

        p_ax, p_ay, r_ax, r_ay = self._compute_anchor_world(e_a, constraint.anchor_a)
        v_ax = e_a.velocity.vx - e_a.velocity.omega * r_ay
        v_ay = e_a.velocity.vy + e_a.velocity.omega * r_ax
        m_a_inv, i_a_inv = self._get_constraint_inv_mass_inertia(e_a)

        if e_b is not None:
            p_bx, p_by, r_bx, r_by = self._compute_anchor_world(e_b, constraint.anchor_b)
            v_bx = e_b.velocity.vx - e_b.velocity.omega * r_by
            v_by = e_b.velocity.vy + e_b.velocity.omega * r_bx
            m_b_inv, i_b_inv = self._get_constraint_inv_mass_inertia(e_b)
        else:
            p_bx, p_by, r_bx, r_by = constraint.anchor_b.x, constraint.anchor_b.y, 0.0, 0.0
            v_bx, v_by = 0.0, 0.0
            m_b_inv, i_b_inv = 0.0, 0.0

        dx = p_bx - p_ax
        dy = p_by - p_ay
        dist = math.hypot(dx, dy)
        if dist < 1e-9:
            ux, uy = 1.0, 0.0
        else:
            ux = dx / dist
            uy = dy / dist

        rest_len = constraint.length if constraint.length is not None else 0.0
        delta_l = dist - rest_len
        v_rel = (v_bx - v_ax) * ux + (v_by - v_ay) * uy

        f_spring = constraint.stiffness * delta_l + constraint.damping * v_rel
        jx = f_spring * dt * ux
        jy = f_spring * dt * uy

        new_e_a = e_a
        if m_a_inv > 0.0 or i_a_inv > 0.0:
            new_vax = e_a.velocity.vx + m_a_inv * jx
            new_vay = e_a.velocity.vy + m_a_inv * jy
            new_w_a = e_a.velocity.omega + i_a_inv * (r_ax * jy - r_ay * jx)
            new_e_a = self._update_entity_kinematics(
                e_a, e_a.position.x, e_a.position.y, new_vax, new_vay, new_w_a, e_a.angle
            )

        new_e_b = e_b
        if e_b is not None and (m_b_inv > 0.0 or i_b_inv > 0.0):
            new_vbx = e_b.velocity.vx - m_b_inv * jx
            new_vby = e_b.velocity.vy - m_b_inv * jy
            new_w_b = e_b.velocity.omega - i_b_inv * (r_bx * jy - r_by * jx)
            new_e_b = self._update_entity_kinematics(
                e_b, e_b.position.x, e_b.position.y, new_vbx, new_vby, new_w_b, e_b.angle
            )

        return new_e_a, new_e_b

    def _solve_distance_constraint(
        self,
        e_a: Entity,
        e_b: Optional[Entity],
        constraint: Constraint,
        dt: float,
    ) -> Tuple[Entity, Optional[Entity]]:
        """Applies Baumgarte-stabilized impulse to maintain exact distance between anchors."""
        p_ax, p_ay, r_ax, r_ay = self._compute_anchor_world(e_a, constraint.anchor_a)
        v_ax = e_a.velocity.vx - e_a.velocity.omega * r_ay
        v_ay = e_a.velocity.vy + e_a.velocity.omega * r_ax
        m_a_inv, i_a_inv = self._get_constraint_inv_mass_inertia(e_a)

        if e_b is not None:
            p_bx, p_by, r_bx, r_by = self._compute_anchor_world(e_b, constraint.anchor_b)
            v_bx = e_b.velocity.vx - e_b.velocity.omega * r_by
            v_by = e_b.velocity.vy + e_b.velocity.omega * r_bx
            m_b_inv, i_b_inv = self._get_constraint_inv_mass_inertia(e_b)
        else:
            p_bx, p_by, r_bx, r_by = constraint.anchor_b.x, constraint.anchor_b.y, 0.0, 0.0
            v_bx, v_by = 0.0, 0.0
            m_b_inv, i_b_inv = 0.0, 0.0

        dx = p_bx - p_ax
        dy = p_by - p_ay
        dist = math.hypot(dx, dy)
        if dist < 1e-9:
            ux, uy = 1.0, 0.0
        else:
            ux = dx / dist
            uy = dy / dist

        target_dist = constraint.length if constraint.length is not None else dist
        c_pos = dist - target_dist
        v_rel = (v_bx - v_ax) * ux + (v_by - v_ay) * uy

        rn_a = r_ax * uy - r_ay * ux
        rn_b = r_bx * uy - r_by * ux
        inv_mass_total = m_a_inv + m_b_inv + (rn_a * rn_a) * i_a_inv + (rn_b * rn_b) * i_b_inv
        if inv_mass_total <= 1e-12:
            return e_a, e_b

        beta = 0.25
        bias = (beta / max(dt, 1e-6)) * c_pos if dt > 0.0 else 0.0
        j = -(v_rel + bias) / inv_mass_total

        jx = j * ux
        jy = j * uy

        m_sum = m_a_inv + m_b_inv
        pos_corr = 0.9 * c_pos / m_sum if m_sum > 1e-12 else 0.0
        px_corr = pos_corr * ux
        py_corr = pos_corr * uy

        new_e_a = e_a
        if m_a_inv > 0.0 or i_a_inv > 0.0:
            new_vax = e_a.velocity.vx - m_a_inv * jx
            new_vay = e_a.velocity.vy - m_a_inv * jy
            new_w_a = e_a.velocity.omega - i_a_inv * (r_ax * jy - r_ay * jx)
            new_pos_ax = e_a.position.x + m_a_inv * px_corr
            new_pos_ay = e_a.position.y + m_a_inv * py_corr
            new_e_a = self._update_entity_kinematics(
                e_a, new_pos_ax, new_pos_ay, new_vax, new_vay, new_w_a, e_a.angle
            )

        new_e_b = e_b
        if e_b is not None and (m_b_inv > 0.0 or i_b_inv > 0.0):
            new_vbx = e_b.velocity.vx + m_b_inv * jx
            new_vby = e_b.velocity.vy + m_b_inv * jy
            new_w_b = e_b.velocity.omega + i_b_inv * (r_bx * jy - r_by * jx)
            new_pos_bx = e_b.position.x - m_b_inv * px_corr
            new_pos_by = e_b.position.y - m_b_inv * py_corr
            new_e_b = self._update_entity_kinematics(
                e_b, new_pos_bx, new_pos_by, new_vbx, new_vby, new_w_b, e_b.angle
            )

        return new_e_a, new_e_b

    def _solve_pin_constraint(
        self,
        e_a: Entity,
        e_b: Optional[Entity],
        constraint: Constraint,
        dt: float,
    ) -> Tuple[Entity, Optional[Entity]]:
        """Applies 2D point-to-point constraint locking anchor A to anchor B."""
        p_ax, p_ay, r_ax, r_ay = self._compute_anchor_world(e_a, constraint.anchor_a)
        v_ax = e_a.velocity.vx - e_a.velocity.omega * r_ay
        v_ay = e_a.velocity.vy + e_a.velocity.omega * r_ax
        m_a_inv, i_a_inv = self._get_constraint_inv_mass_inertia(e_a)

        if e_b is not None:
            p_bx, p_by, r_bx, r_by = self._compute_anchor_world(e_b, constraint.anchor_b)
            v_bx = e_b.velocity.vx - e_b.velocity.omega * r_by
            v_by = e_b.velocity.vy + e_b.velocity.omega * r_bx
            m_b_inv, i_b_inv = self._get_constraint_inv_mass_inertia(e_b)
        else:
            p_bx, p_by, r_bx, r_by = constraint.anchor_b.x, constraint.anchor_b.y, 0.0, 0.0
            v_bx, v_by = 0.0, 0.0
            m_b_inv, i_b_inv = 0.0, 0.0

        cx = p_bx - p_ax
        cy = p_by - p_ay
        vrx = v_bx - v_ax
        vry = v_by - v_ay

        k_xx = m_a_inv + m_b_inv + r_ay * r_ay * i_a_inv + r_by * r_by * i_b_inv
        k_xy = -r_ax * r_ay * i_a_inv - r_bx * r_by * i_b_inv
        k_yy = m_a_inv + m_b_inv + r_ax * r_ax * i_a_inv + r_bx * r_bx * i_b_inv

        det = k_xx * k_yy - k_xy * k_xy
        if det <= 1e-12:
            return e_a, e_b

        beta = 0.25
        inv_dt = (beta / max(dt, 1e-6)) if dt > 0.0 else 0.0
        bx = -(vrx + inv_dt * cx)
        by = -(vry + inv_dt * cy)

        jx = (k_yy * bx - k_xy * by) / det
        jy = (-k_xy * bx + k_xx * by) / det

        m_sum = m_a_inv + m_b_inv
        pos_corr = 0.9 if m_sum > 1e-12 else 0.0
        px_corr = (pos_corr * cx) / m_sum if m_sum > 1e-12 else 0.0
        py_corr = (pos_corr * cy) / m_sum if m_sum > 1e-12 else 0.0

        new_e_a = e_a
        if m_a_inv > 0.0 or i_a_inv > 0.0:
            new_vax = e_a.velocity.vx - m_a_inv * jx
            new_vay = e_a.velocity.vy - m_a_inv * jy
            new_w_a = e_a.velocity.omega - i_a_inv * (r_ax * jy - r_ay * jx)
            new_pos_ax = e_a.position.x + m_a_inv * px_corr
            new_pos_ay = e_a.position.y + m_a_inv * py_corr
            new_e_a = self._update_entity_kinematics(
                e_a, new_pos_ax, new_pos_ay, new_vax, new_vay, new_w_a, e_a.angle
            )

        new_e_b = e_b
        if e_b is not None and (m_b_inv > 0.0 or i_b_inv > 0.0):
            new_vbx = e_b.velocity.vx + m_b_inv * jx
            new_vby = e_b.velocity.vy + m_b_inv * jy
            new_w_b = e_b.velocity.omega + i_b_inv * (r_bx * jy - r_by * jx)
            new_pos_bx = e_b.position.x - m_b_inv * px_corr
            new_pos_by = e_b.position.y - m_b_inv * py_corr
            new_e_b = self._update_entity_kinematics(
                e_b, new_pos_bx, new_pos_by, new_vbx, new_vby, new_w_b, e_b.angle
            )

        return new_e_a, new_e_b

    def _resolve_constraints(
        self, entities: List[Entity], constraints: List[Constraint], dt: float
    ) -> List[Entity]:
        """Resolves all active constraints over entities."""
        if not constraints or dt <= 0.0:
            return entities

        id_to_idx = {e.id: idx for idx, e in enumerate(entities)}
        iterations = 2
        for _ in range(iterations):
            for c in constraints:
                idx_a = id_to_idx.get(c.entity_a)
                if idx_a is None:
                    continue
                e_a = entities[idx_a]
                if not e_a.active:
                    continue

                idx_b = id_to_idx.get(c.entity_b) if c.entity_b is not None else None
                e_b = entities[idx_b] if idx_b is not None else None
                if e_b is not None and not e_b.active:
                    continue

                if c.type == "spring":
                    res_a, res_b = self._solve_spring_constraint(e_a, e_b, c, dt / iterations)
                elif c.type == "distance":
                    res_a, res_b = self._solve_distance_constraint(e_a, e_b, c, dt)
                elif c.type == "pin":
                    res_a, res_b = self._solve_pin_constraint(e_a, e_b, c, dt)
                else:
                    continue

                entities[idx_a] = res_a
                if idx_b is not None and res_b is not None:
                    entities[idx_b] = res_b

        return entities

    def is_quiescent(self, state: SimulationState, vel_tol: float = 1e-5) -> bool:
        """Determines if the simulation state is physically at rest and eligible for host CPU sleep."""
        for e in state.entities:
            if not e.active:
                continue
            v = e.velocity
            if abs(v.vx) > vel_tol or abs(v.vy) > vel_tol or abs(v.omega) > vel_tol:
                return False
        return True

    def step(
        self,
        state: SimulationState,
        dt: float,
        inputs: Optional[Dict[str, float]] = None,
    ) -> SimulationState:
        """Advances simulation by time step dt >= 0 deterministically."""
        if dt < 0:
            raise ValueError(f"Time step dt must be non-negative (got {dt}).")

        env = state.environment
        input_map = inputs or {}
        state_variables = self._clone_state_variables(state.state_variables)

        # Dual-mode execution fast path: dt == 0.0 processes events without advancing physical time
        if dt == 0.0:
            moved_entities = list(state.entities)
            new_pointer, pointer_events = self._process_pointer_input(state, input_map, moved_entities, env)

            step_reward = 0.0
            terminated = state.terminated
            truncated = state.truncated

            entity_map: Dict[str, int] = {e.id: idx for idx, e in enumerate(moved_entities)}
            for rule in state.rules:
                if self._is_rule_triggered(
                    rule, set(), pointer_events, moved_entities, entity_map, state_variables
                ):
                    r, term, trunc = self._execute_rule_actions(rule.actions, moved_entities, entity_map, state_variables)
                    step_reward += r
                    if term:
                        terminated = True
                    if trunc:
                        truncated = True

            new_shapes = self._compute_shapes(env, moved_entities, state_variables)
            new_result = EvaluationResult(
                width=env.width,
                height=env.height,
                background=env.background,
                shapes=new_shapes,
            )

            return SimulationState(
                time=state.time,
                environment=env,
                entities=moved_entities,
                result=new_result,
                state_variables=state_variables,
                rules=state.rules,
                step_reward=step_reward,
                terminated=terminated,
                truncated=truncated,
                pointer=new_pointer,
                constraints=state.constraints,
            )

        # 1. Integrate motion & environment boundary constraints
        moved_entities = [
            self._integrate_entity_motion(e, dt, input_map, env)
            for e in state.entities
        ]

        # 2. Resolve interactive mechanical constraints (Distance, Spring, Pin)
        moved_entities = self._resolve_constraints(moved_entities, state.constraints, dt)

        # 3. Resolve pairwise solid collisions
        moved_entities, collision_events = self._resolve_pairwise_collisions(moved_entities, env)

        # 4. Process pointer inputs & lifecycle transitions
        new_pointer, pointer_events = self._process_pointer_input(state, input_map, moved_entities, env)

        step_reward = 0.0
        terminated = state.terminated
        truncated = state.truncated

        # 5. Evaluate declarative rules and execute actions
        entity_map: Dict[str, int] = {e.id: idx for idx, e in enumerate(moved_entities)}
        for rule in state.rules:
            if self._is_rule_triggered(
                rule, collision_events, pointer_events, moved_entities, entity_map, state_variables
            ):
                r, term, trunc = self._execute_rule_actions(rule.actions, moved_entities, entity_map, state_variables)
                step_reward += r
                if term:
                    terminated = True
                if trunc:
                    truncated = True

        # 6. Compute concrete shape coordinates for active entities
        new_shapes = self._compute_shapes(env, moved_entities, state_variables)
        new_result = EvaluationResult(
            width=env.width,
            height=env.height,
            background=env.background,
            shapes=new_shapes,
        )

        return SimulationState(
            time=state.time + dt,
            environment=env,
            entities=moved_entities,
            result=new_result,
            state_variables=state_variables,
            rules=state.rules,
            step_reward=step_reward,
            terminated=terminated,
            truncated=truncated,
            pointer=new_pointer,
            constraints=state.constraints,
        )


