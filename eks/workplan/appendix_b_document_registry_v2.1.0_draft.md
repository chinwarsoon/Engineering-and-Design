# Appendix B — Document Registry

**Version**: 2.1.0 (Draft for Review)  
**Last Updated**: 2026-08-04  
**Phase**: 1 — Foundation  
**Status**: 🔷 Pending Review  
**Related Files**:
- [`eks/engine/core/registry.py`](../engine/core/registry.py)
- [`eks/engine/core/revision.py`](../engine/core/revision.py)
- [`eks/engine/core/config_registry.py`](../engine/core/config_registry.py)
- [`eks/config/schemas/eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) — Document column definitions (v1.8.0)
- [`eks/config/schemas/eks_doc_setup_schema.json`](../config/schemas/eks_doc_setup_schema.json) — Table declarations, extraction rules, health scoring
- [`eks/config/schemas/eks_doc_config.json`](../config/schemas/eks_doc_config.json) — Element expectations, score tiers

**Migration Note**: This version implements the unified document type definition structure (B2.1) that merges the previous B2.1 Registry Structure and B3.2 Enrich Document Type sections. The content previously in B3.2 has been integrated into B2.1. Previous version archived as `archive/appendix_b_document_registry_v2.0.0_2026-08-04.md`.

---

## Table of Contents

- [Revision History](#revision-history)
- [B1. Overview](#b1-overview)
- [B2. Architecture](#b2-architecture)
  - [B2.1 Unified Document Type Definition](#b21-unified-document-type-definition)
    - [1. Identity & Classification](#1-identity--classification)
    - [2. Structural Characteristics](#2-structural-characteristics)
    - [3. Document Semantics](#3-document-semantics)
    - [4. Processing Profiles](#4-processing-profiles)
    - [5. Knowledge Relationships](#5-knowledge-relationships)
    - [6. Lifecycle & Governance](#6-lifecycle--governance)
    - [7. Capabilities & Extensions](#7-capabilities--extensions)
  - [B2.2 Registry workflow](#b22-registry-workflow)
- [B3. Ontology Hierarchy for EPC RAG System](#b3-ontology-hierarchy-for-epc-rag-system)
  - [B3.1 Document Class, Document Type, and Document Family](#b31-document-class-document-type-and-document-family)
  - [B3.2 Document Type Registry](#b32-document-type-registry)
  - [B3.3 File Type Registry](#b33-file-type-registry)
  - [B3.4 Element Type Registry](#b34-element-type-registry)
- [B4. Database Schema](#b4-database-schema)
  - [Schema to Unified Document Type Definition Mapping](#schema-to-unified-document-type-definition-mapping)
  - [Identity (2 columns)](#identity-2-columns)
  - [Project (5 columns)](#project-5-columns)
  - [Document Core (7 columns)](#document-core-7-columns)
  - [Timestamps (1 column)](#timestamps-1-column)
  - [Account (3 columns)](#account-3-columns)
  - [Origin & Security (2 columns)](#origin--security-2-columns)
  - [Asset Tags & Technical (2 columns)](#asset-tags--technical-2-columns)
  - [Quality (4 columns)](#quality-4-columns)
  - [OS File Properties (4 columns — v1.4.0, Appendix J)](#os-file-properties-4-columns--v140-appendix-j)
  - [Embedded Metadata (9 columns — v1.4.0, Appendix J)](#embedded-metadata-9-columns--v140-appendix-j)
  - [Document Lifecycle (15 columns — v1.6.0)](#document-lifecycle-15-columns--v160)
  - [B4.1. Ontology Mapping (Knowledge Graph Triggers)](#b41-ontology-mapping-knowledge-graph-triggers)
- [B5. Function Reference](#b5-function-reference)
  - [B5.1 `DocumentRegistry.__init__(logger, db_path=None)`](#b51-documentregistry__initlogger-db_pathnone)
  - [B5.2 `DocumentRegistry.register_document(metadata) → str`](#b52-documentregistryregister_documentmetadata--str)
  - [B5.3 `DocumentRegistry.get_document(doc_number, revision=None) → dict | None`](#b53-documentregistryget_documentdoc_number-revisionnone--dict--none)
  - [B5.4 `DocumentRegistry.get_latest_by_key(doc_number, revision) → dict | None`](#b54-documentregistryget_latest_by_keydoc_number-revision--dict--none)
  - [B5.5 `DocumentRegistry.list_documents(filters, latest_only=True, order_by=None) → list[dict]`](#b55-documentregistrylist_documentsfilters-latest_onlytrue-order_bynone--listdict)
  - [B5.6 `DocumentRegistry.update_document_status(doc_id, status, confidence=None, notes=None, extra_properties=None) → bool`](#b56-documentregistryupdate_document_statusdoc_id-status-confidencenone-notesnone-extra_propertiesnone--bool)
  - [B5.7 `DocumentRegistry.sync_schema() → dict`](#b57-documentregistrysync_schema--dict)
  - [B5.8 `DocumentRegistry.store_elements(doc_id, elements) → int`](#b58-documentregistrystore_elementsdoc_id-elements--int)
  - [B5.9 `DocumentRegistry.get_elements(doc_id) → list[dict]`](#b59-documentregistryget_elementsdoc_id--listdict)
  - [B5.10 `DocumentRegistry.get_elements_by_type(doc_id, element_type) → list[dict]`](#b510-documentregistryget_elements_by_typedoc_id-element_type--listdict)
  - [B5.11 `DocumentRegistry.delete_elements(doc_id) → int`](#b511-documentregistrydelete_elementsdoc_id--int)
- [B6. Extraction & Verification Workflow](#b6-extraction--verification-workflow)
  - [Phase 1 — Foundation Extraction (✅ IMPLEMENTED)](#phase-1--foundation-extraction--implemented)
  - [Phase 3 — Knowledge Graph Ingestion (🔷 PLANNED)](#phase-3--knowledge-graph-ingestion--planned)
  - [Phase 5 — Manual Verification (🔷 PLANNED)](#phase-5--manual-verification--planned)
- [B7. Document Registry Establishment Summary (TWRP Project)](#b7-document-registry-establishment-summary-twrp-project)
  - [B7.1. Existing Data Assets (`eks/data/twrp/`)](#b71-existing-data-assets-ekdatatwrp)
  - [B7.2. Establishment Workflow](#b72-establishment-workflow)
  - [B7.3. Next Steps for TWRP Ingestion (Require Approval)](#b73-next-steps-for-twrp-ingestion-require-approval)
- [B8. References](#b8-references)

---

## Revision History

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
| 1.0 | 2026-07-19 | opencode | I196 gap-closure sweep: updated B3 `id` format to UUID v4 (I186), B2 diagram INSERT (not REPLACE); added `CAD` to B3.2; corrected B6.2 Phase 1 scope re: `asset_tags`; updated B3 PK description for composite index. |
| 1.1 | 2026-07-19 | CodeBuddy | I196 full gap-closure: expanded B3 from 24→54 columns (v1.8.0 schema alignment); corrected auto/manual labels for checked_by, approved_by, originator_company; added references_documents + lifecycle_stage to B3.1 ontology mapping; added 7 missing public methods to B4 (sync_schema, store_elements, get_elements, get_elements_by_type, delete_elements, get_latest_by_key, update_document_status); documented I186 UUID migration in B4.1; rewrote B5 to document Phase 1 extraction pipeline (FilenameParser, FilePropertyExtractor, StructureDetector, HealthScorer); added column groupings, element thresholds to B3.4; corrected parser class paths to eks.engine.*; removed unsupported PostgreSQL claim; added export artifacts section to B6.2. |
| 1.2 | 2026-08-04 | Franklin Song | Added requirements for document definitions in Section B.3 |
| 2.1.0 | 2026-08-04 | Franklin Song | **ALIGNMENT FIX**: Unified B2.1 and B3.2 into single Document Type Definition structure with 7 functional domains; deprecated B3.2 with migration note; added B3.1 cross-reference to B2.1; updated B4 schema references to unified structure; standardized terminology across sections. |

---

## B1. Overview

The Document Registry is the central metadata store for all engineering documents ingested into EKS. It is backed by DuckDB (`output/eks_registry.db`) and managed through the `DocumentRegistry` class in `engine/core/registry.py`. It records every document revision that enters the system, tracks which revision is current (`is_latest`), and provides filtered query access for the retrieval pipeline.

The registry is config-driven — the DB path is read from `eks_config.json` at startup via `ConfigRegistry`. No hardcoded paths or connection strings exist in the implementation. (PostgreSQL support is planned for a future phase; Phase 1 uses DuckDB exclusively.)

**General Business Logic**
- Document will be organized per project, area, discipline, type, sequence number, and revision.
- Different documents can have different source file formats (native files), such as doc, pptx, xlx, dwg, dgn, etc. And final printout can also have PDF format.
- Different documents can have different metadata, rules, behaviours, and relationships.
- Different documents can have different elements, such as coversheet, index of content, sections, table, figure, sections, appendix, references, etc. which will require different parser processes.
- Same asset tags can be associated to different documents.
- Relationship between documents can be defined.

---

## B2. Architecture

### B2.1 Unified Document Type Definition

The Document Type Definition provides a unified structure that serves both registry implementation and semantic ontology purposes. It is organized into 7 functional domains:

```
Document Type Definition
├── 1. Identity & Classification
│      ├── Identity (concept_id, label, short_name, ontology_class, parent_class, document_type_id, display_name, description, version)
│      ├── Classification (document_class, document_family, discipline, category, project_phase, lifecycle_stage)
│      └── Metadata (required, optional fields)
│
├── 2. Structural Characteristics
│      ├── Document Structure (title_block, revision_table, cover_page, signature_block, multi_sheet, vector_graphics)
│      ├── Content Organization (section_based, drawing_based, embedded_tables, table_regions, has_table_of_contents)
│      └── Visual Elements (contains_callouts, contains_symbols, contains_cross_references, legend, grid, drawing_scale, sheet_number, north_arrow, table_regions, revision_block, signature_block, approval_block, change_cloud, callout_regions)
│
├── 3. Document Semantics
│      ├── Semantic Entities (semantic_entities list)
│      ├── Semantic Relationships (semantic_relationships list)
│      ├── Semantic Constraints (semantic_constraints list)
│      └── Business/Engineering Objects (business_objects, engineering_objects)
│
├── 4. Processing Profiles
│      ├── Extraction Profile (Parser, OCR, layout_analysis, vector_drawing, table_detection, symbol_detection, entity_linking, caption_detection, Layout, Title Block, Revision Table, Entity Extraction, Table Extraction, Figure Extraction, Cross-reference, Callout, Symbol Detection, CAD Parser, Vision LLM, LLM Verification, Confidence Threshold)
│      ├── Chunking Profile (chunk_strategy, chunk_size, anchor_priority, embedding_scope)
│      ├── Retrieval Profile (embedding_model, reranker, vector_weight, graph_weight, metadata_weight, keyword_weight, hybrid_search, cross_document_search, section_priority, entity_priority, table_priority, figure_priority)
│      ├── Validation Profile (metadata, structure, business, engineering, graph, quality rules)
│      ├── Indexing Profile (optional)
│      ├── AI Reasoning Profile (question_types, reasoning_level, preferred_context, requires_graph, requires_multimodal, preferred_chunk, citation_priority)
│      └── Graph Mapping Profile (optional, future)
│
├── 5. Knowledge Relationships
│      └── Relationship Types (produced_from, validated_by, references, implements, supersedes, derived_from, contains, linked_to, verified_against, governs)
│
├── 6. Lifecycle & Governance
│      ├── Lifecycle (lifecycle_stage, revision_strategy, revision_date, revision_description)
│      └── Governance (owner, confidentiality_default, approval_workflow)
│
└── 7. Capabilities & Extensions
      ├── Capabilities (what operations this document type supports)
      └── Extension Points (custom parsers, custom validators, etc.)
```

#### 1. Identity & Classification

**Identity** defines immutable properties of Document Type:

```json
{
   "concept_id": "PID_DRAWING",
   "label": "P&ID Drawing",
   "short_name": "P&ID",
   "ontology_class": "PID_Drawing",
   "parent_class": "Drawing",
   "document_type_id": "PI-PID",
   "display_name": "P&ID Drawing",
   "description": "Process and Instrumentation Diagram representing process flow, piping and instrumentation.",
   "version": "1.0"
}
```

**Classification** categorizes documents within the hierarchy:

- `document_class`: High-level class (Drawing, Specification, Calculation, Manual, Datasheet, Register, Report, Procedure)
- `document_family`: Grouping by discipline (Process Drawing, Instrument Drawing, Electrical Drawing, Mechanical Drawing)
- `discipline`: Discipline code (Process, Instrument, Electrical, Civil, Mechanical)
- `category`: Engineering category (Engineering, Design, Construction, Operation)
- `project_phase`: Project lifecycle phase (tender, FEED, Detailed Engineering, Construction, Commissioning, Operation)
- `lifecycle_stage`: Document lifecycle stage (draft, issued_for_review, issued_for_construction, as_built, superseded, archived)

**Metadata** defines required and optional fields per document type.

#### 2. Structural Characteristics

**Document Structure** defines the physical layout:

```json
{
   "title_block": "standard",
   "revision_table": "standard",
   "cover_page": "required",
   "signature_block": "required",
   "multi_sheet": true,
   "vector_graphics": true
}
```

**Content Organization** defines how content is organized:

```json
{
   "section_based": false,
   "drawing_based": true,
   "embedded_tables": false,
   "table_regions": "none",
   "has_table_of_contents": false
}
```

**Visual Elements** defines visual components present:

```json
{
   "contains_callouts": true,
   "contains_symbols": true,
   "contains_cross_references": true,
   "legend": "standard",
   "grid": "standard",
   "drawing_scale": "1:100",
   "sheet_number": "standard",
   "north_arrow": "standard",
   "table_regions": "none",
   "revision_block": "standard",
   "signature_block": "required",
   "approval_block": "required",
   "change_cloud": "optional",
   "callout_regions": "detected"
}
```

#### 3. Document Semantics

**Document Semantics** defines what knowledge a document contains, directly feeding the graph database:

- `semantic_entities`: List of entity types (Equipment, Instrument, Valve, Pipe, Control Loop, Stream, Area, Subsystem)
- `semantic_relationships`: List of relationship types (connected_to, measures, installed_on, controls)
- `semantic_constraints`: Constraints on entity relationships
- `business_objects`: Business-relevant objects
- `engineering_objects`: Engineering-relevant objects

**Example for P&ID**:
```
P&ID
   contains
      Equipment
      Instrument
      Valve
      Pipe
      Control Loop
      Stream
      Area
      Subsystem

Equipment
   connected_to
      Pipe

Instrument
   measures
      Line

Valve
   installed_on
      Line

Control Loop
   controls
      Valve
```

#### 4. Processing Profiles

**Extraction Profile** defines parser chains:

```json
{
   "parser": "PDFParser",
   "ocr": false,
   "layout_analysis": true,
   "vector_drawing": true,
   "table_detection": false,
   "symbol_detection": true,
   "entity_linking": true,
   "caption_detection": true,
   "extraction_steps": [
      "Layout",
      "Title Block",
      "Revision Table",
      "Entity Extraction",
      "Table Extraction",
      "Figure Extraction",
      "Cross-reference",
      "Callout",
      "Symbol Detection",
      "CAD Parser",
      "Vision LLM",
      "LLM Verification"
   ],
   "confidence_threshold": 0.85
}
```

**Parser Capability Matrix** helps with parser orchestration:

| Document  | OCR | Table | CAD | Vision | Graph   |
| --------- | --- | ----- | --- | ------ | ------- |
| P&ID      | No  | No    | Yes | Yes    | Yes     |
| Manual    | Yes | Yes   | No  | No     | No      |
| Datasheet | Yes | Yes   | No  | No     | Partial |

**Parser example for P&ID**:
```
P&ID
↓
PDF Parser
↓
CAD Parser
↓
Vision Model
↓
Symbol Detection
↓
Graph Builder
```

**Chunking Profile** defines how documents are chunked:

```json
{
   "chunk_strategy": "drawing",
   "chunk_size": 1,
   "anchor_priority": ["Equipment", "Line", "Instrument", "Valve"],
   "embedding_scope": "sheet"
}
```

**Chunk Strategy Registry** (expandable):
- Section
- Heading
- Drawing
- Table
- Paragraph
- Sheet
- Revision
- Title Block

**Document type mapping**:
- Drawing → Sheet Chunk
- Manual → Heading Chunk
- Specification → Section Chunk
- Register → Row Chunk

**Retrieval Profile** defines retrieval behavior:

```json
{
   "embedding_model": "text-embedding-3-small",
   "reranker": "cross-encoder",
   "vector_weight": 0.4,
   "graph_weight": 0.3,
   "metadata_weight": 0.2,
   "keyword_weight": 0.1,
   "hybrid_search": true,
   "cross_document_search": true,
   "section_priority": ["high"],
   "entity_priority": ["Equipment", "Instrument"],
   "table_priority": ["high"],
   "figure_priority": ["medium"]
}
```

**Validation Profile** defines validation rules across multiple layers:

```json
{
   "validation_layers": {
      "metadata": ["required_fields", "format_validation"],
      "structure": ["element_presence", "element_order"],
      "business": ["business_rules", "consistency_checks"],
      "engineering": ["engineering_standards", "calculations"],
      "graph": ["entity_integrity", "relationship_validity"],
      "quality": ["completeness", "accuracy_thresholds"]
   }
}
```

**AI Reasoning Profile** defines how AI interacts with document type:

```json
{
   "question_types": ["equipment_location", "line_routing", "control_loop", "valve_location", "instrument_function"],
   "reasoning_level": "technical",
   "preferred_context": ["title_block", "equipment_tags", "process_flow"],
   "requires_graph": true,
   "requires_multimodal": true,
   "preferred_chunk": "sheet",
   "citation_priority": ["equipment", "instrument", "valve"]
}
```

**Note**: For example, AI can answer equipment, line routing, control loop, valve location, and instrument function from P&IDs, but it cannot answer operating procedures.

#### 5. Knowledge Relationships

**Relationship Types** define typed relationships between documents:

```
relationships
   produced_from
   validated_by
   references
   implements
   supersedes
   derived_from
   contains
   linked_to
   verified_against
   governs
```

#### 6. Lifecycle & Governance

**Lifecycle** defines document lifecycle management:

```json
{
   "lifecycle_stage": ["draft", "issued_for_review", "issued_for_construction", "as_built", "superseded", "archived"],
   "revision_strategy": "sequential",
   "revision_date": "ISO 8601",
   "revision_description": "required"
}
```

**Governance** defines ownership and security:

```json
{
   "owner": "discipline_lead",
   "confidentiality_default": "internal",
   "approval_workflow": "standard"
}
```

#### 7. Capabilities & Extensions

**Capabilities** defines what operations this document type supports (placeholder for future definition).

**Extension Points** defines custom parsers, validators, and other extensions (placeholder).


### B2.2 Registry workflow

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

## B3. Ontology Hierarchy for EPC RAG System

For an enterprise RAG system (especially Engineering, EPC, Oil & Gas, Pharma, Manufacturing), document types are enriched into a knowledge ontology instead of just a lookup table.

**Cross-Reference**: For detailed document type definition structure, see B2.1 §Unified Document Type Definition.

### B3.1 Document Class, Document Type, and Document Family

**Document Class**: different projects may share same document classes. Document Class should be defined for a project.
```
Document Class
      ├── Drawing
      ├── Specification
      ├── Calculation
      ├── Manual
      ├── Datasheet
      ├── Register
      ├── Report
      └── Procedure
```

**Document Type** should be categorized into a hierarchy and a Document Type can be linked to a Document Class. A sample is given below. The schema definition for Document Type should be expandible and shall not be hard coded in EKS system.

`Document Type ID` should be considered.

```
│
├── Drawing
│   ├── PFD
│   ├── P&ID
│   ├── Plot Plan
│   ├── Equipment Layout
│   ├── GA Drawing
│   ├── Isometric
│   ├── Hook-up Drawing
│   ├── Loop Drawing
│   ├── Single Line Diagram
│   ├── Wiring Diagram
│   └── Cause & Effect Matrix
├── Specification
│   ├── Process Specification
│   ├── Equipment Specification
│   ├── Material Specification
│   ├── Instrument Specification
│   ├── Electrical Specification
│   └── Civil Specification
├── Datasheet
│   ├── Pump Datasheet
│   ├── Valve Datasheet
│   ├── Instrument Datasheet
│   ├── Heat Exchanger Datasheet
│   └── Compressor Datasheet
├── Calculation
│   ├── Hydraulic Calculation
│   ├── Relief Valve Calculation
│   ├── Stress Calculation
│   └── Structural Calculation
├── Report
│   ├── Design Report
│   ├── Inspection Report
│   ├── FAT Report
│   ├── SAT Report
│   └── Test Report
├── Manual
│   ├── O&M Manual
│   ├── Installation Manual
│   ├── Maintenance Manual
│   └── Vendor Manual
├── Register
│   ├── Line List
│   ├── Equipment List
│   ├── Instrument Index
│   ├── Cable Schedule
│   └── I/O List
└── Procedure
    ├── Operating Procedure
    ├── Shutdown Procedure
    ├── Commissioning Procedure
    ├── Inspection Procedure
    └── Maintenance Procedure
```

**Document Family** can group related document from related disciplines, which becomes useful for semantic search. Such as:
```
Drawing
├── Process Drawing
│   ├──PFD
│   ├──P&ID
│   └──Utility Flow Diagram
├── Instrument Drawing
│   ├──Loop Drawing
│   ├──Hook-up Drawing
│   └──Wiring Diagram
├── Electrical Drawing
│   ├──SLD
│   ├──Lighting Layout
│   └──Cable Routing
└── Mechanical Drawing
    ├──GA
    ├──Fabrication
    └──Assembly
```

### B3.2 Document Type Registry

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

### B3.3 File Type Registry

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
- `file_type` column in registry (B4 table) stores extension for format tracking.

### B3.4 Element Type Registry

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

## B4. Database Schema

**Table**: `documents`  
**Backend**: DuckDB (`output/eks_registry.db`)  
**Created by**: `_init_db()` on first instantiation (`CREATE TABLE IF NOT EXISTS`)  
**Schema source**: [`eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) v1.8.0 — 54 columns  

**Primary key**: `id` (UUID v4, system-generated per I186). Business key `(document_number, revision)` is indexed separately via `idx_doc_business_key` for fast lookup. The old `{document_number}-{revision}` format is retired — each call to `register_document()` now generates a new UUID unconditionally, controlled by the I185 three-tier check (key lookup → hash match → hash mismatch/supersedes) in `FileScanner.register_placeholders()`.

**Source codes**:
- `Auto` = Automatically extracted by the Phase 1 pipeline (parsers, filename scanner, FilePropertyExtractor, StructureDetector, or system logic)
- `Manual` = Requires human input (planned for Phase 5 verification dashboard)
- `System` = Set by internal pipeline logic (not from file content)

### Schema to Unified Document Type Definition Mapping

The database schema columns map to the unified document type definition structure (B2.1) as follows:

| B2.1 Domain | Schema Columns | Description |
|:----------- |:-------------- |:----------- |
| Identity & Classification | `document_type`, `document_number`, `revision`, `project_number`, `area`, `discipline`, `department` | Document identity and classification fields |
| Structural Characteristics | `page_count`, `total_sheets` | Document structure metadata |
| Document Semantics | `asset_tags`, `references_documents` | Semantic entities and relationships |
| Processing Profiles | `extract_status`, `extraction_confidence`, `extraction_notes` | Extraction and validation results |
| Knowledge Relationships | `supersedes`, `superseded_by`, `references_documents` | Document relationship edges |
| Lifecycle & Governance | `lifecycle_stage`, `revision_date`, `revision_description`, `project_phase`, `contract_package`, `issued_date`, `responsible_engineer`, `vendor_name`, `originator_company`, `security_class` | Lifecycle and governance fields |
| Capabilities & Extensions | *(none in Phase 1)* | Future extension points |

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

### B4.1. Ontology Mapping (Knowledge Graph Triggers)

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

## B5. Function Reference

### B5.1 `DocumentRegistry.__init__(logger, db_path=None)`

Initialises the registry. Implements **Automatic Schema Migration**:

1. **`_init_db()`** — Creates `documents` and `document_elements` tables using DDL auto-generated from `eks_doc_base_schema.json` via `SchemaToDDL`. Creates schema indexes (`idx_doc_business_key`, etc.).
2. **`_migrate_schema()`** — Checks for missing columns vs. schema definitions and executes `ALTER TABLE ADD COLUMN` to upgrade existing databases without data loss. Also runs NOT NULL constraint diagnostics on project-metadata columns (which should be nullable; reports schema drift if NOT NULL is misapplied).
3. **`_migrate_ids_to_uuid()` (I186)** — One-time migration: converts existing business-key-derived ids (e.g. `DWG-001-A`) to pure UUID v4 format. Steps: (a) add temporary `_old_id` column with current values, (b) generate new UUID for each non-UUID row, (c) update FK references in `document_elements` table, (d) drop temporary column. Idempotent — skips if all ids are already UUID format (36 chars with hyphens).

### B5.2 `DocumentRegistry.register_document(metadata) → str`

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

### B5.3 `DocumentRegistry.get_document(doc_number, revision=None) → dict | None`

Retrieve metadata for a specific document. If `revision` is `None`, returns the latest revision (`is_latest = TRUE`).

### B5.4 `DocumentRegistry.get_latest_by_key(doc_number, revision) → dict | None`

Retrieve the most-recently-registered (`is_latest = TRUE`) row for a given `(document_number, revision)` pair. Introduced with I186 UUID migration to provide the authoritative "current" row when multiple rows share the same composite key due to content changes.

### B5.5 `DocumentRegistry.list_documents(filters, latest_only=True, order_by=None) → list[dict]`

List documents with optional filtering (`COLUMN_ALLOWLIST` validated) and SQL-level sorting. Default: latest-only.

### B5.6 `DocumentRegistry.update_document_status(doc_id, status, confidence=None, notes=None, extra_properties=None) → bool`

Update document extraction status. Features:
- **I184 diff logging**: Before executing UPDATE, queries current row and compares extraction-related fields (`DIFF_TRACK_FIELDS`). Changes are serialized as `[DIFF] {"field": {"old": ..., "new": ...}}` and prepended to `extraction_notes`.
- **Dynamic extra properties**: Accepts `extra_properties` dict to update additional registry columns (e.g. `file_size`, `file_hash`, `embedded_title` from `FilePropertyExtractor`). Only keys present in `COLUMN_ALLOWLIST` are applied.
- **Retry**: Uses `_with_retry` for safe concurrent access (DuckDB locking).

### B5.7 `DocumentRegistry.sync_schema() → dict`

Synchronize database schema with JSON schema definitions. Compares current DB columns against schema and applies any missing columns via `ALTER TABLE ADD COLUMN`. Creates missing indexes. Returns summary dict with keys: `documents_added`, `document_elements_added`, `indexes_created`.

### B5.8 `DocumentRegistry.store_elements(doc_id, elements) → int`

Insert structural elements for a document into `document_elements` table. Each element has: `doc_id`, `element_type`, `element_id`, `title`, `content`, `confidence`, `source`. Returns count inserted. Called by `PipelineOrchestrator` after `StructureDetector` analysis.

### B5.9 `DocumentRegistry.get_elements(doc_id) → list[dict]`

Retrieve all structural elements for a document, ordered by `doc_id, element_type`.

### B5.10 `DocumentRegistry.get_elements_by_type(doc_id, element_type) → list[dict]`

Retrieve structural elements of a specific type for a document.

### B5.11 `DocumentRegistry.delete_elements(doc_id) → int`

Delete all structural elements for a document. Returns count deleted.

---

## B6. Extraction & Verification Workflow

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

## B7. Document Registry Establishment Summary (TWRP Project)

### B7.1. Existing Data Assets (`eks/data/twrp/`)

| Category | Contents | Count/Size |
|----------|----------|------------|
| **Engineering Drawings (PDF)** | Civil (C), Electrical (E), Instrumentation (I), Piping (P), Structural (S) | 100+ PDFs across Volume 5 Part-IA & Part-IB |
| **CAD Drawings (DGN)** | MicroStation DGN files | 6 files (Part-II) |
| **Structured Asset Datadrop** | `Datadrop Summary.xlsx` (7 sheets, 7,681 plant items) | 1.3 MB |

### B7.2. Establishment Workflow

**Phase 1 — Foundation (✅ COMPLETE — T1.7, T1.8, T1.21, T1.22):**

1. **Registry Initialization** — `DocumentRegistry()` auto-creates `eks/output/eks_registry.db` with full schema (54 columns as of v1.8.0). DDL is auto-generated from JSON schema via `SchemaToDDL`. Schema migration adds missing columns on subsequent runs (non-destructive).

2. **Parser Plug-ins** — PDF, DOCX, XLSX parsers extract embedded metadata (`created_by`, `embedded_title`, `embedded_subject`, `embedded_created_date`, `embedded_modified_date`, `embedded_creator_app`, `embedded_producer`, `embedded_keywords`, `embedded_sheet_count`, `embedded_revision_number`, `page_count`) + OS-level file properties (`file_size`, `file_hash`, `file_created_at`, `file_modified_at`) via `FilePropertyExtractor` (Appendix J). DWG/DGN parsers are stubs (OS-only extraction).

3. **Filename Parsing** — Schema-driven `FilenameParser` (Appendix I) extracts `project_number`, `area`, `document_type`, `discipline` from delimited filenames (e.g. `131101-XXX-DWG-PI-0001_A.pdf`). Handles revision suffix stripping, segment validation against `document_type_registry`, and fallback resolution for unrecognised patterns.

4. **Structure Detection** — `StructureDetector` analyses page 1 of each PDF to detect 8 element types (cover_page, revision_table, section, table, image, link, legend, note), classifies cover type (A–E), and performs best-effort `asset_tags` regex detection from the title block. Results are persisted to the `document_elements` table via `registry.store_elements()` for downstream health scoring and Phase 2/3 knowledge graph population.

5. **Health Scoring** — `HealthScorer` computes a 6-dimensional composite score per document (completeness 20% + extraction_confidence 20% + structural_completeness 20% + source_quality 15% + xref_quality 15% + consistency 10%). Structural completeness dimension uses `element_expectations` thresholds from B3.4. Score tiers map to pipeline actions (auto_register → manual_entry).

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

### B7.3. Next Steps for TWRP Ingestion (Require Approval)

| Step | Action | Dependencies |
|------|--------|--------------|
| 1 | Define ingestion script to walk `eks/data/twrp/spec/` | Phase 1 registry + parsers ready |
| 2 | Implement cover-sheet metadata extraction (LLM/regex) | Phase 3 extractors |
| 3 | Map `asset_tags` → datadrop `keytag` for graph edges | Phase 3 asset graph |
| 4 | Configure `document_type` → ontology class mapping | `eks_ontology_config.json` (T1.29 ✅) |
| 5 | Build Manual Verification UI | Phase 5 |

---

## B8. References

1. [`registry.py`](../engine/core/registry.py) — DocumentRegistry implementation
2. [Phase 1 Foundation Workplan](phase_1_foundation_workplan.md) — T1.21, T1.22
3. [Phase 3 Knowledge Graph Workplan](phase_3_knowledge_graph_workplan.md) — T3.21 (Extraction)
4. [Phase 5 UI Integration Workplan](phase_5_ui_integration_workplan.md) — T5.18 (Verification UI)
5. [Appendix B Alignment Fix Workplan](appendix_b_alignment_fix_workplan.md) — v2.1.0 alignment changes
