"""Unit tests for MLUE Phase 4: Dual-Mode Event Runtime & Responsive Edge Anchors.

Verifies:
- Quiescence detection for host CPU sleep (is_quiescent)
- Instantaneous dt=0.0 event execution (pointer clicks, state updates, 0 time advance)
- 9-point edge anchor resolution across different viewports (top-left, bottom-right, center, etc.)
- Hardware safe-area insets (notch/home-bar margins)
- Responsive auto-stacking (direction: "auto" landscape vs. portrait)
- Loader schema invariant validation
- Cyclomatic complexity bounds (NIST <= 30)
"""

import math
import unittest
from runtime.model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    BoxSize,
    CircleSize,
    Velocity,
    Rule,
    Action,
)
from runtime.engine import MLUEEngine
from runtime.spatial import get_anchor_origin, get_entity_effective_pos
from runtime.loader import validate_and_parse, MLUEValidationError


class TestEventRuntimeAndAnchors(unittest.TestCase):

    def setUp(self):
        self.engine = MLUEEngine()
        self.env = Environment(width=800, height=800)

    def test_quiescence_detection(self):
        """Verifies that is_quiescent accurately detects whether physics state is at rest."""
        # 1. Quiescent scene: Stationary entities
        doc_still = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="button",
                    type="box",
                    position=Position(0.5, 0.5),
                    size=BoxSize(width=0.2, height=0.08),
                    velocity=Velocity(vx=0.0, vy=0.0, omega=0.0),
                )
            ],
        )
        state_still = self.engine.init_simulation(doc_still)
        self.assertTrue(self.engine.is_quiescent(state_still))

        # 2. Non-quiescent: Linear velocity
        doc_moving = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="ball",
                    type="circle",
                    position=Position(0.5, 0.5),
                    size=CircleSize(radius=0.04),
                    velocity=Velocity(vx=0.1, vy=0.0, omega=0.0),
                )
            ],
        )
        state_moving = self.engine.init_simulation(doc_moving)
        self.assertFalse(self.engine.is_quiescent(state_moving))

        # 3. Non-quiescent: Angular spin
        doc_spinning = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="rotor",
                    type="box",
                    position=Position(0.5, 0.5),
                    size=BoxSize(width=0.2, height=0.05),
                    velocity=Velocity(vx=0.0, vy=0.0, omega=1.0),
                )
            ],
        )
        state_spinning = self.engine.init_simulation(doc_spinning)
        self.assertFalse(self.engine.is_quiescent(state_spinning))

    def test_zero_dt_pointer_click_processing(self):
        """Stepping with dt=0.0 dispatches pointer click and executes rules with zero time advance."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="btn_submit",
                    type="box",
                    position=Position(0.5, 0.5),
                    size=BoxSize(width=0.2, height=0.1),
                    properties={"color": "#3B82F6"},
                )
            ],
            state_variables={"clicks": 0},
            rules=[
                Rule(
                    trigger="on_click",
                    event="pointer_click",
                    entity="btn_submit",
                    actions=[Action(type="increment_path", target="clicks", amount=1.0)],
                )
            ],
        )

        state = self.engine.init_simulation(doc)
        self.assertEqual(state.time, 0.0)
        self.assertEqual(state.state_variables["clicks"], 0)

        # 1. Pointer Down on the button (dt = 0.0)
        state_down = self.engine.step(
            state,
            dt=0.0,
            inputs={"pointer": {"x": 0.5, "y": 0.5, "pressed": True}},
        )
        self.assertEqual(state_down.time, 0.0)  # Clock must not advance
        self.assertEqual(state_down.pointer.pressed_entity_id, "btn_submit")
        self.assertEqual(state_down.state_variables["clicks"], 0)

        # 2. Pointer Up on the button (dt = 0.0) -> triggers pointer_click
        state_up = self.engine.step(
            state_down,
            dt=0.0,
            inputs={"pointer": {"x": 0.5, "y": 0.5, "pressed": False}},
        )
        self.assertEqual(state_up.time, 0.0)  # Clock still 0.0
        self.assertIsNone(state_up.pointer.pressed_entity_id)
        # Rule executed: clicks incremented to 1
        self.assertEqual(state_up.state_variables["clicks"], 1)

    def test_9_point_edge_anchors(self):
        """Validates that all 9 edge anchor origins are calculated correctly."""
        env_standard = Environment(width=1920, height=1080)

        # Test each anchor origin
        origins = {
            "top-left": (0.0, 0.0),
            "top-center": (0.5, 0.0),
            "top-right": (1.0, 0.0),
            "center-left": (0.0, 0.5),
            "center": (0.5, 0.5),
            "center-right": (1.0, 0.5),
            "bottom-left": (0.0, 1.0),
            "bottom-center": (0.5, 1.0),
            "bottom-right": (1.0, 1.0),
        }

        for anchor_name, expected_origin in origins.items():
            ox, oy = get_anchor_origin(anchor_name, env_standard)
            self.assertAlmostEqual(ox, expected_origin[0], places=5, msg=f"Mismatch for {anchor_name} X")
            self.assertAlmostEqual(oy, expected_origin[1], places=5, msg=f"Mismatch for {anchor_name} Y")

    def test_edge_anchored_entity_geometry(self):
        """Edge-anchored entities evaluate concrete screen coordinates relative to viewport corners."""
        # Speedometer anchored at top-right with offset (-0.05, 0.05)
        # Pedal anchored at bottom-right with offset (-0.08, -0.08)
        # Pause button anchored at top-left with offset (0.05, 0.05)
        doc = MLUEDocument(
            version="1.6",
            environment=Environment(width=1600, height=900),  # 16:9
            entities=[
                Entity(
                    id="pause_btn",
                    type="box",
                    position=Position(0.05, 0.05),
                    size=BoxSize(width=0.06, height=0.06),
                    anchor="top-left",
                ),
                Entity(
                    id="speedometer",
                    type="circle",
                    position=Position(-0.06, 0.06),
                    size=CircleSize(radius=0.04),
                    anchor="top-right",
                ),
                Entity(
                    id="pedal_gas",
                    type="box",
                    position=Position(-0.08, -0.08),
                    size=BoxSize(width=0.06, height=0.12),
                    anchor="bottom-right",
                ),
            ],
        )

        res = self.engine.evaluate(doc)
        shape_by_id = {s.id: s for s in res.shapes}

        # pause_btn center should be at (0.05 * 1600, 0.05 * 900) = (80.0, 45.0)
        self.assertAlmostEqual(shape_by_id["pause_btn"].center[0], 80.0, places=2)
        self.assertAlmostEqual(shape_by_id["pause_btn"].center[1], 45.0, places=2)

        # speedometer center should be at ((1.0 - 0.06) * 1600, 0.06 * 900) = (1504.0, 54.0)
        self.assertAlmostEqual(shape_by_id["speedometer"].center[0], 1504.0, places=2)
        self.assertAlmostEqual(shape_by_id["speedometer"].center[1], 54.0, places=2)

        # pedal_gas center should be at ((1.0 - 0.08) * 1600, (1.0 - 0.08) * 900) = (1472.0, 828.0)
        self.assertAlmostEqual(shape_by_id["pedal_gas"].center[0], 1472.0, places=2)
        self.assertAlmostEqual(shape_by_id["pedal_gas"].center[1], 828.0, places=2)

    def test_safe_area_insets(self):
        """Safe-area insets adjust edge anchor origins to prevent occlusion by notches / home bars."""
        env_with_notch = Environment(
            width=390,
            height=844,  # Modern smartphone portrait
            safe_area={"top": 0.055, "bottom": 0.040, "left": 0.020, "right": 0.020},
        )

        # Top-left anchor should shift right by 0.020 and down by 0.055
        ox_tl, oy_tl = get_anchor_origin("top-left", env_with_notch)
        self.assertAlmostEqual(ox_tl, 0.020, places=5)
        self.assertAlmostEqual(oy_tl, 0.055, places=5)

        # Bottom-right anchor should shift left by 0.020 and up by 0.040
        ox_br, oy_br = get_anchor_origin("bottom-right", env_with_notch)
        self.assertAlmostEqual(ox_br, 1.0 - 0.020, places=5)
        self.assertAlmostEqual(oy_br, 1.0 - 0.040, places=5)

    def test_direction_auto_responsive_stacking(self):
        """direction: 'auto' stacks horizontally in landscape and vertically in portrait."""
        def make_stack_doc(w: int, h: int) -> MLUEDocument:
            return MLUEDocument(
                version="1.6",
                environment=Environment(width=w, height=h),
                entities=[
                    Entity(
                        id="container",
                        type="box",
                        position=Position(0.5, 0.5),
                        size=BoxSize(width=0.8, height=0.8),
                        layout={"direction": "auto", "gap": 0.02, "padding": 0.05},
                    ),
                    Entity(
                        id="card_1",
                        type="box",
                        position=Position(0.0, 0.0),
                        size=BoxSize(width=0.2, height=0.2),
                        parent_id="container",
                    ),
                    Entity(
                        id="card_2",
                        type="box",
                        position=Position(0.0, 0.0),
                        size=BoxSize(width=0.2, height=0.2),
                        parent_id="container",
                    ),
                ],
            )

        # 1. Landscape (W=1200 > H=600): Cards should stack horizontally (different X, same Y)
        doc_landscape = make_stack_doc(1200, 600)
        res_landscape = self.engine.evaluate(doc_landscape)
        shapes_land = {s.id: s for s in res_landscape.shapes}
        c1_land = shapes_land["card_1"].center
        c2_land = shapes_land["card_2"].center
        self.assertNotEqual(c1_land[0], c2_land[0])  # Stacked along X
        self.assertAlmostEqual(c1_land[1], c2_land[1], places=2)  # Same Y

        # 2. Portrait (W=400 < H=800): Cards should stack vertically (same X, different Y)
        doc_portrait = make_stack_doc(400, 800)
        res_portrait = self.engine.evaluate(doc_portrait)
        shapes_port = {s.id: s for s in res_portrait.shapes}
        c1_port = shapes_port["card_1"].center
        c2_port = shapes_port["card_2"].center
        self.assertAlmostEqual(c1_port[0], c2_port[0], places=2)  # Same X
        self.assertNotEqual(c1_port[1], c2_port[1])  # Stacked along Y

    def test_loader_anchor_and_safe_area_validation(self):
        """Loader enforces valid anchor names and numerical safe area bounds."""
        base_doc = {
            "mlue_version": "1.6",
            "environment": {"dimensions": [400, 400]},
            "entities": [
                {"id": "e1", "type": "box", "position": {"x": 0.5, "y": 0.5}, "size": {"width": 0.1, "height": 0.1}}
            ],
        }

        # 1. Invalid anchor name
        bad_anchor_doc = dict(base_doc)
        bad_anchor_doc["entities"] = [
            {"id": "e1", "type": "box", "position": {"x": 0.5, "y": 0.5}, "size": {"width": 0.1, "height": 0.1}, "anchor": "floating-top"}
        ]
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(bad_anchor_doc)

        # 2. Negative safe area inset
        bad_sa_doc = dict(base_doc)
        bad_sa_doc["environment"] = {"dimensions": [400, 400], "safe_area": {"top": -0.05}}
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(bad_sa_doc)

        # 3. Excessive safe area inset (>= 0.5)
        bad_sa_doc2 = dict(base_doc)
        bad_sa_doc2["environment"] = {"dimensions": [400, 400], "safe_area": {"bottom": 0.6}}
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(bad_sa_doc2)

        # 4. Valid document with anchor and safe_area
        good_doc = dict(base_doc)
        good_doc["environment"] = {
            "dimensions": [400, 400],
            "safe_area": {"top": 0.05, "bottom": 0.03, "left": 0.02, "right": 0.02},
        }
        good_doc["entities"] = [
            {
                "id": "e1",
                "type": "box",
                "position": {"x": 0.0, "y": 0.0},
                "size": {"width": 0.1, "height": 0.1},
                "anchor": "bottom-right",
            }
        ]
        parsed = validate_and_parse(good_doc)
        self.assertEqual(parsed.entities[0].anchor, "bottom-right")
        self.assertIsNotNone(parsed.environment.safe_area)
        self.assertEqual(parsed.environment.safe_area["top"], 0.05)

    def test_cyclomatic_complexity_bounds(self):
        """Verifies that step and is_quiescent adhere to NIST CC <= 30."""
        import ast
        import inspect

        def calculate_cc(node):
            complexity = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                    complexity += 1
                elif isinstance(child, ast.BoolOp):
                    complexity += len(child.values) - 1
            return complexity

        engine_source = inspect.getsource(MLUEEngine)
        tree = ast.parse(engine_source)

        for item in tree.body[0].body:
            if isinstance(item, ast.FunctionDef) and item.name in ("step", "is_quiescent"):
                cc = calculate_cc(item)
                self.assertLessEqual(
                    cc, 30, f"Method {item.name} exceeds NIST CC bound: {cc} > 30"
                )


if __name__ == "__main__":
    unittest.main()
