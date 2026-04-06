"""
Schema validation and circular dependency detection.
Extracted from schema_validation.py SchemaValidator class.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Set

from dcc.workflow.schema_engine.engine.utils.paths import safe_resolve
from dcc.workflow.schema_engine.engine.loader.schema_loader import SchemaLoader
from dcc.workflow.schema_engine.engine.validator.fields import (
    validate_schema_document,
    find_record_section,
)

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validate a main schema file and its external references."""

    def __init__(self, schema_file: str | Path):
        self.schema_file = safe_resolve(Path(schema_file))
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
        validate_schema_document(self.schema_file, main_schema, results, validated_paths)
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
        resolved_current_path = safe_resolve(current_path)
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
            validate_schema_document(resolved_path, ref_schema, results, validated_paths)

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

    def load_main_schema(self) -> Dict[str, Any]:
        """Load the main schema after validation has passed."""
        return self.loader.load_json_file(self.schema_file)

    def load_resolved_schema(self) -> Dict[str, Any]:
        """Load the main schema and resolve all configured dependencies."""
        main_schema = self.load_main_schema()
        return self.loader.resolve_schema_dependencies(main_schema)
