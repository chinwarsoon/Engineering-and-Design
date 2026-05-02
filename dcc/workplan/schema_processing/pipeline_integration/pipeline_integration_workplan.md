# Pipeline Integration Workplan

**Purpose:** Integrate all schema changes (from recursive_schema_loader_workplan.md Phases A–I) into `dcc_engine_pipeline.py` and test the full pipeline end-to-end.

**Created:** 2026-04-17
**Status:** ✅ Complete (All Phases 1-9 Implemented)

**Related Documents:**
- [recursive_schema_loader_workplan.md](recursive_schema_loader_workplan.md) - Schema architecture changes (Phases A–I)
- [schema_update_record.md](schema_update_record.md) - Column status tracking
- [dcc_engine_pipeline.py](../../workflow/dcc_engine_pipeline.py) - Main pipeline entry point

---

## Context Summary

### Key Schema Changes (Phases A–I Complete)

- `dcc_register_enhanced.json` → deleted; replaced by `dcc_register_base.json` + `dcc_register_setup.json` + `dcc_register_config.json`
- `approval_code_schema.json` added as standalone schema
- `dcc_global_parameters.json` added as values-only schema (renamed from `global_parameters.json`)
- All schemas now use URI-based `$ref` (`https://dcc-pipeline.internal/schemas/...`)
- `schema_references` dict pattern → deprecated; replaced by URI `$ref` resolution via `RefResolver`
- `master_registry.json` → NOT REQUIRED (Phase F)

### Architecture Resolution ✅

The pipeline now supports dual architecture via `SchemaValidator.load_resolved_schema()`:

- **New Architecture (V2):** Uses URI `$ref` resolution via `RefResolver` when top-level `columns` key detected
- **Legacy Architecture:** Falls back to `resolve_schema_dependencies()` for `schema_references` dict pattern

The `SchemaValidator._load_resolved_schema_v2()` method handles URI `$ref` resolution and normalizes output to the canonical shape expected by all engines. Legacy support maintained for backward compatibility.

---

## Pipeline Flow (Current)

```
main()
  ├── parse_cli_args()
  ├── build_native_defaults(base_path)
  ├── test_environment(base_path)
  ├── safe_resolve(schema_path)              ← resolves dcc_register_config.json
  ├── resolve_effective_parameters()         ← loads global_parameters from schema
  └── run_engine_pipeline()
        ├── Step 1: ProjectSetupValidator.validate()
        ├── Step 2: SchemaValidator(schema_path).validate()
        │           └── load_resolved_schema()   ← USES LEGACY schema_references
        ├── Step 3: load_excel_data() + ColumnMapperEngine.map_dataframe()
        │           └── mapper.resolved_schema = resolved_schema
        ├── Step 4: CalculationEngine(resolved_schema).process_data()
        │           └── schema_data.get('enhanced_schema', {})  ← KEY MISMATCH
        ├── Step 5: SchemaProcessor.reorder_dataframe()
        │           └── resolved_schema.get('column_sequence')  ← KEY MISMATCH
        └── Step 6: Export + write_processing_summary()
```

---

## Schema Key Mapping (Old → New)

| Old Key (enhanced_schema pattern) | New Key (dcc_register_config.json) | Used By |
|---|---|---|
| `enhanced_schema.columns` | `columns` | `CalculationEngine.__init__` |
| `enhanced_schema.column_sequence` | `column_sequence` | `CalculationEngine.apply_phased_processing`, `SchemaProcessor.reorder_dataframe` |
| `schema_references.approval_code_schema` | `approval_codes` (via URI `$ref`) | `BaseProcessor._resolve_schema_reference` |
| `approval_code_schema_data.approval` | `approval_codes` | All approval code lookups |
| `parameters` (from `schema_references`) | `global_parameters[0]` | `CalculationEngine.__init__`, `load_excel_data` |
| `schema_references.department_schema` | `departments` (via URI `$ref`) | Validation |
| `schema_references.discipline_schema` | `disciplines` (via URI `$ref`) | Validation |
| `schema_references.facility_schema` | `facilities` (via URI `$ref`) | Validation |
| `schema_references.document_type_schema` | `document_types` (via URI `$ref`) | Validation |
| `schema_references.project_code_schema` | `projects` (via URI `$ref`) | Validation |

---

## Global Parameters (I/O Reference)

| Parameter | Source | Consumer |
|---|---|---|
| `upload_file_name` | `global_parameters[0]` | `run_engine_pipeline` → `load_excel_data` |
| `upload_sheet_name` | `global_parameters[0]` | `load_excel_data` |
| `header_row_index` | `global_parameters[0]` | `load_excel_data` |
| `start_col`, `end_col` | `global_parameters[0]` | `load_excel_data` |
| `fail_fast` | `global_parameters[0]` | `CalculationEngine.__init__` |
| `duration_is_working_day` | `global_parameters[0]` | date calculations |
| `first_review_duration`, `second_review_duration`, `resubmission_duration` | `global_parameters[0]` | date calculations |
| `overwrite_existing_downloads` | `global_parameters[0]` | `validate_export_paths` |
| `pending_status` | `global_parameters[0]` | `Review_Status` null handling |
| `dynamic_column_creation` | `global_parameters[0]` | `initialize_missing_columns` |

---

## Workplan Phases

---

### Phase 1 — Schema Loading Adapter
**Status:** ✅ Complete — [phase_1_report.md](phase_1_report.md)
**Goal:** Create a `load_resolved_schema_v2()` adapter that loads `dcc_register_config.json` using URI `$ref` resolution and normalizes the output to the shape expected by downstream engines.

**Functions to modify:**
- `workflow/schema_engine/validator/schema_validator.py`
  - `SchemaValidator.load_resolved_schema()` — add new path using `RefResolver` when URI `$ref` detected
  - New helper `_normalize_resolved_schema(raw)` — maps new top-level keys to shape expected by engines

**I/O:**
- Input: `dcc_register_config.json` path
- Output: `resolved_schema` dict with keys: `columns`, `column_sequence`, `parameters`, `approval_codes`, `departments`, `disciplines`, `facilities`, `document_types`, `projects`

**Test:** Load schema, assert all keys present, assert `len(columns) == 47`, assert `len(approval_codes) == 7`.

---

### Phase 2 — Global Parameters Normalization
**Status:** ✅ Complete — [phase_2_report.md](phase_2_report.md)
**Goal:** Fix `resolve_effective_parameters()` and `load_schema_parameters()` to read from `global_parameters[0]` (array) instead of `parameters` (dict).

**Functions to modify:**
- `workflow/schema_engine/loader/schema_loader.py`
  - `load_schema_parameters()` — handle `global_parameters` array, extract `global_parameters[0]`
- `workflow/initiation_engine/utils/parameters.py`
  - `resolve_effective_parameters()` — merge from `global_parameters[0]`

**I/O:**
- Input: `dcc_register_config.json`
- Output: `effective_parameters` dict with all global params flattened

**Test:** Assert `effective_parameters['upload_sheet_name'] == 'Prolog Submittals'`, `header_row_index == 4`, `fail_fast == False`.

---

### Phase 3 — CalculationEngine Schema Key Fix
**Status:** ✅ Complete — [phase_3_report.md](phase_3_report.md)
**Goal:** Fix `CalculationEngine.__init__` and `apply_phased_processing()` to read `columns` and `column_sequence` directly from top-level schema (not `enhanced_schema` wrapper).

**Functions to modify:**
- `workflow/processor_engine/core/engine.py`
  - `CalculationEngine.__init__` — change `schema_data.get('enhanced_schema', {})` → `schema_data`
  - `CalculationEngine.apply_phased_processing()` — same fix for `column_sequence`
- `workflow/processor_engine/core/base.py`
  - `BaseProcessor._resolve_schema_reference()` — fix lookup from `approval_code_schema_data.approval` → `approval_codes`

**I/O:**
- Input: normalized `resolved_schema` from Phase 1
- Output: `CalculationEngine` instance with correct `self.columns` (47 cols) and `self.calculation_order`

**Test:** Instantiate `CalculationEngine(resolved_schema)`, assert `len(engine.columns) == 47`, assert `'Document_ID' in engine.columns`.

---

### Phase 4 — SchemaProcessor Column Sequence Fix
**Status:** ✅ Complete — [phase_4_report.md](phase_4_report.md)
**Goal:** Fix `SchemaProcessor.reorder_dataframe()` to read `column_sequence` from top-level schema.

**Functions to modify:**
- `workflow/processor_engine/schema/processor.py`
  - `SchemaProcessor` — fix key path: `schema_data.get('column_sequence')` instead of `enhanced_schema.get('column_sequence')`

**I/O:**
- Input: normalized `resolved_schema`, processed `df`
- Output: `df` with columns reordered per `column_sequence`

**Test:** Assert output column order matches `dcc_register_config.json` `column_sequence` (47 columns).

---

### Phase 5 — Approval Code Reference Resolution
**Status:** ✅ Complete — [phase_5_report.md](phase_5_report.md)
**Goal:** Fix all approval code lookups to use `approval_codes` list directly instead of `approval_code_schema_data.approval`.

**Functions to modify:**
- `workflow/processor_engine/core/base.py`
  - `_resolve_schema_reference()` — add fallback: check `resolved_schema['approval_codes']` when `approval_code_schema_data` not found
- `workflow/processor_engine/calculations/mapping.py`
  - `status_to_code` mapping — fix reference to `approval_codes`
- `workflow/processor_engine/calculations/validation.py`
  - `schema_reference_check` for `approval_code_schema` — fix data section lookup
- `workflow/processor_engine/calculations/null_handling.py`
  - `fill_value_reference` resolution for `PEN` code — fix lookup path

**I/O:**
- Input: `resolved_schema['approval_codes']` (7 entries)
- Output: correct status→code mapping

**Test:** Assert `status_to_code("Approved")` → `"APP"`, `status_to_code("Pending")` → `"PEN"`, `status_to_code("Awaiting S.O.'s response")` → `"PEN"`.

---

### Phase 6 — Categorical Schema Reference Validation Fix
**Status:** ✅ Complete — [phase_6_report.md](phase_6_report.md)
**Goal:** Fix `schema_reference_check` validation for `Project_Code`, `Facility_Code`, `Document_Type`, `Discipline`, `Department` to use new top-level keys.

**Functions to modify:**
- `workflow/processor_engine/calculations/validation.py`
  - `_resolve_reference_data()` — fix lookup to use `projects`, `facilities`, `document_types`, `disciplines`, `departments` from top-level schema

**Reference mapping:**

| Column | schema_reference | Old lookup key | New lookup key | data_section field |
|---|---|---|---|---|
| `Project_Code` | `project_code_schema` | `project_code_schema_data.project` | `projects` | `code` |
| `Facility_Code` | `facility_schema` | `facility_schema_data.facility` | `facilities` | `prefix` |
| `Document_Type` | `document_type_schema` | `document_type_schema_data.document` | `document_types` | `code` |
| `Discipline` | `discipline_schema` | `discipline_schema_data.discipline` | `disciplines` | `code` |
| `Department` | `department_schema` | `department_schema_data.choices` | `departments` | `code` |

**Test:** Assert `Project_Code` validation passes for valid code, fails for invalid code.

---

### Phase 7 — ColumnMapperEngine Schema Integration Verification
**Status:** ✅ Complete — [phase_7_report.md](phase_7_report.md)
**Goal:** Verify `ColumnMapperEngine` works with new `resolved_schema` structure. Aliases are still under `columns[col]['aliases']` — no structural change expected, but confirm end-to-end.

**Functions to verify:**
- `workflow/mapper_engine/core/engine.py` — `map_dataframe()` reads `resolved_schema['columns']`
- `workflow/mapper_engine/mappers/detection.py` — `detect_columns()` reads aliases

**Test:** Run mapper on `data/Submittal and RFI Tracker Lists.xlsx`, assert match rate > 80%.

---

### Phase 8 — SchemaValidator Alignment Fix
**Status:** ✅ Complete — [phase_8_report.md](phase_8_report.md)
**Goal:** Fix `SchemaValidator.validate()` which currently checks for `enhanced_schema.columns` — update to check `columns` at top level.

**Functions to modify:**
- `workflow/schema_engine/validator/schema_validator.py`
  - `SchemaValidator.validate()` — remove `enhanced_schema` wrapper check, validate `columns` at top level

**Test:** Assert `SchemaValidator(dcc_register_config_path).validate()['ready'] == True`.

---

### Phase 9 — Full Pipeline Integration Test
**Status:** ✅ Complete — [phase_9_report.md](phase_9_report.md)
**Goal:** Run `dcc_engine_pipeline.py` end-to-end with all fixes applied.

**Test sequence:**
1. Run `python dcc_engine_pipeline.py` from `dcc/` directory
2. Assert Step 1 (initiation) passes — `ProjectSetupValidator.validate()['ready'] == True`
3. Assert Step 2 (schema validation) passes — no `enhanced_schema` errors
4. Assert Step 3 (column mapping) passes — match rate reported > 80%
5. Assert Step 4 (processing) passes — all 47 columns processed through P1→P2→P2.5→P3
6. Assert Step 5 (reorder) passes — output columns match `column_sequence`
7. Assert Step 6 (export) passes — CSV, Excel, summary written to `output/`
8. Inspect `output/processing_summary.txt` and `output/debug_log.json` for errors

---

## Files to Modify

| File | Phases |
|---|---|
| `workflow/schema_engine/validator/schema_validator.py` | 1, 8 |
| `workflow/schema_engine/loader/schema_loader.py` | 2 |
| `workflow/initiation_engine/utils/parameters.py` | 2 |
| `workflow/processor_engine/core/engine.py` | 3 |
| `workflow/processor_engine/core/base.py` | 3, 5 |
| `workflow/processor_engine/schema/processor.py` | 4 |
| `workflow/processor_engine/calculations/mapping.py` | 5 |
| `workflow/processor_engine/calculations/validation.py` | 5, 6 |
| `workflow/processor_engine/calculations/null_handling.py` | 5 |

---

## Phase Completion Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Schema Loading Adapter | ✅ Complete |
| Phase 2 | Global Parameters Normalization | ✅ Complete |
| Phase 3 | CalculationEngine Schema Key Fix | ✅ Complete |
| Phase 4 | SchemaProcessor Column Sequence Fix | ✅ Complete |
| Phase 5 | Approval Code Reference Resolution | ✅ Complete |
| Phase 6 | Categorical Schema Reference Validation Fix | ✅ Complete |
| Phase 7 | ColumnMapperEngine Schema Integration Verification | ✅ Complete |
| Phase 8 | SchemaValidator Alignment Fix | ✅ Complete |
| Phase 9 | Full Pipeline Integration Test | ✅ Complete |

---

*Workplan Created: 2026-04-17*
*Based on pipeline_integration_workplan.mg and recursive_schema_loader_workplan.md*
*Status: All phases implemented and tested. Pipeline operational with dual architecture support.*
