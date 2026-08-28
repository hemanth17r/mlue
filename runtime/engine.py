"""MLUE Phase 0.6 Core Engine

Deterministic computational engine evaluating spatial geometry, multi-entity composition,
external input signals, linear velocity time-integration (dt), environment boundary constraints,
pairwise relational collisions, collision-based event triggers, entity lifecycle management,
property mutations, and state variable conditions.
Completely decoupled from any rendering or platform display subsystem.
"""

import math
from typing import List, Tuple, Dict, Any, Optional, Set, FrozenSet
from .model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    CircleSize,
    BoxSize,
    Velocity,
    EvaluationResult,
    ComputedShape,
    SimulationState,
    Rule,
    Condition,
    Action,
)


class MLUEEngine:
    """Deterministic computational engine for evaluating MLUE representations and simulations."""

    def _compute_shapes(self, env: Environment, entities: List[Entity]) -> List[ComputedShape]:
        """Resolves normalized entity coordinates and sizes into concrete screen-space geometry."""
        w = env.width
        h = env.height
        min_dim = min(w, h)

        computed_shapes: List[ComputedShape] = []

        for entity in entities:
            if not entity.active:
                continue

            color = entity.properties.get("color", "#FFFFFF")
            cx = entity.position.x * w
            cy = entity.position.y * h

            if entity.type == "circle" and isinstance(entity.size, CircleSize):
                r = entity.size.radius * min_dim
                bbox = (cx - r, cy - r, cx + r, cy + r)
            elif entity.type == "box" and isinstance(entity.size, BoxSize):
                hw = (entity.size.width / 2.0) * w
                hh = (entity.size.height / 2.0) * h
                bbox = (cx - hw, cy - hh, cx + hw, cy + hh)
            else:
                continue

            shape = ComputedShape(
                id=entity.id,
                type=entity.type,
                bbox=bbox,
                center=(cx, cy),
                color=color,
            )
            computed_shapes.append(shape)

        return computed_shapes

    def evaluate(self, doc: MLUEDocument) -> EvaluationResult:
        """Evaluates an MLUEDocument into resolved computational entity states (instantaneous snapshot)."""
        shapes = self._compute_shapes(doc.environment, doc.entities)
        return EvaluationResult(
            width=doc.environment.width,
            height=doc.environment.height,
            background=doc.environment.background,
            shapes=shapes,
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
        )

    def _get_entity_extents(self, entity: Entity, env: Environment) -> Tuple[float, float]:
        """Returns normalized half-extents (ex, ey) for an entity."""
        w = env.width
        h = env.height
        min_dim = min(w, h)

        if entity.type == "circle" and isinstance(entity.size, CircleSize):
            r = entity.size.radius
            ex = r * (min_dim / w)
            ey = r * (min_dim / h)
            return ex, ey
        elif entity.type == "box" and isinstance(entity.size, BoxSize):
            return entity.size.width / 2.0, entity.size.height / 2.0
        return 0.0, 0.0

    def _resolve_circle_box_collision(
        self, circle: Entity, box: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between a Circle and a Box."""
        cx = circle.position.x
        cy = circle.position.y
        rx, ry = self._get_entity_extents(circle, env)

        bx = box.position.x
        by = box.position.y
        hw, hh = self._get_entity_extents(box, env)

        # Clamped closest point on Box
        px = max(bx - hw, min(cx, bx + hw))
        py = max(by - hh, min(cy, by + hh))

        dx = cx - px
        dy = cy - py

        # Normalized distance squared
        norm_dist_sq = (dx / rx) ** 2 + (dy / ry) ** 2 if (rx > 0 and ry > 0) else 0.0

        if norm_dist_sq < 1.0 or (dx == 0.0 and dy == 0.0):
            # Collision detected. Compute contact normal
            if dx == 0.0 and dy == 0.0:
                dist_left = cx - (bx - hw)
                dist_right = (bx + hw) - cx
                dist_top = cy - (by - hh)
                dist_bottom = (by + hh) - cy
                min_d = min(dist_left, dist_right, dist_top, dist_bottom)

                if min_d == dist_left:
                    nx, ny = -1.0, 0.0
                    new_cx = bx - hw - rx
                    new_cy = cy
                elif min_d == dist_right:
                    nx, ny = 1.0, 0.0
                    new_cx = bx + hw + rx
                    new_cy = cy
                elif min_d == dist_top:
                    nx, ny = 0.0, -1.0
                    new_cx = cx
                    new_cy = by - hh - ry
                else:
                    nx, ny = 0.0, 1.0
                    new_cx = cx
                    new_cy = by + hh + ry
            else:
                dist = math.hypot(dx, dy)
                nx = dx / dist
                ny = dy / dist
                new_cx = px + nx * rx
                new_cy = py + ny * ry

            # Reflect circle relative velocity
            rel_vx = circle.velocity.vx - box.velocity.vx
            rel_vy = circle.velocity.vy - box.velocity.vy
            v_dot = rel_vx * nx + rel_vy * ny

            new_cvx = circle.velocity.vx
            new_cvy = circle.velocity.vy

            if v_dot < 0.0:
                new_cvx = circle.velocity.vx - 2.0 * v_dot * nx
                new_cvy = circle.velocity.vy - 2.0 * v_dot * ny

            updated_circle = Entity(
                id=circle.id,
                type=circle.type,
                position=Position(x=new_cx, y=new_cy),
                size=circle.size,
                velocity=Velocity(vx=new_cvx, vy=new_cvy),
                properties=circle.properties,
                active=circle.active,
            )
            return updated_circle, box, True

        return circle, box, False

    def _resolve_circle_circle_collision(
        self, c1: Entity, c2: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between two Circles."""
        r1x, _ = self._get_entity_extents(c1, env)
        r2x, _ = self._get_entity_extents(c2, env)
        target_dist = r1x + r2x

        dx = c1.position.x - c2.position.x
        dy = c1.position.y - c2.position.y
        dist = math.hypot(dx, dy)

        if dist < target_dist and dist > 0.0:
            nx = dx / dist
            ny = dy / dist

            overlap = target_dist - dist
            new_c1x = c1.position.x + nx * (overlap / 2.0)
            new_c1y = c1.position.y + ny * (overlap / 2.0)
            new_c2x = c2.position.x - nx * (overlap / 2.0)
            new_c2y = c2.position.y - ny * (overlap / 2.0)

            rel_vx = c1.velocity.vx - c2.velocity.vx
            rel_vy = c1.velocity.vy - c2.velocity.vy
            v_dot = rel_vx * nx + rel_vy * ny

            new_v1x, new_v1y = c1.velocity.vx, c1.velocity.vy
            new_v2x, new_v2y = c2.velocity.vx, c2.velocity.vy

            if v_dot < 0.0:
                new_v1x -= v_dot * nx
                new_v1y -= v_dot * ny
                new_v2x += v_dot * nx
                new_v2y += v_dot * ny

            u1 = Entity(
                id=c1.id,
                type=c1.type,
                position=Position(x=new_c1x, y=new_c1y),
                size=c1.size,
                velocity=Velocity(vx=new_v1x, vy=new_v1y),
                properties=c1.properties,
                active=c1.active,
            )
            u2 = Entity(
                id=c2.id,
                type=c2.type,
                position=Position(x=new_c2x, y=new_c2y),
                size=c2.size,
                velocity=Velocity(vx=new_v2x, vy=new_v2y),
                properties=c2.properties,
                active=c2.active,
            )
            return u1, u2, True

        return c1, c2, False

    def _resolve_box_box_collision(
        self, b1: Entity, b2: Entity, env: Environment
    ) -> Tuple[Entity, Entity, bool]:
        """Resolves pairwise collision between two Boxes."""
        hw1, hh1 = self._get_entity_extents(b1, env)
        hw2, hh2 = self._get_entity_extents(b2, env)

        dx = b1.position.x - b2.position.x
        dy = b1.position.y - b2.position.y

        overlap_x = (hw1 + hw2) - abs(dx)
        overlap_y = (hh1 + hh2) - abs(dy)

        if overlap_x > 0.0 and overlap_y > 0.0:
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

            rel_vx = b1.velocity.vx - b2.velocity.vx
            rel_vy = b1.velocity.vy - b2.velocity.vy
            v_dot = rel_vx * nx + rel_vy * ny

            new_v1x, new_v1y = b1.velocity.vx, b1.velocity.vy
            new_v2x, new_v2y = b2.velocity.vx, b2.velocity.vy

            if v_dot < 0.0:
                new_v1x -= v_dot * nx
                new_v1y -= v_dot * ny
                new_v2x += v_dot * nx
                new_v2y += v_dot * ny

            u1 = Entity(
                id=b1.id,
                type=b1.type,
                position=Position(x=new_b1x, y=new_b1y),
                size=b1.size,
                velocity=Velocity(vx=new_v1x, vy=new_v1y),
                properties=b1.properties,
                active=b1.active,
            )
            u2 = Entity(
                id=b2.id,
                type=b2.type,
                position=Position(x=new_b2x, y=new_b2y),
                size=b2.size,
                velocity=Velocity(vx=new_v2x, vy=new_v2y),
                properties=b2.properties,
                active=b2.active,
            )
            return u1, u2, True

        return b1, b2, False

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
        return 0.0

    def _integrate_entity_motion(
        self,
        entity: Entity,
        dt: float,
        input_map: Dict[str, float],
        env: Environment,
    ) -> Entity:
        """Applies input control modulation, time integration, and boundary constraints to a single entity."""
        if not entity.active:
            return entity

        ex, ey = self._get_entity_extents(entity, env)
        x, y = entity.position.x, entity.position.y
        vx, vy = entity.velocity.vx, entity.velocity.vy
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
            else:
                if axis == "y":
                    vy = 0.0
                elif axis == "x":
                    vx = 0.0

        new_x = x + vx * dt
        new_y = y + vy * dt
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
                    new_vx = -new_vx
            elif new_x + ex >= 1.0:
                new_x = 1.0 - ex
                if new_vx > 0.0:
                    new_vx = -new_vx

            if new_y - ey <= 0.0:
                new_y = ey
                if new_vy < 0.0:
                    new_vy = -new_vy
            elif new_y + ey >= 1.0:
                new_y = 1.0 - ey
                if new_vy > 0.0:
                    new_vy = -new_vy

        return Entity(
            id=entity.id,
            type=entity.type,
            position=Position(x=new_x, y=new_y),
            size=entity.size,
            velocity=Velocity(vx=new_vx, vy=new_vy),
            properties=dict(entity.properties),
            active=entity.active,
        )

    def _resolve_pairwise_collisions(
        self, entities: List[Entity], env: Environment
    ) -> Tuple[List[Entity], Set[FrozenSet[str]]]:
        """Resolves pairwise relational collisions between active solid entities and records collision events."""
        collision_events: Set[FrozenSet[str]] = set()
        n = len(entities)

        for i in range(n):
            for j in range(i + 1, n):
                e1 = entities[i]
                e2 = entities[j]
                if not (e1.active and e2.active):
                    continue

                if e1.properties.get("solid", False) and e2.properties.get("solid", False):
                    has_collided = False
                    if e1.type == "circle" and e2.type == "box":
                        e1_res, e2_res, has_collided = self._resolve_circle_box_collision(e1, e2, env)
                        entities[i], entities[j] = e1_res, e2_res
                    elif e1.type == "box" and e2.type == "circle":
                        e2_res, e1_res, has_collided = self._resolve_circle_box_collision(e2, e1, env)
                        entities[i], entities[j] = e1_res, e2_res
                    elif e1.type == "circle" and e2.type == "circle":
                        e1_res, e2_res, has_collided = self._resolve_circle_circle_collision(e1, e2, env)
                        entities[i], entities[j] = e1_res, e2_res
                    elif e1.type == "box" and e2.type == "box":
                        e1_res, e2_res, has_collided = self._resolve_box_box_collision(e1, e2, env)
                        entities[i], entities[j] = e1_res, e2_res

                    if has_collided:
                        collision_events.add(frozenset([e1.id, e2.id]))

        return entities, collision_events

    def _evaluate_rule_condition(
        self,
        cond: Condition,
        entities: List[Entity],
        entity_map: Dict[str, int],
        state_variables: Dict[str, Any],
    ) -> bool:
        """Evaluates whether a single rule condition is satisfied."""
        if cond.state_variable is not None:
            actual_val = state_variables.get(cond.state_variable, 0)
            threshold = cond.value
            if cond.op == "<=": return actual_val <= threshold
            if cond.op == ">=": return actual_val >= threshold
            if cond.op == "<":  return actual_val < threshold
            if cond.op == ">":  return actual_val > threshold
            if cond.op == "==": return actual_val == threshold

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

        return False

    def _execute_rule_actions(
        self,
        actions: List[Action],
        entities: List[Entity],
        entity_map: Dict[str, int],
        state_variables: Dict[str, Any],
    ) -> None:
        """Executes a list of state mutation actions."""
        for action in actions:
            if action.type in ("destroy_entity", "deactivate_entity"):
                t_idx = entity_map.get(action.target)
                if t_idx is not None:
                    curr = entities[t_idx]
                    entities[t_idx] = Entity(
                        id=curr.id, type=curr.type, position=curr.position,
                        size=curr.size, velocity=curr.velocity, properties=curr.properties,
                        active=False,
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
                    )
            elif action.type == "increment" and action.target in state_variables:
                amt = action.amount if action.amount is not None else 1.0
                state_variables[action.target] = state_variables[action.target] + amt
            elif action.type == "set" and action.target in state_variables:
                state_variables[action.target] = action.value
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
                    )

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
        state_variables = dict(state.state_variables)

        # 1. Integrate motion & environment boundary constraints
        moved_entities = [
            self._integrate_entity_motion(e, dt, input_map, env)
            for e in state.entities
        ]

        # 2. Resolve pairwise solid collisions
        moved_entities, collision_events = self._resolve_pairwise_collisions(moved_entities, env)

        # 3. Evaluate declarative rules and execute actions
        entity_map: Dict[str, int] = {e.id: idx for idx, e in enumerate(moved_entities)}
        for rule in state.rules:
            is_triggered = False
            if rule.event == "collision" and rule.entities:
                is_triggered = frozenset(rule.entities) in collision_events
            elif rule.condition is not None:
                is_triggered = self._evaluate_rule_condition(
                    rule.condition, moved_entities, entity_map, state_variables
                )

            if is_triggered:
                self._execute_rule_actions(rule.actions, moved_entities, entity_map, state_variables)

        # 4. Compute concrete shape coordinates for active entities
        new_shapes = self._compute_shapes(env, moved_entities)
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
        )

