"""Unit tests for MLUE Subphase 1.3.1: Continuous Spatial Indexing & Broadphase Core.

Tests AABB intersection math, SpatialHashGrid2D candidate pairing, BVH tree queries,
zero false-negative collision guarantees, and high-entity broadphase cull efficiency.
"""

import unittest
import random
from runtime.model import Entity, Position, Velocity, CircleSize, BoxSize, Environment
from runtime.spatial import (
    AABB2D,
    compute_entity_aabb,
    SpatialHashGrid2D,
    BVHTree2D,
)


class TestSpatialIndex(unittest.TestCase):
    """Test suite for 2D spatial indexing, bounding box arithmetic, and spatial hash grid broadphase."""

    def setUp(self):
        self.env = Environment(width=800, height=600, background="#000000")

    # =========================================================================
    # 1. AABB ARITHMETIC & OVERLAP TESTS
    # =========================================================================

    def test_aabb_intersection(self):
        """Verify AABB2D intersection logic across overlapping, touching, and disjoint boxes."""
        box_a = AABB2D(min_x=0.1, min_y=0.1, max_x=0.3, max_y=0.3)
        box_b = AABB2D(min_x=0.2, min_y=0.2, max_x=0.4, max_y=0.4)
        box_c = AABB2D(min_x=0.5, min_y=0.5, max_x=0.7, max_y=0.7)
        box_edge = AABB2D(min_x=0.3, min_y=0.3, max_x=0.5, max_y=0.5)

        # Overlap
        self.assertTrue(box_a.intersects(box_b))
        self.assertTrue(box_b.intersects(box_a))

        # Disjoint
        self.assertFalse(box_a.intersects(box_c))
        self.assertFalse(box_c.intersects(box_a))

        # Edge contact
        self.assertTrue(box_a.intersects(box_edge))

    def test_aabb_contains_point(self):
        """Verify AABB contains_point identifies interior, boundary, and exterior points."""
        box = AABB2D(min_x=0.2, min_y=0.2, max_x=0.6, max_y=0.6)
        self.assertTrue(box.contains_point(0.4, 0.4))
        self.assertTrue(box.contains_point(0.2, 0.2))  # Corner
        self.assertTrue(box.contains_point(0.6, 0.4))  # Edge
        self.assertFalse(box.contains_point(0.19, 0.4)) # Exterior

    def test_compute_entity_aabb(self):
        """Verify compute_entity_aabb calculates correct normalized bounds for circle and box."""
        circle_ent = Entity(
            id="c1",
            type="circle",
            position=Position(x=0.5, y=0.5),
            size=CircleSize(radius=0.1),
            velocity=Velocity(vx=0.0, vy=0.0),
        )
        box_ent = Entity(
            id="b1",
            type="box",
            position=Position(x=0.5, y=0.5),
            size=BoxSize(width=0.2, height=0.1),
            velocity=Velocity(vx=0.0, vy=0.0),
        )

        aabb_c = compute_entity_aabb(circle_ent, self.env)
        aabb_b = compute_entity_aabb(box_ent, self.env)

        # Circle half-extents in 800x600 (min_dim=600): ex = 0.1 * 600/800 = 0.075, ey = 0.1 * 600/600 = 0.1
        self.assertAlmostEqual(aabb_c.min_x, 0.5 - 0.075, places=6)
        self.assertAlmostEqual(aabb_c.max_x, 0.5 + 0.075, places=6)
        self.assertAlmostEqual(aabb_c.min_y, 0.5 - 0.1, places=6)
        self.assertAlmostEqual(aabb_c.max_y, 0.5 + 0.1, places=6)

        # Box half-extents: ex = 0.1, ey = 0.05
        self.assertAlmostEqual(aabb_b.min_x, 0.4, places=6)
        self.assertAlmostEqual(aabb_b.max_x, 0.6, places=6)
        self.assertAlmostEqual(aabb_b.min_y, 0.45, places=6)
        self.assertAlmostEqual(aabb_b.max_y, 0.55, places=6)

    # =========================================================================
    # 2. SPATIAL HASH GRID & BROADPHASE TESTS
    # =========================================================================

    def test_spatial_grid_candidate_pairs_basic(self):
        """Verify spatial grid detects close candidate pairs and ignores distant entities."""
        entities = [
            Entity("e1", "circle", Position(0.2, 0.2), CircleSize(0.04), Velocity(0, 0), active=True),
            Entity("e2", "circle", Position(0.22, 0.22), CircleSize(0.04), Velocity(0, 0), active=True),
            Entity("e3", "circle", Position(0.8, 0.8), CircleSize(0.04), Velocity(0, 0), active=True),
        ]
        grid = SpatialHashGrid2D(cell_size=0.1)
        aabbs = grid.build(entities, self.env)
        pairs = grid.get_candidate_pairs(aabbs)

        # e1 and e2 overlap and should be paired; e3 is far away
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0], (0, 1))

    def test_zero_false_negatives_fuzz(self):
        """Fuzz test: Prove with 0.0% false-negatives that spatial grid catches ALL overlapping AABB pairs."""
        rng = random.Random(42)
        entities: List[Entity] = []

        # Spawn 80 randomly placed entities
        for i in range(80):
            px = rng.uniform(0.1, 0.9)
            py = rng.uniform(0.1, 0.9)
            r = rng.uniform(0.01, 0.04)
            entities.append(
                Entity(f"ent_{i}", "circle", Position(px, py), CircleSize(r), Velocity(0, 0), active=True)
            )

        grid = SpatialHashGrid2D(cell_size=0.08)
        aabbs = grid.build(entities, self.env)

        # Compute ground truth via brute-force O(N^2) search
        ground_truth_pairs = set()
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                if aabbs[i].intersects(aabbs[j]):
                    ground_truth_pairs.add((i, j))

        grid_candidate_pairs = set(grid.get_candidate_pairs(aabbs))

        # Check for false negatives
        for true_pair in ground_truth_pairs:
            self.assertIn(
                true_pair,
                grid_candidate_pairs,
                f"False negative detected! Overlapping pair {true_pair} was missed by spatial grid."
            )

    def test_broadphase_cull_efficiency(self):
        """Verify spatial grid prunes over 95% of non-colliding pairs in a 200-entity scene."""
        rng = random.Random(123)
        entities: List[Entity] = []
        n = 200

        for i in range(n):
            px = rng.uniform(0.05, 0.95)
            py = rng.uniform(0.05, 0.95)
            entities.append(
                Entity(f"e_{i}", "circle", Position(px, py), CircleSize(0.015), Velocity(0, 0), active=True)
            )

        grid = SpatialHashGrid2D()
        aabbs = grid.build(entities, self.env)
        candidates = grid.get_candidate_pairs(aabbs)

        total_pairwise_possible = (n * (n - 1)) // 2  # 19,900
        cull_efficiency = (1.0 - (len(candidates) / total_pairwise_possible)) * 100.0

        # In a dispersed 200-entity arena, cull efficiency should be > 95%
        self.assertGreater(cull_efficiency, 95.0)
        self.assertLess(len(candidates), 1000)

    # =========================================================================
    # 3. BVH TREE HIERARCHICAL QUERIES
    # =========================================================================

    def test_bvh_tree_query_parity(self):
        """Verify BVHTree2D spatial query matches brute-force bounding box overlap search."""
        rng = random.Random(999)
        entities: List[Entity] = []

        for i in range(50):
            px = rng.uniform(0.1, 0.9)
            py = rng.uniform(0.1, 0.9)
            entities.append(
                Entity(f"bvh_e_{i}", "box", Position(px, py), BoxSize(0.04, 0.04), Velocity(0, 0), active=True)
            )

        bvh = BVHTree2D()
        bvh.build(entities, self.env)

        query_box = AABB2D(min_x=0.3, min_y=0.3, max_x=0.6, max_y=0.6)
        bvh_results = set(bvh.query_aabb(query_box))

        # Ground truth search
        ground_truth: set = set()
        for i, e in enumerate(entities):
            aabb = compute_entity_aabb(e, self.env)
            if query_box.intersects(aabb):
                ground_truth.add(i)

        self.assertEqual(bvh_results, ground_truth)


if __name__ == "__main__":
    unittest.main()
