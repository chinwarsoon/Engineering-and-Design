# Error Catalog Consolidation Plan

**Version:** 2.0
**Date:** 2026-04-24
**Status:** PHASES 1-3 COMPLETE, Phase 4 Consolidation in Progress
**Scope:** `dcc/workflow/processor_engine/error_handling/config/`

---

## 📋 Quick Links (New Consolidated Documentation)

| Document | Purpose | Status |
|----------|---------|--------|
| [README.md](../README.md) | Master documentation index | NEW |
| [Error Handling Taxonomy](../error_handling_taxonomy.md) | Complete error code reference | NEW |
| [Consolidated Implementation Report](../reports/consolidated_implementation_report.md) | All phases summary | NEW |
| [Phase 4 Workplan](../error_code_standardization_phase4_consolidation.md) | Consolidation tasks | NEW |

---

## 🎉 Phase 1-3 Completion Summary

### What Was Accomplished

| Phase | Description | Key Deliverables | Status |
|-------|-------------|------------------|--------|
| **Phase 1** | Schema Architecture | 4 schema files (agent_rule.md compliant), 37 error codes defined | ✅ COMPLETE |
| **Phase 2** | Code Migration | 5 string codes migrated, messages in 2 languages | ✅ COMPLETE |
| **Phase 3** | Testing & Validation | 28 tests, 100% pass rate | ✅ COMPLETE |

### New Schema Architecture

**Files Created in `dcc/config/schemas/`:**
- `error_code_base.json` - 8 reusable definitions
- `error_code_setup.json` - Properties structure (allOf)
- `system_error_config.json` - 20 system error codes (S-C-S-XXXX)
- `data_error_config.json` - 17 data/logic error codes (LL-M-F-XXXX)

**Files Archived:**
- `error_codes.json` → `archive/workflow/processor_engine/error_handling/config/`
- `system_error_codes.json` → `archive/workflow/initiation_engine/error_handling/config/`

### Migrations Completed

| Old String Code | New Standard Code | Status |
|-----------------|-------------------|--------|
| CLOSED_WITH_PLAN_DATE | L3-L-V-0302 | ✅ Migrated |
| RESUBMISSION_MISMATCH | L3-L-V-0303 | ✅ Migrated |
| OVERDUE_MISMATCH | L3-L-V-0304 | ✅ Migrated |
| VERSION_REGRESSION | L3-L-V-0305 | ✅ Migrated |
| REVISION_GAP | L3-L-V-0306 | ✅ Migrated |

### Test Results

| Category | Tests | Passed | Failed |
|----------|-------|--------|--------|
| Schema Validation | 4 | 4 | 0 |
| Format Validation | 5 | 5 | 0 |
| Migration Verification | 5 | 5 | 0 |
| Message Resolution | 4 | 4 | 0 |
| Code Integration | 5 | 5 | 0 |
| Health Score Weights | 5 | 5 | 0 |
| **TOTAL** | **28** | **28** | **0** |

**Pass Rate:** 100%

---

## 📁 Original Plan (For Reference)

*The following sections document the original consolidation plan. The actual implementation followed a phased approach documented above.*

### 1. Original State Assessment

**Note:** This assessment was made before Phase 1-3 implementation.

---

## 1. Current State Assessment

### 1.1 What exists in `error_codes.json` today

The current `error_codes.json` is a **stub** — it contains only 2 placeholder entries (`VAL-001`, `SYS-001`) using a different format than the actual codebase. It does not reflect any of the real error codes used by the detectors.

```json
"codes": [
  { "code": "VAL-001", "message": "Required field missing", "severity": "error" },
  { "code": "SYS-001", "message": "File not found", "severity": "fatal" }
]
```

The `ErrorRegistry` class (`core/registry.py`) expects an `"errors": {}` dict keyed by code — but the JSON uses a `"codes": []` array. **The registry is currently broken** — `self._errors` is always `{}`.

### 1.2 What exists in `system_error_codes.json` today

The new `initiation_engine/error_handling/config/system_error_codes.json` (created in SE1) contains all 20 system error codes in the correct `"errors": {}` dict format. This is complete and correct.

### 1.3 Actual error codes used in detectors (source of truth)

The following codes are hardcoded as string constants in detector files but **absent from `error_codes.json`**:

#### Group A — E-M-F-XXXX format (24 codes)

| Code | Name | Severity | Detector | Layer |
|------|------|----------|----------|-------|
| `P1-A-P-0101` | NULL_ANCHOR | CRITICAL | anchor.py | L3 |
| `P1-A-V-0102` | INVALID_SESSION_FORMAT | HIGH | anchor.py | L3 |
| `P1-A-V-0103` | INVALID_DATE_FORMAT | HIGH | anchor.py | L3 |
| `P2-I-P-0201` | DOCUMENT_ID_UNCERTAIN | CRITICAL | identity.py | L3 |
| `P2-I-P-0202` | REVISION_MISSING | CRITICAL | identity.py | L3 |
| `P2-I-V-0203` | DUPLICATE_TRANSMITTAL | HIGH | identity.py | L3 |
| `P2-I-V-0204` | DOCUMENT_ID_FORMAT_INVALID | HIGH | identity.py / row_validator.py | L3 |
| `L3-L-P-0301` | DATE_INVERSION | CRITICAL | logic.py / row_validator.py | L3 |
| `L3-L-V-0302` | REVISION_REGRESSION | HIGH | logic.py | L3 |
| `L3-L-V-0303` | STATUS_CONFLICT | HIGH | logic.py | L3 |
| `L3-L-W-0304` | OVERDUE_PENDING | WARNING | logic.py | L3 |
| `F4-C-F-0401` | FILL_JUMP_LIMIT | HIGH | fill.py | L3 |
| `F4-C-F-0402` | FILL_BOUNDARY_CROSS | HIGH | fill.py | L3 |
| `F4-C-F-0403` | FILL_INFERRED | WARNING | fill.py | L3 |
| `F4-C-F-0404` | FILL_EXCESSIVE_NULLS | WARNING | fill.py | L3 |
| `F4-C-F-0405` | FILL_INVALID_GROUPING | ERROR | fill.py | L3 |
| `V5-I-V-0501` | PATTERN_MISMATCH | HIGH | validation.py / schema.py | L2 |
| `V5-I-V-0502` | LENGTH_EXCEEDED | HIGH | validation.py / schema.py | L2 |
| `V5-I-V-0503` | INVALID_ENUM | HIGH | validation.py / schema.py | L2 |
| `V5-I-V-0504` | TYPE_MISMATCH | HIGH | validation.py / schema.py | L2 |
| `V5-I-V-0505` | REQUIRED_MISSING | CRITICAL | validation.py | L2 |
| `V5-I-V-0506` | FOREIGN_KEY_FAIL | HIGH | validation.py | L2 |
| `C6-C-C-0601` | DEPENDENCY_FAIL | CRITICAL | calculation.py | L3 |
| `C6-C-C-0602` | CIRCULAR_DEPENDENCY | CRITICAL | calculation.py | L3 |
| `C6-C-C-0603` | DIVISION_BY_ZERO | HIGH | calculation.py | L3 |
| `C6-C-C-0604` | AGGREGATE_EMPTY | HIGH | calculation.py | L3 |
| `C6-C-C-0605` | DATE_ARITHMETIC_FAIL | HIGH | calculation.py | L3 |
| `C6-C-C-0606` | MAPPING_NO_MATCH | HIGH | calculation.py | L3 |

#### Group B — Named string codes (10 codes, row_validator.py only)

These use plain string names instead of E-M-F-XXXX format. They are also referenced in `ROW_ERROR_WEIGHTS` for health scoring.

| Code (string) | Severity | Weight | Description |
|---------------|----------|--------|-------------|
| `CLOSED_WITH_PLAN_DATE` | HIGH | 10 | Resubmission_Plan_Date set when Submission_Closed=YES |
| `RESUBMISSION_MISMATCH` | MEDIUM | — | REJ status without Resubmission_Required=YES |
| `OVERDUE_MISMATCH` | MEDIUM | 5 | Past plan date but not marked Overdue |
| `GROUP_INCONSISTENT` | MEDIUM | 15 | Submission_Date inconsistent within session |
| `VERSION_REGRESSION` | HIGH | 15 | Document_Revision decreases per Document_ID |
| `REVISION_GAP` | LOW | 5 | Submission_Session_Revision not sequential |
| `INCONSISTENT_SUBJECT` | MEDIUM | 5 | Submission_Session_Subject inconsistent |
| `ANCHOR_NULL` | HIGH | 25 | (weight key only — maps to P1-A-P-0101) |
| `COMPOSITE_MISMATCH` | HIGH | 20 | (weight key only — maps to P2-I-V-0204) |
| `INCONSISTENT_CLOSURE` | HIGH | 10 | (weight key only — no detector yet) |

#### Group C — Input/Schema layer codes (4 codes, input.py / schema.py)

| Code | Severity | Detector |
|------|----------|----------|
| `S1-I-F-0804` | CRITICAL | input.py |
| `S1-I-F-0805` | HIGH | input.py |
| `S1-I-V-0501` | HIGH | input.py |
| `S1-I-V-0502` | CRITICAL | input.py |

#### Group D — Historical codes (3 codes, planned but no detector file yet)

| Code | Description |
|------|-------------|
| `H2-V-H-0201` | Cross-session duplicate Document_ID |
| `H2-V-H-0202` | Revision regression vs history |
| `H2-V-H-0203` | Temporal inconsistency across sessions |

---

## 2. Gap Analysis

| Issue | Impact |
|-------|--------|
| `error_codes.json` is a stub with 2 wrong-format entries | `ErrorRegistry` always returns empty — lookup, scoring, aggregation all broken |
| `ErrorRegistry` expects `"errors": {}` dict but JSON has `"codes": []` array | Registry class unusable |
| 28 E-M-F-XXXX codes used in detectors have no JSON definition | No centralized description, hint, remediation, or rule coverage |
| 10 named string codes in `row_validator.py` not in E-M-F-XXXX format | Inconsistent with taxonomy; cannot be looked up by registry |
| `ROW_ERROR_WEIGHTS` hardcoded in `row_validator.py` | Weights not in JSON — cannot be changed without code edit |
| `en.json` messages exist but are not linked to error codes by key | Messages cannot be resolved via registry |
| `taxonomy.json` uses different engine codes (PR, MA, SC) than detectors (P, M, I) | Taxonomy inconsistent with actual codes |
| `anatomy_schema.json` pattern `^[A-Z]-[A-Z]-[A-Z]-[0-9]{4}$` doesn't match `P1-A-P-0101` (has digit in engine) | Schema validation would reject all real codes |
| `remediation_types.json` has only 4 types (MANUAL, AUTOMATIC, IGNORE, RETRY) vs 8 in workplan | Incomplete |
| No `rule_coverage` field — cannot check which validation rules are covered | Rule coverage check not possible |

---

## 3. Consolidation Plan

### Goal

A single `error_codes.json` that is the **single source of truth** for all data error codes — used by detection, lookup, aggregation, scoring, and rule coverage checks. The `system_error_codes.json` remains separate (different lifecycle, no row-level aggregation).

### 3.1 Fix `error_codes.json` structure

Change from `"codes": []` array to `"errors": {}` dict (matching `ErrorRegistry` expectation):

```json
{
  "version": "2.0",
  "last_updated": "2026-05-01",
  "errors": {
    "P1-A-P-0101": {
      "name": "NULL_ANCHOR",
      "severity": "CRITICAL",
      "layer": "L3",
      "phase": "P1",
      "fail_fast": true,
      "stops_pipeline": false,
      "message_key": "error.anchor.null_project_code",
      "action_key": "action.fix_in_excel",
      "remediation_type": "MANUAL_FIX",
      "health_weight": 25,
      "rule_coverage": ["anchor_null_check"],
      "taxonomy": {
        "engine": "Processor", "engine_code": "P",
        "module": "Core", "module_code": "C",
        "function": "Process", "function_code": "P",
        "family": "Anchor", "family_code": "1"
      },
      "detectors": ["anchor.py", "row_validator.py"]
    }
  }
}
```

### 3.2 Assign E-M-F-XXXX codes to Group B named codes

The 10 named string codes in `row_validator.py` need proper codes. Proposed mapping:

| Current string | Proposed code | Rationale |
|----------------|---------------|-----------|
| `CLOSED_WITH_PLAN_DATE` | `L3-L-V-0305` | Logic layer, business rule |
| `RESUBMISSION_MISMATCH` | `L3-L-V-0306` | Logic layer, business rule |
| `OVERDUE_MISMATCH` | `L3-L-V-0307` | Logic layer, business rule |
| `GROUP_INCONSISTENT` | `L3-L-V-0308` | Logic layer, group consistency |
| `VERSION_REGRESSION` | `L3-L-V-0309` | Logic layer (duplicate of L3-L-V-0302 — merge) |
| `REVISION_GAP` | `L3-L-V-0310` | Logic layer, sequence |
| `INCONSISTENT_SUBJECT` | `L3-L-V-0311` | Logic layer, group consistency |
| `INCONSISTENT_CLOSURE` | `L3-L-V-0312` | Logic layer (weight key, no detector yet) |

Note: `ANCHOR_NULL` and `COMPOSITE_MISMATCH` are weight keys that already map to `P1-A-P-0101` and `P2-I-V-0204` — no new codes needed, just add `health_weight` to those entries.

### 3.3 Add `health_weight` field to all codes

Move `ROW_ERROR_WEIGHTS` from `row_validator.py` into `error_codes.json` as a `health_weight` field on each code. The registry can then provide weights for scoring without hardcoding.

### 3.4 Add `rule_coverage` field for rule coverage checks

Each error code gets a `rule_coverage` list — the validation rules it covers. This enables:
- Checking which rules have no detector (coverage gaps)
- Checking which detectors cover multiple rules (overlap)
- Generating a rule coverage report

```json
"rule_coverage": ["anchor_null_check", "p1_completeness"]
```

### 3.5 Fix `taxonomy.json` engine codes

Update to match actual codes used in detectors:

| Current (wrong) | Correct |
|-----------------|---------|
| `PR` | `P` (Processor) |
| `MA` | `M` (Mapper) |
| `SC` | `S` (Schema) |
| `IN` | `I` (Initiation) |
| `RE` | `R` (Reporting) |

Add missing engines: `H` (Historical), `V` (Validation), `F` (Fill), `L` (Logic).

### 3.6 Fix `anatomy_schema.json` pattern

Current pattern `^[A-Z]-[A-Z]-[A-Z]-[0-9]{4}$` rejects `P1-A-P-0101` (digit in engine position).

Fix: `^[A-Z][0-9]?-[A-Z]-[A-Z]-[0-9]{4}$`

### 3.7 Fix `remediation_types.json`

Replace 4 stub types with the 8 types defined in `error_handling_module_workplan.md`:
AUTO_FIX, MANUAL_FIX, SUPPRESS, ESCALATE, DERIVE, DEFAULT, FILL_DOWN, AGGREGATE.

### 3.8 Link `en.json` message keys to error codes

Each error code entry references a `message_key` (e.g. `"error.anchor.null_project_code"`) and `action_key`. These already exist in `en.json` — the link just needs to be explicit in `error_codes.json` so the registry can resolve messages.

---

## 4. Implementation Phases

### Phase EC1 — Fix `error_codes.json` (all 38 data error codes)
- Rewrite with correct `"errors": {}` dict structure
- Add all 28 E-M-F-XXXX codes (Groups A + C)
- Add 8 new E-M-F-XXXX codes for Group B named codes (L3-L-V-0305 to 0312)
- Add 3 planned H2 history codes
- Add `health_weight`, `rule_coverage`, `message_key`, `action_key`, `remediation_type`, `detectors` fields
- **Files:** `processor_engine/error_handling/config/error_codes.json`

### Phase EC2 — Fix supporting config files
- Fix `taxonomy.json` engine codes
- Fix `anatomy_schema.json` regex pattern
- Fix `remediation_types.json` (8 types)
- **Files:** `taxonomy.json`, `anatomy_schema.json`, `remediation_types.json`

### Phase EC3 — Update `row_validator.py` to use new codes
- Replace 8 named string codes with new `L3-L-V-03XX` codes
- Remove `ROW_ERROR_WEIGHTS` dict (weights now in JSON)
- Add `ErrorRegistry` lookup for weights
- **Files:** `processor_engine/error_handling/detectors/row_validator.py`

### Phase EC4 — Fix `ErrorRegistry` to load new structure
- `_load_registry()` already reads `"errors": {}` — will work once JSON is fixed
- Add `get_health_weight(code)` method
- Add `get_rule_coverage()` method returning coverage map
- Add `get_uncovered_rules()` method for gap detection
- **Files:** `processor_engine/error_handling/core/registry.py`

---

## 5. Acceptance Criteria

- [ ] `ErrorRegistry().get_error("P1-A-P-0101")` returns full definition
- [ ] `ErrorRegistry().get_all_codes()` returns all 38+ data error codes
- [ ] `ErrorRegistry().get_health_weight("P1-A-P-0101")` returns 25
- [ ] `ErrorRegistry().get_rule_coverage()` returns coverage map
- [ ] `row_validator.py` uses no hardcoded string error codes
- [ ] `ROW_ERROR_WEIGHTS` removed from `row_validator.py`
- [ ] `taxonomy.json` engine codes match actual detector codes
- [ ] `anatomy_schema.json` pattern accepts `P1-A-P-0101`
- [ ] `remediation_types.json` has all 8 types

---

## 6. Estimated Effort

| Phase | Effort |
|-------|--------|
| EC1 — Rewrite `error_codes.json` | 3 h |
| EC2 — Fix supporting configs | 1 h |
| EC3 — Update `row_validator.py` | 1 h |
| EC4 — Extend `ErrorRegistry` | 1 h |
| **Total** | **~6 h** |

---

*Last updated: 2026-05-01*
*Status: PENDING APPROVAL*
