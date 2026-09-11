"""MLUE Unit Tests: Zero-Copy Tensor & Vector Observation Bridge

Verifies contiguous buffer allocation, zero-copy in-place memory extraction,
zero heap allocation churn in the step loop, and batch buffer indexing.
"""

import unittest
import math
from runtime.model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    Velocity,
    CircleSize,
    BoxSize,
    SimulationState,
)
from runtime.engine import MLUEEngine
from runtime.tensor import (
    ObservationSpec,
    TensorObservationBuffer,
    BatchTensorObservationBuffer,
    HAS_NUMPY,
)

if HAS_NUMPY:
    import numpy as np


class TestTensorBridge(unittest.TestCase):
    """Verifies vector observation extraction from simulation states into contiguous float buffers."""

    def setUp(self):
        self.engine = MLUEEngine()
        self.env = Environment(width=200, height=200)

    def test_observation_spec_dimension_calculation(self):
        """Calculates exact vector dimensions based on tracked entities, sensors, and state variables."""
        spec = ObservationSpec(
            entity_ids=["robot", "goal"],
            include_velocities=True,   # 4 per entity (x, y, vx, vy) -> 8
            include_active=True,       # +1 per entity -> +2 -> 10
            lidar_entity_id="robot",
            lidar_num_rays=8,          # +8 rays -> 18
            state_variables=["score", "battery"], # +2 -> 20
        )
        self.assertEqual(spec.dimension, 20)

    def test_single_env_extraction_values(self):
        """Extracts entity positions, velocities, LiDAR readings, and state variables into contiguous buffer."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="agent",
                    type="circle",
                    position=Position(x=0.4, y=0.6),
                    size=CircleSize(radius=0.05),
                    velocity=Velocity(vx=0.25, vy=-0.5),
                    properties={},
                ),
                Entity(
                    id="target",
                    type="box",
                    position=Position(x=0.8, y=0.6),
                    size=BoxSize(width=0.1, height=0.1),
                    properties={},
                ),
            ],
            state_variables={"score": 100.0, "step": 42.0},
        )
        state = self.engine.init_simulation(doc)

        spec = ObservationSpec(
            entity_ids=["agent", "target"],
            include_velocities=True,
            include_active=False,
            lidar_entity_id="agent",
            lidar_num_rays=4,
            state_variables=["score", "step"],
        )
        # Expected dim: agent(4) + target(4) + lidar(4) + state_vars(2) = 14
        self.assertEqual(spec.dimension, 14)

        buf = TensorObservationBuffer(spec, use_numpy=True)
        obs = buf.extract(state, engine=self.engine)

        if HAS_NUMPY:
            self.assertIsInstance(obs, np.ndarray)
            self.assertEqual(obs.shape, (14,))
            self.assertEqual(obs.dtype, np.float32)
            # agent pos (x, y)
            self.assertAlmostEqual(obs[0], 0.4, places=5)
            self.assertAlmostEqual(obs[1], 0.6, places=5)
            # agent vel (vx, vy)
            self.assertAlmostEqual(obs[2], 0.25, places=5)
            self.assertAlmostEqual(obs[3], -0.5, places=5)
            # target pos (x, y)
            self.assertAlmostEqual(obs[4], 0.8, places=5)
            self.assertAlmostEqual(obs[5], 0.6, places=5)
            # state variables
            self.assertAlmostEqual(obs[12], 100.0, places=5)
            self.assertAlmostEqual(obs[13], 42.0, places=5)

    def test_zero_allocation_in_place_extraction(self):
        """Verifies buffer memory address remains identical across multiple step extractions."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="particle",
                    type="circle",
                    position=Position(x=0.5, y=0.5),
                    size=CircleSize(radius=0.02),
                    velocity=Velocity(vx=0.1, vy=0.1),
                )
            ],
        )
        state = self.engine.init_simulation(doc)

        spec = ObservationSpec(
            entity_ids=["particle"],
            include_velocities=True,
        )
        buf = TensorObservationBuffer(spec, use_numpy=True)

        obs1 = buf.extract(state, engine=self.engine)
        if HAS_NUMPY:
            ptr1 = obs1.__array_interface__["data"][0]

            for _ in range(100):
                state = self.engine.step(state, dt=0.01)
                obs_step = buf.extract(state, engine=self.engine)
                ptr_step = obs_step.__array_interface__["data"][0]
                # Memory address must be strictly identical (in-place write)
                self.assertEqual(ptr1, ptr_step)

    def test_batch_observation_buffer(self):
        """Extracts states across multiple parallel environments into a single 2D contiguous array."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="e1",
                    type="circle",
                    position=Position(x=0.5, y=0.5),
                    size=CircleSize(radius=0.05),
                )
            ],
        )
        spec = ObservationSpec(entity_ids=["e1"], include_velocities=False)
        self.assertEqual(spec.dimension, 2)

        batch_buf = BatchTensorObservationBuffer(num_envs=3, spec=spec, use_numpy=True)

        # State 0: pos=(0.1, 0.2)
        s0 = self.engine.init_simulation(doc)
        s0 = SimulationState(
            time=0.0, environment=self.env,
            entities=[Entity(id="e1", type="circle", position=Position(x=0.1, y=0.2), size=CircleSize(radius=0.05))],
            result=s0.result, state_variables={}, rules=[]
        )

        # State 1: pos=(0.3, 0.4)
        s1 = SimulationState(
            time=0.0, environment=self.env,
            entities=[Entity(id="e1", type="circle", position=Position(x=0.3, y=0.4), size=CircleSize(radius=0.05))],
            result=s0.result, state_variables={}, rules=[]
        )

        # State 2: pos=(0.5, 0.6)
        s2 = SimulationState(
            time=0.0, environment=self.env,
            entities=[Entity(id="e1", type="circle", position=Position(x=0.5, y=0.6), size=CircleSize(radius=0.05))],
            result=s0.result, state_variables={}, rules=[]
        )

        batch_buf.extract_env(0, s0, engine=self.engine)
        batch_buf.extract_env(1, s1, engine=self.engine)
        batch_buf.extract_env(2, s2, engine=self.engine)

        batch_obs = batch_buf.get_batch()
        if HAS_NUMPY:
            self.assertEqual(batch_obs.shape, (3, 2))
            self.assertAlmostEqual(batch_obs[0, 0], 0.1, places=5)
            self.assertAlmostEqual(batch_obs[0, 1], 0.2, places=5)
            self.assertAlmostEqual(batch_obs[1, 0], 0.3, places=5)
            self.assertAlmostEqual(batch_obs[1, 1], 0.4, places=5)
            self.assertAlmostEqual(batch_obs[2, 0], 0.5, places=5)
            self.assertAlmostEqual(batch_obs[2, 1], 0.6, places=5)


if __name__ == "__main__":
    unittest.main()
