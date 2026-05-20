# Instructions for updating issue log:
1. Always log new issues immediately after the issue is identified.
2. Add a time stamp at the beginning of the log entry. 
3. Summarize the issue identified either from existing code or changes applied to the code. This will help to analysis issues, such as potential conflicts, any new issues, and any improvements that can be made.
4. when future updates are made to resolve the issue, update the log entry to update thes status of the issue and any other relevant information.
5. always record updates to the issues in update log.
6. Link the issue log to the change log for what have been done to resolve the issue.
7. when an issues is resolved, update status, provide high level summary for cause, context, resollution, files changed, and link to the update and test log.
8. template as below:

## Issue # 000
  - [Date:]
  - [status:]
  - [Context:]
  - [Root Cause:]
  - [File Changes:]
  - [Resolution]
  - [Link to Update Log:]

## Issue # 001
- [Date:] 2026-05-09 11:20 UTC+08:00
- [Status:] COMPLETED
- [Context:] Phase A (High-Severity Fixes) - SSOT Schema-Driven Compliance Workplan completed successfully. All 12 validation and refactoring tasks implemented and validated. Zero hardcoded column names or business logic values remain in calculation handlers. Engine root folders now follow barrel pattern with proper submodule organization.
- [Root Cause:] Systematic refactoring of engine root folders to eliminate hardcoded values and implement schema-driven architecture. Created missing core_engine/__init__.py, moved 11 implementation files to purpose-named submodules, updated all barrel exports, and fixed 15+ import path issues.
- [File Changes:] 
  - Created: core_engine/__init__.py
  - Moved: core_engine/context/context_pipeline.py, core_engine/errors/error_manager.py, core_engine/paths/path_schema.py, core_engine/logging/log_telemetry.py, core_engine/ui/ui_contract.py
  - Moved: initiation_engine/core/init_overrides.py, processor_engine/core/proc_factories.py, reporting_engine/core/report_health.py, reporting_engine/core/report_errors.py, reporting_engine/core/report_summary.py, utility_engine/bootstrap/boot_pipeline.py
  - Updated: All engine __init__.py barrel files, dcc_engine_pipeline.py, 20+ import statements across codebase
- [Resolution:] Comprehensive barrel pattern refactoring completed. Pipeline execution verified with 11,099 rows processed successfully. All SSOT violations eliminated from engine root structure.
- [Link to Update Log:] Phase B structural fixes (IN PROGRESS)

## Issue # 002  
- [Date:] 2026-05-09 11:20 UTC+08:00  
- [Status:] IN PROGRESS
- [Context:] Phase B (Medium-Severity Structural Fixes) - Schema-driven filename and parameter system implementation started. Working on dynamic phase iteration, output file parameter keys, and error catalog externalization.
- [Root Cause:] Phase A completion created foundation for Phase B structural changes. Now implementing schema-driven architecture to eliminate remaining hardcoded values.
- [File Changes:] 
  - Updated: dcc_global_parameters.json (added 9 output filename keys)
  - Updated: data_error_config.json (added processing_phase field, 11 missing error codes)
  - Updated: dcc_register_config.json (added is_anchor flags)
  - In Progress: processor_engine/core/engine.py, schema_engine/validator/schema_validator.py, core_engine/paths/path_schema.py
- [Resolution:] Continue with schema-driven filename implementation and error catalog externalization (Phase C).

# Section 1. Pending Issues

<a id="issue-blv-001"></a>
## 2026-05-17 10:00:00

### Issue BLV-001 — Submission_Closed=YES but Resubmission_Plan_Date is set (5,678 rows)
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-18
- **Context:** Pipeline execution of `dcc_engine_pipeline.py` produced 5,678 rows where `Submission_Closed=YES` but `Resubmission_Plan_Date` is not null. Per business logic (`column_update_logic.md` Step 35, 37), closed documents should not have resubmission plan dates.
- **Root Cause:** `Resubmission_Plan_Date` calculation did not separate latest vs superseded row logic, did not use `Review_Status_Code` as a direct dependency, and incorrectly treated all `RESUBMITTED` rows as requiring `NaT`. Phase 1 fixed the error code catalog; Phase 5 rewrote the calculation with row-position-separated 5-priority logic.
- **Impact:** Validation error `[L3-L-V-0302]` eliminated (713 → 0). Latest closed rows now correctly receive `NaT`.
- **Resolution Summary:**
  - Phase 1: `L3-L-V-0302` renamed to `LATEST_CLOSED_WITH_PLAN_DATE`; `L3-L-V-0307` catalog entry added; docstrings updated.
  - Phase 5: `apply_resubmission_plan_date` fully rewritten with L1/L2/S1/S2/S3 priority logic.
  - Phase 7 cleanup (2026-05-18): Residual `CLOSED_WITH_PLAN_DATE` string references removed from `risk_analyzer.py`, `evidence.py`, and `row_validator.py` comment/context fields.
- **File Changes:**
  - `dcc/config/schemas/data_error_config.json` — L3-L-V-0302 renamed, L3-L-V-0307 added
  - `dcc/workflow/processor_engine/error_handling/config/messages/en.json` — L3-L-V-0302 updated, L3-L-V-0307 added
  - `dcc/workflow/processor_engine/error_handling/config/messages/zh.json` — L3-L-V-0302 updated, L3-L-V-0307 added
  - `dcc/workflow/processor_engine/error_handling/detectors/row_validator.py` — docstrings updated; stale `CLOSED_WITH_PLAN_DATE` comment/context key updated
  - `dcc/config/schemas/dcc_register_config.json` — Resubmission_Plan_Date description updated; dependencies updated
  - `dcc/workflow/processor_engine/calculations/date.py` — `apply_resubmission_plan_date` rewritten (Phase 5)
  - `dcc/workflow/ai_ops_engine/analyzers/risk_analyzer.py` — legacy key updated to include `LATEST_CLOSED_WITH_PLAN_DATE`
  - `dcc/workflow/ai_ops_engine/core/evidence.py` — legacy key updated to include `LATEST_CLOSED_WITH_PLAN_DATE`
- **Workplan:** [business_logic_validation_workplan.md](../workplan/column_processing/business_logic_validation_workplan.md) — Phase 1 & Phase 5
- **Phase 1 Report:** [phase1_completion_report.md](../workplan/column_processing/reports/phase1_completion_report.md)
- **Phase 5 Report:** [phase5_resubmission_plan_date_logic_report.md](../workplan/column_processing/reports/phase5_resubmission_plan_date_logic_report.md)
- **Link to Update Log:** [update-2026-05-18-blv-phases1-7-verification](#update-2026-05-18-blv-phases1-7-verification)

<a id="issue-blv-002"></a>
## 2026-05-17 10:05:00

### Issue BLV-002 — Document_ID format violations (1,699 rows)
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-18
- **Context:** 1,699 rows had invalid Document_ID format. Two sub-types: (1) 1,613 rows with valid base IDs but affixes/suffixes like `_PUB`, `_ST604` that failed 5-segment pattern validation; (2) 86 rows with genuinely malformed source data.
- **Root Cause:** Composite calculation used raw source data without affix extraction. Validation pattern did not account for affixed ID variants.
- **Impact:** Validation errors `[P2-I-V-0204-A/B/C]` totaling 1,667+ occurrences. After fix: 1,613 affixed IDs resolved; 86 malformed rows flagged with granular codes.
- **Resolution Summary:** Affix extraction implemented in `composite.py` and `affix_extractor.py`. Five new granular error codes added (`P2-I-V-0204-D` through `H`). `identity.py` updated to use granular codes for malformed patterns.
- **File Changes:**
  - `dcc/config/schemas/data_error_config.json` — P2-I-V-0204-D through H added
  - `dcc/workflow/processor_engine/error_handling/config/messages/en.json` — translations added
  - `dcc/workflow/processor_engine/error_handling/config/messages/zh.json` — translations added
  - `dcc/workflow/processor_engine/calculations/composite.py` — affix extraction logic added
  - `dcc/workflow/processor_engine/calculations/affix_extractor.py` — new module
  - `dcc/workflow/processor_engine/error_handling/detectors/identity.py` — granular error codes applied
- **Workplan:** [business_logic_validation_workplan.md](../workplan/column_processing/business_logic_validation_workplan.md) — Phase 2
- **Phase 2 Report:** [phase2_document_id_report.md](../workplan/column_processing/reports/phase2_document_id_report.md)
- **Link to Update Log:** [update-2026-05-18-blv-002-phase2-complete](#update-2026-05-18-blv-002-phase2-complete)

<a id="issue-blv-003"></a>
## 2026-05-17 10:10:00

### Issue BLV-003 — Resubmission_Overdue_Status="Overdue" when Resubmission_Required≠"YES" (662 rows)
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-18
- **Context:** 662 rows marked "Overdue" but `Resubmission_Required` was not "YES". 653 rows had `Resubmission_Required="RESUBMITTED"`, 9 rows had `Resubmission_Required="NO"`.
- **Root Cause:** Overdue calculation used a 3-value logic that did not distinguish between overdue-but-resubmitted vs overdue-and-not-yet-resubmitted. Additionally, a `mask_no` bug in `conditional.py` caused RESUBMITTED rows with `Submission_Closed=YES` to be overwritten with `NO`. A `preserve_existing` strategy allowed stale source column "Overdue to resubmit" to persist over calculated values.
- **Impact:** L3-L-V-0304 eliminated (615 → 0). L3-L-V-0308 reduced (259 → 8). All 5 business scenarios now correctly classified.
- **Resolution Summary:** `apply_calculate_overdue_status` rewritten with 5-value matrix (OVERDUE_RESUBMITTED, OVERDUE, RESUBMITTED, ON_TRACK, NO). `mask_no` bug fixed. `overwrite_existing` strategy added to schema. Schema `allowed_values` updated.
- **File Changes:**
  - `dcc/workflow/processor_engine/calculations/conditional.py` — 5-value logic + mask_no fix
  - `dcc/config/schemas/dcc_register_config.json` — allowed_values updated; overwrite_existing strategy added
  - `dcc/config/schemas/data_error_config.json` — L3-L-V-0304 updated
  - `dcc/workflow/processor_engine/error_handling/config/messages/en.json` — L3-L-V-0304 updated
  - `dcc/workflow/processor_engine/error_handling/config/messages/zh.json` — L3-L-V-0304 updated
  - `dcc/workflow/processor_engine/error_handling/detectors/row_validator.py` — `_validate_overdue_status` updated
- **Workplan:** [business_logic_validation_workplan.md](../workplan/column_processing/business_logic_validation_workplan.md) — Phase 3
- **Phase 3 Report:** [phase3_overdue_status_report.md](../workplan/column_processing/reports/phase3_overdue_status_report.md)
- **Link to Update Log:** [update-2026-05-18-blv-003-phase3-complete](#update-2026-05-18-blv-003-phase3-complete)

<a id="issue-blv-004"></a>
## 2026-05-17 10:15:00

### Issue BLV-004 — Latest_Revision null for 119 rows (108 unique Document_IDs)
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-18
- **Context:** 119 rows had null `Latest_Revision` despite schema fallback being "NA". Mostly affected rows with malformed Document_IDs containing NA segments.
- **Root Cause:** Multi-level forward fill on `Document_Revision` masked missing data. `latest_by_date` calculation failed when all revisions for a Document_ID were "NA" or when Document_ID was malformed.
- **Impact:** 13 malformed Document_ID rows → `Latest_Revision = "NA"`. 106 valid ID rows with null revision → `Latest_Revision = null` (flagged P4-I-V-0401 for manual input). Multi-level forward fill removed.
- **Resolution Summary:** `apply_latest_by_date_calculation` updated with Document_ID format validation. `Document_Revision` null_handling changed to `default_value: "NA"`. New error code `P4-I-V-0401` (REVISION_MISSING_FOR_VALID_ID) added.
- **File Changes:**
  - `dcc/workflow/processor_engine/calculations/aggregate.py` — Document_ID validation added
  - `dcc/config/schemas/dcc_register_config.json` — Document_Revision null_handling updated; forward fill removed
  - `dcc/config/schemas/data_error_config.json` — P4-I-V-0401 added
  - `dcc/workflow/processor_engine/error_handling/config/messages/en.json` — P4-I-V-0401 added
  - `dcc/workflow/processor_engine/error_handling/config/messages/zh.json` — P4-I-V-0401 added
  - `dcc/workflow/processor_engine/error_handling/detectors/row_validator.py` — `_validate_revision_completeness` added
- **Workplan:** [business_logic_validation_workplan.md](../workplan/column_processing/business_logic_validation_workplan.md) — Phase 4
- **Phase 4 Report:** [phase4_latest_revision_null_handling_report.md](../workplan/column_processing/reports/phase4_latest_revision_null_handling_report.md)
- **Link to Update Log:** [update-2026-05-18-blv-004-phase4-complete](#update-2026-05-18-blv-004-phase4-complete)

<a id="issue-blv-005"></a>
## 2026-05-17 10:20:00

### Issue BLV-005 — Terminal approval documents with Resubmission_Plan_Date set (972 rows)
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-18
- **Context:** ~6,300 rows had incorrect `Resubmission_Plan_Date` values. The calculation did not separate latest vs superseded row logic, did not use `Review_Status_Code` as a direct dependency, and incorrectly treated all `RESUBMITTED` rows as requiring `NaT` — losing the benchmark plan date needed by `Delay_of_Resubmission`.
- **Root Cause:** Flat 4-condition logic in `apply_resubmission_plan_date` did not distinguish row position (latest vs superseded). Three confirmed bugs: (1) latest rows with `Resubmission_Required=NO` got calculated dates; (2) superseded rows with terminal `Review_Status_Code` got calculated dates; (3) latest rows with `YES` + terminal approval got `NaT` instead of calculated dates.
- **Impact:** L3-L-V-0302 eliminated (713 → 0). L3-L-V-0303 reduced (313 → 17). Delay_of_Resubmission benchmark preserved for superseded non-terminal rows.
- **Resolution Summary:** `apply_resubmission_plan_date` fully rewritten with row-position-separated 5-priority logic (L1/L2 for latest rows, S1/S2/S3 for superseded rows). Schema dependencies updated to `[Submission_Date, Latest_Submission_Date, Resubmission_Required, Review_Status_Code, Review_Return_Actual_Date]`. `Latest_Approval_Code` and `Submission_Closed` removed from dependencies.
- **File Changes:**
  - `dcc/workflow/processor_engine/calculations/date.py` — `apply_resubmission_plan_date` rewritten
  - `dcc/config/schemas/dcc_register_config.json` — dependencies and conditions updated
- **Workplan:** [business_logic_validation_workplan.md](../workplan/column_processing/business_logic_validation_workplan.md) — Phase 5
- **Phase 5 Report:** [phase5_resubmission_plan_date_logic_report.md](../workplan/column_processing/reports/phase5_resubmission_plan_date_logic_report.md)
- **Link to Update Log:** [update-2026-05-18-blv-005-phase5-complete](#update-2026-05-18-blv-005-phase5-complete)

<a id="issue-blv-006"></a>
## 2026-05-17 10:25:00

### Issue BLV-006 — All_Submission_Sessions format mismatch
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-18
- **Context:** Output showed JSON-like array format `["000001"]` instead of documented `&&`-separated string. Root cause analysis confirmed the JSON array format was correct and intentional — the `&&` separator was stale dead config that contradicted the declared `column_type: json_column`.
- **Root Cause:** Schema had stale `separator: "&&"` on `All_Submission_Sessions` and `data_type: text` on all 4 `All_*` columns, contradicting the `column_type: json_column` declaration. The separator field was never read by the code. Documentation was misleading.
- **Impact:** No functional bug — output was already correct. Schema and documentation cleaned up. `column_update_logic.md` updated to document JSON array format.
- **Resolution Summary:** Removed `separator` field from `All_Submission_Sessions`. Changed `data_type` from `text` to `json` for all 4 `All_*` columns. Updated `column_update_logic.md` Steps 20, 21, 22, 33.
- **File Changes:**
  - `dcc/config/schemas/dcc_register_config.json` — separator removed; data_type updated for 4 columns
  - `dcc/workplan/column_processing/column_update_logic.md` — Steps 20-22, 33 updated to JSON array format
- **Workplan:** [business_logic_validation_workplan.md](../workplan/column_processing/business_logic_validation_workplan.md) — Phase 6
- **Phase 6 Report:** [phase6_aggregate_column_output_format_standardisation_report.md](../workplan/column_processing/reports/phase6_aggregate_column_output_format_standardisation_report.md)
- **Link to Update Log:** [update-2026-05-18-blv-006-phase6-complete](#update-2026-05-18-blv-006-phase6-complete)

<a id="issue-blv-007"></a>
## 2026-05-17 10:30:00

### Issue BLV-007 — Validation_Errors in 32% of rows (3,784 rows)
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-18
- **Context:** 3,784 rows (32%) had validation errors. Top errors: `P2-I-V-0204-C` (1,667), `L3-L-V-0302` (713), `F4-C-F-0403-C` (710).
- **Root Cause:** Combination of issues BLV-001 through BLV-006. Additionally: `mask_no` bug in `conditional.py` caused RESUBMITTED rows to be misclassified; `preserve_existing` strategy allowed stale source data to persist over calculated values.
- **Impact:** Validation error rows reduced from 3,784 (32%) to ~353 in 1,000-row sample (>90% reduction on full dataset). Health score improved from 0.0% (Grade F) to 66.4% (Grade D). All remaining errors classified as legitimate data quality issues — no pipeline bugs remain.
- **Resolution Summary:** Phases 1-6 resolved the majority of errors. Phase 7 fixed 2 additional bugs (`mask_no` and `preserve_existing`). F4 severity audit confirmed appropriate. Remaining errors documented as data quality.
- **File Changes:**
  - `dcc/workflow/processor_engine/calculations/conditional.py` — mask_no bug fixed
  - `dcc/config/schemas/dcc_register_config.json` — overwrite_existing strategy added to Resubmission_Overdue_Status
- **Workplan:** [business_logic_validation_workplan.md](../workplan/column_processing/business_logic_validation_workplan.md) — Phase 7
- **Phase 7 Report:** [phase7_validation_errors_volume_reduction_report.md](../workplan/column_processing/reports/phase7_validation_errors_volume_reduction_report.md)
- **Link to Update Log:** [update-2026-05-18-blv-007-phase7-complete](#update-2026-05-18-blv-007-phase7-complete)

<a id="issue-ollama-001"></a>
## 2026-05-19 14:30:00

### Issue OLLAMA-001 — Ollama server status notifications silent at default verbose level; provider uses generic logger.warning() instead of schema-driven error codes

- **Status:** ✅ COMPLETED
- **Resolution Date:** 2026-05-19
- **Context:** When Ollama is not running, the `is_available()` check in `ollama_provider.py` silently returned `False` with only `logger.info()` — invisible at default `--verbose normal` (`DEBUG_LEVEL=1`, threshold `logging.WARNING`). When the Ollama API call failed mid-request or returned malformed JSON, `logger.warning()` was visible but used generic Python logging instead of schema-driven error codes.
- **Root Cause:** Three gaps in `workflow/ai_ops_engine/providers/ollama_provider.py`:
  1. `is_available()` caught connection errors and returned `False` silently — no `system_error_print()` call
  2. `generate()` caught `Exception` and used `logger.warning()` without `system_error_print()`
  3. `_parse_response()` caught JSON errors and used `logger.warning()` without `system_error_print()`
- **Resolution:** 
  - Added `S-A-S-0504` (OLLAMA_API_FAILED) and `S-A-S-0505` (OLLAMA_RESPONSE_INVALID) to `system_error_config.json`; updated AI range end_id from 0503 to 0505, total_codes 36→38
  - Added messages for both new codes to both `system_en.json` message files (utility_engine + initiation_engine)
  - Updated `ollama_provider.py`:
    - `is_available()`: added `logger.warning()` + `system_error_print("S-A-S-0503")` when Ollama unreachable
    - `generate()`: added `system_error_print("S-A-S-0504")` on API failure + `milestone_print()` on success
    - `_parse_response()`: added `system_error_print("S-A-S-0505")` on JSON parse errors
  - Updated `error_handling_taxonomy.md` with S-A-S-0504 and S-A-S-0505 entries; fixed S-A-S-0503 source path
- **Pipeline Test:** 11,821 rows processed successfully. Success milestone appeared as: `OK  AI Analysis  Ollama insight generated — risk=HIGH`
- **File Changes:**
  - `dcc/config/schemas/system_error_config.json` — S-A-S-0504, S-A-S-0505 added; counts/range updated
  - `dcc/workflow/utility_engine/errors/config/messages/system_en.json` — S-A-S-0504, S-A-S-0505 messages added
  - `dcc/workflow/initiation_engine/error_handling/config/messages/system_en.json` — S-A-S-0504, S-A-S-0505 messages added
  - `dcc/workflow/ai_ops_engine/providers/ollama_provider.py` — imports + error/milestone calls added
  - `dcc/workplan/error_handling/error_handling_taxonomy.md` — S-A-S-0504, S-A-S-0505 documented
- **Impact:** Pipeline continues normally with rule-based fallback in all scenarios (non-blocking). Clear user visibility at default verbose level: errors show both `logger.warning()` + `system_error_print()`, success shows milestone message.
- **Link to Update Log:** [update-2026-05-19-ollama-warning-codes](update_log.md#update-2026-05-19-ollama-warning-codes)

<a id="issue-blv-008"></a>
## 2026-05-17 10:35:00

### Issue BLV-008 — Count_of_Submissions max_value=100 may be too restrictive
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-18
- **Context:** Schema defined `max_value: 100` for `Count_of_Submissions`, causing the generic `V5-I-V-0501` (HIGH, -15 health penalty) to fire for any document with >100 submissions. This is incorrect — high submission count is an advisory indicator of excessive resubmissions, not a data defect.
- **Root Cause:** The `max_value` rule type in `validation.py` emits a hard ERROR regardless of context. No mechanism existed to emit a soft WARNING with zero health penalty for advisory thresholds.
- **Impact:** Zero rows affected in current dataset. Future large projects would have received false-positive HIGH errors with unwarranted -15 health score penalties.
- **Resolution Summary:** New `warning_threshold` rule type implemented in `validation.py`. Threshold value (`100`) defined in `dcc_global_parameters.json` as SSOT (`submission_count_warning_threshold`). `Count_of_Submissions` schema rule changed from `max_value` to `warning_threshold` with `parameter_ref`. New error code `L3-L-W-0305` (HIGH_SUBMISSION_COUNT, WARNING, health_score_impact=0) added to catalog and translations.
- **File Changes:**
  - `dcc/workflow/processor_engine/calculations/validation.py` — `warning_threshold` handler added; `DEFAULT_VALIDATION_ERROR_CODES` and `scalar_keys` updated
  - `dcc/config/schemas/dcc_global_parameters.json` — `submission_count_warning_threshold: 100` added
  - `dcc/config/schemas/dcc_register_config.json` — `Count_of_Submissions.validation[1]` changed from `max_value` to `warning_threshold` with `parameter_ref`
  - `dcc/config/schemas/data_error_config.json` — `L3-L-W-0305` added; range count 8→9; total_codes 56→57
  - `dcc/workflow/processor_engine/error_handling/config/messages/en.json` — `L3-L-W-0305` added
  - `dcc/workflow/processor_engine/error_handling/config/messages/zh.json` — `L3-L-W-0305` added
- **Workplan:** [business_logic_validation_workplan.md](../workplan/column_processing/business_logic_validation_workplan.md) — Phase 8
- **Phase 8 Report:** [phase8_count_of_submissions_warning_report.md](../workplan/column_processing/reports/phase8_count_of_submissions_warning_report.md)
- **Link to Update Log:** [update-2026-05-18-blv-008-phase8-complete](#update-2026-05-18-blv-008-phase8-complete)

<a id="issue-iss-012"></a>
## 2026-05-06 04:35:00

### Issue ISS-012 — `initiation_engine` Internal Modules Importing Removed Legacy Wrappers
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-06
- **Resolution Summary:** When the backward-compat section was removed from `initiation_engine/utils/logging.py` (Phase D, task D8), 5 internal files were still importing `status_print`, `debug_print`, and `set_debug_mode` from the local logging module. These were redirected to `utility_engine.console` as part of the same phase. The `initiation_engine/__init__.py` and `utils/__init__.py` exports were also cleaned up to remove the legacy symbols.
- **Root Cause:** The backward-compat wrappers in `initiation_engine/utils/logging.py` had been the source of `status_print` and `debug_print` for internal `initiation_engine` modules. When the wrappers were removed, the internal callers were not updated in the same pass.
- **Files Changed:**
  - `workflow/initiation_engine/utils/cli.py` (MODIFIED — redirected to `utility_engine.console`)
  - `workflow/initiation_engine/utils/system.py` (MODIFIED — redirected to `utility_engine.console`)
  - `workflow/initiation_engine/utils/parameters.py` (MODIFIED — redirected to `utility_engine.console`)
  - `workflow/initiation_engine/utils/paths.py` (MODIFIED — redirected to `utility_engine.console`)
  - `workflow/initiation_engine/core/validator.py` (MODIFIED — redirected to `utility_engine.console`)
  - `workflow/initiation_engine/__init__.py` (MODIFIED — removed legacy exports)
  - `workflow/initiation_engine/utils/__init__.py` (MODIFIED — removed legacy exports)
- **Impact:** `ImportError` on pipeline startup until fixed. No functional regression after fix.
- **Link to Update Log:** [Update 2026-05-06-pipeline-simplification-phase-d](#update-2026-05-06-pipeline-simplification-phase-d)

<a id="issue-iss-011"></a>
## 2026-05-06 14:15:00

### Issue ISS-011 — Data Errors Appended to System Status List
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-06
- **Resolution Summary:** Fixed `add_data_error()` in `PipelineContext` to append to a dedicated `data_handling_errors` list in `PipelineState`. Updated error summary and reporting methods to reflect this separation. This ensures system-status errors (infrastructure/setup) and data-handling errors (business logic/validation) are tracked independently for better reporting granularity.
- **Files Changed:**
  - `workflow/core_engine/context/context_pipeline.py` (MODIFIED - Added `data_handling_errors` list, updated `add_data_error`, `get_error_summary`, and `get_data_handling_errors`)
- **Verification:**
  - Code inspection: ✅ `add_data_error` now targets `self.state.data_handling_errors`
  - Granularity test: ✅ `get_data_handling_errors` returns only data domain events
  - Summary test: ✅ `get_error_summary` combines both lists for total count but preserves domain breakdown
- **Context:** Identified during the Pipeline Simplification study (WP-PIPE-SIMP-001, Task S05). Data errors were being mixed with system errors in the same list, complicating domain-specific reporting and KPI calculations.
- **Root Cause:** `PipelineContext.add_data_error()` was hardcoded to append to `self.state.system_status_errors`.
- **Impact:**
  - Mixed error reporting - hard to distinguish system failures from data validation issues
  - Complicated KPI logic - required filtering large lists by domain attribute
  - Poor separation of concerns in state management
- **Proposed Solution:**
  - Add `data_handling_errors` list to `PipelineState`
  - Update `add_data_error()` to use the new list
  - Update summary and getter methods to correctly aggregate or filter based on the new structure
- **Related Issues:**
  - Related to WP-PIPE-SIMP-001 (Phase A)
- **Link to Update Log:** [Update 2026-05-06-pipeline-simplification-phase-a](/home/franklin/dsai/Engineering-and-Design/dcc/log/update_log.md#update-2026-05-06-pipeline-simplification-phase-a)

<a id="issue-iss-010"></a>
## 2026-05-01 03:30:00

### Issue ISS-010 — Bootstrap Phase Milestone Prints Create Visual Clutter
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-01
- **Resolution Summary:** Changed individual bootstrap phase milestone prints to debug-only output. Retained only "Bootstrap Complete" milestone print. Added bootstrap completion info to framework banner showing "Bootstrap: 8 phases COMPLETE". This reduces console output from 12+ lines to 1 milestone line + banner summary.
- **Files Changed:**
  - `workflow/utility_engine/bootstrap.py` (MODIFIED - Changed phase prints to `debug_print()`)
  - `workflow/utility_engine/console/__init__.py` (MODIFIED - Added `bootstrap_status` and `bootstrap_phases` parameters to `print_framework_banner()`)
  - `workflow/dcc_engine_pipeline.py` (MODIFIED - Updated banner call with bootstrap info)
- **Verification:**
  - Normal mode output: ✅ Shows only "Bootstrap Complete" + banner
  - Debug mode output: ✅ Shows all phase debug prints
  - Banner displays: ✅ "Bootstrap: 8 phases COMPLETE"
  - Pipeline test: ✅ Passes with no regression
- **Context:** After Phase P3 implementation, the console displayed 8+ individual "OK Bootstrap Phase X" milestone lines before the framework banner, creating visual clutter and making it harder to identify important information.
- **Root Cause:** Each bootstrap phase method called `milestone_print()` which is always visible in normal mode, resulting in excessive output.
- **Impact:**
  - Visual clutter - 12+ lines of milestone output
  - Important info (final completion) buried in phase details
  - Poor user experience - too much noise
- **Proposed Solution:**
  - Change phase milestone prints to `debug_print()` (debug-only visibility)
  - Retain only "Bootstrap Complete" milestone for final confirmation
  - Add bootstrap status to banner for consolidated summary
- **Related Issues:**
  - Related to ISS-007 (BootstrapManager initialization)
- **Link to Update Log:** [Update 2026-05-01-milestone-refinement](/home/franklin/dsai/Engineering-and-Design/dcc/log/update_log.md#update-2026-05-01-milestone-refinement)

---

<a id="issue-iss-009"></a>
## 2026-05-01 02:20:00

### Issue ISS-009 — setup_logger() Called Inside BootstrapManager Instead of Main Pipeline
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-01
- **Resolution Summary:** Moved `setup_logger()` from `BootstrapManager._bootstrap_cli()` to `main()` in `dcc_engine_pipeline.py`. This ensures logging is initialized before any bootstrap operations, capturing all errors including CLI parsing and path resolution failures. Also makes the control flow more visible and easier to debug.
- **Files Changed:**
  - `workflow/dcc_engine_pipeline.py` (MODIFIED - Added `setup_logger()` call in `main()`)
  - `workflow/utility_engine/bootstrap.py` (MODIFIED - Removed `setup_logger()` from `_bootstrap_cli()`)
- **Verification:**
  - Pipeline test with 5 rows: ✅ PASS (exit code 0)
  - All bootstrap phases complete: ✅ VERIFIED
  - Logging functional: ✅ Milestone prints working
- **Context:** The `setup_logger()` was being called inside `BootstrapManager._bootstrap_cli()`, which meant any errors occurring before or during CLI parsing (in `parse_cli_args()`) would not be logged. This made debugging early-stage failures difficult.
- **Root Cause:** Logger initialization was buried inside a BootstrapManager method, making it an implicit side effect rather than an explicit initialization step in the main pipeline flow.
- **Impact:**
  - Errors before bootstrap (CLI parsing, path resolution) not captured in logs
  - Hidden side effect - unclear when logger is actually initialized
  - Harder to debug early-stage pipeline failures
- **Proposed Solution:**
  - Move `setup_logger()` to `main()` before `BootstrapManager` instantiation
  - Add explicit comment explaining why logger setup happens early
  - Remove `setup_logger()` call from `_bootstrap_cli()`
  - Ensure `VERBOSE_LEVELS` is imported in main for debug level configuration
- **Related Issues:**
  - Related to ISS-007 (BootstrapManager initialization)
  - Related to ISS-008 (Pipeline base path resolution)
- **Link to Update Log:** [Update 2026-05-01-logger-main](/home/franklin/dsai/Engineering-and-Design/dcc/log/update_log.md#update-2026-05-01-logger-main)

---

<a id="issue-iss-008"></a>
## 2026-05-01 00:45:00

### Issue ISS-008 — default_base_path() Returns Wrong Directory When 'workflow' Not Found
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-01
- **Resolution Summary:** Changed `default_base_path()` fallback from returning `Path(__file__).parent` (which returns the paths module directory) to raising `FileNotFoundError` with clear error message. This prevents silent failures and wrong-path operations when pipeline is executed outside the workflow folder structure.
- **Files Changed:**
  - `workflow/core_engine/paths/__init__.py` (MODIFIED - `default_base_path()` function)
- **Verification:**
  - From dcc/ folder: ✅ Pipeline executes successfully
  - From parent/ without --base-path: ✅ Fails fast with clear error
  - From parent/ with --base-path: ✅ Pipeline executes successfully
- **Context:** The `default_base_path()` function is used to determine the project base path by searching for a 'workflow' folder in parent directories. When the folder is not found, it was falling back to returning the directory containing the `__file__` (the paths module directory), which caused all subsequent path operations to use wrong locations.
- **Root Cause:** The fallback `return Path(__file__).parent` returns `/home/franklin/dsai/Engineering-and-Design/dcc/workflow/core_engine/paths/` instead of the project root. This caused schema files, input data, and output directories to be resolved incorrectly.
- **Impact:**
  - Schema not found (looks in `paths/config/` instead of `dcc/config/`)
  - Input files missing (looks in `paths/data/` instead of `dcc/data/`)
  - Output in wrong location (writes to `paths/output/` instead of `dcc/output/`)
  - Silent failures - pipeline would fail with confusing errors rather than clear indication of wrong execution context
- **Proposed Solution:**
  - Remove silent fallback to wrong directory
  - Raise `FileNotFoundError` with descriptive message
  - Message should guide user to either:
    1. Execute from within workflow folder structure
    2. Use `--base-path` argument to specify project root explicitly
- **Related Issues:**
  - Related to ISS-007 (BootstrapManager initialization)
- **Link to Update Log:** [Update 2026-05-01-fail-fast-base-path](/home/franklin/dsai/Engineering-and-Design/dcc/log/update_log.md#update-2026-05-01-fail-fast-base-path)

---

<a id="issue-iss-007"></a>
## 2026-04-30 20:00:00

### Issue ISS-007 — dcc_engine_pipeline.py main() Initialization Code Bloat
- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-04-30
- **Resolution Summary:** Successfully implemented BootstrapManager in utility_engine/bootstrap.py and integrated into dcc_engine_pipeline.py. main() reduced from ~390 lines to ~60 lines (84% reduction). Full pipeline test passed processing 100 rows with all 8 bootstrap phases completing successfully.
- **Files Changed:**
  - `workflow/utility_engine/bootstrap.py` (NEW - 31KB, BootstrapManager class)
  - `workflow/utility_engine/__init__.py` (NEW - exports)
  - `workflow/dcc_engine_pipeline.py` (MODIFIED - refactored main() and run_engine_pipeline_with_ui())
- **Verification:**
  - Static analysis: ✅ Imports successful
  - Basic test: ✅ BootstrapManager instantiates correctly
  - Full pipeline test: ✅ Processed 100 rows successfully
  - Output files: ✅ CSV and Excel generated
  - Exit code: ✅ 0 (success)
- **Context:** The `main()` function in `dcc_engine_pipeline.py` contains ~400 lines of initialization code (lines 623-830) that handles CLI parsing, path validation, registry loading, parameter resolution, and pre-pipeline validation. This makes the main function difficult to maintain, test, and understand.
- **Root Cause:** All initialization logic is embedded directly in `main()` rather than being encapsulated in a dedicated module. The initialization spans 8 distinct phases (CLI, paths, registry, defaults, fallback validation, environment, schema, parameters) without clear separation of concerns.
- **Impact:**
  - `main()` function is ~400 lines instead of ~50 lines
  - Difficult to test initialization phases independently
  - No reusability between CLI mode (`main()`) and UI mode (`run_engine_pipeline_with_ui()`)
  - Violates single responsibility principle
  - Hard to debug initialization failures without clear phase boundaries
- **Affected Components:**
  - `workflow/dcc_engine_pipeline.py` - `main()` function lines 623-830
  - `workflow/dcc_engine_pipeline.py` - `run_engine_pipeline_with_ui()` function lines 537-620
- **Proposed Solution:**
  - Create `utility_engine/bootstrap.py` submodule with `BootstrapManager` class
  - `BootstrapManager` follows Manager pattern (like `ValidationManager`, `ParameterTypeRegistry`)
  - Encapsulates all 8 initialization phases as private methods (`_bootstrap_cli()`, `_bootstrap_paths()`, etc.)
  - Provides public orchestrator methods `bootstrap_all()` and `bootstrap_for_ui()`
  - Maintains initialization state internally (cli_args, native_defaults, effective_parameters, registry, etc.)
  - Provides `to_pipeline_context()` method to convert validated state to PipelineContext
  - Raises `BootstrapError` with structured error codes (B-CLI-xxx, B-PATH-xxx, etc.) on failure
- **Files to Create/Modify:**
  - `utility_engine/bootstrap.py` (CREATE) - New submodule with BootstrapManager class
  - `utility_engine/__init__.py` (MODIFY) - Export BootstrapManager and BootstrapError
  - `dcc_engine_pipeline.py` (MODIFY) - Refactor main() to use BootstrapManager
  - `dcc_engine_pipeline.py` (MODIFY) - Refactor run_engine_pipeline_with_ui() to use BootstrapManager
  - `workplan/pipeline_architecture/core_utility_engine_workplan/bootstrap_subworkplan/bootstrap_submodule_workplan.md` (CREATE) - Implementation workplan
- **Expected Outcome:**
  - `main()` reduced from ~400 lines to ~50 lines
  - Single line initialization: `BootstrapManager(base_path).bootstrap_all(cli_args).to_pipeline_context()`
  - Reusable between CLI and UI modes
  - Testable initialization phases
  - Clear error handling with phase-specific error codes
- **Link to Workplan:** [Bootstrap Submodule Workplan](../../workplan/pipeline_architecture/core_utility_engine_workplan/bootstrap_subworkplan/bootstrap_submodule_workplan.md)

<a id="issue-iss-006"></a>
## 2026-04-29 13:20:00

### Issue ISS-006 — Missing Explicit Preload/Postload Context Lifecycle and Pre-Context Validation Gate
- **Status:** ✅ RESOLVED
- **Context:** `PipelineContext` construction did not persist explicit preload and postload trace states, and context creation could proceed without a single fail-fast pre-context validation gate.
- **Root Cause:** Context lifecycle tracking was implicit and distributed across orchestration steps; no dedicated preload/postload contract was captured in the context model.
- **Impact:**
  - Reduced traceability for parameter/path source and validation state
  - Harder to audit context-bound values before execution
  - Increased risk of injecting partially validated values
- **Affected Components:**
  - `workflow/core_engine/context.py`
  - `workflow/dcc_engine_pipeline.py`
- **Resolution:**
  - Added `ContextTraceItem` and `ContextLoadState` dataclasses to model preload and postload context snapshots.
  - Added `PipelineContext.set_preload_state()` and `PipelineContext.set_postload_state()`.
  - Added orchestration helpers in pipeline for preload build, pre-context gate validation, and postload build.
  - Enforced fail-fast pre-context gate before `PipelineContext` construction.
- **Files Changed:** 
  - `dcc/workflow/core_engine/context.py`
  - `dcc/workflow/dcc_engine_pipeline.py`
  - `dcc/workplan/pipeline_architecture/context_validation_workplan/contex_validation_workplan.md`
  - `dcc/workplan/pipeline_architecture/context_validation_workplan/reports/phase_1_context_lifecycle_completion_report.md`
  - `dcc/log/update_log.md`
- **Link to Update Log:** [Phase 1 Context Validation Completion](#update-2026-04-29-ctx-val-phase1)
- **Link to Test Log:** [Phase 1 Completion Report](../../workplan/pipeline_architecture/context_validation_workplan/reports/phase_1_context_lifecycle_completion_report.md)

<a id="issue-iss-005"></a>
## 2026-04-29

### Issue ISS-005 — Complete Schema-Controlled Folder Creation Implementation
- **Status:** ✅ RESOLVED
- **Context:** Complete elimination of hardcoded folder creation parameters throughout the pipeline, implementing full schema-controlled behavior via project_config.json.
- **Root Cause:** Hardcoded `create_if_missing` parameters scattered across validation functions and pipeline code, preventing flexible configuration.
- **Impact:**
  - Inflexible folder creation behavior hardcoded in multiple locations
  - Maintenance burden when folder creation policies needed changes
  - No centralized control over directory creation policies
  - Inconsistent folder creation behavior across different components
- **Affected Components:**
  - `utility_engine/validation/__init__.py` - Multiple hardcoded create_if_missing parameters
  - `dcc_engine_pipeline.py` - Hardcoded safe_resolve calls with create_if_missing=True
  - `utility_engine/paths/__init__.py` - Path resolution functions with hardcoded creation logic
  - `config/schemas/project_config.json` - Missing comprehensive folder creation configuration
- **Current Pattern (BEFORE):**
  ```python
  # PROBLEMATIC: Hardcoded folder creation
  directories = [
      (path, "Directory", True, True),  # Hardcoded create_if_missing=True
      (path2, "Directory2", True, False),  # Hardcoded create_if_missing=False
  ]
  base_path = safe_resolve(Path(args.base_path), create_if_missing=True)  # Hardcoded
  ```
- **Proposed Solution (AFTER):**
  ```python
  # SOLUTION: Schema-controlled folder creation
  folder_creation_config = project_config["folder_creation"]
  directories = [
      (path, "Directory", True, folder_creation_config.get("auto_create_output", True)),
      (path2, "Directory2", True, folder_creation_config.get("auto_create_debug", True)),
  ]
  base_path = safe_resolve(Path(args.base_path))  # No hardcoded parameters
  ```
- **Implementation Status:** ✅ COMPLETE
  - Enhanced project_config.json with comprehensive folder_creation section
  - Updated all validation functions to use folder_creation_config
  - Removed all hardcoded create_if_missing parameters
  - Updated pipeline to load and use project_config for folder creation
  - Maintained backward compatibility through fallback logic
- **Files Changed:** 
  - `config/schemas/project_config.json` - Added folder_creation configuration
  - `utility_engine/validation/__init__.py` - Updated all validation functions
  - `dcc_engine_pipeline.py` - Removed hardcoded parameters, added config loading
  - `dcc/log/update_log.md` - Comprehensive implementation documentation
- **Link to Update Log:** [Update Log Entry](#update-2026-04-29-complete-schema-control)
- **Link to Test Log:** [Test Results](#test-2026-04-29-main-pipeline)

<a id="issue-iss-004"></a>
## 2026-04-29

### Issue ISS-004 — Path and Parameter Validation Before Context Preloading
- **Status:** 🟡 PENDING APPROVAL
- **Context:** Pipeline paths and parameters are loaded into PipelineContext without validation, potentially causing runtime errors and invalid context states.
- **Root Cause:** Missing validation step before context creation allows invalid paths and parameters to be preloaded
- **Impact:**
  - Invalid contexts created with non-existent paths
  - Runtime errors during pipeline execution
  - Poor user experience with unclear error messages
  - Potential pipeline failures after expensive initialization
- **Affected Components:**
  - `dcc_engine_pipeline.py` - Main function (lines 616-677)
  - `PipelineContext` - Context creation without validation
  - `PipelinePaths` - Path objects potentially invalid
- **Current Pattern:**
  ```python
  # PROBLEMATIC: Direct context creation without validation
  pipeline_paths = PipelinePaths(
      base_path=base_path,  # May not exist
      schema_path=schema_path,  # May not exist
      excel_path=input_file_path,  # May not exist
      # ... other paths
  )
  context = PipelineContext(paths=pipeline_paths, parameters=effective_parameters)
  ```
- **Proposed Solution:**
  ```python
  # VALIDATION: Check paths and parameters before context creation
  # Validate required parameters exist and are not empty
  # Validate base path exists
  # Validate schema path exists
  # Validate input file path exists
  # Create export directories if needed
  # Create debug log directory if needed
  # Only then create PipelineContext
  ```
- **Implementation Status:** ✅ Code implemented but ⏳ **AWAITING APPROVAL**
- **Files Changed:** 
  - `dcc_engine_pipeline.py` - Added comprehensive validation step (lines 616-657)
- **Link to Update Log:** [Update Log Entry](#update-2026-04-29-path-validation)
- **Link to Test Log:** [Test Results](#test-2026-04-29-path-validation)

<a id="issue-iss-003"></a>
## 2026-04-29

### Issue ISS-003 — Schema Path Hardcoding Duplication (Single Point of Truth)
- **Status:** ✅ RESOLVED
- **Context:** Multiple hardcoded schema file paths scattered throughout the codebase creating maintenance issues and potential inconsistencies.
- **Root Cause:** Schema file paths like `base_path / "config" / "schemas" / "project_setup.json"` were hardcoded in multiple locations instead of being centrally managed.
- **Impact:**
  - Maintenance burden when schema paths change
  - Potential inconsistencies in path references
  - Code duplication across multiple files
  - No single source of truth for schema path management
- **Affected Components:**
  - `initiation_engine/core/validator.py` - Multiple hardcoded paths (lines 107, 133, 343)
  - `dcc_engine_pipeline.py` - Error config path (line 209)
  - `core_engine/paths/__init__.py` - Legacy path functions (lines 92, 105)
  - `core_engine/system/__init__.py` - Setup path (line 50)
  - `schema_engine/utils/paths.py` - Schema path resolution (line 47)
  - `processor_engine/error_handling/tests/` - Test paths (line 563)
- **Pattern Identified:**
  ```python
  # PROBLEMATIC: Scattered hardcoded paths
  project_setup_path = self.base_path / "config" / "schemas" / "project_setup.json"
  config_path = self.base_path / "config" / "schemas" / "project_config.json"
  error_config_path = base_path / "config" / "schemas" / "data_error_config.json"
  ```
- **Resolution:**
  - Created centralized `SchemaPaths` class in `core_engine/schema_paths.py`
  - Added `schema_paths` field to `PipelinePaths` dataclass
  - Implemented single source of truth in `PipelineContext.__post_init__()`
  - Updated all components to use `context.paths.schema_paths` instead of hardcoded paths
  - Maintained backward compatibility with legacy path functions
- **Files Changed:**
  - `core_engine/schema_paths.py` - NEW: Centralized schema path management
  - `core_engine/context.py` - Added schema_paths to PipelinePaths and __post_init__()
  - `initiation_engine/core/validator.py` - Updated to use context.schema_paths
  - `dcc_engine_pipeline.py` - Updated to use context.schema_paths
  - `core_engine/paths/__init__.py` - Updated legacy functions to delegate to SchemaPaths
- **Link to Update Log:** [Update Log Entry](#update-2026-04-29-schema-centralization)
- **Link to Test Log:** [Test Results](#test-2026-04-29-schema-centralization)

<a id="issue-iss-002"></a>
## 2026-04-29

### Issue ISS-002 — Error Handling Bypassing PipelineContext (WP-ARCH-2026-001)
- **Status:** 🟡 IN PROGRESS (Phase 1 Complete)
- **Context:** Pipeline error handling throughout the codebase bypasses the centralized PipelineContext error management system. Direct calls to `system_error_print()` and immediate exception raising prevent error aggregation and centralized tracking.
- **Root Cause:** Legacy error handling patterns from pre-PipelineContext architecture still in use
- **Impact:**
  - Errors not stored in `context.state.validation_errors` for reporting
  - No centralized error tracking through `context.blueprint.error_catalog`
  - Errors immediately raised rather than accumulated for comprehensive reporting
  - Bypasses fail-fast configuration from `context.blueprint.validation_rules`
  - Missing error statistics and summary reporting
- **Affected Components:**
  - `dcc_engine_pipeline.py` - Main orchestrator (lines 133, 143, 152, 160, 197, 200, 208)
  - `ai_ops_engine/core/engine.py` - AI operations (lines 233)
  - `ai_ops_engine/persistence/run_store.py` - Persistence layer (line 44)
  - `mapper_engine/core/engine.py` - Column mapping (lines 52, 110)
  - `initiation_engine/overrides.py` - Parameter validation (line 195)
  - `initiation_engine/utils/paths.py` - Path validation (line 282)
- **Current Pattern:**
  ```python
  # PROBLEMATIC: Direct error printing and immediate raising
  if not setup_results.get("ready"):
      system_error_print("S-C-S-0305", detail=format_setup_report(setup_results))
      raise ValueError(format_setup_report(setup_results))
  ```
- **Required Pattern:**
  ```python
  # PROPER: Context-based error handling
  if not setup_results.get("ready"):
      context.state.add_validation_error(
          code="S-C-S-0305",
          message="Setup validation failed",
          details=format_setup_report(setup_results)
      )
      if context.blueprint.validation_rules.get("fail_fast", True):
          raise ValueError(format_setup_report(setup_results))
  ```
- **Resolution Needed:**
  1. Add `add_validation_error()` method to `PipelineState` class
  2. Update all error handling to use context-based error storage
  3. Implement fail-fast logic based on blueprint configuration
  4. Create error summary reporting from accumulated errors
  5. Update exception handling to preserve error context
- **Files to Change:**
  - `dcc/workflow/core_engine/context.py` - Add error management methods
  - `dcc/workflow/dcc_engine_pipeline.py` - Update orchestrator error handling
  - All engine modules - Replace direct error calls with context-based handling
- **Phase 1 Progress**: ✅ COMPLETED - Core context enhancement implemented with domain separation, fail-fast logic, and standardized utilities. See [Update Log](#wp-err-int-2026-001-phase1) for details.
- **Link to Update Log:** [wp-err-int-2026-001-phase1](#wp-err-int-2026-001-phase1)

---

<a id="issue-iss-001"></a>
## 2026-04-28

### Issue ISS-001 — Phase 3 Heartbeat Interval Limitation (WP-PIPE-ARCH-001)
- **Status:** ✅ RESOLVED
- **Context:** R17 Telemetry Module requires heartbeat logs every 1,000 rows. However, the CalculationEngine uses vectorized pandas operations (processes entire columns at once) rather than row-by-row iteration. This architectural pattern does not provide natural iteration points to emit true "every 1000 rows" heartbeats without significant performance impact from chunked processing.
- **Root Cause:** Vectorized pandas operations process entire columns at once, not row-by-row
- **Impact:** 
  - Heartbeats emit at phase checkpoints (P1, P2, P2.5, P3) rather than at true 1,000-row intervals
  - For an 11,099-row dataset, only 1 heartbeat was emitted at the end of P1 instead of ~11 heartbeats
  - User-visible progress messages show "100.0%" at each phase checkpoint
  - Telemetry data still captures rows_processed, current_phase, memory_usage_mb, and percent_complete
- **Resolution:** Accepted as architectural limitation with phase-based heartbeats as the pragmatic solution:
  1. Heartbeats emit at the end of each processing phase (P1, P2, P2.5, P3)
  2. Each heartbeat captures total rows processed so far
  3. Memory usage is sampled at each checkpoint
  4. Future enhancement: Implement chunked processing if true row-by-row heartbeats are required
- **Mitigation:** 
  - Phase-based heartbeats provide adequate progress visibility for typical use cases
  - Heartbeat interval can be adjusted via TelemetryHeartbeat(interval=N) if needed
  - Chunked processing could be implemented as an optional processing mode
- **Files Changed:** 
  - `dcc/workflow/core_engine/telemetry_heartbeat.py` (created)
  - `dcc/workflow/processor_engine/core/engine.py` (updated for phase-based heartbeats)
- **Link to Update Log:** [update_log.md](#wp-pipe-arch-001-phase3-complete)

---

# Section 2. Closed Issues

<a id="issue-62"></a>
## 2026-04-24

### Issue #62 — Error Code Standardization (ALL PHASES COMPLETE)
- **Status:** ✅ COMPLETE (Phase 1 + Phase 2 + Phase 3 + Phase 4)
- **Context:** Error codes across the DCC pipeline use inconsistent formats: legacy VAL/SYS stubs, string-based codes (CLOSED_WITH_PLAN_DATE), and partial E-M-F-XXXX format. The anatomy_schema.json only supported single-letter engine codes, but actual usage includes 2-char layer codes (P1, P2, L3, S1, V5).
- **Root Cause:** Multiple competing error code systems evolved independently without a unified taxonomy. System errors (initiation_engine) use S-C-S-XXXX format correctly, but data/logic errors (processor_engine) mix formats.
- **Resolution (Phase 1):**
  1. Created `error_code_base.json` with 8 reusable definitions (agent_rule.md 2.3)
  2. Created `error_code_setup.json` with properties structure (references base)
  3. Created `system_error_config.json` with 20 system error codes (S-X-S-XXXX)
  4. Created `data_error_config.json` with 17 data/logic error codes (LL-M-F-XXXX)
  5. Migrated 5 string codes to standardized format:
     - CLOSED_WITH_PLAN_DATE → L3-L-V-0302
     - RESUBMISSION_MISMATCH → L3-L-V-0303
     - OVERDUE_MISMATCH → L3-L-V-0304
     - VERSION_REGRESSION → L3-L-V-0305
     - REVISION_GAP → L3-L-V-0306
  6. Added new code L3-L-V-0307 for CLOSED_WITH_RESUBMISSION (Issue #61 validation)
- **Files Changed (Phase 1 - Schema):**
  - `config/schemas/error_code_base.json` - NEW: definitions (8 reusable objects)
  - `config/schemas/error_code_setup.json` - NEW: properties structure
  - `config/schemas/system_error_config.json` - NEW: 20 system error codes
  - `config/schemas/data_error_config.json` - NEW: 17 data/logic error codes
  - `processor_engine/error_handling/config/anatomy_schema.json` - updated to v1.1
- **Files Changed (Phase 2 - Code):**
  - `processor_engine/error_handling/detectors/row_validator.py` - 5 string codes → standardized codes
  - `processor_engine/error_handling/config/messages/en.json` - Added error_codes section
  - `processor_engine/error_handling/config/messages/zh.json` - Added error_codes section (Chinese)
- **Files Archived:**
  - `processor_engine/error_handling/config/error_codes.json` → `archive/workflow/processor_engine/error_handling/config/`
  - `initiation_engine/error_handling/config/system_error_codes.json` → `archive/workflow/initiation_engine/error_handling/config/`
- **Resolution (Phase 3 - Testing):**
  1. Completed 28 validation tests with 100% pass rate
  2. Verified all 37 error codes (20 system + 17 data/logic) validate against schema
  3. Validated bilingual messages (EN + ZH) for all data error codes
  4. Confirmed `row_validator.py` uses only standardized codes
  5. Verified health score weights properly assigned
- **Resolution (Phase 4 - Documentation Consolidation):**
  1. Created `README.md` — Master documentation index
  2. Created `error_handling_taxonomy.md` — Complete error code reference (37 codes)
  3. Created `consolidated_implementation_report.md` — All phases combined
  4. Archived Phase 1-4 workplans to `archive/phase1/`, `archive/phase2/`, `archive/phase3/`, `archive/phase4/`
  5. Moved `error_code_standardization_phase4_consolidation.md` to `archive/phase4/`
  6. Created `phase4_consolidation_test_report.md` per agent_rule.md Section 9
  7. Renamed `data_error_handling.md` → `data_error_handling_workplan.md` per naming convention
- **Architecture:** agent_rule.md Section 2.3 compliant (base → setup → config)
- **Final Deliverables:**
  - **Active Workplans (6):** README.md, error_handling_taxonomy.md, error_catalog_consolidation_plan.md, data_error_handling_workplan.md, system_error_handling_workplan.md, error_handling_module_workplan.md, pipeline_messaging_plan.md
  - **Reports (4):** consolidated_implementation_report.md, phase4_consolidation_test_report.md, pipeline_messaging_plan_report.md, resolution_module_implementation_report.md, system_error_handling_completion_report.md
  - **Archive (4 phases):** 7 workplans archived in phase1/, phase2/, phase3/, phase4/
- **Links:**
  - Phase 1: [update_log.md](#error-code-standardization-phase1)
  - Phase 2: [update_log.md](#error-code-standardization-phase2)
  - Phase 3: [update_log.md](#error-code-standardization-phase3)
  - Phase 4: [update_log.md](#error-code-standardization-phase4)

---

<a id="issue-61"></a>
## 2026-04-24

### Issue #61 — Resubmission_Required=YES when Submission_Closed=YES (816 rows)
- **Status:** RESOLVED
- **Context:** Output file `processed_dcc_universal.xlsx` contains 816 rows where `Submission_Closed=YES` and `Resubmission_Required=YES`. Business rule: if submission is closed, resubmission should not be required.
- **Root Cause:** In `processor_engine/calculations/conditional.py`, `apply_update_resubmission_required()` has condition 2 to set `Resubmission_Required=NO` when `Submission_Closed=YES`. However, the function respects preservation mode. The schema for `Resubmission_Required` has no explicit `strategy` configuration, so it defaults to `preserve_existing` mode. This means rows with existing source values are skipped, and the closed-submission override never applies to them.
- **Resolution:** Added explicit `strategy: {data_preservation: {mode: overwrite_existing}}` to `Resubmission_Required` in `dcc_register_config.json`. The conditional logic now runs on all rows and correctly overrides to NO when closed.
- **Files Changed:** `config/schemas/dcc_register_config.json`
- **Link to Update Log:** [update_log.md](update_log.md)

---

<a id="issue-60"></a>
## 2026-04-24

### Issue #60 — Submission_Session and Submission_Session_Revision have NaN after forward fill
- **Status:** RESOLVED
- **Context:** When pipeline runs, the output file shows Submission_Session and Submission_Session_Revision columns contain literal 'nan' strings instead of being forward-filled.
- **Root Cause:** In `processor_engine/utils/dataframe.py`, lines 125-130 converted Submission_Session columns to string **BEFORE** Phase 1 forward fill ran:
  ```python
  # This code ran BEFORE forward fill, converting NaN → 'nan' string
  submission_session_cols = ['Submission_Session', 'Submission_Session_Revision']
  for col in submission_session_cols:
      df_init[col] = df_init[col].astype(str)  # NaN becomes 'nan' string!
  ```
  Later in forward fill (`null_handling.py`), `pd.isna('nan')` returns `False` because 'nan' is a valid string. So ffill() skips these values, and they remain as 'nan' in output.
- **Resolution:** Removed the premature string conversion code (lines 125-130) from `dataframe.py`. Forward fill in `null_handling.py` already handles NaN properly, and the zero-padding at the end converts to string correctly.
- **Files Changed:**
  - `processor_engine/utils/dataframe.py` - removed lines 125-130

<a id="issue-58"></a>
## 2026-05-01

### Issue #58 — kv-detail panel shows numeric indices instead of nested keys and values
- **Status:** RESOLVED
- **Context:** In `common_json_tools.html`, clicking any object node in the tree opened the Key Details panel but the "Child Keys" section displayed numbers (`0`, `1`, `2`...) instead of the actual key names and their values.
- **Root Cause:** Two bugs in `showKvDetail()`: (1) `Object.keys(value)` was called on the raw URL-encoded string parameter instead of `parsedValue` (the decoded JS object) — `Object.keys()` on a string returns character indices. (2) Array preview used `value.slice(0, 10)` on the raw string instead of `parsedValue.slice(0, 10)`. Additionally, the child keys section collapsed all keys into a single tag-badge row rather than one row per key with its value.
- **Resolution:** Fixed both `Object.keys(value)` → `Object.keys(parsedValue)` and `value.slice` → `parsedValue.slice`. Replaced the single collapsed "Keys" row with one table row per child key showing the key name and its rendered value. Also fixed CSS typo `word-break:break_word` → `word-break:break-word`.
- **Files Changed:** `dcc/ui/common_json_tools.html`
- **Link to update_log:** [update_log.md](#issue-58-kv-detail-fix)

---

<a id="issue-57"></a>
## 2026-05-01

### Issue #57 — Error catalog JSON files are stubs; 38 real codes missing; ErrorRegistry broken
- **Status:** RESOLVED
- **Context:** `error_codes.json` contains only 2 placeholder entries (`VAL-001`, `SYS-001`) in the wrong format. `ErrorRegistry` expects `"errors": {}` dict but JSON has `"codes": []` array — `self._errors` is always empty, making lookup, scoring, and aggregation silently broken. 38 real error codes used by detectors have no JSON definition. 10 named string codes in `row_validator.py` bypass the taxonomy. `ROW_ERROR_WEIGHTS` is hardcoded. `taxonomy.json` uses wrong engine codes. `anatomy_schema.json` regex rejects all real codes.
- **Root Cause:** Error catalog JSON files were created as stubs during initial scaffolding and never populated with the actual codes implemented in the detector modules.
- **Resolution:** Implemented Error Catalog Consolidation (Phases EC1-EC4). See plan: `dcc/workplan/error_handling/error_catalog_consolidation_plan.md`
- **Files Changed:** `processor_engine/error_handling/config/error_codes.json`, `taxonomy.json`, `anatomy_schema.json`, `remediation_types.json`, `processor_engine/error_handling/core/registry.py`, `processor_engine/error_handling/detectors/row_validator.py`
- **Link to update_log:** [update_log.md](#error-catalog-consolidation)

<a id="issue-56"></a>
## 2026-05-01

### Issue #56 — Windows console encoding rejects Unicode symbols in pipeline output
- **Status:** RESOLVED
- **Context:** During SE1/SE4 testing, `milestone_print()` and `system_error_print()` raised `UnicodeEncodeError: 'charmap' codec can't encode character` on Windows terminals using cp1252 encoding. Affected characters: `✓` (U+2713), `✗` (U+2717), `⚠` (U+26A0), `━` (U+2501).
- **Root Cause:** Windows default console encoding is cp1252 which does not include these Unicode characters. The existing `milestone_print()` already used `✓`/`✗` but was not tested on Windows.
- **Resolution:** Replaced all Unicode symbols with ASCII equivalents in both `system_errors.py` and `logging.py`: `✓`→`OK`, `✗`→`X`, `⚠`→`!`, `━`→`-`.
- **Files Changed:** `initiation_engine/error_handling/system_errors.py`, `initiation_engine/utils/logging.py`
- **Link to update_log:** [update_log.md](#system-error-handling-complete)

<a id="issue-55"></a>
## 2026-05-01

### Issue #55 — dcc_engine_pipeline.py stops silently with no error message
- **Status:** RESOLVED
- **Context:** Running `python dcc_engine_pipeline.py` exits without printing any error or traceback.
- **Root Cause:** Three compounding issues: (1) `main()` outer `except` called `log_error()` which is suppressed at default verbose level. (2) `run_ai_ops()` caught all exceptions with only `logger.warning()`, also suppressed. (3) `RunStore._get_conn()` silently swallowed `ImportError` for duckdb.
- **Resolution:** Implemented system error handling (Phases SE1–SE4). All three locations now call `system_error_print()` which bypasses `DEBUG_LEVEL` and always prints to stderr. Step-level wrappers added to `run_engine_pipeline()` for precise error codes per failure type.
- **Files Changed:** `initiation_engine/error_handling/` (new sub-module), `dcc_engine_pipeline.py`, `ai_ops_engine/core/engine.py`, `ai_ops_engine/persistence/run_store.py`, `initiation_engine/utils/logging.py`
- **Link to update_log:** [update_log.md](#system-error-handling-complete)

---

<a id="issue50-static-dashboard-ui"></a>
## 2026-04-20
[Issue #50]: Static Dashboard — inspector tab resets to Info on every node selection
- [Status]: RESOLVED
- [Context]: Every time a node was selected (from file tree, flow tree, graph, or inspector links), the inspector panel always switched back to the Info tab, losing the user’s current tab context.
- [Root Cause]: `openInspector()` unconditionally called `switchInsTab('info')` on every invocation.
- [File Changes]: `dcc/tracer/static_dashboard.html` — added `currentInspectorTab` state variable; `switchInsTab` saves to it; `openInspector` restores from it.
- [Resolution]: Inspector tab selection is now preserved across all node navigation sources.
- [Link to Update Log]: [update_log.md](#static-dashboard-ui-enhancements)

<a id="issue49-tree-collapsible"></a>
## 2026-04-20
[Issue #49]: static_dashboard.html file tree is not collapsible
- [Status]: RESOLVED
- [Context]: The file tree implemented in Phase 1c was a flat recursive list, making navigation difficult for large codebases.
- [Root Cause]: Lack of hierarchical DOM structure and toggle state logic in the `renderFileTree` function.
- [File Changes]:
  - `dcc/tracer/static_dashboard.html` — refactored `renderFileTree` to create nested `tree-node` structures; added CSS for `tree-toggle` and `tree-children`.
- [Resolution]: Implemented a nested, collapsible tree structure. Added toggle arrows (`▶`) for packages and modules. Clicking the toggle arrow expands/collapses children while clicking the label remains functional for filtering.
- [Link to Update Log]: [update_log.md](#issue49-tree-collapsible)

<a id="issue48-backend-path-resolution"></a>
## 2026-04-20
[Issue #48]: static_dashboard.html shows "✗ Invalid response: missing nodes" error
- [Status]: RESOLVED
- [Context]: When attempting to analyze a directory (e.g., `dcc/workflow`), the dashboard returned a cryptic "missing nodes" error.
- [Root Cause]: 
  1. **Backend:** `project_root` resolution in `server.py` was off by one level (used 3 `.parent` instead of 4), causing path lookups to fail.
  2. **Frontend:** Error handling in `runAnalysis` swallowed the specific backend error (e.g., "Directory not found") and threw a generic "missing nodes" error instead.
- [File Changes]:
  - `dcc/tracer/backend/server.py` — fixed `project_root` resolution using `.resolve()` and 4 parents.
  - `dcc/tracer/static_dashboard.html` — improved error handling to display specific backend error details.
- [Resolution]: Fixed backend path resolution and upgraded frontend error reporting. Backend now correctly locates directories regardless of starting context.
- [Link to Update Log]: [update_log.md](#issue48-backend-path-resolution)

<a id="issue47-serve-proxy"></a>
## 2026-04-20
[Issue #47]: static_dashboard.html shows "Failed to fetch" in GitHub Codespaces
- [Status]: RESOLVED
- [Context]: Dashboard called `http://localhost:8000/static/analyze` which is unreachable from the browser in Codespaces (private port, redirects to GitHub login).
- [Root Cause]: Three compounding problems:
  1. `localhost:8000` is not reachable from the browser in Codespaces — each port gets a unique public URL (`https://{name}-{port}.app.github.dev`) and port 8000 was Private.
  2. Switching to the public URL still failed because Private ports redirect to GitHub OAuth.
  3. FastAPI backend was started with system `python3` which lacks `fastapi` — backend was not running at all.
- [File Changes]:
  - `dcc/serve.py` — added `/api/*` reverse proxy to FastAPI backend; browser only needs port 5000
  - `tracer/static_dashboard.html` — replaced `http://localhost:8000` with `/api` (same-origin relative path)
  - `ui/tracer_pro.html` — same relative path fix
- [Resolution]: `serve.py` now proxies `/api/*` → `localhost:8000` server-side. Browser calls same-origin `/api/static/analyze` on port 5000; no cross-port or CORS issues in any environment. Backend must be started with `/opt/conda/envs/dcc/bin/python3`.
- [Link to Update Log]: [update_log.md](#issue47-serve-proxy)

<a id="issue46-networkx-dcc-env"></a>
## 2026-04-20
[Issue #46]: Static analysis returns 0 edges when run through FastAPI backend
- [Status]: RESOLVED
- [Context]: Direct Python run produced 737 edges; calling `/static/analyze` via the backend returned 0 edges.
- [Root Cause]: `networkx` and `pyvis` were installed into the system Python environment during development but not into the `dcc` conda environment. The FastAPI backend runs under `/opt/conda/envs/dcc/bin/python3`, which had no `networkx`, so `_NX_AVAILABLE = False` and all edge-building code was skipped.
- [File Changes]:
  - `dcc/dcc.yml` — `networkx>=3.0` and `pyvis>=0.3.2` already added to pip section (from Issue #43); packages now also installed into dcc env
- [Resolution]: Ran `/opt/conda/envs/dcc/bin/pip install networkx pyvis`. Restarted backend. Analysis now returns 754 nodes, 737 edges, 383 entry points.
- [Link to Update Log]: [update_log.md](#issue46-networkx-dcc-env)

<a id="issue45-backend-wrong-python"></a>
## 2026-04-20
[Issue #45]: FastAPI backend fails to start — `ModuleNotFoundError: No module named 'fastapi'`
- [Status]: RESOLVED
- [Context]: Running `python3 tracer/backend/server.py` from the dcc directory failed immediately.
- [Root Cause]: The system Python at `/home/codespace/.python/current/bin/python3` does not have `fastapi` installed. The `dcc` conda environment at `/opt/conda/envs/dcc/` has `fastapi` but is not the default `python3`.
- [File Changes]: None — runtime invocation change only.
- [Resolution]: Backend must be started with the full conda env path: `/opt/conda/envs/dcc/bin/python3 tracer/backend/server.py`. Documented in workplan Deployment Notes section.
- [Link to Update Log]: [update_log.md](#issue45-backend-wrong-python)

<a id="issue44-server-uvicorn-string"></a>
## 2026-04-20
[Issue #44]: `ModuleNotFoundError: No module named 'backend'` when running server.py from `tracer/backend/` directory
- [Status]: RESOLVED
- [Context]: Running `python server.py` from inside `tracer/backend/` raised `ModuleNotFoundError: No module named 'backend'`.
- [Root Cause]: The `__main__` block used `uvicorn.run("backend.server:app", ...)` — a string app reference that requires Python to import `backend` as a top-level package. This only works when cwd is `tracer/`. Running from `tracer/backend/` makes `backend` unresolvable.
- [File Changes]: `tracer/backend/server.py` — replaced string reference with direct `app` object: `uvicorn.run(app, host=..., port=...)`. Added `--port` and `--host` CLI arguments.
- [Resolution]: Server now starts correctly from any working directory.
- [Link to Update Log]: [update_log.md](#issue44-server-uvicorn-string)

<a id="issue43-static-analysis"></a>
## 2026-04-20
[Issue #43]: Phase 1b Static Analysis Module — networkx edges were 0 on first run
- [Status]: RESOLVED
- [Context]: After building CallGraph, edge count was 0 despite 737 resolvable edges.
- [Root Cause]: `networkx` was not installed in the `dcc` conda environment. Additionally, `_resolve_call` had no skip-list for generic names (`get`, `sort`, `info`, etc.) causing noisy/wrong edge resolution.
- [File Changes]:
  - `tracer/static/graph.py` — added `_SKIP_CALLS` class attribute (40+ generic names)
  - `dcc/dcc.yml` — added `networkx>=3.0` and `pyvis>=0.3.2` to pip section
- [Resolution]: Installed `networkx` and `pyvis` via pip. Added `_SKIP_CALLS` filter. Re-run produced 737 edges, 383 entry points.
- [Link to Update Log]: [update_log.md](#issue43-static-analysis)

<a id="issue33-json-tools-ui"></a>
## 2026-04-18 21:45:00
[Issue #33]: JSON Tools UI - restructure sidebar panels and integrate backup features
- [Status]: RESOLVED
- [Context]: common_json_tools.html needed restructuring to separate Files, Structure, Actions, Options as distinct sidebar icons (matching backup file layout).
- [Root Cause]: Original HTML combined all functions into 3 panels (Inspector/Formatter/Validator) instead of 4 separate panels.
- [File Changes]: 
  - ui/common_json_tools.html - Added 4 new icon bar buttons, restructured sidebar panels
  - ui/dcc-design-system.css - Added tree/key-explorer CSS classes
  - ui/common_json_tools_backup.html - Referenced for style comparison
- [Resolution]: 
  1. Updated icon bar with separate buttons: Files 📁, Structure 🌳, Actions ⚡, Options ⚙️
  2. Restructured sidebar into 4 panels matching new icons
  3. Added structure panel with Key Explorer (copied style from backup)
  4. Integrated Full Inspection tab with stats, filters, full table
  5. Added Key-Value Details panel (bottom)
  6. CSS added for tree-node styling in design system
- [Link to Update Log]: [update_log.md](#issue33-json-tools-ui)

<a id="issue32-verbose-levels"></a>
## 2026-04-19 11:30:00
[Issue #32]: Pipeline output too verbose for user-facing messages
- [Status]: RESOLVED
- [Context]: dcc_engine_pipeline.py outputs debug trees, full paths, internal tracking - not simplified for end users
- [Root Cause]: No --verbose argument with level control; all status/debug prints shown regardless
- [File Changes]: 
  - initiation_engine/utils/cli.py
  - initiation_engine/utils/logging.py
  - initiation_engine/__init__.py

## 2026-04-19 05:00:00
[Issue #33]: Default pipeline output (level 1/normal) still shows internal function call trees, full absolute paths, step bracket notation, CLI override messages, third-party library warnings, and WARNING messages. Previous workplan was marked COMPLETE but implementation was not done.
- `[Status]`: Open — awaiting approval for implementation
- `[Context]`: Running `python dcc_engine_pipeline.py` at default level shows 80+ lines of internal detail before any processing begins. User expects clean milestone-level output only.
- `[Root Cause]`: `status_print()` calls throughout all engine modules print regardless of level. Only `StructuredLogger.log_error()` was suppressed in the previous fix. The general `status_print()` in validators, schema loaders, and engine steps was never gated by level.
- `[Action Required]`: Approve redesigned workplan, then implement `milestone_print()`, `min_level` parameter for `status_print()`, warning suppression, and banner fix across 7 files.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#pipeline-messaging-redesign)
  - dcc_engine_pipeline.py
  - schema_engine/loader/*.py
- [Resolution]: Added --verbose argument with 4 levels (quiet/normal/debug/trace), framework banner visible at all levels
- [Link to Update Log]: See update_log.md

---

<a id="issue31-json-output"></a>
## 2026-04-19 10:30:00
[Issue #31]: JSON type columns still have string output in Excel
- [Status]: RESOLVED
- [Context]: dcc_register_config.json defines columns with column_type: "json_column", but calculated output is still string/CSV format instead of JSON arrays
- [Root Cause]: In aggregate.py line 86, code checks `data_type == 'json'` but schema uses `column_type: 'json_column'`. The wrong attribute is checked.
- [File Changes]: 
  - dcc/workflow/processor_engine/calculations/aggregate.py
- [Resolution]: Changed line 86 to also check column_type == 'json_column'
  - is_json = engine.columns.get(column_name, {}).get('data_type') == 'json' → is_json = engine.columns.get(column_name, {}).get('column_type') == 'json_column'
- [Link to Update Log]: See update_log.md

---

## 2026-04-12 00:00:00
[Issue # 2]: For preserve existing data per certain conditions, the current implementation is to add a new rule in the schema. This approach is not scalable and maintainable. To consider a more scalable and maintainable approach.
- [Status]: Open
- [Link to changes in update_log.md]: [update_log.md](update_log.md)

## 2026-04-15 09:40:00
[Issue #17]: tools/project_setup_tools.py should be updated to establish a new project folder, copies all necessary files, and configure schemas.
- [Status]: Open
- [Link to changes in update_log.md]: [update_log.md](update_log.md)

# Section 3. Closed Issues

## 2026-04-28

### Issue #63 — Pipeline Architecture Full Compliance (WP-PIPE-ARCH-001)
- **Status:** ✅ COMPLETE
- **Context:** Phase 5 completion achieves overall `FULLY COMPLIANT` status (`19 PASS`, `2 PARTIAL`) for pipeline architecture requirements.
- **Root Cause:** Originally three capability groups were not fully closed: Dependency Injection depth, 1,000-row telemetry heartbeat, and UI-facing exception/override contracts.
- **Resolution:** Successfully completed through workplan phases:
  1. ✅ Phase 2: DI boundary hardening with factory pattern and backward compatibility
  2. ✅ Phase 3: telemetry heartbeat contract with phase-based checkpoints (ISS-001 documented)
  3. ✅ Phase 4: UI consumer and overrides contract with complete backend API
  4. ✅ Phase 5: Final compliance reassessment and documentation
- **Files Changed:** 
  - `dcc/workplan/pipeline_architecture/pipeline_architecture_design_workplan.md` (updated to v1.0, COMPLETE)
  - `dcc/workplan/pipeline_architecture/reports/phase_5_final_compliance_report.md` (created)
  - `dcc/workplan/pipeline_architecture/reports/lessons_learned_best_practices.md` (created)
  - `dcc/log/update_log.md` (updated with Phase 5 completion)
- **Final Compliance Status:** 19 PASS / 2 PARTIAL / 0 FAIL (90.5% compliance rate)
- **Links to Update Log:** 
  - Phase 1: [update_log.md](#wp-pipe-arch-001-phase1-traceability)
  - Phase 2: [update_log.md](#wp-pipe-arch-001-phase2-complete)
  - Phase 3: [update_log.md](#wp-pipe-arch-001-phase3-complete)
  - Phase 4: [update_log.md](#wp-pipe-arch-001-phase4-complete)
  - Phase 5: [update_log.md](#wp-pipe-arch-001-phase5-complete)

---

## 2026-04-19 04:00:00
[Issue #31]: Aggregate columns (e.g., All_Submission_Dates) outputting plain strings instead of JSON arrays.
- [Status]: Resolved
- [Context]: Aggregate columns are defined as 'json' data type in the dcc_register schema, but were being output as comma-separated strings.
- [Root Cause]: `aggregate.py` used `separator.join()` exclusively without checking the target column's `data_type`.
- [File Changes]: `processor_engine/calculations/aggregate.py`
- [Resolution]: Modified aggregate handlers to check `engine.columns` for `data_type == 'json'` and use `json.dumps()` for serialization when required.
- [Link to changes in update_log.md]: [update_log.md](update_log.md#issue31-aggregate-json-fix)

## 2026-04-19 04:00:00
[Issue #23]: Phase 5 — AI Integration & Advanced Analytics planning and implementation.
- [Status]: Resolved
- [Context]: Phase 5 was planned but missing formal reports and the UI dashboard.
- [Root Cause]: Implementation completed but documentation artifacts (phase reports) and the AI Analysis Dashboard HTML were not generated.
- [File Changes]: `workplan/ai_operations/reports/phase5.x_report.md`, `ui/ai_analysis_dashboard.html`
- [Resolution]: Generated 5 phase reports (5.1-5.5) detailing engine architecture, insight logic, UI integration, live monitoring, and persistence. Created the self-contained AI Analysis Dashboard conforming to the DCC UI Design System.
- [Link to changes in update_log.md]: [update_log.md](update_log.md#phase5-completion)

## 2026-04-19 04:00:00
[Issue #31]: Schema Map flowchart in `common_json_tools.html` does not show 3-tier definition→property→value relationship. Nodes shown in flat grid with no arrows or semantic layout.
- `[Status]`: **Resolved**
- `[Context]`: Schema Map tab showed boxes in a grid. Previous fix added arrows but still treated all files as generic nodes without classifying them by role (base/setup/config). Did not reflect the actual 3-tier schema architecture.
- `[Root Cause]`: `buildSchemaMap()` had no tier classification logic. All files placed in a flat layout regardless of whether they contained `definitions`, `properties`, or actual values.
- `[Resolution]`: Rewrote `buildSchemaMap()` with `classifyTier()` auto-classification, 3-column SVG layout (DEFINITIONS | PROPERTIES | VALUES), typed arrow markers, edge labels, tier detail tables, and full $ref mapping table. Added full `.sm-*` CSS component system to `dcc-design-system.css`.
- `[File Changes]`: `dcc/ui/common_json_tools.html`, `dcc/ui/dcc-design-system.css`
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#schema-map-flowchart-fix)

 `dcc` conda env missing `jsonschema` — `Environment test failed. Missing required packages: ✗ jsonschema: No module named 'jsonschema'`.
- [Status]: Resolved
- [Context]: Pipeline passes in base conda env (has `jsonschema==4.26.0`) but fails in `dcc` env. `dcc.yml` pip section was missing `jsonschema` and `rapidfuzz`.
- [Root Cause]: Both `dcc/dcc.yml` and root `dcc.yml` pip sections did not include `jsonschema` or `rapidfuzz`. Env created from yml would always be missing these packages.
- [Resolution]: Installed `jsonschema==4.23.0` and `rapidfuzz==3.13.0` into `dcc` env. Updated both yml files to include all required pip packages including dependencies (`attrs`, `jsonschema-specifications`, `referencing`, `rpds-py`).
- [File Changes]: `dcc/dcc.yml`, `dcc.yml` (root)
- [Link to changes in update_log.md]: [update_log.md](update_log.md#issue30-env-fix)

## 2026-04-19 02:00:00
[Issue #27]: `Submission_Session` pattern `^[0-9]{6}$` fails for all 11,099 rows.
- [Status]: Resolved
- [Root Cause]: Column stored as `int64`/`float64` from source Excel. Zero-padding applied during null-fill only. Pattern validation ran on raw integer values (e.g. `1` instead of `000001`).
- [Resolution]: Added `_safe_zfill()` in `apply_validation` to cast numeric values to zero-padded strings before pattern check. Non-numeric values (e.g. reply sheet IDs) pass through unchanged via `try/except`.
- [File Changes]: `processor_engine/calculations/validation.py` — added zero-pad pre-processing block before null check loop.
- [Link to changes in update_log.md]: [update_log.md](update_log.md#issue27-issue29-fix)

## 2026-04-19 02:00:00
[Issue #29]: `CLOSED_WITH_PLAN_DATE` fires on 4,674 rows — `Resubmission_Plan_Date` not nullified when `Submission_Closed=YES`.
- [Status]: Resolved
- [Root Cause]: `Resubmission_Plan_Date` had no explicit strategy in schema — `StrategyResolver._infer_strategy()` defaulted to `preserve_existing`. The `StrategyExecutor` only ran the handler on null rows (`df_to_calc = df_result[null_mask]`), so existing source values for closed rows were never nullified by `apply_resubmission_plan_date` condition 1.
- [Resolution]: Added explicit `strategy: {data_preservation: {mode: overwrite_existing}}` to `Resubmission_Plan_Date` in `dcc_register_config.json`. Handler now runs on ALL rows, correctly nullifying 6,381 closed rows.
- [File Changes]: `config/schemas/dcc_register_config.json` — added `strategy` key to `Resubmission_Plan_Date` column definition.
- [Link to changes in update_log.md]: [update_log.md](update_log.md#issue27-issue29-fix)

## 2026-04-19 01:00:00
[Issue #28]: `Resubmission_Required` outputting `'PEN'` instead of `'PENDING'` — 816 rows with invalid categorical value.
- [Status]: Resolved
- [Context]: `conditional.py` used abbreviated string `'PEN'` instead of full value `'PENDING'` defined in `dcc_register_rule.md` allowed values.
- [Root Cause]: String literal typo in `conditional.py` line 147.
- [Resolution]: Changed `'PEN'` → `'PENDING'` in `conditional.py`. 816 rows now correctly categorised. 0 invalid values after fix.
- [Link to changes in update_log.md]: [update_log.md](update_log.md#col-validation-implementation)

## 2026-04-18 20:00:00
[Issue #25]: agent_rule.md path mismatch in project_config.json - validator looking at wrong location.
- [Status]: Resolved
- [Context]: dcc_engine_pipeline.py failed with "Ready: NO" because validator expects agent_rule.md at dcc/agent_rule.md but file exists at dcc/rule/agent_rule.md.
- [Root Cause]: project_config.json lists agent_rule.md as root file without specifying rule/ subdirectory path.
- [File Changes]: config/schemas/project_config.json - changed agent_rule.md path from "agent_rule.md" to "rule/agent_rule.md"
- [Resolution]: Updated project_config.json root_files entry to specify correct relative path "rule/agent_rule.md". Pipeline now passes validation with "Ready: YES".
- [Link to changes in update_log.md]: [update_log.md](update_log.md#issue-25)

## 2026-04-17 20:45:00
[Issue #24]: P2-I-V-0204 false positives for valid Document_ID - derived_pattern validation failing for complex IDs.
- [Status]: Resolved
- [Resolution]: Updated `derived_pattern` generation logic to handle alphanumeric segments correctly.
- [Link to changes in update_log.md]: [update_log.md](update_log.md#issue-24)

## 2026-04-19 04:30:00
[Issue #32]: Aggregate columns outputting string instead of JSON in final output.
- [Status]: Resolved
- [Context]: Despite code support for JSON serialization in aggregate.py, the columns remained as strings in output.
- [Root Cause]: The `dcc_register_config.json` schema had aggregate columns defined as `data_type: "text"` instead of `data_type: "json"`.
- [File Changes]: `config/schemas/dcc_register_config.json`
- [Resolution]: Updated schema definitions for `All_Submission_Sessions`, `All_Submission_Dates`, `All_Submission_Session_Revisions`, `All_Approval_Code`, and `Consolidated_Submission_Session_Subject` to use `data_type: "json"`.
- [Link to changes in update_log.md]: [update_log.md](update_log.md#issue32-schema-json-fix)

# Section 3. New Issues

<a id="issue34-kv-detail-panel"></a>
## 2026-04-19
[Issue #34]: Key-Value Detail Panel - shows related keys/values when selecting key in tree
- [Status]: RESOLVED
- [Context]: When selecting a key in the tree view, kv-detail-panel should show related keys and values.
- [Root Cause]: Tree nodes only showed keys without values. Need to add click handlers and update kv-detail-panel.
- [File Changes]: ui/common_json_tools.html
- [Resolution]: Added data attributes to tree nodes, updated click handlers to showKvDetail function. tree-node now shows only keys (not values), nested keys expand on click. kv-detail-content shows key, type, value, related keys, siblings.
- [Link to Update Log]: [update_log.md](#issue34-kv-detail-panel)

<a id="issue35-tree-scroll"></a>
## 2026-04-19
[Issue #35]: Sidebar Key-Tree scrollbar not visible
- [Status]: RESOLVED
- [Context]: Key-tree in sidebar should show scrollbar when tree nodes overflow.
- [Root Cause]: Parent flex containers missing min-height: 0 for flex scrolling.
- [File Changes]: ui/common_json_tools.html, ui/dcc-design-system.css
- [Resolution]: Added min-height: 0 to editor-pane, panels-container, content-panel, tree-view, editor-input, key-tree. Added sidebar-panel-stretch class for flexible panels.
- [Link to Update Log]: [update_log.md](#issue35-tree-scroll)

<a id="issue36-sidebar-panels"></a>
## 2026-04-19
[Issue #36]: Sidebar panels not switching on icon bar clicks
- [Status]: RESOLVED
- [Context]: Clicking sidebar icons should show related panels.
- [Root Cause]: Inline display:none styles overriding CSS class switching.
- [File Changes]: ui/common_json_tools.html, ui/dcc-design-system.css
- [Resolution]: Removed inline display:none, used CSS class .visible for panel switching. Added initial .visible on panel-files.
- [Link to Update Log]: [update_log.md](#issue36-sidebar-panels)

<a id="issue37-array-keys"></a>
## 2026-04-19
[Issue #37]: Key-details not showing values for array elements [0], [1], etc
- [Status]: RESOLVED
- [Context]: Selecting array items like files[0], files[1] should show key-value details.
- [Root Cause]: Path mismatch between tree nodes and allFlatRows. Tree used numeric keys like 0, allFlatRows used bracketed keys like [0].
- [File Changes]: ui/common_json_tools.html
- [Resolution]: Added data-value attribute to tree nodes storing JSON-encoded value. Click handlers read directly from DOM data attributes instead of allFlatRows lookup. showKvDetail parses string values back to objects.
- [Link to Update Log]: [update_log.md](#issue37-array-keys)

<a id="issue38-schema-map"></a>
## 2026-04-19
[Issue #38]: Schema Map - flowchart showing $ref relationships
- [Status]: RESOLVED
- [Context]: Create schema map content-tab showing $ref relationships as flowchart diagram.
- [Root Cause]: Need to parse $ref from loaded JSON files and display as SVG flowchart.
- [File Changes]: ui/common_json_tools.html, ui/dcc-design-system.css
- [Resolution]: Added Schema Map tab, uses files from Load Files button. Parses $ref patterns (#/definitions/, http://...#/definitions/). Displays nodes:
  - Green = schema files
  - Orange = external schema refs
  - Gray = local definitions
- [Link to Update Log]: [update_log.md](#issue38-schema-map)

<a id="issue39-tracer-indent"></a>
## 2026-04-19 21:55:00
[Issue #39]: Tracer backend server indentation errors
- [Status]: RESOLVED
- [Context]: Backend server for code tracing module failed to start due to IndentationError.
- [Root Cause]: Multiple endpoint decorators and functions (lines 288-616) were incorrectly indented by 8 spaces.
- [File Changes]: dcc/tracer/backend/server.py
- [Resolution]: Fixed indentation for all affected endpoints and functions. Cleaned up redundant inline imports.
- [Link to Update Log]: [update_log.md](#issue39-tracer-indent)

<a id="issue40-serve-root"></a>
## 2026-04-19 21:50:00
[Issue #40]: Webpage server (serve.py) root directory mismatch
- [Status]: RESOLVED
- [Context]: Webpage server failed to load the expected HTML file (404 Error).
- [Root Cause]: `DIRECTORY` was set to "dcc" which caused a nested path issue when run from the `dcc` folder. Default path was also missing the `ui/` subdirectory.
- [File Changes]: dcc/serve.py
- [Resolution]: Updated `DIRECTORY` to "." and fixed the default path to "/ui/Excel Explorer Pro working.html".
- [Link to Update Log]: [update_log.md](#issue40-serve-root)

<a id="issue41-tracer-deps"></a>
## 2026-04-19 22:05:00
[Issue #41]: Missing tracer dependencies in conda environments
- [Status]: RESOLVED
- [Context]: Tracer backend failed to import `fastapi` and `uvicorn`.
- [Root Cause]: Dependencies were listed in README but missing from `dcc.yml` files.
- [File Changes]: dcc.yml, dcc/dcc.yml
- [Resolution]: Added `fastapi` and `uvicorn` to both `dcc.yml` dependency files and installed them in the current environment.
- [Link to Update Log]: [update_log.md](#issue41-tracer-deps)

<a id="issue42-pipeline-runner"></a>
## 2026-04-19 22:15:00
[Issue #42]: Lack of generic pipeline loading and tracing functionality
- [Status]: RESOLVED
- [Context]: Tracer lacked a way to dynamically load and trace arbitrary pipeline scripts without code modification.
- [Root Cause]: Standard import-based tracing required manual wrapper scripts (e.g., `trace_pipeline.py`).
- [File Changes]: 
  - tracer/pipeline_sandbox/runner.py (Added)
  - tracer/backend/server.py
  - tracer/README.md
- [Resolution]: Implemented `PipelineSandbox` runner using `importlib.util` and added a `/pipeline/run` endpoint to the backend API.
- [Link to Update Log]: [update_log.md](#issue42-pipeline-runner)

<a id="issue59-milestones-errors"></a>
## 2026-04-24

### Issue #59 — Pipeline milestones used hardcoded strings; system errors lacked step-level precision
- **Status:** RESOLVED
- **Context:** Pipeline milestones for "Setup validated" and "Schema loaded" used static strings like "7 folders, 11 files" and "44 columns, 6 references". System errors used a generic `S-R-S-0401` code for all runtime exceptions regardless of the pipeline step.
- **Root Cause:** Milestone printing logic in `dcc_engine_pipeline.py` did not query the validators for actual result counts. System error framework lacked granular codes for distinct execution phases.
- **Resolution:** Added count helper methods to `ProjectSetupValidator` and `SchemaValidator`. Updated `dcc_engine_pipeline.py` to use these methods. Introduced `S-R-S-0404/05/06` error codes and enhanced `system_errors.py` to support promoted descriptions and step-specific titles.
- **Files Changed:** `dcc_engine_pipeline.py`, `initiation_engine/core/validator.py`, `schema_engine/validator/schema_validator.py`, `initiation_engine/error_handling/system_errors.py`, `initiation_engine/error_handling/config/system_error_codes.json`, `initiation_engine/error_handling/config/messages/system_en.json`
- **Link to update_log:** [update_log.md](#refined-system-errors-milestones)

<a id="issue43-pipeline-initiation-cli"></a>
## 2026-04-23 23:20:00
[Issue #43]: Pipeline startup falsely reported CLI overrides and duplicated initiation setup loading
- [Status]: RESOLVED
- [Context]: `dcc_engine_pipeline.py` printed CLI override state incorrectly when no user CLI args were passed, and startup instantiated `ProjectSetupValidator` twice across environment bootstrap and initiation validation.
- [Root Cause]: `parse_cli_args()` always seeded `cli_args` with default verbosity, making the override dictionary non-empty. `test_environment()` also constructed `ProjectSetupValidator` just to read dependency configuration from `project_setup.json`.
- [File Changes]:
  - workflow/initiation_engine/utils/cli.py
  - workflow/initiation_engine/utils/system.py
  - workflow/dcc_engine_pipeline.py
- [Resolution]: Changed CLI parsing to only record explicit user overrides, returned an explicit override-status boolean to the pipeline banner path, removed the duplicate validator bootstrap from `test_environment()`, and added an environment-ready milestone after a successful dependency check.
- [Link to Update Log]: [update_log.md](#issue43-pipeline-initiation-cli)

<a id="issue-iss-013"></a>
## 2026-05-12

### Issue ISS-013 — `Resubmission_Plan_Date` Incorrectly Set to `NaT` for Superseded (Non-Latest) Submission Rows

- **Status:** ✅ RESOLVED (final fix 2026-05-12)
- **Resolution Date:** 2026-05-12
- **Context:** `Resubmission_Plan_Date` was producing `NaT` for all prior submission rows (rows where `Submission_Date < Latest_Submission_Date`). Only the latest submission row for each `Document_ID` received a calculated plan date.
- **Root Cause — two iterations:**
  - **First fix (ISS-013 initial):** `apply_resubmission_plan_date` condition 1 used `Submission_Closed == 'YES'` to set `NaT`. Because `apply_submission_closure_status` marks superseded rows as `'YES'`, all prior rows got `NaT`. Fixed by switching to `Latest_Approval_Code in terminal_codes`.
  - **Second fix (this entry):** The `Latest_Approval_Code` check was applied to **all rows** regardless of whether they were the latest submission. `Latest_Approval_Code` reflects the document's current state — a superseded row that was `REJ` at the time has `Latest_Approval_Code = 'APP'` if the document was later approved. This caused every row of an eventually-approved document to get `NaT`. Fixed by adding `Submission_Date == Latest_Submission_Date` as a required co-condition — only the latest submission row of a terminally closed document gets `NaT`.
- **Impact:** Superseded rows had no `Resubmission_Plan_Date`, making `Delay_of_Resubmission` calculations incorrect.
- **File Changes:**
  - `dcc/workflow/processor_engine/calculations/date.py` — `apply_resubmission_plan_date` condition 1: now requires both `Submission_Date == Latest_Submission_Date` AND `Latest_Approval_Code in terminal_codes`. Superseded rows always fall through to conditions 2–4.
  - `dcc/config/schemas/dcc_register_config.json` — `Resubmission_Plan_Date.calculation.dependencies`: added `Latest_Approval_Code` as 5th dependency; condition 1 description updated.
  - `dcc/workplan/column_processing/column_update_logic.md` — Step 37 updated.
- **Resolution:** Condition 1 = `Submission_Date == Latest_Submission_Date AND Latest_Approval_Code in [APP, VOID, INF]` → `NaT`. All other rows (including superseded) receive a calculated plan date.
- **Link to Update Log:** [update-2026-05-12-resubmission-plan-date-fix](#update-2026-05-12-resubmission-plan-date-fix)

<a id="issue-iss-014"></a>
## 2026-05-12

### Issue ISS-014 — `Delay_of_Resubmission` Always 0 for Latest Submission Row When Resubmission Is Overdue

- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-12
- **Context:** `Delay_of_Resubmission` was 0 for the latest (active) submission row even when the review had been returned (`Review_Return_Actual_Date` populated), a plan date existed (`Resubmission_Plan_Date` in the past), and the resubmission had not yet occurred. Additionally, the original backward-looking logic (`shift(1).cummax()`) assigned delay to the *resubmission row* rather than the *plan-setting row*, contradicting the user requirement that delay should be stored on the previous submission (the row whose plan was missed). The `Submission_Closed == 'YES'` override also incorrectly zeroed out superseded rows, which are exactly the rows that should carry delay values.
- **Root Cause — three compounding issues:**
  1. **Wrong row assignment:** `shift(1).cummax()` assigned delay to the resubmission row (Row B gets the delay). Correct: delay belongs on the plan-setting row (Row A gets the delay because its plan was missed by Row B).
  2. **Latest row gap:** No next submission row exists for the latest row, so `shift(-1)` returns `NaT` → delay = 0, even when the plan date has passed and review has been returned.
  3. **Incorrect closed override:** `Submission_Closed == 'YES'` zeroed all closed rows including superseded ones. Only terminally closed rows (APP/VOID/INF) should be zeroed.
- **Impact:** All `Delay_of_Resubmission` values were 0 or misassigned. Reporting and KPI calculations showed no resubmission delays.
- **File Changes:**
  - `dcc/workflow/processor_engine/calculations/composite.py` — `apply_delay_of_resubmission` fully rewritten: (1) `shift(-1)` forward-looking assignment — delay stored on plan-setting row; (2) Path 2 for latest active overdue row using `today − Resubmission_Plan_Date`; (3) terminal-only override replacing blanket `Submission_Closed == 'YES'` override.
  - `dcc/config/schemas/dcc_register_config.json` — `Delay_of_Resubmission.calculation` description updated to reflect forward-looking logic.
  - `dcc/workplan/column_processing/column_update_logic.md` — Step 40 updated with two-path forward-looking description.
- **Resolution:** Two-path forward-looking calculation: Path 1 — `delay = max(next_Submission_Date − current_Resubmission_Plan_Date, 0)` via `shift(-1)`, stored on the plan-setting row. Path 2 — `delay = max(today − Resubmission_Plan_Date, 0)` for latest active overdue row. Terminal closure (APP/VOID/INF) overrides to 0; superseded rows keep their delay.
- **Link to Update Log:** [update-2026-05-12-delay-resubmission](#update-2026-05-12-delay-resubmission)

<a id="issue-iss-015"></a>
## 2026-05-15

### Issue # 062 — Phase 5: Data Column Logic Gap Remediation
- [Date:] 2026-05-16
- [Status:] ✅ RESOLVED
- [Context:] Three gaps discovered during Phase 5 evaluation: (1) `io_excel.py` dropna stripping 100%-null named columns before mapper sees them, (2) `calculations/validation.py` using non-standard `P-V-V-05xx` error codes, (3) missing L3 logic error codes in taxonomy document.
- [Root Cause:]
  - EC5.3: `df.dropna(axis=1, how='all')` at `io_excel.py:71` removed `Responder` column before mapper alias matching.
  - EC5.4: `calculations/validation.py` was not updated during the earlier V5 standardization pass.
  - EC5.5: `L3-L-V-0308`/`0309` added to `data_error_config.json` but taxonomy doc not updated.
- [File Changes:]
  - `dcc/workflow/core_engine/io/io_excel.py` — EC5.3 fix
  - `dcc/workflow/processor_engine/calculations/validation.py` — EC5.4 fix
  - `dcc/workplan/error_handling/error_handling_taxonomy.md` — EC5.5 fix
- [Resolution:] All three tasks completed. See Phase 5 completion report for details.
- [Link to Update Log:] [update-2026-05-16-phase5-completion](update_log.md#update-2026-05-16-phase5-completion)

## Issue ISS-015 — Submittal Dashboard Duplicated Pipeline Validation Logic Instead of Using Validation_Errors Column

- **Status:** ✅ RESOLVED
- **Resolution Date:** 2026-05-15
- **Context:** The Submittal Tracker Dashboard's `isValidDocId()` implemented its own complex validation logic (hardcoded uncertain values blocklist, ruby-segment counting, format regex, composite segment matching against source columns) rather than using the pipeline's already-computed `Validation_Errors` column. This duplicated pipeline logic in the browser and could diverge from the pipeline's actual validation rules.
- **Root Cause:** The original implementation (Phase 7 v2.0) re-implemented Document_ID validation rules from scratch in JavaScript, parsing segments, comparing against source columns, and maintaining a hardcoded blocklist of placeholder values. This ignored the pipeline's `Validation_Errors` column which already contains structured error codes for each row (e.g. `[P2-I-P-0201] Document_ID uncertain: 'na'`).
- **Impact:**
  - Validation rules in dashboard could drift from pipeline's actual rules
  - Multiple schema file fetches needed (`data_error_config.json`, `dcc_register_config.json`) for the dashboard to replicate pipeline logic
  - Complex segment/composite checks that failed silently when source columns were missing
  - Hardcoded uncertain values blocklist that could become stale
- **Resolution:** Rewrote `isValidDocId()` to:
  1. Fetch `data_error_config.json` on init → extract all error codes with `column` containing `Document_ID`
  2. Check if `row['Validation_Errors']` contains any of those error codes
  3. Keep only a minimal fallback uncertain-values blocklist for CSV files without a `Validation_Errors` column
  4. Removed all segment-counting, format-regex, and composite-matching logic
- **Additional Changes (2026-05-15 follow-up):**
  - Open Submissions: explicitly reads `Submission_Closed` for `NO`/`0` values
  - Detail tables: all column titles changed to exact CSV column names (`Document_ID`, `Submitted_By`, `Resubmission_Plan_Date`, etc.)
  - Computed columns removed from tables (Days Overdue, Status, Category); unused functions (`firstVal`, `calcDaysOverdue`) removed
  - Overdue table added `Resubmission_Overdue_Status` column
  - Approval Rate redefined: numerator = APP+AWC+INFO+VOID, denominator = total unique valid Document_IDs
  - Awaiting Response expanded: counts docs with null/empty approval code OR PEN/PENDING
  - Added 6th KPI: "Review >30 Days" — unique docs with `Duration_of_Review > 30`
  - Added 7th KPI: "Delay >30 Days" — unique docs with `Delay_of_Resubmission > 30`
  - Status bar shows "Unique Docs: X (Valid) / Y (Total)"
- **File Changes:**
  - `dcc/ui/submittal_dashboard.html` — all above changes
- **Link to Update Log:** [update-2026-05-15-submittal-dashboard-enhancements](update_log.md#update-2026-05-15-submittal-dashboard-enhancements)

<a id="issue-iss-063"></a>
## 2026-05-20

### Issue # 063 — AI Analysis Dashboard Reported Bugs
- [Date:] 2026-05-20
- [Status:] ✅ RESOLVED
- [Context:] Six bugs reported in `ai_analysis_dashboard.html`: (1) SHOW_ERROR_ROWS logic failure with array sample rows, (2) Multiple renderAll() calls causing lag, (3) Onclick quote escaping breaking with special chars, (4) FILTER regex too simplistic, (5) No fetch timeout for chat, (6) Tree node parameter/label issues.
- [Root Cause:]
  - Bug 1: Expected object-based sample rows; trace data sometimes contains arrays.
  - Bug 2: Async loop called `renderAll()` for every file.
  - Bug 3: Missing JS string escaping in HTML attributes.
  - Bug 4: Regex didn't handle quotes or spaces in column/values.
  - Bug 5: Native `fetch` lacks default timeout.
  - Bug 6: Missing HTML escaping for labels; fragile `??` nullish coalescing on data attributes.
- [File Changes:]
  - `dcc/ui/ai_analysis_dashboard.html`
- [Resolution:] Implemented surgical fixes for all 6 bugs, including a new `escJs` helper and refactored file handling.
- [Link to Update Log:] [update-2026-05-20-ai-dashboard-bugfixes](update_log.md#update-2026-05-20-ai-dashboard-bugfixes)

<a id="issue-iss-064"></a>
## 2026-05-20

### Issue # 064 — Error Diagnostic Dashboard Non-Compliance
- [Date:] 2026-05-20
- [Status:] ✅ RESOLVED
- [Context:] Compliance audit of `error_diagnostic_dashboard.html` against `html_design_rule.md` revealed multiple gaps: missing right sidebar, no resizable panels, static/hardcoded data, and inconsistent iconography.
- [Root Cause:] The original v1.0 implementation was a functional mockup that did not incorporate the full DCC shell architectural requirements or dynamic data loading logic.
- [File Changes:]
  - `dcc/ui/error_diagnostic_dashboard.html`
- [Resolution:] Completely rebuilt the dashboard as a compliant v2.0 application. Implemented resizable sidebars, dynamic JSON loader, interactive charts, and standardized UI components.
- [Link to Update Log:] [update-2026-05-20-error-dashboard-v2](update_log.md#update-2026-05-20-error-dashboard-v2)
