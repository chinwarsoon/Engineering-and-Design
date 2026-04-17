# Phase 2 Report — Global Parameters Normalization

**Status:** ✅ COMPLETE
**Completed:** 2026-04-17
**File Modified:** `workflow/schema_engine/loader/schema_loader.py`

---

## Objective

Fix `load_schema_parameters()` to read from `global_parameters[0]` (array) in the new schema architecture, instead of the legacy `parameters` (dict) key.

---

## Changes Made

### `load_schema_parameters()` in `schema_loader.py`

Added architecture detection with two paths:

- **New architecture:** `global_parameters` is a list → returns `global_parameters[0]`
- **Legacy architecture:** `parameters` is a dict → returns `parameters`
- **Fallback:** returns `{}`

**Before:**
```python
def load_schema_parameters(schema_path: Path) -> Dict[str, Any]:
    with schema_path.open("r", encoding="utf-8") as handle:
        return json.load(handle).get("parameters", {})
```

**After:**
```python
def load_schema_parameters(schema_path: Path) -> Dict[str, Any]:
    with schema_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    # New architecture: global_parameters is an array
    gp = data.get("global_parameters")
    if isinstance(gp, list) and gp and isinstance(gp[0], dict):
        return gp[0]

    # Legacy architecture: parameters is a dict
    params = data.get("parameters", {})
    if isinstance(params, dict):
        return params

    return {}
```

### `_normalize_resolved_schema()` in `schema_validator.py` *(Phase 1 contribution)*

Also handles `global_parameters` → `parameters` normalization within the resolved schema object, ensuring `CalculationEngine` receives `schema_data['parameters']` correctly.

---

## Note on `resolve_effective_parameters()`

`resolve_effective_parameters()` in `initiation_engine/utils/parameters.py` did **not** require changes. It already calls `load_schema_params_fn(schema_path)` and merges the result — the fix in `load_schema_parameters()` is sufficient for the correct parameters to flow through.

---

## Test Results

| Assertion | Expected | Actual | Pass |
|---|---|---|---|
| `params['upload_sheet_name']` | `'Prolog Submittals'` | `'Prolog Submittals'` | ✅ |
| `params['header_row_index']` | `4` | `4` | ✅ |
| `params['fail_fast']` | `False` | `False` | ✅ |
| `params['start_col']` | `'P'` | `'P'` | ✅ |
| `params['end_col']` | `'AP'` | `'AP'` | ✅ |
| `params['duration_is_working_day']` | `True` | `True` | ✅ |
| `params['overwrite_existing_downloads']` | `True` | `True` | ✅ |
| `'pending_status' in params` | `True` | `True` | ✅ |
| `'dynamic_column_creation' in params` | `True` | `True` | ✅ |

---

## Backward Compatibility

- Legacy schemas with `parameters` dict key still work via fallback path
- No changes to `resolve_effective_parameters()` — existing merge logic unchanged

---

*Report generated: 2026-04-17*
