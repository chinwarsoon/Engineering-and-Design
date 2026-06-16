# Engineering Knowledge System (EKS) — Master Workplan

**Document ID**: WP-EKS-001  
**Current Version**: 0.7  
**Status**: 🔵 DRAFT — PENDING APPROVAL  
**Last Updated**: 2026-06-18  

---

## 1. Title and Description

This is the **master index workplan** for the Engineering Knowledge System (EKS) — a hybrid RAG (Retrieval-Augmented Generation) system that allows users to query and retrieve knowledge from engineering documents using natural language. The system is built on a layered knowledge architecture combining structured metadata, vector embeddings, and a knowledge relationship graph.

Each implementation phase is managed as an **independent workplan file** (see Section 8). This master document tracks overall scope, requirements, and phase status only.

---

## 2. Revision Control & Version History

| Version | Date       | Author | Summary of Changes                                                              |
| :------ | :--------- | :----- | :------------------------------------------------------------------------------ |
| 0.1     | 2026-06-11 | System | Initial workplan draft — full scope from eks/readme.md                          |
| 0.2     | 2026-06-11 | System | Restructured: master index only. Phase details moved to individual workplan files |
| 0.3     | 2026-06-15 | System | Added project asset data requirements R36–R38: universal plant item schema, structured asset loader, asset-aware retrieval. Updated Phase 1–5 workplans accordingly |
| 0.4     | 2026-06-16 | System | Fixed R36 status: corrected from 🔷 PLANNED to ✅ PASS (delivered in Phase 1 v0.6). Fixed fragment count in Section 6: corrected "10 reusable fragments" to "13 fragments" per gap analysis against actual datadrop (added specialist_equipment A2.12 and motor_control A2.13). |
| 0.5     | 2026-06-17 | System | Added R39: Zero-code asset extensibility — conditional_fragments structure in schema enables adding new plant asset types/sub-types without code changes. Assigned to Phase 1 (schema) and Phase 3 (loader). |
| 0.6     | 2026-06-18 | System | Phase 1 marked PASS: T1.20 complete, all success criteria met, test_phase1.py updated, logs and report updated. R36 and R39 status updated to PASS in master scope table. |
| 0.7     | 2026-06-18 | System | Added Section 10: EKS Pipeline Architecture — full workflow diagram covering ingestion, embedding, graph, retrieval, and UI across all 5 phases. Added R40 (Asset Embedding Strategy), R41 (Asset Chunk Registry Extension), R42 (Asset Vector Upsert) based on datadrop embedding analysis. Updated scope table, phase index, and index of content. |

---

## 3. Objective

Design and implement a production-ready Engineering Knowledge System (EKS) that:
- Ingests and indexes multi-format engineering documents (PDF, DOCX, XLSX, DWG, DGN)
- Ingests structured project asset data (equipment, instruments, pipelines, valves, motors) from Excel datadrop
- Stores and manages structured metadata, vector embeddings, and a knowledge graph
- Provides an interactive user inquiry interface for both documents and plant assets
- Retrieves, re-ranks, and assembles context for LLM-based answering
- Supports SSOT + schema-driven extensibility (no code changes to add new doc types or metadata)
- Enforces revision management, source traceability, and plug-in architecture

---

## 4. Scope Summary

| ID  | Category             | Requirement                              | Details                                                                                      | Status     | Phase |
| :-- | :------------------- | :--------------------------------------- | :------------------------------------------------------------------------------------------- | :--------: | :---: |
| R01 | Knowledge Base       | Document Ingestion                       | Ingest PDF, DOCX, XLSX, DWG, DGN formats via plug-in parsers                                | ✅ PASS    | 1     |
| R02 | Knowledge Base       | Document Registry                        | Store document metadata in structured DB (PostgreSQL/DuckDB)                                 | ✅ PASS    | 1     |
| R03 | Knowledge Base       | Chunk Registry                           | Parent-child chunking strategy with chunk metadata                                           | 🔷 PLANNED | 2     |
| R04 | Knowledge Base       | Vector Storage                           | Embed chunks and store in vector DB (Qdrant)                                                 | 🔷 PLANNED | 2     |
| R05 | Knowledge Base       | Knowledge Graph                          | Neo4j graph for doc-to-doc, doc-to-object, object-to-object relationships                   | 🔷 PLANNED | 3     |
| R06 | Schema               | SSOT Schema-Driven Design                | Metadata schema reuses dcc/config/schemas pattern; project_setup_base / setup / config       | ✅ PASS    | 1     |
| R07 | Schema               | Canonical Data Model                     | Foundation for metadata schemas, retrieval filters, relationship graphs, future integrations | ✅ PASS    | 1     |
| R08 | Schema               | Schema Fragment Pattern                  | Fragment-based, inheritance (base + project) pattern per agent_rule Section 2                | ✅ PASS    | 1     |
| R09 | Metadata             | Project & Document Metadata              | project_title, project_number, area, discipline, department, document_type, document_number  | ✅ PASS    | 1     |
| R10 | Metadata             | Source Location Metadata                 | file name, file location, section/paragraph, page                                            | 🔷 PLANNED | 2     |
| R11 | Metadata             | Engineering Object Metadata              | Plant item, item tag, tag properties; cross-reference metadata                               | 🔷 PLANNED | 3     |
| R12 | Metadata             | Multi-Level Metadata                     | Project-level, document-level, and chunk-level metadata hierarchy                            | 🔷 PLANNED | 2     |
| R13 | Embedding            | Embedding Pollution Prevention           | Separate metadata, administrative data, and vector content                                   | 🔷 PLANNED | 2     |
| R14 | Embedding            | Hybrid Embedding Approach                | Prepend small contextual header; store full metadata separately                              | 🔷 PLANNED | 2     |
| R15 | Embedding            | Plug-in Embedding Providers              | Support OpenAI, Ollama, or custom providers without code changes                             | 🔷 PLANNED | 2     |
| R16 | Retrieval Pipeline   | Metadata Filtering                       | Filter candidates by project, discipline, document type, revision                            | 🔷 PLANNED | 4     |
| R17 | Retrieval Pipeline   | Relationship Expansion                   | Use knowledge graph to expand context with related docs/objects                              | 🔷 PLANNED | 4     |
| R18 | Retrieval Pipeline   | Vector + Keyword Search                  | Hybrid semantic + keyword search                                                             | 🔷 PLANNED | 4     |
| R19 | Retrieval Pipeline   | Retrieval Scoring & Reranking            | Score and re-rank retrieved chunks for relevance                                             | 🔷 PLANNED | 4     |
| R20 | Retrieval Pipeline   | Context Assembly & LLM Answering         | Assemble final context and pass to LLM for response generation                              | 🔷 PLANNED | 4     |
| R21 | Revision Management  | Preserve All Revisions                   | All document revisions retained; no overwrite                                                | ✅ PASS    | 1     |
| R22 | Revision Management  | Latest Revision Filtering                | Support filtering to latest revision only                                                    | ✅ PASS    | 1     |
| R23 | Revision Management  | Superseded Lookup                        | Support querying superseded document revisions                                               | 🔷 PLANNED | 3     |
| R24 | Revision Management  | Revision-Aware Retrieval                 | Retrieval pipeline respects document revision context                                        | 🔷 PLANNED | 4     |
| R25 | Traceability         | Source Traceability                      | document_number, revision, page, section, chunk_id, source_file per retrieved chunk         | 🔷 PLANNED | 2     |
| R26 | Plug-in Architecture | Document Parser Plugins                  | Plug-in parsers for PDF, DOCX, XLSX, DWG, DGN                                              | ✅ PASS    | 1     |
| R27 | Plug-in Architecture | Metadata Extractor Plugins               | Plug-in extractors for equipment, instrument, valve, pipeline metadata                      | 🔷 PLANNED | 3     |
| R28 | Plug-in Architecture | Vector DB Plug-in                        | Swappable vector DB provider (Qdrant default)                                               | 🔷 PLANNED | 2     |
| R29 | Infrastructure       | Metadata DB                              | PostgreSQL or DuckDB for structured metadata storage                                        | ✅ PASS    | 1     |
| R30 | Infrastructure       | Vector DB                                | Qdrant for vector storage                                                                    | 🔷 PLANNED | 2     |
| R31 | Infrastructure       | Graph DB                                 | Neo4j for knowledge relationship graph                                                       | 🔷 PLANNED | 3     |
| R32 | UI                   | Standalone Interactive Inquiry Interface | User-facing query interface for natural language retrieval                                   | 🔷 PLANNED | 5     |
| R33 | Logging & Debug      | Tiered Logging (levels 0–3)              | Per agent_rule Section 6: status, warning, trace levels                                     | ✅ PASS    | 1     |
| R34 | Logging & Debug      | Debug Object & Structured Trace Table    | Debug dict → debug_log.json, trace table with timestamps                                    | ✅ PASS    | 1     |
| R35 | Module Design        | SSOT Global Parameters                   | All global keys, paths, codes in schema-driven config; no hardcoding                        | ✅ PASS    | 1     |
| R36 | Schema               | Universal Plant Item Schema              | Fragment-based asset schema covering Equipment, Inline Component, Instrument, Motor, Pipeline, Control Valve, Manual Valve | ✅ PASS    | 1     |
| R37 | Knowledge Base       | Structured Asset Ingestion               | Load and index project asset data from Excel datadrop into knowledge graph + document registry | 🔷 PLANNED | 3     |
| R38 | Retrieval Pipeline   | Asset-Aware Retrieval                    | Filter and expand context by asset attributes (unit, service, tag_type, pipeline) and asset-to-document relationships | 🔷 PLANNED | 4     |
| R39 | Schema               | Zero-Code Asset Extensibility            | `conditional_fragments` structure in `eks_asset_setup_schema.json` and `eks_asset_config.json` enables adding new AT_ tag types and conditional fragment rules without any code changes — config-only update | 🔶 PARTIAL | 1,3   |
| R40 | Embedding            | Asset Embedding Strategy                 | Define asset-to-text representation (contextual header + key field summary); store asset vectors in separate Qdrant collection `eks_assets`; prevent null/code pollution | 🔷 PLANNED | 2,3   |
| R41 | Knowledge Base       | Asset Chunk Registry Extension           | Extend chunk registry to support asset records keyed on `keytag` (no parent-child); asset metadata schema: keytag, tag_type, unit, service, tag_no, p_and_id_file | 🔷 PLANNED | 2     |
| R42 | Knowledge Base       | Asset Vector Upsert                      | When datadrop is re-exported, invalidate and re-embed affected asset vectors in `eks_assets` collection; align with Neo4j node upsert strategy | 🔷 PLANNED | 3     |

**Status Legend:** ✅ PASS | 🔶 PARTIAL | ❌ FAIL | 🔷 PLANNED

---

## 5. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Revision Control & Version History](#2-revision-control--version-history)
- [3. Objective](#3-objective)
- [4. Scope Summary](#4-scope-summary)
- [5. Index of Content](#5-index-of-content)
- [6. Evaluation and Alignment with Existing Architecture](#6-evaluation-and-alignment-with-existing-architecture)
- [7. Dependencies with Other Tasks](#7-dependencies-with-other-tasks)
- [8. Phase Workplan Index](#8-phase-workplan-index)
- [9. References](#9-references)
- [10. EKS Pipeline Architecture](#10-eks-pipeline-architecture)

---

## 6. Evaluation and Alignment with Existing Architecture

The EKS project is a **clean-slate build** under `eks/`. The only existing artifact is `eks/readme.md`.

**Alignment with Existing Patterns (DCC / agent_rule.md):**
- Schema design reuses the `project_setup_base.json / project_setup.json / project_config.json` inheritance pattern from `dcc/config/schemas`
- Module design follows SSOT + schema-driven global parameters (agent_rule Section 4)
- Tiered logging (levels 0–3) and debug object pattern from agent_rule Section 6
- Workplan, log, and report structure follows agent_rule Sections 8–9
- Plug-in architecture aligns with DCC's modular engine approach

**New Patterns Required:**
- Multi-database integration (metadata DB + vector DB + graph DB)
- Parent-child chunking strategy
- Hybrid retrieval pipeline (metadata → graph → vector → rerank → assemble)
- Revision-aware retrieval logic
- Universal plant item schema with fragment composition (13 fragments)
- Structured asset ingestion (bypasses document chunking; loads directly into graph DB)

**Gap Assessment:**
- 42 requirements identified (35 original + 3 asset data + 1 schema extensibility + 3 asset embedding)
- Full greenfield build — no prior EKS implementation exists

---

## 7. Dependencies with Other Tasks

1. **agent_rule.md** — Governs all coding standards, module design, logging, workplan, and documentation rules
2. **dcc/config/schemas** — Metadata schema patterns to be reused and extended for EKS
3. **dcc/workplan/** — Reference workplans for format and conventions
4. External: PostgreSQL or DuckDB, Qdrant, Neo4j installations/services
5. External: Embedding provider (OpenAI API key or Ollama local instance)
6. **Project asset datadrop** — Structured Excel file at `eks/data/twrp/datadrop/Datadrop Summary.xlsx` with 7 sheets covering 7,681 plant items across 447,867 fields

---

## 8. Phase Workplan Index

Each phase is an independent workplan file. Phase execution requires approval before start.

| Phase | Title                                          | Doc ID        | Status     | Requirements        | Workplan File |
| :---: | :--------------------------------------------- | :------------ | :--------: | :------------------ | :------------ |
| 1     | Foundation — Project Structure, Schema & Registry | WP-EKS-P1-001 | ✅ PASS    | R01,R02,R06–R09,R21,R22,R26,R29,R33–R35,R36,R39(schema) | [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) |
| 2     | Chunking, Embedding & Vector Storage           | WP-EKS-P2-001 | 🔷 PLANNED | R03,R04,R10,R12–R15,R25,R28,R30,R40,R41 | [phase_2_chunking_embedding_workplan.md](phase_2_chunking_embedding_workplan.md) |
| 3     | Knowledge Graph & Structured Asset Ingestion   | WP-EKS-P3-001 | 🔷 PLANNED | R05,R11,R23,R27,R31,R37,R39(loader),R40(asset embed),R42 | [phase_3_knowledge_graph_workplan.md](phase_3_knowledge_graph_workplan.md) |
| 4     | Retrieval & Scoring Pipeline                   | WP-EKS-P4-001 | 🔷 PLANNED | R16–R20,R24,R38,R40(retrieval) | [phase_4_retrieval_pipeline_workplan.md](phase_4_retrieval_pipeline_workplan.md) |
| 5     | UI, Retrieval Cache & System Integration       | WP-EKS-P5-001 | 🔷 PLANNED | R32 + cache | [phase_5_ui_integration_workplan.md](phase_5_ui_integration_workplan.md) |

**Phase Dependency Chain:** Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5  
Each phase must be approved and completed before the next phase begins.

---

---

## 10. EKS Pipeline Architecture

Full end-to-end workflow across all 5 phases. Two parallel ingestion paths (documents and assets) converge at the retrieval stage.

```
╔═════════════════════════════════════════════════════════════════════════════════════╗
║                        EKS — FULL PIPELINE ARCHITECTURE                            ║
╚═════════════════════════════════════════════════════════════════════════════════════╝

 INPUT SOURCES
 ─────────────────────────────────────────────────────────────────────────────────────
  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────────┐
  │  PDF Files  │  │ DOCX Files  │  │ XLSX Files  │  │   Datadrop Excel             │
  │ (drawings,  │  │ (specs,     │  │ (sheets,    │  │   7 sheets · 7,681 items     │
  │  reports)   │  │  procedures)│  │  registers) │  │   Equipment / Instrument /   │
  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │   Valve / Pipeline / Motor   │
         └────────────────┴────────────────┘          └──────────────┬───────────────┘
                          │                                           │
               DOCUMENT PATH (Phase 1–2)               ASSET PATH (Phase 1,3)
                          │                                           │
 ════════════════════════════════════════════════════════════════════════════════════
  PHASE 1 — PARSE & REGISTER
 ════════════════════════════════════════════════════════════════════════════════════
                          │                                           │
                          ▼                                           ▼
            ┌─────────────────────────┐             ┌─────────────────────────────┐
            │   Plug-in Parser        │             │   Structured Asset Loader   │
            │   PDFParser             │             │                             │
            │   DOCXParser            │             │ 1. Read sheet + header row  │
            │   XLSXParser            │             │ 2. Apply column norm map    │
            │   DWGParserStub (P3)    │             │ 3. Lookup tag_type in       │
            │   DGNParserStub (P3)    │             │    asset_type_registry      │
            │                         │             │ 4. Evaluate conditional_    │
            │ Output:                 │             │    fragments rules (R39)    │
            │  raw text + structure   │             │ 5. Compose property dict    │
            │  doc-level metadata     │             │ 6. Deduplicate Pipeline     │
            └────────────┬────────────┘             │    KEYTAGs (merge rows)     │
                         │                          └──────────────┬──────────────┘
                         ▼                                         │
            ┌─────────────────────────┐                           │
            │   Document Registry     │                           │
            │   DuckDB                │                           │
            │                         │                           │
            │  doc_number, revision   │                           │
            │  discipline, doc_type   │                           │
            │  is_latest flag         │                           │
            │  file_path              │                           │
            └────────────┬────────────┘                           │
                         │                                        │
 ════════════════════════════════════════════════════════════════════════════════════
  PHASE 2 — CHUNK, EMBED & VECTOR STORAGE (Documents + Asset Records)
 ════════════════════════════════════════════════════════════════════════════════════
                         │                                        │
                         ▼                                        │
            ┌─────────────────────────┐                          │
            │   Chunker               │                          │
            │   section_chunker.py    │                          │
            │   chunker.py            │                          │
            │                         │                          │
            │  PDF/DOCX → section     │                          │
            │  XLSX     → row/table   │                          │
            │  size-based fallback    │                          │
            │                         │                          │
            │  Output per chunk:      │                          │
            │   chunk_id, parent_id   │                          │
            │   text, page, section   │                          │
            └────────────┬────────────┘                          │
                         │                                        │
                         ▼                                        ▼
            ┌─────────────────────────┐          ┌───────────────────────────────┐
            │   Chunk Registry        │          │   Asset Chunk Registry        │
            │   DuckDB                │          │   DuckDB (R41)                │
            │                         │          │                               │
            │  chunk_id → parent_id   │          │  keytag (primary key)         │
            │  doc_number, revision   │          │  tag_type, tag_no             │
            │  page, section          │          │  unit, service                │
            │  source_file            │          │  p_and_id_file                │
            └────────────┬────────────┘          └──────────────┬────────────────┘
                         │                                       │
                         ▼                                       ▼
            ┌─────────────────────────┐          ┌───────────────────────────────┐
            │   Hybrid Embedding      │          │   Asset Text Builder (R40)    │
            │   Strategy              │          │                               │
            │   hybrid_strategy.py    │          │  Build contextual summary:    │
            │                         │          │  "[{tag_type} | Unit {unit}   │
            │  Header prepended:      │          │   | Svc {service}]            │
            │  "[{discipline} |        │          │   {description}:             │
            │   {doc_type} |          │          │   {key property fields}"      │
            │   {doc_no} Rev {rev} |  │          │                               │
            │   p.{page} §{section}]" │          │  Full metadata stored         │
            │                         │          │  in asset chunk registry      │
            │  Full metadata stored   │          │  NOT embedded (R13)           │
            │  in chunk registry      │          └──────────────┬────────────────┘
            │  NOT embedded (R13)     │                         │
            └────────────┬────────────┘                         │
                         │                                       │
                         └─────────────────┬─────────────────────┘
                                           │
                                           ▼
                            ┌──────────────────────────┐
                            │   Embedding Provider     │
                            │   openai_embedder.py     │
                            │   ollama_embedder.py     │
                            │                          │
                            │  Input:  header + text   │
                            │  Output: vector [n-dim]  │
                            │  Batch:  supported       │
                            └──────────┬───────────────┘
                                       │
                         ┌─────────────┴─────────────┐
                         │                           │
                         ▼                           ▼
            ┌────────────────────────┐  ┌────────────────────────────┐
            │  Qdrant: eks_chunks    │  │  Qdrant: eks_assets (R40)  │
            │                        │  │                            │
            │  Payload:              │  │  Payload:                  │
            │  • chunk_id            │  │  • keytag, tag_no          │
            │  • doc_number, rev     │  │  • tag_type                │
            │  • page, section       │  │  • unit, service           │
            │  • project, discipline │  │  • p_and_id_file           │
            │  • source_file         │  │                            │
            │                        │  │  Enables semantic search   │
            │  Doc content search    │  │  over asset properties     │
            └────────────────────────┘  └────────────────────────────┘

 ════════════════════════════════════════════════════════════════════════════════════
  PHASE 3 — KNOWLEDGE GRAPH & ASSET INGESTION
 ════════════════════════════════════════════════════════════════════════════════════

                    Document nodes          Asset nodes (from loader)
                         │                          │
                         ▼                          ▼
            ┌──────────────────────────────────────────────────────────────┐
            │                    Neo4j Graph DB                            │
            │                                                              │
            │  Document nodes:     Asset nodes (14 AT_ types):            │
            │  • Document          • AT_EQPMP, AT_EQUIP, AT_EQTNK …       │
            │  • Revision          • AT_INST_, AT_INST_CS, AT_INST_FLO    │
            │  • Chunk             • AT_MOTOR, AT_CVALVE, AT_HVALVE …     │
            │                      • AT_PROCESS, AT_INCOMP, AT_PSV        │
            │  Relationships:                                              │
            │  REFERENCES          REFERENCED_BY_DWG   (asset → P&ID)    │
            │  SUPERSEDES          BELONGS_TO_UNIT      (asset → unit)    │
            │  CONTAINS            BELONGS_TO_SERVICE   (asset → svc)     │
            │  RELATES_TO          CONNECTS_TO          (pipeline → comp) │
            │                      HAS_ACTUATOR         (valve → act)     │
            └──────────────────────────────────────────────────────────────┘
                         │                          │
                         │    Asset vector upsert   │
                         │    on datadrop reload     │
                         │    (R42) ◄───────────────┘
                         │
 ════════════════════════════════════════════════════════════════════════════════════
  PHASE 4 — RETRIEVAL & SCORING PIPELINE
 ════════════════════════════════════════════════════════════════════════════════════

  User Query (natural language)
         │
         ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 1 — Metadata Filter                                                   │
  │  Document: project, discipline, doc_type, is_latest, revision                │
  │  Asset:    unit, service, tag_type, pipeline_tag (R38)                       │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 2 — Graph Relationship Expansion                                      │
  │  Doc→Doc:   REFERENCES, SUPERSEDES                                           │
  │  Doc→Asset: REFERENCED_BY_DWG  ←  surface docs linked to matching assets    │
  │  Asset→Asset: CONNECTS_TO, HAS_ACTUATOR  ←  expand pipeline subgraphs       │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                     ┌───────────┴───────────┐
                     │                       │
                     ▼                       ▼
  ┌──────────────────────────┐  ┌───────────────────────────────────────────────┐
  │  STAGE 3a                │  │  STAGE 3b                                     │
  │  Hybrid Search           │  │  Asset Query (R38, R40)                       │
  │  (Documents)             │  │                                               │
  │                          │  │  Structured: Neo4j Cypher for exact tag,      │
  │  Vector: eks_chunks      │  │  unit, service, pipeline lookups              │
  │  BM25 keyword            │  │                                               │
  │  Merge + deduplicate     │  │  Semantic: eks_assets vector search for       │
  └──────────────┬───────────┘  │  fuzzy property queries (R40)                │
                 │              └───────────────────────────┬───────────────────┘
                 └──────────────────────┬────────────────────┘
                                        │
                                        ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 4 — Scorer                                                            │
  │  cosine similarity score + keyword score + graph proximity boost             │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 5 — Reranker                                                          │
  │  Rule-based (default) or cross-encoder (sentence-transformers, optional)     │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 6 — Context Assembler                                                 │
  │  Select top-k chunks + asset records → fit LLM context window               │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  STAGE 7 — LLM Answering                                                     │
  │  OpenAI / Ollama provider (plug-in)                                          │
  │  Response includes source citations:                                         │
  │  doc_number · revision · page · chunk_id · asset keytag                     │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
 ════════════════════════════════════════════════════════════════════════════════════
  PHASE 5 — UI, CACHE & SYSTEM INTEGRATION
 ════════════════════════════════════════════════════════════════════════════════════
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  Retrieval Cache (memory / Redis)                                            │
  │  Keyed on query hash + filter hash → skip pipeline on hit                   │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  FastAPI Backend                                                             │
  │  /query   → full retrieval pipeline + LLM answer + citations                │
  │  /assets  → asset browse/filter (unit, service, tag_type, pipeline_tag)     │
  │  /ingest  → document upload + parse + chunk + embed trigger                 │
  │  /status  → system health                                                   │
  └──────────────────────────────┬───────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────────────────────┐
  │  Web UI                                                                      │
  │  • Query input + filter panel (doc + asset dimensions)                      │
  │  • Answer display with source citation cards                                 │
  │  • Asset browsing panel (attributes + linked P&ID documents)                │
  │  • Document ingestion upload                                                 │
  └──────────────────────────────────────────────────────────────────────────────┘
```

**Data store summary:**

| Store | Technology | Contents | Phase |
| :---- | :--------- | :------- | :---: |
| Document Registry | DuckDB | Document metadata, revision flags | 1 |
| Asset Chunk Registry | DuckDB | Asset record metadata (keytag, tag_type, unit, service) | 2 |
| Vector Store — Documents | Qdrant `eks_chunks` | Document chunk vectors + payload | 2 |
| Vector Store — Assets | Qdrant `eks_assets` | Asset contextual summary vectors + payload | 2/3 |
| Knowledge Graph | Neo4j | All nodes (docs, chunks, assets) + all relationships | 3 |
| Retrieval Cache | Memory / Redis | Query result cache keyed on query+filter hash | 5 |


## 9. References

1. [agent_rule.md](/home/franklin/dsai/Engineering-and-Design/agent_rule.md)
2. [eks/readme.md](/home/franklin/dsai/Engineering-and-Design/eks/readme.md)
3. [dcc/config/schemas](/home/franklin/dsai/Engineering-and-Design/dcc/config/schemas) — Schema pattern reference
4. [dcc/workplan/pipeline_architecture/pipeline_architecture_workplan/pipeline_architecture_design_workplan.md](/home/franklin/dsai/Engineering-and-Design/dcc/workplan/pipeline_architecture/pipeline_architecture_workplan/pipeline_architecture_design_workplan.md) — Workplan format reference
5. [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md)
6. [phase_2_chunking_embedding_workplan.md](phase_2_chunking_embedding_workplan.md)
7. [phase_3_knowledge_graph_workplan.md](phase_3_knowledge_graph_workplan.md)
8. [phase_4_retrieval_pipeline_workplan.md](phase_4_retrieval_pipeline_workplan.md)
9. [phase_5_ui_integration_workplan.md](phase_5_ui_integration_workplan.md)
