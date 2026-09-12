"""MLUE Runtime Package — Native AI Computational & Spatial Simulation Substrate (v2.5.0)"""

from .model import (
    Position,
    Velocity,
    CircleSize,
    BoxSize,
    SegmentSize,
    CapsuleSize,
    TextSize,
    Entity,
    Environment,
    Condition,
    Action,
    Rule,
    ComputedShape,
    ComputedConstraint,
    EvaluationResult,
    Constraint,
    MLUEDocument,
    PointerState,
    SimulationState,
)
from .loader import load_mlue, validate_and_parse, MLUEValidationError
from .engine import MLUEEngine
from .adapter import PresentationAdapter, TkinterAdapter
from .ai_interface import MLUEAIInterface
from .binary import load_mlueb, save_mlueb
from .wal import WALWriter, WALReader, WALReplayer
from .patch import MLUEPatchEngine, apply_patch
from .spatial import SpatialGrid, BVHTree2D, AABB2D
from .fixed_point import FixedPointEngine, FixedVector
from .batch import BatchSimulator

__version__ = "2.5.0"

__all__ = [
    "Position",
    "Velocity",
    "CircleSize",
    "BoxSize",
    "SegmentSize",
    "CapsuleSize",
    "TextSize",
    "Entity",
    "Environment",
    "Condition",
    "Action",
    "Rule",
    "ComputedShape",
    "ComputedConstraint",
    "EvaluationResult",
    "Constraint",
    "MLUEDocument",
    "PointerState",
    "SimulationState",
    "load_mlue",
    "validate_and_parse",
    "MLUEValidationError",
    "MLUEEngine",
    "PresentationAdapter",
    "TkinterAdapter",
    "MLUEAIInterface",
    "load_mlueb",
    "save_mlueb",
    "WALWriter",
    "WALReader",
    "WALReplayer",
    "MLUEPatchEngine",
    "apply_patch",
    "SpatialGrid",
    "BVHTree2D",
    "AABB2D",
    "FixedPointEngine",
    "FixedVector",
    "BatchSimulator",
    "__version__",
]

