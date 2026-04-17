# Phase 6 Report — Categorical Schema Reference Validation Fix

**Status:** ✅ COMPLETE
**Completed:** 2026-04-17
**File Modified:** `workflow/processor_engine/calculations/validation.py`

---

## Objective

Fix `schema_reference_check` validation for all categorical columns (`Project_Code`, `Facility_Code`, `Document_Type`, `Discipline`, `Department`) to resolve allowed values from the new top-level schema keys instead of the legacy `_data` suffix pattern.

---

## Changes Made

### New: `_SCHEMA_REF_KEY_MAP` constant

Maps schema reference names to top-level resolved schema keys:

```python
_SCHEMA_REF_KEY_MAP = {
    'approval_code_schema': 'approval_codes',
    'department_schema':    'departments',
    'discipline_schema':    'disciplines',
    'facility_schema':      'facilities',
    'document_type_schema': 'document_types',
    'project_code_schema':  'projects',
    'project_schema':       'projects',
}
```

### New: `_get_ref_data(schema_ref, schema_data)` helper

Centralizes all reference data resolution. Returns a normalized dict wrapping the top-level list under a predictable section key, or falls back to legacy `_data` suffix:

```python
def _get_ref_data(schema_ref: str, schema_data: dict) -> dict:
    top_key = _SCHEMA_REF_KEY_MAP.get(schema_ref)
    if top_key and isinstance(schema_data.get(top_key), list):
        section = 'approval' if 'approval' in schema_ref else top_key
        return {section: schema_data[top_key]}
    return schema_data.get(f'{schema_ref}_data', {})
```

### Replaced all `schema_data.get(f'{schema_ref}_data', {})` calls

4 call sites updated to use `_get_ref_data()`:

| Location | Function |
|---|---|
| `starts_with_schema_reference` rule handler | `apply_validation()` |
| `_apply_schema_reference_validation()` | entry point |
| `_get_column_representative_regex()` — schema_reference_check rule | regex builder |
| `_get_column_representative_regex()` — fallback | regex builder |

---

## Reference Mapping Table

| Column | schema_reference | New top-level key | data_section field |
|---|---|---|---|
| `Project_Code` | `project_code_schema` | `projects` | `code` |
| `Facility_Code` | `facility_schema` | `facilities` | `prefix` |
| `Document_Type` | `document_type_schema` | `document_types` | `code` |
| `Discipline` | `discipline_schema` | `disciplines` | `code` |
| `Department` | `department_schema` | `departments` | `code` |
| `Review_Status` | `approval_code_schema` | `approval_codes` | `status` |
| `Approval_Code` | `approval_code_schema` | `approval_codes` | `code` |

---

## Test Results

| Schema Reference | Field | Entries Resolved | Pass |
|---|---|---|---|
| `approval_code_schema` | `code` | 7 | ✅ |
| `department_schema` | `code` | 17 | ✅ |
| `discipline_schema` | `code` | 15 | ✅ |
| `facility_schema` | `prefix` | 97 | ✅ |
| `document_type_schema` | `code` | 15 | ✅ |
| `project_code_schema` | `code` | 2 | ✅ |

---

## Backward Compatibility

- `_get_ref_data()` falls back to `schema_data.get(f'{schema_ref}_data', {})` for legacy schemas
- No changes to `_get_schema_reference_allowed_codes()` — it works with any normalized dict

---

*Report generated: 2026-04-17*
