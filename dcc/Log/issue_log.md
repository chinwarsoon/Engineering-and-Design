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

# Section 2. Pending Issues

## 2026-04-17 21:35:00
[Issue #25]: agent_rule.md path mismatch in project_config.json - validator looking at wrong location.
- `[Status]`: Resolved
- `[Context]`: dcc_engine_pipeline.py failed with "Ready: NO" because validator expects agent_rule.md at dcc/agent_rule.md but file exists at dcc/rule/agent_rule.md.
- `[Root Cause]`: project_config.json lists agent_rule.md as root file without specifying rule/ subdirectory path.
- `[File Changes]`: config/schemas/project_config.json - changed agent_rule.md path from "agent_rule.md" to "rule/agent_rule.md"
- `[Resolution]`: Updated project_config.json root_files entry to specify correct relative path "rule/agent_rule.md". Pipeline now passes validation with "Ready: YES".
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-25)

## 2026-04-12 00:00:00
[Issue # 2]: For preserve existing data per certain conditions, the current implementation is to add a new rule in the schema. This approach is not scalable and maintainable. To consider a more scalable and maintainable approach.
- `[Status]`: Open
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md)

## 2026-04-15 09:40:00
[Issue #17]: tools/project_setup_tools.py should be updated to establish a new project folder, copies all necessary files, and configure schemas.
- `[status]`: Open
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md)

## 2026-04-18 18:00:00
[Issue #23]: Phase 5 — AI Integration & Advanced Analytics planning required. Define scope, deliverables, and implementation workplan for Phase 5 sub-phases (5.1–5.5).
- `[Status]`: Open
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#phase5-planning)

# Section 3. Closed Issues

## 2026-04-17 20:45:00
[Issue #24]: P2-I-V-0204 false positives for valid Document_ID - derived_pattern validation failing for correctly formatted Document_IDs.
- `[Status]`: Resolved
- `[Context]`: Pipeline reported 10496 invalid Document_ID values with sample bases: ['131242-WST00-PP-PM-0001', '131242-WST00-PP-PC-0001', '131242-WSW41-PP-PC-0001']. These follow correct format (PROJECT-FACILITY-TYPE-DISCIPLINE-SEQUENCE) but were flagged as invalid.
- `[Root Cause]`: `_get_column_representative_regex()` function built strict regex pattern using alternation of allowed codes from schema references for Document_Type, Discipline, Facility_Code. If source column contained value not in reference schema, Document_ID failed validation even if format was correct.
- `[Resolution]`: Modified `_get_column_representative_regex()` to use general pattern `[A-Z0-9-]+` for schema reference columns instead of strict alternation. Document_ID now validates based on format while individual columns validated separately by schema_reference_check.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-24)

## 2026-04-17 15:30:00
[Issue #22]: `test_environment()` fails when `workflow/` not in `sys.path` — blocks pipeline startup.
- `[Status]`: Resolved
- `[Context]`: `test_environment()` in `system.py` calls `importlib.import_module()` on engine modules without ensuring `workflow/` in `sys.path`. Engine module failures treated as blocking errors. `dcc.yml` missing `openpyxl` and `jsonschema` dependencies.
- `[Resolution]`: Added `sys.path` insert for `workflow/` at function start. Demoted engine module failures to warnings. Improved failure message with missing package details. Added `openpyxl==3.1.5` and `jsonschema==4.23.0` to `dcc.yml`.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-22)

## 2026-04-17 15:00:00
[Issue #21]: `skip_duplicate_check: true` not respected — P2-I-V-0203 errors still reported after schema migration.
- `[Status]`: Resolved
- `[Context]`: `identity.py` `_detect_duplicate_transmittal()` read config via legacy `enhanced_schema.columns` wrapper. After migration, `columns` at top level → config always empty → skip never applied. Same bug in `_get_schema_pattern()` and `_get_affix_extraction_params()`.
- `[Resolution]`: Fixed all three methods to use `schema_data.get('columns') or schema_data.get('enhanced_schema', {}).get('columns', {})` for backward compatibility.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-21)

## 2026-04-15 23:15:00
[Issue #5]: Schema architecture compliance and optimization - Complete rebuild of JSON schema configuration ecosystem required to comply with agent_rule.md Section 2.
- `[Status]`: Resolved (Phase 1-9 Complete)
- `[Context]`: Required agent_rule.md Section 2.3 compliance (fragment pattern), Unified Schema Registry with URI-based $ref, strict validation, separation of definitions/properties/data, column optimization.
- `[Resolution]`: 9/10 phases completed. 32/32 schema references use Unified Schema Registry. 60% potential schema size reduction. Complete agent_rule.md Section 2.3 compliance. Centralized parameter and column management.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#schema-rebuild-completion)
- `[Workplan Location]`: [rebuild_schema_workplan.md](../workplan/schema_processing/rebuild_schema_workplan.md)

## 2026-04-12 00:00:00
[Issue #1]: Recursive schema loader for all schemas - Create loader that "walks" through JSON schema files and automatically pulls in any file referenced by $ref key to reduce maintenance effort.
- `[Status]`: Resolved (Phases A-E Complete, F Not Required)
- `[Context]`: Multi-level caching (L1/L2/L3) with TTL and mtime validation. Universal $ref resolution (string, object, nested). Strict registration with pattern-based auto-discovery. Unified URI Registry mapping Digital IDs to physical files.
- `[Resolution]`: Phases A-E complete (RefResolver, Dependency Graph, SchemaLoader). Phase F marked NOT REQUIRED (dcc_register schemas provide same functionality). Complete documentation suite (API, Guides, Architecture).
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#recursive-schema-loader-workplan-rebuild)
- `[Workplan Location]`: [recursive_schema_loader_workplan.md](../workplan/schema_processing/recursive_schema_loader_workplan.md)

## 2026-04-17 10:30:00
[Issue #18]: Schema URI and Filename Mismatches - Internal $ref strings used hyphenated names while physical files used underscores, causing resolution failures.
- `[Status]`: Resolved
- `[Resolution]`: Standardized all schema $id and $ref values to use underscore-based naming matching physical file stems.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#schema-uri-standardization)

## 2026-04-17 11:15:00
[Issue #19]: Circular Dependency in project_setup_base - Base schema contained self-referencing definitions triggering `CircularDependencyError` in topological sort.
- `[Status]`: Resolved
- `[Resolution]`: Updated `SchemaDependencyGraph` to explicitly ignore self-references during graph construction, allowing recursive schema definitions while preventing multi-file loops.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#circular-dependency-fix)

## 2026-04-17 12:00:00
[Issue #20]: JSON Syntax Errors in Engine Configuration - Engine schemas contained `...` placeholders, making them invalid JSON and breaking loading pipeline.
- `[Status]`: Resolved
- `[Resolution]`: Cleaned all engine config schemas by removing placeholders and finalizing structures.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#engine-config-cleanup)

## 2026-04-12 12:00:00
[Issue #3]: Validation failures recorded in 'Validation_Errors' column but reporting_engine does not aggregate or report these per-row errors in final summary report, leading to "silent" failures.
- `[Status]`: Resolved (Phase 4 & 5 Complete)
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-3-phase-5)

## 2026-04-12 12:00:00
[Issue #4]: Row_Index incorrectly initialized with "NA" during initiation phase, causing calculation engine to skip generation due to preserve_existing strategy.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-4)

## 2026-04-12 12:00:00
[Issue #5]: Row Alignment Discrepancy in Aggregate Calculations - Data from late rows assigned to early rows due to index reset and positional assignment in aggregate handlers.
- `[Status]`: Resolved
- `[Resolution]`: Concatenate methods now use copy + reindex pattern. Original DataFrame order preserved throughout calculations. Null Handling Phase A-B complete.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-10)

## 2026-04-11 14:30:00
[Issue #7]: `aggregate/concatenate_unique` handler only supports `source_column` (singular), while enhanced schema for `All_Approval_Code` uses `source_columns` (plural).
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-11-150000)

## 2026-04-11 14:30:00
[Issue #8]: Missing calculation handler for `error_tracking/aggregate_row_errors` - `Validation_Errors` column not populated with aggregated error messages.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-11-150000)

## 2026-04-11 14:30:00
[Issue #9]: `Document_ID` format validation (P2-I-V-0204) fails for values with optional revision suffix (e.g., `-0`) not accounted for in expected pattern.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-11-150000)

## 2026-04-11 15:45:00
[Issue #11]: Incorrect null reporting in `error_dashboard_data.json` for `First_Submission_Date` and `Document_Sequence_Number` - flagged as CRITICAL null errors in Phase 1 despite being calculated/populated in later phases.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-11-155000)

## 2026-04-11 16:30:00
[Issue #12]: `Document_ID uncertain (P2-I-P-0201)` errors reported prematurely in Phase 2 - `Document_ID` is P2.5 calculated column but `IdentityDetector` validated during Phase 2 before calculation.
- `[Status]`: Resolved
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-11-163500)

## 2026-04-11 16:35:00
[Issue #13]: Error code P2-I-V-0203 (Duplicate Transmittal_Number) should not apply to fact tables - transmittal_number can legitimately be duplicated (1 transmittal → N documents).
- `[Status]`: Resolved (Schema Configuration + Tested)
- `[Resolution]`: Schema configuration added to skip duplicate validation for fact table attributes. `identity.py` checks `strategy.validation_context.skip_duplicate_check` before flagging duplicates.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-13)
- `[Link to test results]`: [test_log.md](test_log.md#2026-04-12-111500)

## 2026-04-12 12:30:00
[Issue #14]: Pipeline output messy with mixed JSON logs and print statements causing unreadable console output.
- `[Status]`: Resolved (Code Quality)
- `[Resolution]`: Moved pipeline banner prints from module level into `main()`. Changed logger to simple `[LEVEL] message` formatter. Set console handler to WARNING+ only. Added `propagate = False` to prevent duplicates.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-14)

## 2026-04-12 12:45:00
[Issue #15]: Document_ID validation (P2-I-V-0204) fails for valid single-letter discipline codes (e.g., "P") - detector hardcoded pattern requires 2-10 uppercase letters but schema allows 1-3 alphanumeric.
- `[Status]`: Resolved (Pattern Alignment)
- `[Resolution]`: Created shared `get_derived_pattern_regex()` function in `validation.py` for both Phase 2 and Phase 4. Phase 2 now uses schema-driven `derived_pattern` from `dcc_register_enhanced.json`. Hardcoded pattern retained as fallback.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#issue-15)

## 2026-04-12 12:55:00
[Issue #16]: Document_ID may contain affixes like "_ST607", "_ST608_BCA", "_MS2", "_Withdrawn" - detector should strip affixes before validation and store in separate field.
- `[Status]`: Resolved
- `[Resolution]`: Added `Document_ID_Affixes` column to schema. Implemented `extract_document_id_affixes()` function in `affix_extractor.py`. Integrated with identity detector to validate base ID only. Fixed schema `PreservationMode` from `recalculate_always` to `overwrite_existing`. Registered `extract_affixes` handler in `registry.py`.
- `[Link to changes in update_log.md]`: [update_log.md](update_log.md#2026-04-12-164500)