# Recursive Schema Loader Workplan

**Issue #1:** Create a recursive schema loader for all schemas that automatically walks through all JSON schema files and pulls in any file referenced by a $ref key.

**Status:** In Progress (Phase C Complete)
**Created:** 2026-04-16
**Updated:** 2026-04-16
**Related Documents:**
- [agent_rule.md](../../agent_rule.md) - Schema requirements (Section 2)
- [issue_log.md](../../Log/issue_log.md) - Issue #1 details
- [update_log.md](../../Log/update_log.md) - Implementation progress

---

## Objective

Create a recursive schema loader that automatically discovers and resolves all schema dependencies ($ref links) without requiring manual `schema_references` declarations. This will reduce maintenance effort and improve code maintainability by eliminating the need to write custom code every time a new sub-schema is added.

---

## Schema Architecture (Per agent_rule.md Section 2)

### Schema Structure Pattern
- **Base Schema**: Stores "definitions" (e.g., `project_setup_base.json`)
- **Setup Schema**: Stores "properties" (e.g., `project_setup.json`)
- **Config Schema**: Stores actual items/data (e.g., `project_config.json`)
- **Requirement**: Always check one-to-one match between base, setup, and config schemas

### Schema Fragment Pattern
- Adopt schema fragment pattern for better maintainability and reusability
- Implement inheritance (base + project) pattern
- Use 'Definitions' for repetitive objects
- Use pattern-based discovery rule for organizing schema files
- Set `additionalProperties: false` for important property control
- Define 'required' for properties if applicable

### $ref Support Requirements
- Support different types of $ref: string, object, nested object, recursive, etc.
- Use Unified Schema Registry (URIs) giving every schema a unique, permanent "Digital ID"
- Support JSON Schema standard `$ref` and absolute URI-based resolution
- Support cross-directory `$ref` resolution via internal protocol

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
- `project_setup_base.json` - Base definitions
- `project_code_schema.json` - Project code definitions
- `project_config.json` - Project configuration
- `facility_schema.json` - Facility code definitions
- `department_schema.json` - Department codes
- `discipline_schema.json` - Discipline codes
- `document_type_schema.json` - Document type definitions
- `approval_code_schema.json` - Approval workflow codes
- `global_parameters.json` - Global parameters configuration

#### 3. DCC Register Schemas (Updated Architecture)
**Location:** `config/schemas/`
- `dcc_register_base.json` - Base definitions (12 definitions: department_entry, discipline_entry, facility_entry, document_type_entry, project_entry, approval_entry, column_groups_entry, column_sequence_entry, etc.)
- `dcc_register_setup.json` - Setup structure (12 properties: departments, disciplines, facilities, document_types, projects, approval_codes, column_types, column_patterns, column_strategies, column_groups, column_sequence, global_parameters)
- `dcc_register_config.json` - Actual configuration data (47 columns, column_groups, column_sequence, $ref to approval_code_schema.json, etc.)
- **Note:** `dcc_register_enhanced.json` was deleted on 2026-04-16 after migration to base/setup/config architecture

#### 4. Engine-Specific Schemas
**Location:** `workflow/processor_engine/error_handling/config/`
- `taxonomy.json` - Error anatomy definitions
- `approval_workflow.json` - Workflow state definitions
- `error_codes.json` - Error code registry
- `remediation_types.json` - Remediation categories
- `status_lifecycle.json` - Status transition rules
- `suppression_rules.json` - Error suppression logic
- `messages/en.json`, `messages/zh.json` - Localization files

**Note:** Engine schemas reference each other and must be auto-resolved during loading.

---

## Current $ref Usage

### URI-Based $ref (Primary Pattern)
```json
// dcc_register_config.json
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
```

### Internal $ref (Same-File References)
```json
// dcc_register_setup.json
"departments": {
  "type": "array",
  "description": "Department classifications for project",
  "items": {"$ref": "https://dcc-pipeline.internal/schemas/dcc-register-base#/definitions/department_entry"}
},
"disciplines": {
  "type": "array",
  "description": "Discipline classifications for project",
  "items": {"$ref": "https://dcc-pipeline.internal/schemas/dcc-register-base#/definitions/discipline_entry"}
}
```

---

## Proposed Enhancement

### Core Features
1. **Recursive Schema Discovery** - Automatically walk through all JSON schema files and resolve $ref dependencies
2. **Unified Schema Registry** - Use URIs (e.g., `https://dcc-pipeline.internal/schemas/department`) as permanent Digital IDs
3. **Multi-Directory Support** - Scan both `config/schemas/` and `workflow/processor_engine/error_handling/config/` directories
4. **Universal $ref Resolution** - Support ALL $ref types: string, object, nested object, recursive, etc.
5. **Schema Fragment Pattern** - Support base/setup/config architecture with one-to-one matching
6. **Dependency Graph Builder** - Track all schema relationships including cross-directory links
7. **Circular Reference Detection** - Prevent infinite loops across the entire schema graph
8. **Smart Caching** - Cache resolved schemas for performance with TTL support

### $ref Formats to Support

| Format Type | Example | Location |
|-------------|---------|----------|
| URI-Based $ref | `{"$ref": "https://dcc-pipeline.internal/schemas/department#/departments"}` | External schemas |
| Internal Reference | `{"$ref": "#/definitions/Type"}` | Within same file |
| Cross-Directory URI | `{"$ref": "https://dcc-pipeline.internal/schemas/dcc-register-base#/definitions/entry"}` | Cross-file definitions |

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
- **20 active schemas** discovered (11 config + 9 engine)
- **3 $ref patterns** identified:
  - Type 1: URI-based $ref (e.g., `https://dcc-pipeline.internal/schemas/department#/departments`) - Primary pattern
  - Type 2: Internal $ref (e.g., `#/definitions/Type`) - Within same file
  - Type 3: DCC custom $ref object (in parameters) - Legacy pattern (DEPRECATED)
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

### Phase C: Schema Registry & Optimization (2-3 hours) ✅ COMPLETE
**Completed:** 2026-04-13

**Files Updated:**
- All schemas in `config/schemas/` refactored to use URI-based $ref
- Strict validation with `additionalProperties: false`
- Mandatory property enforcement with `required` arrays

**Agent Rule Compliance:**

| Rule | Section | Implementation |
|------|---------|----------------|
| **Schema Standard Compliance** | 2.1 | ✅ JSON Schema Draft 7 compliance |
| **Flat Structure** | 2.2 | ✅ Arrays of objects maintained |
| **Base/Setup/Config Pattern** | 2.3 | ✅ Definitions in base, properties in setup, data in config |
| **URI-Based $ref** | 2.4 | ✅ Unified Schema Registry URIs used |
| **Schema Fragment Pattern** | 2.5 | ✅ Fragment schemas created |
| **Inheritance Pattern** | 2.6 | ✅ `allOf` + `$ref` to base schema |
| **Definitions** | 2.7 | ✅ Centralized reusable definitions |
| **Pattern-Based Discovery** | 2.8 | ✅ Discovery rules added |
| **Additional Properties** | 2.9 | ✅ `additionalProperties: false` enforced |
| **Required Properties** | 2.10 | ✅ `required` arrays defined |

**Optimization Results:**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| URI-Based $ref | 0% | 100% | All schemas use Unified Registry |
| Strict Validation | Partial | 100% | `additionalProperties: false` everywhere |
| Required Enforcement | Partial | 100% | All critical properties have `required` |
| Schema Architecture | Mixed | Consistent | base/setup/config pattern |

---

### Phase D: Dependency Graph Builder (4-5 hours) ✅ COMPLETE
**Completed:** 2026-04-14
**Report:** [phase_d_report.md](phase_d_report.md)

**New File:** [dependency_graph.py](../../workflow/schema_engine/loader/dependency_graph.py) (294 lines)
**Test File:** [test_dependency_graph.py](../../test/test_dependency_graph.py) (122 lines)

**Implementation Details:**
- **SchemaDependencyGraph class**: Graph of schema dependencies across multiple directories
- **Multi-Directory Support**: Via RefResolver integration (scans registered schemas)
- **URI Registry Mapping**: Delegated to RefResolver._resolve_uri_to_file()
- **Topological Sort**: Determine loading order to resolve dependencies correctly
- **Cycle Detection**: Detect circular dependencies before resolution

**Methods Implemented:**
1. ✅ [x] Create `SchemaDependencyGraph` class
2. ✅ [x] Implement `build_graph()` - Scan for $ref dependencies
3. ✅ [x] Implement `detect_cycles()` - Circular dependency detection
4. ✅ [x] Implement `get_resolution_order()` - Topological sort
5. ✅ [x] Implement `get_dependencies()` - Direct dependencies
6. ✅ [x] Implement `get_all_dependencies()` - Transitive dependencies
7. ✅ [x] Add logging per agent_rule.md Section 6 (tiered logging)
8. ✅ [x] Export from `__init__.py`

**Test Coverage:**
- Basic dependency detection
- Custom DCC $ref format
- schema_references format
- Circular dependency detection
- Complex multi-level graph

**Data Structure:**
```python
class SchemaDependencyGraph:
    """Graph of schema dependencies across multiple directories."""
    
    graph: Dict[str, Set[str]]  # adjacency list: schema_name → dependencies
    schemas: Dict[str, Dict]     # loaded schema contents
    resolver: RefResolver       # for path resolution and registration
```

---

### Phase E: SchemaLoader Enhancement (3-4 hours) ✅ COMPLETE
**Completed:** 2026-04-14
**Report:** [phase_e_report.md](phase_e_report.md)

**File Updated:** [schema_loader.py](../../workflow/schema_engine/loader/schema_loader.py) (417 lines)

**Enhancements:**
- **Multi-Directory Support**: Via RefResolver integration (base_path parameter)
- **URI Registry Integration**: RefResolver handles URI-based $ref resolution
- **Recursive Discovery**: load_recursive() automatically loads dependent schemas
- **Dependency Graph Integration**: SchemaDependencyGraph for loading order
- **Strict Registration**: _validate_registration() enforces project_setup.json catalog

**Methods Implemented:**
1. ✅ [x] Update `__init__()` to accept project_setup_path, auto_resolve_refs, max_recursion_depth
2. ✅ [x] Implement `_init_with_project_setup()` - Initialize RefResolver and DependencyGraph
3. ✅ [x] Implement `_validate_registration()` - Strict registration validation
4. ✅ [x] Implement `get_schema_dependencies()` - Get all dependencies via graph
5. ✅ [x] Implement `load_recursive()` - Recursive loading with topological sort
6. ✅ [x] Implement `resolve_all_refs()` - Universal $ref resolution via RefResolver
7. ✅ [x] Add breadcrumb comments per agent_rule.md Section 5
8. ✅ [x] Add tiered logging per agent_rule.md Section 6

**Backward Compatibility:**
- Legacy mode supported (works without project_setup.json)
- Original methods preserved (load_schema, load_schema_from_path, etc.)
- Gradual migration path to enhanced features

**Methods Added:**
```python
class SchemaLoader:
    def __init__(self, base_path, project_setup_path=None, auto_resolve_refs=True, max_recursion_depth=100)
    def _init_with_project_setup(self, project_setup_path)
    def _validate_registration(self, schema_name)
    def get_schema_dependencies(self, schema_name)
    def load_recursive(self, schema_name, auto_resolve=True, max_depth=100)
    def resolve_all_refs(self, value, current_schema, path="", max_depth=100)
```

---

### Phase F: master_registry.json Integration (2-3 hours) ❌ NOT REQUIRED
**Completed:** 2026-04-14 (marked complete in archived workplan)
**Verified:** 2026-04-16 (actual state check - dcc_register schemas provide same functionality)
**Updated:** 2026-04-16 (marked NOT REQUIRED per user feedback)
**Report:** [phase_f_report.md](phase_f_report.md)

**Purpose:** Link master_registry.json as configuration source per agent_rule.md Section 2.3

**Status:** ❌ NOT REQUIRED - dcc_register schemas (base/setup/config) already provide DCC-specific configuration functionality.

**Rationale:**
- dcc_register_base.json - Base definitions for DCC register (departments, disciplines, facilities, document_types, projects, approval_codes, column configurations)
- dcc_register_setup.json - Setup structure for DCC register
- dcc_register_config.json - Actual configuration data for DCC register

Since dcc_register schemas following base/setup/config pattern already provide comprehensive DCC-specific configuration, master_registry.json integration is redundant.

**Actions Taken:**
- ✅ Removed registry property from project_setup.json (lines 198-201)
- ✅ Removed "registry" from required array in project_setup.json (line 206)
- ✅ dcc_master_registry.json remains archived (not required)

---

### Phase G: Caching & Performance (3-4 hours) ✅ COMPLETE
**Completed:** 2026-04-17
**Report:** [phase_g_report.md](phase_g_report.md)
**File New:** [schema_cache.py](../../workflow/schema_engine/loader/schema_cache.py)
**Test File:** [test_schema_cache.py](../../test/test_schema_cache.py)

**Implementation Details:**
- **Multi-Level Caching**: L1 (in-memory), L2 (disk), L3 (dependency graph)
- **TTL Support**: Time-based cache expiration (L1: 5m, L2: 1h defaults)
- **Cache Invalidation**: File modification time tracking (mtime)
- **Performance Monitoring**: Cache hit/miss metrics tracking
- **Content Hashing**: SHA256 for L1 content validation

**Tasks Completed:**
1. ✅ [x] Create `SchemaCache` class with L1/L2/L3 levels
2. ✅ [x] Implement cache key generation (MD5 for file safety)
3. ✅ [x] Implement TTL-based expiration
4. ✅ [x] Implement file modification monitoring
5. ✅ [x] Add cache hit/miss metrics
6. ✅ [x] Add cache clearing utilities
7. ✅ [x] Integrate into `RefResolver` and `SchemaLoader`

---

### Phase H: Integration & Testing (4-5 hours) ✅ COMPLETE
**Completed:** 2026-04-17
**Report:** [phase_h_report.md](phase_h_report.md)
**Test File:** [check_registration.py](../../test/check_registration.py)

**Testing Strategy:**
- **Unit Tests**: Test individual components (RefResolver, DependencyGraph, SchemaCache)
- **Integration Tests**: Test full recursive loading workflow (Pass: 20/20 schemas)
- **Schema Validation Tests**: Validate base/setup/config one-to-one matching
- **Performance Tests**: Measure loading time with and without caching (Result: 116 L1 hits)
- **Edge Cases**: Test circular references, missing schemas, invalid URIs

**Test Results:**
1. ✅ [x] Test URI-based $ref resolution (Passed: 20/20)
2. ✅ [x] Test internal $ref resolution (Passed: anatomy_schema, etc.)
3. ✅ [x] Test cross-directory $ref resolution (Passed: workflow -> config)
4. ✅ [x] Test circular reference detection (Passed: project_setup_base self-ref allowed)
5. ✅ [x] Test schema architecture validation (Passed: base/setup/config loops)
6. ✅ [x] Test multi-directory discovery (Passed: config/schemas + workflow)
7. ✅ [x] Test cache invalidation (Passed: verified in test_schema_cache.py)
8. ✅ [x] Test strict registration enforcement (Passed: 20/20 enforced)

---

### Phase I: Documentation (2-3 hours) ⏳ PENDING
**Documentation Tasks:**
1. [ ] Update `schema_loader.py` docstrings with recursive loading details
2. [ ] Create API documentation for RefResolver, DependencyGraph, SchemaCache
3. [ ] Update agent_rule.md if any new patterns emerge
4. [ ] Create usage examples for recursive schema loading
5. [ ] Document URI registry format and conventions
6. [ ] Document base/setup/config validation rules

---

### Status

### Phase Completion Status
- **Phase A**: ✅ COMPLETE (Updated 2026-04-16)
- **Phase B**: ✅ COMPLETE
- **Phase C**: ✅ COMPLETE
- **Phase D**: ✅ COMPLETE
- **Phase E**: ✅ COMPLETE
- **Phase F**: ❌ NOT REQUIRED (dcc_register schemas provide same functionality)
- **Phase G**: ✅ COMPLETE
- **Phase H**: ✅ COMPLETE
- **Phase I**: ⏳ PENDING

### Overall Progress
- **Phases Completed:** 7/9 (78%)
- **Phases Not Required:** 1/9 (Phase F - master_registry.json Integration)
- **Estimated Time Remaining:** 2-3 hours
- **Next Phase:** Phase I - Documentation


---

## Key Requirements Summary (Per agent_rule.md Section 2)

1. ✅ **Schema Standard Compliance** - JSON Schema Draft 7
2. ✅ **Flat Structure** - Arrays of objects, avoid arrays of lists
3. ✅ **Base/Setup/Config Pattern** - Definitions in base, properties in setup, data in config
4. ✅ **One-to-One Matching** - Always check matching between base, setup, config
5. ✅ **Universal $ref Support** - String, object, nested object, recursive types
6. ✅ **Unified Schema Registry** - URIs as permanent Digital IDs
7. ✅ **Schema Fragment Pattern** - Better maintainability and reusability
8. ✅ **Inheritance Pattern** - Base + project pattern
9. ✅ **Definitions** - For repetitive objects
10. ✅ **Pattern-Based Discovery** - Organizing schema files
11. ✅ **Additional Properties** - Set to false for control
12. ✅ **Required Properties** - Define when applicable

---

*Workplan Created: 2026-04-16*
*Based on Issue #1 from issue_log.md and agent_rule.md Section 2*
*Status: Ready for Phase D Implementation*
