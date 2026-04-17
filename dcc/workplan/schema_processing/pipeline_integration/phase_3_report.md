# Phase 3 Report — CalculationEngine Schema Key Fix

**Status:** ✅ COMPLETE
**Completed:** 2026-04-17
**Files Modified:**
- `workflow/processor_engine/core/engine.py`
- `workflow/processor_engine/core/base.py`

---

## Objective

Fix `CalculationEngine.__init__` and `apply_phased_processing()` to read `columns` and `column_sequence` directly from the top-level schema instead of the legacy `enhanced_schema` wrapper. Fix `BaseProcessor._resolve_schema_reference()` to look up approval codes from the new top-level `approval_codes` key.

---

## Changes Made

### `engine.py` — `CalculationEngine.__init__`

**Before:**
```python
enhanced_schema = schema_data.get('enhanced_schema', {})
raw_columns = enhanced_schema.get('columns', {})
column_sequence = enhanced_schema.get('column_sequence', [])
```

**After:**
```python
_schema_root = schema_data if 'columns' in schema_data else schema_data.get('enhanced_schema', {})
raw_columns = _schema_root.get('columns', {})
column_sequence = _schema_root.get('column_sequence', [])
```

### `engine.py` — `apply_phased_processing()`

**Before:**
```python
enhanced_schema = self.schema_data.get('enhanced_schema', {})
column_sequence = enhanced_schema.get('column_sequence', [])
```

**After:**
```python
_schema_root = self.schema_data if 'column_sequence' in self.schema_data else self.schema_data.get('enhanced_schema', {})
column_sequence = _schema_root.get('column_sequence', [])
```

### `base.py` — `BaseProcessor._resolve_schema_reference()`

Added `_new_key_map` to translate schema names to top-level keys, with legacy `_data` suffix fallback:

```python
_new_key_map = {
    'approval_code_schema': 'approval_codes',
    'department_schema':    'departments',
    ...
}
top_level_key = _new_key_map.get(schema_name)
if top_level_key and isinstance(self.schema_data.get(top_level_key), list):
    entries = self.schema_data[top_level_key]
else:
    ref_schema_data = self.schema_data.get(f'{schema_name}_data', {})
    entries = ref_schema_data.get(data_section, [])
```

---

## Test Results

| Assertion | Expected | Actual | Pass |
|---|---|---|---|
| `len(engine.columns)` | `47` | `47` | ✅ |
| `'Document_ID' in engine.columns` | `True` | `True` | ✅ |
| `len(engine.calculation_order)` | `25` | `25` | ✅ |
| `len(column_sequence)` | `47` | `47` | ✅ |

---

## Backward Compatibility

- Legacy schemas with `enhanced_schema.columns` still work via fallback
- `_resolve_schema_reference()` falls back to `_data` suffix if top-level key not found

---

*Report generated: 2026-04-17*
