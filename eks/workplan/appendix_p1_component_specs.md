# Appendix P1-B: Component Specification Index

> Extracted from [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md)
> Auto-generated: 2026-07-20

---

## Contents

- [14. Foundation, Environment & Compliance (R99)](#foundation-environment--compliance-r99)
- [16. Core Schema Suite (base/setup/config + fragment schemas)](#core-schema-suite-basesetupconfig--fragment-schemas)
- [17. Asset Schema — Universal Plant Item (R36/R39)](#asset-schema---universal-plant-item-r36r39)
- [18. Ontology Integration (R44, ISO 15926)](#ontology-integration-r44-iso-15926)
- [19. Logging, Errors & Health Scoring (R33/R34/R51)](#logging-errors--health-scoring-r33r34r51)
- [20. Document Registry & Revision Management (R02/R21/R22/R29)](#document-registry--revision-management-r02r21r22r29)
- [21. Document Parsers — PDF/DOCX/XLSX (R01/R26)](#document-parsers---pdfdocxxlsx-r01r26)
- [22. Document Schema v2 — 3-Layer Reorganization (R52/R53)](#document-schema-v2---3-layer-reorganization-r52r53)
- [23. Pipeline Orchestration (R54–R58/R57)](#pipeline-orchestration-r54r58r57)
- [24. Initiation Integrity, Hardening & Harmonization (T1.77–T1.89](#initiation-integrity-hardening--harmonization-t177t189)
- [25. Phase 1.3 — Initiation Schema & Validation Harmonization (T1](#phase-13---initiation-schema--validation-harmonization-t1)
- [26. Initiation Config Flattening — DCC project_config Pattern (T](#initiation-config-flattening---dcc-projectconfig-pattern-t)
- [27. Schema Discovery & Registration — Discovery-Driven Loading (](#schema-discovery--registration---discovery-driven-loading-)
- [28. System Parameters — SSOT Centralization (T1.97)](#system-parameters---ssot-centralization-t197)
- [29. Universal Path Resolution & Schema-Driven Initialization (I0](#universal-path-resolution--schema-driven-initialization-i0)
- [30. Pipeline Entry-Point & Per-Phase Sub-Pipeline Convergence (I](#pipeline-entry-point--per-phase-sub-pipeline-convergence-i)

---

## 14. Foundation, Environment & Compliance (R99)

Project scaffolding, conda environment, SSOT config registry, tests/logs, cross-cutting remediation, architectural base classes, setup validation, and cross-platform hardening.

### Task Breakdown

| # | Task | Details | Scope | Status | Related |
| :---

## 16. Core Schema Suite (base/setup/config + fragment schemas)

Canonical 3-layer schema design/loader and project-scoped fragment schemas (project code, discipline, department, facility) plus base-schema SSOT enforcement and asset-context fragment.

### Task Breakdown

| # | Task | Details | Scope | Status | Related |
| :---

## 17. Asset Schema — Universal Plant Item (R36/R39)

13 reusable asset fragments, asset type registry, and gap-analysis-driven fragment expansion with zero-code extensibility.

### Task Breakdown

| # | Task | Details | Scope | Status | Related |
| :---

## 18. Ontology Integration (R44, ISO 15926)

Dynamic, config-driven ontology schema, config, loader extension, alias-aware mapping, embedded relationship metadata, and document ontology/mapping metadata.

### Task Breakdown

| # | Task | Details | Scope | Status | Related |
| :---

## 19. Logging, Errors & Health Scoring (R33/R34/R51)

Tiered logger/debug object, schema-driven error/message catalog, error & message managers, 6-dimension health scorer, structure detector, and server-side activation/persistence.

### Task Breakdown

| # | Task | Details | Scope | Status | Related |
| :---

## 20. Document Registry & Revision Management (R02/R21/R22/R29)

DuckDB-backed document registry with full CRUD, revision preservation + latest-revision flag, registry remediation, and extended document metadata.

### Task Breakdown

| # | Task | Details | Scope | Status | Related |
| :---

## 21. Document Parsers — PDF/DOCX/XLSX (R01/R26)

Abstract base parser plus concrete PDF, XLSX, and DOCX parsers with plug-in interface.

### Task Breakdown

| # | Task | Details | Scope | Status | Related |
| :---

## 22. Document Schema v2 — 3-Layer Reorganization (R52/R53)

Separate document schema set with type/file/element registries and enhanced enums.

### Task Breakdown

| # | Task | Details | Scope | Status | Related |
| :---

## 23. Pipeline Orchestration (R54–R58/R57)

Auto-DDL generation, file scanner, parser router, orchestrator, manual review, contract enforcement, and checkpoint persistence.

### Task Breakdown

| # | Task | Details | Scope | Status | Related |
| :---

## 24. Initiation Integrity, Hardening & Harmonization (T1.77–T1.89)

Phase 1 foundation is extended by two follow-on initiation work batches that close DCC-alignment gaps and universalize project-setup validation. Detailed test evidence lives in the consolidated foundation report (§24/§25) and in `../archive/phase_1_t179_t183_report.md` (RP-EKS-P1-T179-001, archived) for T1.79–T1.83.

### 24. Initiation Integrity (T1.77–T1.78)1
- **T1.77**: `ProjectSetupValidator.validate_all()` + `get_readiness_status()` wired into `phase1_server._run()` fail-fast gate; `--debug`/`--level` CLI flags with effective-level logic; `data_dir` existence + `recursive` bool validated before concurrency guard. 8 validator unit tests + 3 server integration tests. 202/202 pass.
- **T1.78**: Remediation of DCC gaps — `eks.yml`→`eks/eks.yml` path fix, input-file readability (G2), dependency probe + output-path validation (G3/G4), `--skip-readiness` override (G5), error code constants (G7); fixed pre-existing `_LogCapture.level` bug. 207/207 pass.

### 24. Initiation Schema-Driven Hardening (T1.79–T1.83)2
| Task | I-Ref | Description | Status |
| :---

## 25. Phase 1.3 — Initiation Schema & Validation Harmonization (T1.84–T1.89)

**Source workplan (archived)**: [phase_1.3_initiation_harmonization_workplan.md](../archive/phase_1.3_initiation_harmonization_workplan.md) — WP-EKS-P1.3-001
**Status**: ✅ COMPLETE — T1.84–T1.89 all implemented. Universal `ValidationManager` in `common/library/utility/validation/`. EKS `project_setup` schema reshaped to DCC-aligned object model. DCC itself NOT modified (deferred follow-up).

### 25.1 Objective
Achieve **schema-design consistency** and **code-module universality** for project-setup validation, so that EKS and (later) DCC validate project structure through one shared, well-tested module and through schemas that follow the same shape. EKS's AGENTS.md §7-mandated folder names are preserved — only the *schema shape* (not the folder names) aligns with DCC.

### 25.2 Scope Summary
| ID | Category | Title | Details | Status | Related |
| :-- | :---

## 26. Initiation Config Flattening — DCC project_config Pattern (T1.90–T1.95)

**Objective**: Align EKS `eks_config.json` with DCC `project_config.json` — store the actual setup values (`folders` / `root_files` / `schema_files` / `environment` / `dependencies` / `project_metadata` / `discovery_rules`) at the **top level** instead of nested under a `project_setup` wrapper. This makes the universal `ValidationManager` (and a future universal schema loader) work for both projects with **zero per-project branching**, completing the Phase 1.3 universality goal, and removes the orphaned `eks_project_setup_config.json` (T1.86 artifact).

### 26.1 Scope Summary
| ID | Category | Title | Details | Status | Related |
| :-- | :---

## 27. Schema Discovery & Registration — Discovery-Driven Loading (T1.96)

**Objective**: Add discovery-driven schema registration to EKS by (1) extracting the shared `discover_schema_files()` function from DCC `ref_resolver.py:164-230` into the `common/` library, (2) adding `discovery_rules` data to `eks_config.json`, (3) refactoring `schema_loader.py` to use config-driven loading (explicit `schema_files` + `discovery_rules` glob), and (4) wiring `ValidationManager.validate_discovery_rules()` into `setup_validator.py`. Closes I087.

**Rationale**: Currently `schema_loader.py` hardcodes 22 filenames — adding a new schema set requires source code changes. DCC's `_extract_registered_schemas()` implements a reusable pattern: explicit `schema_files` merge with glob-based `discovery_rules`. Extracting this to `common/` makes it available to both projects and future phases.

### 27.1 Scope Summary

| ID | Category | Title | Details | Status | Related |
| :-- | :---

## 28. System Parameters — SSOT Centralization (T1.97)

**Objective**: Centralize all runtime behavior knobs (`fail_fast`, `log_level`, `debug_mode`, `skip_readiness`, `retry_count`, `retry_delay`, `api_timeout`, `ollama_timeout`, `db_timeout`) into a schema-defined `system_parameters` block in `eks_config.json`. Create a universal `get_system_param()` function in `common/library/config/` that handles both EKS flat-object and DCC array-of-entries shapes. Remove hardcoded equivalents from `phase1_server.py`, `error_manager.py`, `registry.py`, `server.py`. Closes I088.

**Rationale**: Currently these values are scattered across global variables (`phase1_server.py:103-105`), constructor defaults (`error_manager.py:21`), function defaults (`registry.py:326`), and literal constants (`server.py:359,429`). I088 documents this as a SSOT violation versus DCC's `project_config.json → system_parameters` pattern. A universal `get_system_param()` in `common/` makes the fix reusable for DCC and future phases.

### 28.1 Scope Summary

| ID | Category | Title | Details | Status | Related |
| :-- | :---

## 29. Universal Path Resolution & Schema-Driven Initialization (I089 + I090)

**Objective**: (1) Adopt EKS's `global_paths` as the universal canonical schema-driven path pattern and provide a shared `PathResolver` in `common/library/paths/` that normalizes both EKS and DCC path shapes — closes **I089**. (2) Bring EKS to DCC parity for `workflow_files`/`tool_files`/`folder_creation` (schema-driven initialization) — closes **I090**.

**Rationale**: A re-audit of DCC's actual code (I089 re-evaluation) found its path model is weaker than EKS's:
- `base_path` is derived by **script-location traversal** (`default_base_path()` walks `Path(__file__).parents` to find `"workflow"`), not from config.
- `data`/`output` dirs are **hardcoded literals** (`base_path / "data"`, `base_path / "output"`).
- `discovery_rules[].directory` are used **only for schema discovery**, not working dirs.
- `folder_creation.required_directories[].name` is used only for auto-create checks.

By contrast, EKS's `global_paths` (hardened by T1.80/T1.82/T1.83 — no hardcoded fallbacks) is **genuinely schema-driven SSOT**. Therefore the universal pattern adopts EKS `global_paths` as canonical, with a bidirectional `PathResolver` normalizing DCC's shape into it. For I090, EKS gains `workflow_files`/`tool_files` blocks (currently absent), while `folder_creation` is satisfied by the resolver deriving the create-list from the canonical `global_paths` — EKS deliberately does **not** add a separate DCC-style `folder_creation` block (documented design decision).

### 29.1 Scope Summary

| ID | Category | Title | Details | Status | Related |
| :-- | :---

## 30. Pipeline Entry-Point & Per-Phase Sub-Pipeline Convergence (I092 / R60)

**Objective**: Resolve I092 by converging EKS pipeline entry points on a shared `run_pipeline(context)` funnel (mirroring DCC's CLI + UI + web → one `run_engine_pipeline(context)`) and satisfying R60 / AGENTS.md §18.13 — every phase (1–5) runs as an independent sub-pipeline with its own `phase{N}_server.py` backend. Phase 1 already has `phase1_server.py`; it needs the convergence cleanup. Phases 2–5 need the full backend + runner.

### 30. Tasks (Phase 1 entry-point convergence — T1.99.1–7 ✅ COMPLETE; T1.99.8–12 ✅ COMPLETE; T1.99.13–16 ✅ COMPLETE — anchor-folder path resolution; T1.99.17–26 ✅ COMPLETE — I098 / universal L17 entry-point cross-platform discovery; T1.99.27–29 ✅ COMPLETE — I099 / universal L18 schema-driven CLI parser; T1.99.30 NOT TO BE IMPLEMENTED; T1.99.31 ✅ COMPLETE — I100 config drift; T1.99.32 ✅ COMPLETE — I102; T1.99.33 ✅ COMPLETE — I103; T1.99.34 ✅ COMPLETE — I104; T1.99.35–39 ✅ COMPLETE — I105 messaging; T1.99.40–44 ✅ COMPLETE — I106 context threading; T1.99.45–49 ✅ COMPLETE — I107 bootstrap completeness; T1.99.50–63 ✅ COMPLETE — I108–I111 universal BootstrapManager / EKS wiring / simplification / errors; Phases 2–5 tracked in their own workplans)

| ID | Phase | Task | Detail | Status | Refs |
| :-- | :---

