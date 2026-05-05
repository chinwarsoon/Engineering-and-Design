"""
Schema validation and circular dependency detection.
Extracted from schema_validation.py SchemaValidator class.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Set

from ..utils.paths import safe_resolve
from ..loader.schema_loader import (
    SchemaLoader,
)
from .fields import (
    validate_schema_document,
    find_record_section,
)
from core_engine.schema_utils import resolve_schema_root

logger = logging.getLogger(__name__)


from core_engine.context.context_pipeline import PipelineContext
from core_engine.base import BaseEngine

class SchemaValidator(BaseEngine):
    """Validate a main schema file and its external references."""

    def __init__(self, context: PipelineContext):
        super().__init__(context)
        self.schema_file = safe_resolve(Path(self.context.paths.schema_path))
        self.loader = SchemaLoader()
        self.loader.set_main_schema_path(self.schema_file)

    def run(self) -> Dict[str, Any]:
        """Execute schema validation through the uniform engine interface."""
        return self.validate()

    def validate(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "main_schema_path": str(self.schema_file),
            "column_count": 0,
            "references": [],
            "dependency_cycle": [],
            "errors": [],
            "ready": True,
        }

        if not self.schema_file.is_file():
            error_msg = f"Main schema file not found: {self.schema_file}"
            results["errors"].append(error_msg)
            results["ready"] = False
            # Record error in context
            if hasattr(self.context, 'add_system_error'):
                self.context.add_system_error(
                    code="S-F-S-0204",
                    message=error_msg,
                    details=str(self.schema_file),
                    engine="schema_engine",
                    phase="schema_validation",
                    severity="critical",
                    fatal=True
                )
            return results

        try:
            main_schema = self.loader.load_json_file(self.schema_file)
        except json.JSONDecodeError as exc:
            error_msg = f"Invalid JSON in main schema {self.schema_file}: {exc}"
            results["errors"].append(error_msg)
            results["ready"] = False
            # Record error in context
            if hasattr(self.context, 'capture_exception'):
                self.context.capture_exception(
                    code="S-C-S-0302",
                    exception=exc,
                    engine="schema_engine",
                    phase="schema_validation"
                )
            return results
        except Exception as exc:
            error_msg = f"Error loading main schema {self.schema_file}: {exc}"
            results["errors"].append(error_msg)
            results["ready"] = False
            # Record error in context
            if hasattr(self.context, 'capture_exception'):
                self.context.capture_exception(
                    code="S-R-S-0404",
                    exception=exc,
                    engine="schema_engine",
                    phase="schema_validation"
                )
            return results

        # Use centralized schema root resolution
        schema_root = resolve_schema_root(main_schema)
        columns = schema_root.get("columns", {})
        
        if not isinstance(columns, dict) or not columns:
            error_msg = "Main schema is missing a valid 'columns' object"
            results["errors"].append(error_msg)
            # Record error in context
            if hasattr(self.context, 'add_system_error'):
                self.context.add_system_error(
                    code="S-C-S-0301",
                    message=error_msg,
                    details="Schema must contain a 'columns' object with column definitions",
                    engine="schema_engine",
                    phase="schema_validation",
                    severity="critical",
                    fatal=True
                )
        else:
            results["column_count"] = len(columns)

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
            error_msg = f"Circular schema dependency detected: {cycle_text}"
            results["errors"].append(error_msg)
            # Record error in context
            if hasattr(self.context, 'add_system_error'):
                self.context.add_system_error(
                    code="S-C-S-0304",
                    message=error_msg,
                    details=f"Dependency cycle: {cycle_text}",
                    engine="schema_engine",
                    phase="schema_validation",
                    severity="critical",
                    fatal=True
                )

        results["ready"] = not results["errors"]
        return results

    def build_blueprint(self, context: PipelineContext) -> None:
        """
        Populate the PipelineContext Blueprint from the resolved schema.
        Enforces SSOT by delegating this logic to the schema engine.
        """
        resolved_schema = self.load_resolved_schema()
        context.state.resolved_schema = resolved_schema
        
        # Resolve schema root
        schema_root = resolve_schema_root(resolved_schema)
        
        context.blueprint.columns = schema_root.get("columns", {})
        context.blueprint.validation_rules = resolved_schema.get("parameters", {})
        
        # Pre-calculate phase map for efficient processing
        column_sequence = schema_root.get("column_sequence", [])
        phase_map = {"P1": [], "P2": [], "P2.5": [], "P3": []}
        for col_name in column_sequence:
            if col_name in context.blueprint.columns:
                phase = context.blueprint.columns[col_name].get("processing_phase", "P3")
                if phase in phase_map:
                    phase_map[phase].append(col_name)
        context.blueprint.phase_map = phase_map
        
        # Load Data Error Catalog into Blueprint
        error_config_path = context.paths.schema_paths.data_error_config
        if error_config_path.exists():
            try:
                with open(error_config_path, "r", encoding="utf-8") as f:
                    context.blueprint.error_catalog = json.load(f).get("data_logic_errors", {})
            except Exception as e:
                from initiation_engine.error_handling import get_system_error_message
                msg = get_system_error_message("S-C-S-0311").format(detail=str(e))
                context.add_system_error(
                    code="S-C-S-0311",
                    message=msg,
                    details=str(e),
                    engine="schema_engine",
                    phase="step2_schema_validation",
                    severity="medium",
                    fatal=False
                )

    def get_total_columns(self, results: Dict[str, Any]) -> int:
        """Return the total number of columns in the main schema."""
        return results.get("column_count", 0)

    def get_total_references(self, results: Dict[str, Any]) -> int:
        """Return the total number of unique schema references found."""
        return len(results.get("references", []))

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
            # Skip schema definition metadata (type, additionalProperties, properties, etc.)
            # These are keys that define the schema structure, not actual schema references
            if ref_name in ("type", "additionalProperties", "properties", "description", "title"):
                continue
            # Skip non-string ref_paths (e.g., complex schema definitions)
            if not isinstance(ref_path, str):
                continue
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
        """
        Load and resolve the main schema.

        For new-architecture schemas (URI $ref, top-level 'columns'):
          - Loads each fragment schema referenced via URI $ref
          - Normalizes the result to the canonical shape expected by all engines
        For legacy schemas (schema_references dict):
          - Falls back to resolve_schema_dependencies()
        """
        main_schema = self.load_main_schema()
        # New architecture: top-level 'columns' key present
        if "columns" in main_schema:
            return self._load_resolved_schema_v2(main_schema)
        # Legacy architecture: schema_references dict
        return self.loader.resolve_schema_dependencies(main_schema)

    def _load_resolved_schema_v2(self, main_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load fragment schemas referenced via URI $ref and normalize to engine-expected shape.

        Breadcrumb: main_schema → resolve URI $refs → normalize → resolved_schema
        """
        schema_dir = self.schema_file.parent
        resolved = main_schema.copy()

        # URI stem → filename mapping for fragment schemas
        uri_stem_map = {
            "department_schema": "department_schema.json",
            "discipline_schema": "discipline_schema.json",
            "facility_schema": "facility_schema.json",
            "document_type_schema": "document_type_schema.json",
            "project_code_schema": "project_code_schema.json",
            "approval_code_schema": "approval_code_schema.json",
            "global_parameters": "global_parameters.json",
        }

        # Top-level keys that hold URI $ref objects — resolve each
        ref_keys = [
            "departments", "disciplines", "facilities",
            "document_types", "projects", "approval_codes",
            "parameters",
        ]
        for key in ref_keys:
            value = main_schema.get(key)
            if isinstance(value, dict) and "$ref" in value:
                ref_uri = value["$ref"]
                # Extract stem from URI (before any # fragment)
                uri_base = ref_uri.split("#")[0]
                fragment = ref_uri.split("#")[1].lstrip("/") if "#" in ref_uri else ""
                stem = uri_base.rstrip("/").split("/")[-1].replace("-", "_")
                filename = uri_stem_map.get(stem, f"{stem}.json")
                frag_path = schema_dir / filename
                if frag_path.is_file():
                    try:
                        frag_data = self.loader.load_json_file(frag_path)
                        # Resolve fragment pointer if present
                        if fragment:
                            for seg in fragment.split("/"):
                                if seg:
                                    frag_data = frag_data.get(seg, frag_data)
                        resolved[key] = frag_data
                    except Exception:
                        pass  # Keep original $ref object on failure

        return self._normalize_resolved_schema(resolved)

    @staticmethod
    def _normalize_resolved_schema(raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize a loaded dcc_register_config schema to the canonical shape
        expected by CalculationEngine, SchemaProcessor, and ColumnMapperEngine.

        Canonical shape:
          columns          - dict of column definitions (47 cols)
          column_sequence  - list of ordered column names
          column_groups    - dict of column group lists
          parameters       - flattened global parameters dict
          approval_codes   - list of approval code entries
          departments      - list of department entries
          disciplines      - list of discipline entries
          facilities       - list of facility entries
          document_types   - list of document type entries
          projects         - list of project entries
        """
        normalized = raw.copy()

        # Handle 'parameters' key - could be a direct dict, a list, or a resolved schema object
        params = normalized.get("parameters")
        
        # Case 1: parameters is a resolved schema from global_parameters.json (has a 'parameters' list)
        if isinstance(params, dict) and "parameters" in params and isinstance(params["parameters"], list) and params["parameters"]:
            normalized["parameters"] = params["parameters"][0]
        # Case 2: parameters is already a list (flatten it)
        elif isinstance(params, list) and params:
            normalized["parameters"] = params[0]
        # Case 3: parameters is missing or is just a $ref, fallback to global_parameters
        elif not params or (isinstance(params, dict) and "$ref" in params):
            gp = raw.get("global_parameters", [])
            if isinstance(gp, list) and gp:
                normalized["parameters"] = gp[0]
            elif isinstance(gp, dict):
                normalized["parameters"] = gp

        return normalized
