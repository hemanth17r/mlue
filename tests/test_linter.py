"""Unit tests for the MLUE Self-Healing AI Diagnostic Linter.

Verifies static compile-time error detection, fuzzy repair suggestions,
spatial boundary warnings, and machine-actionable JSON diagnostic reports.
"""

import unittest
from pathlib import Path
from runtime.linter import MLUELinter, lint_mlue, LintReport, DiagnosticIssue


class TestMLUELinter(unittest.TestCase):
    """Test suite verifying compile-time diagnostics and self-healing guidance."""

    def setUp(self):
        self.linter = MLUELinter()

    def test_valid_minimal_scene(self):
        """Minimal valid document passes with 0 errors."""
        doc = {
            "version": "2.5.0",
            "environment": {"dimensions": {"width": 1.0, "height": 1.0}},
            "entities": [
                {
                    "id": "player",
                    "type": "circle",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"radius": 0.05},
                }
            ],
        }
        report = self.linter.lint(doc)
        self.assertTrue(report.valid)
        self.assertEqual(report.error_count, 0)
        self.assertIn("[OK]", report.format_console())

    def test_invalid_json_syntax(self):
        """Malformed JSON strings trigger INVALID_JSON_SYNTAX."""
        bad_json = '{"version": "2.5.0", "entities": ['
        report = self.linter.lint(bad_json)
        self.assertFalse(report.valid)
        self.assertEqual(report.error_count, 1)
        self.assertEqual(report.errors[0].code, "INVALID_JSON_SYNTAX")

    def test_missing_entities_array(self):
        """Document missing entities array produces MISSING_ENTITIES_ARRAY error."""
        doc = {"version": "2.5.0", "environment": {}}
        report = self.linter.lint(doc)
        self.assertFalse(report.valid)
        codes = [e.code for e in report.errors]
        self.assertIn("MISSING_ENTITIES_ARRAY", codes)

    def test_duplicate_entity_id(self):
        """Duplicate entity IDs are flagged with a fix recommendation."""
        doc = {
            "version": "2.5.0",
            "entities": [
                {
                    "id": "ball",
                    "type": "circle",
                    "position": {"x": 0.2, "y": 0.2},
                    "size": {"radius": 0.04},
                },
                {
                    "id": "ball",
                    "type": "box",
                    "position": {"x": 0.8, "y": 0.8},
                    "size": {"width": 0.1, "height": 0.1},
                },
            ],
        }
        report = self.linter.lint(doc)
        self.assertFalse(report.valid)
        codes = [e.code for e in report.errors]
        self.assertIn("DUPLICATE_ENTITY_ID", codes)
        dup_issue = next(e for e in report.errors if e.code == "DUPLICATE_ENTITY_ID")
        self.assertIsNotNone(dup_issue.suggested_fix)

    def test_fuzzy_suggested_entity_type(self):
        """Typo in entity type (e.g. 'circl') fuzzy-matches to 'circle'."""
        doc = {
            "version": "2.5.0",
            "entities": [
                {
                    "id": "node",
                    "type": "circl",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"radius": 0.05},
                }
            ],
        }
        report = self.linter.lint(doc)
        self.assertFalse(report.valid)
        err = report.errors[0]
        self.assertEqual(err.code, "INVALID_ENTITY_TYPE")
        self.assertEqual(err.suggested_fix, "circle")

    def test_negative_size_validation(self):
        """Negative radius or box dimensions trigger validation errors."""
        doc = {
            "version": "2.5.0",
            "entities": [
                {
                    "id": "bad_circle",
                    "type": "circle",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"radius": -0.1},
                }
            ],
        }
        report = self.linter.lint(doc)
        self.assertFalse(report.valid)
        err = report.errors[0]
        self.assertEqual(err.code, "INVALID_CIRCLE_RADIUS")
        self.assertGreater(err.suggested_fix, 0.0)

    def test_spatial_out_of_bounds_warning(self):
        """Entity placed outside [0.0, 1.0] generates an OUT_OF_BOUNDS_SPATIAL warning."""
        doc = {
            "version": "2.5.0",
            "environment": {"dimensions": {"width": 1.0, "height": 1.0}},
            "entities": [
                {
                    "id": "offscreen",
                    "type": "box",
                    "position": {"x": 1.45, "y": 0.5},
                    "size": {"width": 0.1, "height": 0.1},
                }
            ],
        }
        report = self.linter.lint(doc)
        self.assertTrue(report.valid)  # Warnings do not invalidate scene
        self.assertEqual(report.warning_count, 1)
        warn = report.warnings[0]
        self.assertEqual(warn.code, "OUT_OF_BOUNDS_SPATIAL")
        self.assertAlmostEqual(warn.suggested_fix, 1.0)

    def test_unknown_rule_target_with_suggestion(self):
        """Rule targeting non-existent entity suggests closest matching ID."""
        doc = {
            "version": "2.5.0",
            "entities": [
                {
                    "id": "paddle_bottom",
                    "type": "box",
                    "position": {"x": 0.5, "y": 0.95},
                    "size": {"width": 0.2, "height": 0.02},
                }
            ],
            "rules": [
                {
                    "trigger": "pointer_click",
                    "target": "paddle_botom",  # Typo!
                    "actions": [{"type": "set_velocity", "target": "paddle_bottom"}],
                }
            ],
        }
        report = self.linter.lint(doc)
        self.assertFalse(report.valid)
        err = next(e for e in report.errors if e.code == "UNKNOWN_TARGET_ENTITY")
        self.assertEqual(err.suggested_fix, "paddle_bottom")

    def test_json_export_structure(self):
        """Linter output serializes to standard machine-actionable dictionary."""
        doc = {
            "entities": [
                {
                    "id": "box_1",
                    "type": "box",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.1, "height": 0.1},
                }
            ]
        }
        report = lint_mlue(doc)
        d = report.to_dict()
        self.assertIn("valid", d)
        self.assertIn("error_count", d)
        self.assertIn("warning_count", d)
        self.assertIn("errors", d)
        self.assertIn("warnings", d)


if __name__ == "__main__":
    unittest.main()
