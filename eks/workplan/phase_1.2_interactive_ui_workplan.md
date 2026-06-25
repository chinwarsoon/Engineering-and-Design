# EKS Phase 1.2 — Interactive UI & Document Processing Sub-Pipeline

**Document ID**: WP-EKS-P1.2-001  
**Current Version**: 1.0  
**Status**: 📋 Proposed for Review  
**Last Updated**: 2026-06-25  
**Parent Workplan**: [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md)  
**Phase Dependency**: Phase 1 (Foundation) — COMPLETE  

---

## Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------- |
| 1.0 | 2026-06-25 | opencode | Initial workplan proposal for interactive UI and sub-pipeline |

---

## Object

Create a standalone interactive UI (HTML/CSS/JavaScript) with a document processing sub-pipeline that leverages the Phase 1 foundation module to process real engineering documents from the `data/` folder. The UI follows AGENTS.md §18 VS Code-style design specifications.

---

## Scope Summary

| ID | Details | Category | Status |
| :- | :------ | :------- | :-----: |
| S1.2.1 | Interactive standalone HTML/CSS UI (VS Code style) | UI Development | Pending |
| S1.2.2 | Document processing sub-pipeline orchestration | Pipeline | Pending |
| S1.2.3 | Real document ingestion from data/ folder | Data Ingestion | Pending |
| S1.2.4 | Manual review workflow integration | Workflow | Pending |
| S1.2.5 | Health scoring visualization | Visualization | Pending |
| S1.2.6 | Schema-driven help system (ui_help.json) | Documentation | Pending |

**Related Phase**: Phase 1.2 — Interactive UI & Document Processing

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
┌────────────────────────────┴────────────────────────────────────┐
│              Python Backend (eks/ui/backend/)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Simple HTTP  │  │ Pipeline     │  │ Document     │          │
│  │ Server       │  │ Orchestrator │  │ Registry API │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
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

1. **User loads files** → UI File Loading Panel → JavaScript → Backend HTTP Server → FileScanner
2. **FileScanner discovers files** → ParserRouter → Parsers
3. **Parsers extract content** → StructureDetector → HealthScorer
4. **HealthScorer computes scores** → DocumentRegistry → DuckDB
5. **UI polls for status** → JavaScript fetch → Backend → Registry → JSON response
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

| Theme | Background | Text | Accent |
| :---- | :--------- | :--- | :----- |
| Light | #ffffff | #000000 | #007acc |
| Dark | #1e1e1e | #d4d4d4 | #3794ff |
| Sky | #e0f7fa | #000000 | #00bcd4 |
| Ocean | #e3f2fd | #000000 | #2196f3 |
| Presentation | #f5f5f5 | #333333 | #666666 |

- Theme selection saved in `localStorage`
- Default theme: Dark

### Layout Switching

- **Single Column**: Main panel only (sidebars hidden)
- **Two Columns**: Left sidebar + Main panel
- **Three Columns**: Left sidebar + Main panel + Right sidebar
- Layout selection saved in `localStorage`
- Default layout: Two columns

### Help System

- **ui_help.json** structure:
  ```json
  {
    "about": "EKS Document Processing System v1.0",
    "help": {
      "file_load": "Load documents from local disk or pipeline folder",
      "tree_view": "Navigate document hierarchy",
      "health_score": "6-dimension document quality assessment"
    },
    "default_folders": {
      "data": "eks/data/",
      "output": "eks/output/"
    },
    "definitions": {
      "document": "Engineering document with metadata and revisions",
      "health_score": "Quality score from 0.0 to 1.0"
    }
  }
  ```

---

## Technology Stack

### Frontend (UI)

| Component | Technology | Rationale |
| :-------- | :--------- | :-------- |
| Structure | HTML5 | Semantic markup, native browser support |
| Styling | CSS3 | Independent CSS file per AGENTS.md §18 |
| Logic | Vanilla JavaScript | No framework dependency, lightweight |
| HTTP Client | Fetch API | Native browser API, no external dependencies |
| Charts | Chart.js (CDN) | Simple, lightweight, works without build |
| Icons | Unicode | No external icon library needed |
| State | localStorage | Native browser storage for theme/layout |

### Backend (Simple HTTP Server)

| Component | Technology | Rationale |
| :-------- | :--------- | :-------- |
| Framework | http.server (Python stdlib) | No external dependency, simple |
| JSON API | Manual JSON serialization | Lightweight, no framework needed |
| CORS | Manual CORS headers | Simple implementation |
| Background Tasks | threading | Run pipeline in background thread |

### Integration

| Component | Technology | Rationale |
| :-------- | :--------- | :-------- |
| Phase 1 Engine | Direct import | Reuse existing `eks.engine.*` modules |
| Schema Loader | Direct import | Reuse existing `schema_loader.py` |
| Config Registry | Direct import | Reuse existing `config_registry.py` |

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

### 2. Pipeline Execution

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

### 3. Status Polling

```
UI Action: Poll every 2 seconds
    ↓
GET /api/pipeline/status/{job_id}
    ↓
Return: JSON with progress (current/total), current stage, errors
    ↓
UI: Update progress bar and log viewer
```

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

### Phase 1.2.1: Backend HTTP Server (Week 1)

**Timeline**: 5 days  
**Milestones**: Simple HTTP server with Phase 1 integration

**Tasks**:
- T1.2.1.1: Create `eks/ui/backend/` package structure
- T1.2.1.2: Implement simple HTTP server using `http.server`
- T1.2.1.3: Integrate Phase 1 engine modules (import paths)
- T1.2.1.4: Implement file discovery endpoint (`POST /api/files/load`)
- T1.2.1.5: Implement document list endpoint (`GET /api/documents`)
- T1.2.1.6: Implement document detail endpoint (`GET /api/documents/{id}`)
- T1.2.1.7: Add CORS headers for cross-origin requests
- T1.2.1.8: Write backend tests

**Deliverables**:
- HTTP server at `eks/ui/backend/server.py`
- API endpoints for document CRUD operations
- Integration tests passing

**Risks**:
- Phase 1 sync calls may block HTTP server
- DuckDB concurrent access

**Mitigation**:
- Run pipeline in background thread
- Use DuckDB connection singleton

---

### Phase 1.2.2: Pipeline Orchestration (Week 2)

**Timeline**: 5 days  
**Milestones**: Pipeline execution with status tracking

**Tasks**:
- T1.2.2.1: Implement pipeline start endpoint (`POST /api/pipeline/start`)
- T1.2.2.2: Implement pipeline status endpoint (`GET /api/pipeline/status/{job_id}`)
- T1.2.2.3: Implement pipeline cancellation endpoint (`DELETE /api/pipeline/{job_id}`)
- T1.2.2.4: Create in-memory job tracking system
- T1.2.2.5: Integrate PipelineOrchestrator from Phase 1
- T1.2.2.6: Add error handling and logging
- T1.2.2.7: Implement log streaming endpoint
- T1.2.2.8: Write pipeline API tests

**Deliverables**:
- Pipeline execution endpoints
- Job tracking system
- Log streaming

**Risks**:
- Long-running pipeline blocks server
- Job state persistence

**Mitigation**:
- Use threading for background execution
- Simple file-based job persistence

---

### Phase 1.2.3: HTML/CSS Foundation (Week 3)

**Timeline**: 5 days  
**Milestones**: VS Code-style layout with theme system

**Tasks**:
- T1.2.3.1: Create `eks/ui/` folder structure
- T1.2.3.2: Create `index.html` with VS Code layout structure
- T1.2.3.3: Create `eks.css` with independent styles per AGENTS.md §18
- T1.2.3.4: Implement title bar (theme, layout, menu, search)
- T1.2.3.5: Implement side icon bars (left and right)
- T1.2.3.6: Implement left sidebar (file load, tree view)
- T1.2.3.7: Implement right sidebar (health score, details)
- T1.2.3.8: Implement bottom status bar
- T1.2.3.9: Implement theme system (5 themes)
- T1.2.3.10: Implement layout switching (1-3 columns)
- T1.2.3.11: Add localStorage persistence for theme/layout
- T1.2.3.12: Test in multiple browsers

**Deliverables**:
- `eks/ui/index.html`
- `eks/ui/eks.css`
- VS Code-style layout working

**Risks**:
- CSS complexity for resizable sidebars
- Browser compatibility

**Mitigation**:
- Use CSS Grid/Flexbox for layout
- Test on Chrome, Firefox, Edge

---

### Phase 1.2.4: JavaScript Integration (Week 4)

**Timeline**: 5 days  
**Milestones**: JavaScript logic for API communication

**Tasks**:
- T1.2.4.1: Create `eks/ui/eks.js` with API client functions
- T1.2.4.2: Implement file loading logic (drag-drop, file input)
- T1.2.4.3: Implement document list fetching and rendering
- T1.2.4.4: Implement document detail fetching and rendering
- T1.2.4.5: Implement pipeline status polling
- T1.2.4.6: Implement manual review form submission
- T1.2.4.7: Add error handling and user feedback
- T1.2.4.8: Implement loading states

**Deliverables**:
- `eks/ui/eks.js` with full API integration
- Working document list and detail views

**Risks**:
- Fetch API complexity
- Error handling edge cases

**Mitigation**:
- Use async/await pattern
- Add try-catch blocks with user-friendly messages

---

### Phase 1.2.5: Health Score Visualization (Week 5)

**Timeline**: 5 days  
**Milestones**: Health score charts and breakdown

**Tasks**:
- T1.2.5.1: Integrate Chart.js via CDN
- T1.2.5.2: Implement health score distribution chart
- T1.2.5.3: Implement 6-dimension breakdown visualization
- T1.2.5.4: Add dimension-specific recommendations
- T1.2.5.5: Implement health score color coding (red/yellow/green)
- T1.2.5.6: Add drill-down to dimension details
- T1.2.5.7: Test with sample health score data

**Deliverables**:
- Health score charts working
- Dimension breakdown display

**Risks**:
- Chart.js learning curve
- Chart responsiveness

**Mitigation**:
- Use simple chart examples
- Add responsive CSS

---

### Phase 1.2.6: Help System (Week 6)

**Timeline**: 5 days  
**Milestones**: Schema-driven help system

**Tasks**:
- T1.2.6.1: Create `eks/ui/ui_help.json` schema
- T1.2.6.2: Populate ui_help.json with help text
- T1.2.6.3: Implement help modal/dialog
- T1.2.6.4: Load help text from ui_help.json
- T1.2.6.5: Implement about section
- T1.2.6.6: Implement definitions section
- T1.2.6.7: Add keyboard shortcuts (F1 for help)
- T1.2.6.8: Test help system

**Deliverables**:
- `eks/ui/ui_help.json`
- Working help system

**Risks**:
- JSON schema complexity
- Help text completeness

**Mitigation**:
- Start with simple JSON structure
- Incrementally add help content

---

### Phase 1.2.7: Integration and Testing (Week 7)

**Timeline**: 5 days  
**Milestones**: End-to-end testing with real documents

**Tasks**:
- T1.2.7.1: Deploy sample documents to `data/twrp/`
- T1.2.7.2: Run end-to-end pipeline tests
- T1.2.7.3: Test manual review workflow
- T1.2.7.4: Performance testing (large document sets)
- T1.2.7.5: Browser compatibility testing
- T1.2.7.6: Fix bugs and refine UI
- T1.2.7.7: Write user documentation
- T1.2.7.8: Create deployment guide

**Deliverables**:
- Tested end-to-end system
- User documentation
- Deployment guide

**Risks**:
- Real documents expose edge cases
- Performance issues

**Mitigation**:
- Start with small document subset
- Add caching as needed

---

## Dependencies

### Phase 1 Foundation (COMPLETE)

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
| Python stdlib | 3.13+ | http.server, threading, json |
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

## References

### Phase 1 Documents

- [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) — Foundation module specification
- [phase_1_foundation_report.md](reports/phase_1_foundation_report.md) — Phase 1 test report
- [appendix_e_schema_design.md](appendix_e_schema_design.md) — Schema design documentation

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
2. **Phase 1.2.1 Start**: Begin backend HTTP server implementation
3. **Weekly Check-ins**: Progress review at end of each phase
4. **UAT**: User acceptance testing after Phase 1.2.7
5. **Deployment**: Deploy to staging environment for pilot use

---

**End of Workplan**
