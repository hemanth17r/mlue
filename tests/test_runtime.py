"""MLUE Phase 0.5 Unit Tests

Verifies loading, validation, geometry calculation, multi-entity composition,
deterministic time-step evaluation (dt), environment boundary reflections,
pairwise relational collisions, input signals, and declarative trigger rules for Pong.
"""

import unittest
import math
from pathlib import Path
from runtime import (
    load_mlue,
    validate_and_parse,
    MLUEEngine,
    MLUEValidationError,
    BoxSize,
    CircleSize,
    Position,
    Velocity,
    Entity,
    Environment,
    MLUEDocument,
    Condition,
    Action,
    Rule,
)


class TestMLUERuntime(unittest.TestCase):

    def setUp(self):
        self.examples_dir = Path(__file__).parent.parent / "examples"
        self.engine = MLUEEngine()

    def test_load_and_evaluate_phase_01_compatibility(self):
        """Verify Phase 0.1 static circle document loads and evaluates correctly."""
        path = self.examples_dir / "first_object.mlue"
        doc = load_mlue(path)
        self.assertEqual(doc.version, "0.1")
        self.assertEqual(doc.environment.width, 400)
        self.assertEqual(doc.environment.height, 400)
        self.assertEqual(len(doc.entities), 1)

        entity = doc.entities[0]
        self.assertEqual(entity.id, "circle_01")
        self.assertEqual(entity.type, "circle")
        self.assertAlmostEqual(entity.position.x, 0.5)
        self.assertAlmostEqual(entity.position.y, 0.5)
        self.assertAlmostEqual(entity.size.radius, 0.2)
        self.assertEqual(entity.velocity.vx, 0.0)
        self.assertEqual(entity.velocity.vy, 0.0)

        result = self.engine.evaluate(doc)
        self.assertEqual(result.width, 400)
        self.assertEqual(result.height, 400)
        self.assertEqual(result.background, "#0F172A")
        self.assertEqual(len(result.shapes), 1)

        shape = result.shapes[0]
        self.assertEqual(shape.id, "circle_01")
        self.assertEqual(shape.type, "circle")
        self.assertEqual(shape.center, (200.0, 200.0))
        self.assertEqual(shape.bbox, (120.0, 120.0, 280.0, 280.0))
        self.assertEqual(shape.color, "#38BDF8")

    def test_load_and_evaluate_box_geometry(self):
        """Verify box entity geometry and bounding box projection."""
        payload = {
            "mlue_version": "0.2",
            "environment": {"dimensions": [600, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "paddle",
                    "type": "box",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.1, "height": 0.5},
                    "properties": {"color": "#FF0000"}
                }
            ]
        }
        doc = validate_and_parse(payload)
        self.assertEqual(doc.version, "0.2")
        self.assertEqual(doc.entities[0].type, "box")
        self.assertIsInstance(doc.entities[0].size, BoxSize)
        self.assertAlmostEqual(doc.entities[0].size.width, 0.1)
        self.assertAlmostEqual(doc.entities[0].size.height, 0.5)

        result = self.engine.evaluate(doc)
        shape = result.shapes[0]
        self.assertEqual(shape.id, "paddle")
        self.assertEqual(shape.type, "box")
        self.assertEqual(shape.center, (300.0, 200.0))
        self.assertEqual(shape.bbox, (270.0, 100.0, 330.0, 300.0))

    def test_validation_duplicate_entity_ids(self):
        """Rejects documents with duplicate entity IDs."""
        payload = {
            "mlue_version": "0.5",
            "entities": [
                {"id": "e1", "type": "circle", "position": {"x": 0.2, "y": 0.2}, "size": {"radius": 0.1}},
                {"id": "e1", "type": "box", "position": {"x": 0.8, "y": 0.8}, "size": {"width": 0.1, "height": 0.1}},
            ]
        }
        with self.assertRaises(MLUEValidationError) as ctx:
            validate_and_parse(payload)
        self.assertIn("Duplicate entity id 'e1'", str(ctx.exception))

    def test_validation_rules_unknown_targets(self):
        """Rejects rules targeting non-existent entities or state variables."""
        payload_bad_entity = {
            "mlue_version": "0.5",
            "entities": [{"id": "b1", "type": "circle", "position": {"x": 0.5, "y": 0.5}, "size": {"radius": 0.1}}],
            "rules": [
                {
                    "trigger": "r1",
                    "condition": {"entity": "non_existent", "property": "position.x", "op": "<=", "value": 0.1},
                    "actions": [{"type": "increment", "target": "score", "amount": 1}]
                }
            ]
        }
        with self.assertRaises(MLUEValidationError) as ctx:
            validate_and_parse(payload_bad_entity)
        self.assertIn("targets unknown entity 'non_existent'", str(ctx.exception))

        payload_bad_var = {
            "mlue_version": "0.5",
            "state_variables": {"score_a": 0},
            "entities": [{"id": "b1", "type": "circle", "position": {"x": 0.5, "y": 0.5}, "size": {"radius": 0.1}}],
            "rules": [
                {
                    "trigger": "r1",
                    "condition": {"entity": "b1", "property": "position.x", "op": "<=", "value": 0.1},
                    "actions": [{"type": "increment", "target": "score_unknown", "amount": 1}]
                }
            ]
        }
        with self.assertRaises(MLUEValidationError) as ctx:
            validate_and_parse(payload_bad_var)
        self.assertIn("targets unknown state_variable 'score_unknown'", str(ctx.exception))

    def test_circle_box_collision_left_face(self):
        """Verify circle hitting the left face of a solid box reflects vx and separates."""
        doc = MLUEDocument(
            version="0.3",
            environment=Environment(width=400, height=400),
            entities=[
                Entity(
                    id="ball",
                    type="circle",
                    position=Position(x=0.32, y=0.5),
                    size=CircleSize(radius=0.05),
                    velocity=Velocity(vx=0.1, vy=0.0),
                    properties={"solid": True},
                ),
                Entity(
                    id="barrier",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.2, height=0.4),
                    velocity=Velocity(vx=0.0, vy=0.0),
                    properties={"solid": True},
                ),
            ]
        )
        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=1.0)

        ball = next_state.entities[0]
        self.assertAlmostEqual(ball.velocity.vx, -0.1)
        self.assertEqual(ball.velocity.vy, 0.0)
        self.assertAlmostEqual(ball.position.x, 0.35)
        self.assertAlmostEqual(ball.position.y, 0.5)

    def test_circle_circle_collision(self):
        """Verify two solid circles colliding in 1D reflect velocities."""
        doc = MLUEDocument(
            version="0.3",
            environment=Environment(width=400, height=400),
            entities=[
                Entity(
                    id="c1",
                    type="circle",
                    position=Position(x=0.4, y=0.5),
                    size=CircleSize(radius=0.05),
                    velocity=Velocity(vx=0.1, vy=0.0),
                    properties={"solid": True},
                ),
                Entity(
                    id="c2",
                    type="circle",
                    position=Position(x=0.6, y=0.5),
                    size=CircleSize(radius=0.05),
                    velocity=Velocity(vx=-0.1, vy=0.0),
                    properties={"solid": True},
                ),
            ]
        )
        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=0.6)

        c1 = next_state.entities[0]
        c2 = next_state.entities[1]
        self.assertAlmostEqual(c1.velocity.vx, -0.1)
        self.assertAlmostEqual(c2.velocity.vx, 0.1)

    def test_box_box_collision(self):
        """Verify two solid boxes colliding along X reflect velocities."""
        doc = MLUEDocument(
            version="0.3",
            environment=Environment(width=400, height=400),
            entities=[
                Entity(
                    id="b1",
                    type="box",
                    position=Position(x=0.35, y=0.5),
                    size=BoxSize(width=0.2, height=0.2),
                    velocity=Velocity(vx=0.1, vy=0.0),
                    properties={"solid": True},
                ),
                Entity(
                    id="b2",
                    type="box",
                    position=Position(x=0.65, y=0.5),
                    size=BoxSize(width=0.2, height=0.2),
                    velocity=Velocity(vx=-0.1, vy=0.0),
                    properties={"solid": True},
                ),
            ]
        )
        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=0.6)

        b1 = next_state.entities[0]
        b2 = next_state.entities[1]
        self.assertAlmostEqual(b1.velocity.vx, -0.1)
        self.assertAlmostEqual(b2.velocity.vx, 0.1)

    def test_circle_moving_paddle_relative_velocity(self):
        """Verify circle reflecting off a paddle moving horizontally with relative velocity."""
        doc = MLUEDocument(
            version="0.3",
            environment=Environment(width=400, height=400),
            entities=[
                Entity(
                    id="ball",
                    type="circle",
                    position=Position(x=0.35, y=0.5),
                    size=CircleSize(radius=0.05),
                    velocity=Velocity(vx=0.2, vy=0.0),
                    properties={"solid": True},
                ),
                Entity(
                    id="paddle",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.1, height=0.4),
                    velocity=Velocity(vx=-0.1, vy=0.0),
                    properties={"solid": True},
                ),
            ]
        )
        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=0.5)
        ball = next_state.entities[0]
        self.assertAlmostEqual(ball.velocity.vx, -0.4)

    def test_non_solid_entities_pass_through(self):
        """Verify entities without solid=True pass through each other without collision."""
        doc = MLUEDocument(
            version="0.3",
            environment=Environment(width=400, height=400),
            entities=[
                Entity(
                    id="ball",
                    type="circle",
                    position=Position(x=0.4, y=0.5),
                    size=CircleSize(radius=0.05),
                    velocity=Velocity(vx=0.1, vy=0.0),
                    properties={"solid": False},
                ),
                Entity(
                    id="barrier",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.2, height=0.2),
                    velocity=Velocity(vx=0.0, vy=0.0),
                    properties={"solid": False},
                ),
            ]
        )
        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=1.0)
        ball = next_state.entities[0]
        self.assertAlmostEqual(ball.velocity.vx, 0.1)
        self.assertAlmostEqual(ball.position.x, 0.5)

    def test_controlled_entity_signal_modulation(self):
        """Verify input signals directly modulate velocity and position of controlled entity."""
        doc = MLUEDocument(
            version="0.4",
            environment=Environment(width=400, height=400),
            entities=[
                Entity(
                    id="paddle",
                    type="box",
                    position=Position(x=0.1, y=0.5),
                    size=BoxSize(width=0.05, height=0.2),
                    velocity=Velocity(vx=0.0, vy=0.0),
                    properties={
                        "control": {"channel": "player_left", "axis": "y", "speed": 0.4}
                    },
                )
            ]
        )
        state = self.engine.init_simulation(doc)

        s1 = self.engine.step(state, dt=0.5, inputs={"player_left": 1.0})
        p = s1.entities[0]
        self.assertAlmostEqual(p.velocity.vy, 0.4)
        self.assertAlmostEqual(p.position.y, 0.7)

        s2 = self.engine.step(s1, dt=0.5, inputs={"player_left": -0.5})
        p2 = s2.entities[0]
        self.assertAlmostEqual(p2.velocity.vy, -0.2)
        self.assertAlmostEqual(p2.position.y, 0.6)

        s3 = self.engine.step(s2, dt=1.0, inputs={"player_left": 0.0})
        p3 = s3.entities[0]
        self.assertAlmostEqual(p3.velocity.vy, 0.0)
        self.assertAlmostEqual(p3.position.y, 0.6)

    def test_rule_trigger_score_and_reset(self):
        """Verify declarative rules trigger state variable increments and entity reset."""
        doc = MLUEDocument(
            version="0.5",
            environment=Environment(width=400, height=400),
            state_variables={"score_p1": 0},
            entities=[
                Entity(
                    id="ball",
                    type="circle",
                    position=Position(x=0.9, y=0.5),
                    size=CircleSize(radius=0.05),
                    velocity=Velocity(vx=0.2, vy=0.0),
                )
            ],
            rules=[
                Rule(
                    trigger="goal_right",
                    condition=Condition(entity="ball", property="position.x", op=">=", value=0.95),
                    actions=[
                        Action(type="increment", target="score_p1", amount=1),
                        Action(
                            type="reset_entity",
                            target="ball",
                            position=Position(x=0.5, y=0.5),
                            velocity=Velocity(vx=-0.2, vy=0.0),
                        ),
                    ],
                )
            ],
        )
        state = self.engine.init_simulation(doc)
        self.assertEqual(state.state_variables["score_p1"], 0)

        # In dt = 0.5, ball moves to 0.9 + 0.2 * 0.5 = 1.0 >= 0.95 -> Trigger fires!
        next_state = self.engine.step(state, dt=0.5)
        self.assertEqual(next_state.state_variables["score_p1"], 1)
        ball = next_state.entities[0]
        self.assertAlmostEqual(ball.position.x, 0.5)
        self.assertAlmostEqual(ball.position.y, 0.5)
        self.assertAlmostEqual(ball.velocity.vx, -0.2)

    def test_emergent_pong_full_simulation(self):
        """Verify examples/pong.mlue executes a full game loop with goal triggers and score updates."""
        path = self.examples_dir / "pong.mlue"
        doc = load_mlue(path)
        self.assertEqual(doc.version, "0.5")
        self.assertIn("score_left", doc.state_variables)
        self.assertIn("score_right", doc.state_variables)

        state = self.engine.init_simulation(doc)

        # Run simulation for 3 seconds (180 ticks at 60 FPS) without player inputs
        for _ in range(180):
            state = self.engine.step(state, dt=1.0 / 60.0)

        # Both left and right scores should have incremented as ball bounced past undefended goals
        total_goals = state.state_variables["score_left"] + state.state_variables["score_right"]
        self.assertGreater(total_goals, 0)
        self.assertAlmostEqual(state.time, 3.0)


if __name__ == "__main__":
    unittest.main()
