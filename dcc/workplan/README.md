# DCC Workplan Directory

## Overview

This directory contains all workplan documents for the DCC (Data Column Compiler) project. Workplans are organized by domain, each defining phases, deliverables, success criteria, and references for a specific area of the codebase.

## Domain Folders

| Domain | Description | Key Workplans |
|--------|-------------|---------------|
| `pipeline_architecture/` | Core pipeline design, barrel pattern refactoring, SSOT schema-driven compliance, engine structuring | `pipeline_architecture_design_workplan.md`, `barrel_pattern_refactoring_workplan.md`, `ssot_schema_driven_workplan.md` |
| `error_handling/` | Error code standardization, taxonomy, data error handling, pipeline messaging | `data_error_handling_workplan.md`, `error_catalog_consolidation_plan.md`, `system_error_handling_workplan.md` |
| `schema_processing/` | Schema consolidation, recursive schema loading, register decoupling, pipeline integration | `schema_consolidation_workplan.md`, `recursive_schema_loader_workplan.md`, `pipeline_integration_workplan.md` |
| `column_processing/` | Business logic validation, column update logic, priority references | `business_logic_validation_workplan.md`, `column_update_logic.md` |
| `ui_design/` | Web interface design, HTML rules, data explorer, log neurogram network | `web_interface_workplan.md`, `log_neurogram_workplan.md`, `html_design_rule.md` |
| `ai_operations/` | AI-assisted operations, engine design, test strategy, IO contracts | `ai_operations_workplan.md`, `phase5_engine_design.md` |
| `data_validation/` | Row and column validation rules (integrity, domain, relational) | `row_validation_workplan.md`, `col_validation_workplan.md` |
| `dcc_pipeline_stage/` | Stage definitions for the DCC pipeline (file upload through export) | `stage-map.md`, `stage1`–`stage9` definitions |
| `maintenance/` | Archive cleanup and project maintenance | `archive_cleanup_workplan.md` |
| `document_id_handling/` | Document ID affix handling and extraction rules | `document_id_handling_workplan.md` |
| `initiation_engine/` | Project setup validation and initiation guides | `project-setup-validation-guide.md` |
| `project_setup/` | Project planning and setup documentation | `project-plan.md` |
| `code_quality/` | Code quality standards (currently empty) | — |

## Log Neurogram Network

The **Log Neurogram** is an interactive network graph that visualizes the entire DCC project — workplans, issues, updates, tests, files, and their semantic relationships — as a force-directed graph.

### `parse_logs.py`

This script extracts entities from all workplan files and log files and produces a single JSON graph dataset.

**Usage:**
```bash
# From the project root:
python3 dcc/workplan/parse_logs.py
```

**What it does:**

1. **Scans all `.md` files** under `dcc/workplan/` and `dcc/log/` — 160+ workplan files across 13 domain folders, plus 4 log files (issue, update, test, gemini)
2. **Extracts entities**: workplans, reports, issues, updates, tests, files, error codes, engines, folders, phases, steps, actions
3. **Embeds sub-elements** as `properties.content[]` arrays per the Requirements spec — sections, steps, criteria, milestones, deliverables, and dependencies are stored as structured JSON inside their parent node rather than as independent graph nodes
4. **Promotes with external refs**: steps and actions that reference files, error codes, or cross-entity IDs are promoted to standalone graph nodes
5. **Builds semantic edges**: 20+ edge types representing relationships (`addresses`, `fixes`, `resolves`, `affects`, `contains`, `evaluates`, `targets`, `belongs_to`, `references`, etc.)
6. **Runs coverage audit**: cross-checks parsed counts against ground truth — reports missing workplans, domain gaps, and entity count mismatches in metadata
7. **Outputs** `dcc/output/dcc_log_graph.json` (~1,400 nodes, ~5,000 edges)

**Output schema (key fields per node):**
- `layer`: 1 (executive), 2 (operational), or 3 (micro-audit) — controls visibility in the UI
- `properties.content[]`: embedded sub-elements with `type`, `text`, `order`, `status`
- `context`: hierarchical path string (e.g., `"wp-document_id_handling.section-1.step-3"`)
- `date`: flat timestamp property for timeline filtering

### `dcc/ui/log_neurogram.html`

The HTML UI for exploring the generated graph.

**Opening:**
```bash
# Serve locally (recommended):
python3 dcc/ui/serve.py
# Then open http://localhost:8000 in a browser
```

**Features:**
- **3-layer topology toggle** — Executive (layer 1), Operational (layer 2), Micro-audit (layer 3) — per Req 3
- **Force-directed graph** — Vis.js with BarnesHut solver, drag/zoom, click-to-inspect
- **Detail panel** — click any node to see metadata, linked nodes, file changes
- **Type/status/severity/domain filters** — toggle visibility by any attribute
- **Inline search** — real-time filtering by node label or ID
- **Time slider** — filter nodes by date range
- **Tree view** — hierarchical exploration by engine → workplan → issue
- **Clustering** — group nodes by type to reduce visual clutter
- **5 themes** — dark, light, sky, ocean, presentation (persisted to localStorage)
- **Export** — PNG screenshot or filtered subgraph JSON
- **`file://` support** — FileReader fallback if fetch fails

### Interpreting the Network

- **⭐ Workplans** are the primary organizing entities — each workplan file becomes a star-shaped node containing its internal structure
- **🔴 Issues / 🔵 Updates / 🟢 Tests** show the project's troubleshooting history and their resolution chains
- **⚪ Error codes** cluster around issues that introduced them and updates that fixed them
- **🟠 Engines** group files and workplans by codebase area
- **📁 Folders** show the directory hierarchy
- **Edges are semantic only** — every edge represents a real project relationship (never structural containment)

## Related Files

| File | Path |
|------|------|
| Graph data (generated) | `dcc/output/dcc_log_graph.json` |
| Neurogram UI | `dcc/ui/log_neurogram.html` |
| Neurogram workplan | `dcc/workplan/ui_design/log_neurogram/log_neurogram_workplan.md` |
| UI design rules | `dcc/workplan/ui_design/html_design_rule.md` |
| Help data | `dcc/ui/ui_help.json` |
| Design system CSS | `dcc/ui/dcc-design-system.css` |
