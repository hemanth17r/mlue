"""MLUE Native C-ABI Core Loader & ctypes Interface.

Provides direct binary ctypes bindings to the compiled C kernel (mlue_core.dll / .so / .dylib).
Lays out entity records in 64-byte aligned contiguous memory matching the .mlueb format.
Adheres strictly to Tier L1 Substrate Decoupling (Standard Library only: ctypes, pathlib, typing).
"""

import sys
import ctypes
from pathlib import Path
from typing import List, Tuple, Optional, Set, FrozenSet
from runtime.model import Entity, Position, Velocity, CircleSize, BoxSize, Environment
from runtime.fixed_point import FixedPointEngine


# =========================================================================
# C-ABI STRUCTURE DEFINITIONS (EXACT 64-BYTE ENTITY RECORD)
# =========================================================================

class EntityRecordC(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("id_idx", ctypes.c_uint32),
        ("color_rgba", ctypes.c_uint32),
        ("entity_type", ctypes.c_uint8),
        ("flags", ctypes.c_uint8),
        ("ctrl_axis", ctypes.c_uint8),
        ("reserved_1", ctypes.c_uint8),
        ("ctrl_channel_idx", ctypes.c_uint32),
        ("pos_x", ctypes.c_double),
        ("pos_y", ctypes.c_double),
        ("vel_vx", ctypes.c_double),
        ("vel_vy", ctypes.c_double),
        ("size_p1", ctypes.c_double),
        ("size_p2", ctypes.c_double),
    ]


class EnvironmentC(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("width", ctypes.c_uint32),
        ("height", ctypes.c_uint32),
        ("bg_rgba", ctypes.c_uint32),
        ("reserved_0", ctypes.c_uint32),
    ]


class StepResultC(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("num_active_entities", ctypes.c_uint32),
        ("num_collision_events", ctypes.c_uint32),
        ("candidate_pairs_checked", ctypes.c_uint32),
        ("status_flags", ctypes.c_uint32),
    ]


# =========================================================================
# NATIVE CORE SINGLETON & LOADER
# =========================================================================

class NativeCore:
    """Interface to native C simulation kernel."""

    _lib: Optional[ctypes.CDLL] = None
    _initialized: bool = False
    _fallback_engine: Optional[FixedPointEngine] = None

    @classmethod
    def _find_library_path(cls) -> Optional[Path]:
        bin_dir = Path(__file__).resolve().parent / "native" / "bin"
        if sys.platform == "win32" or sys.platform == "cygwin":
            target = bin_dir / "mlue_core.dll"
        elif sys.platform == "darwin":
            target = bin_dir / "libmlue_core.dylib"
        else:
            target = bin_dir / "libmlue_core.so"

        if target.exists():
            return target
        return None

    @classmethod
    def initialize(cls) -> bool:
        if cls._initialized:
            return cls._lib is not None

        lib_path = cls._find_library_path()
        if lib_path:
            try:
                lib = ctypes.CDLL(str(lib_path))
                # Bind function signatures
                lib.mlue_core_version.restype = ctypes.c_uint32
                lib.mlue_core_version.argtypes = []

                lib.mlue_core_step.restype = StepResultC
                lib.mlue_core_step.argtypes = [
                    ctypes.POINTER(EntityRecordC),
                    ctypes.c_uint32,
                    ctypes.POINTER(EnvironmentC),
                    ctypes.c_double,
                ]

                lib.mlue_core_step_fixed.restype = StepResultC
                lib.mlue_core_step_fixed.argtypes = [
                    ctypes.POINTER(EntityRecordC),
                    ctypes.c_uint32,
                    ctypes.POINTER(EnvironmentC),
                    ctypes.c_int64,
                ]

                cls._lib = lib
            except Exception:
                cls._lib = None
        else:
            cls._lib = None

        cls._fallback_engine = FixedPointEngine(dt=1.0 / 60.0)
        cls._initialized = True
        return cls._lib is not None

    @classmethod
    def is_available(cls) -> bool:
        cls.initialize()
        return cls._lib is not None

    @classmethod
    def get_version(cls) -> Tuple[int, int, int]:
        cls.initialize()
        if cls._lib:
            v = cls._lib.mlue_core_version()
            return ((v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF)
        return (1, 5, 0)

    @classmethod
    def step(
        cls, entities: List[Entity], env: Environment, dt: float = 1.0 / 60.0
    ) -> Tuple[List[Entity], Set[FrozenSet[str]]]:
        """Executes a high-speed simulation step using native C kernel (or integer Q32.32 fallback)."""
        cls.initialize()

        if cls._lib is None:
            # Clean fallback to verified Q32.32 engine
            return cls._fallback_engine.step(entities, env)

        n = len(entities)
        if n == 0:
            return [], set()

        # Allocate contiguous C array of 64-byte records
        records_array = (EntityRecordC * n)()
        for i, e in enumerate(entities):
            flags = 0
            if e.properties.get("solid", False):
                flags |= 1
            if e.active:
                flags |= 2

            etype = 1 if e.type == "circle" else 2
            if e.type == "circle" and isinstance(e.size, CircleSize):
                p1, p2 = e.size.radius, 0.0
            elif e.type == "box" and isinstance(e.size, BoxSize):
                p1, p2 = e.size.width, e.size.height
            else:
                p1, p2 = 0.0, 0.0

            records_array[i] = EntityRecordC(
                id_idx=0,
                color_rgba=0xFFFFFFFF,
                entity_type=etype,
                flags=flags,
                ctrl_axis=0,
                reserved_1=0,
                ctrl_channel_idx=0,
                pos_x=float(e.position.x),
                pos_y=float(e.position.y),
                vel_vx=float(e.velocity.vx),
                vel_vy=float(e.velocity.vy),
                size_p1=p1,
                size_p2=p2,
            )

        env_c = EnvironmentC(
            width=env.width,
            height=env.height,
            bg_rgba=0x000000FF,
            reserved_0=0,
        )

        res = cls._lib.mlue_core_step(records_array, n, ctypes.byref(env_c), float(dt))

        # Reconstruct updated entities from C buffer
        updated: List[Entity] = []
        for i, e in enumerate(entities):
            rec = records_array[i]
            updated.append(
                Entity(
                    id=e.id,
                    type=e.type,
                    position=Position(x=rec.pos_x, y=rec.pos_y),
                    size=e.size,
                    velocity=Velocity(vx=rec.vel_vx, vy=rec.vel_vy),
                    properties=dict(e.properties),
                    active=bool(rec.flags & 2),
                )
            )

        # Collision events
        collision_events: Set[FrozenSet[str]] = set()
        return updated, collision_events
