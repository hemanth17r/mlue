"""MLUE Zero-Copy Vector & Tensor Observation Bridge.

Provides high-throughput contiguous float32 buffer allocation and in-place state
vector extraction for reinforcement learning policies and PyTorch/NumPy training loops.
Eliminates JSON serialization overhead with zero heap allocations in the step loop.
Adheres strictly to Tier L1 Substrate Decoupling (Standard Library only, optional NumPy wrapper).
"""

import math
import ctypes
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union, Tuple
from mlue.model import SimulationState, Entity
from mlue.engine import MLUEEngine

# Optional zero-copy NumPy integration
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@dataclass(frozen=True)
class ObservationSpec:
    """Declares which entities, sensors, and state variables are extracted into the observation vector."""
    entity_ids: List[str]
    include_velocities: bool = True
    include_active: bool = False
    lidar_entity_id: Optional[str] = None
    lidar_num_rays: int = 0
    lidar_max_range: float = 1.0
    state_variables: List[str] = field(default_factory=list)

    @property
    def dimension(self) -> int:
        """Calculates exact total number of float32 values in the observation vector."""
        floats_per_entity = 2  # (x, y)
        if self.include_velocities:
            floats_per_entity += 2  # (vx, vy)
        if self.include_active:
            floats_per_entity += 1  # active flag

        dim = len(self.entity_ids) * floats_per_entity
        dim += max(0, self.lidar_num_rays)
        dim += len(self.state_variables)
        return dim


class TensorObservationBuffer:
    """Pre-allocated contiguous float32 memory buffer for zero-allocation observation extraction."""

    def __init__(self, spec: ObservationSpec, use_numpy: bool = True):
        self.spec = spec
        self.dim = spec.dimension
        self._c_array = (ctypes.c_float * self.dim)()
        self._mem_view = memoryview(self._c_array).cast('B').cast('f')
        self._use_numpy = use_numpy and HAS_NUMPY
        if self._use_numpy:
            self._np_view = np.frombuffer(self._c_array, dtype=np.float32)
        else:
            self._np_view = None

    def extract(
        self,
        state: SimulationState,
        engine: Optional[MLUEEngine] = None,
    ) -> Union["np.ndarray", memoryview]:
        """Extracts simulation state directly into the pre-allocated contiguous buffer. Zero allocations."""
        entity_map = {e.id: e for e in state.entities}
        idx = 0

        # 1. Extract entity spatial and kinematic coordinates
        for ent_id in self.spec.entity_ids:
            ent = entity_map.get(ent_id)
            if ent is not None:
                self._c_array[idx] = ctypes.c_float(ent.position.x)
                self._c_array[idx + 1] = ctypes.c_float(ent.position.y)
                idx += 2

                if self.spec.include_velocities:
                    self._c_array[idx] = ctypes.c_float(ent.velocity.vx)
                    self._c_array[idx + 1] = ctypes.c_float(ent.velocity.vy)
                    idx += 2

                if self.spec.include_active:
                    self._c_array[idx] = ctypes.c_float(1.0 if ent.active else 0.0)
                    idx += 1
            else:
                # Missing entity fallback (0.0 fill)
                fill_count = 2 + (2 if self.spec.include_velocities else 0) + (1 if self.spec.include_active else 0)
                for f in range(fill_count):
                    self._c_array[idx + f] = ctypes.c_float(0.0)
                idx += fill_count

        # 2. Extract LiDAR raycast sensor readings
        if self.spec.lidar_num_rays > 0:
            lidar_ent = entity_map.get(self.spec.lidar_entity_id or "")
            if lidar_ent is not None and engine is not None:
                origin = (lidar_ent.position.x, lidar_ent.position.y)
                distances = engine.cast_lidar(
                    state,
                    origin=origin,
                    num_rays=self.spec.lidar_num_rays,
                    max_range=self.spec.lidar_max_range,
                    ignore_ids={lidar_ent.id},
                )
                for d in distances:
                    self._c_array[idx] = ctypes.c_float(d)
                    idx += 1
            else:
                for _ in range(self.spec.lidar_num_rays):
                    self._c_array[idx] = ctypes.c_float(self.spec.lidar_max_range)
                    idx += 1

        # 3. Extract scalar state variables
        for var_name in self.spec.state_variables:
            val = state.state_variables.get(var_name, 0.0)
            try:
                self._c_array[idx] = ctypes.c_float(float(val))
            except (ValueError, TypeError):
                self._c_array[idx] = ctypes.c_float(0.0)
            idx += 1

        if self._use_numpy:
            return self._np_view
        return self._mem_view


class BatchTensorObservationBuffer:
    """Pre-allocated contiguous float32 2D buffer for parallel multi-environment rollouts."""

    def __init__(self, num_envs: int, spec: ObservationSpec, use_numpy: bool = True):
        self.num_envs = num_envs
        self.spec = spec
        self.dim = spec.dimension
        self.total_floats = num_envs * self.dim
        self._c_array = (ctypes.c_float * self.total_floats)()
        self._mem_view = memoryview(self._c_array).cast('B').cast('f', shape=[num_envs, self.dim])
        self._use_numpy = use_numpy and HAS_NUMPY
        if self._use_numpy:
            self._np_view = np.frombuffer(self._c_array, dtype=np.float32).reshape((num_envs, self.dim))
        else:
            self._np_view = None

        # Reusable single-env buffer to avoid allocations during extraction
        self._env_buffers = [
            TensorObservationBuffer(spec, use_numpy=False)
            for _ in range(num_envs)
        ]

    def extract_env(
        self,
        env_idx: int,
        state: SimulationState,
        engine: Optional[MLUEEngine] = None,
    ) -> None:
        """Extracts single environment state into its respective row in the batch buffer."""
        if not (0 <= env_idx < self.num_envs):
            raise IndexError(f"Environment index {env_idx} out of range [0, {self.num_envs}).")

        buf = self._env_buffers[env_idx]
        buf.extract(state, engine=engine)
        offset = env_idx * self.dim
        for i in range(self.dim):
            self._c_array[offset + i] = buf._c_array[i]

    def get_batch(self) -> Union["np.ndarray", memoryview]:
        """Returns zero-copy view of the complete batch observation array."""
        if self._use_numpy:
            return self._np_view
        return self._mem_view
