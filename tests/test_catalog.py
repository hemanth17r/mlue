"""Tests for MLUE AI-Native Catalog Engine

Validates in-memory index loading, search ranking, coordinate bounds validation,
CRUD registration, and error handling for standard shapes, parts, tokens, and blueprints.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from runtime.catalog import Catalog, CatalogError, CatalogValidationError


class TestCatalogEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.catalog = Catalog()

    def test_01_catalog_loads_all_definitions(self):
        """Asserts that all 18 baseline catalog definitions are loaded into memory."""
        self.assertGreaterEqual(len(self.catalog._index), 18)
        # Check presence of key items across all kinds
        self.assertIsNotNone(self.catalog.get("shape", "box"))
        self.assertIsNotNone(self.catalog.get("shape", "circle"))
        self.assertIsNotNone(self.catalog.get("part", "paddle"))
        self.assertIsNotNone(self.catalog.get("part", "ball"))
        self.assertIsNotNone(self.catalog.get("token", "palettes"))
        self.assertIsNotNone(self.catalog.get("blueprint", "breakout"))

    def test_02_get_returns_deep_copy(self):
        """Asserts get returns isolated copies to prevent cache mutation."""
        paddle1 = self.catalog.get("part", "paddle")
        self.assertIsNotNone(paddle1)
        paddle1["defaults"]["speed"] = 999.0

        paddle2 = self.catalog.get("part", "paddle")
        self.assertNotEqual(paddle2["defaults"]["speed"], 999.0)

    def test_03_list_filtering(self):
        """Asserts list filters accurately by kind and tag."""
        all_items = self.catalog.list()
        self.assertGreaterEqual(len(all_items), 18)

        parts = self.catalog.list(kind="part")
        self.assertEqual(len(parts), 8)
        for p in parts:
            self.assertEqual(p["kind"], "part")

        shapes = self.catalog.list(kind="shape")
        self.assertEqual(len(shapes), 4)

        game_items = self.catalog.list(tag="game")
        self.assertGreaterEqual(len(game_items), 4)
        for item in game_items:
            self.assertIn("game", item["tags"])

    def test_04_search_ranking(self):
        """Asserts search prioritizes exact ID match and tag relevance."""
        # Exact ID match test
        results = self.catalog.search("paddle")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["id"], "paddle")

        # Tag/Summary search test
        ball_results = self.catalog.search("bounce")
        self.assertGreater(len(ball_results), 0)
        self.assertEqual(ball_results[0]["id"], "ball")

        # Design token search
        slate_results = self.catalog.search("slate")
        self.assertGreater(len(slate_results), 0)
        self.assertEqual(slate_results[0]["id"], "palettes")

    def test_05_coordinate_bounds_validation(self):
        """Asserts validate enforces strict [0.0, 1.0] coordinate clamping."""
        # Valid entry
        valid_entry = {
            "id": "test_box",
            "kind": "shape",
            "tags": ["test"],
            "summary": "Valid test box",
            "entity_template": {
                "position": {"x": 0.5, "y": 0.5},
                "size": {"width": 0.2, "height": 0.1}
            }
        }
        self.assertEqual(self.catalog.validate(valid_entry), [])

        # Invalid entry: x > 1.0
        invalid_entry_1 = {
            "id": "test_box",
            "kind": "shape",
            "tags": ["test"],
            "summary": "Invalid coordinate box",
            "entity_template": {
                "position": {"x": 1.5, "y": 0.5}
            }
        }
        errors_1 = self.catalog.validate(invalid_entry_1)
        self.assertTrue(any("out of bounds" in err for err in errors_1))

        # Invalid entry: radius < 0.0
        invalid_entry_2 = {
            "id": "test_circle",
            "kind": "shape",
            "tags": ["test"],
            "summary": "Negative radius circle",
            "entity_template": {
                "size": {"radius": -0.05}
            }
        }
        errors_2 = self.catalog.validate(invalid_entry_2)
        self.assertTrue(any("out of bounds" in err for err in errors_2))

        # Missing required field
        invalid_entry_3 = {"id": "no_tags"}
        errors_3 = self.catalog.validate(invalid_entry_3)
        self.assertTrue(any("Missing required field" in err for err in errors_3))

    def test_06_programmatic_registration_crud(self):
        """Asserts register writes file, updates in-memory index, and enables immediate search."""
        temp_dir = tempfile.mkdtemp()
        try:
            temp_catalog = Catalog(catalog_dir=temp_dir)
            self.assertEqual(len(temp_catalog._index), 0)

            new_part = {
                "id": "laser_turret",
                "kind": "part",
                "tags": ["weapon", "kinematic", "laser"],
                "summary": "Directional laser emitter turret",
                "defaults": {
                    "position": {"x": 0.5, "y": 0.1},
                    "size": {"width": 0.08, "height": 0.04}
                },
                "entity_template": {
                    "type": "box",
                    "position": {"x": 0.5, "y": 0.1},
                    "size": {"width": 0.08, "height": 0.04}
                }
            }

            res = temp_catalog.register("part", "laser_turret", new_part)
            self.assertTrue(res["success"])
            self.assertTrue(os.path.exists(res["file_path"]))

            # Index was updated in memory immediately
            fetched = temp_catalog.get("part", "laser_turret")
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched["id"], "laser_turret")

            # Search immediately discovers it
            search_res = temp_catalog.search("laser")
            self.assertEqual(len(search_res), 1)
            self.assertEqual(search_res[0]["id"], "laser_turret")

            # Duplicate without overwrite raises CatalogError
            with self.assertRaises(CatalogError):
                temp_catalog.register("part", "laser_turret", new_part, overwrite=False)

            # Duplicate with overwrite succeeds
            res2 = temp_catalog.register("part", "laser_turret", new_part, overwrite=True)
            self.assertTrue(res2["success"])

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
