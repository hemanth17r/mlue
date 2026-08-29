"""Unit tests for MLUE Subphase 1.1: Hierarchical State-Trees & Query/Mutation Primitives.

Validates keypath grammar, static path reachability, all 5 atomic mutation actions
(set_path, increment_path, push, pop, delete_key), path conditions, and 50,000-tick bit-exact determinism.
"""

import unittest
import hashlib
from pathlib import Path
from runtime.loader import load_mlue, validate_and_parse, parse_keypath, MLUEValidationError
from runtime.engine import MLUEEngine
from runtime.model import MLUEDocument, Environment, Entity, Position, CircleSize, Velocity, Rule, Condition, Action


class TestHierarchicalState(unittest.TestCase):
    """Test suite for Phase 1.1 hierarchical document state trees and path mutations."""

    def setUp(self):
        self.engine = MLUEEngine()
        self.examples_dir = Path(__file__).resolve().parent.parent / "examples"

    # =========================================================================
    # 1. KEYPATH PARSING & GRAMMAR
    # =========================================================================

    def test_parse_keypath_valid(self):
        """Verify valid dot and bracket keypaths are parsed correctly."""
        self.assertEqual(parse_keypath("score"), ["score"])
        self.assertEqual(parse_keypath("session.stats.energy"), ["session", "stats", "energy"])
        self.assertEqual(parse_keypath("inventory[0].durability"), ["inventory", 0, "durability"])
        self.assertEqual(parse_keypath("grid.cells[1][2].type"), ["grid", "cells", 1, 2, "type"])
        self.assertEqual(parse_keypath("items[-1]"), ["items", -1])
        self.assertEqual(parse_keypath("inventory.length"), ["inventory", "length"])

    def test_parse_keypath_invalid(self):
        """Verify invalid keypath strings raise MLUEValidationError."""
        invalid_cases = [
            "",
            "   ",
            "a..b",
            "a[abc]",
            "[0]",
            "a[]",
            "a.[0]",
            "123abc",
            "session.stats.",
            ".session",
        ]
        for bad_path in invalid_cases:
            with self.subTest(bad_path=bad_path):
                with self.assertRaises(MLUEValidationError):
                    parse_keypath(bad_path)

    # =========================================================================
    # 2. STATIC VALIDATION & LOADER
    # =========================================================================

    def test_loader_valid_1_1_capstone(self):
        """Verify examples/inventory_system.mlue loads and parses under version 1.1."""
        doc = load_mlue(self.examples_dir / "inventory_system.mlue")
        self.assertEqual(doc.version, "1.1")
        self.assertIn("session", doc.state_variables)
        self.assertIn("inventory", doc.state_variables)
        self.assertEqual(len(doc.entities), 4)
        self.assertEqual(len(doc.rules), 4)

    def test_loader_reject_unknown_root_variable(self):
        """Verify loader rejects rules targeting unknown root state variable."""
        raw = {
            "mlue_version": "1.1",
            "state_variables": {"session": {"score": 0}},
            "entities": [{"id": "b", "type": "circle", "position": {"x": 0.5, "y": 0.5}, "size": {"radius": 0.05}}],
            "rules": [
                {
                    "trigger": "r1",
                    "condition": {"state_path": "missing_root.score", "op": ">=", "value": 10},
                    "actions": [{"type": "increment_path", "target": "missing_root.score", "amount": 1}]
                }
            ]
        }
        with self.assertRaises(MLUEValidationError) as ctx:
            validate_and_parse(raw)
        self.assertIn("unknown root state_variable", str(ctx.exception).lower())

    def test_loader_reject_static_out_of_bounds(self):
        """Verify loader rejects rules indexing out of bounds in initial arrays."""
        raw = {
            "mlue_version": "1.1",
            "state_variables": {"items": [{"id": "item1"}]},
            "entities": [{"id": "b", "type": "circle", "position": {"x": 0.5, "y": 0.5}, "size": {"radius": 0.05}}],
            "rules": [
                {
                    "trigger": "r1",
                    "condition": {"state_path": "items[5].id", "op": "==", "value": "item1"},
                    "actions": [{"type": "pop", "target": "items", "index": 0}]
                }
            ]
        }
        with self.assertRaises(MLUEValidationError) as ctx:
            validate_and_parse(raw)
        self.assertIn("out of bounds", str(ctx.exception).lower())

    # =========================================================================
    # 3. ENGINE PATH QUERY & RESOLUTION
    # =========================================================================

    def test_engine_path_resolution(self):
        """Verify _get_path_value retrieves nested keys, array items, and array .length."""
        state = {
            "session": {"mode": "SURVIVAL", "stats": {"energy": 100.0}},
            "inventory": [
                {"id": "sword", "durability": 85},
                {"id": "shield", "durability": 100},
            ]
        }
        self.assertEqual(self.engine._get_path_value(state, "session.mode"), "SURVIVAL")
        self.assertEqual(self.engine._get_path_value(state, "session.stats.energy"), 100.0)
        self.assertEqual(self.engine._get_path_value(state, "inventory[0].durability"), 85)
        self.assertEqual(self.engine._get_path_value(state, "inventory[1].id"), "shield")
        self.assertEqual(self.engine._get_path_value(state, "inventory.length"), 2)
        self.assertIsNone(self.engine._get_path_value(state, "session.stats.nonexistent"))
        self.assertIsNone(self.engine._get_path_value(state, "inventory[99]"))

    # =========================================================================
    # 4. ATOMIC MUTATION ACTIONS
    # =========================================================================

    def test_engine_set_path(self):
        """Verify set_path mutates nested object and array locations."""
        state = {"user": {"name": "Alice", "tags": ["admin", "tester"]}}
        self.engine._set_path_value(state, "user.name", "Bob")
        self.assertEqual(state["user"]["name"], "Bob")

        self.engine._set_path_value(state, "user.tags[1]", "moderator")
        self.assertEqual(state["user"]["tags"][1], "moderator")

    def test_engine_increment_path(self):
        """Verify increment_path adds positive and negative numeric deltas."""
        state = {"stats": {"energy": 50.0, "level": 1}}
        self.engine._increment_path_value(state, "stats.energy", 25.5)
        self.assertEqual(state["stats"]["energy"], 75.5)

        self.engine._increment_path_value(state, "stats.level", 1)
        self.assertEqual(state["stats"]["level"], 2)

    def test_engine_push_and_pop(self):
        """Verify push appends and pop removes elements from lists."""
        state = {"inventory": [{"id": "item_1"}]}
        self.engine._push_path_value(state, "inventory", {"id": "item_2"})
        self.assertEqual(len(state["inventory"]), 2)
        self.assertEqual(state["inventory"][1]["id"], "item_2")

        # Pop last element
        self.engine._pop_path_value(state, "inventory", -1)
        self.assertEqual(len(state["inventory"]), 1)
        self.assertEqual(state["inventory"][0]["id"], "item_1")

    def test_engine_delete_key(self):
        """Verify delete_key removes keys from nested dictionaries."""
        state = {"zones": {"north": {"unlocked": True}, "south": {"unlocked": False}}}
        self.engine._delete_path_key(state, "zones.south")
        self.assertNotIn("south", state["zones"])
        self.assertIn("north", state["zones"])

    # =========================================================================
    # 5. STATE PATH CONDITION TRIGGERS
    # =========================================================================

    def test_engine_state_path_conditions(self):
        """Verify conditions with state_path and comparison operators."""
        state = {
            "session": {"stats": {"score": 100, "rank": "GOLD"}},
            "items": [1, 2, 3]
        }
        entities = []
        entity_map = {}

        # Greater than / equal
        c1 = Condition(state_path="session.stats.score", op=">=", value=100)
        self.assertTrue(self.engine._evaluate_rule_condition(c1, entities, entity_map, state))

        # Array length query
        c2 = Condition(state_path="items.length", op="==", value=3)
        self.assertTrue(self.engine._evaluate_rule_condition(c2, entities, entity_map, state))

        # Not equal operator
        c3 = Condition(state_path="session.stats.rank", op="!=", value="BRONZE")
        self.assertTrue(self.engine._evaluate_rule_condition(c3, entities, entity_map, state))

        # False condition
        c4 = Condition(state_path="session.stats.score", op="<", value=50)
        self.assertFalse(self.engine._evaluate_rule_condition(c4, entities, entity_map, state))

    # =========================================================================
    # 6. CAPSTONE SIMULATION & FULL LIFECYCLE
    # =========================================================================

    def test_emergent_inventory_system_simulation(self):
        """Verify complete step execution of examples/inventory_system.mlue."""
        doc = load_mlue(self.examples_dir / "inventory_system.mlue")
        sim_state = self.engine.init_simulation(doc)
        dt = 1.0 / 60.0

        # Step 300 ticks to allow collector to hit gems
        for _ in range(300):
            sim_state = self.engine.step(sim_state, dt)

        # Assert items were collected and pushed to inventory
        stats = sim_state.state_variables["session"]["stats"]
        self.assertGreater(stats["gems_collected"], 0)
        self.assertGreater(stats["energy"], 100.0)

    # =========================================================================
    # 7. DETERMINISM & CRYPTOGRAPHIC REPEATABILITY
    # =========================================================================

    def test_50k_ticks_hierarchical_determinism(self):
        """Verify 50,000 continuous simulation steps produce bit-exact SHA-256 digest on hierarchical state."""
        def run_sim():
            doc = load_mlue(self.examples_dir / "inventory_system.mlue")
            state = self.engine.init_simulation(doc)
            dt = 1.0 / 60.0
            for _ in range(50000):
                state = self.engine.step(state, dt)
            hasher = hashlib.sha256()
            for e in state.entities:
                hasher.update(f"{e.id}:{e.position.x:.12f}:{e.position.y:.12f}:{e.velocity.vx:.12f}:{e.velocity.vy:.12f}:{e.active}".encode("utf-8"))
            # Hash nested state deterministically
            def hash_obj(obj):
                if isinstance(obj, dict):
                    for k in sorted(obj.keys()):
                        hasher.update(f"k:{k}".encode("utf-8"))
                        hash_obj(obj[k])
                elif isinstance(obj, list):
                    for item in obj:
                        hash_obj(item)
                else:
                    hasher.update(f"v:{obj}".encode("utf-8"))
            hash_obj(state.state_variables)
            return hasher.hexdigest()

        hash1 = run_sim()
        hash2 = run_sim()
        self.assertEqual(hash1, hash2)
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 64)


if __name__ == "__main__":
    unittest.main()
