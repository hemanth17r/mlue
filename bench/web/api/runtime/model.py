"""MLUE Phase 0.6 Data Model

Defines structured representations for MLUE entities, geometry, velocity,
declarative state variables, relational trigger rules, collision events,
entity lifecycles, and evaluated simulation states.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Union, Optional


@dataclass(frozen=True)
class Position:
    x: float
    y: float


@dataclass(frozen=True)
class CircleSize:
    radius: float


@dataclass(frozen=True)
class BoxSize:
    width: float
    height: float


@dataclass(frozen=True)
class Velocity:
    vx: float = 0.0
    vy: float = 0.0


@dataclass(frozen=True)
class Entity:
    id: str
    type: str
    position: Position
    size: Union[CircleSize, BoxSize]
    velocity: Velocity = field(default_factory=Velocity)
    properties: Dict[str, Any] = field(default_factory=dict)
    active: bool = True


@dataclass(frozen=True)
class Environment:
    width: int = 400
    height: int = 400
    background: str = "#000000"


@dataclass(frozen=True)
class Condition:
    op: str
    value: Any
    entity: Optional[str] = None
    property: Optional[str] = None
    state_variable: Optional[str] = None


@dataclass(frozen=True)
class Action:
    type: str
    target: str
    amount: Optional[float] = None
    value: Optional[Any] = None
    property: Optional[str] = None
    position: Optional[Position] = None
    velocity: Optional[Velocity] = None


@dataclass(frozen=True)
class Rule:
    trigger: str
    actions: List[Action] = field(default_factory=list)
    event: Optional[str] = None
    entities: Optional[Tuple[str, str]] = None
    condition: Optional[Condition] = None


@dataclass(frozen=True)
class ComputedShape:
    id: str
    type: str
    # Bounding box in concrete coordinate units (x0, y0, x1, y1)
    bbox: Tuple[float, float, float, float]
    # Center position in concrete coordinate units (cx, cy)
    center: Tuple[float, float]
    color: str


@dataclass(frozen=True)
class EvaluationResult:
    width: int
    height: int
    background: str
    shapes: List[ComputedShape]


@dataclass(frozen=True)
class MLUEDocument:
    version: str
    environment: Environment
    entities: List[Entity]
    state_variables: Dict[str, Any] = field(default_factory=dict)
    rules: List[Rule] = field(default_factory=list)


@dataclass(frozen=True)
class SimulationState:
    time: float
    environment: Environment
    entities: List[Entity]
    result: EvaluationResult
    state_variables: Dict[str, Any] = field(default_factory=dict)
    rules: List[Rule] = field(default_factory=list)
