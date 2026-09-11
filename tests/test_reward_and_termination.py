"""MLUE Unit Tests: Declarative RL Objectives (Reward & Termination Engine)

Verifies declarative reward accumulation, episode termination, episode truncation,
schema validation of reward/terminate/truncate actions, and persistence of
terminal flags across subsequent steps.
"""

import unittest
from runtime.model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    Velocity,
    CircleSize,
    BoxSize,
    Rule,
    Condition,
    Action,
)
from runtime.loader import validate_and_parse, MLUEValidationError
from runtime.engine import MLUEEngine


class TestRewardAndTermination(unittest.TestCase):
    """Verifies reward, terminate, and truncate actions in the MLUE simulation engine."""

    def setUp(self):
        self.engine = MLUEEngine()

    def test_declarative_reward_on_collision(self):
        """Collision between two solid entities triggers a reward action."""
        doc = MLUEDocument(
            version="1.6",
            environment=Environment(width=100, height=100),
            entities=[
                Entity(
                    id="ball_a",
                    type="circle",
                    position=Position(x=0.45, y=0.5),
                    size=CircleSize(radius=0.05),
                    velocity=Velocity(vx=1.0, vy=0.0),
                    properties={"solid": True},
                ),
                Entity(
                    id="ball_b",
                    type="circle",
                    position=Position(x=0.55, y=0.5),
                    size=CircleSize(radius=0.05),
                    velocity=Velocity(vx=-1.0, vy=0.0),
                    properties={"solid": True},
                ),
            ],
            rules=[
                Rule(
                    trigger="score_goal",
                    event="collision",
                    entities=("ball_a", "ball_b"),
                    actions=[Action(type="reward", amount=10.0)],
                )
            ],
        )

        state = self.engine.init_simulation(doc)
        self.assertEqual(state.step_reward, 0.0)
        self.assertFalse(state.terminated)
        self.assertFalse(state.truncated)

        # Step into collision
        state = self.engine.step(state, dt=0.05)
        self.assertEqual(state.step_reward, 10.0)
        self.assertFalse(state.terminated)

        # Next step: no new collision, reward should be 0.0
        state = self.engine.step(state, dt=0.05)
        self.assertEqual(state.step_reward, 0.0)

    def test_declarative_termination_on_condition(self):
        """Spatial condition boundary triggers episode termination."""
        doc = MLUEDocument(
            version="1.6",
            environment=Environment(width=100, height=100),
            entities=[
                Entity(
                    id="agent",
                    type="box",
                    position=Position(x=0.8, y=0.5),
                    size=BoxSize(width=0.1, height=0.1),
                    velocity=Velocity(vx=0.5, vy=0.0),
                    properties={"solid": False},
                )
            ],
            rules=[
                Rule(
                    trigger="out_of_bounds",
                    condition=Condition(entity="agent", property="position.x", op=">=", value=0.85),
                    actions=[
                        Action(type="reward", amount=-5.0),
                        Action(type="terminate"),
                    ],
                )
            ],
        )

        state = self.engine.init_simulation(doc)
        self.assertFalse(state.terminated)

        # Step until x >= 0.85
        state = self.engine.step(state, dt=0.2)
        self.assertTrue(state.terminated)
        self.assertEqual(state.step_reward, -5.0)

        # Terminal state must persist on subsequent steps
        state = self.engine.step(state, dt=0.01)
        self.assertTrue(state.terminated)

    def test_declarative_truncation_on_time_limit(self):
        """State variable threshold triggers truncation."""
        raw_doc = {
            "mlue_version": "1.6",
            "environment": {"dimensions": [100, 100]},
            "state_variables": {"step_count": 0},
            "entities": [
                {
                    "id": "runner",
                    "type": "circle",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"radius": 0.05},
                    "properties": {},
                }
            ],
            "rules": [
                {
                    "trigger": "tick_counter",
                    "condition": {"state_variable": "step_count", "op": ">=", "value": 0},
                    "actions": [{"type": "increment", "target": "step_count", "amount": 1}],
                },
                {
                    "trigger": "time_limit",
                    "condition": {"state_variable": "step_count", "op": ">=", "value": 3},
                    "actions": [{"type": "truncate"}],
                },
            ],
        }

        doc = validate_and_parse(raw_doc)
        state = self.engine.init_simulation(doc)
        self.assertFalse(state.truncated)

        # Step 1: step_count becomes 1
        state = self.engine.step(state, dt=0.01)
        self.assertFalse(state.truncated)

        # Step 2: step_count becomes 2
        state = self.engine.step(state, dt=0.01)
        self.assertFalse(state.truncated)

        # Step 3: step_count becomes 3, triggers truncate
        state = self.engine.step(state, dt=0.01)
        self.assertTrue(state.truncated)

    def test_multiple_reward_accumulation_in_single_step(self):
        """Multiple rules triggering in the same step accumulate rewards correctly."""
        doc = MLUEDocument(
            version="1.6",
            environment=Environment(width=100, height=100),
            entities=[
                Entity(
                    id="agent",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.1, height=0.1),
                    properties={},
                )
            ],
            rules=[
                Rule(
                    trigger="r1",
                    condition=Condition(entity="agent", property="position.x", op="==", value=0.5),
                    actions=[Action(type="reward", amount=2.5)],
                ),
                Rule(
                    trigger="r2",
                    condition=Condition(entity="agent", property="position.y", op="==", value=0.5),
                    actions=[Action(type="reward", amount=1.5)],
                ),
            ],
        )

        state = self.engine.init_simulation(doc)
        state = self.engine.step(state, dt=0.01)
        self.assertAlmostEqual(state.step_reward, 4.0, places=5)

    def test_validation_rejects_nan_reward(self):
        """Loader rejects NaN or Infinite reward amounts."""
        raw_doc = {
            "mlue_version": "1.6",
            "environment": {"dimensions": [100, 100]},
            "entities": [
                {
                    "id": "e1",
                    "type": "circle",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"radius": 0.05},
                    "properties": {},
                }
            ],
            "rules": [
                {
                    "trigger": "invalid_reward",
                    "condition": {"entity": "e1", "property": "position.x", "op": "==", "value": 0.5},
                    "actions": [{"type": "reward", "amount": float("nan")}],
                }
            ],
        }
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(raw_doc)


if __name__ == "__main__":
    unittest.main()
