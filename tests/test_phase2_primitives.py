"""MLUE Phase 2.1 Unit Tests: Universal Spatial Substrate

Verifies continuous line segments, swept rounded capsules, declarative state-bound typography,
parent-child spatial hierarchy, container auto-stacking (stack_x, stack_y), analytical O(1)
distance solvers, pairwise narrowphase collision physics, and static schema validation.
"""

import unittest
import math
from runtime.model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    Velocity,
    CircleSize,
    BoxSize,
    SegmentSize,
    CapsuleSize,
    TextSize,
    Rule,
    Condition,
    Action,
)
from runtime.loader import validate_and_parse, MLUEValidationError
from runtime.engine import (
    MLUEEngine,
    _analytical_point_to_segment,
    _analytical_segment_to_segment,
)



class TestAnalyticalDistanceSolvers(unittest.TestCase):
    """Verifies closed-form O(1) analytical distance solvers."""

    def test_point_to_segment_interior(self):
        """Point projecting orthogonally onto segment interior."""
        # Segment from (0.0, 0.5) to (1.0, 0.5), point at (0.5, 0.8)
        _, _, dist, _, _ = _analytical_point_to_segment(0.5, 0.8, 0.0, 0.5, 1.0, 0.5)
        self.assertAlmostEqual(dist, 0.3, places=7)

    def test_point_to_segment_clamped_start(self):
        """Point projecting before start point A clamps to A."""
        # Segment from (0.2, 0.2) to (0.8, 0.2), point at (0.0, 0.2)
        _, _, dist, _, _ = _analytical_point_to_segment(0.0, 0.2, 0.2, 0.2, 0.8, 0.2)
        self.assertAlmostEqual(dist, 0.2, places=7)

    def test_point_to_segment_clamped_end(self):
        """Point projecting past end point B clamps to B."""
        # Segment from (0.2, 0.2) to (0.8, 0.2), point at (1.0, 0.2)
        _, _, dist, _, _ = _analytical_point_to_segment(1.0, 0.2, 0.2, 0.2, 0.8, 0.2)
        self.assertAlmostEqual(dist, 0.2, places=7)

    def test_point_to_segment_on_line(self):
        """Point lying directly on the line segment has distance 0.0."""
        _, _, dist, _, _ = _analytical_point_to_segment(0.5, 0.5, 0.1, 0.5, 0.9, 0.5)
        self.assertAlmostEqual(dist, 0.0, places=7)

    def test_point_to_segment_degenerate(self):
        """Degenerate zero-length segment computes point-to-point Euclidean distance."""
        _, _, dist, _, _ = _analytical_point_to_segment(0.3, 0.4, 0.0, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(dist, 0.5, places=7)

    def test_segment_to_segment_parallel(self):
        """Parallel horizontal segments."""
        # S1: (0.1, 0.2) -> (0.9, 0.2), S2: (0.1, 0.6) -> (0.9, 0.6)
        _, _, _, _, dist, _, _ = _analytical_segment_to_segment(
            0.1, 0.2, 0.9, 0.2,
            0.1, 0.6, 0.9, 0.6,
        )
        self.assertAlmostEqual(dist, 0.4, places=7)

    def test_segment_to_segment_intersecting(self):
        """Intersecting cross segments have distance 0.0."""
        # S1: (0.0, 0.5) -> (1.0, 0.5), S2: (0.5, 0.0) -> (0.5, 1.0)
        _, _, _, _, dist, _, _ = _analytical_segment_to_segment(
            0.0, 0.5, 1.0, 0.5,
            0.5, 0.0, 0.5, 1.0,
        )
        self.assertAlmostEqual(dist, 0.0, places=7)

    def test_segment_to_segment_collinear_overlapping(self):
        """Collinear overlapping segments have distance 0.0."""
        _, _, _, _, dist, _, _ = _analytical_segment_to_segment(
            0.1, 0.5, 0.6, 0.5,
            0.4, 0.5, 0.9, 0.5,
        )
        self.assertAlmostEqual(dist, 0.0, places=7)

    def test_segment_to_segment_collinear_disjoint(self):
        """Collinear disjoint segments have distance equal to gap between endpoints."""
        _, _, _, _, dist, _, _ = _analytical_segment_to_segment(
            0.1, 0.5, 0.3, 0.5,
            0.5, 0.5, 0.8, 0.5,
        )
        self.assertAlmostEqual(dist, 0.2, places=7)

    def test_segment_to_segment_perpendicular_disjoint(self):
        """Perpendicular disjoint segments."""
        # S1: (0.0, 0.0) -> (0.4, 0.0), S2: (0.5, 0.2) -> (0.5, 0.8)
        _, _, _, _, dist, _, _ = _analytical_segment_to_segment(
            0.0, 0.0, 0.4, 0.0,
            0.5, 0.2, 0.5, 0.8,
        )
        # Shortest distance is between (0.4, 0.0) and (0.5, 0.2) = sqrt(0.1^2 + 0.2^2) = sqrt(0.05)
        expected = math.sqrt(0.01 + 0.04)
        self.assertAlmostEqual(dist, expected, places=7)

    def test_segment_to_segment_degenerate(self):
        """Degenerate zero-length segments fall back to point-to-point distance."""
        _, _, _, _, dist, _, _ = _analytical_segment_to_segment(
            0.1, 0.1, 0.1, 0.1,
            0.4, 0.5, 0.4, 0.5,
        )
        # sqrt(0.3^2 + 0.4^2) = 0.5
        self.assertAlmostEqual(dist, 0.5, places=7)


class TestStaticSchemaValidation(unittest.TestCase):
    """Verifies schema validation for Phase 2 primitives, cycles, and constraints."""

    def test_valid_phase2_document(self):
        """Valid document containing segment, capsule, text, and layout loads without error."""
        raw = {
            "mlue_version": "2.1",
            "environment": {"dimensions": [800, 600], "background": "#0F172A"},
            "state_variables": {"title": "Dashboard", "counter": 42},
            "entities": [
                {
                    "id": "container",
                    "type": "box",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.8, "height": 0.8},
                    "layout": {"direction": "vertical", "gap": 0.02},
                    "properties": {"color": "#1E293B"},
                },
                {
                    "id": "lbl",
                    "type": "text",
                    "parent_id": "container",
                    "template": "Title: {title} ({counter})",
                    "size": {"font_scale": 0.02, "align": "left"},
                    "properties": {"color": "#FFFFFF"},
                },
                {
                    "id": "div",
                    "type": "segment",
                    "parent_id": "container",
                    "start": {"x": 0.1, "y": 0.0},
                    "end": {"x": 0.9, "y": 0.0},
                    "thickness": 0.002,
                    "properties": {"color": "#475569"},
                },
                {
                    "id": "badge",
                    "type": "capsule",
                    "parent_id": "container",
                    "size": {"radius": 0.02, "length": 0.1, "angle": 0.0},
                    "properties": {"color": "#22C55E"},
                },
            ],
            "rules": [],
        }
        doc = validate_and_parse(raw)
        self.assertEqual(len(doc.entities), 4)
        self.assertEqual(doc.entities[1].type, "text")
        self.assertEqual(doc.entities[2].type, "segment")
        self.assertEqual(doc.entities[3].type, "capsule")

    def test_invalid_segment_start_out_of_bounds(self):
        """Segment with start coordinates < 0.0 or > 1.0 is rejected."""
        raw = {
            "mlue_version": "2.1",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "seg_bad",
                    "type": "segment",
                    "start": {"x": -0.1, "y": 0.5},
                    "end": {"x": 0.9, "y": 0.5},
                    "thickness": 0.002,
                }
            ],
            "rules": [],
        }
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(raw)

    def test_invalid_segment_thickness(self):
        """Segment with non-positive thickness is rejected."""
        raw = {
            "mlue_version": "2.1",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "seg_bad",
                    "type": "segment",
                    "start": {"x": 0.1, "y": 0.5},
                    "end": {"x": 0.9, "y": 0.5},
                    "thickness": -0.01,
                }
            ],
            "rules": [],
        }
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(raw)

    def test_invalid_capsule_negative_radius(self):
        """Capsule with radius <= 0 is rejected."""
        raw = {
            "mlue_version": "2.1",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "cap_bad",
                    "type": "capsule",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"radius": -0.05, "length": 0.1},
                }
            ],
            "rules": [],
        }
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(raw)

    def test_invalid_capsule_negative_length(self):
        """Capsule with length < 0 is rejected."""
        raw = {
            "mlue_version": "2.1",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "cap_bad",
                    "type": "capsule",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"radius": 0.05, "length": -0.2},
                }
            ],
            "rules": [],
        }
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(raw)

    def test_invalid_text_align(self):
        """Text with invalid alignment option is rejected."""
        raw = {
            "mlue_version": "2.1",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "txt_bad",
                    "type": "text",
                    "template": "Hello",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"font_scale": 0.02, "align": "diagonal"},
                }
            ],
            "rules": [],
        }
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(raw)

    def test_hierarchy_nonexistent_parent(self):
        """Entity referencing a non-existent parent_id is rejected."""
        raw = {
            "mlue_version": "2.1",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "orphan",
                    "type": "box",
                    "parent_id": "ghost_parent",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.1, "height": 0.1},
                }
            ],
            "rules": [],
        }
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(raw)

    def test_hierarchy_self_reference_cycle(self):
        """Entity referencing itself as parent is rejected."""
        raw = {
            "mlue_version": "2.1",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "narcissus",
                    "type": "box",
                    "parent_id": "narcissus",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.1, "height": 0.1},
                }
            ],
            "rules": [],
        }
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(raw)

    def test_hierarchy_two_node_cycle(self):
        """Cyclic parent-child reference A -> B -> A is rejected."""
        raw = {
            "mlue_version": "2.1",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "node_a",
                    "type": "box",
                    "parent_id": "node_b",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.1, "height": 0.1},
                },
                {
                    "id": "node_b",
                    "type": "box",
                    "parent_id": "node_a",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.1, "height": 0.1},
                },
            ],
            "rules": [],
        }
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(raw)

    def test_hierarchy_multi_node_cycle(self):
        """Three-node cycle A -> B -> C -> A is rejected."""
        raw = {
            "mlue_version": "2.1",
            "environment": {"dimensions": [400, 400], "background": "#000000"},
            "entities": [
                {
                    "id": "a",
                    "type": "box",
                    "parent_id": "c",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.1, "height": 0.1},
                },
                {
                    "id": "b",
                    "type": "box",
                    "parent_id": "a",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.1, "height": 0.1},
                },
                {
                    "id": "c",
                    "type": "box",
                    "parent_id": "b",
                    "position": {"x": 0.5, "y": 0.5},
                    "size": {"width": 0.1, "height": 0.1},
                },
            ],
            "rules": [],
        }
        with self.assertRaises(MLUEValidationError):
            validate_and_parse(raw)


class TestAutoStackingAndHierarchy(unittest.TestCase):
    """Verifies layout engine calculation of auto-stacking containers."""

    def setUp(self):
        self.engine = MLUEEngine()

    def test_vertical_stacking_positions(self):
        """Container with stack_y positions children monotonically with non-overlapping bounds."""
        doc = MLUEDocument(
            version="2.1",
            environment=Environment(width=800, height=800, background="#000000"),
            entities=[
                Entity(
                    id="container",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.8, height=0.8),
                    velocity=Velocity(0.0, 0.0),
                    properties={},
                    layout={"direction": "vertical", "gap": 0.02},
                ),
                Entity(
                    id="child_1",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.7, height=0.1),
                    velocity=Velocity(0.0, 0.0),
                    properties={},
                    parent_id="container",
                ),
                Entity(
                    id="child_2",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.7, height=0.15),
                    velocity=Velocity(0.0, 0.0),
                    properties={},
                    parent_id="container",
                ),
                Entity(
                    id="child_3",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.7, height=0.08),
                    velocity=Velocity(0.0, 0.0),
                    properties={},
                    parent_id="container",
                ),
            ],
            rules=[],
        )

        result = self.engine.evaluate(doc)
        shapes_by_id = {s.id: s for s in result.shapes}

        c1 = shapes_by_id["child_1"]
        c2 = shapes_by_id["child_2"]
        c3 = shapes_by_id["child_3"]

        # Y center positions must increase monotonically (downwards in screen coords)
        self.assertLess(c1.center[1], c2.center[1])
        self.assertLess(c2.center[1], c3.center[1])

        # Children must not overlap vertically: bottom of child N <= top of child N+1
        # bbox is (min_x, min_y, max_x, max_y)
        self.assertLessEqual(c1.bbox[3], c2.bbox[1] + 1e-4)
        self.assertLessEqual(c2.bbox[3], c3.bbox[1] + 1e-4)

    def test_horizontal_stacking_positions(self):
        """Container with stack_x positions children monotonically horizontally."""
        doc = MLUEDocument(
            version="2.1",
            environment=Environment(width=800, height=800, background="#000000"),
            entities=[
                Entity(
                    id="row",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.8, height=0.3),
                    velocity=Velocity(0.0, 0.0),
                    properties={},
                    layout={"direction": "horizontal", "gap": 0.05},
                ),
                Entity(
                    id="item_1",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.2, height=0.2),
                    velocity=Velocity(0.0, 0.0),
                    properties={},
                    parent_id="row",
                ),
                Entity(
                    id="item_2",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.2, height=0.2),
                    velocity=Velocity(0.0, 0.0),
                    properties={},
                    parent_id="row",
                ),
            ],
            rules=[],
        )

        result = self.engine.evaluate(doc)
        shapes_by_id = {s.id: s for s in result.shapes}

        i1 = shapes_by_id["item_1"]
        i2 = shapes_by_id["item_2"]

        self.assertLess(i1.center[0], i2.center[0])
        # Right edge of item_1 <= Left edge of item_2
        self.assertLessEqual(i1.bbox[2], i2.bbox[0] + 1e-4)

    def test_bounds_clipping(self):
        """Child with clip_bounds: true is clipped to parent container bounds."""
        doc = MLUEDocument(
            version="2.1",
            environment=Environment(width=800, height=800, background="#000000"),
            entities=[
                Entity(
                    id="parent_box",
                    type="box",
                    position=Position(x=0.5, y=0.5),
                    size=BoxSize(width=0.4, height=0.4),  # [0.3, 0.7] -> [240, 560]
                    velocity=Velocity(0.0, 0.0),
                    properties={},
                ),
                Entity(
                    id="overflow_child",
                    type="box",
                    position=Position(x=0.8, y=0.8),  # Way outside parent
                    size=BoxSize(width=0.2, height=0.2),
                    velocity=Velocity(0.0, 0.0),
                    properties={},
                    parent_id="parent_box",
                    clip_bounds=True,
                ),
            ],
            rules=[],
        )

        result = self.engine.evaluate(doc)
        shapes = {s.id: s for s in result.shapes}
        child = shapes["overflow_child"]
        parent = shapes["parent_box"]

        # Child bbox must be clamped within parent bbox
        self.assertGreaterEqual(child.bbox[0], parent.bbox[0] - 1e-4)
        self.assertGreaterEqual(child.bbox[1], parent.bbox[1] - 1e-4)
        self.assertLessEqual(child.bbox[2], parent.bbox[2] + 1e-4)
        self.assertLessEqual(child.bbox[3], parent.bbox[3] + 1e-4)


class TestDynamicTextInterpolation(unittest.TestCase):
    """Verifies state-bound text template evaluation and mutation reactivity."""

    def setUp(self):
        self.engine = MLUEEngine()

    def test_template_interpolation(self):
        """Text template resolves nested state variable values."""
        doc = MLUEDocument(
            version="2.1",
            environment=Environment(width=400, height=400, background="#000000"),
            state_variables={
                "player": {"score": 9500, "rank": "Master"},
                "config": {"lives": 3},
            },
            entities=[
                Entity(
                    id="hud",
                    type="text",
                    position=Position(x=0.1, y=0.1),
                    size=TextSize(font_scale=0.02, align="left"),
                    velocity=Velocity(0.0, 0.0),
                    properties={"color": "#FFFFFF"},
                    template="Score: {player.score} | Rank: {player.rank} | Lives: {config.lives}",
                )
            ],
            rules=[],
        )

        result = self.engine.evaluate(doc)
        self.assertEqual(len(result.shapes), 1)
        self.assertEqual(
            result.shapes[0].text,
            "Score: 9500 | Rank: Master | Lives: 3",
        )

    def test_missing_state_variable_leaves_empty(self):
        """Unresolved state variable placeholder evaluates to empty string without crashing."""
        doc = MLUEDocument(
            version="2.1",
            environment=Environment(width=400, height=400, background="#000000"),
            state_variables={"active": True},
            entities=[
                Entity(
                    id="hud",
                    type="text",
                    position=Position(x=0.1, y=0.1),
                    size=TextSize(font_scale=0.02),
                    velocity=Velocity(0.0, 0.0),
                    properties={},
                    template="Status: {unknown.key}",
                )
            ],
            rules=[],
        )

        result = self.engine.evaluate(doc)
        self.assertEqual(result.shapes[0].text, "Status: ")


class TestPairwiseAnalyticalCollisions(unittest.TestCase):
    """Verifies narrowphase collision detection and impulse resolution for Phase 2 primitives."""

    def setUp(self):
        self.engine = MLUEEngine()

    def test_circle_segment_collision(self):
        """Circle moving downward toward horizontal solid segment bounces upon impact."""
        doc = MLUEDocument(
            version="2.1",
            environment=Environment(width=500, height=500, background="#000000"),
            entities=[
                Entity(
                    id="floor",
                    type="segment",
                    position=Position(x=0.1, y=0.6),
                    size=SegmentSize(end_x=0.9, end_y=0.6, thickness=0.01),
                    velocity=Velocity(0.0, 0.0),
                    properties={"solid": True},
                ),
                Entity(
                    id="ball",
                    type="circle",
                    position=Position(x=0.5, y=0.58),  # Center 0.58, radius 0.03 -> bottom edge 0.61 penetrates floor at 0.60
                    size=CircleSize(radius=0.03),
                    velocity=Velocity(0.0, 0.2),  # Moving down
                    properties={"solid": True},
                ),
            ],
            rules=[],
        )

        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=0.016)
        entities = {e.id: e for e in next_state.entities}
        ball = entities["ball"]

        # Velocity must reflect upwards
        self.assertLess(ball.velocity.vy, 0.0)
        # Ball position must be separated above floor
        self.assertLess(ball.position.y, 0.60)

    def test_capsule_circle_collision(self):
        """Horizontal capsule and downward moving circle collide and bounce."""
        doc = MLUEDocument(
            version="2.1",
            environment=Environment(width=500, height=500, background="#000000"),
            entities=[
                Entity(
                    id="cap",
                    type="capsule",
                    position=Position(x=0.5, y=0.5),
                    size=CapsuleSize(radius=0.04, length=0.2, angle=0.0),
                    velocity=Velocity(0.0, -0.1),
                    properties={"solid": True},
                ),
                Entity(
                    id="ball",
                    type="circle",
                    position=Position(x=0.5, y=0.45),  # Overlapping capsule body
                    size=CircleSize(radius=0.03),
                    velocity=Velocity(0.0, 0.1),
                    properties={"solid": True},
                ),
            ],
            rules=[],
        )

        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=0.016)
        entities = {e.id: e for e in next_state.entities}
        ball = entities["ball"]
        cap = entities["cap"]
        # Ball should bounce upwards and capsule downwards
        self.assertLess(ball.velocity.vy, 0.0)
        self.assertGreater(cap.velocity.vy, 0.0)

    def test_capsule_capsule_collision(self):
        """Two capsules colliding head-on bounce and separate."""
        doc = MLUEDocument(
            version="2.1",
            environment=Environment(width=500, height=500, background="#000000"),
            entities=[
                Entity(
                    id="cap_1",
                    type="capsule",
                    position=Position(x=0.45, y=0.5),
                    size=CapsuleSize(radius=0.03, length=0.1, angle=0.0),
                    velocity=Velocity(0.1, 0.0),  # Moving right
                    properties={"solid": True},
                ),
                Entity(
                    id="cap_2",
                    type="capsule",
                    position=Position(x=0.52, y=0.5),
                    size=CapsuleSize(radius=0.03, length=0.1, angle=0.0),
                    velocity=Velocity(-0.1, 0.0),  # Moving left
                    properties={"solid": True},
                ),
            ],
            rules=[],
        )

        state = self.engine.init_simulation(doc)
        next_state = self.engine.step(state, dt=0.016)
        entities = {e.id: e for e in next_state.entities}
        c1 = entities["cap_1"]
        c2 = entities["cap_2"]

        # Velocities should reflect
        self.assertLess(c1.velocity.vx, 0.0)
        self.assertGreater(c2.velocity.vx, 0.0)


if __name__ == "__main__":
    unittest.main()

