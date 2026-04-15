# Section 1. Rule for updating issue log:
1. Always log new issues immediately after the issue is identified.
2. Add a time stamp at the beginning of the log entry.
3. Summarize the issue identified either from existing code or changes applied to the code. This will help to analysis issues, such as potential conflicts, any new issues, and any improvements that can be made.
4. when future updates are made to resolve the issue, update the log entry to update thes status of the issue and any other relevant information.
5. Link the issue log to the change log for what have been done to resolve the issue.

# Section 2. Log entries   

## 2026-04-12 00:00:00
[Issue # 1]: to consider a recursive schema loader for all schemas. Instead of writing custom code every time adding a new sub-schema, to create a loader that "walks" through all JSON schema files and automatically pulls in any file referenced by a $ref key. This will help to reduce the maintenance effort and improve the maintainability of the code.
- `[Status]`: In Progress (Phase C Complete)
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#unified-schema-registry)
- `[Phase A Report]`: [phase_a_analysis_report.md](../workplan/schema_processing/phase_a_analysis_report.md)
- `[Phase B Module]`: [ref_resolver.py](../../workflow/schema_engine/loader/ref_resolver.py)
- `[Phase C Optimization]`: Completed schema URI refactoring, strict validation (additionalProperties: false), and mandatory property enforcement (required) to prevent partial configuration bugs.
- `[Workplan Location]`: [recursive_schema_loader_workplan.md](../workplan/schema_processing/recursive_schema_loader_workplan.md)
- `[Key Requirements]`:
  - Multi-directory schema discovery (`config/schemas/` + `workflow/processor_engine/error_handling/config/`)
  - Main entry point: `project_setup.json` for drill-down discovery
  - Support JSON Schema standard `$ref` and absolute URI-based resolution
  - Cross-directory `$ref` resolution via internal internal internal protocol
  - Circular reference detection
  - Smart caching with TTL support
- `[Implementation Phases]`: 9 phases (A-I), estimated 26 hours
  - Phase A: Analysis & Design (scanning both directories) - DONE
  - Phase B: RefResolver Module (new `ref_resolver.py`) - DONE
  - Phase C: Schema Registry & Optimization (URI refactoring + strict validation) - DONE
  - Phase D: Dependency Graph Builder (new `dependency_graph.py`)
  - Phase E: SchemaLoader Enhancement (multi-directory support)
  - Phase F: Circular Reference Handling
  - Phase G: Caching & Performance
  - Phase H: Integration & Testing
  - Phase I: Documentation

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

## 2026-04-12 18:00:00
[Issue # 10]: DataFrame Sorting Operations Analysis - Impact on Row Index Tracking for Null Handling Error Detection
- `[Status]`: Analysis Complete - Action Required
- `[Link to changes in update_log.md]`:

**Summary:**
Multiple functions in the DCC pipeline use `DataFrame.sort_values()` operations that occur AFTER null handling phases. This can invalidate row index-based tracking (e.g., fill history), making it impossible to accurately correlate errors with specific rows.

**Affected Functions - Detailed Analysis:**

### 1. `apply_delay_of_resubmission()` (composite.py:174)
**Purpose:** Calculate delay for resubmission by comparing current row with previous submission of same Document_ID
**Input:** 
- `df` (DataFrame): Full dataset
- `doc_id_col` (str): "Document_ID"
- `submission_date_col` (str): "Submission_Date"
- `plan_date_col` (str): "Resubmission_Plan_Date"
**Sort Operation:** `df.sort_values([doc_id_col, submission_date_col])`
**Output:** DataFrame with calculated delay values
**Potential Issues:**
- Sorts by Document_ID then Submission_Date for vectorized calculation
- Original row order is NOT preserved (no index reset or sort restoration)
- Fill history recorded in Phase 2 will have mismatched row indices

### 2. `apply_aggregate_calculation()` - concatenate_unique (aggregate.py:93)
**Purpose:** Concatenate unique values from grouped data in sorted order
**Input:**
- `df` (DataFrame): Full dataset
- `sort_by` (list): User-defined sort columns from schema
- `group_by` (list): Grouping columns
- `source_column` (str): Column to aggregate
**Sort Operation:** `df.sort_values(sort_by)` (conditional on sort_by being defined)
**Output:** DataFrame with concatenated string values
**Potential Issues:**
- Sorts entire DataFrame if `sort_by` is defined in schema
- Used by columns: All_Submission_Sessions, All_Submission_Dates, All_Approval_Code
- Row index alignment may break for subsequent operations

### 3. `apply_aggregate_calculation()` - concatenate_unique_quoted (aggregate.py:133)
**Purpose:** Same as concatenate_unique but with quoted values
**Input:** Same as concatenate_unique
**Sort Operation:** `df.sort_values(sort_by)` (conditional)
**Output:** DataFrame with quoted concatenated strings
**Potential Issues:**
- Same row index concerns as concatenate_unique
- Used by columns requiring quoted unique values

### 4. `apply_aggregate_calculation()` - concatenate_dates (aggregate.py:167)
**Purpose:** Concatenate unique dates in chronological order
**Input:**
- `df` (DataFrame): Full dataset
- `sort_by` (list): Date sort columns
- `group_by` (list): Grouping columns
- `source_column` (str): Date column to aggregate
**Sort Operation:** `df.sort_values(sort_by)` (conditional)
**Output:** DataFrame with formatted date strings
**Potential Issues:**
- Date sorting ensures chronological order but may disrupt row alignment
- Used by: All_Submission_Dates column

### 5. `apply_latest_by_date_calculation()` (aggregate.py:239)
**Purpose:** Find latest value per group based on date column
**Input:**
- `df` (DataFrame): Full dataset
- `sort_by` (list): Date columns for sorting
- `sort_dir` (list): Ascending/descending flags
- `group_by` (list): Grouping columns
- `source_column` (str): Column to find latest value
**Sort Operation:** `filtered_df.sort_values(sort_by, ascending=asc_flags)`
**Output:** DataFrame with latest values applied to null positions
**Potential Issues:**
- Sorts filtered DataFrame (subset) - working on copy, so less risky
- Used by: Latest_Approval_Status, Latest_Submission_Date
- Map back to original index correctly preserves alignment

### 6. `apply_latest_non_pending_status()` - get_latest_non_pending (aggregate.py:350)
**Purpose:** Find latest non-pending status within each group
**Input:**
- `group_df` (DataFrame): Group subset
- `sort_by` (list): Usually ["Submission_Date"]
- `source_column` (str): Status column
- `exclude_values` (list): Values to exclude (e.g., ["Pending"])
**Sort Operation:** `group_df.sort_values(by=sort_by[0], ascending=False)`
**Output:** Single value per group (latest non-pending status)
**Potential Issues:**
- Works on group subset (via groupby().apply()), not full DataFrame
- Sorts each group independently - row indices from original DataFrame preserved
- Used by: Latest_Approval_Status

### 7. `LogicDetector._detect_revision_regression()` (logic.py:144, 435)
**Purpose:** Detect revision number regressions within document sequences
**Input:**
- `group` (DataFrame): Document_ID group subset
- "Submission_Date" column (optional)
**Sort Operation:** `group.sort_values("Submission_Date")` (conditional)
**Output:** Error codes appended to detection results
**Potential Issues:**
- Works on group subset from `df.groupby(id_col)`
- Sorts each document group by submission date
- Original row indices preserved (group is a view/copy of subset)

**Impact Assessment:**

| Function | Sorts Full DF? | Preserves Index? | Risk Level | Phase |
|----------|---------------|------------------|------------|-------|
| apply_delay_of_resubmission | YES | NO | HIGH | P2.5 |
| concatenate_unique | YES (conditional) | NO | MEDIUM | P2.5 |
| concatenate_unique_quoted | YES (conditional) | NO | MEDIUM | P2.5 |
| concatenate_dates | YES (conditional) | NO | MEDIUM | P2.5 |
| latest_by_date | NO (subset) | YES | LOW | P2.5 |
| latest_non_pending | NO (group) | YES | LOW | P2.5 |
| revision_regression | NO (group) | YES | LOW | Detection |

**Root Cause Analysis:**
1. Functions 1-4 sort the FULL DataFrame without preserving/restoring original index order
2. Null handling in Phase 2 uses row indices to track fill operations
3. After sorting in Phase 2.5, row indices no longer correspond to original positions
4. FillDetector in Phase 2.5/4 cannot accurately map fill history to data

**Recommended Solutions:**

**Option 1: Row Key-Based Tracking (RECOMMENDED)**
- Replace integer row indices with compound keys (Document_ID + Submission_Date)
- Resilient to sorting operations
- Implementation: Modify fill_history to store `{'Document_ID': 'xxx', 'Submission_Date': 'yyy', 'row_index': N}`

**Option 2: Preserve Index Through Sorting**
- Add `df.sort_index()` after each sort operation to restore original order
- Risk: May affect calculation results that depend on sorted order

**Option 3: Post-Processing Detection**
- Run FillDetector at Phase 4 after all calculations complete
- Analyze data state rather than tracking operations
- Requires different detection approach

**Option 4: Copy-on-Sort**
- Ensure calculations work on DataFrame copies
- Sort copy, calculate, then merge results back to original
- Higher memory usage but preserves original DataFrame order
- **SELECTED APPROACH** - Implemented for concatenate methods

**Status Update:**
- `[Status]`: RESOLVED (Fixes applied - see [update_log.md](update_log.md#issue-10))
- Concatenate methods now use copy + reindex pattern
- Original DataFrame order preserved throughout calculations
- Null Handling Phase A: Fill History Tracking - COMPLETE ([update_log.md](update_log.md#null-handling-phase-a))
- Null Handling Phase B: FillDetector Enhancement - COMPLETE ([update_log.md](update_log.md#null-handling-phase-b))

**Next Steps:**
- [ ] Optimize `latest_by_date` to use `max()` instead of sort (optional)
- [ ] Add integration tests with sorting scenarios
- [ ] Update technical documentation

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

## 2026-04-15 09:40:00
[issue #17] tools/project_setup_tools.py should be updated to establish a new project folder, copies all necessary files, and configure schemas

- `[status]`: open
- `[Link to changes in update_log.md]`: 