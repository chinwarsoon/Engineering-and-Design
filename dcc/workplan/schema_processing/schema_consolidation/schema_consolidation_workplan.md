# Schema Consolidation Workplan (Revised)

## Objective
Apply **domain separation principle** to global parameters schema:
- **System/Infrastructure** parameters → `project_setup_*` files
- **Data Processing** parameters → `dcc_register_*` files + `dcc_global_parameters.json` (as independent values file)

Reference `dcc_global_parameters.json` from `dcc_register_config.json` (like other independent value files).

---

## Domain Separation Principle

| Domain | Purpose | Files |
|:---|:---|:---|
| **System/Infrastructure** | Python environment, debug flags, execution mode | `project_setup_base.json`, `project_setup.json`, `project_config.json` |
| **Data Processing/DCC** | Excel paths, column settings, review durations | `dcc_register_base.json`, `dcc_register_setup.json`, `dcc_global_parameters.json` (values), `dcc_register_config.json` |

---

## Current State Analysis

### Parameter Distribution (24 parameters listed, ~44 total)

| Parameter | Type | Domain | Target Location |
|:---|:---|:---|:---|
| `fail_fast` | boolean | System | `project_setup_base` → `project_setup` → `project_config` |
| `debug_dev_mode` | boolean | System | `project_setup_base` → `project_setup` → `project_config` |
| `is_colab` | boolean | System | `project_setup_base` → `project_setup` → `project_config` |
| `overwrite_existing_downloads` | boolean | System | `project_setup_base` → `project_setup` → `project_config` |
| `duration_is_working_day` | boolean | Data Processing | `dcc_register_base#/definitions/dcc_parameter_entry` → `dcc_register_setup#/properties/dcc_parameters[]` → `dcc_global_parameters.json#/dcc_parameters` |
| `pc_name` | string | System | `project_setup_base` → `project_setup` → `project_config` |
| `start_col` | string | Data Processing | `dcc_register_base#/definitions/dcc_parameter_entry` → `dcc_register_setup#/properties/dcc_parameters[]` → `dcc_global_parameters.json#/dcc_parameters` |
| `end_col` | string | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `header_row_index` | integer | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `first_review_duration` | integer | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `second_review_duration` | integer | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `resubmission_duration` | integer | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `progress_stage` | string | System | `project_setup_base` → `project_setup` → `project_config` |
| `upload_sheet_name` | string | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `win_upload_file` | string | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `win_download_path` | string | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `linux_upload_file` | string | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `linux_download_path` | string | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `colab_upload_file` | string | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `colab_download_path` | string | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `upload_file_name` | string | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `download_file_path` | string | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_global_parameters.json` |
| `pending_status` | object | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_register_config.json` (already there) |
| `dynamic_column_creation` | object | Data Processing | `dcc_register_base` → `dcc_register_setup` → `dcc_register_config.json` (already there) |

*Note: 44 total parameters — need complete list during implementation*

---

## Detailed Consolidation Plan

### Phase 1: Domain Classification & Definition Migration

**Objective**: Separate parameters into System vs Data Processing domains

#### 1.1 Add domain-specific parameter entry definitions

**Completed:** Added `system_parameter_entry` and `dcc_parameter_entry` definitions.

| Source | Target System | Target Data Processing |
|:---|:---|:---|
| `project_setup_base:420-487` | `project_setup_base#/definitions/system_parameter_entry` | `dcc_register_base#/definitions/dcc_parameter_entry` |

#### 1.2 Update `project_setup_base.json` ✅ COMPLETED
- Added `system_parameter_entry` (lines 489-542) for system/infrastructure parameters
- `global_parameters_entry` kept for backward compatibility (deprecated)

#### 1.3 Update `dcc_register_base.json` 
- Added `dcc_parameter_entry` (lines 537-605) for data processing parameters
- Includes file, directory, scalar, boolean, integer, object types

---

### Phase 2: Property Schema Updates

#### 2.1 Update `project_setup.json`
- Add `system_parameters` property array
- Reference `project_setup_base#/definitions/system_parameter_entry`

#### 2.2 Update `dcc_register_setup.json` 
#### 2.2 Update `dcc_register_setup.json` ✅ COMPLETED
- Renamed `global_parameters` → `dcc_parameters` (lines 81-87)
- Updated items to reference `dcc_register_base#/definitions/dcc_parameter_entry`
- Property now contains parameter structure definitions (metadata)

---

### Phase 3: Value File Restructuring

#### 3.1 Create `dcc_global_parameters.json` (NEW values-only file) ✅ COMPLETED

**Current**: Contains both metadata AND values
```json
{
  "dcc_parameters": [
    {
      "key": "upload_file_name",  // ← Metadata
      "type": "file",              // ← Metadata
      "default_value": "data/..."  // ← Metadata (not actual value)
    }
  ]
}
```

**Target**: Contains ONLY actual values (like other value files)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://dcc-pipeline.internal/schemas/dcc_global_parameters",
  "title": "Global Processing Parameter Values",
  "description": "Actual runtime values for data processing parameters",
  "version": "1.0.0",
  "type": "object",
  "allOf": [{"$ref": "https://dcc-pipeline.internal/schemas/dcc_register_base"}],
  "dcc_parameters": {
    "fail_fast": false,              // ← ACTUAL VALUE
    "upload_file_name": "data/...",  // ← ACTUAL VALUE
    ...
  }
}
```

#### 3.2 Create `project_config.json` updates (if needed) ✅ COMPLETED
- Added `system_parameters` object with values for system-related params (6 params)
- Added `dcc_global_parameters.json` to schema_files
- Marked `global_parameters.json` as deprecated in schema_files

---

### Phase 4: Config References Update & Archiving

**Objective**: Update `dcc_register_config.json` to use `$ref` instead of inline values, and archive deprecated files

#### 4.1 Update `dcc_register_config.json`

**Current**: Inline `dcc_parameters[0]` array
```json
{
  "dcc_parameters": [
    {
      "fail_fast": false,
      "upload_file_name": "data/..."
    }
  ]
}
```

**Target**: Reference to `dcc_global_parameters.json` (like other independent value files)
```json
{
  "dcc_parameters": {
    "$ref": "https://dcc-pipeline.internal/schemas/dcc_global_parameters#/dcc_parameters"
  }
}
```

#### 4.2 Archive Deprecated File 
- **File:** `global_parameters.json` moved to `dcc/archive/config/schemas/global_parameters_YYYYMMDD_HHMMSS.json`
- **Reason:** Deprecated after migration to domain-separated schema structure
- **Status:** Successfully archived maintaining folder structure

---

### Phase 5: Code Updates ✅ COMPLETED

**Objective**: Update all Python functions to use new schema structure with consistent naming

**Status:** All Python files updated to support dual-domain parameter loading with `dcc_` and `system_` prefixes.

**Summary:**
- bootstrap.py: Registry loads from `dcc_register_setup.json` and `project_setup.json`
- parameter_type_registry.py: Unified registry with `load_from_schema(dcc_schema_path, system_schema_path)`
- cli/__init__.py: `resolve_effective_parameters(dcc_schema_path, ..., system_params_path)`
- schema_loader.py: `load_schema_parameters(schema_path, key=None)` with $ref resolution

#### Naming Convention Established

All code now uses consistent prefixes:

| Domain | Prefix | Variable Examples | File Examples |
|:---|:---|:---|:---|
| **System** | `system_` | `system_params_path`, `system_parameters`, `system_schema_path` | `project_setup.json`, `project_config.json` |
| **DCC** | `dcc_` | `dcc_params_path`, `dcc_parameters`, `dcc_schema_path` | `dcc_register_setup.json`, `dcc_register_config.json`, `dcc_global_parameters.json` |

#### 5.1 bootstrap.py Changes ✅ COMPLETED

| Current | Change |
|:---|:---|
| Loads `dcc_global_parameters.json` for registry (metadata) | Load `dcc_register_setup.json` for registry (structure) |
| Loads `dcc_register_config.json#/global_parameters[0]` for values | Load `dcc_global_parameters.json#/global_parameters` for values |

**Line 656**: 
```python
# FROM:
schema_params_path = self.base_path / "config" / "schemas" / "dcc_global_parameters.json"
# TO:
schema_params_path = self.base_path / "config" / "schemas" / "dcc_register_setup.json"
```

**Value loading**:
```python
# Add support for $ref resolution
global_params = resolve_ref(dcc_register_config, "global_parameters")
# Or directly load dcc_global_parameters.json
```

#### 5.2 parameter_type_registry.py Changes

| Current | Change |
|:---|:---|
| Loads from `dcc_global_parameters.json` | Load from `dcc_register_setup.json` |
| Expects array of parameter definitions | Expects `properties.global_parameters` structure |

#### 5.3 resolve_effective_parameters Changes

| Current | Change |
|:---|:---|
| Merges CLI → `dcc_register_config#/global_parameters[0]` → native defaults | Merges CLI → `dcc_global_parameters.json#/global_parameters` → native defaults |

---

### Reference Architecture

#### Final File Structure

```
dcc/config/schemas/
├── SYSTEM/INFRASTRUCTURE
│   ├── project_setup_base.json
│   │   └── definitions
│   │       ├── system_parameter_entry  (from global_parameters_entry)
│   │       ├── folder_entry
│   │       └── file_entry
│   ├── project_setup.json
│   │   └── properties
│   │       └── system_parameters[]
│   └── project_config.json
│       └── system_parameters {values}
│
├── DATA PROCESSING/DCC
│   ├── dcc_register_base.json
│   │   └── definitions
│   │       ├── processing_parameter_entry  (from global_parameters_entry)
│   │       ├── column_groups_entry
│   │       ├── department_entry
│   │       ├── discipline_entry
│   │       └── approval_entry
│   ├── dcc_register_setup.json
│   │   └── properties
│   │       ├── global_parameters[]  (structure, from dcc_global_parameters.json metadata)
│   │       ├── departments
│   │       ├── disciplines
│   │       └── approval_codes
│   ├── dcc_global_parameters.json  ← KEEP (transformed to values file)
│   │   └── global_parameters {values only}
│   └── dcc_register_config.json
│       ├── global_parameters: {$ref: dcc_global_parameters.json}  ← Reference, not inline
│       ├── departments: {$ref: department_schema}
│       ├── disciplines: {$ref: discipline_schema}
│       └── columns
│
└── REFERENCE DATA (independent value files - KEEP ALL)
    ├── approval_code_schema.json
    ├── department_schema.json
    ├── discipline_schema.json
    ├── document_type_schema.json
    ├── facility_schema.json
    └── project_code_schema.json
```

#### Reference Chain (Data Processing)

```
dcc_register_config.json
    ├── global_parameters: {$ref: dcc_global_parameters.json#/global_parameters}
    │       └── {actual values: upload_file_name, start_col, etc.}
    ├── departments: {$ref: department_schema#/departments}
    ├── disciplines: {$ref: discipline_schema#/disciplines}
    └── columns: [inline]

bootstrap.py
    ├── Loads registry from: dcc_register_setup.json
    │       └── Uses: dcc_register_base#/definitions/processing_parameter_entry
    │       └── Reads: properties.global_parameters[] structure
    │
    └── Loads values from: dcc_global_parameters.json (resolved via dcc_register_config)
            └── Uses: global_parameters {values}
```

---

## Implementation Phases

| Phase | Duration | Dependencies | Description |
|:---|:---|:---|:---|:---|
| 1. Domain Classification & Definition Migration | 2 hours | None | Categorize all 44 parameters, update base definitions |
| 2. Property Schema Updates | 3 hours | Phase 1 | Move metadata to dcc_register_setup, system to project_setup |
| 3. Value File Restructuring | 2 hours | Phase 2 | Transform dcc_global_parameters.json to values-only |
| 4. Config References Update | 2 hours | Phase 3 | Update dcc_register_config.json with $ref |
| 5. Code Updates | 3 hours | Phase 4 | Update all affected functions (see "Affected Functions" section) |
| 6. Testing & Validation | 7 hours | Phase 5 | Comprehensive testing (see Phase 6 sub-phases below) |

### Phase 6 Sub-Phases (Testing & Validation)

| Sub-Phase | Duration | Dependencies | Description |
|:---|:---|:---|:---|
| 6.1 Unit Function Testing | 2 hours | Phase 5 | Test modified functions in isolation |
| 6.2 Bootstrap Testing | 1 hour | Phase 6.1 | Test bootstrap phases P1-P8 |
| 6.3 Main Pipeline Testing | 2 hours | Phase 6.2 | Test full pipeline with various CLI args |
| 6.4 Integration & Regression | 2 hours | Phase 6.3 | Full regression test, schema validation |

**Total Estimated Time**: 19 hours

**Critical Path**: All Phase 6 sub-phases (6.1 → 6.2 → 6.3 → 6.4) must pass before final approval.

---

## Risk Assessment

| Risk | Impact | Mitigation |
|:---|:---|:---|
| Parameter classification error | Medium | Review list with user before Phase 1 |
| Missing parameter after split | High | Comprehensive testing of all 44 params |
| $ref resolution complexity | Medium | Implement or use existing resolver |
| CLI backward compatibility | High | Maintain CLI arg names, internal mapping only |

---

## Files to Create/Modify

### Files to Modify
| File | Changes |
|:---|:---|
| `project_setup_base.json` | Add `system_parameter_entry`, remove `global_parameters_entry` |
| `project_setup.json` | Add `system_parameters` property |
| `project_config.json` | Add `system_parameters` values |
| `dcc_register_base.json` | Add `processing_parameter_entry` |
| `dcc_register_setup.json` | Add detailed `global_parameters[]` structure |
| `dcc_global_parameters.json` | **Transform to values-only** (major change) |
| `dcc_register_config.json` | Change `global_parameters` to `$ref` |
| `utility_engine/bootstrap.py` | Update registry and value loading |
| `utility_engine/cli/__init__.py` | Update parameter resolution |
| `parameter_type_registry.py` | Update schema loading path |
| `core_engine/schema_paths.py` | Update `global_parameters` property path |
| `schema_engine/loader/schema_loader.py` | Update `load_schema_parameters` for new structure |
| `initiation_engine/utils/parameters.py` | Update parameter loading logic |
| `dcc_engine_pipeline.py` | Verify pipeline initialization |

---

## Affected Functions — Check & Revise

These functions directly read the schema files being modified. Each must be checked and revised during Phase 5 (Code Updates).

### Category 1: Registry Loading (CRITICAL)

| Function | File | Line | Current Behavior | Required Change |
|:---|:---|:---:|:---|:---|
| `load_from_schema()` | `parameter_type_registry.py` | 123 | Loads metadata + params from `global_parameters.json` | Load structure from `dcc_register_setup.json#/properties/global_parameters` |
| `get_parameter_registry()` | `parameter_type_registry.py` | 298 | Singleton accessing `global_parameters.json` | Access `dcc_register_setup.json` for structure |
| `_bootstrap_registry()` | `bootstrap.py` | 656 | Loads `global_parameters.json` for registry | Load `dcc_register_setup.json` |

### Category 2: Parameter Resolution (CRITICAL)

| Function | File | Line | Current Behavior | Required Change |
|:---|:---|:---:|:---|:---|
| `load_schema_parameters()` | `schema_loader.py` | 420 | Returns `global_parameters[0]` from dcc_register_config | Support `$ref` resolution to `global_parameters.json` |
| `resolve_effective_parameters()` | `cli/__init__.py` | 629 | Merges CLI + schema params + defaults | Support dual domains (system + processing params) |
| `get_canonical_key()` | `cli/__init__.py` | 74 | Uses registry for key resolution | Verify registry source change doesn't break |

### Category 3: Path Resolution (MEDIUM)

| Function | File | Line | Current Behavior | Required Change |
|:---|:---|:---:|:---|:---|
| `global_parameters` | `schema_paths.py` | 63 | Returns path to `global_parameters.json` | Keep but document new role (values-only) |
| `check_all_schemas_exist()` | `schema_paths.py` | 119 | Checks `global_parameters` exists | Add check for `dcc_register_setup.json` |
| `SchemaPaths` properties | `schema_paths.py` | various | Returns schema file paths | Add `dcc_register_setup` property if missing |

### Category 4: Parameter Access (MEDIUM)

| Function | File | Line | Current Behavior | Required Change |
|:---|:---|:---:|:---|:---|
| `get_processing_config()` | `initiation_engine/utils/parameters.py` | TBD | Loads processing parameters | Split to system vs processing sources |
| `get_system_config()` | `initiation_engine/utils/parameters.py` | TBD | May load from project_config | Verify source separation |

### Category 5: Validation (LOW)

| Function | File | Line | Current Behavior | Required Change |
|:---|:---|:---:|:---|:---|
| `validate_schema()` | `schema_validator.py` | TBD | Validates schema files | Add validation for new structure |
| `SchemaValidator` | `initiation_engine/core/validator.py` | TBD | Schema validation | Update for domain-separated schemas |

---

### Files to Keep (Unchanged)
| File | Role |
|:---|:---|
| `approval_code_schema.json` | Independent values file (correct pattern) |
| `department_schema.json` | Independent values file (correct pattern) |
| `discipline_schema.json` | Independent values file (correct pattern) |
| `document_type_schema.json` | Independent values file (correct pattern) |
| `facility_schema.json` | Independent values file (correct pattern) |
| `project_code_schema.json` | Independent values file (correct pattern) |
| `error_code_base.json` | Error code definitions |
| `error_code_setup.json` | Error code properties |
| `data_error_config.json` | Error code values |
| `system_error_config.json` | System error values |

---

## Testing Checklist

- [ ] All 44 parameters correctly classified (system vs processing)
- [ ] System parameters load from `project_config.json`
- [ ] Processing parameters load from `global_parameters.json`
- [ ] Bootstrap registry loads from `dcc_register_setup.json`
- [ ] `$ref` resolution works for `global_parameters` in `dcc_register_config.json`
- [ ] CLI arguments work for all parameters
- [ ] Pipeline runs successfully (nrows=10)
- [ ] Schema validation passes
- [ ] No duplicate parameter definitions
- [ ] Backward compatibility maintained
- [ ] **Function Tests**: All affected functions pass unit tests
- [ ] **Bootstrap Tests**: P1-P8 phases complete without errors
- [ ] **Pipeline Tests**: Main pipeline runs with various CLI args
- [ ] **Regression Tests**: No breaking changes in existing workflows

---

## Approval Required

**This workplan requires approval before proceeding.**

Please review:
1. **Domain separation approach** (System vs Data Processing)
2. **Parameter classification** (need to verify all 44 parameters — currently 6 system + 18 processing listed)
3. **Global parameters as independent value file** (like department_schema, etc.)
4. **Reference architecture** (dcc_register_config → global_parameters.json via $ref)
5. **Affected functions** (15 functions across 8 files to modify)
6. **Testing coverage** (unit → bootstrap → pipeline → regression)
7. **Implementation phases and timeline** (19 hours total)

**Approve / Request Changes / Reject**

---

*Created per agent_rule.md Section 4 (Module Design)*  
*Date: 2026-05-02*  
*Revision: 2.0 - Domain Separation Approach*
