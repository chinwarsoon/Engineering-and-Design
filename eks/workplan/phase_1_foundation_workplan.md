# EKS Phase 1 — Foundation: Project Structure, Schema & Document Registry

**Document ID**: WP-EKS-P1-001  
**Current Version**: 0.3  
**Status**: 🔵 DRAFT — PENDING APPROVAL  
**Last Updated**: 2026-06-11  
**Parent Workplan**: [eks_system_workplan.md](eks_system_workplan.md)  
**Phase Dependency**: None — first phase  

---

## 1. Title and Description

Establish the EKS project foundation: folder structure, canonical schema design, document ingestion plug-ins for common formats (PDF, DOCX, XLSX), document registry (metadata DB), revision management, and foundational logging/debug infrastructure. This phase creates the bedrock that all subsequent phases build upon.

---

## 2. Revision Control & Version History

| Version | Date       | Author | Summary of Changes                            |
| :------ | :--------- | :----- | :-------------------------------------------- |
| 0.1     | 2026-06-11 | System | Initial phase workplan draft for approval     |
| 0.2     | 2026-06-11 | System | Added Section 7b: Proposed Project Folder Structure (full tree across all phases); added eks.yml task; fixed duplicate T1.5 numbering |
| 0.3     | 2026-06-11 | System | T1.1 complete: EKS folder scaffolding created. T1.2 complete: eks.yml created with all Phase 1–5 dependencies. Log files created. |

---

## 3. Objective

- Create the EKS project folder structure compliant with agent_rule.md
- Design and implement the canonical schema (base/setup/config pattern)
- Build the document registry (metadata DB) with full CRUD support
- Implement plug-in document parsers: PDF, DOCX, XLSX
- Implement revision management: preserve all revisions, latest revision flag
- Establish tiered logging (levels 0–3), debug object, and structured trace table
- Implement SSOT global parameter registry via schema-driven config

---

## 4. Scope Summary

| ID  | Category             | Requirement               | Details                                                                                      | Status     |
| :-- | :------------------- | :------------------------ | :------------------------------------------------------------------------------------------- | :--------: |
| R01 | Knowledge Base       | Document Ingestion        | Ingest PDF, DOCX, XLSX formats via plug-in parsers (DWG/DGN deferred to Phase 3)            | 🔷 PLANNED |
| R02 | Knowledge Base       | Document Registry         | Store document metadata in structured DB (PostgreSQL/DuckDB)                                 | 🔷 PLANNED |
| R06 | Schema               | SSOT Schema-Driven Design | Metadata schema reuses dcc/config/schemas pattern; project_setup_base / setup / config       | 🔷 PLANNED |
| R07 | Schema               | Canonical Data Model      | Foundation for metadata schemas, retrieval filters, relationship graphs, future integrations | 🔷 PLANNED |
| R08 | Schema               | Schema Fragment Pattern   | Fragment-based, inheritance (base + project) pattern per agent_rule Section 2                | 🔷 PLANNED |
| R09 | Metadata             | Project & Document Metadata | project_title, project_number, area, discipline, department, document_type, document_number | 🔷 PLANNED |
| R21 | Revision Management  | Preserve All Revisions    | All document revisions retained; no overwrite                                                | 🔷 PLANNED |
| R22 | Revision Management  | Latest Revision Filtering | Support filtering to latest revision only                                                    | 🔷 PLANNED |
| R26 | Plug-in Architecture | Document Parser Plugins   | Plug-in parsers for PDF, DOCX, XLSX (abstract base + concrete implementations)              | 🔷 PLANNED |
| R29 | Infrastructure       | Metadata DB               | PostgreSQL or DuckDB for structured metadata storage                                        | 🔷 PLANNED |
| R33 | Logging & Debug      | Tiered Logging (levels 0–3) | Per agent_rule Section 6: status, warning, trace levels                                   | 🔷 PLANNED |
| R34 | Logging & Debug      | Debug Object & Trace Table | Debug dict → debug_log.json, trace table with timestamps                                   | 🔷 PLANNED |
| R35 | Module Design        | SSOT Global Parameters    | All global keys, paths, codes in schema-driven config; no hardcoding                        | 🔷 PLANNED |

**Status Legend:** ✅ PASS | 🔶 PARTIAL | ❌ FAIL | 🔷 PLANNED

---

## 5. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Revision Control & Version History](#2-revision-control--version-history)
- [3. Objective](#3-objective)
- [4. Scope Summary](#4-scope-summary)
- [5. Index of Content](#5-index-of-content)
- [6. Evaluation and Alignment](#6-evaluation-and-alignment-with-existing-architecture)
- [7. Dependencies](#7-dependencies-with-other-tasks)
- [7b. Proposed Project Folder Structure](#7b-proposed-project-folder-structure)
- [8. Task Breakdown](#8-task-breakdown)
- [9. Files and Modules](#9-files-and-modules-to-createupdate)
- [10. Risks and Mitigation](#10-risks-and-mitigation)
- [11. Potential Future Issues](#11-potential-future-issues)
- [12. Success Criteria](#12-success-criteria)
- [13. Deliverables](#13-deliverables)
- [14. References](#14-references)

---

## 6. Evaluation and Alignment with Existing Architecture

- **Schema pattern**: Directly adopts `project_setup_base.json / project_setup.json / project_config.json` from `dcc/config/schemas`
- **Logging**: Directly adopts tiered logging and debug object from `dcc/workflow/core_engine/` patterns
- **Module design**: SSOT global parameters via schema-driven config per agent_rule Section 4
- **New**: Document registry with metadata DB is new to this workspace; no prior precedent in DCC

---

## 7. Dependencies with Other Tasks

1. **agent_rule.md** — Governs all coding standards, module design, logging
2. **dcc/config/schemas** — Schema base/setup/config pattern to replicate
3. **External**: DuckDB (preferred for dev) or PostgreSQL for metadata DB
4. **Next Phase**: Phase 2 depends on document registry and parsers from this phase

---

## 7b. Proposed Project Folder Structure

The EKS project folder follows the standard structure defined in `agent_rule.md`. All folders are created in Phase 1 (T1.1) as empty scaffolding so subsequent phases can populate them without restructuring.

```
eks/
├── eks.yml                         # Conda environment file (all phases)
├── readme.md                       # Project overview (existing)
│
├── archive/                        # Archived/superseded files
│
├── config/                         # Schema and configuration files
│   ├── eks_base_schema.json        # Canonical schema — definitions
│   ├── eks_setup_schema.json       # Canonical schema — property declarations
│   └── eks_config.json             # Actual config values (paths, DB, providers)
│
├── data/                           # Input documents for ingestion
│   └── (user-supplied engineering documents)
│
├── output/                         # Pipeline outputs (debug logs, reports, graphs)
│   └── debug_log.json              # Debug object output
│
├── engine/                         # Core processing modules (all phases)
│   ├── __init__.py                 # Package init with version
│   │
│   ├── core/                       # Foundation: registry, revision, config (Phase 1)
│   │   ├── __init__.py
│   │   ├── registry.py             # Document registry — metadata DB CRUD
│   │   ├── revision.py             # Revision management logic
│   │   └── config_registry.py     # SSOT global parameter access
│   │
│   ├── logging/                    # Tiered logging infrastructure (Phase 1)
│   │   ├── __init__.py
│   │   └── logger.py               # Levels 0–3, debug object, trace table
│   │
│   ├── parsers/                    # Plug-in document parsers (Phase 1 + 3)
│   │   ├── __init__.py
│   │   ├── base_parser.py          # Abstract parser interface
│   │   ├── pdf_parser.py           # PDF parser
│   │   ├── docx_parser.py          # DOCX parser
│   │   ├── xlsx_parser.py          # XLSX parser
│   │   ├── dwg_parser_stub.py      # DWG stub (Phase 3)
│   │   └── dgn_parser_stub.py      # DGN stub (Phase 3)
│   │
│   ├── chunking/                   # Chunking strategies and registry (Phase 2)
│   │   ├── __init__.py
│   │   ├── chunker.py              # Abstract + size-based chunker
│   │   ├── section_chunker.py      # Section-aware chunker
│   │   └── chunk_registry.py       # Parent-child chunk management
│   │
│   ├── embedding/                  # Embedding providers (Phase 2)
│   │   ├── __init__.py
│   │   ├── base_embedder.py        # Abstract embedder interface
│   │   ├── openai_embedder.py      # OpenAI provider
│   │   ├── ollama_embedder.py      # Ollama provider
│   │   └── hybrid_strategy.py      # Contextual header + embedding pipeline
│   │
│   ├── vector_store/               # Vector DB interface (Phase 2)
│   │   ├── __init__.py
│   │   ├── base_vector_store.py    # Abstract vector store interface
│   │   └── qdrant_store.py         # Qdrant implementation
│   │
│   ├── graph/                      # Knowledge graph (Phase 3)
│   │   ├── __init__.py
│   │   ├── graph_store.py          # Abstract graph store interface
│   │   ├── neo4j_store.py          # Neo4j implementation
│   │   ├── graph_schema.py         # Node labels and relationship types
│   │   └── relationship_builders.py # Doc-to-doc, doc-to-object builders
│   │
│   ├── extractors/                 # Engineering object metadata extractors (Phase 3)
│   │   ├── __init__.py
│   │   ├── base_extractor.py       # Abstract extractor interface
│   │   ├── equipment_extractor.py  # Equipment metadata
│   │   ├── instrument_extractor.py # Instrument metadata
│   │   ├── valve_extractor.py      # Valve metadata
│   │   └── pipeline_extractor.py   # Pipeline metadata
│   │
│   ├── retrieval/                  # Retrieval and scoring pipeline (Phase 4)
│   │   ├── __init__.py
│   │   ├── metadata_filter.py      # Metadata + revision-aware filtering
│   │   ├── graph_expander.py       # Graph relationship expansion
│   │   ├── vector_search.py        # Qdrant vector similarity search
│   │   ├── keyword_search.py       # BM25/full-text keyword search
│   │   ├── hybrid_search.py        # Merge vector + keyword results
│   │   ├── scorer.py               # Candidate scoring
│   │   ├── reranker.py             # Reranking top-k candidates
│   │   ├── context_assembler.py    # Context window assembly
│   │   ├── llm_interface.py        # Abstract LLM provider interface
│   │   ├── openai_llm.py           # OpenAI LLM provider
│   │   ├── ollama_llm.py           # Ollama LLM provider
│   │   └── pipeline.py             # End-to-end pipeline orchestrator
│   │
│   └── cache/                      # Retrieval cache (Phase 5)
│       ├── __init__.py
│       ├── retrieval_cache.py      # Abstract cache interface
│       ├── memory_cache.py         # In-memory LRU cache
│       └── redis_cache.py          # Redis cache (optional)
│
├── ui/                             # User interface (Phase 5)
│   ├── app.py                      # FastAPI/Flask application entry point
│   ├── routes/
│   │   ├── query.py                # /query endpoint
│   │   ├── ingest.py               # /ingest endpoint
│   │   └── status.py               # /status, /health endpoints
│   ├── static/                     # Frontend assets (CSS, JS)
│   └── templates/
│       └── index.html              # Main query interface
│
├── test/                           # Unit and integration tests (all phases)
│   ├── test_phase1.py              # Phase 1 tests
│   ├── test_phase2.py              # Phase 2 tests
│   ├── test_phase3.py              # Phase 3 tests
│   ├── test_phase4.py              # Phase 4 tests
│   └── test_phase5.py              # Phase 5 tests
│
├── docs/                           # Documentation
│   └── eks_system_documentation.md # 16-section system docs (Phase 5)
│
├── log/                            # Issue, update, and test logs
│   ├── issue_log.md
│   └── update_log.md
│
└── workplan/                       # Workplans and reports
    ├── eks_system_workplan.md      # Master index workplan
    ├── phase_1_foundation_workplan.md
    ├── phase_2_chunking_embedding_workplan.md
    ├── phase_3_knowledge_graph_workplan.md
    ├── phase_4_retrieval_pipeline_workplan.md
    ├── phase_5_ui_integration_workplan.md
    └── reports/                    # Phase test reports
        ├── phase_1_foundation_report.md
        ├── phase_2_chunking_embedding_report.md
        ├── phase_3_knowledge_graph_report.md
        ├── phase_4_retrieval_pipeline_report.md
        └── phase_5_ui_integration_report.md
```

**Notes:**
- Folders for all phases (chunking, embedding, graph, retrieval, cache, ui) are created as **empty scaffolding** in Phase 1 (T1.1) to establish the full layout upfront
- Each phase populates only its designated folders; no folder restructuring is needed later
- `data/` is for raw input documents supplied by the user; not committed to version control
- `output/` holds runtime artifacts (debug logs, exported graphs); not committed to version control

---

## 8. Task Breakdown

**Timeline**: TBD — starts after approval  
**Estimated Effort**: Medium (foundation build)

| # | Task | Details | Status |
| :- | :--- | :------ | :----: |
| T1.1 | Create EKS folder structure | archive, config, data, output, engine, log, docs, workplan, test, ui | ✅ |
| T1.2 | Create environment file `eks.yml` | Conda environment with all Phase 1–5 dependencies (Python, DuckDB, FastAPI, parsers, vector DB, graph DB clients, embedding providers) | ✅ |
| T1.3 | Design canonical schema — base | `eks_base_schema.json`: definitions for all shared types | 🔷 |
| T1.4 | Design canonical schema — setup | `eks_setup_schema.json`: property declarations using base definitions | 🔷 |
| T1.5 | Design canonical schema — config | `eks_config.json`: actual values (paths, DB settings, provider settings) | 🔷 |
| T1.6 | Implement schema loader | Load and resolve base/setup/config with $ref support (reuse dcc pattern) | 🔷 |
| T1.6 | Implement document registry | CRUD interface for document metadata backed by DuckDB/PostgreSQL | 🔷 |
| T1.7 | Implement revision management | Preserve all revisions; is_latest flag; revision chain lookup | 🔷 |
| T1.8 | Implement abstract base parser | `base_parser.py`: plug-in interface with parse(), extract_metadata() | 🔷 |
| T1.9 | Implement PDF parser | `pdf_parser.py`: extract text, metadata, page numbers | 🔷 |
| T1.10 | Implement DOCX parser | `docx_parser.py`: extract text, metadata, sections | 🔷 |
| T1.11 | Implement XLSX parser | `xlsx_parser.py`: extract sheet data, metadata | 🔷 |
| T1.12 | Implement tiered logger | `logger.py`: levels 0–3, debug object, trace table, depth counter | 🔷 |
| T1.13 | Implement SSOT config registry | Global parameter access via schema-driven config; no hardcoding | 🔷 |
| T1.14 | Write unit tests | Schema loader, document registry, revision management, parsers, logger | 🔷 |
| T1.15 | Create log files | `update_log.md`, `issue_log.md` under `eks/log/` | 🔷 |

---

## 9. Files and Modules to Create/Update

| File/Folder                           | Action | Purpose                                               |
| :------------------------------------ | :----- | :---------------------------------------------------- |
| `eks/eks.yml`                         | Create | Conda environment file with all EKS dependencies      |
| `eks/engine/__init__.py`              | Create | Package init with version info                        |
| `eks/engine/core/__init__.py`         | Create | Core engine package init                              |
| `eks/engine/core/registry.py`         | Create | Document registry — metadata DB CRUD interface        |
| `eks/engine/core/revision.py`         | Create | Revision management — preserve, filter, chain lookup  |
| `eks/engine/core/config_registry.py`  | Create | SSOT global parameter access via schema config        |
| `eks/engine/parsers/__init__.py`      | Create | Parser plug-in package init                           |
| `eks/engine/parsers/base_parser.py`   | Create | Abstract base parser interface                        |
| `eks/engine/parsers/pdf_parser.py`    | Create | PDF document parser                                   |
| `eks/engine/parsers/docx_parser.py`   | Create | DOCX document parser                                  |
| `eks/engine/parsers/xlsx_parser.py`   | Create | XLSX document parser                                  |
| `eks/engine/logging/__init__.py`      | Create | Logging package init                                  |
| `eks/engine/logging/logger.py`        | Create | Tiered logger (levels 0–3), debug object, trace table |
| `eks/config/eks_base_schema.json`     | Create | Canonical schema — definitions                        |
| `eks/config/eks_setup_schema.json`    | Create | Canonical schema — property declarations              |
| `eks/config/eks_config.json`          | Create | Actual config values (paths, DB, provider settings)   |
| `eks/log/update_log.md`               | Create | Update log                                            |
| `eks/log/issue_log.md`                | Create | Issue log                                             |
| `eks/test/test_phase1.py`             | Create | Unit tests for all Phase 1 components                 |

---

## 10. Risks and Mitigation

| Risk                                         | Likelihood | Impact | Mitigation                                                         |
| :------------------------------------------- | :--------: | :----: | :----------------------------------------------------------------- |
| DB schema changes cascade to downstream code | Medium     | High   | Schema-driven design isolates DB structure from processing logic   |
| PDF/DOCX parsing quality varies by doc type  | High       | Medium | Abstract parser interface allows per-format tuning; log errors     |
| DWG/DGN parsing requires CAD libraries       | High       | Low    | Deferred to Phase 3; stub plug-in interface stubbed in this phase  |
| Schema design diverges from dcc pattern      | Low        | Medium | Explicitly use dcc/config/schemas as template reference            |

---

## 11. Potential Future Issues

- CAD format parsing (DWG/DGN) may require specialized third-party libraries or commercial services
- Large document volumes may require async/batch ingestion pipelines
- Document registry may need sharding or partitioning for very large corpora

---

## 12. Success Criteria

- [x] EKS folder structure created and compliant with agent_rule.md project folder conventions
- [x] `eks.yml` created and environment activates cleanly (`conda env create -f eks.yml`)
- [ ] Canonical schema files (base/setup/config) created with one-to-one mapping
- [ ] Schema loader resolves all $ref types (string, object, nested, recursive)
- [ ] Document registry operational: CRUD for document metadata
- [ ] Revision management working: preserve all revisions, is_latest flag, chain lookup
- [ ] PDF, DOCX, XLSX parsers functional via abstract plug-in interface
- [ ] Tiered logger (levels 0–3), debug object, trace table all operational
- [ ] SSOT config registry operational; zero hardcoded global parameters
- [ ] All unit tests passing for Phase 1 components
- [ ] `update_log.md` and `issue_log.md` created under `eks/log/`

---

## 13. Deliverables

- EKS project folder structure
- `eks/eks.yml` — Conda environment file
- Canonical schema files: `eks_base_schema.json`, `eks_setup_schema.json`, `eks_config.json`
- Engine modules: `registry.py`, `revision.py`, `config_registry.py`
- Parser modules: `base_parser.py`, `pdf_parser.py`, `docx_parser.py`, `xlsx_parser.py`
- Logging module: `logger.py`
- Test file: `test_phase1.py`
- Log files: `update_log.md`, `issue_log.md`
- Report: `eks/workplan/reports/phase_1_foundation_report.md`

---

## 14. References

1. [eks_system_workplan.md](eks_system_workplan.md) — Master workplan
2. [agent_rule.md](/home/franklin/dsai/Engineering-and-Design/agent_rule.md)
3. [eks/readme.md](/home/franklin/dsai/Engineering-and-Design/eks/readme.md)
4. [dcc/config/schemas](/home/franklin/dsai/Engineering-and-Design/dcc/config/schemas) — Schema pattern reference
