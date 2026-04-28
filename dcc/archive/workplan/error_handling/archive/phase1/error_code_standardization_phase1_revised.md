# Error Code Standardization — Phase 1 Revised Workplan

**Date:** 2026-04-24  
**Status:** COMPLETED  
**Architecture:** agent_rule.md Section 2.3 Compliant  
**Related:** [rebuild_schema_workplan.md](../schema_processing/rebuild_schema/rebuild_schema_workplan.md)

---

## Architecture Overview

Following **agent_rule.md Section 2.3** schema separation pattern:

```
error_code_base.json      → Definitions (reusable objects)
error_code_setup.json     → Properties (schema structure)
system_error_config.json  → Items (actual system error data)
data_error_config.json    → Items (actual data/logic error data)
```

---

## Files Created

### 1. error_code_base.json (Definitions)

**Location:** `dcc/config/schemas/error_code_base.json`  
**URI:** `https://dcc-pipeline.internal/schemas/error-code/base`

**Contains 8 definitions:**
| Definition | Purpose |
|------------|---------|
| `layer_code` | 2-character layer/phase pattern (P1, P2, L3, S1, V5, S-E, S-F, etc.) |
| `module_code` | Single letter module codes (C, V, A, D, S, F, L, G, E, P, I) |
| `function_code` | Function type codes (P, V, C, F, S) |
| `unique_id` | 4-digit sequential ID pattern |
| `error_severity` | Severity enum (FATAL, CRITICAL, HIGH, MEDIUM, WARNING, INFO) |
| `system_category` | System error categories (Environment, File, Config, Runtime, AI) |
| `error_code_format` | LL-M-F-XXXX pattern for data/logic errors |
| `system_error_code_format` | S-C-S-XXXX pattern for system errors |
| `error_code_components` | Structured components object |
| `system_error_entry` | System error entry structure |
| `data_error_entry` | Data/logic error entry structure |
| `error_category_range` | Range definition for error categories |
| `error_catalog_metadata` | Catalog metadata structure |
| `migration_log_entry` | Migration log structure |

**Features:**
- ✅ `additionalProperties: false` on all definitions
- ✅ Explicit `required` fields defined
- ✅ Strict type validation
- ✅ Pattern-based validation for codes

---

### 2. error_code_setup.json (Properties)

**Location:** `dcc/config/schemas/error_code_setup.json`  
**URI:** `https://dcc-pipeline.internal/schemas/error-code/setup`

**Structure:**
```json
{
  "metadata": { /* Catalog metadata */ },
  "system_error_ranges": { /* 5 category ranges */ },
  "data_error_ranges": { /* 6 layer ranges */ },
  "system_errors": { /* System error entries */ },
  "data_logic_errors": { /* Data/logic error entries */ },
  "migration_log": { /* Migration history */ }
}
```

**Inheritance:**
- Uses `allOf` to inherit from `error_code_base.json`
- All properties reference base definitions via `$ref`
- No inline definitions

---

### 3. system_error_config.json (System Error Data)

**Location:** `dcc/config/schemas/system_error_config.json`  
**URI:** `https://dcc-pipeline.internal/schemas/error-code/system-config`

**Contains:** 20 system error codes (S-C-S-XXXX format)

| Range | Category | Count |
|-------|----------|-------|
| S-E-S-01xx | Environment | 4 codes |
| S-F-S-02xx | File/IO | 5 codes |
| S-C-S-03xx | Config | 5 codes |
| S-R-S-04xx | Runtime | 6 codes |
| S-A-S-05xx | AI/Optional | 3 codes |

**Structure:**
```json
{
  "metadata": { "total_codes": 20, "system_codes": 20, ... },
  "system_error_ranges": { /* ranges */ },
  "system_errors": {
    "S-E-S-0101": { "code": "S-E-S-0101", "name": "MISSING_PACKAGE", ... },
    "S-E-S-0102": { ... },
    ...
  },
  "migration_log": { /* history */ }
}
```

---

### 4. data_error_config.json (Data/Logic Error Data)

**Location:** `dcc/config/schemas/data_error_config.json`  
**URI:** `https://dcc-pipeline.internal/schemas/error-code/data-config`

**Contains:** 17 data/logic error codes (LL-M-F-XXXX format)

| Range | Layer/Phase | Count |
|-------|-------------|-------|
| P1-A-P-01xx | Phase 1 - Anchor | 1 code |
| P2-I-V-02xx | Phase 2 - Identity | 1 code |
| L3-L-V-03xx | Layer 3 - Logic | 7 codes |
| V5-I-V-05xx | Validation - Schema | 4 codes |
| S1-I-F-08xx | System Input - File | 2 codes |
| S1-I-V-05xx | System Input - Validation | 2 codes |

**Migrated String Codes:**
| Old String | New Code |
|------------|----------|
| CLOSED_WITH_PLAN_DATE | L3-L-V-0302 |
| RESUBMISSION_MISMATCH | L3-L-V-0303 |
| OVERDUE_MISMATCH | L3-L-V-0304 |
| VERSION_REGRESSION | L3-L-V-0305 |
| REVISION_GAP | L3-L-V-0306 |

**New Code:**
| Code | Name | Purpose |
|------|------|---------|
| L3-L-V-0307 | CLOSED_WITH_RESUBMISSION | Issue #61 validation |

---

## Schema Inheritance Chain

```
error_code_base.json
    ↓ $ref (definitions)
error_code_setup.json (allOf + properties)
    ↓ $ref (setup schema)
system_error_config.json (actual system error data)
data_error_config.json (actual data/logic error data)
```

---

## Compliance with agent_rule.md

| Rule | Implementation |
|------|----------------|
| **2.3 - Three-file architecture** | ✅ Base (definitions) → Setup (properties) → Config (data) |
| **3 - Flat schema structure** | ✅ Array of objects for error entries |
| **4 - Unified Schema Registry** | ✅ All use `https://dcc-pipeline.internal/schemas/error-code/*` |
| **5 - Schema fragment pattern** | ✅ Base provides fragments, setup references them |
| **6 - Inheritance pattern** | ✅ `allOf` inheritance from base to setup to config |
| **7 - Definitions for reuse** | ✅ 8 reusable definitions in base |
| **9 - additionalProperties: false** | ✅ All objects have strict control |
| **10 - Required fields** | ✅ All entries define required fields |

---

## URI Registry

| File | URI | Type |
|------|-----|------|
| error_code_base.json | `https://dcc-pipeline.internal/schemas/error-code/base` | Base |
| error_code_setup.json | `https://dcc-pipeline.internal/schemas/error-code/setup` | Setup |
| system_error_config.json | `https://dcc-pipeline.internal/schemas/error-code/system-config` | Config |
| data_error_config.json | `https://dcc-pipeline.internal/schemas/error-code/data-config` | Config |

---

## Total Error Codes

| Type | Format | Count | File |
|------|--------|-------|------|
| System | S-C-S-XXXX | 20 | system_error_config.json |
| Data/Logic | LL-M-F-XXXX | 17 | data_error_config.json |
| **Total** | | **37** | |

---

## Migration Summary

**From:**
- `processor_engine/error_handling/config/error_codes.json` (2 stubs + duplicates)
- `initiation_engine/error_handling/config/system_error_codes.json` (20 codes)

**To:**
- `config/schemas/error_code_base.json` (definitions)
- `config/schemas/error_code_setup.json` (properties)
- `config/schemas/system_error_config.json` (20 system codes)
- `config/schemas/data_error_config.json` (17 data/logic codes)

**Benefits:**
1. **No duplication** - System errors referenced, not duplicated
2. **Clear separation** - Definitions, properties, data clearly separated
3. **Schema compliance** - Follows agent_rule.md Section 2.3 exactly
4. **Maintainability** - Changes to base propagate via inheritance
5. **Validation** - Strict schema validation at all levels

---

## Phase 2 Tasks (COMPLETED)

| Task | Status | Files Changed |
|------|--------|---------------|
| Update detectors | ✅ Complete | row_validator.py - 5 codes migrated |
| Update messages | ✅ Complete | en.json, zh.json - error_codes section added |
| Update documentation | ✅ Complete | Workplan updated |
| Archive old files | ✅ Complete | Moved to dcc/archive/workflow/ |

**Phase 2 Changes:**
- `row_validator.py`: String codes → Standardized codes (L3-L-V-0302 to 0306)
- `messages/en.json`: Added error_codes section with 17 code keys
- `messages/zh.json`: Added error_codes section with 17 code keys (Chinese)
- **Archived old files:**
  - `processor_engine/error_handling/config/error_codes.json` → `archive/workflow/processor_engine/error_handling/config/`
  - `initiation_engine/error_handling/config/system_error_codes.json` → `archive/workflow/initiation_engine/error_handling/config/`

---

## Files Created Summary (Phase 1 + 2)

### Schema Files (Phase 1)
| File | Lines | Purpose |
|------|-------|---------|
| error_code_base.json | ~200 | 8 definitions for reuse |
| error_code_setup.json | ~70 | Properties structure |
| system_error_config.json | ~180 | 20 system error values |
| data_error_config.json | ~260 | 17 data/logic error values |

### Code Files (Phase 2)
| File | Lines Changed | Purpose |
|------|---------------|---------|
| row_validator.py | ~30 | Migrated 5 string codes to standardized codes |
| messages/en.json | ~20 | Added error_codes section |
| messages/zh.json | ~20 | Added error_codes section (Chinese) |

**Total:** 4 new schema files, 3 updated code files, 37 error codes, 100% agent_rule.md compliant

---

**Status:** Phase 1 ✅ COMPLETE | Phase 2 ✅ COMPLETE | Phase 3 ✅ COMPLETE

---

## Phase 3 Tasks (COMPLETED)

| Task | Status | Results |
|------|--------|---------|
| Schema validation | ✅ Complete | 4/4 files valid |
| Format validation | ✅ Complete | 5/5 codes valid |
| Migration verification | ✅ Complete | 5/5 codes migrated |
| Message resolution | ✅ Complete | 17/17 messages per locale |
| Code integration | ✅ Complete | 6/6 codes in row_validator.py |
| Health score weights | ✅ Complete | 5/5 codes in ROW_ERROR_WEIGHTS |

**Phase 3 Test Results:**
- **Total Tests:** 28
- **Passed:** 28
- **Failed:** 0
- **Pass Rate:** 100%

**Test Artifacts:**
- Test workplan: `error_code_standardization_phase3_testing.md`
- Test report: `report/phase3_testing_report.md`
