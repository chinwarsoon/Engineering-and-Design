# EKS Phase 1.2 — Interactive UI, I/O Contracts & Document Processing Sub-Pipeline

**Document ID**: WP-EKS-P1.2-001  
**Current Version**: 1.5  
**Status**: ✅ COMPLETE (All Phases 1.2.0–1.2.7)  
**Last Updated**: 2026-07-01  
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
                             │ JavaScript (Fetch API)
                             │ port 5000
┌────────────────────────────┴────────────────────────────────────┐
│              Main Launcher Server — eks/server.py               │
│  ┌──────────────────────┐  ┌──────────────────────────────┐    │
│  │ HTML File Picker     │  │ Proxy: /api/* → localhost:   │    │
│  │ (VS Code style,      │  │ 5001 (Phase 1 backend)       │    │
│  │  tool discovery)     │  │ Proxy: /ollama/* → localhost:│    │
│  │                      │  │ 11434                        │    │
│  │ Serve: eks/ui/static │  │ CORS headers on all          │    │
│  └──────────────────────┘  └──────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │ proxy via urllib
                             │ port 5001
┌────────────────────────────┴────────────────────────────────────┐
│  Phase 1 Backend — eks/ui/backend/phase1_server.py             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ API          │  │ Pipeline     │  │ Document     │          │
│  │ Endpoints    │  │ Orchestrator │  │ Registry API │          │
│  │ (files, docs,│  │ (background  │  │ (DuckDB)     │          │
│  │  pipeline)   │  │  thread)     │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │ direct import
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
│  │ (Registry)   │  │ (Documents)  │  │ (ui_help.json)│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User loads files** → UI File Loading Panel → JavaScript → port 5000 → `eks/server.py` (proxy) → port 5001 → `phase1_server.py` → FileScanner
2. **FileScanner discovers files** → ParserRouter → Parsers
3. **Parsers extract content** → StructureDetector → HealthScorer
4. **HealthScorer computes scores** → DocumentRegistry → DuckDB
5. **UI polls for status** → JavaScript fetch → port 5000 → `eks/server.py` (proxy) → port 5001 → `phase1_server.py` → Registry → JSON response
6. **UI updates display** → Main Panel → Document Dashboard
7. **User reviews flagged docs** → ManualReviewManager → Registry updates

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

Technology stack decisions (frontend: vanilla JS + Fetch API + Chart.js CDN; backend: http.server; rationale) are documented in **Appendix G §2.1** (Document Processing Dashboard).

---

## Pipeline Workflow

### 1. File Loading

```
User Action: Click file load icon or drag-drop files
    ↓
JavaScript: Read file list from input
    ↓
POST /api/files/load
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
POST /api/pipeline/start
    ↓
Backend: Start background thread with PipelineOrchestrator
    ↓
Return: Job ID for tracking
    ↓
UI: Start polling /api/pipeline/status/{job_id} every 2s
```

### 3. Status Polling (per Appendix G §4)

Job lifecycle (`queued → running → completed/failed/cancelled`), polling parameters, and response format are defined in **Appendix G §4**. Frontend implementation follows the `pollJobStatus` pattern in G4.4.

### 4. Results Display

```
GET /api/documents
    ↓
Return: JSON with paginated document list
    ↓
UI: Render document table in main panel
    ↓
User Action: Click document row
    ↓
GET /api/documents/{doc_id}
    ↓
Return: JSON with full document metadata + health score
    ↓
UI: Render document detail view
```

### 5. Manual Review

```
User Action: Edit metadata fields in detail view
    ↓
PUT /api/documents/{doc_id}
    ↓
Backend: ManualReviewManager.update_document()
    ↓
DocumentRegistry.update()
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

## Dependencies

### Server Architecture Dependencies

| Server | Depends On | Port |
| :----- | :--------- | :--- |
| `eks/server.py` | (none — entry point) | 5000 |
| `eks/ui/backend/phase1_server.py` | Must be reachable by main server proxy | 5001 |

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

| Dependency | Version | Purpose |
| :--------- | :------ | :------- |
| Python stdlib | 3.13+ | http.server, threading, json, urllib |
| Chart.js | 4+ (CDN) | Health score charts |
| Browser APIs | Native | Fetch, localStorage |

---

## Risks and Mitigation

| Risk | Severity | Impact | Mitigation |
| :--- | :------: | :----- | :--------- |
| Phase 1 sync calls block HTTP server | 🟠 High | Server unresponsive | Run pipeline in background thread |
| DuckDB concurrent access | 🟠 High | Database corruption | Use connection singleton |
| CSS complexity for resizable sidebars | 🟡 Medium | Layout breaks | Use CSS Grid with resize handles |
- Browser compatibility | 🟢 Low | UI breaks in some browsers | Test on Chrome, Firefox, Edge |
- Chart.js CDN availability | 🟢 Low | Charts fail to load | Add fallback text |
- localStorage quota exceeded | 🟢 Low | Theme/layout not saved | Handle quota errors gracefully |

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
- [appendix_g_interface_architecture.md](appendix_g_interface_architecture.md) — UI theme (§5), help system (§6), API conventions (§3), polling (§4), UI contracts (§7), server architecture (§10)

### Other Phase 1 Documents

- [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) — Foundation module specification
- [phase_1_foundation_report.md](reports/phase_1_foundation_report.md) — Phase 1 test report

### AGENTS.md References

- AGENTS.md §18 — UI Web Design (VS Code style layout)
- AGENTS.md §15 — Workplan requirements
- AGENTS.md §6 — Folder convention

### Technical References

- [Chart.js Documentation](https://www.chartjs.org/)
- [Fetch API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [localStorage Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)

### Configuration Files

- `eks/config/schemas/eks_config.json` — Core configuration
- `eks/config/schemas/eks_doc_config.json` — Document configuration
- `eks/config/schemas/eks_base_schema.json` — Schema definitions

---

## Next Steps

1. **Review and Approval**: Stakeholder review of this workplan
2. **Phase 1.2.0 Complete**: Engine I/O contracts defined and tested (35 tests)
3. **Phase 1.2.1 Complete**: Backend HTTP servers (main launcher + Phase 1 backend, 12 API endpoints, 20 integration tests)
4. **Weekly Check-ins**: Progress review at end of each phase
5. **UAT**: User acceptance testing after Phase 1.2.7
6. **Deployment**: Deploy to staging environment for pilot use

---

**End of Workplan**
