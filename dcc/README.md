# AI Assisted Document Control Center (AI-DCC)

## `AI Assisted Document Control Centre` is designed to:
- streamline the management of documents within organizations,
- automate processes, enhance security, and improve efficiency.

## The following workflows will be automated step by step:
 - Step 1: AI assisted User Interface to request or update document submission.
 - Step 2: Validation of document to be submitted.
 - Step 3: Archive of document to be submitted.
 - Step 4: Update of `Submittal Register`, and generate `Transmittal`.
 - Step 5: Request Document Controller to submit document to Client server.
 - Step 6: When Document have been returned from Client, strip PDF transmittal and update `Submittal Register` accordingly.
 - Step 7: Archive returned `Comment Return Sheet` to respective document submission archive folder.
 - Step 8: Send emails and distribute `Comment Return Sheet` to submitters for document update and resubmissoin.

 ## The following architecture design will be considered:
 - Single Source of Thruth and Schema Driven, which will allow user to easily set up `AI Assisted Document Control Center`.
 - Standalone interactive webpage user interfaces. Files to be shared in company intranet or SharePoint.
 - Modularized design to allow independent module/function/engine test.
 - Utilizing xlsx, csv, txt, md, and json files for data and reports.
 - Generating duckdb for external data processing and analysis.
 - Dashboards for status reporting and analysis.
 - Considering AI assisted data and report analysis.



# Revisions
| Revision | Status | Updates |
|----------|--------|---------|
| 1.0.1 | ✅ ACTIVE | Added UI section to README; documented 8 browser-based tools under `ui/` |
| 1.0.0 | ✅ ACTIVE | Initial release — 7-engine pipeline, 3-tier schema system, error taxonomy, 15+ dashboards |

---

# Step 1 - Not started
# Step 2 - Not started
# Step 3 - Not started
# Step 4 - In Progress

## Current Progress
A 7-engine pipeline that transforms raw document registers into validated, analysis-ready outputs:

```
Input (Excel) → Validation → Mapping → Processing → Reports (Excel/JSON)
```

## Key Capabilities
- Multi-engine architecture — [`workflow/README.md`](workflow/README.md)
- 3-tier schema system — [`workplan/schema_processing/README.md`](workplan/schema_processing/README.md)
- 15+ interactive dashboards — [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)
- Standardized error codes — [`workplan/error_handling/error_handling_taxonomy.md`](workplan/error_handling/error_handling_taxonomy.md)

## Quick Start
```bash
# Setup
conda env create -f dcc.yml && conda activate dcc

# Run pipeline
python workflow/dcc_engine_pipeline.py --verbose normal

# View dashboards
python serve.py
```

## Documentation
| Topic | File/Path |
|-------|-----------|
| **Architecture & CLI** | [`workflow/README.md`](workflow/README.md) |
| **Folder Structure** | [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) |
| **Error Codes** | [`workplan/error_handling/error_handling_taxonomy.md`](workplan/error_handling/error_handling_taxonomy.md) |
| **User Guides** | [`docs/user_guide/`](docs/user_guide/) |
| **Developer Guides** | [`docs/developer_guide/`](docs/developer_guide/) |
| **Change Log** | [`log/update_log.md`](log/update_log.md) |
| **Issue Log** | [`log/issue_log.md`](log/issue_log.md) |

---

# Step 5 - Not started
# Step 6 - Not started
# Step 7 - Not started
# Step 8 - Not started
# User Interface Design - In Progress

## Current Progress
Suite of browser-based tools under [`ui/`](ui/) for data visualization, pipeline monitoring, schema management, and analysis. All tools are single-file HTML5 apps sharing a unified design system — no build step required.

## Key Capabilities
- **8 interactive tools**: Pipeline Dashboard, Excel Explorer Pro, Submittal Tracker, Error Diagnostic Dashboard, Schema Manager, Log Explorer Pro, Common JSON Tools, Excel → Schema Generator — [`ui/user_guide.md`](ui/user_guide.md)
- **Unified design system**: VS Code-inspired layout with 5 color themes (Dark, Light, Sky, Ocean, Presentation)
- **Client-side only**: All processing in-browser via FileReader API; no data sent externally
- **Zero-server option**: Tools work from `file://`; `serve.py` enables cross-file data fetching

## Quick Start
```bash
# From the dcc/ folder, start the dev server
python serve.py

# Open in browser:
# http://localhost:5000           (default: Excel Explorer Pro)
# http://localhost:5000/ui/pipeline_dashboard.html
# http://localhost:5000/ui/submittal_dashboard.html
# http://localhost:5000/ui/schema_manager.html
# http://localhost:5000/ui/log_explorer_pro.html
# http://localhost:5000/ui/error_diagnostic_dashboard.html
# http://localhost:5000/ui/common_json_tools.html
# http://localhost:5000/ui/excel_to_schema.html
```

## Documentation
| Topic | File/Path |
|-------|-----------|
| **User Guide** | [`ui/user_guide.md`](ui/user_guide.md) |
| **Design System** | [`ui/dcc-design-system.css`](ui/dcc-design-system.css) |
| **UI Help Reference** | [`ui/ui_help.json`](ui/ui_help.json) |


*Maintained by Engineering Team | Updated 2026-05-19*
