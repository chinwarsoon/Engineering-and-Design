# Engineering Knowledge System (EKS) — Master Workplan

**Document ID**: WP-EKS-001  
**Current Version**: 0.2  
**Status**: 🔵 DRAFT — PENDING APPROVAL  
**Last Updated**: 2026-06-11  

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

---

## 3. Objective

Design and implement a production-ready Engineering Knowledge System (EKS) that:
- Ingests and indexes multi-format engineering documents (PDF, DOCX, XLSX, DWG, DGN)
- Stores and manages structured metadata, vector embeddings, and a knowledge graph
- Provides an interactive user inquiry interface
- Retrieves, re-ranks, and assembles context for LLM-based answering
- Supports SSOT + schema-driven extensibility (no code changes to add new doc types or metadata)
- Enforces revision management, source traceability, and plug-in architecture

---

## 4. Scope Summary

| ID  | Category             | Requirement                              | Details                                                                                      | Status     | Phase |
| :-- | :------------------- | :--------------------------------------- | :------------------------------------------------------------------------------------------- | :--------: | :---: |
| R01 | Knowledge Base       | Document Ingestion                       | Ingest PDF, DOCX, XLSX, DWG, DGN formats via plug-in parsers                                | 🔷 PLANNED | 1     |
| R02 | Knowledge Base       | Document Registry                        | Store document metadata in structured DB (PostgreSQL/DuckDB)                                 | 🔷 PLANNED | 1     |
| R03 | Knowledge Base       | Chunk Registry                           | Parent-child chunking strategy with chunk metadata                                           | 🔷 PLANNED | 2     |
| R04 | Knowledge Base       | Vector Storage                           | Embed chunks and store in vector DB (Qdrant)                                                 | 🔷 PLANNED | 2     |
| R05 | Knowledge Base       | Knowledge Graph                          | Neo4j graph for doc-to-doc, doc-to-object, object-to-object relationships                   | 🔷 PLANNED | 3     |
| R06 | Schema               | SSOT Schema-Driven Design                | Metadata schema reuses dcc/config/schemas pattern; project_setup_base / setup / config       | 🔷 PLANNED | 1     |
| R07 | Schema               | Canonical Data Model                     | Foundation for metadata schemas, retrieval filters, relationship graphs, future integrations | 🔷 PLANNED | 1     |
| R08 | Schema               | Schema Fragment Pattern                  | Fragment-based, inheritance (base + project) pattern per agent_rule Section 2                | 🔷 PLANNED | 1     |
| R09 | Metadata             | Project & Document Metadata              | project_title, project_number, area, discipline, department, document_type, document_number  | 🔷 PLANNED | 1     |
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
| R21 | Revision Management  | Preserve All Revisions                   | All document revisions retained; no overwrite                                                | 🔷 PLANNED | 1     |
| R22 | Revision Management  | Latest Revision Filtering                | Support filtering to latest revision only                                                    | 🔷 PLANNED | 1     |
| R23 | Revision Management  | Superseded Lookup                        | Support querying superseded document revisions                                               | 🔷 PLANNED | 3     |
| R24 | Revision Management  | Revision-Aware Retrieval                 | Retrieval pipeline respects document revision context                                        | 🔷 PLANNED | 4     |
| R25 | Traceability         | Source Traceability                      | document_number, revision, page, section, chunk_id, source_file per retrieved chunk         | 🔷 PLANNED | 2     |
| R26 | Plug-in Architecture | Document Parser Plugins                  | Plug-in parsers for PDF, DOCX, XLSX, DWG, DGN                                              | 🔷 PLANNED | 1     |
| R27 | Plug-in Architecture | Metadata Extractor Plugins               | Plug-in extractors for equipment, instrument, valve, pipeline metadata                      | 🔷 PLANNED | 3     |
| R28 | Plug-in Architecture | Vector DB Plug-in                        | Swappable vector DB provider (Qdrant default)                                               | 🔷 PLANNED | 2     |
| R29 | Infrastructure       | Metadata DB                              | PostgreSQL or DuckDB for structured metadata storage                                        | 🔷 PLANNED | 1     |
| R30 | Infrastructure       | Vector DB                                | Qdrant for vector storage                                                                    | 🔷 PLANNED | 2     |
| R31 | Infrastructure       | Graph DB                                 | Neo4j for knowledge relationship graph                                                       | 🔷 PLANNED | 3     |
| R32 | UI                   | Standalone Interactive Inquiry Interface | User-facing query interface for natural language retrieval                                   | 🔷 PLANNED | 5     |
| R33 | Logging & Debug      | Tiered Logging (levels 0–3)              | Per agent_rule Section 6: status, warning, trace levels                                     | 🔷 PLANNED | 1     |
| R34 | Logging & Debug      | Debug Object & Structured Trace Table    | Debug dict → debug_log.json, trace table with timestamps                                    | 🔷 PLANNED | 1     |
| R35 | Module Design        | SSOT Global Parameters                   | All global keys, paths, codes in schema-driven config; no hardcoding                        | 🔷 PLANNED | 1     |

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

**Gap Assessment:**
- 35 requirements identified, all PLANNED
- Full greenfield build — no prior EKS implementation exists

---

## 7. Dependencies with Other Tasks

1. **agent_rule.md** — Governs all coding standards, module design, logging, workplan, and documentation rules
2. **dcc/config/schemas** — Metadata schema patterns to be reused and extended for EKS
3. **dcc/workplan/** — Reference workplans for format and conventions
4. External: PostgreSQL or DuckDB, Qdrant, Neo4j installations/services
5. External: Embedding provider (OpenAI API key or Ollama local instance)

---

## 8. Phase Workplan Index

Each phase is an independent workplan file. Phase execution requires approval before start.

| Phase | Title                                          | Doc ID        | Status     | Requirements        | Workplan File |
| :---: | :--------------------------------------------- | :------------ | :--------: | :------------------ | :------------ |
| 1     | Foundation — Project Structure, Schema & Registry | WP-EKS-P1-001 | 🔷 PLANNED | R01,R02,R06–R09,R21,R22,R26,R29,R33–R35 | [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) |
| 2     | Chunking, Embedding & Vector Storage           | WP-EKS-P2-001 | 🔷 PLANNED | R03,R04,R10,R12–R15,R25,R28,R30 | [phase_2_chunking_embedding_workplan.md](phase_2_chunking_embedding_workplan.md) |
| 3     | Knowledge Graph & Engineering Object Metadata  | WP-EKS-P3-001 | 🔷 PLANNED | R05,R11,R23,R27,R31 | [phase_3_knowledge_graph_workplan.md](phase_3_knowledge_graph_workplan.md) |
| 4     | Retrieval & Scoring Pipeline                   | WP-EKS-P4-001 | 🔷 PLANNED | R16–R20,R24 | [phase_4_retrieval_pipeline_workplan.md](phase_4_retrieval_pipeline_workplan.md) |
| 5     | UI, Retrieval Cache & System Integration       | WP-EKS-P5-001 | 🔷 PLANNED | R32 + cache | [phase_5_ui_integration_workplan.md](phase_5_ui_integration_workplan.md) |

**Phase Dependency Chain:** Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5  
Each phase must be approved and completed before the next phase begins.

---

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
