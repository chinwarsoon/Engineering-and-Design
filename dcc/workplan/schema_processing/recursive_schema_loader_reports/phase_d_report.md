# Phase D Report: Dependency Graph Builder

**Phase:** D - Dependency Graph Builder
**Status:** ✅ COMPLETE
**Completed:** 2026-04-14
**Duration:** 3-4 hours
**Workplan:** [recursive_schema_loader_workplan.md](recursive_schema_loader_workplan.md#phase-d-dependency-graph-builder-4-5-hours-)

---

## Objective

Build a dependency graph of JSON schemas to track relationships, detect circular references, and determine optimal loading order (topological sort) for recursive schema resolution.

---

## Implementation Summary

### New File Created
**File:** `workflow/schema_engine/loader/dependency_graph.py` (294 lines)
**Purpose:** Analyzes schema relationships, detects circular references, and determines optimal loading order

### Test File Created
**File:** `test/test_dependency_graph.py` (122 lines)
**Purpose:** Unit tests for dependency graph functionality

### Files Updated
**File:** `workflow/schema_engine/loader/__init__.py`
**Changes:** Added exports for SchemaDependencyGraph and CircularDependencyError

---

## Class Structure

### SchemaDependencyGraph Class

```python
class SchemaDependencyGraph:
    """Builds and manages a dependency graph of JSON schemas."""
    
    def __init__(self, ref_resolver: RefResolver):
        """Initialize graph with a RefResolver for path resolution and registration."""
```

**Initialization Parameters:**
- `ref_resolver`: Initialized RefResolver instance for schema resolution and registration validation

**Instance Variables:**
- `resolver`: RefResolver instance
- `graph`: Dict[str, Set[str]] - Adjacency list representing dependency graph
- `schemas`: Dict[str, Dict[str, Any]] - Loaded schema contents

---

## Method Breakdown

### 1. build_graph() (lines 81-100)
**Purpose:** Scan all registered schemas and build the dependency graph
**Returns:** Adjacency list representing the dependency graph

**Logic:**
1. Initialize empty graph and schemas dict
2. Get list of all registered schemas from RefResolver
3. Process each schema to identify dependencies
4. Build edges in graph based on dependencies
5. Return completed graph

**Breadcrumb:** registered_schemas → load_schemas → scan_refs → build_edges

### 2. _process_schema() (lines 102-134)
**Purpose:** Load a schema and identify its dependencies
**Parameters:**
- `schema_name`: Name of schema to process

**Logic:**
1. Check if schema already processed (skip if yes)
2. Find and load schema file using RefResolver
3. Store schema content in schemas dict
4. Initialize empty dependency set in graph
5. Extract dependencies from schema content
6. Add dependencies to graph
7. Handle errors gracefully (add to graph with no dependencies if load fails)

**Breadcrumb:** schema_name → load_file → find_refs → add_to_graph

### 3. _extract_dependencies() (lines 136-180)
**Purpose:** Recursively extract schema names from $ref and schema_references
**Parameters:**
- `data`: JSON data to scan

**Returns:** Set of schema names found as dependencies

**Logic:**
1. Initialize empty dependencies set
2. Check for Type 1 (schema_references):
   - Extract schema names from ref_path values
3. Check for $ref:
   - Type 2 (DCC custom object): Extract "schema" field
   - Type 3 (Standard string): Extract schema name from file part
   - Skip internal refs (starting with #)
4. Recurse into all dict values
5. Recurse into all list items
6. Return dependencies set

**Breadcrumb:** data → recursive_search → identify_schema_names → dependency_set

**$ref Types Supported:**
- **Type 1:** schema_references dict
- **Type 2:** DCC custom $ref object `{"schema": "name", "code": "X", "field": "Y"}`
- **Type 3:** Standard JSON Schema $ref string (external only)

### 4. detect_cycles() (lines 182-222)
**Purpose:** Detect circular dependencies in the graph using DFS
**Returns:** List of schema names forming the first detected cycle, or None

**Logic:**
1. Initialize visited set, recursion stack, and recursion set
2. Define recursive visit function:
   - If node in rec_set: cycle detected, extract cycle path
   - If node in visited: already processed, no cycle
   - Mark node as visited and add to recursion stack
   - Visit all neighbors recursively
   - Remove from recursion stack after visiting
3. Visit all nodes in graph
4. Return first cycle found, or None if no cycles

**Breadcrumb:** graph → dfs → visited_stack → cycle_detection

**Cycle Detection Algorithm:** DFS with recursion stack tracking

### 5. get_resolution_order() (lines 224-258)
**Purpose:** Get the topological sort order for schema resolution
**Returns:** List of schema names in loading order

**Raises:** CircularDependencyError if a cycle is detected

**Logic:**
1. Check for cycles using detect_cycles()
2. If cycle found, raise CircularDependencyError
3. Initialize result list and visited set
4. Define recursive visit function:
   - If node visited: return
   - Mark node as visited
   - Visit all dependencies first
   - Add node to result after dependencies
5. Visit all nodes in graph
6. Return result (dependencies come before dependents)

**Breadcrumb:** graph → topological_sort → ordered_list

**Topological Sort:** Post-order DFS traversal

### 6. get_dependencies() (lines 260-270)
**Purpose:** Get all direct dependencies for a specific schema
**Parameters:**
- `schema_name`: Name of the schema

**Returns:** Set of dependency schema names

**Logic:** Simple lookup in graph adjacency list

### 7. get_all_dependencies() (lines 272-293)
**Purpose:** Get all transitive dependencies for a specific schema
**Parameters:**
- `schema_name`: Name of the schema

**Returns:** Set of all schema names this schema depends on (recursive)

**Logic:**
1. Initialize all_deps set and stack with direct dependencies
2. Iterate through stack:
   - Pop dependency
   - If not already in all_deps: add it
   - Add its dependencies to stack
3. Return all_deps (includes all recursive dependencies)

**Breadcrumb:** schema_name → recursive_lookup → transitive_set

---

## Exception Class

### CircularDependencyError (lines 37-51)
**Purpose:** Raised when a circular reference is detected in the schema graph

**Parameters:**
- `cycle`: List of schema names forming the cycle

**Message Format:**
```
Circular dependency detected: schema_a -> schema_b -> schema_a
```

---

## Unit Tests

### Test File: test/test_dependency_graph.py (122 lines)

#### Test Cases:

1. **test_basic_dependency** (lines 48-57)
   - Tests basic $ref dependency detection
   - Schema A references Schema B
   - Verifies dependency extraction and resolution order

2. **test_custom_dcc_ref** (lines 59-71)
   - Tests DCC custom $ref object format
   - Schema A has DCC ref to Schema B
   - Verifies custom ref extraction

3. **test_schema_references** (lines 73-85)
   - Tests schema_references dict format
   - Schema A has schema_references to Schema B
   - Verifies Type 1 ref extraction

4. **test_circular_dependency** (lines 87-97)
   - Tests circular reference detection
   - Schema A → Schema B → Schema A
   - Verifies cycle detection and error raising

5. **test_complex_graph** (lines 99-118)
   - Tests complex multi-level dependencies
   - A → B, A → C, B → D, C → D, D → E
   - Verifies topological sort order

**Test Results:** All tests pass ✅

---

## Agent Rule Compliance

| Rule | Section | Implementation |
|------|---------|----------------|
| **Module Design** | 4 | ✅ Clean separation of concerns |
| **Breadcrumb Comments** | 5 | ✅ All methods trace parameter flow |
| **Tiered Logging** | 6 | ✅ debug_print with level parameter |
| **Schema Standard Compliance** | 2.1 | ✅ JSON Schema Draft 7 compliance |

---

## Multi-Directory Support

**Implementation:** Via RefResolver integration
- RefResolver handles multiple schema directories
- SchemaDependencyGraph uses RefResolver for path resolution
- No separate discover_schemas() method needed (build_graph scans registered schemas)

**URI Registry Mapping:**
- Handled by RefResolver._resolve_uri_to_file()
- SchemaDependencyGraph delegates URI resolution to RefResolver
- No separate resolve_uri_to_path() method needed

---

## Performance Considerations

### Graph Building
- **Time Complexity:** O(N * M) where N = number of schemas, M = average schema size
- **Space Complexity:** O(N + E) where E = number of dependencies

### Cycle Detection
- **Time Complexity:** O(N + E) using DFS
- **Space Complexity:** O(N) for recursion stack

### Topological Sort
- **Time Complexity:** O(N + E) using post-order DFS
- **Space Complexity:** O(N) for visited set and result list

---

## Integration Points

### With RefResolver
- **Initialization:** SchemaDependencyGraph requires RefResolver instance
- **Schema Loading:** Uses RefResolver._find_schema_file()
- **Registration Validation:** Uses RefResolver.registered_schemas
- **URI Resolution:** Delegates to RefResolver for URI-based $ref

### With SchemaLoader
- **Usage:** SchemaLoader can use SchemaDependencyGraph for batch loading
- **Loading Order:** Use get_resolution_order() to determine optimal load sequence
- **Dependency Tracking:** Use get_all_dependencies() for full dependency tree

---

## Known Limitations

1. **No Direct Multi-Directory Discovery:** Relies on RefResolver's registered schemas
2. **No Separate URI Resolution:** Delegates to RefResolver
3. **No Graph Visualization:** No visualization/debug methods beyond text output
4. **No Incremental Updates:** Must rebuild entire graph on schema changes

---

## Success Criteria

- ✅ SchemaDependencyGraph class created
- ✅ build_graph() method implemented
- ✅ detect_cycles() method implemented
- ✅ get_resolution_order() (topological sort) implemented
- ✅ get_dependencies() and get_all_dependencies() methods implemented
- ✅ Multi-directory support via RefResolver
- ✅ URI registry mapping via RefResolver
- ✅ Circular dependency detection with full cycle path
- ✅ Topological sort for optimal loading order
- ✅ Tiered logging support
- ✅ Exported from __init__.py
- ✅ Comprehensive unit tests (5 test cases)

---

## Benefits Achieved

### 1. Dependency Tracking
- **Explicit Dependencies:** Clear view of schema relationships
- **Transitive Dependencies:** Recursive lookup for full dependency tree
- **Dependency Graph:** Visual representation of schema ecosystem

### 2. Loading Optimization
- **Topological Sort:** Optimal loading order (dependencies first)
- **Batch Loading:** Load all schemas in correct sequence
- **Efficiency:** Avoids redundant loads

### 3. Error Prevention
- **Cycle Detection:** Prevents infinite loops during resolution
- **Clear Error Messages:** Full cycle path in error message
- **Early Detection:** Catches circular dependencies before loading

### 4. Maintainability
- **Clean Interface:** Simple API for dependency queries
- **Modular Design:** Separate from RefResolver and SchemaLoader
- **Testable:** Comprehensive unit test coverage

---

## Next Steps

1. **Phase E:** Integrate with SchemaLoader enhancement
2. **Phase F:** master_registry.json integration
3. **Phase G:** Circular Reference Handling (enhanced)
4. **Phase G:** Caching & Performance
5. **Phase H:** Integration & Testing

---

## File Inventory

### Active Files
- `workflow/schema_engine/loader/dependency_graph.py` (294 lines) - Main implementation
- `test/test_dependency_graph.py` (122 lines) - Unit tests

### Updated Files
- `workflow/schema_engine/loader/__init__.py` - Added exports

---

*Report Generated: 2026-04-16*
*Phase D Status: COMPLETE*
*Next Phase: Phase E - SchemaLoader Enhancement*
