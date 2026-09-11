"""MLUE 2D Spatial Indexing & Broadphase Acceleration Core.

Provides high-performance 2D Axis-Aligned Bounding Box (AABB) math,
Dynamic Uniform Spatial Hash Grid, and Bounding Volume Hierarchy (BVH).
Adheres strictly to Tier L1 Substrate Decoupling (Standard Library only: math, dataclasses, typing, collections).
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set, Union
from collections import defaultdict
from runtime.model import Entity, CircleSize, BoxSize, SegmentSize, CapsuleSize, TextSize, Environment


@dataclass(slots=True)
class AABB2D:
    """Represents a 2D Axis-Aligned Bounding Box in continuous normalized coordinates [0.0, 1.0]^2."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def intersects(self, other: "AABB2D") -> bool:
        """Evaluates whether two AABBs overlap (including edge contact)."""
        return not (
            self.max_x < other.min_x
            or self.min_x > other.max_x
            or self.max_y < other.min_y
            or self.min_y > other.max_y
        )

    def contains_point(self, x: float, y: float) -> bool:
        """Returns True if point (x, y) lies inside or on the boundary of this AABB."""
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y

    def union(self, other: "AABB2D") -> "AABB2D":
        """Returns the minimal enclosing AABB covering both this and other."""
        return AABB2D(
            min_x=min(self.min_x, other.min_x),
            min_y=min(self.min_y, other.min_y),
            max_x=max(self.max_x, other.max_x),
            max_y=max(self.max_y, other.max_y),
        )

    def area(self) -> float:
        """Returns the 2D surface area of this bounding box."""
        return max(0.0, self.max_x - self.min_x) * max(0.0, self.max_y - self.min_y)


def compute_entity_aabb(entity: Entity, env: Environment) -> AABB2D:
    """Computes exact normalized AABB for an entity in the given environment viewport."""
    w = env.width
    h = env.height
    min_dim = min(w, h)

    px, py = entity.position.x, entity.position.y
    if entity.type == "circle" and isinstance(entity.size, CircleSize):
        r = entity.size.radius
        ex = r * (min_dim / w)
        ey = r * (min_dim / h)
        return AABB2D(min_x=px - ex, min_y=py - ey, max_x=px + ex, max_y=py + ey)
    elif entity.type == "box" and isinstance(entity.size, BoxSize):
        ex = entity.size.width / 2.0
        ey = entity.size.height / 2.0
        return AABB2D(min_x=px - ex, min_y=py - ey, max_x=px + ex, max_y=py + ey)
    elif entity.type == "segment" and isinstance(entity.size, SegmentSize):
        x1, y1 = px, py
        x2, y2 = entity.size.end_x, entity.size.end_y
        th_x = (entity.size.thickness / 2.0) * (min_dim / w)
        th_y = (entity.size.thickness / 2.0) * (min_dim / h)
        return AABB2D(
            min_x=min(x1, x2) - th_x,
            min_y=min(y1, y2) - th_y,
            max_x=max(x1, x2) + th_x,
            max_y=max(y1, y2) + th_y,
        )
    elif entity.type == "capsule" and isinstance(entity.size, CapsuleSize):
        r = entity.size.radius
        rx = r * (min_dim / w)
        ry = r * (min_dim / h)
        hl = entity.size.length / 2.0
        dx = hl * math.cos(entity.size.angle)
        dy = hl * math.sin(entity.size.angle)
        return AABB2D(
            min_x=min(px - dx, px + dx) - rx,
            min_y=min(py - dy, py + dy) - ry,
            max_x=max(px - dx, px + dx) + rx,
            max_y=max(py - dy, py + dy) + ry,
        )
    else:
        return AABB2D(min_x=px, min_y=py, max_x=px, max_y=py)


class SpatialHashGrid2D:
    """Uniform Spatial Hash Grid broadphase accelerator with O(1) amortized insertion and O(N log N) / O(N) querying."""

    def __init__(self, cell_size: float = 0.05):
        self.cell_size = max(0.001, float(cell_size))
        self.inv_cell_size = 1.0 / self.cell_size
        self._grid: Dict[Tuple[int, int], List[int]] = defaultdict(list)
        self.entity_count = 0

    def clear(self) -> None:
        """Clears all grid cell bucket registrations."""
        self._grid.clear()
        self.entity_count = 0

    def insert(self, entity_idx: int, aabb: AABB2D) -> None:
        """Inserts an entity index into all intersecting grid cell buckets."""
        c_min_x = math.floor(aabb.min_x * self.inv_cell_size)
        c_max_x = math.floor(aabb.max_x * self.inv_cell_size)
        c_min_y = math.floor(aabb.min_y * self.inv_cell_size)
        c_max_y = math.floor(aabb.max_y * self.inv_cell_size)

        for cy in range(c_min_y, c_max_y + 1):
            for cx in range(c_min_x, c_max_x + 1):
                self._grid[(cx, cy)].append(entity_idx)

        self.entity_count += 1

    def build(
        self,
        entities: List[Entity],
        env: Environment,
        precomputed_aabbs: Optional[List[AABB2D]] = None,
    ) -> List[AABB2D]:
        """Builds spatial grid from entity list. Returns list of computed AABBs."""
        self.clear()
        aabbs: List[AABB2D] = []

        # Automatically adapt cell size if entity size distribution warrants it
        max_extent = 0.025
        for i, e in enumerate(entities):
            if not e.active:
                aabbs.append(AABB2D(0.0, 0.0, 0.0, 0.0))
                continue
            aabb = precomputed_aabbs[i] if precomputed_aabbs is not None else compute_entity_aabb(e, env)
            aabbs.append(aabb)
            ex = aabb.max_x - aabb.min_x
            ey = aabb.max_y - aabb.min_y
            if ex > max_extent:
                max_extent = ex
            if ey > max_extent:
                max_extent = ey

        # Optimal cell size is roughly 2x the maximum entity diameter
        adapted_cell_size = max(0.02, min(0.25, max_extent * 2.0))
        self.cell_size = adapted_cell_size
        self.inv_cell_size = 1.0 / self.cell_size

        for i, e in enumerate(entities):
            if e.active:
                self.insert(i, aabbs[i])

        return aabbs

    def get_candidate_pairs(self, aabbs: List[AABB2D]) -> List[Tuple[int, int]]:
        """Extracts broadphase candidate pairs with AABB overlap validation.
        
        Guarantees zero false negatives and deduplicated (i, j) pairs where i < j.
        """
        candidate_set: Set[Tuple[int, int]] = set()

        for cell_entities in self._grid.values():
            n = len(cell_entities)
            if n < 2:
                continue
            for i_idx in range(n):
                idx_a = cell_entities[i_idx]
                for j_idx in range(i_idx + 1, n):
                    idx_b = cell_entities[j_idx]
                    if idx_a == idx_b:
                        continue
                    pair = (idx_a, idx_b) if idx_a < idx_b else (idx_b, idx_a)
                    candidate_set.add(pair)

        # Broadphase AABB overlap filter
        valid_candidates: List[Tuple[int, int]] = []
        for i, j in candidate_set:
            if aabbs[i].intersects(aabbs[j]):
                valid_candidates.append((i, j))

        return valid_candidates

    def query_aabb(self, query_box: AABB2D, aabbs: List[AABB2D]) -> List[int]:
        """Queries all active entity indices overlapping query_box."""
        c_min_x = math.floor(query_box.min_x * self.inv_cell_size)
        c_max_x = math.floor(query_box.max_x * self.inv_cell_size)
        c_min_y = math.floor(query_box.min_y * self.inv_cell_size)
        c_max_y = math.floor(query_box.max_y * self.inv_cell_size)

        candidate_indices: Set[int] = set()
        for cy in range(c_min_y, c_max_y + 1):
            for cx in range(c_min_x, c_max_x + 1):
                for idx in self._grid.get((cx, cy), []):
                    candidate_indices.add(idx)

        return [idx for idx in candidate_indices if query_box.intersects(aabbs[idx])]


@dataclass
class BVHNode2D:
    """Node in dynamic Bounding Volume Hierarchy tree."""
    aabb: AABB2D
    left: Optional["BVHNode2D"] = None
    right: Optional["BVHNode2D"] = None
    entity_idx: Optional[int] = None

    @property
    def is_leaf(self) -> bool:
        return self.entity_idx is not None


class BVHTree2D:
    """Dynamic 2D Bounding Volume Hierarchy (BVH) for sparse and hierarchical spatial queries."""

    def __init__(self):
        self.root: Optional[BVHNode2D] = None

    def build(self, entities: List[Entity], env: Environment) -> None:
        """Constructs a balanced BVH tree using recursive spatial median splitting."""
        items: List[Tuple[int, AABB2D]] = [
            (i, compute_entity_aabb(e, env))
            for i, e in enumerate(entities)
            if e.active
        ]
        if not items:
            self.root = None
            return

        self.root = self._build_recursive(items, axis=0)

    def _build_recursive(self, items: List[Tuple[int, AABB2D]], axis: int) -> BVHNode2D:
        if len(items) == 1:
            idx, aabb = items[0]
            return BVHNode2D(aabb=aabb, entity_idx=idx)

        # Sort items along split axis (0: X-center, 1: Y-center)
        if axis == 0:
            items.sort(key=lambda item: (item[1].min_x + item[1].max_x) * 0.5)
        else:
            items.sort(key=lambda item: (item[1].min_y + item[1].max_y) * 0.5)

        mid = len(items) // 2
        left_child = self._build_recursive(items[:mid], 1 - axis)
        right_child = self._build_recursive(items[mid:], 1 - axis)

        combined_aabb = left_child.aabb.union(right_child.aabb)
        return BVHNode2D(aabb=combined_aabb, left=left_child, right=right_child)

    def query_aabb(self, query_box: AABB2D) -> List[int]:
        """Traverses BVH tree and returns all entity indices whose bounding box intersects query_box."""
        results: List[int] = []
        if self.root is None:
            return results

        stack = [self.root]
        while stack:
            node = stack.pop()
            if not node.aabb.intersects(query_box):
                continue
            if node.is_leaf:
                if node.entity_idx is not None:
                    results.append(node.entity_idx)
            else:
                if node.left:
                    stack.append(node.left)
                if node.right:
                    stack.append(node.right)

        return results


# =========================================================================
# ANALYTICAL 2D RAYCAST & LIDAR PERCEPTION SENSORS
# =========================================================================

@dataclass(slots=True)
class Ray2D:
    """Represents a 2D ray with origin (origin_x, origin_y), normalized direction, and max_range."""
    origin_x: float
    origin_y: float
    dir_x: float
    dir_y: float
    max_range: float = 1.0

    @classmethod
    def from_angle(cls, x: float, y: float, angle_rad: float, max_range: float = 1.0) -> "Ray2D":
        return cls(
            origin_x=x,
            origin_y=y,
            dir_x=math.cos(angle_rad),
            dir_y=math.sin(angle_rad),
            max_range=max_range,
        )

    def to_aabb(self) -> AABB2D:
        """Returns the minimal enclosing normalized AABB covering the ray trajectory."""
        end_x = self.origin_x + self.dir_x * self.max_range
        end_y = self.origin_y + self.dir_y * self.max_range
        return AABB2D(
            min_x=min(self.origin_x, end_x),
            min_y=min(self.origin_y, end_y),
            max_x=max(self.origin_x, end_x),
            max_y=max(self.origin_y, end_y),
        )


@dataclass(slots=True)
class RayHit:
    """Represents an analytical ray intersection result."""
    distance: float
    hit_x: float
    hit_y: float
    entity_id: Optional[str] = None
    normal_x: float = 0.0
    normal_y: float = 0.0
    hit: bool = True


def ray_intersect_circle_iso(
    ox: float, oy: float, dx: float, dy: float,
    cx: float, cy: float, radius: float, max_range: float
) -> Optional[Tuple[float, float, float]]:
    """Analytical ray vs circle in isotropic space. Returns (t, normal_x, normal_y) or None."""
    delta_x = ox - cx
    delta_y = oy - cy
    b = dx * delta_x + dy * delta_y
    c = delta_x * delta_x + delta_y * delta_y - radius * radius

    if c <= 0.0:
        # Ray origin is inside the circle
        norm = math.hypot(delta_x, delta_y)
        if norm > 1e-12:
            return 0.0, delta_x / norm, delta_y / norm
        return 0.0, -dx, -dy

    disc = b * b - c
    if disc < 0.0:
        return None

    sqrt_disc = math.sqrt(disc)
    t = -b - sqrt_disc
    if 0.0 <= t <= max_range:
        hit_x = ox + t * dx
        hit_y = oy + t * dy
        nx = (hit_x - cx) / radius
        ny = (hit_y - cy) / radius
        return t, nx, ny

    return None


def ray_intersect_box_iso(
    ox: float, oy: float, dx: float, dy: float,
    min_x: float, min_y: float, max_x: float, max_y: float, max_range: float
) -> Optional[Tuple[float, float, float]]:
    """Analytical ray vs AABB box via slab method in isotropic space. Returns (t, normal_x, normal_y) or None."""
    if abs(dx) < 1e-12:
        if ox < min_x or ox > max_x:
            return None
        tx1 = -float("inf")
        tx2 = float("inf")
        nx_enter = 0.0
    else:
        inv_dx = 1.0 / dx
        t_a = (min_x - ox) * inv_dx
        t_b = (max_x - ox) * inv_dx
        if t_a < t_b:
            tx1, tx2 = t_a, t_b
            nx_enter = -1.0
        else:
            tx1, tx2 = t_b, t_a
            nx_enter = 1.0

    if abs(dy) < 1e-12:
        if oy < min_y or oy > max_y:
            return None
        ty1 = -float("inf")
        ty2 = float("inf")
        ny_enter = 0.0
    else:
        inv_dy = 1.0 / dy
        t_c = (min_y - oy) * inv_dy
        t_d = (max_y - oy) * inv_dy
        if t_c < t_d:
            ty1, ty2 = t_c, t_d
            ny_enter = -1.0
        else:
            ty1, ty2 = t_d, t_c
            ny_enter = 1.0

    t_enter = max(tx1, ty1)
    t_exit = min(tx2, ty2)

    if t_enter > t_exit or t_exit < 0.0:
        return None

    if t_enter < 0.0:
        # Origin inside box
        return 0.0, 0.0, 0.0

    if t_enter <= max_range:
        if tx1 > ty1:
            nx, ny = nx_enter, 0.0
        else:
            nx, ny = 0.0, ny_enter
        return t_enter, nx, ny

    return None


def ray_intersect_segment_iso(
    ox: float, oy: float, dx: float, dy: float,
    ax: float, ay: float, bx: float, by: float,
    thickness: float, max_range: float
) -> Optional[Tuple[float, float, float]]:
    """Analytical ray vs thick segment in isotropic space. Returns (t, normal_x, normal_y) or None."""
    vx = bx - ax
    vy = by - ay
    cross = dx * vy - dy * vx

    # Thin line segment intersection first
    if abs(cross) > 1e-12:
        delta_x = ax - ox
        delta_y = ay - oy
        t = (delta_x * vy - delta_y * vx) / cross
        s = (delta_x * dy - delta_y * dx) / cross
        if 0.0 <= s <= 1.0 and 0.0 <= t <= max_range:
            seg_len = math.hypot(vx, vy)
            if seg_len > 1e-12:
                n1_x = -vy / seg_len
                n1_y = vx / seg_len
                # Orient normal against ray direction
                if dx * n1_x + dy * n1_y > 0.0:
                    return t, -n1_x, -n1_y
                return t, n1_x, n1_y
            return t, -dx, -dy

    # If thickness > 0, check caps at endpoints A and B
    radius = thickness / 2.0
    if radius > 1e-6:
        hit_a = ray_intersect_circle_iso(ox, oy, dx, dy, ax, ay, radius, max_range)
        hit_b = ray_intersect_circle_iso(ox, oy, dx, dy, bx, by, radius, max_range)
        if hit_a and hit_b:
            return hit_a if hit_a[0] < hit_b[0] else hit_b
        return hit_a or hit_b

    return None


def ray_intersect_capsule_iso(
    ox: float, oy: float, dx: float, dy: float,
    cx: float, cy: float, radius: float, length: float, angle: float, max_range: float
) -> Optional[Tuple[float, float, float]]:
    """Analytical ray vs capsule in isotropic space. Returns (t, normal_x, normal_y) or None."""
    hl = length / 2.0
    dx_h = hl * math.cos(angle)
    dy_h = hl * math.sin(angle)
    p1x, p1y = cx - dx_h, cy - dy_h
    p2x, p2y = cx + dx_h, cy + dy_h

    # Check two circle caps
    best_hit = None
    hit1 = ray_intersect_circle_iso(ox, oy, dx, dy, p1x, p1y, radius, max_range)
    if hit1:
        best_hit = hit1

    hit2 = ray_intersect_circle_iso(ox, oy, dx, dy, p2x, p2y, radius, max_range)
    if hit2 and (best_hit is None or hit2[0] < best_hit[0]):
        best_hit = hit2

    # Check two lateral side boundaries
    nx_cap = -math.sin(angle) * radius
    ny_cap = math.cos(angle) * radius

    side1 = ray_intersect_segment_iso(
        ox, oy, dx, dy,
        p1x + nx_cap, p1y + ny_cap, p2x + nx_cap, p2y + ny_cap,
        0.0, max_range
    )
    if side1 and (best_hit is None or side1[0] < best_hit[0]):
        best_hit = side1

    side2 = ray_intersect_segment_iso(
        ox, oy, dx, dy,
        p1x - nx_cap, p1y - ny_cap, p2x - nx_cap, p2y - ny_cap,
        0.0, max_range
    )
    if side2 and (best_hit is None or side2[0] < best_hit[0]):
        best_hit = side2

    return best_hit


def cast_ray_scene(
    entities: List[Entity],
    env: Environment,
    ray: Ray2D,
    ignore_ids: Optional[Set[str]] = None,
) -> RayHit:
    """Casts an analytical ray across the scene, checking geometry and viewport boundaries."""
    w = float(env.width)
    h = float(env.height)
    min_dim = min(w, h)
    scale_x = w / min_dim
    scale_y = h / min_dim

    # Ray in isotropic coordinates
    ox = ray.origin_x * scale_x
    oy = ray.origin_y * scale_y
    dx = ray.dir_x
    dy = ray.dir_y
    max_range = ray.max_range

    best_t = max_range
    best_entity_id = None
    best_normal = (0.0, 0.0)

    # 1. Check viewport boundary walls
    t_bx = (scale_x - ox) / dx if dx > 1e-12 else (-ox / dx if dx < -1e-12 else float("inf"))
    t_by = (scale_y - oy) / dy if dy > 1e-12 else (-oy / dy if dy < -1e-12 else float("inf"))
    t_bound = min(t_bx, t_by)
    if 0.0 <= t_bound < best_t:
        best_t = t_bound
        best_entity_id = "boundary"
        if t_bx < t_by:
            best_normal = (-1.0 if dx > 0 else 1.0, 0.0)
        else:
            best_normal = (0.0, -1.0 if dy > 0 else 1.0)

    # 2. Check active entities
    ignored = ignore_ids or set()
    ray_aabb = ray.to_aabb()

    for entity in entities:
        if not entity.active or entity.id in ignored:
            continue

        # Fast AABB broadphase culling
        ent_aabb = compute_entity_aabb(entity, env)
        if not ray_aabb.intersects(ent_aabb):
            continue

        hit_res = None
        if entity.type == "circle" and isinstance(entity.size, CircleSize):
            cx = entity.position.x * scale_x
            cy = entity.position.y * scale_y
            hit_res = ray_intersect_circle_iso(ox, oy, dx, dy, cx, cy, entity.size.radius, best_t)
        elif entity.type == "box" and isinstance(entity.size, BoxSize):
            hw = (entity.size.width / 2.0) * scale_x
            hh = (entity.size.height / 2.0) * scale_y
            bx = entity.position.x * scale_x
            by = entity.position.y * scale_y
            hit_res = ray_intersect_box_iso(ox, oy, dx, dy, bx - hw, by - hh, bx + hw, by + hh, best_t)
        elif entity.type == "segment" and isinstance(entity.size, SegmentSize):
            ax = entity.position.x * scale_x
            ay = entity.position.y * scale_y
            bx = entity.size.end_x * scale_x
            by = entity.size.end_y * scale_y
            hit_res = ray_intersect_segment_iso(ox, oy, dx, dy, ax, ay, bx, by, entity.size.thickness, best_t)
        elif entity.type == "capsule" and isinstance(entity.size, CapsuleSize):
            cx = entity.position.x * scale_x
            cy = entity.position.y * scale_y
            hit_res = ray_intersect_capsule_iso(
                ox, oy, dx, dy, cx, cy, entity.size.radius, entity.size.length, entity.size.angle, best_t
            )

        if hit_res is not None and hit_res[0] < best_t:
            best_t, best_normal = hit_res[0], (hit_res[1], hit_res[2])
            best_entity_id = entity.id

    hit_px = (ox + best_t * dx) / scale_x
    hit_py = (oy + best_t * dy) / scale_y

    return RayHit(
        distance=best_t,
        hit_x=max(0.0, min(1.0, hit_px)),
        hit_y=max(0.0, min(1.0, hit_py)),
        entity_id=best_entity_id,
        normal_x=best_normal[0],
        normal_y=best_normal[1],
        hit=best_entity_id is not None,
    )

