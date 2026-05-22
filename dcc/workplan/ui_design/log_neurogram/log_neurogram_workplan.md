# Log Neurogram Network — Interactive DCC Log Explorer

**Document ID:** WP-UI-LOG-001  
**Current Version:** 1.4  
**Status:** ✅ COMPLETE  
**Last Updated:** 2026-05-21  
**Lead:** Franklin Song

---

## Revision Control & Version History

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 1.0 | 2026-05-21 | System | Initial workplan — proposed interactive neurogram network graph to explore DCC log data (issues, updates, tests, files, phases, error codes, engines, workplans). Single standalone HTML file, Vis.js force-directed graph, DCC shell layout, file:// compatible. |
| 1.1 | 2026-05-21 | System | Phase 1 expanded: added parsing of all 159 files under `dcc/workplan/` across 15 domain folders. New entity types: Workplan (from workplan files), Report (from reports/ subfolders). Updated entity counts, edge types, extraction rules, and success criteria. |
| 1.2 | 2026-05-21 | System | Updated graph data output path from `dcc/output/log_neurogram/dcc_log_graph.json` to `dcc/output/dcc_log_graph.json` (project root output folder). |
| 1.3 | 2026-05-21 | System | Updated `log_neurogram.html` output path to `dcc/ui/` folder (alongside other UI files). Updated `ui_help.json` to reference existing file at `dcc/ui/ui_help.json` (append, not create). |
| 1.4 | 2026-05-21 | System | All phases complete. Graph data generated (588 nodes, 341 edges). HTML webpage built with DCC shell layout, Vis.js force graph, tree view, filtering, search, timeline, export. ui_help.json updated with neurogram entries. |

---

## 1. Objective

Create a standalone interactive webpage that visualizes the complete DCC project history as a neurogram-style network graph. Compacts all 4 log files (`issue_log.md`, `update_log.md`, `test_log.md`, `gemini.md`) and all 159 workplan files under `dcc/workplan/` into a structured graph dataset (~350 nodes, ~700 edges) and provides an interactive explorer with force-directed layout, filtering, search, timeline animation, and detail panels. Zero server dependency — works via `file://` protocol.

---

## 2. Scope Summary

| ID | Detail | Category | Status |
| :--- | :--- | :--- | :--- |
| 1 | Parse 4 log files + 159 workplan files → extract entities (Issue, Update, Test, File, Phase, Error Code, Engine, Workplan, Report, Session) | Data Extraction | ✅ Complete |
| 2 | Generate `dcc_log_graph.json` — SSOT compacted graph data | Data Generation | ✅ Complete |
| 3 | Build `log_neurogram.html` — Vis.js force graph + DCC shell layout | UI Development | ✅ Complete |
| 4 | Update `ui_help.json` — add neurogram help/about/revision text | Documentation | ✅ Complete |
| 5 | Test via `file://` protocol — verify all interactions | Testing | ✅ Complete |
| 6 | Log issue + generate phase report | Logging & Reporting | ✅ Complete |

---

## 3. Index of Content

1. [Objective](#1-objective)
2. [Scope Summary](#2-scope-summary)
3. [Dependencies & Alignment](#4-dependencies--alignment)
4. [Implementation Phases](#5-implementation-phases)
   - [Phase 1: Data Extraction & Compaction](#phase-1-data-extraction--compaction)
   - [Phase 2: Graph Data Generation](#phase-2-graph-data-generation)
   - [Phase 3: Interactive Webpage Build](#phase-3-interactive-webpage-build)
   - [Phase 4: Help Data & Documentation](#phase-4-help-data--documentation)
   - [Phase 5: Testing & Verification](#phase-5-testing--verification)
   - [Phase 6: Logging & Reporting](#phase-6-logging--reporting)
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
| Log Files | `dcc/log/issue_log.md`, `update_log.md`, `test_log.md`, `gemini.md` | Primary data source — issues, updates, tests, sessions |
| Workplan Files | `dcc/workplan/` — 159 files across 15 domain folders | Workplan metadata, phases, scope, status, reports, references |
| DCC Design System | `dcc/ui/dcc-design-system.css` | Reuse existing CSS for shell layout, themes, panels, status bar |
| Vis.js Network | CDN: `https://unpkg.com/vis-network/standalone/vis-network.min.js` | Force-directed graph engine (no build step, single import) |
| SheetJS (optional) | CDN: `https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js` | Potential future: export graph data to Excel |

### Architecture Alignment

- Single standalone HTML file — no server, no build step, `file://` compatible
- SSOT graph data — `dcc_log_graph.json` drives all visualizations
- Schema-driven node/edge types — `node_types` and `edge_types` arrays define visual properties
- DCC shell layout — VS Code-style (title bar, icon bar, left/right sidebars, status bar) per `html_design_rule.md`
- 5 theme support — dark, light, sky, ocean, presentation (saved to localStorage)
- Follows `agent_rule.md` Section 8 (workplan), Section 9 (report), Section 11 (UI design), Section 13 (compact logs)
- Graph data in `dcc/output/dcc_log_graph.json` (SSOT); HTML in `dcc/ui/log_neurogram.html` (alongside existing UI tools); existing `dcc/ui/ui_help.json` updated with neurogram entries; `dcc/ui/dcc-design-system.css` reused
- Workplan in `dcc/workplan/ui_design/log_neurogram/` per workplan conventions

---

## 5. Implementation Phases

### Phase 1: Data Extraction & Compaction

**Timeline:** Day 1  
**Status:** ✅ COMPLETE

#### 1.1 Log File Parsing

Parse all 4 log files with regex/markdown parsing to extract structured entities:

| Entity Type | Est. Count | Source | Key Fields |
| :--- | :--- | :--- | :--- |
| Issue | ~32 | issue_log.md | id, title, status, date, severity, root_cause, files_changed[], related_issues[], rows_affected |
| Update | ~42 | update_log.md | id, date, summary, phases[], files_modified[], linked_issue, linked_test |
| Test | ~26 | test_log.md | id, date, result, scope, checks[], linked_issue, linked_update |
| Session | 3 | gemini.md | id |

#### 1.2 Workplan File Parsing

Parse all 159 files under `dcc/workplan/` across 15 domain folders:

| Domain Folder | Files | Workplans | Reports | Key Entities |
| :--- | :--- | :--- | :--- | :--- |
| `pipeline_architecture/` | ~30 | 5 | ~10 | WP-PIPE-SIMP-001, WP-PIPE-SSOT-001, barrel_pattern, context_validation, bootstrap_subworkplan |
| `error_handling/` | ~25 | 6 | ~8 | WP-DCC-EH-DATA-001, system_error, bootstrap_error, error_catalog, pipeline_messaging, module |
| `schema_processing/` | ~25 | 6 | ~15 | schema_consolidation, recursive_schema_loader, rebuild_schema, pipeline_integration, register_decoupling |
| `column_processing/` | ~12 | 1 | ~8 | business_logic_validation_workplan, column_update_logic, column_priority_reference, 8 phase reports |
| `ui_design/` | ~15 | 2 | 1 | web_interface_workplan, html_design_rule, data_explorer events |
| `ai_operations/` | ~8 | 1 | ~6 | ai_operations_workplan, phase5 sub-plans, 5 phase reports |
| `data_validation/` | ~7 | 3 | 0 | row_validation, col_validation, dcc_register_rule |
| `dcc_pipeline_stage/` | ~10 | 1 | 0 | stage-map, stages 1-9 |
| `maintenance/` | ~2 | 1 | ~1 | archive_cleanup_workplan |
| `document_id_handling/` | ~1 | 1 | 0 | document_id_handling_workplan |
| `initiation_engine/` | ~1 | 0 | 0 | project-setup-validation-guide |
| `project_setup/` | ~2 | 0 | ~1 | project-plan, project_plan_report |
| `code_quality/` | ~1 | 0 | 0 | (if present) |

**New Entity Types from Workplan Parsing:**

| Entity Type | Est. Count | Source | Key Fields |
| :--- | :--- | :--- | :--- |
| Workplan | ~15 | workplan *_workplan.md files | id, title, version, status, date, description, scope_summary[], phases[], sub_phases[], delivery_sequence[], references[] |
| Phase (workplan) | ~80 | workplan phase sections | workplan_id, phase_id, phase_name, status, timeline, tasks[], deliverables[], success_criteria[], risks[] |
| Report | ~50 | workplan reports/ subfolders | id, workplan_id, phase_id, title, date, status, findings[], files_modified[], test_results[] |

#### 1.3 Combined Entity Summary

| Entity Type | Est. Count | Source(s) | Key Fields |
| :--- | :--- | :--- | :--- |
| Issue | ~32 | issue_log.md | id, title, status, date, severity, root_cause, files_changed[], related_issues[], rows_affected |
| Update | ~42 | update_log.md | id, date, summary, phases[], files_modified[], linked_issue, linked_test |
| Test | ~26 | test_log.md | id, date, result, scope, checks[], linked_issue, linked_update |
| File | ~85 | all logs | path, engine, touch_count, first_seen, last_seen |
| Phase | ~110 | update_log.md + workplans | workplan_id, phase_id, status, report_path, tasks[], deliverables[] |
| Error Code | ~60 | issue_log.md, update_log.md | code, severity, description, status (introduced/fixed) |
| Engine | 8 | all logs | name, issue_count, file_count |
| Workplan | ~15 | workplan files | id, title, version, status, date, description, phase_count |
| Report | ~50 | workplan reports/ | id, workplan_id, phase_id, title, date, findings[] |
| Session | 3 | gemini.md | id |

#### 1.4 Edge Types (Relationships)

| Edge Type | Source → Target | Description |
| :--- | :--- | :--- |
| `resolved_by` | Issue → Update | Issue resolved by this update |
| `verified_by` | Update → Test | Update verified by this test |
| `tested_by` | Issue → Test | Issue tested by this test |
| `modifies` | Update → File | Update modifies this file |
| `affects` | Issue → File | Issue affects this file |
| `related_to` | Issue → Issue | Issues are related |
| `blocks` | Issue → Issue | One issue blocks another |
| `depends_on` | Issue → Issue | One issue depends on another |
| `implements` | Update → Phase | Update implements this phase |
| `belongs_to` | Phase → Workplan | Phase belongs to this workplan |
| `belongs_to` | Report → Workplan | Report belongs to this workplan |
| `belongs_to` | Report → Phase | Report belongs to this phase |
| `belongs_to` | File → Engine | File belongs to this engine |
| `introduces` | Issue → Error Code | Issue introduces this error code |
| `fixes` | Update → Error Code | Update fixes this error code |
| `session_for` | Session → Issue | Gemini session worked on this issue |
| `addresses` | Workplan → Issue | Workplan addresses this issue |
| `references` | Workplan → Workplan | Workplan references another workplan |
| `documented_by` | Phase → Report | Phase documented by this report |

#### 1.5 Extraction Rules

**Log Files:**
- Parse `## Issue # XXX` / `### Issue XXX-XXX` headers for issue boundaries
- Parse `<a id="...">` anchors for cross-reference IDs
- Extract `**File Changes:**` / `**Files Modified:**` sections for file lists
- Extract `**Link to Update Log:**` / `**Link to Issue Log:**` for relationships
- Parse `**Status:**` fields for entity status
- Parse dates from `[Date:]` or `## YYYY-MM-DD` headers
- Parse severity from context or explicit fields
- Parse error codes from `L3-L-V-0302`, `S-A-S-0504` patterns

**Workplan Files:**
- Parse `**Document ID:**` or `**Workplan ID**` or `# Workplan ID:` for workplan ID
- Parse `**Current Version:**` / `**Version**` for version
- Parse `**Status:**` for status (COMPLETED, PENDING APPROVAL, IN PROGRESS, etc.)
- Parse `**Last Updated:**` / `**Date**` for date
- Parse `## Revision Control` / `## Revision History` tables for version history
- Parse `## Scope Summary` tables for scope items (ID, detail, category, status, phase)
- Parse `## Implementation Phases` / `## Sub-Phases` for phase definitions
- Parse `## Delivery Sequence` tables for deliverables
- Parse `## References` / `## Links` for cross-workplan references
- Parse `**Related Issue:**` / `**Issue Ref**` for issue linkage
- Parse `reports/` subfolder for report files — extract filename as report ID
- Parse report filenames for phase mapping (e.g., `phase1_report.md` → Phase 1)
- Normalize paths: strip `dcc/workplan/` prefix, use relative paths

---

### Phase 2: Graph Data Generation

**Timeline:** Day 1  
**Status:** ✅ COMPLETE

#### Output: `dcc/output/dcc_log_graph.json`

Schema-driven flat structure with array-of-objects pattern:

```json
{
  "$schema": "https://dcc-pipeline.internal/schemas/log_neurogram/v1",
  "metadata": {
    "generated": "2026-05-21T...",
    "source_logs": ["issue_log.md", "update_log.md", "test_log.md", "gemini.md"],
    "source_workplans": "dcc/workplan/ (159 files, 15 domain folders)",
    "date_range": {"start": "2026-04-12", "end": "2026-05-21"},
    "counts": {"nodes": 350, "edges": 700, "issues": 32, "updates": 42, "tests": 26, "files": 85, "phases": 110, "error_codes": 60, "engines": 8, "workplans": 15, "reports": 50, "sessions": 3}
  },
  "node_types": [
    {"id": "issue", "label": "Issue", "color": "#e74c3c", "shape": "dot", "icon": "🔴"},
    {"id": "update", "label": "Update", "color": "#3498db", "shape": "square", "icon": "🔵"},
    {"id": "test", "label": "Test", "color": "#2ecc71", "shape": "diamond", "icon": "🟢"},
    {"id": "file", "label": "File", "color": "#f1c40f", "shape": "triangle", "icon": "🟡"},
    {"id": "phase", "label": "Phase", "color": "#9b59b6", "shape": "hexagon", "icon": "🟣"},
    {"id": "error_code", "label": "Error Code", "color": "#ecf0f1", "shape": "dot", "icon": "⚪"},
    {"id": "engine", "label": "Engine", "color": "#e67e22", "shape": "dot", "icon": "🟠"},
    {"id": "workplan", "label": "Workplan", "color": "#1abc9c", "shape": "star", "icon": "⭐"},
    {"id": "report", "label": "Report", "color": "#34495e", "shape": "database", "icon": "📄"},
    {"id": "session", "label": "Session", "color": "#95a5a6", "shape": "database", "icon": "💾"}
  ],
  "edge_types": [
    {"id": "resolved_by", "label": "Resolved By", "color": "#2ecc71", "dashes": false},
    {"id": "verified_by", "label": "Verified By", "color": "#3498db", "dashes": false},
    {"id": "tested_by", "label": "Tested By", "color": "#2ecc71", "dashes": true},
    {"id": "modifies", "label": "Modifies", "color": "#f1c40f", "dashes": false},
    {"id": "affects", "label": "Affects", "color": "#e74c3c", "dashes": false},
    {"id": "related_to", "label": "Related To", "color": "#95a5a6", "dashes": true},
    {"id": "blocks", "label": "Blocks", "color": "#e74c3c", "dashes": false, "arrows": "to"},
    {"id": "depends_on", "label": "Depends On", "color": "#f39c12", "dashes": false, "arrows": "to"},
    {"id": "implements", "label": "Implements", "color": "#9b59b6", "dashes": false},
    {"id": "belongs_to", "label": "Belongs To", "color": "#1abc9c", "dashes": true},
    {"id": "introduces", "label": "Introduces", "color": "#e74c3c", "dashes": false},
    {"id": "fixes", "label": "Fixes", "color": "#2ecc71", "dashes": false},
    {"id": "session_for", "label": "Session For", "color": "#95a5a6", "dashes": true},
    {"id": "addresses", "label": "Addresses", "color": "#1abc9c", "dashes": false, "arrows": "to"},
    {"id": "references", "label": "References", "color": "#95a5a6", "dashes": true, "arrows": "to"},
    {"id": "documented_by", "label": "Documented By", "color": "#34495e", "dashes": false}
  ],
  "nodes": [...],
  "edges": [...]
}
```

#### Node Sizing Rules

| Entity Type | Size Factor | Min | Max |
| :--- | :--- | :--- | :--- |
| Issue | severity weight (HIGH=30, MEDIUM=20, LOW=10) + rows_affected/1000 | 15 | 50 |
| Update | files_modified count | 10 | 30 |
| Test | result (PASS=15, FAIL=20, PARTIAL=18) | 10 | 25 |
| File | touch_count | 8 | 25 |
| Phase | fixed | 12 | 12 |
| Error Code | fixed | 6 | 6 |
| Engine | connection count | 25 | 40 |
| Workplan | phase_count | 15 | 30 |
| Report | fixed | 8 | 8 |
| Session | fixed | 12 | 12 |

---

### Phase 3: Interactive Webpage Build

**Timeline:** Day 2–3  
**Status:** ✅ COMPLETE

#### Output: `dcc/ui/log_neurogram.html`

#### DCC Shell Layout (per html_design_rule.md)

```
┌─────────────────────────────────────────────────────────────┐
│ Title Bar:  📊 Log Neurogram    🔍Search  🎨Theme  ☰Layout  │
├───┬───────────────────────────────────────────────┬─────────┤
│   │                                               │         │
│ I │              Main Content Area                │ R       │
│ C │              (Vis.js Force Graph)             │ I       │
│ O │                                               │ G       │
│ N │                                               │ H       │
│ S │                                               │ T       │
│   │                                               │         │
├───┤                                               ├─────────┤
│   │                                               │         │
│ L │              Left Sidebar                     │ Detail  │
│ E │              (Tree / Filter / Load)           │ Panel   │
│ F │                                               │ (node   │
│ T │                                               │  info)  │
│   │                                               │         │
├───┴───────────────────────────────────────────────┴─────────┤
│ Status Bar:  nodes:350 edges:700  filtered:all  v1.3       │
└─────────────────────────────────────────────────────────────┘
```

#### Icon Bar

| Position | Icon | Label | Panel |
| :--- | :--- | :--- | :--- |
| Left-Top 1 | 📊 | Graph | Main graph view (default) |
| Left-Top 2 | 🌳 | Tree | Hierarchical tree view |
| Left-Top 3 | 📂 | Load | File loading panel |
| Left-Top 4 | 🔍 | Filter | Filter panel |
| Left-Bottom 1 (after divider) | ⚙️ | Settings | Settings panel |
| Left-Bottom 2 | ❓ | Help | Help panel (loads dcc/ui/ui_help.json → neurogram.help) |
| Left-Bottom 3 | ℹ️ | About | About panel (loads dcc/ui/ui_help.json → neurogram.about) |
| Right-Bottom 1 | ℹ️ | Detail | Detail panel (node metadata) |

#### Interactive Features

| # | Feature | Detail |
| :--- | :--- | :--- |
| 1 | Force-directed graph | Vis.js Network, physics enabled, BarnesHut solver, smooth stabilization |
| 2 | Node styling | Color/shape/icon by type per `node_types` schema |
| 3 | Node sizing | Dynamic per sizing rules (Phase 2) |
| 4 | Click node | Right detail panel slides in — full metadata, linked nodes (clickable to navigate focus), file changes list |
| 5 | Hover edge | Highlight relationship type label, dim unrelated edges |
| 6 | Filter panel | Toggle node types on/off, filter by date range (slider), status, severity, engine |
| 7 | Search | Fuzzy search across all node labels, auto-focus and highlight matching nodes |
| 8 | Highlight path | Click node → highlight 1-hop, 2-hop, or full connected subgraph; dim rest |
| 9 | Time slider | Animate graph growth from 2026-04-12 → 2026-05-21, nodes appear chronologically |
| 10 | Cluster mode | Group nodes by engine, workplan, domain folder, or status; click cluster to expand |
| 11 | Tree view | Hierarchical tree: Domain → Workplan → Phase → Issue → Update → Test → Report; click node to focus graph |
| 12 | Export | Download current view as PNG; download filtered subgraph as JSON |
| 13 | Mini-map | Overview navigator in bottom-right corner |
| 14 | file:// support | Load `dcc_log_graph.json` via fetch() with FileReader fallback (folder picker) |
| 15 | Theme toggle | 5 themes (dark/light/sky/ocean/presentation), saved to localStorage |
| 16 | Layout toggle | Switch between single column, two columns, three columns |
| 17 | Resizable panels | Drag left/right panel edges to resize; min-width enforced |
| 18 | Collapsible panels | Click icon bar to collapse/expand panels |

#### Detail Panel Content

When a node is clicked, the right panel displays:

- **Header:** Node title, type badge, status badge
- **Metadata:** Date, severity, rows_affected (if issue), result (if test), version (if workplan)
- **Description:** Full context/root_cause/summary text (truncated with expand)
- **Linked Nodes:** List of connected nodes grouped by edge type — each clickable to navigate
- **File Changes:** List of files modified/affected (if applicable)
- **Phases/Deliverables:** For workplan nodes — list of phases with status
- **Timeline:** Position in project timeline relative to other nodes

---

### Phase 4: Help Data & Documentation

**Timeline:** Day 3  
**Status:** ✅ COMPLETE

#### Update: `dcc/ui/ui_help.json` (existing file)

Append neurogram-specific help/about/revision entries to the existing `dcc/ui/ui_help.json` file. New keys added under `neurogram` namespace to avoid conflicts with existing entries:

```json
{
  "neurogram": {
    "help": {
      "title": "Log Neurogram Help",
      "sections": [
        {"heading": "Getting Started", "text": "The graph loads automatically. Use the icon bar on the left to switch views. Click any node to see details."},
        {"heading": "Navigation", "text": "Pan: drag background. Zoom: scroll wheel. Focus node: double-click. Reset view: double-click background."},
        {"heading": "Filtering", "text": "Click 🔍 Filter to toggle node types, set date range, filter by status or severity."},
        {"heading": "Search", "text": "Type in the search bar to find nodes. Matching nodes are highlighted; press Enter to focus next match."},
        {"heading": "Timeline", "text": "Use the time slider at the bottom to animate graph growth over the project history."},
        {"heading": "Tree View", "text": "Click 🌳 Tree for a hierarchical view. Expand nodes to see children. Click any tree node to focus it in the graph."},
        {"heading": "Export", "text": "Click ⚙️ Settings → Export to download the current view as PNG or filtered data as JSON."},
        {"heading": "Themes", "text": "Click 🎨 Theme in the title bar to switch between dark, light, sky, ocean, and presentation themes."}
      ]
    },
    "about": {
      "title": "About Log Neurogram",
      "text": "Log Neurogram visualizes the complete DCC project history as an interactive network graph. Data is extracted from 4 log files and 159 workplan files across 15 domain folders.",
      "version": "1.0",
      "date": "2026-05-21",
      "author": "Franklin Song"
    },
    "defaults": {
      "graph_data_file": "../output/dcc_log_graph.json",
      "help_file": "ui_help.json"
    }
  }
}
```

---

### Phase 5: Testing & Verification

**Timeline:** Day 3  
**Status:** ✅ COMPLETE

#### Test Cases

| ID | Test | Method | Expected |
| :--- | :--- | :--- | :--- |
| T1 | Graph loads via file:// | Open HTML directly in browser | Graph renders with all nodes/edges |
| T2 | Graph loads via fetch | Serve from local server | Graph renders via fetch() |
| T3 | Node click | Click Issue node | Detail panel shows full metadata |
| T4 | Linked node navigation | Click linked node in detail panel | Graph focus shifts to clicked node |
| T5 | Filter toggle | Disable "File" node type | All file nodes hidden; edge count updates |
| T6 | Date range filter | Set range to May 2026 only | Only May nodes visible |
| T7 | Search | Type "BLV-001" | BLV-001 node highlighted and focused |
| T8 | Path highlight | Click node with 5+ connections | 1-hop subgraph highlighted, rest dimmed |
| T9 | Time slider | Animate from start to end | Nodes appear chronologically |
| T10 | Cluster mode | Cluster by engine | 8 engine clusters visible |
| T11 | Tree view | Switch to tree view | Hierarchical tree renders correctly |
| T12 | Theme toggle | Cycle through 5 themes | Each theme applies correctly; persists in localStorage |
| T13 | Panel resize | Drag left panel edge | Panel resizes; min-width enforced |
| T14 | Panel collapse | Click icon to collapse | Panel collapses; icon updates |
| T15 | Export PNG | Click Export → PNG | PNG file downloaded |
| T16 | Export JSON | Click Export → JSON | Filtered JSON file downloaded |
| T17 | Help panel | Click ❓ Help | Help content loaded from dcc/ui/ui_help.json (neurogram section) |
| T18 | About panel | Click ℹ️ About | About content loaded from dcc/ui/ui_help.json (neurogram section) |
| T19 | Status bar | Observe bottom bar | Shows correct node/edge counts and filter state |
| T20 | Mini-map | Observe bottom-right | Overview shows full graph position |

---

### Phase 6: Logging & Reporting

**Timeline:** Day 3  
**Status:** ✅ COMPLETE

#### Actions

| Action | File | Detail |
| :--- | :--- | :--- |
| Log issue | `dcc/log/issue_log.md` | New entry for Log Neurogram creation |
| Log update | `dcc/log/update_log.md` | Entry for each phase completion |
| Log test | `dcc/log/test_log.md` | Entry for Phase 5 test results |
| Phase report | `dcc/workplan/ui_design/log_neurogram/reports/phase1_report.md` | Data extraction report |
| Phase report | `dcc/workplan/ui_design/log_neurogram/reports/phase2_report.md` | Graph generation report |
| Phase report | `dcc/workplan/ui_design/log_neurogram/reports/phase3_report.md` | UI build report |
| Phase report | `dcc/workplan/ui_design/log_neurogram/reports/phase5_test_report.md` | Test results report |
| Update workplan | This file | Mark phases as completed, update version |

---

## 6. Delivery Sequence

| Step | Deliverable | Path |
| :--- | :--- | :--- |
| 1 | Workplan (this file) | `dcc/workplan/ui_design/log_neurogram/log_neurogram_workplan.md` |
| 2 | Compacted graph data | `dcc/output/dcc_log_graph.json` |
| 3 | Interactive webpage | `dcc/ui/log_neurogram.html` |
| 4 | Help data (update existing) | `dcc/ui/ui_help.json` |
| 5 | Test log entry | `dcc/log/test_log.md` (new entry) |
| 6 | Issue log entry | `dcc/log/issue_log.md` (new entry) |
| 7 | Update log entry | `dcc/log/update_log.md` (new entry) |
| 8 | Phase reports | `dcc/workplan/ui_design/log_neurogram/reports/` |

---

## 7. Success Criteria

| # | Criterion | Target |
| :--- | :--- | :--- |
| 1 | All 4 log files parsed | 100% entity extraction coverage |
| 2 | All 159 workplan files parsed | 15 domain folders, ~15 workplans, ~50 reports, ~110 phases extracted |
| 3 | Graph data generated | Valid JSON, ~350 nodes, ~700 edges |
| 4 | Graph renders correctly | All nodes visible, force layout stable |
| 5 | All 20 test cases pass | 20/20 PASS |
| 6 | file:// protocol works | No server required |
| 7 | All 5 themes functional | Theme toggle persists via localStorage |
| 8 | Panels resizable & collapsible | Drag and click interactions work |
| 9 | Search functional | Fuzzy search returns correct results |
| 10 | Time slider animates | Chronological node appearance |
| 11 | Export works | PNG and JSON download correctly |
| 12 | Logs updated | Issue, update, test entries created |
| 13 | Phase reports generated | All 4 reports in reports/ folder |
| 14 | Workplan cross-references resolved | All `addresses`, `references`, `belongs_to` edges point to valid nodes |

---

## 8. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
| :--- | :--- | :--- | :--- |
| Log format inconsistency | Entity extraction misses entries | Medium | Use multiple regex patterns; manual verification of edge cases |
| Workplan format variation | Different workplans use different header/metadata formats | Medium | Support multiple metadata patterns (table, key-value, header); fallback to filename-based ID |
| Vis.js CDN unavailable offline | Graph won't load without internet | Low | Bundle vis-network.min.js locally in output folder |
| Large graph performance | 350 nodes may lag on slow machines | Low | Vis.js BarnesHut solver handles 350 nodes easily; enable clustering; hide report nodes by default |
| file:// CORS blocks fetch() | Graph data won't load | Medium | Implement FileReader fallback with folder picker (existing dashboard pattern) |
| Cross-reference ID mismatches | Edges point to non-existent nodes | Medium | Validate all edge source/target IDs against node IDs during generation; log orphan edges |
| Complex file paths | File entity deduplication issues | Low | Normalize paths to relative form; use consistent path separator |
| Report-to-phase mapping ambiguity | Cannot determine which report belongs to which phase | Medium | Use filename convention (phase1_report.md → Phase 1); fallback to workplan-level attribution |

---

## 9. Known Limitations & Future Issues

| Limitation | Detail | Future Enhancement |
| :--- | :--- | :--- |
| Static data snapshot | Graph represents logs and workplans at extraction time only | Add "refresh" button to re-parse logs/workplans and regenerate graph |
| No write-back | Viewer only — cannot edit log data or workplans from UI | Future: integrate with log editing workflow |
| No AI analysis | Graph shows relationships but no insight generation | Future: add pattern detection (e.g., "this file caused 15 issues", "this workplan spans 3 months") |
| No real-time updates | Requires manual regeneration | Future: watch log files and workplan folder for changes and auto-regenerate |
| Vis.js dependency | Requires CDN or local bundle | Future: evaluate D3.js or custom canvas renderer |
| No mobile optimization | Desktop-focused layout | Future: responsive design for mobile/tablet |
| Report content not fully parsed | Report files parsed for metadata only, not detailed findings | Future: parse report findings, test results, and recommendations as sub-nodes |

---

## 10. References

| Reference | Path |
| :--- | :--- |
| agent_rule.md | `/agent_rule.md` |
| html_design_rule.md | `dcc/workplan/ui_design/html_design_rule.md` |
| DCC Design System CSS | `dcc/ui/dcc-design-system.css` |
| Web Interface Workplan (format reference) | `dcc/workplan/ui_design/web_interface/web_interface_workplan.md` |
| Issue Log | `dcc/log/issue_log.md` |
| Update Log | `dcc/log/update_log.md` |
| Test Log | `dcc/log/test_log.md` |
| Gemini Sessions | `dcc/log/gemini.md` |
| Workplan Root | `dcc/workplan/` (159 files, 15 domain folders) |
| Pipeline Architecture Workplans | `dcc/workplan/pipeline_architecture/` |
| Error Handling Workplans | `dcc/workplan/error_handling/` |
| Schema Processing Workplans | `dcc/workplan/schema_processing/` |
| Column Processing Workplans | `dcc/workplan/column_processing/` |
| AI Operations Workplans | `dcc/workplan/ai_operations/` |
| Data Validation Workplans | `dcc/workplan/data_validation/` |
| UI Design Workplans | `dcc/workplan/ui_design/` |
| Vis.js Network Docs | https://visjs.github.io/vis-network/docs/network/ |
