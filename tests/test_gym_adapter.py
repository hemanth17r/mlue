"""MLUE Unit Tests: Gymnasium and PettingZoo Environment Adapters

Verifies standard gym.Env interface compliance (reset, step, action/observation spaces),
continuous/discrete action mapping, reward signals, episode termination, and
multi-agent parallel swarm environments.
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
from runtime.gym import MLUEGymEnv
from runtime.pettingzoo import MLUEParallelEnv
from runtime.tensor import ObservationSpec, HAS_NUMPY

if HAS_NUMPY:
    import numpy as np


class TestGymAdapter(unittest.TestCase):
    """Verifies standard Gymnasium single-agent environment adapter."""

    def setUp(self):
        # Create a simple navigation scene: agent moves toward a target
        self.doc = MLUEDocument(
            version="1.6",
            environment=Environment(width=200, height=200),
            entities=[
                Entity(
                    id="agent_bot",
                    type="circle",
                    position=Position(x=0.2, y=0.5),
                    size=CircleSize(radius=0.05),
                    velocity=Velocity(vx=0.0, vy=0.0),
                    properties={
                        "solid": True,
                        "control": {
                            "channel": "drive_x",
                            "axis": "x",
                            "speed": 0.5,
                        },
                    },
                ),
                Entity(
                    id="goal_post",
                    type="box",
                    position=Position(x=0.8, y=0.5),
                    size=BoxSize(width=0.1, height=0.1),
                    properties={"solid": True},
                ),
            ],
            rules=[
                Rule(
                    trigger="reach_goal",
                    event="collision",
                    entities=("agent_bot", "goal_post"),
                    actions=[
                        Action(type="reward", amount=100.0),
                        Action(type="terminate"),
                    ],
                )
            ],
            state_variables={"score": 0.0},
        )

    def test_gym_lifecycle_continuous(self):
        """Verifies reset, action space, observation space, and step execution with continuous actions."""
        env = MLUEGymEnv(
            mlue_source=self.doc,
            action_channels=["drive_x"],
            continuous_actions=True,
            max_episode_steps=50,
        )

        obs, info = env.reset()
        self.assertEqual(info["step"], 0)
        self.assertEqual(env.action_space.shape, (1,))

        # Action: drive forward (+X)
        action = [1.0]
        obs, reward, terminated, truncated, info = env.step(action)

        self.assertEqual(info["step"], 1)
        self.assertFalse(terminated)
        self.assertFalse(truncated)

        # In observation, agent_bot is first entity, pos.x should have increased
        agent_x = obs[0]
        self.assertGreater(agent_x, 0.2)

    def test_gym_lifecycle_discrete(self):
        """Verifies discrete action space mapping to continuous channel velocities."""
        env = MLUEGymEnv(
            mlue_source=self.doc,
            action_channels=["drive_x"],
            continuous_actions=False,
            max_episode_steps=10,
        )

        obs, info = env.reset()
        self.assertEqual(env.action_space.n, 3)

        # Action index 2 maps to +1.0
        obs, reward, terminated, truncated, info = env.step(2)
        agent_x = obs[0]
        self.assertGreater(agent_x, 0.2)

    def test_goal_termination_and_reward(self):
        """Stepping until goal contact triggers reward 100.0 and terminated=True."""
        env = MLUEGymEnv(
            mlue_source=self.doc,
            action_channels=["drive_x"],
            dt=0.1,  # Large dt to reach goal quickly
            max_episode_steps=50,
        )

        env.reset()
        reached = False
        for _ in range(30):
            obs, reward, terminated, truncated, info = env.step([1.0])
            if reward == 100.0:
                self.assertTrue(terminated)
                reached = True
                break

        self.assertTrue(reached)

    def test_truncation_on_max_steps(self):
        """Episode truncates when current_step reaches max_episode_steps."""
        env = MLUEGymEnv(
            mlue_source=self.doc,
            action_channels=["drive_x"],
            max_episode_steps=5,
        )

        env.reset()
        for i in range(4):
            _, _, terminated, truncated, _ = env.step([0.0])
            self.assertFalse(truncated)

        # Step 5 reaches max_episode_steps
        _, _, terminated, truncated, _ = env.step([0.0])
        self.assertTrue(truncated)


class TestPettingZooAdapter(unittest.TestCase):
    """Verifies multi-agent PettingZoo parallel environment adapter."""

    def test_multi_agent_swarm(self):
        """Two agents step simultaneously in a shared environment."""
        doc = MLUEDocument(
            version="1.6",
            environment=Environment(width=200, height=200),
            entities=[
                Entity(
                    id="agent_a",
                    type="circle",
                    position=Position(x=0.3, y=0.5),
                    size=CircleSize(radius=0.05),
                    properties={"control": {"channel": "a_drive", "axis": "x", "speed": 0.5}},
                ),
                Entity(
                    id="agent_b",
                    type="circle",
                    position=Position(x=0.7, y=0.5),
                    size=CircleSize(radius=0.05),
                    properties={"control": {"channel": "b_drive", "axis": "x", "speed": 0.5}},
                ),
            ],
        )

        agent_configs = {
            "agent_a": {"action_channels": ["a_drive"]},
            "agent_b": {"action_channels": ["b_drive"]},
        }

        env = MLUEParallelEnv(doc, agent_configs, max_episode_steps=20)
        obs, info = env.reset()

        self.assertIn("agent_a", obs)
        self.assertIn("agent_b", obs)

        joint_actions = {
            "agent_a": [1.0],   # Move right
            "agent_b": [-1.0],  # Move left
        }

        obs, rewards, terms, truncs, infos = env.step(joint_actions)

        # Agent A moved right (+X)
        self.assertGreater(obs["agent_a"][0], 0.3)
        # Agent B moved left (-X)
        self.assertLess(obs["agent_b"][0], 0.7)


if __name__ == "__main__":
    unittest.main()
