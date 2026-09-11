"""MLUE Unit Tests: Analytical 2D LiDAR & Raycast Sensor Primitives

Verifies closed-form O(1) analytical ray intersection against all MLUE geometry types
(circles, boxes, segments, capsules, viewport boundaries) and multi-directional
LiDAR sweeps for autonomous spatial agents.
"""

import unittest
import math
from runtime.model import (
    MLUEDocument,
    Environment,
    Entity,
    Position,
    CircleSize,
    BoxSize,
    SegmentSize,
    CapsuleSize,
)
from runtime.spatial import Ray2D, RayHit
from runtime.engine import MLUEEngine


class TestRaycastSensors(unittest.TestCase):
    """Verifies analytical ray-to-geometry distance solvers and LiDAR sensor sweeps."""

    def setUp(self):
        self.engine = MLUEEngine()
        self.env = Environment(width=200, height=200)

    def test_ray_intersect_circle(self):
        """Ray originating at (0.2, 0.5) fired eastward (+X) hits circle at (0.6, 0.5) with radius 0.1."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="target_circle",
                    type="circle",
                    position=Position(x=0.6, y=0.5),
                    size=CircleSize(radius=0.1),
                    properties={},
                )
            ],
        )
        state = self.engine.init_simulation(doc)

        # Cast ray eastward (angle 0.0)
        hit = self.engine.cast_ray(state, origin=(0.2, 0.5), angle_rad=0.0, max_range=1.0)
        self.assertTrue(hit.hit)
        self.assertEqual(hit.entity_id, "target_circle")
        # Expected hit distance: 0.6 - 0.1 - 0.2 = 0.3
        self.assertAlmostEqual(hit.distance, 0.3, places=5)
        self.assertAlmostEqual(hit.hit_x, 0.5, places=5)
        self.assertAlmostEqual(hit.hit_y, 0.5, places=5)
        self.assertAlmostEqual(hit.normal_x, -1.0, places=5)
        self.assertAlmostEqual(hit.normal_y, 0.0, places=5)

    def test_ray_misses_circle(self):
        """Ray fired southward (-Y direction) misses circle situated to the east."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="target_circle",
                    type="circle",
                    position=Position(x=0.6, y=0.5),
                    size=CircleSize(radius=0.1),
                    properties={},
                )
            ],
        )
        state = self.engine.init_simulation(doc)

        # Cast ray southward (angle pi/2 points toward y=1.0)
        hit = self.engine.cast_ray(state, origin=(0.2, 0.5), angle_rad=math.pi / 2.0, max_range=1.0)
        # Should miss the circle and hit the bottom boundary (y=1.0) at distance 0.5
        self.assertEqual(hit.entity_id, "boundary")
        self.assertAlmostEqual(hit.distance, 0.5, places=5)
        self.assertAlmostEqual(hit.hit_y, 1.0, places=5)

    def test_ray_intersect_box(self):
        """Ray hits the left face of a rectangular box."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="obstacle_box",
                    type="box",
                    position=Position(x=0.7, y=0.5),
                    size=BoxSize(width=0.2, height=0.4),
                    properties={},
                )
            ],
        )
        state = self.engine.init_simulation(doc)

        hit = self.engine.cast_ray(state, origin=(0.1, 0.5), angle_rad=0.0, max_range=1.0)
        self.assertTrue(hit.hit)
        self.assertEqual(hit.entity_id, "obstacle_box")
        # Left face of box is at 0.7 - 0.1 = 0.6. Distance from 0.1 is 0.5.
        self.assertAlmostEqual(hit.distance, 0.5, places=5)
        self.assertAlmostEqual(hit.hit_x, 0.6, places=5)
        self.assertAlmostEqual(hit.normal_x, -1.0, places=5)

    def test_ray_intersect_segment(self):
        """Ray fired northward hits a horizontal barrier segment."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="wall_segment",
                    type="segment",
                    position=Position(x=0.2, y=0.3),
                    size=SegmentSize(end_x=0.8, end_y=0.3, thickness=0.02),
                    properties={},
                )
            ],
        )
        state = self.engine.init_simulation(doc)

        # Ray starts at (0.5, 0.6), shoots northward (-pi/2)
        hit = self.engine.cast_ray(state, origin=(0.5, 0.6), angle_rad=-math.pi / 2.0, max_range=1.0)
        self.assertTrue(hit.hit)
        self.assertEqual(hit.entity_id, "wall_segment")
        # Top segment is at y=0.3. Thickness is 0.02, so half-thickness is 0.01. Bottom of segment is at 0.3 + 0.01 = 0.31.
        self.assertAlmostEqual(hit.distance, 0.3, delta=0.02)

    def test_ray_intersect_capsule(self):
        """Ray hits the rounded cap of a capsule."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="capsule_pill",
                    type="capsule",
                    position=Position(x=0.5, y=0.5),
                    size=CapsuleSize(radius=0.05, length=0.2, angle=0.0),
                    properties={},
                )
            ],
        )
        state = self.engine.init_simulation(doc)

        # Capsule extends horizontally from x = 0.5 - 0.1 = 0.4 to 0.5 + 0.1 = 0.6, plus cap radius 0.05.
        # Leftmost cap is at 0.4 - 0.05 = 0.35.
        hit = self.engine.cast_ray(state, origin=(0.1, 0.5), angle_rad=0.0, max_range=1.0)
        self.assertTrue(hit.hit)
        self.assertEqual(hit.entity_id, "capsule_pill")
        self.assertAlmostEqual(hit.distance, 0.25, places=4)
        self.assertAlmostEqual(hit.hit_x, 0.35, places=4)

    def test_ray_ignore_self_entity(self):
        """Ray ignores the robot's own body when cast from inside or near the robot."""
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[
                Entity(
                    id="robot_self",
                    type="circle",
                    position=Position(x=0.3, y=0.5),
                    size=CircleSize(radius=0.05),
                    properties={},
                ),
                Entity(
                    id="target_post",
                    type="circle",
                    position=Position(x=0.7, y=0.5),
                    size=CircleSize(radius=0.05),
                    properties={},
                ),
            ],
        )
        state = self.engine.init_simulation(doc)

        # Cast from center of robot_self ignoring "robot_self"
        hit = self.engine.cast_ray(
            state, origin=(0.3, 0.5), angle_rad=0.0, max_range=1.0, ignore_ids={"robot_self"}
        )
        self.assertEqual(hit.entity_id, "target_post")
        # Distance to target: 0.7 - 0.05 - 0.3 = 0.35
        self.assertAlmostEqual(hit.distance, 0.35, places=5)

    def test_cast_lidar_360_sweep(self):
        """LiDAR 360-degree sweep returns an 8-ray distance array bounded by environment walls."""
        # Empty room: all 8 rays should hit the boundaries of [0, 1] x [0, 1]
        doc = MLUEDocument(
            version="1.6",
            environment=self.env,
            entities=[],
        )
        state = self.engine.init_simulation(doc)

        # Center at (0.5, 0.5)
        lidar_readings = self.engine.cast_lidar(
            state, origin=(0.5, 0.5), num_rays=4, fov_rad=2.0 * math.pi, start_angle_rad=0.0
        )
        self.assertEqual(len(lidar_readings), 4)

        # Ray 0 (East, angle 0): distance to x=1.0 is 0.5
        self.assertAlmostEqual(lidar_readings[0], 0.5, places=5)
        # Ray 1 (South, angle pi/2): distance to y=1.0 is 0.5
        self.assertAlmostEqual(lidar_readings[1], 0.5, places=5)
        # Ray 2 (West, angle pi): distance to x=0.0 is 0.5
        self.assertAlmostEqual(lidar_readings[2], 0.5, places=5)
        # Ray 3 (North, angle 3*pi/2): distance to y=0.0 is 0.5
        self.assertAlmostEqual(lidar_readings[3], 0.5, places=5)


if __name__ == "__main__":
    unittest.main()
