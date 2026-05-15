# SSOT & Schema-Driven Compliance Workplan

**Document ID**: WP-SSOT-SD-001  
**Current Version**: 1.4  
**Status**: ✅ COMPLETE  
**Last Updated**: 2026-05-15  

---

## 1. Title and Description

This workplan addresses SSOT (Single Source of Truth) and schema-driven compliance violations identified across the `dcc/workflow` codebase through systematic multi-pass scans of all functions, classes, and global parameters.

**v0.1–v0.6 (original scope):** 35 violations across 24 production files and 4 schema files, organized into 3 implementation phases (A: 12 tasks, B: 12 tasks, C: 15 tasks). Completed 2026-05-12.

**v1.0 (new scope — 2026-05-15):** A previously unaddressed violation category was discovered: **error message text is hardcoded in 63 `detect_error()` calls across 9 detector files**, while the `message` field in `data_error_config.json` exists but is never read at runtime — it is dead metadata. Additionally, 8 error codes used in code are missing from the catalog, and 1 catalog code is never used. This expands the scope by +12 violations across 11 files.

The goal is to ensure that all business rules, column names, processing phases, status values, thresholds, filenames, error codes, severity levels, **message templates**, and configuration defaults are driven exclusively by the schema and `PipelineContext` — with no values duplicated or hardcoded in Python logic.

---

## 2. Revision Control & Version History

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 0.1 | 2026-05-07 | System | Initial workplan created from SSOT/schema-driven compliance scan of dcc/workflow |
| 0.2 | 2026-05-07 | System | Added schema file column to all tables. Confirmed APP/VOID/PEN/REJ/NAP/AWC/INF are SSOT in `approval_code_schema.json`. Confirmed `allowed_values` for YES/NO/RESUBMITTED/PENDING in `dcc_register_config.json`. Confirmed `data_error_config.json` has severity/layer per error code but missing `processing_phase` field — schema update required. Confirmed `Submission_Session` validation pattern `^[0-9]{6}$` in `dcc_register_config.json`. |
| 0.3 | 2026-05-07 | System | Completed schema file column in all phase task tables and files tables. Updated Phase B risks to reflect confirmed `SESSION_PATTERN` already in schema. Expanded Phase A files table to include `date.py` and `composite.py`. Clarified `dcc_global_parameters.json` schema updates required for B5, C4, C5, C6. |
| 0.4 | 2026-05-07 | System | Full output file compliance audit added. Found 12 pipeline outputs — 7 partially compliant (`.get()` pattern used but parameter keys missing from schema), 4 violations (hardcoded literals). Added V16–V21 to violation table. Expanded Phase B with dedicated output file task group (B5a–B5f). Added 9 missing parameter keys to `dcc_global_parameters.json` schema update requirement. Updated Schema File Reference Map, Object, Impact Assessment, and References. |
| 0.5 | 2026-05-07 | System | Deep global scan completed. Found 5 additional violation categories: (1) 55 hardcoded `severity=` strings in 9 detector files — must read from `data_error_config.json`; (2) 4 severity mismatches between detectors and catalog (`input.py`, `row_validator.py`); (3) 11 error codes in `calculation.py`, `fill.py`, `logic.py` missing from `data_error_config.json`; (4) 41 hardcoded column names in 6 detector files — must read from schema `processing_phase`, `source_columns`, `is_anchor`; (5) `ROW_ERROR_WEIGHTS`, `ANCHOR_REQUIRED`, `DOC_ID_SEGMENTS`, `IDENTITY_COLUMNS`, `ANCHOR_COLUMNS` class-level constants in detectors must be schema-driven. Added V22–V26. Phase C expanded with detector catalog tasks. |
| 0.6 | 2026-05-07 | System | PipelineContext audit completed. Found 6 violations: (1) `severity_levels` numeric ordering dict hardcoded in `should_fail_fast()` — not in any schema; (2) `get_fail_fast_config()` default `severity_threshold: "critical"` not in schema; (3) `add_system_error()`/`add_data_error()` hardcoded severity defaults; (4) `SchemaPaths` hardcodes 3 schema filenames not in `project_config.json` schema_files list; (5) `SchemaPaths.validate_required_schemas()` hardcodes required schema list instead of reading from `project_config.json`; (6) `SchemaPaths.global_parameters` still references deprecated `global_parameters.json`. Added V27–V32. Phase A extended with context fixes. |
| 0.7 | 2026-05-07 | System | Phase A validated and marked complete. All 12 tasks passed automated validation suite (A1–A12) and pipeline smoke test. Phase A report generated. Scope summary V01–V05d, V13, V27–V32 updated to COMPLETE. |
| 0.9 | 2026-05-12 | System | Phase C completed. All 15 tasks implemented: C1–C15. Schema updates: dcc_global_parameters.json (fill_jump_limit, fill_max_percentage, health_pass_threshold, health_fail_threshold, health_grade_thresholds), dcc_register_config.json (is_anchor: true on 6 anchor columns). All files pass syntax check. |
| 1.0 | 2026-05-15 | System | Post-completion audit discovered error messages are not schema-driven. Added V33–V44 (12 new violations). Added Phase D (message_template externalization — 54 call sites updated, 11 files). Added Phase E (split 6 multi-semantic codes into 16 affixed codes; add 7 missing codes; replace legacy keys; resolve orphan code). Updated Object, Scope Summary, Violation Table, Dependencies, Evaluation, and References. |
| 1.1 | 2026-05-15 | System | Phase D implemented: 54/63 hardcoded messages replaced. Phase E implemented: 7 missing codes added, 6 multi-semantic codes split into 16 affixed (-A/-B/-C) variants, 2 legacy string keys replaced with L3-L-V-0308/0309, orphan L3-L-V-0307 removed. Catalog expanded from 29 to 55 codes. |
| 1.2 | 2026-05-15 | System | Phase E cleanup: input.py and schema.py updated to use error code class constants instead of raw string literals — error code defined once, referenced via constant in error_code / _format_message / _get_severity. All 9 detectors now use consistent constant pattern. |
| 1.3 | 2026-05-15 | System | Post-completion audit found 56 hardcoded severity fallbacks (5 mismatches with catalog) and 12 hardcoded remediation_type strings. Added Phase F: auto-resolve severity + remediation from catalog in detect_error(), eliminating need for caller to pass them. |
| 1.4 | 2026-05-15 | System | Phase F implemented: remediation/remediation_type fields added to all 55 catalog entries; _get_remediation()/_get_remediation_type() helpers in base.py; detect_error() auto-resolves severity, remediation, remediation_type from catalog; all 56 call sites cleaned up; 5 severity mismatches resolved. |

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
14. **Adding `message_template` field to `data_error_config.json`** — the existing `message` field is a static description never read at runtime; `message_template` with `{placeholder}` syntax becomes the SSOT for error message text
15. **Replacing 54 hardcoded f-string messages in 9 detector files** with `BaseDetector._format_message()` reading from the error catalog
16. **Adding 7 missing error codes** to catalog (`P2-I-P-0201`, `P2-I-P-0202`, `P2-I-V-0203`, `P1-A-V-0102`, `P1-A-V-0103`, `V5-I-V-0505`, `V5-I-V-0506`)
17. **Splitting 6 multi-semantic error codes into 16 distinct codes using letter affix** (`-A`, `-B`, `-C`) — each detection scenario gets its own code with its own `message_template`
18. **Replacing legacy string keys** `GROUP_INCONSISTENT` / `INCONSISTENT_SUBJECT` with standardized `LL-M-F-XXXX` codes
19. **Auto-resolving severity from catalog in `detect_error()`** — severity has been read from catalog via `_get_severity()` since Phase C, but callers still pass a hardcoded fallback string. `detect_error()` should resolve severity from the `error_code` automatically.
20. **Adding `remediation_type` to the catalog** and auto-resolving it in `detect_error()` — currently 12 hardcoded `"MANUAL_FIX"` strings in 2 files, and 0 in the other 7 files.

---

## 4. Scope Summary

### Schema File Reference Map

All values that must be read from schema are sourced from these files:

| Schema File | Path | Contains |
|:---|:---|:---|
| `project_config.json` | `dcc/config/schemas/project_config.json` | Project structure: `folders`, `schema_files` (with `required` flag), `system_parameters` (includes `fail_fast`). **Missing**: `severity_threshold` for fail-fast config, `severity_level_order` for numeric ordering, `error_domain_names`, `phase_status_values` — must be added (see V27–V30) |
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

> **Key finding — PipelineContext audit:** `PipelineContext` and `SchemaPaths` contain 6 violations. The most impactful are: (1) `severity_levels` numeric ordering dict `{"critical": 4, "high": 3, "medium": 2, "low": 1}` is hardcoded in `should_fail_fast()` — the enum is defined in `error_code_base.json` but the ordering is not; (2) `get_fail_fast_config()` returns a hardcoded default `{"enabled": True, "severity_threshold": "critical"}` — `fail_fast` exists in `project_config.json` `system_parameters` but `severity_threshold` does not; (3) `SchemaPaths` hardcodes 3 schema filenames (`dcc_register_config.json`, `dcc_register_enhanced.json`, `data_error_config.json`) not listed in `project_config.json` `schema_files`; (4) `SchemaPaths.validate_required_schemas()` hardcodes a required schema list instead of reading from `project_config.json`.

> **Key finding — `error_code_base.json` already defines severity enum:** `error_severity` enum = `["FATAL", "CRITICAL", "HIGH", "MEDIUM", "WARNING", "INFO"]`. The numeric ordering for `should_fail_fast()` should be derived from this enum's position, not hardcoded as a separate dict.

> **Key finding — Error messages are NOT schema-driven (v1.0):** The `message` field in `data_error_config.json` exists as a static description but is never read at runtime. All 63 `detect_error()` calls across 9 detector files hardcode f-string messages directly. Additionally, 8 error codes used in code have no catalog entry at all, and 1 catalog code (`L3-L-V-0307`) is never used in any detector. A new phase (Phase D) adds `message_template` to the catalog and replaces 54 hardcoded messages with `_format_message()` catalog lookups. Remaining items (8 missing codes, legacy string keys, multi-semantic code reuse, unused catalog code) are deferred to Phase E.

---

### Violation Table

| ID | Category | Violation | Location | Schema File | Field to Read | Severity | Phase |
|:---|:---|:---|:---|:---|:---|:---:|:---:|
| V01 | Schema-Driven | Hardcoded sibling column names in calculation handlers | `conditional.py` lines 80–302, `null_handling.py`, `composite.py`, `date.py` | `dcc_register_config.json` | `columns[col].calculation.dependencies[]` | HIGH | A ✅ |
| V02 | Schema-Driven | Hardcoded `"Validation_Errors"` and `"Data_Health_Score"` column names in engine | `processor_engine/core/engine.py` lines 377, 382 | `dcc_register_config.json` | `column_sequence` — find by `processing_phase: P3` + `is_calculated: true` | HIGH | A ✅ |
| V03 | Schema-Driven | Hardcoded phase strings `"P1"`, `"P2"`, `"P2.5"`, `"P3"`, `"P4"` in `apply_phased_processing()` | `processor_engine/core/engine.py` lines 284–368 | `dcc_register_config.json` | `columns[col].processing_phase` — iterate `blueprint.phase_map.keys()` | HIGH | B ✅ |
| V04 | Schema-Driven | Hardcoded phase map init `{"P1": [], "P2": [], "P2.5": [], "P3": []}` in `build_blueprint()` | `schema_engine/validator/schema_validator.py` line 164 | `dcc_register_config.json` | `columns[col].processing_phase` — build dynamically via `setdefault` | LOW | B ✅ |
| V05a | Schema-Driven | Hardcoded `'YES'`, `'NO'`, `'RESUBMITTED'`, `'PEN'` in `conditional.py` | `conditional.py` lines 113–154 | `dcc_register_config.json` | `columns['Resubmission_Required'].validation[type=allowed_values].allowed_values` = `['YES','NO','RESUBMITTED','PEN']` | HIGH | A ✅ |
| V05b | Schema-Driven | Hardcoded `'Overdue'`, `'NO'` in `conditional.py` | `conditional.py` lines 296–302 | `dcc_register_config.json` | `columns['Resubmission_Overdue_Status'].validation[type=allowed_values].allowed_values` = `['Resubmitted','Overdue','NO']` | HIGH | A ✅ |
| V05c | Schema-Driven | Hardcoded `['APP', 'VOID']` approval codes in `conditional.py` | `conditional.py` line 230 | `approval_code_schema.json` | Filter `approval_codes[]` where `status` in `['Approved','Void']` → codes `APP`, `VOID`. **SSOT: `approval_code_schema.json`** | HIGH | A ✅ |
| V05d | Schema-Driven | Hardcoded `'YES'` for `Submission_Closed` check in `date.py`, `composite.py` | `date.py:148`, `composite.py:188` | `dcc_register_config.json` | `columns['Submission_Closed'].validation[type=allowed_values].allowed_values[0]` = `'YES'` | HIGH | A ✅ |
| V06 | Schema-Driven | Hardcoded `ERROR_CODES` dict in `validation.py` | `processor_engine/calculations/validation.py` line 70 | `data_error_config.json` | `data_logic_errors[code].message`, `.name` | MEDIUM | C |
| V07 | Schema-Driven | Hardcoded severity/layer maps in `categorizer.py` | `processor_engine/error_handling/resolution/categorizer.py` lines 44–70 | `data_error_config.json` | `data_logic_errors[code].severity`, `.layer` — **already in schema** | MEDIUM | C ✅ |
| V08 | Schema-Driven | Hardcoded error-to-phase mapping dict in `evidence.py` | `ai_ops_engine/core/evidence.py` lines 19–31 | `data_error_config.json` | `data_logic_errors[code].processing_phase` — **field missing, must be added to schema** | MEDIUM | C |
| V09 | Schema-Driven | Hardcoded output filenames as literals | `report_errors.py:149,100`, `persistence.py:20`, `log_state.py:61` | `dcc_global_parameters.json` | `dcc_parameters.error_dashboard_filename`, `.error_diagnostic_log_filename`, `.schema_validation_status_filename`, `.debug_log_filename` — **keys missing, must be added** | MEDIUM | B ✅ |
| V10 | Schema-Driven | Hardcoded health score grade thresholds and pass/fail thresholds | `report_health.py` lines 60–72, `report_errors.py:57` | `dcc_global_parameters.json` | `dcc_parameters.health_grade_thresholds`, `.health_pass_threshold`, `.health_fail_threshold` — **keys missing, must be added** | MEDIUM | C |
| V11 | Schema-Driven | Hardcoded `SESSION_PATTERN = re.compile(r'^\d{6}$')` class constant | `detectors/anchor.py` line 45 | `dcc_register_config.json` | `columns['Submission_Session'].validation[type=pattern].pattern` = `"^[0-9]{6}$"` — **already in schema** | MEDIUM | B ✅ |
| V12 | Schema-Driven | Hardcoded `DOC_ID_PATTERN` fallback regex class constant | `detectors/identity.py` line 64 | `dcc_register_config.json` | `columns['Document_ID'].validation[type=pattern].pattern` — schema-driven path already at line 278; fallback to be removed | LOW | B ✅ |
| V13 | SSOT | `ErrorReporter.output_dir` and `effective_parameters` patched post-construction | `dcc_engine_pipeline.py` lines 203–204, 212–213 | `context.paths`, `context.parameters` | `context.paths.csv_output_path.parent`, `context.parameters` — already in context, pass at construction | MEDIUM | A ✅ |
| V14 | SSOT | `_SCHEMA_REF_KEY_MAP` hardcoded in `validation.py` (duplicate of `base_processor.py` default) | `processor_engine/calculations/validation.py` lines 41–50 | `dcc_register_config.json` | `schema_data.get('schema_reference_map', {...})` — use same pattern as `base_processor.py` | LOW | B ✅ |
| V15 | Schema-Driven | Hardcoded `jump_limit=20` default in fill detector | `detectors/fill.py:48`, `detectors/business.py:109` | `dcc_global_parameters.json` | `dcc_parameters.fill_jump_limit` — **key missing, must be added** | LOW | C |
| V16 | Schema-Driven | 9 output filename parameter keys used in code but absent from `dcc_global_parameters.json` | `boot_pipeline.py`, `path_resolvers.py`, `report_errors.py`, `context_builder.py`, `ai_ops_engine/core/engine.py` | `dcc_global_parameters.json` | `output_filename_pattern`, `summary_filename`, `error_dashboard_filename`, `debug_log_filename`, `ai_insight_summary_filename`, `ai_insight_report_filename`, `ai_insight_trace_filename`, `schema_validation_status_filename`, `ai_runs_db_filename` — **all missing from schema** | HIGH | B ✅ |
| V17 | Schema-Driven | `debug_log.json` hardcoded literal in `log_state.py` | `core_engine/logging/log_state.py:61` | `dcc_global_parameters.json` | `dcc_parameters.debug_log_filename` — **must add key to schema first** | MEDIUM | B ✅ |
| V18 | Schema-Driven | `schema_validation_status.json` path hardcoded in `persistence.py` | `schema_engine/status/persistence.py:20` | `dcc_global_parameters.json` | `dcc_parameters.schema_validation_status_filename` — **must add key to schema first** | MEDIUM | B ✅ |
| V19 | Schema-Driven | `error_diagnostic_log.csv` hardcoded as function default in `report_errors.py` | `reporting_engine/core/report_errors.py:100` | `dcc_global_parameters.json` | `dcc_parameters.error_diagnostic_log_filename` — **must add key to schema first** | MEDIUM | B ✅ |
| V20 | Schema-Driven | `dcc_runs.duckdb` hardcoded in `AiOpsEngine.__init__` and `RunStore` | `ai_ops_engine/core/engine.py:60`, `ai_ops_engine/persistence/run_store.py:18` | `dcc_global_parameters.json` | `dcc_parameters.ai_runs_db_filename` — **must add key to schema first** | MEDIUM | B ✅ |
| V21 | Schema-Driven | `debug.json` hardcoded in UI contract path | `initiation_engine/core/init_overrides.py:95` | `dcc_global_parameters.json` | `dcc_parameters.debug_log_filename` — same key as V17, consistent naming | LOW | B ✅ |
| V22 | Schema-Driven | 55 hardcoded `severity=` strings in 9 detector files — severity must come from error catalog | `detectors/row_validator.py` (9), `detectors/calculation.py` (9), `detectors/fill.py` (8), `detectors/schema.py` (7), `detectors/input.py` (7), `detectors/logic.py` (5), `detectors/identity.py` (5), `detectors/anchor.py` (4), `detectors/validation.py` (1) | `data_error_config.json` | `data_logic_errors[code].severity` — **already in catalog for 17 codes; 11 codes missing (see V23)** | HIGH | C |
| V23 | Schema-Driven | 11 error codes used in detectors are missing from `data_error_config.json` | `detectors/calculation.py`: `C6-C-C-0601/0602/0603/0605/0606`; `detectors/fill.py`: `F4-C-F-0401/0402/0403/0404/0405`; `detectors/logic.py`: `L3-L-W-0304` | `data_error_config.json` | Must add 11 entries with `code`, `name`, `message`, `severity`, `layer`, `processing_phase` — **schema update required before V22** | HIGH | C ✅ |
| V24 | Schema-Driven | 4 severity mismatches between detector code and `data_error_config.json` catalog | `detectors/input.py`: `S1-I-F-0805` (code=HIGH, catalog=CRITICAL), `S1-I-V-0502` (code=HIGH, catalog=CRITICAL); `detectors/row_validator.py`: `P1-A-P-0101` (code=HIGH, catalog=CRITICAL), `L3-L-V-0306` (code=LOW, catalog=MEDIUM) | `data_error_config.json` | `data_logic_errors[code].severity` — catalog is SSOT; detector code must be corrected | HIGH | C ✅ |
| V25 | Schema-Driven | Class-level column constant lists in detectors hardcode column names that should come from schema | `detectors/anchor.py`: `ANCHOR_COLUMNS` (5 cols); `detectors/identity.py`: `IDENTITY_COLUMNS` (4 cols); `detectors/row_validator.py`: `ANCHOR_REQUIRED` (5 cols), `DOC_ID_SEGMENTS` (5 cols) | `dcc_register_config.json` | `ANCHOR_COLUMNS` → P1 columns with `required: true`; `DOC_ID_SEGMENTS` → `columns['Document_ID'].calculation.source_columns`; `IDENTITY_COLUMNS` → P2 columns with `required: true`. **Schema must add `is_anchor` flag** | HIGH | C |
| V26 | Schema-Driven | `ROW_ERROR_WEIGHTS` dict in `row_validator.py` hardcodes health score weights per error code | `detectors/row_validator.py` lines 38–49 | `data_error_config.json` | `data_logic_errors[code].health_score_impact` — **already present in catalog** (e.g., `P1-A-P-0101: -20`); detector must read from catalog instead of maintaining a parallel dict | MEDIUM | C |
| V27 | Schema-Driven | `severity_levels` numeric ordering dict hardcoded in `should_fail_fast()` | `context_pipeline.py:323` | `error_code_base.json` | `definitions.error_severity.enum` = `["FATAL","CRITICAL","HIGH","MEDIUM","WARNING","INFO"]` — derive ordering from enum position; **`severity_level_order` key missing from schema** | MEDIUM | A ✅ |
| V28 | Schema-Driven | `get_fail_fast_config()` default `severity_threshold: "critical"` hardcoded | `context_pipeline.py:45` | `project_config.json` | `system_parameters.severity_threshold` — **key missing, must be added** | MEDIUM | A ✅ |
| V29 | Schema-Driven | `add_system_error()` default `severity="critical"` and `add_data_error()` default `severity="medium"` hardcoded | `context_pipeline.py:216, 241` | `project_config.json` | `system_parameters.default_system_error_severity`, `system_parameters.default_data_error_severity` — **keys missing, must be added** | LOW | A ✅ |
| V30 | Schema-Driven | `SchemaPaths` hardcodes 3 schema filenames not in `project_config.json` `schema_files` list | `core_engine/paths/path_schema.py` | `project_config.json` | `schema_files[].filename` — `dcc_register_config.json`, `dcc_register_enhanced.json`, `data_error_config.json` must be added to `schema_files` list | MEDIUM | A ✅ |
| V31 | Schema-Driven | `SchemaPaths.validate_required_schemas()` hardcodes required schema list | `core_engine/paths/path_schema.py:120–127` | `project_config.json` | `schema_files[].filename` where `required: true` — read from schema instead of hardcoded list | LOW | A ✅ |
| V32 | Schema-Driven | `SchemaPaths.global_parameters` property references deprecated `global_parameters.json` | `core_engine/paths/path_schema.py:65` | `project_config.json` | `schema_files[].filename` where `filename == 'dcc_global_parameters.json'` — update property to use current filename | LOW | A ✅ |
| V33 | Schema-Driven | `message` field in `data_error_config.json` exists but is never read — dead metadata | `config/schemas/data_error_config.json` | `data_error_config.json` | `message` field present but no runtime code reads it — must add `message_template` with `{placeholder}` syntax | HIGH | D ✅ |
| V34 | Schema-Driven | 54 `message=` f-strings hardcoded in 9 detector files — must read from catalog | `detectors/row_validator.py` (9), `calculation.py` (9), `fill.py` (9), `schema.py` (7), `input.py` (7), `logic.py` (5), `identity.py` (1), `anchor.py` (2), `validation.py` (5) | `data_error_config.json` | `data_logic_errors[code].message_template` | HIGH | D ✅ |
| V35 | Schema-Driven | Error code `P2-I-P-0201` used in `identity.py` but missing from catalog | `detectors/identity.py:151` | `data_error_config.json` | Missing entry — must add with `code`, `name`, `message`, `severity`, `layer`, `processing_phase` | HIGH | E |
| V36 | Schema-Driven | Error code `P2-I-P-0202` used in `identity.py` but missing from catalog | `detectors/identity.py:180` | `data_error_config.json` | Missing entry | HIGH | E |
| V37 | Schema-Driven | Error code `P2-I-V-0203` used in `identity.py` but missing from catalog | `detectors/identity.py:233,252` | `data_error_config.json` | Missing entry | HIGH | E |
| V38 | Schema-Driven | Error code `P1-A-V-0102` used in `anchor.py` but missing from catalog | `detectors/anchor.py:197` | `data_error_config.json` | Missing entry | MEDIUM | E |
| V39 | Schema-Driven | Error code `P1-A-V-0103` used in `anchor.py` but missing from catalog | `detectors/anchor.py:236` | `data_error_config.json` | Missing entry | MEDIUM | E |
| V40 | Schema-Driven | Error code `V5-I-V-0505` used in `validation.py` but missing from catalog | `detectors/validation.py:373` | `data_error_config.json` | Missing entry | HIGH | E |
| V41 | Schema-Driven | Error code `V5-I-V-0506` used in `validation.py` but missing from catalog | `detectors/validation.py:417` | `data_error_config.json` | Missing entry | HIGH | E |
| V42 | Schema-Driven | Catalog code `L3-L-V-0307` defined but never used in any detector | `config/schemas/data_error_config.json` | `data_error_config.json` | Orphan code — either implement detection logic or remove from catalog | LOW | E |
| V43 | Schema-Driven | Legacy string keys `"GROUP_INCONSISTENT"` and `"INCONSISTENT_SUBJECT"` in `row_validator.py` | `detectors/row_validator.py:~497,~630` | `data_error_config.json` | Must be replaced with standardized `LL-M-F-XXXX` codes | MEDIUM | E |
| V44 | Schema-Driven | Multi-semantic code reuse — same error code used for semantically different detection scenarios | `detectors/identity.py` (P2-I-V-0204: 3 scenarios), `row_validator.py` (P2-I-V-0204: 2 of 3), `detectors/fill.py` (F4-C-F-0401: 2, F4-C-F-0402: 2, F4-C-F-0403: 3), `detectors/calculation.py` (C6-C-C-0605: 4), `detectors/logic.py` (L3-L-V-0303: 2), `detectors/input.py` (S1-I-F-0805: 2) | `data_error_config.json` | Split into distinct codes using letter affix: `-A`, `-B`, `-C` per detection scenario | MEDIUM | E |

**Status Legend:** 🔵 PLANNED | 🟡 IN PROGRESS | ✅ COMPLETE | ❌ DEFERRED

**Violation Count (Phase A–E):** 44 items — 13 HIGH, 19 MEDIUM, 12 LOW — **ALL COMPLETED**  
**Violation Count (Phase F — new):** 2 items — 0 HIGH, 0 MEDIUM, 2 LOW  
**Files Affected:** 35 production files across 6 engines  
**Final Catalog Size:** 55 error codes (29 original + 7 new + 16 affix variants + 2 legacy replacements - 1 orphan removed)  
**Schema Updates Required (original scope — completed):**
- `dcc_global_parameters.json` — add 13 parameter keys: 9 output filenames + `fill_jump_limit` + `health_grade_thresholds` + `health_pass_threshold` + `health_fail_threshold`
- `data_error_config.json` — add `processing_phase` field to all 17 existing entries; add 11 missing error code entries; confirm `health_score_impact` present on all entries
- `dcc_register_config.json` — add `is_anchor: true` flag to P1 anchor columns
- `project_config.json` — add `severity_threshold`, `default_system_error_severity`, `default_data_error_severity` to `system_parameters`; add `dcc_register_config.json`, `dcc_register_enhanced.json`, `data_error_config.json` to `schema_files` list

**Schema Updates Required (Phase D — completed):**
- `data_error_config.json` — add `message_template` field to all 29 existing entries with `{placeholder}` syntax for dynamic values

**Schema Updates Required (Phase E — completed):**
- `data_error_config.json` — added 7 missing error codes; split 6 multi-semantic codes into 16 affixed variants; added 2 codes for legacy string keys; removed orphan `L3-L-V-0307`. Catalog expanded from 29 to 55 codes.

**Schema Updates Required (Phase F — planned):**
- `data_error_config.json` — add `remediation` (remedy description) and `remediation_type` (classification) fields to all 55 entries

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
  - [Phase D — Message Template Externalization](#phase-d--message-template-externalization)
  - [Phase E — Catalog Completion and Cleanup](#phase-e--catalog-completion-and-cleanup)
  - [Phase F — Auto-Resolve Severity and Remediation from Catalog](#phase-f--auto-resolve-severity-and-remediation-from-catalog)
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
| Section 4.3 | SSOT for global parameters, variables, keys, codes, values | ✅ Phase D extends SSOT to error message text via `message_template` |
| Section 8.2 | Workplan must include revision control, scope, phases, risks | ✅ v1.0 updated with Phase D/E, new violations, full compliance |

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
| Phase A | 10 files + 2 schema files | Low-Medium — calculation handler behavior + PipelineContext defaults + SchemaPaths fixes |
| Phase B | 12 files + 1 schema file | 🟡 Low-Medium — structural, behavior-preserving; schema update is prerequisite |
| Phase C | 19 files + 3 schema files | 🟡 Medium — schema updates required first; detector changes are behavior-preserving once catalog is complete |
| Phase D | 11 files + 1 schema file | 🟢 Low — externalization only, no logic change; 54 call sites replaced with catalog lookup |
| Phase E | 5 files + 1 schema file | 🟢 Low — additive catalog entries; legacy key replacement; cleanup only |

---

## 7. Dependencies with Other Tasks

1. **WP-PIPE-SIMP-001** — [pipeline_simplification_workplan.md](pipeline_simplification/pipeline_simplification_workplan.md) — Completed. Phase D removed legacy schema fallbacks; this workplan builds on the clean schema architecture that remains.
2. **WP-PIPE-ARCH-001** — [pipeline_architecture_design_workplan.md](pipeline_architecture_workplan/pipeline_architecture_design_workplan.md) — R05 (Schema-Driven Logic) and R07 (Error Categorization) are directly addressed by this workplan.
3. **Error Handling Workplan** — `dcc/workplan/error_handling/` — V06, V07, V08 touch the error catalog and categorizer; coordinate with any active error handling work.
4. **Schema files** — `dcc/config/schemas/dcc_register_config.json` — Phase A requires verifying that `allowed_values`, `choices`, and `depends_on` fields are present in the schema for affected columns. Schema updates may be needed before code changes.
5. **agent_rule.md** — Section 2 (Schema), Section 1 (Data Columns), Section 8 (Workplan)
6. **Phase D requires Phase C completion** — `_get_severity()` and error catalog infrastructure from Phase C is prerequisite for `_format_message()` added in Phase D.
7. **Phase E requires Phase D completion** — `_format_message()` helper and catalog `message_template` from Phase D is prerequisite for adding missing codes (V35–V41) and legacy key replacement (V43).
8. **Phase F requires Phase E completion** — 55-entry catalog with all codes populated is prerequisite for adding `remediation_type` field and auto-resolving in `detect_error()`.

---

## 8. Implementation Phases and Task Breakdown

---

### Phase A — High-Severity Fixes
**Status:** ✅ COMPLETED (2026-05-09)  
**Timeline:** Completed (1 session)  
**Milestone:** Zero hardcoded column names or business logic values in calculation handlers  
**Risk Level:** 🟡 Medium — changes how calculation handlers resolve sibling columns and status values

**Timeline:** Completed (1 session)  
**Milestone:** No hardcoded column names or business logic values in calculation handlers  
**Risk Level:** 🟡 Medium — changes how calculation handlers resolve sibling columns and status values

#### Pre-Condition Checklist (must verify before coding)

- [x] Confirm `conditional.py` column dependencies (`Submission_Closed`, `Document_ID`, `Submission_Date`, `Review_Return_Actual_Date`, `Resubmission_Required`, `Latest_Approval_Code`) are declared in `dcc_register_config.json` — **CONFIRMED**: `columns['Submission_Closed'].calculation.dependencies` = `['Latest_Approval_Code', 'Document_ID', 'Submission_Date', 'Latest_Submission_Date']`
- [x] Confirm `allowed_values` fields exist in schema for status columns — **CONFIRMED**: `Submission_Closed` = `['YES','NO']`, `Resubmission_Required` = `['YES','NO','RESUBMITTED','PEN']`, `Resubmission_Overdue_Status` = `['Resubmitted','Overdue','NO']`
- [x] Confirm `approval_codes` reference list in schema contains `APP` and `VOID` — **CONFIRMED**: `approval_code_schema.json` has `APP` (Approved) and `VOID` (Void) as SSOT codes
- [x] Confirm `Validation_Errors` and `Data_Health_Score` are in `column_sequence` in schema — **CONFIRMED**: both at positions 47–48 in `dcc_register_config.json` `column_sequence`

#### Tasks

| # | Task | File | Action | Status |
|:---|:---|:---|:---|:---|
| A1 | Replace hardcoded sibling column lookups in `conditional.py` | `conditional.py` | Read column dependencies from `calculation.get('dependencies', [])` | ✅ |
| A2 | Replace hardcoded status values in `conditional.py` | `conditional.py` | Read `'YES'`/`'NO'`/`'RESUBMITTED'`/`'PEN'` from `allowed_values` | ✅ |
| A3 | Replace `['APP', 'VOID']` hardcoded approval codes | `conditional.py` | Read from `engine.schema_data['approval_codes']` | ✅ |
| A4 | Replace hardcoded output columns in engine | `engine.py` | Read column names from `context.blueprint.phase_map['P3']` | ✅ |
| A5 | Replace hardcoded row key lookups | `null_handling.py` | Read key columns from schema `columns[col].is_row_key: true` | ✅ |
| A6 | Fix `ErrorReporter` post-construction patching | `engine.py`, `pipeline.py` | Pass `output_dir` and `parameters` at construction | ✅ |
| A7 | Add severity defaults to `project_config.json` | `project_config.json` | Add `severity_threshold` and default severity keys | ✅ |
| A8 | Replace hardcoded `severity_levels` in context | `context_pipeline.py` | Derive ordering from `error_code_base.json` enum position | ✅ |
| A9 | Replace hardcoded severity defaults in context | `context_pipeline.py` | Read defaults from `blueprint.validation_rules` | ✅ |
| A10 | Add missing schema files to `project_config.json` | `project_config.json` | Add `dcc_register_config.json`, etc. | ✅ |
| A11 | Dynamic required schema validation | `path_schema.py` | Read required list from `project_config.json` | ✅ |
| A12 | Fix `global_parameters` deprecated reference | `path_schema.py` | Update to reference `dcc_global_parameters.json` | ✅ |

#### Files Updated/Created

| File | Action | Schema File Used | Status |
|:---|:---|:---|:---|
| `dcc/config/schemas/project_config.json` | Updated | — | ✅ |
| `dcc/workflow/processor_engine/calculations/conditional.py` | Updated | `dcc_register_config.json`, `approval_code_schema.json` | ✅ |
| `dcc/workflow/processor_engine/calculations/null_handling.py` | Updated | `dcc_register_config.json` | ✅ |
| `dcc/workflow/processor_engine/calculations/date.py` | Updated | `dcc_register_config.json` | ✅ |
| `dcc/workflow/processor_engine/calculations/composite.py` | Updated | `dcc_register_config.json` | ✅ |
| `dcc/workflow/processor_engine/core/engine.py` | Updated | `dcc_register_config.json` | ✅ |
| `dcc/workflow/dcc_engine_pipeline.py` | Updated | — | ✅ |
| `dcc/workflow/core_engine/context/context_pipeline.py` | Updated | `error_code_base.json`, `project_config.json` | ✅ |
| `dcc/workflow/core_engine/paths/path_schema.py` | Updated | `project_config.json` | ✅ |
| `dcc/config/schemas/dcc_register_config.json` | Updated | — | ✅ |
| `dcc/workplan/pipeline_architecture/ssot_schema_driven_compliance/reports/phase_A_report.md` | Created | — | ✅ |

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
- [x] Pre-condition checklist passed
- [x] Zero hardcoded column names in `conditional.py`
- [x] Zero hardcoded status values (`'YES'`/`'NO'`/`'RESUBMITTED'`/`'PENDING'`/`'Overdue'`) in calculation handlers
- [x] `['APP', 'VOID']` replaced with schema reference lookup
- [x] `"Validation_Errors"` and `"Data_Health_Score"` not hardcoded in `engine.py`
- [x] `ErrorReporter` receives `output_dir` and `effective_parameters` at construction, not post-patched
- [x] `severity_levels` dict removed from `should_fail_fast()` — ordering derived from `error_code_base.json` enum
- [x] `severity_threshold` default reads from `project_config.json` `system_parameters`
- [x] `add_system_error()` and `add_data_error()` severity defaults read from schema
- [x] `SchemaPaths.validate_required_schemas()` reads from `project_config.json` `schema_files`
- [x] `SchemaPaths.global_parameters` references `dcc_global_parameters.json`
- [x] Pipeline smoke test passes

#### Deliverables
- Updated `conditional.py`, `null_handling.py`, `engine.py`, `dcc_engine_pipeline.py`, `context_pipeline.py`, `path_schema.py`
- Updated `project_config.json` (severity defaults + 3 schema file entries)
- `reports/phase_A_report.md` ✅ [View Report](reports/phase_A_report.md)

---

### Phase B — Medium-Severity Structural Fixes ✅ COMPLETE

**Timeline:** Completed 2026-05-07  
**Milestone:** Dynamic phase iteration, schema-driven filenames, schema-driven regex patterns  
**Risk Level:** None — all tasks validated; 3 partial implementations with schema-driven primary paths

#### Tasks

| # | Task | File | Action | Schema File | Schema Field | Status |
|:---|:---|:---|:---|:---|:---|:---|
| B1 | Make `apply_phased_processing()` iterate phases dynamically | `processor_engine/core/engine.py` | Replace 4 hardcoded `get_columns_by_phase('Px')` calls with loop over `context.blueprint.phase_map.keys()` in defined order | `dcc_register_config.json` | `columns[col].processing_phase` — already in `blueprint.phase_map` | 🟡 IN PROGRESS |
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
- [x] `apply_phased_processing()` has no hardcoded phase string literals in the main loop
- [x] `build_blueprint()` phase_map init is dynamic
- [x] `SESSION_PATTERN` schema lookup implemented (fallback constant retained as safety net)
- [x] `DOC_ID_PATTERN` class constant removed
- [x] All 9 output filename parameter keys added to `dcc_global_parameters.json`
- [x] All 12 pipeline outputs use `parameters.get(key, default)` — zero bare hardcoded literals
- [x] `_SCHEMA_REF_KEY_MAP` renamed to `DEFAULT_SCHEMA_REF_KEY_MAP` as fallback; schema-driven primary path
- [x] Pipeline smoke test passes — all 12 output files written correctly

#### Deliverables
- Updated files (see table above)
- `reports/phase_B_report.md` ✅ [View Report](reports/phase_B_report.md)

---

### Phase C — Catalog and Threshold Externalization ✅ COMPLETE

**Timeline:** Completed 2026-05-12  
**Milestone:** Error codes, severity maps, and health thresholds all read from schema/catalog  
**Risk Level:** 🟢 Low — externalization only, no logic change

#### Pre-Condition Checklist

- [x] Confirm `context.blueprint.error_catalog` contains all error codes referenced in `validation.py` `ERROR_CODES` dict — **CONFIRMED**: all 17 original codes present; 11 new codes added (C7 complete)
- [x] Confirm `context.blueprint.error_catalog` contains `processing_phase` field for all codes in `evidence.py` — **CONFIRMED**: `processing_phase` added to all entries as part of C7
- [x] Add 11 missing error codes to `data_error_config.json` — **COMPLETE (C7)**: all 11 codes added with full fields
- [x] Correct 4 severity mismatches in `data_error_config.json` — **COMPLETE (C9)**: catalog corrected
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
- [x] Pre-condition checklist passed
- [x] `ERROR_CODES` dict removed from `validation.py` — replaced with `DEFAULT_VALIDATION_ERROR_CODES` + schema override
- [x] `_severity_map` and `_layer_map` removed from `categorizer.py`
- [x] Hardcoded error-to-phase dict removed from `evidence.py` — catalog-driven with fallback
- [x] Health grade thresholds read from schema parameters
- [x] Pass/fail thresholds read from schema parameters
- [x] `jump_limit` reads from schema parameters
- [x] 11 missing error codes added to `data_error_config.json`
- [x] 4 severity mismatches corrected (catalog is SSOT)
- [x] Zero hardcoded `severity=` strings in all 9 detector files — all use `_get_severity()` via base.py
- [x] `ANCHOR_COLUMNS`, `ANCHOR_REQUIRED`, `DOC_ID_SEGMENTS`, `IDENTITY_COLUMNS` class constants replaced with schema-driven lookups
- [x] `ROW_ERROR_WEIGHTS` replaced with `health_score_impact` from catalog
- [x] `"REJ"` string replaced with `approval_code_schema.json` lookup
- [x] `'PEN'` fallback already schema-driven (no change needed)
- [x] Pipeline smoke test passes

#### Deliverables
- Updated files (see table above — 19 files)
- `reports/phase_C_report.md` 🟡 [View Status Report](reports/phase_C_report.md)

---

### Phase D — Message Template Externalization ✅ COMPLETE

**Timeline:** Completed 2026-05-15  
**Milestone:** Error message text is schema-driven — `message_template` in catalog is SSOT  
**Risk Level:** 🟢 Low — externalization only, no logic change

#### Summary

A post-completion audit discovered that the `message` field in `data_error_config.json` was never read at runtime — all 63 `detect_error()` calls across 9 detector files hardcoded f-string messages. Phase D:
1. Added `message_template` field to all 29 entries in `data_error_config.json` with `{placeholder}` syntax
2. Added `BaseDetector._format_message(error_code, **kwargs)` method in `base.py` (parallel to existing `_get_severity()`)
3. Replaced 54 of 63 hardcoded messages with `self._format_message()` catalog lookups
4. Left 9 calls unchanged (8 for codes not yet in catalog, 1 for legacy `GROUP_INCONSISTENT` key)

#### Design Pattern

Single-message codes use exact template with kwargs:
```python
message=self._format_message("S1-I-F-0804", file_path=file_path)
```

Multi-message codes (same code used for different scenarios) use a generic template from config:
```python
message=self._format_message("F4-C-F-0403")  # Returns canonical description
```

Config stores `message_template` alongside existing `message` field:
```json
"message": "Forward fill row jump exceeded limit",
"message_template": "Forward fill row jump exceeded limit"
```

#### Tasks

| # | Task | File | Action | Status |
|:---|:---|:---|:---|:---:|
| D1 | Add `message_template` to all 29 catalog entries | `data_error_config.json` | Add field with `{placeholder}` syntax matching primary detector message | ✅ |
| D2 | Add `_format_message()` to BaseDetector | `base.py` | Add method reading `message_template` from `error_catalog`, with graceful fallback | ✅ |
| D3 | Update `anchor.py` (2 of 4 messages) | `anchor.py` | Replace P1-A-P-0101 messages; leave P1-A-V-0102/0103 (not in catalog) | ✅ |
| D4 | Update `identity.py` (1 of 5 messages) | `identity.py` | Replace P2-I-V-0204 message; leave P2-I-P-0201/0202, P2-I-V-0203 (not in catalog) | ✅ |
| D5 | Update `row_validator.py` (9 of 10 messages) | `row_validator.py` | Replace all standardized codes; leave `GROUP_INCONSISTENT` legacy key | ✅ |
| D6 | Update `calculation.py` (9 messages) | `calculation.py` | Replace all C6xx messages | ✅ |
| D7 | Update `fill.py` (9 messages) | `fill.py` | Replace all F4xx messages | ✅ |
| D8 | Update `input.py` (7 messages) | `input.py` | Replace all S1xx messages | ✅ |
| D9 | Update `logic.py` (5 messages) | `logic.py` | Replace all L3xx messages | ✅ |
| D10 | Update `schema.py` (7 messages) | `schema.py` | Replace all V5xx messages | ✅ |
| D11 | Update `validation.py` (5 of 7 messages) | `validation.py` | Replace V5-I-V-0501/0502/0503/0504; leave V5-I-V-0505/0506 (not in catalog) | ✅ |

#### Files Modified

| File | Change |
|:---|:---|
| `dcc/config/schemas/data_error_config.json` | Added `message_template` to all 29 entries |
| `dcc/workflow/processor_engine/error_handling/detectors/base.py` | Added `_format_message()` method |
| `dcc/workflow/processor_engine/error_handling/detectors/anchor.py` | 2 messages → `_format_message()` |
| `dcc/workflow/processor_engine/error_handling/detectors/identity.py` | 1 message → `_format_message()` |
| `dcc/workflow/processor_engine/error_handling/detectors/row_validator.py` | 9 messages → `_format_message()` |
| `dcc/workflow/processor_engine/error_handling/detectors/calculation.py` | 9 messages → `_format_message()` |
| `dcc/workflow/processor_engine/error_handling/detectors/fill.py` | 9 messages → `_format_message()` |
| `dcc/workflow/processor_engine/error_handling/detectors/input.py` | 7 messages → `_format_message()` |
| `dcc/workflow/processor_engine/error_handling/detectors/logic.py` | 5 messages → `_format_message()` |
| `dcc/workflow/processor_engine/error_handling/detectors/schema.py` | 7 messages → `_format_message()` |
| `dcc/workflow/processor_engine/error_handling/detectors/validation.py` | 5 messages → `_format_message()` |

#### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|:---|:---:|:---:|:---:|
| Template placeholder name mismatch between config and `_format_message()` kwargs | Low | Medium | `_format_message()` catches `KeyError` and returns unformatted template — no crash |

#### Potential Future Issues
- Multi-message codes (same code, different detection scenarios) use a single generic template — the specific detail is lost in the catalog. If per-variant templates are needed, `message_templates` (plural) as a dict keyed by variant name should be considered.
- 9 hardcoded messages remain for codes not yet in catalog — these must be resolved in Phase E.

#### Success Criteria
- [x] All 29 catalog entries have `message_template` field
- [x] `BaseDetector._format_message()` implemented and tested with syntax check
- [x] 54 of 63 hardcoded messages replaced with catalog lookup
- [x] All 11 modified files pass `ast.parse()` syntax check
- [x] JSON schema file passes `json.load()` validation

#### Deliverables
- Updated files (11 files — see table above)
- Phase D implementation completed in single session

---

### Phase E — Catalog Completion and Cleanup ✅ COMPLETE

**Timeline:** Completed 2026-05-15  
**Milestone:** Every error code used in code has a catalog entry; multi-semantic codes split with affixes; legacy keys eliminated; orphan codes resolved  
**Risk Level:** 🟢 Low — additive catalog entries and code splits only

#### Scope

Phase E addresses remaining violations not covered by Phase D. The core work is two-fold: (1) add 7 missing error codes to the catalog, and (2) split 6 existing multi-semantic codes into distinct codes using **letter affix notation** (`-A`, `-B`, `-C`).

| ID | Violation | Severity |
|:---|:---|:---:|
| V35 | `P2-I-P-0201` used in `identity.py` — missing from catalog | HIGH |
| V36 | `P2-I-P-0202` used in `identity.py` — missing from catalog | HIGH |
| V37 | `P2-I-V-0203` used in `identity.py` — missing from catalog | HIGH |
| V38 | `P1-A-V-0102` used in `anchor.py` — missing from catalog | MEDIUM |
| V39 | `P1-A-V-0103` used in `anchor.py` — missing from catalog | MEDIUM |
| V40 | `V5-I-V-0505` used in `validation.py` — missing from catalog | HIGH |
| V41 | `V5-I-V-0506` used in `validation.py` — missing from catalog | HIGH |
| V42 | `L3-L-V-0307` defined in catalog — never used in any detector — **REMOVED** | LOW |
| V43 | Legacy string keys `"GROUP_INCONSISTENT"` / `"INCONSISTENT_SUBJECT"` in `row_validator.py` | MEDIUM |
| V44 | Multi-semantic code reuse — 6 codes, 16 total detection scenarios | MEDIUM |

#### Affix Split Plan (V44)

Each multi-semantic code is split into distinct codes using a letter affix. The original code is kept as a parent umbrella entry (for backward compatibility); detectors use the affixed child codes.

| Base Code | Split Codes | Affix | Detection Scenario | File |
|:---|:---|:---:|:---|:---:|
| P2-I-V-0204 | P2-I-V-0204-A | -A | Invalid Document_ID format (regex fail) | `identity.py:413` |
| P2-I-V-0204 | P2-I-V-0204-B | -B | Document_ID has fewer than 5 segments | `row_validator.py:258` |
| P2-I-V-0204 | P2-I-V-0204-C | -C | Document_ID composite segment mismatch | `row_validator.py:278` |
| S1-I-F-0805 | S1-I-F-0805-A | -A | Unsupported file format | `input.py:124` |
| S1-I-F-0805 | S1-I-F-0805-B | -B | File too large (exceeds max size) | `input.py:144` |
| F4-C-F-0401 | F4-C-F-0401-A | -A | Forward fill row jump exceeded (history path) | `fill.py:178` |
| F4-C-F-0401 | F4-C-F-0401-B | -B | Potential forward fill detected (heuristic path) | `fill.py:303` |
| F4-C-F-0402 | F4-C-F-0402-A | -A | Forward fill crossed session boundary (history path) | `fill.py:206` |
| F4-C-F-0402 | F4-C-F-0402-B | -B | Value appears in multiple sessions (heuristic path) | `fill.py:357` |
| F4-C-F-0403 | F4-C-F-0403-A | -A | Multi-level fill failed, default applied | `fill.py:248` |
| F4-C-F-0403 | F4-C-F-0403-B | -B | Value may be calculated/inferred | `fill.py:410` |
| F4-C-F-0403 | F4-C-F-0403-C | -C | Default value applied to fill nulls | `fill.py:535` |
| C6-C-C-0605 | C6-C-C-0605-A | -A | Invalid start date in column | `calculation.py:253` |
| C6-C-C-0605 | C6-C-C-0605-B | -B | Invalid end date in column | `calculation.py:268` |
| C6-C-C-0605 | C6-C-C-0605-C | -C | Negative duration detected | `calculation.py:313` |
| C6-C-C-0605 | C6-C-C-0605-D | -D | Date calculation error in column | `calculation.py:393` |
| L3-L-V-0303 | L3-L-V-0303-A | -A | Approved but marked for resubmission | `logic.py:207` |
| L3-L-V-0303 | L3-L-V-0303-B | -B | Closed but review still active | `logic.py:233` |

The original parent codes (`P2-I-V-0204`, `S1-I-F-0805`, `F4-C-F-0401`, `F4-C-F-0402`, `F4-C-F-0403`, `C6-C-C-0605`, `L3-L-V-0303`) are retained in the catalog as umbrella entries for backward compatibility and dashboard aggregation.

#### Proposed Tasks

| # | Task | File | Action |
|:---|:---|:---|:---|
| E1 | Add 7 missing error codes to catalog | `data_error_config.json` | Add entries for P2-I-P-0201, P2-I-P-0202, P2-I-V-0203, P1-A-V-0102, P1-A-V-0103, V5-I-V-0505, V5-I-V-0506 with full fields |
| E2 | Update 7 hardcoded messages to use catalog | `identity.py` (3), `anchor.py` (2), `validation.py` (2) | Replace remaining f-strings with `_format_message()` after E1 |
| E3 | Split P2-I-V-0204 into 3 codes with affix | `data_error_config.json`, `identity.py`, `row_validator.py` | Add P2-I-V-0204-A/B/C; update detector error_code constants and calls |
| E4 | Split S1-I-F-0805 into 2 codes with affix | `data_error_config.json`, `input.py` | Add S1-I-F-0805-A/B; update error_code and detect_error() calls |
| E5 | Split F4-C-F-0401/0402/0403 into 7 codes with affix | `data_error_config.json`, `fill.py` | Add -A/-B/-C variants; update error code constants and detector calls |
| E6 | Split C6-C-C-0605 into 4 codes with affix | `data_error_config.json`, `calculation.py` | Add C6-C-C-0605-A/B/C/D; update error code constants and detector calls |
| E7 | Split L3-L-V-0303 into 2 codes with affix | `data_error_config.json`, `logic.py` | Add L3-L-V-0303-A/B; update error code constants and detector calls |
| E8 | Replace legacy string keys with standardized codes | `row_validator.py`, `data_error_config.json` | Replace `"GROUP_INCONSISTENT"` / `"INCONSISTENT_SUBJECT"` with new codes (e.g., L3-L-V-0308, L3-L-V-0309); add to catalog |
| E9 | Resolve orphan code `L3-L-V-0307` | `data_error_config.json` | Either implement detection logic or remove the unused entry |

#### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|:---|:---:|:---:|:---|
| Affixed codes break dashboard aggregation queries that filter by parent code | Low | Medium | Retain parent code in catalog as umbrella; dashboards can match by prefix `LIKE 'P2-I-V-0204%'` |
| Legacy string keys (GROUP_INCONSISTENT) used in multiple call sites beyond `row_validator.py` | Low | Medium | Search all files for legacy key strings before replacement |
| Detector error_code constants need coordinated updates with catalog entries | Low | Low | Update catalog first, then detector constants, then call sites — sequential verification per task |

#### Potential Future Issues
- Affix convention (`-A`, `-B`, `-C`) must be documented in `data_error_config.json` metadata as the standard for variant splitting
- Dashboard and reporting tools must support prefix-based code matching (e.g., `startswith("P2-I-V-0204")`) to aggregate parent + child codes

#### Success Criteria
- [x] 7 missing error codes added to `data_error_config.json`
- [x] 6 multi-semantic codes split into 16 distinct affixed codes
- [x] All `detect_error()` calls updated to use affixed codes
- [x] Zero hardcoded messages remaining in all 9 detector files
- [x] Legacy string keys eliminated from `row_validator.py`
- [x] `L3-L-V-0307` removed (orphan, never used in any detector)
- [x] Parent umbrella codes retained in catalog for backward compatibility
- [x] All modified files pass `ast.parse()` syntax check
- [x] JSON schema file passes `json.load()` validation

---

### Phase F — Auto-Resolve Severity and Remediation from Catalog ✅ COMPLETE

**Timeline:** Completed 2026-05-15  
**Milestone:** `detect_error()` resolves severity and remediation from catalog automatically — callers pass only `error_code`, `message`, `row`, `column`  
**Risk Level:** 🟢 Low — housed entirely within `base.py`'s `detect_error()` internals

#### Summary

Post-completion audit of all 56 `_get_severity()` calls found:
- All calls pass a hardcoded fallback string (e.g. `_get_severity(code, "HIGH")`)
- 5 of 56 fallbacks **mismatch** the catalog (wrong severity if catalog were missing)
- 12 `remediation_type="MANUAL_FIX"` strings hardcoded in `schema.py` and `input.py`
- 7 detector files omit `remediation_type` entirely (defaults to `None`)

The fix: `detect_error()` already receives `error_code`. It should use that code to look up `severity` and `remediation_type` from the catalog automatically, removing the need for callers to pass them.

#### Violations (newly discovered)

| ID | Category | Violation | Location | Schema File | Severity | Phase |
|:---|:---|:---|:---|:---|:---:|:---:|
| V45 | Schema-Driven | `_get_severity()` fallback hardcoded in all 56 calls — 5 mismatches with catalog | all 9 detector files | `data_error_config.json` | LOW | F |
| V46 | Schema-Driven | `remediation_type="MANUAL_FIX"` hardcoded in 12 calls in 2 files | `schema.py` (6), `input.py` (6) | `data_error_config.json` | LOW | F |

#### Proposed Tasks

| # | Task | File | Action |
|:---|:---|:---|:---|
| F1 | Define `remediation` per error code in catalog | `data_error_config.json` | Add `remediation` field to all 55 entries with a context-appropriate remedy description (e.g. "Verify input file path" for FILE_NOT_FOUND, "Provide valid Document_ID" for DOCUMENT_ID_UNCERTAIN) |
| F1a | Add `remediation_type` field to all 55 catalog entries | `data_error_config.json` | Classify each error as `"MANUAL_FIX"`, `"AUTO_FIX"`, `"REVIEW"`, or `"RERUN"` based on error context |
| F2 | Add `_get_remediation()` and `_get_remediation_type()` to `BaseDetector` | `base.py` | Parallel to `_get_severity()` — reads from `error_catalog[code].remediation` / `.remediation_type` |
| F3 | Make `detect_error()` auto-resolve severity + remediation | `base.py` | If `severity` not explicitly passed, resolve from catalog via `_get_severity()`. Same for `remediation` and `remediation_type`. |
| F4 | Remove `severity=` and `remediation_type=` from all `detect_error()` calls | 9 detector files | Clean up ~68 parameters across 56 calls |
| F5 | Fix 5 severity fallback mismatches | `input.py:221`, `logic.py:212,238`, `row_validator.py:216,592` | Correct fallback strings to match catalog |

#### Remediation Proposal (per context)

| Error Category | Example Codes | Proposed Remediation | Remediation Type |
|:---|:---|:---|:---:|
| Missing/invalid input file | S1-I-F-0804, S1-I-F-0805-A/B | "Verify input file path, format, and size" | MANUAL_FIX |
| Missing/uncertain identity | P2-I-P-0201, P2-I-P-0202 | "Provide valid Document_ID or Document_Revision" | MANUAL_FIX |
| Format/validation violation | V5-I-V-0501..0504, P1-A-V-0102/0103 | "Correct value format per field specification" | MANUAL_FIX |
| Missing required data | S1-I-V-0502, V5-I-V-0505, C6-C-C-0601 | "Add missing required columns or values to input" | MANUAL_FIX |
| Calculation/dependency error | C6-C-C-0602, C6-C-C-0603, C6-C-C-0605-A/B/C/D | "Review calculation inputs and formula logic" | REVIEW |
| Mapping failure | C6-C-C-0606 | "Add mapping for unmapped values or use default" | MANUAL_FIX |
| Fill/boundary warning | F4-C-F-0401-A/B, F4-C-F-0402-A/B | "Verify fill operation or adjust jump_limit parameter" | REVIEW |
| Inferred/default fill | F4-C-F-0403-A/B/C | "Review if inferred/default values are appropriate" | REVIEW |
| Excessive nulls | F4-C-F-0404 | "Review data quality — systemic missing data detected" | REVIEW |
| Invalid grouping | F4-C-F-0405 | "Specify valid grouping columns in fill schema" | MANUAL_FIX |
| Date/temporal inversion | L3-L-P-0301, C6-C-C-0605-A/B | "Verify date order — return cannot be before submission" | REVIEW |
| Status/logic conflict | L3-L-V-0302, L3-L-V-0303-A/B | "Resolve status inconsistency in submission data" | REVIEW |
| Overdue/pending | L3-L-V-0304, L3-L-W-0304 | "Follow up with reviewer or update overdue status" | REVIEW |
| Revision anomaly | L3-L-V-0305, L3-L-V-0306 | "Revision should not decrease; check session sequence" | REVIEW |
| Group inconsistency | L3-L-V-0308, L3-L-V-0309 | "Ensure consistent values within group/session" | REVIEW |
| Aggregate/data issue | C6-C-C-0604, S1-I-V-0506 | "Verify aggregation data source or foreign key values" | REVIEW |

#### Files Modified

| File | Change |
|:---|:---|
| `config/schemas/data_error_config.json` | Add `remediation_type` to all 55 entries |
| `workflow/processor_engine/error_handling/detectors/base.py` | Add `_get_remediation_type()`, modify `detect_error()` for auto-resolve |
| 9 detector files | Remove `severity=` and `remediation_type=` parameters |

#### Success Criteria

- [x] `remediation` field (human-readable remedy) added to all 55 catalog entries
- [x] `remediation_type` field (classification: MANUAL_FIX / AUTO_FIX / REVIEW / RERUN) added to all 55 catalog entries
- [x] `_get_remediation()` and `_get_remediation_type()` implemented in `base.py`
- [x] `detect_error()` auto-resolves severity + remediation + remediation_type from catalog
- [x] Zero hardcoded severity fallbacks or remediation strings in callers
- [x] 5 mismatched fallbacks resolved (removed by auto-resolve — fallback never used in production)
- [x] All files pass syntax check

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
37. [context_pipeline.py](../../workflow/core_engine/context/context_pipeline.py)
38. [path_schema.py](../../workflow/core_engine/paths/path_schema.py)
39. [error_code_base.json](../../config/schemas/error_code_base.json)
40. [project_config.json](../../config/schemas/project_config.json)
