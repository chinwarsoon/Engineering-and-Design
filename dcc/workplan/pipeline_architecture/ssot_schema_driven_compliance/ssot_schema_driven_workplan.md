# SSOT & Schema-Driven Compliance Workplan

**Document ID**: WP-SSOT-SD-001  
**Current Version**: 0.5  
**Status**: 🟠 PENDING APPROVAL  
**Last Updated**: 2026-05-07  

---

## 1. Title and Description

This workplan addresses SSOT (Single Source of Truth) and schema-driven compliance violations identified across the `dcc/workflow` codebase. A systematic scan of all functions and classes found 10 violation categories covering hardcoded column names, hardcoded processing phases, hardcoded business logic values, hardcoded error/severity maps, hardcoded output filenames, hardcoded health score thresholds, hardcoded regex patterns, post-construction state patching, and duplicate phase map initialization.

The goal is to ensure that all business rules, column names, processing phases, status values, thresholds, and filenames are driven exclusively by the schema and `PipelineContext` — with no values duplicated or hardcoded in Python logic.

---

## 2. Revision Control & Version History

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 0.1 | 2026-05-07 | System | Initial workplan created from SSOT/schema-driven compliance scan of dcc/workflow |
| 0.2 | 2026-05-07 | System | Added schema file column to all tables. Confirmed APP/VOID/PEN/REJ/NAP/AWC/INF are SSOT in `approval_code_schema.json`. Confirmed `allowed_values` for YES/NO/RESUBMITTED/PENDING in `dcc_register_config.json`. Confirmed `data_error_config.json` has severity/layer per error code but missing `processing_phase` field — schema update required. Confirmed `Submission_Session` validation pattern `^[0-9]{6}$` in `dcc_register_config.json`. |
| 0.3 | 2026-05-07 | System | Completed schema file column in all phase task tables and files tables. Updated Phase B risks to reflect confirmed `SESSION_PATTERN` already in schema. Expanded Phase A files table to include `date.py` and `composite.py`. Clarified `dcc_global_parameters.json` schema updates required for B5, C4, C5, C6. |
| 0.4 | 2026-05-07 | System | Full output file compliance audit added. Found 12 pipeline outputs — 7 partially compliant (`.get()` pattern used but parameter keys missing from schema), 4 violations (hardcoded literals). Added V16–V21 to violation table. Expanded Phase B with dedicated output file task group (B5a–B5f). Added 9 missing parameter keys to `dcc_global_parameters.json` schema update requirement. Updated Schema File Reference Map, Object, Impact Assessment, and References. |
| 0.5 | 2026-05-07 | System | Deep global scan completed. Found 5 additional violation categories: (1) 55 hardcoded `severity=` strings in 9 detector files — must read from `data_error_config.json`; (2) 4 severity mismatches between detectors and catalog (`input.py`, `row_validator.py`); (3) 11 error codes in `calculation.py`, `fill.py`, `logic.py` missing from `data_error_config.json`; (4) 41 hardcoded column names in 6 detector files — must read from schema `processing_phase`, `source_columns`, `is_anchor`; (5) `ROW_ERROR_WEIGHTS`, `ANCHOR_REQUIRED`, `DOC_ID_SEGMENTS`, `IDENTITY_COLUMNS`, `ANCHOR_COLUMNS` class-level constants in detectors must be schema-driven. Added V22–V26. Phase C expanded with detector catalog tasks. |

---

## 3. Object

Eliminate all SSOT and schema-driven violations in `dcc/workflow` by:

1. Replacing hardcoded column name references with schema-driven lookups via `calculation.get('depends_on')` or `context.blueprint.columns`
2. Making processing phase iteration dynamic — driven by `context.blueprint.phase_map.keys()` rather than hardcoded phase strings
3. Moving business logic values (status codes, approval codes) to schema `allowed_values` / `choices` / reference data
4. Replacing hardcoded error/severity maps with `context.blueprint.error_catalog` lookups
5. **Ensuring all 12 pipeline output filenames are declared in `dcc_global_parameters.json` and read from `context.parameters`** — currently 9 parameter keys are used in code but missing from schema, and 4 filenames are hardcoded literals
6. Moving health score grade thresholds to schema parameters
7. Removing hardcoded regex patterns — reading from schema column `validation.pattern`
8. Eliminating post-construction state patching of `ErrorReporter` — passing context at construction
9. Making phase map initialization in `build_blueprint()` fully dynamic
10. **Replacing 55 hardcoded `severity=` strings in 9 detector files** — severity is the SSOT of `data_error_config.json`; detectors must read it from the catalog
11. **Adding 11 missing error codes to `data_error_config.json`** and correcting 4 severity mismatches between catalog and detector code
12. **Replacing class-level column constant lists** (`ANCHOR_COLUMNS`, `ANCHOR_REQUIRED`, `DOC_ID_SEGMENTS`, `IDENTITY_COLUMNS`) in detectors with schema-driven lookups
13. **Replacing `ROW_ERROR_WEIGHTS` dict** in `row_validator.py` with `data_error_config.json` `health_score_impact` values

---

## 4. Scope Summary

### Schema File Reference Map

All values that must be read from schema are sourced from these files:

| Schema File | Path | Contains |
|:---|:---|:---|
| `dcc_register_config.json` | `dcc/config/schemas/dcc_register_config.json` | Column definitions, `allowed_values`, `source_column`, `dependencies`, `validation.pattern`, `column_sequence`, `processing_phase` per column |
| `approval_code_schema.json` | `dcc/config/schemas/approval_code_schema.json` | **SSOT for all approval codes**: APP, VOID, REJ, NAP, AWC, INF, PEN — each with `code`, `status`, `aliases` |
| `data_error_config.json` | `dcc/config/schemas/data_error_config.json` | Error catalog: `code`, `name`, `message`, `severity`, `layer`, `column`, `health_score_impact` per error code. **Missing**: `processing_phase` field — must be added (see V08). **Also missing 11 error codes** used in detectors: `C6-C-C-0601/0602/0603/0605/0606` (calculation), `F4-C-F-0401/0402/0403/0404/0405` (fill), `L3-L-W-0304` (logic) — must be added (see V23). **4 severity mismatches** between catalog and detector code (see V24) |
| `dcc_global_parameters.json` | `dcc/config/schemas/dcc_global_parameters.json` | Runtime parameters: `pending_status` (schema-ref to PEN), `first_review_duration`, `second_review_duration`, `dynamic_column_creation`. **Missing 9 output filename keys** — must be added (see V09, V16–V21): `output_filename_pattern`, `summary_filename`, `error_dashboard_filename`, `debug_log_filename`, `ai_insight_summary_filename`, `ai_insight_report_filename`, `ai_insight_trace_filename`, `schema_validation_status_filename`, `ai_runs_db_filename`. Also missing: `fill_jump_limit`, `health_grade_thresholds`, `health_pass_threshold`, `health_fail_threshold` (see V10, V15) |

> **Key finding — APP/VOID as SSOT:** `approval_code_schema.json` is the single source of truth for all approval codes. The codes `APP` and `VOID` hardcoded in `conditional.py` must be resolved at runtime from `approval_code_schema.json` filtered by terminal status. The `pending_status` parameter in `dcc_global_parameters.json` already uses this pattern (`{schema: 'approval_code_schema', code: 'PEN', field: 'status'}`) — the same must be applied to `APP`/`VOID`.

> **Key finding — `allowed_values` already in schema:** `dcc_register_config.json` already defines `allowed_values` for `Submission_Closed` (`['YES','NO']`), `Resubmission_Required` (`['YES','NO','RESUBMITTED','PEN']`), and `Resubmission_Overdue_Status` (`['Resubmitted','Overdue','NO']`). These are the SSOT — Python code must read them, not redeclare them.

> **Key finding — Output file compliance audit:** The pipeline produces 12 output files. All use `.get()` with a default — the pattern is correct — but **9 parameter keys are missing from `dcc_global_parameters.json`**, making them undiscoverable and unconfigurable. Additionally, 4 files have hardcoded literals that bypass the parameter system entirely. The schema update (adding 9 keys to `dcc_global_parameters.json`) is the prerequisite for all output file code fixes.

### Output File Compliance Inventory

| # | Output File | Written By | Current Status | Parameter Key | In Schema? |
|:---|:---|:---|:---|:---|:---:|
| 1 | `processed_dcc_universal.csv` | `dcc_engine_pipeline.py` | `.get('output_filename_pattern', ...)` ✅ | `output_filename_pattern` | ❌ Missing |
| 2 | `processed_dcc_universal.xlsx` | `dcc_engine_pipeline.py` | Derived from CSV via `.with_suffix('.xlsx')` ✅ | — | ✅ N/A |
| 3 | `processing_summary.txt` | `reporting_engine/report_summary.py` | `.get('summary_filename', ...)` ✅ | `summary_filename` | ❌ Missing |
| 4 | `error_dashboard_data.json` | `reporting_engine/report_errors.py` | `.get('error_dashboard_filename', ...)` ✅ | `error_dashboard_filename` | ❌ Missing |
| 5 | `debug_log.json` | `core_engine/logging/log_state.py` | **Hardcoded** `Path("debug_log.json")` ❌ | `debug_log_filename` | ❌ Missing |
| 6 | `schema_validation_status.json` | `schema_engine/status/persistence.py` | **Hardcoded** path derived from schema location ❌ | `schema_validation_status_filename` | ❌ Missing |
| 7 | `error_diagnostic_log.csv` | `reporting_engine/report_errors.py` | **Hardcoded** function default `"error_diagnostic_log.csv"` ❌ | `error_diagnostic_log_filename` | ❌ Missing |
| 8 | `ai_insight_summary.json` | `ai_ops_engine/core/engine.py` | `.get('ai_insight_summary_filename', ...)` ✅ | `ai_insight_summary_filename` | ❌ Missing |
| 9 | `ai_insight_report.md` | `ai_ops_engine/core/engine.py` | `.get('ai_insight_report_filename', ...)` ✅ | `ai_insight_report_filename` | ❌ Missing |
| 10 | `ai_insight_trace.json` | `ai_ops_engine/core/engine.py` | `.get('ai_insight_trace_filename', ...)` ✅ | `ai_insight_trace_filename` | ❌ Missing |
| 11 | `dcc_runs.duckdb` | `ai_ops_engine/core/engine.py` | **Hardcoded** `self.output_dir / "dcc_runs.duckdb"` ❌ | `ai_runs_db_filename` | ❌ Missing |
| 12 | `debug.json` (UI path) | `initiation_engine/core/init_overrides.py` | **Hardcoded** `"debug.json"` ❌ | `debug_log_filename` | ❌ Missing |

**Output compliance summary:** 0 fully compliant · 7 partially compliant (`.get()` used, key missing from schema) · 4 violations (hardcoded literal)

> **Key finding — Detector class-level constants are not schema-driven:** 9 detector files contain 55 hardcoded `severity=` strings, 41 hardcoded column name references, and 5 class-level constant lists (`ANCHOR_COLUMNS`, `ANCHOR_REQUIRED`, `DOC_ID_SEGMENTS`, `IDENTITY_COLUMNS`, `ROW_ERROR_WEIGHTS`) that duplicate data already in the schema. These are global metadata — not local function logic — and must be SSOT-driven. Additionally, 11 error codes used in detectors are missing from `data_error_config.json`, and 4 existing codes have severity mismatches between the catalog and the detector code.

---

### Violation Table

| ID | Category | Violation | Location | Schema File | Field to Read | Severity | Phase |
|:---|:---|:---|:---|:---|:---|:---:|:---:|
| V01 | Schema-Driven | Hardcoded sibling column names in calculation handlers | `conditional.py` lines 80–302, `null_handling.py`, `composite.py`, `date.py` | `dcc_register_config.json` | `columns[col].calculation.dependencies[]` | HIGH | A |
| V02 | Schema-Driven | Hardcoded `"Validation_Errors"` and `"Data_Health_Score"` column names in engine | `processor_engine/core/engine.py` lines 377, 382 | `dcc_register_config.json` | `column_sequence` — find by `processing_phase: P3` + `is_calculated: true` | HIGH | A |
| V03 | Schema-Driven | Hardcoded phase strings `"P1"`, `"P2"`, `"P2.5"`, `"P3"`, `"P4"` in `apply_phased_processing()` | `processor_engine/core/engine.py` lines 284–368 | `dcc_register_config.json` | `columns[col].processing_phase` — iterate `blueprint.phase_map.keys()` | HIGH | B |
| V04 | Schema-Driven | Hardcoded phase map init `{"P1": [], "P2": [], "P2.5": [], "P3": []}` in `build_blueprint()` | `schema_engine/validator/schema_validator.py` line 164 | `dcc_register_config.json` | `columns[col].processing_phase` — build dynamically via `setdefault` | LOW | B |
| V05a | Schema-Driven | Hardcoded `'YES'`, `'NO'`, `'RESUBMITTED'`, `'PEN'` in `conditional.py` | `conditional.py` lines 113–154 | `dcc_register_config.json` | `columns['Resubmission_Required'].validation[type=allowed_values].allowed_values` = `['YES','NO','RESUBMITTED','PEN']` | HIGH | A |
| V05b | Schema-Driven | Hardcoded `'Overdue'`, `'NO'` in `conditional.py` | `conditional.py` lines 296–302 | `dcc_register_config.json` | `columns['Resubmission_Overdue_Status'].validation[type=allowed_values].allowed_values` = `['Resubmitted','Overdue','NO']` | HIGH | A |
| V05c | Schema-Driven | Hardcoded `['APP', 'VOID']` approval codes in `conditional.py` | `conditional.py` line 230 | `approval_code_schema.json` | Filter `approval_codes[]` where `status` in `['Approved','Void']` → codes `APP`, `VOID`. **SSOT: `approval_code_schema.json`** | HIGH | A |
| V05d | Schema-Driven | Hardcoded `'YES'` for `Submission_Closed` check in `date.py`, `composite.py` | `date.py:148`, `composite.py:188` | `dcc_register_config.json` | `columns['Submission_Closed'].validation[type=allowed_values].allowed_values[0]` = `'YES'` | HIGH | A |
| V06 | Schema-Driven | Hardcoded `ERROR_CODES` dict in `validation.py` | `processor_engine/calculations/validation.py` line 70 | `data_error_config.json` | `data_logic_errors[code].message`, `.name` | MEDIUM | C |
| V07 | Schema-Driven | Hardcoded severity/layer maps in `categorizer.py` | `processor_engine/error_handling/resolution/categorizer.py` lines 44–70 | `data_error_config.json` | `data_logic_errors[code].severity`, `.layer` — **already in schema** | MEDIUM | C |
| V08 | Schema-Driven | Hardcoded error-to-phase mapping dict in `evidence.py` | `ai_ops_engine/core/evidence.py` lines 19–31 | `data_error_config.json` | `data_logic_errors[code].processing_phase` — **field missing, must be added to schema** | MEDIUM | C |
| V09 | Schema-Driven | Hardcoded output filenames as literals | `report_errors.py:149,100`, `persistence.py:20`, `log_state.py:61` | `dcc_global_parameters.json` | `dcc_parameters.error_dashboard_filename`, `.error_diagnostic_log_filename`, `.schema_validation_status_filename`, `.debug_log_filename` — **keys missing, must be added** | MEDIUM | B |
| V10 | Schema-Driven | Hardcoded health score grade thresholds and pass/fail thresholds | `report_health.py` lines 60–72, `report_errors.py:57` | `dcc_global_parameters.json` | `dcc_parameters.health_grade_thresholds`, `.health_pass_threshold`, `.health_fail_threshold` — **keys missing, must be added** | MEDIUM | C |
| V11 | Schema-Driven | Hardcoded `SESSION_PATTERN = re.compile(r'^\d{6}$')` class constant | `detectors/anchor.py` line 45 | `dcc_register_config.json` | `columns['Submission_Session'].validation[type=pattern].pattern` = `"^[0-9]{6}$"` — **already in schema** | MEDIUM | B |
| V12 | Schema-Driven | Hardcoded `DOC_ID_PATTERN` fallback regex class constant | `detectors/identity.py` line 64 | `dcc_register_config.json` | `columns['Document_ID'].validation[type=pattern].pattern` — schema-driven path already at line 278; fallback to be removed | LOW | B |
| V13 | SSOT | `ErrorReporter.output_dir` and `effective_parameters` patched post-construction | `dcc_engine_pipeline.py` lines 203–204, 212–213 | `context.paths`, `context.parameters` | `context.paths.csv_output_path.parent`, `context.parameters` — already in context, pass at construction | MEDIUM | A |
| V14 | SSOT | `_SCHEMA_REF_KEY_MAP` hardcoded in `validation.py` (duplicate of `base_processor.py` default) | `processor_engine/calculations/validation.py` lines 41–50 | `dcc_register_config.json` | `schema_data.get('schema_reference_map', {...})` — use same pattern as `base_processor.py` | LOW | B |
| V15 | Schema-Driven | Hardcoded `jump_limit=20` default in fill detector | `detectors/fill.py:48`, `detectors/business.py:109` | `dcc_global_parameters.json` | `dcc_parameters.fill_jump_limit` — **key missing, must be added** | LOW | C |
| V16 | Schema-Driven | 9 output filename parameter keys used in code but absent from `dcc_global_parameters.json` | `boot_pipeline.py`, `path_resolvers.py`, `report_errors.py`, `context_builder.py`, `ai_ops_engine/core/engine.py` | `dcc_global_parameters.json` | `output_filename_pattern`, `summary_filename`, `error_dashboard_filename`, `debug_log_filename`, `ai_insight_summary_filename`, `ai_insight_report_filename`, `ai_insight_trace_filename`, `schema_validation_status_filename`, `ai_runs_db_filename` — **all missing from schema** | HIGH | B |
| V17 | Schema-Driven | `debug_log.json` hardcoded literal in `log_state.py` | `core_engine/logging/log_state.py:61` | `dcc_global_parameters.json` | `dcc_parameters.debug_log_filename` — **must add key to schema first** | MEDIUM | B |
| V18 | Schema-Driven | `schema_validation_status.json` path hardcoded in `persistence.py` | `schema_engine/status/persistence.py:20` | `dcc_global_parameters.json` | `dcc_parameters.schema_validation_status_filename` — **must add key to schema first** | MEDIUM | B |
| V19 | Schema-Driven | `error_diagnostic_log.csv` hardcoded as function default in `report_errors.py` | `reporting_engine/core/report_errors.py:100` | `dcc_global_parameters.json` | `dcc_parameters.error_diagnostic_log_filename` — **must add key to schema first** | MEDIUM | B |
| V20 | Schema-Driven | `dcc_runs.duckdb` hardcoded in `AiOpsEngine.__init__` and `RunStore` | `ai_ops_engine/core/engine.py:60`, `ai_ops_engine/persistence/run_store.py:18` | `dcc_global_parameters.json` | `dcc_parameters.ai_runs_db_filename` — **must add key to schema first** | MEDIUM | B |
| V21 | Schema-Driven | `debug.json` hardcoded in UI contract path | `initiation_engine/core/init_overrides.py:95` | `dcc_global_parameters.json` | `dcc_parameters.debug_log_filename` — same key as V17, consistent naming | LOW | B |
| V22 | Schema-Driven | 55 hardcoded `severity=` strings in 9 detector files — severity must come from error catalog | `detectors/row_validator.py` (9), `detectors/calculation.py` (9), `detectors/fill.py` (8), `detectors/schema.py` (7), `detectors/input.py` (7), `detectors/logic.py` (5), `detectors/identity.py` (5), `detectors/anchor.py` (4), `detectors/validation.py` (1) | `data_error_config.json` | `data_logic_errors[code].severity` — **already in catalog for 17 codes; 11 codes missing (see V23)** | HIGH | C |
| V23 | Schema-Driven | 11 error codes used in detectors are missing from `data_error_config.json` | `detectors/calculation.py`: `C6-C-C-0601/0602/0603/0605/0606`; `detectors/fill.py`: `F4-C-F-0401/0402/0403/0404/0405`; `detectors/logic.py`: `L3-L-W-0304` | `data_error_config.json` | Must add 11 entries with `code`, `name`, `message`, `severity`, `layer`, `processing_phase` — **schema update required before V22** | HIGH | C |
| V24 | Schema-Driven | 4 severity mismatches between detector code and `data_error_config.json` catalog | `detectors/input.py`: `S1-I-F-0805` (code=HIGH, catalog=CRITICAL), `S1-I-V-0502` (code=HIGH, catalog=CRITICAL); `detectors/row_validator.py`: `P1-A-P-0101` (code=HIGH, catalog=CRITICAL), `L3-L-V-0306` (code=LOW, catalog=MEDIUM) | `data_error_config.json` | `data_logic_errors[code].severity` — catalog is SSOT; detector code must be corrected | HIGH | C |
| V25 | Schema-Driven | Class-level column constant lists in detectors hardcode column names that should come from schema | `detectors/anchor.py`: `ANCHOR_COLUMNS` (5 cols); `detectors/identity.py`: `IDENTITY_COLUMNS` (4 cols); `detectors/row_validator.py`: `ANCHOR_REQUIRED` (5 cols), `DOC_ID_SEGMENTS` (5 cols) | `dcc_register_config.json` | `ANCHOR_COLUMNS` → P1 columns with `required: true`; `DOC_ID_SEGMENTS` → `columns['Document_ID'].calculation.source_columns`; `IDENTITY_COLUMNS` → P2 columns with `required: true`. **Schema must add `is_anchor` flag** | HIGH | C |
| V26 | Schema-Driven | `ROW_ERROR_WEIGHTS` dict in `row_validator.py` hardcodes health score weights per error code | `detectors/row_validator.py` lines 38–49 | `data_error_config.json` | `data_logic_errors[code].health_score_impact` — **already present in catalog** (e.g., `P1-A-P-0101: -20`); detector must read from catalog instead of maintaining a parallel dict | MEDIUM | C |

**Status Legend:** 🔵 PLANNED | 🟡 IN PROGRESS | ✅ COMPLETE | ❌ DEFERRED

**Violation Count:** 29 items — 9 HIGH, 12 MEDIUM, 8 LOW  
**Files Affected:** 22 production files across 6 engines  
**Schema Updates Required:**
- `dcc_global_parameters.json` — add 13 parameter keys: 9 output filenames + `fill_jump_limit` + `health_grade_thresholds` + `health_pass_threshold` + `health_fail_threshold`
- `data_error_config.json` — add `processing_phase` field to all 17 existing entries; add 11 missing error code entries; add `is_anchor` flag to anchor columns
- `dcc_register_config.json` — add `is_anchor: true` flag to P1 anchor columns

---

## 5. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Revision Control & Version History](#2-revision-control--version-history)
- [3. Object](#3-object)
- [4. Scope Summary](#4-scope-summary)
- [5. Index of Content](#5-index-of-content)
- [6. Evaluation and Alignment](#6-evaluation-and-alignment-with-existing-architecture)
- [7. Dependencies](#7-dependencies-with-other-tasks)
- [8. Implementation Phases](#8-implementation-phases-and-task-breakdown)
  - [Phase A — High-Severity Fixes](#phase-a--high-severity-fixes)
  - [Phase B — Medium-Severity Structural Fixes](#phase-b--medium-severity-structural-fixes)
  - [Phase C — Catalog and Threshold Externalization](#phase-c--catalog-and-threshold-externalization)
- [9. References](#9-references)

---

## 6. Evaluation and Alignment with Existing Architecture

### Alignment with agent_rule.md

| Rule | Requirement | Alignment |
|:---|:---|:---:|
| Section 2.1 | Always check and ensure compliance with schema standard | ✅ This workplan enforces schema-driven behavior throughout |
| Section 2.5 | Adopt schema fragment pattern for maintainability | ✅ Phase A/B moves values to schema fragments |
| Section 4.1 | Module design for functions and classes | ✅ No structural changes — only value sources change |
| Section 1.4 | Always check and define data column priority | ✅ Phase A ensures column dependencies are schema-declared |
| Section 6.7 | Fail-fast metadata in functions | ✅ Phase A adds schema-driven validation for missing dependencies |

### Alignment with Existing Architecture

| Component | Current State | Post-Fix State |
|:---|:---|:---|
| `context.blueprint.columns` | Populated but bypassed by hardcoded names | Used as the single source for column names and dependencies |
| `context.blueprint.phase_map` | Built correctly but phases hardcoded in engine loop | Engine loop iterates `phase_map.keys()` dynamically |
| `context.blueprint.error_catalog` | Loaded but not used by `validation.py` or `categorizer.py` | All error code lookups go through error catalog |
| `context.parameters` | SSOT for filenames but bypassed in 4 places | All filename lookups use `context.parameters.get()` |
| Schema `allowed_values` / `choices` | Defined in schema but not read by `conditional.py` | Calculation handlers read status values from schema |

### Impact Assessment

| Phase | Files Changed | Risk |
|:---|:---:|:---:|
| Phase A | 7 files | 🟡 Medium — changes calculation handler behavior |
| Phase B | 12 files + 1 schema file | 🟡 Low-Medium — structural, behavior-preserving; schema update is prerequisite |
| Phase C | 19 files + 3 schema files | � Medium — schema updates required first; detector changes are behavior-preserving once catalog is complete |

---

## 7. Dependencies with Other Tasks

1. **WP-PIPE-SIMP-001** — [pipeline_simplification_workplan.md](pipeline_simplification/pipeline_simplification_workplan.md) — Completed. Phase D removed legacy schema fallbacks; this workplan builds on the clean schema architecture that remains.
2. **WP-PIPE-ARCH-001** — [pipeline_architecture_design_workplan.md](pipeline_architecture_workplan/pipeline_architecture_design_workplan.md) — R05 (Schema-Driven Logic) and R07 (Error Categorization) are directly addressed by this workplan.
3. **Error Handling Workplan** — `dcc/workplan/error_handling/` — V06, V07, V08 touch the error catalog and categorizer; coordinate with any active error handling work.
4. **Schema files** — `dcc/config/schemas/dcc_register_config.json` — Phase A requires verifying that `allowed_values`, `choices`, and `depends_on` fields are present in the schema for affected columns. Schema updates may be needed before code changes.
5. **agent_rule.md** — Section 2 (Schema), Section 1 (Data Columns), Section 8 (Workplan)

---

## 8. Implementation Phases and Task Breakdown

---

### Phase A — High-Severity Fixes

**Timeline:** TBD (estimated 2 sessions)  
**Milestone:** No hardcoded column names or business logic values in calculation handlers  
**Risk Level:** 🟡 Medium — changes how calculation handlers resolve sibling columns and status values

#### Pre-Condition Checklist (must verify before coding)

- [x] Confirm `conditional.py` column dependencies (`Submission_Closed`, `Document_ID`, `Submission_Date`, `Review_Return_Actual_Date`, `Resubmission_Required`, `Latest_Approval_Code`) are declared in `dcc_register_config.json` — **CONFIRMED**: `columns['Submission_Closed'].calculation.dependencies` = `['Latest_Approval_Code', 'Document_ID', 'Submission_Date', 'Latest_Submission_Date']`
- [x] Confirm `allowed_values` fields exist in schema for status columns — **CONFIRMED**: `Submission_Closed` = `['YES','NO']`, `Resubmission_Required` = `['YES','NO','RESUBMITTED','PEN']`, `Resubmission_Overdue_Status` = `['Resubmitted','Overdue','NO']`
- [x] Confirm `approval_codes` reference list in schema contains `APP` and `VOID` — **CONFIRMED**: `approval_code_schema.json` has `APP` (Approved) and `VOID` (Void) as SSOT codes
- [x] Confirm `Validation_Errors` and `Data_Health_Score` are in `column_sequence` in schema — **CONFIRMED**: both at positions 47–48 in `dcc_register_config.json` `column_sequence`

#### Tasks

| # | Task | File | Action | Schema File | Schema Field |
|:---|:---|:---|:---|:---|:---|
| A1 | Replace hardcoded sibling column lookups in `conditional.py` | `processor_engine/calculations/conditional.py` | Read column dependencies from `calculation.get('dependencies', [])` instead of hardcoded names | `dcc_register_config.json` | `columns[col].calculation.dependencies[]` |
| A2 | Replace hardcoded status values in `conditional.py` | `processor_engine/calculations/conditional.py` | Read `'YES'`/`'NO'`/`'RESUBMITTED'`/`'PEN'` from `column.validation[type=allowed_values].allowed_values` | `dcc_register_config.json` | `columns['Resubmission_Required'].validation[type=allowed_values].allowed_values` |
| A3 | Replace `['APP', 'VOID']` hardcoded approval codes | `processor_engine/calculations/conditional.py` line 230 | Read from `engine.schema_data['approval_codes']` filtered by terminal status (`Approved`, `Void`) | `approval_code_schema.json` | `approval_codes[].code` where `status` in `['Approved','Void']` |
| A4 | Replace hardcoded `"Validation_Errors"` and `"Data_Health_Score"` in engine | `processor_engine/core/engine.py` lines 377, 382 | Read column names from `context.blueprint.phase_map['P3']` filtered by `is_calculated: true` | `dcc_register_config.json` | `column_sequence` + `columns[col].processing_phase` + `columns[col].is_calculated` |
| A5 | Replace hardcoded sibling column lookups in `null_handling.py` `_get_row_key()` | `processor_engine/calculations/null_handling.py` | Read key columns from schema `columns[col].is_row_key: true` flag | `dcc_register_config.json` | `columns[col].is_row_key` (field to be added if missing) |
| A6 | Fix `ErrorReporter` post-construction patching | `dcc_engine_pipeline.py` lines 203–204, 212–213 | Pass `context.paths.csv_output_path.parent` and `context.parameters` to `CalculationEngine` at construction; engine passes to `ErrorReporter` | `context.paths`, `context.parameters` | Already in `PipelineContext` — no schema change needed |

#### Files Updated/Created

| File | Action | Schema File Used | Purpose |
|:---|:---|:---|:---|
| `dcc/workflow/processor_engine/calculations/conditional.py` | Update | `dcc_register_config.json`, `approval_code_schema.json` | Replace hardcoded column names, status values, and approval codes |
| `dcc/workflow/processor_engine/calculations/null_handling.py` | Update | `dcc_register_config.json` | Replace hardcoded row key column names via `columns[col].is_row_key` |
| `dcc/workflow/processor_engine/calculations/date.py` | Update | `dcc_register_config.json` | Replace hardcoded `'YES'` for `Submission_Closed` check |
| `dcc/workflow/processor_engine/calculations/composite.py` | Update | `dcc_register_config.json` | Replace hardcoded `'YES'` for `Submission_Closed` check |
| `dcc/workflow/processor_engine/core/engine.py` | Update | `dcc_register_config.json` | Replace hardcoded output column names; pass context to `ErrorReporter` at construction |
| `dcc/workflow/dcc_engine_pipeline.py` | Update | — | Remove post-construction `ErrorReporter` patching |
| `dcc/config/schemas/dcc_register_config.json` | Update (if needed) | — | Add `is_row_key` flag to row-key columns if missing |
| `dcc/workplan/pipeline_architecture/ssot_schema_driven_compliance/reports/phase_A_report.md` | Create | — | Phase A test and completion report |

#### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|:---|:---:|:---:|:---|
| Schema missing `depends_on` / `allowed_values` fields for affected columns | Medium | High | Pre-condition checklist must pass; add schema fields before code changes |
| Calculation handler breaks if schema field is absent | Low | Medium | Use `.get()` with existing hardcoded value as fallback during transition; remove fallback after schema verified |
| `ErrorReporter` construction change breaks DI injection | Low | Low | `CalculationEngine` already accepts `error_reporter` as injectable — pass context-derived values only when not injected |

#### Potential Future Issues
- If schema `depends_on` fields are not maintained when columns are renamed, handlers will silently fail — add schema validation rule to check `depends_on` references exist
- `allowed_values` in schema must stay in sync with any UI dropdowns

#### Success Criteria
- [ ] Pre-condition checklist passed
- [ ] Zero hardcoded column names in `conditional.py`
- [ ] Zero hardcoded status values (`'YES'`/`'NO'`/`'RESUBMITTED'`/`'PENDING'`/`'Overdue'`) in calculation handlers
- [ ] `['APP', 'VOID']` replaced with schema reference lookup
- [ ] `"Validation_Errors"` and `"Data_Health_Score"` not hardcoded in `engine.py`
- [ ] `ErrorReporter` receives `output_dir` and `effective_parameters` at construction, not post-patched
- [ ] Pipeline smoke test passes

#### Deliverables
- Updated `conditional.py`, `null_handling.py`, `engine.py`, `dcc_engine_pipeline.py`
- Updated schema files (if needed)
- `reports/phase_A_report.md`

---

### Phase B — Medium-Severity Structural Fixes

**Timeline:** TBD (estimated 2 sessions)  
**Milestone:** Dynamic phase iteration, schema-driven filenames, schema-driven regex patterns  
**Risk Level:** 🟡 Low-Medium — behavior-preserving structural changes

#### Tasks

| # | Task | File | Action | Schema File | Schema Field |
|:---|:---|:---|:---|:---|:---|
| B1 | Make `apply_phased_processing()` iterate phases dynamically | `processor_engine/core/engine.py` | Replace 4 hardcoded `get_columns_by_phase('Px')` calls with loop over `context.blueprint.phase_map.keys()` in defined order | `dcc_register_config.json` | `columns[col].processing_phase` — already in `blueprint.phase_map` |
| B2 | Make `build_blueprint()` phase_map init dynamic | `schema_engine/validator/schema_validator.py` | Replace `phase_map = {"P1": [], "P2": [], "P2.5": [], "P3": []}` with `phase_map = {}` and `phase_map.setdefault(phase, []).append(col_name)` | `dcc_register_config.json` | `columns[col].processing_phase` |
| B3 | Replace hardcoded `SESSION_PATTERN` with schema lookup | `processor_engine/error_handling/detectors/anchor.py` | Read `validation.pattern` from `Submission_Session` column schema; compile at init from schema | `dcc_register_config.json` | `columns['Submission_Session'].validation[type=pattern].pattern` = `"^[0-9]{6}$"` — **already in schema** |
| B4 | Remove `DOC_ID_PATTERN` class-level fallback | `processor_engine/error_handling/detectors/identity.py` | Remove fallback constant; schema-driven pattern at line 278 is the only path | `dcc_register_config.json` | `columns['Document_ID'].validation[type=pattern].pattern` — schema-driven path already exists |
| B5 | **[Schema update first]** Add 9 output filename keys to `dcc_global_parameters.json` | `dcc/config/schemas/dcc_global_parameters.json` | Add all missing output filename parameter keys with current defaults as values — this is the prerequisite for B5a–B5f | `dcc_global_parameters.json` | New keys: `output_filename_pattern`, `summary_filename`, `error_dashboard_filename`, `debug_log_filename`, `ai_insight_summary_filename`, `ai_insight_report_filename`, `ai_insight_trace_filename`, `schema_validation_status_filename`, `ai_runs_db_filename` |
| B5a | Fix `debug_log.json` hardcoded literal in `log_state.py` | `core_engine/logging/log_state.py:61` | Replace `Path("debug_log.json")` with `parameters.get('debug_log_filename', 'debug_log.json')` — pass parameters at call site | `dcc_global_parameters.json` | `dcc_parameters.debug_log_filename` |
| B5b | Fix `schema_validation_status.json` hardcoded path in `persistence.py` | `schema_engine/status/persistence.py:20` | Accept `parameters` dict in `get_validation_status_path()`; use `parameters.get('schema_validation_status_filename', 'schema_validation_status.json')` | `dcc_global_parameters.json` | `dcc_parameters.schema_validation_status_filename` |
| B5c | Fix `error_diagnostic_log.csv` hardcoded function default in `report_errors.py` | `reporting_engine/core/report_errors.py:100` | Replace default arg with `self.effective_parameters.get('error_diagnostic_log_filename', 'error_diagnostic_log.csv')` | `dcc_global_parameters.json` | `dcc_parameters.error_diagnostic_log_filename` |
| B5d | Fix `dcc_runs.duckdb` hardcoded in `AiOpsEngine` and `RunStore` | `ai_ops_engine/core/engine.py:60`, `ai_ops_engine/persistence/run_store.py:18` | Read from `effective_parameters.get('ai_runs_db_filename', 'dcc_runs.duckdb')`; remove `_DEFAULT_DB` module constant | `dcc_global_parameters.json` | `dcc_parameters.ai_runs_db_filename` |
| B5e | Fix `debug.json` hardcoded in UI contract path | `initiation_engine/core/init_overrides.py:95` | Use `debug_log_filename` parameter consistent with V17 | `dcc_global_parameters.json` | `dcc_parameters.debug_log_filename` |
| B5f | Verify 7 partially-compliant outputs use correct parameter keys | `boot_pipeline.py`, `path_resolvers.py`, `context_builder.py`, `ai_ops_engine/core/engine.py` | Confirm `.get()` calls use the exact keys added in B5; update any mismatched key names | `dcc_global_parameters.json` | `output_filename_pattern`, `summary_filename`, `error_dashboard_filename`, `ai_insight_summary_filename`, `ai_insight_report_filename`, `ai_insight_trace_filename` |
| B6 | Remove duplicate `_SCHEMA_REF_KEY_MAP` in `validation.py` | `processor_engine/calculations/validation.py` | Use `schema_data.get('schema_reference_map', {...})` consistent with `base_processor.py` | `dcc_register_config.json` | `schema_reference_map` top-level key (or built-in default in `base_processor.py`) |

#### Files Updated/Created

| File | Action | Schema File Used | Purpose |
|:---|:---|:---|:---|
| `dcc/config/schemas/dcc_global_parameters.json` | **Update first** | — | Add 9 output filename parameter keys — prerequisite for all B5x tasks |
| `dcc/workflow/processor_engine/core/engine.py` | Update | `dcc_register_config.json` | Dynamic phase iteration via `blueprint.phase_map.keys()` |
| `dcc/workflow/schema_engine/validator/schema_validator.py` | Update | `dcc_register_config.json` | Dynamic phase_map init via `setdefault` |
| `dcc/workflow/processor_engine/error_handling/detectors/anchor.py` | Update | `dcc_register_config.json` | Schema-driven `SESSION_PATTERN` from `columns['Submission_Session'].validation[type=pattern].pattern` |
| `dcc/workflow/processor_engine/error_handling/detectors/identity.py` | Update | `dcc_register_config.json` | Remove `DOC_ID_PATTERN` fallback |
| `dcc/workflow/core_engine/logging/log_state.py` | Update | `dcc_global_parameters.json` | Fix hardcoded `debug_log.json` — use `dcc_parameters.debug_log_filename` |
| `dcc/workflow/schema_engine/status/persistence.py` | Update | `dcc_global_parameters.json` | Fix hardcoded `schema_validation_status.json` path — use `dcc_parameters.schema_validation_status_filename` |
| `dcc/workflow/reporting_engine/core/report_errors.py` | Update | `dcc_global_parameters.json` | Fix hardcoded `error_diagnostic_log.csv` default — use `dcc_parameters.error_diagnostic_log_filename` |
| `dcc/workflow/ai_ops_engine/core/engine.py` | Update | `dcc_global_parameters.json` | Fix hardcoded `dcc_runs.duckdb` — use `dcc_parameters.ai_runs_db_filename` |
| `dcc/workflow/ai_ops_engine/persistence/run_store.py` | Update | `dcc_global_parameters.json` | Remove `_DEFAULT_DB` module constant |
| `dcc/workflow/initiation_engine/core/init_overrides.py` | Update | `dcc_global_parameters.json` | Fix hardcoded `debug.json` — use `dcc_parameters.debug_log_filename` |
| `dcc/workflow/processor_engine/calculations/validation.py` | Update | `dcc_register_config.json` | Remove duplicate `_SCHEMA_REF_KEY_MAP` |
| `dcc/workplan/pipeline_architecture/ssot_schema_driven_compliance/reports/phase_B_report.md` | Create | — | Phase B test and completion report |

#### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|:---|:---:|:---:|:---|
| Phase order matters — dynamic iteration must preserve P1→P2→P2.5→P3→P4 sequence | Medium | High | Add `processing_phase_order` array to `dcc_register_config.json`; use as sort key in `build_blueprint()` |
| `Submission_Session` schema pattern confirmed present — no risk | None | None | `dcc_register_config.json` `columns['Submission_Session'].validation[type=pattern].pattern` = `"^[0-9]{6}$"` ✅ |
| `log_state.py` used before context available | Low | Low | Keep `"debug_log.json"` as hardcoded startup default only; override from parameters once context is available |
| `persistence.py` signature change breaks callers | Low | Low | Add `parameters` as optional kwarg with `None` default; fall back to current behavior if not provided |
| Output filename key mismatch between code and schema | Low | Medium | B5f explicitly verifies all `.get()` key names match the schema keys added in B5 |

#### Potential Future Issues
- Phase order must be maintained in schema `processing_phase_order` — document this as a schema maintenance requirement
- All 9 output filename keys in `dcc_global_parameters.json` must be kept in sync with any UI configuration panels

#### Success Criteria
- [ ] `apply_phased_processing()` has no hardcoded phase string literals
- [ ] `build_blueprint()` phase_map init is dynamic
- [ ] `SESSION_PATTERN` reads from schema
- [ ] `DOC_ID_PATTERN` class constant removed
- [ ] All 9 output filename parameter keys added to `dcc_global_parameters.json`
- [ ] All 12 pipeline outputs use `parameters.get(key, default)` — zero hardcoded literals
- [ ] `_SCHEMA_REF_KEY_MAP` removed from `validation.py`
- [ ] Pipeline smoke test passes — all 12 output files written correctly

#### Deliverables
- Updated files (see table above)
- `reports/phase_B_report.md`

---

### Phase C — Catalog and Threshold Externalization

**Timeline:** TBD (estimated 1–2 sessions)  
**Milestone:** Error codes, severity maps, and health thresholds all read from schema/catalog  
**Risk Level:** 🟢 Low — externalization only, no logic change

#### Pre-Condition Checklist

- [x] Confirm `context.blueprint.error_catalog` contains severity and layer fields for all codes in `categorizer.py` — **CONFIRMED**: `data_error_config.json` has `severity` and `layer` per error code entry
- [ ] Confirm `context.blueprint.error_catalog` contains all error codes referenced in `validation.py` `ERROR_CODES` dict — verify coverage
- [ ] Confirm `context.blueprint.error_catalog` contains `processing_phase` field for all codes in `evidence.py` — **NOT PRESENT**: must add `processing_phase` field to each entry in `data_error_config.json`
- [ ] Add 11 missing error codes to `data_error_config.json` (`C6-C-C-0601/0602/0603/0605/0606`, `F4-C-F-0401/0402/0403/0404/0405`, `L3-L-W-0304`) with full `code`, `name`, `message`, `severity`, `layer`, `processing_phase`, `health_score_impact` fields
- [ ] Correct 4 severity mismatches in `data_error_config.json` or detector code (catalog is SSOT)
- [ ] Add `is_anchor: true` flag to P1 anchor columns in `dcc_register_config.json`
- [ ] Add `health_grade_thresholds`, `health_pass_threshold`, `health_fail_threshold` to `dcc_global_parameters.json`
- [ ] Add `fill_jump_limit` to `dcc_global_parameters.json`

#### Tasks

| # | Task | File | Action | Schema File | Schema Field |
|:---|:---|:---|:---|:---|:---|
| C1 | Replace `ERROR_CODES` dict with error catalog lookup | `processor_engine/calculations/validation.py` | Replace module-level `ERROR_CODES` dict with `context.blueprint.error_catalog.get(code, {})` lookups | `data_error_config.json` | `data_logic_errors[code].message`, `.name` |
| C2 | Replace `_severity_map` / `_layer_map` in `categorizer.py` with error catalog | `processor_engine/error_handling/resolution/categorizer.py` | Read severity and layer from `blueprint.error_catalog[code].get('severity')` and `.get('layer')` | `data_error_config.json` | `data_logic_errors[code].severity`, `.layer` — **already in schema** |
| C3 | Replace hardcoded error-to-phase dict in `evidence.py` | `ai_ops_engine/core/evidence.py` | Read phase from `blueprint.error_catalog[code].get('processing_phase')` | `data_error_config.json` | `data_logic_errors[code].processing_phase` — **must add field to schema first** |
| C4 | Move health grade thresholds to schema parameters | `reporting_engine/core/report_health.py` | Read grade thresholds from `parameters.get('health_grade_thresholds', {...})` with current values as defaults | `dcc_global_parameters.json` | `dcc_parameters.health_grade_thresholds` — **must add to schema** |
| C5 | Move pass/fail thresholds to schema parameters | `reporting_engine/core/report_errors.py` line 57 | Read `health_pass_threshold` and `health_fail_threshold` from parameters | `dcc_global_parameters.json` | `dcc_parameters.health_pass_threshold`, `.health_fail_threshold` — **must add to schema** |
| C6 | Move `jump_limit` to schema parameters | `processor_engine/error_handling/detectors/fill.py`, `business.py` | Read from `parameters.get('fill_jump_limit', 20)` | `dcc_global_parameters.json` | `dcc_parameters.fill_jump_limit` — **must add to schema** |
| C7 | **[Schema update first]** Add 11 missing error codes to `data_error_config.json` | `dcc/config/schemas/data_error_config.json` | Add full entries for `C6-C-C-0601/0602/0603/0605/0606`, `F4-C-F-0401/0402/0403/0404/0405`, `L3-L-W-0304` with `code`, `name`, `message`, `severity`, `layer`, `processing_phase`, `health_score_impact` | `data_error_config.json` | New entries — prerequisite for C8 |
| C8 | Replace 55 hardcoded `severity=` strings in 9 detector files with catalog lookup | `detectors/row_validator.py`, `calculation.py`, `fill.py`, `schema.py`, `input.py`, `logic.py`, `identity.py`, `anchor.py`, `validation.py` | Each detector reads `blueprint.error_catalog[self.ERROR_CODE].get('severity')` at detection time instead of hardcoding the string | `data_error_config.json` | `data_logic_errors[code].severity` |
| C9 | Correct 4 severity mismatches — align detector code with catalog | `detectors/input.py`, `detectors/row_validator.py` | Fix: `S1-I-F-0805` HIGH→CRITICAL, `S1-I-V-0502` HIGH→CRITICAL, `P1-A-P-0101` HIGH→CRITICAL, `L3-L-V-0306` LOW→MEDIUM | `data_error_config.json` | `data_logic_errors[code].severity` is SSOT |
| C10 | Replace `ANCHOR_COLUMNS` and `ANCHOR_REQUIRED` class constants with schema lookup | `detectors/anchor.py`, `detectors/row_validator.py` | Read P1 columns with `required: true` and `is_anchor: true` from `blueprint.columns` | `dcc_register_config.json` | `columns[col].processing_phase == 'P1'` + `columns[col].is_anchor == true` — **must add `is_anchor` flag to schema** |
| C11 | Replace `DOC_ID_SEGMENTS` class constant with schema lookup | `detectors/row_validator.py` | Read from `blueprint.columns['Document_ID'].calculation.source_columns` | `dcc_register_config.json` | `columns['Document_ID'].calculation.source_columns` = `['Project_Code','Facility_Code','Document_Type','Discipline','Document_Sequence_Number']` — **already in schema** |
| C12 | Replace `IDENTITY_COLUMNS` class constant with schema lookup | `detectors/identity.py` | Read P2 columns with `required: true` from `blueprint.columns` | `dcc_register_config.json` | `columns[col].processing_phase == 'P2'` + `columns[col].required == true` |
| C13 | Replace `ROW_ERROR_WEIGHTS` dict with catalog `health_score_impact` | `detectors/row_validator.py` lines 38–49 | Read `blueprint.error_catalog[code].get('health_score_impact', 0)` instead of parallel dict | `data_error_config.json` | `data_logic_errors[code].health_score_impact` — **already in catalog** |
| C14 | Replace hardcoded `"REJ"` string in `row_validator.py` with catalog lookup | `detectors/row_validator.py:319` | Read rejected code from `approval_code_schema.json` filtered by `status == 'Rejected'` → code `REJ` | `approval_code_schema.json` | `approval_codes[].code` where `status == 'Rejected'` |
| C15 | Replace hardcoded `"PEN"` fallback in `aggregate.py` with `pending_status` parameter | `processor_engine/calculations/aggregate.py:311` | Read from `engine.schema_data` via `pending_status` schema reference (already defined in `dcc_global_parameters.json`) | `dcc_global_parameters.json` | `dcc_parameters.pending_status.code` = `'PEN'` — **already in schema** |

#### Files Updated/Created

| File | Action | Schema File Used | Purpose |
|:---|:---|:---|:---|
| `dcc/config/schemas/data_error_config.json` | **Update first** | — | Add `processing_phase` to all 17 entries; add 11 missing error codes; add `health_score_impact` where missing — prerequisite for C3, C7, C8, C13 |
| `dcc/config/schemas/dcc_register_config.json` | Update | — | Add `is_anchor: true` flag to P1 anchor columns — prerequisite for C10 |
| `dcc/config/schemas/dcc_global_parameters.json` | Update | — | Add `health_grade_thresholds`, `health_pass_threshold`, `health_fail_threshold`, `fill_jump_limit` |
| `dcc/workflow/processor_engine/calculations/validation.py` | Update | `data_error_config.json` | Replace `ERROR_CODES` with error catalog lookup |
| `dcc/workflow/processor_engine/error_handling/resolution/categorizer.py` | Update | `data_error_config.json` | Replace severity/layer maps with `data_logic_errors[code].severity` / `.layer` |
| `dcc/workflow/ai_ops_engine/core/evidence.py` | Update | `data_error_config.json` | Replace phase map with `data_logic_errors[code].processing_phase` |
| `dcc/workflow/reporting_engine/core/report_health.py` | Update | `dcc_global_parameters.json` | Parameterized grade thresholds via `dcc_parameters.health_grade_thresholds` |
| `dcc/workflow/reporting_engine/core/report_errors.py` | Update | `dcc_global_parameters.json` | Parameterized pass/fail thresholds via `dcc_parameters.health_pass_threshold` / `.health_fail_threshold` |
| `dcc/workflow/processor_engine/error_handling/detectors/fill.py` | Update | `dcc_global_parameters.json`, `data_error_config.json` | Parameterized jump limit; replace hardcoded severity with catalog |
| `dcc/workflow/processor_engine/error_handling/detectors/business.py` | Update | `dcc_global_parameters.json` | Parameterized jump limit |
| `dcc/workflow/processor_engine/error_handling/detectors/row_validator.py` | Update | `dcc_register_config.json`, `data_error_config.json`, `approval_code_schema.json` | Replace `ANCHOR_REQUIRED`, `DOC_ID_SEGMENTS`, `ROW_ERROR_WEIGHTS`, hardcoded severity, `"REJ"` string |
| `dcc/workflow/processor_engine/error_handling/detectors/anchor.py` | Update | `dcc_register_config.json`, `data_error_config.json` | Replace `ANCHOR_COLUMNS`, hardcoded severity |
| `dcc/workflow/processor_engine/error_handling/detectors/identity.py` | Update | `dcc_register_config.json`, `data_error_config.json` | Replace `IDENTITY_COLUMNS`, hardcoded severity |
| `dcc/workflow/processor_engine/error_handling/detectors/logic.py` | Update | `data_error_config.json` | Replace hardcoded severity |
| `dcc/workflow/processor_engine/error_handling/detectors/calculation.py` | Update | `data_error_config.json` | Replace hardcoded severity |
| `dcc/workflow/processor_engine/error_handling/detectors/schema.py` | Update | `data_error_config.json` | Replace hardcoded severity |
| `dcc/workflow/processor_engine/error_handling/detectors/input.py` | Update | `data_error_config.json` | Replace hardcoded severity; fix 2 severity mismatches |
| `dcc/workflow/processor_engine/error_handling/detectors/validation.py` | Update | `data_error_config.json` | Replace hardcoded severity |
| `dcc/workflow/processor_engine/calculations/aggregate.py` | Update | `dcc_global_parameters.json` | Replace hardcoded `'PEN'` fallback with `pending_status` parameter |
| `dcc/workplan/pipeline_architecture/ssot_schema_driven_compliance/reports/phase_C_report.md` | Create | — | Phase C test and completion report |

#### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|:---|:---:|:---:|:---|
| 11 missing error codes need full catalog entries before detectors can read severity from catalog | High | High | C7 is the prerequisite schema update — complete before any C8–C13 code changes |
| Detectors receive errors before `context.blueprint` is available | Low | Medium | Pass error catalog as explicit parameter at detector construction; detectors already accept `schema_data` context |
| `ANCHOR_COLUMNS` list in schema requires new `is_anchor` field — schema change needed | Medium | Medium | Add `is_anchor: true` to P1 required columns in `dcc_register_config.json` as part of C10 pre-condition |
| `ROW_ERROR_WEIGHTS` values may differ from `health_score_impact` in catalog | Low | Low | Audit both before C13; catalog is SSOT — update catalog values if needed, not the code |
| Grade threshold changes affect existing reports | Low | Low | Keep current values as schema defaults — no behavioral change unless schema is explicitly updated |
| `evidence.py` in `ai_ops_engine` does not have direct access to `context.blueprint` | Low | Medium | Pass error catalog as a parameter to `run_ai_ops()` |

#### Potential Future Issues
- Error catalog must be kept in sync with all error codes used across the codebase — consider a schema validation check that verifies all `error_code=` strings in detector files exist in `data_error_config.json`
- `is_anchor` flag in schema must be maintained when columns are added or reclassified
- `DOC_ID_SEGMENTS` is already in schema (`Document_ID.calculation.source_columns`) — this is the correct pattern for all composite column dependencies

#### Success Criteria
- [ ] Pre-condition checklist passed
- [ ] `ERROR_CODES` dict removed from `validation.py`
- [ ] `_severity_map` and `_layer_map` removed from `categorizer.py`
- [ ] Hardcoded error-to-phase dict removed from `evidence.py`
- [ ] Health grade thresholds read from schema parameters
- [ ] Pass/fail thresholds read from schema parameters
- [ ] `jump_limit` reads from schema parameters
- [ ] 11 missing error codes added to `data_error_config.json`
- [ ] 4 severity mismatches corrected (catalog is SSOT)
- [ ] Zero hardcoded `severity=` strings in all 9 detector files
- [ ] `ANCHOR_COLUMNS`, `ANCHOR_REQUIRED`, `DOC_ID_SEGMENTS`, `IDENTITY_COLUMNS` class constants replaced with schema lookups
- [ ] `ROW_ERROR_WEIGHTS` replaced with `health_score_impact` from catalog
- [ ] `"REJ"` string in `row_validator.py` replaced with `approval_code_schema.json` lookup
- [ ] `'PEN'` fallback in `aggregate.py` replaced with `pending_status` parameter
- [ ] Pipeline smoke test passes

#### Deliverables
- Updated files (see table above — 19 files)
- `reports/phase_C_report.md`

---

## 9. References

1. [agent_rule.md](../../agent_rule.md)
2. [dcc_engine_pipeline.py](../../workflow/dcc_engine_pipeline.py)
3. [conditional.py](../../workflow/processor_engine/calculations/conditional.py)
4. [null_handling.py](../../workflow/processor_engine/calculations/null_handling.py)
5. [validation.py — calculations](../../workflow/processor_engine/calculations/validation.py)
6. [aggregate.py](../../workflow/processor_engine/calculations/aggregate.py)
7. [date.py](../../workflow/processor_engine/calculations/date.py)
8. [composite.py](../../workflow/processor_engine/calculations/composite.py)
9. [engine.py — processor](../../workflow/processor_engine/core/engine.py)
10. [schema_validator.py](../../workflow/schema_engine/validator/schema_validator.py)
11. [report_health.py](../../workflow/reporting_engine/core/report_health.py)
12. [report_errors.py](../../workflow/reporting_engine/core/report_errors.py)
13. [anchor.py](../../workflow/processor_engine/error_handling/detectors/anchor.py)
14. [identity.py](../../workflow/processor_engine/error_handling/detectors/identity.py)
15. [logic.py](../../workflow/processor_engine/error_handling/detectors/logic.py)
16. [fill.py](../../workflow/processor_engine/error_handling/detectors/fill.py)
17. [calculation.py](../../workflow/processor_engine/error_handling/detectors/calculation.py)
18. [schema.py — detector](../../workflow/processor_engine/error_handling/detectors/schema.py)
19. [input.py — detector](../../workflow/processor_engine/error_handling/detectors/input.py)
20. [row_validator.py](../../workflow/processor_engine/error_handling/detectors/row_validator.py)
21. [validation.py — detector](../../workflow/processor_engine/error_handling/detectors/validation.py)
22. [categorizer.py](../../workflow/processor_engine/error_handling/resolution/categorizer.py)
23. [evidence.py](../../workflow/ai_ops_engine/core/evidence.py)
24. [ai_ops_engine/core/engine.py](../../workflow/ai_ops_engine/core/engine.py)
25. [ai_ops_engine/core/context_builder.py](../../workflow/ai_ops_engine/core/context_builder.py)
26. [ai_ops_engine/persistence/run_store.py](../../workflow/ai_ops_engine/persistence/run_store.py)
27. [schema_engine/status/persistence.py](../../workflow/schema_engine/status/persistence.py)
28. [core_engine/logging/log_state.py](../../workflow/core_engine/logging/log_state.py)
29. [initiation_engine/core/init_overrides.py](../../workflow/initiation_engine/core/init_overrides.py)
30. [dcc_global_parameters.json](../../config/schemas/dcc_global_parameters.json)
31. [approval_code_schema.json](../../config/schemas/approval_code_schema.json)
32. [data_error_config.json](../../config/schemas/data_error_config.json)
33. [dcc_register_config.json](../../config/schemas/dcc_register_config.json)
34. [pipeline_simplification_workplan.md](pipeline_simplification/pipeline_simplification_workplan.md)
35. [pipeline_architecture_design_workplan.md](pipeline_architecture_workplan/pipeline_architecture_design_workplan.md)
36. [issue_log.md](../issue_log.md)
