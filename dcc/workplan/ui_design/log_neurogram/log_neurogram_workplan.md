# Log Neurogram Network — Interactive DCC Log Explorer

**Document ID:** WP-UI-LOG-001  
**Current Version:** 1.5  
**Status:** ✅ APPROVED  
**Last Updated:** 2026-05-22  
**Lead:** Franklin Song

---
## Requirements
1. consider following nodes as core pillars:
- `folder`
- `engine`
- `workplan`
- `issue`
- `error code`
- `update`
- `test`
- `reprot`
- other markdown `reference file`
2. consider semantic relationships
- `folder` -> contain -> `log`, `report`, `workplan`, `reference file`
- `workpan` -> contain -> `scope`, `dependency`, `milesonte`, `phase` or `section`, `step`, `success criteria`, `reference file`
- `workplan` -> address -> `issue`, `requirement`,
- `workplan` -> target -> `engine`, `schema file`, `reference file`, `deliverables`
- `reprot` -> evaluate -> `workplan`
- `issue` -> address -> `error` -> target -> `error code`
- `update` -> fix -> `issue`
- `update` -> resolve -> `error code`
- `update` -> affect -> `engine`, `schema file`, `reference file`
- `test` -> evaluate -> `update`
- `test` -> target -> `engine`, `schema file`, `reference file`
3. multi-layer topology toggle
- layer 1: executive/architectural view. show only `folder`, `engine`, `workplan`, `report`, `issue`
- layer 2: operational view: show `update`, `error code`, `milestone`, `phase`, `step`
- layer 3: micro-audit view (hidden by defulat): expose underline `phase`, `step`, `success criteria`, and other sub nodes when a user clicks on or inspects a specific high-level node.
4. parent files (such as workplan, reports, update_log, issue_log, test_log, other markdown files) as the promary entity and store inner structures as structured metadata inside it.
- store sections and steps as an array of json objects inside a properties.content field.
- only extract `step` or `action` as an independent node if it explicitly linkes out to an external dependency, a code file, or a specific error_code. otherwise, roll up.
5. Embed the timestamp direclty as a flat property within the relevant node. use graph UI timeline filters to filter by date instead of using physical nodes.
6. use a hierarchical naming convention for node IDs or add a `path` property. such as `"context": "wp-document_id_handling.section-1.step-3"`, which will reserve graph edges exclusively for **semantic connections**.
---
## Data Model Specification (Derived from Requirements 1–6)

### Node Types

Each node becomes a **graph entity** in Vis.js. Nodes marked "embedded" are stored in the parent's `properties.content[]` array (not as graph nodes), per Req 4.

| # | Node Type | Layer | Storage | Source |
|---|-----------|-------|---------|--------|
| 1 | `folder` | 1 | Graph node | Directory tree under `dcc/workplan/` |
| 2 | `engine` | 1 | Graph node | Core DCC engines (core, initiation, processor, reporting, utility, schema, mapper, ai_ops) |
| 3 | `workplan` | 1 | Graph node | `*_workplan.md` files |
| 4 | `issue` | 1 | Graph node | `issue_log.md` |
| 5 | `report` | 1 | Graph node | `reports/*.md` files |
| 6 | `update` | 2 | Graph node | `update_log.md` |
| 7 | `error_code` | 2 | Graph node | `L3-L-V-0302` patterns in logs |
| 8 | `milestone` | 2 | Embedded | Workplan milestone tables |
| 9 | `phase` | 2–3 | Graph node (layer 2) / Embedded sub-items (layer 3) | Workplan phase sections |
| 10 | `step` | 2–3 | Graph node only if external ref; else embedded | Numbered lists in workplans |
| 11 | `success_criteria` | 3 | Embedded | `- [x] ...` checklist items |
| 12 | `scope` | 3 | Embedded | Workplan scope fields |
| 13 | `dependency` | 3 | Embedded | Dependency sections |
| 14 | `reference_file` | 3 | Graph node only if linked | External `.md`/`.py`/`.json` file refs |
| 15 | `session` | 3 | Graph node | `gemini.md` UUIDs |

### Node Field Structures

#### Graph Nodes (stored as top-level objects in `nodes[]`)

**folder**
```json
{ "id": "folder-pipeline_architecture", "type": "folder", "label": "pipeline_architecture",
  "path": "pipeline_architecture", "depth": 1 }
```

**engine**
```json
{ "id": "engine-core_engine", "type": "engine", "label": "Core Engine",
  "name": "core_engine", "connection_count": 0 }
```

**workplan**
```json
{ "id": "wp-wp-ui-log-001", "type": "workplan", "label": "Log Neurogram Network",
  "wid": "WP-UI-LOG-001", "version": "1.5", "status": "PENDING APPROVAL",
  "date": "2026-05-22", "domain": "ui_design", "path": "ui_design/log_neurogram/...",
  "properties": {
    "content": [
      {"type": "section", "title": "Objective", "order": 0},
      {"type": "section", "title": "Scope Summary", "order": 1},
      {"type": "scope", "text": "Parse 4 log files + 159 workplan files"},
      {"type": "milestone", "id": "M1", "text": "Data extraction", "status": "COMPLETE"},
      {"type": "dependency", "text": "Log Files at dcc/log/"},
      {"type": "phase", "id": "Phase 1", "status": "COMPLETE", "timeline": "Day 1"},
      {"type": "criteria", "text": "All 4 log files parsed", "status": "PENDING"}
    ],
    "references": ["dcc/log/issue_log.md", "dcc/log/update_log.md"]
  }
}
```
Notes per Req 4:
- `properties.content[]` stores sections, steps, criteria, milestones, scopes, dependencies as embedded JSON
- Only promotes to graph node if the item has an explicit external reference (e.g., `step` that mentions `dcc/core_engine/foo.py` or error code `L3-L-V-0302`)
- `properties.references[]` stores cross-file reference paths

**issue**
```json
{ "id": "issue-BLV-001", "type": "issue", "label": "BLV-001",
  "title": "Business Logic Validation Failed", "status": "RESOLVED",
  "date": "2026-04-15", "severity": "HIGH", "root_cause": "Missing null check...",
  "rows_affected": 1500, "files_changed": ["dcc/core_engine/validator.py"],
  "related_issues": ["BLV-002"], "error_codes": ["L3-L-V-0302"] }
```

**report**
```json
{ "id": "report-phase1_report", "type": "report", "label": "Phase 1 Report",
  "date": "2026-05-21", "path": "pipeline_architecture/reports/phase1_report.md",
  "report_id": "RPT-001", "version": "1.0", "status": "COMPLETE",
  "findings": [], "files_modified": [], "test_results": [] }
```

**update**
```json
{ "id": "update-2026-05-20-fix-validation", "type": "update", "label": "Fix validation bug",
  "date": "2026-05-20", "summary": "Added null check in validator.py",
  "phases": ["Phase 3"], "files_modified": ["dcc/core_engine/validator.py"],
  "linked_issue": "issue-BLV-001", "linked_test": "test-TC-042" }
```

**error_code**
```json
{ "id": "ec-L3-L-V-0302", "type": "error_code", "label": "L3-L-V-0302",
  "severity": "HIGH", "status": "fixed" }
```

**test**
```json
{ "id": "test-TC-042", "type": "test", "label": "TC-042",
  "date": "2026-05-20", "result": "PASS", "scope": "Validates null handling",
  "checks": ["Null input returns error"], "linked_issue": "issue-BLV-001",
  "linked_update": "update-2026-05-20-fix-validation" }
```

**phase** (graph node — only when needed as connection hub)
```json
{ "id": "phase-pipe-simp-001-1", "type": "phase", "label": "Phase 1",
  "phase_id": "1", "status": "COMPLETE", "timeline": "Day 1",
  "tasks": ["Parse log files"], "deliverables": ["Entity list"],
  "success_criteria": ["100% coverage"], "risks": ["Format inconsistency"] }
```

**step** (graph node — only when external ref exists)
```json
{ "id": "step-wp-eh-data-001-3", "type": "step", "label": "Run validation on input",
  "order": 3, "context": "wp-wp-eh-data-001.section-2.step-3",
  "link": "dcc/core_engine/validator.py" }
```

**session**
```json
{ "id": "session-a1b2c3d4", "type": "session", "label": "Session a1b2c3d4",
  "session_id": "a1b2c3d4-e5f6-..." }
```

**reference_file** (graph node — only when referenced from logs/workplans)
```json
{ "id": "file-validator-py", "type": "file", "label": "validator.py",
  "path": "dcc/core_engine/validator.py", "engine": "core_engine",
  "touch_count": 5}
```

#### Embedded Content (stored in `properties.content[]` — NOT graph nodes)

These items appear inside a parent node's `properties.content[]` array. Per Req 4, they are **not** independent graph entities unless they carry an external link.

```json
// Section
{"type": "section", "title": "Objective", "order": 0}
{"type": "section", "title": "Scope Summary", "order": 1}

// Step (embedded — no external ref)
{"type": "step", "text": "Install dependencies", "order": 1}

// Step (promoted to graph node — has external ref)
// This becomes a standalone node; omitted from properties.content
// Example: "step-wp-eh-data-001-3" above

// Success Criteria
{"type": "criteria", "text": "All 4 log files parsed", "status": "PENDING"}

// Scope
{"type": "scope", "text": "Parse 4 log files + 159 workplan files"}

// Dependency
{"type": "dependency", "text": "Log Files at dcc/log/",
 "link": "dcc/log/issue_log.md"}

// Milestone
{"type": "milestone", "id": "M1", "text": "Data extraction complete",
 "status": "COMPLETE"}

// Phase (embedded summary — full phase details stored in graph node if promoted)
{"type": "phase", "id": "Phase 1", "status": "COMPLETE", "timeline": "Day 1"}
```

### Edge Types (Semantic Connections Only — Per Req 6)

Edges are reserved exclusively for **semantic connections** between graph nodes. Embedded items use the parent's edges, not their own.

| Edge Type | Source → Target | Req Source |
|-----------|----------------|------------|
| `contains` | `folder` → `log`, `report`, `workplan`, `reference_file` | Req 2 |
| `contains` | `workplan` → `phase`, `step`, `scope`, `dependency`, `milestone`, `success_criteria`, `reference_file` | Req 2 |
| `addresses` | `workplan` → `issue` | Req 2 |
| `targets` | `workplan` → `engine`, `schema_file`, `reference_file`, `deliverable` | Req 2 |
| `evaluates` | `report` → `workplan` | Req 2 ("reprot" typo) |
| `addresses` | `issue` → `error_code` (via `error` → `error code`) | Req 2 |
| `fixes` | `update` → `issue` | Req 2 |
| `resolves` | `update` → `error_code` | Req 2 |
| `affects` | `update` → `engine`, `schema_file`, `reference_file` | Req 2 |
| `evaluates` | `test` → `update` | Req 2 |
| `targets` | `test` → `engine`, `schema_file`, `reference_file` | Req 2 |

**Additional cross-reference edges** (inferred from log structure, not from Req 2):

| Edge Type | Source → Target | Purpose |
|-----------|----------------|---------|
| `verified_by` | `update` → `test` | Update verified by test |
| `tested_by` | `issue` → `test` | Issue tested by test |
| `related_to` | `issue` → `issue` | Issues are related |
| `blocks` | `issue` → `issue` | One issue blocks another |
| `depends_on` | `issue` → `issue` | One issue depends on another |
| `belongs_to` | `phase` → `workplan` | Phase belongs to workplan |
| `belongs_to` | `report` → `workplan` | Report belongs to workplan |
| `belongs_to` | `file` → `engine` | File belongs to engine |
| `references` | `workplan` → `workplan` | Workplan references another |
| `session_for` | `session` → `issue` | Gemini session worked on issue |
| `documented_by` | `phase` → `report` | Phase documented by report |

### Storage Rules (Per Req 4–6)

1. **Parent-as-primary**: Every markdown file (workplan, report, log) becomes a graph node. Its internal structure (sections, steps, criteria, milestones, scopes, dependencies) is stored in `properties.content[]` as an ordered array of JSON objects.

2. **Promotion rule** (Req 4): A `step` or `action` is promoted from `properties.content[]` to an independent graph node **only if** its text contains an explicit link to:
   - A file path (`` `path/to/file.py` ``)
   - An error code (`L3-L-V-0302`)
   - A cross-reference (`Issue #123`, `Update #456`)
   - Otherwise, it stays embedded.

3. **Timestamp rule** (Req 5): Every node that has a date gets a flat `"date": "YYYY-MM-DD"` property. No physical `timestamp` nodes are created. The HTML time slider filters using this property.

4. **Naming convention** (Req 6): Node IDs follow hierarchical patterns:
   - `wp-{workplan_id}` for workplans
   - `issue-{issue_id}` for issues
   - `ec-{error_code}` for error codes
   - `folder-{path}` for folders
   - A `context` property stores hierarchical path for sub-elements: `"wp-document_id_handling.section-1.step-3"`

5. **Layer visibility** (Req 3): Each node type has a `layer` field (1, 2, or 3). The HTML provides 3 toggle buttons:
   - Layer 1 ON → executive nodes visible
   - Layer 2 ON → operational nodes visible
   - Layer 3 ON → micro-audit nodes visible (default: OFF)
   - Multiple layers can be active simultaneously.

---
## Revision Control & Version History

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 1.0 | 2026-05-21 | System | Initial workplan — proposed interactive neurogram network graph to explore DCC log data (issues, updates, tests, files, phases, error codes, engines, workplans). Single standalone HTML file, Vis.js force-directed graph, DCC shell layout, file:// compatible. |
| 1.1 | 2026-05-21 | System | Phase 1 expanded: added parsing of all 159 files under `dcc/workplan/` across 15 domain folders. New entity types: Workplan (from workplan files), Report (from reports/ subfolders). Updated entity counts, edge types, extraction rules, and success criteria. |
| 1.2 | 2026-05-21 | System | Updated graph data output path from `dcc/output/log_neurogram/dcc_log_graph.json` to `dcc/output/dcc_log_graph.json` (project root output folder). |
| 1.3 | 2026-05-21 | System | Updated `log_neurogram.html` output path to `dcc/ui/` folder (alongside other UI files). Updated `ui_help.json` to reference existing file at `dcc/ui/ui_help.json` (append, not create). |
| 1.4 | 2026-05-21 | System | All phases complete. Graph data generated (588 nodes, 341 edges). HTML webpage built with DCC shell layout, Vis.js force graph, tree view, filtering, search, timeline, export. ui_help.json updated with neurogram entries. |
| 1.5 | 2026-05-22 | System | Proposed fixes (PENDING APPROVAL): 8 gaps identified against Requirements (Sec 0) and spec. Added: 10.1 workplan coverage audit (105/159 files found, 12/15 domains). Existing gaps: graph data bloat (7919 nodes vs ~350), multi-layer toggle, timestamp-as-nodes, missing phase reports/log entries, `graphEdges` bug, missing features. See Sec 10 for full Implementation Plan. |

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
| 5 | Test via `file://` protocol — verify all interactions | Testing | ⏳ Requires verification (7 gaps found) |
| 6 | Log issue + generate phase report | Logging & Reporting | ⏳ PENDING (reports empty, no log entries) |

---

## 3. Index of Content

0. [Requirements](#requirements)
0. [Data Model Specification](#data-model-specification-derived-from-requirements-1-6)
0. [Revision Control & Version History](#revision-control--version-history)
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
9. [Requirements Implementation Plan (Proposed)](#10-requirements-implementation-plan-proposed--pending-approval)
10. [References](#11-references)

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
**Status:** ⏳ PENDING REWORK (see Sec 10)

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
**Status:** ⏳ PENDING REWORK (see Sec 10)

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

---

## 10. Requirements Implementation Plan (Proposed — PENDING APPROVAL)

*This section documents the gaps between the current v1.4 implementation and the Requirements defined in Section 0, and proposes specific implementation changes. Status of each item will be updated upon approval.*

### 10.1 Gap: Missing Nodes — Workplan Coverage Audit

**Problem:** The parser may be missing workplan files or entities due to format variations, unexpected folder structures, or regex failures. The workplan claims 159 files across 15 domain folders, but the parser found 105 files across 12 domains. The actual number of workplan files, reports, issues, updates, and tests in the graph may not match the ground truth in the repository.

**Implementation:**

1. **Enumerate complete file inventory** at parse time and compare against expected counts:
   ```python
   def audit_coverage():
       actual_files = list(WORKPLAN_DIR.rglob("*.md"))
       actual_reports = [f for f in actual_files if '/reports/' in str(f)]
       actual_workplans = [f for f in actual_files if 'workplan' in f.name or 'work_plan' in f.name]
       actual_domains = set(f.relative_to(WORKPLAN_DIR).parts[0] for f in actual_files if f.parent != WORKPLAN_DIR)
       
       # Compare against metadata claims
       coverage = {
           "total_files_found": len(actual_files),
           "workplans_found": len(actual_workplans),
           "reports_found": len(actual_reports),
           "domains_found": len(actual_domains),
           "domains_list": sorted(actual_domains),
           "files_missing_from_graph": [
               str(f.relative_to(WORKPLAN_DIR)) 
               for f in actual_files 
               if safe_id(f.stem) not in node_ids and 'workplan' in f.name
           ]
       }
       return coverage
   ```
2. **Log orphan/unmatched files** — After parsing, report which `.md` files in the workplan tree were not turned into any node (by filename or extracted ID):
   ```python
   all_parsed_ids = set(n['id'] for n in nodes)
   uncovered = []
   for f in all_wp_files:
       stem_id = safe_id(f.stem)
       # Check if any node ID or label contains the filename stem
       if not any(stem_id in n['id'] or stem_id in (n.get('path','') or '') for n in nodes):
           uncovered.append(str(f.relative_to(WORKPLAN_DIR)))
   ```
3. **Validate domain folders** — Ensure all 15 expected domains are represented. Flag missing ones in metadata output and phase reports.
4. **Cross-check log entity counts** — Parse `issue_log.md`, `update_log.md`, `test_log.md` with a lightweight header counter (count `## Issue #` / `<a id="issue-"` patterns) and compare against actual node counts:
   ```python
   issue_count_expected = len(re.findall(r'<a id="issue-', issue_text))
   issue_count_actual = sum(1 for n in nodes if n['type'] == 'issue')
   if issue_count_expected != issue_count_actual:
       warnings.append(f"Issue count mismatch: expected {issue_count_expected}, got {issue_count_actual}")
   ```
5. **Output coverage report** — Include a `coverage` section in the graph JSON metadata:
   ```json
   "coverage": {
       "expected_files": 159,
       "parsed_files": 105,
       "missing_domains": ["code_quality", "project_setup"],
       "missing_workplans": ["..."],
       "issue_coverage_pct": 100.0,
       "update_coverage_pct": 94.2
   }
   ```

### 10.2 Gap: Graph Data Bloat — `parse_file_content()` Creates Too Many Nodes

**Problem:** `parse_file_content()` at `parse_logs.py:306` creates independent graph nodes for every section header, step, action, criteria, milestone, deliverable, finding, lesson, table, analysis, dependency, case, scenario, scope, reason, and timestamp found in workplan/report files. This inflated the graph from the estimated ~350 nodes to 7,919 nodes (22× overshoot), making the graph visually unusable.

**Implementation:**

1. **Collapse sub-elements into `properties.content` arrays** (Req 4 — "store sections and steps as an array of JSON objects inside a `properties.content` field"):
   ```python
   # In parse_file_content(), replace individual node creation with content array:
   parent_node["properties"] = parent_node.get("properties", {})
   parent_node["properties"]["content"] = [
       {"type": "section", "title": "...", "order": 0},
       {"type": "step", "text": "...", "order": 1},
       {"type": "criteria", "text": "...", "status": "COMPLETE"},
   ]
   ```
2. **Promote only cross-referencing sub-elements to nodes** (Req 4 — "only extract step/action as an independent node if it explicitly links out to an external dependency, a code file, or a specific error_code; otherwise, roll up"):
   ```python
   # Before creating a node for a step, check for external references
   def has_external_ref(text):
       return bool(re.search(r'`[\w/.-]+\.\w+`', text)       # file reference
                   or re.search(r'[A-Z]\d-[A-Z]-[A-Z]-\d{4}', text)  # error code
                   or re.search(r'(?:issue|update|test)[-\s][\w-]+', text, re.I))  # cross-ref
   ```
3. **Target node count:** ~400–500 nodes (core pillars + promoted cross-references only).

### 10.3 Gap: Multi-Layer Topology Toggle Not Implemented (Req 3)

**Problem:** The HTML has a flat filter checkbox list (25 node types). Req 3 specifies three zoomable layers:
- Layer 1 — Executive/Architectural: `folder`, `engine`, `workplan`, `report`, `issue`
- Layer 2 — Operational: `update`, `error_code`, `milestone`, `phase`, `step`
- Layer 3 — Micro-audit: `phase`, `step`, `success_criteria`, sub-nodes (hidden by default)

**Implementation:**

1. Add `layer` field to each node type in `parse_logs.py` `node_types` array:
   ```python
   {"id": "issue", "label": "Issue", "layer": 1, ...},
   {"id": "update", "label": "Update", "layer": 2, ...},
   {"id": "criteria", "label": "Criteria", "layer": 3, ...},
   ```
2. Include `layer` in output JSON's `node_types` schema.
3. In `log_neurogram.html`, replace flat checkboxes with 3 layer toggle buttons at top:
   ```html
   <div id="layerToggles">
     <button data-layer="1" class="active">🏛️ Executive</button>
     <button data-layer="2">⚙️ Operational</button>
     <button data-layer="3">🔬 Micro-Audit</button>
   </div>
   ```
4. `applyFilters()` reads active layer(s) and auto-filters node types belonging to those layers.

### 10.4 Gap: Timestamps as Physical Nodes (Violates Req 5)

**Problem:** Req 5 states "embed the timestamp directly as a flat property within the relevant node. Use graph UI timeline filters to filter by date instead of using physical nodes." The parser creates 130 `timestamp` sub-nodes.

**Implementation:**

1. In `parse_file_content()`, remove the "Extract Timestamps" block (lines 320–325):
   - Delete: `timestamps = re.findall(...)` and the loop that creates `tsid` nodes
2. Instead, ensure every parent node has a `date` property set to the file's `Last Updated` or `Date` field.
3. The time slider in HTML already filters by `n.date` — no change needed on the frontend.

### 10.5 Gap: Phase Reports Not Generated

**Problem:** The workplan's Phase 6 requires 4 phase reports in `dcc/workplan/ui_design/log_neurogram/reports/`:
- `phase1_report.md` — Data Extraction Report
- `phase2_report.md` — Graph Generation Report  
- `phase3_report.md` — UI Build Report
- `phase5_test_report.md` — Test Results Report

The `reports/` directory exists but is empty.

**Implementation:**

1. Add a `--reports` flag to `parse_logs.py` that generates markdown reports:
   ```python
   def generate_report(phase, data):
       report = f"# Phase {phase} Report\n\n"
       report += f"**Date:** {datetime.now().date()}\n\n"
       report += f"## Summary\n\n{data['summary']}\n\n"
       report += f"## Statistics\n\n{json.dumps(data['stats'], indent=2)}\n\n"
       (REPORTS_DIR / f"phase{phase}_report.md").write_text(report)
   ```
2. Reports contain: entity counts, files parsed, edge types generated, any warnings/orphan edges.

### 10.6 Gap: No Log Entries for Neurogram

**Problem:** Phase 6 requires entries in `dcc/log/issue_log.md`, `update_log.md`, and `test_log.md` for the neurogram work, but none exist.

**Implementation:**

1. **Issue log entry** — Create a new issue in `issue_log.md`:
   ```
   <a id="issue-log-neurogram-001"></a>
   ### Issue Log Neurogram — Requirements Gap Fixes
   **Status:** OPEN
   **Date:** 2026-05-22
   **Severity:** MEDIUM
   **Description:** 7 gaps identified in log_neurogram v1.4 against Requirements section of the workplan. See workplan Sec 11.
   **Files Changed:** dcc/workplan/ui_design/log_neurogram/log_neurogram_workplan.md, parse_logs.py, dcc/ui/log_neurogram.html
   ```
2. **Update log entry** — One or more entries in `update_log.md` for phases as they are completed.
3. **Test log entry** — After fixes, a test entry logging verification results.

### 10.7 Gap: `graphEdges` Bug in `showFilePicker()`

**Problem:** `log_neurogram.html:410` references the undefined variable `graphEdges` instead of `graphData.edges`. Will throw `ReferenceError` if fetch fails and user picks a file.

**Implementation:**
- Change line 410: `graphEdges = ...` → `graphData.edges`

### 10.8 Gap: Missing Features vs Interactive Features Table (Phase 3)

**Problem:** Several features listed in the Phase 3 Interactive Features table are missing or incomplete:

| # | Feature | Status | Implementation |
| :--- | :--- | :--- | :--- |
| 7 | Search | `prompt()` dialog | Replace with inline `<input>` in title bar; implement real fuzzy search (simple Levenshtein or prefix match) |
| 13 | Mini-map | Missing | Add `<div id="minimap">` with a second vis.DataSet representing a zoomed-out overview; or use Vis.js built-in `network.setOptions({configure: ...})` + a canvas overlay |
| 14 | file:// FileReader fallback | Buggy (`graphEdges`) | Fix bug; add explicit folder-picker UI in Load panel |
| 16–18 | Layout toggle, resizable panels, collapsible panels | Minimal | Implement `split.js` or manual mouse-drag resize on left/right panels; add collapse animation |
| 15 | Theme toggle | Works | Already functional — no change needed |

**Implementation:**

1. **Inline search bar** (`log_neurogram.html`):
   ```html
   <div class="actions" style="display:flex;align-items:center;gap:4px">
     <input id="searchInput" type="text" placeholder="Search nodes..." 
            style="width:160px;padding:2px 6px;font-size:12px;background:var(--bg-input);border:1px solid var(--border);color:var(--text);border-radius:3px">
     <span id="searchCount" style="font-size:11px;color:var(--text2);min-width:40px"></span>
   </div>
   ```
   Add `input` event listener that filters nodes in real time.

2. **Mini-map** — Use Vis.js `network.setOptions({configure: ...})` or a dedicated mini canvas. Simplest approach: add a small `<canvas>` overlay in the bottom-right corner of the graph area that mirrors the main network.

3. **Resizable panels** — Add `mousedown` listeners on panel borders:
   ```javascript
   function makeResizable(panelId, handleId, direction) {
     const handle = document.getElementById(handleId);
     const panel = document.getElementById(panelId);
     handle.addEventListener('mousedown', (e) => {
       document.addEventListener('mousemove', resize);
       document.addEventListener('mouseup', () => document.removeEventListener('mousemove', resize));
     });
   }
   ```

---

## 11. References

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
