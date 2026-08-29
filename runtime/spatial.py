"""MLUE 2D Spatial Indexing & Broadphase Acceleration Core.

Provides high-performance 2D Axis-Aligned Bounding Box (AABB) math,
Dynamic Uniform Spatial Hash Grid, and Bounding Volume Hierarchy (BVH).
Adheres strictly to Tier L1 Substrate Decoupling (Standard Library only: math, dataclasses, typing, collections).
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set, Union
from collections import defaultdict
from runtime.model import Entity, CircleSize, BoxSize, Environment


@dataclass(slots=True)
class AABB2D:
    """Represents a 2D Axis-Aligned Bounding Box in continuous normalized coordinates [0.0, 1.0]^2."""
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def intersects(self, other: "AABB2D") -> bool:
        """Evaluates whether two AABBs overlap (including edge contact)."""
        return not (
            self.max_x < other.min_x
            or self.min_x > other.max_x
            or self.max_y < other.min_y
            or self.min_y > other.max_y
        )

    def contains_point(self, x: float, y: float) -> bool:
        """Returns True if point (x, y) lies inside or on the boundary of this AABB."""
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y

    def union(self, other: "AABB2D") -> "AABB2D":
        """Returns the minimal enclosing AABB covering both this and other."""
        return AABB2D(
            min_x=min(self.min_x, other.min_x),
            min_y=min(self.min_y, other.min_y),
            max_x=max(self.max_x, other.max_x),
            max_y=max(self.max_y, other.max_y),
        )

    def area(self) -> float:
        """Returns the 2D surface area of this bounding box."""
        return max(0.0, self.max_x - self.min_x) * max(0.0, self.max_y - self.min_y)


def compute_entity_aabb(entity: Entity, env: Environment) -> AABB2D:
    """Computes exact normalized AABB for an entity in the given environment viewport."""
    w = env.width
    h = env.height
    min_dim = min(w, h)

    if entity.type == "circle" and isinstance(entity.size, CircleSize):
        r = entity.size.radius
        ex = r * (min_dim / w)
        ey = r * (min_dim / h)
    elif entity.type == "box" and isinstance(entity.size, BoxSize):
        ex = entity.size.width / 2.0
        ey = entity.size.height / 2.0
    else:
        ex, ey = 0.0, 0.0

    px, py = entity.position.x, entity.position.y
    return AABB2D(
        min_x=px - ex,
        min_y=py - ey,
        max_x=px + ex,
        max_y=py + ey,
    )


class SpatialHashGrid2D:
    """Uniform Spatial Hash Grid broadphase accelerator with O(1) amortized insertion and O(N log N) / O(N) querying."""

    def __init__(self, cell_size: float = 0.05):
        self.cell_size = max(0.001, float(cell_size))
        self.inv_cell_size = 1.0 / self.cell_size
        self._grid: Dict[Tuple[int, int], List[int]] = defaultdict(list)
        self.entity_count = 0

    def clear(self) -> None:
        """Clears all grid cell bucket registrations."""
        self._grid.clear()
        self.entity_count = 0

    def insert(self, entity_idx: int, aabb: AABB2D) -> None:
        """Inserts an entity index into all intersecting grid cell buckets."""
        c_min_x = math.floor(aabb.min_x * self.inv_cell_size)
        c_max_x = math.floor(aabb.max_x * self.inv_cell_size)
        c_min_y = math.floor(aabb.min_y * self.inv_cell_size)
        c_max_y = math.floor(aabb.max_y * self.inv_cell_size)

        for cy in range(c_min_y, c_max_y + 1):
            for cx in range(c_min_x, c_max_x + 1):
                self._grid[(cx, cy)].append(entity_idx)

        self.entity_count += 1

    def build(
        self,
        entities: List[Entity],
        env: Environment,
        precomputed_aabbs: Optional[List[AABB2D]] = None,
    ) -> List[AABB2D]:
        """Builds spatial grid from entity list. Returns list of computed AABBs."""
        self.clear()
        aabbs: List[AABB2D] = []

        # Automatically adapt cell size if entity size distribution warrants it
        max_extent = 0.025
        for i, e in enumerate(entities):
            if not e.active:
                aabbs.append(AABB2D(0.0, 0.0, 0.0, 0.0))
                continue
            aabb = precomputed_aabbs[i] if precomputed_aabbs is not None else compute_entity_aabb(e, env)
            aabbs.append(aabb)
            ex = aabb.max_x - aabb.min_x
            ey = aabb.max_y - aabb.min_y
            if ex > max_extent:
                max_extent = ex
            if ey > max_extent:
                max_extent = ey

        # Optimal cell size is roughly 2x the maximum entity diameter
        adapted_cell_size = max(0.02, min(0.25, max_extent * 2.0))
        self.cell_size = adapted_cell_size
        self.inv_cell_size = 1.0 / self.cell_size

        for i, e in enumerate(entities):
            if e.active:
                self.insert(i, aabbs[i])

        return aabbs

    def get_candidate_pairs(self, aabbs: List[AABB2D]) -> List[Tuple[int, int]]:
        """Extracts broadphase candidate pairs with AABB overlap validation.
        
        Guarantees zero false negatives and deduplicated (i, j) pairs where i < j.
        """
        candidate_set: Set[Tuple[int, int]] = set()

        for cell_entities in self._grid.values():
            n = len(cell_entities)
            if n < 2:
                continue
            for i_idx in range(n):
                idx_a = cell_entities[i_idx]
                for j_idx in range(i_idx + 1, n):
                    idx_b = cell_entities[j_idx]
                    if idx_a == idx_b:
                        continue
                    pair = (idx_a, idx_b) if idx_a < idx_b else (idx_b, idx_a)
                    candidate_set.add(pair)

        # Broadphase AABB overlap filter
        valid_candidates: List[Tuple[int, int]] = []
        for i, j in candidate_set:
            if aabbs[i].intersects(aabbs[j]):
                valid_candidates.append((i, j))

        return valid_candidates

    def query_aabb(self, query_box: AABB2D, aabbs: List[AABB2D]) -> List[int]:
        """Queries all active entity indices overlapping query_box."""
        c_min_x = math.floor(query_box.min_x * self.inv_cell_size)
        c_max_x = math.floor(query_box.max_x * self.inv_cell_size)
        c_min_y = math.floor(query_box.min_y * self.inv_cell_size)
        c_max_y = math.floor(query_box.max_y * self.inv_cell_size)

        candidate_indices: Set[int] = set()
        for cy in range(c_min_y, c_max_y + 1):
            for cx in range(c_min_x, c_max_x + 1):
                for idx in self._grid.get((cx, cy), []):
                    candidate_indices.add(idx)

        return [idx for idx in candidate_indices if query_box.intersects(aabbs[idx])]


@dataclass
class BVHNode2D:
    """Node in dynamic Bounding Volume Hierarchy tree."""
    aabb: AABB2D
    left: Optional["BVHNode2D"] = None
    right: Optional["BVHNode2D"] = None
    entity_idx: Optional[int] = None

    @property
    def is_leaf(self) -> bool:
        return self.entity_idx is not None


class BVHTree2D:
    """Dynamic 2D Bounding Volume Hierarchy (BVH) for sparse and hierarchical spatial queries."""

    def __init__(self):
        self.root: Optional[BVHNode2D] = None

    def build(self, entities: List[Entity], env: Environment) -> None:
        """Constructs a balanced BVH tree using recursive spatial median splitting."""
        items: List[Tuple[int, AABB2D]] = [
            (i, compute_entity_aabb(e, env))
            for i, e in enumerate(entities)
            if e.active
        ]
        if not items:
            self.root = None
            return

        self.root = self._build_recursive(items, axis=0)

    def _build_recursive(self, items: List[Tuple[int, AABB2D]], axis: int) -> BVHNode2D:
        if len(items) == 1:
            idx, aabb = items[0]
            return BVHNode2D(aabb=aabb, entity_idx=idx)

        # Sort items along split axis (0: X-center, 1: Y-center)
        if axis == 0:
            items.sort(key=lambda item: (item[1].min_x + item[1].max_x) * 0.5)
        else:
            items.sort(key=lambda item: (item[1].min_y + item[1].max_y) * 0.5)

        mid = len(items) // 2
        left_child = self._build_recursive(items[:mid], 1 - axis)
        right_child = self._build_recursive(items[mid:], 1 - axis)

        combined_aabb = left_child.aabb.union(right_child.aabb)
        return BVHNode2D(aabb=combined_aabb, left=left_child, right=right_child)

    def query_aabb(self, query_box: AABB2D) -> List[int]:
        """Traverses BVH tree and returns all entity indices whose bounding box intersects query_box."""
        results: List[int] = []
        if self.root is None:
            return results

        stack = [self.root]
        while stack:
            node = stack.pop()
            if not node.aabb.intersects(query_box):
                continue
            if node.is_leaf:
                if node.entity_idx is not None:
                    results.append(node.entity_idx)
            else:
                if node.left:
                    stack.append(node.left)
                if node.right:
                    stack.append(node.right)

        return results
