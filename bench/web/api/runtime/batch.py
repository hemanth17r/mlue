"""MLUE Vectorized Batch Environment Orchestrator.

Provides high-throughput multi-agent parallel simulation for AI training,
Monte Carlo Tree Search (MCTS), and automated benchmarking.
Adheres strictly to Tier L1 Substrate Decoupling (Standard Library only).
"""

import copy
from typing import List, Dict, Any, Optional
from runtime.model import MLUEDocument, Entity, Environment, Velocity
from runtime.native_core import NativeCore


class BatchEnvironmentPool:
    """Manages M independent parallel simulation instances with atomic batch step/reset."""

    def __init__(self, doc: MLUEDocument, num_envs: int = 100):
        if num_envs <= 0:
            raise ValueError("num_envs must be at least 1")

        self.template_doc = doc
        self.num_envs = num_envs
        self.env_config = doc.environment

        # Initialize M independent entity state lists
        self.lane_entities: List[List[Entity]] = [
            copy.deepcopy(doc.entities) for _ in range(num_envs)
        ]
        self.lane_state_vars: List[Dict[str, Any]] = [
            copy.deepcopy(doc.state_variables) for _ in range(num_envs)
        ]
        self.step_counts: List[int] = [0 for _ in range(num_envs)]

    def step(
        self,
        actions_by_lane: Optional[Dict[int, Dict[str, float]]] = None,
        dt: float = 1.0 / 60.0,
    ) -> List[List[Entity]]:
        """Simulates all M environments forward by dt in a single vectorized batch pass."""
        # 1. Apply independent control actions to specific lanes
        if actions_by_lane:
            for lane_idx, actions in actions_by_lane.items():
                if 0 <= lane_idx < self.num_envs:
                    new_entities = []
                    for entity in self.lane_entities[lane_idx]:
                        ctrl = entity.properties.get("control")
                        if isinstance(ctrl, dict):
                            ch = ctrl.get("channel")
                            axis = ctrl.get("axis", "x")
                            if ch in actions:
                                val = actions[ch]
                                new_vx = val if axis == "x" else entity.velocity.vx
                                new_vy = val if axis == "y" else entity.velocity.vy
                                entity = Entity(
                                    id=entity.id,
                                    type=entity.type,
                                    position=entity.position,
                                    size=entity.size,
                                    velocity=Velocity(vx=new_vx, vy=new_vy),
                                    properties=entity.properties,
                                    active=entity.active,
                                )
                        new_entities.append(entity)
                    self.lane_entities[lane_idx] = new_entities

        # 2. Vectorized Step
        self.lane_entities = NativeCore.step_batch(
            self.lane_entities, self.env_config, dt=dt
        )

        for i in range(self.num_envs):
            self.step_counts[i] += 1

        return self.lane_entities

    def reset(self, lane_indices: Optional[List[int]] = None) -> None:
        """Resets specified lanes (or all lanes if None) back to template initial state."""
        targets = lane_indices if lane_indices is not None else range(self.num_envs)
        for idx in targets:
            if 0 <= idx < self.num_envs:
                self.lane_entities[idx] = copy.deepcopy(self.template_doc.entities)
                self.lane_state_vars[idx] = copy.deepcopy(self.template_doc.state_variables)
                self.step_counts[idx] = 0

    def get_states(self) -> List[List[Entity]]:
        """Returns deep copies of entity lists across all active lanes."""
        return [list(entities) for entities in self.lane_entities]

    def get_step_counts(self) -> List[int]:
        return list(self.step_counts)
