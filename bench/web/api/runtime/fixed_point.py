"""MLUE Q32.32 Fixed-Point Deterministic Math Core.

Provides 64-bit signed Q32.32 fixed-point integer arithmetic and 2D vector operations.
Guarantees bit-exact cross-architecture determinism across x86_64, ARM64, WASM, and RISC-V.
Adheres strictly to Tier L1 Substrate Decoupling (Standard Library only: math, dataclasses, typing).
"""

import math
from dataclasses import dataclass
from typing import Tuple, Union, List, Set, FrozenSet, Optional
from runtime.model import Entity, Position, Velocity, CircleSize, BoxSize, Environment


# Q32.32 Fixed-Point Constants
FP_SHIFT = 32
FP_SCALE = 1 << FP_SHIFT  # 4,294,967,296
FP_HALF = 1 << (FP_SHIFT - 1)  # 2,147,483,648
FP_ONE = FP_SCALE
FP_ZERO = 0


def float_to_fp(val: float) -> int:
    """Converts a continuous floating-point number into a Q32.32 raw integer."""
    if math.isnan(val) or math.isinf(val):
        return 0
    return int(round(val * FP_SCALE))


def fp_to_float(raw: int) -> float:
    """Converts a Q32.32 raw integer back to a floating-point number."""
    return float(raw) / FP_SCALE


def fp_add(a: int, b: int) -> int:
    """Fixed-point addition: (a + b)."""
    return a + b


def fp_sub(a: int, b: int) -> int:
    """Fixed-point subtraction: (a - b)."""
    return a - b


def fp_mul(a: int, b: int) -> int:
    """Fixed-point multiplication: (a * b) >> 32."""
    return (a * b) >> FP_SHIFT


def fp_div(a: int, b: int) -> int:
    """Fixed-point division: (a << 32) // b."""
    if b == 0:
        return 0
    return (a << FP_SHIFT) // b


def fp_sqrt(a: int) -> int:
    """Fixed-point square root using integer square root: isqrt(a << 32)."""
    if a <= 0:
        return 0
    return math.isqrt(a << FP_SHIFT)


def fp_abs(a: int) -> int:
    """Fixed-point absolute value."""
    return abs(a)


def fp_min(a: int, b: int) -> int:
    return min(a, b)


def fp_max(a: int, b: int) -> int:
    return max(a, b)


def fp_clamp(val: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(max_val, val))


@dataclass(slots=True)
class Vec2FP:
    """2D Vector with Q32.32 fixed-point integer coordinates."""
    x: int
    y: int

    @classmethod
    def from_float(cls, x: float, y: float) -> "Vec2FP":
        """Constructs a Vec2FP from continuous floating-point coordinates."""
        return cls(x=float_to_fp(x), y=float_to_fp(y))

    def to_float(self) -> Tuple[float, float]:
        """Converts Vec2FP back to a continuous float pair (x, y)."""
        return (fp_to_float(self.x), fp_to_float(self.y))

    def __add__(self, other: "Vec2FP") -> "Vec2FP":
        return Vec2FP(x=self.x + other.x, y=self.y + other.y)

    def __sub__(self, other: "Vec2FP") -> "Vec2FP":
        return Vec2FP(x=self.x - other.x, y=self.y - other.y)

    def __mul__(self, scalar_fp: int) -> "Vec2FP":
        return Vec2FP(x=fp_mul(self.x, scalar_fp), y=fp_mul(self.y, scalar_fp))

    def __neg__(self) -> "Vec2FP":
        return Vec2FP(x=-self.x, y=-self.y)

    def dot(self, other: "Vec2FP") -> int:
        """Returns the Q32.32 dot product: (x1*x2 + y1*y2) >> 32."""
        return ((self.x * other.x) + (self.y * other.y)) >> FP_SHIFT

    def length_sq(self) -> int:
        """Returns the squared length as a Q32.32 integer."""
        return ((self.x * self.x) + (self.y * self.y)) >> FP_SHIFT

    def length(self) -> int:
        """Returns the magnitude of the vector as a Q32.32 integer."""
        sq = (self.x * self.x) + (self.y * self.y)
        if sq <= 0:
            return 0
        return math.isqrt(sq)

    def normalize(self) -> "Vec2FP":
        """Returns the unit vector in the same direction."""
        mag = self.length()
        if mag == 0:
            return Vec2FP(0, 0)
        return Vec2FP(
            x=(self.x << FP_SHIFT) // mag,
            y=(self.y << FP_SHIFT) // mag,
        )

    def reflect(self, normal: "Vec2FP") -> "Vec2FP":
        """Reflects this vector off a unit normal vector: v' = v - 2(v . n)n."""
        dot_prod = self.dot(normal)
        two_dot = dot_prod << 1
        return Vec2FP(
            x=self.x - fp_mul(two_dot, normal.x),
            y=self.y - fp_mul(two_dot, normal.y),
        )


class FixedPointEngine:
    """Deterministic simulation engine operating exclusively with Q32.32 fixed-point integer mathematics."""

    def __init__(self, dt: float = 1.0 / 60.0):
        self.dt_fp = float_to_fp(dt)

    def step(
        self, entities: List[Entity], env: Environment
    ) -> Tuple[List[Entity], Set[FrozenSet[str]]]:
        """Integrates positions and resolves boundary and pairwise collisions using Q32.32 integer arithmetic."""
        w = env.width
        h = env.height
        min_dim = min(w, h)

        updated_entities: List[Entity] = []

        # 1. Continuous Position Integration & Boundary Reflections
        for e in entities:
            if not e.active:
                updated_entities.append(e)
                continue

            pos = Vec2FP.from_float(e.position.x, e.position.y)
            vel = Vec2FP.from_float(e.velocity.vx, e.velocity.vy)

            # Integrate: pos += vel * dt
            new_pos = Vec2FP(
                x=pos.x + fp_mul(vel.x, self.dt_fp),
                y=pos.y + fp_mul(vel.y, self.dt_fp),
            )
            new_vel = vel

            # Half-extents
            if e.type == "circle" and isinstance(e.size, CircleSize):
                r_fp = float_to_fp(e.size.radius)
                ex_fp = (r_fp * min_dim) // w
                ey_fp = (r_fp * min_dim) // h
            elif e.type == "box" and isinstance(e.size, BoxSize):
                ex_fp = float_to_fp(e.size.width / 2.0)
                ey_fp = float_to_fp(e.size.height / 2.0)
            else:
                ex_fp, ey_fp = 0, 0

            # Arena Boundaries [0, FP_ONE]
            if new_pos.x - ex_fp <= 0:
                new_pos = Vec2FP(ex_fp, new_pos.y)
                if new_vel.x < 0:
                    new_vel = Vec2FP(-new_vel.x, new_vel.y)
            elif new_pos.x + ex_fp >= FP_ONE:
                new_pos = Vec2FP(FP_ONE - ex_fp, new_pos.y)
                if new_vel.x > 0:
                    new_vel = Vec2FP(-new_vel.x, new_vel.y)

            if new_pos.y - ey_fp <= 0:
                new_pos = Vec2FP(new_pos.x, ey_fp)
                if new_vel.y < 0:
                    new_vel = Vec2FP(new_vel.x, -new_vel.y)
            elif new_pos.y + ey_fp >= FP_ONE:
                new_pos = Vec2FP(new_pos.x, FP_ONE - ey_fp)
                if new_vel.y > 0:
                    new_vel = Vec2FP(new_vel.x, -new_vel.y)

                # Clamp inside [0, FP_ONE]
            clamped_x = fp_clamp(new_pos.x, ex_fp, FP_ONE - ex_fp)
            clamped_y = fp_clamp(new_pos.y, ey_fp, FP_ONE - ey_fp)

            px, py = fp_to_float(clamped_x), fp_to_float(clamped_y)
            vx, vy = fp_to_float(new_vel.x), fp_to_float(new_vel.y)

            updated_entities.append(
                Entity(
                    id=e.id,
                    type=e.type,
                    position=Position(x=px, y=py),
                    size=e.size,
                    velocity=Velocity(vx=vx, vy=vy),
                    properties=dict(e.properties),
                    active=e.active,
                )
            )

        # 2. Pairwise Circle-Circle Impulses
        collision_events: Set[FrozenSet[str]] = set()
        n = len(updated_entities)
        for i in range(n):
            for j in range(i + 1, n):
                e1 = updated_entities[i]
                e2 = updated_entities[j]
                if not (e1.active and e2.active and e1.properties.get("solid", False) and e2.properties.get("solid", False)):
                    continue

                if e1.type == "circle" and e2.type == "circle" and isinstance(e1.size, CircleSize) and isinstance(e2.size, CircleSize):
                    p1 = Vec2FP.from_float(e1.position.x, e1.position.y)
                    p2 = Vec2FP.from_float(e2.position.x, e2.position.y)
                    r1 = float_to_fp(e1.size.radius)
                    r2 = float_to_fp(e2.size.radius)

                    diff = p1 - p2
                    dist_sq = diff.length_sq()
                    min_dist = r1 + r2
                    min_dist_sq = fp_mul(min_dist, min_dist)

                    if dist_sq < min_dist_sq and dist_sq > 0:
                        dist = diff.length()
                        normal = diff.normalize()
                        v1 = Vec2FP.from_float(e1.velocity.vx, e1.velocity.vy)
                        v2 = Vec2FP.from_float(e2.velocity.vx, e2.velocity.vy)
                        v_rel = v1 - v2
                        vel_along_norm = v_rel.dot(normal)

                        if vel_along_norm < 0:
                            # Elastic impulse J = -vel_along_norm
                            impulse = -vel_along_norm
                            v1_new = v1 + (normal * impulse)
                            v2_new = v2 - (normal * impulse)

                            # Positional separation
                            pen = min_dist - dist
                            half_pen = pen >> 1
                            p1_new = p1 + (normal * half_pen)
                            p2_new = p2 - (normal * half_pen)

                            p1_f = p1_new.to_float()
                            p2_f = p2_new.to_float()
                            v1_f = v1_new.to_float()
                            v2_f = v2_new.to_float()

                            updated_entities[i] = Entity(
                                id=e1.id, type=e1.type,
                                position=Position(x=p1_f[0], y=p1_f[1]),
                                size=e1.size,
                                velocity=Velocity(vx=v1_f[0], vy=v1_f[1]),
                                properties=e1.properties, active=e1.active,
                            )
                            updated_entities[j] = Entity(
                                id=e2.id, type=e2.type,
                                position=Position(x=p2_f[0], y=p2_f[1]),
                                size=e2.size,
                                velocity=Velocity(vx=v2_f[0], vy=v2_f[1]),
                                properties=e2.properties, active=e2.active,
                            )
                            collision_events.add(frozenset([e1.id, e2.id]))

        return updated_entities, collision_events
