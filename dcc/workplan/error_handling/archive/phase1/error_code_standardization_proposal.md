# Error Code Standardization Proposal

**Date:** 2026-04-24  
**Status:** PENDING APPROVAL  
**Scope:** Standardize all error codes to unified E-M-F-XXXX format including System and Data/Logic errors

---

## Executive Summary

This proposal standardizes ALL error codes across the DCC pipeline to a unified `E-M-F-XXXX` format:
- **System Errors** (initiation_engine): `S-C-S-XXXX` format (already compliant)
- **Data/Logic Errors** (processor_engine): `LL-M-F-XXXX` format (needs migration)
- **Total codes to standardize**: 20 system + 17 data/logic = 37 error codes

---

## 1. Current State Analysis

### 1.1 Four Competing Systems Detected

| System | Format | Example | Location | Status |
|--------|--------|---------|----------|--------|
| **System Errors** | S-C-S-XXXX | `S-E-S-0101` | initiation_engine | ✅ **Already Compliant** |
| **L3xx Pattern** | L3-L-P-0301 | `L3-L-P-0301` | row_validator.py (1 code) | ❌ Inconsistent with schema |
| **E-M-F-XXXX** | E-M-F-XXXX | `P-C-P-0101` | Tests, examples | ✅ Matches anatomy_schema.json |
| **String Codes** | WORD_WORD | `CLOSED_WITH_PLAN_DATE` | row_validator.py (5 codes) | ❌ Not in any schema |
| **Legacy VAL/SYS** | XXX-NNN | `VAL-001` | error_codes.json | ❌ Stub only, 2 entries |

### 1.2 Code Usage Inventory

#### System Errors (initiation_engine) — ✅ ALREADY COMPLIANT
| Code | Category | Severity | Description |
|------|----------|----------|-------------|
| `S-E-S-0101` | Environment | FATAL | MISSING_PACKAGE |
| `S-E-S-0102` | Environment | FATAL | WRONG_PYTHON_VERSION |
| `S-E-S-0103` | Environment | FATAL | ENV_TEST_FAILED |
| `S-E-S-0104` | Environment | FATAL | IMPORT_ERROR |
| `S-F-S-0201` | File | FATAL | INPUT_FILE_NOT_FOUND |
| `S-F-S-0202` | File | FATAL | INPUT_FILE_UNREADABLE |
| `S-F-S-0203` | File | FATAL | OUTPUT_DIR_NOT_WRITABLE |
| `S-F-S-0204` | File | FATAL | SCHEMA_FILE_NOT_FOUND |
| `S-F-S-0205` | File | FATAL | CONFIG_FILE_NOT_FOUND |
| `S-C-S-0301` | Config | FATAL | INVALID_PARAMETER |
| `S-C-S-0302` | Config | FATAL | SCHEMA_PARSE_ERROR |
| `S-C-S-0303` | Config | FATAL | SCHEMA_VALIDATION_FAILED |
| `S-C-S-0304` | Config | FATAL | MISSING_REQUIRED_CONFIG |
| `S-C-S-0305` | Config | FATAL | PROJECT_SETUP_FAILED |
| `S-R-S-0401` | Runtime | FATAL | STEP_EXCEPTION_INIT |
| `S-R-S-0404` | Runtime | FATAL | STEP_EXCEPTION_SCHEMA |
| `S-R-S-0405` | Runtime | FATAL | STEP_EXCEPTION_MAPPING |
| `S-R-S-0406` | Runtime | FATAL | STEP_EXCEPTION_PROC |
| `S-R-S-0402` | Runtime | FATAL | FAIL_FAST_TRIGGERED |
| `S-R-S-0403` | Runtime | FATAL | MEMORY_ERROR |
| `S-A-S-0501` | AI | WARNING | AI_OPS_FAILED |
| `S-A-S-0502` | AI | WARNING | DUCKDB_UNAVAILABLE |
| `S-A-S-0503` | AI | WARNING | OLLAMA_UNAVAILABLE |

#### Data/Logic Errors (processor_engine) — NEEDS MIGRATION
| Code | Location | Layer | Module | Function |
|------|----------|-------|--------|----------|
| `P1-A-P-0101` | row_validator.py:154 | P1 (Phase 1) | A (Anchor) | P (Process) |
| `P2-I-V-0204` | row_validator.py:199,219 | P2 (Phase 2) | I (Identity) | V (Validate) |
| `L3-L-P-0301` | row_validator.py:254 | L3 (Layer 3) | L (Logic) | P (Process) |
| `S1-I-F-0804` | input.py:109 | S1 (System) | I (Input) | F (File) |
| `S1-I-F-0805` | input.py:125,145 | S1 | I | F |
| `S1-I-V-0501` | input.py:167 | S1 | I | V (Validate) |
| `S1-I-V-0502` | input.py:195,212,245 | S1 | I | V |
| `V5-I-V-0501` | schema.py:114,141,358 | V5 (Validation) | I | V |
| `V5-I-V-0502` | schema.py:191,209 | V5 | I | V |
| `V5-I-V-0503` | schema.py:260 | V5 | I | V |
| `V5-I-V-0504` | schema.py:301 | V5 | I | V |

#### String Codes (Non-Compliant)
| Code | Location | Proposed Standardization |
|------|----------|--------------------------|
| `CLOSED_WITH_PLAN_DATE` | row_validator.py:289 | `L3-L-V-0302` |
| `RESUBMISSION_MISMATCH` | row_validator.py:322 | `L3-L-V-0303` |
| `OVERDUE_MISMATCH` | row_validator.py:369 | `L3-L-V-0304` |
| `VERSION_REGRESSION` | row_validator.py:472 | `L3-L-V-0305` |
| `REVISION_GAP` | row_validator.py:531 | `L3-L-V-0306` |
| `CLOSED_WITH_RESUBMISSION` | (proposed new) | `L3-L-V-0307` |

### 1.3 Schema vs Reality Mismatch

**anatomy_schema.json** defines:
- Engine codes: P, M, I, S, R, H, V
- Module codes: C, V, A, D, S, F, L, G, E, P
- Function codes: P, V, C, F
- Format: `^[A-Z]-[A-Z]-[A-Z]-[0-9]{4}$`

**Actual usage** includes:
- 2-character engines: P1, P2, L3, S1, V5 (❌ violates single-letter rule)
- 1-character modules: A, I, L (❌ not in module enum)

### 1.4 JSON Configuration Gaps

| File | Status | Issue |
|------|--------|-------|
| `error_codes.json` | ❌ Stub | Only 2 entries (VAL-001, SYS-001), wrong format |
| `taxonomy.json` | ⚠️ Unused | E-M-F-U format not aligned with E-M-F-XXXX |
| `anatomy_schema.json` | ✅ Valid | Correct schema but codes don't follow it |
| `messages/en.json` | ⚠️ Mismatch | Uses descriptive keys, not error codes |

---

## 2. Standardization Options

### Option A: Strict E-M-F-XXXX Compliance
Convert ALL codes to strict `^[A-Z]-[A-Z]-[A-Z]-[0-9]{4}$` format.

**Changes Required:**
- `P1-A-P-0101` → `P-A-P-0101` (drop numeric from engine)
- `L3-L-P-0301` → `L-L-P-0301` (L becomes engine, not layer)
- Add engine codes: 1, 2, 3, 5 to anatomy_schema.json OR
- Rename engines to single letters: A (Anchor), I (Identity), L (Logic), etc.

**Pros:** Schema-compliant, consistent  
**Cons:** Loss of phase/layer information, breaking change

### Option B: Extended Format (RECOMMENDED)
Adopt `LL-M-F-XXXX` where LL = Layer/Phase (2 chars), M = Module, F = Function.

**Pattern:** `^[A-Z0-9]{2}-[A-Z]-[A-Z]-[0-9]{4}$`

**Mappings:**
| Current | Standardized | Meaning |
|---------|--------------|---------|
| P1 | P1 | Phase 1 (Input) |
| P2 | P2 | Phase 2 (Identity) |
| L3 | L3 | Layer 3 (Logic/Output) |
| S1 | S1 | System/Input layer |
| V5 | V5 | Validation layer |

**Pros:** Preserves layer info, matches current usage closely  
**Cons:** Requires updating anatomy_schema.json pattern

### Option C: Hybrid with Namespaces
Use `E-M-F-XXXX` for system errors, descriptive strings for business rules.

**Pros:** Business-readable codes  
**Cons:** Two systems to maintain, no schema validation for strings

---

## 3. Proposed Implementation (Option B Extended)

### 3.1 Unified Error Code Taxonomy

#### Two Complementary Formats:

**1. System Errors (initiation_engine):** `S-C-S-XXXX`
```
S  = System (always 'S')
C  = Category (1 char)
     E = Environment
     F = File
     C = Config
     R = Runtime
     A = AI
S  = System (always 'S')
XXXX = Unique ID (4 digits)
```

**2. Data/Logic Errors (processor_engine):** `LL-M-F-XXXX`
```
LL = Layer/Phase (2 chars)
     P1 = Phase 1 (Input/Anchor)
     P2 = Phase 2 (Identity/Transaction)
     L3 = Layer 3 (Logic/Validation)
     S1 = System Input Detection
     V5 = Schema Validation

M  = Module (1 char)
     A = Anchor
     I = Identity/Input
     L = Logic
     V = Validation
     F = File
     C = Core
     D = Date
     G = Group

F  = Function (1 char)
     P = Process
     V = Validate
     C = Calculate
     F = Fill/Forward

XXXX = Unique ID (4 digits, 0001-9999)
```

#### Complete Code Ranges:

| Range | Type | Count | Status |
|-------|------|-------|--------|
| S-E-S-01xx | System/Environment | 4 | ✅ Defined |
| S-F-S-02xx | System/File | 5 | ✅ Defined |
| S-C-S-03xx | System/Config | 5 | ✅ Defined |
| S-R-S-04xx | System/Runtime | 5 | ✅ Defined |
| S-A-S-05xx | System/AI | 3 | ✅ Defined |
| P1-A-P-01xx | Phase 1/Anchor | 1 | ✅ Active |
| P2-I-V-02xx | Phase 2/Identity | 1 | ✅ Active |
| L3-L-V-03xx | Layer 3/Logic | 7 | 🔧 6 to migrate |
| V5-I-V-05xx | Validation | 4 | ✅ Active |
| S1-I-F-08xx | System Input/File | 2 | ✅ Active |
| S1-I-V-05xx | System Input/Validate | 2 | ✅ Active |

### 3.2 Code Migration Mapping

| Current Code | Current File | New Code | Category |
|--------------|--------------|----------|----------|
| `P1-A-P-0101` | row_validator.py:154 | `P1-A-P-0101` | ✅ Keep |
| `P2-I-V-0204` | row_validator.py:199 | `P2-I-V-0204` | ✅ Keep |
| `L3-L-P-0301` | row_validator.py:254 | `L3-L-P-0301` | ✅ Keep |
| `CLOSED_WITH_PLAN_DATE` | row_validator.py:289 | `L3-L-V-0302` | 🔧 Migrate |
| `RESUBMISSION_MISMATCH` | row_validator.py:322 | `L3-L-V-0303` | 🔧 Migrate |
| `OVERDUE_MISMATCH` | row_validator.py:369 | `L3-L-V-0304` | 🔧 Migrate |
| `VERSION_REGRESSION` | row_validator.py:472 | `L3-L-V-0305` | 🔧 Migrate |
| `REVISION_GAP` | row_validator.py:531 | `L3-L-V-0306` | 🔧 Migrate |
| (new) | (proposed) | `L3-L-V-0307` | ➕ Add |
| `S1-I-F-0804` | input.py:109 | `S1-I-F-0804` | ✅ Keep |
| `S1-I-F-0805` | input.py:125 | `S1-I-F-0805` | ✅ Keep |
| `S1-I-V-0501` | input.py:167 | `S1-I-V-0501` | ✅ Keep |
| `S1-I-V-0502` | input.py:195 | `S1-I-V-0502` | ✅ Keep |
| `V5-I-V-0501` | schema.py:114 | `V5-I-V-0501` | ✅ Keep |
| `V5-I-V-0502` | schema.py:191 | `V5-I-V-0502` | ✅ Keep |
| `V5-I-V-0503` | schema.py:260 | `V5-I-V-0503` | ✅ Keep |
| `V5-I-V-0504` | schema.py:301 | `V5-I-V-0504` | ✅ Keep |

### 3.3 JSON Schema Updates Required

**anatomy_schema.json:**
```json
{
  "definitions": {
    "layer_code": {
      "type": "string",
      "pattern": "^[A-Z0-9]{2}$",
      "description": "2-character layer/phase code (P1, P2, L3, S1, V5)"
    },
    "error_code_format": {
      "type": "string",
      "pattern": "^[A-Z0-9]{2}-[A-Z]-[A-Z]-[0-9]{4}$",
      "description": "Complete error code in LL-M-F-XXXX format"
    }
  }
}
```

**error_codes.json:**
Populate with all 37 error codes (20 system + 17 data/logic) with full metadata.
Include cross-reference to system_error_codes.json for S-X-S-XXXX codes.

### 3.4 Message Mapping

Update `messages/en.json` to use error codes as keys:

```json
{
  "L3-L-V-0302": {
    "message": "Submission_Closed=YES but Resubmission_Plan_Date is set",
    "severity": "HIGH",
    "action": "review_source"
  },
  "L3-L-V-0303": {
    "message": "Review_Status contains REJ but Resubmission_Required is not YES/RESUBMITTED",
    "severity": "MEDIUM",
    "action": "review_source"
  }
}
```

---

## 4. Implementation Plan

### Phase 1: Schema Updates (1.5 hours)
1. Update `anatomy_schema.json` to accept 2-char layer codes
2. Create unified `error_codes.json` with:
   - All 20 system error codes (S-X-S-XXXX)
   - All 17 data/logic error codes (LL-M-F-XXXX)
   - Cross-references between processor_engine and initiation_engine codes
3. Add new code `L3-L-V-0307` for CLOSED_WITH_RESUBMISSION
4. Verify `system_error_codes.json` is consistent with unified taxonomy

### Phase 2: Code Migration (2 hours)
1. Update `row_validator.py`: Replace 5 string codes with standardized codes
2. Update `messages/en.json`: Add entries for new codes
3. Update `messages/system_en.json`: Verify consistency with unified taxonomy
4. Update `workplan/data_validation/row_validation_p2_logic.md`: Reference standardized codes
5. Update `workplan/error_handling/data_error_handling.md`: Reference standardized codes
6. Add cross-reference documentation between system and data error codes

### Phase 3: Testing (1 hour)
1. Run validation tests to ensure codes are recognized
2. Verify error messages display correctly
3. Check error_codes.json validates against anatomy_schema.json

### Phase 4: Documentation (30 min)
1. Update error catalog consolidation plan
2. Document the LL-M-F-XXXX standard
3. Create migration guide for future codes

---

## 5. Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `processor_engine/error_handling/config/anatomy_schema.json` | Update pattern to `^[A-Z0-9]{2}-[A-Z]-[A-Z]-[0-9]{4}$` | HIGH |
| `processor_engine/error_handling/config/error_codes.json` | Add all 37 codes (20 system + 17 data) with metadata | HIGH |
| `initiation_engine/error_handling/config/system_error_codes.json` | Verify consistency with unified taxonomy | HIGH |
| `processor_engine/error_handling/detectors/row_validator.py` | Replace 5 string codes | HIGH |
| `processor_engine/error_handling/config/messages/en.json` | Add entries for migrated codes | MEDIUM |
| `initiation_engine/error_handling/config/messages/system_en.json` | Verify consistency with unified taxonomy | MEDIUM |
| `workplan/data_validation/row_validation_p2_logic.md` | Update code references | MEDIUM |
| `workplan/error_handling/data_error_handling.md` | Update code references | MEDIUM |

---

## 6. Summary

**Current State:** 4 competing error code systems with partial system error compliance  
**Proposed Solution:** Unified taxonomy with:
- **System Errors:** `S-C-S-XXXX` (20 codes, already compliant)  
- **Data/Logic Errors:** `LL-M-F-XXXX` (17 codes, needs migration)  

**Impact:** 
- 6 string codes need migration → LL-M-F-XXXX
- 1 new code to add (L3-L-V-0307)
- 8 JSON files to update
- 20 system codes to include in unified catalog

**Effort:** ~5 hours total (increased due to system error integration)  
**Benefit:** Complete, consistent, schema-validated error taxonomy across entire pipeline

---

**Awaiting approval to proceed with Phase 1.**
