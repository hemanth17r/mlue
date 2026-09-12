"""Unit tests for MLUE Phase 5: Presentation Adapter & Visual Output Fidelity.

Verifies:
- ComputedShape rotation angle theta export across flat and hierarchical entities
- EvaluationResult constraints export with concrete screen-space endpoints (p1, p2)
- TkinterAdapter headless verification for static snapshot and interactive stepping
- Cyclomatic complexity compliance (NIST CC <= 30)
"""

import ast
import inspect
import math
import unittest
from runtime.model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    BoxSize,
    CapsuleSize,
    Constraint,
)
from runtime.engine import MLUEEngine
from runtime.adapter import TkinterAdapter


class TestPresentationAdapter(unittest.TestCase):

    def setUp(self):
        self.engine = MLUEEngine()
        self.env = Environment(width=800, height=600)

    def test_computed_shape_theta_export(self):
        """Verifies that evaluate() correctly exports rotation angle theta on ComputedShape."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="unrotated_box",
                    type="box",
                    position=Position(0.2, 0.2),
                    size=BoxSize(0.1, 0.05),
                    angle=0.0,
                ),
                Entity(
                    id="rotated_box",
                    type="box",
                    position=Position(0.5, 0.5),
                    size=BoxSize(0.2, 0.04),
                    angle=0.785398,  # pi/4
                ),
                Entity(
                    id="rotated_capsule",
                    type="capsule",
                    position=Position(0.8, 0.8),
                    size=CapsuleSize(radius=0.02, length=0.1, angle=0.5),
                    angle=0.5,
                ),
            ],
        )

        res = self.engine.evaluate(doc)
        shape_by_id = {s.id: s for s in res.shapes}

        self.assertAlmostEqual(shape_by_id["unrotated_box"].theta, 0.0, places=5)
        self.assertAlmostEqual(shape_by_id["rotated_box"].theta, 0.785398, places=5)
        self.assertAlmostEqual(shape_by_id["rotated_capsule"].theta, 1.0, places=5)

    def test_evaluation_result_constraints_export(self):
        """Verifies that evaluate() exports ComputedConstraint with accurate screen coordinates."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,  # 800 x 600
            entities=[
                Entity(
                    id="post_a",
                    type="box",
                    position=Position(0.25, 0.5),
                    size=BoxSize(0.05, 0.2),
                ),
                Entity(
                    id="post_b",
                    type="box",
                    position=Position(0.75, 0.5),
                    size=BoxSize(0.05, 0.2),
                ),
            ],
            constraints=[
                Constraint(
                    id="link_rod",
                    type="distance",
                    entity_a="post_a",
                    entity_b="post_b",
                    anchor_a=Position(0.025, 0.0),
                    anchor_b=Position(-0.025, 0.0),
                ),
                Constraint(
                    id="world_spring",
                    type="spring",
                    entity_a="post_a",
                    entity_b=None,
                    anchor_a=Position(0.0, -0.1),
                    anchor_b=Position(0.25, 0.1),
                ),
            ],
        )

        res = self.engine.evaluate(doc)
        self.assertEqual(len(res.constraints), 2)
        c_by_id = {c.id: c for c in res.constraints}

        # link_rod:
        # p1: (0.25 + 0.025) * 800 = 0.275 * 800 = 220.0, 0.5 * 600 = 300.0
        # p2: (0.75 - 0.025) * 800 = 0.725 * 800 = 580.0, 0.5 * 600 = 300.0
        self.assertEqual(c_by_id["link_rod"].type, "distance")
        self.assertAlmostEqual(c_by_id["link_rod"].p1[0], 220.0, places=2)
        self.assertAlmostEqual(c_by_id["link_rod"].p1[1], 300.0, places=2)
        self.assertAlmostEqual(c_by_id["link_rod"].p2[0], 580.0, places=2)
        self.assertAlmostEqual(c_by_id["link_rod"].p2[1], 300.0, places=2)

        # world_spring:
        # p1: 0.25 * 800 = 200.0, (0.5 - 0.1) * 600 = 0.4 * 600 = 240.0
        # p2: 0.25 * 800 = 200.0, 0.1 * 600 = 60.0
        self.assertEqual(c_by_id["world_spring"].type, "spring")
        self.assertAlmostEqual(c_by_id["world_spring"].p1[0], 200.0, places=2)
        self.assertAlmostEqual(c_by_id["world_spring"].p1[1], 240.0, places=2)
        self.assertAlmostEqual(c_by_id["world_spring"].p2[0], 200.0, places=2)
        self.assertAlmostEqual(c_by_id["world_spring"].p2[1], 60.0, places=2)

    def test_tkinter_adapter_static_render(self):
        """Verifies that TkinterAdapter.present() runs with block=False without error."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="spinner",
                    type="box",
                    position=Position(0.5, 0.5),
                    size=BoxSize(0.2, 0.04),
                    angle=0.5,
                )
            ],
            constraints=[
                Constraint(
                    id="spring_1",
                    type="spring",
                    entity_a="spinner",
                    entity_b=None,
                    anchor_a=Position(0.0, 0.0),
                    anchor_b=Position(0.5, 0.1),
                )
            ],
        )
        res = self.engine.evaluate(doc)
        adapter = TkinterAdapter()
        # present with block=False initializes GUI, draws shapes/constraints, and updates
        adapter.present(res, block=False)

    def test_tkinter_adapter_simulation_step(self):
        """Verifies that TkinterAdapter.run_simulation() steps cleanly with duration limit."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="spinner",
                    type="box",
                    position=Position(0.5, 0.5),
                    size=BoxSize(0.2, 0.04),
                    angle=0.5,
                )
            ],
        )
        adapter = TkinterAdapter()
        # run_simulation for 0.05 seconds ensures loop executes and shuts down cleanly
        adapter.run_simulation(self.engine, doc, fps=60, duration=0.05, block=True)

    def test_cyclomatic_complexity_bounds(self):
        """Verifies that TkinterAdapter methods adhere to NIST CC <= 30."""
        def calc_cc(fn):
            import textwrap
            source = textwrap.dedent(inspect.getsource(fn))
            tree = ast.parse(source)
            cc = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With)):
                    cc += 1
                elif isinstance(node, ast.BoolOp):
                    cc += len(node.values) - 1
            return cc

        adapter = TkinterAdapter()
        self.assertLessEqual(calc_cc(adapter._draw_shape), 30)
        self.assertLessEqual(calc_cc(adapter.present), 30)


if __name__ == "__main__":
    unittest.main()
