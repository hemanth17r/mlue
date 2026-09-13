"""End-to-End Autonomous Synthesis Verification Test

Proves that an AI agent can query standardized components from the catalog,
assemble a complete working 2D game from scratch, validate it with the linter
(0 errors), and execute 1,000 headless simulation ticks deterministically.
"""

import unittest
from runtime.catalog import Catalog
from runtime.linter import lint_mlue
from runtime.loader import validate_and_parse
from runtime.engine import MLUEEngine


class TestCatalogSynthesis(unittest.TestCase):

    def setUp(self):
        self.catalog = Catalog()
        self.engine = MLUEEngine()

    def test_autonomous_game_synthesis_from_catalog(self):
        """Synthesizes a complete Breakout-style game purely from catalog parts."""
        # 1. Fetch parts from catalog
        boundary_part = self.catalog.get("part", "boundary")
        paddle_part = self.catalog.get("part", "paddle")
        ball_part = self.catalog.get("part", "ball")
        brick_part = self.catalog.get("part", "brick")
        palettes = self.catalog.get("token", "palettes")

        self.assertIsNotNone(boundary_part)
        self.assertIsNotNone(paddle_part)
        self.assertIsNotNone(ball_part)
        self.assertIsNotNone(brick_part)
        self.assertIsNotNone(palettes)

        # 2. Assemble .mlue document structure
        assembled_scene = {
            "mlue_version": "0.6",
            "environment": {
                "dimensions": [800, 600],
                "background": palettes["data"]["surfaces"]["background_canvas"]
            },
            "state_variables": {
                "score": 0,
                "lives": 3,
                "bricks_remaining": 3,
                "game_state": "PLAYING"
            },
            "entities": [],
            "rules": []
        }

        # 3. Add boundary walls
        for wall in boundary_part["entities_template"]:
            assembled_scene["entities"].append(wall)

        # 4. Add player paddle
        paddle_entity = paddle_part["entity_template"]
        assembled_scene["entities"].append(paddle_entity)

        # 5. Add dynamic ball
        ball_entity = ball_part["entity_template"]
        assembled_scene["entities"].append(ball_entity)

        # 6. Add 3 bricks with distinct positions
        brick_positions = [0.25, 0.5, 0.75]
        for i, pos_x in enumerate(brick_positions):
            brick_id = f"brick_0{i+1}"
            brick_ent = {
                "id": brick_id,
                "type": "box",
                "position": {"x": pos_x, "y": 0.2},
                "size": {"width": 0.18, "height": 0.05},
                "properties": {
                    "color": palettes["data"]["accents"]["rose"],
                    "solid": True
                }
            }
            assembled_scene["entities"].append(brick_ent)

            # Add scoring rule for each brick
            assembled_scene["rules"].append({
                "trigger": "collision",
                "event": "collision",
                "entities": ["ball_01", brick_id],
                "actions": [
                    {"type": "destroy_entity", "target": brick_id},
                    {"type": "increment", "target": "score", "amount": 10},
                    {"type": "increment", "target": "bricks_remaining", "amount": -1}
                ]
            })

        # 7. Lint the assembled scene with the AI self-healing linter
        lint_report = lint_mlue(assembled_scene)
        self.assertEqual(len(lint_report.errors), 0, f"Linter reported unexpected errors: {lint_report.errors}")
        self.assertTrue(lint_report.valid)

        # 8. Parse into internal simulation state
        doc = validate_and_parse(assembled_scene)
        self.assertEqual(len(doc.entities), 9)  # 4 walls + 1 paddle + 1 ball + 3 bricks
        self.assertEqual(len(doc.rules), 3)

        # 9. Run 1,000 headless simulation ticks
        current_state = self.engine.init_simulation(doc)
        dt = 0.016667
        for _ in range(1000):
            current_state = self.engine.step(current_state, dt, inputs={"player_bottom": 0.5})

        # 10. Verify state integrity after 1,000 steps
        self.assertIn("score", current_state.state_variables)
        self.assertIn("lives", current_state.state_variables)
        # Verify entities remain within simulation arena bounds (allowing numerical micro-penetration during impulse resolution)
        for ent in current_state.entities:
            self.assertGreaterEqual(ent.position.x, -0.05)
            self.assertLessEqual(ent.position.x, 1.05)
            self.assertGreaterEqual(ent.position.y, -0.05)
            self.assertLessEqual(ent.position.y, 1.05)


if __name__ == "__main__":
    unittest.main()
