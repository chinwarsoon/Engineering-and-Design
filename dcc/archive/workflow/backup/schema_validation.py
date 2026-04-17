#!/usr/bin/env python3
"""
Shared schema loading and validation utilities for DCC workflow modules.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path


def _safe_resolve(path: Path) -> Path:
    """Return an absolute path without filesystem I/O (no resolve, no expanduser)."""
    return Path(path).absolute()


def _safe_cwd() -> Path:
    """Get current working directory safely, falling back if inaccessible."""
    try:
        return Path.cwd().absolute()
    except (OSError, PermissionError):
        pass
    try:
        return Path(os.getcwd())
    except (OSError, PermissionError):
        pass
    # Final fallback: script directory (guaranteed to exist since script is running)
    return Path(__file__).parent.absolute()


from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_validation_status_path(schema_file: str | Path) -> Path:
    """Return the default persisted schema-validation status path."""
    schema_path = _safe_resolve(Path(schema_file))
    project_root = schema_path.parents[2] if len(schema_path.parents) >= 3 else schema_path.parent
    return project_root / "output" / "schema_validation_status.json"


def _tracked_schema_files(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build tracked schema file metadata for pipeline enforcement."""
    tracked_files: List[Dict[str, Any]] = []
    main_schema_path = _safe_resolve(Path(results["main_schema_path"]))
    if main_schema_path.exists():
        tracked_files.append(
            {
                "path": str(main_schema_path),
                "mtime_ns": main_schema_path.stat().st_mtime_ns,
            }
        )

    seen_paths = {str(main_schema_path)}
    for item in results.get("references", []):
        resolved_path = item.get("resolved_path")
        if not resolved_path or resolved_path in seen_paths:
            continue
        path = _safe_resolve(Path(resolved_path))
        if not path.exists():
            continue
        tracked_files.append(
            {
                "path": str(path),
                "mtime_ns": path.stat().st_mtime_ns,
            }
        )
        seen_paths.add(str(path))

    return tracked_files


def write_validation_status(results: Dict[str, Any], status_path: str | Path | None = None) -> Path:
    """Persist schema-validation status for downstream pipeline steps."""
    destination = _safe_resolve(Path(status_path)) if status_path else get_validation_status_path(results["main_schema_path"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "main_schema_path": results["main_schema_path"],
        "ready": bool(results.get("ready", False)),
        "errors": results.get("errors", []),
        "dependency_cycle": results.get("dependency_cycle", []),
        "tracked_files": _tracked_schema_files(results),
    }
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination


def load_validation_status(schema_file: str | Path, status_path: str | Path | None = None) -> Dict[str, Any]:
    """Load the persisted schema-validation status for a schema file."""
    source = _safe_resolve(Path(status_path)) if status_path else get_validation_status_path(schema_file)
    with source.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_validation_status(schema_file: str | Path, status_path: str | Path | None = None) -> tuple[bool, str]:
    """Check whether a persisted validation status is present and current."""
    schema_path = _safe_resolve(Path(schema_file))
    try:
        status = load_validation_status(schema_path, status_path)
    except FileNotFoundError:
        return False, (
            f"Schema validation status not found for {schema_path}. "
            f"Run `python dcc/workflow/schema_validation.py --schema-file {schema_path}` first."
        )
    except Exception as exc:
        return False, f"Could not read schema validation status for {schema_path}: {exc}"

    if _safe_resolve(Path(status.get("main_schema_path", ""))) != schema_path:
        return False, (
            f"Schema validation status does not match {schema_path}. "
            f"Run `python dcc/workflow/schema_validation.py --schema-file {schema_path}` first."
        )

    if not status.get("ready", False):
        return False, (
            f"Schema validation status for {schema_path} is not ready. "
            f"Fix schema validation errors and rerun schema_validation.py."
        )

    for item in status.get("tracked_files", []):
        tracked_path = _safe_resolve(Path(item["path"]))
        if not tracked_path.exists():
            return False, (
                f"Schema validation status is stale because {tracked_path} is missing. "
                f"Rerun schema_validation.py."
            )
        if tracked_path.stat().st_mtime_ns != item.get("mtime_ns"):
            return False, (
                f"Schema validation status is stale because {tracked_path} changed. "
                f"Rerun schema_validation.py."
            )

    return True, ""


class SchemaLoader:
    """Load JSON schemas, resolve references, and expand dependencies."""

    def __init__(self, base_path: str | Path | None = None):
        if base_path is None:
            base_path = _safe_resolve(Path(__file__).parent.parent / "config" / "schemas")
        self.base_path = _safe_resolve(Path(base_path))
        self.main_schema_path: Path | None = None
        self.loaded_schemas: Dict[str, Dict[str, Any]] = {}

    def set_main_schema_path(self, schema_file: str | Path) -> Path:
        """Set the main schema path so relative references resolve correctly."""
        self.main_schema_path = _safe_resolve(Path(schema_file))
        if self.main_schema_path.parent.exists():
            self.base_path = self.main_schema_path.parent
        return self.main_schema_path

    def load_json_file(self, path: str | Path) -> Dict[str, Any]:
        """Load and return a JSON document from disk."""
        resolved = _safe_resolve(Path(path))
        with resolved.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _resolve_reference_path(self, ref_path: str | Path) -> Path:
        """Resolve a schema reference path using several fallback strategies."""
        candidate = Path(ref_path)
        if candidate.is_absolute():
            return _safe_resolve(candidate)

        search_paths: List[Path] = []
        if self.main_schema_path is not None:
            search_paths.append(_safe_resolve(self.main_schema_path.parent / candidate))
        search_paths.append(_safe_resolve(self.base_path / candidate))

        candidate_name = candidate.name
        search_paths.append(_safe_resolve(self.base_path / candidate_name))
        if self.main_schema_path is not None:
            search_paths.append(_safe_resolve(self.main_schema_path.parent / candidate_name))

        cwd = _safe_cwd()
        search_paths.append(_safe_resolve(cwd / candidate))
        search_paths.append(_safe_resolve(cwd / candidate_name))

        for resolved in search_paths:
            if resolved.exists():
                return resolved

        return _safe_resolve(self.base_path / candidate)

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
        cache_key = str(_safe_resolve(Path(schema_path))) if Path(schema_path).is_absolute() else str(schema_path)
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
        self.schema_file = _safe_resolve(Path(schema_file))
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
        validated_paths: Set[Path] = set()
        self._validate_schema_document(self.schema_file, main_schema, results, validated_paths)
        dependency_cycle = self._detect_circular_dependencies(
            current_path=self.schema_file,
            current_schema=main_schema,
            visited_paths=visited_paths,
            recursion_stack=[],
            results=results,
            validated_paths=validated_paths,
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
        validated_paths: Set[Path],
    ) -> List[Path]:
        """Walk nested schema references and return one cycle path if found."""
        resolved_current_path = _safe_resolve(current_path)
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
            self._validate_schema_document(resolved_path, ref_schema, results, validated_paths)

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
                    validated_paths=validated_paths,
                )
                if cycle:
                    return cycle

        return []

    def _validate_schema_document(
        self,
        schema_path: Path,
        schema_data: Dict[str, Any],
        results: Dict[str, Any],
        validated_paths: Set[Path],
    ) -> None:
        """Validate field definitions for one schema document."""
        resolved_schema_path = _safe_resolve(schema_path)
        if resolved_schema_path in validated_paths:
            return
        validated_paths.add(resolved_schema_path)

        field_definitions = schema_data.get("field_definitions", {})
        if not isinstance(field_definitions, dict) or not field_definitions:
            return

        data_section_name = schema_data.get("data_section")
        data_item_type = schema_data.get("data_item_type", "object")
        records = None
        if isinstance(data_section_name, str):
            records = schema_data.get(data_section_name)
        if records is None:
            records = self._find_record_section(schema_data)

        if not isinstance(records, list):
            results["errors"].append(
                f"Schema field_definitions validation failed for {resolved_schema_path}: record section is missing or not a list"
            )
            return

        if data_item_type == "scalar":
            self._validate_scalar_record_section(
                schema_path=resolved_schema_path,
                records=records,
                field_definitions=field_definitions,
                results=results,
            )
            return

        unique_trackers: Dict[str, Dict[str, int]] = {}
        global_item_trackers: Dict[str, Dict[str, int]] = {}

        for field_name, field_def in field_definitions.items():
            validation = field_def.get("validation", {}) if isinstance(field_def, dict) else {}
            if validation.get("unique"):
                unique_trackers[field_name] = {}
            if validation.get("global_unique_items"):
                global_item_trackers[field_name] = {}

        for index, record in enumerate(records):
            if not isinstance(record, dict):
                results["errors"].append(
                    f"Schema field_definitions validation failed for {resolved_schema_path}: record at index {index} is not an object"
                )
                continue

            for field_name, field_def in field_definitions.items():
                self._validate_record_field(
                    schema_path=resolved_schema_path,
                    record=record,
                    record_index=index,
                    field_name=field_name,
                    field_def=field_def,
                    results=results,
                    unique_trackers=unique_trackers,
                    global_item_trackers=global_item_trackers,
                )

    def _validate_scalar_record_section(
        self,
        schema_path: Path,
        records: List[Any],
        field_definitions: Dict[str, Any],
        results: Dict[str, Any],
    ) -> None:
        """Validate a list of scalar values using a single field definition."""
        if len(field_definitions) != 1:
            results["errors"].append(
                f"Schema field_definitions validation failed for {schema_path}: scalar data sections require exactly one field definition"
            )
            return

        field_name, field_def = next(iter(field_definitions.items()))
        unique_trackers: Dict[str, Dict[str, int]] = {}
        global_item_trackers: Dict[str, Dict[str, int]] = {}
        validation = field_def.get("validation", {}) if isinstance(field_def, dict) else {}
        if validation.get("unique"):
            unique_trackers[field_name] = {}
        if validation.get("global_unique_items"):
            global_item_trackers[field_name] = {}

        for index, value in enumerate(records):
            self._validate_scalar_value(
                schema_path=schema_path,
                record_index=index,
                field_name=field_name,
                value=value,
                field_def=field_def,
                results=results,
                unique_trackers=unique_trackers,
                global_item_trackers=global_item_trackers,
            )

    def _find_record_section(self, schema_data: Dict[str, Any]) -> List[Dict[str, Any]] | None:
        """Find the most likely top-level record section for field_definitions validation."""
        ignored_keys = {
            "schema_name",
            "type",
            "description",
            "created",
            "version",
            "schema_references",
            "field_definitions",
            "data_section",
        }
        for key, value in schema_data.items():
            if key in ignored_keys:
                continue
            if isinstance(value, list) and (not value or isinstance(value[0], dict)):
                return value
        return None

    def _validate_scalar_value(
        self,
        schema_path: Path,
        record_index: int,
        field_name: str,
        value: Any,
        field_def: Dict[str, Any],
        results: Dict[str, Any],
        unique_trackers: Dict[str, Dict[str, int]],
        global_item_trackers: Dict[str, Dict[str, int]],
    ) -> None:
        """Validate a scalar list item against one field definition."""
        data_type = field_def.get("data_type")
        validation = field_def.get("validation", {})

        if data_type == "string":
            if not isinstance(value, str):
                results["errors"].append(
                    f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must be a string"
                )
                return
            self._validate_scalar_rules(schema_path, record_index, field_name, value, validation, results)
            self._track_unique_scalar(schema_path, record_index, field_name, value, validation, unique_trackers, results)
            return

        if data_type == "numeric":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                results["errors"].append(
                    f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must be numeric"
                )
                return
            self._track_unique_scalar(schema_path, record_index, field_name, str(value), validation, unique_trackers, results)
            return

        if data_type == "boolean":
            if not isinstance(value, bool):
                results["errors"].append(
                    f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must be boolean"
                )
            return

    def _validate_record_field(
        self,
        schema_path: Path,
        record: Dict[str, Any],
        record_index: int,
        field_name: str,
        field_def: Dict[str, Any],
        results: Dict[str, Any],
        unique_trackers: Dict[str, Dict[str, int]],
        global_item_trackers: Dict[str, Dict[str, int]],
    ) -> None:
        """Validate one field in one record against field_definitions."""
        required = bool(field_def.get("required", False))
        value = record.get(field_name)
        if value is None:
            if required:
                results["errors"].append(
                    f"Schema field_definitions validation failed for {schema_path}: record {record_index} missing required field '{field_name}'"
                )
            return

        data_type = field_def.get("data_type")
        validation = field_def.get("validation", {})

        if data_type == "string":
            if not isinstance(value, str):
                results["errors"].append(
                    f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must be a string"
                )
                return
            self._validate_scalar_rules(schema_path, record_index, field_name, value, validation, results)
            self._track_unique_scalar(schema_path, record_index, field_name, value, validation, unique_trackers, results)
            return

        if data_type == "array[string]":
            if not isinstance(value, list):
                results["errors"].append(
                    f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must be a list"
                )
                return
            if any(not isinstance(item, str) for item in value):
                results["errors"].append(
                    f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must contain only strings"
                )
                return
            self._validate_array_rules(
                schema_path,
                record_index,
                field_name,
                value,
                validation,
                global_item_trackers,
                results,
            )
            return

        if data_type == "numeric":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                results["errors"].append(
                    f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must be numeric"
                )
                return
            self._track_unique_scalar(schema_path, record_index, field_name, str(value), validation, unique_trackers, results)
            return

        if data_type == "boolean":
            if not isinstance(value, bool):
                results["errors"].append(
                    f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must be boolean"
                )
            return

    def _validate_scalar_rules(
        self,
        schema_path: Path,
        record_index: int,
        field_name: str,
        value: str,
        validation: Dict[str, Any],
        results: Dict[str, Any],
    ) -> None:
        import re

        min_length = validation.get("min_length")
        max_length = validation.get("max_length")
        pattern = validation.get("pattern")

        if min_length is not None and len(value) < min_length:
            results["errors"].append(
                f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' is shorter than {min_length}"
            )
        if max_length is not None and len(value) > max_length:
            results["errors"].append(
                f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' is longer than {max_length}"
            )
        if pattern and not re.fullmatch(pattern, value):
            results["errors"].append(
                f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' does not match pattern {pattern}"
            )

    def _track_unique_scalar(
        self,
        schema_path: Path,
        record_index: int,
        field_name: str,
        value: str,
        validation: Dict[str, Any],
        unique_trackers: Dict[str, Dict[str, int]],
        results: Dict[str, Any],
    ) -> None:
        if not validation.get("unique"):
            return
        tracker = unique_trackers.setdefault(field_name, {})
        if value in tracker:
            results["errors"].append(
                f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' duplicates record {tracker[value]}"
            )
            return
        tracker[value] = record_index

    def _validate_array_rules(
        self,
        schema_path: Path,
        record_index: int,
        field_name: str,
        value: List[str],
        validation: Dict[str, Any],
        global_item_trackers: Dict[str, Dict[str, int]],
        results: Dict[str, Any],
    ) -> None:
        min_items = validation.get("min_items")
        if min_items is not None and len(value) < min_items:
            results["errors"].append(
                f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' has fewer than {min_items} items"
            )

        if validation.get("unique_items") and len(value) != len(set(value)):
            results["errors"].append(
                f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' contains duplicate items"
            )

        if validation.get("global_unique_items"):
            tracker = global_item_trackers.setdefault(field_name, {})
            for item in value:
                if item in tracker:
                    results["errors"].append(
                        f"Schema field_definitions validation failed for {schema_path}: item '{item}' in field '{field_name}' duplicates record {tracker[item]}"
                    )
                    continue
                tracker[item] = record_index

    def load_main_schema(self) -> Dict[str, Any]:
        """Load the main schema after validation has passed."""
        return self.loader.load_json_file(self.schema_file)

    def load_resolved_schema(self) -> Dict[str, Any]:
        """Load the main schema and resolve all configured dependencies."""
        main_schema = self.load_main_schema()
        return self.loader.resolve_schema_dependencies(main_schema)


def _default_schema_path() -> Path:
    return _safe_resolve(Path(__file__).parent.parent / "config" / "schemas" / "dcc_register_enhanced.json")


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
    status_path = write_validation_status(results)
    logger.info("Wrote schema validation status: %s", status_path)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_report(results))

    return 0 if results.get("ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
