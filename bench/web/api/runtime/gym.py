"""MLUE Standard Gymnasium Environment Adapter.

Provides a drop-in standard gymnasium.Env interface for training reinforcement learning
agents on MLUE simulation documents. Adheres strictly to Tier L1 Substrate Decoupling
with a pure Python stdlib fallback when gymnasium is not installed.
"""

import math
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from runtime.model import MLUEDocument, SimulationState
from runtime.loader import load_mlue, validate_and_parse
from runtime.engine import MLUEEngine
from runtime.tensor import ObservationSpec, TensorObservationBuffer, HAS_NUMPY

if HAS_NUMPY:
    import numpy as np

# Detect optional gymnasium installation
try:
    import gymnasium as gym
    from gymnasium import spaces
    HAS_GYMNASIUM = True
    BaseEnv = gym.Env
except ImportError:
    HAS_GYMNASIUM = False

    class BaseEnv:
        """Lightweight stdlib fallback for gymnasium.Env."""
        pass

    class DummySpaces:
        """Lightweight stdlib fallback spaces mirroring gymnasium.spaces."""
        class Box:
            def __init__(self, low: float, high: float, shape: Tuple[int, ...], dtype=None):
                self.low = low
                self.high = high
                self.shape = shape
                self.dtype = dtype or (np.float32 if HAS_NUMPY else float)

            def sample(self) -> Union["np.ndarray", List[float]]:
                if HAS_NUMPY:
                    return np.random.uniform(self.low, self.high, size=self.shape).astype(self.dtype)
                return [random.uniform(self.low, self.high) for _ in range(self.shape[0])]

        class Discrete:
            def __init__(self, n: int, start: int = 0):
                self.n = n
                self.start = start

            def sample(self) -> int:
                return random.randint(self.start, self.start + self.n - 1)

    spaces = DummySpaces()


class MLUEGymEnv(BaseEnv):
    """Standard single-agent Gymnasium environment wrapper around an MLUE simulation document."""

    metadata = {"render_modes": ["headless"], "render_fps": 60}

    def __init__(
        self,
        mlue_source: Union[str, Path, MLUEDocument, Dict[str, Any]],
        obs_spec: Optional[ObservationSpec] = None,
        action_channels: Optional[List[str]] = None,
        dt: float = 0.0167,
        continuous_actions: bool = True,
        max_episode_steps: int = 1000,
        use_numpy: bool = True,
    ):
        super().__init__()
        self.engine = MLUEEngine()

        # Parse document
        if isinstance(mlue_source, MLUEDocument):
            self._initial_doc = mlue_source
        elif isinstance(mlue_source, (str, Path)):
            self._initial_doc = load_mlue(mlue_source)
        elif isinstance(mlue_source, dict):
            self._initial_doc = validate_and_parse(mlue_source)
        else:
            raise TypeError(f"Unsupported MLUE document source type: {type(mlue_source)}")

        self.dt = dt
        self.max_episode_steps = max_episode_steps
        self.continuous_actions = continuous_actions

        # Discover action channels from document if not explicitly provided
        if action_channels is not None:
            self.action_channels = list(action_channels)
        else:
            discovered = set()
            for ent in self._initial_doc.entities:
                ctrl = ent.properties.get("control")
                if isinstance(ctrl, dict) and "channel" in ctrl:
                    discovered.add(ctrl["channel"])
            self.action_channels = sorted(list(discovered))
            if not self.action_channels:
                self.action_channels = ["default_channel"]

        # Configure action space
        self.num_actions = len(self.action_channels)
        if self.continuous_actions:
            self.action_space = spaces.Box(
                low=-1.0, high=1.0, shape=(self.num_actions,), dtype=np.float32 if HAS_NUMPY else float
            )
        else:
            # Discrete space with 3 actions per channel: [-1.0, 0.0, 1.0]
            self.action_space = spaces.Discrete(3 ** self.num_actions)

        # Configure observation specification and space
        if obs_spec is not None:
            self.obs_spec = obs_spec
        else:
            active_ids = [e.id for e in self._initial_doc.entities if e.active]
            self.obs_spec = ObservationSpec(
                entity_ids=active_ids,
                include_velocities=True,
                include_active=False,
                state_variables=list(self._initial_doc.state_variables.keys()),
            )

        self._obs_buffer = TensorObservationBuffer(self.obs_spec, use_numpy=use_numpy)
        self.observation_space = spaces.Box(
            low=-float("inf"),
            high=float("inf"),
            shape=(self.obs_spec.dimension,),
            dtype=np.float32 if HAS_NUMPY else float,
        )

        # Session tracking state
        self.state: Optional[SimulationState] = None
        self.current_step = 0
        self.cumulative_reward = 0.0

    def _get_obs(self) -> Union["np.ndarray", memoryview]:
        """Extracts observation from current simulation state using the zero-allocation buffer."""
        return self._obs_buffer.extract(self.state, engine=self.engine)

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Union["np.ndarray", memoryview], Dict[str, Any]]:
        """Resets simulation to initial state and returns initial observation."""
        if seed is not None:
            random.seed(seed)
            if HAS_NUMPY:
                np.random.seed(seed)

        self.state = self.engine.init_simulation(self._initial_doc)
        self.current_step = 0
        self.cumulative_reward = 0.0

        obs = self._get_obs()
        info = {
            "time": self.state.time,
            "step": 0,
            "entities": len(self.state.entities),
        }
        return obs, info

    def step(
        self,
        action: Union[float, int, List[float], "np.ndarray"],
    ) -> Tuple[Union["np.ndarray", memoryview], float, bool, bool, Dict[str, Any]]:
        """Advances simulation by one dt step with given agent action."""
        if self.state is None:
            raise RuntimeError("Cannot call step() before reset().")

        # Map action into input channels
        inputs: Dict[str, float] = {}
        if self.continuous_actions:
            if isinstance(action, (int, float)):
                action_list = [float(action)]
            else:
                action_list = [float(a) for a in action]

            for i, channel in enumerate(self.action_channels):
                val = action_list[i] if i < len(action_list) else 0.0
                inputs[channel] = max(-1.0, min(1.0, val))
        else:
            # Decode discrete integer index into trinary vector {-1, 0, 1}
            action_int = int(action)
            for i, channel in enumerate(self.action_channels):
                val_idx = (action_int // (3 ** i)) % 3
                # 0 -> -1.0, 1 -> 0.0, 2 -> 1.0
                inputs[channel] = float(val_idx - 1)

        # Advance deterministic engine
        self.state = self.engine.step(self.state, dt=self.dt, inputs=inputs)
        self.current_step += 1

        reward = float(self.state.step_reward)
        self.cumulative_reward += reward

        terminated = bool(self.state.terminated)
        truncated = bool(self.state.truncated or (self.current_step >= self.max_episode_steps))

        obs = self._get_obs()
        info = {
            "time": round(self.state.time, 5),
            "step": self.current_step,
            "cumulative_reward": round(self.cumulative_reward, 5),
            "state_variables": self.state.state_variables,
        }

        return obs, reward, terminated, truncated, info

    def render(self) -> None:
        """Headless environment: rendering is a no-op."""
        pass

    def close(self) -> None:
        """Cleanly releases simulation resources."""
        self.state = None
