# Phase 5 Report — Approval Code Reference Resolution

**Status:** ✅ COMPLETE
**Completed:** 2026-04-17
**Files Modified:**
- `workflow/processor_engine/core/base.py`
- `workflow/processor_engine/calculations/mapping.py`

---

## Objective

Fix all approval code lookups to use the new top-level `approval_codes` list directly instead of the legacy `approval_code_schema_data.approval` pattern.

---

## Changes Made

### `base.py` — `BaseProcessor._resolve_schema_reference()`

Added `_new_key_map` dict mapping schema names to top-level resolved schema keys. Lookup now checks top-level list first, falls back to legacy `_data` suffix pattern:

```python
_new_key_map = {
    'approval_code_schema': 'approval_codes',
    'department_schema':    'departments',
    'discipline_schema':    'disciplines',
    'facility_schema':      'facilities',
    'document_type_schema': 'document_types',
    'project_code_schema':  'projects',
}
top_level_key = _new_key_map.get(schema_name)
if top_level_key and isinstance(self.schema_data.get(top_level_key), list):
    entries = self.schema_data[top_level_key]
else:
    ref_schema_data = self.schema_data.get(f'{schema_name}_data', {})
    entries = ref_schema_data.get(data_section, [])
```

### `mapping.py` — `apply_mapping_calculation()`

Fixed approval code mapping build loop to check top-level `approval_codes` first:

**Before:**
```python
ref_data = engine.schema_data.get(f'{mapping_ref}_data', {})
if ref_data:
    approval_rows = ref_data.get('approval', [])
```

**After:**
```python
_new_key_map = {'approval_code_schema': 'approval_codes'}
top_key = _new_key_map.get(mapping_ref)
if top_key and isinstance(engine.schema_data.get(top_key), list):
    approval_rows = engine.schema_data[top_key]
else:
    ref_data = engine.schema_data.get(f'{mapping_ref}_data', {})
    approval_rows = ref_data.get('approval', [])
```

---

## Test Results

| Assertion | Expected | Actual | Pass |
|---|---|---|---|
| `_resolve_schema_reference(PEN, status)` | `"Awaiting S.O.'s response"` | `"Awaiting S.O.'s response"` | ✅ |
| `_resolve_schema_reference(APP, status)` | `"Approved"` | `"Approved"` | ✅ |
| `_resolve_schema_reference(AWC, code)` | `"AWC"` | `"AWC"` | ✅ |
| `mapping["Approved"]` | `"APP"` | `"APP"` | ✅ |
| `mapping["Pending"]` | `"PEN"` | `"PEN"` | ✅ |
| `mapping["Void"]` | `"VOID"` | `"VOID"` | ✅ |

---

## Backward Compatibility

- All lookups fall back to legacy `_data` suffix pattern if top-level key not present

---

*Report generated: 2026-04-17*
