# Appendix B — Document Registry

**Version**: 2.0.0  
**Last Updated**: 2026-07-19  
**Phase**: 1 — Foundation  
**Status**: ✅ Implemented & Tested  
**Related Files**:
- [`eks/engine/core/registry.py`](../engine/core/registry.py)
- [`eks/engine/core/revision.py`](../engine/core/revision.py)
- [`eks/engine/core/config_registry.py`](../engine/core/config_registry.py)
- [`eks/config/schemas/eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) — Document column definitions (v1.8.0)
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
| 1.0.0 | 2026-07-19 | opencode | I196 gap-closure sweep: updated B3 `id` format to UUID v4 (I186), B2 diagram INSERT (not REPLACE); added `CAD` to B3.2; corrected B6.2 Phase 1 scope re: `asset_tags`; updated B3 PK description for composite index. |
| 2.0.0 | 2026-07-19 | CodeBuddy | I196 full gap-closure: expanded B3 from 24→54 columns (v1.8.0 schema alignment); corrected auto/manual labels for checked_by, approved_by, originator_company; added references_documents + lifecycle_stage to B3.1 ontology mapping; added 7 missing public methods to B4 (sync_schema, store_elements, get_elements, get_elements_by_type, delete_elements, get_latest_by_key, update_document_status); documented I186 UUID migration in B4.1; rewrote B5 to document Phase 1 extraction pipeline (FilenameParser, FilePropertyExtractor, StructureDetector, HealthScorer); added column groupings, element thresholds to B3.4; corrected parser class paths to eks.engine.*; removed unsupported PostgreSQL claim; added export artifacts section to B6.2. |

---

## B1. Overview

The Document Registry is the central metadata store for all engineering documents ingested into EKS. It is backed by DuckDB (`output/eks_registry.db`) and managed through the `DocumentRegistry` class in `engine/core/registry.py`. It records every document revision that enters the system, tracks which revision is current (`is_latest`), and provides filtered query access for the retrieval pipeline.

The registry is config-driven — the DB path is read from `eks_config.json` at startup via `ConfigRegistry`. No hardcoded paths or connection strings exist in the implementation. (PostgreSQL support is planned for a future phase; Phase 1 uses DuckDB exclusively.)

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
┌──────────────────────────────────────────────────────────────┐
│                   DocumentRegistry                            │
│                  (registry.py)                               │
│                                                              │
│  COLUMN_ALLOWLIST = {...}  (schema-derived, v1.8.0: 54 cols) │
│                                                              │
│  __init__(logger, db_path=None)                              │
│    └─ ConfigRegistry() ──► eks_config.json                   │
│    └─ _init_db() ──► CREATE TABLE IF NOT EXISTS docs +       │
│                       document_elements (DDL from SchemaToDDL)│
│    └─ _migrate_schema() ──► ALTER TABLE (schema evolution)   │
│    └─ _migrate_ids_to_uuid() ──► business-key → UUID (I186) │
│                                                              │
│  register_document(metadata) ──► doc_id (UUID v4)            │
│    └─ UPDATE is_latest = FALSE (prior revisions)             │
│    └─ json.dumps(asset_tags, references_docs) if list        │
│    └─ document_title derivation (embedded → filename → key)  │
│    └─ supersedes chain: link prev→new, new→prev (T1.99.141) │
│    └─ INSERT (pure — I186 UUID, no REPLACE)                  │
│                                                              │
│  get_document(doc_number, revision=None) ──► dict|None       │
│  get_latest_by_key(doc_number, revision) ──► dict|None (I186)│
│                                                              │
│  list_documents(filters, latest_only, order_by) ──► list     │
│    └─ COLUMN_ALLOWLIST validation for keys/order_by          │
│                                                              │
│  sync_schema() ──► dict (column/index changes applied)       │
│  store_elements(doc_id, elements) ──► count inserted         │
│  get_elements(doc_id) ──► list[dict]                         │
│  get_elements_by_type(doc_id, type) ──► list[dict]           │
│  delete_elements(doc_id) ──► count deleted                   │
│                                                              │
│  update_document_status(doc_id, status, ...) ──► bool        │
│    └─ I184 diff logging: [DIFF] prepended to extraction_notes│
└──────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│                   RevisionManager                             │
│                  (revision.py)                               │
│                                                              │
│  get_revision_history(document_number) ──► list[dict]        │
│    └─ list_documents(order_by="ingested_at DESC")            │
│    └─ sorted at SQL level (G3 Fix ✅)                        │
└──────────────────────────────────────────────────────────────┘
```

---

## B3. Database Schema

**Table**: `documents`  
**Backend**: DuckDB (`output/eks_registry.db`)  
**Created by**: `_init_db()` on first instantiation (`CREATE TABLE IF NOT EXISTS`)  
**Schema source**: [`eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) v1.8.0 — 54 columns  

**Primary key**: `id` (UUID v4, system-generated per I186). Business key `(document_number, revision)` is indexed separately via `idx_doc_business_key` for fast lookup. The old `{document_number}-{revision}` format is retired — each call to `register_document()` now generates a new UUID unconditionally, controlled by the I185 three-tier check (key lookup → hash match → hash mismatch/supersedes) in `FileScanner.register_placeholders()`.

**Source codes**:
- `Auto` = Automatically extracted by the Phase 1 pipeline (parsers, filename scanner, FilePropertyExtractor, StructureDetector, or system logic)
- `Manual` = Requires human input (planned for Phase 5 verification dashboard)
- `System` = Set by internal pipeline logic (not from file content)

### Identity (2 columns)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `id` | VARCHAR | NOT NULL | — | System | Primary key. UUID v4 (I186) |
| `source_type` | VARCHAR | YES | `'ingested'` | System | Source: `ingested`, `referenced`, `stub` |

### Project (5 columns)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `project_title` | VARCHAR | YES | NULL | Auto | Project full name (from filename) |
| `project_number` | VARCHAR | YES | NULL | Auto | Project code e.g. `WSD11` (from filename) |
| `area` | VARCHAR | YES | NULL | Auto | Plant area or zone (from filename) |
| `discipline` | VARCHAR | YES | NULL | Auto | Discipline code PI, EL, CV, etc. (from filename) |
| `department` | VARCHAR | YES | NULL | Manual | Originating department |

### Document Core (7 columns)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `document_type` | VARCHAR | YES | NULL | Auto | Type code: CAD, DWG, PI-PID, SPC, DS, MAN, OM, RPT (from filename) |
| `document_number` | VARCHAR | YES | NULL | Auto | Document identifier (from filename) |
| `revision` | VARCHAR | YES | NULL | Auto | Revision identifier A, B, 0, 1, etc. (from filename) |
| `status` | VARCHAR | YES | NULL | Manual | Workflow status APPROVED, IFR, IFC, etc. |
| `is_latest` | BOOLEAN | YES | TRUE | System | TRUE for current active revision only |
| `file_path` | VARCHAR | YES | NULL | Auto | Relative path to source file (from scanner) |
| `file_type` | VARCHAR | YES | NULL | Auto | Source file format: pdf, dgn, docx, xlsx, dwg (from scanner) |

### Timestamps (1 column)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `ingested_at` | TIMESTAMP | YES | CURRENT_TIMESTAMP | System | UTC timestamp of ingestion |

### Account (3 columns)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `created_by` | VARCHAR | YES | NULL | Auto | Author (from parser metadata: pdf→author, docx→author, xlsx→author) |
| `checked_by` | VARCHAR | YES | NULL | Manual | Reviewer name |
| `approved_by` | VARCHAR | YES | NULL | Manual | Approver name |

### Origin & Security (2 columns)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `originator_company` | VARCHAR | YES | NULL | Manual | Producing company name |
| `security_class` | VARCHAR | YES | NULL | Manual | Security classification |

### Asset Tags & Technical (2 columns)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `asset_tags` | VARCHAR | YES | NULL | Auto | JSON-serialized list of asset tags. Detected by StructureDetector regex from cover page / title block. Python lists auto-serialized via `json.dumps()` on write. |
| `page_count` | INTEGER | YES | NULL | Auto | Total pages (from parser metadata: pdf page count) |

### Quality (4 columns)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `extract_status` | VARCHAR | YES | `'pending'` | System | Enum: `pending`, `success`, `partial`, `failed` |
| `extraction_confidence` | DOUBLE | YES | NULL | System | Confidence score 0.0 – 1.0 (from health scorer) |
| `extraction_notes` | TEXT | YES | NULL | System | Extraction logs, failure reasons, I184 diff records |
| `verified_by` | VARCHAR | YES | NULL | Manual | Name of manual validator (Phase 5) |

### OS File Properties (4 columns — v1.4.0, Appendix J)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `file_size` | INTEGER | YES | NULL | Auto | OS-level file size in bytes (from `Path.stat().st_size`) |
| `file_created_at` | VARCHAR | YES | NULL | Auto | OS creation timestamp UTC ISO 8601 (from `st_ctime`) |
| `file_modified_at` | VARCHAR | YES | NULL | Auto | OS last-modified timestamp UTC ISO 8601 (from `st_mtime`) |
| `file_hash` | VARCHAR | YES | NULL | Auto | MD5 content hash for integrity verification (I185 dedup) |

### Embedded Metadata (9 columns — v1.4.0, Appendix J)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `embedded_title` | VARCHAR | YES | NULL | Auto | Embedded document title from parser metadata |
| `embedded_subject` | VARCHAR | YES | NULL | Auto | Embedded document subject from parser metadata |
| `embedded_created_date` | VARCHAR | YES | NULL | Auto | Embedded creation date from parser metadata |
| `embedded_modified_date` | VARCHAR | YES | NULL | Auto | Embedded modification date from parser metadata |
| `embedded_creator_app` | VARCHAR | YES | NULL | Auto | Application that created the file (e.g. `AutoCAD 2024`) |
| `embedded_producer` | VARCHAR | YES | NULL | Auto | Library that generated the file (e.g. `pdfplot15.hdi`) |
| `embedded_last_modified_by` | VARCHAR | YES | NULL | Auto | Last modifier from DOCX/XLSX core properties |
| `embedded_keywords` | VARCHAR | YES | NULL | Auto | Embedded keywords from parser metadata |
| `embedded_sheet_count` | INTEGER | YES | NULL | Auto | Number of sheets in XLSX workbook |

### Document Lifecycle (15 columns — v1.6.0)

| Column | Type | Nullable | Default | Source | Description |
| :----- | :--- | :------: | :------ | :----: | :---------- |
| `document_title` | VARCHAR | YES | NULL | Auto | Human-readable title. Derived from embedded_title (filtering boilerplate prefixes), falling back to filename stem, falling back to document_number. T1.99.142. |
| `supersedes` | VARCHAR | YES | NULL | System | FK → documents.id — previous revision this document supersedes. Auto-set by revision chain logic. T1.99.141. |
| `superseded_by` | VARCHAR | YES | NULL | System | FK → documents.id — next revision that supersedes this document. Auto-set when a newer revision is registered. T1.99.141. |
| `lifecycle_stage` | VARCHAR | YES | `'draft'` | Manual | Enum: `draft`, `issued_for_review`, `issued_for_construction`, `as_built`, `superseded`, `archived`. T1.99.143. |
| `revision_date` | VARCHAR | YES | NULL | Manual | Date of this revision (ISO 8601 string). T1.99.143. |
| `revision_description` | VARCHAR | YES | NULL | Manual | Description of changes in this revision. T1.99.143. |
| `embedded_revision_number` | VARCHAR | YES | NULL | Auto | Revision number from embedded DOCX/XLSX core properties. T1.99.144. |
| `references_documents` | VARCHAR | YES | `'[]'` | Manual | JSON array of doc_id strings this document references. T1.99.145. |
| `project_phase` | VARCHAR | YES | NULL | Manual | Project lifecycle phase (e.g. `tender`, `construction`, `as_built`). T1.99.146. |
| `contract_package` | VARCHAR | YES | NULL | Manual | Procurement contract package grouping. T1.99.146. |
| `issued_date` | VARCHAR | YES | NULL | Manual | Formal issue/submission date to client (ISO 8601). T1.99.146. |
| `responsible_engineer` | VARCHAR | YES | NULL | Manual | Engineer accountable for the document. T1.99.146. |
| `total_sheets` | INTEGER | YES | NULL | Auto | Total sheets in multi-sheet drawing set. Defaults to `page_count` if not explicitly set. T1.99.146. |
| `language` | VARCHAR | YES | `'en'` | System | ISO 639-1 language code. Default `en`. T1.99.146. |
| `vendor_name` | VARCHAR | YES | NULL | Manual | Equipment vendor name for vendor-supplied documents. T1.99.146. |

**Column count summary**: Identity(2) + Project(5) + Document Core(7) + Timestamps(1) + Account(3) + Origin/Security(2) + Asset Tags/Tech(2) + Quality(4) + OS File Props(4) + Embedded Metadata(9) + Document Lifecycle(15) = **54 columns** (v1.8.0 schema).

### B3.1. Ontology Mapping (Knowledge Graph Triggers)

The following registry fields are mapped to Ontology classes and relationships during Phase 3 ingestion:

| Registry Field | Ontology Trigger | Logic / Edge Produced |
| :--- | :--- | :--- |
| `document_type` | `IS_A` | Class Assignment: maps to `Drawing`, `PID_Drawing`, `Specification`, `Manual`, or `Report`. |
| `document_number` | `SUPERSEDES` | Links revisions of the same number in a time-ordered chain. |
| `asset_tags` | `REFERENCES_ASSET` | Produces M:N edges to `FunctionalObject` (Tag) nodes. |
| `originator_company` | `PRODUCED_BY` | Links Document to a `GovernanceObject` (Company/Entity). |
| `file_type` | `HAS_FORMAT` | Links Document to a `FileFormat` node indicating source format. |
| `references_documents` | `REFERENCES_DOC` | Produces M:N cross-reference edges between Document nodes. T1.99.145. |
| `lifecycle_stage` | `HAS_STAGE` | Links Document to its current lifecycle stage node. Enum: draft/issued_for_review/issued_for_construction/as_built/superseded/archived. T1.99.143. |

---

### B3.2. Document Type Registry

The following document type codes are defined in `eks_doc_config.json` → `document_type_registry`. They map to ontology classes (Appendix C) and expected file formats for TWRP ingestion.

| Code | Label | Ontology Class | Description | Expected File Types |
|:---- |:----- |:-------------- |:----------- |:------------------- |
| `CAD` | AutoCAD Drawing | `Drawing` | Native AutoCAD DWG drawing file | `dwg` |
| `DWG` | Engineering Drawing | `Drawing` | Engineering design drawing | `pdf` |
| `PI-PID` | P&ID Drawing | `PID_Drawing` | Piping and instrumentation diagram | `pdf`, `dgn` |
| `SPC` | Technical Specification | `Specification` | Technical specification document | `pdf`, `docx` |
| `DS` | Data Sheet | `Specification` | Equipment/instrument data sheet | `pdf`, `xlsx` |
| `OM` | Operation Manual | `Manual` | System operation manual | `pdf`, `docx` |
| `MAN` | Vendor O&M Manual | `Manual` | Vendor operation and maintenance manual | `pdf` |
| `RPT` | Technical Report | `Report` | Technical report or study | `pdf`, `docx` |

**Alignment**:
- Ontology class hierarchy per Appendix C §C4: `Drawing` → `PID_Drawing`; `Specification` covers `SPC` and `DS`; `Manual` covers `MAN` and `OM`.
- TWRP assets per Appendix B §B6.1: 100+ PDF drawings (DWG/PI-PID), 6 DGN drawings (PI-PID), specifications, manuals, reports.
- Phase 1 filename parsing extracts `document_type`; Phase 3 cover sheet parsing also extracts it → ontology class assignment.

---

### B3.3. File Type Registry

Maps source file extensions to parser implementations (Phase 1 plug-in architecture) and MIME types.

| Extension | Display Name | Parser Class | TWRP Use | MIME Type |
|:--------- |:------------ |:------------ |:-------- |:--------- |
| `pdf` | PDF Document | `eks.engine.parsers.pdf_parser.PDFParser` | Drawings (100+), Specs, Manuals, Reports | `application/pdf` |
| `dgn` | DGN Drawing | `eks.engine.parsers.dgn_parser.DGNParserStub` | CAD Drawings (6) | `image/vnd.dgn` |
| `docx` | Word Document | `eks.engine.parsers.docx_parser.DOCXParser` | Specs, Manuals, Reports | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| `xlsx` | Excel Workbook | `eks.engine.parsers.xlsx_parser.XLSXParser` | Data Sheets, Datadrop | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| `dwg` | AutoCAD Drawing | `eks.engine.parsers.dwg_parser.DWGParserStub` | Future CAD support | `image/vnd.dwg` |

**Alignment**:
- Parser plug-ins defined in `eks_config.json` → `parsers` section. Full class paths as stored in `eks_config.json`.
- Phase 1 implements PDF, DOCX, XLSX; DWG/DGN are stubs for Phase 3 (Appendix B §B6.2).
- `file_type` column in registry (B3 table) stores extension for format tracking.

---

### B3.4. Element Type Registry

Structural element types per Appendix D §D7.10, used for structural completeness scoring and Phase 2/3 knowledge graph population.

Expected-element counts per document type are defined in `eks_doc_config.json` → `element_expectations`:

| Element Type | Description | Source Method | Phase 2 Use | Phase 3 Use | Expected By Cover Type |
|:------------ |:----------- |:------------- |:----------- |:----------- |:---------------------- |
| `cover_page` | Cover page fields from page 1 | `regex` | Section anchor | Document-type node | A, B, D, E |
| `revision_table` | Revision history table from page 1 | `table` | Change tracking | Revision nodes | A, B |
| `section` | Section heading (regex `\d+\.\d+`) | `regex` | Chunk boundary | Section nodes | A, B, D, E |
| `table` | Data table on page | `heuristic` | Context chunks | Table nodes | E |
| `image` | Image/chart on page | `heuristic` | Skip | Figure nodes | A, B |
| `link` | URL or file path reference | `regex` | Skip | Reference edges | A, B, C, D, E |
| `legend` | Page legend/symbol key | `heuristic` | Skip | Legend nodes | A, B |
| `note` | Page 1 annotation block | `heuristic` | Skip | Annotation nodes | A, B |

**Element Expectations by Document Type (Thresholds)**:

| Doc Type | Expected Elements | Threshold | Cover Type |
|:-------- |:----------------- |:--------: |:----------:|
| `CAD` | cover_page, revision_table, section, image, link | 4 | A |
| `DWG` | cover_page, revision_table, section, image, link | 4 | A |
| `PI-PID` | cover_page, revision_table, section, image, link | 4 | B |
| `SPC` | (none) | 0 | C |
| `DS` | cover_page, section, table | 2 | E |
| `MAN` | cover_page, section | 2 | D |
| `OM` | cover_page, section | 2 | D |
| `RPT` | cover_page, section, table | 2 | E |

The `threshold` value is the minimum number of expected element types that must be detected for the structural completeness sub-score to reach a passing tier. Cover types (A–E) are preserved for backward compatibility with `StructureDetector` classification logic.

**Alignment**:
- `structure_detector.py` (T1.32) detects elements and stores in `document_elements` table via `DocumentRegistry.store_elements()`.
- Structural completeness scoring (health scorer dimension 3) uses `element_expectations` keyed by document type.
- Asset tag detection (`asset_tags`) is a best-effort regex from cover page / title block (T1.99.162).

---

## B4. Function Reference

### B4.1 `DocumentRegistry.__init__(logger, db_path=None)`

Initialises the registry. Implements **Automatic Schema Migration**:

1. **`_init_db()`** — Creates `documents` and `document_elements` tables using DDL auto-generated from `eks_doc_base_schema.json` via `SchemaToDDL`. Creates schema indexes (`idx_doc_business_key`, etc.).
2. **`_migrate_schema()`** — Checks for missing columns vs. schema definitions and executes `ALTER TABLE ADD COLUMN` to upgrade existing databases without data loss. Also runs NOT NULL constraint diagnostics on project-metadata columns (which should be nullable; reports schema drift if NOT NULL is misapplied).
3. **`_migrate_ids_to_uuid()` (I186)** — One-time migration: converts existing business-key-derived ids (e.g. `DWG-001-A`) to pure UUID v4 format. Steps: (a) add temporary `_old_id` column with current values, (b) generate new UUID for each non-UUID row, (c) update FK references in `document_elements` table, (d) drop temporary column. Idempotent — skips if all ids are already UUID format (36 chars with hyphens).

### B4.2 `DocumentRegistry.register_document(metadata) → str`

Registers a new document revision. Returns the UUID v4 document id (I186).

**Registration logic (in order)**:
1. Validate/resolve `document_number` — if missing, generates synthetic key via `common.library.utility.synthetic_key`.
2. Generate UUID v4 `id` (I186 — pure UUID, not business-key-derived).
3. Serialize `asset_tags` and `references_documents` to JSON strings if provided as Python lists.
4. Derive `document_title`: embedded_title (filtering boilerplate prefixes via SSOT config) → filename stem → document_number fallback.
5. Default `total_sheets` to `page_count` if not explicitly set.
6. Clear `is_latest` on all prior revisions of same `document_number`.
7. Capture previous-latest `id` for supersedes chain.
8. Dynamic INSERT — builds column/value list from metadata keys matching `COLUMN_ALLOWLIST`.
9. If supersedes chain: set previous revision's `superseded_by` to this new `id`.

**All Metadata Keys (54 columns, grouped)**:
- **Identity**: `source_type`
- **Project**: `project_title`, `project_number`, `area`, `discipline`, `department`
- **Document Core**: `document_type`, `document_number`, `revision`, `status`, `file_path`, `file_type`
- **Account**: `created_by`, `checked_by`, `approved_by`
- **Origin/Security**: `originator_company`, `security_class`
- **Asset/Tech**: `asset_tags` (list → auto-serialized), `page_count`
- **Quality**: `extract_status`, `extraction_confidence`, `extraction_notes`, `verified_by`
- **OS File Properties**: `file_size`, `file_created_at`, `file_modified_at`, `file_hash`
- **Embedded Metadata**: `embedded_title`, `embedded_subject`, `embedded_created_date`, `embedded_modified_date`, `embedded_creator_app`, `embedded_producer`, `embedded_last_modified_by`, `embedded_keywords`, `embedded_sheet_count`
- **Document Lifecycle**: `document_title`, `supersedes`, `superseded_by`, `lifecycle_stage`, `revision_date`, `revision_description`, `embedded_revision_number`, `references_documents` (list → auto-serialized), `project_phase`, `contract_package`, `issued_date`, `responsible_engineer`, `total_sheets`, `language`, `vendor_name`

### B4.3 `DocumentRegistry.get_document(doc_number, revision=None) → dict | None`

Retrieve metadata for a specific document. If `revision` is `None`, returns the latest revision (`is_latest = TRUE`).

### B4.4 `DocumentRegistry.get_latest_by_key(doc_number, revision) → dict | None`

Retrieve the most-recently-registered (`is_latest = TRUE`) row for a given `(document_number, revision)` pair. Introduced with I186 UUID migration to provide the authoritative "current" row when multiple rows share the same composite key due to content changes.

### B4.5 `DocumentRegistry.list_documents(filters, latest_only=True, order_by=None) → list[dict]`

List documents with optional filtering (`COLUMN_ALLOWLIST` validated) and SQL-level sorting. Default: latest-only.

### B4.6 `DocumentRegistry.update_document_status(doc_id, status, confidence=None, notes=None, extra_properties=None) → bool`

Update document extraction status. Features:
- **I184 diff logging**: Before executing UPDATE, queries current row and compares extraction-related fields (`DIFF_TRACK_FIELDS`). Changes are serialized as `[DIFF] {"field": {"old": ..., "new": ...}}` and prepended to `extraction_notes`.
- **Dynamic extra properties**: Accepts `extra_properties` dict to update additional registry columns (e.g. `file_size`, `file_hash`, `embedded_title` from `FilePropertyExtractor`). Only keys present in `COLUMN_ALLOWLIST` are applied.
- **Retry**: Uses `_with_retry` for safe concurrent access (DuckDB locking).

### B4.7 `DocumentRegistry.sync_schema() → dict`

Synchronize database schema with JSON schema definitions. Compares current DB columns against schema and applies any missing columns via `ALTER TABLE ADD COLUMN`. Creates missing indexes. Returns summary dict with keys: `documents_added`, `document_elements_added`, `indexes_created`.

### B4.8 `DocumentRegistry.store_elements(doc_id, elements) → int`

Insert structural elements for a document into `document_elements` table. Each element has: `doc_id`, `element_type`, `element_id`, `title`, `content`, `confidence`, `source`. Returns count inserted. Called by `PipelineOrchestrator` after `StructureDetector` analysis.

### B4.9 `DocumentRegistry.get_elements(doc_id) → list[dict]`

Retrieve all structural elements for a document, ordered by `doc_id, element_type`.

### B4.10 `DocumentRegistry.get_elements_by_type(doc_id, element_type) → list[dict]`

Retrieve structural elements of a specific type for a document.

### B4.11 `DocumentRegistry.delete_elements(doc_id) → int`

Delete all structural elements for a document. Returns count deleted.

---

## B5. Extraction & Verification Workflow

### Phase 1 — Foundation Extraction (✅ IMPLEMENTED)

The Phase 1 pipeline performs automated extraction through six subsystems operating in sequence within `PipelineOrchestrator`:

1. **File Scanning** (`FileScanner`):
   - Walks the data directory, discovers files by extension, groups by `(document_number, revision)` composite key.
   - Three-tier I185 dedup check: key lookup → hash match (skip duplicate) → hash mismatch (register new revision with supersedes chain).

2. **Filename Parsing** (`FilenameParser`, Appendix I):
   - Schema-driven segment parsing using patterns from `eks_doc_config.json` → `filename_patterns`.
   - Extracts up to 7 fields: `project_number`, `area`, `document_type`, `discipline`, `sequence_number`, `document_number`, `revision`.
   - Supports per-project patterns (e.g. `131101` for TWRP delimited format: `{project}-{area}-{type}-{disc}-{seq}_rev{rev}.ext`).

3. **File Property Extraction** (`FilePropertyExtractor`, Appendix J):
   - **OS-level**: `file_size`, `file_hash` (MD5), `file_created_at`, `file_modified_at` via `Path.stat()`.
   - **Parser-embedded metadata**: Routes through format-specific parser `extract_metadata()` → property mapping per `eks_doc_config.json` → `file_property_patterns`.
     - PDF: `author`→`created_by`, `title`→`embedded_title`, `page_count`, `creator`→`embedded_creator_app`, `producer`→`embedded_producer`, etc.
     - DOCX: `author`→`created_by`, `title`→`embedded_title`, `revision`→`embedded_revision_number`, `last_modified_by`→`embedded_last_modified_by`, etc.
     - XLSX: `author`→`created_by`, `sheet_count`→`embedded_sheet_count`, `last_modified_by`→`embedded_last_modified_by`, etc.
     - DGN/DWG: OS-only (stub parsers, no embedded metadata extraction yet).

4. **Structure Detection** (`StructureDetector`):
   - Analyses parsed PDF text from page 1 to detect 8 element types: `cover_page`, `revision_table`, `section`, `table`, `image`, `link`, `legend`, `note`.
   - Classifies cover type (A–E) based on detected element combinations.
   - Best-effort `asset_tags` regex detection from title block (`COVER_PAGE_PATTERNS["asset_tags"]`).
   - Results persisted to `document_elements` table via `registry.store_elements()`.

5. **Health Scoring** (`HealthScorer`):
   - Computes a 6-dimensional health score (0.0–1.0): completeness (20%), extraction_confidence (20%), structural_completeness (20%), source_quality (15%), xref_quality (15%), consistency (10%).
   - Structural completeness dimension uses `element_expectations` from `eks_doc_config.json` with per-document-type thresholds.
   - Score tiers determine action: auto_register (≥0.90), optional_review (≥0.70), flag_review (≥0.50), mandatory_review (≥0.20), manual_entry (<0.20).

6. **Pipeline Export** (`--export csv|xlsx|both`):
   - Schema-driven column subsets defined in `eks_doc_base_schema.json` → `export_artifact_def` (I193).
   - Three artifacts: `discovery_inventory` (all `x_export` fields minus extraction), `extraction_results` (all `x_export` fields), `review_flags` (extraction-quality triage subset + `flag_reason`).
   - Columns resolved at runtime from `x_export` boolean flags on each property — no hardcoded column lists.

### Phase 3 — Knowledge Graph Ingestion (🔷 PLANNED)

1. **Bulk Ingestion** — Walk `eks/data/twrp/spec/` recursively.
2. **Metadata Extraction** — Parse cover sheets via LLM/regex for: project_number (WSD11), discipline, document_number, revision, asset_tags.
3. **Asset Linking** — Cross-reference `asset_tags` against datadrop `keytag` values to create `REFERENCES_ASSET` edges.
4. **Document Ontology** — Classify by `document_type` → `Drawing`/`Specification`/`Manual`/`Report`; create `SUPERSEDES` chains.

### Phase 5 — Manual Verification (🔷 PLANNED)

1. **Dashboard** — Present auto-extracted metadata for human review.
2. **Correction** — Set `security_class`, fix extraction errors, populate manual fields (`checked_by`, `approved_by`, `originator_company`, `lifecycle_stage`, `revision_date`, `revision_description`, `project_phase`, `contract_package`, `issued_date`, `responsible_engineer`, `vendor_name`).
3. **Validation** — Record `verified_by` = reviewer name → marks "Project Final".

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

1. **Registry Initialization** — `DocumentRegistry()` auto-creates `eks/output/eks_registry.db` with full schema (54 columns as of v1.8.0). DDL is auto-generated from JSON schema via `SchemaToDDL`. Schema migration adds missing columns on subsequent runs (non-destructive).

2. **Parser Plug-ins** — PDF, DOCX, XLSX parsers extract embedded metadata (`created_by`, `embedded_title`, `embedded_subject`, `embedded_created_date`, `embedded_modified_date`, `embedded_creator_app`, `embedded_producer`, `embedded_keywords`, `embedded_sheet_count`, `embedded_revision_number`, `page_count`) + OS-level file properties (`file_size`, `file_hash`, `file_created_at`, `file_modified_at`) via `FilePropertyExtractor` (Appendix J). DWG/DGN parsers are stubs (OS-only extraction).

3. **Filename Parsing** — Schema-driven `FilenameParser` (Appendix I) extracts `project_number`, `area`, `document_type`, `discipline` from delimited filenames (e.g. `131101-XXX-DWG-PI-0001_A.pdf`). Handles revision suffix stripping, segment validation against `document_type_registry`, and fallback resolution for unrecognised patterns.

4. **Structure Detection** — `StructureDetector` analyses page 1 of each PDF to detect 8 element types (cover_page, revision_table, section, table, image, link, legend, note), classifies cover type (A–E), and performs best-effort `asset_tags` regex detection from the title block. Results are persisted to the `document_elements` table via `registry.store_elements()` for downstream health scoring and Phase 2/3 knowledge graph population.

5. **Health Scoring** — `HealthScorer` computes a 6-dimensional composite score per document (completeness 20% + extraction_confidence 20% + structural_completeness 20% + source_quality 15% + xref_quality 15% + consistency 10%). Structual completeness dimension uses `element_expectations` thresholds from B3.4. Score tiers map to pipeline actions (auto_register → manual_entry).

6. **Revision Control** — Three-tier I185 check in `FileScanner.register_placeholders()`: key lookup → hash match (skip duplicate) → hash mismatch (register new revision with supersedes chain). Each registration uses UUID v4 `id` (I186). Supersedes chain auto-links `supersedes`/`superseded_by` FK pairs.

7. **Pipeline Export** — I193 schema-driven export produces 3 artifacts (`discovery_inventory`, `extraction_results`, `review_flags`) in CSV/XLSX/Both formats. Column subsets are resolved at runtime from `x_export` flags on each schema property — no hardcoded column lists. Outputs written to `eks/output/`.

8. **Test Verification** — Registry CRUD, I185 three-tier dedup, UUID migration (I186), filename parsing (Appendix I), file property extraction (Appendix J), structure detection, element persistence, health scoring, and schema-driven export all passing.

**Note:** `asset_tags` extraction from cover sheet / title block is best-effort in Phase 1 (via `StructureDetector` regex). Full asset tag cross-referencing against the datadrop (`Datadrop Summary.xlsx`, 7,681 plant items) is a Phase 3 task per §B6.2 step 3.

**Phase 3 — Knowledge Graph Ingestion (🔷 PLANNED):**
1. **Bulk Ingestion** — Walk `eks/data/twrp/spec/` recursively
2. **Metadata Extraction** — Parse cover sheets via LLM/regex for: project_number (WSD11), discipline, document_number, revision, asset_tags
3. **Asset Linking** — Cross-reference `asset_tags` against datadrop `keytag` values to create `REFERENCES_ASSET` edges
4. **Document Ontology** — Classify by `document_type` → `Drawing`/`Specification`/`Manual`/`Report`; create `SUPERSEDES` chains

**Phase 5 — Manual Verification (🔷 PLANNED):**
1. **Dashboard** — Present auto-extracted metadata for human review
2. **Correction** — Set `security_class`, fix extraction errors, populate all Manual-source fields
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
