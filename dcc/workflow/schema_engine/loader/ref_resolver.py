"""
Reference resolution engine for JSON schemas.

Supports multiple $ref formats:
- Type 1: schema_references dict (custom DCC)
- Type 2: Custom DCC $ref objects
- Type 3: Standard JSON Schema $ref strings
- Universal: Recursive resolution for all JSON types

Complies with agent_rule.md Section 2 (Schema standards) and Section 4 (Module design).
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Set, List, Optional, Union, Callable
from collections import deque

from ..utils.paths import safe_resolve

# Lazy imports to break circular dependency with initiation_engine
_status_print = None
_debug_print = None
_DEBUG_LEVEL = 1

def _get_debug_level() -> int:
    global _DEBUG_LEVEL
    try:
        from core_engine.logging import DEBUG_LEVEL
        _DEBUG_LEVEL = DEBUG_LEVEL
    except ImportError:
        pass
    return _DEBUG_LEVEL

def status_print(msg: str) -> None:
    if _get_debug_level() >= 1:
        print(f"STATUS: {msg}")

def debug_print(msg: str, level: int = 1) -> None:
    if _get_debug_level() >= level:
        print(f"DEBUG[{level}]: {msg}")


class SchemaNotRegisteredError(Exception):
    """
    Raised when attempting to load a schema not in project_setup.json catalog.
    
    Complies with agent_rule.md Section 2.3: Use project_setup.json as main entry point.
    All schema files must be referenced in project_setup.json.
    """
    
    def __init__(self, schema_name: str, available_schemas: List[str]):
        """
        Initialize error with schema name and available registered schemas.
        
        Breadcrumb: schema_name → available_schemas → formatted_message
        
        Args:
            schema_name: Name of the unregistered schema attempted to load
            available_schemas: List of schema names registered in project_setup.json
        """
        message = (
            f"Schema '{schema_name}' is not registered in project_setup.json. "
            f"Available schemas: {', '.join(available_schemas)}. "
            f"Add '{schema_name}' to the schema_files array to register it."
        )
        super().__init__(message)
        self.schema_name = schema_name
        self.available_schemas = available_schemas


class RefResolutionError(Exception):
    """Raised when reference resolution fails."""
    
    def __init__(self, ref: Any, reason: str, path: str = ""):
        """
        Initialize resolution error.
        
        Breadcrumb: ref → reason → path → formatted_message
        
        Args:
            ref: The reference that failed to resolve
            reason: Explanation of why resolution failed
            path: JSON path where the reference was found
        """
        path_info = f" at '{path}'" if path else ""
        message = f"Failed to resolve $ref{path_info}: {ref}. Reason: {reason}"
        super().__init__(message)
        self.ref = ref
        self.path = path
        self.reason = reason


from .schema_cache import SchemaCache

class RefResolver:
    """
    Universal reference resolver for JSON schemas.
    
    This class implements the Unified Schema Registry pattern (agent_rule.md Section 2.4).
    It translates permanent internal URIs to physical file system paths and performs
    deep, recursive resolution of all standard and custom DCC reference types.
    
    Capabilities:
    - URI-to-Path mapping via $id registry.
    - String-based refs: "#/definitions/Type" or "file.json#/field".
    - Object-based refs: {"schema": "name", "code": "X", "field": "Y"}.
    - Recursive resolution of nested structures (objects and arrays).
    - Multi-directory search for schema fragments.
    - Integrated multi-level caching (L1/L2).
    
    Complies with agent_rule.md Section 4: Module design for functions and classes.
    """
    
    def __init__(
        self,
        project_setup_path: Path,
        schema_directories: List[Path],
        cache: Optional[SchemaCache] = None
    ):
        """
        Initialize resolver with mandatory project_setup.json and schema directories.
        
        Breadcrumb: project_setup_path → schema_directories → cache → loaded_setup
        
        Args:
            project_setup_path: Path to project_setup.json (mandatory root)
            schema_directories: List of directories to search for schemas
            cache: Optional SchemaCache instance for loaded schemas
            
        Raises:
            FileNotFoundError: If project_setup_path does not exist
            SchemaNotRegisteredError: If project_setup.json is malformed
            
        Complies with agent_rule.md Section 2.3: project_setup.json as main entry point.
        """
        # Breadcrumb: Validate and load project_setup.json
        self.project_setup_path = safe_resolve(project_setup_path)
        if not self.project_setup_path.exists():
            raise FileNotFoundError(
                f"project_setup.json not found at {self.project_setup_path}. "
                "This file is mandatory as the main schema entry point."
            )
        
        # Breadcrumb: Load and parse project_setup.json
        with self.project_setup_path.open('r', encoding='utf-8') as f:
            self.project_setup = json.load(f)
        
        # Breadcrumb: Extract registered schema catalog
        self.schema_directories = [safe_resolve(d) for d in schema_directories]
        self.registered_schemas = self._extract_registered_schemas()
        self.cache = cache or SchemaCache()
        self._resolution_stack: Set[str] = set()  # For circular reference detection
        
        # Breadcrumb: Build URI-to-file registry for $id resolution
        self.uri_registry = self._build_uri_registry()
        
        debug_print(
            f"RefResolver initialized with {len(self.registered_schemas)} registered schemas, "
            f"{len(self.uri_registry)} URI mappings",
            level=2
        )
    
    def _extract_registered_schemas(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract schema catalog from project_setup.json, including discovery_rules.
        
        Handles:
        1. Instance files: {"schema_files": [{"filename": "..."}]}
        2. Schema files: {"properties": {"schema_files": {"default": [{"filename": "..."}]}}}
        3. Discovery rules: {"discovery_rules": [{"pattern": "*.json", "directory": "...", ...}]}
        
        Breadcrumb: project_setup → schema_files → discovery_rules → normalized_registry
        
        Returns:
            Dict mapping schema name (stem) to registration metadata
            
        Complies with agent_rule.md Section 2.3: All schema files must be referenced
        in project_setup.json (manually or via discovery rules).
        """
        registry = {}
        
        # Breadcrumb: Process explicit schema_files
        schema_files = self.project_setup.get("schema_files", [])
        
        # Case 2: Schema with default values (schema file)
        if not schema_files and "$schema" in self.project_setup:
            properties = self.project_setup.get("properties", {})
            schema_files_def = properties.get("schema_files", {})
            schema_files = schema_files_def.get("default", [])
        
        for entry in schema_files:
            filename = entry.get("filename", "")
            if filename:
                schema_name = Path(filename).stem
                registry[schema_name] = {
                    "filename": filename,
                    "required": entry.get("required", False),
                    "description": entry.get("description", ""),
                    "registered": True,
                    "source": "explicit"
                }
        
        # Breadcrumb: Process discovery_rules (agent_rule.md Section 2.8)
        discovery_rules = self.project_setup.get("discovery_rules", [])
        
        project_root = self.project_setup_path.parent.parent.parent # Root of DCC
        
        for rule in discovery_rules:
            pattern = rule.get("pattern")
            directory_rel = rule.get("directory", ".")
            recursive = rule.get("recursive", False)
            auto_register = rule.get("auto_register", True)
            exclude_patterns = rule.get("exclude_patterns", [])
            
            if not pattern or not auto_register:
                continue
                
            # Breadcrumb: Locate discovery directory
            # Directory is relative to project root or absolute
            search_dir = safe_resolve(project_root / directory_rel)
            
            if not search_dir.exists():
                debug_print(f"Discovery directory not found: {search_dir}", level=2)
                continue
            
            # Add to schema_directories if not already present
            if search_dir not in self.schema_directories:
                self.schema_directories.append(search_dir)
                
            # Breadcrumb: Scan for matching files
            glob_pattern = f"**/{pattern}" if recursive else pattern
            for schema_file in search_dir.glob(glob_pattern):
                # Check exclude patterns
                is_excluded = False
                for exclude in exclude_patterns:
                    if schema_file.match(exclude) or any(schema_file.match(p) for p in exclude_patterns):
                        is_excluded = True
                        break
                
                if is_excluded:
                    continue
                    
                schema_name = schema_file.stem
                if schema_name not in registry:
                    registry[schema_name] = {
                        "filename": schema_file.name,
                        "path": str(schema_file),
                        "required": False,
                        "description": rule.get("category", "discovered"),
                        "registered": True,
                        "source": "discovery"
                    }
                    debug_print(f"Auto-registered schema: {schema_name} (via {pattern})", level=3)
        
        return registry
    
    def _build_uri_registry(self) -> Dict[str, Path]:
        """
        Build URI-to-file registry by scanning schema directories for $id declarations.
        
        Breadcrumb: schema_directories → scan_files → extract_$id → uri_registry
        
        Returns:
            Dict mapping $id URI (e.g., https://dcc-pipeline.internal/schemas/name)
            to resolved file path
            
        Complies with agent_rule.md Section 2.4: Unified Schema Registry (URIs).
        """
        uri_registry: Dict[str, Path] = {}
        
        for directory in self.schema_directories:
            if not directory.exists():
                continue
                
            # Scan all JSON files in directory
            for schema_file in directory.glob("*.json"):
                try:
                    with schema_file.open('r', encoding='utf-8') as f:
                        schema_data = json.load(f)
                    
                    # Extract $id if present
                    schema_id = schema_data.get("$id")
                    if schema_id:
                        uri_registry[schema_id] = safe_resolve(schema_file)
                        debug_print(
                            f"Registered URI '{schema_id}' → {schema_file.name}",
                            level=3
                        )
                        
                except (json.JSONDecodeError, IOError) as exc:
                    debug_print(
                        f"Skipping {schema_file.name}: {exc}",
                        level=3
                    )
                    continue
        
        return uri_registry
    
    def _resolve_uri_to_file(self, uri: str) -> Optional[Path]:
        """
        Resolve a schema URI to its file path.
        
        Breadcrumb: uri → uri_registry → file_path
        
        Args:
            uri: Schema $id URI (e.g., https://dcc-pipeline.internal/schemas/name)
            
        Returns:
            Resolved file path or None if URI not registered
            
        Complies with agent_rule.md Section 2.4: URI-based schema resolution.
        """
        return self.uri_registry.get(uri)
    
    def validate_registration(self, schema_name: str) -> None:
        """
        Validate that a schema is registered in project_setup.json.
        
        Breadcrumb: schema_name → registered_schemas → validation_result
        
        Args:
            schema_name: Name of schema to validate
            
        Raises:
            SchemaNotRegisteredError: If schema not in registry
            
        Complies with agent_rule.md Section 2.3: Strict registration enforcement.
        """
        if schema_name not in self.registered_schemas:
            available = list(self.registered_schemas.keys())
            raise SchemaNotRegisteredError(schema_name, available)
        
        debug_print(f"Schema '{schema_name}' is registered", level=2)
    
    def resolve(
        self,
        value: Any,
        current_schema: Dict[str, Any],
        path: str = "",
        max_depth: int = 100
    ) -> Any:
        """
        Universal JSON value resolver - handles ALL JSON types.
        
        Breadcrumb: value → type_check → resolution_strategy → resolved_value
        
        Supports per agent_rule.md Section 2.4:
        - Simple strings: returned as-is
        - Nested objects: recursively resolved
        - Recursive objects: cycle detection via _resolution_stack
        - Arrays: each element recursively resolved
        - Deeply nested: full depth traversal with path tracking
        - Mixed types: $ref fields resolved, others preserved
        
        Args:
            value: Any JSON value (primitive, dict, list)
            current_schema: The schema currently being processed
            path: Current JSON path for error reporting
            max_depth: Maximum recursion depth to prevent infinite loops
            
        Returns:
            Resolved value with all $refs expanded
            
        Raises:
            RefResolutionError: If resolution fails
            RecursionError: If max_depth exceeded
        """
        # Breadcrumb: Depth limit check
        if len(self._resolution_stack) > max_depth:
            raise RecursionError(
                f"Maximum resolution depth ({max_depth}) exceeded at '{path}'. "
                "Possible circular reference."
            )
        
        # Breadcrumb: Primitive types - return as-is (agent_rule.md: simple strings)
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        
        # Breadcrumb: List/Array handling - recurse into each element
        if isinstance(value, list):
            return [
                self.resolve(item, current_schema, f"{path}[{i}]", max_depth)
                for i, item in enumerate(value)
            ]
        
        # Breadcrumb: Dict/Object handling - check for $ref
        if isinstance(value, dict):
            # Breadcrumb: Direct $ref object - resolve it
            if "$ref" in value:
                ref = value["$ref"]
                resolved = self._resolve_ref_object(ref, current_schema, path)
                # Breadcrumb: Recursively resolve the result (may contain more $refs)
                return self.resolve(resolved, current_schema, path, max_depth)
            
            # Breadcrumb: Regular dict - recurse into each value
            return {
                key: self.resolve(val, current_schema, f"{path}.{key}", max_depth)
                for key, val in value.items()
            }
        
        # Breadcrumb: Unknown type - return as-is
        return value
    
    def _resolve_ref_object(
        self,
        ref: Any,
        current_schema: Dict[str, Any],
        path: str
    ) -> Any:
        """
        Resolve a $ref value based on its type.
        
        Breadcrumb: ref → type_detection → resolver_dispatch → result
        
        Args:
            ref: The $ref value (string or dict)
            current_schema: Current schema for context
            path: JSON path for error reporting
            
        Returns:
            Resolved reference value
            
        Raises:
            RefResolutionError: If ref type is unsupported or resolution fails
        """
        # Breadcrumb: String reference (standard JSON Schema or internal)
        if isinstance(ref, str):
            return self._resolve_string_ref(ref, current_schema, path)
        
        # Breadcrumb: Object reference (custom DCC format)
        if isinstance(ref, dict):
            return self._resolve_dcc_ref_object(ref, current_schema, path)
        
        # Breadcrumb: Unsupported ref type
        raise RefResolutionError(
            ref,
            f"Unsupported $ref type: {type(ref).__name__}. "
            "Expected string or dict.",
            path
        )
    
    def _resolve_string_ref(
        self,
        ref_path: str,
        current_schema: Dict[str, Any],
        path: str
    ) -> Any:
        """
        Resolve a string $ref path.
        
        Breadcrumb: ref_path → pattern_match → resolution → result
        
        Supports:
        - Internal refs: "#/definitions/Type" or "#/properties/field"
        - External refs: "schema.json#/field" (relative or absolute)
        
        Args:
            ref_path: String reference path
            current_schema: Current schema for internal refs
            path: JSON path for error reporting
            
        Returns:
            Resolved reference value
            
        Raises:
            RefResolutionError: If path cannot be resolved
        """
        # Breadcrumb: Internal reference - within current schema
        if ref_path.startswith("#"):
            return self._resolve_internal_ref(ref_path, current_schema, path)
        
        # Breadcrumb: External reference - load other schema
        return self._resolve_external_ref(ref_path, path)
    
    def _resolve_internal_ref(
        self,
        ref_path: str,
        schema: Dict[str, Any],
        path: str
    ) -> Any:
        """
        Resolve an internal #/path/to/field reference.
        
        Breadcrumb: ref_path → strip_hash → path_segments → traverse → value
        
        Args:
            ref_path: Internal reference like "#/definitions/Type" or "#/properties/field"
            schema: Schema dict to traverse
            path: JSON path for error reporting
            
        Returns:
            Value at the referenced path
            
        Raises:
            RefResolutionError: If path doesn't exist in schema
        """
        # Breadcrumb: Remove leading # and split into segments
        clean_path = ref_path.lstrip("#").lstrip("/")
        segments = clean_path.split("/") if clean_path else []
        
        # Breadcrumb: Traverse schema following path segments
        current = schema
        for segment in segments:
            if isinstance(current, dict) and segment in current:
                current = current[segment]
            else:
                raise RefResolutionError(
                    ref_path,
                    f"Path segment '{segment}' not found in schema",
                    path
                )
        
        debug_print(f"Resolved internal ref '{ref_path}'", level=2)
        return current
    
    def _resolve_external_ref(
        self,
        ref_path: str,
        path: str
    ) -> Any:
        """
        Resolve an external file reference.
        
        Breadcrumb: ref_path → uri_check|file_check → load → resolve_pointer
        
        Supports:
        - URI references: https://dcc-pipeline.internal/schemas/name#/pointer
        - File references: schema.json#/definitions/Type
        
        Args:
            ref_path: External ref like "schema.json#/definitions/Type" 
                      or "https://.../schemas/name#/pointer"
            path: JSON path for error reporting
            
        Returns:
            Resolved value from external schema
            
        Raises:
            RefResolutionError: If file not found or path invalid
            
        Complies with agent_rule.md Section 2.4: URI-based schema resolution.
        """
        # Breadcrumb: Split file path and JSON pointer
        if "#" in ref_path:
            file_part, pointer = ref_path.split("#", 1)
            pointer = pointer.lstrip("/")
        else:
            file_part = ref_path
            pointer = ""
        
        # Breadcrumb: Check if file_part is a URI (starts with http/https)
        if file_part.startswith(("http://", "https://")):
            # Breadcrumb: Resolve URI to file path
            schema_path = self._resolve_uri_to_file(file_part)
            if schema_path is None:
                raise RefResolutionError(
                    ref_path,
                    f"URI '{file_part}' not found in registry. "
                    f"Ensure the schema has a matching $id.",
                    path
                )
            schema_name = schema_path.stem
            # Breadcrumb: Validate registration
            self.validate_registration(schema_name)
        else:
            # Breadcrumb: Traditional file-based reference
            schema_name = Path(file_part).stem
            self.validate_registration(schema_name)
            schema_path = None  # Will be resolved by _find_schema_file
        
        # Breadcrumb: Load schema (with caching)
        target_schema = self.cache.get(schema_name, schema_path)
        if target_schema is None:
            if schema_path is None:
                schema_path = self._find_schema_file(file_part)
            with schema_path.open('r', encoding='utf-8') as f:
                target_schema = json.load(f)
            self.cache.set(schema_name, target_schema, schema_path)
        
        # Breadcrumb: If no pointer, return entire schema
        if not pointer:
            return target_schema
        
        # Breadcrumb: Resolve JSON pointer within target schema
        return self._resolve_internal_ref(f"#/{pointer}", target_schema, path)
    
    def _resolve_dcc_ref_object(
        self,
        ref_obj: Dict[str, Any],
        current_schema: Dict[str, Any],
        path: str
    ) -> Any:
        """
        Resolve a custom DCC $ref object.
        
        Breadcrumb: ref_obj → extract_keys → locate_schema → query_data → value
        
        Format per Phase A analysis:
        {
            "schema": "approval_code_schema",
            "code": "PEN",
            "field": "status",
            "description": "..."
        }
        
        Args:
            ref_obj: DCC ref dict with schema, code, field keys
            current_schema: Current schema (for context)
            path: JSON path for error reporting
            
        Returns:
            Resolved field value from target schema
            
        Raises:
            RefResolutionError: If schema or code not found
        """
        # Breadcrumb: Extract ref parameters
        schema_name = ref_obj.get("schema")
        code = ref_obj.get("code")
        field = ref_obj.get("field")
        
        if not schema_name or not code or not field:
            raise RefResolutionError(
                ref_obj,
                "DCC $ref must contain 'schema', 'code', and 'field' keys",
                path
            )
        
        # Breadcrumb: Validate registration
        self.validate_registration(schema_name)
        
        # Breadcrumb: Load target schema
        target_schema = self.cache.get(schema_name)
        if target_schema is None:
            schema_path = self._find_schema_file(f"{schema_name}.json")
            with schema_path.open('r', encoding='utf-8') as f:
                target_schema = json.load(f)
            self.cache.set(schema_name, target_schema, schema_path)
        
        # Breadcrumb: Query target schema by code
        # Assumes schema has array of objects with 'code' field
        entries = target_schema.get("entries", target_schema.get("codes", []))
        if not isinstance(entries, list):
            # Try to find array in schema values
            for val in target_schema.values():
                if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                    entries = val
                    break
        
        # Breadcrumb: Find entry matching code
        target_entry = None
        for entry in entries:
            if isinstance(entry, dict) and entry.get("code") == code:
                target_entry = entry
                break
        
        if not target_entry:
            raise RefResolutionError(
                ref_obj,
                f"Code '{code}' not found in schema '{schema_name}'",
                path
            )
        
        # Breadcrumb: Extract requested field
        if field not in target_entry:
            raise RefResolutionError(
                ref_obj,
                f"Field '{field}' not found in entry with code '{code}'",
                path
            )
        
        debug_print(
            f"Resolved DCC ref: {schema_name}[code={code}].{field}",
            level=2
        )
        return target_entry[field]
    
    def _find_schema_file(self, filename: str) -> Path:
        """
        Find a schema file in registered directories.
        
        Breadcrumb: filename → search_directories → first_match → resolved_path
        
        Args:
            filename: Schema filename to find
            
        Returns:
            Resolved path to schema file
            
        Raises:
            FileNotFoundError: If schema not found in any directory
        """
        # Breadcrumb: Search all registered directories
        for directory in self.schema_directories:
            candidate = directory / filename
            if candidate.exists():
                return safe_resolve(candidate)
        
        # Breadcrumb: Schema not found
        search_paths = [str(d / filename) for d in self.schema_directories]
        raise FileNotFoundError(
            f"Schema file '{filename}' not found. Searched:\n" +
            "\n".join(f"  - {p}" for p in search_paths)
        )
    
    def resolve_schema_references(
        self,
        schema: Dict[str, Any],
        max_depth: int = 100
    ) -> Dict[str, Any]:
        """
        Resolve all $refs within schema_references block.
        
        Breadcrumb: schema → schema_references → iterate → resolve_each → merged_dict
        
        Handles Type 1 refs per Phase A analysis:
        "schema_references": {
            "project_schema": "../config/schemas/project_schema.json",
            ...
        }
        
        Args:
            schema: Schema containing schema_references dict
            max_depth: Max recursion depth for nested refs
            
        Returns:
            Dict with all referenced schemas loaded and merged
            
        Raises:
            SchemaNotRegisteredError: If referenced schema not registered
            RefResolutionError: If resolution fails
        """
        # Breadcrumb: Check for schema_references
        schema_refs = schema.get("schema_references", {})
        if not schema_refs:
            return {}
        
        resolved = {}
        
        # Breadcrumb: Resolve each reference
        for ref_name, ref_path in schema_refs.items():
            schema_name = Path(ref_path).stem
            
            # Breadcrumb: Validate registration
            self.validate_registration(schema_name)
            
            # Breadcrumb: Load referenced schema
            schema_data = self.cache.get(schema_name)
            if schema_data is None:
                full_path = self._find_schema_file(f"{schema_name}.json")
                with full_path.open('r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                self.cache.set(schema_name, schema_data, full_path)
            
            resolved[ref_name] = schema_data
            debug_print(f"Resolved schema_reference: {ref_name}", level=2)
        
        return resolved
