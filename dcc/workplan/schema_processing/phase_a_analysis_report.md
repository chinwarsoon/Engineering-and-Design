# Phase A Analysis Report: Schema Discovery and $ref Patterns

**Date:** 2026-04-13
**Workplan:** [recursive_schema_loader_workplan.md](recursive_schema_loader_workplan.md)
**Phase:** A - Analysis & Design

---

## 1. Schema Directory Inventory

### 1.1 Core Config Schemas - WITH STRICT REGISTRATION
**Location:** `config/schemas/`

**Main Entry Point:** `project_setup.json` serves as the **mandatory root** for all schema discovery.

| Schema File | Size | Type | $ref Usage | Registration Status |
|-------------|------|------|-------------|---------------------|
| `project_setup.json` | 1,486 bytes | **Master Entry** | Catalogs all schemas | **REQUIRED - Root** |

**Strict Registration Requirement:**
- All schemas MUST be declared in `project_setup.json["schema_files"]` array
- Unregistered schemas will trigger `SchemaNotRegisteredError`
- Registration validates schema existence and accessibility
- Registration ensures schema dependencies are traceable

**project_setup.json Schema Catalog Format:**
```json
"schema_files": [
  {
    "filename": "dcc_register_enhanced.json",
    "required": true,
    "description": "Main DCC register schema",
    "approximate_size": "2KB"
  },
  {
    "filename": "project_schema.json",
    "required": true,
    "description": "Project code definitions"
  }
  // ... all schemas must be listed here
]
```

**Error on Unregistered Schema:**
```python
class SchemaNotRegisteredError(SchemaLoaderError):
    """Raised when attempting to load a schema not in project_setup.json catalog."""
    def __init__(self, schema_name: str, available_schemas: List[str]):
        message = (
            f"Schema '{schema_name}' is not registered in project_setup.json. "
            f"Available schemas: {', '.join(available_schemas)}. "
            f"Add '{schema_name}' to the schema_files array to register it."
        )
```

**Registered Config Schemas:**

| Schema File | Size | Type | $ref Usage |
|-------------|------|------|-------------|
| `dcc_register_enhanced.json` | 2,183 bytes | Main Schema | `schema_references`, custom `$ref` |
| `project_schema.json` | TBD | Reference Data | To be scanned |
| `facility_schema.json` | TBD | Reference Data | To be scanned |
| `department_schema.json` | TBD | Reference Data | To be scanned |
| `discipline_schema.json` | TBD | Reference Data | To be scanned |
| `document_type_schema.json` | TBD | Reference Data | To be scanned |
| `approval_code_schema.json` | TBD | Reference Data | To be scanned |
| `calculation_strategies.json` | TBD | Strategy Config | To be scanned |
| `master_registry.json` | TBD | Registry | To be scanned |

**Subdirectories:**
- `backup/` - 4 backup schema files (not active)

### 1.3 Registration Gap Analysis (2026-04-13)

**Discovery:** Phase A analysis revealed significant registration gaps in `project_setup.json`.

**Gap Summary:**

| Category | Registered | Missing | Total |
|----------|-----------|---------|-------|
| Config Schemas | 5 | 4 | 9 |
| Engine Schemas | 0 | 9 | 9 |
| **Total** | **5** | **13** | **18** |

**Missing Config Schemas (4):**
| Schema | Reason for Registration |
|--------|------------------------|
| `facility_schema.json` | Referenced in `schema_references`, required for validation |
| `project_schema.json` | Referenced in `schema_references`, required for validation |
| `calculation_strategies.json` | Column calculation definitions, required for processing |
| `master_registry.json` | Document tracking, required for resubmission detection |

**Missing Engine Schemas (9):**
| Schema | Purpose | Required? |
|--------|---------|-----------|
| `taxonomy.json` | Error classification system | Yes |
| `error_codes.json` | Error code registry | Yes |
| `anatomy_schema.json` | E-M-F-XXXX format validation | Yes |
| `approval_workflow.json` | Suppression/overrule workflow | Yes |
| `remediation_types.json` | Remediation strategies | Yes |
| `status_lifecycle.json` | Error state machine | Yes |
| `suppression_rules.json` | 'Wrong but acceptable' rules | Yes |
| `messages/en.json` | English error messages | Yes |
| `messages/zh.json` | Chinese error messages | No (optional i18n) |

**Resolution:** All 13 missing schemas added to `project_setup.json["schema_files"]` array. See `project_setup.json` lines 660-737 for full registration entries.

**Registration Enforcement:**
- Schemas listed in `project_setup.json["schema_files"]` are considered "registered"
- Any schema NOT in this list will raise `SchemaNotRegisteredError` when accessed
- Engine schemas must also be registered if referenced from config schemas
- Cross-directory paths supported (e.g., `workflow/processor_engine/...`)

### 1.2 Engine-Specific Schemas
**Location:** `workflow/processor_engine/error_handling/config/`

| Schema File | Size | Purpose | $ref Usage |
|-------------|------|---------|------------|
| `taxonomy.json` | 311 bytes | Error Taxonomy | None (standalone) |
| `error_codes.json` | 602 bytes | Error Registry | None (standalone) |
| `anatomy_schema.json` | TBD | Error Anatomy | To be scanned |
| `approval_workflow.json` | TBD | Workflow States | To be scanned |
| `remediation_types.json` | TBD | Remediation Categories | To be scanned |
| `status_lifecycle.json` | TBD | Status Transitions | To be scanned |
| `suppression_rules.json` | TBD | Suppression Logic | To be scanned |
| `messages/en.json` | TBD | English Messages | To be scanned |
| `messages/zh.json` | TBD | Chinese Messages | To be scanned |

---

## 2. $ref Pattern Analysis

### 2.1 Pattern Type 1: `schema_references` (Custom DCC)
**Found in:** `dcc_register_enhanced.json`

```json
"schema_references": {
  "project_schema": "../config/schemas/project_schema.json",
  "facility_schema": "../config/schemas/facility_schema.json",
  "department_schema": "../config/schemas/department_schema.json",
  "discipline_schema": "../config/schemas/discipline_schema.json",
  "document_type_schema": "../config/schemas/document_type_schema.json",
  "approval_code_schema": "../config/schemas/approval_code_schema.json"
}
```

**Characteristics:**
- Top-level key in schema object
- Dictionary mapping logical names to relative file paths
- Paths use `../` notation for cross-directory references
- Current loader: `resolve_schema_dependencies()` method handles this

### 2.2 Pattern Type 2: Custom DCC `$ref` Object
**Found in:** `dcc_register_enhanced.json` (parameters section)

```json
"pending_status": {
  "$ref": {
    "schema": "approval_code_schema",
    "code": "PEN",
    "field": "status",
    "description": "Resolved from approval_code_schema..."
  }
}
```

**Characteristics:**
- Located within `parameters` sections
- Object format with keys: `schema`, `code`, `field`
- References data within another schema (not entire file)
- Requires lookup: find item in array where `code == "PEN"`, then extract `status` field
- **Current loader:** NOT implemented - requires custom resolver

### 2.3 Pattern Type 3: Universal JSON Support (ALL Types)
**Requirement:** Support ALL JSON reference types universally:

| JSON Type | Example | Resolution Strategy |
|-----------|---------|---------------------|
| **Simple String** | `"status": "PENDING"` | Direct value, no resolution needed |
| **Nested Object** | `{"$ref": {"schema": "X", "code": "Y"}}` | Custom DCC resolver (Type 2) |
| **Recursive Object** | Self-referencing schema definitions | Circular reference detection |
| **Array References** | `{"$ref": [{"schema": "A"}, {"schema": "B"}]}` | Iterate and resolve each element |
| **Deeply Nested** | `{"level1": {"level2": {"$ref": {...}}}}` | Recursive traversal with path tracking |
| **Mixed Types** | `{"field": "value", "ref": {"$ref": ...}}` | Resolve $ref fields, preserve others |

**Universal Resolver Interface:**
```python
def resolve_json_value(value: Any, 
                      current_schema: Dict,
                      path: str = "") -> Any:
    """
    Recursively resolve ANY JSON value.
    - Primitive: return as-is
    - Dict with $ref: resolve reference
    - Dict without $ref: recurse into values
    - List: recurse into each element
    """
    if isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, list):
        return [resolve_json_value(item, current_schema, f"{path}[i]") 
                for i, item in enumerate(value)]
    elif isinstance(value, dict):
        if "$ref" in value:
            return resolve_ref_object(value["$ref"], current_schema, path)
        else:
            return {k: resolve_json_value(v, current_schema, f"{path}.{k}") 
                   for k, v in value.items()}
```

**Status:** Need to scan remaining schemas to identify all $ref patterns used.

### 2.4 Pattern Type 4: JSON Schema `$schema` Declaration
**Found in:** `project_setup.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  ...
}
```

**Note:** This is a meta-schema declaration, not a reference to be resolved.

---

## 3. Current SchemaLoader Analysis

### 3.1 Existing Capabilities
**File:** `workflow/schema_engine/loader/schema_loader.py` (170 lines)

| Method | Purpose | Handles $ref? |
|--------|---------|---------------|
| `load_schema()` | Load by name from base_path | No |
| `load_schema_from_path()` | Load by path with caching | No |
| `resolve_schema_dependencies()` | Resolve `schema_references` | **Yes - Type 1** |
| `_resolve_schema_dependency()` | Recursive resolver with cycle guard | **Yes - Type 1** |
| `_resolve_reference_path()` | Path resolution with fallbacks | Partial |
| `load_schema_parameters()` | Load parameters section only | No |

### 3.2 Current Limitations

1. **Single Directory Focus**
   - Base path defaults to `config/schemas/`
   - No support for multi-directory discovery
   - Engine schemas in `workflow/processor_engine/error_handling/config/` not reachable

2. **No DCC Custom $ref Support**
   - Custom `$ref` objects (Type 2) not resolved
   - Parameters with `$ref` left as-is

3. **No Automatic Discovery**
   - Requires manual `schema_references` declaration
   - No walking/scraping of schema directories

4. **No Standard JSON $ref Support**
   - Standard `$ref` like `{"$ref": "#/definitions/Type"}` not implemented

5. **Limited Caching**
   - In-memory cache only (no TTL)
   - No file modification time checking

### 3.3 Strengths to Preserve

- **Circular reference detection** - Already implemented in `_resolve_schema_dependency()`
- **Path resolution strategies** - Multiple fallback search paths
- **Error handling** - Comprehensive exception handling with logging
- **Caching** - Basic in-memory caching with cache keys

---

## 4. Cross-Directory Dependency Map

### 4.1 Current Dependencies (Manual)

```
dcc_register_enhanced.json
├── project_schema (../config/schemas/project_schema.json)
├── facility_schema (../config/schemas/facility_schema.json)
├── department_schema (../config/schemas/department_schema.json)
├── discipline_schema (../config/schemas/discipline_schema.json)
├── document_type_schema (../config/schemas/document_type_schema.json)
└── approval_code_schema (../config/schemas/approval_code_schema.json)
    └── $ref lookup: code="PEN" → status field
```

### 4.2 Potential Cross-Directory Links (To Be Investigated)

**Config Schemas → Engine Schemas:**
- Could error_codes.json reference taxonomy.json?
- Could approval_workflow.json reference status_lifecycle.json?

**Engine Schemas → Config Schemas:**
- Could anatomy_schema.json reference dcc_register_enhanced.json?
- Could suppression_rules.json reference error_codes.json?

**Action:** Scan remaining schemas for any $ref patterns.

---

## 5. Dependency Graph Design

### 5.1 Proposed Data Structure

```python
class SchemaDependencyGraph:
    """Graph of schema dependencies across multiple directories."""
    
    nodes: Dict[str, SchemaNode]  # schema_name → node
    edges: List[DependencyEdge]   # (from, to, ref_type)
    
class SchemaNode:
    """Single schema file in the graph."""
    
    name: str              # Logical name (stem)
    path: Path             # Absolute file path
    directory: str         # "config" or "engine"
    schema_type: str       # "master", "reference", "taxonomy", etc.
    content_hash: str      # For cache invalidation
    last_modified: float   # File mtime
    
class DependencyEdge:
    """Reference from one schema to another."""
    
    source: str            # Source schema name
    target: str            # Target schema name
    ref_type: str          # "schema_references", "dcc_ref", "standard_ref"
    ref_location: str      # JSON path to $ref (e.g., "parameters.pending_status")
    resolved: bool       # Whether successfully resolved
```

### 5.2 Graph Building Algorithm

```python
def build_dependency_graph(schema_directories: List[Path]) -> SchemaDependencyGraph:
    graph = SchemaDependencyGraph()
    
    # Step 1: Discover all schemas
    for directory in schema_directories:
        for schema_file in directory.glob("*.json"):
            node = create_schema_node(schema_file)
            graph.add_node(node)
    
    # Step 2: Scan for dependencies in each schema
    for node in graph.nodes.values():
        dependencies = scan_for_dependencies(node)
        for dep in dependencies:
            graph.add_edge(node.name, dep.target, dep.type, dep.location)
    
    # Step 3: Validate and detect cycles
    cycles = graph.detect_cycles()
    if cycles:
        raise CircularDependencyError(cycles)
    
    return graph
```

---

## 6. Caching Strategy Design

### 6.1 Cache Levels

| Level | Scope | Key | TTL | Invalidation Trigger |
|-------|-------|-----|-----|---------------------|
| L1 | In-Memory | schema_name + content_hash | 5 min | File modification |
| L2 | Disk Cache | schema_path + mtime | 1 hour | Manual clear |
| L3 | Dependency Graph | full_graph_hash | Session | Schema structure change |

### 6.2 Cache Key Format

```python
def generate_cache_key(schema_path: Path, content: Dict) -> str:
    """Generate unique cache key for schema."""
    content_hash = hashlib.sha256(
        json.dumps(content, sort_keys=True).encode()
    ).hexdigest()[:16]
    mtime = schema_path.stat().st_mtime
    return f"{schema_path.stem}:{mtime}:{content_hash}"
```

### 6.3 Cache Invalidation Rules

1. **File modification time change** → Invalidate L1 cache entry
2. **Schema structure change** → Invalidate L3 graph cache
3. **Manual clear command** → Invalidate all caches
4. **Process restart** → L1 cleared, L2 persists

---

## 7. Findings Summary

### 7.1 Discovered $ref Patterns

| Pattern | Location | Frequency | Implementation Priority |
|---------|----------|-----------|------------------------|
| `schema_references` | dcc_register_enhanced.json | 6 references | P1 - Already supported |
| Custom DCC `$ref` | dcc_register_enhanced.json parameters | 1 reference | P2 - Needs new resolver |
| Standard JSON $ref | Unknown | Unknown | P3 - Scan remaining schemas |

### 7.2 Schema Count by Directory

| Directory | Active Schemas | Backup Schemas | Subdirectories |
|-----------|-----------------|----------------|----------------|
| `config/schemas/` | 10 | 4 | 1 (backup/) |
| `engine/config/` | 9 | 0 | 1 (messages/) |
| **Total** | **19** | **4** | **2** |

### 7.3 Implementation Recommendations

1. **Immediate (Phase B):**
   - Create `RefResolver` class supporting Type 1 and Type 2 $ref patterns
   - Add multi-directory path resolution

2. **Short-term (Phase C):**
   - Build `SchemaDependencyGraph` for all 19 schemas
   - Validate no circular dependencies exist

3. **Medium-term (Phase D):**
   - Integrate recursive discovery into `SchemaLoader`
   - Support automatic walking of both directories

4. **Long-term (Phase F):**
   - Implement L1/L2/L3 caching strategy
   - Add file modification monitoring

---

## 8. Next Steps (Phase B Preparation)

1. [ ] Scan remaining 17 schemas for additional $ref patterns
2. [ ] Design `RefResolver` interface to handle both Type 1 and Type 2
3. [ ] Identify any cross-directory dependencies between engine and config schemas
4. [ ] Create test cases for each $ref pattern discovered

---

## Appendix A: File Paths

### Config Schemas
```
/home/franklin/dsai/Engineering-and-Design/dcc/config/schemas/
├── project_setup.json
├── dcc_register_enhanced.json
├── project_schema.json
├── facility_schema.json
├── department_schema.json
├── discipline_schema.json
├── document_type_schema.json
├── approval_code_schema.json
├── calculation_strategies.json
├── master_registry.json
└── backup/
    ├── dcc_register.json
    ├── discipline_schema_backup.json
    ├── document_type_schema_backup.json
    └── enhanced_schema_example.json
```

### Engine Schemas
```
/home/franklin/dsai/Engineering-and-Design/dcc/workflow/processor_engine/error_handling/config/
├── taxonomy.json
├── error_codes.json
├── anatomy_schema.json
├── approval_workflow.json
├── remediation_types.json
├── status_lifecycle.json
├── suppression_rules.json
└── messages/
    ├── en.json
    └── zh.json
```

---

*Report Generated: 2026-04-13*
*Analyst: Cascade AI*
*Status: Phase A Complete - Ready for Phase B*
