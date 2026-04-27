"""
Dependency graph builder for JSON schemas.

Analyzes schema relationships, detects circular references, and determines
the optimal loading order (topological sort).

Complies with agent_rule.md Section 4 (Module design).
"""

import json
from pathlib import Path
from typing import Dict, Any, Set, List, Optional, Iterator

from .ref_resolver import RefResolver, RefResolutionError

# Lazy imports to break circular dependency with initiation_engine
_status_print = None
_debug_print = None
_DEBUG_LEVEL = 1

def _get_debug_level() -> int:
    global _DEBUG_LEVEL
    try:
        from dcc_core.logging import DEBUG_LEVEL
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


class CircularDependencyError(Exception):
    """Raised when a circular reference is detected in the schema graph."""
    
    def __init__(self, cycle: List[str]):
        """
        Initialize error with the detected cycle.
        
        Breadcrumb: cycle → formatted_message
        
        Args:
            cycle: List of schema names forming the cycle
        """
        message = f"Circular dependency detected: {' -> '.join(cycle)}"
        super().__init__(message)
        self.cycle = cycle


class SchemaDependencyGraph:
    """
    Builds and manages a dependency graph of JSON schemas.
    
    Identifies relationships between schemas via:
    - Type 1: schema_references
    - Type 2: Custom DCC $ref objects
    - Type 3: Standard JSON Schema $ref strings
    
    Provides cycle detection and topological sorting.
    """
    
    def __init__(self, ref_resolver: RefResolver):
        """
        Initialize graph with a RefResolver for path resolution and registration.
        
        Breadcrumb: ref_resolver → graph_initialization
        
        Args:
            ref_resolver: Initialized RefResolver instance
        """
        self.resolver = ref_resolver
        self.graph: Dict[str, Set[str]] = {}
        self.schemas: Dict[str, Dict[str, Any]] = {}
        
        debug_print("SchemaDependencyGraph initialized", level=2)
    
    def build_graph(self) -> Dict[str, Set[str]]:
        """
        Scan all registered schemas and build the dependency graph.
        
        Breadcrumb: registered_schemas → load_schemas → scan_refs → build_edges
        
        Returns:
            Adjacency list representing the dependency graph
        """
        self.graph = {}
        self.schemas = {}
        
        # Breadcrumb: Identify all schemas to scan
        schema_names = list(self.resolver.registered_schemas.keys())
        
        for name in schema_names:
            self._process_schema(name)
            
        debug_print(f"Graph built with {len(self.graph)} nodes", level=2)
        return self.graph
    
    def _process_schema(self, schema_name: str) -> None:
        """
        Load a schema and identify its dependencies.
        
        Breadcrumb: schema_name → load_file → find_refs → add_to_graph
        
        Args:
            schema_name: Name of schema to process
        """
        if schema_name in self.schemas:
            return
            
        try:
            # Breadcrumb: Find and load schema file
            filename = f"{schema_name}.json"
            schema_path = self.resolver._find_schema_file(filename)
            
            with schema_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.schemas[schema_name] = data
            self.graph[schema_name] = set()
            
            # Breadcrumb: Scan for dependencies
            dependencies = self._extract_dependencies(data)
            for dep in dependencies:
                # Breadcrumb: Allow self-references (agent_rule.md Section 2.4 recursive refs)
                if dep != schema_name:
                    self.graph[schema_name].add(dep)
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            debug_print(f"Error processing schema '{schema_name}': {e}", level=1)
            # We still add to graph but with no dependencies if it fails to load
            if schema_name not in self.graph:
                self.graph[schema_name] = set()
    
    def _extract_dependencies(self, data: Any) -> Set[str]:
        """
        Recursively extract schema names from $ref and schema_references.
        
        Breadcrumb: data → recursive_search → identify_schema_names → dependency_set
        
        Args:
            data: JSON data to scan
            
        Returns:
            Set of schema names found as dependencies
        """
        deps = set()
        
        if isinstance(data, dict):
            # Breadcrumb: Check for Type 1 (schema_references)
            if "schema_references" in data and isinstance(data["schema_references"], dict):
                for ref_path in data["schema_references"].values():
                    dep_name = Path(ref_path).stem
                    deps.add(dep_name)
            
            # Breadcrumb: Check for $ref
            if "$ref" in data:
                ref = data["$ref"]
                # Breadcrumb: Type 2 (DCC custom object)
                if isinstance(ref, dict) and "schema" in ref:
                    deps.add(ref["schema"])
                # Breadcrumb: Type 3 (Standard string)
                elif isinstance(ref, str) and not ref.startswith("#"):
                    # Extract schema name from file part of ref
                    file_part = ref.split("#")[0]
                    if file_part:
                        dep_name = Path(file_part).stem
                        deps.add(dep_name)
            
            # Breadcrumb: Recurse into all dict values
            for val in data.values():
                deps.update(self._extract_dependencies(val))
                
        elif isinstance(data, list):
            # Breadcrumb: Recurse into all list items
            for item in data:
                deps.update(self._extract_dependencies(item))
                
        return deps
    
    def detect_cycles(self) -> Optional[List[str]]:
        """
        Detect circular dependencies in the graph using DFS.
        
        Breadcrumb: graph → dfs → visited_stack → cycle_detection
        
        Returns:
            List of schema names forming the first detected cycle, or None
        """
        visited = set()
        rec_stack = []
        rec_set = set()
        
        def visit(node: str) -> Optional[List[str]]:
            if node in rec_set:
                # Cycle detected! Extract the cycle from rec_stack
                idx = rec_stack.index(node)
                return rec_stack[idx:] + [node]
                
            if node in visited:
                return None
                
            visited.add(node)
            rec_stack.append(node)
            rec_set.add(node)
            
            for neighbor in self.graph.get(node, []):
                cycle = visit(neighbor)
                if cycle:
                    return cycle
                    
            rec_stack.pop()
            rec_set.remove(node)
            return None
            
        for schema in self.graph:
            cycle = visit(schema)
            if cycle:
                return cycle
                
        return None
    
    def get_resolution_order(self) -> List[str]:
        """
        Get the topological sort order for schema resolution.
        
        Schemas with fewer dependencies come first.
        
        Breadcrumb: graph → topological_sort → ordered_list
        
        Returns:
            List of schema names in loading order
            
        Raises:
            CircularDependencyError: If a cycle is detected
        """
        cycle = self.detect_cycles()
        if cycle:
            raise CircularDependencyError(cycle)
            
        result = []
        visited = set()
        
        def visit(node: str):
            if node in visited:
                return
            visited.add(node)
            
            for neighbor in self.graph.get(node, []):
                visit(neighbor)
                
            result.append(node)
            
        for schema in self.graph:
            visit(schema)
            
        return result
    
    def get_dependencies(self, schema_name: str) -> Set[str]:
        """
        Get all direct dependencies for a specific schema.
        
        Args:
            schema_name: Name of the schema
            
        Returns:
            Set of dependency schema names
        """
        return self.graph.get(schema_name, set())

    def get_all_dependencies(self, schema_name: str) -> Set[str]:
        """
        Get all transitive dependencies for a specific schema.
        
        Breadcrumb: schema_name → recursive_lookup → transitive_set
        
        Args:
            schema_name: Name of the schema
            
        Returns:
            Set of all schema names this schema depends on (recursive)
        """
        all_deps = set()
        stack = list(self.get_dependencies(schema_name))
        
        while stack:
            dep = stack.pop()
            if dep not in all_deps:
                all_deps.add(dep)
                stack.extend(list(self.get_dependencies(dep)))
                
        return all_deps
