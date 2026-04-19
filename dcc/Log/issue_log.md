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
