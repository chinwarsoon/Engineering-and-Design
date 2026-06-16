# EKS Phase 3 — Knowledge Graph & Engineering Object Metadata

**Document ID**: WP-EKS-P3-001  
**Current Version**: 0.6  
**Status**: 🔵 DRAFT — PENDING APPROVAL  
**Last Updated**: 2026-06-16  
**Parent Workplan**: [eks_system_workplan.md](eks_system_workplan.md)  
**Phase Dependency**: Phase 2 must be complete and approved  

---

## 1. Title and Description

Build the Neo4j knowledge relationship graph capturing all engineering knowledge connections: document-to-document, document-to-asset, asset-to-asset, and asset-to-metadata. Ingest structured project asset data from the Excel datadrop (7,681 items across 7 categories) into the graph using the universal plant item schema from Phase 1. Implement structured asset loaders (replacing NLP-based extractors) for equipment, instruments, valves, pipelines, and motors. Add CAD format parser stubs (DWG/DGN) and implement superseded document revision chain lookup. Integrate automated document metadata extraction (cover sheet blocks) for the extended metadata schema.

---

## 2. Revision Control & Version History

| Version | Date       | Author | Summary of Changes                        |
| :------ | :--------- | :----- | :---------------------------------------- |
| 0.1     | 2026-06-11 | System | Initial phase workplan draft for approval |
| 0.2     | 2026-06-15 | System | Replaced NLP-based engineering object extractors with structured asset loaders reading Excel datadrop directly (R37). Added asset graph nodes, pipeline-to-component relationships, and P&ID-to-asset linking. Updated risks and success criteria |
| 0.3     | 2026-06-16 | System | Fixed fragment count in Section 6: corrected "10 reusable fragments" to "11 reusable fragments" to align with Phase 1 v0.6 delivery. Added Timestamp column to task breakdown table per agent_rule Section 8.8. |
| 0.4     | 2026-06-17 | System | Added R39 to scope. Updated T3.9 base asset loader to read conditional_fragments from config and evaluate when/in conditions at runtime — zero code changes needed to add new asset types. Schema loader confirmed no update needed (file-agnostic). |
| 0.5     | 2026-06-18 | System | Added R40 (asset embedding trigger after Neo4j load) and R42 (asset vector upsert on datadrop reload) to scope and tasks. T3.15 sheet orchestrator updated to trigger Phase 2 asset text builder + Qdrant upsert after each node batch. |
| 0.6     | 2026-06-16 | System | Added R43: Automated Document Metadata Extraction. Added T3.21 to task breakdown. |

---

## 3. Objective

- Integrate Neo4j as the knowledge graph database
- Define the graph schema: document nodes, asset nodes (with typed labels per AT_ category), and all relationship types
- Implement five relationship categories: doc↔doc, doc↔asset, asset↔asset (pipeline→component), asset↔metadata, metadata↔metadata
- Ingest structured project asset data from Excel datadrop using universal schema fragments (R37)
- Implement structured asset loaders that map Excel sheets → Neo4j nodes by tag_type composition rules
- Implement pipeline-to-component relationships from FROM_COMPONENT / TO_COMPONENT fields
- Implement P&ID-to-asset linking via PID NUMBER / DOC_FNAME columns
- Implement superseded document lookup via revision chain graph traversal
- Add DWG/DGN parser stubs (full implementation if CAD library available, else interface stubs)

---

## 4. Scope Summary

| ID  | Category             | Requirement                    | Details                                                                          | Status     |
| :-- | :------------------- | :----------------------------- | :------------------------------------------------------------------------------- | :--------: |
| R05 | Knowledge Base       | Knowledge Graph                | Neo4j graph for doc-to-doc, doc-to-asset, asset-to-asset relationships           | 🔷 PLANNED |
| R11 | Metadata             | Engineering Object Metadata    | Plant item, item tag, tag properties; cross-reference metadata                   | 🔷 PLANNED |
| R23 | Revision Management  | Superseded Lookup              | Support querying superseded document revisions via graph traversal               | 🔷 PLANNED |
| R27 | Plug-in Architecture | Structured Asset Loaders       | Loaders for Equipment, Instrument, Valve, Pipeline, Motor from Excel datadrop    | 🔷 PLANNED |
| R31 | Infrastructure       | Graph DB                       | Neo4j for knowledge relationship graph                                           | 🔷 PLANNED |
| R37 | Knowledge Base       | Structured Asset Ingestion     | Load and index project asset data from Excel datadrop into knowledge graph       | 🔷 PLANNED |
| R39 | Schema               | Zero-Code Asset Extensibility  | Base asset loader reads `conditional_fragments` from config at runtime; no code changes needed to add new AT_ types or conditional fragment rules | 🔷 PLANNED |
| R40 | Embedding            | Asset Embedding Trigger        | After loading each asset batch to Neo4j, call asset text builder and upsert vectors into `eks_assets` Qdrant collection | 🔷 PLANNED |
| R42 | Knowledge Base       | Asset Vector Upsert            | On datadrop reload: upsert Neo4j nodes + invalidate and re-embed corresponding `eks_assets` vectors for changed keytags | 🔷 PLANNED |
| R43 | Metadata             | Automated Metadata Extraction | Automated extraction of 11 extended fields (Accountability, Origin, Quality) from doc cover sheets during ingestion | 🔷 PLANNED |

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

- **Phase 1/2 dependency**: Requires document registry (registry.py), chunk registry, schema, and asset schema fragments from prior phases
- **New pattern**: Graph DB integration is entirely new to this workspace — no DCC precedent
- **Schema-driven**: Graph node and relationship types defined in schema; tag_type→fragment composition rules drive node property layout
- **Structured loading**: Asset data is loaded from structured Excel (not NLP-extracted from text), using the universal plant item schema from Phase 1 (R36)
- **Phase 1 asset schema**: 13 fragments define all asset properties; the `asset_type_registry` maps each AT_ tag_type to its fragment composition (includes `specialist_equipment` A2.12 for UV/filtration/conveyor and `motor_control` A2.13 for motor electrical fields)

---

## 7. Dependencies with Other Tasks

1. **Phase 1 (WP-EKS-P1-001)** — Document registry, schema, logger, asset schema fragments (R36), `eks_asset_config.json`
2. **Phase 2 (WP-EKS-P2-001)** — Chunk registry and vector store for graph-aware retrieval in Phase 4
3. **Project asset datadrop** — `eks/data/twrp/datadrop/Datadrop Summary.xlsx` (7 sheets, 7,681 items)
4. **External**: Neo4j service (Docker or cloud), `neo4j` Python driver
5. **Next Phase**: Phase 4 retrieval pipeline uses graph expansion from this phase

---

## 8. Task Breakdown

**Timeline**: TBD — starts after Phase 2 approval and completion  
**Estimated Effort**: High (new infrastructure + extraction logic)

| # | Task | Details | Status | Timestamp |
| :- | :--- | :------ | :----: | :-------- |
| T3.1 | Set up Neo4j integration | Docker Compose setup; `neo4j` Python driver; connection config in `eks_config.json` | 🔷 | — |
| T3.2 | Define graph schema — node types | Document, Revision, Chunk + asset nodes per AT_ (AT_EQUIP, AT_EQPMP, AT_INST_, AT_CVALVE, AT_HVALVE, AT_PROCESS, AT_MOTOR, AT_INCOMP) + EngineeringObject, Tag, Metadata | 🔷 | — |
| T3.3 | Define graph schema — relationship types | REFERENCES, SUPERSEDES, CONTAINS, RELATES_TO, HAS_TAG, HAS_PROPERTY, CROSS_REFERENCES, CONNECTS_TO (pipeline→component), REFERENCED_BY_DWG (asset→P&ID) | 🔷 | — |
| T3.4 | Implement graph store interface | `graph_store.py`: abstract interface — create_node(), create_relationship(), query() | 🔷 | — |
| T3.5 | Implement Neo4j graph store | `neo4j_store.py`: Neo4j-specific implementation of graph store interface | 🔷 | — |
| T3.6 | Implement doc-to-doc relationship builder | Detect cross-references between documents and create REFERENCES edges | 🔷 | — |
| T3.7 | Implement doc-to-asset relationship builder | Link documents to engineering assets via P&ID file name cross-reference (PID NUMBER / DOC_FNAME columns) | 🔷 | — |
| T3.8 | Implement superseded revision lookup | Traverse SUPERSEDES chain to find all revisions of a document | 🔷 | — |
| T3.9 | Implement structured asset loader interface | `base_asset_loader.py`: load(sheet_data, tag_type) → (1) read `fragments` list from `asset_type_registry[tag_type]`; (2) read `conditional_fragments` list and evaluate each `when`/`in` condition against the row's field value; (3) merge all applicable fragment properties; (4) create Neo4j node. Adding a new AT_ type or conditional rule requires only a config update — zero code changes. | 🔷 | — |
| T3.10 | Implement Equipment loader | Load Equipment sheet rows into typed nodes (AT_EQUIP, AT_EQPMP, AT_EQTNK, AT_EQVES, AT_EQEXC) with rotating_equipment fragment | 🔷 | — |
| T3.11 | Implement Instrument loader | Load Instrument sheet rows into AT_INST_ nodes with instrumentation fragment (ISA IDs, sensors, alarms, output) | 🔷 | — |
| T3.12 | Implement Valve loader | Load CONTROLVALVE (AT_CVALVE, AT_PSV) and MANUALVALVE (AT_HVALVE) rows with valve_internals + actuator fragments | 🔷 | — |
| T3.13 | Implement Pipeline loader | Load Pipeline sheet rows into AT_PROCESS nodes with pipeline_route fragment; create CONNECTS_TO edges from FROM/TO_COMPONENT | 🔷 | — |
| T3.14 | Implement Motor loader | Load Motor sheet rows into AT_MOTOR nodes with rotating_equipment + manufacturer fragments | 🔷 | — |
| T3.15 | Implement sheet-to-graph orchestrator | Read all 7 sheets, map each row to its tag_type fragment rules, batch-create nodes + relationships; after each batch trigger asset text builder + `eks_assets` upsert (R40) | 🔷 | — |
| T3.20 | Implement asset vector upsert on reload | On datadrop reload: identify changed/new keytags, upsert Neo4j nodes, call asset text builder for changed items, re-upsert `eks_assets` vectors; log stale vectors removed (R42) | 🔷 | — |
| T3.21 | Automated Metadata Extraction | Implement automated extraction of 11 extended metadata fields (created_by, originator, etc.) from doc cover sheets using LLM/Regex logic. Store in Document Registry. | 🔷 | — |
| T3.16 | Add DWG/DGN parser stubs | Stub plug-in interface for CAD formats; log deferred status | 🔷 | — |
| T3.17 | Write integration tests | Graph CRUD, relationship builders, asset loaders, pipeline-to-component links, superseded lookup | 🔷 | — |
| T3.18 | Update schema and config | Add graph node/relationship definitions to `eks_base_schema.json`; asset loader config to `eks_config.json` | 🔷 | — |
| T3.19 | Update logs | `update_log.md`, `issue_log.md` | 🔷 | — |

---

## 9. Files and Modules to Create/Update

| File/Folder                                         | Action | Purpose                                                    |
| :-------------------------------------------------- | :----- | :--------------------------------------------------------- |
| `eks/engine/graph/__init__.py`                      | Create | Graph DB package init                                      |
| `eks/engine/graph/graph_store.py`                   | Create | Abstract graph store interface                             |
| `eks/engine/graph/neo4j_store.py`                   | Create | Neo4j implementation of graph store interface              |
| `eks/engine/graph/graph_schema.py`                  | Create | Node label and relationship type definitions               |
| `eks/engine/graph/relationship_builders.py`         | Create | Doc-to-doc, doc-to-object relationship construction logic  |
| `eks/engine/extractors/__init__.py`                 | Create | Structured asset loader package init                       |
| `eks/engine/extractors/base_asset_loader.py`        | Create | Abstract asset loader interface — load sheet data by tag_type fragment rules |
| `eks/engine/extractors/equipment_loader.py`         | Create | Equipment sheet loader (AT_EQUIP, AT_EQPMP, AT_EQTNK, AT_EQVES, AT_EQEXC) |
| `eks/engine/extractors/instrument_loader.py`        | Create | Instrument sheet loader (AT_INST_, AT_INST_CS, AT_INST_FLO) |
| `eks/engine/extractors/valve_loader.py`             | Create | Valve sheet loader (AT_CVALVE, AT_PSV, AT_HVALVE)         |
| `eks/engine/extractors/pipeline_loader.py`          | Create | Pipeline sheet loader (AT_PROCESS) with CONNECTS_TO edge builder |
| `eks/engine/extractors/motor_loader.py`             | Create | Motor sheet loader (AT_MOTOR)                              |
| `eks/engine/extractors/inline_component_loader.py`  | Create | Inline Component sheet loader (AT_INCOMP)                  |
| `eks/engine/parsers/dwg_parser_stub.py`             | Create | DWG parser stub (deferred implementation)                  |
| `eks/engine/parsers/dgn_parser_stub.py`             | Create | DGN parser stub (deferred implementation)                  |
| `eks/config/eks_base_schema.json`                   | Update | Add graph node/relationship type schema definitions        |
| `eks/config/eks_config.json`                        | Update | Add Neo4j connection settings + asset loader config        |
| `eks/test/test_phase3.py`                           | Create | Integration tests for Phase 3 components                   |
| `eks/engine/extractors/asset_embed_trigger.py`      | Create | Calls asset text builder + Qdrant upsert after Neo4j batch load (R40, R42) |

---

## 10. Risks and Mitigation

| Risk                                             | Likelihood | Impact | Mitigation                                                        |
| :----------------------------------------------- | :--------: | :----: | :---------------------------------------------------------------- |
| Neo4j setup complexity in local/dev environment  | Medium     | Medium | Provide Docker Compose setup; document setup steps in docs        |
| Structured asset data quality varies (44% pending fill) | High | Medium | Schema-driven loading gracefully handles nulls; log data gaps per tag |
| Excel column names differ between sheets         | Medium     | Low    | Column normalization map defined in asset schema config            |
| Graph schema changes cascade to retrieval logic  | Medium     | High   | Abstract graph interface; version graph node/relationship schema  |
| CAD library unavailable for DWG/DGN parsing      | High       | Low    | Stub interfaces only in this phase; full implementation deferred  |
| Pipeline-to-component CONNECTS_TO edges may be incomplete | Medium | Medium | Log missing FROM/TO_COMPONENT; support incremental updates |
| Pipeline sheet has 612 duplicate KEYTAG rows (same tag on multiple P&ID sheets) | High | Medium | Deduplicate on load: merge rows by keytag, collect all DOC_FNAME as list for REFERENCED_BY_DWG edges |

---

## 11. Potential Future Issues

- Datadrop incremental updates: when the source Excel is re-exported with more filled fields, the graph must support upsert without duplicating nodes
- Graph query performance may require index tuning and query optimization for large document sets
- Multi-hop graph traversal for complex engineering relationships may introduce latency
- CAD parsing (DWG/DGN) may require commercial library licenses
- Pipeline-to-component graph traversal depth may need limits for retrieval performance

---

## 12. Success Criteria

- [ ] Neo4j integration operational with Docker Compose setup documented
- [ ] Graph schema defined: all required node labels (per AT_ category) and relationship types (including CONNECTS_TO, REFERENCED_BY_DWG)
- [ ] Document-to-document REFERENCES relationships populated from cross-reference detection
- [ ] Document-to-asset relationships populated from P&ID file name cross-references
- [ ] Superseded document lookup functional via SUPERSEDES chain traversal
- [ ] All 7 Excel sheets ingested into Neo4j: Equipment, Inline Component, Instrument, Motor, Pipeline, CONTROLVALVE, MANUALVALVE
- [ ] Pipeline-to-component CONNECTS_TO edges populated from FROM/TO_COMPONENT fields
- [ ] Structured asset loaders operational for all 14 AT_ tag_types
- [ ] Zero-code extensibility verified: add a new AT_ type and conditional fragment rule to `eks_asset_config.json` only — confirm loader applies correct fragments without code change
- [ ] Asset embeddings upserted to `eks_assets` after each datadrop load batch (R40)
- [ ] Asset vector upsert on reload: changed keytags re-embedded, stale vectors removed (R42)
- [ ] Automated Document Metadata Extraction (R43) operational: extract 11 extended fields from cover sheets; store in Registry
- [ ] DWG/DGN parser stubs in place with correct interface signature
- [ ] Integration tests passing for graph CRUD, asset loaders, relationship builders

---

## 13. Deliverables

- Graph DB modules: `graph_store.py`, `neo4j_store.py`, `graph_schema.py`, `relationship_builders.py`
- Asset loader modules: `base_asset_loader.py`, `equipment_loader.py`, `instrument_loader.py`, `valve_loader.py`, `pipeline_loader.py`, `motor_loader.py`, `inline_component_loader.py`
- Parser stubs: `dwg_parser_stub.py`, `dgn_parser_stub.py`
- Updated schema: `eks_base_schema.json`, `eks_config.json`
- Asset graph dump: `output/eks_asset_graph.json`
- Test file: `test_phase3.py`
- Asset embed trigger: `asset_embed_trigger.py`
- Report: `eks/workplan/reports/phase_3_knowledge_graph_report.md`

---

## 14. References

1. [eks_system_workplan.md](eks_system_workplan.md) — Master workplan
2. [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) — Phase 1 prerequisite
3. [phase_2_chunking_embedding_workplan.md](phase_2_chunking_embedding_workplan.md) — Phase 2 prerequisite
4. [agent_rule.md](/home/franklin/dsai/Engineering-and-Design/agent_rule.md)
5. [eks/readme.md](/home/franklin/dsai/Engineering-and-Design/eks/readme.md)
6. [eks/data/twrp/datadrop/Datadrop Summary.xlsx](/home/franklin/dsai/Engineering-and-Design/eks/data/twrp/datadrop/Datadrop%20Summary.xlsx) — Project asset datadrop (7 sheets)
7. [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) — Phase 1 asset schema fragments (R36)
