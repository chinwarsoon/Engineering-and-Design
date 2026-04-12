# Section 1. Rule for updating issue log:
1. Always log new issues immediately after the issue is identified.
2. Add a time stamp at the beginning of the log entry.
3. Summarize the issue identified either from existing code or changes applied to the code. This will help to analysis issues, such as potential conflicts, any new issues, and any improvements that can be made.
4. when future updates are made to resolve the issue, update the log entry to update thes status of the issue and any other relevant information.
5. Link the issue log to the change log for what have been done to resolve the issue.

# Section 2. Log entries   

## 2026-04-12 00:00:00
[Issue # 1]: to consider a recursive schema loader for all schemas. Instead of writing custom code every time adding a new sub-schema, to create a loader that "walks" through all JSON schema files and automatically pulls in any file referenced by a $ref key. This will help to reduce the maintenance effort and improve the maintainability of the code.
- `[Status]`: Open
- `[Link to changes in update_log.md]`:

## 2026-04-12 00:00:00
[Issue # 2]: For preserve esixting data per certain conditions, the current implementation is to add a new rule in the schema. This approach is not scalable and maintainable. To consider a more scalable and maintainable approach. 
- `[Status]`: Open
- `[Link to changes in update_log.md]`:

## 2026-04-12 12:00:00
[Issue # 3]: Validation failures (like Document_ID mismatches) are recorded in the 'Validation_Errors' column and logged as warnings, but the reporting_engine does not aggregate or report these per-row errors in the final summary report. This leads to "silent" failures where data is exported successfully despite validation issues.
- `[Status]`: Resolved (Phase 4 & 5 Complete)
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-3-phase-5)

## 2026-04-12 12:00:00
[Issue # 4]: Row_Index is incorrectly initialized with "NA" during the initiation phase, causing the calculation engine to skip its generation due to the preserve_existing strategy.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-4)

## 2026-04-12 12:00:00
[Issue # 5]: Row Alignment Discrepancy in Aggregate Calculations. Data from late rows (e.g., row 8) was occasionally assigned to early rows (e.g., row 7) due to index reset and positional assignment (`.values`) in `Latest-Non-Pending-Status` and missing index restoration in `Latest-By-Date` handlers.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-5-row-alignment)

## 2026-04-11 14:30:00
[Issue # 7]: `aggregate/concatenate_unique` (and related) calculation handler in `aggregate.py` only supports `source_column` (singular), while the enhanced schema for `All_Approval_Code` uses `source_columns` (plural), causing the calculation to be skipped.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-11-150000)

## 2026-04-11 14:30:00
[Issue # 8]: Missing calculation handler for `error_tracking/aggregate_row_errors`. The `Validation_Errors` column is not being populated with the aggregated error messages because the handler is not registered in `registry.py`.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-11-150000)

## 2026-04-11 14:30:00
[Issue # 9]: `Document_ID` format validation (P2-I-V-0204) fails for values like `131242-WST00-PP-PM-0001-0` because the expected pattern `PROJECT-FACILITY-TYPE-SEQUENCE` does not account for the optional revision suffix (e.g., `-0`) found in the source data.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-11-150000)

## 2026-04-11 15:45:00
[Issue # 11]: Incorrect null reporting in `error_dashboard_data.json` for `First_Submission_Date` and `Document_Sequence_Number`. These were being flagged as CRITICAL null errors in Phase 1 (AnchorDetector) because they were mistakenly included in the `ANCHOR_COLUMNS` list, despite being calculated or populated in later phases.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-11-155000)

## 2026-04-11 16:30:00
[Issue # 12]: `Document_ID uncertain (P2-I-P-0201)` errors reported prematurely in Phase 2. `Document_ID` is a P2.5 calculated column in the enhanced schema, but `IdentityDetector` was validating it during Phase 2 before the calculation was performed.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-11-163500)

## 2026-04-11 16:35:00
[Issue # 13]: Error code P2-I-V-0203 (Duplicate Transmittal_Number) should not apply to fact tables.

**Analysis:**
- The data from `dcc_engine_pipeline.py` is a fact table structure
- In fact tables, `transmittal_number` can legitimately be duplicated across multiple rows
- This occurs when one transmittal contains multiple documents (1 transmittal → N documents)
- Error P2-I-V-0203 is designed for transactional data where transmittal_number should be unique per submission
- **Conclusion:** Duplicate transmittal_number in the final data table is NOT an error for fact table data

**Resolution:**
- Schema configuration added to skip duplicate validation for fact table attributes.
- Code fix: `identity.py` `_detect_duplicate_transmittal()` now checks `strategy.validation_context.skip_duplicate_check` before flagging duplicates.
- Code fix: `engine.py` now passes `schema_data` in context to all phase detectors.
- See [update_log.md](update_log.md#issue-13) for detailed changes.

**Note:** This is a business logic clarification, not a code bug. The validation rule is context-dependent.
 - `[Status]`: Resolved (Schema Configuration + Tested)
 - `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-13)
 - `[Link to test results]`: [test_log.md](test_log.md#2026-04-12-111500)

## 2026-04-12 12:30:00
[Issue # 14]: Pipeline output is messy with mixed JSON logs and print statements causing unreadable console output.

**Analysis:**
- Module-level `print()` statements in `dcc_engine_pipeline.py` executed on import, not just on run
- `StructuredLogger` using JSON formatter outputting to stdout, creating mixed format output
- Logger propagation causing duplicate messages
- Console overwhelmed with unstructured debug logs

**Resolution:**
- Moved pipeline banner prints from module level into `main()` function
- Changed `logger.py` to use simple `[LEVEL] message` formatter instead of JSON
- Set console handler to WARNING+ only to reduce noise
- Added `propagate = False` to prevent duplicate log entries
- See [update_log.md](update_log.md#issue-14) for detailed changes.

**Note:** This is a code quality improvement for better user experience.
 - `[Status]`: Resolved (Code Quality)
 - `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-14)

## 2026-04-12 12:45:00
[Issue # 15]: "[P2-I-V-0204] Invalid Document_ID format: '131242-WSD11-CL-P-0009' (Document_ID)" are reported as errors but they are not.

**Analysis:**
- Document_ID '131242-WSD11-CL-P-0009' was flagged as invalid by P2-I-V-0204
- The `identity.py` detector uses hardcoded `DOC_ID_PATTERN` requiring 2-10 uppercase letters for discipline: `[A-Z]{2,10}`
- Discipline schema allows 1-3 alphanumeric characters per pattern `^[A-Z0-9]{1,3}$`
- Valid discipline codes include single letters: "A", "B", "C", "D", "P" (from discipline_schema.json)
- The discipline "P" in the example is valid per schema but rejected by the detector's pattern

**Resolution:**
- Initial fix: Updated `identity.py` `DOC_ID_PATTERN` to allow 1-10 alphanumeric characters for Document_Type and Discipline segments
- Refactoring: Created shared `get_derived_pattern_regex()` function in `validation.py` for both Phase 2 and Phase 4
- Phase 2 (identity detector) now uses schema-driven `derived_pattern` from `dcc_register_enhanced.json` via `_get_schema_pattern()`
- Hardcoded pattern retained as fallback for backward compatibility
- Both phases now use identical pattern generation logic from schema configuration
- See [update_log.md](update_log.md#issue-15) for detailed changes.

**Note:** This is a pattern alignment fix to make the detector consistent with the schema.
 - `[Status]`: Resolved (Pattern Alignment)
 - `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-15)

 ## 2026-04-12 12:55:00
[Issue # 16]: "Document_ID" sometimes may contain affixes like "_ST607", "_ST608_BCA", "_MS2", "_Withdrawn" etc. When document_id contains these affixes, the detector should still be able to validate the document_id. May consider to strip these affixes before validation. Separate the affixes from the document_id and store in another new data field.

**Note:** This is a pattern alignment fix to make the detector consistent with the schema.
 - `[Status]`: open
 - `[Link to changes in update_log.md]`:

## 2026-04-12 16:45:00
[Bug Fix]: Pipeline error when processing Document_ID_Affixes column

**Error:**
```
'Recalculate_always' is not a valid PreservationMode
WARNING: No handler registered for calculation type: extract_affixes/extract_document_id_affixes
```

**Analysis:**
- `Document_ID_Affixes` schema configuration used invalid `PreservationMode` value `recalculate_always`
- Valid values are: `preserve_existing`, `overwrite_existing`, `conditional_overwrite`
- Missing calculation handler for `extract_affixes` type in `registry.py`

**Resolution:**
- Fixed schema: Changed `mode` from `recalculate_always` to `overwrite_existing` in `dcc_register_enhanced.json`
- Added `apply_extract_affixes()` function to `composite.py` for affix extraction calculation
- Registered handler in `registry.py` under `CALCULATION_HANDLERS["extract_affixes"]`
- Pipeline now successfully processes affix extraction in Phase 2.5

**Related to:** Issue #16 implementation
 - `[Status]`: Fixed
 - `[Link to changes in update_log.md]`: See update_log.md#2026-04-12-164500
