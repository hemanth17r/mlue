"""MLUE Phase 0.6 Document Loader & Validator

Loads machine-oriented MLUE specifications and verifies semantic constraints.
Supports MLUE schema versions 0.1, 0.2, 0.3, 0.4, 0.5, and 0.6.
"""

import json
import math
from pathlib import Path
from typing import Union, Dict, Any, List, Optional, Tuple
from .model import (
    MLUEDocument,
    Entity,
    Position,
    CircleSize,
    BoxSize,
    Velocity,
    Environment,
    Condition,
    Action,
    Rule,
)


class MLUEValidationError(Exception):
    """Raised when an MLUE document fails schema or semantic validation."""
    pass


def load_mlue(source: Union[str, Path, Dict[str, Any]]) -> MLUEDocument:
    """Load and validate an MLUE document from a file path, JSON string, or dict."""
    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.exists() and path.is_file():
            with open(path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    raise MLUEValidationError(f"Invalid JSON in MLUE document: {e}") from e
        else:
            # Try interpreting source as raw JSON string if not an existing file
            if isinstance(source, str) and source.strip().startswith("{"):
                try:
                    data = json.loads(source)
                except json.JSONDecodeError as e:
                    raise MLUEValidationError(f"Invalid JSON string in MLUE document: {e}") from e
            else:
                raise MLUEValidationError(f"MLUE file not found: {source}")
    elif isinstance(source, dict):
        data = source
    else:
        raise MLUEValidationError(f"Unsupported MLUE source type: {type(source)}")

    return validate_and_parse(data)


def validate_and_parse(data: Dict[str, Any]) -> MLUEDocument:
    """Validate raw dictionary structure against MLUE specification schema."""
    if not isinstance(data, dict):
        raise MLUEValidationError("MLUE document root must be a dictionary/object.")

    version = data.get("mlue_version")
    if version not in ("0.1", "0.2", "0.3", "0.4", "0.5", "0.6"):
        raise MLUEValidationError(
            f"Unsupported MLUE version '{version}'. Expected '0.1', '0.2', '0.3', '0.4', '0.5', or '0.6'."
        )

    # Environment
    env_data = data.get("environment", {})
    if not isinstance(env_data, dict):
        raise MLUEValidationError("'environment' must be an object.")

    dims = env_data.get("dimensions", [400, 400])
    if not (isinstance(dims, list) and len(dims) == 2 and all(isinstance(d, int) and d > 0 for d in dims)):
        raise MLUEValidationError("'environment.dimensions' must be a list of two positive integers [width, height].")

    background = env_data.get("background", "#0F172A")
    if not isinstance(background, str):
        raise MLUEValidationError("'environment.background' must be a color string.")

    environment = Environment(width=dims[0], height=dims[1], background=background)

    # State Variables
    state_variables_raw = data.get("state_variables", {})
    if not isinstance(state_variables_raw, dict):
        raise MLUEValidationError("'state_variables' must be a dictionary.")
    state_variables = dict(state_variables_raw)

    # Entities
    entities_data = data.get("entities")
    if not isinstance(entities_data, list) or len(entities_data) == 0:
        raise MLUEValidationError("'entities' must be a non-empty list of entity objects.")

    entities: List[Entity] = []
    seen_ids = set()

    for idx, ent_raw in enumerate(entities_data):
        if not isinstance(ent_raw, dict):
            raise MLUEValidationError(f"Entity at index {idx} must be an object.")

        ent_id = ent_raw.get("id")
        if not (isinstance(ent_id, str) and ent_id.strip()):
            raise MLUEValidationError(f"Entity at index {idx} requires a non-empty 'id' string.")

        if ent_id in seen_ids:
            raise MLUEValidationError(f"Duplicate entity id '{ent_id}' found at index {idx}.")
        seen_ids.add(ent_id)

        ent_type = ent_raw.get("type")
        if ent_type not in ("circle", "box"):
            raise MLUEValidationError(
                f"Entity '{ent_id}' has unsupported type '{ent_type}'. Supported types: 'circle', 'box'."
            )

        # Active state (default True)
        active = bool(ent_raw.get("active", True))

        # Position
        pos_raw = ent_raw.get("position")
        if not isinstance(pos_raw, dict):
            raise MLUEValidationError(f"Entity '{ent_id}' requires a 'position' object.")

        x = pos_raw.get("x")
        y = pos_raw.get("y")
        if not (isinstance(x, (int, float)) and not math.isnan(x) and 0.0 <= x <= 1.0):
            raise MLUEValidationError(f"Entity '{ent_id}' position.x must be a number in range [0.0, 1.0] (got {x}).")
        if not (isinstance(y, (int, float)) and not math.isnan(y) and 0.0 <= y <= 1.0):
            raise MLUEValidationError(f"Entity '{ent_id}' position.y must be a number in range [0.0, 1.0] (got {y}).")

        # Size
        size_raw = ent_raw.get("size")
        if not isinstance(size_raw, dict):
            raise MLUEValidationError(f"Entity '{ent_id}' requires a 'size' object.")

        if ent_type == "circle":
            radius = size_raw.get("radius")
            if not (isinstance(radius, (int, float)) and not math.isnan(radius) and 0.0 < radius <= 0.5):
                raise MLUEValidationError(
                    f"Entity '{ent_id}' size.radius must be a number in range (0.0, 0.5] (got {radius})."
                )
            size = CircleSize(radius=float(radius))
        elif ent_type == "box":
            width = size_raw.get("width")
            height = size_raw.get("height")
            if not (isinstance(width, (int, float)) and not math.isnan(width) and 0.0 < width <= 1.0):
                raise MLUEValidationError(
                    f"Entity '{ent_id}' size.width must be a number in range (0.0, 1.0] (got {width})."
                )
            if not (isinstance(height, (int, float)) and not math.isnan(height) and 0.0 < height <= 1.0):
                raise MLUEValidationError(
                    f"Entity '{ent_id}' size.height must be a number in range (0.0, 1.0] (got {height})."
                )
            size = BoxSize(width=float(width), height=float(height))

        # Velocity (Optional)
        vel_raw = ent_raw.get("velocity", {})
        if not isinstance(vel_raw, dict):
            raise MLUEValidationError(f"Entity '{ent_id}' 'velocity' must be an object if specified.")

        vx = vel_raw.get("vx", 0.0)
        vy = vel_raw.get("vy", 0.0)
        if not (isinstance(vx, (int, float)) and not math.isnan(vx) and not math.isinf(vx)):
            raise MLUEValidationError(f"Entity '{ent_id}' velocity.vx must be a finite number (got {vx}).")
        if not (isinstance(vy, (int, float)) and not math.isnan(vy) and not math.isinf(vy)):
            raise MLUEValidationError(f"Entity '{ent_id}' velocity.vy must be a finite number (got {vy}).")

        velocity = Velocity(vx=float(vx), vy=float(vy))

        # Properties
        properties = ent_raw.get("properties", {})
        if not isinstance(properties, dict):
            raise MLUEValidationError(f"Entity '{ent_id}' 'properties' must be a dictionary.")

        if "solid" in properties and not isinstance(properties["solid"], bool):
            raise MLUEValidationError(f"Entity '{ent_id}' properties.solid must be a boolean.")

        # Control Configuration
        if "control" in properties:
            ctrl = properties["control"]
            if not isinstance(ctrl, dict):
                raise MLUEValidationError(f"Entity '{ent_id}' properties.control must be an object.")
            channel = ctrl.get("channel")
            if not (isinstance(channel, str) and channel.strip()):
                raise MLUEValidationError(f"Entity '{ent_id}' control.channel must be a non-empty string.")
            axis = ctrl.get("axis")
            if axis not in ("x", "y"):
                raise MLUEValidationError(f"Entity '{ent_id}' control.axis must be 'x' or 'y' (got '{axis}').")
            speed = ctrl.get("speed")
            if not (isinstance(speed, (int, float)) and not math.isnan(speed) and speed > 0.0):
                raise MLUEValidationError(f"Entity '{ent_id}' control.speed must be a positive number (got {speed}).")

        entity = Entity(
            id=ent_id,
            type=ent_type,
            position=Position(x=float(x), y=float(y)),
            size=size,
            velocity=velocity,
            properties=dict(properties),
            active=active,
        )
        entities.append(entity)

    # Rules Validation
    rules_data = data.get("rules", [])
    if not isinstance(rules_data, list):
        raise MLUEValidationError("'rules' must be a list of rule objects.")

    rules: List[Rule] = []
    for r_idx, rule_raw in enumerate(rules_data):
        if not isinstance(rule_raw, dict):
            raise MLUEValidationError(f"Rule at index {r_idx} must be an object.")

        trigger = rule_raw.get("trigger", f"rule_{r_idx}")
        if not isinstance(trigger, str):
            raise MLUEValidationError(f"Rule at index {r_idx} 'trigger' must be a string.")

        event_name = rule_raw.get("event")
        entities_pair: Optional[Tuple[str, str]] = None
        condition: Optional[Condition] = None

        if event_name is not None:
            if event_name != "collision":
                raise MLUEValidationError(
                    f"Rule '{trigger}' event '{event_name}' is unsupported. Supported: 'collision'."
                )
            pair_raw = rule_raw.get("entities")
            if not (isinstance(pair_raw, list) and len(pair_raw) == 2 and all(isinstance(e, str) for e in pair_raw)):
                raise MLUEValidationError(
                    f"Rule '{trigger}' collision event requires 'entities' list of two entity IDs."
                )
            for ent_ref in pair_raw:
                if ent_ref not in seen_ids:
                    raise MLUEValidationError(
                        f"Rule '{trigger}' collision event targets unknown entity '{ent_ref}'."
                    )
            entities_pair = (pair_raw[0], pair_raw[1])
        else:
            cond_raw = rule_raw.get("condition")
            if not isinstance(cond_raw, dict):
                raise MLUEValidationError(f"Rule '{trigger}' requires either an 'event' or 'condition' object.")

            op = cond_raw.get("op", "==")
            if op not in ("<=", ">=", "==", "<", ">"):
                raise MLUEValidationError(
                    f"Rule '{trigger}' condition op '{op}' is invalid. Supported: <=, >=, ==, <, >."
                )

            val = cond_raw.get("value")

            if "state_variable" in cond_raw:
                sv_name = cond_raw["state_variable"]
                if sv_name not in state_variables:
                    raise MLUEValidationError(
                        f"Rule '{trigger}' condition targets unknown state_variable '{sv_name}'."
                    )
                condition = Condition(state_variable=sv_name, op=op, value=val)
            else:
                target_ent = cond_raw.get("entity")
                if target_ent not in seen_ids:
                    raise MLUEValidationError(
                        f"Rule '{trigger}' condition targets unknown entity '{target_ent}'."
                    )

                prop_name = cond_raw.get("property")
                if prop_name not in ("position.x", "position.y", "velocity.vx", "velocity.vy"):
                    raise MLUEValidationError(
                        f"Rule '{trigger}' condition property '{prop_name}' is invalid."
                    )
                if not (isinstance(val, (int, float)) and not math.isnan(val)):
                    raise MLUEValidationError(f"Rule '{trigger}' condition 'value' must be a finite number.")

                condition = Condition(entity=target_ent, property=prop_name, op=op, value=float(val))

        actions_data = rule_raw.get("actions")
        if not isinstance(actions_data, list) or len(actions_data) == 0:
            raise MLUEValidationError(f"Rule '{trigger}' requires a non-empty 'actions' list.")

        actions: List[Action] = []
        for a_idx, act_raw in enumerate(actions_data):
            if not isinstance(act_raw, dict):
                raise MLUEValidationError(f"Rule '{trigger}' action at index {a_idx} must be an object.")

            act_type = act_raw.get("type")
            target = act_raw.get("target")

            if act_type in ("destroy_entity", "deactivate_entity"):
                if target not in seen_ids:
                    raise MLUEValidationError(
                        f"Rule '{trigger}' {act_type} action targets unknown entity '{target}'."
                    )
                actions.append(Action(type="destroy_entity", target=target))
            elif act_type == "set_property":
                if target not in seen_ids:
                    raise MLUEValidationError(
                        f"Rule '{trigger}' set_property action targets unknown entity '{target}'."
                    )
                prop_key = act_raw.get("property")
                if not isinstance(prop_key, str):
                    raise MLUEValidationError(
                        f"Rule '{trigger}' set_property action requires a 'property' string."
                    )
                prop_val = act_raw.get("value")
                actions.append(Action(type="set_property", target=target, property=prop_key, value=prop_val))
            elif act_type == "increment":
                if target not in state_variables:
                    raise MLUEValidationError(
                        f"Rule '{trigger}' increment action targets unknown state_variable '{target}'."
                    )
                amount = float(act_raw.get("amount", 1))
                actions.append(Action(type="increment", target=target, amount=amount))
            elif act_type == "set":
                if target not in state_variables:
                    raise MLUEValidationError(
                        f"Rule '{trigger}' set action targets unknown state_variable '{target}'."
                    )
                val = act_raw.get("value")
                actions.append(Action(type="set", target=target, value=val))
            elif act_type == "reset_entity":
                if target not in seen_ids:
                    raise MLUEValidationError(
                        f"Rule '{trigger}' reset_entity action targets unknown entity '{target}'."
                    )
                pos_data = act_raw.get("position", {"x": 0.5, "y": 0.5})
                vel_data = act_raw.get("velocity", {"vx": 0.0, "vy": 0.0})
                reset_pos = Position(x=float(pos_data["x"]), y=float(pos_data["y"]))
                reset_vel = Velocity(vx=float(vel_data["vx"]), vy=float(vel_data["vy"]))
                actions.append(
                    Action(type="reset_entity", target=target, position=reset_pos, velocity=reset_vel)
                )
            else:
                raise MLUEValidationError(
                    f"Rule '{trigger}' action type '{act_type}' is unsupported."
                )

        rules.append(Rule(
            trigger=trigger,
            actions=actions,
            event=event_name,
            entities=entities_pair,
            condition=condition,
        ))

    return MLUEDocument(
        version=version,
        environment=environment,
        entities=entities,
        state_variables=state_variables,
        rules=rules,
    )
