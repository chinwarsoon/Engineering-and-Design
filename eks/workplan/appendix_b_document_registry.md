# Appendix B — Document Registry

**Version**: 0.9  
**Last Updated**: 2026-06-22  
**Phase**: 1 — Foundation  
**Status**: ✅ Implemented & Tested  
**Related Files**:
- [`eks/engine/core/registry.py`](../engine/core/registry.py)
- [`eks/engine/core/revision.py`](../engine/core/revision.py)
- [`eks/engine/core/config_registry.py`](../engine/core/config_registry.py)
- [`eks/config/schemas/eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) — Document column definitions
- [`eks/config/schemas/eks_doc_setup_schema.json`](../config/schemas/eks_doc_setup_schema.json) — Table declarations, extraction rules, health scoring
- [`eks/config/schemas/eks_doc_config.json`](../config/schemas/eks_doc_config.json) — Element expectations, score tiers

### Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------ |
| 0.1 | 2026-06-16 | Gemini CLI | Initial draft: B1–B4 (Overview, Architecture, Schema, Functions) |
| 0.2 | 2026-06-16 | Gemini CLI | Added B5 (Extraction & Verification Workflow), B6 (References) |
| 0.3 | 2026-06-16 | Gemini CLI | Added extended metadata fields (T1.22), renumbered B5→B5, B6→B6 |
| 0.4 | 2026-06-16 | Gemini CLI | Added B7 (Establishment Summary) with TWRP data assets and workflow |
| 0.5 | 2026-06-16 | Gemini CLI | Added TWRP ingestion next steps table (B7.3) |
| 0.6 | 2026-06-18 | opencode | Added B3.1 Ontology Mapping (Knowledge Graph Triggers); updated version/date |
| 0.7 | 2026-06-19 | opencode | Renumbered B7→B6, B8→B7 for sequential ordering; updated DB path from `data/eks_registry.db` to `output/eks_registry.db` |
| 0.8 | 2026-06-22 | opencode | Updated schema references to new dedicated doc schema files (`eks_doc_base_schema.json`, `eks_doc_setup_schema.json`, `eks_doc_config.json`) per T1.34. |
| 0.9 | 2026-06-22 | opencode | Added B3.2 Document Type Registry, B3.3 File Type Registry, B3.4 Element Type Registry per T1.35; added `file_type` column to B3 table. |

---

## B1. Overview

The Document Registry is the central metadata store for all engineering documents ingested into EKS. It is backed by DuckDB (configurable to PostgreSQL) and managed through the `DocumentRegistry` class in `engine/core/registry.py`. It records every document revision that enters the system, tracks which revision is current (`is_latest`), and provides filtered query access for the retrieval pipeline.

The registry is config-driven — the DB path and backend type are read from `eks_config.json` at startup via `ConfigRegistry`. No hardcoded paths or connection strings exist in the implementation.

**General Business Logic**
- Document will be organized per project, area, discipline, type, sequence number, and revision.
- Different documents can have different file formats, such as doc, pdf, pptx, xlx, dwg, dgn, etc.
- Different documents can have different metadata.
- Different documents can have different elements, such as coversheet, index of content, sections, table, figure, sections, appendix, references, etc.
- Same asset tags can be associated to different documents.
- Relationship between documents can be defined.

---

## B2. Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   DocumentRegistry                        │
│                  (registry.py)                           │
│                                                          │
│  COLUMN_ALLOWLIST = {...}                                │
│                                                          │
│  __init__(logger)                                        │
│    └─ ConfigRegistry() ──► eks_config.json               │
│    └─ _init_db() ──► CREATE TABLE IF NOT EXISTS docs     │
│    └─ _migrate_schema() ──► ALTER TABLE (G1 + Ext Meta)  │
│                                                          │
│  register_document(metadata) ──► doc_id                  │
│    └─ UPDATE is_latest = FALSE                           │
│    └─ json.dumps(asset_tags) if list                     │
│    └─ INSERT OR REPLACE                                  │
│                                                          │
│  get_document(doc_number, revision=None) ──► dict|None   │
│                                                          │
│  list_documents(filters, latest_only, order_by) ──► list │
│    └─ COLUMN_ALLOWLIST validation for keys/order_by      │
└──────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│                   RevisionManager                         │
│                  (revision.py)                           │
│                                                          │
│  get_revision_history(document_number) ──► list[dict]    │
│    └─ list_documents(order_by="ingested_at DESC")        │
│    └─ sorted at SQL level (G3 Fix ✅)                    │
└──────────────────────────────────────────────────────────┘
```

---

## B3. Database Schema

**Table**: `documents`  
**Backend**: DuckDB (`output/eks_registry.db`) — configurable to PostgreSQL  
**Created by**: `_init_db()` on first instantiation (`CREATE TABLE IF NOT EXISTS`)  
**Schema source**: [`eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) (definitions), [`eks_doc_setup_schema.json`](../config/schemas/eks_doc_setup_schema.json) (declarations), [`eks_doc_config.json`](../config/schemas/eks_doc_config.json) (runtime values)

| Group | Column | Type | Nullable | Default | Description |
| :--- | :----- | :--- | :------: | :------ | :---------- |
| **Identity** | `id` | VARCHAR | NOT NULL | — | Primary key. Format: `{doc_num}-{rev}` |
| | `source_type` | VARCHAR | YES | 'ingested' | Source: `ingested`, `referenced`, `stub` (G1 ✅) |
| **Project** | `project_title` | VARCHAR | YES | NULL | Project full name |
| | `project_number` | VARCHAR | YES | NULL | Project code e.g. `WSD11` |
| | `area` | VARCHAR | YES | NULL | Plant area or zone |
| | `discipline` | VARCHAR | YES | NULL | Engineering discipline code (PI, EL, etc.) |
| | `department` | VARCHAR | YES | NULL | Originating department |
| **Document** | `document_type` | VARCHAR | YES | NULL | Document type code (DWG, SPC, RPT, etc.) |
| | `document_number` | VARCHAR | YES | NULL | Document identifier |
| | `revision` | VARCHAR | YES | NULL | Revision identifier (A, B, 0, 1, etc.) |
| | `status` | VARCHAR | YES | NULL | Workflow status (APPROVED, IFR, IFC, etc.) |
| | `is_latest` | BOOLEAN | YES | TRUE | TRUE for current active revision only |
| | `file_path` | VARCHAR | YES | NULL | Relative path to source file |
| | `file_type` | VARCHAR | YES | NULL | Source file format (pdf, dgn, docx, xlsx, dwg) |
| | `ingested_at` | TIMESTAMP | YES | CURRENT_TIMESTAMP | UTC timestamp of ingestion |
| **Account** | `created_by` | VARCHAR | YES | NULL | Author (Auto-extracted) |
| | `checked_by` | VARCHAR | YES | NULL | Reviewer (Auto-extracted) |
| | `approved_by` | VARCHAR | YES | NULL | Approver (Auto-extracted) |
| **Origin** | `originator_company`| VARCHAR | YES | NULL | Producing company (Auto-extracted) |
| | `security_class` | VARCHAR | YES | NULL | Security classification (Manual) |
| | **`asset_tags`** | **VARCHAR** | YES | NULL | **List of asset tags found (e.g. `["P-101", "V-202"]`). Stored as a JSON-serialized string in DuckDB VARCHAR column. Python lists are auto-serialized via `json.dumps()` on write and deserialized via `json.loads()` on read. DuckDB's native JSON type is not used to maintain PostgreSQL compatibility.** |
| **Technical** | `page_count` | INTEGER | YES | NULL | Total pages (Auto-extracted) |
| **Quality** | `extract_status` | VARCHAR | YES | 'pending' | Enum: `pending`, `success`, `partial`, `failed` |
| | `extraction_confidence`| DOUBLE | YES | NULL | Confidence score (0.0 - 1.0) |
| | `extraction_notes` | TEXT | YES | NULL | Extraction logs or failure reasons |
| | `verified_by` | VARCHAR | YES | NULL | Name of manual validator |

**Primary key**: `id` (`{document_number}-{revision}`) — guarantees one row per document+revision pair.

### B3.1. Ontology Mapping (Knowledge Graph Triggers)

The following registry fields are mapped to Ontology classes and relationships during Phase 3 ingestion:

| Registry Field | Ontology Trigger | Logic / Edge Produced |
| :--- | :--- | :--- |
| `document_type` | Class Assignment | Maps to `Drawing`, `Specification`, `Manual`, or `Report`. |
| `document_number`| `SUPERSEDES` | Links revisions of the same number in a time-ordered chain. |
| `asset_tags` | `REFERENCES_ASSET`| Produces M:N edges to `FunctionalObject` (Tag) nodes. |
| `originator_company`| `PRODUCED_BY` | Links Document to a `GovernanceObject` (Company/Entity). |
| `file_type` | `HAS_FORMAT` | Links Document to a `FileFormat` node indicating source format. |

---

### B3.2. Document Type Registry

The following document type codes are defined in `eks_doc_config.json` → `document_type_registry`. They map to ontology classes (Appendix C) and expected file formats for TWRP ingestion.

| Code | Label | Ontology Class | Description | Expected File Types |
|:---- |:----- |:-------------- |:----------- |:------------------- |
| `DWG` | Engineering Drawing | `Drawing` | Engineering design drawing | `pdf` |
| `PI-PID` | P&ID Drawing | `PID_Drawing` | Piping and instrumentation diagram | `pdf`, `dgn` |
| `SPC` | Technical Specification | `Specification` | Technical specification document | `pdf`, `docx` |
| `DS` | Data Sheet | `Specification` | Equipment/instrument data sheet | `pdf`, `xlsx` |
| `MAN` | Vendor O&M Manual | `Manual` | Vendor operation and maintenance manual | `pdf` |
| `OM` | Operation Manual | `Manual` | System operation manual | `pdf`, `docx` |
| `RPT` | Technical Report | `Report` | Technical report or study | `pdf`, `docx` |

**Alignment**:
- Ontology class hierarchy per Appendix C §C4: `Drawing` → `PID_Drawing`; `Specification` covers `SPC` and `DS`; `Manual` covers `MAN` and `OM`.
- TWRP assets per Appendix B §B6.1: 100+ PDF drawings (DWG/PI-PID), 6 DGN drawings (PI-PID), specifications, manuals, reports.
- Phase 3 extraction per Appendix B §B6.2: cover sheet parsing extracts `document_type` → ontology class assignment.

---

### B3.3. File Type Registry

Maps source file extensions to parser implementations (Phase 1 plug-in architecture per Appendix B §B4/B5) and MIME types.

| Extension | Display Name | Parser Class | TWRP Use | MIME Type |
|:--------- |:------------ |:------------ |:-------- |:--------- |
| `pdf` | PDF Document | `engine.parsers.pdf_parser.PDFParser` | Drawings (100+), Specs, Manuals, Reports | `application/pdf` |
| `dgn` | DGN Drawing | `engine.parsers.dgn_parser.DGNParserStub` | CAD Drawings (6) | `image/vnd.dgn` |
| `docx` | Word Document | `engine.parsers.docx_parser.DOCXParser` | Specs, Manuals, Reports | `application/vnd.openxmlformats...` |
| `xlsx` | Excel Workbook | `engine.parsers.xlsx_parser.XLSXParser` | Data Sheets, Datadrop | `application/vnd.openxmlformats...` |
| `dwg` | AutoCAD Drawing | `engine.parsers.dwg_parser.DWGParserStub` | Future CAD support | `image/vnd.dwg` |

**Alignment**:
- Parser plug-ins defined in `eks_config.json` → `parsers` section (Appendix B §B2).
- Phase 1 implements PDF, DOCX, XLSX; DWG/DGN are stubs for Phase 3 (Appendix B §B6.2).
- `file_type` column in registry (B3 table) stores extension for format tracking.

---

### B3.4. Element Type Registry

Structural element types per Appendix D §D7.10, used for structural completeness scoring and Phase 2/3 knowledge graph population.

| Element Type | Description | Source Method | Phase 2 Use | Phase 3 Use | Expected By Cover Type |
|:------------ |:----------- |:------------- |:----------- |:----------- |:---------------------- |
| `cover_page` | Cover page fields from page 1 | `regex` | Section anchor | Document-type node | A, B, D, E |
| `revision_table` | Revision history table from page 1 | `table` | Change tracking | Revision nodes | A, B |
| `section` | Section heading (regex `\d+\.\d+`) | `regex` | Chunk boundary | Section nodes | A, B, D, E |
| `table` | Data table on page | `heuristic` | Context chunks | Table nodes | E |
| `image` | Image/chart on page | `heuristic` | Skip | Figure nodes | A, B |
| `link` | URL or file path reference | `regex` | Skip | Reference edges | (all) |
| `legend` | Page legend/symbol key | `heuristic` | Skip | Legend nodes | A, B |
| `note` | Page 1 annotation block | `heuristic` | Skip | Annotation nodes | A, B |

**Alignment**:
- `structure_detector.py` (T1.32) detects elements and stores in `document_elements` table (Appendix B §B6.2).
- Structural completeness scoring (Appendix D §D7.3) uses `element_expectations` keyed by document type.
- Cover types (A–E) preserved for backward compatibility with `structure_detector.py` logic.

---

## B4. Function Reference

### B4.1 `DocumentRegistry.__init__(logger)`

Initialises the registry. Implements **Automatic Schema Migration**: checks for missing columns (e.g. `source_type` or extended metadata) and executes `ALTER TABLE` to upgrade existing databases without data loss.

### B4.2 `DocumentRegistry.register_document(metadata) → str`

Registers a new revision. If keys like `asset_tags` are provided as Python lists, the registry automatically serializes them to JSON strings (`json.dumps()`) for storage in the VARCHAR column. On read, callers receive the raw JSON string and should deserialize with `json.loads()` if a list is needed.

**Metadata Keys (Extended):**
- `source_type`: `ingested`, `referenced`, `stub`
- `asset_tags`: List of strings — auto-serialized to JSON string on write (e.g. `'["P-101", "V-202"]'`)
- `extract_status`: `pending` (default), `success`, `partial`, `failed`
- `extraction_confidence`: Float 0.0 - 1.0
- `verified_by`: String (null until manual verification)

---

## B5. Extraction & Verification Workflow

The extended metadata fields support a hybrid automated/manual workflow implemented across Phase 3 and Phase 5.

1.  **Automated Extraction (Phase 3)**:
    *   The Ingestion Engine uses LLM/Regex logic to extract cover sheet metadata.
    *   Fields `created_by`, `originator_company`, `asset_tags`, and `page_count` are populated.
    *   `extract_status` is set to `success` or `partial`.
    *   `extraction_confidence` is recorded.
2.  **Manual Verification (Phase 5)**:
    *   Users access the "Manual Verification Dashboard" in the EKS UI.
    *   Auto-extracted values are presented for review.
    *   User sets `security_class` and corrects any auto-extracted errors.
    *   Upon submission, the UI sets `verified_by` to the current user's name.
    *   A record is considered "Project Final" only when `verified_by` is NOT NULL.

---

## B6. Document Registry Establishment Summary (TWRP Project)

### B6.1. Existing Data Assets (`eks/data/twrp/`)

| Category | Contents | Count/Size |
|----------|----------|------------|
| **Engineering Drawings (PDF)** | Civil (C), Electrical (E), Instrumentation (I), Piping (P), Structural (S) | 100+ PDFs across Volume 5 Part-IA & Part-IB |
| **CAD Drawings (DGN)** | MicroStation DGN files | 6 files (Part-II) |
| **Structured Asset Datadrop** | `Datadrop Summary.xlsx` (7 sheets, 7,681 plant items) | 1.3 MB |

### B6.2. Establishment Workflow

**Phase 1 — Foundation (✅ COMPLETE — T1.7, T1.8, T1.21, T1.22):**
1. **Registry Initialization** — `DocumentRegistry()` auto-creates `eks/output/eks_registry.db` with full 27-column schema
2. **Parser Plug-ins** — PDF, DOCX, XLSX parsers extract metadata (`created_by`, `originator_company`, `page_count`, etc.)
3. **Revision Control** — Each ingestion sets prior revision `is_latest=FALSE`, inserts new with `is_latest=TRUE`
4. **Test Verification** — Registry tested successfully (2026-06-19): register, retrieve, list, revision history all passing

**Phase 3 — Knowledge Graph Ingestion (🔷 PLANNED):**
1. **Bulk Ingestion** — Walk `eks/data/twrp/spec/` recursively
2. **Metadata Extraction** — Parse cover sheets via LLM/regex for: project_number (WSD11), discipline, document_number, revision, asset_tags
3. **Asset Linking** — Cross-reference `asset_tags` against datadrop `keytag` values to create `REFERENCES_ASSET` edges
4. **Document Ontology** — Classify by `document_type` → `Drawing`/`Specification`/`Manual`/`Report`; create `SUPERSEDES` chains

**Phase 5 — Manual Verification (🔷 PLANNED):**
1. **Dashboard** — Present auto-extracted metadata for human review
2. **Correction** — Set `security_class`, fix extraction errors
3. **Validation** — Record `verified_by` = reviewer name → marks "Project Final"

### B6.3. Next Steps for TWRP Ingestion (Require Approval)

| Step | Action | Dependencies |
|------|--------|--------------|
| 1 | Define ingestion script to walk `eks/data/twrp/spec/` | Phase 1 registry + parsers ready |
| 2 | Implement cover-sheet metadata extraction (LLM/regex) | Phase 3 extractors |
| 3 | Map `asset_tags` → datadrop `keytag` for graph edges | Phase 3 asset graph |
| 4 | Configure `document_type` → ontology class mapping | `eks_ontology_config.json` (T1.29 ✅) |
| 5 | Build Manual Verification UI | Phase 5 |

---

## B7. References

1. [`registry.py`](../engine/core/registry.py) — DocumentRegistry implementation
2. [Phase 1 Foundation Workplan](phase_1_foundation_workplan.md) — T1.21, T1.22
3. [Phase 3 Knowledge Graph Workplan](phase_3_knowledge_graph_workplan.md) — T3.21 (Extraction)
4. [Phase 5 UI Integration Workplan](phase_5_ui_integration_workplan.md) — T5.18 (Verification UI)
