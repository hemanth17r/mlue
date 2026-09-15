"""MLUE AI-Native Catalog Engine

Zero-dependency in-memory catalog registry for discovering, searching, validating,
and programmatically registering standardized MLUE shapes, parts, tokens, and blueprints.
Designed for sub-millisecond execution and deterministic AI model ergonomics.
"""

import os
import json
import copy
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class CatalogError(Exception):
    """Base exception for catalog operations."""
    pass


class CatalogValidationError(CatalogError):
    """Raised when an entry fails schema or coordinate bounds invariants."""
    def __init__(self, errors: List[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


class Catalog:
    """In-memory index and CRUD engine for MLUE catalog definitions."""

    VALID_KINDS = {"shape", "part", "token", "blueprint"}

    def __init__(self, catalog_dir: Optional[str] = None):
        if catalog_dir:
            self.catalog_dir = Path(catalog_dir).resolve()
        else:
            # Check packaged catalog_data first, then fallback to repo root catalog
            pkg_data_dir = (Path(__file__).resolve().parent / "catalog_data").resolve()
            if pkg_data_dir.exists():
                self.catalog_dir = pkg_data_dir
            else:
                base_dir = Path(__file__).resolve().parent.parent
                self.catalog_dir = (base_dir / "catalog").resolve()

        self._index: Dict[str, Dict[str, Any]] = {}
        self._tag_index: Dict[str, List[str]] = {}
        self._kind_index: Dict[str, List[str]] = {k: [] for k in self.VALID_KINDS}
        self.reload()

    def reload(self) -> None:
        """Scans catalog_dir and loads all definitions into the in-memory cache."""
        self._index.clear()
        self._tag_index.clear()
        self._kind_index = {k: [] for k in self.VALID_KINDS}

        if not self.catalog_dir.exists():
            return

        for json_path in self.catalog_dir.rglob("*.json"):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                
                entry_id = entry.get("id")
                entry_kind = entry.get("kind")
                if not entry_id or not entry_kind:
                    continue

                key = f"{entry_kind}/{entry_id}"
                self._index[key] = entry

                if entry_kind in self._kind_index:
                    self._kind_index[entry_kind].append(key)

                for tag in entry.get("tags", []):
                    norm_tag = str(tag).lower().strip()
                    if norm_tag not in self._tag_index:
                        self._tag_index[norm_tag] = []
                    self._tag_index[norm_tag].append(key)

            except Exception:
                # Silently ignore corrupt files during reload, let validate catch them
                continue

    def get(self, kind: str, name: str) -> Optional[Dict[str, Any]]:
        """Fetches a deep copy of a catalog entry by kind and name."""
        key = f"{kind}/{name}"
        entry = self._index.get(key)
        if entry is None:
            # Fallback search across all kinds if kind was omitted or misspelled
            for k, data in self._index.items():
                if k.endswith(f"/{name}") or data.get("id") == name:
                    return copy.deepcopy(data)
            return None
        return copy.deepcopy(entry)

    def list(self, kind: Optional[str] = None, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns indexed summaries of catalog items filtered by kind and/or tag."""
        if kind and kind in self._kind_index:
            candidate_keys = self._kind_index[kind]
        else:
            candidate_keys = list(self._index.keys())

        if tag:
            norm_tag = str(tag).lower().strip()
            tagged_keys = set(self._tag_index.get(norm_tag, []))
            candidate_keys = [k for k in candidate_keys if k in tagged_keys]

        results = []
        for k in sorted(candidate_keys):
            item = self._index[k]
            results.append({
                "id": item.get("id"),
                "kind": item.get("kind"),
                "version": item.get("version", "1.0.0"),
                "summary": item.get("summary", ""),
                "tags": item.get("tags", [])
            })
        return results

    def search(self, query: str, kind: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Rank-orders catalog items matching a search query.
        
        Scoring heuristics:
          - Exact ID match: 100 pts
          - ID starts with query: 60 pts
          - ID contains query: 40 pts
          - Tag exact match: 50 pts
          - Tag contains query: 25 pts
          - Summary keyword match: 15 pts per word
        """
        if not query or not query.strip():
            return self.list(kind=kind)[:limit]

        tokens = [t.lower().strip() for t in query.split() if t.strip()]
        full_query = query.lower().strip()

        candidates = self.list(kind=kind)
        scored: List[Tuple[float, Dict[str, Any]]] = []

        for item in candidates:
            score = 0.0
            item_id = str(item.get("id", "")).lower()
            item_tags = [str(t).lower() for t in item.get("tags", [])]
            item_summary = str(item.get("summary", "")).lower()

            # ID scoring
            if item_id == full_query:
                score += 100.0
            elif item_id.startswith(full_query):
                score += 60.0
            elif full_query in item_id:
                score += 40.0

            # Tag scoring
            for tag in item_tags:
                if tag == full_query:
                    score += 50.0
                elif full_query in tag:
                    score += 25.0

            # Keyword scoring
            for token in tokens:
                if token in item_id:
                    score += 20.0
                for tag in item_tags:
                    if token in tag:
                        score += 15.0
                if token in item_summary:
                    score += 10.0

            if score > 0.0:
                scored.append((score, item))

        # Sort descending by score
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    def validate(self, entry: Dict[str, Any]) -> List[str]:
        """Strictly validates an entry against schema and [0.0, 1.0] coordinate invariants."""
        errors: List[str] = []

        if not isinstance(entry, dict):
            return ["Catalog entry must be a JSON object (dict)."]

        # Required fields
        for field in ("id", "kind", "tags", "summary"):
            if field not in entry:
                errors.append(f"Missing required field '{field}'.")

        entry_id = entry.get("id")
        if entry_id and not isinstance(entry_id, str):
            errors.append("Field 'id' must be a string.")

        entry_kind = entry.get("kind")
        if entry_kind not in self.VALID_KINDS:
            errors.append(f"Invalid kind '{entry_kind}'. Must be one of {sorted(list(self.VALID_KINDS))}.")

        tags = entry.get("tags")
        if tags is not None and not isinstance(tags, list):
            errors.append("Field 'tags' must be a list of strings.")

        # Coordinate clamping validation helper
        def check_coords(obj: Any, path: str):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    subpath = f"{path}.{k}" if path else k
                    if k in ("x", "y", "width", "height", "radius", "thickness"):
                        if isinstance(v, (int, float)):
                            if v < 0.0 or v > 1.0:
                                errors.append(f"Coordinate out of bounds [0.0, 1.0] at '{subpath}': {v}")
                    else:
                        check_coords(v, subpath)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_coords(item, f"{path}[{i}]")

        if "defaults" in entry:
            check_coords(entry["defaults"], "defaults")
        if "entity_template" in entry:
            check_coords(entry["entity_template"], "entity_template")
        if "entities_template" in entry:
            check_coords(entry["entities_template"], "entities_template")

        return errors

    def register(self, kind: str, name: str, entry: Dict[str, Any], overwrite: bool = False) -> Dict[str, Any]:
        """Validates and persists a new catalog entry to disk, immediately updating the in-memory index."""
        if kind not in self.VALID_KINDS:
            raise CatalogError(f"Invalid kind '{kind}'. Must be one of {sorted(list(self.VALID_KINDS))}.")

        entry["kind"] = kind
        entry["id"] = name

        errors = self.validate(entry)
        if errors:
            raise CatalogValidationError(errors)

        target_dir = self.catalog_dir / f"{kind}s" if not kind.endswith("s") else self.catalog_dir / kind
        # If folder doesn't exist under plural, check singular or plural
        if (self.catalog_dir / kind).is_dir():
            target_dir = self.catalog_dir / kind
        elif (self.catalog_dir / f"{kind}s").is_dir():
            target_dir = self.catalog_dir / f"{kind}s"
        else:
            target_dir = self.catalog_dir / f"{kind}s"

        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / f"{name}.json"

        if target_file.exists() and not overwrite:
            raise CatalogError(f"Catalog entry '{kind}/{name}' already exists at '{target_file}'. Set overwrite=True to replace.")

        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)

        key = f"{kind}/{name}"
        self._index[key] = copy.deepcopy(entry)
        if key not in self._kind_index[kind]:
            self._kind_index[kind].append(key)

        for tag in entry.get("tags", []):
            norm_tag = str(tag).lower().strip()
            if norm_tag not in self._tag_index:
                self._tag_index[norm_tag] = []
            if key not in self._tag_index[norm_tag]:
                self._tag_index[norm_tag].append(key)

        return {
            "success": True,
            "id": name,
            "kind": kind,
            "file_path": str(target_file)
        }
