"""MLUE Machine-Accessible AI Interface

Provides high-level programmatic access for autonomous AI agents to discover schemas,
statically validate scene representations, initialize in-memory simulation sessions,
step physical trajectories with action vectors, inspect live states, and mutate entities.
"""

import uuid
from typing import Dict, Any, Optional, Union, List
from .model import (
    MLUEDocument,
    SimulationState,
    Entity,
    Position,
    Velocity,
    CircleSize,
    BoxSize,
)
from .loader import validate_and_parse, load_mlue, MLUEValidationError
from .engine import MLUEEngine


class MLUEAIInterface:
    """High-level programmatic interface for AI agents interacting with the MLUE substrate."""

    def __init__(self):
        self.engine = MLUEEngine()
        self._sessions: Dict[str, SimulationState] = {}

    def get_schema(self) -> Dict[str, Any]:
        """Returns the machine-readable schema definition and spatial invariant constraints."""
        return {
            "mlue_version": "1.6",
            "description": "MLUE Native AI Computational & Spatial Simulation Substrate",
            "root_fields": {
                "mlue_version": {"type": "string", "enum": ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6"]},
                "environment": {
                    "dimensions": {"type": "array", "items": "integer", "minItems": 2, "maxItems": 2, "description": "[width, height]"},
                    "background": {"type": "string", "description": "Hex color code e.g. #0F172A"}
                },
                "state_variables": {
                    "type": "object",
                    "description": "Hierarchical document state storage (nested objects, lists, scores, counters, flags)"
                },
                "entities": {
                    "type": "array",
                    "items": {
                        "id": {"type": "string", "unique": True},
                        "type": {"type": "string", "enum": ["circle", "box"]},
                        "position": {"x": "float in [0.0, 1.0]", "y": "float in [0.0, 1.0]"},
                        "size": {
                            "circle": {"radius": "float in (0.0, 0.5]"},
                            "box": {"width": "float in (0.0, 1.0]", "height": "float in (0.0, 1.0]"}
                        },
                        "velocity": {"vx": "float (optional, default 0.0)", "vy": "float (optional, default 0.0)"},
                        "properties": {
                            "color": "string hex color",
                            "solid": "boolean (enables pairwise collision reflection)",
                            "control": {
                                "channel": "string channel name (e.g. player_bottom, player_left)",
                                "axis": "x or y",
                                "speed": "positive float velocity multiplier"
                            }
                        },
                        "active": "boolean (optional, default true)"
                    }
                },
                "rules": {
                    "type": "array",
                    "items": {
                        "trigger": "string trigger name",
                        "event": "optional string (e.g. 'collision')",
                        "entities": "optional list of 2 entity IDs for collision events",
                        "condition": {
                            "entity": "string entity ID (for spatial/velocity conditions)",
                            "property": "position.x, position.y, velocity.vx, velocity.vy",
                            "state_variable": "string state variable name (for legacy flat state conditions)",
                            "state_path": "string dot/bracket keypath (e.g. 'session.stats.energy', 'inventory.length')",
                            "op": "<=, >=, ==, <, >, !=",
                            "value": "number, string, boolean, or literal"
                        },
                        "actions": [
                            {"type": "destroy_entity", "target": "entity ID"},
                            {"type": "set_property", "target": "entity ID", "property": "property_name", "value": "new_value"},
                            {"type": "increment", "target": "state_variable_name", "amount": "number"},
                            {"type": "set", "target": "state_variable_name", "value": "new_value"},
                            {"type": "set_path", "target": "dot/bracket keypath", "value": "new_value"},
                            {"type": "increment_path", "target": "dot/bracket keypath", "amount": "number"},
                            {"type": "push", "target": "array keypath", "value": "item_value"},
                            {"type": "pop", "target": "array keypath", "index": "optional int (default -1)"},
                            {"type": "delete_key", "target": "object keypath", "key": "optional string"},
                            {"type": "reset_entity", "target": "entity ID", "position": {"x": "float", "y": "float"}, "velocity": {"vx": "float", "vy": "float"}}
                        ]
                    }
                }
            },
            "spatial_invariants": {
                "left_boundary": "entity.position.x >= half_extent_x",
                "right_boundary": "entity.position.x <= 1.0 - half_extent_x",
                "top_boundary": "entity.position.y >= half_extent_y",
                "bottom_boundary": "entity.position.y <= 1.0 - half_extent_y"
            }
        }

    def validate_scene(self, data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Statically validates an MLUE document against syntax and spatial reachability invariants."""
        try:
            doc = load_mlue(data) if isinstance(data, str) else validate_and_parse(data)
            return {
                "valid": True,
                "version": doc.version,
                "environment": {"width": doc.environment.width, "height": doc.environment.height},
                "entity_count": len(doc.entities),
                "entities": [e.id for e in doc.entities],
                "state_variables": doc.state_variables,
                "rule_count": len(doc.rules),
            }
        except MLUEValidationError as e:
            return {
                "valid": False,
                "error": str(e),
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Unexpected validation failure: {str(e)}",
            }

    def create_session(self, data_or_path: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Initializes a new stateful simulation session in memory."""
        try:
            doc = load_mlue(data_or_path) if isinstance(data_or_path, str) else validate_and_parse(data_or_path)
            state = self.engine.init_simulation(doc)
            session_id = f"sim_{uuid.uuid4().hex[:8]}"
            self._sessions[session_id] = state
            return {
                "success": True,
                "session_id": session_id,
                "initial_state": self._serialize_state(state),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def step_session(
        self,
        session_id: str,
        dt: float = 0.0167,
        inputs: Optional[Dict[str, float]] = None,
        ticks: int = 1,
    ) -> Dict[str, Any]:
        """Advances an active simulation session by N ticks deterministically."""
        state = self._sessions.get(session_id)
        if state is None:
            return {"success": False, "error": f"Session '{session_id}' not found."}

        try:
            for _ in range(max(1, ticks)):
                state = self.engine.step(state, dt=dt, inputs=inputs)
            self._sessions[session_id] = state
            return {
                "success": True,
                "session_id": session_id,
                "ticks_evaluated": ticks,
                "state": self._serialize_state(state),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def inspect_session(self, session_id: str) -> Dict[str, Any]:
        """Returns the complete live state of an active simulation session."""
        state = self._sessions.get(session_id)
        if state is None:
            return {"success": False, "error": f"Session '{session_id}' not found."}

        return {
            "success": True,
            "session_id": session_id,
            "state": self._serialize_state(state),
        }

    def mutate_entity(
        self,
        session_id: str,
        entity_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Dynamically mutates an entity in an active simulation session."""
        state = self._sessions.get(session_id)
        if state is None:
            return {"success": False, "error": f"Session '{session_id}' not found."}

        found_idx = None
        for idx, e in enumerate(state.entities):
            if e.id == entity_id:
                found_idx = idx
                break

        if found_idx is None:
            return {"success": False, "error": f"Entity '{entity_id}' not found in session '{session_id}'."}

        curr = state.entities[found_idx]
        new_pos = curr.position
        new_vel = curr.velocity
        new_active = curr.active
        new_props = dict(curr.properties)

        if "position" in updates:
            p = updates["position"]
            new_pos = Position(x=float(p.get("x", new_pos.x)), y=float(p.get("y", new_pos.y)))
        if "velocity" in updates:
            v = updates["velocity"]
            new_vel = Velocity(vx=float(v.get("vx", new_vel.vx)), vy=float(v.get("vy", new_vel.vy)))
        if "active" in updates:
            new_active = bool(updates["active"])
        if "properties" in updates and isinstance(updates["properties"], dict):
            new_props.update(updates["properties"])

        updated_entities = list(state.entities)
        updated_entities[found_idx] = Entity(
            id=curr.id,
            type=curr.type,
            position=new_pos,
            size=curr.size,
            velocity=new_vel,
            properties=new_props,
            active=new_active,
        )

        new_shapes = self.engine._compute_shapes(state.environment, updated_entities)
        new_result = state.result.__class__(
            width=state.environment.width,
            height=state.environment.height,
            background=state.environment.background,
            shapes=new_shapes,
        )

        new_state = SimulationState(
            time=state.time,
            environment=state.environment,
            entities=updated_entities,
            result=new_result,
            state_variables=state.state_variables,
            rules=state.rules,
        )
        self._sessions[session_id] = new_state
        return {
            "success": True,
            "session_id": session_id,
            "entity": {
                "id": entity_id,
                "position": {"x": new_pos.x, "y": new_pos.y},
                "velocity": {"vx": new_vel.vx, "vy": new_vel.vy},
                "active": new_active,
                "properties": new_props,
            }
        }

    def close_session(self, session_id: str) -> Dict[str, Any]:
        """Terminates and removes an active simulation session from memory."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return {"success": True, "message": f"Session '{session_id}' closed."}
        return {"success": False, "error": f"Session '{session_id}' not found."}

    def _serialize_state(self, state: SimulationState) -> Dict[str, Any]:
        """Serializes a SimulationState into machine-friendly JSON dictionary."""
        entities_data = []
        for e in state.entities:
            entities_data.append({
                "id": e.id,
                "type": e.type,
                "position": {"x": round(e.position.x, 5), "y": round(e.position.y, 5)},
                "velocity": {"vx": round(e.velocity.vx, 5), "vy": round(e.velocity.vy, 5)},
                "active": e.active,
                "properties": e.properties,
            })

        shapes_data = []
        for s in state.result.shapes:
            shapes_data.append({
                "id": s.id,
                "type": s.type,
                "bbox": [round(coord, 2) for coord in s.bbox],
                "color": s.color,
            })

        return {
            "time": round(state.time, 5),
            "state_variables": state.state_variables,
            "entities": entities_data,
            "rendered_shapes": shapes_data,
        }
