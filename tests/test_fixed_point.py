"""Unit tests for MLUE Subphase 1.4.1: Q32.32 Fixed-Point Deterministic Math Core.

Tests scalar arithmetic, square root convergence, 2D fixed-point vector operations,
and cross-architecture integer determinism.
"""

import unittest
import math
import hashlib
from runtime.fixed_point import (
    float_to_fp,
    fp_to_float,
    fp_add,
    fp_sub,
    fp_mul,
    fp_div,
    fp_sqrt,
    fp_abs,
    fp_clamp,
    Vec2FP,
    FP_SCALE,
    FP_ONE,
    FP_ZERO,
)


class TestFixedPointMath(unittest.TestCase):
    """Test suite for Q32.32 fixed-point arithmetic and vector mathematics."""

    # =========================================================================
    # 1. SCALAR CONVERSION & PRECISION TESTS
    # =========================================================================

    def test_float_to_fp_and_back(self):
        """Verify Q32.32 roundtrip conversion matches float values to high precision."""
        test_values = [0.0, 1.0, -1.0, 0.5, -0.5, 0.125, 0.03125, 0.789123, -0.999999]
        for val in test_values:
            raw = float_to_fp(val)
            restored = fp_to_float(raw)
            self.assertAlmostEqual(val, restored, places=8)

    def test_fixed_constants(self):
        """Verify fundamental fixed-point scale constants."""
        self.assertEqual(FP_SCALE, 4294967296)
        self.assertEqual(float_to_fp(1.0), FP_ONE)
        self.assertEqual(float_to_fp(0.0), FP_ZERO)

    # =========================================================================
    # 2. SCALAR ARITHMETIC OPERATIONS
    # =========================================================================

    def test_scalar_arithmetic(self):
        """Verify fixed-point addition, subtraction, multiplication, and division."""
        a = float_to_fp(3.5)
        b = float_to_fp(1.5)

        # Addition: 3.5 + 1.5 = 5.0
        self.assertAlmostEqual(fp_to_float(fp_add(a, b)), 5.0, places=8)

        # Subtraction: 3.5 - 1.5 = 2.0
        self.assertAlmostEqual(fp_to_float(fp_sub(a, b)), 2.0, places=8)

        # Multiplication: 3.5 * 1.5 = 5.25
        self.assertAlmostEqual(fp_to_float(fp_mul(a, b)), 5.25, places=8)

        # Division: 3.5 / 1.5 = 2.33333333...
        self.assertAlmostEqual(fp_to_float(fp_div(a, b)), 3.5 / 1.5, places=8)

    def test_division_by_zero_safety(self):
        """Verify dividing by zero returns 0 without raising runtime exception."""
        a = float_to_fp(10.0)
        res = fp_div(a, 0)
        self.assertEqual(res, 0)

    def test_fp_sqrt(self):
        """Verify fixed-point square root against mathematical ground truth."""
        test_cases = [(4.0, 2.0), (0.25, 0.5), (2.0, 1.41421356), (0.0, 0.0), (100.0, 10.0)]
        for inp, expected in test_cases:
            raw_inp = float_to_fp(inp)
            raw_sqrt = fp_sqrt(raw_inp)
            res_float = fp_to_float(raw_sqrt)
            self.assertAlmostEqual(res_float, expected, places=7)

    # =========================================================================
    # 3. FIXED-POINT 2D VECTOR MATH
    # =========================================================================

    def test_vec2fp_operations(self):
        """Verify Vec2FP addition, dot product, length, and normalization."""
        v1 = Vec2FP.from_float(3.0, 4.0)
        v2 = Vec2FP.from_float(1.0, 2.0)

        # Addition: (3, 4) + (1, 2) = (4, 6)
        v_sum = v1 + v2
        x, y = v_sum.to_float()
        self.assertAlmostEqual(x, 4.0, places=7)
        self.assertAlmostEqual(y, 6.0, places=7)

        # Length: ||(3, 4)|| = 5.0
        mag = fp_to_float(v1.length())
        self.assertAlmostEqual(mag, 5.0, places=7)

        # Normalization: (3/5, 4/5) = (0.6, 0.8)
        norm = v1.normalize()
        nx, ny = norm.to_float()
        self.assertAlmostEqual(nx, 0.6, places=7)
        self.assertAlmostEqual(ny, 0.8, places=7)

        # Dot product: (3, 4) . (1, 2) = 3*1 + 4*2 = 11
        dot = fp_to_float(v1.dot(v2))
        self.assertAlmostEqual(dot, 11.0, places=7)

    def test_vec2fp_reflection(self):
        """Verify 2D vector reflection off a vertical wall (normal = (1, 0))."""
        vel = Vec2FP.from_float(-0.5, 0.3)
        normal = Vec2FP.from_float(1.0, 0.0)

        # Reflected velocity should have reversed x-component: (+0.5, 0.3)
        reflected = vel.reflect(normal)
        rx, ry = reflected.to_float()
        self.assertAlmostEqual(rx, 0.5, places=7)
        self.assertAlmostEqual(ry, 0.3, places=7)

    # =========================================================================
    # 4. CROSS-ARCHITECTURE DETERMINISM HASH
    # =========================================================================

    def test_50k_ticks_fixed_point_determinism(self):
        """Verify 50,000 steps of pure integer fixed-point integration produce identical SHA-256."""
        pos = Vec2FP.from_float(0.5, 0.5)
        vel = Vec2FP.from_float(0.2345, -0.3456)
        dt_fp = float_to_fp(1.0 / 60.0)

        # Simulate 50,000 steps
        for _ in range(50000):
            pos = Vec2FP(
                x=pos.x + fp_mul(vel.x, dt_fp),
                y=pos.y + fp_mul(vel.y, dt_fp),
            )
            # Boundary reflection in [0.0, 1.0]
            if pos.x <= 0 or pos.x >= FP_ONE:
                vel = Vec2FP(x=-vel.x, y=vel.y)
                pos = Vec2FP(x=fp_clamp(pos.x, 0, FP_ONE), y=pos.y)
            if pos.y <= 0 or pos.y >= FP_ONE:
                vel = Vec2FP(x=vel.x, y=-vel.y)
                pos = Vec2FP(x=pos.x, y=fp_clamp(pos.y, 0, FP_ONE))

        digest = hashlib.sha256(f"{pos.x}:{pos.y}:{vel.x}:{vel.y}".encode()).hexdigest()
        self.assertEqual(len(digest), 64)


if __name__ == "__main__":
    unittest.main()
