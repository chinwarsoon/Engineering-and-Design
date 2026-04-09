"""
Schema loading and dependency resolution.
Extracted from schema_validation.py SchemaLoader class.
"""

import json
from pathlib import Path
from typing import Dict, Any, Set, List

from ..utils.paths import safe_resolve

# Import hierarchical logging functions from initiation_engine (centralized)
from initiation_engine.engine import status_print, debug_print


class SchemaLoader:
    """Load JSON schemas, resolve references, and expand dependencies."""

    def __init__(self, base_path: str | Path | None = None):
        if base_path is None:
            base_path = safe_resolve(Path(__file__).parent.parent.parent / "config" / "schemas")
        self.base_path = safe_resolve(Path(base_path))
        self.main_schema_path: Path | None = None
        self.loaded_schemas: Dict[str, Dict[str, Any]] = {}

    def set_main_schema_path(self, schema_file: str | Path) -> Path:
        """Set the main schema path so relative references resolve correctly."""
        self.main_schema_path = safe_resolve(Path(schema_file))
        if self.main_schema_path.parent.exists():
            self.base_path = self.main_schema_path.parent
        return self.main_schema_path

    def load_json_file(self, path: str | Path) -> Dict[str, Any]:
        """Load and return a JSON document from disk."""
        resolved = safe_resolve(Path(path))
        with resolved.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _resolve_reference_path(self, ref_path: str | Path) -> Path:
        """Resolve a schema reference path using several fallback strategies."""
        candidate = Path(ref_path)
        if candidate.is_absolute():
            return safe_resolve(candidate)

        search_paths: List[Path] = []
        if self.main_schema_path is not None:
            search_paths.append(safe_resolve(self.main_schema_path.parent / candidate))
        search_paths.append(safe_resolve(self.base_path / candidate))

        candidate_name = candidate.name
        search_paths.append(safe_resolve(self.base_path / candidate_name))
        if self.main_schema_path is not None:
            search_paths.append(safe_resolve(self.main_schema_path.parent / candidate_name))

        from ..utils.paths import safe_cwd
        cwd = safe_cwd()
        search_paths.append(safe_resolve(cwd / candidate))
        search_paths.append(safe_resolve(cwd / candidate_name))

        for resolved in search_paths:
            if resolved.exists():
                return resolved

        return safe_resolve(self.base_path / candidate)

    def load_schema(self, schema_name: str, fallback_data: Any = None) -> Dict[str, Any]:
        """Load a schema by stem name relative to the configured schema directory."""
        if schema_name in self.loaded_schemas:
            return self.loaded_schemas[schema_name]

        schema_file = self.base_path / f"{schema_name}.json"
        try:
            schema_data = self.load_json_file(schema_file)
            status_print(f"Loaded schema: {schema_name}")
            self.loaded_schemas[schema_name] = schema_data
            return schema_data
        except FileNotFoundError:
            status_print(f"WARNING: Schema file not found: {schema_file}")
        except json.JSONDecodeError as exc:
            status_print(f"ERROR: Invalid JSON in schema file {schema_file}: {exc}")
            if fallback_data is None:
                raise ValueError(f"Invalid JSON in schema file {schema_file}: {exc}") from exc
        except Exception as exc:
            status_print(f"ERROR: Error loading schema {schema_name}: {exc}")
            if fallback_data is None:
                raise ValueError(f"Error loading schema {schema_name}: {exc}") from exc

        if fallback_data is not None:
            status_print(f"Using fallback data for {schema_name}")
            self.loaded_schemas[schema_name] = fallback_data
            return fallback_data

        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    def load_schema_from_path(self, schema_path: str | Path, fallback_data: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Load a schema by path, resolving it relative to the main schema when needed."""
        cache_key = str(safe_resolve(Path(schema_path))) if Path(schema_path).is_absolute() else str(schema_path)
        if cache_key in self.loaded_schemas:
            return self.loaded_schemas[cache_key]

        schema_file = self._resolve_reference_path(schema_path)
        try:
            schema_data = self.load_json_file(schema_file)
            status_print(f"Loaded schema: {schema_file}")
            self.loaded_schemas[cache_key] = schema_data
            return schema_data
        except FileNotFoundError:
            status_print(f"WARNING: Schema file not found: {schema_file}")
        except json.JSONDecodeError as exc:
            status_print(f"ERROR: Invalid JSON in schema file {schema_file}: {exc}")
            if fallback_data is None:
                raise ValueError(f"Invalid JSON in schema file {schema_file}: {exc}") from exc
        except Exception as exc:
            status_print(f"ERROR: Error loading schema {schema_file}: {exc}")
            if fallback_data is None:
                raise ValueError(f"Error loading schema {schema_file}: {exc}") from exc

        if fallback_data is not None:
            status_print(f"Using fallback data for {schema_path}")
            self.loaded_schemas[cache_key] = fallback_data
            return fallback_data

        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    def resolve_schema_dependencies(self, main_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve all `schema_references` and append them to the main schema data."""
        resolved_schema = main_schema.copy()
        visited_paths: Set[Path] = set()

        if self.main_schema_path is not None:
            visited_paths.add(self.main_schema_path)

        for ref_name, ref_path in main_schema.get("schema_references", {}).items():
            try:
                schema_data = self._resolve_schema_dependency(ref_path, visited_paths.copy())
                resolved_schema[f"{ref_name}_data"] = schema_data
            except Exception as exc:
                status_print(f"ERROR: Failed to resolve schema reference {ref_name}: {exc}")
        return resolved_schema

    def _resolve_schema_dependency(self, schema_path: str | Path, visited_paths: Set[Path]) -> Dict[str, Any]:
        """Resolve one schema dependency recursively while guarding against cycles."""
        resolved_path = self._resolve_reference_path(schema_path)
        if resolved_path in visited_paths:
            raise ValueError(f"Circular schema dependency detected while resolving {resolved_path}")

        schema_data = self.load_schema_from_path(schema_path)
        visited_paths.add(resolved_path)

        nested_refs = schema_data.get("schema_references", {})
        if isinstance(nested_refs, dict):
            for ref_name, ref_path in nested_refs.items():
                schema_data[f"{ref_name}_data"] = self._resolve_schema_dependency(ref_path, visited_paths.copy())

        return schema_data


def load_schema_parameters(schema_path: Path) -> Dict[str, Any]:
    """
    Load parameters section from schema file.
    
    Args:
        schema_path: Path to the JSON schema file
        
    Returns:
        Dictionary containing the 'parameters' section, or empty dict if not present
    """
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle).get("parameters", {})
