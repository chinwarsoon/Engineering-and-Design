# Appendix P1-C: Resolved Issue Deep-Dives

> Extracted from [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md)
> Auto-generated: 2026-07-20

---

## Contents

- [31. Pipeline Output Consolidation — Single Overwrite File (I124)](#pipeline-output-consolidation---single-overwrite-file-i124)
- [32. Data Export — CSV/Excel Pipeline Output (I126 / L22) — 🔷 PLA](#data-export---csvexcel-pipeline-output-i126--l22----pla)
- [33. Preload Import Gate Audit & Hardening (I127) — ✅ COMPLETE](#preload-import-gate-audit--hardening-i127----complete)
- [39. Bootstrap Path-Resolution Rooting Defect — I130 (T1.99.101–T](#bootstrap-path-resolution-rooting-defect---i130-t199101t)
- [40. KeyError: 'revision' in register_placeholders — I131 (T1.99.](#keyerror-revision-in-registerplaceholders---i131-t199)
- [41. .dwg File Type Orphan Fix — I132 / Option B — ✅ COMPLETE](#dwg-file-type-orphan-fix---i132--option-b----complete)
- [42. Option A2 — Unified P-Prefix Error Codes + Appendix I Filena](#option-a2---unified-p-prefix-error-codes--appendix-i-filena)
- [43. File Property Extraction — Appendix J Implementation (I147–I](#file-property-extraction---appendix-j-implementation-i147i)
- [44. Document Metadata Completeness — Schema Gaps (I164–I168) — ✅](#document-metadata-completeness---schema-gaps-i164i168---)
- [45. Remaining Metadata Schema Gaps — Phase 1 Bulk Addition (I169](#remaining-metadata-schema-gaps---phase-1-bulk-addition-i169)
- [46. File Registration, Change Detection & Cross-Project Abstract](#file-registration-change-detection--cross-project-abstract)
- [50. `str(5)` Bug Fix — Restore Exception Messages Across All Err](#str5-bug-fix---restore-exception-messages-across-all-err)

---

## 31. Pipeline Output Consolidation — Single Overwrite File (I124) — ✅ COMPLETE

### 31.1 Objective

Replace the unbounded per-job JSON file accumulation in `eks/output/` with a single `pipeline_output.json` that is overwritten on every pipeline run. This addresses I124 — currently up to 10 JSON files are written per job: per-phase `checkpoint_{job_id}_{Px}.json` (`eks_engine_pipeline.py:316`), `pipeline_status_{job_id}.json` (`phase1_server.py:623`), `pipeline_messages_{job_id}.json` (`phase1_server.py:633`). All files are write-only (no code reads them back), data already lives in memory (`_job_state`, `_job_logs`) and serves via API, and checkpoint is unused by resume logic.

### 31.2 Scope Summary

| ID     | File / Location                    | Current Behavior                                                                | Target Behavior                                                                 |
|---

## 32. Data Export — CSV/Excel Pipeline Output (I126 / L22) — 🔷 PLANNED

### 32.1 Objective

Add human-readable CSV and Excel export of Phase 1 pipeline results — discovery inventory, extraction results, and review flags — so non-technical reviewers can open spreadsheets directly without querying DuckDB. Create a universal L22 `DataExporter` module in `common/library/export/` reusable by both EKS and DCC, built on already-available dependencies (`csv` stdlib + `openpyxl`).

### 32.2 Scope Summary

| Scope | Description |
| :---

### 32.8 Stale Output + Test-Production DB Pollution Fix (I189) — ✅ COMPLETE

**Discovery (2026-07-19)**: Post-I188, output CSV/Excel files contained dummy DOC-001/DOC-002 data (from test runs) despite production DB having 172 real rows. Four intertwined root causes identified. See `eks/log/issue_log.md` I189 for full analysis.

#### 32.8.1 Root Causes

| Root Cause | Description |
|:---|:---|
| **(A)** Shared `eks/output/` directory | All runs and tests write to the same directory — no per-run isolation. |
| **(B)** Test data pollutes production DB | Tests call `main()` which creates `DocumentRegistry` via singleton `output/eks_registry.db`. Test runs register synthetic docs into production DB. |
| **(C)** Export queries ALL docs | `list_documents(latest_only=True)` returns every doc ever registered, not just current-run docs. |
| **(D)** Tests with `--export both` overwrite production | `test_main_export_both_runs` writes 6 files to `eks/output/`, overwriting production exports. |

#### 32.8.2 Fix Design

| Fix | Approach | File(s) |
|:---|:---|:---|
| **F1** — Test-isolated DB | Add optional `db_path` parameter to `DocumentRegistry.__init__`. Tests pass temp paths. | `registry.py` |
| **F2** — Export scoped to current run | Capture pre-run `document_number` set; post-run filter export to new docs only (set difference). | `eks_engine_pipeline.py::main()` |
| **F3** — Per-run output directories | Write exports to `output/<run_id>/` instead of `output/` root. | `eks_engine_pipeline.py::main()` |
| **F4** — Tests avoid export pollution | `test_main_export_both_runs` uses `mock.patch` for `DocumentRegistry` with temp DB. | `test_eks_engine_pipeline.py` |

#### 32.8.3 Task Breakdown

| # | Scope | Task | Details | Status |
|:---|:---|:---|:---|:---:|
| T1.99.153 | EKS registry | Add `db_path` param to `DocumentRegistry.__init__` | Optional `db_path` parameter bypasses config for explicit path control. Enables test-isolated databases. Bumped registry.py to v0.6. | ✅ COMPLETE |
| T1.99.154 | EKS export | Scope export to current-run docs (F2) | In `main()`: capture pre-run `document_number` set via `reg_pre.list_documents()`, filter post-run `all_docs` to only new docs. | ✅ COMPLETE |
| T1.99.155 | EKS export | Per-run output subdirectories (F3) | Write exports to `output/<run_id>/` (UUID subdirectory). `run_id` already generated in `main()` via `engine_in.run_id`. | ✅ COMPLETE |
| T1.99.156 | EKS test | Isolate export test DB + output (F4) | `test_main_export_both_runs` uses `mock.patch.object(registry_module, "DocumentRegistry", _IsolatedRegistry)` with temp DB path. | ✅ COMPLETE |

#### 32.8.4 Success Criteria

- [x] `DocumentRegistry.__init__` accepts optional `db_path` parameter
- [x] Export only includes docs from current invocation (not stale/test data)
- [x] Each run writes to its own `output/<run_id>/` subdirectory
- [x] Integration test uses temp DB, does not pollute production
- [x] All 36 tests pass
- [x] I189 → Resolved
- [x] `eks/output/` clean — no stale CSV/XLSX files

---

## 33. Preload Import Gate Audit & Hardening (I127) — ✅ COMPLETE

### 33.1 Objective

Ensure every `from ... import ...` in the `main()` call chain of `eks_engine_pipeline.py` is guarded by either `_preload_infrastructure()` (pre-bootstrap) or `bootstrap_all()` (bootstrap phases) — so the pipeline never crashes with a bare `ModuleNotFoundError` after bootstrap has already succeeded. This closes a gap where 6 imports evade both gates, violating AGENTS.md §5 Rule 14.

### 33.2 Audit Findings — 6 Unguarded Imports in `main()` Call Chain

| Gap | Line | Module | Class(es) | Current Guard | Failure Mode | Severity |
|:---

## 39. Bootstrap Path-Resolution Rooting Defect — I130 (T1.99.101–T1.99.103) — ✅ COMPLETE

### 39.1 Objective

Fix a 5-step defect chain in `EKSBootstrapManager._bootstrap_paths()` where P2_paths (which runs before P3_registry) calls `resolve_paths()` with empty config `{}`, causing `resolve_paths()` to fall into the DCC branch with `eks_root=""` — anchoring all 6 sub-paths at the repository root instead of under `eks/`.

### 39.2 Root Cause (5-Step Defect Chain)

1. Bootstrap phase ordering: `P2_paths` executes before `P3_registry` (by design, universal `BootstrapManager`)
2. During P2, `self.config = {}` (config not yet loaded by P3)
3. `_bootstrap_paths()` L250-251 calls `self._path_resolver(self.project_root, self.config)` with empty config
4. `resolve_paths()` sees no `global_paths` → falls to DCC branch → `ResolvedPaths(eks_root="")`
5. `ResolvedPaths.resolve()` anchors all paths at `root / ""` = repo root

**Secondary defect**: P8 `_bootstrap_params()` only fixes `data_dir` with `eks_root` prefix (L424-433); 5 other paths (`output_dir`, `archive_dir`, `config_dir`, `log_dir`, `schema_dir`) remain anchored at repo root.

**Observed damage**: `engine/` (10 empty subdirs), `archive/` (empty), `test_output/` (56 files) created at `/Engineering-and-Design/` instead of under `eks/`.

### 39.3 Fix Strategy — Option A ✅ Selected

**Option A (selected)**: In `_bootstrap_paths()`, add `and self.config` guard to the path resolver call. When config is empty, skip the resolver and use the existing else-branch (L257-267) which correctly anchors under `self.pipeline_root_dir = "eks"`.

**Rejected alternatives**:
- **Option B**: Reorder phases (P3 before P2) — risks circular dependency (P2 resolves config_dir path needed by P3 to load config)
- **Option C**: Fix all 6 paths in `_bootstrap_params()` and `to_pipeline_context()` — band-aid that doesn't address the root cause

### 39.4 Task Breakdown

| ID | Area | Task | Detail | Status | Refs |
| :-- | :---
## 40. KeyError: 'revision' in register_placeholders — I131 (T1.99.104–T1.99.107) — ✅ COMPLETE

### 40.1 Objective

Fix `KeyError: 'revision'` thrown by `DocumentRegistry.register_document()` when `_parse_filename()` returns a metadata dict without a `revision` key for filenames that match none of the recognized revision-bearing patterns.

### 40.2 Root Cause

**5-step defect chain:**

1. `_parse_filename()` has 3 code paths: `_rev` pattern (Path 1), short-dash-suffix (Path 2), fallback (Path 3)
2. Filename `131101-WSW41-SP-SG-0101.pdf` stem = `131101-WSW41-SP-SG-0101` — no `_rev`, dash-suffix `0101` = 4 chars > 3 limit → both pattern paths fail
3. Path 3 returns `{"document_number": stem}` only — **no `revision` key**
4. `build_placeholder_metadata()` passes parsed dict through `metadata.update()` — still no `revision`
5. `register_document()` line 256: `revision = metadata["revision"]` — direct dict access → **KeyError**

**Interesting asymmetry**: `phase1_server.py` line 400 already has `metadata.setdefault("revision", "00")` — the HTTP API path handles this gracefully, but the pipeline path (`FileScanner.register_placeholders()`) does not.

### 40.3 Fix — 3-Level Layered Defense

| Level | File | Line | Change |
|:---
## 41. .dwg File Type Orphan Fix — I132 / Option B — ✅ COMPLETE

### 41.1 Objective

Resolve `.dwg` file type orphan: `.dwg` was registered in `file_type_registry` but no document type listed it in `expected_file_types`, so `.dwg` files were discovered by `scan()` but classified as `unknown` by `validate_file_types()` and never registered.

### 41.2 Root Cause

- `file_type_registry` had 5 extensions including `.dwg` (AutoCAD Drawing, `DWGParserStub`)
- `document_type_registry` had 7 entries — none with `"expected_file_types": ["dwg"]`
- The existing `DWG` code maps to `["pdf"]` only
- Two-step gate: `scan()` discovers `.dwg` (in `_ext_map`) → `validate_file_types()` discards it (no doc type expects it)

### 41.3 Fix — Option B: New "CAD" Document Type

| # | File | Change |
|---

## 42. Option A2 — Unified P-Prefix Error Codes + Appendix I Filename Parser (I133–I146, I155, I157, I163) — ✅ COMPLETE

### 42.1 Objective

1. **Option A2**: Rename all 12 D5-prefix error codes (`D5-PARSE-001..007`, `D5-PROP-001..005`) to the system-standard P-prefix format (`P5-{module}-{function}-{id}`), eliminating the only non-conforming error format in the codebase.
2. **Appendix I**: Implement the universal `FilenameParser` class — schema-driven, single shared instance across all 4 call sites, extracting 7 filename-derived fields per Appendix B §B3.

### 42.2 Why Option A2 (Not A1 or A3)

| Factor | A1 (extend schema) | A2 (P-prefix rename) | A3 (oneOf dual format) |
|---

## 43. File Property Extraction — Appendix J Implementation (I147–I162) — ✅ COMPLETE

### 43.1 Objective

Implement the schema-driven file property extractor defined in [Appendix J](appendix_j_file_property_parser.md), closing 14 open issues (I147–I154, I156, I158–I162). This module is the **first code anywhere in EKS** to call `os.stat()` / `Path.stat()` and `hashlib` — OS-level file properties are completely absent today. It also closes the **data-dropping pipeline gap**: parser `extract_metadata()` results are captured at `_process_file()` L552 but never persisted to the Document Registry.

**What changes**: Two-layer extraction (OS stat + embedded parser metadata) runs inside Phase B `_process_file()`. Results flow through `update_document_status(extra_properties=...)` → DuckDB `INSERT`/`UPDATE` with dynamically-built column lists. 13 new registry columns are added via auto-migration. All extraction rules are schema-driven via `file_property_patterns` config.

### 43.2 Scope Summary

| Dimension | Detail |
|:---

## 44. Document Metadata Completeness — Schema Gaps (I164–I168) — ✅ COMPLETE

### 44.1 Objective

Close 5 metadata gaps identified in the 2026-07-19 Document Registry Metadata Review. The Phase 1 registry (37 columns + `document_elements`) captures extraction mechanics well but lacks revision-chain, lifecycle, and cross-reference metadata — making it a flat catalog rather than a true document control system.

### 44.2 Scope Summary

| Gap | Issue | Severity | Schema Change | Registry Impact |
|:---

## 45. Remaining Metadata Schema Gaps — Phase 1 Bulk Addition (I169–I175) — ✅ COMPLETE

### 45.1 Objective

Add 7 remaining metadata columns identified as Phase 1 gaps to `document_metadata_def`. These are schema-only additions — nullable columns with sensible defaults, no population logic beyond config defaults. All 7 share the same implementation pattern (add to base schema → `SchemaToDDL._migrate_schema()` auto-adds column → bump version).

### 45.2 Scope Summary

| # | Issue | Column | Type | Default | Phase 1 Populated? |
|---

## 46. File Registration, Change Detection & Cross-Project Abstraction (I184–I187) — 🔷 PLANNED

### 46.1 Objective

Address four Phase 1 gaps in file registration, change detection, and cross-project code reuse. Issues I184–I186 close critical integrity blind spots in the document registry (no change logging, no content-aware registration, destructive `INSERT OR REPLACE` on business-key PK). Issue I187 extracts five reusable utilities to `common/library/` so dcc and code_tracer inherit canonical hash/scan/diff implementations — eliminating SSOT violations.

### 46.2 Scope Summary

| Issue | Severity | Gap | Resolution |
|:---

## 50. `str(5)` Bug Fix — Restore Exception Messages Across All Error Paths (I226)

**Discovery (2026-07-20)**: 13 call sites across 4 files use literal `str(5)` where `str(e)` was intended — a copy-paste bug where `str(5)` was used as a placeholder and never replaced. All error messages silently become the literal string `"5"`, making debugging impossible for any pipeline, CLI, or server failure.

### 50.1 Affected Files & Instances

| File | Count | Lines |
| :--- | :---: | :--- |
| `eks/engine/core/pipeline_orchestrator.py` | 5 | L360, L364, L753, L763, L765 |
| `eks/engine/core/discovery_cli.py` | 1 | L160 |
| `eks/ui/backend/phase1_server.py` | 3 | L89, L525, L666 |
| `eks/serve.py` | 4 | L404, L425, L436, L481 |

### 50.2 Fix Summary

| Category | Count | Fix Applied |
| :------- | :---: | :---------- |
| Simple `str(5)` → `str(e)` (inside `except ... as e:`) | 13 | Direct replacement — every instance verified against a valid `e` in scope |
| All 13 instances confirmed fixed | 13 | ✅ |

### 50.3 Task Breakdown

| # | Scope | Task | Details | Status |
| :--- | :--- | :--- | :--- | :---: |
| T1.99.194 | EKS workflow | Fix `pipeline_orchestrator.py` — 5 instances | Replace all `str(5)` with `str(e)` in 3 except blocks. Verified each `e` in scope. | ✅ COMPLETE |
| T1.99.195 | EKS workflow | Fix `discovery_cli.py` — 1 instance | Replace `str(5)` with `str(e)` in DiscoveryEngineError ErrorRecord. | ✅ COMPLETE |
| T1.99.196 | EKS UI | Fix `phase1_server.py` — 3 instances | L89 `_IMPORT_ERROR`, L525 `"detail"`, L666 `_job_state["error"]`. | ✅ COMPLETE |
| T1.99.197 | EKS UI | Fix `serve.py` — 4 instances | L404 ConnectionRefused check, L425 upstream err, L436 internal err, L481 Ollama err. | ✅ COMPLETE |

### 50.4 Impact by Call Path

| Path | Before (with `str(5)`) | After (with `str(e)`) |
| :--- | :--- | :--- |
| CLI `--scan` (discovery_cli.py) | `error_message: "5"` | Actual Python exception (KeyError, FileNotFound, etc.) |
| UI pipeline start (phase1_server.py:525) | `"detail": "5"` | Exact OS error (PermissionError, disk full, etc.) |
| UI job status poll (phase1_server.py:666) | `"error": "5"` | Actual pipeline exception |
| UI proxy — backend down (serve.py:404) | Check always False → falls to generic "5" | Correctly detects ConnectionRefused → 503 with "Phase backend not running" |
| UI proxy — upstream err (serve.py:425) | `"message": "5"` | Actual upstream error description |
| UI proxy — internal err (serve.py:436) | `"message": "5"` | Actual internal proxy error |
| UI proxy — Ollama (serve.py:481) | `"error": "5"` | Actual Ollama error |
| Pipeline file processing (orchestrator:360,364) | result=`"5"`, msg=`"5"` | Actual processing exception |
| Document export (orchestrator:753) | `"error": "5"` | Actual health scoring exception |
| Pipeline outer catch (orchestrator:763,765) | result=`"5"`, ErrorRecord=`"5"` | Actual pipeline exception |

### 50.5 Success Criteria

- [x] Zero `str(5)` remaining in `eks/**/*.py`
- [x] All 13 instances replaced with `str(e)` where `e` is in scope
- [x] All linter checks pass on modified files
- [x] I226 → Resolved

---

