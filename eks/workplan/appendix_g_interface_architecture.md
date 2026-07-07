# Appendix G — Interface Architecture

**Version**: 0.5  
**Last Updated**: 2026-07-07  
**Phase**: 1.2 — Interactive UI, I/O Contracts & Document Processing  
**Status**: 📋 Proposed  
**Related Documents**:
- [`AGENTS.md §18`](../../AGENTS.md) — UI Web Design (layout structure, theme toggle, layout switching, serve.py rules)
- [`appendix_f_pipeline_architecture_design.md`](appendix_f_pipeline_architecture_design.md) — Engine I/O contracts (EngineInput/EngineOutput, BaseEngine)
- [`phase_1.2_interactive_ui_workplan.md`](phase_1.2_interactive_ui_workplan.md) — Phase 1.2 workplan referencing this appendix
- [`phase_5_ui_integration_workplan.md`](phase_5_ui_integration_workplan.md) — Phase 5 workplan referencing this appendix

### Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------ |
| 0.1 | 2026-06-30 | opencode | Initial draft: G1–G8 covering UI architecture conventions, API patterns, theme system, help system, and cross-phase references |
| 0.2 | 2026-07-01 | opencode | Added G10 Server Architecture (two-server pattern, port allocation, proxy routing). Updated G3.1 (proxy note), G3.4 (two-server flow), G9 (G10 reference). Per Phase 1.2 server design review. |
| 0.3 | 2026-07-02 | opencode | Rewrote G10 to align with DCC serve.py design: dynamic `_build_index()` tool picker, all five phases get own backend server (ports 5001–5005), versioned `/api/v{N}/` prefix routing, full endpoint table for all phases, phase-by-phase build order table, G10.7 implementation rules, G10.8 checklist. Fixed G10.2 routing table (removed /static/*, added all 5 proxy rules). Updated G9 cross-phase reference. |
| 0.4 | 2026-07-02 | opencode | Added G10.9 Restricted Corporate Computer constraints (network, port, env, DuckDB, self-hosting, known issues I047–I054). Updated G10.7 implementation rules (port probe, path security, backend-not-reachable 503, dependency check). Updated G10.3.3 (removed CDN font reference). References AGENTS.md §18.12–18.13. |
| 0.5 | 2026-07-07 | opencode | Updated G2.1 (Chart.js self-hosted), G3.1 (versioned /api/v1/ paths), G5 (design tokens, theme dropdown, accordion sidebar, KPI cards, data table, polish items). Added G5.4–G5.9 UI component documentation. Updated localStorage key to `eks-theme`. Updated G5.3 CSS pattern to match universal_ui_design.css. |

---

## G1. Purpose & Scope

This appendix documents **universal interface architecture decisions** that apply to multiple EKS phases. It sits between the high-level layout rules in AGENTS.md §18 and the engine-level I/O contracts in Appendix F.

| Document | Covers | Scope |
| :------- | :----- | :---- |
| AGENTS.md §18 | Layout structure, theme toggle, layout switching, icons, help system | Universal (all projects) |
| **Appendix G** | Theme colors, help schema, API conventions, polling, job lifecycle, contract ownership | EKS cross-phase |
| Appendix F §2.3 | EngineInput/EngineOutput, BaseEngine, CLI entry points | EKS all phases |
| Phase workplans | Phase-specific UI implementations | Per phase |

Scope of this appendix:
- **G2** — Technology stack decisions per use case
- **G3** — Backend API endpoint and error conventions
- **G4** — Status polling and progress tracking
- **G5** — UI theme palette (5 specific themes, defaults, localStorage keys)
- **G6** — Help system JSON schema (`ui_help.json`)
- **G7** — UI contract ownership and schema
- **G8** — Status bar format convention
- **G9** — Cross-phase references
- **G10** — Server architecture (tool launcher, proxy routing, port allocation, implementation rules)

---

## G2. Technology Stack Guidelines

EKS has two distinct UI use cases that justify different technology stacks:

### G2.1 Document Processing Dashboard (Phase 1.2)

| Layer | Technology | Rationale |
| :---- | :--------- | :-------- |
| Backend | `http.server` (Python stdlib) | Zero dependencies, sufficient for back-office dashboard |
| Frontend | Vanilla JavaScript + HTML5 + CSS3 | No build step, opens directly in browser |
| Charts | Chart.js 4+ (self-hosted at `eks/ui/static/chart.min.js`) | Lightweight, works offline on restricted networks |
| HTTP Client | Fetch API (native) | No external dependency |
| State | localStorage | Theme, layout persistence |

### G2.2 End-User Inquiry Interface (Phase 5)

| Layer | Technology | Rationale |
| :---- | :--------- | :-------- |
| Backend | FastAPI / Flask | Async support, OpenAPI docs, production-grade |
| Frontend | React SPA (recommended) or vanilla JS fallback | Rich interactivity for query + asset browsing |
| Cache | Redis / in-memory | Production caching for repeated queries |
| Charts | Chart.js or D3.js | Phase-specific visualization needs |

### G2.3 Shared Conventions

Despite different stacks, both UI phases must follow:

1. **REST JSON API** — All backend endpoints return `Content-Type: application/json`
2. **CORS enabled** — Manual headers (`http.server`) or middleware (FastAPI)
3. **Fetch API client** — Frontend uses native `fetch()` for all HTTP calls
4. **localStorage** — For UI state (theme, layout, preferences)
5. **No build step for core HTML** — The main dashboard HTML opens directly; React SPA is optional for Phase 5

---

## G3. Backend API Conventions

### G3.1 Endpoint Pattern

All EKS UI backends follow these endpoint conventions:

| Method | Endpoint Pattern | Purpose | Phases |
| :----- | :--------------- | :------ | :----- |
| `POST` | `/api/v1/pipeline/start` | Start async pipeline execution | 1.2 |
| `GET` | `/api/v1/pipeline/status/{job_id}` | Poll pipeline progress | 1.2, 5 |
| `DELETE` | `/api/v1/pipeline/{job_id}` | Cancel running pipeline | 1.2, 5 |
| `GET` | `/api/v1/pipeline/logs/{job_id}` | Stream pipeline logs | 1.2, 5 |
| `GET` | `/api/v1/documents` | List documents with pagination/filters | 1.2, 5 |
| `GET` | `/api/v1/documents/{id}` | Get document detail | 1.2, 5 |
| `PUT` | `/api/v1/documents/{id}` | Update document metadata | 1.2, 5 |
| `POST` | `/api/v1/files/load` | Trigger file discovery scan | 1.2 |
| `GET` | `/api/v1/query` | Submit natural language query | 5 |
| `GET` | `/api/v1/assets` | List/filter assets | 5 |
| `GET` | `/api/v1/ontology/classes` | Get ontology class tree | 5 |

All `/api/v{N}/*` requests arrive at the main server (`eks/server.py`, port 5000) and are **proxied** to the appropriate phase backend server (port 5001 for Phase 1, port 5005 for Phase 5). Un-versioned `/api/*` paths return HTTP 404. See [G10](#g10-server-architecture).

### G3.2 Error Response Format

All endpoints return a consistent error envelope:

```json
{
  "status": "error",
  "error": {
    "code": "P1-D-P-0001",
    "message": "File discovery failed: directory not found",
    "severity": "HIGH",
    "remediation": "Verify the data directory exists at eks/data/"
  }
}
```

### G3.3 CORS Configuration

All backends must accept cross-origin requests from the frontend origin:

| Backend | Implementation |
| :------ | :------------- |
| `http.server` | Manual `Access-Control-Allow-Origin: *` header in response |
| FastAPI | `CORSMiddleware` with `allow_origins=["*"]` |

### G3.4 Background Job Pattern

Long-running tasks (pipeline execution) must run in background threads with job tracking:

```
REQUEST  →  POST /api/pipeline/start
              ↓
MAIN      →  eks/server.py (port 5000) proxies to phase backend
SERVER    →  localhost:5001 (Phase 1)
              ↓
PHASE     →  Generate job_id (UUID)
SERVER    →  Start background thread
              ↓
              Return {job_id, status: "queued"}
              ↓
CLIENT   →  Poll GET /api/pipeline/status/{job_id} every 2s
              ↓
              Display progress bar + log viewer
```

---

## G4. Status Polling Convention

### G4.1 Job Lifecycle

```
queued → running → completed
                    → failed
                    → cancelled
```

### G4.2 Status Response Format

```json
{
  "job_id": "a1b2c3d4-...",
  "status": "running",
  "progress": {
    "current": 7,
    "total": 15,
    "percentage": 47
  },
  "stage": "Parsing documents",
  "errors": [],
  "started_at": "2026-06-30T10:00:00Z",
  "elapsed_seconds": 14.2
}
```

### G4.3 Polling Parameters

| Parameter | Value | Notes |
| :-------- | :---- | :---- |
| Poll interval | 2000ms | Default; adjust per endpoint |
| Backoff strategy | None | Fixed interval for simplicity |
| Timeout | 300000ms (5 min) | Max wait before showing "taking longer than expected" |
| Retry logic | 3 retries on network error | Exponential backoff: 1s, 2s, 4s |

### G4.4 Frontend Polling Implementation

```javascript
async function pollJobStatus(jobId, onUpdate, onComplete, onError) {
  const poll = async () => {
    try {
      const response = await fetch(`/api/pipeline/status/${jobId}`);
      const data = await response.json();
      onUpdate(data);

      if (data.status === 'completed') { onComplete(data); return; }
      if (data.status === 'failed')    { onError(data);   return; }
      if (data.status === 'cancelled') { onComplete(data); return; }

      setTimeout(poll, 2000);
    } catch (err) {
      onError(err);
    }
  };
  poll();
}
```

---

## G5. UI Theme System

### G5.1 Theme Palette

AGENTS.md §18 defines theme toggle and 5 theme options. The specific colors are:

| Theme | Background | Text | Accent | Sidebar | Status Bar |
| :---- | :--------- | :--- | :----- | :------ | :--------- |
| Light | `#ffffff` | `#000000` | `#007acc` | `#f3f3f3` | `#007acc` |
| Dark | `#1e1e1e` | `#d4d4d4` | `#3794ff` | `#252526` | `#007acc` |
| Sky | `#e0f7fa` | `#000000` | `#00bcd4` | `#b2ebf2` | `#00bcd4` |
| Ocean | `#e3f2fd` | `#000000` | `#2196f3` | `#bbdefb` | `#2196f3` |
| Presentation | `#f5f5f5` | `#333333` | `#666666` | `#e0e0e0` | `#666666` |

### G5.2 Persistence

| Setting | localStorage Key | Default |
| :------ | :-------------- | :------ |
| Theme | `eks-theme` | `"dark"` |
| Layout | `eks_layout` | `"triple"` |
| Left sidebar width | `eks-left-sidebar-w` | `"260px"` |
| Right sidebar visibility | `eks_sidebar_right` | `"true"` |

### G5.3 CSS Design Token System

All projects share a common set of CSS custom properties defined in `common/universal_ui_design.css`. Project-specific overrides go in the project's CSS file (e.g. `eks/ui/eks.css`).

**Required token groups** (AGENTS.md §18.3):

| Group | Variables |
| :---- | :-------- |
| Surfaces | `--bg`, `--surface`, `--surface2`, `--surface3` |
| Borders | `--border` |
| Text | `--text`, `--text2`, `--text3` |
| Accent | `--accent`, `--accent-alt` |
| Semantic | `--success`, `--warning`, `--danger`, `--info` |
| Tag | `--tag-bg`, `--tag-border` |
| Table | `--row-stripe`, `--row-hover`, `--th-bg`, `--th-hover` |
| Dimensions | `--icon-bar-w`, `--sidebar-w`, `--right-sidebar-w`, `--titlebar-h`, `--statusbar-h` |
| Radii | `--radius`, `--radius-sm`, `--radius-lg` |
| Fonts | `--font-ui`, `--font-mono` |

All component colors must reference `var(--token)` — never hardcoded hex values. Applied via `:root` / `[data-theme="..."]` overrides in the universal CSS.

### G5.4 Theme Dropdown Pattern

Phase 1.2+ UIs use a dropdown menu (not a cycle button) in the title bar:

```html
<button class="com-theme-btn" id="themeBtn">🎨 <span class="com-theme-dot"></span> Theme</button>
<div class="com-theme-menu">
  <div class="com-theme-opt active" data-theme="dark"><span class="com-theme-dot" style="background:#1e1e1e"></span> Dark</div>
  <div class="com-theme-opt" data-theme="light"><span class="com-theme-dot" style="background:#ffffff"></span> Light</div>
  <div class="com-theme-opt" data-theme="sky"><span class="com-theme-dot" style="background:#e0f7fa"></span> Sky</div>
  <div class="com-theme-opt" data-theme="ocean"><span class="com-theme-dot" style="background:#e3f2fd"></span> Ocean</div>
  <div class="com-theme-opt" data-theme="presentation"><span class="com-theme-dot" style="background:#f5f5f5"></span> Presentation</div>
</div>
```

Initialize with `comUI.theme.initPicker('eks-theme')`. Active option is marked with `.active` class. Theme persisted to `localStorage` under the key `<project>-theme`.

### G5.5 Right Sidebar Accordion

The right sidebar supports three context-switchable views (Detail, Settings, Help) using `.sb-section` accordion elements per AGENTS.md §18.5:

- `.sb-section` — container with bottom border
- `.sb-section-header` — clickable row with icon, label, right-aligned chevron `▼`
- `.sb-section-body` — collapsible content; hidden by `.closed` on the parent `.sb-section` (chevron rotates −90°)
- Initialize accordion with `comUI.sidebar.accordion(element)`
- A "← Back" button in the header reopens the Detail section when in Settings/Help mode

### G5.6 KPI Card Grid

Dashboards display metric tiles using a CSS grid:

```css
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
}
```

Each KPI card shows: large value, label, sub-label (delta or percentage), and a health gauge bar (`linear-gradient(90deg, var(--danger), var(--warning), var(--success))`). Cards are clickable — hover adds `border-color: var(--accent)` + `box-shadow: 0 0 0 1px var(--accent)`.

### G5.7 Stage Cards

Pipeline stages render as individual bordered rounded cards with:

- Numbered emoji icon
- Stage name + meta description (truncated with ellipsis)
- Status text: PASS (`--success`), FAIL (`--danger`), RUNNING (`--accent`), PENDING (`--text3`)
- 4px progress bar colored per status
- Hover state: `border-color: var(--accent)` + `box-shadow: 0 0 0 1px var(--accent)`

### G5.8 Data Table Component

Tabular data renders as `<table>` with:

- Sortable column headers — click toggles asc/desc, shows `▲` / `▼` indicator
- 50-row cap by default with "Show all N" toggle link in footer
- `.selected` class on active row with 3px left-border highlight using `--accent`
- Row count displayed in footer

### G5.9 UI Polish

Additional UI requirements per AGENTS.md §18:

| Item | Requirement | Implementation |
| :--- | :---------- | :------------- |
| Icon bar width | 48px | `--icon-bar-w: 48px` in universal CSS |
| Drag-and-drop | On full page body, not a drop zone | `dragover`/`drop` listeners on `document` |
| Sidebar width | Persisted to localStorage | `comUI.sidebar.resize()` with `storageKey` option |
| Font stack | `system-ui` first | `--font-ui: system-ui, -apple-system, 'Segoe UI', sans-serif` |
| Cache meta | `<meta http-equiv="Cache-Control" content="no-cache">` in HTML `<head>` | Applied in `phase1_ingestion.html` |
| Refresh icon | 🔄 in right icon bar | Triggers `GET /api/v1/documents` re-fetch |
| Info icon | ℹ️ in right icon bar | Shows system version toast |

---

## G6. Help System Schema

### G6.1 File

`eks/ui/ui_help.json` — loaded at page initialization via `fetch()`.

### G6.2 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EKS UI Help System",
  "description": "Help text, about section, default paths, and definitions for the EKS UI",
  "version": "1.0.0",
  "type": "object",
  "required": ["about", "help", "default_folders", "definitions"],
  "properties": {
    "about": {
      "type": "string",
      "description": "System name and version displayed in About modal"
    },
    "help": {
      "type": "object",
      "description": "Context-sensitive help text keyed by feature name",
      "additionalProperties": { "type": "string" }
    },
    "default_folders": {
      "type": "object",
      "description": "Default path suggestions for file pickers",
      "additionalProperties": { "type": "string" }
    },
    "definitions": {
      "type": "object",
      "description": "Glossary of domain terms",
      "additionalProperties": { "type": "string" }
    }
  }
}
```

### G6.3 Example Content

```json
{
  "about": "Engineering Knowledge System (EKS) — Document Processing Dashboard v1.0",
  "help": {
    "file_load": "Load documents from local disk or pipeline data folder",
    "tree_view": "Navigate document hierarchy by project, discipline, and type",
    "health_score": "6-dimension quality assessment (completeness 0.20, confidence 0.15, ...)"
  },
  "default_folders": {
    "data": "eks/data/",
    "output": "eks/output/"
  },
  "definitions": {
    "document": "Engineering document with metadata, revisions, and health score",
    "health_score": "Quality score from 0.0 to 1.0 across 6 dimensions",
    "extract_status": "pending | in_progress | completed | flagged | locked"
  }
}
```

### G6.4 Keyboard Shortcut

| Key | Action |
| :-- | :----- |
| `F1` | Open help modal (loads content from ui_help.json) |

---

## G7. UI Contracts

### G7.1 Ownership

`eks/ui/backend/contracts.py` is the **Single Source of Truth** for UI contract definitions. All phases that define UI contracts must import from this file — never redefine.

### G7.2 Contract Definitions

```python
@dataclass
class DocumentSelectionContract:
    """Validates document selection for pipeline processing"""
    data_dir: str                    # Path to document data folder
    file_types: List[str]            # Filter by extension (e.g., ["pdf", "docx"])
    include_subfolders: bool = True
    max_files: int = 1000

@dataclass
class PipelineConfigContract:
    """Pipeline execution parameters"""
    debug: bool = False
    workers: int = 1
    health_threshold: float = 0.5    # Minimum score for auto-register
    skip_parsing: bool = False       # Dry-run mode

@dataclass
class QueryRequestContract:
    """User query input (Phase 5)"""
    query: str
    filters: Dict[str, Any] = None   # Project, discipline, doc type, revision
    max_results: int = 10

@dataclass
class QueryResponseContract:
    """Query result output (Phase 5)"""
    answer: str
    sources: List[Dict[str, Any]]    # Citations with doc_number, revision, page
    assets: List[Dict[str, Any]]     # Linked asset references
    confidence: float
```

### G7.3 Validation

All contracts must implement:

```python
class UIContractManager:
    def validate_document_selection(self, contract: DocumentSelectionContract) -> bool
    def validate_pipeline_config(self, contract: PipelineConfigContract) -> bool
    def serialize_to_json(self, contract) -> dict
    def deserialize_from_json(self, data: dict, contract_type) -> object
```

---

## G8. Status Bar Convention

### G8.1 Format

```
{Left section} | {Center section} | {Right section}
```

### G8.2 Content

| Section | Phase 1.2 (Dashboard) | Phase 5 (Inquiry) |
| :------ | :-------------------- | :----------------- |
| Left | Selected file name | Selected item name |
| Center | `Health: {score} | Status: {status}` | `Query time: {ms}ms | Results: {n}` |
| Right | Last updated timestamp | Session ID |

### G8.3 Implementation

Status bar must be a fixed `position: fixed; bottom: 0` element updated via JavaScript whenever the selection changes or pipeline status updates.

---

## G9. Cross-Phase References

| What to Reference | Where |
| :---------------- | :---- |
| Layout structure, theme toggle, layout switching, serve.py rules | AGENTS.md §18 |
| Engine I/O contracts (EngineInput/EngineOutput, BaseEngine, CLI) | Appendix F §2.3 |
| Theme colors, CSS variable pattern, help schema | **Appendix G §5–§6** |
| API endpoint conventions, polling pattern | **Appendix G §3–§4** |
| UI contract ownership and validation | **Appendix G §7** |
| Status bar format | **Appendix G §8** |
| Phase-specific UI implementation | Phase workplan (1.2 or 5) |
| Server architecture (tool launcher, port allocation, proxy routing, implementation rules) | **Appendix G §10** |

---

## G10. Server Architecture

### G10.1 Overview

EKS uses a **two-tier server architecture**. The main launcher server (`eks/server.py`) is the single entry point for all browser access — it dynamically discovers every HTML tool under the `eks/` folder and presents a VS Code-styled tool-picker page, while proxying all API traffic to the appropriate phase backend. Each phase has its own dedicated backend server that exposes the API endpoints needed to run, test, and inspect the outputs of that phase in isolation.

| Server | Location | Default Port | Stack | Responsibility |
| :----- | :------- | :----------- | :---- | :------------- |
| Main launcher | `eks/server.py` | 5000 | `http.server` stdlib | Dynamic HTML tool-picker, proxy routing, static file serving, Ollama proxy |
| Phase 1 backend | `eks/ui/backend/phase1_server.py` | 5001 | `http.server` stdlib | Document ingestion, parsing, health scoring, document registry CRUD, manual review |
| Phase 2 backend | `eks/ui/backend/phase2_server.py` | 5002 | `http.server` stdlib | Chunking, embedding, Qdrant vector store — run and inspect chunk/vector results |
| Phase 3 backend | `eks/ui/backend/phase3_server.py` | 5003 | `http.server` stdlib | Asset ingestion, Neo4j graph loading — run and inspect graph nodes and relationships |
| Phase 4 backend | `eks/ui/backend/phase4_server.py` | 5004 | `http.server` stdlib | Retrieval pipeline — submit test queries, inspect stage outputs, evaluate results |
| Phase 5 backend | `eks/ui/backend/phase5_server.py` | 5005 | FastAPI + uvicorn | End-user inquiry interface — production query API, asset browsing, retrieval cache |

**Design principle:** `eks/server.py` is modelled on `dcc/serve.py`. It uses only Python stdlib — zero external dependencies. Each phase backend is independently runnable for testing without the launcher. Adding a new phase UI requires only placing HTML files in `eks/ui/` — no changes to `server.py`.

**Phase backend purpose:** Each phase backend exists to let developers run that phase's pipeline, inspect its outputs, and validate correctness before moving to the next phase. They are test and operation tools, not production services (except Phase 5).

---

### G10.2 Request Routing

`eks/server.py` routes requests in this priority order (first match wins):

| Method | Path Pattern | Action |
| :----- | :----------- | :----- |
| GET | `/` | Return dynamically generated tool-picker HTML page (`_build_index()`) |
| GET/POST/PUT/DELETE | `/api/v1/*` | Proxy → `localhost:5001` (Phase 1 — document processing) |
| GET/POST/PUT/DELETE | `/api/v2/*` | Proxy → `localhost:5002` (Phase 2 — chunking & embedding) |
| GET/POST/PUT/DELETE | `/api/v3/*` | Proxy → `localhost:5003` (Phase 3 — knowledge graph) |
| GET/POST/PUT/DELETE | `/api/v4/*` | Proxy → `localhost:5004` (Phase 4 — retrieval pipeline) |
| GET/POST/PUT/DELETE | `/api/v5/*` | Proxy → `localhost:5005` (Phase 5 — end-user inquiry) |
| GET/POST | `/api/*` | 404 JSON — un-versioned path, not silently forwarded |
| GET/POST | `/ollama/*` | Proxy → `localhost:11434` (local Ollama LLM) |
| OPTIONS | `*` | CORS preflight — return `Access-Control-Allow-Origin: *` |
| GET | anything else | `SimpleHTTPRequestHandler` — serve static file relative to `eks/` root |

**Static file serving:** The `SimpleHTTPRequestHandler` is initialised with `directory = ROOT` (the `eks/` project root). HTML tools, CSS, JS, and JSON files are all served at their natural paths relative to `eks/`:
- `eks/ui/index.html` → `/ui/index.html`
- `eks/ui/eks.css` → `/ui/eks.css`
- `eks/ui/ui_help.json` → `/ui/ui_help.json`

There is no `/static/` prefix. HTML files reference assets using relative paths (e.g. `<link href="eks.css">` from within `ui/`) or root-relative paths (e.g. `/ui/eks.css`).

**Unknown API paths:** Any `/api/*` request that does not match a versioned prefix returns HTTP 404 with JSON `{"error": "Unknown API path: <path>"}`. This prevents silent proxy misrouting.

---

### G10.3 Tool Launcher Index Page (`_build_index()`)

`GET /` returns a **dynamically generated** HTML page produced by `_build_index()`. This page is the entry point for all EKS tools. It is regenerated on every request — adding a new HTML file to any scan directory makes it appear in the launcher immediately, with no server restart.

#### G10.3.1 Discovery

```python
ROOT     = Path(__file__).parent.resolve()   # eks/ directory
SCAN_DIRS = ["ui"]                           # subdirectories to scan (relative to ROOT)
EXCLUDE_DIRS = {"node_modules", "archive", "backup", "__pycache__", "static", "templates"}
```

- Recursively scans each directory in `SCAN_DIRS` for `*.html` files using `rglob("*.html")`
- Skips any file whose relative path contains a component in `EXCLUDE_DIRS`
- Groups discovered files by their immediate parent folder (first path component under `eks/`)
- Returns relative paths from `eks/` root (e.g. `ui/index.html`, `ui/phase2_dashboard.html`)

As new phase UIs are built, they are placed under `eks/ui/` and automatically appear in the launcher. Intended layout as all phases are built out:

```
eks/ui/
├── index.html                   # Phase 1.2 — Document Processing Dashboard  ← exists now
├── phase2_embedding.html        # Phase 2   — Chunking & Embedding Monitor   ← future
├── phase3_graph.html            # Phase 3   — Knowledge Graph Explorer       ← future
├── phase4_retrieval.html        # Phase 4   — Retrieval Pipeline Tester      ← future
├── phase5_inquiry.html          # Phase 5   — End-User Inquiry Interface     ← future
├── eks.css                      # Shared design system CSS
├── eks.js                       # Shared JavaScript utilities
└── ui_help.json                 # Schema-driven help content
```

All five phase dashboards appear in the same tool launcher card group. The launcher makes no assumptions about which phases are implemented — it lists whatever HTML files exist.

#### G10.3.2 Folder Labels

Each scan directory is assigned a display icon and label for the card group header:

| Folder | Icon | Label |
| :----- | :--- | :---- |
| `ui` | 🖥️ | EKS Tools |

Additional folder labels are added to the `FOLDER_LABELS` dict in `server.py` as new scan directories are introduced (e.g. a future `tools/` directory for utility pages).

#### G10.3.3 Index Page Layout

The generated page follows the AGENTS.md §18.12 design with inline styles (no external CSS dependency — the index must work even if `eks.css` is unavailable):

- **Title bar**: "EKS Tool Launcher" logo, total tool count
- **Search input**: live client-side filter — hides non-matching file links without a server round-trip
- **Card grid**: `display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`; one card per folder group
- **Card header**: folder icon + label + file count badge
- **File links**: each `*.html` file as a clickable link opening at its URL path (e.g. `/ui/index.html`)
- **Status bar**: fixed bottom strip — left: tool count (updates as search filters); right: "EKS Local Server · port {PORT}"
- **Styling**: GitHub-dark colour tokens inline (`#0d1117` bg, `#161b22` surface, `#2f81f7` accent). Font: `system-ui, -apple-system, 'Segoe UI', sans-serif` — **no CDN font dependency** (see G10.9.1 and AGENTS.md §18.1).

#### G10.3.4 File URL Mapping

| File on disk | URL served at |
| :----------- | :------------ |
| `eks/ui/index.html` | `http://localhost:5000/ui/index.html` |
| `eks/ui/phase2_embedding.html` | `http://localhost:5000/ui/phase2_embedding.html` |
| `eks/ui/phase3_graph.html` | `http://localhost:5000/ui/phase3_graph.html` |
| `eks/ui/phase4_retrieval.html` | `http://localhost:5000/ui/phase4_retrieval.html` |
| `eks/ui/phase5_inquiry.html` | `http://localhost:5000/ui/phase5_inquiry.html` |

---

### G10.4 API Proxy Versioning

All EKS phase backend API endpoints use a versioned path prefix. The main server routes strictly by prefix to the correct backend.

#### G10.4.1 Prefix Convention

| Path Prefix | Target Backend | Port | Phase | Status |
| :---------- | :------------- | :--- | :---- | :----- |
| `/api/v1/*` | `phase1_server.py` | 5001 | Phase 1 — Document processing | ✅ Built |
| `/api/v2/*` | `phase2_server.py` | 5002 | Phase 2 — Chunking & embedding | 🔷 Planned |
| `/api/v3/*` | `phase3_server.py` | 5003 | Phase 3 — Knowledge graph | 🔷 Planned |
| `/api/v4/*` | `phase4_server.py` | 5004 | Phase 4 — Retrieval pipeline | 🔷 Planned |
| `/api/v5/*` | `phase5_server.py` | 5005 | Phase 5 — End-user inquiry | 🔷 Planned |
| `/api/*` | **404** | — | Un-versioned — always rejected | — |

**Rule:** Clients (HTML pages) must never call `/api/` without a version prefix. Each phase HTML dashboard uses only its own `/api/v{N}/` prefix.

#### G10.4.2 Endpoint Table — All Phases

| Method | Versioned Endpoint | Purpose | Phase |
| :----- | :----------------- | :------ | :---- |
| **Phase 1 — Document Processing** | | | |
| `GET` | `/api/v1/status` | Phase 1 backend health check | 1 |
| `POST` | `/api/v1/files/load` | Trigger file discovery scan | 1 |
| `POST` | `/api/v1/pipeline/start` | Start document processing pipeline | 1 |
| `GET` | `/api/v1/pipeline/status/{job_id}` | Poll pipeline progress | 1 |
| `DELETE` | `/api/v1/pipeline/{job_id}` | Cancel running pipeline | 1 |
| `GET` | `/api/v1/pipeline/logs/{job_id}` | Stream pipeline log entries | 1 |
| `GET` | `/api/v1/documents` | List documents with filters | 1 |
| `GET` | `/api/v1/documents/{id}` | Get document detail + health score | 1 |
| `PUT` | `/api/v1/documents/{id}` | Update document metadata | 1 |
| `GET` | `/api/v1/review/summary` | Review status summary | 1 |
| `GET` | `/api/v1/review/flagged` | List flagged documents | 1 |
| `PUT` | `/api/v1/review/lock` | Lock a reviewed document | 1 |
| `PUT` | `/api/v1/review/recalculate` | Recalculate document health score | 1 |
| **Phase 2 — Chunking & Embedding** | | | |
| `GET` | `/api/v2/status` | Phase 2 backend health check | 2 |
| `POST` | `/api/v2/chunking/run` | Run chunking pipeline on registered documents | 2 |
| `GET` | `/api/v2/chunking/status/{job_id}` | Poll chunking job progress | 2 |
| `GET` | `/api/v2/chunks` | List chunks with filters (doc_number, page, section) | 2 |
| `GET` | `/api/v2/chunks/{chunk_id}` | Get chunk detail + parent/sibling info | 2 |
| `POST` | `/api/v2/embedding/run` | Run embedding pipeline on chunks | 2 |
| `GET` | `/api/v2/embedding/status/{job_id}` | Poll embedding job progress | 2 |
| `GET` | `/api/v2/vectors/search` | Test vector similarity search (query text → top-k chunks) | 2 |
| `GET` | `/api/v2/vectors/stats` | Qdrant collection stats (eks_chunks, eks_assets) | 2 |
| **Phase 3 — Knowledge Graph** | | | |
| `GET` | `/api/v3/status` | Phase 3 backend health check | 3 |
| `POST` | `/api/v3/graph/load-assets` | Load datadrop Excel into Neo4j asset graph | 3 |
| `GET` | `/api/v3/graph/status/{job_id}` | Poll asset loading job progress | 3 |
| `GET` | `/api/v3/assets` | List assets with filters (tag_type, unit, service) | 3 |
| `GET` | `/api/v3/assets/{keytag}` | Get asset node detail + all relationships | 3 |
| `GET` | `/api/v3/graph/stats` | Neo4j node/edge counts by type | 3 |
| `GET` | `/api/v3/graph/neighbours/{keytag}` | Get immediate graph neighbours of an asset node | 3 |
| `POST` | `/api/v3/ontology/reload` | Reload T-Box ontology classes from config | 3 |
| `GET` | `/api/v3/ontology/classes` | Get full ontology class hierarchy | 3 |
| **Phase 4 — Retrieval Pipeline** | | | |
| `GET` | `/api/v4/status` | Phase 4 backend health check | 4 |
| `POST` | `/api/v4/query` | Submit a test query — returns full retrieval trace + LLM answer | 4 |
| `GET` | `/api/v4/query/{query_id}/trace` | Get per-stage retrieval trace for a past query | 4 |
| `GET` | `/api/v4/query/{query_id}/chunks` | Get the chunks assembled for a past query | 4 |
| `GET` | `/api/v4/query/{query_id}/assets` | Get asset results for a past query | 4 |
| `POST` | `/api/v4/query/batch` | Run a batch of test queries for evaluation | 4 |
| `GET` | `/api/v4/eval/metrics` | Get precision@k, recall@k, MRR for batch results | 4 |
| **Phase 5 — End-User Inquiry** | | | |
| `GET` | `/api/v5/status` | Phase 5 backend health check | 5 |
| `POST` | `/api/v5/query` | Submit natural language query — production endpoint | 5 |
| `GET` | `/api/v5/assets` | List/filter assets for browsing | 5 |
| `POST` | `/api/v5/ingest` | Upload document and trigger ingestion | 5 |
| `GET` | `/api/v5/ontology/classes` | Get ontology class tree for UI facets | 5 |

#### G10.4.3 404 Catch-All for Unknown API Paths

Any `/api/*` path that does not match a registered `/api/v{N}/` prefix returns:

```json
HTTP 404
{"error": "Unknown API path: /api/documents"}
```

This prevents un-versioned legacy paths from silently reaching the wrong backend.

#### G10.4.4 Migration Note — Phase 1.2 Endpoint Prefixes

The current `phase1_server.py` exposes endpoints without version prefixes (e.g. `/api/documents`, `/api/pipeline/start`). These must be migrated to `/api/v1/` before Phase 5 is built and before the 404 catch-all is enforced strictly. Until migration, `server.py` may carry a temporary alias forwarding `/api/pipeline/*` and `/api/documents/*` to port 5001, documented explicitly as a migration shim.

---

### G10.5 Phase Server Convention

Every phase backend server (1 through 5) follows these rules:

1. **Location**: `eks/ui/backend/phase{N}_server.py`
2. **Port**: `5000 + N` — `phase1_server.py` → 5001, `phase2_server.py` → 5002, `phase3_server.py` → 5003, `phase4_server.py` → 5004, `phase5_server.py` → 5005
3. **Standalone runnable**: Each server accepts `--port` and runs independently without the main launcher. This is the primary way to develop and test a phase — start only that phase's server, open its HTML dashboard, call its endpoints directly
4. **Phase scope**: Each server exposes endpoints for its own phase only. Cross-phase data access (e.g. Phase 2 reads from Phase 1's DuckDB registry) is done via direct Python import, not via inter-server HTTP calls
5. **No tool-picker responsibility**: Phase servers expose API only. The HTML tool-picker is exclusively the main server's role
6. **Direct engine imports** (Phases 1–4): Phase servers import EKS engine modules directly (`from eks.engine.core import ...`). This differs from DCC, where the pipeline runs as a subprocess. EKS uses direct imports because:
   - The engine is a Python package enabling structured exception handling
   - `_LogCapture` intercepts `EKSLogger` calls at method level — richer than stdout parsing
   - In-process `TelemetryHeartbeat` provides granular progress without stdout keyword matching
   - DuckDB registry access is shared safely via `threading.RLock` within the same process
7. **Phase 5 exception** (FastAPI): Phase 5 uses FastAPI + uvicorn, not `http.server`. Start via `uvicorn eks.ui.backend.phase5_server:app --port 5005`. The main server's urllib-based proxy works identically against a uvicorn server
8. **CORS on all responses**: Every response must include `Access-Control-Allow-Origin: *`
9. **Concurrent-run guard** (pipeline endpoints): Return HTTP 409 if a job is already `running`. One pipeline execution per phase server at a time
10. **Health endpoint required**: Every phase server must implement `GET /api/v{N}/status` returning `{"status": "healthy", "version": "...", "phase": N, "timestamp": "..."}` as the first handled route

---

### G10.6 Port Allocation

| Port | Server | Stack | Phase | Status | Purpose |
| :--- | :----- | :---- | :---- | :----- | :------ |
| 5000 | `eks/server.py` | `http.server` stdlib | All | ✅ Built | Main launcher — always running; browser entry point |
| 5001 | `eks/ui/backend/phase1_server.py` | `http.server` stdlib | 1 | ✅ Built | Document ingestion, parsing, health scoring, registry CRUD, manual review |
| 5002 | `eks/ui/backend/phase2_server.py` | `http.server` stdlib | 2 | 🔷 Planned | Chunking pipeline, embedding pipeline, vector store inspection |
| 5003 | `eks/ui/backend/phase3_server.py` | `http.server` stdlib | 3 | 🔷 Planned | Asset graph loading, Neo4j node/relationship inspection, ontology management |
| 5004 | `eks/ui/backend/phase4_server.py` | `http.server` stdlib | 4 | 🔷 Planned | Retrieval pipeline testing, query stage tracing, batch evaluation |
| 5005 | `eks/ui/backend/phase5_server.py` | FastAPI + uvicorn | 5 | 🔷 Planned | Production end-user inquiry interface, retrieval cache |

---

### G10.7 Server Implementation Rules

These rules apply to `eks/server.py` and all `http.server`-based phase backend servers. They implement the AGENTS.md §18.12–18.13 standard.

| Rule | Requirement |
| :--- | :---------- |
| **TCP server class** | Subclass `socketserver.TCPServer` as `ReusableTCPServer` with `allow_reuse_address = True` and `daemon_threads = True` |
| **Connection reset handling** | Override `handle_error` to suppress `ConnectionResetError` (DEBUG log only, no traceback) |
| **Cache busting** | Override `end_headers()` to inject `Cache-Control: no-cache, no-store, must-revalidate` + `Pragma: no-cache` + `Expires: 0` on every response |
| **Log filtering** | Override `log_message` to suppress 200 and 304. Only print non-success codes |
| **CORS preflight** | `do_OPTIONS` returns HTTP 204 with `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`, `Access-Control-Allow-Headers: Content-Type` |
| **CORS on API responses** | All JSON responses include `Access-Control-Allow-Origin: *` |
| **Port argument** | `--port` via `argparse` with default. All startup code inside `if __name__ == "__main__"` |
| **Port probe** | Before binding, check port availability with `socket.connect_ex`. If occupied, auto-increment up to 10 times and print the resolved port |
| **URL decode** | All path matching uses `urllib.parse.unquote(self.path).split("?")[0]` |
| **Static file root** | `ROOT = Path(__file__).parent.resolve()` resolved absolutely at import time |
| **Path security** | Every static file path must pass `Path(resolved_path).is_relative_to(ROOT)` before serving. Return 403 if outside ROOT |
| **Proxy error handling** | Catch `urllib.error.HTTPError`, `urllib.error.URLError` (503 + friendly message naming the backend), `Exception` (500 + JSON). Never raw traceback |
| **Backend not reachable** | If proxy gets connection refused: return HTTP 503 `{"error": "Phase N backend not running on port 500N. Start: python eks/ui/backend/phaseN_server.py"}` |
| **Ollama proxy** | `_proxy_ollama()` strips `/ollama`, forwards to `localhost:11434`. Timeout: 30s. If unreachable: 503 `{"error": "Ollama not running on port 11434"}` |
| **Health endpoint** | Every phase server exposes `GET /api/v{N}/status` as its first handled route |
| **Dependency check** | Phase servers catch `ImportError` / `ModuleNotFoundError` at startup and print actionable install instructions instead of a raw traceback |

---

### G10.8 Adding a New Phase UI — Checklist

When a phase is ready for its UI (e.g. Phase 2 Embedding Monitor, Phase 3 Graph Explorer):

1. **Create the HTML file** in `eks/ui/` (e.g. `eks/ui/phase2_embedding.html`). It is automatically discovered by `_build_index()` and appears in the tool launcher with no changes to `server.py`
2. **Create the backend server** at `eks/ui/backend/phase{N}_server.py` following G10.5 and AGENTS.md §18.13. Start with `GET /api/v{N}/status` and add endpoints as phase engines are built
3. **Add the proxy rule** in `server.py`: `GET/POST/PUT/DELETE /api/v{N}/*` → `localhost:500{N}`. This is the only change `server.py` requires
4. **Update G10.4.1** prefix table — mark status ✅ Built
5. **Update G10.6** port allocation table — mark status ✅ Built
6. **Add endpoints** to the G10.4.2 endpoint table under the new phase section
7. **Add integration tests** in `eks/test/test_phase{N}_server.py` covering all endpoints including the health check
8. **Update `ui_help.json`** with help text for the new dashboard

**No changes to `_build_index()` or `SCAN_DIRS`** are needed when adding HTML files to `eks/ui/`.

**Phase-by-phase build order** — each phase backend is built and tested in sequence:

| Build order | Phase | HTML dashboard | Backend server | API prefix | Builds on |
| :---------- | :---- | :------------- | :------------- | :--------- | :-------- |
| 1 | Phase 1.2 | `index.html` ✅ | `phase1_server.py` ✅ | `/api/v1/` | — |
| 2 | Phase 2 | `phase2_embedding.html` 🔷 | `phase2_server.py` 🔷 | `/api/v2/` | Phase 1 registry + parsers |
| 3 | Phase 3 | `phase3_graph.html` 🔷 | `phase3_server.py` 🔷 | `/api/v3/` | Phase 2 chunk registry + vectors |
| 4 | Phase 4 | `phase4_retrieval.html` 🔷 | `phase4_server.py` 🔷 | `/api/v4/` | Phase 3 knowledge graph |
| 5 | Phase 5 | `phase5_inquiry.html` 🔷 | `phase5_server.py` 🔷 | `/api/v5/` | Phase 4 retrieval pipeline |

---

### G10.9 Restricted Corporate Computer — Design Constraints

EKS is designed to run on company computers that may have the following restrictions. All server and UI design decisions must account for these constraints.

#### G10.9.1 Network Restrictions

| Constraint | Impact | Mitigation |
| :--------- | :----- | :--------- |
| Corporate firewall may block ports 5000–5005 | Phase servers fail to bind or are unreachable from browser | Use port-probe auto-increment (G10.7); expose `--port` on every server; document alternative ports |
| Corporate proxy intercepts all outbound HTTPS | Google Fonts CDN blocked or certificate error | **Never use CDN fonts** in `serve.py` index page or `eks.css`. Use `system-ui` font stack only (AGENTS.md §18.1) |
| `fonts.googleapis.com` blocked | `@import` in CSS hangs the page for 20–30s | Remove all CDN `@import` from shared CSS. If Inter is desired, self-host the font files under `eks/ui/fonts/` |
| Ollama not installed or port 11434 blocked | `/ollama/*` proxy returns 503 | Phase backends and HTML pages must handle 503 from the Ollama proxy gracefully — degrade to "AI features unavailable" rather than crashing |
| Internet access blocked entirely | CDN Chart.js, CDN fonts fail | Self-host Chart.js under `eks/ui/static/chart.min.js`; reference via `/ui/static/chart.min.js` |

#### G10.9.2 Environment and Installation Restrictions

| Constraint | Impact | Mitigation |
| :--------- | :----- | :--------- |
| No admin rights — cannot install conda or pip globally | Phase backends that require `duckdb`, `pymupdf` etc. may not be installable | The HTTP launcher (`server.py`) uses stdlib only and runs without any install. Phase backends require the `eks` conda env; document this clearly and handle `ImportError` gracefully at startup |
| `conda create` blocked — no access to conda channels | Full `eks.yml` environment cannot be built | Document a minimal pip-based fallback: `pip install duckdb pymupdf python-docx openpyxl jsonschema referencing` for Phase 1 only |
| Python version restrictions (company standard may be 3.9 or 3.10) | EKS engine requires Python 3.11; f-string backslash syntax requires 3.12+ (code_tracer CT-16) | Pin Python to 3.11 minimum in `eks.yml`. Never use backslashes inside f-string expressions. Test on 3.10 for the HTTP layer only |
| pip download blocked without corporate proxy config | `pip install` fails silently | Document proxy setup: `pip install --proxy http://proxy:port <pkg>` |

#### G10.9.3 Port Availability

Default port assignments assume all of 5000–5005 are available. If any port is blocked or occupied:

1. The phase server's `--port` argument overrides the default
2. `server.py` auto-probes ports (G10.7 port-probe rule) and displays the actual port used
3. The tool launcher index page (`_build_index()`) shows the actual server port in the status bar
4. If `phase{N}_server.py` starts on a non-default port, the corresponding `server.py` proxy rule must be updated manually or via `--phase{N}-port` argument

Recommended `server.py` argparse additions for corporate environments:
```python
parser.add_argument("--phase1-port", type=int, default=5001)
parser.add_argument("--phase2-port", type=int, default=5002)
parser.add_argument("--phase3-port", type=int, default=5003)
parser.add_argument("--phase4-port", type=int, default=5004)
parser.add_argument("--phase5-port", type=int, default=5005)
```

#### G10.9.4 Static Asset Self-Hosting

To ensure full offline/restricted-network operation, all external assets must be self-hosted under `eks/ui/static/`:

| Asset | CDN URL (do not use) | Self-hosted path |
| :---- | :------------------- | :--------------- |
| Chart.js | `https://cdn.jsdelivr.net/npm/chart.js` | `eks/ui/static/chart.min.js` |
| Inter font | `https://fonts.googleapis.com/css2?family=Inter` | Remove — use `system-ui` instead |
| JetBrains Mono | `https://fonts.googleapis.com/css2?family=JetBrains+Mono` | `eks/ui/static/fonts/JetBrainsMono.woff2` (optional) |

HTML files reference self-hosted assets using root-relative paths: `<script src="/ui/static/chart.min.js">`.

#### G10.9.5 DuckDB Cross-Process Locking

When multiple phase servers (1–5) run simultaneously and all open `output/eks_registry.db`:

- **Phase 1** is the only write-heavy phase (registering, updating documents)
- **Phases 2–4** are primarily read-only consumers of the registry
- **Phase 5** may write query result caches

Rules:
1. All phases that open DuckDB must use `_with_retry(fn, retries=3, delay=0.5)` on every operation
2. Phases 2–4 should open the registry in read-only mode where possible: `duckdb.connect(str(db_path), read_only=True)`
3. If a phase server gets a DuckDB lock error after retries, return HTTP 503 `{"error": "Registry locked by another process. Retry in a few seconds."}` rather than crashing

#### G10.9.6 Known Issues (from code_tracer and EKS logs)

The following issues from code_tracer and EKS issue logs directly affect the EKS server and UI design. They are tracked here until resolved.

| Issue ID | Source | Severity | Description | Resolution |
| :------- | :----- | :------: | :---------- | :--------- |
| I047 | EKS | 🟠 High | `eks/server.py` routes `GET /` to static `index.html` — `_build_index()` dynamic tool-picker not yet wired | Implement `_build_index()` in `server.py`; route `GET /` to it |
| I048 | EKS | 🟠 High | Phase 1 endpoints lack `/api/v1/` prefix — 404 catch-all cannot be enforced without breaking Phase 1 UI | Migrate all Phase 1 endpoints to `/api/v1/`; update `eks.js` and `index.html` |
| I049 | CT-14 | 🟠 High | No port availability check in any EKS server — `OSError: address already in use` on occupied ports | Add `find_free_port()` / port-probe logic to `server.py` and all phase servers |
| I050 | CT-16 | 🟡 Medium | Google Fonts CDN `@import` in `eks.css` hangs render on blocked corporate networks | Replace with `system-ui` font stack; self-host Chart.js under `eks/ui/static/` |
| I051 | CT-01/02 | 🟡 Medium | No backend readiness check — if conda env not activated, phase server crashes with raw `ModuleNotFoundError` | Wrap engine imports in `try/except ImportError`; print actionable install message |
| I052 | CT-03/05 | 🟡 Medium | Windows path normalization untested — proxy URL construction and static file security check may fail on Windows `\` paths | Use `Path.as_posix()` for URL construction; `Path.is_relative_to()` for security check |
| I053 | I006 | 🟡 Medium | No guidance on DuckDB cross-process locking when Phases 2–5 servers run alongside Phase 1 | Apply `_with_retry()`; document read-only mode for Phases 2–4 (see G10.9.5) |
| I054 | CT R7 | 🟢 Low | No restricted-machine deployment guide or minimal install path equivalent to code_tracer `download_release.py` | Create deployment checklist; document minimal pip fallback for Phase 1 only |

---

**End of Appendix G**
