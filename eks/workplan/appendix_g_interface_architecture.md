# Appendix G — Interface Architecture

**Version**: 0.1  
**Last Updated**: 2026-06-30  
**Phase**: 1.2 — Interactive UI, I/O Contracts & Document Processing  
**Status**: 📋 Proposed  
**Related Documents**:
- [`AGENTS.md §18`](../../AGENTS.md) — UI Web Design (layout structure, theme toggle, layout switching)
- [`appendix_f_pipeline_architecture_design.md`](appendix_f_pipeline_architecture_design.md) — Engine I/O contracts (EngineInput/EngineOutput, BaseEngine)
- [`phase_1.2_interactive_ui_workplan.md`](phase_1.2_interactive_ui_workplan.md) — Phase 1.2 workplan referencing this appendix
- [`phase_5_ui_integration_workplan.md`](phase_5_ui_integration_workplan.md) — Phase 5 workplan referencing this appendix

### Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------ |
| 0.1 | 2026-06-30 | opencode | Initial draft: G1–G8 covering UI architecture conventions, API patterns, theme system, help system, and cross-phase references |
| 0.2 | 2026-07-01 | opencode | Added G10 Server Architecture (two-server pattern, port allocation, proxy routing). Updated G3.1 (proxy note), G3.4 (two-server flow), G9 (G10 reference). Per Phase 1.2 server design review. |

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

---

## G2. Technology Stack Guidelines

EKS has two distinct UI use cases that justify different technology stacks:

### G2.1 Document Processing Dashboard (Phase 1.2)

| Layer | Technology | Rationale |
| :---- | :--------- | :-------- |
| Backend | `http.server` (Python stdlib) | Zero dependencies, sufficient for back-office dashboard |
| Frontend | Vanilla JavaScript + HTML5 + CSS3 | No build step, opens directly in browser |
| Charts | Chart.js 4+ (CDN) | Lightweight, works without build |
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
| `POST` | `/api/pipeline/start` | Start async pipeline execution | 1.2 |
| `GET` | `/api/pipeline/status/{job_id}` | Poll pipeline progress | 1.2, 5 |
| `DELETE` | `/api/pipeline/{job_id}` | Cancel running pipeline | 1.2, 5 |
| `GET` | `/api/pipeline/logs/{job_id}` | Stream pipeline logs | 1.2, 5 |
| `GET` | `/api/documents` | List documents with pagination/filters | 1.2, 5 |
| `GET` | `/api/documents/{id}` | Get document detail | 1.2, 5 |
| `PUT` | `/api/documents/{id}` | Update document metadata | 1.2, 5 |
| `POST` | `/api/files/load` | Trigger file discovery scan | 1.2 |
| `GET` | `/api/query` | Submit natural language query | 5 |
| `GET` | `/api/assets` | List/filter assets | 5 |
| `GET` | `/api/ontology/classes` | Get ontology class tree | 5 |

All `/api/*` requests arrive at the main server (`eks/server.py`, port 5000) and are **proxied** to the appropriate phase backend server (port 5001 for Phase 1, port 5005 for Phase 5). See [G10](#g10-server-architecture).

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
| Theme | `eks_theme` | `"dark"` |
| Layout | `eks_layout` | `"two-columns"` |

### G5.3 CSS Variables Pattern

```css
:root {
  --bg-primary: #1e1e1e;
  --text-primary: #d4d4d4;
  --accent: #3794ff;
  --sidebar-bg: #252526;
  --status-bar-bg: #007acc;
}
[data-theme="light"] { ... }
[data-theme="sky"] { ... }
```

All theme applications must use CSS custom properties on `:root` with `[data-theme="..."]` overrides to enable seamless switching without reload.

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
| Layout structure, theme toggle, layout switching | AGENTS.md §18 |
| Engine I/O contracts (EngineInput/EngineOutput, BaseEngine, CLI) | Appendix F §2.3 |
| Theme colors, CSS variable pattern, help schema | **Appendix G §5–§6** |
| API endpoint conventions, polling pattern | **Appendix G §3–§4** |
| UI contract ownership and validation | **Appendix G §7** |
| Status bar format | **Appendix G §8** |
| Phase-specific UI implementation | Phase workplan (1.2 or 5) |
| Server architecture (port allocation, proxy routing) | **Appendix G §10** |

---

## G10. Server Architecture

### G10.1 Overview

EKS uses a two-server architecture: a main launcher server at the project root, and phase-specific backend servers in `eks/ui/backend/`.

| Server | Location | Default Port | Responsibility |
| :----- | :------- | :----------- | :------------- |
| Main launcher | `eks/server.py` | 5000 | File picker, proxy routing, static files |
| Phase 1 backend | `eks/ui/backend/phase1_server.py` | 5001 | Dashboard API, pipeline execution, document CRUD |
| Phase 5 backend | `eks/ui/backend/phase5_server.py` | 5005 | (Future) End-user inquiry, FastAPI, query |

### G10.2 Request Flow

```
Browser ── GET / ───────────────────────→ eks/server.py (port 5000)
  │                                          │
  │  Receives HTML file picker               │
  │  (VS Code style, lists tools in eks/ui/) │
  │                                          │
  ├─→ /api/files/load ──proxy──→ localhost:5001 ──→ phase1_server.py
  ├─→ /api/documents/*   proxy──→ localhost:5001 ──→ phase1_server.py
  ├─→ /api/pipeline/*    proxy──→ localhost:5001 ──→ phase1_server.py
  ├─→ /ollama/*          proxy──→ localhost:11434
  └─→ /static/*          serve──→ eks/ui/static/
```

### G10.3 Proxy Routing Convention

The main server (`eks/server.py`) proxies `/api/*` to the Phase 1 backend by default. When additional phase servers are added, routing extends with a prefix convention:

| Path Prefix | Target | Phase |
| :---------- | :----- | :---- |
| `/api/v1/*` | `localhost:5001` | Phase 1 (current) |
| `/api/v5/*` | `localhost:5005` | Phase 5 (future) |
| `/api/*` | `localhost:5001` | Default fallback |

### G10.4 Phase Server Convention

All phase servers follow these rules:

1. **Location**: `eks/ui/backend/phase{N}_server.py`
2. **Port**: `5000 + N` (Phase 1 → 5001, Phase 5 → 5005)
3. **Runnable standalone**: Each phase server accepts `--port` and can run independently for testing
4. **No file picker**: Phase servers serve their own UI but do NOT generate the tool picker HTML (that is the main server's role)
5. **Direct imports**: Phase servers import engine modules directly (no subprocess)

### G10.5 Port Allocation

| Port | Server | Notes |
| :--- | :----- | :---- |
| 5000 | `eks/server.py` | Main launcher — always runs |
| 5001 | `eks/ui/backend/phase1_server.py` | Phase 1.2 dashboard backend |
| 5005 | `eks/ui/backend/phase5_server.py` | Phase 5 inquiry backend (future) |

---

**End of Appendix G**
