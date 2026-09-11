"""Unit Tests for WEDGE 2 - Phase 1: Pointer Input & Spatial Interaction Manifold.

Verifies:
1. Analytical point-in-shape hit testing for circles, boxes, capsules, and segments.
2. Scene hit-testing with top-most z-order resolution and AABB broadphase culling.
3. Pointer lifecycle events: pointer_down, pointer_up, pointer_click, hover_enter, hover_exit.
4. Drag-off click cancellation.
5. Interactive reference document execution (examples/interactive_button_counter.mlue).
6. Near-zero heap allocation churn under continuous pointer input.
"""

import math
import tracemalloc
import unittest
from pathlib import Path
from runtime.model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    Velocity,
    CircleSize,
    BoxSize,
    CapsuleSize,
    SegmentSize,
    TextSize,
    PointerState,
    Rule,
    Action,
)
from runtime.spatial import (
    point_in_circle,
    point_in_box,
    point_in_capsule,
    point_near_segment,
    hit_test_entity,
    hit_test_scene,
)
from runtime.engine import MLUEEngine
from runtime.loader import load_mlue, validate_and_parse


class TestAnalyticalHitTesting(unittest.TestCase):
    """Verifies analytical point-in-shape geometric solvers."""

    def test_point_in_circle(self):
        cx, cy, r = 0.5, 0.5, 0.1
        env = Environment(width=400, height=400)
        # Center is inside
        self.assertTrue(point_in_circle(0.5, 0.5, cx, cy, r, env))
        # Point within radius
        self.assertTrue(point_in_circle(0.55, 0.5, cx, cy, r, env))
        # Exact boundary
        self.assertTrue(point_in_circle(0.6, 0.5, cx, cy, r, env))
        # Outside
        self.assertFalse(point_in_circle(0.65, 0.5, cx, cy, r, env))

    def test_point_in_circle_aspect_ratio(self):
        # Viewport 800x400: min_dim=400, scale_x=2.0, scale_y=1.0
        env = Environment(width=800, height=400)
        cx, cy, r = 0.5, 0.5, 0.1
        # In isotropic space: x is scaled by 2.0. So dx_norm = 0.05 -> dx_iso = 0.10 (boundary)
        self.assertTrue(point_in_circle(0.55, 0.5, cx, cy, r, env))
        self.assertFalse(point_in_circle(0.56, 0.5, cx, cy, r, env))

    def test_point_in_box(self):
        bx, by, w, h = 0.5, 0.5, 0.2, 0.1
        # Center
        self.assertTrue(point_in_box(0.5, 0.5, bx, by, w, h))
        # Corner (0.6, 0.55)
        self.assertTrue(point_in_box(0.6, 0.55, bx, by, w, h))
        # Just outside corner
        self.assertFalse(point_in_box(0.61, 0.55, bx, by, w, h))
        self.assertFalse(point_in_box(0.6, 0.56, bx, by, w, h))

    def test_point_in_capsule(self):
        cap_x, cap_y = 0.5, 0.5
        length = 0.2
        radius = 0.05
        env = Environment(width=400, height=400)

        # Center of capsule
        self.assertTrue(point_in_capsule(0.5, 0.5, cap_x, cap_y, length, radius, angle=0.0, env=env))
        # Along horizontal core (length=0.2 means x in [0.4, 0.6])
        self.assertTrue(point_in_capsule(0.4, 0.5, cap_x, cap_y, length, radius, angle=0.0, env=env))
        self.assertTrue(point_in_capsule(0.6, 0.5, cap_x, cap_y, length, radius, angle=0.0, env=env))
        # Semi-circular end cap tip (0.6 + 0.05 = 0.65)
        self.assertTrue(point_in_capsule(0.64, 0.5, cap_x, cap_y, length, radius, angle=0.0, env=env))
        # Outside cap
        self.assertFalse(point_in_capsule(0.66, 0.5, cap_x, cap_y, length, radius, angle=0.0, env=env))

    def test_point_near_segment(self):
        env = Environment(width=400, height=400)
        # Horizontal segment from (0.2, 0.5) to (0.8, 0.5) with thickness 0.02
        self.assertTrue(point_near_segment(0.5, 0.5, 0.2, 0.5, 0.8, 0.5, 0.02, env=env))
        self.assertTrue(point_near_segment(0.5, 0.509, 0.2, 0.5, 0.8, 0.5, 0.02, env=env))
        # Outside thickness
        self.assertFalse(point_near_segment(0.5, 0.52, 0.2, 0.5, 0.8, 0.5, 0.02, env=env))


class TestSceneHitTesting(unittest.TestCase):
    """Verifies scene-level hit testing and z-order resolution."""

    def test_topmost_resolution(self):
        env = Environment(width=400, height=400)
        e1 = Entity("bottom_box", "box", Position(0.5, 0.5), BoxSize(0.4, 0.4), Velocity(0, 0), properties={})
        e2 = Entity("top_circle", "circle", Position(0.5, 0.5), CircleSize(0.1), Velocity(0, 0), properties={})

        # At center, both hit; e2 is declared second (on top)
        hit_id = hit_test_scene([e1, e2], 0.5, 0.5, env=env)
        self.assertEqual(hit_id, "top_circle")

        # Outside e2 but inside e1
        hit_id2 = hit_test_scene([e1, e2], 0.65, 0.5, env=env)
        self.assertEqual(hit_id2, "bottom_box")

        # Outside both
        hit_id3 = hit_test_scene([e1, e2], 0.8, 0.8, env=env)
        self.assertIsNone(hit_id3)

    def test_inactive_entity_skipped(self):
        env = Environment(width=400, height=400)
        e1 = Entity("box_a", "box", Position(0.5, 0.5), BoxSize(0.2, 0.2), Velocity(0, 0), properties={}, active=False)
        e2 = Entity("box_b", "box", Position(0.5, 0.5), BoxSize(0.4, 0.4), Velocity(0, 0), properties={}, active=True)

        hit_id = hit_test_scene([e1, e2], 0.5, 0.5, env=env)
        self.assertEqual(hit_id, "box_b")


class TestPointerInteractionLifecycle(unittest.TestCase):
    """Verifies click, down, up, and hover event lifecycles in the engine."""

    def setUp(self):
        self.engine = MLUEEngine()
        self.env = Environment(width=400, height=400)
        self.button = Entity(
            id="target_btn",
            type="capsule",
            position=Position(0.5, 0.5),
            size=CapsuleSize(length=0.2, radius=0.05, angle=0.0),
            velocity=Velocity(0, 0),
            properties={"solid": False},
        )
        self.rules = [
            Rule(
                trigger="click_rule",
                event="pointer_click",
                entity="target_btn",
                actions=[Action(type="increment_path", target="clicks", amount=1)],
            ),
            Rule(
                trigger="down_rule",
                event="pointer_down",
                entity="target_btn",
                actions=[Action(type="set_path", target="is_down", value=True)],
            ),
            Rule(
                trigger="up_rule",
                event="pointer_up",
                entity="target_btn",
                actions=[Action(type="set_path", target="is_down", value=False)],
            ),
            Rule(
                trigger="hover_enter_rule",
                event="pointer_hover_enter",
                entity="target_btn",
                actions=[Action(type="set_path", target="hovered", value=True)],
            ),
            Rule(
                trigger="hover_exit_rule",
                event="pointer_hover_exit",
                entity="target_btn",
                actions=[Action(type="set_path", target="hovered", value=False)],
            ),
        ]
        self.doc = MLUEDocument(
            version="2.1",
            environment=self.env,
            entities=[self.button],
            state_variables={"clicks": 0, "is_down": False, "hovered": False},
            rules=self.rules,
        )
        self.state = self.engine.init_simulation(self.doc)

    def test_full_click_cycle(self):
        # Step 1: Hover over button
        s1 = self.engine.step(self.state, dt=0.016, inputs={"pointer": {"x": 0.5, "y": 0.5, "pressed": False}})
        self.assertTrue(s1.state_variables["hovered"])
        self.assertEqual(s1.state_variables["clicks"], 0)
        self.assertEqual(s1.pointer.hovered_entity_id, "target_btn")

        # Step 2: Press down on button
        s2 = self.engine.step(s1, dt=0.016, inputs={"pointer": {"x": 0.5, "y": 0.5, "pressed": True}})
        self.assertTrue(s2.state_variables["is_down"])
        self.assertEqual(s2.state_variables["clicks"], 0)
        self.assertEqual(s2.pointer.pressed_entity_id, "target_btn")

        # Step 3: Release while still on button (triggers click)
        s3 = self.engine.step(s2, dt=0.016, inputs={"pointer": {"x": 0.5, "y": 0.5, "pressed": False}})
        self.assertFalse(s3.state_variables["is_down"])
        self.assertEqual(s3.state_variables["clicks"], 1)

    def test_drag_off_cancels_click(self):
        # Step 1: Press down on button
        s1 = self.engine.step(self.state, dt=0.016, inputs={"pointer": {"x": 0.5, "y": 0.5, "pressed": True}})
        self.assertEqual(s1.pointer.pressed_entity_id, "target_btn")
        self.assertTrue(s1.state_variables["is_down"])

        # Step 2: Move pointer off button while still pressed
        s2 = self.engine.step(s1, dt=0.016, inputs={"pointer": {"x": 0.1, "y": 0.1, "pressed": True}})
        self.assertIsNone(s2.pointer.hovered_entity_id)
        self.assertEqual(s2.pointer.pressed_entity_id, "target_btn")

        # Step 3: Release outside button (click must NOT fire)
        s3 = self.engine.step(s2, dt=0.016, inputs={"pointer": {"x": 0.1, "y": 0.1, "pressed": False}})
        self.assertEqual(s3.state_variables["clicks"], 0)

    def test_hover_enter_and_exit(self):
        # Initial: outside
        s0 = self.engine.step(self.state, dt=0.016, inputs={"pointer": {"x": 0.1, "y": 0.1, "pressed": False}})
        self.assertFalse(s0.state_variables["hovered"])

        # Move inside -> hover_enter
        s1 = self.engine.step(s0, dt=0.016, inputs={"pointer": {"x": 0.5, "y": 0.5, "pressed": False}})
        self.assertTrue(s1.state_variables["hovered"])

        # Move outside -> hover_exit
        s2 = self.engine.step(s1, dt=0.016, inputs={"pointer": {"x": 0.9, "y": 0.9, "pressed": False}})
        self.assertFalse(s2.state_variables["hovered"])


class TestInteractiveDocument(unittest.TestCase):
    """Verifies loading and executing examples/interactive_button_counter.mlue."""

    def test_button_counter_execution(self):
        doc_path = Path(__file__).resolve().parent.parent / "examples" / "interactive_button_counter.mlue"
        self.assertTrue(doc_path.exists())
        doc = load_mlue(doc_path)
        self.assertEqual(doc.version, "2.1")

        engine = MLUEEngine()
        state = engine.init_simulation(doc)
        self.assertEqual(state.state_variables["counter"], 0)

        # 5 distinct clicks on button (x=0.5, y=0.55)
        for i in range(5):
            # Press
            state = engine.step(state, dt=0.016, inputs={"pointer": {"x": 0.5, "y": 0.55, "pressed": True}})
            # Release
            state = engine.step(state, dt=0.016, inputs={"pointer": {"x": 0.5, "y": 0.55, "pressed": False}})
            self.assertEqual(state.state_variables["counter"], i + 1)
            self.assertEqual(state.state_variables["status"], "CLICKED")

    def test_pointer_memory_churn(self):
        """Audits memory allocation churn under continuous pointer interaction."""
        doc_path = Path(__file__).resolve().parent.parent / "examples" / "interactive_button_counter.mlue"
        doc = load_mlue(doc_path)
        engine = MLUEEngine()
        state = engine.init_simulation(doc)

        # Warmup
        for _ in range(100):
            state = engine.step(state, dt=0.016, inputs={"pointer": {"x": 0.5, "y": 0.55, "pressed": False}})

        tracemalloc.start()
        snap_before = tracemalloc.take_snapshot()

        steps = 2000
        for i in range(steps):
            pressed = (i % 2 == 1)
            state = engine.step(state, dt=0.016, inputs={"pointer": {"x": 0.5, "y": 0.55, "pressed": pressed}})

        snap_after = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = snap_after.compare_to(snap_before, "lineno")
        total_alloc = sum(s.size_diff for s in stats if s.size_diff > 0)
        bytes_per_step = total_alloc / steps

        # Memory churn must be well under 100 B/step
        self.assertLess(bytes_per_step, 100.0)


if __name__ == "__main__":
    unittest.main()
