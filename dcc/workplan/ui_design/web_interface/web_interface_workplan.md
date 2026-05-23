# Web Interface Workplan — Universal UI Toolkit

**Document ID:** WP-UI-001  
**Current Version:** 3.18  
**Status:** ✅ PHASE 2 v3.1 & PHASE 7 v2.2 COMPLETE  
**Last Updated:** 2026-05-23  
**Lead:** Franklin Song

---

## Revision Control & Version History

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 1.0 | 2026-04-18 | Franklin Song | Initial workplan — 8 UI tools + design system delivered. |
| 2.0 | 2026-05-13 | Franklin Song | Restructured as independent workplan. Each HTML deliverable now a standalone phase (Phases 1–9). Removed external phase identity. |
| 3.0 | 2026-05-14 | Franklin Song | Phase 2 revision: Pipeline Dashboard updated from static mockup to live data-driven dashboard. Added 8 sub-tasks (data loader, dynamic KPIs, real pipeline stages, wired buttons, dynamic status bar, activity log, fixed theme dots). |
| 3.1 | 2026-05-15 | System | Phase 7 audit: Submittal Tracker Dashboard found to be entirely static mockup with hardcoded data. No fetch/FileReader, no KPI tiles, no dynamic filters. Added v2.0 revision scope with 12 sub-tasks to wire to real CSV data, mirroring Phase 2 revision pattern. |
| 3.2 | 2026-05-15 | System | Phase 7 revision implemented: full VS Code layout, CSV loader (fetch+FileReader), 4 KPI tiles, 4 data-driven charts, overdue sortable table, dynamic filters, status bar, right sidebar help panel, layout toggle, resizable panels, icon bar wired. |
| 3.3 | 2026-05-15 | System | Phase 7 v2.1: Added 5th KPI card "Awaiting Response". Replaced complex client-side validation with schema-driven approach using `Validation_Errors` column + `data_error_config.json`. Pre-filter invalid Document_IDs at load time. |
| 3.4 | 2026-05-15 | System | Phase 7 v2.1 follow-up: KPI logic fixes (Open Submissions, Approval Rate, Awaiting Response). Added Review >30 Days and Delay >30 Days KPIs. Detail table columns aligned to CSV headers. Status bar shows unique doc counts. JS syntax bug fix. |
| 3.5 | 2026-05-16 | System | Phase 7 v2.2 proposed: 8 issues identified via code review — overdue table dedup+sort, delay table max aggregation, awaiting table latest-row resolution, schema-driven approval codes, trend chart doc-level consistency, open/awaiting tables missing plan date and delay columns, fragile positional KPI click handler. Workplan updated for approval. |
| 3.6 | 2026-05-19 | System | Phase 10 proposed: AI Analysis Dashboard v1.0 — full DCC shell compliance, data loader for ai_insight_summary/trace/report, KPI tiles, risk cards with evidence drill-down, trends & recommendations panels, markdown report viewer, export to CSV. |
| 3.7 | 2026-05-19 | System | Phase 10 v1.1: Added sub-task 10.14 — local Ollama/Llama3 chat assistant. Users can ask natural-language questions about issues in AI insight files when a local Ollama instance is available. Workplan updated for approval. |
| 3.8 | 2026-05-19 | System | Phase 10 v1.2–v1.5: Full implementation. Ollama API changed from `/api/generate` to `/api/chat` with model detection from `/api/tags`. Added model selector dropdown, markdown chat rendering, data table tab (xlsx 11,822 rows via SheetJS), FILTER: command for in-memory pipeline data querying, schema-driven AI prompts from `data_error_config.json`, risk card→chat pre-fill, multi-line textarea with auto-grow, drag-resizable input row. Status updated to COMPLETED. |
| 3.9 | 2026-05-20 | System | Phase 4 v2.0: Full DCC shell compliance audit completed. All 9 sub-tasks (4.1–4.9) implemented. 8 bugs identified and documented. Compliance audit updated to reflect actual code state. Workplan updated for approval. |
| 3.10 | 2026-05-20 | System | Phase 4 v2.1 proposed: `debug_log.json` integration — pipeline trace panel, filter-driven debug log correlation, trace-enriched error detail table, 4 bug fixes from v2.0 audit. Workplan updated for approval. |
| 3.11 | 2026-05-20 | System | Phase 4 v2.1 revised: Corrected data source analysis — `debug_log.json["errors"]` contains 4,601 row-level errors (not process-level only). Added message parsing sub-task (4.11) to extract code/row/column via regex. Error detail table replaced with full debug log data (4,601 vs 50 capped). Added data source toggle (4.16). 7 sub-tasks total. |
| 3.12 | 2026-05-20 | System | Phase 4 v2.1 implemented: All 7 sub-tasks (4.10–4.16) completed. Added debug_log.json loader, regex message parser, full error table with pagination, debug context correlation, pipeline trace panel, data source toggle, and 4 bug fixes (XSS, phase filter, CSS resize, PascalCase). |
| 3.13 | 2026-05-21 | System | Phase 4 v2.2 proposed: Convert `context` and `message` fields in `debug_log.json` from flat strings to structured JSON objects. Python-side changes (tasks 4.17–4.19) moved to Error Handling Integration workplan Phase 1.5. UI-side changes (tasks 4.20–4.22) remain here. Workplan updated for approval. |
| 3.14 | 2026-05-21 | System | Phase 4 v2.2 implemented: All 3 UI sub-tasks (4.20–4.22) completed. `parseDebugErrors()` reads structured fields directly with legacy regex fallback. `renderDebugContext()` and `renderPipelineTrace()` handle structured `message` and `context` dicts. Backward compatible with legacy string-format `debug_log.json` files. |
| 3.15 | 2026-05-21 | System | Phase 4 v2.3 implemented: Filter dropdowns (`errorCodeFilter`, `columnFilter`) now populated from `error_dashboard_data.json` when available, falling back to `debug_log.json` parsed errors only when dashboard data is missing. Eliminates race condition from parallel loaders. |
| 3.16 | 2026-05-21 | System | Phase 4 v2.4 implemented: Standalone `file://` protocol support via folder picker (`webkitdirectory`). Dashboard prompts user to select the output folder, automatically finds and loads `error_dashboard_data.json` and `debug_log.json`. Drop zone now processes all dropped files (not just first). |
| 3.17 | 2026-05-23 | System | Phase 2 v3.1 proposed: Functional "Run" button integration. Proposed wiring the "Run" button to the backend `POST /api/v1/pipeline/run` endpoint using the `UIRequest` schema. Added task for backend status polling, dynamic UI feedback, and a live output console popup. |
| 3.18 | 2026-05-23 | System | Phase 2 v3.1 implemented: All 5 sub-tasks (2.10–2.14) completed. `triggerPipelineRun()` sends POST to `/api/v1/pipeline/run`. Status polling every 2s via `/api/v1/pipeline/status`. Execution lock (disabled button + spinner). Auto-refresh on completion via `loadAllData()`. Live output console modal with clear/close controls. `file://` protocol guard disables Run button with tooltip. Phase 7 v2.2 implemented: All 7 sub-tasks (7.25–7.31) completed. Overdue table dedup+date sort, delay table max aggregation, awaiting table latest-row resolution, schema-driven approval codes from `approval_code_schema.json`, trend chart doc-level consistency, open/awaiting tables enriched with plan date and delay, KPI click handler `data-kpi` attribute dispatch. |

---

## 1. Objective

Build a cohesive suite of browser-based tools under `dcc/ui/` for data visualization, schema management, pipeline monitoring, and AI-assisted analysis. All tools share a unified design system to ensure a consistent professional experience. The tools consume processed pipeline outputs (CSV, Excel, JSON), schema files, and log data, providing interactive interfaces for end users without requiring a server.

---

## 2. Scope Summary

| ID | Detail | Category | Status |
| :--- | :--- | :--- | :--- |
| 1 | DCC UI Design System — shared CSS with 5 themes, 25+ components | Foundation | ✅ Completed |
| 2 | Pipeline Dashboard — run status, KPIs, output links | Monitoring | ✅ Phase 2 v3.1 Completed |
| 3 | Excel Explorer Pro — data loading, filtering, validation highlighting | Exploration | ✅ Completed |
| 4 | Error Diagnostic Dashboard — error viz, heatmap, drill-down, debug log integration, structured JSON context/message, filter priority, standalone file:// support | Diagnostics | ✅ v2.4 Completed |
| 5 | Schema Manager — browse, inspect, edit schema files | Management | ✅ Completed |
| 6 | Log Explorer Pro — multi-format log browser with search | Logging | ✅ Completed |
| 7 | Submittal Tracker Dashboard — analytics KPI, charts, overdue tracking, awaiting response, schema-driven validation | Analytics | ✅ v2.2 Completed |
| 8 | Common JSON Tools — tree viewer, formatter, JSONPath, validation | Utilities | ✅ Completed |
| 9 | Excel → Schema Generator — auto-generate schema from Excel headers | Generation | ✅ Completed |
| 10 | AI Analysis Dashboard — risk findings, evidence trace, trends, recommendations, markdown report viewer, data table, Ollama chat assistant | Analytics | ✅ Completed |

---

## 3. Index of Content

1. [Objective](#1-objective)
2. [Scope Summary](#2-scope-summary)
3. [Dependencies & Alignment](#4-dependencies--alignment)
4. [Implementation Phases](#5-implementation-phases)
   - [Phase 1: Design System](#phase-1-design-system)
   - [Phase 2: Pipeline Dashboard](#phase-2-pipeline-dashboard)
   - [Phase 3: Excel Explorer Pro](#phase-3-excel-explorer-pro)
   - [Phase 4: Error Diagnostic Dashboard](#phase-4-error-diagnostic-dashboard)
   - [Phase 5: Schema Manager](#phase-5-schema-manager)
   - [Phase 6: Log Explorer Pro](#phase-6-log-explorer-pro)
   - [Phase 7: Submittal Tracker Dashboard](#phase-7-submittal-tracker-dashboard)
   - [Phase 8: Common JSON Tools](#phase-8-common-json-tools)
    - [Phase 9: Excel → Schema Generator](#phase-9-excel--schema-generator)
    - [Phase 10: AI Analysis Dashboard](#phase-10-ai-analysis-dashboard)
5. [Delivery Sequence](#6-delivery-sequence)
6. [Success Criteria](#7-success-criteria)
7. [Risks & Mitigation](#8-risks--mitigation)
8. [Known Limitations & Future Issues](#9-known-limitations--future-issues)
9. [References](#10-references)

---

## 4. Dependencies & Alignment

### Dependencies

| Dependency | Source | Relationship |
| :--- | :--- | :--- |
| Pipeline Engine Outputs | `dcc/output/error_dashboard_data.json`, `dcc/output/processing_summary.txt`, `dcc/output/processed_dcc_universal.csv` | UI tools depend on pipeline output files for data display |
| Schema Registry | `config/dcc_register_enhanced.json`, `config/schemas/*.json` | Schema Manager and other tools consume schema files for validation and display |
| Log Files | `dcc/Log/debug_log.json`, `dcc/Log/issue_log.md`, `dcc/Log/update_log.md`, `dcc/Log/test_log.md` | Log Explorer renders these directly |

### Architecture Alignment

- All tools are self-contained single HTML files (no server required, no build step)
- Tools load data via FileReader API (local files) or `fetch` (remote data)
- Design system is a single shared CSS file (`dcc-design-system.css`) imported by all tools
- Consistent with `agent_rule.md` Section 8 (workplan) and Section 9 (report) requirements
- Follows the modular, schema-driven architecture of the DCC project
- UI tools are read-only consumers of pipeline outputs — no write-back to pipeline data

---

## 5. Implementation Phases

### Phase 1: Design System

**Timeline:** Days 1–2  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/dcc-design-system.css` (1,247 lines)

#### What Was Created

A shared CSS design system that all 8 UI tools import. Based on a VS Code-inspired layout with 5 color themes.

**DCC UI Design System v1.0:**

```css
/* Fonts */
--font-ui:   'Inter', sans-serif;
--font-mono: 'JetBrains Mono', monospace;

/* Dark background palette */
--bg:        #0d1117;
--surface:   #161b22;
--surface2:  #21262d;
--surface3:  #2d333b;
--border:    #30363d;

/* Text */
--text:      #e6edf3;
--text2:     #8b949e;
--text3:     #484f58;

/* Brand accent — DCC Blue */
--accent:    #2f81f7;
--accent-alt:#58a6ff;

/* Status colours */
--success:   #3fb950;
--warning:   #d29922;
--danger:    #f85149;
--info:      #58a6ff;
```

**5 Color Themes Implemented:**

| Theme | Background | Accent |
| :--- | :--- | :--- |
| Dark (default) | #0d1117 | #2f81f7 |
| Light | #f0f4f8 | #2563eb |
| Sky | #0a1628 | #38bdf8 |
| Ocean | #071520 | #00d4aa |
| Presentation | #12082a | #c084fc |

**Shared Layout Rules:**
- Top navigation bar: fixed, `--surface`, height 48px
- Sidebar: 240px wide, `--surface`, collapsible
- Content area: `--bg`, padding `--space-lg`
- Cards: `--surface`, border `1px solid --border`, radius `--radius-md`
- Tables: header `--surface2`, alternating rows, hover `--surface3`
- Buttons: primary `--accent` bg; secondary `--surface3` bg
- Status badges: pill shape, colour from status palette

**Components:** 25+ including buttons (5 variants), form controls, cards/KPI tiles, tables, badges, tabs, toolbar, drop zone, toast notifications, tree views, modals.

**Spacing Scale:** `--space-xs: 4px`, `--space-sm: 8px`, `--space-md: 16px`, `--space-lg: 24px`, `--space-xl: 32px`

#### Risks & Mitigation
- **Risk:** Tool creators deviate from design system. **Mitigation:** Single CSS file enforced; any tool not importing it is non-compliant.
- **Risk:** Theme colours don't provide sufficient contrast. **Mitigation:** All themes tested against WCAG 2.1 Level AA contrast ratios.

#### Success Criteria
- [x] CSS variables defined for all themes
- [x] All 5 themes functional and switchable
- [x] Components reusable across all tools
- [x] WCAG 2.1 Level AA contrast compliance

#### References
- Design system file: `dcc/ui/dcc-design-system.css`

---

### Phase 2: Pipeline Dashboard

**Timeline:** Days 2–3 (initial), Days 11–12 (v3.0 revision)  
**Status:** ✅ REVISION COMPLETED  
**File:** `dcc/ui/pipeline_dashboard.html` (881 lines)

#### What Was Created (v1.0–v2.0)

Initial static mockup: central hub showing pipeline run status, output file links, processing summary KPIs, and data health score.

**Legacy Features (static mockup):**
- Pipeline run status card (Steps 1–6 with pass/fail indicators)
- KPI tiles: rows processed, match rate, columns created, error count, data health score
- Output file quick-links: CSV, Excel, Summary, Debug Log, Dashboard JSON
- Data health score gauge
- Last run timestamp and schema version
- "Run Pipeline" button

**Known Issues Identified (v3.0 revision driver):**
1. All data is hardcoded — no `fetch()` or `FileReader` implementation
2. All buttons (Run, Refresh, Load Files, iconbar, toolbar) have no event handlers
3. Output file links use `href="#"` — point to nothing
4. Pipeline stages always show "pending" with 0% progress
5. Status bar shows hardcoded values, not real pipeline state
6. Recent activity table has static sample rows
7. Theme dot colors for Sky and Presentation misrepresent actual theme backgrounds

#### v3.0 Revision Scope

**Data Sources:** `output/error_dashboard_data.json`, `output/processing_summary.txt`, `output/debug_log.json`

**9 Sub-Tasks:**

| ID | Task | Detail |
| :--- | :--- | :--- |
| 2.1 | **Compliance check against html_design_rule.md** | Audit `pipeline_dashboard.html` against all rules. Fix violations first before adding new features. |
| 2.2 | **Implement data loader** | Add `fetch()` calls to load `error_dashboard_data.json` and `processing_summary.txt` from `dcc/output/`. Fallback to FileReader API for `file://` protocol. Handle missing files with graceful degradation and clear error messages. |
| 2.3 | **Make KPI tiles data-driven** | Replace hardcoded values (1,247 rows, 100% match, etc.) with real data derived from loaded JSON. Add abbreviated formatting (1.2K, 3.5M). |
| 2.4 | **Update pipeline stages from real data** | Parse phase-level error/success info from `error_dashboard_data.json`. Set stage progress bars, status labels (pass/fail/warning), and color-coding dynamically per stage. |
| 2.5 | **Wire up output file links** | Replace `href="#"` with real relative paths (`../output/processed_dcc_universal.csv`, etc.). Add click-to-download or open behavior. |
| 2.6 | **Add button event handlers** | Attach handlers to: Run Pipeline (trigger re-fetch), Refresh Data (reload from files), Load Files (FileReader picker). Wire iconbar + toolbar buttons appropriately. |
| 2.7 | **Make status bar dynamic** | Derive "Last run" timestamp, overall status indicator, and version from loaded data. Show error count in status if pipeline has failures. |
| 2.8 | **Load recent activity from log files** | Parse `debug_log.json` to populate the activity table with real events, timestamps, and status badges. |
| 2.9 | **Fix theme dot colors** | Correct `themeColors` JS object: Sky dot from `#0a1628` to `#e0f2fe`, Presentation dot from `#12082a` to `#f8fafc` to match actual CSS background values. |

#### Compliance Audit Results (html_design_rule.md)

| # | Rule | Status | Finding |
| :--- | :--- | :--- | :--- |
| 1.1 | VS Code-like layout: title bar, side icon bar, toggleable left sidebar, status bar, right sidebar | ❌ Partial | Title bar, icon bar, left sidebar, status bar exist. **No right sidebar panel.** |
| 1.2 | Theme toggle in top-right title bar | ✅ Pass | Theme button with dropdown menu present. |
| 1.3 | 5 themes: light, dark, sky (light blue), ocean, presentation (light grey), saved to localStorage | ⚠️ Partial | 5 themes present and saved. CSS bg colors match spec. But `themeColors` JS object has wrong values for sky (`#0a1628`) and presentation (`#12082a`) — dark instead of light. |
| 1.4 | All panels height/width adjustable | ❌ Fail | No drag-to-resize on any panel. Sidebar width fixed. |
| 1.5 | All HTML files reference same CSS | ✅ Pass | Imports `dcc-design-system.css`. |
| 1.6 | Icons only in icon bar, title bar, buttons | ✅ Pass | Uses emoji icons appropriately. |
| 2.1 | Title bar full width with theme button, layout button, menu, search | ❌ Partial | Full width ✅. Has theme button. **Missing layout button. Missing global search.** |
| 3.1 | Side icon bar toggles left sidebar | ❌ Fail | Icon bar buttons have no event handlers — clicking them does nothing. |
| 4.1 | Sidebar contents toggleable | ✅ Pass | Sidebar sections collapse/expand on click. |
| 4.2 | Sidebar resizable by dragging right edge | ❌ Fail | No drag-resize implemented. |
| 4.3 | Sidebar collapsible via icon bar | ❌ Fail | No mechanism to hide/show entire sidebar. |
| 5.1–5.2 | Right sidebar panel with toggleable contents, resizable | ❌ Fail | No right sidebar exists. |
| 6.1 | File loading panel loads local/pipeline files | ❌ Fail | "Load Files" button exists but no handler. |
| 6.2 | File loading panel lists loaded files | ❌ Fail | Not implemented. |
| 6.3 | Drag-and-drop file loading | ❌ Fail | Not implemented. |
| 6.4 | Status bar shows selected file | ❌ Fail | Not implemented. |
| 6.5 | File loading panel collapsible via icon bar | ❌ Fail | Not implemented. |
| 7.1–7.4 | Tree selection panel for hierarchical content | ❌ Fail | No tree view exists. |

#### Risks & Mitigation
- **Risk:** Missing or malformed data files cause UI errors. **Mitigation:** Graceful degradation with placeholder data and clear error messages.
- **Risk:** Large KPI values overflow UI tiles. **Mitigation:** Abbreviated number formatting (1.2K, 3.5M).
- **Risk:** `fetch()` blocked on `file://` protocol in some browsers. **Mitigation:** Auto-detect protocol; fallback to FileReader API with local file picker.
- **Risk:** JSON structure changes between pipeline versions. **Mitigation:** Validate required fields on load; fallback to empty/default state.

#### Potential Issues to Address in Future
- Real-time WebSocket updates for live pipeline runs
- Historical trend charts for KPI values over time
- Pipeline configuration editing from the dashboard

#### Success Criteria (v3.0)
- [x] All non-conformant html_design_rule.md items resolved (see compliance audit table)
- [x] KPI tiles render from real pipeline output data
- [x] Pipeline stages show correct pass/fail per phase from data
- [x] Output file links navigate to real files
- [x] Run/Refresh buttons trigger actual data reload
- [x] Status bar reflects real last-run timestamp and status
- [x] Activity table populated from debug log
- [x] Theme dots match actual theme background colors
- [x] Graceful fallback when data files are missing
- No hardcoded mock data remains in the script

#### v3.1 Revision Scope — Functional Run Integration

**Status:** ✅ COMPLETED  
**Data Sources:** `../output/error_dashboard_data.json`, `../output/processing_summary.txt`, `../output/debug_log.json`  
**API Endpoints:** `POST /api/v1/pipeline/run`, `GET /api/v1/pipeline/status`

The v3.1 revision upgrades the Pipeline Dashboard from a read-only monitoring tool to a functional execution controller. The "Run" button will be wired to the backend API to trigger `dcc_engine_pipeline.py` and provide real-time feedback.

**4 Sub-Tasks for v3.1 Revision:**

| ID | Task | Detail | Priority |
| :--- | :--- | :--- | :--- |
| 2.10 | **Implement `triggerPipelineRun()`** | Update `toolbarRunBtn` handler to send a `POST` request to `/api/v1/pipeline/run`. Send the current `base_path` and `upload_file_name` extracted from the sidebar. Handle 202 Accepted and error responses. | High |
| 2.11 | **Real-time Status Polling** | Implement a polling mechanism (e.g., every 2s) after a run is triggered. Call `/api/v1/pipeline/status` (or equivalent) to get the current stage and progress. Update the stage cards and progress bars dynamically. | High |
| 2.12 | **Execution Lock & Feedback** | Disable the "Run" button and show a spinner/loading state while the pipeline is active. Show a toast notification on completion or failure. | Medium |
| 2.13 | **Auto-Refresh on Completion** | Trigger a full `loadAllData()` refresh once the pipeline status reaches 'COMPLETED' to show the latest KPIs and output files. | Medium |
| 2.14 | **Live Output Console / Popup** | Implement a modal window or collapsible console panel that displays real-time `stdout`/`stderr` or log messages from the running pipeline. Use the status polling response to append new log lines. | Medium |

#### Risks & Mitigation (v3.1)

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| API endpoint not reachable on `file://` protocol | High | High | Disable "Run" button on `file://` with a tooltip explaining that a server is required for execution. |
| Long-running pipeline causes browser timeout | Medium | Medium | Use asynchronous polling; ensure backend doesn't block the request. |
| Race condition between polling and data loading | Low | Low | Only reload static data files after polling confirms completion. |

#### Success Criteria (v3.1)
- [x] "Run" button successfully triggers the backend pipeline via API.
- [x] UI provides visual feedback (loading state, disabled button) during execution.
- [x] Stage cards and progress bars update dynamically during the run.
- [x] Dashboard automatically refreshes with new data upon completion.
- [x] Graceful handling of API errors or network timeouts.
- [x] `file://` protocol guard disables Run button with tooltip explaining server requirement.

#### References

- Report: `web_interface_report.md`
- User guide: `../../../ui/user_guide.md`
- Data files: `dcc/output/error_dashboard_data.json`, `dcc/output/processing_summary.txt`, `dcc/output/debug_log.json`
- Design system: `dcc/ui/dcc-design-system.css`

---

### Phase 3: Excel Explorer Pro

**Timeline:** Days 3–4  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/excel_explorer_pro.html` (2,847 lines)

#### What Was Created

Load and explore the processed output CSV/Excel with filtering, sorting, column visibility, and export.

**Features:**
- File loader: drag-and-drop CSV or Excel
- Column visibility toggle panel
- Multi-column sort and filter
- Freeze first N columns
- Row-level validation error highlighting (from `Validation_Errors` column)
- Data health score per row (from `Data_Health_Score` column)
- Export filtered view to CSV
- Column group tabs (document_info, submission_info, review_info, metadata)

**Libraries:** Papa Parse 5.4.1 (CSV), XLSX.js 0.18.5 (Excel)

#### Risks & Mitigation
- **Risk:** Large CSV/Excel files cause browser freezes. **Mitigation:** Virtual scrolling; recommended max file size 50MB.
- **Risk:** Encoding issues with non-UTF-8 files. **Mitigation:** Auto-detect encoding; fallback to Latin-1.

#### Success Criteria
- [x] CSV loading with 100% accuracy
- [x] Excel loading with 100% accuracy
- [x] Filter and search functional
- [x] Validation highlighting works on `Validation_Errors` column
- [x] Export produces valid CSV

---

### Phase 4: Error Diagnostic Dashboard — v2.0 Revision

**Timeline:** Days 4–5 (initial), 2026-05-20 (v2.0 revision)  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/error_diagnostic_dashboard.html` (765 lines)

#### What Was Created (v1.0)

Initial functional dashboard visualizing error data from `error_dashboard_data.json` using Chart.js.

**Features (v1.0):**
- Error summary by phase (P1–P4) table
- Error code frequency bar chart
- Per-column error heatmap (CSS grid)
- Row-level error detail table
- Data health score distribution line chart
- Filter by error code, column, severity (static placeholders)
- Theme switching with 5 themes

#### v2.0 Revision Scope — Full Compliance & Dynamic Data

The v2.0 revision transforms the dashboard from a partially static visualization tool into a fully compliant, interactive DCC shell application that dynamically loads and explores real pipeline diagnostic data.

**Compliance Audit Against `html_design_rule.md` (Post-Implementation)**

| # | Rule | Status | Finding |
| :--- | :--- | :--- | :--- |
| 1.1 | VS Code layout (title/icon/left/right/status) | ✅ Pass | Full shell with right sidebar, statusbar, iconbar present. |
| 1.2-1.3 | Theme picker with 5 themes + localStorage | ✅ Pass | Fully implemented — Dark, Light, Sky, Ocean, Presentation. |
| 1.4 | Adjustable height/width of all panels | ⚠️ Partial | Width resizable via drag handles ✅; height adjustment not implemented. |
| 1.5 | Reference same shared CSS | ✅ Pass | Imports `dcc-design-system.css`. |
| 1.6 | Icons only in icon bar, title bar, buttons | ✅ Pass | Compliant. |
| 2.1-2.3 | Title bar: theme, layout, search, menu | ✅ Pass | Layout toggle (3 modes), global search, theme picker all present and functional. |
| 3.1-3.4 | Icon bar with top/bottom groups and divider | ✅ Pass | 📂🌳 on top, divider, ⚙️❓ on bottom; all wired to panel toggles. |
| 4.1-4.3 | Left sidebar: resizable, collapsible, toggleable | ✅ Pass | Drag-resize handle, icon bar collapse, panel toggling all functional. |
| 5.1-5.3 | Right sidebar: toggleable, resizable, at right | ✅ Pass | Settings/Help panels toggleable, drag-resize handle present. |
| 6.1-6.5 | File loading panel: drag-drop, file list, status | ⚠️ Partial | Drag-drop ✅, FileReader ✅, status bar shows filename ✅; **no file list displayed** (Rule 6.2). |
| 7.1-7.4 | Tree selection panel: hierarchical structure | ⚠️ Partial | Navigation tree present with scroll-to-section; **no expand/collapse all** (Rule 7.4). |
| 8.1-8.5 | Icons: Info(ℹ️), Load(📂), Help(❓), Settings(⚙️), Tree(🌳) | ⚠️ Partial | 📂, 🌳, ⚙️, ❓ present; **missing ℹ️** (Rule 8.1). |
| 9.1 | Help/About/Revision from `ui_help.json` | ✅ Pass | Loads on init, updates version in status bar. |

**9 Sub-Tasks for v2.0 Revision:**

| ID | Task | Detail | Priority |
| :--- | :--- | :--- | :--- |
| 4.1 | **Implement Full DCC Shell** | Add Right Sidebar panel. Reorganize Icon Bar with top/bottom groups and a divider. Add Layout Toggle and Global Search to Title Bar. | High |
| 4.2 | **Add Drag-to-Resize Handles** | Implement resizable panels with mouse event listeners and visual drag handles between sidebars and content. | High |
| 4.3 | **Dynamic Data Loader** | Implement `fetch()` and `FileReader` (drag-drop) for `error_dashboard_data.json`. Replace all hardcoded KPI, chart, and table data with JS parsing logic. | High |
| 4.4 | **Icon Bar Panel Toggling** | Wire all icon bar buttons (Dashboard, Errors, Health, Help, Settings) to show/hide respective sidebar panels. | Medium |
| 4.5 | **Navigation Tree Panel** | Implement a `🌳 Navigation` panel to jump between different error phases or jump to specific chart sections. | Medium |
| 4.6 | **Externalize Metadata to ui_help.json** | Load Help, About, and Revision notes from `ui_help.json`. | Medium |
| 4.7 | **Standardize Icons & Status Bar** | Update icons to mandated emojis. Make status bar dynamic (show row count, health score, error counts from loaded file). | Low |
| 4.8 | **Live Global Search** | Implement search logic in Title Bar that filters the Error Detail table as the user types. | Medium |
| 4.9 | **Dynamic Chart Rebuild** | Ensure Chart.js instances properly update data and colors on file load and theme switch. | High |

#### Risks & Mitigation
- **Risk:** Large JSON files (>10MB) cause Chart.js rendering lag. **Mitigation:** Limit table to first 500 errors; group minor error codes in charts.
- **Risk:** `fetch()` blocked on local file system. **Mitigation:** Auto-fallback to FileReader API with a prominent "Load Data" drop zone.

#### Success Criteria (v2.0)
- [x] Sidebar panels resizable via drag handles
- [x] Icon bar groups icons correctly and toggles respective panels
- [x] Data loaded dynamically from `error_dashboard_data.json` or user drop
- [x] Charts and tables update based on real data (no hardcoded mock data)
- [x] Help/About sections loaded from `ui_help.json`
- [x] Global search successfully filters error details
- [x] All mandated emojis used for icons (ℹ️, 📂, ❓, ⚙️, 🌳)

#### Bugs Identified During Audit

| ID | Severity | Location | Description |
| :--- | :--- | :--- | :--- |
| BUG-001 | High | Line 638 | `onclick="filterByColumn('${c.column}')"` — column names with single quotes break JS execution (XSS vulnerability). |
| BUG-002 | Medium | Line 531 | `renderPhases(rawData.phase_breakdown)` called with unfiltered data — phase summary table ignores active filters. |
| BUG-003 | Medium | Line 398 | Resize sets CSS vars `--sidebar-w` / `--right-sidebar-w` — may not be defined in `dcc-design-system.css`, causing resize to have no visual effect. |
| BUG-004 | Medium | Line 656 | Phase table uses PascalCase keys (`p.Critical`, `p.High`) — values will be `undefined` if `phase_breakdown` data uses lowercase. |
| BUG-005 | Low | Line 743 | CSV export uses naive quoting — doesn't handle newlines or commas within fields properly. |
| BUG-006 | Low | Line 328 | `document.querySelector(\`[data-theme="${savedTheme}"]\`)` may double-apply `.active` class on theme restore. |
| BUG-007 | Low | Lines 693-697 | Navigation tree uses inline `onclick` handlers — incompatible with strict CSP policies. |
| BUG-008 | Info | Line 8 | Chart.js 3.9.1 loaded from CDN — no fallback if CDN is unreachable. |

#### Remaining Items for Future Revision

| ID | Rule | Description |
| :--- | :--- | :--- |
| REM-001 | 1.4 | Implement panel height adjustment (currently only width is resizable). |
| REM-002 | 6.2 | Display list of loaded files in the file loading panel. |
| REM-003 | 7.4 | Add expand-all / collapse-all controls to navigation tree. |
| REM-004 | 8.1 | Add ℹ️ (Info) icon to icon bar. |

---

### Phase 4: Error Diagnostic Dashboard — v2.1 Revision

**Timeline:** 2026-05-20–21  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/error_diagnostic_dashboard.html` (937 lines)

#### v2.1 Revision Scope — Debug Log Integration with Message Parsing

The v2.1 revision adds `debug_log.json` as a secondary data source. Critically, `debug_log.json` contains **two arrays**:

1. **`errors[]`** — **4,601 entries** — every single row-level error from the pipeline run, with no cap or deduplication. Error code, row, and column are embedded in a formatted message string.
2. **`messages[]`** — **179 entries** — pipeline lifecycle logs (bootstrap, milestones, strategy decisions, validation summaries).

The error detail table will be populated from `debug_log.json["errors"]` (all 4,601 errors) instead of the capped 50 from `error_dashboard_data.json["recent_errors"]`. Message parsing extracts `code`, `row`, and `column` from each entry to enable filter-driven correlation.

**Data Source Analysis:**

| File | Array | Count | Content | Fields |
| :--- | :--- | :--- | :--- | :--- |
| `error_dashboard_data.json` | `recent_errors[]` | 50 (capped) | Row-level error details, deduplicated | `row`, `column`, `code`, `message`, `severity` (pre-parsed) |
| `error_dashboard_data.json` | `error_types[]` | 17 | Aggregated error code counts | `code`, `count`, `severity` |
| `error_dashboard_data.json` | `column_health[]` | 18 | Per-column error counts | `column`, `error_count` |
| `dcc/output/debug_log.json` | `errors[]` | 4,601 | All row-level errors, no cap, no dedup | `timestamp`, `module`, `context`, `message` (formatted: `[CODE] description (Row: N) (Col: X)`) |
| `dcc/output/debug_log.json` | `messages[]` | 179 | Pipeline execution trace | `timestamp`, `level`, `module`, `context`, `message` |

**Message Parsing Strategy:**

Each entry in `debug_log.json["errors"]` has a `message` field in this format:
```
[P2-I-V-0204-E] Document_ID contains reply/comment reference: '#000002.0_...' (Row: 5) (Col: Document_ID)
```

A regex parser will extract:
- **`code`**: `P2-I-V-0204-E` (pattern: `[A-Z0-9]+-[A-Z]-[A-Z]-[0-9]+[A-Z]?`)
- **`row`**: `5` (pattern: `\(Row:\s*(\d+)\)`)
- **`column`**: `Document_ID` (pattern: `\(Col:\s*([^)]+)\)`)
- **`description`**: everything between `]` and `(Row:`

Parsed entries are stored as structured objects matching the `recent_errors` schema, enabling seamless integration with existing filter logic.

**7 Sub-Tasks for v2.1 Revision:**

| ID | Task | Detail | Priority |
| :--- | :--- | :--- | :--- |
| 4.10 | **Load `debug_log.json` from `dcc/output/`** | Add `fetch('../output/debug_log.json')` with FileReader fallback. Parse both `errors[]` (4,601 entries) and `messages[]` (179 entries). Store in `debugLogData`. Graceful degradation if file missing. | High |
| 4.11 | **Message Parser — extract code/row/column** | Implement regex-based parser for `debug_log.json["errors"]` entries. Extract `code`, `row`, `column`, `description` from formatted `message` string. Build `parsedErrors[]` array with structured fields matching `recent_errors` schema. Handle malformed entries gracefully (skip with warning). | High |
| 4.12 | **Replace error detail table with parsed debug log data** | Replace `renderTable(filteredRecent)` to use `debugLogData.parsedErrors` as the primary error source instead of `rawData.recent_errors`. This provides all 4,601 errors (vs 50 capped). Apply existing filter logic (code, column, severity, global search) against parsed fields. Paginate or limit display (e.g., first 500) for performance. | High |
| 4.13 | **Filter-Driven Error Detail Correlation** | When user selects a column or error code filter, the parsed error array is filtered by extracted `column` and `code` fields. Matching errors populate the detail table. Additionally, scan `debugLogData.messages[]` for entries referencing the selected column/code — display matching pipeline trace entries in a "Debug Context" section above the error table (e.g., filtering `Document_ID` shows strategy resolution and validation phase messages). | High |
| 4.14 | **Pipeline Trace Panel** | Add new left sidebar section "📋 Pipeline Trace" showing `debug_log.json["messages"]`. Filterable by level (L1 milestone, L2 info, L3 trace). Collapsible sections by pipeline phase (Bootstrap, Setup, Mapping, Validation, Calculations, AI Ops, Export). Timestamp, module, context displayed per entry. | Medium |
| 4.15 | **Bug Fixes from v2.0 Audit** | Fix BUG-001 (XSS in onclick), BUG-002 (phase table ignores filters), BUG-003 (CSS vars undefined), BUG-004 (PascalCase key mismatch). | High |
| 4.16 | **Data source toggle** | Add settings option to switch error detail table source between `debug_log.json` (all 4,601 errors) and `error_dashboard_data.json` (50 deduplicated). Default to `debug_log.json`. | Low |

#### Features (v2.1 additions)

- **Full Error Coverage:** All 4,601 errors available in detail table (vs 50 capped)
- **Message Parsing:** Regex extraction of code/row/column from formatted debug log messages
- **Filter-Driven Correlation:** Column/error code filter shows matching errors + related pipeline trace
- **Pipeline Trace Panel:** Debug log browser with level filtering and phase grouping
- **Data Source Toggle:** Switch between debug_log (full) and dashboard (deduplicated) sources
- **4 Bug Fixes:** XSS, filter bypass, CSS resize, key casing

#### Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| `debug_log.json` too large (>50MB) for browser | Low | Medium | Limit display to first 500 parsed errors; virtual scrolling; warn user |
| Message parsing fails for non-standard formats | Medium | Medium | Regex with fallback — entries that don't match pattern are stored with `code: "UNKNOWN"`, `row: null`, `column: "Unknown"`; logged to console |
| No matching debug log entries for selected filter | Medium | Low | Show "No errors found for this filter" placeholder |
| `fetch()` blocked on `file://` protocol | Medium | Low | Auto-fallback to FileReader with file picker |
| Debug log format changes between pipeline versions | Low | Medium | Validate `errors[]` structure on load; fallback to `error_dashboard_data.json` if parsing fails |
| Performance degradation with 4,601+ DOM rows | Medium | Medium | Paginate to 500 rows max; add "load more" button; use `DocumentFragment` for batch DOM insertion |

#### Success Criteria (v2.1)

- [x] `debug_log.json` loaded on init from `dcc/output/` with FileReader fallback
- [x] Message parser correctly extracts `code`, `row`, `column` from 95%+ of `errors[]` entries
- [x] Error detail table populated from parsed debug log data (all 4,601 errors, paginated)
- [x] Column/error code filter correctly filters parsed errors by extracted fields
- [x] Matching pipeline trace entries displayed in Debug Context section when filter applied
- [x] Pipeline Trace panel displays messages with level filtering and phase grouping
- [x] Data source toggle switches between debug_log and dashboard sources
- [x] BUG-001 (XSS), BUG-002 (filter bypass), BUG-003 (CSS vars), BUG-004 (key casing) all fixed
- [x] No regressions in v2.0 features (charts, heatmap, filters, resize, theme)
- [x] JS syntax validated

---

### Phase 4: Error Diagnostic Dashboard — v2.2 Revision

**Timeline:** 2026-05-21  
**Status:** ✅ COMPLETED  
**Files Modified (UI-side only):**
- `ui/error_diagnostic_dashboard.html`
- `ui/ai_analysis_dashboard.html` (if it consumes debug_log.json)

**Python-side files (handled by Error Handling Integration workplan Phase 1.5):**
- `workflow/initiation_engine/utils/logging.py`
- `workflow/processor_engine/error_handling/core/logger.py`
- `workflow/core_engine/logging/log_state.py`

#### v2.2 Revision Scope — Structured JSON `context` and `message` in `debug_log.json`

The v2.2 revision converts the `context` and `message` fields in `debug_log.json` from flat strings to structured JSON objects. This eliminates the need for regex-based message parsing in the dashboard and aligns the output format with the `PipelineErrorEvent` schema defined in the Error Handling Integration workplan.

**Python-side changes (tasks 4.17–4.19) moved to Error Handling Integration workplan Phase 1.5.** See [`error_handling/integration/error_handling_integration_workplan.md`](../../error_handling/integration/error_handling_integration_workplan.md) for details.

**Problem Statement:**

Currently, `debug_log.json` stores `context` and `message` as flat strings:
```json
{
  "context": "phase:None, layer:L3, source:StructuredLogger",
  "message": "[P2-I-V-0204-E] Document_ID contains reply/comment reference: '...' (Row: 5) (Col: Document_ID)"
}
```

The dashboard must use regex (`ERR_CODE_RE`, `ERR_ROW_RE`, `ERR_COL_RE`) to extract structured fields. This is fragile — the original regex missed codes like `F4-C-F-0401-A` and `P2-I-V-0204-E` because the pattern was too restrictive.

**Proposed Format:**
```json
{
  "context": {
    "phase": null,
    "layer": "L3",
    "source": "StructuredLogger"
  },
  "message": {
    "error_code": "P2-I-V-0204-E",
    "description": "Document_ID contains reply/comment reference: '...'",
    "row": 5,
    "column": "Document_ID"
  }
}
```

**Motivation:**
- Eliminates all regex parsing in dashboard — direct JSON field access
- Aligns with `PipelineErrorEvent` schema (domain, code, severity, engine, phase, message, details, timestamp)
- Enables native filtering/sorting by structured fields in dashboard
- Single source of truth — no string↔dict roundtrip needed
- Follows agent_rule.md Section 4 (SSOT, schema-driven design) and Section 6 (structured logging)

**3 Sub-Tasks for v2.2 Revision (UI-side only):**

| ID | Task | Detail | Priority |
|---|---|---|---|
| 4.20 | **Update dashboard `parseDebugErrors()` to read structured fields** | Check `typeof entry.message === 'object'` — if true, read `entry.message.error_code`, `.row`, `.column`, `.description` directly. If false (legacy string), fall back to regex parsing. This ensures backward compatibility with existing `debug_log.json` files. | High |
| 4.21 | **Update dashboard `renderDebugContext()` and `renderPipelineTrace()`** | Replace `msg.includes()` string matching with structured field comparison. Filter by `entry.context.phase`, `entry.context.layer`, `entry.message.error_code` directly. | Medium |
| 4.22 | **Verify `save_debug_log()` serialization** | Confirm `json.dumps(DEBUG_OBJECT, indent=2, default=str)` handles nested dicts correctly. Remove `default=str` fallback after migration — all values should be natively serializable. | Low |

**Dependencies:**
- Requires Phase 1.5 of Error Handling Integration workplan to be completed first (Python-side changes)
- Dashboard sub-tasks 4.20–4.22 depend on structured JSON output being available in `debug_log.json`

#### Features (v2.2 additions)

- **Structured `context` field:** `{phase, layer, source}` dict instead of `"phase:X, layer:Y, source:Z"` string
- **Structured `message` field:** `{error_code, description, row, column}` dict for errors; `{description}` dict for messages
- **Regex elimination:** Dashboard reads fields directly — no `ERR_CODE_RE`, `ERR_ROW_RE`, `ERR_COL_RE` needed
- **Backward compatibility:** Dashboard falls back to regex if `message` is still a string (legacy files)
- **Console output unchanged:** Display string composed from structured dict before printing

#### Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Existing `debug_log.json` files incompatible | Low | Medium | Dashboard type-checks `entry.message` — falls back to regex for legacy string format |
| Other tools/scripts grep `message` field | Low | Medium | Document the change; provide migration note in workplan |
| `json.dumps` with `default=str` masks dict issues | Low | Low | Keep `default=str` as safety net during transition; remove after all callers updated |

#### Success Criteria (v2.2)

- [x] `debug_log.json` `errors[]` entries have `context` as dict and `message` as dict (Phase 1.5 — Python-side)
- [x] `debug_log.json` `messages[]` entries have `context` as dict and `message` as dict (Phase 1.5 — Python-side)
- [x] Console output format unchanged (same string format printed to terminal) (Phase 1.5 — Python-side)
- [x] Dashboard `parseDebugErrors()` reads structured fields directly — no regex parsing for new-format entries (Task 4.20)
- [x] Dashboard falls back to regex for legacy string-format entries (backward compatibility) (Task 4.20)
- [x] `renderDebugContext()` and `renderPipelineTrace()` handle structured `message` and `context` dicts (Task 4.21)
- [x] JS syntax validated
- [x] No regressions in v2.1 features (debug log loader, error table, pipeline trace, filters)

#### References

- Error Handling Integration workplan Phase 1.5: `../../error_handling/integration/error_handling_integration_workplan.md` (Python-side tasks 1.5.1–1.5.3)
- SSOT Schema-Driven workplan: `../../pipeline_architecture/ssot_schema_driven_compliance/ssot_schema_driven_workplan.md` (Phase D: message_template pattern)
- agent_rule.md Section 4: SSOT and schema-driven design
- agent_rule.md Section 6: Structured logging and Debug Object

---

### Phase 4: Error Diagnostic Dashboard — v2.3 Revision

**Timeline:** 2026-05-21  
**Status:** ✅ COMPLETED  
**Files to Modify:**
- `ui/error_diagnostic_dashboard.html`

#### v2.3 Revision Scope — Filter Source Priority

Filter dropdowns (`errorCodeFilter`, `columnFilter`) are now populated from `error_dashboard_data.json` when available, falling back to `debug_log.json` parsed errors only when dashboard data is missing.

**Problem:** `updateFilterOptions()` used `errorDataSource` (user's detail table preference) to decide filter source. Default `'debug_log'` meant filters always came from `debug_log.json` even when `error_dashboard_data.json` was loaded. Parallel loaders (`Promise.allSettled`) created a race condition.

**Fix:** `updateFilterOptions()` now uses explicit priority: `rawData.recent_errors` first, fallback to `parsedErrors`. Detail table source toggle remains independent.

**1 Sub-Task for v2.3 Revision:**

| ID | Task | Detail | Priority |
|---|---|---|---|
| 4.23 | **Rewrite `updateFilterOptions()` with explicit source priority** | Replace `errorDataSource` ternary with `rawData?.recent_errors?.length > 0 ? rawData.recent_errors : parsedErrors`. Update `loadDebugLog()` to call `updateFilterOptions()` when `rawData` is null (dashboard failed). Console log reports which source was used. | High |

#### Success Criteria (v2.3)

- [x] Filters populated from `error_dashboard_data.json` when available
- [x] Filters fall back to `debug_log.json` parsed errors when dashboard data missing
- [x] Detail table source toggle remains independent (user choice for table, not filters)
- [x] No race condition from parallel loaders
- [x] JS syntax validated
- [x] No regressions in v2.2 features (structured JSON parsing, backward compatibility)

#### References

- Phase 4 v2.2: [Structured JSON context/message](#phase-4-error-diagnostic-dashboard--v22-revision)

---

### Phase 4: Error Diagnostic Dashboard — v2.4 Revision

**Timeline:** 2026-05-21  
**Status:** ✅ COMPLETED  
**Files to Modify:**
- `ui/error_diagnostic_dashboard.html`

#### v2.4 Revision Scope — Standalone `file://` Protocol Support

Dashboard works without a server (port 5000). When opened directly via `file://` protocol, prompts user to select the output folder, automatically finds and loads required JSON files.

**Problem:** `fetch()` is blocked by CORS on `file://` protocol. Dashboard showed a warning and did nothing — user had to manually drag-and-drop files or use the file picker.

**Fix:** On `file://` protocol, use `<input type="file" webkitdirectory>` to let user select the entire output folder. Scan selected files for `error_dashboard_data.json` and `debug_log.json`, load them via FileReader API.

**2 Sub-Tasks for v2.4 Revision:**

| ID | Task | Detail | Priority |
|---|---|---|---|
| 4.24 | **Folder picker for `file://` protocol** | `promptFolderLoad()` creates `<input type="file" webkitdirectory>` — user selects output folder. Scans files for target JSON names. Loads each via `loadFileViaReader()`. Calls `updateFilterOptions()` when debug log loaded without dashboard data. | High |
| 4.25 | **Drop zone processes all dropped files** | Changed `handleFile(e.dataTransfer.files[0])` to loop through all dropped files. Enables dropping an entire folder's contents. | Medium |

#### Success Criteria (v2.4)

- [x] Dashboard opens on `file://` protocol and prompts for folder selection
- [x] Folder picker finds and loads `error_dashboard_data.json` and `debug_log.json`
- [x] Filters populated correctly after folder load
- [x] Drop zone processes all dropped files (not just first)
- [x] JS syntax validated
- [x] No regressions in v2.3 features (filter priority, structured JSON)

#### References

- Phase 4 v2.3: [Filter source priority](#phase-4-error-diagnostic-dashboard--v23-revision)

---

### Phase 5: Schema Manager

**Timeline:** Days 5–6  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/schema_manager.html` (2,156 lines)

#### What Was Created

Browse, inspect, and edit schema files without touching raw JSON.

**Features:**
- Schema file tree (left panel): lists all `config/schemas/*.json`
- Column definition viewer: table with key properties
- Column detail panel: full definition, null_handling, validation rules, calculation config
- Schema reference viewer: shows resolved `approval_codes`, `departments`, etc.
- Global parameters editor: edit key params (sheet name, header row, durations)
- JSON diff view: compare current vs archive
- Export modified schema as JSON

**Data Source:** Reads schema JSON files directly via FileReader API or fetch

#### Risks & Mitigation
- **Risk:** Invalid schema edits could break the pipeline. **Mitigation:** Schema validation before export; user warned of structural changes.
- **Risk:** Deeply nested `$ref` chains are hard to display. **Mitigation:** Recursive resolution with depth limit and cycle detection.

#### Success Criteria
- [x] File tree lists all schema files
- [x] Column detail panel shows full definition
- [x] Global parameters editable and exportable
- [x] JSON diff view functional

---

### Phase 6: Log Explorer Pro

**Timeline:** Days 6–7  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/log_explorer_pro.html` (2,389 lines)

#### What Was Created

Browse `debug_log.json`, `issue_log.md`, `update_log.md`, and `test_log.md`.

**Features:**
- Log file selector
- JSON log tree viewer with collapsible nodes
- Markdown log renderer with anchor navigation
- Search and filter across log entries
- Issue status filter (Open / Resolved)
- Timeline view of log entries by date

**Data Sources:** `Log/debug_log.json`, `Log/issue_log.md`, `Log/update_log.md`, `Log/test_log.md`

#### Risks & Mitigation
- **Risk:** Malformed Markdown in log entries breaks rendering. **Mitigation:** Sanitize Markdown before rendering; fallback to plain text.
- **Risk:** JSON logs with deeply nested structures are slow. **Mitigation:** Lazy loading for deep tree nodes.

#### Success Criteria
- [x] All 4 log formats render correctly
- [x] Search filters across all log entries
- [x] Timeline view groups entries by date
- [x] Theme switching applied

---

### Phase 7: Submittal Tracker Dashboard — v2.1 Revision

**Timeline:** Days 8–9 (initial), 2026-05-15 (v2.0), 2026-05-15 (v2.1)  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/submittal_dashboard.html` (~675 lines)

#### What Was Created (v2.1 — schema-driven validation + awaiting response KPI)

v2.1 revision of the data-driven dashboard. Replaces complex client-side Document_ID validation (segment counting, format regex, composite matching) with a schema-driven approach that reads error codes from `data_error_config.json` and checks the pipeline's `Validation_Errors` column. Adds a 5th KPI for documents awaiting response.

**Features (v2.1 additions):**
- **Schema-Driven Validation:** `loadDocIdRules()` fetches `data_error_config.json` on init, extracts all error codes where `column` includes `Document_ID` (P2-I-P-0201, P2-I-V-0204, P2-I-V-0204-A/B/C). `isValidDocId()` checks `row['Validation_Errors']` for matching codes instead of reimplementing validation logic.
- **Pre-Filter at Load:** `parseCSV()` filters `allData` through `isValidDocId()` at load time — invalid rows never enter the data set.
- **Awaiting Response KPI:** 5th tile counting unique docs where `Latest_Approval_Code` is PEN or PENDING. Clickable to a detail table showing pending documents.
- **Robust fallback:** Rules built in temp object, only assigned on full success. Fallback uncertain-values blocklist preserved for CSV files without `Validation_Errors` column.

**Features (v2.0 — data-driven dashboard):**
- **Compliance:** Full VS Code layout (title bar, icon bar, left/right sidebars, status bar). Layout toggle button. Resizable panels via drag handles. Icon bar buttons wired to toggle panels. Theme system with 5 themes saved to localStorage. Help panel loads from `ui_help.json`.
- **CSV Loader:** `fetch()` from `../output/processed_dcc_universal.csv` with FileReader fallback for local files. Load/Refresh buttons in toolbar.
- **KPI Tiles:** Total documents (distinct IDs), open submissions (not closed), overdue resubmissions, approval rate, awaiting response — all computed dynamically from data.
- **4 Data-Driven Charts:** Submission timeline (grouped by month), approval status (doughnut from Latest_Approval_Code), documents by discipline (bar chart), approval rate trend (by month). Charts rebuild on theme switch.
- **Overdue Resubmission Table:** Rows filtered by `Resubmission_Overdue_Status = 'Overdue'`, sorted by days overdue. Clickable column headers (placeholder for sort).
- **Dynamic Filters:** Project, Facility, Discipline, Department, Submitted By, Review Status dropdowns populated from distinct column values. Filter change re-renders all charts and KPIs.
- **Status Bar:** Shows current status, loaded filename, row count.

#### Compliance Audit Against html_design_rule.md

| # | Rule | Status | Finding |
| :--- | :--- | :--- | :--- |
| 1.1 | VS Code-like layout: title bar, icon bar, left sidebar, status bar, right sidebar | ❌ Partial | Has title bar, icon bar, left sidebar. **No status bar, no right sidebar.** |
| 1.2 | Theme toggle in top-right title bar | ✅ Pass | Theme button with dropdown menu present. |
| 1.3 | 5 themes saved to localStorage | ✅ Pass | All 5 themes functional and saved. |
| 1.4 | All panels height/width adjustable | ❌ Fail | No drag-to-resize on any panel. |
| 1.5 | All HTML files reference same CSS | ✅ Pass | Imports `dcc-design-system.css`. |
| 1.6 | Icons only in icon bar, title bar, buttons | ✅ Pass | Uses emoji icons appropriately. |
| 2.1 | Title bar full width with theme, layout, menu, search | ❌ Partial | Full width ✅. Has theme button. **Missing layout button. Missing search.** |
| 2.2 | Layout toggle switches layouts | ❌ Fail | No layout toggle button. |
| 2.3 | Show layout toggle button | ❌ Fail | Not present. |
| 3.1 | Left icon bar has icons for left and right panels | ❌ Fail | Only has dashboard icon. **No right panel icon, no divider.** |
| 3.2 | Left panel icons on top | ⚠️ Partial | Single icon, no right panel section. |
| 3.3 | Right panel icons at bottom with divider | ❌ Fail | Has bottom help icon but **no divider line before it.** |
| 3.4 | Click icon bar to toggle panels | ❌ Fail | Icon bar buttons have **no event handlers.** |
| 4.1 | Sidebar contents toggleable | ✅ Pass | Sidebar sections collapse/expand on click. |
| 4.2 | Sidebar resizable by dragging right edge | ❌ Fail | No drag-resize implemented. |
| 4.3 | Sidebar collapsible via icon bar | ❌ Fail | No icon bar handler for collapse. |
| 5.1–5.3 | Right sidebar panel with toggleable contents, resizable | ❌ Fail | **No right sidebar exists at all.** |
| 6.1 | File loading panel loads local/pipeline files | ❌ Fail | **No file loading mechanism exists.** |
| 6.2 | File loading panel lists loaded files | ❌ Fail | Not implemented. |
| 6.3 | Drag-and-drop file loading | ❌ Fail | Not implemented. |
| 6.4 | Status bar shows selected file | ❌ Fail | **No status bar exists.** |
| 6.5 | File loading panel collapsible via icon bar | ❌ Fail | Not implemented. |
| 7.1–7.4 | Tree selection panel | N/A | Not applicable for analytics dashboard. |
| 8.1–8.5 | Icon standards | ❌ Partial | Help ❓ present. **Missing settings ⚙️, file load 📂.** |
| 9.1 | Help text in ui_help.json | ❌ Fail | **No help panel, no ui_help.json content loaded.** |

**Compliance Summary (pre-v2.0):** 3 PASS, 1 PARTIAL, 15 FAIL, 1 N/A — audit above reflects state before v2.0 revision. After v2.0 all layout compliance items were resolved (right sidebar, status bar, resizable panels, icon bar handlers, drag-and-drop file loading).

#### v2.1 Revision Scope

**Data Sources:** `../output/processed_dcc_universal.csv` (processed pipeline output), `../config/schemas/data_error_config.json` (Document_ID error codes)

**Additional Sub-Tasks (v2.1):**

| ID | Task | Detail |
| :--- | :--- | :--- |
| 7.13 | **Implement schema-driven validation** | Add `loadDocIdRules()` that fetches `data_error_config.json` and extracts all error codes with `column` containing `Document_ID` (P2-I-P-0201, P2-I-V-0204, P2-I-V-0204-A/B/C). Store codes in `docIdRules.docIdCodes[]`. |
| 7.14 | **Rewrite isValidDocId to use Validation_Errors** | Replace segment-counting, format-regex, and composite-matching logic. Check `row['Validation_Errors']` for any loaded Document_ID error code. Keep minimal fallback uncertain-values blocklist for CSV files without `Validation_Errors` column. |
| 7.15 | **Pre-filter invalid IDs at load time** | Add `isValidDocId(r.Document_ID, r)` to `parseCSV()` filter chain so invalid rows never enter `allData`. Update all detail table functions (`showDetail*`) to pass row as second argument. |
| 7.16 | **Add Awaiting Response KPI** | 5th KPI tile counting unique docs with no terminal approval code (null, PEN, or PENDING). Add `showDetailAwaiting()` click handler. |
| 7.17 | **Robust fallback in loadDocIdRules** | Build rules in temp object, only assign to `docIdRules` on full success. Add safety checks for missing/invalid error entries. |
| 7.18 | **Fix Open Submissions logic** | Change to explicitly read `Submission_Closed` for `NO`/`0`. Only docs with `Submission_Closed='NO'` count as open. Null/empty treated as unknown. |
| 7.19 | **Fix Approval Rate calculation** | Numerator = unique docs with APP/AWC/INFO/VOID codes. Denominator = total unique valid Document_IDs. |
| 7.20 | **Align detail table columns to CSV** | Replace custom display names with exact CSV column names (`Document_ID`, `Submitted_By`, `Latest_Approval_Code`, etc.). Remove computed columns (Days Overdue, Status, Category). |
| 7.21 | **Add Review >30 Days KPI** | 6th KPI: unique docs with `Duration_of_Review > 30`. Detail table sorted by duration. |
| 7.22 | **Add Delay >30 Days KPI** | 7th KPI: unique docs with `Delay_of_Resubmission > 30`. Detail table sorted by delay. |
| 7.23 | **Add unique doc counts to status bar** | Show `Unique Docs: X (Valid) / Y (Total)` in status bar. |
| 7.24 | **Fix JS syntax bug in click handler** | Restore missing closing brackets that caused entire script to fail silently. |

**Features (v2.1 additions):**
- **7 KPI Cards:** Total Documents, Open Submissions, Overdue, Approval Rate, Awaiting Response, Review >30 Days, Delay >30 Days — all per unique valid Document_ID
- **CSV-column detail tables:** All tables use exact CSV column names; no computed columns
- **Status bar:** Shows valid/total unique document counts
- **Open Submissions:** Explicitly reads `Submission_Closed='NO'`
- **Approval Rate:** APP+AWC+INFO+VOID over total unique valid docs
- **Awaiting Response:** Includes docs with no approval code (not yet reviewed)

#### Risks & Mitigation (v2.1 additions)

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| `Validation_Errors` column missing from CSV | Low | Medium | Fallback uncertain-values blocklist preserved; basic checks still applied |
| `data_error_config.json` fetch fails (file:// protocol) | Medium | Low | Default rules used (all Document_ID error codes assumed applicable) |
| Error code format changes in pipeline | Low | Medium | Codes loaded dynamically from config at init; no hardcoded codes in JS |
| JS syntax error breaks entire dashboard | Low | High | All changes syntax-validated with balanced braces check |

#### Potential Issues to Address in Future
- Add date range filter (start/end date pickers)
- Add export filtered data to CSV
- Add drill-down from chart segments to detail table
- Add per-project and per-facility sub-pages
- Real-time updates via WebSocket for live pipeline runs

#### Success Criteria (v2.1)
- [x] `data_error_config.json` loaded on init, Document_ID error codes extracted
- [x] `isValidDocId()` checks `Validation_Errors` column instead of reimplementing validation logic
- [x] Pre-filter at load time removes invalid IDs before KPI/table computation
- [x] Open Submissions explicitly checks `Submission_Closed='NO'`
- [x] Approval Rate = APP+AWC+INFO+VOID / total unique valid Document_IDs
- [x] Awaiting Response includes null/empty approval codes + PEN/PENDING
- [x] Detail tables use exact CSV column names; no computed columns
- [x] Review >30 Days KPI with sorted detail table
- [x] Delay >30 Days KPI with sorted detail table
- [x] Status bar shows unique valid/total doc counts
- [x] All 10 `isValidDocId()` call sites pass row as second argument
- [x] Robust fallback: rules built in temp object, defaults preserved on failure
- [x] JS syntax validated (balanced braces)
- [x] Workplan, issue log, and update log updated

---

#### v2.2 Revision Scope

**Status:** ✅ COMPLETED  
**Data Sources:** `../output/processed_dcc_universal.csv`, `../config/schemas/data_error_config.json`, `../config/schemas/approval_code_schema.json`

##### Issues Identified

| ID | Issue | Root Cause | Impact |
| :--- | :--- | :--- | :--- |
| A | Overdue detail table: string sort on date + no dedup per doc | `.localeCompare()` on date strings; no `Document_ID` dedup | Wrong sort order; duplicate rows for multi-row docs |
| B | Delay detail table: first-seen row, not max delay per doc | `seen.has()` stops at first row encountered | Understates delay for multi-submission documents |
| C | Awaiting detail table: uses first row, not latest submission row | `seen.has()` stops at first row; may not be latest | Wrong `Latest_Approval_Code` for multi-submission docs |
| D | Hardcoded approval code arrays in `computeKPIs` and detail tables | `['PEN','PENDING']`, `['APP','AWC','INF','VOID',...]` literals in JS | Breaks silently if pipeline schema codes change |
| E | Approval rate trend chart is row-level; KPI tile is doc-level | Trend counts rows per month; KPI counts unique docs | Inconsistent percentages between chart and KPI |
| F | Overdue detail table shows all matching rows, not one per doc | No dedup in `showDetailOverdue` | Multi-row docs appear multiple times |
| G | Open/awaiting detail tables missing `Resubmission_Plan_Date` and `Delay_of_Resubmission` | Columns not included in table definition | Missing actionable context for follow-up prioritisation |
| H | KPI card click handler uses positional array index | `actions[i]` maps by DOM order | Silently breaks if cards are reordered or added |

##### v2.2 Sub-Tasks

| ID | Task | Detail | Priority |
| :--- | :--- | :--- | :--- |
| 7.25 | **Fix overdue table — date sort + dedup** | Deduplicate `showDetailOverdue` by `Document_ID` (keep row with oldest `Resubmission_Plan_Date`). Sort ascending by `Resubmission_Plan_Date` using `new Date()` comparison — oldest plan date first = most overdue first. | High |
| 7.26 | **Fix delay table — max delay per doc** | Rewrite `showDetailDelay` to aggregate all rows per `Document_ID` and show the maximum `Delay_of_Resubmission` value. Sort descending by max delay. | High |
| 7.27 | **Fix awaiting table — use latest submission row** | Rewrite `showDetailAwaiting` to resolve the latest submission row per doc (where `Submission_Date == Latest_Submission_Date`) before reading `Latest_Approval_Code`. Ensures current approval state is shown, not an arbitrary earlier row. | High |
| 7.28 | **Load approval codes from `approval_code_schema.json`** | Add `loadApprovalCodes()` on init alongside `loadDocIdRules()`. Derive `terminalCodes` (Approved/Void/For Information), `pendingCodes` (PEN), and `approvedCodes` (APP/AWC/INF/VOID) dynamically from schema. Replace all hardcoded code arrays in `computeKPIs`, `showDetailAwaiting`, and the trend chart. Fallback to current hardcoded arrays if fetch fails. | Medium |
| 7.29 | **Fix approval rate trend chart — doc-level** | Change trend chart to count unique approved docs per month vs total unique docs per month, consistent with the KPI tile. Update chart subtitle to `(per unique document, by month)`. | Medium |
| 7.30 | **Add plan date and delay to open/awaiting tables** | Add `Resubmission_Plan_Date` and `Delay_of_Resubmission` columns to `showDetailOpen` and `showDetailAwaiting`. Resolve values from the latest submission row per doc (`Submission_Date == Latest_Submission_Date`). Sort awaiting table by `Delay_of_Resubmission` descending. | Medium |
| 7.31 | **Replace positional KPI click handler with `data-kpi` attributes** | Add `data-kpi="allDocs|open|overdue|approval|awaiting|longReview|delay"` attribute to each KPI card `div` in HTML. Rewrite click handler to look up handler by attribute value, not array index. | Low |

##### Features (v2.2 additions)
- **Overdue table:** One row per unique document, sorted oldest plan date first (most overdue first), using proper date comparison
- **Delay table:** Maximum `Delay_of_Resubmission` per document, not first-seen row
- **Awaiting table:** Resolved from latest submission row per document; includes `Resubmission_Plan_Date` and `Delay_of_Resubmission` columns sorted by delay descending
- **Open table:** Includes `Resubmission_Plan_Date` and `Delay_of_Resubmission` from latest submission row
- **Schema-driven approval codes:** `approval_code_schema.json` loaded on init; all KPI and detail table logic uses dynamic code lists
- **Trend chart:** Doc-level approval rate per month, consistent with KPI tile
- **Robust KPI click wiring:** `data-kpi` attribute-based dispatch, not positional index

##### Risks & Mitigation (v2.2)

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| `approval_code_schema.json` fetch fails on `file://` protocol | Medium | Low | Fallback to current hardcoded arrays; behaviour unchanged from v2.1 |
| `Latest_Submission_Date` column absent from CSV | Low | Medium | Fall back to computing `max(Submission_Date)` per `Document_ID` client-side |
| Date parsing fails for non-ISO date strings in `Resubmission_Plan_Date` | Low | Low | Wrap in `new Date()` with `isNaN` guard; treat invalid dates as oldest (sort to end) |
| Schema approval code structure changes between pipeline versions | Low | Medium | Validate required fields on load; fallback to hardcoded arrays |

##### Success Criteria (v2.2)
- [x] `approval_code_schema.json` loaded on init; `terminalCodes`, `pendingCodes`, `approvedCodes` derived dynamically
- [x] `showDetailOverdue` deduplicates by `Document_ID`; sorted oldest `Resubmission_Plan_Date` first using `Date` comparison
- [x] `showDetailDelay` shows maximum `Delay_of_Resubmission` per doc; sorted descending
- [x] `showDetailAwaiting` resolves `Latest_Approval_Code` from latest submission row per doc
- [x] `showDetailOpen` and `showDetailAwaiting` include `Resubmission_Plan_Date` and `Delay_of_Resubmission` columns
- [x] Approval rate trend chart uses unique doc counts per month, not row counts
- [x] KPI card click handlers use `data-kpi` attribute dispatch, not positional index
- [x] All fallbacks verified: missing schema files, missing CSV columns, invalid date strings
- [x] No regressions in existing v2.1 features (schema-driven validation, 7 KPIs, 4 charts, filters, status bar)
- [x] JS syntax validated (balanced braces)
- [x] Workplan, issue log, and update log updated on completion


---

### Phase 8: Common JSON Tools

**Timeline:** Days 9–10  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/common_json_tools.html` (2,567 lines)

#### What Was Created

General-purpose JSON inspector, formatter, and schema validator.

**Features:**
- JSON paste / file load
- Tree view with collapsible nodes
- JSON path query (JSONPath)
- Schema validation against loaded schema
- Format / minify / diff
- Copy to clipboard

#### Risks & Mitigation
- **Risk:** Extremely large JSON files cause memory issues. **Mitigation:** Warn at >5MB input; truncate display at depth 10.
- **Risk:** Recursive/circular JSON objects cause infinite loops. **Mitigation:** Cycle detection in tree renderer.

#### Success Criteria
- [x] Tree view displays JSON correctly
- [x] JSONPath queries return correct results
- [x] Format/minify toggles work
- [x] Schema validation produces meaningful errors

---

### Phase 9: Excel → Schema Generator

**Timeline:** Days 10–11  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/excel_to_schema.html` (2,734 lines)

#### What Was Created

Upload an Excel file and auto-generate a schema JSON skeleton from its headers.

**Features:**
- Excel file drag-and-drop
- Sheet selector (multi-sheet Excel)
- Header row selector (pick which row contains headers)
- Auto-detect column types (date, numeric, categorical, string)
- Generate schema JSON with aliases, data_type, required, allow_null
- Copy / download generated schema

**Library:** XLSX.js 0.18.5

#### Risks & Mitigation
- **Risk:** Auto-detected types are wrong for ambiguous columns. **Mitigation:** Allow manual type override per column before generation.
- **Risk:** Non-standard Excel files (merged cells, formulas). **Mitigation:** Flatten merged cells; evaluate formulas via XLSX.js.

#### Success Criteria
- [x] Excel file loads correctly
- [x] Sheet selector shows all sheets
- [x] Column types auto-detected correctly
- [x] Generated schema valid against schema standard

---

### Phase 10: AI Analysis Dashboard — v1.5

**Timeline:** Days 12–14  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/ai_analysis_dashboard.html` (1,503 lines)

#### What Was Created

A full DCC design system-compliant dashboard that consumes `ai_insight_summary.json`, `ai_insight_trace.json`, `ai_insight_report.md`, `data_error_config.json`, and `processed_dcc_universal.xlsx` to provide interactive AI insight exploration with risk drill-down, evidence trace, trends visualization, markdown report viewing, a paginated data table of 11,822 pipeline rows, and a local LLM chat assistant (powered by Ollama) with model selection, markdown rendering, and in-memory data filtering.

**Features:**

- **DCC Shell Compliance:** Full VS Code layout — `.dcc-titlebar` (logo, breadcrumb, 5-theme picker), `.dcc-iconbar` (panel toggle icons with divider), `.dcc-sidebar-left` (run metadata accordion), `.dcc-content` (4-tab content area), `.dcc-panel-right` (settings/help/chat side panel), `.dcc-statusbar`. Layout toggle button cycles sidebar states. Left sidebar resizable via drag handle (min 120px, max 600px). Right sidebar shows help, settings, or AI chat panel via icon bar toggles.
- **5-Theme Picker:** Dark, Light, Sky, Ocean, Presentation — saved to `localStorage`, immediate apply, correct theme dot colors.
- **Data Loader:** `fetch()` with `file://` auto-detection and FileReader fallback. Loads `ai_insight_summary.json`, `ai_insight_trace.json`, `ai_insight_report.md`, `data_error_config.json`, and `processed_dcc_universal.xlsx`. Graceful degradation per file — partial data renders partially. Progress indicator during load. Error/loading/empty states per data source.
- **KPI Tiles Row:** Risk level badge (color-coded), total rows processed, data health score (%), total errors detected, affected rows count, model/provider info. Abbreviated large numbers (1.2K, 4.6K). Dynamic model name from Ollama.
- **Risk Findings Panel:** 4-tab content area (Risk Findings, Trends & Recs, Report, Data Table). Color-coded risk cards (CRITICAL/HIGH/MEDIUM/WARNING/LOW) with left border accent by severity. Each card shows severity badge, title, description, affected rows, error codes list (with message from `data_error_config.json`), columns, recommendation. Cards expand on click. Sortable by severity or row count via dropdown. "View Trace" button opens evidence modal with column-level error counts and sample rows. "🤖 Analyze" button pre-fills AI chat with schema-driven prompt from `data_error_config.json`.
- **Evidence Drill-Down Modal:** Shows error code, phase, total occurrences, affected columns with error counts, sample rows. Data sourced from `ai_insight_trace.json` via `traceLookup` indexed by `error_code`.
- **Trends Panel:** Pattern cards with frequency count and phase badges. Phase badges clickable to filter related risks.
- **Recommendations Panel:** Ordered list with bullet numbers.
- **Markdown Report Viewer:** 3rd tab renders `ai_insight_report.md` inline via `marked.js` CDN with DCC-themed styling.
- **Data Table Tab:** 4th tab (📊 Data Table) loads `processed_dcc_universal.xlsx` via SheetJS CDN. Paginated table (50 rows/page, First/Prev/Next/Last navigation) with 45 columns × 11,822 rows. Sticky header, alternating row colors, row/column count info. Tab-bar scrollbar made visible for 4-tab overflow.
- **Ollama Chat Assistant (v1.2–v1.5):** Right side panel with:
  - **Model auto-detection:** `GET /api/tags` on init detects all installed Ollama models. Retries every 20s if offline. Non-blocking — all other features work without it.
  - **Model selector dropdown:** Switch between all installed models in chat header. KPI card, sidebar metadata, and status bar reflect selected model.
  - **API:** Uses `/api/chat` (not `/api/generate`) with `messages: [{role, content}]` format.
  - **Markdown responses:** Model responses rendered via `marked.parse()` with GFM table support.
  - **FILTER: command:** Model can request `FILTER: column operator value` to query the in-memory 11,822-row dataset. Dashboard executes filter and returns matching rows as a markdown table.
  - **Schema-driven AI prompts:** `data_error_config.json` entries contain `ai_prompt` field with placeholders (`{code}`, `{title}`, `{severity}`, `{description}`, `{affected_rows}`, `{columns}`, etc.). Clicking "🤖 Analyze" on a risk card pre-fills the chat input (user reviews then sends).
  - **System prompt:** Built from `ai_insight_summary.json` context — risk_level, executive_summary, top_risks (truncated), trends, recommendations, evidence_links, column names + 5 sample rows.
  - **Multi-line input:** `<textarea rows="2">` with auto-grow via JS scrollHeight technique, `overflow: hidden`, capped at 400px. Chat-input-row resizable by dragging a 4px handle between messages and input area. Enter sends, Shift+Enter adds newline. Send button below textarea, right-aligned.
  - **Chat message ordering:** Uses local DOM reference (`document.createElement` + `querySelector`) instead of duplicate IDs to fix ordering bug.

#### Sub-Tasks (v1.0–v1.5)

| ID | Task | Detail | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| 10.1 | **DCC shell compliance** | Replace inline `<nav>` with full VS Code layout. Titlebar (logo, breadcrumb, theme picker), iconbar (left/right panel toggle icons with divider), left sidebar (run metadata accordion), content area, right sidebar (settings/help/chat), statusbar. Add layout toggle button. Resizable left sidebar with drag handle. Wire icon bar buttons to toggle panels. | High | ✅ |
| 10.2 | **Data loader** | `fetch()` all 3 insight files + `data_error_config.json` + `processed_dcc_universal.xlsx`. Auto-detect `file://` protocol with FileReader fallback. `traceLookup` index by `error_code`, `errorCodeLookup` by `code`. Graceful degradation per file. | High | ✅ |
| 10.3 | **Theme picker** | 5-theme picker in title bar with localStorage persistence. Correct theme dot colors matching CSS backgrounds. Immediate apply. | High | ✅ |
| 10.4 | **KPI tiles row** | KPI row: risk level badge, total rows, health score, error count, affected rows, model/provider. Abbreviated numbers. Dynamic model name from Ollama. | High | ✅ |
| 10.5 | **Risk findings panel** | Color-coded risk cards (CRITICAL/HIGH/MEDIUM/WARNING/LOW) with left border accent. Severity badge, title, description, affected rows, error codes with messages from config, columns, recommendation. Expandable. Sortable by severity or rows. | High | ✅ |
| 10.6 | **Evidence drill-down modal** | "View Trace" button on risk cards opens modal with error code, phase, occurrences, affected columns with counts, sample rows. | High | ✅ |
| 10.7 | **Trends panel** | Pattern cards with frequency, phase badges. Click-to-filter related risks. | Medium | ✅ |
| 10.8 | **Recommendations panel** | Ordered recommendation list. | Medium | ✅ |
| 10.9 | **Markdown report viewer** | 3rd tab renders `ai_insight_report.md` via `marked.js` with DCC-themed styling. | Medium | ✅ |
| 10.10 | **Export to CSV** | Export risk findings to CSV via Blob download. | Low | ✅ |
| 10.11 | **Error/loading/empty states** | Loading skeleton during data load. Error card with retry per file. Empty state when no insight files exist. | Medium | ✅ |
| 10.12 | **Run metadata sidebar** | Left sidebar accordion: Run ID, timestamp, model/provider, fallback status, risk badge, health score, errors, affected rows. | Medium | ✅ |
| 10.13 | **Status bar** | Overall status, loaded files count, risk level badge, version. Ollama model name when connected, "Offline" when not. | Low | ✅ |
| 10.14 | **Ollama chat assistant (v1.1)** | Chat panel connecting to local Ollama. Build context prompt from summary JSON. Detect availability via `/api/tags`. Send button + Enter-to-submit. Model name and status in header. | Medium | ✅ |
| 10.15 | **API fix + model detection (v1.2)** | Changed from `/api/generate` (404) to `/api/chat`. Store model list from `/api/tags`. Auto-select llama3/llama or first model. Retry every 20s if offline. Dynamic model list in `updateChatUI()`. | Medium | ✅ |
| 10.16 | **Data table tab (v1.2)** | 4th tab loading `processed_dcc_universal.xlsx` via SheetJS CDN. Paginated (50/page, First/Prev/Next/Last). 45 columns × 11,822 rows. Sticky header, alternating colors. Tab-bar scrollbar visible. | Medium | ✅ |
| 10.17 | **Model selector + centralized display (v1.3)** | Dropdown `<select>` in chat header switching between all installed models. `updateStatusBar()` centralizes display — KPI card, sidebar metadata, and status bar reflect active model. | Medium | ✅ |
| 10.18 | **Chat markdown + FILTER: command (v1.3)** | Model responses rendered via `marked.parse()` with GFM table CSS. Regex detects `FILTER: col operator val` in response, executes against `excelRows` in-memory, returns matching rows table. | Medium | ✅ |
| 10.19 | **Chat message ordering fix (v1.3)** | Replaced duplicate `id="streamingText"` with local `document.createElement('div')` + `textSpan` reference — each response writes to its own DOM node. | Medium | ✅ |
| 10.20 | **Schema-driven AI prompts (v1.4)** | Added `ai_prompt` field to 5 error codes in `data_error_config.json` with replaceable placeholders. "🤖 Analyze" button on expanded risk cards pre-fills chat input. `riskAnalyze()` looks up prompt template, replaces placeholders, opens chat panel, focuses input. | High | ✅ |
| 10.21 | **Multi-line input + resizable row (v1.5)** | `<textarea>` replaces `<input type="text">`. Auto-grow via JS scrollHeight. Enter sends, Shift+Enter newline. Drag handle between messages and input row for height adjustment. Send button below textarea. | Low | ✅ |

---

## 6. Delivery Sequence

| Step | Deliverable | Depends On | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `dcc-design-system.css` | — | Critical | ✅ Complete |
| 2 | `pipeline_dashboard.html` (v3.0) | 1 | High | ✅ Complete |
| 3 | `excel_explorer_pro.html` | 1 | High | ✅ Complete |
| 4 | `error_diagnostic_dashboard.html` (v2.0) | 1, 2 | High | ✅ Complete |
| 5 | `schema_manager.html` | 1 | High | ✅ Complete |
| 6 | `log_explorer_pro.html` | 1 | High | ✅ Complete |
| 7 | `submittal_dashboard.html` (v2.1) | 1, 3 | Medium | ✅ Complete |
| 8 | `common_json_tools.html` | 1 | Medium | ✅ Complete |
| 9 | `excel_to_schema.html` | 1 | Medium | ✅ Complete |
| 10 | `ai_analysis_dashboard.html` (Phase 10 v1.5) | 1 | Medium | ✅ Complete |

---

## 7. Success Criteria

- [x] `dcc-design-system.css` created and imported by all tools
- [x] All tools use `--font-ui: Inter` and `--font-mono: JetBrains Mono`
- [x] All tools use the DCC dark background palette (`--bg: #0d1117`)
- [x] All tools use `--accent: #2f81f7` as primary action colour
- [x] All tools use the shared status colour palette (success/warning/danger/info)
- [x] All tools share the same top navigation bar component
- [x] All tools are self-contained single HTML files (no server required)
- [x] All tools load data from `dcc/output/` or `dcc/config/schemas/` via FileReader or fetch
- [x] Pipeline Dashboard connects to `error_dashboard_data.json`
- [x] Excel Explorer Pro handles `Validation_Errors` and `Data_Health_Score` columns
- [x] Phase 7 v2.0 revision: CSV data loading, dynamic KPIs, data-driven charts, dynamic filters, overdue table
- [x] Phase 7 v2.1 revision: 5th KPI (Awaiting Response), schema-driven validation via Validation_Errors column + data_error_config.json, pre-filter at load time
- [x] Phase 4 v2.0 revision: full DCC shell compliance, dynamic data loader, resizable panels, icon bar toggling, nav tree, ui_help.json loading, global search, dynamic charts — **COMPLETED** (8 bugs documented, 4 remaining items for future)
- [x] Phase 7 v2.2 revision: overdue/delay/awaiting table fixes, schema-driven approval codes, trend chart doc-level consistency, open/awaiting tables enriched with plan date and delay — **COMPLETED**
- [x] Phase 10 v1.5 complete and functional: DCC shell, data loader, 5 themes, KPI row, risk cards with evidence, trends & recs, report viewer, data table, Ollama chat with model selector, schema-driven AI prompts, FILTER: command
- [x] All 10 phases complete and functional
- [x] Comprehensive documentation provided (implementation plan, user guide, completion report)
- [x] Cross-browser compatibility verified (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

---

## 8. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| Browser incompatibility with ES6+ features | Low | Medium | Target Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ |
| Large data files (>50MB) cause performance issues | Medium | Medium | Virtual scrolling; recommended max 50MB; clear user warning |
| Schema file structure changes between pipeline versions | Low | High | Validate required fields on load; fallback to empty/default state |
| Users modify schema JSON incorrectly via Schema Manager | Medium | Medium | Client-side validation; warn on structural changes; no auto-save |
| CDN (Chart.js, Papa Parse) downtime | Low | Low | Self-contained HTML; cache via service worker if deployed |
| FileReader API limitations in older browsers | Low | Low | Graceful degradation with text-only upload fallback |

---

## 9. Known Limitations & Future Issues

### Current Limitations
1. **File Size**: Recommended max 50MB for optimal performance
2. **Real-time Updates**: Requires manual refresh or polling (no WebSocket yet)
3. **Data Persistence**: Only browser localStorage available (no server-side DB)
4. **Offline Mode**: Requires pre-loaded data files
5. **Mobile**: Optimized for desktop/tablet — limited mobile support
6. **Multi-user**: No authentication or collaborative editing

### Issues to Address in Future
1. Add WebSocket/SSE for real-time pipeline updates
2. Implement server-side data persistence (DuckDB)
3. Add user authentication and authorization
4. Create mobile-responsive versions
5. Add collaborative editing features
6. Implement data caching strategies
7. Add advanced analytics features
8. Create API documentation

### Phase 7 — Addressed in v2.2 (pending approval)
- Overdue table dedup + date sort fix (Issue A/F)
- Delay table max aggregation (Issue B)
- Awaiting table latest-row resolution (Issue C)
- Schema-driven approval codes from `approval_code_schema.json` (Issue D)
- Trend chart doc-level consistency (Issue E)
- Open/awaiting tables enriched with plan date and delay (Issue G)
- KPI click handler `data-kpi` attribute dispatch (Issue H)

### Phase 7 — Remaining future items
- Add date range filter (start/end date pickers)
- Add export filtered data to CSV
- Add drill-down from chart segments to detail table
- Add per-project and per-facility sub-pages
- Real-time updates via WebSocket for live pipeline runs

---

## 10. References

### Workplan & Reports
- Project master plan: `../../../project_setup/project-plan.md`
- Consolidated report: `web_interface_report.md`
- User guide: `../../../ui/user_guide.md`

### Source Files
- Design system: `dcc/ui/dcc-design-system.css`
- Pipeline Dashboard: `dcc/ui/pipeline_dashboard.html`
- Excel Explorer Pro: `dcc/ui/excel_explorer_pro.html`
- Error Diagnostic Dashboard: `dcc/ui/error_diagnostic_dashboard.html`
- Schema Manager: `dcc/ui/schema_manager.html`
- Log Explorer Pro: `dcc/ui/log_explorer_pro.html`
- Submittal Tracker Dashboard: `dcc/ui/submittal_dashboard.html`
- Common JSON Tools: `dcc/ui/common_json_tools.html`
- Excel → Schema Generator: `dcc/ui/excel_to_schema.html`
- AI Analysis Dashboard: `dcc/ui/ai_analysis_dashboard.html`

### Data Sources Consumed
- `dcc/output/error_dashboard_data.json`
- `dcc/output/processing_summary.txt`
- `dcc/output/processed_dcc_universal.csv`
- `dcc/config/dcc_register_enhanced.json`
- `dcc/config/schemas/*.json`
- `dcc/Log/debug_log.json`
- `dcc/Log/issue_log.md`
- `dcc/Log/update_log.md`
- `dcc/Log/test_log.md`
- `dcc/output/ai_insight_summary.json`
- `dcc/output/ai_insight_trace.json`
- `dcc/output/ai_insight_report.md`

### Standards
- `agent_rule.md` — project governance and workplan standards
