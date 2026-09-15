"""MLUE PettingZoo ParallelEnv Multi-Agent Swarm Adapter.

Provides a multi-agent parallel environment wrapper around MLUE simulation documents
for training multi-agent reinforcement learning (MARL) policies and cooperative/competitive swarms.
Adheres strictly to Tier L1 Substrate Decoupling (Standard Library only, optional PettingZoo wrapper).
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from mlue.model import MLUEDocument, SimulationState
from mlue.loader import load_mlue, validate_and_parse
from mlue.engine import MLUEEngine
from mlue.tensor import ObservationSpec, TensorObservationBuffer, HAS_NUMPY
from mlue.gym import spaces

if HAS_NUMPY:
    import numpy as np

try:
    from pettingzoo import ParallelEnv
    HAS_PETTINGZOO = True
except ImportError:
    HAS_PETTINGZOO = False

    class ParallelEnv:
        """Lightweight stdlib fallback for pettingzoo.ParallelEnv."""
        pass


class MLUEParallelEnv(ParallelEnv):
    """Multi-agent parallel environment wrapper for MLUE simulation scenes."""

    def __init__(
        self,
        mlue_source: Union[str, MLUEDocument, Dict[str, Any]],
        agent_configs: Dict[str, Dict[str, Any]],
        dt: float = 0.0167,
        max_episode_steps: int = 1000,
        use_numpy: bool = True,
    ):
        super().__init__()
        self.engine = MLUEEngine()

        if isinstance(mlue_source, MLUEDocument):
            self._initial_doc = mlue_source
        elif isinstance(mlue_source, str):
            self._initial_doc = load_mlue(mlue_source)
        elif isinstance(mlue_source, dict):
            self._initial_doc = validate_and_parse(mlue_source)
        else:
            raise TypeError(f"Unsupported MLUE document source type: {type(mlue_source)}")

        self.dt = dt
        self.max_episode_steps = max_episode_steps
        self.possible_agents = sorted(list(agent_configs.keys()))
        self.agents = list(self.possible_agents)

        self._agent_configs = agent_configs
        self._obs_buffers: Dict[str, TensorObservationBuffer] = {}
        self.observation_spaces: Dict[str, Any] = {}
        self.action_spaces: Dict[str, Any] = {}

        for agent_id, cfg in agent_configs.items():
            channels = cfg.get("action_channels", [f"{agent_id}_axis"])
            self.action_spaces[agent_id] = spaces.Box(
                low=-1.0, high=1.0, shape=(len(channels),), dtype=np.float32 if HAS_NUMPY else float
            )

            spec = cfg.get("obs_spec")
            if spec is None:
                spec = ObservationSpec(
                    entity_ids=[agent_id],
                    include_velocities=True,
                    lidar_entity_id=agent_id if cfg.get("lidar_rays", 0) > 0 else None,
                    lidar_num_rays=cfg.get("lidar_rays", 0),
                )
            self._obs_buffers[agent_id] = TensorObservationBuffer(spec, use_numpy=use_numpy)
            self.observation_spaces[agent_id] = spaces.Box(
                low=-float("inf"), high=float("inf"), shape=(spec.dimension,), dtype=np.float32 if HAS_NUMPY else float
            )

        self.state: Optional[SimulationState] = None
        self.current_step = 0

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Resets multi-agent world and returns per-agent observation dictionary."""
        self.state = self.engine.init_simulation(self._initial_doc)
        self.agents = list(self.possible_agents)
        self.current_step = 0

        obs_dict = {
            agent: self._obs_buffers[agent].extract(self.state, engine=self.engine)
            for agent in self.agents
        }
        info_dict = {agent: {"step": 0} for agent in self.agents}
        return obs_dict, info_dict

    def step(
        self,
        actions: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Dict[str, float], Dict[str, bool], Dict[str, bool], Dict[str, Any]]:
        """Advances multi-agent world with joint actions from active agents."""
        if self.state is None:
            raise RuntimeError("Cannot call step() before reset().")

        # Aggregate inputs from all active agents
        inputs: Dict[str, float] = {}
        for agent_id, act in actions.items():
            cfg = self._agent_configs.get(agent_id, {})
            channels = cfg.get("action_channels", [f"{agent_id}_axis"])
            act_list = [float(a) for a in act] if hasattr(act, "__iter__") else [float(act)]
            for i, ch in enumerate(channels):
                val = act_list[i] if i < len(act_list) else 0.0
                inputs[ch] = max(-1.0, min(1.0, val))

        self.state = self.engine.step(self.state, dt=self.dt, inputs=inputs)
        self.current_step += 1

        is_term = bool(self.state.terminated)
        is_trunc = bool(self.state.truncated or (self.current_step >= self.max_episode_steps))

        obs_dict = {}
        rewards_dict = {}
        terminations_dict = {}
        truncations_dict = {}
        infos_dict = {}

        # Default cooperative reward sharing or agent-specific rewards
        step_reward = float(self.state.step_reward)

        for agent in list(self.agents):
            obs_dict[agent] = self._obs_buffers[agent].extract(self.state, engine=self.engine)
            rewards_dict[agent] = step_reward
            terminations_dict[agent] = is_term
            truncations_dict[agent] = is_trunc
            infos_dict[agent] = {"step": self.current_step}

        if is_term or is_trunc:
            self.agents = []

        return obs_dict, rewards_dict, terminations_dict, truncations_dict, infos_dict
