# Appendix B — Document Registry

**Version**: 2.1.6  
**Last Updated**: 2026-08-13  
**Phase**: 1 — Foundation  
**Status**: ✅ Official  
**Related Files**:
- [`eks/engine/core/registry.py`](../engine/core/registry.py)
- [`eks/engine/core/revision.py`](../engine/core/revision.py)
- [`eks/engine/core/config_registry.py`](../engine/core/config_registry.py)
- [`eks/config/schemas/eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) — Document column definitions (v1.17.0)
- [`eks/config/schemas/eks_doc_setup_schema.json`](../config/schemas/eks_doc_setup_schema.json) — Table declarations, extraction rules, health scoring
- [`eks/config/schemas/eks_doc_config.json`](../config/schemas/eks_doc_config.json) — Element expectations, score tiers (v1.12.0)
- [`eks/config/schemas/eks_document_type_schema.json`](../config/schemas/eks_document_type_schema.json) — 5-section carrier (classes/types/family/bindings/templates, v2.3.0)
- [`eks/config/schemas/eks_ontology_config.json`](../config/schemas/eks_ontology_config.json) — Document class hierarchy (§C4, v1.7.0)
- [`eks/config/schemas/eks_export_view_config.json`](../config/schemas/eks_export_view_config.json) — Default export view values SSOT (I308, v1.1.0)
- [`eks/engine/core/schema_to_ddl.py`](../engine/core/schema_to_ddl.py) — `generate_view_ddl()` renders persistent `v_*` export views (I308)

**Sub-Appendices**:
- [Appendix B.1 — Cross-Relationship Chart](appendix_b.1_cross_relationship_chart.md) — Complete entity relationships, DB table relationship map, FK closure paths, and cross-document gap analysis
- [Appendix B.2 — DB Table Design](appendix_b.2_db_table_design.md) — All 42 table definitions (39 definition + 3 pipeline runtime), columns, types, constraints, schema provenance, load order, and the I308 export view model (3 persistent `v_*` views)

**Migration Note**: This version implements the unified document type definition structure (B2.1) that merges the previous B2.1 Registry Structure and B3.2 Enrich Document Type sections. The content previously in B3.2 has been integrated into B2.1. Previous version archived as `archive/appendix_b_document_registry_v2.0.0_2026-08-04.md`. v2.1.1 (I282): the concept layer (`document_type_concepts`) is removed from the carrier; bindings reference `class_id`; document classes are the 8 shape-only entries in `document_classes`. v2.1.3 (I280): §2 Structural Characteristics implemented via per-class/type `structural_profile` (carrier v2.2.0, base v1.16.0). v2.1.5 (I283): four-level Class→Type→Template→Element detection implemented — `element_type_code` 8→11 (`title_block`/`grid`/`signature_block`), template `expected_elements` is the element-set SSOT (structural_profile = capability metadata only), cover type schema-first (detection fallback only when unavailable), all detectors gated by `expected_elements` (carrier v2.3.0, base v1.17.0, doc config v1.12.0). v2.1.6 (I308 T1.286): export step upgraded to the schema-driven **export view model** — 3 persistent DuckDB views (`v_discovery_inventory`, `v_extraction_results`, `v_review_flags`) rendered by `generate_view_ddl()` from `eks_export_view_config.json` v1.1.0 (view id / source table / is_latest filter / ordered columns / file base name / sheet name / formats), view id = `export_artifact.artifact_type`, `documents.flag_reason` materialized, missing view config → fail-fast S-C-S-0312, version-control columns pruned from exports (GAP-016 two-tier gap RESOLVED). See U295/TL056.

---

## Table of Contents

- [Revision History](#revision-history)
- [Sub-Appendices](#sub-appendices)
  - [B.1 — Cross-Relationship Chart](appendix_b.1_cross_relationship_chart.md)
  - [B.2 — DB Table Design](appendix_b.2_db_table_design.md)
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
  - [B5.1 `DocumentRegistry.__init__(logger, db_path=None, pre_generated_ddl=None)]
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
| 2.1.1 | 2026-08-05 | Franklin Song | **DOCS SYNC**: Aligned all sections to code/schema reality post I255/I264/I274/I275/I276/I277/I278/I279. Updated B2.1 tree with Phase 1 scope annotations; fixed B2.2 workflow diagram (added `_ensure_schema_version()`, fixed `COLUMN_ALLOWLIST` description); expanded B3.2 table to 15 codes with project-binding model and three-section SSOT reference; added `format_category` column to B3.3; updated B3.4 `element_expectations` source reference to `document_templates`; updated B4 schema version to v1.13.0; fixed B4.1 ontology trigger routing description; added `_ensure_schema_version()` + `pre_generated_ddl` to B5.1; updated B6 Phase 1 steps 2/3/6 for FilenameParser auto-detect/format_category/column-scope; updated B7.2 steps 3/4/7; added revision history entries for I264/I275–I279. Retired `appendix_b_document_registry.md` (original). |
| 2.1.2 | 2026-08-05 | opencode | **I282 T1.236**: Documented removal of the concept layer (`document_type_concepts`) and the migration to the 5-section class-based carrier (`document_classes`/`document_types`/`document_family`/`project_document_types`/`document_templates`). Updated B2.1 Identity fields (class_id/type_id/family_id), B3.1 tree note, B3.2 binding tables (Concept→Class), document class list (8 classes closing I282), B4.1 ontology trigger, and related-file refs (v1.14.0 / v1.7.0). |
| 2.1.3 | 2026-08-06 | opencode | **I280 T1.221**: Documented B3.2 sub-object implementation in B2.1 §2 Structural Characteristics — `structural_profile` (11 fields) populated on 8 classes / 28 types (carrier v2.2.0, base v1.16.0), SSOT hierarchy + `structural_profile_for()` resolution, extraction/retrieval/validation profile refs, Phase-3 stubs, and per-class profile table. |
| 2.1.3 | 2026-08-05 | opencode | **I281 T1.223/T1.224**: Documented the 11-type processing profile registry (Domain 4). Profile VALUES now live in `eks_processing_config.json` (SSOT §9/§16) — `extraction_profiles` (5 `technip_*`) migrated from `eks_doc_config.json#/parsing_profiles`; core `eks_base_schema.json` holds shape-only defs (`processing_profile_registry_def` + 11 per-type defs incl. `extraction_profile_def` superset); core `eks_setup_schema.json` `processing_profiles` declares the `{type}_profiles` sections; updated Phase 1 scope note. Related-file refs (base v1.16.0 / setup v1.10.0 / doc config v1.10.0). |
| 2.1.4 | 2026-08-07 | opencode | **I283 RESUMMARIZED (T1.230/T1.231)**: Four-level Class→Type→Template→Element detection model documented. Element-set SSOT = template `expected_elements` (structural_profile = capability metadata only); `element_type_code` expands 8→11 with `title_block`/`grid`/`signature_block` detectors; `classify_cover_type()` keyword classification retired — cover type schema-first from carrier `document_templates[template_id].cover_type`, detection fallback only when unavailable; Phase 1 gates all detectors by `expected_elements` (link/note placeholders); detection output feeds health score (I284) from metadata sources only. See U270. |
| 2.1.5 | 2026-08-07 | opencode | **I283 T1.230/T1.231**: Four-level Class→Type→Template→Element detection IMPLEMENTED. `element_type_code` 8→11 (`title_block`/`grid`/`signature_block`) in doc base v1.17.0; `element_type_registry` 11 entries (doc config v1.12.0); carrier v2.3.0 — `twrp_drawing` (A) + `twrp_pandid` (B) `expected_elements` → 8 (`cover_page`/`revision_table`/`section`/`image`/`link`/`title_block`/`grid`/`signature_block`), `threshold` 5; `StructureDetector.detect()` gated by template `expected_elements` (all 11 detectors incl. link/note placeholders) + schema-first `cover_type` param, `classify_cover_type()` retired; `resolve_cover_type()` → Optional (None = schema unavailable → detection fallback); detection output wired to `HealthInput.cover_type` (I284 base); `valid_element_types` derived from base enum. See U271/TL046. |
| 2.1.6 | 2026-08-13 | AI Assistant | **I308 T1.282–T1.286**: Export upgraded to schema-driven **export view model**. `eks_export_view_config.json` v1.1.0 defines the 3 default views (`discovery_inventory`, `extraction_results`, `review_flags`) — view_id, source_table, `filter` (is_latest = TRUE), ordered `columns`, `file_base_name`, `sheet_name`, `formats`; `schema_to_ddl.generate_view_ddl()` renders idempotent `CREATE OR REPLACE VIEW v_<view_id>` created in `_init_db()` AFTER the I311 migration gate; `export_artifact.artifact_type` = view_id; `documents.flag_reason` materialized at ingest (`core/flag_utils`); version-control columns pruned from exports; missing view config → fail-fast S-C-S-0312; hardcoded column lists + `_fallback` dicts removed (I274/I276 cleanup); GAP-016 (two-tier gap) RESOLVED. Updated §B6 step 6 + B7.2 step 7 + Related Files + Sub-Appendix B.2 (EXPORT VIEW MODEL). See U295/TL056. |

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

> **Phase 1 Scope Note**: Domains 1 (Identity & Classification — partial), 2 (Structural Characteristics — ✅ per-class/type profile via `structural_profile`, I280; template-level `expected_elements` also present; I283 resummarized 2026-08-07 — four-level Class→Type→Template→Element detection, element-set SSOT = template `expected_elements`, `element_type_code` 8→11, cover type schema-first, Phase 1 gates all detectors, detection feeds health score from metadata-only sources), 4 (Processing Profiles — Extraction/Validation containers + config SSOT via I281; values in `eks_processing_config.json`), 5 (Knowledge Relationships — registry columns only), and 6 (Lifecycle & Governance) are implemented in Phase 1. Domains 3 (Document Semantics — 🔷 Phase 3), 4 remaining profiles (Chunking, Retrieval, Indexing, AI Reasoning, Graph Mapping, Embedding, Asset, Ontology, Prompt — 🔷 Phase 2/3), and 7 (Capabilities & Extensions — 🔷 future) are planned. See I280, I281, I283, I284 for open gaps.

```
Document Type Life Cycle Definition
├── 1. Identity & Classification  [✅ Phase 1 — partial]
│      ├── Identity (class_id, type_id, label, ontology_class, family_id, display_name, description, version)
│      ├── Classification (document_class, document_family, discipline, category, project_phase, lifecycle_stage)
│      └── Metadata (required, optional fields)
│          Note: class_id/label/ontology_class/common_rules implemented in document_class_def (shape-only, I282).
│          family_id and nested parent_class_id supported at runtime via get_class_ancestry(); type hierarchy ✅ I282 (8 classes / 28 types); detection layer 🔷 I283 (Class→Type→Template→Element, resummarized 2026-08-07).
│
├── 2. Structural Characteristics  [✅ per-class/type profile — I280]
│      ├── Document Structure (cover_page, revision_table, title_block, signature_block, multi_sheet — structural_profile on classes/types, I280)
│      ├── Content Organization (section_based, drawing_based — structural_profile, I280; expected_elements in document_templates)
│      └── Visual Elements (contains_callouts, contains_symbols, legend, grid — structural_profile, I280)
│
├── 3. Document Semantics  [🔷 Phase 3 — not implemented]
│      ├── Semantic Entities (semantic_entities list)
│      ├── Semantic Relationships (semantic_relationships list)
│      ├── Semantic Constraints (semantic_constraints list)
│      └── Business/Engineering Objects (business_objects, engineering_objects)
│
├── 4. Processing Profiles  [✅ Extraction/Validation containers + config — Chunking/Retrieval/Indexing/AI/Graph Mapping/Embedding/Asset/Ontology/Prompt 🔷 I281]
│      ├── Extraction Profile [✅] (extraction_profiles in eks_processing_config.json — 5 profiles: technip_pdf/docx/dwg/dgn/xlsx; I281 migrated from eks_doc_config.json#/parsing_profiles)
│      ├── Chunking Profile [🔷 Phase 2] (chunk_strategy, chunk_size, anchor_priority, embedding_scope)
│      ├── Retrieval Profile [🔷 Phase 2] (embedding_model, reranker, vector/graph/metadata/keyword weights)
│      ├── Validation Profile [🔷 I284] (validation_layers: metadata/structure/business/engineering/graph/quality; per-type tier columns — column-value layer hardcoded in health_scorer.py, I284)
│      ├── Indexing Profile [🔷 Phase 3] (optional)
│      ├── AI Reasoning Profile [🔷 Phase 3] (question_types, reasoning_level, requires_graph)
│      ├── Graph Mapping Profile [🔷 Phase 3] (optional, future — stub fields: entity_mapping, relationship_mapping, tag_type_mapping, document_type_mapping, node_label_strategy, edge_definition)
│      ├── Embedding Profile [🔷 Phase 2/3]
│      ├── Asset Profile [🔷 Phase 3]
│      ├── Ontology Profile [🔷 Phase 3]
│      └── Prompt Profile [🔷 Phase 3]
│          Note: profile VALUES live in eks_processing_config.json (SSOT §9/§16, I281);
│          core eks_base_schema.json holds shape-only defs (processing_profile_registry_def
│          + 11 per-type defs); core eks_setup_schema.json processing_profiles declares the
│          {type}_profiles sections.
│
├── 5. Knowledge Relationships  [✅ registry columns only — graph edges 🔷 Phase 3]
│      └── Relationship Types (supersedes, superseded_by, references_documents — in DB schema)
│
├── 6. Lifecycle & Governance  [✅ Phase 1]
│      ├── Lifecycle (lifecycle_stage, revision_date, revision_description — in DB schema)
│      └── Governance (originator_company, security_class, responsible_engineer — in DB schema)
│
└── 7. Capabilities & Extensions  [🔷 future]
      ├── Capabilities (what operations this document type supports)
      └── Extension Points (custom parsers, custom validators, etc.)
```

#### 1. Identity & Classification

**Identity** defines immutable properties of Document Type:

```json
{
   "type_id": "PID_DRAWING",
   "label": "P&ID Drawing",
   "short_name": "P&ID",
   "ontology_class": "PID_Drawing",
   "class_id": "Drawing",
   "family_id": "Process Drawing",
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

**Structural Characteristics** define the physical layout, content organization, and visual elements of a document type. **I280 (T1.218–T1.220)** implemented a per-class/per-type `structural_profile` (11 fields) with SSOT in the carrier (`eks_document_type_schema.json` v2.2.0):

**SSOT hierarchy** (resolved by `SchemaLoader.structural_profile_for(type_id, class_id)` in `schema_loader.py`):
1. **Type-level override** — a `document_types[].structural_profile` entry (present on all 28 types) wins when it differs from the class default.
2. **Class-level default** — the `document_classes[].structural_profile` entry (present on all 8 classes) supplies the base profile; types without an explicit field inherit it.
3. **Schema shape** — `structural_profile_def` in `eks_doc_base_schema.json` v1.16.0 (11 fields; presence fields use `required|optional|absent` enums; flags are boolean). `additionalProperties: false` preserved on `document_class_def` / `document_type_def`.
4. **Projection** — `_derive_doc_type_projection()` attaches `structural_profile` to flat `document_type_registry` entries (validated via `document_type_entry_def`).

Presence fields (`cover_page`, `revision_table`, `title_block`, `legend`, `grid`, `signature_block`) use `required|optional|absent`; flags (`multi_sheet`, `drawing_based`, `section_based`, `contains_callouts`, `contains_symbols`) are booleans.

**Profile refs**: `extraction_profile_ref` (implemented, resolves to `eks_processing_config.json#/extraction_profiles` ids — I281), `retrieval_profile_ref` / `validation_profile_ref` (schema-declared, 🔷 no values yet). Phase-3 stubs `document_semantics_def` / `ai_profile_def` / `knowledge_relationships_def` are declared in the base schema (shape-only, no values).

**Current carrier population (8 classes / 28 types)**:

| Class | structural_profile highlight | extraction_profile_ref |
| ----- | --------------------------- | --------------------- |
| Drawing | drawing_based, multi_sheet, contains_symbols, legend/grid required-optional | `technip_pdf` |
| Specification | section_based, title_block required, no symbols | `technip_docx` |
| Manual | section_based, cover_page required | `technip_docx` |
| Report | section_based, cover_page required | `technip_docx` |
| Procedure | section_based, cover_page required | `technip_docx` |
| Datasheet | cover_page optional, embedded-table oriented, not drawing_based | `technip_xlsx` |
| Register | cover_page/revision_table optional, not drawing_based | `technip_xlsx` |
| Calculation | title_block required, not drawing_based | `technip_pdf` |

**Type-level overrides**: e.g. `PID_DRAWING` forces `legend: required` + `contains_symbols: true`; `ISOMETRIC` is single-sheet (`multi_sheet: false`) while class default stays `multi_sheet: true`. Presence fields not explicitly set on a type inherit the class value.

**Document Structure** defines the physical layout (template-level `expected_elements`/`threshold` remain in `document_templates`):

```json
{
   "title_block": "required",
   "revision_table": "required",
   "cover_page": "required",
   "signature_block": "required",
   "multi_sheet": true
}
```

**Content Organization** defines how content is organized:

```json
{
   "section_based": false,
   "drawing_based": true
}
```

**Visual Elements** defines visual components present:

```json
{
   "contains_callouts": true,
   "contains_symbols": true,
   "legend": "required",
   "grid": "optional"
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

**Capabilities** defines what operations this document type supports (🔷 placeholder for future definition).

**Extension Points** defines custom parsers, validators, and other extensions (🔷 placeholder).


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

**Implemented registry (I282, `eks_document_type_schema.json` v2.1.0)**: The carrier `document_types` section holds 28 types across the 8 classes (e.g. `PID_DRAWING`, `PFD`, `PLOT_PLAN`, `GA_DRAWING`, `ISOMETRIC`, `LOOP_DRAWING`, `SLD`, `WIRING_DIAGRAM`, `CAUSE_EFFECT` under `Drawing`; 6 `Specification` types; 5 `Datasheet` types; `CALCULATION`; `VENDOR_MANUAL`/`OPERATION_MANUAL`; `LINE_LIST`/`EQUIPMENT_LIST`/`INSTRUMENT_INDEX`; `REPORT`; `PROCEDURE`). `document_family` holds the 4 drawing families (Process/Instrument/Electrical/Mechanical Drawing). Each type declares `class_id` (required) and optional `family_id`. Base-schema defs are shape-only — no value enums (SSOT §9/§16).

### B3.2 Document Type Registry

**SSOT (I279/I282/I280)**: Document type codes are defined in `eks_document_type_schema.json` v2.2.0 — the five-section runtime carrier (`document_classes` / `document_types` / `document_family` / `project_document_types` / `document_templates`). The `document_type_registry` section was removed from `eks_doc_config.json` v1.9.0, and the former concept layer (`document_type_concepts`) was **removed** in v2.1.0 (I282) — bindings reference `class_id` directly. v2.2.0 (I280) adds the B3.2 sub-objects: `structural_profile` on all 8 classes / 28 types and `extraction_profile_ref` on all 8 classes. Codes are **project-bound**: the same class (e.g. `Drawing`) may use different local codes in different projects (`DWG` in project 131101, `DR` in project 131242).

**Project 131101 bindings**:

| Local Code | Class | Ontology Class | Template | Format | Expected File Types |
|:---------- |:------- |:-------------- |:-------- |:------ |:------------------- |
| `DWG` | `Drawing` | `Drawing` | `twrp_drawing` | print | `pdf` |
| `PI-PID` | `Drawing` | `PID_Drawing` | `twrp_pandid` | print | `pdf`, `dgn` |
| `SPC` | `Specification` | `Specification` | `twrp_spec_c` | print | `pdf`, `docx` |
| `DS` | `Datasheet` | `Datasheet` | `twrp_datasheet_e` | print | `pdf`, `xlsx` |
| `MAN` | `Manual` | `Manual` | `twrp_manual_d` | print | `pdf`, `docx` |
| `OM` | `Manual` | `OpsManual` | `twrp_manual_d` | print | `pdf`, `docx` |
| `RPT` | `Report` | `Report` | `twrp_report_e` | print | `pdf`, `docx` |
| `CAD` | `Drawing` | `CAD_Drawing` | `twrp_drawing` | native | `dwg` |

**Project 131242 bindings**:

| Local Code | Class | Ontology Class | Template | Format | Expected File Types |
|:---------- |:------- |:-------------- |:-------- |:------ |:------------------- |
| `DR` | `Drawing` | `Drawing` | `twrp_drawing` | print | `pdf`, `docx` |
| `SP` | `Specification` | `Specification` | `twrp_spec_c` | print | `pdf`, `docx` |
| `CL` | `Specification` | `Specification` | `twrp_spec_c` | print | `pdf`, `docx` |
| `BQ` | `Specification` | `Specification` | `twrp_spec_c` | print | `pdf`, `xlsx` |
| `VI` | `Manual` | `OpsManual` | `twrp_manual_d` | print | `pdf` |
| `M3` | `Drawing` | `Drawing` | `twrp_drawing` | print | `pdf` |
| `QA` | `Report` | `Report` | `twrp_report_e` | print | `pdf`, `docx` |

**Document classes** (in `document_classes`): `Drawing`, `Specification`, `Datasheet`, `Calculation`, `Manual`, `Register`, `Report`, `Procedure` — the 8 core classes (I282, closing the I282 gap that previously omitted `CALCULATION`/`REGISTER`/`PROCEDURE`). Each class's `ontology_class` resolves against `eks_ontology_config.json` at load time.

**Alignment**:
- Ontology class hierarchy per Appendix C §C4: `Drawing` -> `PID_Drawing`; `Specification` covers `SPC`/`DS`/`SP`/`CL`/`BQ`; `Manual` covers `MAN`/`OM`/`VI`.
- TWRP assets per §B7.1: 100+ PDF drawings (DWG/PI-PID), 6 DGN drawings (PI-PID), specifications, manuals, reports.
- Phase 1 filename parsing extracts local code; Phase 3 cover sheet parsing extracts it -> class -> ontology class assignment.

### B3.3 File Type Registry

Maps source file extensions to parser implementations (Phase 1 plug-in architecture) and MIME types. `format_category` (I279 T1.215) distinguishes native formats (rich embedded metadata available) from PDF prints (flattened â€” only OS properties + cover-page OCR). This field drives I275 column scope, I276 two-axis parser routing, and I277 extraction method gating.

| Extension | Display Name | Parser Class | Format Category | TWRP Use | MIME Type |
|:--------- |:------------ |:------------ |:--------------- |:-------- |:--------- |
| `pdf` | PDF Document | `eks.engine.parsers.pdf_parser.PDFParser` | `print` | Drawings (100+), Specs, Manuals, Reports | `application/pdf` |
| `dgn` | DGN Drawing | `eks.engine.parsers.dgn_parser.DGNParserStub` | `native` | CAD Drawings (6) | `image/vnd.dgn` |
| `docx` | Word Document | `eks.engine.parsers.docx_parser.DOCXParser` | `native` | Specs, Manuals, Reports | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| `xlsx` | Excel Workbook | `eks.engine.parsers.xlsx_parser.XLSXParser` | `native` | Data Sheets, Datadrop | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` |
| `dwg` | AutoCAD Drawing | `eks.engine.parsers.dwg_parser.DWGParserStub` | `native` | Native CAD (CAD local code) | `image/vnd.dwg` |

**Alignment**:
- `format_category` stored in `eks_doc_config.json` -> `file_type_registry[].format_category` (I279 T1.215).
- Phase 1 implements PDF, DOCX, XLSX parsers fully; DWG/DGN are stubs (OS-only extraction, `format_category=native`).
- `file_type` column in registry (B4 table) stores extension for format tracking.

### B3.4 Element Type Registry

Structural element types per Appendix D Â§D7.10, used for structural completeness scoring and Phase 2/3 knowledge graph population.

**SSOT (I279)**: Expected-element counts are defined in `eks_document_type_schema.json` -> `document_templates[template_id].expected_elements`. The `element_expectations` section was removed from `eks_doc_config.json` v1.9.0. Mapping: `local_code` -> project binding -> `template` -> `expected_elements` + `threshold` + `cover_type`.

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
| `title_block` | Drawing title block fields | `regex` | Section anchor | Title-block node | A, B, D, E |
| `grid` | Drawing grid reference system | `regex` | Skip | Grid-coordinate nodes | A, B |
| `signature_block` | Signature/approval block | `regex` | Skip | Approval nodes | A, B |

**Element Expectations by Template (from `document_templates` — I279/I283)**:

| Template | Expected Elements | Threshold | Cover Type | Used By |
|:-------- |:----------------- |:--------: |:----------:|:------- |
| `twrp_drawing` | cover_page, revision_table, section, image, link, title_block, grid, signature_block | 5 | A | DWG, CAD, DR, M3 |
| `twrp_pandid` | cover_page, revision_table, section, image, link, title_block, grid, signature_block | 5 | B | PI-PID |
| `twrp_spec_c` | (none) | 0 | C | SPC, SP, CL, BQ |
| `twrp_datasheet_e` | cover_page, section, table | 2 | E | DS |
| `twrp_manual_d` | cover_page, section | 2 | D | MAN, OM, VI |
| `twrp_report_e` | cover_page, section, table | 2 | E | RPT, QA |

The `threshold` is the minimum detected element types for structural completeness to reach a passing tier. Cover type `C` (no-cover) skips cover-page detection and `cover_page_element`-based columns entirely (I278).

**Alignment**:
- `structure_detector.py` detects elements and stores in `document_elements` table via `DocumentRegistry.store_elements()`; `detect()` is gated by template `expected_elements` (all detectors, incl. `link`/`note` placeholders) and takes a schema-first `cover_type` param (I283).
- `HealthScorer._build_expected_elements_map()` reads from `document_templates` at runtime (I279 T1.213) — no hardcoded map.
- `EKSColumnProcessor.resolve_cover_type()` reads `document_templates[template_id].cover_type` as SSOT (I278); returns `None` when the schema value is unavailable (detection fallback, I283).
- `SchemaLoader.valid_element_types` is derived from the `element_type_code` enum (11 codes, I283).
- Asset tag detection (`asset_tags`) is best-effort regex from cover page / title block (T1.99.162).

---

## B4. Database Schema

**Table**: `documents`  
**Backend**: DuckDB (`output/eks_registry.db`)  
**Created by**: `_init_db()` on first instantiation (`CREATE TABLE IF NOT EXISTS`)  
**Schema source**: [`eks_doc_base_schema.json`](../config/schemas/eks_doc_base_schema.json) v1.16.0 — 54 columns  

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
| `page_count` | INTEGER | YES | NULL | Auto | **[SSOT]** Total pages (from parser metadata: pdf page count). Single source of truth for page count across EKS. `health_score` only checks if this field is populated (Tier 2 scoring — no copy); `total_sheets` uses this as fallback (priority-chain derived column). I296. |

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
| `total_sheets` | INTEGER | YES | NULL | Auto | Total sheets in multi-sheet drawing set. **Derived column** (Priority-3 per AGENTS.md §8): calculated by ColumnProcessor priority chain (detected sheet count → `page_count` fallback → NULL). Reads from `page_count` SSOT — does not store independently. T1.99.146 / I296. |
| `language` | VARCHAR | YES | `'en'` | System | ISO 639-1 language code. Default `en`. T1.99.146. |
| `vendor_name` | VARCHAR | YES | NULL | Manual | Equipment vendor name for vendor-supplied documents. T1.99.146. |

**Column count summary**: Identity(2) + Project(5) + Document Core(7) + Timestamps(1) + Account(3) + Origin/Security(2) + Asset Tags/Tech(2) + Quality(4) + OS File Props(4) + Embedded Metadata(9) + Document Lifecycle(15) = **54 columns** (v1.8.0 schema).

### B4.1. Ontology Mapping (Knowledge Graph Triggers)

The following registry fields are mapped to Ontology classes and relationships during Phase 3 ingestion:

| Registry Field | Ontology Trigger | Logic / Edge Produced |
| :--- | :--- | :--- |
| `document_type` | `IS_A` | Class Assignment: `document_type` (project-local code) -> project binding -> `class_id` -> `ontology_class` (I279/I282). Maps to `Drawing`, `PID_Drawing`, `Specification`, `Datasheet`, `Manual`, `OpsManual`, `Report`, or `CAD_Drawing`. |
| `document_number` | `SUPERSEDES` | Links revisions of the same number in a time-ordered chain. |
| `asset_tags` | `REFERENCES_ASSET` | Produces M:N edges to `FunctionalObject` (Tag) nodes. |
| `originator_company` | `PRODUCED_BY` | Links Document to a `GovernanceObject` (Company/Entity). |
| `file_type` | `HAS_FORMAT` | Links Document to a `FileFormat` node indicating source format. |
| `references_documents` | `REFERENCES_DOC` | Produces M:N cross-reference edges between Document nodes. T1.99.145. |
| `lifecycle_stage` | `HAS_STAGE` | Links Document to its current lifecycle stage node. Enum: draft/issued_for_review/issued_for_construction/as_built/superseded/archived. T1.99.143. |

---

## B5. Function Reference

### B5.1 `DocumentRegistry.__init__(logger, db_path=None, pre_generated_ddl=None)`

Initialises the registry. Implements **Automatic Schema Migration**:

1. **`_init_db()`** — Creates `documents` and `document_elements` tables using DDL auto-generated from `eks_doc_base_schema.json` via `SchemaToDDL`. Creates schema indexes (`idx_doc_business_key`, etc.).
2. **`_migrate_schema()`** — Checks for missing columns vs. schema definitions and executes `ALTER TABLE ADD COLUMN` to upgrade existing databases without data loss. Also runs NOT NULL constraint diagnostics on project-metadata columns (which should be nullable; reports schema drift if NOT NULL is misapplied).
3. **`_ensure_schema_version()`** (I225) — Creates `_eks_schema_meta` table on first run and stores a hash of the current DDL. On subsequent runs, compares stored hash against current DDL to detect schema drift. Idempotent.
4. **`_migrate_ids_to_uuid()`** (I186) — One-time migration: converts existing business-key-derived ids to pure UUID v4 format. Idempotent — skips if all ids are already UUID format (36 chars with hyphens).

**`pre_generated_ddl`** parameter (I225): when provided by bootstrap P7, schema re-loading from disk is skipped and the pre-generated DDL is used directly. Keys: `documents_ddl`, `elements_ddl`, `indexes`, `definitions`.

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
   - Auto-detects project code per filename via `_detect_pattern()` (I255 T1.157) — no `project_code` constructor parameter. Extracts up to 7 fields: `project_number`, `area`, `document_type`, `discipline`, `sequence_number`, `document_number`, `revision`.
   - Supports per-project patterns (e.g. `131101` for TWRP delimited format: `{project}-{area}-{type}-{disc}-{seq}_rev{rev}.ext`). Project code auto-detected per filename — not passed as constructor argument (I255).

3. **File Property Extraction** (`FilePropertyExtractor`, Appendix J):
   - **OS-level**: `file_size`, `file_hash` (MD5), `file_created_at`, `file_modified_at` via `Path.stat()`.
   - **Parser-embedded metadata**: Routes through format-specific parser `extract_metadata()` → property mapping per `eks_doc_config.json` → `file_property_patterns`.
     - PDF: `author`→`created_by`, `title`→`embedded_title`, `page_count`, `creator`→`embedded_creator_app`, `producer`→`embedded_producer`, etc.
     - DOCX: `author`→`created_by`, `title`→`embedded_title`, `revision`→`embedded_revision_number`, `last_modified_by`→`embedded_last_modified_by`, etc.
     - XLSX: `author`→`created_by`, `sheet_count`→`embedded_sheet_count`, `last_modified_by`→`embedded_last_modified_by`, etc.
     - DGN/DWG: OS-only extraction (`format_category=native`, stub parsers). `format_category` from `file_type_registry` determines extraction mode — native formats support embedded metadata; PDF prints are flattened (I279 T1.215).

4. **Structure Detection** (`StructureDetector`):
   - Analyses parsed PDF text from page 1 to detect element types (11 `element_type_code` values, I283: `cover_page`, `revision_table`, `section`, `table`, `image`, `link`, `legend`, `note`, `title_block`, `grid`, `signature_block`), gated by template `expected_elements`. Cover type resolved schema-first from `document_templates[template_id].cover_type` SSOT (I279/I283; `classify_cover_type()` keyword classification retired); detection fallback only when the schema value is unavailable. Cover type `C` (no-cover templates: SPC/SP/CL/BQ) skips cover-page detection and `cover_page_element`-based columns entirely (I278).
   - Classifies cover type (A–E) based on detected element combinations.
   - Best-effort `asset_tags` regex detection from title block (`COVER_PAGE_PATTERNS["asset_tags"]`).
   - Results persisted to `document_elements` table via `registry.store_elements()`.

5. **Health Scoring** (`HealthScorer`):
   - Computes a 6-dimensional health score (0.0–1.0): completeness (20%), extraction_confidence (20%), structural_completeness (20%), source_quality (15%), xref_quality (15%), consistency (10%).
   - Structural completeness dimension uses `element_expectations` from `eks_doc_config.json` with per-document-type thresholds.
   - Score tiers determine action: auto_register (≥0.90), optional_review (≥0.70), flag_review (≥0.50), mandatory_review (≥0.20), manual_entry (<0.20).

6. **Pipeline Export** (`--export csv|xlsx|both`):
   - **Schema-driven export view model (I308)**: 3 persistent DuckDB views — `v_discovery_inventory` (46 columns: all `x_export` fields minus extraction), `v_extraction_results` (49 columns: all `x_export` fields), `v_review_flags` (12 columns: extraction-quality triage subset + materialized `flag_reason`) — rendered by `generate_view_ddl()` as `CREATE OR REPLACE VIEW v_<view_id>` from `eks_export_view_config.json` v1.1.0, created in `_init_db()` AFTER the I311 migration gate.
   - View id / source table (`documents`) / `filter` (`is_latest = TRUE`) / ordered `columns` / `file_base_name` / `sheet_name` / `formats` all read from the view config — **no hardcoded column lists** (I193/I275 `x_export` → superseded by `columns[]` SSOT; version-control columns `is_latest`/`supersedes`/`superseded_by` pruned).
   - `export_artifact.artifact_type` = view_id; missing view config → **fail-fast** S-C-S-0312 (no partial export). Outputs: `eks/output/discovery_inventory.csv/.xlsx`, `extraction_results.csv/.xlsx`, `review_flags.csv` (one worksheet per view: Discovery / Extraction / Review Flags).

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

3. **Filename Parsing** — Schema-driven `FilenameParser` (Appendix I) auto-detects project code per filename via `_detect_pattern()` (I255) — no constructor `project_code` parameter. Extracts `project_number`, `area`, `document_type`, `discipline` from delimited filenames (e.g. `131101-XXX-DWG-PI-0001_A.pdf`). Handles revision suffix stripping, segment validation against the five-section SSOT carrier (I279/I282), and fallback resolution for unrecognised patterns.

4. **Structure Detection** — `StructureDetector` analyses page 1 of each PDF to detect element types (11 `element_type_code` values, gated by template `expected_elements` — I283), resolves cover type schema-first from `document_templates[template_id].cover_type` SSOT (I279/I283; `classify_cover_type()` retired, detection fallback only when unavailable), and performs best-effort `asset_tags` regex detection from the title block. Cover type `C` (no-cover templates: SPC/SP/CL/BQ) skips cover-page detection and `cover_page_element`-based columns entirely (I278). Results persisted to `document_elements` table via `registry.store_elements()`.

5. **Health Scoring** — `HealthScorer` computes a 6-dimensional composite score per document (completeness 20% + extraction_confidence 20% + structural_completeness 20% + source_quality 15% + xref_quality 15% + consistency 10%). Structural completeness dimension uses `element_expectations` thresholds from B3.4. Score tiers map to pipeline actions (auto_register → manual_entry).

6. **Revision Control** — Three-tier I185 check in `FileScanner.register_placeholders()`: key lookup → hash match (skip duplicate) → hash mismatch (register new revision with supersedes chain). Each registration uses UUID v4 `id` (I186). Supersedes chain auto-links `supersedes`/`superseded_by` FK pairs.

7. **Pipeline Export** — I308 schema-driven **export view model**: 3 persistent DuckDB views (`v_discovery_inventory`, `v_extraction_results`, `v_review_flags`) rendered by `generate_view_ddl()` from `eks_export_view_config.json` v1.1.0 (view id / source table / `is_latest` filter / ordered columns / file base name / sheet name / formats), created after the I311 migration gate. `export_artifact.artifact_type` = view_id; `documents.flag_reason` materialized; version-control columns pruned; missing view config → fail-fast S-C-S-0312. Exports: `discovery_inventory` / `extraction_results` (csv + xlsx) and `review_flags` (csv) written to `eks/output/` (supersedes I193 `x_export` runtime resolution / I275 column_processing scoping).

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
