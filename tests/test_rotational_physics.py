"""Unit tests for MLUE Phase 2: Rotational Dynamics & Surface Friction.

Verifies:
- Angular kinematics integration (theta_next = (theta + omega * dt) % 2pi)
- Rotated OBB AABB bounds computation
- Rotated box point-in-shape hit testing
- Normal impulse with restitution scaling
- Off-center collisions imparting torque and angular acceleration
- Coulomb surface friction imparting tangential impulse and spin
- Spinning paddle deflection dynamics
- Fixed rotation constraint invariance
- Loader validation of angle, omega, restitution, friction
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
    CapsuleSize,
    Velocity,
)
from runtime.engine import MLUEEngine
from runtime.spatial import compute_entity_aabb, point_in_box
from runtime.loader import validate_and_parse, MLUEValidationError


class TestRotationalDynamicsAndFriction(unittest.TestCase):

    def setUp(self):
        self.engine = MLUEEngine()
        self.env = Environment(width=800, height=800)

    def test_angular_kinematics_integration(self):
        """Orientation angle updates by omega * dt each tick modulo 2pi."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="spinner",
                    type="box",
                    position=Position(0.5, 0.5),
                    size=BoxSize(width=0.2, height=0.05),
                    velocity=Velocity(vx=0.0, vy=0.0, omega=math.pi),
                    properties={"solid": False},
                    angle=0.0,
                )
            ],
        )
        state = self.engine.init_simulation(doc)
        dt = 0.5
        next_state = self.engine.step(state, dt=dt)
        self.assertAlmostEqual(next_state.entities[0].angle, 0.5 * math.pi, places=5)

        next_state2 = self.engine.step(next_state, dt=1.5)
        self.assertAlmostEqual(next_state2.entities[0].angle, 0.0, places=5)

    def test_rotated_box_aabb_bounds(self):
        """Rotated box AABB correctly expands from w/2, h/2 to (|w cos| + |h sin|)/2."""
        box = Entity(
            id="b1",
            type="box",
            position=Position(0.5, 0.5),
            size=BoxSize(width=0.2, height=0.1),
            angle=0.0,
        )
        aabb0 = compute_entity_aabb(box, self.env)
        self.assertAlmostEqual(aabb0.min_x, 0.4, places=5)
        self.assertAlmostEqual(aabb0.max_x, 0.6, places=5)
        self.assertAlmostEqual(aabb0.min_y, 0.45, places=5)
        self.assertAlmostEqual(aabb0.max_y, 0.55, places=5)

        box_90 = Entity(
            id="b1",
            type="box",
            position=Position(0.5, 0.5),
            size=BoxSize(width=0.2, height=0.1),
            angle=math.pi / 2.0,
        )
        aabb90 = compute_entity_aabb(box_90, self.env)
        self.assertAlmostEqual(aabb90.min_x, 0.45, places=5)
        self.assertAlmostEqual(aabb90.max_x, 0.55, places=5)
        self.assertAlmostEqual(aabb90.min_y, 0.4, places=5)
        self.assertAlmostEqual(aabb90.max_y, 0.6, places=5)

    def test_rotated_box_point_in_box_hit_testing(self):
        """Point inside rotated box detects hit; point outside rotated bounds misses."""
        angle = math.pi / 4.0
        self.assertTrue(point_in_box(0.5, 0.5, 0.5, 0.5, 0.4, 0.04, angle))

        tip_x = 0.5 + 0.15 * math.cos(angle)
        tip_y = 0.5 + 0.15 * math.sin(angle)
        self.assertTrue(point_in_box(tip_x, tip_y, 0.5, 0.5, 0.4, 0.04, angle))

        self.assertFalse(point_in_box(0.65, 0.5, 0.5, 0.5, 0.4, 0.04, angle))

    def test_restitution_damping(self):
        """Collisions with restitution < 1.0 exhibit velocity damping."""
        doc_elastic = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity("c1", "circle", Position(0.4, 0.5), CircleSize(0.05), Velocity(0.2, 0.0), properties={"solid": True, "restitution": 1.0}),
                Entity("c2", "circle", Position(0.5, 0.5), CircleSize(0.05), Velocity(0.0, 0.0), properties={"solid": True, "restitution": 1.0}),
            ],
        )
        s_el = self.engine.init_simulation(doc_elastic)
        s_el_next = self.engine.step(s_el, dt=0.01)
        rel_vel_el = abs(s_el_next.entities[0].velocity.vx - s_el_next.entities[1].velocity.vx)

        doc_inelastic = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity("c1", "circle", Position(0.4, 0.5), CircleSize(0.05), Velocity(0.2, 0.0), properties={"solid": True, "restitution": 0.5}),
                Entity("c2", "circle", Position(0.5, 0.5), CircleSize(0.05), Velocity(0.0, 0.0), properties={"solid": True, "restitution": 0.5}),
            ],
        )
        s_in = self.engine.init_simulation(doc_inelastic)
        s_in_next = self.engine.step(s_in, dt=0.01)
        rel_vel_in = abs(s_in_next.entities[0].velocity.vx - s_in_next.entities[1].velocity.vx)

        self.assertAlmostEqual(rel_vel_in, 0.5 * rel_vel_el, places=4)

    def test_off_center_collision_imparts_angular_velocity(self):
        """Off-center strike on a floating dynamic box imparts angular velocity."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity("box", "box", Position(0.5, 0.5), BoxSize(0.2, 0.05), Velocity(0.0, 0.0, 0.0), properties={"solid": True, "mass": 1.0, "dynamic": True}),
                Entity("ball", "circle", Position(0.58, 0.48), CircleSize(0.02), Velocity(0.0, 0.5, 0.0), properties={"solid": True, "mass": 0.5}),
            ],
        )
        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=0.01)

        box_after = next_state.entities[0]
        self.assertNotEqual(box_after.velocity.omega, 0.0)
        self.assertGreater(box_after.velocity.omega, 0.0)

    def test_coulomb_surface_friction_imparts_spin(self):
        """Glancing collision with surface friction imparts spin and tangential impulse."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity("c1", "circle", Position(0.46, 0.48), CircleSize(0.04), Velocity(0.3, 0.2, 0.0), properties={"solid": True, "friction": 0.8}),
                Entity("c2", "circle", Position(0.52, 0.52), CircleSize(0.04), Velocity(0.0, 0.0, 0.0), properties={"solid": True, "friction": 0.8}),
            ],
        )
        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=0.01)

        c1_w = next_state.entities[0].velocity.omega
        c2_w = next_state.entities[1].velocity.omega
        self.assertNotEqual(c1_w, 0.0)
        self.assertNotEqual(c2_w, 0.0)

    def test_spinning_paddle_deflection_velocity_boost(self):
        """A spinning paddle imparts greater normal deflection to a colliding ball."""
        def run_bounce(paddle_omega: float) -> float:
            doc = MLUEDocument(
                version="1.6",
                environment=self.env,
                entities=[
                    Entity("paddle", "box", Position(0.5, 0.5), BoxSize(0.3, 0.04), Velocity(0.0, 0.0, paddle_omega), properties={"solid": True, "static": True}),
                    Entity("ball", "circle", Position(0.6, 0.47), CircleSize(0.02), Velocity(0.0, 0.2, 0.0), properties={"solid": True}),
                ],
            )
            state = self.engine.init_simulation(doc)
            next_state = self.engine.step(state, dt=0.01)
            return next_state.entities[1].velocity.vy

        vy_stationary = run_bounce(0.0)
        vy_spinning = run_bounce(-10.0)
        self.assertLess(vy_spinning, vy_stationary)

    def test_fixed_rotation_invariance(self):
        """Entities with fixed_rotation: True do not gain angular velocity from off-center hits."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity("box", "box", Position(0.5, 0.5), BoxSize(0.2, 0.05), Velocity(0.0, 0.0, 0.0), properties={"solid": True, "mass": 1.0, "dynamic": True, "fixed_rotation": True}),
                Entity("ball", "circle", Position(0.58, 0.48), CircleSize(0.02), Velocity(0.0, 0.5, 0.0), properties={"solid": True, "mass": 0.5}),
            ],
        )
        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=0.01)
        self.assertEqual(next_state.entities[0].velocity.omega, 0.0)

    def test_loader_validation_rotational_properties(self):
        """Loader accepts valid angle, omega, restitution, friction and rejects out-of-range values."""
        valid_doc = {
            "mlue_version": "1.6",
            "environment": {"dimensions": [600, 600]},
            "entities": [
                {
                    "id": "spinner",
                    "type": "box",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.2, "height": 0.05},
                    "angle": 1.57,
                    "velocity": {"vx": 0.1, "vy": 0.0, "omega": 3.14},
                    "properties": {"solid": True, "restitution": 0.85, "friction": 0.25},
                }
            ],
        }
        parsed = validate_and_parse(valid_doc)
        ent = parsed.entities[0]
        self.assertAlmostEqual(ent.angle, 1.57, places=4)
        self.assertAlmostEqual(ent.velocity.omega, 3.14, places=4)
        self.assertAlmostEqual(ent.properties["restitution"], 0.85, places=4)
        self.assertAlmostEqual(ent.properties["friction"], 0.25, places=4)

        invalid_rest = dict(valid_doc)
        invalid_rest["entities"] = [dict(valid_doc["entities"][0], properties={"restitution": 1.5})]
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(invalid_rest)

        invalid_fric = dict(valid_doc)
        invalid_fric["entities"] = [dict(valid_doc["entities"][0], properties={"friction": -0.2})]
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(invalid_fric)


if __name__ == "__main__":
    unittest.main()
