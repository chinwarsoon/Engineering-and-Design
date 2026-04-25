# DCC Project Structure & Maintenance Reference

**Last Updated**: 2026-04-25  
**Purpose**: Primary technical reference for project structure, engine architecture, and maintenance standards for the Document Control Center (DCC) project.

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

| Tool | Purpose |
| :--- | :--- |
| **`Excel Explorer Pro`** | High-performance viewer for large Excel/CSV datasets with fuzzy search. |
| **`Log Explorer Pro`** | Interactive viewer for structured pipeline logs and error diagnostics. |
| **`Pipeline Dashboard`** | Real-time visualization of the 7-engine pipeline execution status. |
| **`Schema Manager`** | Visual tool for exploring the 3-tier schema inheritance and relationships. |
| **`Tracer Pro`** | Interactive code tracing and call-graph visualization. |

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

## 🔧 Maintenance & Cleanup Protocol

This document serves as the ground truth for the **Project Maintenance Workplan (WP-MAINT-001)**.

### Safe for Archiving
- Files in `data/` older than the current session if results are exported.
- Redundant schemas not referenced by `dcc_register_config.json`.
- Logs in `log/` older than 30 days.

### Critical (DO NOT MOVE)
- Any file in `config/schemas/` with a corresponding `$ref` in `dcc_register_config.json`.
- Engine core files in `workflow/`.
- `dcc.yml` environment specification.

### Link Maintenance
- When moving schemas to `archive/`, update all `$ref` paths in referencing JSON files.
- Use `grep -r "$FILE_NAME"` to verify all occurrences before moving.

---

## 📚 References
- [Agent Rules](file:///home/franklin/dsai/Engineering-and-Design/agent_rule.md)
- [Maintenance Workplan](file:///home/franklin/dsai/Engineering-and-Design/dcc/workplan/maintenance/archive_cleanup_workplan.md)
- [Main README](file:///home/franklin/dsai/Engineering-and-Design/dcc/README.md)
