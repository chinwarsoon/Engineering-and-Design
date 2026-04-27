"""
Field-level schema validation logic.
Extracted from schema_validation.py field validation methods.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Set

from ..utils.paths import safe_resolve

# Lazy import to break circular dependency with initiation_engine
_status_print = None

def status_print(msg: str, min_level: int = 1) -> None:
    """Print status message (lazy import)."""
    global _status_print
    if _status_print is None:
        from utility_engine.console import status_print as sp
        _status_print = sp
    _status_print(msg, min_level=min_level)

logger = logging.getLogger(__name__)


def validate_schema_document(
    schema_path: Path,
    schema_data: Dict[str, Any],
    results: Dict[str, Any],
    validated_paths: Set[Path],
) -> None:
    """Validate field definitions for one schema document."""
    resolved_schema_path = safe_resolve(schema_path)
    if resolved_schema_path in validated_paths:
        return
    validated_paths.add(resolved_schema_path)

    status_print(f"Validating field_definitions in schema: {resolved_schema_path}", min_level=3)

    field_definitions = schema_data.get("field_definitions", {})
    if not isinstance(field_definitions, dict) or not field_definitions:
        return
    
    data_section_path = schema_data.get("data_section")
    data_item_type = schema_data.get("data_item_type", "object")
    
    # Resolve the records section (supports dot-notation for nesting)
    records = None
    if isinstance(data_section_path, str):
        records = schema_data
        for part in data_section_path.split('.'):
            if isinstance(records, dict):
                records = records.get(part)
            else:
                records = None
                break
    
    if records is None:
        records = find_record_section(schema_data)

    if records is None or (not isinstance(records, list) and not isinstance(records, dict)):
        results["errors"].append(
            f"Schema field_definitions validation failed for {resolved_schema_path}: record section '{data_section_path}' is missing or invalid type"
        )
        return

    # Convert dictionary values to a list for standardized validation
    if isinstance(records, dict):
        records_to_validate = list(records.values())
    else:
        records_to_validate = records

    if data_item_type == "scalar":
        validate_scalar_record_section(
            schema_path=resolved_schema_path,
            records=records_to_validate,
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

    for index, record in enumerate(records_to_validate):
        if not isinstance(record, dict):
            results["errors"].append(
                f"Schema field_definitions validation failed for {resolved_schema_path}: record at index {index} is not an object"
            )
            continue

        for field_name, field_def in field_definitions.items():
            validate_record_field(
                schema_path=resolved_schema_path,
                record=record,
                record_index=index,
                field_name=field_name,
                field_def=field_def,
                results=results,
                unique_trackers=unique_trackers,
                global_item_trackers=global_item_trackers,
            )


def validate_scalar_record_section(
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
        validate_scalar_value(
            schema_path=schema_path,
            record_index=index,
            field_name=field_name,
            value=value,
            field_def=field_def,
            results=results,
            unique_trackers=unique_trackers,
            global_item_trackers=global_item_trackers,
        )


def find_record_section(schema_data: Dict[str, Any]) -> List[Dict[str, Any]] | None:
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


def validate_scalar_value(
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
        validate_scalar_rules(schema_path, record_index, field_name, value, validation, results)
        track_unique_scalar(schema_path, record_index, field_name, value, validation, unique_trackers, results)
        return

    if data_type == "numeric":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            results["errors"].append(
                f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must be numeric"
            )
            return
        track_unique_scalar(schema_path, record_index, field_name, str(value), validation, unique_trackers, results)
        return

    if data_type == "boolean":
        if not isinstance(value, bool):
            results["errors"].append(
                f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must be boolean"
            )
        return


def validate_record_field(
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
        validate_scalar_rules(schema_path, record_index, field_name, value, validation, results)
        track_unique_scalar(schema_path, record_index, field_name, value, validation, unique_trackers, results)
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
        validate_array_rules(
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
        track_unique_scalar(schema_path, record_index, field_name, str(value), validation, unique_trackers, results)
        return

    if data_type == "boolean":
        if not isinstance(value, bool):
            results["errors"].append(
                f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' must be boolean"
            )
        return


def validate_scalar_rules(
    schema_path: Path,
    record_index: int,
    field_name: str,
    value: str,
    validation: Dict[str, Any],
    results: Dict[str, Any],
) -> None:
    """Validate scalar value against min_length, max_length, and pattern rules."""
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


def track_unique_scalar(
    schema_path: Path,
    record_index: int,
    field_name: str,
    value: str,
    validation: Dict[str, Any],
    unique_trackers: Dict[str, Dict[str, int]],
    results: Dict[str, Any],
) -> None:
    """Track unique scalar values and report duplicates."""
    if not validation.get("unique"):
        return
    tracker = unique_trackers.setdefault(field_name, {})
    if value in tracker:
        results["errors"].append(
            f"Schema field_definitions validation failed for {schema_path}: record {record_index} field '{field_name}' duplicates record {tracker[value]}"
        )
        return
    tracker[value] = record_index


def validate_array_rules(
    schema_path: Path,
    record_index: int,
    field_name: str,
    value: List[str],
    validation: Dict[str, Any],
    global_item_trackers: Dict[str, Dict[str, int]],
    results: Dict[str, Any],
) -> None:
    """Validate array value against min_items, unique_items, and global_unique_items rules."""
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
