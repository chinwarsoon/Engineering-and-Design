#!/usr/bin/env python3
"""
Shared schema loading and validation utilities for DCC workflow modules.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SchemaLoader:
    """Load JSON schemas, resolve references, and expand dependencies."""

    def __init__(self, base_path: str | Path | None = None):
        if base_path is None:
            base_path = Path(__file__).resolve().parent.parent / "config" / "schemas"
        self.base_path = Path(base_path).expanduser().resolve()
        self.main_schema_path: Path | None = None
        self.loaded_schemas: Dict[str, Dict[str, Any]] = {}

    def set_main_schema_path(self, schema_file: str | Path) -> Path:
        """Set the main schema path so relative references resolve correctly."""
        self.main_schema_path = Path(schema_file).expanduser().resolve()
        if self.main_schema_path.parent.exists():
            self.base_path = self.main_schema_path.parent
        return self.main_schema_path

    def load_json_file(self, path: str | Path) -> Dict[str, Any]:
        """Load and return a JSON document from disk."""
        resolved = Path(path).expanduser().resolve()
        with resolved.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _resolve_reference_path(self, ref_path: str | Path) -> Path:
        """Resolve a schema reference path using several fallback strategies."""
        candidate = Path(ref_path)
        if candidate.is_absolute():
            return candidate.expanduser().resolve()

        search_paths: List[Path] = []
        if self.main_schema_path is not None:
            search_paths.append((self.main_schema_path.parent / candidate).resolve())
        search_paths.append((self.base_path / candidate).resolve())

        candidate_name = candidate.name
        search_paths.append((self.base_path / candidate_name).resolve())
        if self.main_schema_path is not None:
            search_paths.append((self.main_schema_path.parent / candidate_name).resolve())

        search_paths.append((Path.cwd() / candidate).resolve())
        search_paths.append((Path.cwd() / candidate_name).resolve())

        for resolved in search_paths:
            if resolved.exists():
                return resolved

        return (self.base_path / candidate).resolve()

    def load_schema(self, schema_name: str, fallback_data: Any = None) -> Dict[str, Any]:
        """Load a schema by stem name relative to the configured schema directory."""
        if schema_name in self.loaded_schemas:
            return self.loaded_schemas[schema_name]

        schema_file = self.base_path / f"{schema_name}.json"
        try:
            schema_data = self.load_json_file(schema_file)
            logger.info("Loaded schema: %s", schema_name)
            self.loaded_schemas[schema_name] = schema_data
            return schema_data
        except FileNotFoundError:
            logger.warning("Schema file not found: %s", schema_file)
        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON in schema file %s: %s", schema_file, exc)
            if fallback_data is None:
                raise ValueError(f"Invalid JSON in schema file {schema_file}: {exc}") from exc
        except Exception as exc:
            logger.error("Error loading schema %s: %s", schema_name, exc)
            if fallback_data is None:
                raise ValueError(f"Error loading schema {schema_name}: {exc}") from exc

        if fallback_data is not None:
            logger.info("Using fallback data for %s", schema_name)
            self.loaded_schemas[schema_name] = fallback_data
            return fallback_data

        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    def load_schema_from_path(self, schema_path: str | Path, fallback_data: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Load a schema by path, resolving it relative to the main schema when needed."""
        cache_key = str(Path(schema_path).expanduser().resolve()) if Path(schema_path).is_absolute() else str(schema_path)
        if cache_key in self.loaded_schemas:
            return self.loaded_schemas[cache_key]

        schema_file = self._resolve_reference_path(schema_path)
        try:
            schema_data = self.load_json_file(schema_file)
            logger.info("Loaded schema: %s", schema_file)
            self.loaded_schemas[cache_key] = schema_data
            return schema_data
        except FileNotFoundError:
            logger.warning("Schema file not found: %s", schema_file)
        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON in schema file %s: %s", schema_file, exc)
            if fallback_data is None:
                raise ValueError(f"Invalid JSON in schema file {schema_file}: {exc}") from exc
        except Exception as exc:
            logger.error("Error loading schema %s: %s", schema_file, exc)
            if fallback_data is None:
                raise ValueError(f"Error loading schema {schema_file}: {exc}") from exc

        if fallback_data is not None:
            logger.info("Using fallback data for %s", schema_path)
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
                logger.error("Failed to resolve schema reference %s: %s", ref_name, exc)
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


class SchemaValidator:
    """Validate a main schema file and its external references."""

    def __init__(self, schema_file: str | Path):
        self.schema_file = Path(schema_file).expanduser().resolve()
        self.loader = SchemaLoader()
        self.loader.set_main_schema_path(self.schema_file)

    def validate(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "main_schema_path": str(self.schema_file),
            "references": [],
            "dependency_cycle": [],
            "errors": [],
            "ready": True,
        }

        if not self.schema_file.is_file():
            results["errors"].append(f"Main schema file not found: {self.schema_file}")
            results["ready"] = False
            return results

        try:
            main_schema = self.loader.load_json_file(self.schema_file)
        except json.JSONDecodeError as exc:
            results["errors"].append(f"Invalid JSON in main schema {self.schema_file}: {exc}")
            results["ready"] = False
            return results
        except Exception as exc:
            results["errors"].append(f"Error loading main schema {self.schema_file}: {exc}")
            results["ready"] = False
            return results

        enhanced_schema = main_schema.get("enhanced_schema", {})
        columns = enhanced_schema.get("columns", {})
        if not isinstance(enhanced_schema, dict):
            results["errors"].append("Main schema is missing a valid 'enhanced_schema' object")
        if not isinstance(columns, dict):
            results["errors"].append("Main schema is missing a valid 'enhanced_schema.columns' object")

        visited_paths: Set[Path] = set()
        dependency_cycle = self._detect_circular_dependencies(
            current_path=self.schema_file,
            current_schema=main_schema,
            visited_paths=visited_paths,
            recursion_stack=[],
            results=results,
        )
        if dependency_cycle:
            cycle_text = " -> ".join(str(path) for path in dependency_cycle)
            results["dependency_cycle"] = [str(path) for path in dependency_cycle]
            results["errors"].append(f"Circular schema dependency detected: {cycle_text}")

        results["ready"] = not results["errors"]
        return results

    def _detect_circular_dependencies(
        self,
        current_path: Path,
        current_schema: Dict[str, Any],
        visited_paths: Set[Path],
        recursion_stack: List[Path],
        results: Dict[str, Any],
    ) -> List[Path]:
        """Walk nested schema references and return one cycle path if found."""
        resolved_current_path = current_path.expanduser().resolve()
        visited_paths.add(resolved_current_path)
        recursion_stack.append(resolved_current_path)

        for ref_name, ref_path in current_schema.get("schema_references", {}).items():
            resolved_path = self.loader._resolve_reference_path(ref_path)
            reference_result: Dict[str, Any] = {
                "reference": ref_name,
                "configured_path": ref_path,
                "source_path": str(resolved_current_path),
                "resolved_path": str(resolved_path),
                "exists": resolved_path.is_file(),
            }

            if not resolved_path.is_file():
                reference_result["error"] = f"Referenced schema file not found: {ref_path}"
                results["errors"].append(reference_result["error"])
                results["references"].append(reference_result)
                continue

            try:
                ref_schema = self.loader.load_json_file(resolved_path)
            except json.JSONDecodeError as exc:
                reference_result["exists"] = False
                reference_result["error"] = f"Invalid JSON in referenced schema {ref_path}: {exc}"
                results["errors"].append(reference_result["error"])
                results["references"].append(reference_result)
                continue
            except Exception as exc:
                reference_result["exists"] = False
                reference_result["error"] = f"Error reading referenced schema {ref_path}: {exc}"
                results["errors"].append(reference_result["error"])
                results["references"].append(reference_result)
                continue

            results["references"].append(reference_result)

            if resolved_path in recursion_stack:
                cycle_start = recursion_stack.index(resolved_path)
                return recursion_stack[cycle_start:] + [resolved_path]

            if resolved_path not in visited_paths:
                cycle = self._detect_circular_dependencies(
                    current_path=resolved_path,
                    current_schema=ref_schema,
                    visited_paths=visited_paths,
                    recursion_stack=recursion_stack.copy(),
                    results=results,
                )
                if cycle:
                    return cycle

        return []

    def load_main_schema(self) -> Dict[str, Any]:
        """Load the main schema after validation has passed."""
        return self.loader.load_json_file(self.schema_file)

    def load_resolved_schema(self) -> Dict[str, Any]:
        """Load the main schema and resolve all configured dependencies."""
        main_schema = self.load_main_schema()
        return self.loader.resolve_schema_dependencies(main_schema)


def _default_schema_path() -> Path:
    return Path(__file__).resolve().parent.parent / "config" / "schemas" / "dcc_register_enhanced.json"


def format_report(results: Dict[str, Any]) -> str:
    """Format schema validation results for terminal output."""
    lines: List[str] = []
    lines.append("SCHEMA VALIDATION")
    lines.append("=" * 72)
    lines.append(f"Main Schema: {results['main_schema_path']}")

    if results.get("references"):
        lines.append("")
        lines.append("Schema References:")
        for item in results["references"]:
            status = "OK" if item.get("exists") else "MISS"
            label = item.get("reference") or "schema_reference"
            target = item.get("resolved_path") or item.get("error") or "unresolved"
            lines.append(f"  [{status}] {label} -> {target}")

    if results.get("dependency_cycle"):
        lines.append("")
        lines.append("Dependency Cycle:")
        lines.append(f"  {' -> '.join(results['dependency_cycle'])}")

    if results.get("errors"):
        lines.append("")
        lines.append("Errors:")
        for error in results["errors"]:
            lines.append(f"  - {error}")

    lines.append("")
    lines.append("Summary:")
    lines.append(f"  Ready: {'YES' if results.get('ready') else 'NO'}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate schema references and detect circular schema dependencies.")
    parser.add_argument(
        "--schema-file",
        default=str(_default_schema_path()),
        help="Main schema file to validate. Defaults to dcc_register_enhanced.json in config/schemas.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print validation results as JSON instead of a text report.",
    )
    args = parser.parse_args()

    results = SchemaValidator(args.schema_file).validate()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_report(results))

    return 0 if results.get("ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
