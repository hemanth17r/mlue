"""MLUE Phase 0.6 Unit Tests

Verifies loading, validation, geometry calculation, multi-entity composition,
deterministic time-step evaluation (dt), environment boundary reflections,
pairwise relational collisions, input signals, state variables, collision triggers,
entity lifecycle destruction, and Emergent Breakout match loops.
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
    SimulationState,
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
            "mlue_version": "0.6",
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
            "mlue_version": "0.6",
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

    def test_emergent_pong_full_simulation(self):
        """Verify examples/pong.mlue executes a full game loop with goal triggers and score updates."""
        path = self.examples_dir / "pong.mlue"
        doc = load_mlue(path)
        self.assertEqual(doc.version, "0.5")
        self.assertIn("score_left", doc.state_variables)
        self.assertIn("score_right", doc.state_variables)

        state = self.engine.init_simulation(doc)
        for _ in range(180):
            state = self.engine.step(state, dt=1.0 / 60.0)

        total_goals = state.state_variables["score_left"] + state.state_variables["score_right"]
        self.assertGreater(total_goals, 0)
        self.assertAlmostEqual(state.time, 3.0)

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

    def test_collision_event_trigger_and_destruction(self):
        """Verify collision between ball and brick destroys brick and awards points."""
        doc = MLUEDocument(
            version="0.6",
            environment=Environment(width=400, height=400),
            state_variables={"score": 0, "bricks_left": 1},
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
                    id="brick",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.1, height=0.2),
                    velocity=Velocity(vx=0.0, vy=0.0),
                    properties={"solid": True},
                ),
            ],
            rules=[
                Rule(
                    trigger="hit_brick",
                    event="collision",
                    entities=("ball", "brick"),
                    actions=[
                        Action(type="destroy_entity", target="brick"),
                        Action(type="increment", target="score", amount=100),
                        Action(type="increment", target="bricks_left", amount=-1),
                    ],
                )
            ],
        )
        state = self.engine.init_simulation(doc)
        self.assertEqual(len(state.result.shapes), 2)
        self.assertEqual(state.state_variables["score"], 0)

        # In dt = 0.5, ball hits brick -> collision event fires!
        next_state = self.engine.step(state, dt=0.5)
        self.assertEqual(next_state.state_variables["score"], 100)
        self.assertEqual(next_state.state_variables["bricks_left"], 0)

        # Brick should now be inactive and omitted from rendered shapes
        brick_entity = next_state.entities[1]
        self.assertFalse(brick_entity.active)
        self.assertEqual(len(next_state.result.shapes), 1)
        self.assertEqual(next_state.result.shapes[0].id, "ball")

    def test_state_variable_condition_and_property_mutation(self):
        """Verify state variable conditions trigger victory and set_property modifies entity."""
        doc = MLUEDocument(
            version="0.6",
            environment=Environment(width=400, height=400),
            state_variables={"bricks_left": 0, "status": "PLAYING"},
            entities=[
                Entity(
                    id="banner",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.2, height=0.1),
                    properties={"color": "#FFFFFF"},
                )
            ],
            rules=[
                Rule(
                    trigger="check_win",
                    condition=Condition(state_variable="bricks_left", op="<=", value=0),
                    actions=[
                        Action(type="set", target="status", value="VICTORY"),
                        Action(type="set_property", target="banner", property="color", value="#00FF00"),
                    ],
                )
            ],
        )
        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=0.1)

        self.assertEqual(next_state.state_variables["status"], "VICTORY")
        banner = next_state.entities[0]
        self.assertEqual(banner.properties["color"], "#00FF00")
        self.assertEqual(next_state.result.shapes[0].color, "#00FF00")

    def test_emergent_breakout_full_simulation(self):
        """Verify examples/breakout.mlue executes a full game loop with brick destructions."""
        path = self.examples_dir / "breakout.mlue"
        doc = load_mlue(path)
        self.assertEqual(doc.version, "0.6")
        self.assertIn("score", doc.state_variables)
        self.assertIn("bricks_remaining", doc.state_variables)
        self.assertEqual(doc.state_variables["bricks_remaining"], 6)

        state = self.engine.init_simulation(doc)
        self.assertEqual(len(state.result.shapes), 8)  # 1 ball + 1 paddle + 6 bricks

        # Run simulation for 2 seconds (120 ticks at 60 FPS)
        for _ in range(120):
            state = self.engine.step(state, dt=1.0 / 60.0)

        # As ball bounces into the brick grid, at least 1 brick should be destroyed
        self.assertGreater(state.state_variables["score"], 0)
        self.assertLess(state.state_variables["bricks_remaining"], 6)
        self.assertLess(len(state.result.shapes), 8)

    def test_breakout_floor_breach_lives_reduction(self):
        """Verify that when ball misses paddle and hits floor, lives reduce from 3 to 2 and ball resets."""
        path = self.examples_dir / "breakout.mlue"
        doc = load_mlue(path)
        state = self.engine.init_simulation(doc)
        self.assertEqual(state.state_variables["lives"], 3)

        # Paddle is at x=0.5. Move paddle far left (inputs player_bottom = -1.0) so ball misses paddle completely!
        # Ball starts at y=0.7 moving downward vy=0.45 (or we send ball downward)
        # Let's set ball velocity downward to floor
        ball = state.entities[0]
        state = SimulationState(
            time=state.time,
            environment=state.environment,
            entities=[
                Entity(
                    id=ball.id,
                    type=ball.type,
                    position=Position(x=0.8, y=0.85),
                    size=ball.size,
                    velocity=Velocity(vx=0.0, vy=0.5),
                    properties=ball.properties,
                    active=ball.active,
                ),
                state.entities[1], # paddle at x=0.1
                *state.entities[2:],
            ],
            result=state.result,
            state_variables=state.state_variables,
            rules=state.rules,
        )

        # In dt = 0.3s, ball goes to y = 0.85 + 0.5*0.3 = 1.0 (clamped to 0.975 >= 0.97) -> floor_breach fires!
        next_state = self.engine.step(state, dt=0.3, inputs={"player_bottom": -1.0})
        self.assertEqual(next_state.state_variables["lives"], 2)
        # Ball should have reset to position (0.5, 0.7)
        reset_ball = next_state.entities[0]
        self.assertAlmostEqual(reset_ball.position.x, 0.5)
        self.assertAlmostEqual(reset_ball.position.y, 0.7)

    def test_static_reachability_validation_rejection(self):
        """Verify loader statically rejects mathematically unreachable spatial rule conditions."""
        # Ball with radius 0.05 in 400x400 -> bottom boundary is 1.0 - 0.05 = 0.95
        # Attempting condition y >= 0.98 must be rejected at load time!
        unreachable_payload = {
            "mlue_version": "0.6",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "b1",
                    "type": "circle",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"radius": 0.05},
                    "properties": {"solid": True}
                }
            ],
            "rules": [
                {
                    "trigger": "impossible_floor",
                    "condition": {"entity": "b1", "property": "position.y", "op": ">=", "value": 0.98},
                    "actions": [{"type": "reset_entity", "target": "b1"}]
                }
            ]
        }
        with self.assertRaises(MLUEValidationError) as ctx:
            validate_and_parse(unreachable_payload)
        self.assertIn("mathematically unreachable", str(ctx.exception))
        self.assertIn("bottom boundary limit is 0.9500", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
