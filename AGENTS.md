# Repository Guidelines

## Projects

| Folder | Purpose | Python Version |
|--------|---------|----------------|
| `code_tracer/` | Static call-graph analyser + interactive dashboard | 3.10+ |
| `eks/` | Engineering Knowledge System (schema-driven registry) | 3.13 (conda) |
| `dcc/` | Document Control (legacy, data processing) | 3.13 (conda) |
| `releases/` | Packaged zip releases | — |

## Key Commands

```bash
# code_tracer — install and run
pip install ./code_tracer/engine
code-tracer /path/to/project
python code_tracer/engine/launch.py /path/to/project

# code_tracer — Docker
TARGET_DIR=/path/to/project docker compose -f code_tracer/engine/docker-compose.yml up

# code_tracer — tests (unittest)
python -m pytest code_tracer/engine/tests/

# code_tracer — frontend
cd code_tracer/engine/frontend && npm start
npm test  # React tests

# EKS — tests (pytest, must run from repo root)
python -m pytest eks/test/

# EKS — environment
conda env create -f eks/eks.yml
conda activate eks
```

## Critical Workflow Rules (from `agent_rule.md`)

1. **Plan before code**: Always create a workplan, wait for approval, then implement.
2. **Archive before delete**: Move files to `archive/` before removing.
3. **Log everything**: Issues → `issue_log.md`, updates → `update_log.md`, tests → `test_log.md`.
4. **Workplan required**: Every task gets a workplan in `<project>/workplan/`. Update it as work proceeds.
5. **Test reports after phases**: Generate test reports in `<project>/workplan/reports/` after each workplan phase.
6. **Revision control**: Every file carries revision metadata (number, date, author, summary).
7. **Review related workplans** before starting any implementation.
8. **Messaging and errors**: All modules, engines, functions must utilize messaging and error logging to report status, errors, warnings and issues for data quality and data integrity, and healthyness of coding execution.

## Folder Convention (all projects)

Each project must use this subfolder layout:

```
archive/    config/     data/       output/     test/
ui/         engine/     log/        docs/       workplan/
```

Do not add unexpected top-level directories.

## Files and Context

When scanning code for context, ignore:
- Files under any `backup/` folder
- Dot-folders and dot-files (`.git`, `.vscode`, etc.)
- Markdown files (`.md`) not in `workplan` folder
- Test folders

## Data Column Priority (EKS / dcc)

When processing tabular data:

**Rules:**
- No sorting before forward fill.
- Forward fill must never overwrite existing values.
- Always check for duplicate columns in the data frame.

**Priority order:**
1. **Priority 1 — Meta columns** (such as Project_Code, Department, etc.): forward-fill first. Null-handling must be "bounded" (stop if row index jumps or new file starts).
2. **Priority 2 — Relational keys** (such as Document_ID, Revision, etc.): validate, never blind-fill. If `Document_Revision` is null, trigger a lookup or flag a validation error.
3. **Priority 3 — Derived columns** (such as Submission_Closed, Days_Overdue, etc.): recalculate every run. Never have manual data.

**Processing sequence:**
1. Impute Priority 1: such as fill missing Project/Session info to anchor rows.
2. Validate Priority 2: such as ensure every document has an ID and a Revision.
3. Calculate Priority 3: such as run logic from `submission_closed_schema.json`.

## Schema Pattern

Schemas follow a 3-layer inheritance model:
- `*_base_schema.json` — shared `definitions`
- `*_setup_schema.json` — `properties` and `$ref` to base
- `*_config.json` — actual values

Three parallel schema sets: **core** (eks_*), **asset** (eks_asset_*), **ontology** (eks_ontology_*).

**Schema rules:**
- Flat structure; use array of objects, avoid array of lists.
- Use `definitions` for repetitive objects.
- `additionalProperties: false` on important property controls.
- Define `required` for properties if applicable.
- Each schema file must have `$schema`, `$id`, `title`, `description`, `version`, `$ref` calls if applicable.
- Schema loader must support all `$ref` types: string, object, nested object, recursive.
- Use Unified Schema Registry (URIs) — every schema gets a unique permanent `$id`.
- Pattern-based discovery for organizing schema files.

**Fragment pattern (asset):** Asset types compose schema fragments defined in `eks_asset_base_schema.json` (13 fragments: item_core, process_conditions, manufacturer, etc.). Conditional fragments bind to `device_type_code` values.

## Module Design

- Module design for all functions and classes.
- `__init__.py` shall only contain import statements and version information.
- SSOT (Single Source of Truth) for all global parameters, variables, keys, codes, values, names, paths, files that outlive a single function.
- Schema-driven design for global parameters that outlive a single function.

## Function Coding

- Every function gets a standardized docstring explaining purpose, parameters, and return values.
- Breadcrumb comments tracing parameter flow.

## Debugging (agent_rule.md Section 6)

**Tiered logging** (categorized by severity):
- Level 0: silent / only errors
- Level 1: status/info — milestone progress, high-level workflow status, system snapshot
- Level 2: warning/debug — warnings, variable values, path resolutions
- Level 3: trace — OS-specific path slashes, JSON raw extraction, deep technical info

**Debug Object:** Collect all debug info into a single dict, save to `debug_log.json`, pass to `format_report`, print at end of workflow.

**Trace table:** Track parameter flow, resolved values, source, and status. Add timestamp/duration for each step.

**Print formatting:** Indent messages per hierarchy level of calling functions. Use a global depth counter that increments on entry, decrements on exit.

**Messages:** Always include function name or module name and calling context in warning/debug/trace messages.

**Global parameter tracing:** Log state before and after every major transformation.

**Fail-fast:** Implement fail-fast metadata in functions to stop execution on critical errors.

## Revision Control (Section 7a)

Apply revision control to every file created or modified:

- **All files:** Include revision number, date, summary of change, and author.
- **Markdown/docs:** Top-of-file revision table with `Revision`, `Date`, `Author`, `Summary`.
- **Code files:** Header comment block or module docstring with revision metadata.
- **Config/schema files:** Standard metadata fields (`version`, `title`, `description`, `revisionHistory`) plus comments if necessary.
- **Log updates:** Update `update_log.md` in the project `log/` folder on every file revision.
- **Archiving:** Preserve revision entries when archiving or renaming; archived files retain history.
- **Numbering:** Use consistent semantics (e.g. `0.1`, `1.0`, `1.1`, `2.0`); increment for each substantive update.

## Documentation (Section 7)

Documentation must include all that apply:
1. Overall summary
2. Content index
3. Key features
4. Documentation map
5. Quick start and Mermaid workflow/chart
6. Module/function structure
7. List of functions
8. I/O table
9. Global Parameter Trace Matrix
10. Details of each function/module
11. Debugging and troubleshooting
12. Usage examples
13. Best practice and pending issues
14. Development test result
15. Dependencies and environment
16. Coding/programming engineering standard achieved

## Workplan (Section 8)

Every task gets a workplan in `<project>/workplan/`:

**Required sections:**
- Title and description
- Document ID, revision control, version history, status
- Object
- Scope summary (ID, details, category, status, related phase)
- Index of content with links
- Dependencies with other tasks
- Evaluation and alignment with existing architecture
- Implementation phases with task breakdown, each containing:
  - Timeline, milestones, deliverables
  - What will be updated/created
  - Risks and mitigation
  - Potential future issues
  - Success criteria
  - References (files, reports, code)

**Rules:**
- Always update the workplan when there are changes.
- Always review related workplans before starting implementation.
- Always log issues to `issue_log.md` under the workplan's parent folder.
- Always generate a report per phase in `<project>/workplan/reports/`.
- Always update logs in `<project>/log/`.
- Timestamp all phases and steps.

## Test Reports (Section 9)

Test reports go in `<project>/workplan/reports/` after each workplan phase:

**Required sections:**
- Title and description
- Document ID, revision control, version history, status
- Index of content with links
- Test objective, scope, execution summary
- Test methodology, environment, tools
- Test phases, steps, cases, status, detailed results
- Test success criteria and checklist
- Files archived, modified, version controlled
- Recommendations for future actions
- Lessons learned

**Rules:**
- Log issues to `issue_log.md` under the workplan's parent folder.
- Update `update_log.md` in `<project>/log/`.
- Cross-reference reports to workplan files.
- Timestamp all phases and steps.

## Function Table and Call Graph (Section 10)

When documenting modules, provide:
- All functions in a module/engine/class
- Function calling sequence
- Function description and purpose
- Function parameters (in) and return values (out)
- Function dependencies and relationships
- Function error/exception handling
- Function tracing and status reporting
- Function UI and interaction

## UI Web Design (Section 11)

All HTML files must follow these rules:

**Dependencies:**
- Interactive standalone webpage design.
- Separate independent CSS file per project.
- Schema-driven.

**Layout (VS Code style):**
- Title/menu bar spanning full width (theme button, layout button, menu, global search).
- Side icon bar panel (left) — icons only; left panel icons on top, right panel icons at bottom with divider.
- Toggleable left sidebar — collapsible, resizable by dragging right edge, content toggleable.
- Toggleable right sidebar — collapsible, resizable by dragging left edge, anchored to screen right.
- Bottom status bar showing selected file.

**Theme:**
- Toggle via button in top-right of title bar.
- Options: light (bright bg), dark (dark bg), sky (sky blue), ocean (ocean blue), presentation (light grey).
- Save theme selection in localStorage.

**Layout switching:**
- Layout button in title bar switches between single column, two columns, three columns, etc.

**File loading panel:**
- Load files from local disk or specific pipeline files.
- List all loaded files.
- Drag-and-drop to load.
- Collapsible via side icon bar.

**Tree selection panel:**
- Show hierarchical structure of loaded content.
- Select any node to show content in main panel.
- Expand all / collapse all.

**Icons (Unicode):**
- Info: ℹ️
- File load: 📂
- Help: ❓
- Setting: ⚙️
- Tree: 🌳

**Help system:**
- Store help text, about text, revision text, default file names/folders/definitions in `ui_help.json`.
- HTML files load values from this JSON file.

## Data Health, Score, and Errors (Section 12)

Each business logic must have an independent error code defined to trace related errors.

## Neurogram / Compact Records (Section 13)

Refer to `dcc/workplan/ui_design/log_neurogram/`. Generate a neurogram network JSON file (`dcc_log_graph.json`) in the respective `<project>/output/` folder. Ensure details can be compacted into the JSON file.

## Testing Notes

- `code_tracer` tests use `unittest`; `eks` tests use `pytest`.
- EKS tests expect config files at `eks/config/` (relative to repo root).
- EKS tests create/clean `eks/test_output/` and `data/eks_registry.db`.
- code_tracer tests use `unittest.main()` and can be run directly or via pytest.

## Formatting

- Prettier config at root: `printWidth: 100`, `singleQuote: true`, `endOfLine: "lf"`.
