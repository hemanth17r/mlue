"""Unit tests for MLUE Subphase 1.5: Native C-ABI Core & ctypes Interface.

Tests C struct exact memory sizes (64-byte entity record), field byte offsets,
ctypes function bindings, and continuous collision integration.
"""

import unittest
import ctypes
from runtime.model import Entity, Position, Velocity, CircleSize, BoxSize, Environment
from runtime.native_core import (
    EntityRecordC,
    EnvironmentC,
    StepResultC,
    NativeCore,
)


class TestNativeCore(unittest.TestCase):
    """Test suite for native C memory alignment and FFI execution."""

    def setUp(self):
        self.env = Environment(width=800, height=600, background="#000000")

    # =========================================================================
    # 1. MEMORY ALIGNMENT & STRUCT SIZES
    # =========================================================================

    def test_c_struct_exact_sizes(self):
        """Verify C structs match exact memory layouts defined in spec/1.5.md."""
        self.assertEqual(ctypes.sizeof(EntityRecordC), 64, "MLUE_EntityRecord must be exactly 64 bytes")
        self.assertEqual(ctypes.sizeof(EnvironmentC), 16, "MLUE_Environment must be exactly 16 bytes")
        self.assertEqual(ctypes.sizeof(StepResultC), 16, "MLUE_StepResult must be exactly 16 bytes")

    def test_c_struct_field_offsets(self):
        """Verify field byte offsets in EntityRecordC align with the binary .mlueb specification."""
        self.assertEqual(EntityRecordC.id_idx.offset, 0)
        self.assertEqual(EntityRecordC.color_rgba.offset, 4)
        self.assertEqual(EntityRecordC.entity_type.offset, 8)
        self.assertEqual(EntityRecordC.flags.offset, 9)
        self.assertEqual(EntityRecordC.ctrl_axis.offset, 10)
        self.assertEqual(EntityRecordC.reserved_1.offset, 11)
        self.assertEqual(EntityRecordC.ctrl_channel_idx.offset, 12)
        self.assertEqual(EntityRecordC.pos_x.offset, 16)
        self.assertEqual(EntityRecordC.pos_y.offset, 24)
        self.assertEqual(EntityRecordC.vel_vx.offset, 32)
        self.assertEqual(EntityRecordC.vel_vy.offset, 40)
        self.assertEqual(EntityRecordC.size_p1.offset, 48)
        self.assertEqual(EntityRecordC.size_p2.offset, 56)

    # =========================================================================
    # 2. INITIALIZATION & VERSIONING
    # =========================================================================

    def test_native_core_version(self):
        """Verify NativeCore reports version 1.5.0."""
        version = NativeCore.get_version()
        self.assertEqual(version, (1, 5, 0))

    # =========================================================================
    # 3. CONTINUOUS SIMULATION STEPPING
    # =========================================================================

    def test_native_step_boundary_reflection(self):
        """Verify NativeCore steps entity forward and reflects off arena boundary."""
        ent = Entity(
            id="ball",
            type="circle",
            position=Position(x=0.05, y=0.5),
            size=CircleSize(radius=0.04),
            velocity=Velocity(vx=-0.2, vy=0.0),
            properties={"solid": True},
            active=True,
        )

        # Step 15 frames (should hit left wall and reverse vx to positive)
        current_entities = [ent]
        for _ in range(15):
            current_entities, _ = NativeCore.step(current_entities, self.env, dt=1.0 / 60.0)

        updated_ball = current_entities[0]
        self.assertGreaterEqual(updated_ball.position.x, 0.03)
        self.assertGreaterEqual(updated_ball.velocity.vx, 0.0)

    def test_native_step_circle_collision(self):
        """Verify two solid circles colliding exchange velocities via NativeCore."""
        e1 = Entity("c1", "circle", Position(0.40, 0.50), CircleSize(0.05), Velocity(0.20, 0.0), properties={"solid": True}, active=True)
        e2 = Entity("c2", "circle", Position(0.60, 0.50), CircleSize(0.05), Velocity(-0.20, 0.0), properties={"solid": True}, active=True)

        entities = [e1, e2]
        # Step until collision occurs
        for _ in range(30):
            entities, _ = NativeCore.step(entities, self.env, dt=1.0 / 60.0)

        # After collision, velocities should be reversed
        self.assertLess(entities[0].velocity.vx, 0.0)
        self.assertGreater(entities[1].velocity.vx, 0.0)


if __name__ == "__main__":
    unittest.main()
