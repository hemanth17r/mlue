"""Unit tests for MLUE Subphase 1.6: Vectorized Batch Rollout Engine.

Tests multi-environment memory layout, lane isolation, selective reset,
and parallel determinism across batched simulation instances.
"""

import unittest
from runtime.model import MLUEDocument, Entity, Position, Velocity, CircleSize, Environment
from runtime.batch import BatchEnvironmentPool


class TestBatchRollout(unittest.TestCase):
    """Test suite for vectorized multi-environment parallel simulation."""

    def setUp(self):
        self.doc = MLUEDocument(
            version="1.6",
            environment=Environment(width=800, height=600, background="#000000"),
            entities=[
                Entity(
                    id="ball_01",
                    type="circle",
                    position=Position(x=0.25, y=0.50),
                    size=CircleSize(radius=0.04),
                    velocity=Velocity(vx=0.20, vy=0.10),
                    properties={"solid": True},
                    active=True,
                ),
                Entity(
                    id="paddle",
                    type="circle",
                    position=Position(x=0.75, y=0.50),
                    size=CircleSize(radius=0.04),
                    velocity=Velocity(vx=0.0, vy=0.0),
                    properties={"solid": True, "control": {"channel": "player_1", "axis": "y"}},
                    active=True,
                ),
            ],
            rules=[],
            state_variables={"game": {"score": 0}},
        )

    # =========================================================================
    # 1. BATCH POOL INITIALIZATION
    # =========================================================================

    def test_batch_pool_initialization(self):
        """Verify BatchEnvironmentPool initializes M independent identical lanes."""
        pool = BatchEnvironmentPool(self.doc, num_envs=25)
        self.assertEqual(pool.num_envs, 25)
        self.assertEqual(len(pool.lane_entities), 25)

        for lane in pool.lane_entities:
            self.assertEqual(len(lane), 2)
            self.assertEqual(lane[0].id, "ball_01")
            self.assertEqual(lane[1].id, "paddle")

    # =========================================================================
    # 2. LANE ISOLATION INVARIANT
    # =========================================================================

    def test_batch_lane_isolation(self):
        """Verify steering Lane 0 with input has ZERO effect on unsteered Lane 1."""
        pool = BatchEnvironmentPool(self.doc, num_envs=4)

        # Step 20 ticks: steer only Lane 0 upward (vy = -0.5)
        for _ in range(20):
            pool.step(actions_by_lane={0: {"player_1": -0.50}})

        states = pool.get_states()

        # Lane 0 paddle must have moved upward (y < 0.50)
        lane_0_paddle = next(e for e in states[0] if e.id == "paddle")
        self.assertLess(lane_0_paddle.position.y, 0.45)

        # Lane 1 paddle was unsteered (must remain at initial y = 0.50)
        lane_1_paddle = next(e for e in states[1] if e.id == "paddle")
        self.assertAlmostEqual(lane_1_paddle.position.y, 0.50, places=5)

    # =========================================================================
    # 3. SELECTIVE RESET
    # =========================================================================

    def test_batch_reset_selective(self):
        """Verify resetting a specific lane resets only that lane, preserving others."""
        pool = BatchEnvironmentPool(self.doc, num_envs=4)

        # Step 30 ticks
        for _ in range(30):
            pool.step()

        # Reset only Lane 2
        pool.reset(lane_indices=[2])

        states = pool.get_states()

        # Lane 2 ball must be back at initial position (x=0.25, y=0.50)
        lane_2_ball = next(e for e in states[2] if e.id == "ball_01")
        self.assertAlmostEqual(lane_2_ball.position.x, 0.25, places=5)
        self.assertAlmostEqual(lane_2_ball.position.y, 0.50, places=5)

        # Lane 0 ball must be in progressed position (x > 0.25)
        lane_0_ball = next(e for e in states[0] if e.id == "ball_01")
        self.assertNotAlmostEqual(lane_0_ball.position.x, 0.25, places=3)

    # =========================================================================
    # 4. DETERMINISTIC MULTI-LANE REPRODUCIBILITY
    # =========================================================================

    def test_batch_deterministic_multi_lane(self):
        """Verify identical unsteered lanes produce identical bit-exact trajectories."""
        pool = BatchEnvironmentPool(self.doc, num_envs=10)

        for _ in range(50):
            pool.step()

        states = pool.get_states()
        lane_0_ball = next(e for e in states[0] if e.id == "ball_01")

        for k in range(1, 10):
            lane_k_ball = next(e for e in states[k] if e.id == "ball_01")
            self.assertEqual(lane_0_ball.position.x, lane_k_ball.position.x)
            self.assertEqual(lane_0_ball.position.y, lane_k_ball.position.y)
            self.assertEqual(lane_0_ball.velocity.vx, lane_k_ball.velocity.vx)
            self.assertEqual(lane_0_ball.velocity.vy, lane_k_ball.velocity.vy)


if __name__ == "__main__":
    unittest.main()
