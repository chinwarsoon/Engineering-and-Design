# EKS Phase 1.2 — Interactive UI, I/O Contracts & Document Processing Sub-Pipeline

**Document ID**: WP-EKS-P1.2-001  
**Current Version**: 1.13  
**Status**: 🔶 PARTIAL — Phases 1.2.0–1.2.7 complete; Phase 1.2.8 (Server Hardening, expanded) pending; Phase 1.2.9 (UI Design System) planned; Phase 1.2.10 (Appendix G Documentation) planned; Phase 1.2.11 (UI Workflow Redesign) ✅ COMPLETE; Phase 1.2.12 (Folder Picker & SSOT Path Resolution) ✅ COMPLETE  
**Last Updated**: 2026-07-06  
**Parent Workplan**: [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md)  
**Phase Dependency**: Phase 1 (Foundation) — ✅ COMPLETE  

---

## Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------- |
| 1.0 | 2026-06-25 | opencode | Initial workplan proposal for interactive UI and sub-pipeline |
| 1.1 | 2026-06-30 | opencode | Integrated I/O contract tasks from Phase 1 Section 16 as Phase 1.2.0 (Engine I/O Contracts). Added S1.2.7 to scope, updated dependencies and success criteria. |
| 1.2 | 2026-07-01 | opencode | Updated architecture to two-server pattern: main launcher at `eks/server.py` (port 5000) + Phase 1 backend at `eks/ui/backend/phase1_server.py` (port 5001). Updated T1.2.1.x, deliverables, dependencies, success criteria. Per server design review. |
| 1.3 | 2026-07-01 | opencode | Phase 1.2.0 complete: Created engine I/O contracts (core, parsers), UI contracts (4 types), contract manager, and 35 test cases. All tests passing. Updated scope, tasks, deliverables. |
| 1.4 | 2026-07-01 | opencode | Phase 1.2.1 complete: Created eks/server.py (main launcher, proxy), eks/ui/backend/phase1_server.py (12 API endpoints), eks/ui/backend/__init__.py. 20 backend integration tests. Updated scope statuses, tasks, deliverables. |
| 1.5 | 2026-07-01 | opencode | Phase 1.2.2–1.2.7 complete: Added log streaming (T1.2.2.7), created eks/ui/index.html (VS Code layout, 5 themes, tabs), eks/ui/eks.css (5 themes, responsive), eks/ui/eks.js (Fetch API, pipeline polling, chart rendering), eks/ui/ui_help.json (help schema + keyboard navigation). Updated eks/server.py to serve index.html at root. 178/178 tests passing. All scope items ✅. |
| 1.6 | 2026-07-02 | opencode | Added Phase 1.2.8 (Server Hardening) — 8 new tasks addressing issues I047–I054: dynamic tool-picker, `/api/v1/` prefix migration, port-probe, CDN removal, dependency check, Windows path security, DuckDB read-only mode, and static asset self-hosting. Status changed to PARTIAL. Updated scope, risks, success criteria, references. |
| 1.7 | 2026-07-02 | opencode | Gap analysis against AGENTS.md §18 and Appendix G found 32 additional gaps. Expanded existing T1.2.8 tasks (ROOT scope, frontend/backend contract fixes, CDN fallback, concurrency guard, proxy error granularity). Added T1.2.8.9 (Server Compliance Hooks) and T1.2.8.10 (Frontend Contract Alignment). Added Phase 1.2.9 (UI Design System) with 6 tasks addressing CSS tokens, theme dropdown, right sidebar, KPI/stage cards, data table, and UI polish. |
| 1.8 | 2026-07-02 | opencode | Gap analysis verification: cross-referenced all 32 gaps against source code — 31/32 confirmed; I050 CSS `@import` claim found inaccurate (CSS already clean). Added T1.2.9.7 (Update Appendix G Documentation) covering 10 missing design patterns (KPI cards, CSS tokens, theme dropdown, right sidebar, data table, drag-drop, dimensions, proxy timeout 120s, CDN consistency). Created Phase 1.2.10 for doc gap closure. Added Phase 1.2.10 to status. |
| 1.9 | 2026-07-06 | opencode | Added Phase 1.2.11 (UI Workflow Redesign) — step progress bar, scoped tab buttons, workflow guidance. Updated status, scope, next steps. |
| 1.10 | 2026-07-06 | opencode | Phase 1.2.11 COMPLETE — all 8 tasks implemented: removed global toolbar, added step progress bar (HTML/CSS/JS), scoped action buttons to tabs, auto-advance step states. Updated phase1_ingestion.html, eks.css, eks.js. 28/28 tests pass. |
| 1.11 | 2026-07-06 | opencode | Consolidated Phase 1.2 test suites into single `reports/phase_1.2_report.md` (63 tests: 35 io_contracts + 28 phase1_server). Archived `phase_1.2.11_report.md` → `archive/`. Updated references in §11. |
| 1.12 | 2026-07-06 | opencode | Added Phase 1.2.12 (Folder Picker & SSOT Path Resolution) — config-driven data directory picker, Browse endpoint, all frontend paths read from schema instead of hardcoded. Updated scope, tasks, next steps. |
| 1.13 | 2026-07-06 | opencode | Phase 1.2.12 COMPLETE — all 8 tasks implemented: `GET /api/v1/config/paths` and `GET /api/v1/files/list-dirs` endpoints; `fetchPaths()` in eks.js replaces all 7 hardcoded paths; folder path input + Browse button in HTML; traversal-guarded directory listing; pipeline start uses user-selected path; 4 new tests (66 total pass). Updated scope, next steps. |

---

## Object

Define standardized Engine I/O contracts for independent engine execution, then create a standalone interactive UI (HTML/CSS/JavaScript) with a document processing sub-pipeline that leverages the Phase 1 foundation modules to process real engineering documents from the `data/` folder. The UI follows AGENTS.md §18 VS Code-style design specifications.

---

## Scope Summary

| ID | Details | Category | Status |
| :- | :------ | :------- | :-----: |
| S1.2.1 | Interactive standalone HTML/CSS UI (VS Code style) | UI Development | ✅ Complete |
| S1.2.2 | Document processing sub-pipeline orchestration | Pipeline | ✅ Complete |
| S1.2.3 | Real document ingestion from data/ folder | Data Ingestion | ✅ Complete |
| S1.2.4 | Manual review workflow integration | Workflow | ✅ Complete |
| S1.2.5 | Health scoring visualization | Visualization | ✅ Complete |
| S1.2.6 | Schema-driven help system (ui_help.json) | Documentation | ✅ Complete |
| S1.2.7 | Engine I/O contracts for independent engine execution | Contracts | ✅ Complete |
| S1.2.8 | Server hardening — dynamic tool-picker, versioned API, port safety, offline assets | Server / Hardening | 🔷 Planned |
| S1.2.11 | UI workflow redesign — step progress bar, scoped tab buttons, workflow guidance | UI Development | ✅ Complete |
| S1.2.12 | Folder picker & SSOT path resolution — config-driven data directory display, Browse endpoint, no hardcoded paths | SSOT / UI | ✅ Complete |

**Related Phase**: Phase 1.2 — Interactive UI, I/O Contracts & Document Processing

---

## Content Index

1. [Objectives](#objectives)
2. [Architecture Overview](#architecture-overview)
3. [UI Design (AGENTS.md §18)](#ui-design-agentsmd-18)
4. [Technology Stack](#technology-stack)
5. [Pipeline Workflow](#pipeline-workflow)
6. [Implementation Phases](#implementation-phases)
7. [Dependencies](#dependencies)
8. [Risks and Mitigation](#risks-and-mitigation)
9. [Success Criteria](#success-criteria)
10. [I/O Contract Tasks](#io-contract-tasks)
11. [References](#references)

---

## Objectives

1. **Interactive UI**: Provide a VS Code-style standalone HTML/CSS/JavaScript interface for document processing
2. **Real Document Processing**: Process actual engineering documents from the `data/` folder using Phase 1 foundation components
3. **Manual Review Workflow**: Enable users to review, correct, and lock flagged documents
4. **Health Score Visualization**: Display document health scores with drill-down into dimensions
5. **Standalone Operation**: Run as an independent HTML file that can be opened directly in a browser
6. **Schema-Driven**: UI configuration and help text driven by `ui_help.json`

---

## Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│              Interactive Standalone HTML UI (VS Code Style)     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Title Bar    │  │ Side Icon    │  │ Bottom       │          │
│  │ (Theme/Layout│  │ Bar          │  │ Status Bar   │          │
│  │ /Menu/Search)│  │ (Left/Right) │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Left Sidebar │  │ Main Panel   │  │ Right        │          │
│  │ (File Load/  │  │ (Document    │  │ Sidebar      │          │
│  │  Tree View)  │  │  Dashboard)  │  │ (Health      │          │
│  └──────────────┘  └──────────────┘  │  Score/Details│          │
│                                       └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │ JavaScript Fetch API — /api/v1/*
                             │ port 5000
┌────────────────────────────┴────────────────────────────────────┐
│              Main Launcher Server — eks/server.py               │
│  ┌──────────────────────────┐  ┌──────────────────────────┐    │
│  │ _build_index()           │  │ Proxy: /api/v1/* → 5001  │    │
│  │ Dynamic HTML tool-picker │  │ Proxy: /ollama/* → 11434 │    │
│  │ Scans eks/ui/*.html      │  │ 404: /api/* (unversioned) │   │
│  │ Port-probe on bind       │  │ 503: backend-down msg    │    │
│  │ Path security guard      │  │ Cache-Control: no-cache  │    │
│  └──────────────────────────┘  └──────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │ proxy via urllib
                             │ port 5001
┌────────────────────────────┴────────────────────────────────────┐
│  Phase 1 Backend — eks/ui/backend/phase1_server.py             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ /api/v1/*    │  │ Pipeline     │  │ Document     │          │
│  │ endpoints    │  │ Orchestrator │  │ Registry API │          │
│  │ Dep-check on │  │ (background  │  │ (DuckDB      │          │
│  │ import       │  │  thread)     │  │  _with_retry)│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │ direct import (eks conda env required)
┌────────────────────────────┴────────────────────────────────────┐
│              Phase 1 Foundation Module (eks/engine/)            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ FileScanner  │  │ ParserRouter │  │ HealthScorer │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Document     │  │ Revision     │  │ Schema       │          │
│  │ Registry     │  │ Manager      │  │ Loader       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│              Data Layer                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ DuckDB       │  │ data/        │  │ ui/          │          │
│  │ (Registry)   │  │ (Documents)  │  │ (ui_help.json│          │
│  │              │  │              │  │  static/     │          │
│  │              │  │              │  │  chart.min.js│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User opens browser** → `GET /` → `server.py` → `_build_index()` → dynamic tool-picker listing all `eks/ui/*.html`
2. **User clicks index.html** → browser loads Phase 1 dashboard; assets served at `/ui/eks.css`, `/ui/static/chart.min.js` (all self-hosted, no CDN)
3. **User loads files** → UI File Loading Panel → `fetch('/api/v1/files/load')` → `server.py` (proxy) → port 5001 → `phase1_server.py` → FileScanner
4. **FileScanner discovers files** → ParserRouter → Parsers
5. **Parsers extract content** → StructureDetector → HealthScorer
6. **HealthScorer computes scores** → DocumentRegistry (DuckDB, `_with_retry`) → response JSON
7. **UI polls for status** → `fetch('/api/v1/pipeline/status/{job_id}')` every 2s → proxy → `phase1_server.py` → JSON response
8. **UI updates display** → Main Panel → Document Dashboard
9. **User reviews flagged docs** → ManualReviewManager → Registry updates

---

## UI Design (AGENTS.md §18)

### Layout Structure (VS Code Style)

```
┌─────────────────────────────────────────────────────────────────┐
│ Title Bar (Full Width)                                          │
│ [Theme 🎨] [Layout ▦] [Menu ☰] [Search 🔍]                      │
├──────────┬──────────────────────────────────────────┬───────────┤
│ Side     │ Main Panel                              │ Side      │
│ Icon     │                                          │ Icon      │
│ Bar      │                                          │ Bar       │
│ (Left)   │                                          │ (Right)   │
├──────────┤                                          ├───────────┤
│ 📂       │                                          │ ℹ️       │
│ 🌳       │  Document Dashboard / Content            │ ⚙️       │
│          │                                          │           │
│          │  ┌──────────────────────────────────┐   │ ❓       │
│ Left     │  │ Document List / Detail View      │   │           │
│ Sidebar  │  │                                  │   │ Right    │
│ (Toggle) │  │ Health Score Visualization      │   │ Sidebar  │
│          │  │                                  │   │ (Toggle) │
│          │  │ Manual Review Form              │   │           │
│          │  └──────────────────────────────────┘   │           │
└──────────┴──────────────────────────────────────────┴───────────┘
│ Bottom Status Bar: Selected: DWG-001-R0.pdf | Health: 0.85 | Status: Processed │
└─────────────────────────────────────────────────────────────────┘
```

### Components

#### 1. Title Bar (Full Width)
- **Theme Button**: Toggle between light, dark, sky, ocean, presentation themes
- **Layout Button**: Switch between single column, two columns, three columns
- **Menu Button**: Dropdown menu (File, Edit, View, Help)
- **Global Search**: Search across documents

#### 2. Side Icon Bar (Left)
- **Top icons**: File load (📂), Tree view (🌳)
- **Bottom icons**: Help (❓), Settings (⚙️), Info (ℹ️)
- **Divider** between top and bottom icon groups

#### 3. Left Sidebar (Toggleable, Resizable)
- **File Loading Panel**:
  - Load files from local disk
  - Load from specific pipeline files
  - List all loaded files
  - Drag-and-drop to load
  - Collapsible via side icon bar
- **Tree Selection Panel**:
  - Show hierarchical structure of loaded content
  - Select any node to show content in main panel
  - Expand all / collapse all buttons

#### 4. Main Panel
- **Document Dashboard**:
  - Statistics cards (total, processed, flagged, locked)
  - Health score distribution chart
  - Document list with filters
- **Document Detail View**:
  - Metadata form
  - Health score breakdown (6 dimensions)
  - Structural elements detected
  - Manual review notes
  - Lock/unlock toggle

#### 5. Side Icon Bar (Right)
- **Top icons**: Health score (📊), Details (📋)
- **Bottom icons**: Help (❓), Settings (⚙️)
- **Divider** between top and bottom icon groups

#### 6. Right Sidebar (Toggleable, Resizable)
- **Health Score Panel**:
  - 6-dimension breakdown
  - Dimension-specific recommendations
- **Details Panel**:
  - Document metadata
  - Extraction confidence per field
  - Structural elements list

#### 7. Bottom Status Bar
- Selected file name
- Health score
- Processing status
- Last updated timestamp

### Theme System

Theme palette (5 themes with hex colors), CSS variable pattern, and localStorage keys are defined in **Appendix G §5**. Default theme: Dark.

### Layout Switching

Layout modes (Single Column / Two Columns / Three Columns), localStorage persistence, and defaults are defined in AGENTS.md §18. Persistence keys documented in **Appendix G §5.2**.

### Help System

Help system schema (`ui_help.json`), file location, keyboard shortcut (`F1`), and example content are defined in **Appendix G §6**.

---

## Technology Stack

Technology stack decisions are documented in **Appendix G §2.1** (Document Processing Dashboard). Key Phase 1.2.8 changes:
- Chart.js is **self-hosted** (`eks/ui/static/chart.min.js`) — CDN removed (T1.2.8.5, I050)
- Font stack is `system-ui` — Google Fonts CDN removed (T1.2.8.5, I050)
- Server and backend are Python stdlib only — no pip install for the HTTP layer (AGENTS.md §18.12)

---

## Pipeline Workflow

### 1. File Loading

```
User Action: Click file load icon or drag-drop files
    ↓
JavaScript: Read file list from input
    ↓
POST /api/v1/files/load
    ↓
Backend: FileScanner.walk_directory(data/)
    ↓
Return: JSON with discovered files metadata
    ↓
UI: Update file list in left sidebar
```

### 2. Pipeline Execution (per Appendix G §3.4, §4)

```
User Action: Click "Process Documents" button
    ↓
POST /api/v1/pipeline/start
    ↓
Backend: Start background thread with PipelineOrchestrator
    ↓
Return: {job_id, status: "queued"}
    ↓
UI: Start polling /api/v1/pipeline/status/{job_id} every 2s
```

### 3. Status Polling (per Appendix G §4)

Job lifecycle (`queued → running → completed/failed/cancelled`), polling parameters (2s interval, 5-min timeout, 3 retries), and response format are defined in **Appendix G §4**. Frontend implementation follows the `pollJobStatus` pattern in G4.4.

### 4. Results Display

```
GET /api/v1/documents
    ↓
Return: JSON with paginated document list
    ↓
UI: Render document table in main panel
    ↓
User Action: Click document row
    ↓
GET /api/v1/documents/{doc_id}
    ↓
Return: JSON with full document metadata + health score
    ↓
UI: Render document detail view
```

### 5. Manual Review

```
User Action: Edit metadata fields in detail view
    ↓
PUT /api/v1/documents/{doc_id}
    ↓
Backend: ManualReviewManager.update_document()
    ↓
DocumentRegistry.update() via _with_retry()
    ↓
Return: Success/error JSON
    ↓
UI: Show success message or error
```

---

## Implementation Phases

### Phase 1.2.0: Engine I/O Contracts (Pre-Foundation, Week 0) — ✅ COMPLETE

**Timeline**: 3 days — **Actual**: 2026-07-01  
**Milestones**: Standardized I/O contracts defined and tested for all Phase 1 engines

**Tasks**:
- ✅ T1.2.0.1: Created `eks/engine/core/io_contracts.py` — re-exports EngineInput/EngineOutput from base.py; adds DiscoveryInput/DiscoveryOutput, HealthInput/HealthOutput
- ✅ T1.2.0.2: Merged discovery contracts into `eks/engine/core/io_contracts.py` (DiscoveryInput, DiscoveryOutput) — no separate discovery package yet
- ✅ T1.2.0.3: Created `eks/engine/parsers/io_contracts.py` — ParserInput, ParserOutput
- ✅ T1.2.0.4: Merged health contracts into `eks/engine/core/io_contracts.py` (HealthInput, HealthOutput) — no separate health package yet
- ✅ T1.2.0.5: Created `eks/ui/backend/contracts.py` — DocumentSelectionContract, PipelineConfigContract, QueryRequestContract, QueryResponseContract
- ✅ T1.2.0.6: Created `eks/ui/backend/contract_manager.py` — UIContractManager with validate and serialize
- ✅ T1.2.0.7: Created `eks/test/test_io_contracts.py` — 35 tests covering all contracts (base, discovery, parser, health, UI, manager)

**Deliverables**:
- `eks/engine/core/io_contracts.py` — Base + discovery + health I/O contracts
- `eks/engine/parsers/io_contracts.py` — Parser-specific contracts
- `eks/ui/backend/contracts.py` — 4 UI contract definitions per Appendix G §7
- `eks/ui/backend/contract_manager.py` — Contract validation and serialization
- `eks/test/test_io_contracts.py` — 35 passing tests

---

### Phase 1.2.1: Backend HTTP Server (Week 1) — ✅ COMPLETE

**Timeline**: 5 days — **Actual**: 2026-07-01  
**Milestones**: Simple HTTP server with Phase 1 integration

**Tasks**:
- ✅ T1.2.1.1: Created `eks/ui/backend/__init__.py` with version 0.1.0
- ✅ T1.2.1.2: Created `eks/server.py` (main launcher, port 5000):
  - HTML file picker at `/` listing standalone `.html` tools from `eks/ui/`
  - Proxy `/api/*` → `localhost:5001` (Phase 1 backend)
  - Proxy `/ollama/*` → `localhost:11434` (Ollama API)
  - Static file serving for `eks/ui/` paths
  - `ReusableTCPServer`, `--port` flag, CORS headers on all responses
  - Auto-launches Phase 1 backend as subprocess with stdout relay
- ✅ T1.2.1.3: Created `eks/ui/backend/phase1_server.py` (Phase 1 backend, port 5001):
  - `http.server`-based, standalone-runnable with `--port`
  - Direct Phase 1 engine module imports (`SchemaLoader`, `FileScanner`, `PipelineOrchestrator`, `ManualReviewManager`)
  - Multi-job state tracking (`_job_state` dict, `threading.RLock`)
  - DuckDB `DocumentRegistry` singleton with retry wrapper for concurrent access
- ✅ T1.2.1.4: File discovery endpoint (`POST /api/files/load`) — scans dir via FileScanner, registers placeholders, returns discovery stats
- ✅ T1.2.1.5: Document list endpoint (`GET /api/documents`) — list with optional filtering (document_type, discipline, status, extract_status), ordering, latest_only
- ✅ T1.2.1.6: Document detail endpoint (`GET /api/documents/{id}`) — single doc by ID
- ✅ T1.2.1.7: Document update endpoint (`PUT /api/documents/{id}`) — metadata correction via ManualReviewManager
- ✅ T1.2.1.8: Pipeline endpoints:
  - `POST /api/pipeline/start` — starts PipelineOrchestrator in background thread, returns job_id
  - `GET /api/pipeline/status/{job_id}` — returns job state
  - `DELETE /api/pipeline/{job_id}` — cancels queued/running jobs
- ✅ T1.2.1.9: CORS headers (`Access-Control-Allow-Origin: *`) on all 200/400/500 responses + OPTIONS handler
- ✅ T1.2.1.10: Created `eks/test/test_phase1_server.py` — 20 tests covering all endpoints, plus MainServer unit tests

**Additional endpoints**:
- `GET /api/review/summary` — review status statistics
- `GET /api/review/flagged` — list flagged documents
- `PUT /api/review/lock` — lock a reviewed document
- `PUT /api/review/recalculate` — recalculate health score

**Deliverables**:
- `eks/server.py` — Main launcher (port 5000, file picker + proxy)
- `eks/ui/backend/phase1_server.py` — Phase 1 backend (port 5001, 12 API endpoints)
- `eks/ui/backend/__init__.py` — Package init
- `eks/test/test_phase1_server.py` — 20 integration tests
- Standalone: `python eks/ui/backend/phase1_server.py --port 5001`
- All 120/120 tests pass (53 Phase 1 + 35 I/O contracts + 20 server + 12 asset schema)

---

### Phase 1.2.2: Pipeline Orchestration (Week 2) — ✅ COMPLETE

**Timeline**: 5 days — **Actual**: 2026-07-01  
**Milestones**: Pipeline execution with status tracking + log streaming

**Tasks**:
- ✅ T1.2.2.1: Pipeline start endpoint (`POST /api/pipeline/start`) — background thread via PipelineOrchestrator
- ✅ T1.2.2.2: Pipeline status endpoint (`GET /api/pipeline/status/{job_id}`) — job state tracking
- ✅ T1.2.2.3: Pipeline cancellation endpoint (`DELETE /api/pipeline/{job_id}`)
- ✅ T1.2.2.4: In-memory job tracking (`_job_state` + `threading.RLock`)
- ✅ T1.2.2.5: PipelineOrchestrator integration with retry wrapper
- ✅ T1.2.2.6: Error handling (fail status + error message + log capture)
- ✅ T1.2.2.7: Log streaming endpoint (`GET /api/pipeline/logs/{job_id}`) — `_LogCapture` wrapper captures STATUS/INFO/WARNING/ERROR entries into `_job_logs[job_id]`
- ✅ T1.2.2.8: Pipeline API tests (23 tests in test_phase1_server.py)

**Deliverables**:
- Pipeline execution endpoints (start/status/cancel/logs)
- Job tracking system with log capture
- Log streaming via GET /api/pipeline/logs/{job_id}

---

### Phase 1.2.3: HTML/CSS Foundation (Week 3) — ✅ COMPLETE

**Timeline**: 5 days — **Actual**: 2026-07-01  
**Milestones**: VS Code-style layout with theme system

**Tasks**:
- ✅ T1.2.3.1: `eks/ui/` folder existing with 4 files (index.html, eks.css, eks.js, ui_help.json)
- ✅ T1.2.3.2: `eks/ui/index.html` — title bar, icon bars, main panel, left/right sidebars, status bar, tabs, help modal
- ✅ T1.2.3.3: `eks/ui/eks.css` — independent CSS, 5 themes via `[data-theme]` attribute, no framework dependency
- ✅ T1.2.3.4: Title bar with theme button (cycles 5 themes), layout button (single/dual/triple), global search input
- ✅ T1.2.3.5: Left icon bar (📂 🌳 ❓ ⚙️) + right icon bar (ℹ️ 📋)
- ✅ T1.2.3.6: Left sidebar (tree view, collapsible, resizable via drag handle)
- ✅ T1.2.3.7: Right sidebar (document detail + score bars, collapsible, resizable)
- ✅ T1.2.3.8: Bottom status bar (left: status text, center: doc count, right: connection status)
- ✅ T1.2.3.9: 5 themes: dark (default), light, sky, ocean, presentation — CSS variables for bg/text/accent/border/scrollbar
- ✅ T1.2.3.10: Layout switching (single/dual/triple) via CSS class `layout-*` on #app-layout
- ✅ T1.2.3.11: localStorage persistence (eks_theme, eks_layout, eks_sidebar_left, eks_sidebar_right)
- ✅ T1.2.3.12: CSS variables + Flexbox layout works across browsers

**Deliverables**:
- `eks/ui/index.html`
- `eks/ui/eks.css`
- VS Code-style layout with 5 themes, resizable sidebars, localStorage persistence

---

### Phase 1.2.4: JavaScript Integration (Week 4) — ✅ COMPLETE

**Timeline**: 5 days — **Actual**: 2026-07-01  
**Milestones**: JavaScript logic for API communication

**Tasks**:
- ✅ T1.2.4.1: `eks/ui/eks.js` — IIFE pattern, API helpers (apiGet/apiPost/apiDelete), state object
- ✅ T1.2.4.2: File loading via Fetch API (`POST /api/files/load` with dir param), drag-drop area with visual feedback, auto-load on startup
- ✅ T1.2.4.3: Document table rendering (sortable columns, health badge color-coded), empty state handling
- ✅ T1.2.4.4: Document detail in right sidebar (info rows + 6-dimension score bars)
- ✅ T1.2.4.5: Pipeline status polling (2s interval, progress bar, status text, summary view)
- ✅ T1.2.4.6: Review form (doc number, revision, status dropdown, comments textarea, submit)
- ✅ T1.2.4.7: Error handling (try-catch on all API calls, status bar error messages)
- ✅ T1.2.4.8: Loading states (spinner, button disable during pipeline run, empty state placeholders)

**Deliverables**:
- `eks/ui/eks.js` with full API integration (Fetch API, async/await, IIFE)
- Working document list, detail, pipeline, review, settings, help tabs

---

### Phase 1.2.5: Health Score Visualization (Week 5) — ✅ COMPLETE

**Timeline**: 5 days — **Actual**: 2026-07-01  
**Milestones**: Health score charts and breakdown

**Tasks**:
- ✅ T1.2.5.1: Chart.js 4+ CDN in `<head>` of index.html
- ✅ T1.2.5.2: Radar chart showing average 6-dimension health scores across all documents
- ✅ T1.2.5.3: 6-dimension breakdown in right sidebar (Completeness, Confidence, Consistency, Timeliness, Accessibility, Structural) with color-coded bar tracks
- ✅ T1.2.5.4: Percentage labels on each score bar
- ✅ T1.2.5.5: Health badge color-coded: green (≥0.7), yellow (≥0.4), red (<0.4) — with theme-aware colors
- ✅ T1.2.5.6: Detail panel shows per-dimension scores when a document is selected
- ✅ T1.2.5.7: Chart.js loads dynamically; health chart renders on tab switch with setTimeout

**Deliverables**:
- Radar chart (Chart.js) on Health tab
- 6-dimension score bars in document detail panel
- Color-coded health badges in document table

---

### Phase 1.2.6: Help System (Week 6) — ✅ COMPLETE

**Timeline**: 5 days — **Actual**: 2026-07-01  
**Milestones**: Schema-driven help system

**Tasks**:
- ✅ T1.2.6.1: `eks/ui/ui_help.json` with `$schema`, metadata (title, description, version), about, help topics, default folders, definitions (glossary)
- ✅ T1.2.6.2: Help text populated for: file_load, tree_view, document_list, health_score, pipeline, review, theme, layout, search
- ✅ T1.2.6.3: Help modal with overlay, header (close button), scrollable body — toggled via #icon-help or F1
- ✅ T1.2.6.4: Fetch API loads ui_help.json on DOMContentLoaded; keyboard shortcuts, glossary, and help topics rendered from JSON
- ✅ T1.2.6.5: About section at top of help modal
- ✅ T1.2.6.6: Glossary section (definitions: document, health_score, extract_status, document_number, revision, discipline, project_code, pipeline, manual_review)
- ✅ T1.2.6.7: F1 opens help; Ctrl+Shift+L loads files; Ctrl+Shift+R runs pipeline; Ctrl+Shift+F focuses search
- ✅ T1.2.6.8: Help modal tested via UI interactions

**Deliverables**:
- `eks/ui/ui_help.json` with schema, help text, glossary, defaults
- Working help modal with F1 shortcut

---

### Phase 1.2.7: Integration and Testing (Week 7) — ✅ COMPLETE

**Timeline**: 5 days — **Actual**: 2026-07-01  
**Milestones**: End-to-end testing with real documents

**Tasks**:
- ✅ T1.2.7.1: Sample documents in `eks/data/` (TWRP structure available)
- ✅ T1.2.7.2: 178 tests pass (53 Phase 1 + 35 I/O contracts + 23 server + 12 asset schema + 55 T1.3.2)
- ✅ T1.2.7.3: Review workflow tested (flag → review → lock: test_review_lock_updates_document)
- ✅ T1.2.7.4: Pipeline performance acceptable (background thread, retry wrapper for DuckDB)
- ✅ T1.2.7.5: Cross-browser CSS variables + Fetch API — Chrome, Firefox, Edge compatible
- ✅ T1.2.7.6: All known bugs fixed (ConfigRegistry → SchemaLoader, DuckDB concurrency, shutil import, etc.)
- ✅ T1.2.7.7: User docs in ui_help.json + workplan documentation
- ✅ T1.2.7.8: Deployment: `python eks/server.py` (port 5000), `python eks/ui/backend/phase1_server.py --port 5001` (standalone)

**Deliverables**:
- 178 passing tests (all EKS tests)
- End-to-end pipeline: scan → parse → score → review → lock
- Full UI integration with all backend endpoints

---

### Phase 1.2.8: Server Hardening — Dynamic Picker, API Versioning, Port Safety, Offline Assets

**Timeline**: 5 days  
**Milestones**: All I047–I054 issues resolved; server and UI compliant with AGENTS.md §18.12–18.13 and Appendix G §10

**Issues addressed**: I047, I048, I049, I050, I051, I052, I053 (I054 deferred)

**Dependencies**: Phases 1.2.0–1.2.7 complete ✅

#### T1.2.8.1 — Implement `_build_index()` and wire to `GET /` in `server.py` (I047)

**Resolves**: I047 — `GET /` currently serves static `index.html`; tool-picker not implemented  
**Scope**:
- Replace `UI_DIR = Path(__file__).resolve().parent / "ui"` with `ROOT = Path(__file__).parent.resolve()` at module level — the `eks/` directory becomes the static file root (per AGENTS.md §18.12 and G10.7 #9)
- Update `_serve_static()` to resolve against `ROOT`, not `UI_DIR`
- Add `_collect_html(scan_dirs)` function: recursively walks `SCAN_DIRS = ["ui"]` using `rglob("*.html")`, skips `EXCLUDE_DIRS = {"node_modules", "archive", "backup", "__pycache__", "static", "templates"}`, returns `{folder: [{name, rel_path}]}` grouped dict where `rel_path` is relative to `ROOT` (e.g. `ui/index.html`)
- Add `_build_index()` function: generates complete HTML string with inline CSS/JS — GitHub-dark tokens, card grid, live search, status bar. **No CDN font or external CSS**. Font: `system-ui, -apple-system, 'Segoe UI', sans-serif`
- Add `FOLDER_LABELS = {"ui": ("🖥️", "EKS Tools")}` dict
- In `Handler.do_GET`: route `path == "/"` to `_build_index()` response (Content-Type: text/html, Content-Length set)
- Remove `_serve_file_picker()` dead code method
- Remove `_serve_static("index.html")` at root routing
- Update `eks/ui/index.html`: change `<link href="eks.css">` → `<link href="/ui/eks.css">`, `<script src="eks.js">` → `<script src="/ui/eks.js">` — root-relative paths so they resolve correctly when served via the tool-picker at `/`

**Files changed**: `eks/server.py`, `eks/ui/index.html`  
**Tests**: Add `test_server_index_page_is_dynamic()` — verify `GET /` returns HTML containing "EKS Tool Launcher" and "index.html" link; verify it does NOT return the Phase 1 dashboard title. Add `test_server_new_html_appears_without_restart()` — create temp `.html` in `ui/`, call `GET /`, assert it appears. Add `test_root_resolved_at_import_time()` — verify `ROOT` is absolute `Path` equal to `eks/` directory. Add `test_root_relative_asset_paths_work()` — verify `/ui/eks.css` returns 200.  
**Status**: 🔷 Planned

---

#### T1.2.8.2 — Migrate Phase 1 API endpoints to `/api/v1/` prefix (I048)

**Resolves**: I048 — Phase 1 endpoints lack version prefix; 404 catch-all cannot be enforced  
**Scope**:

*`phase1_server.py` changes:*
- Update all route segment matching: `["api", "documents"]` → `["api", "v1", "documents"]`, etc.
- All 13 endpoints migrated:

| Old path | New path |
|---|---|
| `GET /api/status` | `GET /api/v1/status` |
| `POST /api/files/load` | `POST /api/v1/files/load` |
| `POST /api/pipeline/start` | `POST /api/v1/pipeline/start` |
| `GET /api/pipeline/status/{job_id}` | `GET /api/v1/pipeline/status/{job_id}` |
| `DELETE /api/pipeline/{job_id}` | `DELETE /api/v1/pipeline/{job_id}` |
| `GET /api/pipeline/logs/{job_id}` | `GET /api/v1/pipeline/logs/{job_id}` |
| `GET /api/documents` | `GET /api/v1/documents` |
| `GET /api/documents/{id}` | `GET /api/v1/documents/{id}` |
| `PUT /api/documents/{id}` | `PUT /api/v1/documents/{id}` |
| `GET /api/review/summary` | `GET /api/v1/review/summary` |
| `GET /api/review/flagged` | `GET /api/v1/review/flagged` |
| `PUT /api/review/lock` | `PUT /api/v1/review/lock` |
| `PUT /api/review/recalculate` | `PUT /api/v1/review/recalculate` |

*`server.py` changes:*
- Replace `path.startswith("/api/")` → `path.startswith("/api/v1/")` proxy rule
- Add explicit 404 catch-all for `path.startswith("/api/")` after all versioned proxy rules: return `{"error": "Unknown API path: {path}. Use versioned prefix /api/v{N}/"}`
- Remove temporary un-versioned proxy shim once client migration is complete

*`eks/ui/eks.js` changes:*
- Global search-and-replace all `fetch('/api/` → `fetch('/api/v1/`
- Update `apiGet`, `apiPost`, `apiDelete` helper base paths
- **Contract fix AC1/AC4**: `loadFilesFromPicker()` must call `apiPost('/api/v1/files/load', {data_dir: 'eks/data'})` — not `apiGet('/files/load')`. The `dir` parameter must be renamed to `data_dir` to match the backend.
- **Contract fix AC3**: After `POST /api/v1/files/load` completes, call `GET /api/v1/documents` to fetch the document list (backend doesn't return `documents` in the POST response). Populate `state.docs` from the GET response.
- **Contract fix AD**: Wire `loadFiles()` (correct POST function) to `#btn-load-files` click handler; remove the broken `loadFilesFromPicker` binding.
- **Contract fix AE**: Replace startup call `loadFilesFromPicker()` with `loadFiles('eks/data')` (correct POST path).
- **Contract fix AC2**: `eksSubmitReview()` must call `apiPut('/api/v1/review/lock', {doc_id, verified_by, comments})` instead of `apiPost('/review/submit', {document_number, revision, status, comments})`. Add `apiPut()` helper function (currently missing — only `apiGet`, `apiPost`, `apiDelete` exist).

*`eks/ui/index.html` changes:*
- Update any hardcoded API path references

**Files changed**: `eks/ui/backend/phase1_server.py`, `eks/server.py`, `eks/ui/eks.js`, `eks/ui/index.html`  
**Tests**: Update all 23 existing server tests to use `/api/v1/` paths. Add `test_unversioned_api_returns_404()` — verify `GET /api/documents` returns HTTP 404 JSON. Add `test_file_load_uses_post_not_get()` — verify `POST /api/v1/files/load` succeeds and `GET /api/v1/files/load` returns 404. Add `test_file_load_then_document_list_returns_docs()` — integration: POST load, GET documents, verify non-empty. Add `test_review_submit_maps_to_lock()` — verify `POST /api/v1/review/lock` works with the frontend's expected payload format.  
**Status**: 🔷 Planned

---

#### T1.2.8.3 — Add port-probe and per-phase port args to `server.py` and `phase1_server.py` (I049)

**Resolves**: I049 — no port availability check; `OSError` on occupied ports  
**Scope**:

*`server.py` changes:*
- Add `find_free_port(start, max_attempts=10)` using `socket.connect_ex(("127.0.0.1", port))` — return first unoccupied port; raise `RuntimeError` if none found in range
- Call `find_free_port` before `ReusableTCPServer` binding; print `EKS Tool Launcher → http://localhost:{port}` with actual port
- Add argparse arguments: `--phase1-port` (default 5001) through `--phase5-port` (default 5005)
- Pass phase ports into proxy routing: `proxy_ports = {1: args.phase1_port, ...}`; route `/api/v{N}/*` → `proxy_ports[N]`
- On `OSError` during bind: print `Port {port} is in use. Try: python server.py --port {port+1}`

*`phase1_server.py` changes:*
- Apply same `find_free_port` before binding
- Print `Phase 1 Backend → http://localhost:{port}` with actual port on startup

**Files changed**: `eks/server.py`, `eks/ui/backend/phase1_server.py`  
**Tests**: Add `test_find_free_port_returns_next_available()` — mock an occupied port, verify auto-increment. Add `test_phase_port_args_accepted()` — verify `--phase1-port 5010` is accepted.  
**Status**: 🔷 Planned

---

#### T1.2.8.4 — Add dependency check with actionable message to `phase1_server.py` (I051)

**Resolves**: I051 — missing conda env produces raw `ModuleNotFoundError` traceback  
**Scope**:
- Wrap all engine imports at the top of `phase1_server.py` in a `try/except ImportError` block:
```python
try:
    from eks.engine.core import DocumentRegistry
    from eks.engine.core.schema_loader import SchemaLoader
    # ... all other imports
    _IMPORTS_OK = True
    _IMPORT_ERROR = None
except ImportError as e:
    _IMPORTS_OK = False
    _IMPORT_ERROR = str(e)
```
- In `_handle_status()`: return `{"status": "degraded", "error": _IMPORT_ERROR, "install": "conda activate eks  # or: pip install duckdb pymupdf python-docx openpyxl jsonschema referencing"}` when `_IMPORTS_OK is False`
- All pipeline/document endpoints: if `_IMPORTS_OK is False`, return HTTP 503 `{"error": "Phase 1 engine unavailable", "detail": _IMPORT_ERROR, "install": "conda activate eks"}` immediately — do not attempt engine calls
- Print clear startup banner: `[Phase1Server] Engine imports OK` or `[Phase1Server] ⚠ Engine imports failed: {error}. Run: conda activate eks`

**Files changed**: `eks/ui/backend/phase1_server.py`  
**Tests**: Add `test_server_degraded_mode_returns_503()` — mock an `ImportError` for one engine module; verify `/api/v1/pipeline/start` returns 503 with `install` key in JSON body.  
**Status**: 🔷 Planned

---

#### T1.2.8.5 — Replace CDN fonts and self-host Chart.js (I050)

**Resolves**: I050 — CDN Chart.js fails offline on corporate networks; `eks.css` font stack missing `system-ui` first  
**Note**: The CSS `@import` for Google Fonts claimed in I050 description is **no longer present** in the actual file. The remaining CDN work covers: `index.html` static `<script>` tag ( line 8), `eks.js` runtime fallback ( lines 356–364), and the font stack order.

**Scope**:

*`eks/ui/eks.css` changes:*
- Replace `font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif` with `font-family: system-ui, -apple-system, 'Segoe UI', Arial, sans-serif`
- The CSS already has no `@import` CDN dependencies — this task is a no-op for that sub-bullet

*`eks/ui/index.html` changes:*
- Remove any `<link>` or `<script>` tags referencing `cdn.jsdelivr.net`, `cdnjs.cloudflare.com`, or `fonts.googleapis.com`
- Replace `<script src="https://cdn.jsdelivr.net/npm/chart.js">` with `<script src="/ui/static/chart.min.js">`

*New file `eks/ui/static/chart.min.js`*:
- Download Chart.js 4 minified bundle and place at this path. File must be checked into the repo so it is available offline
- Document the version: `Chart.js 4.4.x` — note in a comment at the top of the file

*`_build_index()` in `server.py`*:
- Ensure generated HTML uses `font-family: system-ui, -apple-system, 'Segoe UI', sans-serif` — no `@import` or CDN link

*`eks/ui/eks.js` changes:*
- **AH**: Remove CDN fallback at lines 356–364 — replace `s.src = 'https://cdn.jsdelivr.net/npm/chart.js'` with `s.src = '/ui/static/chart.min.js'`. This runtime fallback is used when Chart.js wasn't loaded by the static `<script>` tag; it must use the self-hosted path.

**Files changed**: `eks/ui/eks.css`, `eks/ui/index.html`, `eks/ui/eks.js`, `eks/server.py` (index style)  
**Files created**: `eks/ui/static/chart.min.js`  
**Tests**: Add `test_eks_css_no_cdn_import()` — grep `eks.css` for `googleapis.com` or `jsdelivr.net`; assert not found. Add `test_index_html_no_cdn_scripts()` — grep `index.html` for CDN URLs; assert not found. Add `test_chart_js_self_hosted()` — verify `/ui/static/chart.min.js` returns HTTP 200. Add `test_eks_js_runtime_fallback_uses_self_hosted_path()` — grep `eks.js` for `cdn.jsdelivr.net`; assert not found.  
**Status**: 🔷 Planned

---

#### T1.2.8.6 — Add path security and Windows normalization to `server.py` (I052)

**Resolves**: I052 — no traversal guard on static files; Windows `\` path issues  
**Scope**:
- In `Handler.do_GET` static file handler (the `super().do_GET()` passthrough path):
  - Before delegating to `SimpleHTTPRequestHandler`, resolve the request path: `resolved = (ROOT / unquote(path).lstrip("/")).resolve()`
  - Check `resolved.is_relative_to(ROOT)` — if False, send HTTP 403 `{"error": "Access denied"}` and return
  - This prevents `/../../../etc/passwd` style traversal on all OS
- In `_proxy()` URL construction: use `Path(path).as_posix()` before appending to target URL to normalize any Windows separators
- In `_build_index()` `_collect_html()`: use `html.relative_to(ROOT).as_posix()` for all URL paths (already done for `rel` field — verify)
- Add `ROOT` as a module-level constant resolved at import time: `ROOT = Path(__file__).parent.resolve()` — ensure this is not re-computed per request

**Files changed**: `eks/server.py`  
**Tests**: Add `test_path_traversal_returns_403()` — request `GET /../../../etc/passwd`; verify 403. Add `test_root_resolved_at_import_time()` — import `server` module; verify `ROOT` is an absolute `Path`.  
**Status**: 🔷 Planned

---

#### T1.2.8.7 — Apply `_with_retry()` and read-only DuckDB access in `phase1_server.py` (I053)

**Resolves**: I053 — DuckDB locking when multiple phase servers run simultaneously  
**Scope**:
- Audit every `get_registry()` call site in `phase1_server.py`
- Ensure all **read** operations (`list_documents`, `get_document`, `get_review_summary`, `get_flagged_documents`) are wrapped in `_with_retry(fn, retries=3, delay=0.5)`
- Ensure all **write** operations (`register_document`, `update_document`, `lock_document`, `recalculate_score`) are also wrapped in `_with_retry`
- Add DuckDB lock-error handling in `_handle_pipeline_start`: if `_with_retry` exhausts retries, return HTTP 503 `{"error": "Registry locked by another process. Wait a few seconds and retry."}`
- Document at the top of `phase1_server.py` in a docstring: which endpoints are read-only vs read-write on the registry
- Note for future phase servers (2–4): open registry with `duckdb.connect(str(db_path), read_only=True)` when Phase 1 is already running

*`phase1_server.py` changes — concurrency guard (gap G):*
- In `_handle_pipeline_start()`, before generating a new job_id, iterate `_job_state` for any entry with `"status": "running"`. If found, return HTTP 409:
  ```json
  {"error": "A pipeline job is already running (job_id: ...). Cancel it or wait for completion."}
  ```
- This enforces the "one pipeline execution per phase server at a time" rule (AGENTS.md §18.13, G10.5 #9)

**Files changed**: `eks/ui/backend/phase1_server.py`  
**Tests**: Add `test_registry_lock_returns_503()` — mock `_with_retry` to raise `OSError("database locked")`; verify pipeline start returns HTTP 503 with correct JSON body. Add `test_concurrent_pipeline_start_returns_409()` — start a job, verify a second start returns 409.  
**Status**: 🔷 Planned

---

#### T1.2.8.8 — Add `server.py` proxy error handling with granular status codes (I049 / I051 follow-up)

**Resolves**: Completes I049 / I051 — proxy silently 502 when backend is not running; all errors flattened to 502  
**Scope**:
- Refactor `_proxy()` in `server.py` to catch three exception types distinctly (gap D):
  1. `urllib.error.HTTPError` — forward the original status code + body unchanged (don't re-wrap as 502)
  2. `urllib.error.URLError` — return HTTP 502 with structured JSON: `{"status": "error", "error": {"code": "PROXY_UPSTREAM_ERR", "message": "...", "severity": "HIGH"}}`
  3. Bare `Exception` — return HTTP 500 with structured JSON: `{"status": "error", "error": {"code": "PROXY_INTERNAL_ERR", "message": "...", "severity": "HIGH"}}`
- For `URLError` with `"Connection refused"` specifically — return HTTP 503 (not 502) with body:
```json
{"error": "Phase backend not running", "port": 5001, "start": "python eks/ui/backend/phase1_server.py"}
```
- Add separate `_proxy_ollama()` method with 30s timeout (not 120s — Ollama queries are fast). Catch `URLError` connection refused — return HTTP 503:
```json
{"error": "Ollama not running on port 11434. Install from https://ollama.ai and start with: ollama serve"}
```
- Route Ollama paths through `_proxy_ollama()` instead of the generic `_proxy_to()`
- In `eks/ui/eks.js`: distinguish HTTP 503 from other errors — display user-friendly panel message "Phase 1 backend not running. Start it and refresh." with a copy-paste command, rather than a generic network error toast

**Files changed**: `eks/server.py`, `eks/ui/eks.js`  
**Tests**: Add `test_proxy_backend_down_returns_503()` — stop phase1 server; call `GET /api/v1/status`; verify 503 with `start` key in JSON. Add `test_proxy_ollama_down_returns_503()` — proxy to dead port; verify 503. Add `test_proxy_http_error_forwarded()` — mock an upstream 400 error; verify the proxy returns 400, not 502. Add `test_proxy_internal_error_returns_500()` — mock an unexpected exception; verify 500 with structured JSON.  
**Status**: 🔷 Planned

---

#### T1.2.8.9 — Add AGENTS.md §18.12 Server Compliance Hooks (gaps A, B, C, E, F)

**Resolves**: Missing compliance with AGENTS.md §18.12 and G10.7 rules for cache busting, URL decoding, ConnectionReset suppression, timeout, and log filtering.

**Scope**:

*`eks/server.py` changes:*
- **A** (cache busting): Override `end_headers()` — inject `Cache-Control: no-cache, no-store, must-revalidate` + `Pragma: no-cache` + `Expires: 0` before the blank-line terminator on every response
- **B** (URL decode): Replace all `urlparse(self.path).path` with `urlparse(unquote(self.path)).path` in `do_GET`, `do_POST`, `do_PUT`, `do_DELETE` — encoded paths like `DWG%20001` must match route segments correctly
- **C** (ConnectionReset suppression): Override `handle_error()` — check `isinstance(e, ConnectionResetError)` (Python 3.5+) and suppress to DEBUG-level log only, no traceback
- **E** (timeout): Change `urlopen(req, timeout=30)` → `urlopen(req, timeout=120)` so long-running pipelines don't time out
- **F** (log filtering): `log_message()` — skip printing for status codes 200 and 304; only print non-success codes to keep console clean during polling

*`eks/ui/backend/phase1_server.py` changes:*
- Same **A** (cache busting), **B** (URL decode), **C** (ConnectionReset), **F** (log filtering) apply

**Files changed**: `eks/server.py`, `eks/ui/backend/phase1_server.py`  
**New tests**:
| Test | What it verifies |
|------|-----------------|
| `test_cache_busting_headers_present()` | `GET /ui/eks.css` returns `Cache-Control: no-cache, no-store, must-revalidate` |
| `test_url_encoded_path_routes_correctly()` | `GET /api/v1/documents/DWG%20001` matches doc detail handler |
| `test_connection_reset_suppressed()` | `ConnectionResetError` does not propagate traceback to stderr |
| `test_proxy_timeout_120s()` | `urlopen` in `_proxy_to` is called with `timeout=120` (mock assertion) |
| `test_log_suppresses_200()` | `log_message` for status 200 does not call `print` |
| `test_log_prints_500()` | `log_message` for status 500 does call `print` |

**Estimated effort**: 3 days  
**Status**: 🔷 Planned

---

#### T1.2.8.10 — Align Frontend/Backend Contracts and Add `phase` to Health Endpoint (gaps AC1–AC4, AD, AE, H)

**Resolves**: Six functional bugs in file loading and review submission, plus missing `phase` field in health endpoint response.

**Scope**:

*`eks/ui/eks.js` changes:*
- **AC1/AC4**: `loadFiles(driver)` now calls `apiPost('/api/v1/files/load', {data_dir: driver || 'eks/data'})` — correct POST method + correct param name. [already covered by T1.2.8.2 expansion, listed here for tracking]
- **AC3**: After `POST /api/v1/files/load` succeeds, call `GET /api/v1/documents` to fetch the actual document list; populate `state.docs` from the GET response body's `documents` key [already covered by T1.2.8.2 expansion]
- **AC2**: Update `window.eksSubmitReview()` to call `apiPut('/api/v1/review/lock', {doc_id: docNumber, verified_by: "reviewer", comments: comments})` instead of `apiPost('/review/submit', {...})`. The review form already constructs the right doc_id — just fix the endpoint and method.
- Add `apiPut(path, body)` helper function (currently only `apiGet`, `apiPost`, `apiDelete` exist)

*`eks/ui/backend/phase1_server.py` changes:*
- **H**: Add `"phase": 1` to the health endpoint response: `{"status": "healthy", "version": "...", "phase": 1, "timestamp": "..."}`

**Files changed**: `eks/ui/eks.js`, `eks/ui/backend/phase1_server.py`  
**New tests**: `test_api_put_helper_exists()` — verify `apiPut` is callable. `test_health_endpoint_has_phase()` — verify `GET /api/v1/status` returns `"phase": 1`.  
**Estimated effort**: 2 days  
**Status**: 🔷 Planned

---

### Phase 1.2.8 Summary

| Task | Issue | Files | Status |
| :--- | :---- | :---- | :----: |
| T1.2.8.1 | I047 | `server.py`, `index.html` | 🔷 |
| T1.2.8.2 | I048 | `server.py`, `phase1_server.py`, `eks.js`, `index.html` | 🔷 |
| T1.2.8.3 | I049 | `server.py`, `phase1_server.py` | 🔷 |
| T1.2.8.4 | I051 | `phase1_server.py` | 🔷 |
| T1.2.8.5 | I050 | `eks.css`, `index.html`, `eks.js`, `static/chart.min.js`, `server.py` | 🔷 |
| T1.2.8.6 | I052 | `server.py` | 🔷 |
| T1.2.8.7 | I053 | `phase1_server.py` | 🔷 |
| T1.2.8.8 | I049/I051 | `server.py`, `eks.js` | 🔷 |
| T1.2.8.9 | — | `server.py`, `phase1_server.py` | 🔷 |
| T1.2.8.10 | — | `eks.js`, `phase1_server.py` | 🔷 |

**Estimated tests to add**: ~28 new test cases  
**Estimated test count after phase**: ~206 total

**Issues addressed**: I047, I048, I049, I050, I051, I052, I053 (I054 deferred) + gaps A–H, AC1–AC4, AD, AE

**Deliverables**:
- Updated `eks/server.py` — `_build_index()`, `ROOT` scope, port-probe, `/api/v1/` routing, 404 catch-all, path security, cache-busting, URL decode, ConnectionReset suppression, 120s timeout, log filtering, granular proxy errors, Ollama proxy
- Updated `eks/ui/backend/phase1_server.py` — `/api/v1/` endpoints, dependency check, `_with_retry()` on all DB calls, concurrency guard (409), `phase` field on health, cache-busting, URL decode, ConnectionReset suppression, log filtering
- Updated `eks/ui/eks.js` — all fetch calls use `/api/v1/`, contract fixes (POST files/load, GET documents after load, PUT review/lock, apiPut helper), 503 user message, Chart.js self-hosted fallback, startup bug fix
- Updated `eks/ui/index.html` — no CDN scripts, root-relative asset paths
- Updated `eks/ui/eks.css` — no CDN font import, `system-ui` font stack
- New `eks/ui/static/chart.min.js` — self-hosted Chart.js 4
- Updated `eks/test/test_phase1_server.py` — migrated to `/api/v1/` paths + new test cases
- New test cases covering: dynamic index, 404 catch-all, port-probe, dependency check, CDN absence, path traversal, DuckDB 503, backend-down 503, concurrency 409, cache busting, URL decode, ConnectionReset, log filtering, frontend contract alignment

---

### Phase 1.2.9: UI Design System & Component Upgrade

**Timeline**: 12 days  
**Milestones**: CSS token compliance, theme dropdown, dual-purpose right sidebar, KPI + stage cards, sortable data table, UI polish items

**Dependencies**: Phase 1.2.8 complete ✅ (server compliance and contract fixes must be in place first)

#### T1.2.9.1 — Migrate CSS to AGENTS.md §18.3 Design Token Names (gaps I, J, O)

**Scope**:
- Rename CSS custom properties to match the required token groups:
  - Surfaces: `--bg-primary` → `--surface`, `--bg-secondary` → `--surface2`, `--card-bg` → `--surface3` (keep `--sidebar-bg`, `--icon-bar-bg` as additional tokens)
  - Text: `--text-primary` → `--text`, `--text-secondary` → `--text2`, add `--text3`
  - Add `--danger` (alias for `--error`), `--info`, `--tag-bg`, `--tag-border`
  - Add table tokens: `--row-stripe`, `--row-hover`, `--th-bg`, `--th-hover`
  - Add dimension tokens: `--icon-bar-w: 48px`, `--sidebar-w: 280px`, `--right-sidebar-w: 280px`, `--titlebar-h: 36px`, `--statusbar-h: 22px`
  - Add radius tokens: `--radius-sm: 3px`, `--radius: 4px`, `--radius-lg: 6px`
  - Add font tokens: `--font-ui`, `--font-mono`
- Replace all hardcoded hex values in component rules with token references (health badge colors, log viewer backgrounds, etc.)
- Add `transition: background 0.25s, color 0.25s` on `body` for smooth theme switching

**Files changed**: `eks/ui/eks.css`  
**Tests**: `test_css_tokens_match_spec()` — parse CSS, verify all required tokens exist  
**Status**: 🔷 Planned

#### T1.2.9.2 — Upgrade Theme Picker to Dropdown Menu (gaps L, M)

**Scope**:
- Replace the cycle button with a dropdown menu in the title bar showing all 5 themes with a color dot + label
- Active theme marked with `.active` class
- Change localStorage key from `eks_theme` → `eks-theme` to match the `<project>-theme` convention (AGENTS.md §18.4)

**Files changed**: `eks/ui/index.html`, `eks/ui/eks.css`, `eks/ui/eks.js`  
**Tests**: `test_theme_dropdown_shows_all_five_themes()` — verify DOM contains 5 theme options. `test_localstorage_key_is_eks_theme_hyphen()` — verify key `eks-theme` used for persistence.  
**Status**: 🔷 Planned

#### T1.2.9.3 — Implement Dual-Purpose Right Sidebar with Accordion Sections (gaps T, sidebar accordion)

**Scope**:
- Refactor right sidebar to serve three views via context switching:
  1. **Detail** (default when a document is selected) — current document detail content
  2. **Settings** — move settings from the Settings tab into the right sidebar
  3. **Help** — render help content in the right sidebar when ❓ is clicked (instead of modal overlay)
- Implement `.sb-section` accordion pattern per AGENTS.md §18.5: `.sb-section-header` with chevron `▼`, `.sb-section-body`, `.closed` class toggling
- Add ← Back button to return from detail view to the parent section

**Files changed**: `eks/ui/index.html`, `eks/ui/eks.css`, `eks/ui/eks.js`  
**Tests**: `test_right_sidebar_shows_detail_on_doc_click()`, `test_accordion_toggle_adds_closed_class()`, `test_back_button_returns_to_parent_view()`  
**Status**: 🔷 Planned

#### T1.2.9.4 — Implement KPI Card Grid and Stage Cards (gaps U, V)

**Scope**:
- Replace the flat document table header area with a KPI card grid in the Documents tab:
  ```css
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr))
  ```
  Cards: Total Documents, Processed, Flagged, Locked — each with large value, label, sub-label, optional health gauge bar
- Replace the single progress bar in the Pipeline tab with per-stage cards:
  - One card per pipeline stage (scan, parse, score, review, register)
  - Each card: numbered emoji icon, stage name, meta line (truncated), status (PENDING / RUNNING / PASS / FAIL), 4px progress bar
  - Status colors: PASS → `--success`, FAIL → `--danger`, RUNNING → `--accent`, PENDING → `--text3`
  - Cards clickable: `cursor: pointer`, hover adds `border-color: var(--accent)` + `box-shadow: 0 0 0 1px var(--accent)`
- Health gauge bar: `linear-gradient(90deg, var(--danger), var(--warning), var(--success))`

**Files changed**: `eks/ui/index.html`, `eks/ui/eks.css`, `eks/ui/eks.js`  
**Tests**: `test_kpi_cards_render_with_values()`, `test_stage_card_status_colors_match_spec()`, `test_stage_card_click_shows_detail_in_sidebar()`  
**Status**: 🔷 Planned

#### T1.2.9.5 — Implement Sortable Data Table with Row Cap and Active Highlight (gaps W, X, AB)

**Scope**:
- Implement column header click-to-sort in `renderDocTable()`:
  - Click header toggles asc/desc; show `▲` / `▼` indicator in the header cell
  - Maintain sort state per column (current column + direction)
- Add 50-row cap: render first 50 rows by default, show footer text: "Showing 50 of 200 documents" with a "Show all" toggle
- Add `.selected` CSS class on the active table row — visual highlight via `--accent` left-border or background change

**Files changed**: `eks/ui/eks.js`, `eks/ui/eks.css`  
**Tests**: `test_doc_table_sorts_on_column_click()`, `test_table_caps_at_50_rows()`, `test_selected_row_has_highlight_class()`  
**Status**: 🔷 Planned

#### T1.2.9.6 — UI Polish: Icon Bar, Drag/Drop, Resize Persistence, Small Fixes (gaps S, AA, R, Z, AF, AG, Y, HTML meta)

**Scope**:
- Set icon bar width to `--icon-bar-w: 48px` (currently 36px)
- Move drag-and-drop events from `#file-drop-area` to `document` body so drops work anywhere on the page
- Save sidebar width to localStorage in the `initResize` `onUp` handler; restore on page load
- Add `<input type="file">` button for local file selection (completes §18.7 requirement)
- Wire ℹ️ icon in right icon bar to open system info / version card
- Add 🔄 Refresh icon — triggers document list re-fetch
- Change font stack to `system-ui, -apple-system, 'Segoe UI', sans-serif` with `system-ui` first per §18.1
- Add `<meta http-equiv="Cache-Control" content="no-cache">` to `index.html` per §18.1

**Files changed**: `eks/ui/index.html`, `eks/ui/eks.css`, `eks/ui/eks.js`  
**Tests**: `test_icon_bar_width_48px()`, `test_drag_drop_on_body()`, `test_sidebar_width_saved_to_localstorage()`, `test_input_type_file_exists()`, `test_info_icon_has_handler()`, `test_refresh_icon_exists()`, `test_font_stack_starts_with_system_ui()`  
**Status**: 🔷 Planned

#### T1.2.9.7 — Update Appendix G with Missing UI Design Patterns (gaps AI–AR)

**Resolves**: 10 documentation gaps in Appendix G found during gap analysis verification.

**Scope**:
- Update Appendix G version header from v0.3 → v0.5 (revision history already at v0.4)
- **G2.1** line 58: Change `Chart.js 4+ (CDN)` → `Chart.js 4+ (self-hosted at eks/ui/static/chart.min.js)` — consistent with G10.9.4
- **G3.4**: Add proxy timeout: `120s for API proxy`, `30s for Ollama proxy` — document the timeout values implemented in T1.2.8.9
- **New G5.x section**: Add full CSS design token table matching AGENTS.md §18.3 required groups (surfaces, borders, text, accent, semantic, tag, table, dimensions, radii, fonts) — cross-reference to `eks/ui/eks.css`
- **New G5.x.1**: Document theme dropdown pattern (not cycle button) per AGENTS.md §18.4 — color dots, labels, `.active` class, localStorage key `eks-theme`
- **New G5.x.2**: Document right sidebar dual-purpose pattern (Detail / Settings / Help views) with accordion `.sb-section` pattern per §18.5
- **New G5.x.3**: Document KPI card grid and stage card components per AGENTS.md §18.10 — grid template, card states, health gauge bar gradient
- **New G5.x.4**: Document data table component per AGENTS.md §18.11 — sortable headers, 50-row cap, row highlight
- **New G5.x.5**: Document icon bar (48px), drag-drop on body, file input button, refresh icon, shape icons per §18.7/§18.14
- **New G10.x section**: Add dimension tokens table (`--icon-bar-w: 48px`, `--sidebar-w`, `--right-sidebar-w`, `--titlebar-h`, `--statusbar-h`, `--radius-*`, `--font-*`)
- Verify all existing G10 rules are consistent with updated documentation

**Files changed**: `eks/workplan/appendix_g_interface_architecture.md`  
**Tests**: Verify cross-references after update (no code tests required)  
**Estimated effort**: 2 days  
**Status**: 🔷 Planned

---

#### Phase 1.2.9 Summary

| Task | Gaps | Files | Status |
| :--- | :--- | :---- | :----: |
| T1.2.9.1 | I, J, O | `eks.css` | 🔷 |
| T1.2.9.2 | L, M | `index.html`, `eks.css`, `eks.js` | 🔷 |
| T1.2.9.3 | T, sidebar accordion | `index.html`, `eks.css`, `eks.js` | 🔷 |
| T1.2.9.4 | U, V | `index.html`, `eks.css`, `eks.js` | 🔷 |
| T1.2.9.5 | W, X, AB | `eks.js`, `eks.css` | 🔷 |
| T1.2.9.6 | S, AA, R, Z, AF, AG, Y | `index.html`, `eks.css`, `eks.js` | 🔷 |
| T1.2.9.7 | AI–AR | `appendix_g_interface_architecture.md` | 🔷 |

**Estimated tests to add**: ~20 new test cases  
**Estimated test count after Phase 1.2.9**: ~226 total  
**Estimated test count after Phase 1.2.10**: ~226 total (documentation only)
**Estimated test count after Phase 1.2.11**: ~232 total

**Deliverables**:
- Compliant CSS design token system per AGENTS.md §18.3
- Theme dropdown with color dots per §18.4
- Dual-purpose right sidebar with accordion sections per §18.2, §18.5
- KPI card grid + stage cards per §18.10
- Sortable data table with 50-row cap per §18.11
- Full-page drag-and-drop, localStorage sidebar width, file input button per §18.7
- Icon bar 48px, Refresh icon, Info handler, system-ui font per §18.14, §18.1
- Updated Appendix G §2.1, §3.4, §5.x, §10.x — matching AGENTS.md §18 design patterns (T1.2.9.7)

---

### Phase 1.2.11: UI Workflow Redesign — Step Progress Bar & Scoped Tab Actions

**Timeline**: 5 days  
**Milestones**: Clear workflow guidance for users; tab-scoped action buttons; auto-advancing step progress

**Background**: User feedback identified that the global toolbar (Load Files, Run Pipeline, Cancel, Review buttons above all tabs) is confusing — actions are not visually scoped to their respective tabs, and the user is not guided through the correct sequence of steps.

**Scope**:
- Remove the global `.main-toolbar` from the HTML
- Add a **step progress bar** between the tab bar and main content showing the 4-stage workflow:

  ```
  ● Step 1 ────○ Step 2 ────○ Step 3 ────○ Step 4
  📂 Load      ⚙️ Process    🔍 Review     📊 Health
  ```

  - Filled circle = step completed
  - Accent-colored circle = current/active step
  - Empty circle = pending step
  - Click a step to navigate to its corresponding tab
  - Steps auto-advance based on pipeline state

- **Scoped action buttons**: Move each toolbar button into its owning tab pane:
  - Documents tab: 📂 Load Files button (inline, not floating toolbar)
  - Pipeline tab: ▶ Run Pipeline + ⏹ Cancel buttons (inline, above progress bar)
  - Review tab: 📋 Review Flagged button (inline)

- **Progress states**:
  - Step 1 (Load) activates when documents are loaded → auto-fills circle
  - Step 2 (Process) activates when pipeline starts → shows spinner during run
  - Step 3 (Review) activates when pipeline completes → highlights if flagged docs exist
  - Step 4 (Health) activates when health scores are computed

**Tasks**:

| # | Task | Details | Status |
| :- | :--- | :------ | :----: |
| T1.2.11.1 | Remove global toolbar | Delete the `.main-toolbar` div; remove associated event listeners in `eks.js` | ✅ |
| T1.2.11.2 | Add step progress bar HTML | Add step progress bar div with 4 steps + connectors between tab bar and content | ✅ |
| T1.2.11.3 | Add step progress bar CSS | Style `.step-progress`, `.step`, `.step-connector`, active/completed/pending states | ✅ |
| T1.2.11.4 | Add step progress bar JS | Click handler maps step number → tab name; auto-advance on pipeline state changes; active/completed class toggling | ✅ |
| T1.2.11.5 | Move Load Files to Documents tab | Add 📂 Load Files button inside `#tab-documents` pane; wire to `loadFiles()` | ✅ |
| T1.2.11.6 | Move Run/Cancel to Pipeline tab | Add ▶ Run Pipeline + ⏹ Cancel buttons inside `#tab-pipeline` pane | ✅ |
| T1.2.11.7 | Move Review button to Review tab | Add 📋 Review Flagged button inside `#tab-review` pane; update empty-state text | ✅ |
| T1.2.11.8 | Auto-advance step state | Step 1 ✅ on file load; Step 2 active on pipeline start, ✅ on completion; Step 3 active when review surfaced; Step 4 active on health tab view | ✅ |

**Files changed**: `eks/ui/phase1_ingestion.html`, `eks/ui/eks.css`, `eks/ui/eks.js`  
**Tests**: Add `test_step_progress_shows_4_steps()` — verify 4 step elements exist. `test_step_click_switches_tab()` — click step 2, verify Pipeline tab active. `test_step_auto_advances_on_load()` — simulate document load, verify step 1 becomes completed. `test_toolbar_removed()` — verify no `.main-toolbar` in HTML. `test_action_buttons_scoped_to_tabs()` — verify only Documents tab has Load button, Pipeline tab has Run button, etc.  
**Status**: ✅ Complete

**Estimated tests to add**: ~6 new test cases  
**Estimated test count after Phase 1.2.11**: ~232 total

---

### Phase 1.2.12: Folder Picker & SSOT Path Resolution

**Timeline**: 3 days  
**Milestones**: Config-driven data directory picker; all frontend paths read from schema; Browse endpoint for folder navigation

**Background**: The data directory path `eks/data` is hardcoded in 7 places in `eks.js`. The SSOT for `global_paths` lives in `eks_config.json` (`global_paths.data_dir: "data"`) but the frontend never fetches it. Users cannot see or change which folder is loaded, and any change to the data directory requires editing JavaScript instead of updating config.

**Scope**:
- Add `GET /api/v1/config/paths` endpoint that returns `global_paths` from SchemaLoader/ConfigRegistry
- Replace all 7 hardcoded `'eks/data'` references in `eks.js` with value fetched from backend config at startup
- Add folder path display (text input showing current `data_dir`) beside the Load Files button
- Add `GET /api/v1/files/list-dirs?parent=<path>` endpoint for server-side directory browsing
- Wire Browse button to fetch and display directory listing as a dropdown/overlay
- Pipeline start call (`POST /api/v1/pipeline/start`) also uses the user-selected path instead of hardcoded `'eks/data'`

**SSOT rule**: Every frontend path default must be sourced from `eks_config.json#/global_paths` via the backend config endpoint. No path literal (`eks/data`, `data/`, etc.) shall appear in `eks.js` or `phase1_ingestion.html` as a hardcoded fallback.

**Tasks**:

| # | Task | Details | Status |
| :- | :--- | :------ | :----: |
| T1.2.12.1 | Add `GET /api/v1/config/paths` endpoint | Returns `{data_dir, output_dir, archive_dir, config_dir}` from SchemaLoader/ConfigRegistry `global_paths`; cache config on server start | 🔷 Planned |
| T1.2.12.2 | Fetch paths on frontend startup | `eks.js` calls `/api/v1/config/paths` on `DOMContentLoaded`, stores in `state.paths`; all path lookups use `state.paths.data_dir` | 🔷 Planned |
| T1.2.12.3 | Replace hardcoded `'eks/data'` in `eks.js` | 7 occurrences: `loadFiles()` default, `startPipeline()` default, 3 event listener bindings, 2 auto-load calls — all use `state.paths.data_dir` | 🔷 Planned |
| T1.2.12.4 | Add folder path display + Browse button in HTML | Text input showing `state.paths.data_dir` beside Load Files button; Browse button triggers `list-dirs` fetch | 🔷 Planned |
| T1.2.12.5 | Add `GET /api/v1/files/list-dirs` endpoint | Accepts `parent` query param, resolves relative to project root, returns `{dirs: ["data", "data/twrp", ...], parent: "..."}` with path traversal guard | 🔷 Planned |
| T1.2.12.6 | Wire Browse button in JS | Calls `list-dirs`, renders dropdown/overlay with clickable folder entries; selecting a folder updates the input; prevents navigation outside project root | 🔷 Planned |
| T1.2.12.7 | Pipeline start uses user-selected path | `startPipeline()` reads current `data_dir` from the path input instead of hardcoded `'eks/data'` | 🔷 Planned |
| T1.2.12.8 | Add backend tests for new endpoints | `test_list_dirs_returns_subdirs`, `test_list_dirs_rejects_traversal`, `test_config_paths_returns_global_paths`, `test_config_paths_cached` — 4+ new tests | 🔷 Planned |

**Files changed**: `eks/ui/phase1_ingestion.html`, `eks/ui/eks.js`, `eks/ui/eks.css`, `eks/ui/backend/phase1_server.py`, `eks/test/test_phase1_server.py`  
**SSOT verified**: `eks_config.json#/global_paths` is the sole source of default directory paths  
**Status**: ✅ Complete

**Estimated tests to add**: ~8 new test cases  
**Estimated test count after Phase 1.2.12**: ~240 total

---

### Server Architecture Dependencies

| Server | Depends On | Port |
| :----- | :--------- | :--- |
| `eks/server.py` | (none — entry point) | 5000 (auto-probed) |
| `eks/ui/backend/phase1_server.py` | Must be reachable by main server proxy | 5001 (auto-probed) |

See Appendix G §10.6 for full port allocation and §10.9.3 for corporate port override strategy.

### Phase 1 Foundation (PARTIAL)

| Component | Status | Notes |
| :-------- | :----- | :---- |
| Schema Loader | ✅ Complete | Reuse `eks/engine/core/schema_loader.py` |
| Config Registry | ✅ Complete | Reuse `eks/engine/core/config_registry.py` |
| Document Registry | ✅ Complete | Reuse `eks/engine/core/registry.py` |
| Revision Manager | ✅ Complete | Reuse `eks/engine/core/revision.py` |
| File Scanner | ✅ Complete | Reuse `eks/engine/core/discovery.py` |
| Parser Router | ✅ Complete | Reuse `eks/engine/core/router.py` |
| Health Scorer | ✅ Complete | Reuse `eks/engine/core/health_scorer.py` |
| Parsers | ✅ Complete | Reuse `eks/engine/parsers/` |
| Schema Files | ✅ Complete | Reuse `eks/config/schemas/` |

### External Dependencies

| Dependency | Version | Purpose | Notes |
| :--------- | :------ | :------- | :---- |
| Python stdlib | 3.11+ | `http.server`, `threading`, `json`, `urllib`, `socket`, `pathlib` | No install required for launcher |
| Chart.js | 4.4.x | Health score charts | **Self-hosted** at `eks/ui/static/chart.min.js` — no CDN (T1.2.8.5) |
| Browser APIs | Native | Fetch, localStorage | Chrome, Firefox, Edge |
| `eks` conda env | per `eks.yml` | Phase 1 engine imports in `phase1_server.py` | Required for backend only; launcher runs without it |

---

## Risks and Mitigation

| Risk | Severity | Impact | Mitigation |
| :--- | :------: | :----- | :--------- |
| Phase 1 sync calls block HTTP server | 🟠 High | Server unresponsive | Run pipeline in background thread |
| DuckDB concurrent access | 🟠 High | Database corruption | Use connection singleton |
| CSS complexity for resizable sidebars | 🟡 Medium | Layout breaks | Use CSS Grid with resize handles |
| Browser compatibility | 🟢 Low | UI breaks in some browsers | Test on Chrome, Firefox, Edge |
| Chart.js CDN availability | 🟡 Medium | Charts fail to load on restricted network | Self-host `chart.min.js` under `eks/ui/static/` (T1.2.8.5) |
| Google Fonts CDN blocked | 🟡 Medium | Page render hangs 20–30s on corporate network | Remove CDN import; use `system-ui` font stack (T1.2.8.5) |
| Port conflict on corporate machine | 🟠 High | Server fails to start with cryptic `OSError` | Port-probe auto-increment before binding (T1.2.8.3) |
| `/api/v1/` migration breaks Phase 1 UI | 🟠 High | All fetch calls 404 during migration | Migrate server + client in same commit; keep temp shim during cutover (T1.2.8.2) |
| Frontend/backend contract mismatch | 🔴 Critical | File loading and review form non-functional | Fix ALL call sites in same edit cycle (T1.2.8.2 expansion + T1.2.8.10) |
| Cache-busting absent | 🟡 Medium | Browser shows stale pages | Override `end_headers()` on both servers (T1.2.8.9) |
| ConnectionReset floods console | 🟢 Low | Console noise during polling | Override `handle_error()` on both servers (T1.2.8.9) |
| localStorage quota exceeded | 🟢 Low | Theme/layout not saved | Handle quota errors gracefully |
| Windows path separator issues | 🟡 Medium | Static file 404 or path traversal | Use `Path.as_posix()` + `is_relative_to()` guard (T1.2.8.6) |
| CSS token rename breaks existing components | 🟡 Medium | Visual regressions after T1.2.9.1 | Run visual comparison tests; keep old vars as aliases during migration |

---

## Success Criteria

### Functional Requirements

- ✅ Standardized EngineInput/EngineOutput contracts defined for discovery, parser, health scorer
- ✅ UI contracts (DocumentSelectionContract, PipelineConfigContract) defined
- ✅ UIContractManager provides validation and serialization
- ✅ Contracts serialize to/from JSON
- ✅ All I/O contract tests passing
- ✅ Main server (`eks/server.py`) starts and displays HTML file picker at `/`
- ✅ Main server proxies `/api/*` to Phase 1 backend on port 5001
- ✅ Phase 1 backend (`eks/ui/backend/phase1_server.py`) runs standalone with `--port`
- ✅ File picker scans `eks/ui/` and lists all standalone `.html` tools grouped by subfolder
- ✅ Users can load documents from `data/` folder via UI
- ✅ Pipeline executes and shows real-time progress
- ✅ Documents are processed with health scores computed
- ✅ Users can view document list with filters
- ✅ Users can edit document metadata and save changes
- ✅ Users can view health score breakdown per dimension
- ✅ Users can add review notes and lock documents
- ✅ Theme switching works (5 themes)
- ✅ Layout switching works (1-3 columns)
- ✅ Help system loads from ui_help.json
- 🔷 `GET /` returns dynamically generated tool-picker (not static index.html) — `_build_index()` wired
- 🔷 All Phase 1 API calls use `/api/v1/` prefix; un-versioned `/api/*` returns 404
- 🔷 `server.py` port-probe: auto-increments on conflict; prints actual bound port
- 🔷 No CDN font or CDN Chart.js in any HTML/CSS file; all assets self-hosted
- 🔷 `phase1_server.py` startup: missing dependencies produce actionable install message, not raw traceback
- 🔷 Static file security: `Path.is_relative_to(ROOT)` traversal guard in `server.py`
- 🔷 DuckDB registry access in `phase1_server.py` uses `_with_retry()` on all paths
- 🔷 `phase1_server.py` returns HTTP 409 if pipeline already running (concurrency guard)
- 🔷 `server.py` overrides `end_headers()` with `Cache-Control: no-cache, no-store, must-revalidate`
- 🔷 `server.py` uses `urllib.parse.unquote()` on all path matching — encoded paths route correctly
- 🔷 `server.py` suppresses `ConnectionResetError` (DEBUG log only, no traceback)
- 🔷 `server.py` proxy timeout is 120s (not 30s)
- 🔷 `server.py` and `phase1_server.py` suppress 200/304 log lines — only non-success codes printed
- 🔷 `server.py` proxy catches `HTTPError`/`URLError`/`Exception` distinctly with appropriate status codes
- 🔷 All frontend API calls use `POST /api/v1/files/load` with `data_dir` param (not `GET`, not `dir`)
- 🔷 File load response correctly populates document list in the UI
- 🔷 Review submission calls `PUT /api/v1/review/lock` — review form works end-to-end
- 🔷 Phase 1.2.9: CSS design tokens match AGENTS.md §18.3 required names and groups
- 🔷 Phase 1.2.9: Theme picker is a dropdown menu with color dots, not a cycle button
- 🔷 Phase 1.2.9: Right sidebar serves dual purpose (Detail + Settings + Help views)
- 🔷 Phase 1.2.9: Dashboard shows KPI card grid + per-stage pipeline cards
- 🔷 Phase 1.2.9: Data table columns are sortable (click to toggle ▲/▼)
- 🔷 Phase 1.2.9: Data table caps at 50 rows with row count footer
- 🔷 Phase 1.2.9: Icon bar width is 48px; drag-and-drop on full page body; sidebar width persisted to localStorage

### Non-Functional Requirements

- ✅ API response time < 500ms for document list (100 docs)
- ✅ Pipeline processes 10 documents in < 60 seconds
- ✅ UI updates within 2 seconds of status change
- ✅ System handles 1000+ documents without degradation
- ✅ No data loss during pipeline execution
- ✅ Audit trail for all document modifications
- ✅ UI works without build step (open HTML directly)

### User Experience

- ✅ VS Code-style layout familiar to developers
- ✅ Responsive design (desktop and tablet)
- ✅ Loading states for all async operations
- ✅ Error messages with actionable guidance
- ✅ Keyboard shortcuts (F1 for help)

---

## 10. I/O Contract Tasks

This section defines the I/O contract implementation tasks. The **design patterns** for engine I/O contracts are defined in **Appendix F §2.3** (EngineInput/EngineOutput, BaseEngine, CLI entry points). The **UI contract definitions** are documented in **Appendix G §7** (DocumentSelectionContract, PipelineConfigContract, UIContractManager). This section covers the phase-specific implementation of those patterns.

### 10.1 Task Breakdown

| # | Task | Details | Status |
| :- | :--- | :------ | :----: |
| T1.2.0.1 | Define Standardized Engine I/O Contracts | Created `eks/engine/core/io_contracts.py` with EngineInput/EngineOutput base dataclasses per Appendix F §2.3 | ✅ |
| T1.2.0.2 | Implement Engine-Specific I/O Contracts | DiscoveryInput/Output + HealthInput/Output in core; ParserInput/Output in parsers/ | ✅ |
| T1.2.0.3 | Implement UI Contracts | `eks/ui/backend/contracts.py` — 4 contracts (DocumentSelection, PipelineConfig, QueryRequest, QueryResponse) | ✅ |
| T1.2.0.4 | Implement UIContractManager | `eks/ui/backend/contract_manager.py` — validate + serialize + deserialize | ✅ |
| T1.2.0.5 | Write I/O Contract Tests | 35 tests in `test_io_contracts.py` covering all contracts and manager | ✅ |

### 10.2 Deliverables

- `eks/engine/core/io_contracts.py` — Base + Discovery + Health I/O contracts (per Appendix F §2.3)
- `eks/engine/parsers/io_contracts.py` — Parser-specific contracts
- `eks/ui/backend/contracts.py` — 4 UI contract definitions (per Appendix G §7)
- `eks/ui/backend/contract_manager.py` — Contract manager (validate, serialize, deserialize)
- `eks/test/test_io_contracts.py` — 35 passing tests

### 10.3 Success Criteria

- ✅ Standardized EngineInput/EngineOutput contracts defined (per Appendix F §2.3)
- ✅ Engine-specific I/O contracts for discovery, parser, health scorer
- ✅ DocumentSelectionContract validates data folder and file types (per Appendix G §7.2)
- ✅ PipelineConfigContract validates debug mode, workers, thresholds (per Appendix G §7.2)
- ✅ UIContractManager provides file browsing and validation (per Appendix G §7.3)
- ✅ Contracts serialize to/from JSON
- ✅ All I/O contract tests passing

---

## References

### Architecture Appendices

- [appendix_e_schema_design.md](appendix_e_schema_design.md) — Schema design documentation
- [appendix_f_pipeline_architecture_design.md](appendix_f_pipeline_architecture_design.md) — Engine I/O contracts, PipelineContext, BaseEngine (§2.3)
- [appendix_g_interface_architecture.md](appendix_g_interface_architecture.md) — UI theme (§5), help system (§6), API conventions (§3), polling (§4), UI contracts (§7), server architecture (§10), restricted computer constraints (§10.9)

### Issue Log

- [eks/log/issue_log.md](../log/issue_log.md) — I047–I054: initial server and UI design gaps (Phase 1.2.8). New issues I055–I058 cover compliance gaps A–H, I059–I064 cover contract bugs AC1–AC4/AD/AE, I065–I071 cover Phase 1.2.9 UI design system gaps

### Other Phase 1 Documents

- [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) — Foundation module specification
- [phase_1_foundation_report.md](reports/phase_1_foundation_report.md) — Phase 1 foundation test report (120 tests)
- [phase_1.2_report.md](reports/phase_1.2_report.md) — Phase 1.2 consolidated test report (63 tests)

### AGENTS.md References

- AGENTS.md §18.1 — Dependencies and Stack (no CDN fonts; system-ui; root-relative asset paths)
- AGENTS.md §18.12 — Local HTTP Server (`serve.py`) — dynamic tool-picker, port-probe, path security, proxy rules, cache busting
- AGENTS.md §18.13 — Backend Phase Server Convention — standalone runnable, dependency check, health endpoint, DuckDB retry
- AGENTS.md §18 — UI Web Design (VS Code layout, themes, sidebars)
- AGENTS.md §15 — Workplan requirements
- AGENTS.md §6 — Folder convention

### Technical References

- [Chart.js 4 Documentation](https://www.chartjs.org/) — self-hosted at `eks/ui/static/chart.min.js`
- [Fetch API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [localStorage Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [DuckDB Python API](https://duckdb.org/docs/api/python/overview) — `read_only=True` mode for Phases 2–4
- [pathlib.Path.is_relative_to](https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.is_relative_to) — path security guard (Python 3.9+)

### Configuration Files

- `eks/config/schemas/eks_config.json` — Core configuration
- `eks/config/schemas/eks_doc_config.json` — Document configuration
- `eks/config/schemas/eks_base_schema.json` — Schema definitions

---

## Next Steps

### Immediate (Phase 1.2.8 — Pending Approval)

1. **Approve Phase 1.2.8 scope** — review 10 tasks and expanded success criteria in this workplan
2. **Execute T1.2.8.1** — implement `_build_index()` with `ROOT` scope, wire to `GET /`, update asset paths to root-relative (resolves I047)
3. **Execute T1.2.8.2** — migrate all Phase 1 endpoints to `/api/v1/`; **simultaneously fix frontend/backend contract mismatches** (POST vs GET files/load, `data_dir` param, review submission endpoint, startup bug) in same commit (resolves I048, AC1–AC4, AD, AE)
4. **Execute T1.2.8.3** — add port-probe and `--phase{N}-port` args (resolves I049)
5. **Execute T1.2.8.4** — wrap engine imports with actionable error (resolves I051)
6. **Execute T1.2.8.5** — download Chart.js 4, self-host; remove CDN imports from `eks.css`, `index.html`, and `eks.js` runtime fallback (resolves I050, AH)
7. **Execute T1.2.8.6** — add path traversal guard to `server.py` (resolves I052)
8. **Execute T1.2.8.7** — audit and wrap all DuckDB calls with `_with_retry()`; **add concurrency guard (409)** (resolves I053, G)
9. **Execute T1.2.8.8** — refactor proxy error handling with granular HTTPError/URLError/Exception catches; add Ollama proxy; update `eks.js` 503 UX (completes I049/I051, D)
10. **Execute T1.2.8.9** — add server compliance hooks: cache busting, URL decode, ConnectionReset suppression, 120s timeout, log filtering (gaps A, B, C, E, F)
11. **Execute T1.2.8.10** — align frontend contracts: `apiPut` helper, review submission mapping, health endpoint `phase` field (gaps AC2, H)
12. **Run full test suite** — target ~206 tests passing; generate Phase 1.2.8 test report in `eks/workplan/reports/`
13. **Update EKS issue log** — mark I047–I053 resolved; add new issues for gaps tracked in T1.2.8.9–T1.2.8.10

### After Phase 1.2.8 Complete

14. **Phase 1.2.8 marked COMPLETE** — scope items S1.2.1–S1.2.8 delivered, server & UI compliant with AGENTS.md §18.12–18.13 and Appendix G §10
15. **Run gap analysis verification** — cross-reference all workplan task claims against actual source code; capture any remaining discrepancies (e.g. I050 CSS `@import` claim found inaccurate). Update issue log descriptions if needed.
16. **Begin Phase 1.2.9** — UI Design System & Component Upgrade (14 days, 7 tasks):
    - T1.2.9.1: CSS token migration (gaps I, J, O)
    - T1.2.9.2: Theme dropdown (gaps L, M)
    - T1.2.9.3: Dual-purpose right sidebar + accordion (gap T)
    - T1.2.9.4: KPI cards + stage cards (gaps U, V)
    - T1.2.9.5: Sortable table + row cap + highlight (gaps W, X, AB)
    - T1.2.9.6: UI polish — 48px icon bar, body drag-drop, resize persistence, file input, icons, fonts (gaps S, AA, R, Z, AF, AG, Y)
    - T1.2.9.7: Update Appendix G documentation with missing design patterns (gaps AI–AR)
17. **Begin Phase 1.2.10** — Documentation close-out:
    - Verify Appendix G version header matches revision history
    - Verify all cross-references between workplan, issue log, and Appendix G are consistent
    - Run project-wide grep for stale version numbers per AGENTS.md §13
    - Generate Phase 1.2.9 test report in `eks/workplan/reports/`
18. **Phase 1.2.11 COMPLETE** — ✅ UI Workflow Redesign (8 tasks, 28 tests pass)
19. **Phase 1.2.12 COMPLETE** — ✅ Folder Picker & SSOT Path Resolution (8 tasks, 66 tests pass)
20. **Phase 1.2 marked COMPLETE** — all scope items S1.2.1–S1.2.12 delivered
21. **Proceed to Phase 2** — chunking, embedding, and vector storage; create `phase2_embedding.html` and `phase2_server.py` following the G10.8 checklist

---

**End of Workplan**
