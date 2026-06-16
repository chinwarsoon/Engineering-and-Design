# EKS Phase 4 — Retrieval & Scoring Pipeline

**Document ID**: WP-EKS-P4-001  
**Current Version**: 0.7  
**Status**: 🔵 DRAFT — PENDING APPROVAL  
**Last Updated**: 2026-06-16  
**Parent Workplan**: [eks_system_workplan.md](eks_system_workplan.md)  
**Phase Dependency**: Phase 3 must be complete and approved  

---

## 1. Title and Description

Build the full hybrid retrieval and scoring pipeline that transforms a natural language query into a grounded, cited LLM response. The pipeline stages are: metadata filtering (documents + assets) → knowledge graph relationship expansion (document + asset graph) → hybrid vector + keyword search → scoring & reranking → context assembly → LLM answering. Revision-aware retrieval and asset-aware retrieval are enforced throughout.

---

## 2. Revision Control & Version History

| Version | Date       | Author | Summary of Changes                        |
| :------ | :--------- | :----- | :---------------------------------------- |
| 0.1     | 2026-06-11 | System | Initial phase workplan draft for approval |
| 0.2     | 2026-06-15 | System | Added asset-aware metadata filtering (unit, service, tag_type) and asset relationship expansion (CONNECTS_TO pipeline-to-component, REFERENCED_BY_DWG P&ID links). Updated scope, tasks, success criteria for R38 |
| 0.3     | 2026-06-16 | System | Added T4.18 asset query handler, reranker model guidance, Timestamp column in task table. |
| 0.4     | 2026-06-18 | System | Added R40 to scope: dual-collection vector search (eks_chunks + eks_assets). Added T4.19 dual-collection merger. Updated success criteria. |
| 0.5     | 2026-06-16 | System | Updated T4.1 to include new metadata dimensions: `originator_company` and `security_class`. |
| 0.6     | 2026-06-16 | System | Added T4.20–T4.21 for dynamic ontology-aware query expansion and unlimited path depth connectivity tracing. Linked Appendix C. |
| 0.7     | 2026-06-16 | System | Ontology Option C gap closure: added T4.22 (dedicated ontology_resolver.py module); T4.23 (CONTROLS + FEEDS_FROM traversal in graph expander); T4.24 (PhysicalObject lookup via INSTALLED_AT). Added success criteria for all three. Added ontology_resolver.py to files table. |

---

## 3. Objective

- Implement metadata filtering to narrow candidates by project, discipline, doc type, revision, AND asset attributes (unit, service, tag_type, pipeline tag)
- Implement knowledge graph relationship expansion to surface related documents, assets, and pipeline-to-component connections
- Implement hybrid vector + keyword search across Qdrant and document registry
- Implement retrieval scoring and reranking to select top-k most relevant chunks
- Implement context assembly (chunk selection, ordering, truncation for LLM context window)
- Integrate LLM answering with source citations (doc_number, revision, page, chunk_id, asset tag)
- Enforce revision-aware retrieval (latest or specific revision filtering)
- Enforce asset-aware retrieval (filter by unit, service, tag_type)
- Build the pipeline orchestrator that connects all stages end-to-end

---

## 4. Scope Summary

| ID  | Category           | Requirement                      | Details                                                                    | Status     |
| :-- | :----------------- | :------------------------------- | :------------------------------------------------------------------------- | :--------: |
| R16 | Retrieval Pipeline | Metadata Filtering               | Filter candidates by project, discipline, doc type, revision, AND asset attributes (unit, service, tag_type) | 🔷 PLANNED |
| R17 | Retrieval Pipeline | Relationship Expansion           | Use knowledge graph to expand context with related docs, assets, and pipeline-to-component connections | 🔷 PLANNED |
| R18 | Retrieval Pipeline | Vector + Keyword Search          | Hybrid semantic + keyword search                                           | 🔷 PLANNED |
| R19 | Retrieval Pipeline | Retrieval Scoring & Reranking    | Score and re-rank retrieved chunks for relevance                           | 🔷 PLANNED |
| R20 | Retrieval Pipeline | Context Assembly & LLM Answering | Assemble final context and pass to LLM for response generation            | 🔷 PLANNED |
| R24 | Revision Management| Revision-Aware Retrieval         | Retrieval pipeline respects document revision context                      | 🔷 PLANNED |
| R38 | Retrieval Pipeline | Asset-Aware Retrieval            | Filter and expand context by asset attributes and asset-to-document graph relationships | 🔷 PLANNED |
| R40 | Retrieval Pipeline | Asset Semantic Search            | Query `eks_assets` Qdrant collection for fuzzy/semantic asset property queries; merge with Neo4j structured results before scoring | 🔷 PLANNED |
| R44 | Schema             | ISO 15926 Ontology Integration   | Separate FunctionalObject (Tag) and PhysicalObject (Equipment) properties in ontology schema; zero-code config-driven classes and relationships | 🔷 PLANNED |
| R46 | Retrieval Pipeline | Ontology-Aware Retrieval         | Dynamic query expansion via T-Box subclass traversal; trace piping connections at unlimited depth | 🔷 PLANNED |

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
- [8. Task Breakdown](#8-task-breakdown)
- [9. Files and Modules](#9-files-and-modules-to-createupdate)
- [10. Risks and Mitigation](#10-risks-and-mitigation)
- [11. Potential Future Issues](#11-potential-future-issues)
- [12. Success Criteria](#12-success-criteria)
- [13. Deliverables](#13-deliverables)
- [14. References](#14-references)

---

## 6. Evaluation and Alignment with Existing Architecture

- **All prior phases required**: Uses document registry (Phase 1), chunk/vector store (Phase 2), knowledge graph + asset graph (Phase 3)
- **Schema-driven**: Retrieval pipeline configuration (top_k, reranker settings, LLM provider, context window, asset filter dimensions) managed via `eks_config.json`
- **Plug-in pattern**: LLM interface follows same abstract provider pattern as embedding providers
- **New pattern**: Multi-stage hybrid retrieval pipeline is entirely new to this workspace
- **Asset awareness**: Metadata filter and graph expander gain asset-specific dimensions from the Phase 3 asset graph (CONNECTS_TO, REFERENCED_BY_DWG relationships)

---

## 7. Dependencies with Other Tasks

1. **Phase 1 (WP-EKS-P1-001)** — Document registry, revision management, logger
2. **Phase 2 (WP-EKS-P2-001)** — Chunk registry, vector store (Qdrant), embedding providers
3. **Phase 3 (WP-EKS-P3-001)** — Knowledge graph, relationship expansion, engineering object metadata
4. **External**: LLM provider (OpenAI API or Ollama); reranker model (optional cross-encoder)
5. **Next Phase**: Phase 5 UI wraps this pipeline as its backend query interface

---

## 8. Task Breakdown

**Timeline**: TBD — starts after Phase 3 approval and completion  
**Estimated Effort**: High (core intelligence of the system)

| # | Task | Details | Status |
| :- | :--- | :------ | :----: |
| T4.1 | Implement metadata filter | Filter chunk candidates by project, discipline, doc_type, originator, security_class, is_latest revision flags + asset attributes (unit, service, tag_type, pipeline_tag) | 🔷 |
| T4.2 | Implement revision-aware filter | Apply latest/specific revision filter as part of metadata filtering stage | 🔷 |
| T4.3 | Implement graph relationship expander | Query Neo4j for related documents, assets, and pipeline-to-component connections (CONNECTS_TO, REFERENCED_BY_DWG); expand candidate set | 🔷 |
| T4.4 | Implement vector search | Similarity search via Qdrant using query embedding — query `eks_chunks` (documents) and `eks_assets` (asset semantic search, R40); collection selected by query context | 🔷 |
| T4.5 | Implement keyword search | BM25 or full-text search over document registry for keyword matching | 🔷 |
| T4.6 | Implement hybrid search merger | Merge and deduplicate vector + keyword search results | 🔷 |
| T4.7 | Implement retrieval scorer | Score candidates by relevance (cosine similarity + keyword score) | 🔷 |
| T4.8 | Implement reranker | Cross-encoder or rule-based reranking of top-k candidates | 🔷 |
| T4.9 | Implement context assembler | Select, order, and truncate chunks to fit LLM context window | 🔷 |
| T4.10 | Implement abstract LLM interface | `llm_interface.py`: generate(prompt, context) → answer, with provider plug-in | 🔷 |
| T4.11 | Implement OpenAI LLM provider | `openai_llm.py`: calls OpenAI chat completions API | 🔷 |
| T4.12 | Implement Ollama LLM provider | `ollama_llm.py`: calls local Ollama chat endpoint | 🔷 |
| T4.13 | Implement source citation in response | Include doc_number, revision, page, chunk_id in LLM response output | 🔷 |
| T4.14 | Implement pipeline orchestrator | `pipeline.py`: orchestrate all stages end-to-end for a given query | 🔷 |
| T4.15 | Write end-to-end tests | Test full pipeline with sample engineering documents and queries | 🔷 |
| T4.16 | Update config | Add retrieval settings: top_k, reranker_model, llm_provider, context_window to `eks_config.json` | 🔷 |
| T4.17 | Update logs | `update_log.md`, `issue_log.md` | 🔷 |
| T4.18 | Implement asset query handler | Add `query_assets` in `pipeline.py` to retrieve asset card details and P&ID links for UI (R38) | 🔷 |
| T4.19 | Implement dual-collection search merger | Merge `eks_chunks` and `eks_assets` vector search results using RRF or normalized scores (R40) | 🔷 |
| T4.20 | Implement ontology-aware query expansion | Update `metadata_filter.py` to resolve subclass hierarchies dynamically from Neo4j T-Box (R46) | 🔷 |
| T4.21 | Implement unlimited-depth connectivity path tracing | Update `graph_expander.py` to trace CONNECTS_TO* downstream/upstream paths with no depth limits (R46) | 🔷 |
| T4.22 | Implement OntologyResolver module | Create `ontology_resolver.py`: `resolve_class(user_label) → [AT_codes]` — queries Neo4j T-Box using dynamic Cypher: `MATCH (parent:OntologyClass {label: $label})<-[:SUBCLASS_OF*0..10]-(sub) RETURN collect(sub.name)`; maps returned class names to AT_ codes via `ontology_class_map`; returns list for metadata filter — zero hardcoded class lists in Python | 🔷 |
| T4.23 | Extend graph expander with CONTROLS + FEEDS_FROM | Update `graph_expander.py` to traverse `CONTROLS` relationships (instrument→asset: "what controls this pump?") and `FEEDS_FROM` relationships; add to the candidate expansion set alongside existing CONNECTS_TO and REFERENCED_BY_DWG traversals | 🔷 |
| T4.24 | Implement PhysicalObject lookup via INSTALLED_AT | Add query path in `graph_expander.py`: when query targets a tag node (FunctionalObject), traverse `INSTALLED_AT` in reverse to find linked PhysicalObject nodes; include manufacturer, serial_number, brand in LLM context assembly for physical equipment queries | 🔷 |

---

## 9. Files and Modules to Create/Update

| File/Folder                                       | Action | Purpose                                                      |
| :------------------------------------------------ | :----- | :----------------------------------------------------------- |
| `eks/engine/retrieval/__init__.py`                | Create | Retrieval pipeline package init                              |
| `eks/engine/retrieval/metadata_filter.py`         | Create | Metadata-based candidate filtering + revision-aware filter   |
| `eks/engine/retrieval/graph_expander.py`          | Create | Knowledge graph relationship expansion                       |
| `eks/engine/retrieval/vector_search.py`           | Create | Qdrant vector similarity search                              |
| `eks/engine/retrieval/keyword_search.py`          | Create | BM25/full-text keyword search over document registry         |
| `eks/engine/retrieval/hybrid_search.py`           | Create | Merge and deduplicate vector + keyword search results        |
| `eks/engine/retrieval/scorer.py`                  | Create | Candidate scoring (cosine similarity + keyword score)        |
| `eks/engine/retrieval/reranker.py`                | Create | Cross-encoder or rule-based reranking of top-k candidates    |
| `eks/engine/retrieval/context_assembler.py`       | Create | Context window selection, ordering, truncation               |
| `eks/engine/retrieval/llm_interface.py`           | Create | Abstract LLM provider interface                              |
| `eks/engine/retrieval/openai_llm.py`              | Create | OpenAI LLM provider                                          |
| `eks/engine/retrieval/ollama_llm.py`              | Create | Ollama LLM provider                                          |
| `eks/engine/retrieval/pipeline.py`                | Create | Pipeline orchestrator — end-to-end query execution           |
| `eks/config/eks_config.json`                      | Update | Add retrieval pipeline configuration settings                |
| `eks/test/test_phase4.py`                         | Create | End-to-end retrieval pipeline tests                          |

---

## 10. Risks and Mitigation

| Risk                                               | Likelihood | Impact | Mitigation                                                   |
| :------------------------------------------------- | :--------: | :----: | :----------------------------------------------------------- |
| Retrieval quality varies significantly by query    | High       | High   | Tunable pipeline stages; tiered logging for query analysis   |
| LLM hallucination on out-of-context queries        | Medium     | High   | Strict context window; enforce source citations in response  |
| Pipeline latency for complex multi-stage queries   | Medium     | Medium | Retrieval cache in Phase 5; async stage execution            |
| Reranker model unavailable or slow                 | Medium     | Medium | Rule-based reranker as fallback; reranker is optional stage  |

---

## 11. Potential Future Issues

- Advanced query understanding (intent detection, entity extraction from query) may significantly improve retrieval accuracy
- Multi-hop graph traversal may introduce latency for deeply connected document sets
- Streaming LLM responses (token-by-token) will require WebSocket/SSE infrastructure (Phase 5)
- Query caching strategy may need eviction policies for large query volumes

---

## 12. Success Criteria

- [ ] Metadata filtering reduces candidate set by both document attributes AND asset attributes (unit, service, tag_type)
- [ ] Graph expansion surfaces related documents, engineering assets, and pipeline-to-component connections
- [ ] Hybrid search returns more relevant chunks than vector-only or keyword-only alone
- [ ] Reranking improves top-k precision versus unranked results
- [ ] Context assembler respects LLM context window limit
- [ ] LLM answers include source citations: doc_number, revision, page, chunk_id, asset tag
- [ ] Revision-aware retrieval: latest revision returned by default; specific revision queryable
- [ ] Asset-aware retrieval: filter by unit, service, tag_type; expand via pipeline CONNECTS_TO
- [ ] Asset query handler (`query_assets`) in `pipeline.py` operational for Phase 5 `/assets` endpoint

- [ ] `eks_assets` Qdrant collection queried for semantic asset property searches (R40)

- [ ] Dual-collection search results merged and scored consistently
- [ ] Ontology-aware query expansion dynamically resolves subclasses from Neo4j T-Box (T4.20)
- [ ] Unlimited-depth connectivity path tracing (`CONNECTS_TO*`) tracing is operational in retrieval pipeline (T4.21)
- [ ] End-to-end pipeline tests passing with sample engineering documents and asset queries

---

## 13. Deliverables

- Retrieval modules: `metadata_filter.py`, `graph_expander.py`, `vector_search.py`, `keyword_search.py`, `hybrid_search.py`
- Scoring modules: `scorer.py`, `reranker.py`
- Assembly modules: `context_assembler.py`
- LLM modules: `llm_interface.py`, `openai_llm.py`, `ollama_llm.py`
- Orchestrator: `pipeline.py`
- Updated config: `eks_config.json`
- Test file: `test_phase4.py`
- Report: `eks/workplan/reports/phase_4_retrieval_pipeline_report.md`

---

## 14. References

1. [eks_system_workplan.md](eks_system_workplan.md) — Master workplan
2. [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) — Phase 1 prerequisite
3. [phase_2_chunking_embedding_workplan.md](phase_2_chunking_embedding_workplan.md) — Phase 2 prerequisite
4. [phase_3_knowledge_graph_workplan.md](phase_3_knowledge_graph_workplan.md) — Phase 3 prerequisite
5. [agent_rule.md](/home/franklin/dsai/Engineering-and-Design/agent_rule.md)
6. [eks/readme.md](/home/franklin/dsai/Engineering-and-Design/eks/readme.md)
7. [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) — Asset schema (R36) for metadata filter dimensions
8. [appendix_c_ontology.md](appendix_c_ontology.md) — Dynamic ISO 15926-Aligned Ontology
