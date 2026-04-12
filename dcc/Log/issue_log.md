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
[Issue # 13]: Error code 0203 for duplicate transmittal_number should not apply since tranmittal_number can be duplicate in dimensional tables.
 - `[Status]`: open
 - `[Link to changes in update_log.md]`: