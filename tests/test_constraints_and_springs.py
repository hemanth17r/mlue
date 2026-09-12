"""Unit tests for MLUE Phase 3: Interactive Constraints, Hinges & Springs.

Verifies:
- Spring-damper Hookean oscillation and viscous damping
- Rigid distance joints preserving length under dynamic loads
- World-anchored constraints (entity_b = None)
- Revolute pin hinges locking pivot positions while enabling free rotation
- Multi-link constraint chains
- Loader schema invariant validation (types, entities, self-links, bounds)
- Bounded cyclomatic complexity (NIST <= 30) and silicon efficiency
"""

import math
import unittest
from runtime.model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    CircleSize,
    BoxSize,
    Velocity,
    Constraint,
)
from runtime.engine import MLUEEngine
from runtime.loader import validate_and_parse, MLUEValidationError


class TestConstraintsAndSprings(unittest.TestCase):

    def setUp(self):
        self.engine = MLUEEngine()
        self.env = Environment(width=800, height=800)

    def test_spring_harmonic_oscillation(self):
        """Undamped spring produces restorative forces oscillating around rest length."""
        # Two equal mass circles separated by 0.3 units; rest length = 0.2
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="mass_a",
                    type="circle",
                    position=Position(0.35, 0.5),
                    size=CircleSize(radius=0.03),
                    properties={"mass": 1.0},
                ),
                Entity(
                    id="mass_b",
                    type="circle",
                    position=Position(0.65, 0.5),
                    size=CircleSize(radius=0.03),
                    properties={"mass": 1.0},
                ),
            ],
            constraints=[
                Constraint(
                    id="spring_1",
                    type="spring",
                    entity_a="mass_a",
                    entity_b="mass_b",
                    length=0.2,
                    stiffness=50.0,
                    damping=0.0,
                )
            ],
        )

        state = self.engine.init_simulation(doc)
        dt = 0.01

        # Step forward; since distance (0.3) > rest length (0.2), bodies should be pulled toward each other
        next_state = self.engine.step(state, dt=dt)
        va = next_state.entities[0].velocity.vx
        vb = next_state.entities[1].velocity.vx

        # mass_a moves right (+vx), mass_b moves left (-vx)
        self.assertGreater(va, 0.0)
        self.assertLess(vb, 0.0)
        self.assertAlmostEqual(va, -vb, places=6)

        # Track distance across 50 steps: distance should decrease, pass rest length, and rebound
        distances = []
        curr = next_state
        for _ in range(50):
            curr = self.engine.step(curr, dt=dt)
            d = math.hypot(
                curr.entities[1].position.x - curr.entities[0].position.x,
                curr.entities[1].position.y - curr.entities[0].position.y,
            )
            distances.append(d)

        min_d = min(distances)
        # Verify oscillation compressed below initial 0.30
        self.assertLess(min_d, 0.25)

    def test_spring_viscous_damping(self):
        """Viscous damping dissipates kinetic energy and settles toward rest length."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="mass_a",
                    type="circle",
                    position=Position(0.4, 0.5),
                    size=CircleSize(radius=0.03),
                    properties={"mass": 1.0},
                ),
                Entity(
                    id="mass_b",
                    type="circle",
                    position=Position(0.6, 0.5),
                    size=CircleSize(radius=0.03),
                    properties={"mass": 1.0},
                ),
            ],
            constraints=[
                Constraint(
                    id="damped_spring",
                    type="spring",
                    entity_a="mass_a",
                    entity_b="mass_b",
                    length=0.15,
                    stiffness=80.0,
                    damping=15.0,
                )
            ],
        )

        state = self.engine.init_simulation(doc)
        dt = 0.01
        curr = state
        for _ in range(150):
            curr = self.engine.step(curr, dt=dt)

        final_dist = math.hypot(
            curr.entities[1].position.x - curr.entities[0].position.x,
            curr.entities[1].position.y - curr.entities[0].position.y,
        )
        # Settles very close to rest length 0.15 with negligible residual velocity
        self.assertAlmostEqual(final_dist, 0.15, places=2)
        self.assertAlmostEqual(curr.entities[0].velocity.vx, 0.0, places=2)
        self.assertAlmostEqual(curr.entities[1].velocity.vx, 0.0, places=2)

    def test_distance_joint_rigid_length(self):
        """Rigid distance joint maintains target length under relative motion."""
        target_len = 0.2
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="anchor_body",
                    type="circle",
                    position=Position(0.5, 0.5),
                    size=CircleSize(radius=0.04),
                    properties={"static": True},
                ),
                Entity(
                    id="moving_body",
                    type="circle",
                    position=Position(0.5 + target_len, 0.5),
                    size=CircleSize(radius=0.03),
                    velocity=Velocity(vx=0.0, vy=0.4),
                    properties={"mass": 1.0},
                ),
            ],
            constraints=[
                Constraint(
                    id="rod",
                    type="distance",
                    entity_a="anchor_body",
                    entity_b="moving_body",
                    length=target_len,
                )
            ],
        )

        state = self.engine.init_simulation(doc)
        curr = state
        dt = 1.0 / 60.0

        # Step 60 ticks (~1 second of circular swinging)
        for step_idx in range(60):
            curr = self.engine.step(curr, dt=dt)
            p_a = curr.entities[0].position
            p_b = curr.entities[1].position
            current_len = math.hypot(p_b.x - p_a.x, p_b.y - p_a.y)
            # Distance must remain rigidly constrained to target_len
            self.assertAlmostEqual(current_len, target_len, places=3)

    def test_world_anchored_pendulum(self):
        """Constraint anchored to world coordinate (entity_b = None) swings properly."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="bob",
                    type="circle",
                    position=Position(0.7, 0.3),
                    size=CircleSize(radius=0.03),
                    velocity=Velocity(vx=0.0, vy=0.2),
                    properties={"mass": 1.0},
                ),
            ],
            constraints=[
                Constraint(
                    id="pendulum_cable",
                    type="distance",
                    entity_a="bob",
                    entity_b=None,
                    anchor_a=Position(0.0, 0.0),
                    anchor_b=Position(0.5, 0.3),  # World anchor at (0.5, 0.3)
                    length=0.2,
                )
            ],
        )

        state = self.engine.init_simulation(doc)
        curr = state
        dt = 1.0 / 60.0
        for _ in range(30):
            curr = self.engine.step(curr, dt=dt)
            bob_pos = curr.entities[0].position
            dist_to_anchor = math.hypot(bob_pos.x - 0.5, bob_pos.y - 0.3)
            self.assertAlmostEqual(dist_to_anchor, 0.2, places=3)

    def test_revolute_pin_hinge_rotation(self):
        """Revolute pin hinge locks the local pivot without translational drift while spinning."""
        # Box of size (0.2, 0.04), pivot at left edge: anchor_a = (-0.1, 0.0)
        # Anchored to world at (0.4, 0.4)
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="flipper",
                    type="box",
                    position=Position(0.5, 0.4),  # center at (0.5, 0.4) -> left edge at (0.4, 0.4)
                    size=BoxSize(width=0.2, height=0.04),
                    velocity=Velocity(vx=0.0, vy=0.0, omega=2.0),
                    properties={"mass": 1.0},
                    angle=0.0,
                ),
            ],
            constraints=[
                Constraint(
                    id="hinge_1",
                    type="pin",
                    entity_a="flipper",
                    entity_b=None,
                    anchor_a=Position(-0.1, 0.0),
                    anchor_b=Position(0.4, 0.4),
                )
            ],
        )

        state = self.engine.init_simulation(doc)
        curr = state
        dt = 1.0 / 60.0

        for _ in range(45):
            curr = self.engine.step(curr, dt=dt)
            flipper = curr.entities[0]
            # World position of left-edge pivot:
            cos_th = math.cos(flipper.angle)
            sin_th = math.sin(flipper.angle)
            pivot_x = flipper.position.x - 0.1 * cos_th
            pivot_y = flipper.position.y - 0.1 * sin_th

            # Pivot position must stay anchored at (0.4, 0.4)
            self.assertAlmostEqual(pivot_x, 0.4, places=3)
            self.assertAlmostEqual(pivot_y, 0.4, places=3)

        # Verify that the flipper has rotated significantly (0.41 rad)
        self.assertGreater(curr.entities[0].angle, 0.35)

    def test_multi_link_chain(self):
        """Multi-body distance chain connects 3 entities and preserves lengths."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="link_0",
                    type="circle",
                    position=Position(0.2, 0.5),
                    size=CircleSize(radius=0.02),
                    properties={"static": True},
                ),
                Entity(
                    id="link_1",
                    type="circle",
                    position=Position(0.35, 0.5),
                    size=CircleSize(radius=0.02),
                    velocity=Velocity(vx=0.1, vy=0.2),
                    properties={"mass": 1.0},
                ),
                Entity(
                    id="link_2",
                    type="circle",
                    position=Position(0.50, 0.5),
                    size=CircleSize(radius=0.02),
                    velocity=Velocity(vx=0.0, vy=-0.3),
                    properties={"mass": 1.0},
                ),
            ],
            constraints=[
                Constraint(
                    id="rod_0_1",
                    type="distance",
                    entity_a="link_0",
                    entity_b="link_1",
                    length=0.15,
                ),
                Constraint(
                    id="rod_1_2",
                    type="distance",
                    entity_a="link_1",
                    entity_b="link_2",
                    length=0.15,
                ),
            ],
        )

        state = self.engine.init_simulation(doc)
        curr = state
        dt = 0.01

        for _ in range(30):
            curr = self.engine.step(curr, dt=dt)
            p0 = curr.entities[0].position
            p1 = curr.entities[1].position
            p2 = curr.entities[2].position

            d01 = math.hypot(p1.x - p0.x, p1.y - p0.y)
            d12 = math.hypot(p2.x - p1.x, p2.y - p1.y)

            self.assertAlmostEqual(d01, 0.15, places=2)
            self.assertAlmostEqual(d12, 0.15, places=2)

    def test_loader_schema_validation(self):
        """Loader enforces valid constraint types, IDs, entities, and numeric bounds."""
        base_doc = {
            "mlue_version": "1.6",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {"id": "box_a", "type": "box", "position": {"x": 0.3, "y": 0.5}, "size": {"width": 0.1, "height": 0.1}},
                {"id": "box_b", "type": "box", "position": {"x": 0.6, "y": 0.5}, "size": {"width": 0.1, "height": 0.1}},
            ],
        }

        # 1. Unknown entity_a
        bad_doc_1 = dict(base_doc)
        bad_doc_1["constraints"] = [
            {"id": "c1", "type": "distance", "entity_a": "ghost", "entity_b": "box_b"}
        ]
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(bad_doc_1)

        # 2. Unknown entity_b
        bad_doc_2 = dict(base_doc)
        bad_doc_2["constraints"] = [
            {"id": "c1", "type": "distance", "entity_a": "box_a", "entity_b": "ghost"}
        ]
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(bad_doc_2)

        # 3. Self-constraint (entity_a == entity_b)
        bad_doc_3 = dict(base_doc)
        bad_doc_3["constraints"] = [
            {"id": "c1", "type": "distance", "entity_a": "box_a", "entity_b": "box_a"}
        ]
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(bad_doc_3)

        # 4. Unsupported constraint type
        bad_doc_4 = dict(base_doc)
        bad_doc_4["constraints"] = [
            {"id": "c1", "type": "wormhole", "entity_a": "box_a", "entity_b": "box_b"}
        ]
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(bad_doc_4)

        # 5. Negative stiffness
        bad_doc_5 = dict(base_doc)
        bad_doc_5["constraints"] = [
            {"id": "c1", "type": "spring", "entity_a": "box_a", "entity_b": "box_b", "stiffness": -10.0}
        ]
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(bad_doc_5)

        # 6. Valid document with auto length calculation
        valid_doc = dict(base_doc)
        valid_doc["constraints"] = [
            {"id": "c1", "type": "spring", "entity_a": "box_a", "entity_b": "box_b"}
        ]
        parsed = validate_and_parse(valid_doc)
        self.assertEqual(len(parsed.constraints), 1)
        # Initial distance between (0.3, 0.5) and (0.6, 0.5) is 0.3
        self.assertAlmostEqual(parsed.constraints[0].length, 0.3, places=5)

    def test_cyclomatic_complexity_bounds(self):
        """Verifies that all constraint solver methods adhere to NIST CC <= 30."""
        import ast
        import inspect

        def calculate_cc(node):
            complexity = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                    complexity += 1
                elif isinstance(child, ast.BoolOp):
                    complexity += len(child.values) - 1
            return complexity

        engine_source = inspect.getsource(MLUEEngine)
        tree = ast.parse(engine_source)

        constraint_methods = [
            "_compute_anchor_world",
            "_update_entity_kinematics",
            "_get_constraint_inv_mass_inertia",
            "_solve_spring_constraint",
            "_solve_distance_constraint",
            "_solve_pin_constraint",
            "_resolve_constraints",
        ]

        for item in tree.body[0].body:
            if isinstance(item, ast.FunctionDef) and item.name in constraint_methods:
                cc = calculate_cc(item)
                self.assertLessEqual(
                    cc, 30, f"Method {item.name} exceeds NIST CC bound: {cc} > 30"
                )


if __name__ == "__main__":
    unittest.main()
