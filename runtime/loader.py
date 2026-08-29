"""MLUE Document Loader & Semantic Invariant Validator

Loads machine-oriented MLUE specifications and verifies semantic constraints,
type bounds, and static physical/spatial reachability invariants.
Supports MLUE schema versions 0.1, 0.2, 0.3, 0.4, 0.5, and 0.6.
"""

import json
import math
import re
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
    """Raised when an MLUE document fails schema, semantic, or reachability validation."""
    pass


def parse_keypath(path_str: str) -> List[Union[str, int]]:
    """
    Parses a keypath string (e.g. 'session.stats.energy', 'inventory[0].durability')
    into a sequence of dictionary keys and integer indices.
    Raises MLUEValidationError if path syntax is invalid.
    """
    if not isinstance(path_str, str) or not path_str.strip():
        raise MLUEValidationError("Keypath must be a non-empty string.")

    raw_segments = path_str.strip().split('.')
    tokens: List[Union[str, int]] = []

    for seg in raw_segments:
        if not seg:
            raise MLUEValidationError(f"Invalid keypath '{path_str}': empty segment / consecutive dots.")

        if seg[0] == '[':
            raise MLUEValidationError(f"Invalid keypath '{path_str}': segment cannot start with bracket.")

        bracket_start = seg.find('[')
        if bracket_start == -1:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', seg):
                raise MLUEValidationError(f"Invalid keypath identifier '{seg}' in '{path_str}'.")
            tokens.append(seg)
        else:
            ident = seg[:bracket_start]
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', ident):
                raise MLUEValidationError(f"Invalid keypath identifier '{ident}' in '{path_str}'.")
            tokens.append(ident)

            rest = seg[bracket_start:]
            bracket_matches = re.findall(r'\[([^\]]*)\]', rest)
            reconstructed = "".join(f"[{m}]" for m in bracket_matches)
            if reconstructed != rest:
                raise MLUEValidationError(f"Malformed array indexing in keypath '{path_str}'.")
            for m in bracket_matches:
                if not re.match(r'^-?[0-9]+$', m):
                    raise MLUEValidationError(f"Invalid array index '{m}' in keypath '{path_str}'. Must be integer.")
                tokens.append(int(m))

    return tokens


def _validate_path_against_state(path_str: str, state_variables: Dict[str, Any], rule_trigger: str) -> None:
    """Statically validates that a keypath's root and initial indices exist in state_variables."""
    tokens = parse_keypath(path_str)
    root = tokens[0]
    if root not in state_variables:
        raise MLUEValidationError(
            f"Rule '{rule_trigger}' targets unknown root state_variable '{root}' in path '{path_str}'."
        )

    # Statically traverse initial state if possible
    curr: Any = state_variables
    for idx, tok in enumerate(tokens):
        if tok == "length" and idx == len(tokens) - 1 and isinstance(curr, list):
            return
        if isinstance(curr, dict):
            if isinstance(tok, str):
                if tok in curr:
                    curr = curr[tok]
                else:
                    # Key might be created dynamically, but if dict is present, we know structure
                    break
            else:
                raise MLUEValidationError(
                    f"Rule '{rule_trigger}' invalid integer index '{tok}' on dictionary at '{path_str}'."
                )
        elif isinstance(curr, list):
            if isinstance(tok, int):
                if 0 <= tok < len(curr) or (tok < 0 and abs(tok) <= len(curr)):
                    curr = curr[tok]
                else:
                    raise MLUEValidationError(
                        f"Rule '{rule_trigger}' initial array index [{tok}] out of bounds (len={len(curr)}) at '{path_str}'."
                    )
            elif tok == "length" and idx == len(tokens) - 1:
                return
            else:
                raise MLUEValidationError(
                    f"Rule '{rule_trigger}' invalid string key '{tok}' on array at '{path_str}'."
                )
        else:
            # Reached a primitive before end of path
            if idx < len(tokens):
                raise MLUEValidationError(
                    f"Rule '{rule_trigger}' path '{path_str}' attempts to index into primitive value '{curr}'."
                )


def load_mlue(source: Union[str, Path, Dict[str, Any]]) -> MLUEDocument:
    """Load and validate an MLUE document from a file path (.mlue, .mlueb), JSON string, or dict."""
    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.exists() and path.is_file():
            # Check for binary .mlueb magic or extension
            if path.suffix.lower() == ".mlueb":
                from runtime.binary import load_mlueb
                return load_mlueb(path)

            with open(path, "rb") as f:
                header_bytes = f.read(4)
                if header_bytes == b"MLUE":
                    f.seek(0)
                    from runtime.binary import decode_mlueb
                    return decode_mlueb(f.read())

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


def _get_entity_half_extents(entity: Entity, env: Environment) -> Tuple[float, float]:
    """Calculates exact normalized half-extents (ex, ey) for an entity in the given environment."""
    w = env.width
    h = env.height
    min_dim = min(w, h)

    if entity.type == "circle" and isinstance(entity.size, CircleSize):
        r = entity.size.radius
        return r * (min_dim / w), r * (min_dim / h)
    elif entity.type == "box" and isinstance(entity.size, BoxSize):
        return entity.size.width / 2.0, entity.size.height / 2.0
    return 0.0, 0.0


def validate_and_parse(data: Dict[str, Any]) -> MLUEDocument:
    """Validate raw dictionary structure and static mathematical invariants against MLUE specification schema."""
    if not isinstance(data, dict):
        raise MLUEValidationError("MLUE document root must be a dictionary/object.")

    version = data.get("mlue_version")
    if version not in ("0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "1.1", "1.2", "1.3"):
        raise MLUEValidationError(
            f"Unsupported MLUE version '{version}'. Expected '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '1.1', '1.2', or '1.3'."
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

    # Rules Validation & Static Reachability Verification
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
            if op not in ("<=", ">=", "==", "<", ">", "!="):
                raise MLUEValidationError(
                    f"Rule '{trigger}' condition op '{op}' is invalid. Supported: <=, >=, ==, <, >, !=."
                )

            val = cond_raw.get("value")

            if "state_path" in cond_raw:
                sp_name = cond_raw["state_path"]
                if not isinstance(sp_name, str):
                    raise MLUEValidationError(f"Rule '{trigger}' state_path must be a string.")
                _validate_path_against_state(sp_name, state_variables, trigger)
                condition = Condition(state_path=sp_name, op=op, value=val)
            elif "state_variable" in cond_raw:
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

                float_val = float(val)

                # Static Reachability Invariant Check
                if prop_name in ("position.x", "position.y"):
                    ent_obj = next(e for e in entities if e.id == target_ent)
                    ex, ey = _get_entity_half_extents(ent_obj, environment)

                    if prop_name == "position.x":
                        min_x = ex
                        max_x = 1.0 - ex
                        if op in ("<=", "<") and float_val < (min_x - 1e-6):
                            raise MLUEValidationError(
                                f"Rule '{trigger}' condition 'position.x {op} {float_val}' is mathematically unreachable: "
                                f"entity '{target_ent}' left boundary limit is {min_x:.4f}."
                            )
                        elif op in (">=", ">") and float_val > (max_x + 1e-6):
                            raise MLUEValidationError(
                                f"Rule '{trigger}' condition 'position.x {op} {float_val}' is mathematically unreachable: "
                                f"entity '{target_ent}' right boundary limit is {max_x:.4f}."
                            )
                    elif prop_name == "position.y":
                        min_y = ey
                        max_y = 1.0 - ey
                        if op in ("<=", "<") and float_val < (min_y - 1e-6):
                            raise MLUEValidationError(
                                f"Rule '{trigger}' condition 'position.y {op} {float_val}' is mathematically unreachable: "
                                f"entity '{target_ent}' top boundary limit is {min_y:.4f}."
                            )
                        elif op in (">=", ">") and float_val > (max_y + 1e-6):
                            raise MLUEValidationError(
                                f"Rule '{trigger}' condition 'position.y {op} {float_val}' is mathematically unreachable: "
                                f"entity '{target_ent}' bottom boundary limit is {max_y:.4f}."
                            )

                condition = Condition(entity=target_ent, property=prop_name, op=op, value=float_val)

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
            elif act_type == "set_path":
                if not isinstance(target, str):
                    raise MLUEValidationError(f"Rule '{trigger}' set_path action requires a string 'target' path.")
                _validate_path_against_state(target, state_variables, trigger)
                val = act_raw.get("value")
                actions.append(Action(type="set_path", target=target, value=val))
            elif act_type == "increment_path":
                if not isinstance(target, str):
                    raise MLUEValidationError(f"Rule '{trigger}' increment_path action requires a string 'target' path.")
                _validate_path_against_state(target, state_variables, trigger)
                amount = float(act_raw.get("amount", 1.0))
                actions.append(Action(type="increment_path", target=target, amount=amount))
            elif act_type == "push":
                if not isinstance(target, str):
                    raise MLUEValidationError(f"Rule '{trigger}' push action requires a string 'target' path.")
                _validate_path_against_state(target, state_variables, trigger)
                val = act_raw.get("value")
                actions.append(Action(type="push", target=target, value=val))
            elif act_type == "pop":
                if not isinstance(target, str):
                    raise MLUEValidationError(f"Rule '{trigger}' pop action requires a string 'target' path.")
                _validate_path_against_state(target, state_variables, trigger)
                idx = int(act_raw.get("index", -1))
                actions.append(Action(type="pop", target=target, index=idx))
            elif act_type == "delete_key":
                if not isinstance(target, str):
                    raise MLUEValidationError(f"Rule '{trigger}' delete_key action requires a string 'target' path.")
                _validate_path_against_state(target, state_variables, trigger)
                key_name = act_raw.get("key")
                actions.append(Action(type="delete_key", target=target, key=key_name))
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
