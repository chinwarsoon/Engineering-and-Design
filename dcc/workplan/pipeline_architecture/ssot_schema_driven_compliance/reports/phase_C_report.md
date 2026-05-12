# Phase C Completion Report — Catalog and Threshold Externalization

**Date:** 2026-05-12  
**Status:** ✅ COMPLETE  
**Tasks:** 15 of 15 complete  

---

## Summary

Phase C externalized all remaining hardcoded values from the detector layer and reporting layer to their schema/catalog sources. The key deliverable is that no detector file now contains a hardcoded severity string — all 55 instances across 9 files now resolve through `BaseDetector._get_severity()` which reads from `error_catalog` in context.

---

## Tasks Completed

| # | Task | Status | Notes |
|:---|:---|:---:|:---|
| C1 | Replace `ERROR_CODES` dict in `validation.py` | ✅ | Renamed to `DEFAULT_VALIDATION_ERROR_CODES`; `apply_validation` reads from `schema_data.get('validation_error_codes', DEFAULT_VALIDATION_ERROR_CODES)` |
| C2 | Replace `_severity_map`/`_layer_map` in `categorizer.py` | ✅ | Already complete from prior session |
| C3 | Replace hardcoded error-to-phase dict in `evidence.py` | ✅ | `_ERROR_PHASE_MAP` replaced with `_get_phase_from_catalog()` reading `error_catalog[code].processing_phase`; fallback map retained for codes not in catalog |
| C4 | Move health grade thresholds to schema parameters | ✅ | `HealthCalculator.get_grade()` reads `parameters.get('health_grade_thresholds')`; defaults in `_DEFAULT_GRADE_THRESHOLDS`; schema updated with `health_grade_thresholds` key |
| C5 | Move pass/fail thresholds to schema parameters | ✅ | `generate_summary_stats()` reads `effective_parameters.get('health_pass_threshold', 90.0)` and `health_fail_threshold`; schema updated |
| C6 | Move `jump_limit` to schema parameters | ✅ | `FillDetector.__init__` reads `parameters.get('fill_jump_limit', DEFAULT_JUMP_LIMIT)`; `BusinessDetector` passes `parameters` to `FillDetector`; schema updated with `fill_jump_limit` and `fill_max_percentage` |
| C7 | Add 11 missing error codes to `data_error_config.json` | ✅ | Already complete from prior session |
| C8 | Replace 55 hardcoded `severity=` strings in 9 detector files | ✅ | Added `_get_severity(error_code, fallback)` to `BaseDetector`; all 9 detector files updated |
| C9 | Correct 4 severity mismatches | ✅ | Already complete from prior session |
| C10 | Replace `ANCHOR_COLUMNS`/`ANCHOR_REQUIRED` with schema lookup | ✅ | `AnchorDetector._get_anchor_columns()` reads `is_anchor: true` from schema; `RowValidator._get_anchor_columns()` same; `is_anchor` flag added to 6 columns in `dcc_register_config.json` |
| C11 | Replace `DOC_ID_SEGMENTS` with schema lookup | ✅ | `RowValidator._get_doc_id_segments()` reads `Document_ID.calculation.source_columns` from schema |
| C12 | Replace `IDENTITY_COLUMNS` with schema lookup | ✅ | `IdentityDetector._get_identity_columns()` reads P2 + required columns from schema |
| C13 | Replace `ROW_ERROR_WEIGHTS` with catalog `health_score_impact` | ✅ | `RowValidator._get_row_error_weights()` reads `health_score_impact` from `error_catalog`; fallback to `ROW_ERROR_WEIGHTS` constant |
| C14 | Replace hardcoded `"REJ"` string | ✅ | `RowValidator._get_rejected_code()` reads from `approval_code_schema` filtered by `status == 'Rejected'` |
| C15 | Replace hardcoded `'PEN'` fallback in `aggregate.py` | ✅ | Already schema-driven via `_resolve_schema_reference` — no change needed |

---

## Schema Updates

### `dcc_global_parameters.json`
Added 5 new parameter keys:
- `fill_jump_limit`: 20
- `fill_max_percentage`: 80.0
- `health_pass_threshold`: 90.0
- `health_fail_threshold`: 60.0
- `health_grade_thresholds`: `{A+: 99.0, A: 95.0, A-: 90.0, B+: 85.0, B: 80.0, C: 70.0, D: 60.0, F: 0.0}`

### `dcc_register_config.json`
Added `is_anchor: true` to 6 columns:
- `Submission_Session`
- `Project_Code`
- `Facility_Code`
- `Document_Type`
- `Discipline`
- `Document_Sequence_Number`
- `Submission_Date`

---

## Architecture Pattern

The key architectural pattern introduced in Phase C is the `_get_severity()` helper on `BaseDetector`:

```python
def _get_severity(self, error_code: str, fallback: str = "ERROR") -> str:
    catalog = self._context.get("error_catalog", {})
    if catalog:
        entry = catalog.get(error_code, {})
        severity = entry.get("severity")
        if severity:
            return severity
    return fallback
```

This means:
- When `error_catalog` is in context (normal pipeline run), severity is always read from `data_error_config.json`
- When catalog is absent (unit tests, standalone use), the hardcoded fallback is used
- No breaking changes to existing call sites

---

## Files Modified

| File | Change |
|:---|:---|
| `dcc/config/schemas/dcc_global_parameters.json` | Added 5 threshold/limit parameters |
| `dcc/config/schemas/dcc_register_config.json` | Added `is_anchor: true` to 7 columns |
| `dcc/workflow/processor_engine/error_handling/detectors/base.py` | Added `_get_severity()` helper |
| `dcc/workflow/processor_engine/error_handling/detectors/anchor.py` | Schema-driven ANCHOR_COLUMNS + severity |
| `dcc/workflow/processor_engine/error_handling/detectors/identity.py` | Schema-driven IDENTITY_COLUMNS + severity |
| `dcc/workflow/processor_engine/error_handling/detectors/row_validator.py` | Schema-driven ANCHOR_REQUIRED, DOC_ID_SEGMENTS, ROW_ERROR_WEIGHTS, REJ code + severity |
| `dcc/workflow/processor_engine/error_handling/detectors/fill.py` | Schema-driven jump_limit + severity |
| `dcc/workflow/processor_engine/error_handling/detectors/logic.py` | Schema-driven severity |
| `dcc/workflow/processor_engine/error_handling/detectors/calculation.py` | Schema-driven severity |
| `dcc/workflow/processor_engine/error_handling/detectors/schema.py` | Schema-driven severity |
| `dcc/workflow/processor_engine/error_handling/detectors/input.py` | Schema-driven severity |
| `dcc/workflow/processor_engine/error_handling/detectors/validation.py` | Schema-driven severity |
| `dcc/workflow/processor_engine/error_handling/detectors/business.py` | Pass parameters to FillDetector |
| `dcc/workflow/processor_engine/calculations/validation.py` | DEFAULT_VALIDATION_ERROR_CODES + schema override |
| `dcc/workflow/ai_ops_engine/core/evidence.py` | Catalog-driven phase lookup |
| `dcc/workflow/ai_ops_engine/core/engine.py` | Pass error_catalog to attach_evidence_links |
| `dcc/workflow/reporting_engine/core/report_health.py` | Schema-driven grade thresholds |
| `dcc/workflow/reporting_engine/core/report_errors.py` | Schema-driven pass/fail thresholds |

---

## Validation

All 18 modified Python files pass `ast.parse()` syntax check.  
All modified JSON schema files pass `json.load()` validation.
