# Repository Guidelines

## 1. Projects

| Folder | Purpose | Python Version |
|--------|---------|----------------|
| `code_tracer/` | Static call-graph analyser + interactive dashboard | 3.10+ |
| `eks/` | Engineering Knowledge System (schema-driven registry) | 3.13 (conda) |
| `dcc/` | Document Control (legacy, data processing) | 3.13 (conda) |
| `releases/` | Packaged zip releases | — |

**Project naming convention:** Each project listed above must have a single canonical name and abbreviation declared in its `knowledge.json` under `project_metadata.name`. All code, documentation, READMEs, CLI help text, `pyproject.toml` `name` field, and UI elements must use this canonical name. A project-wide grep for alternative names is required before each phase completion.

## 2. Project Knowledge Base

1. Project Knowledge Base will explain how a project is planned and implemented. It will be used by team for maintainance, troubleshooting, furture development with AI assistance. The main purpose is not for human consumption but for AI assistance and automation. It essentially serves as the machine-readable `software blueprint and project charter`.
2. Each project will contain following entities:
- folders and files
- modules, engines, clasess, tests, functions with codes
- schema files and environment for project setups
- input data
- output data
- user interface
- documentation for workplan, test reprots, logs
3. entities will have:
- metadata: such as name, version, date, description, purpose
- logics and relationships: such as dependencies, relationships, intergration points, workflows, functions, data flows, etc.
- actions: such as tests, workflows, functions, etc.
- permissions: such as boundaries, domains area, etc
4. Each project must maintain a `knowledge.json` file at the project root containing:

- **Project metadata**: name, version, description, purpose
- **Architecture overview**: key modules, data flows, integration points
- **Domain concepts**: core entities, relationships, terminology
- **Key schemas**: references to primary schema files (from `config/`)
- **Workflows**: primary operational workflows and entry points
- **Functions**: primary functions, entry points, data processing pipelines
- **Data flows**: data flow diagrams, data flow details, data quality checks
- **Dependencies**: external services, libraries, infrastructure
- **Known issues**: technical debt, limitations, open questions

**Location**: `<project>/knowledge.json`
**Schema**: Defined in `config/schemas/knowledge_base_schema.json` (shared)

5. Automated troubleshooting agent must manage the project effectively:
- automated root-cause analysis (RCA)
- Automomous Testing Execution (ATE)
- Change Impact Traveability (CIT)

## 3. Shared Configuration

A shared `config/` folder exists at the repository root for cross-project schemas and configuration. A shared `common/` folder exists for cross-project UI design system files:

```
config/
  schemas/           # Shared schema definitions (e.g., knowledge_base_schema.json)
common/
  universal_ui_design.css  # Shared CSS design system (5 themes, shell layout, components)
  universal_ui_design.js   # Shared JS library (theme/sidebar/layout/toast/modal/file/table/utils)
  universal_ui_design.md   # Documentation covering both CSS and JS
```

## 4. Key Commands

```bash
# code_tracer — install and run
pip install ./code_tracer/engine
code-tracer /path/to/project
python code_tracer/engine/launch.py /path/to/project

# code_tracer — Docker
TARGET_DIR=/path/to/project docker compose -f code_tracer/engine/docker-compose.yml up

# code_tracer — tests (unittest)
python -m pytest code_tracer/test/

# code_tracer — frontend
cd code_tracer/engine/frontend && npm start
npm test  # React tests

# EKS — tests (pytest, must run from repo root)
python -m pytest eks/test/

# EKS — environment
conda env create -f eks/eks.yml
conda activate eks
```

## 5. Critical Workflow Rules (from `agent_rule.md`)

1. **Plan before code**: Always create a workplan, wait for approval, then implement.
2. **No edits without approval**: Do not modify any file until the user explicitly approves the change. Present the proposed change and rationale, then wait for a yes.
3. **Archive before delete**: Move files to `archive/` before removing.
4. **Log everything**: Issues → `issue_log.md`, updates → `update_log.md`, tests → `test_log.md`.
5. **Workplan required**: Every task gets a workplan in `<project>/workplan/`. Update it as work proceeds.
6. **Test reports after phases**: Generate test reports in `<project>/workplan/reports/` after each workplan phase.
7. **Revision control**: Every file carries revision metadata (number, date, author, summary).
8. **Review related workplans** before starting any implementation.
9. **Messaging and errors**: All modules, engines, functions must utilize messaging and error logging to report status, errors, warnings and issues for data quality and data integrity, and healthyness of coding execution.
10. **Knowledge base required**: Every project must have a `knowledge.json` at root. This file must be created at project inception and updated as part of every phase completion (see §5.6). When a new project is scaffolded, the first task is creating `knowledge.json` populated with initial metadata, architecture overview, and known issues. A project missing `knowledge.json` is not in compliance and must have one created before further development.
11. **Relocation validation**: When any file or package is relocated, perform a project-wide `grep` for all import paths that reference the old location. Update every match in the same edit cycle. Run the full test suite after the change. If the project has no tests that exercise the relocated code, add them before closing the migration task.
12. **Fix breadth**: When fixing a pattern-based defect (not a single-instance bug), use `grep` to identify all occurrences of the broken pattern across the entire project before applying the fix. Update all matches in the same edit. Document the search pattern in the task description so the same fix can be re-applied if the pattern re-emerges.
13. **Cross-source alignment audit**: When a concept spans 3+ independent sources (schemas, config files, library code, project code, design docs, error/message catalogs), run a cross-reference audit across all sources before marking the feature complete. Every source must agree on: format names, code patterns, field names/types, registered IDs, and version numbers. A mismatch in any one source is a blocking defect.
14. **Pre-bootstrap safety**: Pipeline entry points must guard all non-stdlib imports individually inside a pure-stdlib `_preload_infrastructure()` function that runs before any bootstrap phase. Every import must be individually `try/except ImportError`-guarded with errors printed to `stderr` immediately at the failure point. Pre-bootstrap logger, telemetry/heartbeat, and project-root discovery must also run before bootstrap phases begin. If `common.library` is not importable, the entry point must exit with a human-readable message — never a bare `ModuleNotFoundError` traceback.
15. **Path resolution SSOT**: All directory and file paths must be resolved through the schema-driven `global_paths` definitions with precedence: CLI argument > Schema default > code-native fallback. Never use hardcoded path literals (e.g., `parent.parent.parent`, `"data"`, `"output"`). Use anchor-folder-based discovery (`default_base_path(anchor)`) to find the project root, then derive all sub-paths from `global_paths` schema values. Every path must flow through `resolve_paths()` so a single schema change updates all consumers.
16. **Hardcoded fallback removal**: Never maintain hardcoded fallback lists (required folders, required files, dependency lists, default paths) that duplicate values already defined in schema/config files. If config is absent, raise a descriptive error — never silently fall back to a second source of truth. Hardcoded duplicates diverge over time and violate SSOT.
17. **Issue log layout integrity**: The `<project>/log/issue_log.md` file has a fixed structure that must be preserved on every edit. Replacing the entire file content is the primary cause of issue loss (see I190 — 189 issues wiped). The following checks are mandatory before and after every modification:

   **a. Required sections — verify all 4 structural blocks are present and in order:**
   | Order | Section | Contents |
   | :---: | :------ | :------- |
   | 1 | Metadata header | `# Issue Log`, Project, Location, Last Updated line |
   | 2 | Legend block | `## Legend` → `### Status` table (marker, status, meaning for all 8 statuses) → `### Severity` table (marker, severity, meaning for all 5 severities) |
   | 3 | Status Summary | `### Status Summary` table with per-status count (✅, 🔴, ⏳, ⏸️, 🔷, ⛔, 🔶) and grand total |
   | 4 | Priority Resolution Sequence | `## Priority Resolution Sequence` → priority table (Seq, Priority, Issue IDs, Count, Theme) |
   | 5 | Issue Log Table | `## Issue Log Table` → pipe-delimited issue rows with columns: Issue ID, Date, Phase, Severity, Title, Description, Status, Resolution |

   **b. Status Summary regeneration**: After every edit, recount all statuses across every `I\d+` row and update the Status Summary table. Stale counts are treated as a layout defect.

   **c. Issue tag integrity check**: After every edit, grep the entire log for `I\d+` tags to confirm:
   - No duplicates (same ID appearing more than once)
   - No gaps in the sequence from I001 to last issue
   - All referenced issue IDs in the Priority Resolution Sequence table exist in the Issue Log Table
   - All listed counts in the Priority Resolution Sequence match the number of Issue IDs listed in the same row

   **d. Table formatting check**: All markdown tables must have proper pipe-delimited rows with aligned columns, consistent whitespace, and no broken rows caused by unescaped pipes in description text.

   **e. Targeted edits only**: Use `replace_in_file` for all modifications. Never read the full file and write it back as a single block — this is the exact mechanism that caused I190.

   **f. Validation workflow — execute after every edit sequence completes:**

   1. `### Status Summary` → recount and update
   2. `### Status` and `### Severity` legend tables → confirm all 8 statuses + 5 severities present
   3. `## Priority Resolution Sequence` → verify all Issue IDs exist in the Issue Log Table; verify `Count` column matches listed IDs per row
   4. Issue tags → grep `I\d+`, confirm sequential from I001 with no duplicates or gaps
   5. Table rows → confirm all issue rows have 8 pipe-delimited columns (| Issue | Date | Phase | Severity | Title | Description | Status | Resolution |)

## 6. Folder Convention (all projects)

Each project must use this subfolder layout:

```
archive/    config/     data/       output/     test/
ui/         engine/     log/        docs/       workplan/
knowledge.json          # Required at project root
```

Do not add unexpected top-level directories.

**Directory validation:** At project creation and at each phase completion, verify all required directories exist at the project root: `archive/`, `config/`, `data/`, `output/`, `test/`, `ui/`, `engine/`, `log/`, `docs/`, `workplan/`. Missing directories must be created (empty scaffolding) before the phase can be marked complete. Directory names are case-sensitive (lowercase) and must match exactly — `Log/` is not a substitute for `log/`.

### 6.1 Test Folder — Single Source of Truth

**`<project>/test/` is the one and only location for all test functions** belonging to that project. This rule applies regardless of project structure:

- Every test file (`test_*.py`) must reside in `<project>/test/` — no exceptions.
- Test files found in `engine/`, `workflow/`, `tools/`, sub-module `tests/` directories, or any location other than `<project>/test/` violate this convention.
- Embedded test directories (e.g., `<project>/workflow/*/test/`, `<project>/engine/*/tests/`) must be migrated to `<project>/test/`. During migration, create a subfolder within `<project>/test/` (e.g., `test/processor_engine/`) to preserve logical grouping while obeying the single-root rule.
- Test runtime artifacts (generated files, output directories, temp databases) must be placed in `<project>/test_output/` or use `tempfile.TemporaryDirectory` for automatic cleanup. They must never leak to the repository root.
- At each phase completion, verify zero test files exist outside `<project>/test/`.

## 7. Files and Context

When scanning code for context, ignore:
- Files under any `backup/` folder
- Dot-folders and dot-files (`.git`, `.vscode`, etc.)
- Markdown files (`.md`) not in `workplan` folder
- Test folders

Also include:
- `<project>/knowledge.json` — project knowledge base (high priority)

## 8. Data Column Priority (EKS / dcc)

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

## 9. Schema Pattern

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
- Each schema file must have `$schema`, `$id`, `title`, `description`, `version`, `allof`, `$ref` calls if applicable.
- Schema loader must support all `$ref` types: string, object, nested object, recursive.
- Use Unified Schema Registry (URIs) — every schema gets a unique permanent `$id`.
- Pattern-based discovery for organizing schema files.

**Fragment pattern (asset):** Asset types compose schema fragments defined in `eks_asset_base_schema.json` (13 fragments: item_core, process_conditions, manufacturer, etc.). Conditional fragments bind to `device_type_code` values.

**New schema set checklist:** When introducing a new schema set, verify all of:
1. Base file exists (`*_base_schema.json`) with shared `definitions` and `$schema`/`$id`/`title`/`version`
2. Setup file exists (`*_setup_schema.json`) with `allOf` → `$ref` to base, property declarations, and `additionalProperties: false` on important controls
3. Config file exists (`*_config.json`) with actual values and no schema metadata fields (`$schema`, `$id`, `version`, `title`, `description` in data instances)
4. Config validates against setup schema before first commit
5. Schema loader discovers the new set and validates it at startup
6. At least one test validates the new schema chain end-to-end

## 10. Module Design

- Module design for all functions and classes.
- `__init__.py` shall only contain import statements and version information.
- SSOT (Single Source of Truth) for all global parameters, variables, keys, codes, values, names, paths, files that outlive a single function.
- Schema-driven design for global parameters that outlive a single function.
- **SSOT verification**: Before adding any named definition (type, constant, version string, identifier, key), search the entire project to confirm it does not already exist under a different name. If a semantic equivalent exists, use `$ref` or import instead of redefining. For version numbers, each project must declare a single `__version__` in its root `__init__.py`; all other components must import from there.

## 11. Function Coding

- Every function gets a standardized docstring explaining purpose, parameters, and return values.
- Breadcrumb comments tracing parameter flow.

## 12. Debugging (agent_rule.md Section 6)

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

## 13. Revision Control

Apply revision control to every file created or modified:

- **All files:** Include revision number, date, summary of change, and author.
- **Markdown/docs:** Top-of-file revision table with `Revision`, `Date`, `Author`, `Summary`.
- **Code files:** Header comment block or module docstring with revision metadata.
- **Config/schema files:** Standard metadata fields (`version`, `title`, `description`, `revisionHistory`) plus comments if necessary.
- **Log updates:** Update `update_log.md` in the project `log/` folder on every file revision.
- **Archiving:** Preserve revision entries when archiving or renaming; archived files retain history.
- **Numbering:** Use consistent semantics (e.g. `0.1`, `1.0`, `1.1`, `2.0`); increment for each substantive update.
- **Cross-reference validation:** When any file's version or revision metadata changes, all files that reference or document that file must be updated in the same edit cycle. Use `grep` across the project to identify all reference sites before committing the change. If a referenced file has 3+ stale references, create an issue and defer the version bump until all references are corrected.

## 14. Documentation

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

## 15. Workplan

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
- **Feature completion definition**: A feature is only "complete" (✅) when its core business logic is implemented and tested. Structural scaffolding (stubs, placeholder returns, `# TODO` blocks, "foundation in place" with no runtime effect) must be marked as 🔶 PARTIAL or 🔷 PLANNED, never ✅. A feature that always returns a null/fixed value is not complete. A parser that returns "Implementation Pending" is not complete. Document which sub-capabilities are stubs in the task description and link to the deferred issue.
- **Phase scope freeze**: Once a phase workplan is marked COMPLETE, no new tasks may be added to it. Newly discovered work must be captured in a follow-up phase workplan (e.g., Phase 1.2, Phase 1.3) or in the next major phase. The only exception is urgent bug fixes, which must be logged as issues and tracked separately from the phase task list. A phase should only be marked COMPLETE when its scope is fully delivered and no additional tasks are anticipated.

## 16. Test Reports

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

## 17. Function Table and Call Graph

When documenting modules, provide:
- All functions in a module/engine/class
- Function calling sequence
- Function description and purpose
- Function parameters (in) and return values (out)
- Function dependencies and relationships
- Function error/exception handling
- Function tracing and status reporting
- Function UI and interaction

## 18. UI Web Design

All HTML files must follow these rules:

### 18.1 Dependencies and Stack

- Interactive standalone webpage — no build step, no bundler.
- All UIs must use the shared design system from `common/` as their primary CSS and JS dependency. Use `<link rel="stylesheet" href="/common/universal_ui_design.css">` and `<script src="/common/universal_ui_design.js">` as the base. Individual pages add only page-specific overrides via an inline `<style>` block. Project-specific CSS files (e.g. `eks.css`, `dcc-design-system.css`) must only contain overrides and extensions — they must never re-declare design tokens or duplicate shell layout classes already defined in the universal system.
- Schema-driven: all labels, help text, stage definitions, output file names, and default values are stored in `ui_help.json` and loaded at runtime via `fetch()`.
- Zero npm runtime dependencies in the HTML layer. **No external CDN fonts** — use `font-family: system-ui, -apple-system, 'Segoe UI', sans-serif` as the primary font stack so pages render correctly on corporate networks that block `fonts.googleapis.com`. CDN fonts may be used only as an `@import` with a `font-display: swap` fallback that degrades gracefully when blocked.
- Always set `Cache-Control: no-cache` meta tags so reloads always reflect the latest server output.
- All asset paths (CSS, JS, JSON) must be root-relative (e.g. `/common/universal_ui_design.css`, `/ui/eks.css`) or relative to the HTML file's own directory — never hardcoded absolute paths. This ensures files load correctly regardless of the working directory from which `serve.py` is started.

### 18.2 Layout (VS Code shell model)

The page body is divided into exactly four zones stacked as flexbox columns/rows:

```
┌──────────────────── title bar (full width, fixed height 36px) ────────────────────┐
│ icon-bar (48px) │ left sidebar (260px, resizable) │ content area │ right sidebar  │
└────────────────────────── status bar (full width, fixed height 22px) ─────────────┘
```

- **Title bar** — spans full width; contains logo (icon + name + accent word), breadcrumb, and right-aligned action buttons (layout toggle, theme picker).
- **Icon bar** — leftmost strip, 48 px wide; emoji/Unicode icons only, no text labels. Top section holds primary panel icons; bottom section (separated by a 1 px divider) holds utility icons (settings, help). Active icon shows a 2 px left-edge accent bar.
- **Left sidebar** — collapsible (width → 0 with CSS transition), resizable by dragging a 5 px right-edge handle. Contains accordion sections (`sb-section` / `sb-section-header` / `sb-section-body`). Toggle via icon bar button.
- **Right sidebar** — collapsible, resizable by dragging a 5 px left-edge handle, anchored to the right edge. Serves dual purpose: default "Settings" view and context-sensitive "Help" / "Detail" view. Toggle via icon bar button.
- **Content area** — flex: 1, owns a toolbar strip and a scrollable body. Toolbar holds page title, spacer, and action buttons.
- **Status bar** — fixed 22 px strip at the bottom; left side shows current state / selected file; right side shows version string.
- `html, body` must be `height: 100%; overflow: hidden` so the shell fills the viewport exactly without page scroll.
- Custom scrollbar: 6 px width, transparent track, border-colored thumb.

### 18.3 CSS Design System

All design tokens are defined once in `common/universal_ui_design.css` under `:root` / `[data-theme="dark"]` (and all 5 theme variants). Required token groups:

| Group | Variables |
|---|---|
| Surfaces | `--bg`, `--surface`, `--surface2`, `--surface3` |
| Borders | `--border` |
| Text | `--text`, `--text2`, `--text3` |
| Accent | `--accent`, `--accent-alt` |
| Semantic | `--success`, `--warning`, `--danger`, `--info` |
| Tag | `--tag-bg`, `--tag-border` |
| Table | `--row-stripe`, `--row-hover`, `--th-bg`, `--th-hover` |
| Dimensions | `--icon-bar-w`, `--sidebar-w`, `--right-sidebar-w`, `--titlebar-h`, `--statusbar-h` |
| Radii | `--radius`, `--radius-sm`, `--radius-lg` |
| Fonts | `--font-ui` (system-ui), `--font-mono` (JetBrains Mono) |

**SSOT rule**: `common/universal_ui_design.css` is the single source of truth for all design tokens and shell layout classes. Project-specific CSS files (e.g. `eks.css`, `dcc-design-system.css`) must never redefine these tokens — they import the universal file and only add project-specific overrides or additional component rules. All component colors must reference `var(--token)` — never hardcoded hex in component rules. A project-wide grep for hardcoded hex values used as colors (not neutral border grays) is required before each phase completion.

### 18.4 Theme System

- Five themes: `dark` (default), `light`, `sky`, `ocean`, `presentation`.
- Applied by setting `data-theme` attribute on `<html>` (or `<body>`).
- Theme selection persisted to `localStorage` key `<project>-theme` and restored on load.
- Theme picker: a button in the title bar opens a dropdown menu; each option shows a color dot + label. Active option is marked with `.active` class.
- Theme transition: `transition: background 0.25s, color 0.25s` on `body` for smooth switching.

### 18.5 Sidebar Accordion

Left (and right) sidebar content is organized into collapsible accordion sections:

- `.sb-section` — container with bottom border.
- `.sb-section-header` — clickable row with icon, label, and a right-aligned chevron arrow (`▼`).
- `.sb-section-body` — collapsible content; hidden by adding `.closed` to the parent `.sb-section` (chevron rotates −90°).
- Toggle on click of any `.sb-section-header`.

### 18.6 Drag-to-Resize Sidebars

Both sidebars must support mouse drag resizing (`comUI.sidebar.resize()` from the universal JS library):

- Left sidebar: 5 px handle at right edge (`.com-resizer.left-resizer`, `right: -2px`).
- Right sidebar: 5 px handle at left edge (`.com-resizer.right-resizer`, `left: -2px`).
- On hover and while dragging, handle background transitions to `--accent` color with a visible 2 px × 32 px center bar.
- Minimum sidebar width: 120 px; maximum: 480 px (enforced in the `mousemove` handler).
- Width persisted to `localStorage` per sidebar key via the `storageKey` option.

### 18.7 File Loading Panel

Every tool that loads files must implement:

- **Fetch pipeline file** button — loads a well-known default path (e.g. `../output/processed_*.csv`) via `fetch()`.
- **Load local file** button — opens `<input type="file">` picker.
- **Drag-and-drop** — accept `dragover` / `drop` events on the full page body to load files.
- **Loaded files list** — displays all files loaded in the current session; highlights the active file.
- Status bar always reflects the currently active file name.
- Panel is collapsible via its icon bar button.

### 18.8 Layout Switching

- A 🔲 layout toggle button in the title bar cycles the content area through column layouts (1-col → 2-col → 3-col → back to 1-col).
- Layout state persisted to `localStorage`.

### 18.9 Help System

- All help text, about text, revision info, stage definitions, output file names, option labels, and default paths are stored in `ui_help.json` at the `ui/` folder root.
- Pages load `ui_help.json` on startup via `fetch('ui_help.json')` (or a relative path).
- The right sidebar renders a **Help** view when the ❓ icon bar button is clicked; content is built from `ui_help.json` keys.
- The right sidebar renders a **Detail** view (with a ← Back button) when a KPI card, stage card, or output file is clicked — content is generated from live data + config.
- If `ui_help.json` fails to load, all panels must degrade gracefully (show "unavailable" message, never crash).

### 18.10 KPI and Stage Cards

Dashboards that display pipeline or data metrics must use card components:

- **KPI cards** — grid of metric tiles (`display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr))`). Each shows a large value, a label, a sub-label (delta or secondary metric), and optionally a health gauge bar.
- **Stage cards** — one card per pipeline stage; each shows a numbered emoji icon, stage name, meta line (truncated with ellipsis), status text (PENDING / RUNNING / PASS / FAIL), and a 4 px progress bar.
- Cards must be clickable (`cursor: pointer`): hover state adds `border-color: var(--accent)` + `box-shadow: 0 0 0 1px var(--accent)`.
- Stage status colors: PASS → `--success`, FAIL → `--danger`, RUNNING → `--accent`, PENDING → `--text3`.
- Health gauge bar uses a CSS gradient: `linear-gradient(90deg, var(--danger), var(--warning), var(--success))`.

### 18.11 Data Table Viewer

When displaying tabular JSON or CSV data:

- Render as `<table>` with sortable column headers (click to toggle asc/desc, show `▲` / `▼` indicator).
- Cap display to 50 rows by default; show row count footer.
- For JSON files with multiple arrays: use a tab bar (`.dt-tab-bar` / `.dt-tab`) to switch between arrays plus a **Raw JSON** tab.
- For text files: display first 10 KB inline in a monospace block.
- CSV/Excel files: open in a new browser tab (no inline preview).

### 18.12 Local HTTP Server (`serve.py`)

Each project that has a UI must include a `serve.py` at the project root. Requirements:

**Stack and dependencies:**
- **Zero external dependencies** — use only Python stdlib (`http.server`, `socketserver`, `subprocess`, `threading`, `json`, `uuid`, `argparse`, `pathlib`).
- Designed to run on restricted corporate computers: no conda environment, no pip install, no admin rights required for the launcher itself. Engine backends may require their own environments but the HTTP layer must be stdlib-only.

**Server class:**
- **`ReusableTCPServer`** — subclass `socketserver.TCPServer` with `allow_reuse_address = True` and `daemon_threads = True`. Prevents port-in-use errors on restart; ensures background threads do not block process exit.
- Override `handle_error` to suppress `ConnectionResetError` silently (DEBUG log only, no traceback). Browsers frequently reset idle connections and this floods the console.
- `if __name__ == "__main__"` guard around all startup code.

**Port handling:**
- Accept `--port` via `argparse`; default port 5000.
- Before binding, probe the port with `socket.connect_ex(("127.0.0.1", port))`. If occupied, automatically try the next port up to 10 increments and print the resolved port clearly: `Serving on http://localhost:{port}`.
- On `OSError: [Errno 10048]` (Windows) or `[Errno 98]` (Linux), print a human-readable message and suggest `--port <other>`.

**Root index page — dynamic tool launcher:**
- `GET /` returns a **dynamically generated** HTML page (`_build_index()`), not a static file. Regenerated on every request so new HTML files appear without restarting the server.
- Scans configured `SCAN_DIRS` (e.g. `["ui"]`) recursively for `*.html`, skipping `EXCLUDE_DIRS` (`node_modules`, `archive`, `backup`, `__pycache__`, `static`, `templates`).
- Groups files by folder with an icon and label per folder (`FOLDER_LABELS` dict).
- Provides a live search input (client-side JS, no server round-trip).
- Uses GitHub-dark inline styles — **no external CSS or font CDN dependency** — so the index renders on offline/restricted networks.
- Status bar shows total tool count and server port.

**Static file serving:**
- All non-API, non-root `GET` requests fall through to `SimpleHTTPRequestHandler` initialised with `directory = ROOT` where `ROOT = Path(__file__).parent.resolve()` (resolved absolutely at import time, never at request time).
- HTML files reference assets at root-relative paths (e.g. `/ui/eks.css`) — **never** at paths that assume a specific working directory.
- Apply a `Path.is_relative_to(ROOT)` security check on every resolved file path before serving. Return 403 if the path escapes `ROOT`.

**CORS:**
- `do_OPTIONS` returns HTTP 204 with `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`, `Access-Control-Allow-Headers: Content-Type`.
- All API JSON responses include `Access-Control-Allow-Origin: *`.

**Cache busting:**
- Override `end_headers()` to inject `Cache-Control: no-cache, no-store, must-revalidate` + `Pragma: no-cache` + `Expires: 0` on every response.

**Request routing** (priority order, first match wins — use `urllib.parse.unquote(self.path).split("?")[0]` for all path matching):

| Method | Path pattern | Handler |
|---|---|---|
| GET | `/` | `_build_index()` — dynamic tool-picker page |
| GET/POST/PUT/DELETE | `/api/v{N}/*` | Proxy → phase backend on `localhost:500{N}` |
| GET/POST | `/api/*` | 404 JSON — un-versioned, rejected |
| GET/POST | `/ollama/*` | Proxy → `localhost:11434` (Ollama LLM) |
| OPTIONS | `*` | CORS preflight |
| GET | anything else | `SimpleHTTPRequestHandler` static file |

**API proxy** (`_proxy`):
- Strip versioned prefix and forward to the target backend port. Pass through request body, `Content-Type`, and response status code.
- Catch `urllib.error.HTTPError` (forward status + body), `urllib.error.URLError` (502 + JSON), bare `Exception` (500 + JSON). Never propagate as unformatted traceback to the browser.
- Timeout: 120s for long-running pipelines.
- If the target backend is not reachable (connection refused), return `{"error": "Phase {N} backend not running on port 500{N}. Start it with: python eks/ui/backend/phase{N}_server.py"}` with HTTP 503 — not a generic 502.

**Ollama proxy** (`_proxy_ollama`):
- Strip `/ollama` prefix and forward to `localhost:11434`. Handles GET and POST. Timeout: 30s.
- If Ollama is not running, return `{"error": "Ollama not running on port 11434"}` with HTTP 503.

**Logging:**
- Suppress 200 and 304 log lines. Only print non-success codes to keep the console clean during polling.

### 18.13 Backend Phase Server Convention

Each phase of a multi-phase pipeline system must have its own dedicated backend server for running and testing that phase independently. Requirements:

**Design:**
- One backend server per phase: `phase{N}_server.py` in `<project>/ui/backend/`.
- Default port `BASE_PORT + N` where `BASE_PORT` is the launcher port (e.g. launcher on 5000 → phase servers on 5001, 5002, etc.).
- Each server uses only stdlib `http.server` for phases that do not require async production serving. The final user-facing phase may use FastAPI + uvicorn.

**Standalone operation (restricted computer requirement):**
- Every phase server **must** run standalone with `python phase{N}_server.py --port 500{N}` — no launcher required. This is the primary development and testing mode.
- The conda/virtual environment for that phase must be activated separately. The server should detect missing dependencies at startup and print a clear error: `Missing: duckdb. Run: pip install duckdb==1.5.1` rather than a bare `ModuleNotFoundError` traceback.
- Accept `--port` via `argparse`. If the default port is occupied, apply the same auto-probe logic as the launcher.

**Health endpoint:**
- Implement `GET /api/v{N}/status` as the first handled route, returning `{"status": "healthy", "version": "...", "phase": N, "timestamp": "..."}`. This endpoint must succeed even if optional heavy dependencies (Neo4j, Qdrant) are unavailable — report their availability in the response body rather than failing.

**Phase scope:**
- Each server exposes endpoints for its own phase only. Cross-phase data access (e.g. Phase 2 reading Phase 1's DuckDB registry) is done via direct Python import — not via HTTP calls between phase servers.

**Concurrency guard:**
- Return HTTP 409 if a long-running job is already `running` when a new start request arrives.
- Use `threading.RLock` for all shared state. One pipeline execution per phase server at a time.

**DuckDB cross-process safety:**
- Phases that open the shared DuckDB registry must use `_with_retry(fn, retries=3, delay=0.5)` on all read and write operations to handle lock contention when multiple phase servers run simultaneously.
- Document clearly in each phase server which database operations are read-only vs read-write.

**CORS:**
- Every response includes `Access-Control-Allow-Origin: *`.

### 18.14 Icons (Unicode)

Standard icon assignments across all project UIs:

| Purpose | Icon |
|---|---|
| File load / folder | 📂 |
| Help | ❓ |
| Settings / options | ⚙️ |
| Tree / hierarchy | 🌳 |
| Info | ℹ️ |
| Pipeline / dashboard | 📊 |
| Layout toggle | 🔲 |
| Run / execute | ▶ |
| Refresh | 🔄 |
| Success / pass | ✓ |
| Failure / error | ✗ |

### 18.15 Shared JS Library (`comUI`)

All UIs must use `common/universal_ui_design.js` for reusable interactive logic. The library exposes a `window.comUI` namespace with these modules:

| Module | Functions | Purpose |
|--------|-----------|---------|
| `comUI.theme` | `apply(name, storageKey)`, `initPicker(storageKey)` | Apply theme, toggle dropdown, persist to localStorage |
| `comUI.sidebar` | `resize(sbId, handleId, opts)`, `accordion(scopeEl)` | Drag-to-resize sidebars, collapsible accordion sections |
| `comUI.layout` | `toggle(btnId, opts)` | Cycle 1-col → 2-col → 3-col layout modes |
| `comUI.toast` | `show(msg, type, duration)` | Fixed-position notification with auto-dismiss |
| `comUI.modal` | `open(id)`, `close(id)`, `init(id)` | Overlay modal with background-click-to-close |
| `comUI.file` | `setupDropZone(zoneId, onFile)`, `readFileAsText(file)`, `readFileAsJSON(file)`, `readFileAsDataURL(file)` | Drag-drop zone, FileReader promises |
| `comUI.table` | `makeSortable(tableId)` | Column header click sort with ▲/▼ indicators |
| `comUI.utils` | `escHtml(s)`, `formatNum(n)`, `formatBytes(b)`, `setStatus(el, msg)`, `setStatusBar(leftMsg, rightMsg)` | Formatting and status bar helpers |

**Rules:**
- Include `<script src="/common/universal_ui_design.js">` before any page-specific JS.
- Use `comUI.*` functions instead of reimplementing theme toggle, sidebar resize, accordion, toast, modal, or layout switching in each page.
- Storage keys should follow the `<project>-<feature>` convention (e.g. `eks-theme`, `dcc-layout`, `code-tracer-sidebar-w`).
- The library has zero external dependencies — it is vanilla JS (ES5-compatible) with no npm imports.

### 18.16 Icon Bar and File Loading (from universal JS)

The `comUI.file.setupDropZone()` function implements the drag-and-drop requirements of §18.7. The `comUI.layout.toggle()` function implements the layout switching requirements of §18.8. Theme picker dropdown HTML structure must match:

```html
<button class="com-theme-btn" id="themeBtn">🎨 <span class="com-theme-dot"></span> Theme</button>
<div class="com-theme-menu">
  <div class="com-theme-opt active" data-theme="dark"><span class="com-theme-dot" style="background:#0d1117"></span> Dark</div>
  <div class="com-theme-opt" data-theme="light"><span class="com-theme-dot" style="background:#ffffff"></span> Light</div>
  <div class="com-theme-opt" data-theme="sky"><span class="com-theme-dot" style="background:#0b1a2e"></span> Sky</div>
  <div class="com-theme-opt" data-theme="ocean"><span class="com-theme-dot" style="background:#0a1929"></span> Ocean</div>
  <div class="com-theme-opt" data-theme="presentation"><span class="com-theme-dot" style="background:#000000"></span> Presentation</div>
</div>
```

Initialize with: `comUI.theme.initPicker('myapp-theme')`.

## 19. Data Health, Score, and Errors

### 19.1 Error Code Lifecycle

Every error code must complete a full lifecycle across 5+ sources:

1. **Define** — error code constant declared in the code module that raises it.
2. **Register** — code added to `<project>/config/schemas/<project>_error_config.json` with `id`, `category`, `message_template`, `severity`, and `resolution` fields.
3. **Validate** — code pattern must match the regex in `<project>_error_config_base.json`. Unknown pattern formats cause silent lookup failures in `ErrorManager`.
4. **Document** — code format and ranges must appear in the project's pipeline message/error design document (e.g., Appendix D).
5. **Resolve** — all code consumers (ErrorManager, BootstrapManager, pipeline orchestrator, test suite) must be able to resolve the code at runtime.

**Error code format conventions:**
- `S-{cat}-S-{id}` — system/infrastructure errors (e.g., `S-B-S-0601`)
- `P{phase}-{module}-{id}` — data pipeline errors (e.g., `P1-SETUP-FOLDERS`)
- `P1-BOOT-{reason}` — bootstrap/setup hybrid errors (e.g., `P1-BOOT-READINESS`)
- `B-{module}-{id}` — universal bootstrap errors (e.g., `B-CLI-001`, `B-{phase_id}-ERR`)

**Cross-source validation checklist:** When adding or changing any error code, verify:
- [ ] Code exists in `error_config.json` (registered with all metadata fields)
- [ ] Pattern matches regex in `error_code_base.json`
- [ ] Code format documented in design doc (Appendix D or equivalent)
- [ ] All 5 sources agree on the same `id`, `category`, and `severity`
- [ ] Test exercises the error path and verifies the resolved code

### 19.2 Message Catalog Management

- Every status, milestone, warning, and info message must be registered in `<project>_message_config.json` with a unique `id`.
- The message manager must use the correct project-specific catalog file (e.g., `eks_message_config.json`, not the generic `message_config.json`).
- Message catalog and error catalog must be kept in sync: every bootstrap phase, every pipeline phase, and every major operation must have corresponding entries in both catalogs.
- When a message ID is added to the catalog, the corresponding message-format definition must be added to the message base schema.

### 19.3 Independent Error Codes

Each business logic unit (function, phase, module) must have at least one independent error code defined to trace related errors. No two distinct error conditions may share the same error code. Error codes must be granular enough that a log entry uniquely identifies the failure point without additional context.

## 20. Neurogram, Compact Workplans, Records, and Logs for Knowledge of Each Project Folder

Refer to `dcc/workplan/ui_design/log_neurogram/`. Generate a neurogram network JSON file (`dcc_log_graph.json`) in the respective `<project>/output/` folder. Ensure details can be compacted into the JSON file.

## 21. Testing Notes

- `code_tracer` tests use `unittest`; `eks` tests use `pytest`.
- EKS tests must run from the repository root: `python -m pytest eks/test/`.
- EKS tests expect config files at `eks/config/` (relative to repo root).
- Test runtime artifacts go to `<project>/test_output/` (per §6.1). EKS tests create `eks/test_output/` for generated files and `eks/output/eks_registry.db` for the registry database.
- Test output directories (`test_output/`) must be added to `.gitignore` at both repository root and per-project levels.
- Test files that use relative paths (e.g., `Path("test_output/...")`) must scope those paths within the project directory (e.g., `Path("eks/test_output/...")`). Bare `Path("test_output/...")` resolves to the CWD (repo root) and violates §6.1.
- code_tracer tests use `unittest.main()` and can be run directly or via pytest.

**Minimum test coverage:**
- Every engine module (files in `engine/core/`, `engine/parsers/`, etc.) must have at least one test file exercising its primary entry points.
- Every public function should have at least one happy-path test.
- Every HTTP/WebSocket endpoint must have at least one integration test.
- A module with zero tests may not be marked as "complete" in any workplan.
- Test coverage gaps (modules without tests) must be logged as issues and tracked in the next phase workplan.

## 22. Formatting

- Prettier config at root: `printWidth: 100`, `singleQuote: true`, `endOfLine: "lf"`.

## 23. Bootstrap and Pre-Bootstrap Safety

### 23.1 Universal BootstrapManager Pattern

Every pipeline project must use a universal `BootstrapManager` (from `common/library/bootstrap/`) as the single entry point for initialization. The manager runs 8 standardized phases:

| Phase | Name | Purpose |
|-------|------|---------|
| P1 | CLI Parse | Parse command-line arguments for verbosity, paths, and overrides |
| P2 | Paths | Resolve project root, config dir, data dir, output dir via `resolve_paths()` |
| P3 | Config Registry | Load `ConfigRegistry` from schema/config files |
| P4 | Defaults | Apply schema-driven defaults for unset parameters |
| P5 | Schema Registry | Load and validate all schema files |
| P6 | Environment | OS detection + `test_environment()` dependency verification |
| P7 | Readiness Gate | Run `ValidationManager` (folder/file existence, required dependencies) |
| P8 | Parameters | Finalize system parameters (log level, retry, timeout, cache TTL) |

A project-specific subclass (e.g., `EKSBootstrapManager`) injects project-specific hooks: `ConfigRegistry` adapter, validation manager, CLI parser, path resolver, and ErrorManager/MessageManager factories.

### 23.2 Pre-Bootstrap Infrastructure (`_preload_infrastructure()`)

Before any bootstrap phase runs, the pipeline entry point must execute a **pure-stdlib** preload function that guards all `common.library` imports:

- Every non-stdlib import must be individually `try/except ImportError`-guarded.
- Every failure must immediately `print(msg, file=sys.stderr)` — errors are never silently collected.
- All variables must be pre-bound to safe defaults (`None`) before any step runs — a failure in step N must never cause `NameError` in step N+1.
- The preload function returns imported **classes** (not instantiated objects) — logger and heartbeat are instantiated in `main()` after the preload gate passes.
- Repository root must be injected into `sys.path` via a pure-stdlib walk (find ancestor containing both `<project>/` and `common/` anchors) before any import is attempted.

### 23.3 Environment/Dependency Check

- Bootstrap Phase 6 must run `test_environment()` from `common/library/core/system/tester.py` to verify all required/optional dependencies.
- `test_environment()` must maintain a `_PIP_TO_IMPORT` mapping for pip-name-to-import-name mismatches: `python-docx` → `docx`, `qdrant-client` → `qdrant_client`, `pymupdf` → `fitz`, `scikit-learn` → `sklearn`, etc.
- All dependencies listed in `eks.yml` (conda environment) must also be listed in the config `dependencies.required` or `dependencies.optional` section — the two sources must stay in sync.
- If `test_environment()` returns `ready=False`, bootstrap must raise a structured `BootstrapError` with the missing dependency names and installation instructions (e.g., "Run: conda activate eks && pip install <package>").

### 23.4 Ghost/Stale Directory Prevention

- Empty legacy directories (e.g., `eks/eks/`) can cause `discover_project_root()` to return the wrong project root, silently doubling path prefixes.
- Before path resolution, scan for and archive/delete any stale subdirectories that match the project anchor name.
- `discover_project_root()` must fall through to `default_base_path(anchor)` when an anchor directory exists but is empty or contains only irrelevant files.

## 24. Cross-Source Alignment Audit

When a concept (error code format, message ID, field name, configuration value, version number) spans 5+ independent sources, a formal cross-reference audit must be performed before the feature can be marked complete:

**Typical multi-source concepts and their sources:**
1. **Error codes**: `error_code_base.json` (pattern), `error_config.json` (registration), `error_setup_schema.json` (properties), design doc (Appendix D), library code (BootstrapError), project code (raise site)
2. **Message IDs**: `message_base.json` (format), `message_config.json` (registration), `message_setup_schema.json` (properties), design doc (Appendix D), message manager code
3. **Global paths**: `base_schema.json` (definitions), `config.json` (values), path resolver code, pipeline entry point, bootstrap manager, server code
4. **System parameters**: `base_schema.json` (definitions), `config.json` (values), `system_parameters` helper, pipeline entry point, each consumer module

**Audit procedure:**
1. List all sources where the concept appears.
2. For each source, verify: format names match, regex patterns accept all registered values, field names and types are consistent, and version numbers are aligned.
3. Run `grep` for the concept's identifiers across the entire project and `common/library/` — ensure no stale references to old names/formats exist.
4. Any mismatch in any source is a blocking defect — the feature is not complete until all 5+ sources agree.

## 25. File Output Lifecycle Management

### 25.1 Write-Only vs Read-Back Files

- **Read-back files** (registry databases, checkpoint state used by resume logic) must be persisted with unique names per job/run and have a documented retention policy.
- **Write-only files** (pipeline status JSON, debug logs, progress snapshots that are only served via in-memory API) must use a **single overwrite file** (e.g., `pipeline_output.json`) — never accumulate per-job copies.
- Before implementing any file output, document whether the file is ever read back by any code path. If the answer is "no", use the single-overwrite pattern.

### 25.2 Output Directory Hygiene

- `output/` directories accumulate files over repeated pipeline runs. Per-job JSON files grow unbounded (N runs × M JSON files). Implement one of:
  - Single overwrite file (preferred for write-only data)
  - Capped retention (keep last K files, delete oldest)
  - Explicit cleanup phase in the pipeline lifecycle
- At each phase completion, check `output/` for accumulated stale files and clean them up.
- Checkpoint files that are never used by resume/restart logic are dead code and should be removed — not just commented out.
