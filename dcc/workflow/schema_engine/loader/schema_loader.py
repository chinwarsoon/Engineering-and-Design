"""
Schema loading and dependency resolution.
Extracted from schema_validation.py SchemaLoader class.

Phase E Enhancement: Integrated RefResolver and SchemaDependencyGraph
for recursive loading, strict registration validation, and universal $ref resolution.
"""

import json
from pathlib import Path
from typing import Dict, Any, Set, List, Optional

from ..utils.paths import safe_resolve

# Import RefResolver and SchemaDependencyGraph for enhanced functionality
from .ref_resolver import RefResolver, SchemaNotRegisteredError, RefResolutionError
from .dependency_graph import SchemaDependencyGraph, CircularDependencyError

# Lazy imports to break circular dependency with initiation_engine
# These wrapper functions only import when actually called
_status_print = None
_debug_print = None
_log_error = None

def status_print(msg: str) -> None:
    """Print status message."""
    print(f"STATUS: {msg}")

def debug_print(msg: str, level: int = 1) -> None:
    """Print debug message."""
    print(f"DEBUG[{level}]: {msg}")

def log_error(msg: str, module: str = "", function: str = "", fatal: bool = True):
    """Log error message (lazy import)."""
    global _log_error
    if _log_error is None:
        from initiation_engine import log_error as le
        _log_error = le
    _log_error(msg, module, function, fatal)


from .schema_cache import SchemaCache

class SchemaLoader:
    """
    Primary interface for loading, resolving, and validating JSON schemas.
    
    The SchemaLoader orchestrates the loading pipeline:
    1. Registration Check: Enforces strict cataloging via project_setup.json.
    2. Dependency Analysis: Uses SchemaDependencyGraph to determine loading order.
    3. Multi-Level Caching: Utilizes SchemaCache (L1/L2/L3) to maximize performance.
    4. Universal Resolution: Uses RefResolver for deep, recursive $ref expansion.
    
    Complies with agent_rule.md Section 2.3: project_setup.json as mandatory
    main entry point for strict schema registration.
    """

    def __init__(
        self,
        base_path: str | Path | None = None,
        project_setup_path: str | Path | None = None,
        auto_resolve_refs: bool = True,
        max_recursion_depth: int = 100,
        cache: Optional[SchemaCache] = None
    ):
        """
        Initialize SchemaLoader with optional project_setup.json integration.
        
        Breadcrumb: base_path → project_setup_path → resolver → dependency_graph → initialized
        
        Args:
            base_path: Base directory for schema files (optional if project_setup_path provided)
            project_setup_path: Path to project_setup.json for strict registration (optional)
            auto_resolve_refs: Whether to auto-resolve $refs when loading schemas
            max_recursion_depth: Maximum depth for recursive reference resolution
            cache: Optional SchemaCache instance
            
        Complies with agent_rule.md Section 2.3: Use project_setup.json as main entry point.
        """
        # Breadcrumb: Set base path for schema resolution
        if base_path is None:
            base_path = safe_resolve(Path(__file__).parent.parent.parent / "config" / "schemas")
        self.base_path = safe_resolve(Path(base_path))
        self.main_schema_path: Path | None = None
        
        # Breadcrumb: Initialize Cache
        self.cache = cache or SchemaCache()
        
        # Breadcrumb: Initialize RefResolver and DependencyGraph if project_setup provided
        self._resolver: Optional[RefResolver] = None
        self._dependency_graph: Optional[SchemaDependencyGraph] = None
        self._registered_schemas: Set[str] = set()
        self.auto_resolve_refs = auto_resolve_refs
        self.max_recursion_depth = max_recursion_depth
        
        if project_setup_path is not None:
            self._init_with_project_setup(project_setup_path)
        
        debug_print(f"SchemaLoader initialized (auto_resolve={auto_resolve_refs})", level=2)

    def _init_with_project_setup(self, project_setup_path: str | Path) -> None:
        """
        Initialize with project_setup.json for strict registration validation.
        
        Breadcrumb: project_setup_path → resolver → dependency_graph → registered_schemas
        
        Args:
            project_setup_path: Path to project_setup.json
            
        Complies with agent_rule.md Section 2.3: Strict registration enforcement.
        """
        resolved_path = safe_resolve(Path(project_setup_path))
        
        # Breadcrumb: Initialize RefResolver with project_setup.json
        self._resolver = RefResolver(
            project_setup_path=resolved_path,
            schema_directories=[self.base_path],
            cache=self.cache
        )
        
        # Breadcrumb: Extract registered schemas for quick lookup
        self._registered_schemas = set(self._resolver.registered_schemas.keys())
        
        # Breadcrumb: Initialize dependency graph
        # Check L3 cache for dependency graph
        self._dependency_graph = self.cache.get_l3("dependency_graph")
        if self._dependency_graph is None:
            self._dependency_graph = SchemaDependencyGraph(self._resolver)
            self._dependency_graph.build_graph()
            self.cache.set_l3("dependency_graph", self._dependency_graph)
        
        status_print(f"SchemaLoader initialized with project_setup.json ({len(self._registered_schemas)} schemas registered)")

    
    def set_main_schema_path(self, schema_file: str | Path) -> Path:
        """Set the main schema path so relative references resolve correctly."""
        self.main_schema_path = safe_resolve(Path(schema_file))
        if self.main_schema_path.parent.exists():
            self.base_path = self.main_schema_path.parent
        return self.main_schema_path
    
    def _validate_registration(self, schema_name: str) -> None:
        """
        Validate that a schema is registered in project_setup.json.
        
        Breadcrumb: schema_name → registered_schemas → validation_result
        
        Args:
            schema_name: Name of schema to validate
            
        Raises:
            SchemaNotRegisteredError: If schema not in registry and strict mode enabled
            
        Complies with agent_rule.md Section 2.3: Strict registration enforcement.
        """
        if self._resolver is not None:
            self._resolver.validate_registration(schema_name)
        # If no resolver (legacy mode), allow loading without validation
    
    def get_schema_dependencies(self, schema_name: str) -> Set[str]:
        """
        Get all dependencies for a registered schema.
        
        Breadcrumb: schema_name → dependency_graph → dependencies
        
        Args:
            schema_name: Name of the schema to analyze
            
        Returns:
            Set of schema names that are dependencies
            
        Raises:
            SchemaNotRegisteredError: If schema not registered and strict mode enabled
        """
        self._validate_registration(schema_name)
        
        if self._dependency_graph is not None:
            return self._dependency_graph.get_all_dependencies(schema_name)
        
        # Fallback: return empty set if no dependency graph
        return set()
    
    def load_recursive(
        self,
        schema_name: str,
        auto_resolve: bool = True,
        max_depth: int = 100
    ) -> Dict[str, Any]:
        """
        Load schema with all dependencies, validating registration.
        
        Breadcrumb: schema_name → validate_registration → get_resolution_order → load_all
        
        Args:
            schema_name: Name of the schema to load
            auto_resolve: Whether to resolve $refs after loading
            max_depth: Maximum recursion depth for $ref resolution
            
        Returns:
            Dictionary containing the loaded schema
            
        Raises:
            SchemaNotRegisteredError: If schema not in project_setup.json
            CircularDependencyError: If circular dependency detected
            RefResolutionError: If $ref resolution fails
            
        Complies with agent_rule.md Section 2.3, 2.4, 2.5.
        """
        # Breadcrumb: Validate schema is registered
        self._validate_registration(schema_name)
        
        # Breadcrumb: Check for circular dependencies
        if self._dependency_graph is not None:
            cycle = self._dependency_graph.detect_cycles()
            if cycle:
                raise CircularDependencyError(cycle)
        
        # Breadcrumb: Get optimal loading order (topological sort)
        if self._dependency_graph is not None:
            load_order = self._dependency_graph.get_resolution_order()
            deps = self._dependency_graph.get_all_dependencies(schema_name)
            deps.add(schema_name)
            
            # Load dependencies in order
            for dep_name in load_order:
                if dep_name in deps and self.cache.get(dep_name) is None:
                    self._load_schema_internal(dep_name)
        else:
            # Fallback: just load the requested schema
            self._load_schema_internal(schema_name)
        
        # Breadcrumb: Return loaded schema
        result = self.cache.get(schema_name) or {}
        
        # Breadcrumb: Resolve $refs if requested
        if auto_resolve and self._resolver is not None:
            result = self.resolve_all_refs(result, result, max_depth=max_depth)
        
        return result
    
    def _load_schema_internal(self, schema_name: str) -> Dict[str, Any]:
        """
        Internal method to load a single schema without dependency resolution.
        
        Breadcrumb: schema_name → load_from_disk → cache → return
        """
        cached = self.cache.get(schema_name)
        if cached is not None:
            return cached
        
        schema_data = self.load_schema(schema_name)
        return schema_data
    
    def resolve_all_refs(
        self,
        value: Any,
        current_schema: Dict[str, Any],
        path: str = "",
        max_depth: int = 100
    ) -> Any:
        """
        Recursively resolve ALL JSON types with $ref.
        
        Breadcrumb: value → type_check → resolver.resolve → resolved_value
        
        Args:
            value: Any JSON value (primitive, dict, list)
            current_schema: The schema currently being processed
            path: Current JSON path for error reporting
            max_depth: Maximum recursion depth
            
        Returns:
            Resolved value with all $refs expanded
            
        Raises:
            RefResolutionError: If resolution fails
            RecursionError: If max_depth exceeded
            
        Complies with agent_rule.md Section 2.4: Universal JSON support.
        """
        if self._resolver is None:
            # Fallback: return value as-is if no resolver
            return value
        
        return self._resolver.resolve(value, current_schema, path, max_depth)

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
        # Breadcrumb: Try to find schema in any registered directory
        search_directories = [self.base_path]
        if self._resolver is not None:
            # Include all discovered directories
            search_directories = self._resolver.schema_directories
            
        schema_file = None
        for directory in search_directories:
            candidate = directory / f"{schema_name}.json"
            if candidate.exists():
                schema_file = candidate
                break
                
        if schema_file is None:
            # Last resort: just use base_path (will fail and raise below)
            schema_file = self.base_path / f"{schema_name}.json"
        
        cached = self.cache.get(schema_name, schema_file)
        if cached is not None:
            return cached

        try:
            schema_data = self.load_json_file(schema_file)
            status_print(f"Loaded schema: {schema_name}")
            self.cache.set(schema_name, schema_data, schema_file)
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
        schema_file = self._resolve_reference_path(schema_path)
        cache_key = str(schema_file)
        
        cached = self.cache.get(cache_key, schema_file)
        if cached is not None:
            return cached

        try:
            schema_data = self.load_json_file(schema_file)
            status_print(f"Loaded schema: {schema_file}")
            self.cache.set(cache_key, schema_data, schema_file)
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
                log_error(f"Failed to resolve schema reference {ref_name}: {exc}", module="schema_loader")
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
    Load parameters from schema file.

    Supports two schema architectures:
    - New: top-level 'global_parameters' array  -> returns global_parameters[0]
    - Legacy: top-level 'parameters' dict        -> returns parameters

    Args:
        schema_path: Path to the JSON schema file

    Returns:
        Flattened parameters dict, or empty dict if not present
    """
    with schema_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    # New architecture: global_parameters is an array
    gp = data.get("global_parameters")
    if isinstance(gp, list) and gp and isinstance(gp[0], dict):
        return gp[0]

    # Legacy architecture: parameters is a dict
    params = data.get("parameters", {})
    if isinstance(params, dict):
        return params

    return {}
