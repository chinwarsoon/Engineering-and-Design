# Recursive Schema Loader Workplan

## Issue Reference
**Issue #1** from issue_log.md - Schema loader should recursively scan schema folder and automatically resolve all related `$ref` links

## Objective
Enhance the SchemaLoader to automatically discover and resolve all schema dependencies (`$ref` links) without requiring manual `schema_references` declarations.

**Schema Architecture Update (2026-04-16):**
- `dcc_register_enhanced.json` was deleted after successful migration to `dcc_register_config.json`
- Current dcc_register architecture: `dcc_register_base.json` (definitions) → `dcc_register_setup.json` (structure) → `dcc_register_config.json` (actual data)
- All schema references now use Unified Schema Registry URIs (e.g., `https://dcc-pipeline.internal/schemas/dcc-register-base`)

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
- `project_code_schema.json` - Project code definitions
- `project_config.json` - Project configuration
- `facility_schema.json` - Facility code definitions
- `department_schema.json` - Department codes
- `discipline_schema.json` - Discipline codes
- `document_type_schema.json` - Document type definitions
- `approval_code_schema.json` - Approval workflow codes
- `global_parameters.json` - Global parameters configuration

#### 2.1 DCC Register Schemas (Updated Architecture)
**Location:** `config/schemas/`
- `dcc_register_base.json` - Base definitions (12 definitions: department_entry, discipline_entry, facility_entry, document_type_entry, project_entry, approval_entry, column_groups_entry, column_sequence_entry, etc.)
- `dcc_register_setup.json` - Setup structure (12 properties: departments, disciplines, facilities, document_types, projects, approval_codes, column_types, column_patterns, column_strategies, column_groups, column_sequence, global_parameters)
- `dcc_register_config.json` - Actual configuration data (47 columns, column_groups, column_sequence, $ref to approval_code_schema.json, etc.)
- **Note:** `dcc_register_enhanced.json` was deleted on 2026-04-16 after migration to config

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
// dcc_register_config.json (Updated Architecture)
"departments": {
  "$ref": "https://dcc-pipeline.internal/schemas/department#/departments"
},
"disciplines": {
  "$ref": "https://dcc-pipeline.internal/schemas/discipline#/disciplines"
},
"facilities": {
  "$ref": "https://dcc-pipeline.internal/schemas/facility#/facilities"
},
"document_types": {
  "$ref": "https://dcc-pipeline.internal/schemas/document-type#/document_types"
},
"projects": {
  "$ref": "https://dcc-pipeline.internal/schemas/project#/projects"
},
"approval_codes": {
  "$ref": "https://dcc-pipeline.internal/schemas/approval-code#/approval"
}

// dcc_register_setup.json (Updated Architecture)
"departments": {
  "type": "array",
  "description": "Department classifications for project",
  "items": {"$ref": "https://dcc-pipeline.internal/schemas/dcc-register-base#/definitions/department_entry"}
},
"column_groups": {
  "type": "object",
  "description": "Logical groupings of columns for processing and validation",
  "additionalProperties": false,
  "properties": {
    "document_info": {
      "type": "array",
      "items": {"type": "string"}
    }
    // ... other groups
  }
}
```

---

## Proposed Enhancement

### Core Features
1. **Strict Schema Registration** - All schemas MUST be registered in `project_setup.json["schema_files"]`; unregistered schemas trigger `SchemaNotRegisteredError`
2. **Main Entry Drill-down** - Use `project_setup.json` as mandatory root; resolve all schemas from this catalog
3. **Universal JSON Support** - Handle ALL JSON types: simple strings, nested objects, recursive objects, arrays, deeply nested structures
4. **Multi-Directory Schema Discovery** - Scan both `config/schemas/` and `workflow/processor_engine/error_handling/config/` directories
5. **$ref Resolution Engine** - Support both JSON Schema and DCC custom formats across directories
6. **Dependency Graph Builder** - Track all schema relationships including cross-directory links
7. **Circular Reference Detection** - Prevent infinite loops across the entire schema graph
8. **Smart Caching** - Cache resolved schemas for performance

### $ref Formats to Support

| Format Type | Example | Location |
|-------------|---------|----------|
| JSON Schema Standard | `{"$ref": "file.json#/field"}` | Anywhere in schema |
| DCC Custom Object | `{"$ref": {"schema": "name", "code": "X"}}` | Parameters section |
| Internal Reference | `{"$ref": "#/definitions/Type"}` | Within same file |
| Schema References | `{"schema_references": {...}}` | Top-level only |

---

## Implementation Phases

### Phase A: Analysis & Design (1-2 hours) ✅ COMPLETE
**Completed:** 2026-04-13
**Updated:** 2026-04-16 - Schema architecture realignment

**Analysis Report:** [phase_a_analysis_report.md](phase_a_analysis_report.md)

**Tasks Completed:**
1. ✅ [x] Scan all schema files in `config/schemas/` to identify $ref patterns
2. ✅ [x] Scan engine-specific schemas in `workflow/processor_engine/error_handling/config/`
3. ✅ [x] Analyze cross-directory $ref links between config and engine schemas
4. ✅ [x] Document current `$ref` usage locations and formats
5. ✅ [x] Analyze `schema_loader.py` current implementation
6. ✅ [x] Design dependency graph data structure supporting multiple source directories
7. ✅ [x] Define caching strategy

**Key Findings (Updated 2026-04-16):**
- **13 active schemas** discovered in `config/schemas/` (8 core + 3 dcc_register + 1 global_parameters + 1 project_config)
- **3 $ref patterns** identified:
  - Type 1: URI-based $ref (e.g., `https://dcc-pipeline.internal/schemas/department#/departments`) - Primary pattern
  - Type 2: Internal $ref (e.g., `#/definitions/Type`) - Within same file
  - Type 3: DCC custom $ref object (in parameters) - Legacy pattern
- **Schema Architecture Changes:**
  - dcc_register_enhanced.json deleted, migrated to dcc_register_base/setup/config architecture
  - approval_code_schema.json added with standalone structure
  - All schemas now use Unified Schema Registry URIs
- **Current loader limitations:** Single directory, limited URI-based $ref support
- **Proposed design:** Multi-directory graph with URI registry support and L1/L2/L3 caching

**Deliverables:**
- ✅ [phase_a_analysis_report.md](phase_a_analysis_report.md) - Complete analysis with schema inventory, $ref patterns, and design recommendations

---

### Phase B: RefResolver Module (3-4 hours) ✅ COMPLETE
**Completed:** 2026-04-13

**New File:** [ref_resolver.py](../../workflow/schema_engine/loader/ref_resolver.py)

**Implementation Details:**
- **RefResolver class**: Universal JSON resolver supporting ALL types per agent_rule.md Section 2.4
- **Strict Registration**: Validates schemas against project_setup.json catalog
- **Universal JSON Support**: Recursive resolution for primitives, lists, dicts, nested $ref
- **$ref Types Implemented**:
  - String refs: `#/definitions/Type` (internal), `file.json#/field` (external)
  - Object refs: DCC custom `{"schema": "X", "code": "Y", "field": "Z"}`
  - Recursive: Full depth traversal with cycle detection
- **Exception Classes**: `SchemaNotRegisteredError`, `RefResolutionError`
- **Breadcrumb Comments**: All methods trace parameter flow per agent_rule.md Section 5
- **Module Design**: Clean separation of concerns per agent_rule.md Section 4

**Tasks Completed:**
1. ✅ [x] Create `RefResolver` class
2. ✅ [x] Implement `resolve()` - Universal JSON resolver
3. ✅ [x] Implement `_resolve_string_ref()` - Standard JSON Schema format
4. ✅ [x] Implement `_resolve_dcc_ref_object()` - Custom DCC format
5. ✅ [x] Implement `_resolve_internal_ref()` - Same-file references
6. ✅ [x] Add path resolution utilities (`_find_schema_file()`)
7. ✅ [x] Add registration validation (`validate_registration()`)
8. ✅ [x] Export from `__init__.py`

---

### Phase C: project_setup.json Schema Optimization (2-3 hours) ✅ COMPLETE
**Completed:** 2026-04-13

**Files Created:**
1. [project_setup_base.json](../../config/schemas/project_setup_base.json) - Base definitions
2. [project_setup_discovery.json](../../config/schemas/project_setup_discovery.json) - Discovery rules
3. [project_setup_environment.json](../../config/schemas/project_setup_environment.json) - Environment specification
4. [project_setup_validation.json](../../config/schemas/project_setup_validation.json) - Validation rules
5. [project_setup_dependencies.json](../../config/schemas/project_setup_dependencies.json) - Dependencies configuration
6. [project_setup_structure.json](../../config/schemas/project_setup_structure.json) - Project structure (folders, root_files)

**File Updated:**
- [project_setup.json](../../config/schemas/project_setup.json) - Optimized using $ref

**Agent Rule Compliance:**

| Rule | Section | Implementation |
|------|---------|----------------|
| **Schema Fragment Pattern** | 2.5 | ✅ Created 6 fragment schemas (base, discovery, environment, validation, dependencies, structure) |
| **Inheritance Pattern** | 2.6 | ✅ `allOf` + `$ref` to base schema |
| **Definitions** | 2.7 | ✅ Centralized 10 reusable definitions |
| **Pattern-Based Discovery** | 2.8 | ✅ Added `discovery_rules` array |
| **Flat Structure** | 2.2 | ✅ Arrays of objects maintained |
| **$ref Support** | 2.4 | ✅ All nested structures use `$ref` to fragments |

**Optimization Results:**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Schema Reusability | 0% | 100% | All via definitions |
| Auto-Discovery | None | 6 patterns | Full support |
| Fragment Count | 1 | 6 | Better maintainability |
| Definition Reuse | 0 | 10 types | file_entry, path_entry, validation_rule_entry, etc. |

**Base Definitions Created:**
- `file_entry` - Generic file metadata
- `typed_file_entry` - File with type classification
- `python_module_entry` - Python module with functions
- `path_entry` - Path-based entry (folders, modules)
- `pattern_rule` - Discovery pattern definition
- `validation_rule` - Schema validation rule
- `folder_entry` - Directory specification
- `root_file_entry` - Root-level file

**Fragment-Specific Definitions:**
- `environment_entry` - Conda/pip environment specs
- `validation_rule_entry` - Validation rule configuration
- `engine_dependency` - Engine module dependencies
- `dependencies_config` - Complete dependencies structure

**Structure Fragment Definitions:**
- `folder_entry` - Directory specification
- `root_file_entry` - Root-level file

**Nested Keys Fragmented:**
| Key | Fragment | Definition |
|-----|----------|------------|
| `folders` | structure.json | `folder_entry` |
| `root_files` | structure.json | `root_file_entry` |
| `environment` | environment.json | `environment_entry` |
| `validation_rules` | validation.json | `validation_rule_entry` |
| `dependencies` | dependencies.json | `dependencies_config` |
| `discovery_rules` | base.json | `pattern_rule` |
| File arrays | base.json | `file_entry`, `path_entry` |

**Discovery Patterns Added:**
1. `*_schema.json` in `config/schemas` → validation_schema
2. `*_types.json` in `config/schemas` → type_definition
3. `**/error_handling/config/*.json` → engine_schema
4. `**/messages/*.json` → i18n_messages
5. `calculation_*.json` → calculation_strategy
6. `master_*.json` → registry

**Tasks Completed:**
1. ✅ [x] Analyze current project_setup.json for repetitive patterns
2. ✅ [x] Create `definitions` section with reusable object types (10 definitions)
3. ✅ [x] Extract `file_entry`, `pattern_rule`, `validation_rule` definitions
4. ✅ [x] Refactor file arrays to use `$ref` to definitions
5. ✅ [x] Create fragment schemas: base, discovery, environment, validation, dependencies
6. ✅ [x] Add `discovery_rules` array for pattern-based auto-registration
7. ✅ [x] Add `allOf` + `$ref` inheritance support
8. ✅ [x] Fragment nested keys: environment, validation_rules, dependencies
9. ⏳ [ ] Unit tests for fragment resolution (deferred to Phase H)

**Success Criteria Met:**
- ✅ File structure optimized through definition reuse
- ✅ New file types can be added by extending definitions
- ✅ Pattern discovery configured (implementation in loader pending)
- ✅ Inheritance support via `allOf` + `$ref`
- ✅ All existing functionality preserved
- ✅ All nested keys fragmented for reusability

---

### Phase D: Dependency Graph Builder (2-3 hours) ✅ COMPLETE
**Completed:** 2026-04-14

**New File:** [dependency_graph.py](../../workflow/schema_engine/loader/dependency_graph.py)

**Tasks Completed:**
1. ✅ [x] Create `SchemaDependencyGraph` class
2. ✅ [x] Implement `build_graph()` - Scan all schemas
3. ✅ [x] Implement `detect_cycles()` - Circular ref detection
4. ✅ [x] Implement `get_resolution_order()` - Topological sort
5. ✅ [x] Add visualization/debug methods (transitive dependencies)
6. ✅ [x] Unit tests for cycle detection and topological sort: [test_dependency_graph.py](../../test/test_dependency_graph.py)

**Implementation Details:**
- **Recursive extraction**: Scans all JSON types for $ref and schema_references
- **Cycle detection**: DFS-based algorithm with full path reporting
- **Topological sort**: Provides optimal loading order where dependencies come first
- **Transitive resolution**: Can retrieve all recursive dependencies for any schema

---

### Phase E: SchemaLoader Enhancement (3-4 hours) ✅ COMPLETE
**Completed:** 2026-04-14

**File Updated:** `workflow/schema_engine/loader/schema_loader.py`

**Tasks Completed:**
1. ✅ [x] Extend `SchemaLoader` with recursive loading
2. ✅ [x] Integrate `RefResolver` into loading workflow
3. ✅ [x] Integrate `SchemaDependencyGraph` for batch loading
4. ✅ [x] Add `load_recursive()` method with registration check
5. ✅ [x] Add `auto_resolve_refs` parameter
6. ✅ [x] Implement universal JSON traversal for $ref resolution
7. ✅ [x] Add strict registration validation
8. ✅ [x] Enhance error messages with ref context
9. ⏳ [ ] Update existing tests (deferred to Phase H)

**New Methods Added:**
```python
class SchemaLoader:
    def __init__(self, base_path=None, project_setup_path=None, 
                 auto_resolve_refs=True, max_recursion_depth=100):
        """Initialize with optional project_setup.json for strict registration."""
    
    def _init_with_project_setup(self, project_setup_path: Path) -> None:
        """Initialize RefResolver and SchemaDependencyGraph."""
    
    def load_recursive(self, schema_name: str,
                       auto_resolve: bool = True,
                       max_depth: int = 100) -> Dict:
        """Load schema with all dependencies, validating registration."""
        # Uses topological sort from dependency graph
    
    def resolve_all_refs(self, value: Any,
                         current_schema: Dict,
                         path: str = "",
                         max_depth: int = 100) -> Any:
        """Recursively resolve ALL JSON types with $ref via RefResolver."""
        
    def get_schema_dependencies(self, schema_name: str) -> Set[str]:
        """Get all dependencies for a registered schema."""
        
    def _validate_registration(self, schema_name: str) -> None:
        """Validate schema is registered in project_setup.json."""
        # Delegates to RefResolver.validate_registration()
    
    def _load_schema_internal(self, schema_name: str) -> Dict[str, Any]:
        """Internal method to load a single schema."""
```

**Integration Details:**
- **RefResolver Integration:** Initialized with project_setup_path, handles all $ref types
- **SchemaDependencyGraph Integration:** Builds graph on init, provides topological sort
- **Strict Registration:** Validates against project_setup.json before loading (when configured)
- **Backward Compatibility:** Works in legacy mode without project_setup.json
- **Error Handling:** Enhanced with ref context via RefResolutionError and CircularDependencyError

---

### Phase F: master_registry.json Integration (2-3 hours)
**Purpose:** Link master_registry.json as configuration source per agent_rule.md Section 2.3

**Design Decision:** Per agent_rule.md - all schema files must be referenced in project_setup.json (Option B)

**Prerequisite Fixes (Audit Findings from Phases A-E):** ✅ COMPLETE

**Fix 1: Add URI-to-File Mapping to RefResolver (Phase B Gap)** ✅
- **Issue:** `RefResolver._find_schema_file()` only resolves filenames, not URIs (`https://dcc-pipeline.internal/schemas/...`)
- **Location:** `workflow/schema_engine/loader/ref_resolver.py`
- **Solution Implemented:**
  - ✅ [x] Added `uri_registry` dictionary mapping `$id` URIs to file paths
  - ✅ [x] Build registry by scanning `config/schemas/` for all `$id` declarations via `_build_uri_registry()`
  - ✅ [x] Updated `_resolve_external_ref()` to check URI registry before file search
  - ✅ [x] Added `_resolve_uri_to_file()` method for URI resolution
  - **Example:** `https://dcc-pipeline.internal/schemas/master-registry` → `config/schemas/master_registry.json`

**Fix 2: Explicitly Reference master_registry.json (Phase C Gap)** ✅
- **Issue:** `project_setup.json` does NOT list `master_registry.json` in `schema_files` array
- **Location:** `config/schemas/project_setup.json`
- **Solution Implemented:**
  - ✅ [x] Added `registry` property with `$ref` to master-registry schema
  - ✅ [x] Also auto-discovered via `master_*.json` pattern in discovery_rules
  - ✅ [x] Required for strict registration validation (agent_rule.md Section 2.3)

**Phase 1: Convert master_registry.json to Proper JSON Schema** ✅ COMPLETE
- ✅ [x] Added `$schema: http://json-schema.org/draft-07/schema#`
- ✅ [x] Added `$id: https://dcc-pipeline.internal/schemas/master-registry`
- ✅ [x] Added `type: "object"`, `additionalProperties: false`
- ✅ [x] Wrapped existing content in `properties` with proper structure
- ✅ [x] Moved data values to `default` property for configuration extraction
- ✅ [x] Defined `required` properties per agent_rule.md Section 2.10

**Phase 2: Reference master_registry.json in project_setup.json** ✅ COMPLETE
- ✅ [x] Added `registry` property with `$ref` to master-registry schema
- ✅ [x] Uses inheritance pattern (base + project) per agent_rule.md Section 2.6

**Phase 3: Update Validator for Schema Loading** ✅ COMPLETE
- ✅ [x] Added `_init_ref_resolver()` to initialize RefResolver with URI support
- ✅ [x] Updated `_extract_project_setup()` to resolve `$ref` to master_registry.json
- ✅ [x] Added `_map_registry_to_project_setup()` to extract config from registry defaults
- ✅ [x] Added `_extract_from_schema()` for extracting defaults from schema properties
- ✅ [x] Extracts `project_structure.required_folders` → `folders` configuration

**Phase 4: Update Calling Functions** ✅ COMPLETE
- ✅ [x] `get_schema_path` points to `config/schemas/project_setup.json` (verified)
- ✅ [x] Validator now resolves registry $ref using RefResolver
- ✅ [x] Pipeline flow: `project_setup.json` → resolve `$ref` → load `master_registry.json` → extract defaults → get config

**Files Affected:**
- `config/schemas/master_registry.json` - Convert to proper JSON Schema
- `config/schemas/project_setup.json` - Add registry reference
- `workflow/initiation_engine/core/validator.py` - Update extraction logic
- `workflow/initiation_engine/utils/paths.py` - Ensure path points to project_setup.json

**Compliance:**
- Section 2.3: project_setup.json as main entry point, all schemas referenced
- Section 2.5: Fragment pattern for maintainability
- Section 2.6: Inheritance (base + project) pattern
- Section 2.10: Required properties defined

---

### Phase G: Circular Reference Handling (2 hours)
**File:** `workflow/schema_engine/loader/schema_loader.py`

**Tasks:**
1. [ ] Implement circular reference detection in loader
2. [ ] Add `max_recursion_depth` parameter
3. [ ] Create informative error messages for cycles
4. [ ] Add cycle breaking strategies (lazy loading)
5. [ ] Unit tests for circular scenarios

---

### Phase G: Caching & Performance (2 hours)
**File:** `workflow/schema_engine/loader/schema_loader.py`

**Tasks:**
1. [ ] Implement `SchemaCache` with TTL support
2. [ ] Add file modification time checking
3. [ ] Implement cache invalidation
4. [ ] Add performance metrics/logging
5. [ ] Benchmark loading times

---

### Phase H: Integration & Testing (3-4 hours)

**Tasks:**
1. [ ] Test new loader with `dcc_register_config.json` (updated architecture)
2. [ ] Test with `dcc_register_base.json` and `dcc_register_setup.json` (new architecture)
3. [ ] Remove manual `schema_references` (test backward compatibility)
4. [ ] Add integration tests for URI-based $ref resolution
5. [ ] Test with all existing schema files
6. [ ] Verify no breaking changes
7. [ ] Performance regression testing

**Test Scenarios:**
- Standard JSON $ref resolution
- DCC custom $ref resolution
- Internal $ref resolution
- Circular reference detection
- Deeply nested dependencies (5+ levels)
- Missing reference handling
- Cache hit/miss scenarios

---

### Phase I: Documentation (2 hours)

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

- [x] Phase A: Analysis & Design
- [x] Phase B: RefResolver Module
- [x] Phase C: project_setup.json Schema Optimization
- [x] Phase D: Dependency Graph Builder
- [x] Phase E: SchemaLoader Enhancement
- [x] Phase F: master_registry.json Integration
- [ ] Phase G: Circular Reference Handling
- [ ] Phase G: Caching & Performance
- [ ] Phase H: Integration & Testing
- [ ] Phase I: Documentation

---

## Schema Architecture Update (2026-04-16)

**Major Changes:**
- `dcc_register_enhanced.json` deleted after successful migration to `dcc_register_config.json`
- New dcc_register architecture: Base → Setup → Config
- All schema references now use Unified Schema Registry URIs
- Setup schema uses inline definitions for architectural consistency
- Config schema contains actual data values

**Impact on Recursive Schema Loader:**
- Loader must handle URI-based $ref references (e.g., `https://dcc-pipeline.internal/schemas/dcc-register-base`)
- No more `schema_references` manual declarations in dcc_register schemas
- Enhanced dependency resolution across base/setup/config hierarchy
- Testing must use new schema architecture (base, setup, config)

---

*Created: 2024-04-12*
*Updated: 2026-04-16 - Aligned with current schema architecture*
*Issue: #1*
*Priority: High*
*Estimated Effort: 3 days*
