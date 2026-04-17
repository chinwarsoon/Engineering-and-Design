# Phase 7 Report — ColumnMapperEngine Schema Integration Verification

**Status:** ✅ COMPLETE
**Completed:** 2026-04-17
**Files Modified:**
- `workflow/mapper_engine/core/engine.py`
- `workflow/mapper_engine/mappers/detection.py`

---

## Objective

Verify and fix `ColumnMapperEngine` to work correctly with the new `resolved_schema` structure. Two issues were found and fixed:
1. `engine.py` `detect_columns()` still used `enhanced_schema.columns` wrapper
2. `detection.py` `extract_categorical_choices()` still used legacy `_data` suffix for categorical choices

---

## Changes Made

### `engine.py` — `ColumnMapperEngine.detect_columns()`

**Before:**
```python
enhanced_schema = self.resolved_schema.get('enhanced_schema', {})
columns = enhanced_schema.get('columns', {})
```

**After:**
```python
_schema_root = self.resolved_schema if 'columns' in self.resolved_schema else self.resolved_schema.get('enhanced_schema', {})
columns = _schema_root.get('columns', {})
```

### `detection.py` — `extract_categorical_choices()`

Added `_ref_key_map` to resolve choices from new top-level lists first, with full legacy `_data` suffix fallback:

```python
_ref_key_map = {
    'approval_code_schema': 'approval_codes',
    'department_schema':    'departments',
    'discipline_schema':    'disciplines',
    'facility_schema':      'facilities',
    'document_type_schema': 'document_types',
    'project_code_schema':  'projects',
}
# New architecture: top-level list
top_key = _ref_key_map.get(schema_ref)
if top_key and isinstance(resolved_schema.get(top_key), list):
    entries = resolved_schema[top_key]
    code_field = 'prefix' if schema_ref == 'facility_schema' else 'code'
    mapping['choices'] = [item.get(code_field) for item in entries ...]
    ...
    continue
# Legacy fallback: _data suffix
schema_data = resolved_schema.get(f'{schema_ref}_data')
...
```

Note: `facility_schema` uses `prefix` as the code field (not `code`) — handled explicitly.

---

## Test Results (against `data/Submittal and RFI Tracker Lists.xlsx`)

| Assertion | Expected | Actual | Pass |
|---|---|---|---|
| Excel rows loaded | > 0 | 11,099 | ✅ |
| Excel cols loaded | > 0 | 26 | ✅ |
| `match_rate` | ≥ 80% | **100.0%** | ✅ |
| `matched_count` | > 0 | 26 | ✅ |
| `unmatched_headers` | `[]` | `[]` | ✅ |
| `categorical cols with choices` | > 0 | 5 | ✅ |
| `len(columns in schema)` | 47 | 47 | ✅ |

**Note:** `Document_Title` is listed as `missing_required` — this is expected behaviour as the column does not exist in the source Excel file. The schema marks it `required: true` but `create_if_missing: true`, so it will be created by `initialize_missing_columns` during processing.

---

## Backward Compatibility

- Legacy schemas with `enhanced_schema.columns` still work via fallback in `detect_columns()`
- Legacy schemas with `_data` suffix still work via fallback in `extract_categorical_choices()`

---

*Report generated: 2026-04-17*
