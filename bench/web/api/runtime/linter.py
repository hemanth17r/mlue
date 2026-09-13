"""MLUE Self-Healing AI Diagnostic Linter Core.

Provides high-speed compile-time validation, spatial reachability checks,
referential integrity verification, and machine-actionable diagnostics with
exact JSON pointers and suggested fixes for LLMs and autonomous agents.
Adheres strictly to Tier L1 Decoupling (Standard Library only: json, math, difflib, dataclasses, typing, pathlib).
"""

import json
import math
import re
import difflib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Union, Tuple

from runtime.model import MLUEDocument, Entity, Environment


VALID_ENTITY_TYPES = {"circle", "box", "segment", "capsule", "text"}
VALID_ANCHORS = {
    "center",
    "top_left",
    "top_right",
    "bottom_left",
    "bottom_right",
    "top_center",
    "bottom_center",
    "left_center",
    "right_center",
    "top",
    "bottom",
    "left",
    "right",
}
VALID_TRIGGERS = {
    "pointer_click",
    "pointer_down",
    "pointer_up",
    "pointer_enter",
    "pointer_exit",
    "pointer_move",
    "collision",
    "boundary_collision",
    "time_tick",
    "interval",
    "state_change",
    "key_press",
}
VALID_ACTION_TYPES = {
    "mutate_state",
    "mutate_entity",
    "spawn_entity",
    "destroy_entity",
    "emit_signal",
    "apply_force",
    "set_velocity",
    "reset_scene",
}

TEMPLATE_REGEX = re.compile(r"\{([a-zA-Z0-9_\.\[\]]+)\}")


@dataclass
class DiagnosticIssue:
    """Machine-actionable diagnostic issue with exact JSON path and fix recommendation."""
    severity: str  # "error" | "warning"
    code: str
    path: str
    message: str
    suggested_fix: Optional[Any] = None
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d["suggested_fix"] is None:
            del d["suggested_fix"]
        if d["context"] is None:
            del d["context"]
        return d


@dataclass
class LintReport:
    """Consolidated diagnostic report returned to AI agents and toolchain."""
    valid: bool
    error_count: int
    warning_count: int
    issues: List[DiagnosticIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[DiagnosticIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[DiagnosticIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
        }

    def format_console(self) -> str:
        """Formats report as human- and agent-readable text output."""
        if self.valid and not self.warnings:
            return "[OK] [MLUE Linter] 0 errors, 0 warnings. Document is 100% valid."

        lines = []
        lines.append(f"[MLUE Linter] Status: {'VALID (with warnings)' if self.valid else 'INVALID'}")
        lines.append(f"  Errors: {self.error_count}, Warnings: {self.warning_count}\n")

        for issue in self.issues:
            prefix = "[ERROR]" if issue.severity == "error" else "[WARN]"
            lines.append(f"{prefix} [{issue.code}] at '{issue.path}':")
            lines.append(f"    Message: {issue.message}")
            if issue.suggested_fix is not None:
                lines.append(f"    Suggested Fix: {issue.suggested_fix}")
            lines.append("")

        return "\n".join(lines)


class MLUELinter:
    """Performs comprehensive compile-time static linting on MLUE scenes."""

    def __init__(self):
        self.issues: List[DiagnosticIssue] = []

    def _add_issue(
        self,
        severity: str,
        code: str,
        path: str,
        message: str,
        suggested_fix: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.issues.append(
            DiagnosticIssue(
                severity=severity,
                code=code,
                path=path,
                message=message,
                suggested_fix=suggested_fix,
                context=context,
            )
        )

    def lint(self, source: Union[str, Path, Dict[str, Any], MLUEDocument]) -> LintReport:
        """Executes full diagnostic suite on the given MLUE representation."""
        self.issues = []

        raw_data: Optional[Dict[str, Any]] = None

        if isinstance(source, MLUEDocument):
            # Convert document to dictionary representation for full path traversal
            from runtime.loader import document_to_dict
            raw_data = document_to_dict(source)
        elif isinstance(source, (str, Path)):
            if isinstance(source, Path):
                p = source
            elif isinstance(source, str) and not source.strip().startswith("{"):
                p = Path(source)
            else:
                p = None

            if p and p.exists() and p.is_file():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        raw_data = json.load(f)
                except json.JSONDecodeError as e:
                    self._add_issue(
                        severity="error",
                        code="INVALID_JSON_SYNTAX",
                        path=f"line_{e.lineno}_col_{e.colno}",
                        message=f"JSON syntax error: {e.msg}",
                        context={"lineno": e.lineno, "colno": e.colno},
                    )
                    return LintReport(valid=False, error_count=1, warning_count=0, issues=self.issues)
                except Exception as e:
                    self._add_issue(
                        severity="error",
                        code="FILE_READ_ERROR",
                        path=str(p),
                        message=f"Could not read MLUE file: {e}",
                    )
                    return LintReport(valid=False, error_count=1, warning_count=0, issues=self.issues)
            else:
                # String raw json
                try:
                    raw_data = json.loads(str(source))
                except json.JSONDecodeError as e:
                    self._add_issue(
                        severity="error",
                        code="INVALID_JSON_SYNTAX",
                        path=f"line_{e.lineno}_col_{e.colno}",
                        message=f"JSON syntax error: {e.msg}",
                    )
                    return LintReport(valid=False, error_count=1, warning_count=0, issues=self.issues)
        elif isinstance(source, dict):
            raw_data = source
        else:
            self._add_issue(
                severity="error",
                code="UNSUPPORTED_SOURCE_TYPE",
                path="root",
                message=f"Unsupported MLUE source type: {type(source).__name__}",
            )
            return LintReport(valid=False, error_count=1, warning_count=0, issues=self.issues)

        if not isinstance(raw_data, dict):
            self._add_issue(
                severity="error",
                code="INVALID_ROOT_OBJECT",
                path="root",
                message="MLUE document root must be a JSON Object.",
                suggested_fix="Wrap document in { ... }",
            )
            return LintReport(valid=False, error_count=1, warning_count=0, issues=self.issues)

        # 1. Root & Schema Validation
        self._validate_schema_root(raw_data)

        # 2. Environment Validation
        self._validate_environment(raw_data.get("environment"))

        # 3. State Variables
        known_state_keys = self._collect_state_keys(raw_data)

        # 4. Entities Validation
        entity_ids = self._validate_entities(raw_data.get("entities", []))

        # 5. Rules & Referential Integrity
        self._validate_rules(raw_data.get("rules", []), entity_ids, known_state_keys)

        error_count = sum(1 for i in self.issues if i.severity == "error")
        warning_count = sum(1 for i in self.issues if i.severity == "warning")

        return LintReport(
            valid=(error_count == 0),
            error_count=error_count,
            warning_count=warning_count,
            issues=self.issues,
        )

    def _validate_schema_root(self, data: Dict[str, Any]):
        if "version" not in data:
            self._add_issue(
                severity="warning",
                code="MISSING_VERSION",
                path="version",
                message="Document lacks explicit 'version' identifier. Defaulting to '2.5.0'.",
                suggested_fix="2.5.0",
            )

        if "entities" not in data or not isinstance(data.get("entities"), list):
            self._add_issue(
                severity="error",
                code="MISSING_ENTITIES_ARRAY",
                path="entities",
                message="MLUE document must contain an 'entities' list.",
                suggested_fix=[],
            )

    def _validate_environment(self, env: Any):
        if env is None:
            self._add_issue(
                severity="warning",
                code="MISSING_ENVIRONMENT",
                path="environment",
                message="No 'environment' defined. Defaulting to standard 1.0 x 1.0 viewport.",
                suggested_fix={"dimensions": {"width": 1.0, "height": 1.0}},
            )
            return

        if not isinstance(env, dict):
            self._add_issue(
                severity="error",
                code="INVALID_ENVIRONMENT_TYPE",
                path="environment",
                message="'environment' must be a JSON object.",
            )
            return

        dims = env.get("dimensions")
        if dims and isinstance(dims, dict):
            w = dims.get("width")
            h = dims.get("height")
            if w is not None and (not isinstance(w, (int, float)) or w <= 0):
                self._add_issue(
                    severity="error",
                    code="INVALID_ENVIRONMENT_DIMENSIONS",
                    path="environment.dimensions.width",
                    message=f"Environment width must be a positive number. Got {w}.",
                    suggested_fix=1.0,
                )
            if h is not None and (not isinstance(h, (int, float)) or h <= 0):
                self._add_issue(
                    severity="error",
                    code="INVALID_ENVIRONMENT_DIMENSIONS",
                    path="environment.dimensions.height",
                    message=f"Environment height must be a positive number. Got {h}.",
                    suggested_fix=1.0,
                )

    def _collect_state_keys(self, data: Dict[str, Any]) -> List[str]:
        keys = []
        raw_state = data.get("state") or data.get("state_variables")
        if isinstance(raw_state, dict):
            for k, v in raw_state.items():
                keys.append(k)
                if isinstance(v, dict):
                    for sub_k in v.keys():
                        keys.append(f"{k}.{sub_k}")
        return keys

    def _validate_entities(self, entities: Any) -> List[str]:
        if not isinstance(entities, list):
            return []

        entity_ids: List[str] = []
        seen_ids = set()

        for idx, ent in enumerate(entities):
            path_prefix = f"entities[{idx}]"
            if not isinstance(ent, dict):
                self._add_issue(
                    severity="error",
                    code="INVALID_ENTITY_FORMAT",
                    path=path_prefix,
                    message="Entity entry must be a dictionary object.",
                )
                continue

            # ID Validation
            ent_id = ent.get("id")
            if not ent_id or not isinstance(ent_id, str):
                self._add_issue(
                    severity="error",
                    code="MISSING_ENTITY_ID",
                    path=f"{path_prefix}.id",
                    message=f"Entity at index {idx} must have a non-empty string 'id'.",
                    suggested_fix=f"entity_{idx+1}",
                )
            elif ent_id in seen_ids:
                self._add_issue(
                    severity="error",
                    code="DUPLICATE_ENTITY_ID",
                    path=f"{path_prefix}.id",
                    message=f"Duplicate entity ID '{ent_id}'. All entity IDs must be unique.",
                    suggested_fix=f"{ent_id}_{idx}",
                )
            else:
                seen_ids.add(ent_id)
                entity_ids.append(ent_id)

            # Type Validation
            ent_type = ent.get("type")
            if not ent_type or not isinstance(ent_type, str):
                self._add_issue(
                    severity="error",
                    code="MISSING_ENTITY_TYPE",
                    path=f"{path_prefix}.type",
                    message="Entity must define a 'type'.",
                    suggested_fix="box",
                )
            elif ent_type.lower() not in VALID_ENTITY_TYPES:
                closest = difflib.get_close_matches(ent_type.lower(), list(VALID_ENTITY_TYPES), n=1)
                self._add_issue(
                    severity="error",
                    code="INVALID_ENTITY_TYPE",
                    path=f"{path_prefix}.type",
                    message=f"Unsupported entity type '{ent_type}'. Valid types: {sorted(list(VALID_ENTITY_TYPES))}",
                    suggested_fix=closest[0] if closest else "box",
                )

            # Position Validation
            has_parent = ent.get("parent_id") is not None
            has_anchor = ent.get("anchor") is not None or (
                isinstance(ent.get("properties"), dict) and ent.get("properties").get("anchor") is not None
            )
            min_bound = -1.0 if has_anchor else 0.0

            pos = ent.get("position")
            if ent_type == "segment":
                pos = ent.get("start", pos)

            if pos is None and has_parent:
                pos = {"x": 0.5, "y": 0.5}  # Position computed dynamically by parent layout

            if not pos or not isinstance(pos, dict):
                self._add_issue(
                    severity="error",
                    code="MISSING_POSITION",
                    path=f"{path_prefix}.position",
                    message="Entity must define a 'position' object with 'x' and 'y' (or inherit from parent_id layout).",
                    suggested_fix={"x": 0.5, "y": 0.5},
                )
            else:
                x = pos.get("x")
                y = pos.get("y")
                if x is None or not isinstance(x, (int, float)):
                    self._add_issue(
                        severity="error",
                        code="INVALID_COORDINATE_VALUE",
                        path=f"{path_prefix}.position.x",
                        message="Position 'x' must be a numeric value.",
                        suggested_fix=0.5,
                    )
                elif x < min_bound or x > 1.0:
                    self._add_issue(
                        severity="warning",
                        code="OUT_OF_BOUNDS_SPATIAL",
                        path=f"{path_prefix}.position.x",
                        message=f"Entity '{ent_id}' x-coordinate {x} is outside normalized [{min_bound}, 1.0] viewport.",
                        suggested_fix=max(min_bound, min(1.0, float(x))),
                    )

                if y is None or not isinstance(y, (int, float)):
                    self._add_issue(
                        severity="error",
                        code="INVALID_COORDINATE_VALUE",
                        path=f"{path_prefix}.position.y",
                        message="Position 'y' must be a numeric value.",
                        suggested_fix=0.5,
                    )
                elif y < min_bound or y > 1.0:
                    self._add_issue(
                        severity="warning",
                        code="OUT_OF_BOUNDS_SPATIAL",
                        path=f"{path_prefix}.position.y",
                        message=f"Entity '{ent_id}' y-coordinate {y} is outside normalized [{min_bound}, 1.0] viewport.",
                        suggested_fix=max(min_bound, min(1.0, float(y))),
                    )

            # Size Validation
            self._validate_entity_size(ent, path_prefix)

            # Anchor Validation
            anc = ent.get("anchor")
            if anc and isinstance(anc, str) and anc.lower() not in VALID_ANCHORS:
                closest = difflib.get_close_matches(anc.lower(), list(VALID_ANCHORS), n=1)
                self._add_issue(
                    severity="warning",
                    code="UNKNOWN_ANCHOR_VALUE",
                    path=f"{path_prefix}.anchor",
                    message=f"Anchor value '{anc}' is non-standard. Supported: {sorted(list(VALID_ANCHORS))}",
                    suggested_fix=closest[0] if closest else "center",
                )

        return entity_ids

    def _validate_entity_size(self, ent: Dict[str, Any], path_prefix: str):
        ent_type = str(ent.get("type", "")).lower()
        size = ent.get("size")

        if size is None:
            if ent_type == "text":
                return  # Text size defaults to font_scale=0.02
            if ent_type == "segment" and ("end" in ent or "end_x" in ent):
                size = {}
            else:
                self._add_issue(
                    severity="error",
                    code="MISSING_ENTITY_SIZE",
                    path=f"{path_prefix}.size",
                    message=f"Entity of type '{ent_type}' must have a 'size' definition.",
                )
                return

        if not isinstance(size, dict):
            self._add_issue(
                severity="error",
                code="INVALID_SIZE_STRUCTURE",
                path=f"{path_prefix}.size",
                message="Size must be an object with shape-specific dimensions.",
            )
            return

        if ent_type == "circle":
            r = size.get("radius")
            if r is None or not isinstance(r, (int, float)) or r <= 0.0:
                self._add_issue(
                    severity="error",
                    code="INVALID_CIRCLE_RADIUS",
                    path=f"{path_prefix}.size.radius",
                    message=f"Circle 'radius' must be a positive number. Got {r}.",
                    suggested_fix=0.05,
                )
            elif r > 0.5:
                self._add_issue(
                    severity="warning",
                    code="OVERSIZED_PRIMITIVE",
                    path=f"{path_prefix}.size.radius",
                    message=f"Circle radius {r} is very large relative to [0.0, 1.0] viewport.",
                )

        elif ent_type == "box":
            w = size.get("width")
            h = size.get("height")
            if w is None or not isinstance(w, (int, float)) or w <= 0.0:
                self._add_issue(
                    severity="error",
                    code="INVALID_BOX_DIMENSIONS",
                    path=f"{path_prefix}.size.width",
                    message=f"Box 'width' must be a positive number. Got {w}.",
                    suggested_fix=0.1,
                )
            if h is None or not isinstance(h, (int, float)) or h <= 0.0:
                self._add_issue(
                    severity="error",
                    code="INVALID_BOX_DIMENSIONS",
                    path=f"{path_prefix}.size.height",
                    message=f"Box 'height' must be a positive number. Got {h}.",
                    suggested_fix=0.1,
                )

        elif ent_type == "segment":
            end_raw = ent.get("end", size.get("end", size))
            if not isinstance(end_raw, dict):
                self._add_issue(
                    severity="error",
                    code="INVALID_SEGMENT_ENDPOINT",
                    path=f"{path_prefix}.end",
                    message="Segment entity requires an 'end' object with 'x' and 'y' (or end_x/end_y).",
                    suggested_fix={"x": 1.0, "y": 0.5},
                )
            else:
                ex = end_raw.get("x", end_raw.get("end_x"))
                ey = end_raw.get("y", end_raw.get("end_y"))
                if ex is None or not isinstance(ex, (int, float)):
                    self._add_issue(
                        severity="error",
                        code="INVALID_SEGMENT_ENDPOINT",
                        path=f"{path_prefix}.end.x",
                        message="Segment 'end.x' must be a numeric coordinate.",
                        suggested_fix=1.0,
                    )
                if ey is None or not isinstance(ey, (int, float)):
                    self._add_issue(
                        severity="error",
                        code="INVALID_SEGMENT_ENDPOINT",
                        path=f"{path_prefix}.end.y",
                        message="Segment 'end.y' must be a numeric coordinate.",
                        suggested_fix=0.5,
                    )

        elif ent_type == "capsule":
            r = size.get("radius")
            l = size.get("length")
            if r is None or not isinstance(r, (int, float)) or r <= 0.0:
                self._add_issue(
                    severity="error",
                    code="INVALID_CAPSULE_RADIUS",
                    path=f"{path_prefix}.size.radius",
                    message="Capsule 'radius' must be a positive number.",
                    suggested_fix=0.03,
                )
            if l is None or not isinstance(l, (int, float)) or l <= 0.0:
                self._add_issue(
                    severity="error",
                    code="INVALID_CAPSULE_LENGTH",
                    path=f"{path_prefix}.size.length",
                    message="Capsule 'length' must be a positive number.",
                    suggested_fix=0.1,
                )

    def _validate_rules(self, rules: Any, entity_ids: List[str], state_keys: List[str]):
        if not isinstance(rules, list):
            return

        for idx, rule in enumerate(rules):
            path_prefix = f"rules[{idx}]"
            if not isinstance(rule, dict):
                self._add_issue(
                    severity="error",
                    code="INVALID_RULE_STRUCTURE",
                    path=path_prefix,
                    message="Rule entry must be an object.",
                )
                continue

            # Trigger check
            trig = rule.get("trigger")
            if not trig or not isinstance(trig, str):
                self._add_issue(
                    severity="error",
                    code="MISSING_RULE_TRIGGER",
                    path=f"{path_prefix}.trigger",
                    message="Rule must define a 'trigger' string.",
                    suggested_fix="pointer_click",
                )
            elif trig.lower() not in VALID_TRIGGERS:
                closest = difflib.get_close_matches(trig.lower(), list(VALID_TRIGGERS), n=1)
                self._add_issue(
                    severity="warning",
                    code="UNKNOWN_RULE_TRIGGER",
                    path=f"{path_prefix}.trigger",
                    message=f"Trigger '{trig}' is unusual. Known triggers: {sorted(list(VALID_TRIGGERS))}",
                    suggested_fix=closest[0] if closest else "pointer_click",
                )

            # Target entity check
            target = rule.get("target")
            if target and isinstance(target, str):
                if target not in entity_ids and target != "*":
                    closest = difflib.get_close_matches(target, entity_ids, n=1)
                    self._add_issue(
                        severity="error",
                        code="UNKNOWN_TARGET_ENTITY",
                        path=f"{path_prefix}.target",
                        message=f"Rule targets entity '{target}' which does not exist in 'entities'.",
                        suggested_fix=closest[0] if closest else (entity_ids[0] if entity_ids else None),
                    )

            # Actions validation
            actions = rule.get("actions", [])
            if not isinstance(actions, list):
                self._add_issue(
                    severity="error",
                    code="INVALID_ACTIONS_ARRAY",
                    path=f"{path_prefix}.actions",
                    message="'actions' must be a list of action objects.",
                )
            else:
                for act_idx, act in enumerate(actions):
                    act_path = f"{path_prefix}.actions[{act_idx}]"
                    if not isinstance(act, dict):
                        continue

                    act_type = act.get("type")
                    if not act_type or not isinstance(act_type, str):
                        self._add_issue(
                            severity="error",
                            code="MISSING_ACTION_TYPE",
                            path=f"{act_path}.type",
                            message="Action must define a 'type'.",
                            suggested_fix="mutate_state",
                        )
                        continue

                    if act_type == "mutate_state":
                        key = act.get("key")
                        if key and state_keys and key not in state_keys:
                            closest = difflib.get_close_matches(key, state_keys, n=1)
                            self._add_issue(
                                severity="warning",
                                code="UNKNOWN_MUTATE_STATE_KEY",
                                path=f"{act_path}.key",
                                message=f"Action mutates state variable '{key}' which is not declared in root 'state'.",
                                suggested_fix=closest[0] if closest else None,
                            )

                    elif act_type == "mutate_entity":
                        act_target = act.get("target")
                        if act_target and entity_ids and act_target not in entity_ids:
                            closest = difflib.get_close_matches(act_target, entity_ids, n=1)
                            self._add_issue(
                                severity="error",
                                code="UNKNOWN_MUTATE_ENTITY_TARGET",
                                path=f"{act_path}.target",
                                message=f"Action mutates entity '{act_target}' which does not exist.",
                                suggested_fix=closest[0] if closest else None,
                            )


def lint_mlue(source: Union[str, Path, Dict[str, Any], MLUEDocument]) -> LintReport:
    """Convenience functional API for linting MLUE scenes."""
    linter = MLUELinter()
    return linter.lint(source)
