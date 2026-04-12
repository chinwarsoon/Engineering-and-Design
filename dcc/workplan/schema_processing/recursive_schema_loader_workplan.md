# Recursive Schema Loader Workplan

## Issue Reference
**Issue #1** from issue_log.md - Schema loader should recursively scan schema folder and automatically resolve all related `$ref` links

## Objective
Enhance the SchemaLoader to automatically discover and resolve all schema dependencies (`$ref` links) without requiring manual `schema_references` declarations in `dcc_register_enhanced.json`.

---

## Current State Analysis

### Existing Implementation
- **File:** `workflow/schema_engine/loader/schema_loader.py`
- **Method:** `resolve_schema_dependencies()` - Resolves `schema_references` dict
- **Limitation:** Requires manual declaration of all schema references
- **Custom $ref:** Limited support for DCC's custom `$ref` format in parameters

### Schema Locations

#### 1. Main Schema Entry (Drill-down Root)
**File:** `config/schemas/project_setup.json`
- Serves as the **primary entry point** for schema discovery
- Defines project structure validation rules
- Contains `schema_files` array listing all required schemas
- Acts as the "master catalog" for recursive loading

#### 2. Core Config Schemas
**Location:** `config/schemas/`
- `project_setup.json` - Main entry point
- `project_schema.json` - Project code definitions
- `facility_schema.json` - Facility code definitions
- `department_schema.json` - Department codes
- `discipline_schema.json` - Discipline codes
- `document_type_schema.json` - Document type definitions
- `approval_code_schema.json` - Approval workflow codes

#### 3. Engine-Specific Schemas (To Be Linked)
**Location:** `workflow/processor_engine/error_handling/config/`
- `anatomy_schema.json` - Error anatomy definitions
- `approval_workflow.json` - Workflow state definitions
- `error_codes.json` - Error code registry
- `remediation_types.json` - Remediation categories
- `status_lifecycle.json` - Status transition rules
- `suppression_rules.json` - Error suppression logic
- `taxonomy.json` - Error classification taxonomy
- `messages/en.json`, `messages/zh.json` - Localization files

**Note:** Engine schemas reference each other and must be auto-resolved during loading.

### Current $ref Usage
```json
// dcc_register_enhanced.json
"schema_references": {
  "project_schema": "../config/schemas/project_schema.json",
  "facility_schema": "../config/schemas/facility_schema.json",
  "department_schema": "../config/schemas/department_schema.json",
  "discipline_schema": "../config/schemas/discipline_schema.json",
  "document_type_schema": "../config/schemas/document_type_schema.json",
  "approval_code_schema": "../config/schemas/approval_code_schema.json"
},
"parameters": {
  "pending_status": {
    "$ref": {
      "schema": "approval_code_schema",
      "code": "PEN",
      "field": "status"
    }
  }
}
```

---

## Proposed Enhancement

### Core Features
1. **Multi-Directory Schema Discovery** - Scan both `config/schemas/` and `workflow/processor_engine/error_handling/config/` directories
2. **Drill-down from Main Entry** - Use `project_setup.json` as root for recursive discovery
3. **$ref Resolution Engine** - Support both JSON Schema and DCC custom formats across directories
4. **Dependency Graph Builder** - Track all schema relationships including cross-directory links
5. **Circular Reference Detection** - Prevent infinite loops across the entire schema graph
6. **Smart Caching** - Cache resolved schemas for performance

### $ref Formats to Support

| Format Type | Example | Location |
|-------------|---------|----------|
| JSON Schema Standard | `{"$ref": "file.json#/field"}` | Anywhere in schema |
| DCC Custom Object | `{"$ref": {"schema": "name", "code": "X"}}` | Parameters section |
| Internal Reference | `{"$ref": "#/definitions/Type"}` | Within same file |
| Schema References | `{"schema_references": {...}}` | Top-level only |

---

## Implementation Phases

### Phase A: Analysis & Design (1-2 hours)
**Tasks:**
1. [ ] Scan all schema files in `config/schemas/` to identify $ref patterns
2. [ ] Scan engine-specific schemas in `workflow/processor_engine/error_handling/config/`
3. [ ] Analyze cross-directory $ref links between config and engine schemas
4. [ ] Document current `$ref` usage locations and formats
5. [ ] Analyze `schema_loader.py` current implementation
6. [ ] Design dependency graph data structure supporting multiple source directories
7. [ ] Define caching strategy

**Deliverables:**
- `$ref` usage analysis report (both config and engine schemas)
- Cross-directory dependency map
- Dependency graph design document
- Updated workplan with findings

---

### Phase B: RefResolver Module (3-4 hours)
**New File:** `workflow/schema_engine/loader/ref_resolver.py`

**Tasks:**
1. [ ] Create `RefResolver` class
2. [ ] Implement `resolve_standard_ref()` - JSON Schema format
3. [ ] Implement `resolve_dcc_ref()` - Custom DCC format
4. [ ] Implement `resolve_internal_ref()` - Same-file references
5. [ ] Add path resolution utilities
6. [ ] Unit tests for each resolver type

**Interface:**
```python
class RefResolver:
    def __init__(self, schema_dir: Path, cache: SchemaCache)
    
    def resolve(self, ref: Union[str, Dict], 
                current_schema: Dict) -> Any
    
    def resolve_standard_ref(self, ref_path: str) -> Any
    
    def resolve_dcc_ref(self, ref_dict: Dict) -> Any
    
    def resolve_internal_ref(self, ref_path: str, 
                             schema: Dict) -> Any
```

---

### Phase C: Dependency Graph Builder (2-3 hours)
**New File:** `workflow/schema_engine/loader/dependency_graph.py`

**Tasks:**
1. [ ] Create `SchemaDependencyGraph` class
2. [ ] Implement `build_graph()` - Scan all schemas
3. [ ] Implement `detect_cycles()` - Circular ref detection
4. [ ] Implement `get_resolution_order()` - Topological sort
5. [ ] Add visualization/debug methods
6. [ ] Unit tests for cycle detection

**Interface:**
```python
class SchemaDependencyGraph:
    def __init__(self, schema_dir: Path)
    
    def build_graph(self) -> Dict[str, Set[str]]
    
    def detect_cycles(self) -> Optional[List[str]]
    
    def get_resolution_order(self) -> List[str]
    
    def get_dependencies(self, schema_name: str) -> Set[str]
```

---

### Phase D: SchemaLoader Enhancement (3-4 hours)
**File:** `workflow/schema_engine/loader/schema_loader.py`

**Tasks:**
1. [ ] Extend `SchemaLoader` with recursive loading
2. [ ] Integrate `RefResolver` into loading workflow
3. [ ] Integrate `SchemaDependencyGraph` for batch loading
4. [ ] Add `load_recursive()` method
5. [ ] Add `auto_resolve_refs` parameter
6. [ ] Enhance error messages with ref context
7. [ ] Update existing tests

**New Methods:**
```python
class SchemaLoader:
    def load_recursive(self, main_schema_path: Path,
                       auto_resolve: bool = True) -> Dict
    
    def resolve_all_refs(self, schema: Dict,
                         visited: Set[str] = None) -> Dict
    
    def get_schema_dependencies(self, schema_path: Path) -> Set[str]
```

---

### Phase E: Circular Reference Handling (2 hours)
**File:** `workflow/schema_engine/loader/schema_loader.py`

**Tasks:**
1. [ ] Implement circular reference detection in loader
2. [ ] Add `max_recursion_depth` parameter
3. [ ] Create informative error messages for cycles
4. [ ] Add cycle breaking strategies (lazy loading)
5. [ ] Unit tests for circular scenarios

---

### Phase F: Caching & Performance (2 hours)
**File:** `workflow/schema_engine/loader/schema_loader.py`

**Tasks:**
1. [ ] Implement `SchemaCache` with TTL support
2. [ ] Add file modification time checking
3. [ ] Implement cache invalidation
4. [ ] Add performance metrics/logging
5. [ ] Benchmark loading times

---

### Phase G: Integration & Testing (3-4 hours)

**Tasks:**
1. [ ] Update `dcc_register_enhanced.json` to test new loader
2. [ ] Remove manual `schema_references` (test backward compatibility)
3. [ ] Add integration tests
4. [ ] Test with all existing schema files
5. [ ] Verify no breaking changes
6. [ ] Performance regression testing

**Test Scenarios:**
- Standard JSON $ref resolution
- DCC custom $ref resolution
- Internal $ref resolution
- Circular reference detection
- Deeply nested dependencies (5+ levels)
- Missing reference handling
- Cache hit/miss scenarios

---

### Phase H: Documentation (2 hours)

**Tasks:**
1. [ ] Update `docs/schema_engine/readme.md`
2. [ ] Create `docs/schema_engine/schema_loader.md`
3. [ ] Document $ref formats supported
4. [ ] Add troubleshooting guide
5. [ ] Update workplan as complete

---

## Technical Specifications

### File Structure
```
schema_engine/
├── loader/
│   ├── __init__.py
│   ├── schema_loader.py          # Enhanced
│   ├── ref_resolver.py            # NEW
│   ├── dependency_graph.py        # NEW
│   └── cache.py                   # NEW (or inline)
```

### $ref Resolution Order
1. Check cache for resolved reference
2. Parse $ref format (standard vs DCC vs internal)
3. Resolve path/schema lookup
4. Load referenced schema if needed
5. Extract specific field if path includes `#/field`
6. Cache result
7. Return resolved value

### Error Handling
| Error Type | Message | Action |
|------------|---------|--------|
| File Not Found | "Schema file not found: {path}" | Log + Raise |
| Invalid $ref | "Invalid $ref format: {ref}" | Log + Raise |
| Circular Ref | "Circular dependency detected: {cycle}" | Log + Raise |
| Missing Field | "Field not found in schema: {field}" | Log + Raise |
| Parse Error | "Invalid JSON in schema: {exc}" | Log + Raise |

---

## Success Criteria

- [ ] All existing tests pass without modification
- [ ] New recursive loader resolves all current `schema_references` automatically
- [ ] Circular references detected and reported clearly
- [ ] Loading time improved or maintained (with caching)
- [ ] All $ref formats (standard, DCC, internal) supported
- [ ] Documentation complete and accurate

---

## Dependencies

- `pathlib` - Path manipulation
- `json` - JSON parsing
- `networkx` (optional) - Dependency graph visualization
- Existing `SchemaLoader` base class

---

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking changes | Maintain backward compatibility with `schema_references` |
| Performance issues | Implement caching, lazy loading |
| Circular references | Detection + clear error messages |
| Complex $ref formats | Phased implementation, thorough testing |

---

## Timeline Estimate

| Phase | Duration | Cumulative |
|-------|----------|--------------|
| A | 1-2 hrs | 2 hrs |
| B | 3-4 hrs | 6 hrs |
| C | 2-3 hrs | 9 hrs |
| D | 3-4 hrs | 13 hrs |
| E | 2 hrs | 15 hrs |
| F | 2 hrs | 17 hrs |
| G | 3-4 hrs | 21 hrs |
| H | 2 hrs | 23 hrs |

**Total:** ~23 hours (3 days @ 8 hrs/day)

---

## Status

- [ ] Phase A: Analysis & Design
- [ ] Phase B: RefResolver Module
- [ ] Phase C: Dependency Graph Builder
- [ ] Phase D: SchemaLoader Enhancement
- [ ] Phase E: Circular Reference Handling
- [ ] Phase F: Caching & Performance
- [ ] Phase G: Integration & Testing
- [ ] Phase H: Documentation

---

*Created: 2024-04-12*
*Issue: #1*
*Priority: High*
*Estimated Effort: 3 days*
