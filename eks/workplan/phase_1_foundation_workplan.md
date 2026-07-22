# EKS Phase 1 — Foundation: Project Structure, Schema & Document Registry

- **Document ID**: WP-EKS-P1-001
- **Current Version**: 5.4
- **Status**: 🔷 IN PROGRESS — **v5.3**: §10.3 (Defect Root-Cause Fixes) merged into §10.1 — single 36-row table covering design (§5–§30) + defects (§39–§50) in one view. Full history in [Appendix P1.6](appendix_p1.6_phase1_revision_history.md).
- **Last Updated**: 2026-07-20
- **Parent Workplan**: [eks_system_workplan.md](eks_system_workplan.md)
- **Phase Dependency**: None — first phase

---

## 1. Index of Content

- [1. Index of Content](#1-index-of-content)
- [2. Title and Description](#2-title-and-description)
- [3. Revision History → Appendix P1.6](#3-revision-history--appendix-p16)
- [4. Objective](#4-objective)
- [5. Evaluation and Alignment with Existing Architecture](#5-evaluation-and-alignment-with-existing-architecture)
- [6. Dependencies with Other Tasks](#6-dependencies-with-other-tasks)
- [7. Risks and Mitigation](#7-risks-and-mitigation)
- [8. Data Export — CSV/Excel Pipeline Output — ✅ COMPLETE](#8-data-export--csvexcel-pipeline-output--complete)
- [9. Success Criteria & Deliverables → SC Log + P1.2 §4](#9-success-criteria--deliverables)
- [10. Phase 1 Implementation Index](#10-phase-1-implementation-index)
  - [10.1 Design & Implementation](#101-design--implementation)
  - [10.2 Checklists & Deliverables](#102-checklists--deliverables)
- [11. References](#11-references)

---

## 2. Title and Description

Establish the EKS project foundation and the canonical, schema-driven pipeline substrate that all subsequent phases build upon. This phase creates the bedrock that all subsequent phases build upon.

Deliverables:
- AGENTS.md-compliant project folder structure and conda environment
- Canonical 3-layer schema design (base/setup/config) across core, asset, and ontology sets — including the universal plant-item asset schema with 13 reusable fragments and zero-code extensibility, ISO 15926 ontology integration, and the enhanced document schema v2 with type/file/element registries
- Schema-driven SSOT global parameters and universal system parameters (runtime behavior config)
- Document ingestion plug-ins for PDF/DOCX/XLSX plus a DuckDB-backed document registry with full CRUD and revision management (preserve-all revisions + latest-revision flag)
- Tiered logging (levels 0–3), debug object, and structured trace table, along with a schema-driven error/message catalog and per-document 6-dimension health scoring
- The end-to-end discovery → register → route → parse → detect → score → review pipeline (auto-DDL generation, file scanner, parser router, orchestrator with rollback, manual review workflow)
- Universal path resolution and a converged pipeline entry point (CLI + web + per-phase HTTP backend) funneling through a shared `run_pipeline(context)` / `bootstrap_pipeline()` helper
- Initiation integrity, config flattening, cross-cutting remediation, and architectural patterns (BaseEngine, Validator, factories, setup validation, data_dir traversal guard)

---

## 3. Revision History → Appendix P1.6

> **All revision history relocated to [Appendix P1.6](appendix_p1.6_phase1_revision_history.md)** — 102 revision entries from v0.1 (2026-06-11) through v5.3 (2026-07-20). Only the high-level eras summary is retained below.

### Eras Summary

| Era | Versions | Dates | Theme |
|:----|:---------|:------|:------|
| **Foundation** | v0.1–v2.5 | 2026-06-11 to 2026-06-22 | Folder scaffolding, conda env, 3-layer schemas, document parsers, DuckDB registry, document schema v2 |
| **Pipeline Integration** | v3.0–v3.29 | 2026-06-22 to 2026-07-08 | Auto-DDL, file scanner, parser router, orchestrator, Phase 1.3 initiation harmonization, error/message catalog, 6-dim health scoring, project_setup integration, Appendix F architecture patterns |
| **Workplan Restructure** | v3.40–v3.52 | 2026-07-09 to 2026-07-11 | Initiation config flattening, schema discovery, system parameters SSOT, universal path resolution, workplan restructuring (Master Task Index), section resequence, canonical workplan promotion |
| **Bootstrap & Entry-Point Convergence** | v3.53–v3.87 | 2026-07-11 to 2026-07-20 | Universal BootstrapManager (L19), entry-point relocation (CLI + web + backend), anchor-folder path resolution, cross-platform discovery, universal CLI parser (L18), pre-bootstrap logger (I113), environment checks (I114), structured BootstrapError (I111), preload infrastructure guard (I117), lazy-import refactor |
| **Appendix Relocation** | v4.8–v5.0 | 2026-07-20 | §40–§50 defect deep-dives → P1.1; §43 file property extraction → Appendix J; §47 schema-driven export → P1.3; §3 full history → P1.6; 50→11 section collapse; §10 Implementation Index consolidates all appendix redirects |
| **Implementation Index Consolidation** | v5.1–v5.3 | 2026-07-20 | §10.1 table enhanced: added Tasks column (P1.4 cross-ref), Key Issues column (issue_log cross-ref), Status column (completion status per section); §10.3 merged into §10.1 as a single 36-row table |

---

## 4. Objective

- Create the EKS project folder structure compliant with AGENTS.md
- Design and implement the canonical schema (base/setup/config pattern)
- Build the document registry (metadata DB) with full CRUD support
- Implement plug-in document parsers: PDF, DOCX, XLSX
- Implement revision management: preserve all revisions, latest revision flag
- Establish tiered logging (levels 0–3), debug object, and structured trace table
- Implement SSOT global parameter registry via schema-driven config
- Design the universal plant-item asset schema (13 reusable fragments, zero-code extensibility) following the canonical fragment pattern
- Integrate ISO 15926 ontology (dynamic, config-driven ontology schema with classes, properties, relationships)
- Implement the schema-driven error/message catalog and per-document 6-dimension health scoring with structural elements table
- Reorganize the document schema into the enhanced 3-layer Document Schema v2 with type/file/element registries
- Implement the end-to-end pipeline: auto-DDL generation, file scanner, parser router, pipeline orchestration (with rollback), and manual review workflow
- Establish universal path resolution and a converged pipeline entry point (CLI + web + per-phase HTTP backend) funneling through a shared `run_pipeline(context)` / `bootstrap_pipeline()` helper
- Deliver initiation integrity, config flattening, cross-cutting remediation, and architectural patterns (BaseEngine, Validator, factories, setup validation, data_dir traversal guard)

---

## 5. Evaluation and Alignment with Existing Architecture

- **Schema pattern**: Directly adopts `project_setup_base.json / project_setup.json / project_config.json` from `dcc/config/schemas`
- **Logging**: Directly adopts tiered logging and debug object from `dcc/workflow/core_engine/` patterns
- **Module design**: SSOT global parameters via schema-driven config per AGENTS.md Section 4
- **New**: Document registry with metadata DB is new to this workspace; no prior precedent in DCC

---

## 6. Dependencies with Other Tasks

1. **AGENTS.md** — Governs all coding standards, module design, logging
2. **dcc/config/schemas** — Schema base/setup/config pattern to replicate
3. **External**: DuckDB (preferred for dev) or PostgreSQL for metadata DB
4. **Next Phase**: Phase 2 depends on document registry and parsers from this phase

---

## 7. Risks and Mitigation

| Risk                                         | Likelihood | Impact | Mitigation                                                         |
| :------------------------------------------- | :--------: | :----: | :----------------------------------------------------------------- |
| DB schema changes cascade to downstream code | Medium     | High   | Schema-driven design isolates DB structure from processing logic   |
| PDF/DOCX parsing quality varies by doc type  | High       | Medium | Abstract parser interface allows per-format tuning; log errors     |
| DWG/DGN parsing requires CAD libraries       | High       | Low    | Deferred to Phase 3; stub plug-in interface stubbed in this phase  |
| Schema design diverges from dcc pattern      | Low        | Medium | Explicitly use dcc/config/schemas as template reference            |
| Metadata extraction accuracy is low          | Medium     | Medium | Implement Manual Verification workflow in Phase 5                  |

---

## 8. Data Export — CSV/Excel Pipeline Output — ✅ COMPLETE

> **Canonical Source**: [appendix_p1.3_phase1_data_export.md](appendix_p1.3_phase1_data_export.md) — full design, implementation, task breakdowns, success criteria, and post-implementation fixes (I188, I189, I192, I193).

**Summary**: Human-readable CSV/Excel export of Phase 1 pipeline results (discovery inventory, extraction results, review flags) via universal L22 `DataExporter` module in `common/library/export/`. Schema-driven column resolution (I193) replaces the original hardcoded 11-field subset with ~50 `x_export`-flagged fields. Three post-implementation fixes applied: I188 (empty files), I189 (stale output + test-DB pollution), I192 (root-level copies for user convenience). All 5 issues (I126, I188, I189, I192, I193) resolved. Detailed in [Appendix P1.3](appendix_p1.3_phase1_data_export.md).

---

## 9. Success Criteria & Deliverables

> **Success Criteria → [p1_sc_log.md](../log/phase1/p1_sc_log.md)** — 349 success criteria items with issue and task cross-references. Includes all 89 items from retired appendix P1.5 §33 plus per-section criteria, appendix F/I/J items, and Phase 1.2 workplan criteria.
>
> **Deliverables → [P1.2 §4](appendix_p1.2_phase1_scope.md#4-phase-1-deliverables-consolidated-from-34--37)** — Consolidated deliverable list merged from §34 + §37 of this workplan. Includes all artifacts from schema files through pipeline modules and common library components. Appendix P1.5 (source for SC checklist) is retired — archived at `eks/archive/workplan/appendix_p1.5_phase1_checklists.md`.

---

## 10. Phase 1 Implementation Index

> All detailed implementation specifications, task breakdowns, architecture diagrams, and defect analyses have been relocated to dedicated P1.x appendices. This section is a routing table — map from high-level topic to canonical source.

### 10.1 Design & Implementation

| Original § | Topic | Tasks | Key Issues | Canonical Source |
| :---------- | :---- | :---- | :--------- | :--------------- |
| §5 | Scope Summary (R01–R100) | — (scoping doc) | — | [P1.2 §1](appendix_p1.2_phase1_scope.md#1-phase-1-scope-summary) |
| §8 | Master Task Index | T1.1–T1.99.203 (all 203+) | I001–I233 (all Phase 1) | [Task Log](../log/phase1/p1_task_log.md#status-summary) (§2–23) |
| §9 | Pipeline Architecture & 11 Function Tables | — (design doc) | I013, I215, I225, I229, I230 | [P1.1 §3](appendix_p1.1_phase1_architecture.md#3-phase-1-pipeline-architecture--function-tables) |
| §10 | Files & Modules to Create/Update | — (per-file index) | I024, I094, I231 | [P1.2 §3](appendix_p1.2_phase1_scope.md#3-files-and-modules-to-createupdate) + [P1.1 §1.3](appendix_p1.1_phase1_architecture.md#13-module-inventory) |
| §11 | Project Folder Structure | T1.1 | — | [P1.1 §2](appendix_p1.1_phase1_architecture.md#2-phase-project-folder-structure) |
| §12 | Detailed Schema Design | T1.3–T1.5 (design); T1.42–T1.47, T1.50–T1.51 (fragments) | I004, I005, I010, I011, I194 | [Task Log §4](../log/phase1/p1_task_log.md#4-core-schema-suite-basesetupconfig-fragment-schemas-tasks) |
| §13 | Parser Module Architecture | T1.8–T1.11 (parsers); T1.9 (abstract base) | I015, I016, I024 | [P1.1 §5](appendix_p1.1_phase1_architecture.md#5-independent-parser-module-architecture) |
| §14 | Foundation & Compliance (R99) | T1.1–T1.2, T1.14–T1.16, T1.33, T1.48–T1.49, T1.52–T1.53, T1.55–T1.57, T1.65–T1.67, T1.70, T1.74 | I001, I002, I003, I010, I017–I020, I046, I093, I226, I227 | [Task Log §2](../log/phase1/p1_task_log.md#2-foundation-environment-compliance-r99-tasks) |
| §15 | Architectural Patterns — Context, Factories & Orchestration | T1.54, T1.58–T1.64 | I208–I225 (GAP-A1/A18), I230 | [Task Log §3](../log/phase1/p1_task_log.md#3-architectural-patterns-context-factories-orchestration-hardening-appendix-f-tasks) |
| §16 | Core Schema Suite (base/setup/config + fragments) | T1.3–T1.6, T1.42–T1.47, T1.50–T1.51 | I004, I005, I010, I011, I022–I023, I026–I027, I029–I031, I194 | [Task Log §4](../log/phase1/p1_task_log.md#4-core-schema-suite-basesetupconfig-fragment-schemas-tasks) + [P1.1 §6.2](appendix_p1.1_phase1_architecture.md#62-core-schema-suite) |
| §17 | Asset Schema — Universal Plant Item (R36/R39) | T1.17–T1.20 | I228, I021 | [Task Log §5](../log/phase1/p1_task_log.md#5-asset-schema-universal-plant-item-r36r39-tasks) + [P1.1 §6.3](appendix_p1.1_phase1_architecture.md#63-asset-schema--universal-plant-item) |
| §18 | Ontology Integration (R44, ISO 15926) | T1.23–T1.29 | I007, I008 | [Task Log §6](../log/phase1/p1_task_log.md#6-ontology-integration-r44-iso-15926-tasks) + [P1.1 §6.5](appendix_p1.1_phase1_architecture.md#65-ontology-integration-iso-15926) |
| §19 | Logging, Errors & Health Scoring (R33/R34/R51) | T1.13, T1.30–T1.32, T1.41, T1.68–T1.69, T1.71, T1.75–T1.76, T1.99.35–T1.99.39 | I014, I105, I195–I198, I199–I203, I204–I207 (GAP-D1/D13) | [Task Log §7](../log/phase1/p1_task_log.md#7-logging-errors-health-scoring-r33r34r51-tasks) + [P1.1 §6.6](appendix_p1.1_phase1_architecture.md#66-error--message-schemas) |
| §20 | Document Registry & Revision Management (R02/R21/R22/R29) | T1.7–T1.8, T1.21–T1.22 | I006, I131, I147–I162 (file properties), I184–I187 (registration/change), I212, I224 | [Task Log §8](../log/phase1/p1_task_log.md#8-document-registry-revision-management-r02r21r22r29-tasks) |
| §21 | Document Parsers — PDF/DOCX/XLSX (R01/R26) | T1.9–T1.12 | I015, I132, I024, I025, I133–I146, I155, I157, I163 (error codes + FilenameParser) | [Task Log §9](../log/phase1/p1_task_log.md#9-document-parsers-pdfdocxxlsx-r01r26-tasks) + [P1.1 §5](appendix_p1.1_phase1_architecture.md#5-independent-parser-module-architecture) |
| §22 | Document Schema v2 — 3-Layer Reorganization (R52/R53) | T1.34, T1.35.1–T1.35.6 | I012, I164–I168 (5 metadata gaps), I169–I175 (7-column bulk), I194 (cross-source) | [Task Log §10](../log/phase1/p1_task_log.md#10-document-schema-v2-3-layer-reorganization-r52r53-tasks) + [P1.1 §6.4](appendix_p1.1_phase1_architecture.md#64-document-schema-v2) |
| §23 | Pipeline Orchestration (R54–R58/R57) | T1.36–T1.40, T1.72–T1.73 | I013, I215, I225, I229 | [Task Log §11](../log/phase1/p1_task_log.md#11-pipeline-orchestration-r54r58r57-tasks) + [P1.1 §3,§4](appendix_p1.1_phase1_architecture.md#3-phase-1-pipeline-architecture--function-tables) |
| §24 | Initiation Integrity, Hardening & Harmonization | T1.77–T1.83 | I046, I100 | [Task Log §12](../log/phase1/p1_task_log.md#12-initiation-integrity-hardening-harmonization-t177t189-tasks) |
| §25 | Initiation Schema & Validation Harmonization | T1.84–T1.89 | I046 | [Task Log §13](../log/phase1/p1_task_log.md#13-initiation-schema-validation-harmonization-t184t189-tasks) |
| §26 | Initiation Config Flattening — DCC Pattern | T1.90–T1.95 | — | [Task Log §14](../log/phase1/p1_task_log.md#14-initiation-config-flattening-dcc-projectconfig-pattern-t190t195-tasks) |
| §27 | Schema Discovery & Registration — Discovery-Driven Loading | T1.96.1–T1.96.6 | — | [Task Log §15](../log/phase1/p1_task_log.md#15-schema-discovery-registration-discovery-driven-loading-t196-tasks) |
| §28 | System Parameters — SSOT Centralization | T1.97.1–T1.97.14 | I091 | [Task Log §16](../log/phase1/p1_task_log.md#16-system-parameters-ssot-centralization-t197-tasks) |
| §29 | Universal Path Resolution & Schema-Driven Init | T1.98.1–T1.98.8 | I089, I090, I130 | [Task Log §17](../log/phase1/p1_task_log.md#17-universal-path-resolution-schema-driven-initialization-i089-i090-tasks) |
| §30 | Pipeline Entry-Point & Sub-Pipeline Convergence (I092 / R60) | T1.99.1–T1.99.83 | I078, I092, I096–I100, I102–I107, I109–I117, I126, I188–I192, I231–I233 | [Task Log §18](../log/phase1/p1_task_log.md#18-pipeline-entry-point-per-phase-sub-pipeline-convergence-i092-r60-tasks) |
| §39 | Bootstrap path-resolution rooting defect fix | — | I130 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
| §40 | KeyError: 'revision' in register_placeholders | — | I131 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
| §41 | .dwg file type orphan fix (Option B: CAD document type) | — | I132 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
| §42 | Unified P-prefix error codes + Appendix I FilenameParser | — | I133–I146, I155, I157, I163 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
| §43 | File property extraction — 14 issues, 13 registry columns | — | I147–I162 | [Appendix J §J14](appendix_j_file_property_parser.md#j14-implementation-record--complete) |
| §44 | Document metadata completeness — 5 schema gaps | — | I164–I168 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
| §45 | Remaining metadata schema gaps — 7-column bulk addition | — | I169–I175 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
| §46 | File registration, change detection & cross-project abstraction | — | I184–I187 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
| §47 | Schema-driven export columns (~50 fields, replaces 11-field subset) | — | I193 | [P1.3 §5.6](appendix_p1.3_phase1_data_export.md#56-detail-i193--schema-driven-export-columns-t199157-162) |
| §48 | Appendix D vs. actual pipeline cross-source audit (13 gaps) | — | I195–I207 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
| §49 | Appendix E+F vs. pipeline architecture cross-source audit (18 gaps) | — | I208–I225 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |
| §50 | `str(5)` bug fix — restore exception messages (13 instances, 4 files) | — | I226 | [P1.1 §7](appendix_p1.1_phase1_architecture.md#7-issues--fixes--summary-with-cross-references) |

### 10.2 Checklists & Deliverables

| Original § | Topic | Canonical Source |
| :---------- | :---- | :--------------- |
| §33, §36 | Success Criteria (349-item checklist) | [SC Log](../log/phase1/p1_sc_log.md) |
| §34 | Deliverables | [P1.2 §4](appendix_p1.2_phase1_scope.md#4-phase-1-deliverables-consolidated-from-34--37) |

---

## 11. References

1. [AGENTS.md](../../AGENTS.md) — Repository guidelines
2. [eks/readme.md](../readme.md) — EKS project overview
3. [dcc/config/schemas](../../dcc/config/schemas) — Schema pattern reference
4. [appendix_a_asset_schema.md](appendix_a_asset_schema.md) — Universal Plant Item Schema appendix
5. [appendix_c_ontology.md](appendix_c_ontology.md) — Dynamic ISO 15926-Aligned Ontology
6. [appendix_d_pipeline_messages_errors.md](appendix_d_pipeline_messages_errors.md) — Pipeline Messages & Error Codes (v0.3)
7. [appendix_e_schema_design.md](appendix_e_schema_design.md) — EKS Schema Design (v0.1)

### P1.x Appendices

| Appendix | File | Coverage |
| :------- | :--- | :------- |
| P1.1 | [appendix_p1.1_phase1_architecture.md](appendix_p1.1_phase1_architecture.md) | Architecture & design blueprints |
| P1.2 | [appendix_p1.2_phase1_scope.md](appendix_p1.2_phase1_scope.md) | Scope summary, files/modules, deliverables |
| P1.3 | [appendix_p1.3_phase1_data_export.md](appendix_p1.3_phase1_data_export.md) | Data export (CSV/Excel) design & implementation |
| P1.4 | [p1_task_log.md](../log/phase1/p1_task_log.md) | Task breakdown (replaces retired appendix_p1.4) |
| P1.5 | retired — archived at [eks/archive/workplan/](../archive/workplan/appendix_p1.5_phase1_checklists.md) | SC → [SC Log](../log/phase1/p1_sc_log.md); Deliverables → [P1.2 §4](appendix_p1.2_phase1_scope.md#4-phase-1-deliverables-consolidated-from-34--37) |
| P1.6 | [appendix_p1.6_phase1_revision_history.md](appendix_p1.6_phase1_revision_history.md) | Full revision history |
