# Section 1. Rules to update this log
1. Always log changes immediately after the change is made.
2. Add a time stamp at the beginning of the log entry
3. Summarize the changes made in the log entry, what was changed, why it was changed, and what was the impact of the change. This will help to analysis changes, such as potential conflicts, any new issues, and any improvements that can be made.
4. Try to make summary as concise as possible, but still capture all the important information.
5. Provide HTML `<a>` tag with `id="issue-number"` at the beginning of the log entry if the change is related to an issue.

# Section 2. Log entries

<a id="issue-16"></a>
## 2026-04-12 13:30:00
1. Schema update (Phase 1): [dcc_register_enhanced.json](../config/schemas/dcc_register_enhanced.json) - Added new column `Document_ID_Affixes` immediately after `Document_ID`.
2. Column configuration:
   - `data_type`: `string`
   - `is_calculated`: `true` with calculation type `extract_affixes`
   - `processing_phase`: `P2.5` (same as Document_ID validation)
   - `null_handling`: `default_value` with empty string `""` as default
3. Added `Document_ID_Affixes` to `column_sequence` array immediately after `Document_ID`.
4. Purpose: Store affixes/suffixes (e.g., `_ST607`, `_Withdrawn`, `-V1`) extracted from Document_ID before validation.
5. Enables Phase 2.5 validation to strip affixes before pattern matching, preventing P2-I-V-0204 false positives.
6. Related to [Issue #16](issue_log.md#issue-16): Document_ID affix handling.
7. See [document_id_handling_workplan.md](../workplan/document_id_handling/document_id_handling_workplan.md) for full implementation plan.

## 2026-04-12 13:40:00
1. Logic implementation (Phase 2): Created [affix_extractor.py](../workflow/processor_engine/calculations/affix_extractor.py) with core extraction functions.
2. Functions implemented:
   - `extract_document_id_affixes(document_id, delimiter, sequence_length)`: Main extraction with schema-driven parameters
   - `has_affix()`: Check if Document_ID contains affix
   - `strip_affix()`: Remove affix returning base only
   - `extract_affixes_series()`: Vectorized extraction for pandas DataFrames
3. Algorithm:
   - Splits Document_ID by delimiter (from schema, default: "-")
   - Extracts sequence number from last segment (length from schema, default: 4)
   - Remaining chars in last segment = affix
   - Fallback: searches for last separator if not enough segments
4. Schema-driven parameters:
   - `delimiter`: From `Document_ID.validation.derived_pattern.separator` (default: "-")
   - `sequence_length`: From `Document_Sequence_Number.validation.pattern` parsing (default: 4)
5. Returns empty string `""` for affix if none found or invalid Document_ID
6. Handles edge cases: null input, empty strings, no affix, invalid base format
7. Related to [Issue #16](issue_log.md#issue-16): Phase 2 complete.

## 2026-04-12 16:10:00
1. Integration update (Phase 3): [identity.py](../workflow/processor_engine/error_handling/detectors/identity.py) - Modified `_detect_invalid_id_format()` to integrate affix extraction.
2. Changes implemented:
   - Added import for `extract_document_id_affixes` with `HAS_AFFIX_EXTRACTOR` flag for graceful fallback
   - Added `_get_affix_extraction_params()` method to read schema configuration:
     - Extracts `delimiter` from `Document_ID.validation.derived_pattern.separator` (default: "-")
     - Parses `sequence_length` from `Document_Sequence_Number.validation.pattern` like `^[0-9]{4}$` → 4
   - Modified `_detect_invalid_id_format()` workflow:
     - Extracts affix before validation using schema-driven parameters
     - Validates base ID (without affix) against `derived_pattern`
     - Includes affix and base_id in error context for debugging
3. Validation flow with affix handling:
   ```
   Document_ID with affix → Extract (base, affix) → Validate base only → Store affix separately
   ```
4. Error context now includes:
   - `base_id`: Document_ID without affix (what was validated)
   - `affix`: Extracted affix string (e.g., "_ST607", "-V1")
   - `affix_extraction`: "applied" flag
   - `note`: Clarifies validation performed on base ID
5. Prevents P2-I-V-0204 false positives for Document_IDs with valid affixes like `_ST607`, `_Withdrawn`, `-V1`.
6. Schema-driven design ensures automatic adaptation if delimiter or sequence_length changes in schema.
7. Related to [Issue #16](issue_log.md#issue-16): Phase 3 complete.

## 2026-04-12 16:40:00
1. Column calculation update (Phase 4): [validation.py](../workflow/processor_engine/calculations/validation.py) - Modified `derived_pattern` validation to extract and store Document_ID affixes.
2. Changes implemented:
   - Added import for `extract_document_id_affixes` with `HAS_AFFIX_EXTRACTOR` flag for graceful fallback
   - Added helper function `_get_sequence_length_from_schema()` to extract sequence length from schema pattern
   - Modified `derived_pattern` validation block to:
     - Check if affix extraction enabled: Document_ID column with Document_ID_Affixes in DataFrame
     - Extract affixes using `extract_document_id_affixes()` with schema-driven parameters
     - Store extracted affixes in `Document_ID_Affixes` column
     - Validate base ID (without affix) against `derived_pattern` regex
     - Cleanup temp columns after validation
   - Enhanced error logging includes sample bases and affixes for debugging failed validations
3. Affix extraction flow:
   ```
   Document_ID values → Extract affixes (base, affix) → Store affixes in column → Validate bases
   ```
4. Integration with schema:
   - `delimiter` from `Document_ID.validation.derived_pattern.separator`
   - `sequence_length` from `Document_Sequence_Number.validation.pattern` parsing
5. Related to [Issue #16](issue_log.md#issue-16): Phase 4 complete.

<a id="2026-04-12-164500"></a>
## 2026-04-12 16:45:00
1. Bug fix: Pipeline error when processing `Document_ID_Affixes` column
2. Problems identified and fixed:
   - **Error 1**: `'recalculate_always' is not a valid PreservationMode`
     - Root cause: Schema used invalid value `recalculate_always`
     - Fix: Changed to valid `overwrite_existing` in `dcc_register_enhanced.json`
   - **Error 2**: `WARNING: No handler registered for calculation type: extract_affixes/extract_document_id_affixes`
     - Root cause: Missing calculation handler in `registry.py`
     - Fix: Added `apply_extract_affixes()` function to `composite.py`
     - Fix: Registered handler under `CALCULATION_HANDLERS["extract_affixes"]` in `registry.py`
3. Changes made:
   - [dcc_register_enhanced.json](../config/schemas/dcc_register_enhanced.json): Fixed `Document_ID_Affixes.strategy.data_preservation.mode` from `recalculate_always` to `overwrite_existing`
   - [composite.py](../workflow/processor_engine/calculations/composite.py): Added `apply_extract_affixes()` function for affix extraction in Phase 2.5
   - [registry.py](../workflow/processor_engine/core/registry.py): Added `extract_affixes` calculation handler
4. Pipeline now successfully:
   - Extracts affixes from Document_ID in Phase 2.5
   - Stores affixes in Document_ID_Affixes column
   - Validates base Document_ID (without affix) in Phase 4
5. Related to [Issue #16](issue_log.md#issue-16): Pipeline bug fix complete.

<a id="issue-10"></a>
## 2026-04-12 18:30:00
1. Code fix: Fixed DataFrame sorting operations in `aggregate.py` to prevent index misalignment.
2. Problems identified: `concatenate_unique`, `concatenate_unique_quoted`, and `concatenate_dates` methods were sorting the original DataFrame without using `.copy()` or reindexing results back to original index.
3. Changes made:
   - [aggregate.py](../workflow/processor_engine/calculations/aggregate.py):
     - `concatenate_unique` (line 91-135): Added `.copy()` to `df.sort_values(sort_by)` and `calculated.reindex(df.index)`
     - `concatenate_unique_quoted` (line 137-175): Same fixes applied
     - `concatenate_dates` (line 177-200): Same fixes applied
4. Impact: Original DataFrame row order is now preserved throughout all calculations. Calculated values are properly aligned with original row indices, enabling reliable null handling error detection.
5. Related to [Issue #10](issue_log.md#issue-10): Sorting operations analysis and fixes complete.

## 2026-04-12 11:10:00
1. Schema update: [dcc_register_enhanced.json](../config/schemas/dcc_register_enhanced.json) - Added `strategy.validation_context` to `Transmittal_Number` column with `is_fact_attribute: true` and `skip_duplicate_check: true`.
2. This configuration informs the duplicate detection logic in `identity.py` to skip P2-I-V-0203 validation for fact tables where one transmittal can legitimately contain multiple documents.
3. The `consistency_group` setting ensures consistency checks apply only when value is not NA/null.
4. Related to [Issue #13](issue_log.md#issue-13): Duplicate transmittal_number in fact tables is not an error.
5. Test verified: [test_log.md](test_log.md#2026-04-12-111500) - No P2-I-V-0203 errors found with 77 rows of test data.

## 2026-04-12 11:25:00
1. Code fix: [identity.py](../workflow/processor_engine/error_handling/detectors/identity.py) - Updated `_detect_duplicate_transmittal()` to check `strategy.validation_context.skip_duplicate_check` from schema before detecting duplicates.
2. Code fix: [engine.py](../workflow/processor_engine/core/engine.py) - Updated all phase detection calls to pass `schema_data` in context, enabling detectors to access schema configuration.
3. Verification: Pipeline run with 11,099 rows confirmed 0 P2-I-V-0203 errors in output file.
4. Log confirmation: "Skipping duplicate check for Transmittal_Number (skip_duplicate_check: true in schema strategy)" message observed.

<a id="issue-14"></a>
## 2026-04-12 12:30:00
1. Code fix: [dcc_engine_pipeline.py](../workflow/dcc_engine_pipeline.py) - Moved module-level `print()` statements into `main()` function to prevent execution on import.
2. Code fix: [logger.py](../workflow/processor_engine/error_handling/core/logger.py) - Changed console handler from JSON formatter to simple `[LEVEL] message` format for readable output.
3. Code fix: [logger.py](../workflow/processor_engine/error_handling/core/logger.py) - Set console handler level to WARNING+ and added `propagate = False` to eliminate duplicate log entries.
4. Result: Clean pipeline output with structured status messages instead of mixed JSON/print chaos.
5. Related to [Issue #14](issue_log.md#issue-14): Pipeline output cleanup for better user experience.

<a id="issue-15"></a>
## 2026-04-12 12:45:00
1. Code fix: [identity.py](../workflow/processor_engine/error_handling/detectors/identity.py) - Updated `DOC_ID_PATTERN` to align with discipline schema.
2. Pattern change: Document_Type segment changed from `[A-Z]{2,10}` to `[A-Z0-9]{1,10}` (allows 1-10 alphanumeric).
3. Pattern change: Discipline segment changed from `[A-Z]{2,10}` to `[A-Z0-9]{1,10}` (allows 1-10 alphanumeric).
4. Reason: Discipline schema allows codes like "A", "B", "C", "D", "P" (1-3 chars per `^[A-Z0-9]{1,3}$`).
5. Impact: Document_IDs like '131242-WSD11-CL-P-0009' no longer incorrectly trigger P2-I-V-0204 errors.
6. Verification: Tested pattern against sample Document_IDs - '131242-WSD11-CL-P-0009' now passes validation.
7. Related to [Issue #15](issue_log.md#issue-15): P2-I-V-0204 false positives for valid single-letter discipline codes.

## 2026-04-12 12:48:00
1. Refactoring: [validation.py](../workflow/processor_engine/calculations/validation.py) - Created public function `get_derived_pattern_regex()` for reuse by both Phase 2 and Phase 4.
2. Refactoring: [identity.py](../workflow/processor_engine/error_handling/detectors/identity.py) - Added `_get_schema_pattern()` method to use schema-driven `derived_pattern` instead of hardcoded regex.
3. Implementation: Phase 2 (identity detector) now calls same `get_derived_pattern_regex()` function as Phase 4 (schema validation).
4. Fallback: Hardcoded pattern retained for backward compatibility when schema context not available.
5. Result: Both phases now use identical pattern generation logic from `dcc_register_enhanced.json` schema configuration.
6. Related to [Issue #15](issue_log.md#issue-15): Ensures consistency between Phase 2 identity detection and Phase 4 schema validation.

## 2026-04-12 00:00:00
1. Schema update: Modified {} dcc_register_enhanced.json to change the validation of Document_ID from a fixed regex to a dynamic regex based on the document type. derive_pattern is now used to generate the regex based on source columns.
2. Logic update: validation.py to handel the derived_pattern rule type. Implemented a helper function _get_derived_pattern() to generate the regex based on source columns dynamically.
3. This approach provides a single source of truth which will follow changes dynamically from schema definition. This will help to reduce the maintenance effort and improve the maintainability of the code.

## 2026-04-12 00:00:00
<a id="issue-4"></a>
1. Logic update: [dateframe.py](../workflow/processor_engine/utils/dateframe.py) to ensure `is_calculated` columns are initialized with `None` instead of `"NA"` default. This fixes the bug where `Row_Index` calculation was being skipped.
2. Logic update: [validation.py](../workflow/processor_engine/calculations/validation.py) to integrate structured error codes (e.g., `[P-V-V-0501]`) from the error catalog into row-level validation messages. Improving automated error tracking.
3. Schema & Logic update: Moved `Row_Index` strategy into [dcc_register_enhanced.json](../config/schemas/dcc_register_enhanced.json) and removed hardcoded overrides in [calculation_strategy.py](../workflow/processor_engine/core/calculation_strategy.py). System is now fully schema-driven for this column.

<a id="issue-5-row-alignment"></a>
## 2026-04-12 12:00:00
1. Logic update: [aggregate.py](../workflow/processor_engine/calculations/aggregate.py) - Fixed critical index misalignment bugs in `latest_by_date` and `latest_non_pending_status` handlers by restoring original indices after merge operations.
2. Replaced positional assignment (`.values`) with index-aware assignment, ensuring data integrity during multi-column grouping.
3. This fix resolves the reported issue where Row 7 was incorrectly inheriting data from Row 8.
<a id="issue-3-phase-4"></a>
## 2026-04-12 15:00:00
1. Logic update: [aggregator.py](../workflow/processor_engine/error_handling/aggregator.py) & [formatter.py](../workflow/processor_engine/error_handling/formatter.py) - Implemented Phase 4 of the Error Handling Module. Added centralized row-level error aggregation and localized formatting.
2. Logic update: [engine.py](../workflow/processor_engine/core/engine.py) - Integrated `BusinessDetector` and `ErrorAggregator` into the phased processing pipeline. The engine now detects errors after each phase (P1-P3) and populates the `Validation_Errors` column using the aggregator.
3. Localization update: [zh.json](../workflow/processor_engine/error_handling/config/messages/zh.json) - Added comprehensive Chinese support for all 24+ error codes, enabling multi-language diagnostic reports.
4. Logic update: [approval.py](../workflow/processor_engine/error_handling/resolution/approval.py) - Implemented Layer 4 Approval Hook for manual error overrides and audit tracking.
5. This update completes Phase 4 of the Workplan, providing the infrastructure needed for structured error reporting and manual intervention in the pipeline.
<a id="issue-3-phase-5"></a>
## 2026-04-12 21:30:00
1. Analytics update: [data_health.py](../workflow/reporting_engine/data_health.py) - Implemented Metric Aggregator for Phase 5. Added weighted health scoring (0-100%) and letter grading (A-F).
2. Reporting update: [error_reporter.py](../workflow/reporting_engine/error_reporter.py) - Implemented JSON diagnostic telemetry export. Added `export_dashboard_json()` to support UI-based diagnostics. [summary.py](../workflow/reporting_engine/summary.py) now includes health KPIs in text reports.
3. UI update: [error_diagnostic_dashboard.html](../ui/error_diagnostic_dashboard.html) & [log_explorer_pro.html](../ui/log_explorer_pro.html) - Created premium interactive tools for data health visualization and log analysis.
4. Pipeline update: [dcc_engine_pipeline.py](../workflow/dcc_engine_pipeline.py) - Integrated automatic dashboard JSON export and health KPI generation.
5. This update completes the Error Handling Module (Phase 5), providing a complete 6-layer validation, analytics, and visualization suite for document processing.

## 2026-04-11 16:35:00
1. Logic update: [identity.py](../workflow/processor_engine/error_handling/detectors/identity.py) - Updated `detect()` method to filter validations based on `required_identities` list.
2. Logic update: [business.py](../workflow/processor_engine/error_handling/detectors/business.py) - Reconfigured `BusinessDetector` to split identity validation. `Document_Revision`, `Document_Title`, and `Transmittal_Number` are now validated in Phase 2, while `Document_ID` is validated in Phase 2.5.
3. Fixed Issue #12: This prevents `Document_ID uncertain (P2-I-P-0201)` false positives from being reported in Phase 2 before the `Document_ID` has been calculated via the composite strategy.
