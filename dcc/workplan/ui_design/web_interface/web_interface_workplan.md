# Web Interface Workplan — Universal UI Toolkit

**Document ID:** WP-UI-001  
**Current Version:** 3.0  
**Status:** COMPLETED  
**Last Updated:** 2026-05-14  
**Lead:** Franklin Song

---

## Revision Control & Version History

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 1.0 | 2026-04-18 | Franklin Song | Initial workplan — 8 UI tools + design system delivered. |
| 2.0 | 2026-05-13 | Franklin Song | Restructured as independent workplan. Each HTML deliverable now a standalone phase (Phases 1–9). Removed external phase identity. |
| 3.0 | 2026-05-14 | Franklin Song | Phase 2 revision: Pipeline Dashboard updated from static mockup to live data-driven dashboard. Added 8 sub-tasks (data loader, dynamic KPIs, real pipeline stages, wired buttons, dynamic status bar, activity log, fixed theme dots). |

---

## 1. Objective

Build a cohesive suite of browser-based tools under `dcc/ui/` for data visualization, schema management, pipeline monitoring, and AI-assisted analysis. All tools share a unified design system to ensure a consistent professional experience. The tools consume processed pipeline outputs (CSV, Excel, JSON), schema files, and log data, providing interactive interfaces for end users without requiring a server.

---

## 2. Scope Summary

| ID | Detail | Category | Status |
| :--- | :--- | :--- | :--- |
| 1 | DCC UI Design System — shared CSS with 5 themes, 25+ components | Foundation | ✅ Completed |
| 2 | Pipeline Dashboard — run status, KPIs, output links | Monitoring | ✅ Completed |
| 3 | Excel Explorer Pro — data loading, filtering, validation highlighting | Exploration | ✅ Completed |
| 4 | Error Diagnostic Dashboard — error viz, heatmap, drill-down | Diagnostics | ✅ Completed |
| 5 | Schema Manager — browse, inspect, edit schema files | Management | ✅ Completed |
| 6 | Log Explorer Pro — multi-format log browser with search | Logging | ✅ Completed |
| 7 | Submittal Tracker Dashboard — analytics KPI, charts, overdue tracking | Analytics | ✅ Completed |
| 8 | Common JSON Tools — tree viewer, formatter, JSONPath, validation | Utilities | ✅ Completed |
| 9 | Excel → Schema Generator — auto-generate schema from Excel headers | Generation | ✅ Completed |

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
- [x] No hardcoded mock data remains in the script

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

### Phase 4: Error Diagnostic Dashboard

**Timeline:** Days 4–5  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/error_diagnostic_dashboard.html` (2,634 lines)

#### What Was Created

Visualise validation errors and data health from `error_dashboard_data.json`.

**Features:**
- Error summary by phase (P1, P2, P2.5, P3)
- Error code frequency bar chart
- Per-column error heatmap
- Row-level error drill-down table
- Data health score distribution histogram
- Filter by error code, column, severity
- Export error report to CSV

**Library:** Chart.js 3.9.1

#### Risks & Mitigation
- **Risk:** Heatmap becomes unreadable with many columns. **Mitigation:** Scrollable heatmap with sticky row labels.
- **Risk:** JSON data structure changes between pipeline versions. **Mitigation:** Validate required fields on load; fallback to empty state.

#### Success Criteria
- [x] All 4 chart types render correctly
- [x] Drill-down shows row-level error details
- [x] Filters narrow data correctly
- [x] Export generates valid CSV error report

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

### Phase 7: Submittal Tracker Dashboard

**Timeline:** Days 8–9  
**Status:** ✅ COMPLETED  
**File:** `dcc/ui/submittal_dashboard.html` (2,923 lines)

#### What Was Created

Visual analytics dashboard for the processed DCC register data.

**Features:**
- Summary KPI row: total documents, open submissions, overdue resubmissions, approval rate
- Submission timeline chart (by month)
- Approval status breakdown donut chart
- Overdue resubmission list table
- Document status by discipline bar chart
- Submission trend chart
- Filter by project code, facility, discipline, date range
- Load from processed CSV output

**Library:** Chart.js 3.9.1

#### Risks & Mitigation
- **Risk:** Missing date columns break timeline charts. **Mitigation:** Graceful fallback with message indicating required columns.
- **Risk:** Empty data results in misleading charts. **Mitigation:** Empty state with "No data available" message.

#### Success Criteria
- [x] All 4 KPI tiles display correctly
- [x] All 4 chart types render from loaded data
- [x] Filters narrow the data set
- [x] Overdue resubmission table sorts by date

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

## 6. Delivery Sequence

| Step | Deliverable | Depends On | Priority | Status |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `dcc-design-system.css` | — | Critical | ✅ Complete |
| 2 | `pipeline_dashboard.html` (v3.0) | 1 | High | ✅ Complete |
| 3 | `excel_explorer_pro.html` | 1 | High | ✅ Complete |
| 4 | `error_diagnostic_dashboard.html` | 1, 2 | High | ✅ Complete |
| 5 | `schema_manager.html` | 1 | High | ✅ Complete |
| 6 | `log_explorer_pro.html` | 1 | High | ✅ Complete |
| 7 | `submittal_dashboard.html` | 1, 3 | Medium | ✅ Complete |
| 8 | `common_json_tools.html` | 1 | Medium | ✅ Complete |
| 9 | `excel_to_schema.html` | 1 | Medium | ✅ Complete |

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
- [x] All 9 phases complete and functional
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

### Standards
- `agent_rule.md` — project governance and workplan standards
