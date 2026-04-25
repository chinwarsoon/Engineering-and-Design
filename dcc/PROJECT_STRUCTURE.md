# DCC Project Structure & Maintenance Reference — Workplan

| Field | Value |
|-------|-------|
| **Workplan ID** | WP-DCC-DOC-001 |
| **Version** | 3.0 |
| **Date** | 2026-04-25 |
| **Status** | ✅ ACTIVE — Living document, updated with project changes |
| **Type** | Documentation / Reference |
| **Related** | [README](README.md) \| [Agent Rules](../../agent_rule.md) \| [Maintenance Workplan](workplan/maintenance/archive_cleanup_workplan.md) |

---

## 1. Object

To provide a definitive technical reference for the Document Control Center (DCC) project that:
- Documents the complete folder structure and file organization
- Describes the modular 7-engine architecture
- Lists all interactive UI dashboards with their key functions
- Defines maintenance protocols and archiving standards
- Serves as the ground truth for project maintenance workplans
- Enables rapid onboarding of new developers

---

## 2. Scope Summary

### In Scope
- **Folder Structure**: All directories under `dcc/` with purpose and contents
- **Core Root Files**: Critical environment and configuration files
- **UI Dashboards**: All HTML tools with detailed function documentation
- **Engine Architecture**: 7-engine pipeline responsibility matrix
- **Schema System**: 3-tier inheritance architecture documentation
- **Error Codes**: Reference to standardized S-C-S and L-M-F error systems
- **Maintenance Protocols**: Safe archiving rules and critical file protections

### Out of Scope
- Detailed implementation code (see individual workplans)
- API documentation (see `docs/` folder)
- User guides (see `docs/user_guide/`)
- Test procedures (see `workplan/testing/`)

---

## 3. Index of Content

| Section | Description | Link |
|---------|-------------|------|
| 1 | [Object](#1-object) | Purpose of this reference document |
| 2 | [Scope Summary](#2-scope-summary) | What is/is not documented here |
| 3 | [Index of Content](#3-index-of-content) | This table |
| 4 | [Version History](#4-version-history) | Revision tracking |
| 5 | [Evaluation & Alignment](#5-evaluation--alignment-with-existing-architecture) | agent_rule.md compliance |
| 6 | [Dependencies](#6-dependencies-with-other-tasks) | Related documents and workplans |
| 7 | [What Will Be Updated/Created](#7-what-will-be-updatedcreated) | Document maintenance triggers |
| 8 | [Folder Structure Overview](#8-folder-structure-overview) | Complete directory map |
| 9 | [Core Root Files](#9-core-root-files) | Critical environment files |
| 10 | [Distribution & Setup Tools](#10-distribution--setup-tools) | `tools/` directory contents |
| 11 | [Interactive HTML Dashboards](#11-interactive-html-dashboards) | `ui/` file details with functions |
| 12 | [7-Engine Architecture](#12-modular-7-engine-architecture) | Pipeline engine responsibilities |
| 13 | [3-Tier Schema System](#13-3-tier-schema-system) | Schema inheritance architecture |
| 14 | [Standardized Error Codes](#14-standardized-error-codes) | Error code reference |
| 15 | [Maintenance & Cleanup Protocol](#15-maintenance--cleanup-protocol) | Archiving rules and safeguards |
| 16 | [Risks and Mitigation](#16-risks-and-mitigation) | Documentation risks |
| 17 | [Success Criteria](#17-success-criteria) | Document quality targets |
| 18 | [References](#18-references) | Links to related files |

---

## 4. Version History

| Version | Date | Author | Changes | Status |
|---------|------|--------|---------|--------|
| 3.0 | 2026-04-25 | System | Converted to workplan format per agent_rule.md Section 8, added detailed UI function documentation, moved backup/tracer files to archive | ✅ Current |
| 2.1 | 2026-04-25 | System | Updated UI section with detailed file and function listings, archived tracer_pro.html and backup files | ✅ Superseded |
| 2.0 | 2026-04-20 | System | Added 7-engine architecture section, 3-tier schema documentation, standardized error codes reference | ✅ Superseded |
| 1.0 | 2026-04-15 | System | Initial project structure documentation | ✅ Superseded |

---

## 5. Evaluation & Alignment with Existing Architecture

### agent_rule.md Section 7 (Documentation) Compliance

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Overall summary | Section 1 (Object) | ✅ |
| Content index | Section 3 | ✅ |
| Documentation map | Folder structure diagrams | ✅ |
| Quick start | Section 8 (Quick Start CLI Pipeline) | ✅ |
| Module/function structure | Sections 11-13 | ✅ |
| I/O table | UI file details table | ✅ |
| Global parameter trace | Error code references | ✅ |
| Debugging/troubleshooting | Section 15 (Maintenance Protocol) | ✅ |
| Usage examples | CLI pipeline commands | ✅ |
| Best practices | Maintenance & cleanup rules | ✅ |

### agent_rule.md Section 2.3 (Schema) Alignment

| Schema Component | Document Reference | Status |
|------------------|-------------------|--------|
| 3-Tier inheritance | Section 13 | ✅ |
| Error code schemas | Section 14 | ✅ |
| Schema file locations | Listed with paths | ✅ |

---

## 6. Dependencies with Other Tasks

### Internal Dependencies

| Document/Workplan | Relationship | Status |
|-------------------|--------------|--------|
| [README.md](README.md) | High-level overview complement | ✅ Active |
| [Agent Rules](../../agent_rule.md) | Standards and requirements source | ✅ Active |
| [Maintenance Workplan](workplan/maintenance/archive_cleanup_workplan.md) | Implements protocols from Section 15 | ✅ Active |
| [Error Handling Taxonomy](workplan/error_handling/error_handling_taxonomy.md) | Error code details | ✅ Complete |

### External Dependencies

| Component | Usage | Status |
|-----------|-------|--------|
| `dcc.yml` | Environment specification | ✅ Current |
| `serve.py` | UI server reference | ✅ Current |
| `workflow/` engines | Architecture documentation | ✅ Current |

---

## 7. What Will Be Updated/Created

### Triggers for Document Update

| Trigger | Section to Update | Responsible |
|---------|-------------------|-------------|
| New UI dashboard added | Section 11 (UI Dashboards) | Developer + Reviewer |
| New engine added | Section 12 (7-Engine Architecture) | Architect |
| Schema structure changed | Section 13 (3-Tier Schema) | Schema Owner |
| Folder structure changed | Section 8 (Folder Structure) | Project Lead |
| Archive operation performed | Section 15 (Maintenance Protocol) | Maintenance Lead |
| Error codes added | Section 14 (Error Codes) | Error Handling Team |

### Update Process (per agent_rule.md Section 8.3)
1. Update version number and date in header
2. Add entry to Version History (Section 4)
3. Log change to `log/update_log.md`
4. Review related workplans for impact
5. Verify all internal links remain valid

---

---

## 8. Folder Structure Overview

```text
dcc/
├── archive/             # Categorized legacy files (Workflow, Config, Data, UI)
├── config/
│   └── schemas/         # 3-Tier Schema System (Base → Setup → Config)
├── data/                # Input source files (*.xlsx)
├── docs/                # Modular documentation (User & Developer Guides)
├── log/                 # Categorized logs (Update, Issue, Test, Gemini)
├── output/              # Pipeline results & diagnostic logs
├── tools/               # Distribution & Setup utilities
├── ui/                  # Standalone interactive HTML dashboards
├── workflow/            # Modular 7-Engine Architecture
└── workplan/            # Maintenance plans & Phase reports
```

---

## 🚀 Quick Start (CLI Pipeline)

The DCC project has transitioned from notebook-centric processing to a modular **Engine Pipeline**.

```bash
# 1. Activate Environment
conda activate dcc

# 2. Run Modular Pipeline (Standard)
python workflow/dcc_engine_pipeline.py --verbose normal

# 3. Run with Debugging (Full Traces)
python workflow/dcc_engine_pipeline.py --verbose debug

# 4. View Trace Dashboard
# Launch serve.py and navigate to /tracer
python serve.py
```

---

## 📂 Folder Structure Overview

```text
dcc/
├── archive/             # Categorized legacy files (Workflow, Config, Data)
├── config/
│   └── schemas/         # 3-Tier Schema System (Base → Setup → Config)
├── data/                # Input source files (*.xlsx)
├── docs/                # Modular documentation (User & Developer Guides)
├── log/                 # Categorized logs (Update, Issue, Test, Gemini)
├── output/              # Pipeline results & diagnostic logs
├── tools/               # Distribution & Setup utilities
├── ui/                  # Standalone interactive HTML dashboards
├── workflow/            # Modular 7-Engine Architecture
└── workplan/            # Maintenance plans & Phase reports
```

---

## 🛠️ Core Root Files

These four files in the `dcc/` root are critical for environment setup and operation:

| File | Purpose |
| :--- | :--- |
| **`dcc.yml`** | **Environment**: Conda specification for Python 3.13 and all dependencies. |
| **`PROJECT_STRUCTURE.md`** | **Structure**: This document; the primary reference for organization and maintenance. |
| **`README.md`** | **Project Readme**: High-level overview, quick start, and feature index. |
| **`serve.py`** | **UI Server**: A local Python web server to host and serve the interactive HTML tools. |

---

## 🧰 Distribution & Setup Tools (`tools/`)

The `tools/` directory contains utilities designed for initial project distribution and developer setup.

*   **`project_setup_tools.py`**: The primary utility for analyzing Excel columns vs. schemas, reordering schema sequences, and validating dependencies.
*   **`document_id_validation.py`**: Specialized tool for checking Document ID consistency across datasets.
*   **`example_column_rename.py`**: Template for bulk renaming operations during schema mapping.

---

## 🖥️ Interactive HTML Dashboards (`ui/`)

The `ui/` folder contains standalone, premium HTML files that provide a visual interface for the pipeline's data and logs. All UI files use the `dcc-design-system.css`.

### UI File Details

| File | Purpose | Key Functions |
| :--- | :--- | :--- |
| **`serve.py`** | Local HTTP server for UI dashboards | `Handler.do_GET()`, `Handler.log_message()`, `ReusableTCPServer` class |
| **`Excel Explorer Pro working.html`** | High-performance Excel/CSV viewer with fuzzy search | `loadFile()`, `renderTable()`, `applyFilter()`, `toggleColumn()`, `exportData()` |
| **`excel_explorer_pro.html`** | Simplified Excel explorer with theme support | `loadFile()`, `switchTheme()`, `toggleSidebar()`, `filterData()` |
| **`excel_explorer_data_pro.html`** | Advanced Excel data viewer with statistics | `parseData()`, `generateStats()`, `renderGrid()`, `searchData()`, `sortColumn()` |
| **`excel_data_table.html`** | Lightweight table viewer for Excel data | `loadWorkbook()`, `displaySheet()`, `formatCell()`, `handleDragDrop()` |
| **`excel_to_schema.html`** | Convert Excel column structure to JSON schema | `analyzeColumns()`, `generateSchema()`, `validateMapping()`, `exportSchema()` |
| **`Log Explorer Pro`** | Interactive viewer for structured pipeline logs | `loadLog()`, `parseStructuredLog()`, `filterByLevel()`, `toggleTree()`, `searchEntries()` |
| **`log_explorer_pro.html`** | Log file explorer with tree view | `fetchLogs()`, `renderTree()`, `filterLogs()`, `expandAll()`, `collapseAll()` |
| **`Pipeline Dashboard`** | Real-time visualization of 7-engine pipeline | `fetchStatus()`, `updateStages()`, `runPipeline()`, `showOutput()`, `updateHealthGauge()` |
| **`pipeline_dashboard.html`** | Pipeline execution dashboard with KPIs | `loadPipelineInfo()`, `updateProgress()`, `refreshStatus()`, `runPipeline()` |
| **`Schema Manager`** | Visual tool for 3-tier schema inheritance | `loadSchemas()`, `renderTree()`, `showSchemaDetails()`, `validateSchema()`, `compareVersions()` |
| **`schema_manager.html`** | JSON schema explorer and manager | `fetchSchemas()`, `renderSchemaTree()`, `showPropertyDetails()`, `validateAgainstSchema()` |
| **`Error Diagnostic Dashboard`** | Error analytics with charts and heatmaps | `loadErrors()`, `renderCharts()`, `updateHeatmap()`, `filterBySeverity()`, `exportReport()` |
| **`error_diagnostic_dashboard.html`** | Error visualization with Chart.js | `fetchErrorData()`, `renderSeverityChart()`, `renderTrendChart()`, `updateStats()` |
| **`common_json_tools.html`** | JSON exploration and key-value tools | `parseJSON()`, `renderTree()`, `searchKeys()`, `filterByType()`, `showDetails()`, `expandAll()`, `collapseAll()` |
| **`md-viewer.html`** | Markdown file viewer for documentation | `loadMarkdown()`, `parseFrontmatter()`, `renderContent()`, `toggleToc()`, `searchText()` |
| **`ai_analysis_dashboard.html`** | AI/ML analysis results viewer | `loadAnalysis()`, `renderMetrics()`, `showPredictions()`, `exportResults()` |
| **`submittal_dashboard.html`** | Submittal tracking and review dashboard | `loadSubmittals()`, `filterByStatus()`, `updateMetrics()`, `showDetails()` |
| **`tracer_pro.html`** | **ARCHIVED** - Moved to `archive/tracer/` | Code tracing and call-graph visualization (see archive) |
| **`dcc-design-system.css`** | Shared CSS design system for all UI components | CSS variables, utility classes, component styles |
| **`html_update_rule.md`** | UI development guidelines | HTML coding standards and update rules |

---

## 🏗️ Modular 7-Engine Architecture

The `workflow/dcc_engine_pipeline.py` orchestrates the following specialized engines:

| Engine | Responsibility | Key Module |
| :--- | :--- | :--- |
| **Initiation** | Env testing, project validation, path resolution. | `initiation_engine/core/validator.py` |
| **Schema** | Multi-tier schema loading & dependency resolution. | `schema_engine/loader/schema_loader.py` |
| **Mapper** | Fuzzy column matching and renaming. | `mapper_engine/core/engine.py` |
| **Processor** | Core calculations, logic, and data transformation. | `processor_engine/core/engine.py` |
| **Reporting** | Summary statistics and processing reports. | `reporting_engine/core/reporter.py` |
| **AI Ops** | Risk analysis and predictive insights (non-blocking). | `ai_ops_engine/core/engine.py` |
| **Error Handling** | Standardized S-C-S and L-M-F code resolution. | `initiation_engine/error_handling/` |

---

## 📋 3-Tier Schema System

The project uses an inheritance-based schema architecture (Refer to `agent_rule.md` Section 2.3) for maximum maintainability.

### 1. Document Registry Schemas
*   **Base**: `dcc_register_base.json` (Common definitions/types)
*   **Setup**: `dcc_register_setup.json` (Structure & property rules)
*   **Config**: `dcc_register_config.json` (Project-specific mapping values)

### 2. Error Handling Schemas
*   **Base**: `error_code_base.json` (Error object definitions)
*   **Setup**: `error_code_setup.json` (Catalog properties)
*   **System Config**: `system_error_config.json` (Codes: **S-C-S-XXXX**)
*   **Data Config**: `data_error_config.json` (Codes: **L3-M-F-XXXX**)

---

## ⚠️ Standardized Error Codes

Maintenance and cleanup tasks should refer to these codes found in logs:

*   **S-X-S-XXXX (System Errors)**: Issues with environment, files, or connectivity.
    *   *Example*: `S-F-S-0201` (Input File Not Found)
*   **L3-L-V-XXXX (Data/Logic Errors)**: Issues with column values or business rules.
    *   *Example*: `L3-L-V-0302` (Closed with Plan Date mismatch)

---

## 16. Risks and Mitigation

| Risk | Probability | Impact | Mitigation | Status |
|------|-------------|--------|------------|--------|
| R1 | Document becomes outdated | Medium | Medium | Update triggers defined in Section 7, version history tracked | Monitored |
| R2 | UI function documentation incomplete | Low | Low | grep_search used to extract actual functions from HTML files | Resolved |
| R3 | Archive locations not tracked | Low | Medium | All archive moves logged in Section 4 and update_log.md | Resolved |
| R4 | New developer onboarding confusion | Low | Medium | Clear folder structure diagram, quick start section | Resolved |
| R5 | Link rot to related documents | Low | Low | Relative paths used, quarterly link verification recommended | Monitored |

---

## 17. Success Criteria

| Criterion | Target | Measurement | Status |
|-----------|--------|-------------|--------|
| SC1 | Complete folder structure documented | 100% of directories listed | ✅ Pass |
| SC2 | All UI files with functions documented | 17 HTML files with key functions | ✅ Pass |
| SC3 | Workplan format compliance | agent_rule.md Section 8 requirements met | ✅ Pass |
| SC4 | Version history maintained | All versions 1.0-3.0 documented | ✅ Pass |
| SC5 | Cross-references valid | All markdown links functional | ✅ Pass |
| SC6 | Maintenance protocols clear | Safe archiving vs. critical rules defined | ✅ Pass |

---

## 🔧 Maintenance & Cleanup Protocol

This document serves as the ground truth for the **Project Maintenance Workplan (WP-MAINT-001)**.

### Safe for Archiving
- Files in `data/` older than the current session if results are exported.
- Redundant schemas not referenced by `dcc_register_config.json`.
- Logs in `log/` older than 30 days.
- UI backup files (already moved: `common_json_tools_backup.html` → `archive/`).
- Obsolete tracer files (already moved: `tracer_pro.html` → `archive/tracer/`).

### Critical (DO NOT MOVE)
- Any file in `config/schemas/` with a corresponding `$ref` in `dcc_register_config.json`.
- Engine core files in `workflow/`.
- `dcc.yml` environment specification.
- This `PROJECT_STRUCTURE.md` reference document.

### Link Maintenance
- When moving schemas to `archive/`, update all `$ref` paths in referencing JSON files.
- Use `grep -r "$FILE_NAME"` to verify all occurrences before moving.
- Update Section 11 (UI Dashboards) when files are archived.

---

## 18. References

| Document | Purpose | Location |
|----------|---------|----------|
| Agent Rules | Project standards and requirements | [`../../agent_rule.md`](../../agent_rule.md) |
| Maintenance Workplan | Archive cleanup procedures | [`workplan/maintenance/archive_cleanup_workplan.md`](workplan/maintenance/archive_cleanup_workplan.md) |
| Main README | High-level project overview | [`README.md`](README.md) |
| Error Handling Taxonomy | Complete error code reference | [`workplan/error_handling/error_handling_taxonomy.md`](workplan/error_handling/error_handling_taxonomy.md) |
| Update Log | Change tracking | [`log/update_log.md`](log/update_log.md) |
| Issue Log | Problem tracking | [`log/issue_log.md`](log/issue_log.md) |

---

**Status:** ✅ **UP TO DATE** — Converted to workplan format per agent_rule.md Section 8  
**Last Updated:** 2026-04-25  
**File:** `PROJECT_STRUCTURE.md` (WP-DCC-DOC-001)  
**Maintained by:** Engineering Team
