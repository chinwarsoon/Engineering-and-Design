# Appendix P1.3: Phase 1 — Data Export Design (CSV/Excel)

**Document ID**: WP-EKS-P1-APX-1.3
**Version**: 1.2
**Last Updated**: 2026-07-23 (I233 Aligned, §5.1 caveat updated — 6/7 pipeline issues resolved)
**Status**: 🔷 IN PROGRESS — §5.3–§5.5 root cause/fix narrative stripped to align with SSOT (issue_log.md). As of 2026-07-23, pipeline issues I227/I229–I233 resolved (6 of 7); I228 remains open. Layout restructure for design-first flow completed in v1.1.
**Parent Workplan**: [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md) (WP-EKS-P1-001, v5.3, IN PROGRESS)

---

> **Relocation Note**: This appendix is the canonical source for all Phase 1 data export (CSV/Excel) design, implementation, task breakdowns, success criteria, and post-implementation fixes. Content integrated from §32 and §47 of the main workplan, restored from source code analysis, `issue_log.md`, and `update_log.md`.

---

## Contents

- [1. Design Features Overview](#1-design-features-overview)
  - [1.1 What Data Export Delivers](#11-what-data-export-delivers)
  - [1.2 Architecture at a Glance](#12-architecture-at-a-glance)
  - [1.3 Module Inventory](#13-module-inventory)
- [2. Export Architecture & Design](#2-export-architecture--design)
  - [2.1 Universal L22 DataExporter Module](#21-universal-l22-dataexporter-module)
  - [2.2 EKS Pipeline Export Wiring](#22-eks-pipeline-export-wiring)
  - [2.3 Zero-Change Zones](#23-zero-change-zones)
- [3. Exported Files Specification](#3-exported-files-specification)
- [4. API Endpoint](#4-api-endpoint)
- [5. Implementation & Issues — Consolidated Summary](#5-implementation--issues--consolidated-summary)
  - [5.1 Open Pipeline Issues Caveat (I227–I233)](#51-open-pipeline-issues-caveat-i227i233)
  - [5.2 Detail: I126 — No CSV/Excel Export Capability](#52-detail-i126--no-csvxlsx-export-capability-t19987-94)
  - [5.3 Detail: I188 — Empty Export Files](#53-detail-i188--empty-export-files-t199147-151)
  - [5.4 Detail: I189 — Stale Output + Test-DB Pollution](#54-detail-i189--stale-output--test-db-pollution-t199153-156)
  - [5.5 Detail: I192 — UUID Folder Names Not Human-Readable](#55-detail-i192--uuid-folder-names-not-human-readable)
  - [5.6 Detail: I193 — Schema-Driven Export Columns](#56-detail-i193--schema-driven-export-columns-t199157-162)
- [6. Cross-Reference Index](#6-cross-reference-index)
- [Revision History](#revision-history)

---

## 1. Design Features Overview

### 1.1 What Data Export Delivers

Phase 1 data export adds human-readable CSV and Excel output of pipeline results — discovery inventory, extraction results, and review flags — so non-technical reviewers can open spreadsheets directly without querying DuckDB. A universal L22 `DataExporter` module in `common/library/export/` is reusable by both EKS and DCC, built on already-available dependencies (`csv` stdlib + `openpyxl`).

| Category | Capability |
|:---|:---|
| **Universal (L22)** | `common/library/export/` — `DataExporter` with `export_to_csv()`, `export_to_excel()`, `export_multi_sheet()`. Works with `list[dict]` rows (not coupled to pandas). L10 error codes (`S-DE-*`), L13 overwrite validation, L16 path resolution. |
| **EKS CLI** | `--export {csv,xlsx,both,none}` flag in `eks_engine_pipeline.py` — after pipeline completes, exports 3 artifacts to `eks/output/`. Default `none` (backward-compat). |
| **EKS Export Flow** | 3 export calls in `main()` after `run_pipeline()` returns: Phase A → `discovery_inventory.{fmt}`, Phase B → `extraction_results.{fmt}`, Phase C → `review_flags.{fmt}`. Export stays in `main()` (output formatting concern, not pipeline processing). |
| **EKS API** | `GET /api/v1/export/{phase}/{format}` endpoint in `phase1_server.py` — returns file download. |
| **Schema-Driven Columns** | `x_export` boolean flags on all 54 document properties (50 true / 4 false) + `export_artifact_def` enumerating 3 artifacts. Columns resolved at runtime via `resolve_export_columns()` — no hardcoded lists. |
| **Clean Output** | Per-run UUID subdirectories for history/audit + atomic root-level copies so `output/*.csv`/`.xlsx` always reflect latest run. Test-isolated databases prevent production pollution. |
| **DCC (future)** | L22 can replace DCC's inline `df.to_csv()`/`df.to_excel()` — noted, but DCC code not modified in this task. |

### 1.2 Architecture at a Glance

The export subsystem sits **outside the core pipeline** — it is output formatting executed after `run_pipeline()` returns:

1. **L22 DataExporter** (`common/library/export/exporter.py`, ~323 lines): 3 methods producing CSV (UTF-8 BOM via `csv.DictWriter`) and Excel (bold headers, frozen panes, auto-column-width via `openpyxl`). Works with `list[dict]`, zero pandas dependency.
2. **EKS Wiring** (`eks_engine_pipeline.py::main()`): Queries `DocumentRegistry.list_documents(latest_only=True)` post-pipeline, resolves schema-driven columns via `resolve_export_columns()`, builds 3 row-sets via `_build_export_rows()` and `_build_flagged_rows()`, writes 6 files (CSV + XLSX per artifact), copies latest to `output/` root atomically.
3. **API** (`phase1_server.py`): `GET /api/v1/export/{phase}/{format}` serves file downloads with `Content-Disposition`.

**Key metrics**: 1 universal module | 4 error codes (S-DE-001–004) | 3 export artifacts | 46–50 columns (schema-driven) | 6 output files | 20 universal tests + 280 EKS export tests | 5 resolved issues (I126/I188/I189/I192/I193).

### 1.3 Module Inventory

| Module | File | Lines | Description |
|:---|:---|:---|:---|
| **DataExporter class** | `common/library/export/exporter.py` | 1–323 | Core export class: `export_to_csv()`, `export_to_excel()`, `export_multi_sheet()`. 4 L10 error codes. |
| **L22 package init** | `common/library/export/__init__.py` | 1–24 | Package init exporting `DataExporter` + convenience functions. L22 universal module. |
| **L22 tests** | `common/library/export/tests/test_exporter.py` | 1–328 | 4 test classes, 20 tests (CSV round-trip, BOM, CJK unicode, Excel round-trip, multi-sheet, empty rows, error paths, overwrite guard, edge cases) |
| **EKS export wiring** | `eks/engine/eks_engine_pipeline.py` | 965–1070 | Full export flow in `main()`: guard → dirs → DB query → column resolution → row building → CSV/XLSX write → root-level copy |
| **resolve_export_columns()** | `eks/engine/eks_engine_pipeline.py` | 1098–1202 | Schema-driven column resolution with 11-field fallback |
| **`_build_export_rows()`** | `eks/engine/eks_engine_pipeline.py` | 1205–1234 | Pass-through dict + column subsetting |
| **`_build_flagged_rows()`** | `eks/engine/eks_engine_pipeline.py` | 1237–1280 | Flagged row builder with `flag_reason` computed column |
| **CLI flag** | `eks/engine/eks_engine_pipeline.py` | 450–454, 496–499 | `--export` registered in both `build_parser()` (bespoke) and `_EKS_CORE_ARG_SPECS` (schema-driven) |
| **Preload guard** | `eks/engine/eks_engine_pipeline.py` | 751–758 | `_preload_infrastructure()` — DataExporter preloaded |
| **API endpoint** | `eks/ui/backend/phase1_server.py` | — | `GET /api/v1/export/{phase}/{format}` |
| **Registry db_path param** | `eks/engine/core/registry.py` | — | `DocumentRegistry.__init__(db_path=...)` (I189/F1, v0.6) |
| **EKS export tests** | `eks/test/test_eks_engine_pipeline.py` | 386–585 | `TestI107BootstrapCompleteness` — 7 test methods + integration test |

---

## 2. Export Architecture & Design

### 2.1 Universal L22 DataExporter Module

> Source: §32.6 + code analysis of `common/library/export/`.

**DataExporter API:**

| Method | Signature | Description |
|:---|:---|:---|
| `export_to_csv()` | `(rows: list[dict], path: Path, columns: list[str] = None) -> Path` | Writes CSV with UTF-8 BOM (`utf-8-sig`), uses `csv.DictWriter`. Raises `DataExportError` with codes S-DE-001/003/004. |
| `export_to_excel()` | `(rows: list[dict], path: Path, sheet_name: str = "Sheet1", columns: list[str] = None) -> Path` | Writes single-sheet `.xlsx` with bold headers, frozen panes, auto-column-width (max 50). Uses `openpyxl`. Raises S-DE-002/003/004. |
| `export_multi_sheet()` | `(sheets: dict[str, list[dict]], path: Path) -> Path` | Writes multi-sheet `.xlsx` workbook; same formatting as single-sheet. |

**Error Codes (S-DE-\* range):**

| Code | Description |
|:---|:---|
| S-DE-001 | CSV write failed (I/O error) |
| S-DE-002 | Excel write failed (I/O or format error) |
| S-DE-003 | Output directory not writable |
| S-DE-004 | File exists and overwrite disabled |

**Key Design Properties:**

- **No pandas dependency**: Works with `list[dict]` rows directly. If a pandas DataFrame is passed, call `df.to_dict('records')` first.
- **Lightweight**: Only `csv` stdlib + `openpyxl`.
- **Registered**: Exported from `common/library/__init__.py` as L22 universal component.

### 2.2 EKS Pipeline Export Wiring

> Source: §32.2 + code analysis of `eks/engine/eks_engine_pipeline.py`.

**CLI Flag:** `--export {csv,xlsx,both,none}` (default: `none`, backward-compatible). Registered in both `build_parser()` (bespoke) and `_EKS_CORE_ARG_SPECS` (schema-driven parser).

**Export Flow in `main()`:**

1. Extract `export_fmt = parsed.export_format if parsed else "none"` (line 909)
2. Guard: if `export_fmt == "none"`, skip export entirely
3. Create per-run UUID subdirectory: `output/<run_id>/` (line 985–986)
4. Query `DocumentRegistry.list_documents(latest_only=True)` (line 990)
5. Resolve schema-driven columns via `resolve_export_columns()` (line 1003)
6. Build 3 row-sets via `_build_export_rows()` and `_build_flagged_rows()` (lines 1014–1020)
7. Write CSV files if `csv`/`both`: `discovery_inventory.csv`, `extraction_results.csv`, `review_flags.csv`
8. Write XLSX files if `xlsx`/`both`: `discovery_inventory.xlsx`, `extraction_results.xlsx`, `review_flags.xlsx`
9. Copy latest exports atomically to `output/` root (lines 1047–1067, I192)
10. All wrapped in try/except — logs warning on failure, pipeline continues

**Preload Infrastructure:** `DataExporter` is preloaded in `_preload_infrastructure()` and passed through to `main()` via the preload dict (key `_DataExporter`), avoiding bare imports inside `main()`. This satisfies I127 preload import gate requirements.

**Design Rationale — Export Stays in `main()`:** The orchestrator coordinates *processing* (scan → parse → score → review); export is *output formatting*, a concern of the entry point. Keeping export in `main()` means:

- **(a)** `PipelineOrchestrator.run_full_pipeline()` can be unit-tested for core logic without `openpyxl`
- **(b)** The orchestrator signature stays clean (no `export_config: dict = None` parameter)
- **(c)** `run_pipeline()` remains a pure `context → context` function
- **(d)** `main()` queries DB post-pipeline via the returned `context.registry`, which is read-only and cheap

### 2.3 Zero-Change Zones

| Location | Why Unchanged |
|:---|:---|
| `_preload_infrastructure()` | L22 `DataExporter` is a post-pipeline module, not bootstrap infrastructure. Bootstrap guards only `common.library.paths`, `common.library.logging`, `common.library.core.pipeline`, and `eks.engine.core.bootstrap`. |
| `bootstrap.py` / `EKSBootstrapManager` | No new bootstrap phase needed. `openpyxl` is already declared in `eks_config.json` `dependencies.required` and is checked at P6 via `test_environment()`. If missing, P1-BOOT-ENV fires with `conda activate eks` hint. |
| `run_pipeline()` | Export is called *after* `run_pipeline()` returns — `run_pipeline()` stays a pure `PipelineContext → PipelineContext` transform. |
| `PipelineOrchestrator.run_full_pipeline()` | No `export_config` parameter. No export calls inside phase callbacks. Orchestrator stays pure. |
| `eks_config.json` dependencies | `openpyxl` already in `required` list (L10). `csv` is stdlib. Zero new dependencies. |

---

## 3. Exported Files Specification

> Source: §32.3, restored from code analysis.

| File | Phase | Data Source | Columns |
|:---|:---|:---|:---|
| `discovery_inventory.{csv,xlsx}` | After Phase A | All discovered documents (`status_filter=None` per I188 fix) | ~46 columns: all `x_export: true` fields excluding extraction-specific columns (`page_count`, `extract_status`, `extraction_confidence`, `extraction_notes`). Core identity: `document_number`, `revision`, `document_type`, `file_type`, `file_path`, `ingested_at` + file properties + embedded metadata + project context. |
| `extraction_results.{csv,xlsx}` | After Phase B | All documents with extraction data | ~50 columns: all `x_export: true` fields (full document metadata). Includes `page_count`, `extract_status`, `extraction_confidence`, `extraction_notes`, `total_elements`, `cover_pages`, `sections`, `tables`, `images`, `links`. |
| `review_flags.{csv,xlsx}` | After Phase C | Flagged docs: `extract_status != 'success'` OR `confidence < 0.70` OR `confidence IS NULL` | ~8 columns (focused triage view): `document_number`, `revision`, `document_type`, `extract_status`, `extraction_confidence`, `extraction_notes`, `flag_reason`, `ingested_at` |

**Column counts reflect I193 schema-driven export.** Original hardcoded design exported only 11 fields. After I193, `discovery_inventory` exports ~46 fields and `extraction_results` exports ~50 fields.

---

## 4. API Endpoint

> Source: T1.99.94.

| Aspect | Detail |
|:---|:---|
| **Route** | `GET /api/v1/export/{phase}/{format}` |
| **Phases** | `a` (discovery), `b` (extraction), `c` (review), `all` (all 3) |
| **Formats** | `csv`, `xlsx` |
| **Response** | File download with `Content-Disposition` header |
| **File** | `phase1_server.py` (rev 0.11) |

---

## 5. Implementation & Issues — Consolidated Summary

All implementation work was driven by 5 issues. The master table below maps each issue to its tasks and criteria. Expand each detail section for the full task breakdown and success criteria. Issue detail (root cause, fix, outcome) is tracked in the issue log only.

| # | Issue | Tasks | Criteria |
|:---:|:---|:---:|:---:|
| 1 | **I126** — No CSV/Excel export capability | 8 | 12/12 |
| 2 | **I188** — Empty export files (discovery + review always 0 rows) | 5 | 7/7 |
| 3 | **I189** — Stale output + test-DB pollution | 4 | 7/7 |
| 4 | **I192** — UUID folder names not human-readable | — | 1/1 |
| 5 | **I193** — Hardcoded 11-field export; 43 DB columns ignored | 6 | 9/9 |

### 5.1 Pipeline Issues Impacting Export (I227–I233)

6 of 7 pipeline issues now resolved/aligned (I228 remains open). Issue details tracked in [`p1_issue_log.md`](../log/phase1/p1_issue_log.md):

| Issue | Title | Impact on Data Export | Status |
|:---|:---|:---|:---:|
| I227 | 2× I/O scan (no doc-level caching) | Export queries may reflect stale registry state if `scan()` is re-run post-export | ✅ |
| I228 | No post-parse schema/dependency/health validation gate | Documents with `extract_status = "success"` may still have incomplete metadata → exported as-is | 🔴 |
| I229 | File-by-file logging without aggregation | No per-run export summary statistics (row counts, column coverage, flag distribution) | ✅ |
| I230 | No phase-level validation gate (checkpoint quality) | Documents entering Phase B/C without validated Phase A output affect extraction/review exports | ✅ |
| I231 | Version SSOT | Single `__version__` in `eks/__init__.py`. All subpackages import from `eks` | ✅ |
| I232 | Parser module cross-dependencies not formally documented | Parser failures cascading into `extraction_confidence = None` → flagged in review_flags export | ✅ |
| I233 | Monolithic pipeline module | Split into `pipeline_engine/`, zero module-level globals. No impact on export logic | ✅ |

### 5.2 Detail: I126 — No CSV/Excel Export Capability (T1.99.87–94)

<details>
<summary><b>Task Breakdown (8 tasks, 12/12 criteria met)</b></summary>

| # | Scope | Task | Details | Status |
|:---|:---|:---|:---|:---:|
| T1.99.87 | Universal | Create `common/library/export/__init__.py` | Package init exporting `DataExporter` + convenience functions. L22 universal module. | ✅ |
| T1.99.88 | Universal | Create `DataExporter` class | `export_to_csv()` (csv.DictWriter + BOM), `export_to_excel()` (openpyxl, auto-column-width, bold+frozen headers), `export_multi_sheet()` (multi-sheet workbook). Error codes S-DE-001–S-DE-004. | ✅ |
| T1.99.89 | Universal | Register in `common/library/__init__.py` | L22 entry added to universal library exports. | ✅ |
| T1.99.90 | Universal | Add DataExporter tests | 20 tests across 4 classes: CSV round-trip, BOM, CJK/Unicode, Excel round-trip, multi-sheet, empty rows, error paths, overwrite guard, edge cases. | ✅ |
| T1.99.91 | Universal | Update architecture doc | `common/universal_pipeline_architecture_design.md` updated with L22 section. | ✅ |
| T1.99.92 | EKS CLI | Add `--export` flag | Flag added to both `_EKS_CORE_ARG_SPECS` (schema-driven) and `build_parser()` (bespoke). Choices: `csv`, `xlsx`, `both`, `none`. Default: `none`. | ✅ |
| T1.99.93 | EKS Pipeline | Wire export calls in `main()` | 3 export calls after `run_pipeline()` returns: `discovery_inventory`, `extraction_results`, `review_flags` via `DataExporter` + `_build_export_rows`/`_build_flagged_rows`. | ✅ |
| T1.99.94 | EKS API | Add export endpoint | `GET /api/v1/export/{phase}/{format}` — phases: `a`/`b`/`c`/`all`, formats: `csv`/`xlsx`. Returns file download with Content-Disposition. | ✅ |

**Success Criteria:**
- [x] `common/library/export/` exists with `DataExporter` (L22 universal module)
- [x] `export_to_csv()` produces valid CSV with BOM (UTF-8 Excel-compatible)
- [x] `export_to_excel()` produces valid .xlsx with auto-column-width + bold headers
- [x] `export_multi_sheet()` produces multi-sheet workbook with correct sheet names
- [x] All universal tests green (csv + excel + multi-sheet + edge cases)
- [x] `common/universal_pipeline_architecture_design.md` updated with L22
- [x] `--export csv` produces `discovery_inventory.csv`, `extraction_results.csv`, `review_flags.csv`
- [x] `--export xlsx` produces 3 .xlsx files
- [x] `GET /api/v1/export/{phase}/{format}` returns correct file download
- [x] Default `--export none` — zero files written (backward-compat)
- [x] Full EKS test suite green
- [x] I126 → Resolved in `issue_log.md`; U183 in `update_log.md`

**Design Decisions:**
- **Reuse from DCC:** DCC's `_run_export()` uses pandas `.to_csv(index=False)` / `.to_excel(index=False)` inline. L22 extracts the core write logic into a reusable module but does **not** modify DCC code. Future DCC migration: replace `df_processed.to_csv(path, index=False)` → `DataExporter().export_to_csv(rows, path)`.
- **Path Resolution:** Output files go to `resolve_paths() → output_dir` (L16). Discovery inventory / extraction results / review flags are always overwritten on each run.

</details>

### 5.3 Detail: I188 — Empty Export Files (T1.99.147–151)

<details>
<summary><b>Task Breakdown (5 tasks, 7/7 criteria met)</b></summary>

| # | Scope | Task | Details | Status |
|:---|:---|:---|:---|:---:|
| T1.99.147 | EKS Export | Fix discovery filter | Remove `["pending"]` status filter → `None` (all docs). | ✅ |
| T1.99.148 | EKS Export | Fix review flag logic | Change `elif status != "success"` → unconditional `else:` for None-confidence catch-all. | ✅ |
| T1.99.149 | EKS Test | Add `_build_export_rows` tests | Direct unit tests for row construction. | ✅ |
| T1.99.150 | EKS Test | Add `_build_flagged_rows` tests | Direct unit tests for flag logic + None-confidence edge case. | ✅ |
| T1.99.151 | EKS Test | Add integration export test | `main()` with `--export both` → verify 3 files exist. | ✅ |

**Success Criteria:**
- [x] `--export both` produces `discovery_inventory.csv` + `extraction_results.csv` + `review_flags.csv`
- [x] `--export xlsx` produces all 3 .xlsx files
- [x] `discovery_inventory` shows all documents (not 0)
- [x] `review_flags` includes docs with missing `extraction_confidence` even if `extract_status="success"`
- [x] All new export tests pass (7/7)
- [x] I188 → Resolved
- [x] Full EKS test suite remains green (36 tests)

</details>

### 5.4 Detail: I189 — Stale Output + Test-DB Pollution (T1.99.153–156)

<details>
<summary><b>Task Breakdown (4 tasks, 7/7 criteria met)</b></summary>

| # | Scope | Task | Details | Status |
|:---|:---|:---|:---|:---:|
| T1.99.153 | EKS registry | Add `db_path` param to `DocumentRegistry.__init__` | Optional `db_path` parameter bypasses config for explicit path control. Enables test-isolated databases. Bumped registry.py to v0.6. | ✅ |
| T1.99.154 | EKS export | Scope export to current-run docs (F2) | In `main()`: capture pre-run `document_number` set via `reg_pre.list_documents()`, filter post-run `all_docs` to only new docs. | ✅ |
| T1.99.155 | EKS export | Per-run output subdirectories (F3) | Write exports to `output/<run_id>/` (UUID subdirectory). `run_id` already generated in `main()` via `engine_in.run_id`. | ✅ |
| T1.99.156 | EKS test | Isolate export test DB + output (F4) | `test_main_export_both_runs` uses `mock.patch.object(registry_module, "DocumentRegistry", _IsolatedRegistry)` with temp DB path. | ✅ |

**Success Criteria:**
- [x] `DocumentRegistry.__init__` accepts optional `db_path` parameter
- [x] Export only includes docs from current invocation (not stale/test data)
- [x] Each run writes to its own `output/<run_id>/` subdirectory
- [x] Integration test uses temp DB, does not pollute production
- [x] All 36 tests pass
- [x] I189 → Resolved
- [x] `eks/output/` clean — no stale CSV/XLSX files

</details>

### 5.5 Detail: I192 — UUID Folder Names Not Human-Readable

<details>
<summary><b>Success Criteria (1/1 criteria met)</b></summary>

**Success Criteria:**
- [x] Root-level `output/*.csv`/`.xlsx` always reflect latest run
- [x] I192 → Resolved

</details>

### 5.6 Detail: I193 — Schema-Driven Export Columns (T1.99.157–162)

<details>
<summary><b>Objective, Scope, Before/After, Schema Changes, Pipeline Changes, Task Breakdown (6 tasks, 9/9 criteria met), Risks</b></summary>

**Objective:** Replace the hardcoded 11-field export row builder in `_build_export_rows()` with schema-driven column resolution. The `eks_doc_base_schema.json` `document_metadata_def` already defines 54 fields — but only 11 were exported because `_build_export_rows()` manually constructed a dict with exactly those 11 keys. Add an `x_export` boolean flag to every field in the schema and an `export_artifact_def` enumerating the 3 export artifacts with their column subsets. The pipeline reads columns from schema at runtime instead of hardcoded lists.

**Scope Summary:**

| Scope | Description |
|:---|:---|
| **Schema** | `eks_doc_base_schema.json` — add `x_export` (boolean) to every property in `document_metadata_def` and `project_metadata_def`; add new `export_artifact_def` enumerating 3 artifacts via `$ref` |
| **Pipeline** | `eks_engine_pipeline.py` — replace hardcoded `discovery_cols`/`extraction_cols`/`review_cols` lists with schema-driven resolution; update `_build_export_rows()` and `_build_flagged_rows()` to accept full doc dicts |
| **Registry** | `registry.py` — (no change needed; `list_documents()` already returns `SELECT *`) |
| **Test** | `test_phase1.py` — add schema-validation tests for `x_export` flag and `export_artifact_def`; update export tests to verify all expected columns present |

**Current vs Target State:**

| Aspect | Current (broken) | Target (schema-driven) |
|:---|:---|:---|
| **Columns in DB** | 54 (SELECT *) | 54 (unchanged) |
| **Columns exported** | 11 (hardcoded in `_build_export_rows()`) | ~50 (all fields where `x_export: true`, excluding internal-only fields `id`, `is_latest`, `supersedes`, `superseded_by`) |
| **Field-level control** | None — add/remove requires code change | `x_export: true/false` per field in schema |
| **Artifact definitions** | Hardcoded Python lists | `export_artifact_def` in schema with `$ref` to field definitions |
| **New field addition** | Must remember to edit 3 places (schema + `_build_export_rows` + column lists) | Add field to schema with `x_export: true` — pipeline picks it up automatically |

**Schema Changes — `x_export` Flag per Field:**

`x_export: true` fields (50 total): core identity (`source_type`, `document_type`, `document_number`, `revision`, `status`, `file_path`, `file_type`, `ingested_at`), people/org (`created_by`, `checked_by`, `approved_by`, `originator_company`, `security_class`, `verified_by`), asset linking (`asset_tags`), extraction results (`page_count`, `extract_status`, `extraction_confidence`, `extraction_notes`), file properties (`file_size`, `file_created_at`, `file_modified_at`, `file_hash`), embedded metadata (`embedded_title`, `embedded_subject`, `embedded_created_date`, `embedded_modified_date`, `embedded_creator_app`, `embedded_producer`, `embedded_last_modified_by`, `embedded_keywords`, `embedded_sheet_count`), metadata completeness (`document_title`, `lifecycle_stage`, `revision_date`, `revision_description`, `embedded_revision_number`), completeness fields (`references_documents`, `project_phase`, `contract_package`, `issued_date`, `responsible_engineer`, `total_sheets`, `language`, `vendor_name`), project context (`project_title`, `project_number`, `area`, `discipline`, `department`).

`x_export: false` fields (4 internal): `id`, `is_latest`, `supersedes`, `superseded_by`. Export count: 54 − 4 = **50 fields** (up from 11).

**Schema Changes — `export_artifact_def`:**

```json
"export_artifact_def": {
    "type": "object",
    "description": "Defines the column subset for each export artifact.",
    "properties": {
        "discovery_inventory": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Columns for Phase A discovery inventory. All x_export fields except extraction-specific ones."
        },
        "extraction_results": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Columns for Phase B extraction results. All x_export fields."
        },
        "review_flags": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Columns for Phase C review flags. Subset focusing on extraction quality + flag_reason."
        }
    },
    "required": ["discovery_inventory", "extraction_results", "review_flags"],
    "additionalProperties": false
}
```

**Pipeline Changes:**

- **`_build_export_rows()`** — removed the 11-field hardcoded `row` dict. Passes through full doc dict and subsets to `columns`.
- **`_build_flagged_rows()`** — same pass-through pattern + `flag_reason` computed column.
- **`main()` export block** — replaced hardcoded lists with schema resolution: `export_config = resolve_export_columns(eks_doc_schema)`.
- **`resolve_export_columns()`** — new helper reading `x_export` flags and artifact definitions from schema at runtime. Falls back to hardcoded 11-column defaults on failure (with `_fallback: True`).

| # | Scope | Task | Details | Status |
|:---|:---|:---|:---|:---:|
| T1.99.157 | Schema | Add `x_export` flags | Boolean annotation on all 54 properties in `document_metadata_def` + `project_metadata_def`. 50 true, 4 false. | ✅ |
| T1.99.158 | Schema | Add `export_artifact_def` | New definition with 3 artifacts (`discovery_inventory`, `extraction_results`, `review_flags`). `required` + `additionalProperties: false`. | ✅ |
| T1.99.159 | Pipeline | Implement `resolve_export_columns()` | Schema-driven column resolver. Reads `x_export` flags. Falls back to hardcoded 11 on failure. | ✅ |
| T1.99.160 | Pipeline | Refactor `_build_export_rows()` | Remove 11-field hardcoded dict → pass-through + column subsetting via `columns` param. | ✅ |
| T1.99.161 | Pipeline | Refactor `_build_flagged_rows()` | Same pass-through pattern + `flag_reason` computed column. | ✅ |
| T1.99.162 | Test | Update export tests | Schema validation for `x_export` + `export_artifact_def`. Verify 50 columns in output. 300 tests pass (was 71). | ✅ |

**Success Criteria:**
- [x] **SC-1**: Every property in `document_metadata_def` has `x_export: true` or `x_export: false` — 50 true, 4 false
- [x] **SC-2**: `export_artifact_def` exists with 3 artifacts; column names derived from `x_export` flags at runtime
- [x] **SC-3**: `resolve_export_columns()` returns correct per-artifact column lists; `discovery_inventory` (46) ⊆ `extraction_results` (50)
- [x] **SC-4**: `_build_export_rows()` no longer contains hardcoded field list — pass-through dict + column subsetting
- [x] **SC-5**: CSV/Excel exports contain 46–50 columns (all `x_export: true` fields)
- [x] **SC-6**: Previously-missing fields appear: `project_title`, `embedded_title`, `file_size`, `file_hash`, `lifecycle_stage`, `created_by`, `vendor_name`, `originator_company`, `file_modified_at`, `security_class` — all 10 verified
- [x] **SC-7**: `review_flags` artifact includes `flag_reason` computed column
- [x] **SC-8**: All 300 tests pass (was 71, now 300)
- [x] **SC-9**: I193 → Resolved

**Risks:**

| Risk | Likelihood | Mitigation |
|:---|:---|:---|
| Schema change (`x_export`) breaks existing validation | Low | `x_` prefix is a JSON Schema custom annotation — validators ignore unknown keywords per spec §6.4. No schema validation impact. |
| ~50 columns make CSV/Excel too wide for casual review | Medium | Users explicitly asked for all columns. Excel auto-column-width handles this. CSV width is a viewer concern, not an export concern. |
| `resolve_export_columns()` schema load failure | Low | try/except with fallback to hardcoded 11-column lists + warning log — backward-compatible degradation. |
| `review_flags` artifact grows too wide with 50 columns | Medium | Review flags kept as focused subset (8 columns) — a triage view, not a complete data dump. Only `discovery_inventory` and `extraction_results` get the full treatment. |

</details>

---

## 6. Cross-Reference Index

### 6.1 P1-Specific Appendices

| Appendix | Title | Relevance |
|:---|:---|:---|
| [P1.1](appendix_p1.1_phase1_architecture.md) | Phase 1 — Architecture & Design Blueprints | Overall architecture; export subsystem is a Phase 1 output-formatting layer |
| [P1.2](appendix_p1.2_phase1_scope.md) | Phase 1 — Scope & Module Inventory | Scope caveat (§2) for I227–I233 impacting export quality |
| P1-D | Phase 1 — Checklists (superseded by [p1_sc_log.md](../log/phase1/p1_sc_log.md)) | Export-related verification items |

### 6.2 General Appendices

| Appendix | Title | Relevance |
|:---|:---|:---|
| B | Registry Design | `DocumentRegistry.list_documents()` — data source for all export queries |
| D | Error Codes | S-DE-001–S-DE-004 (export error codes) + pipeline error codes surfaced in export |
| F | Pipeline Patterns | Export as post-pipeline output formatting pattern; orchestrator purity constraint |

### 6.3 Key Workplan Sections

| Section | Title | Relevance |
|:---|:---|:---|
| [§32](phase_1_foundation_workplan.md) | Original Export Specification | I126 initial implementation: L22 DataExporter, `--export` flag, task breakdown T1.99.87–94 |
| [§47](phase_1_foundation_workplan.md) | Schema-Driven Export Enhancement | I193: `x_export` flags, `export_artifact_def`, `resolve_export_columns()`, task breakdown T1.99.157–162 |

### 6.4 Issue Log

| Issue | Location | Description |
|:---|:---|:---|
| I126 | `../log/phase1/p1_issue_log.md` | No CSV/Excel export capability |
| I188 | `../log/phase1/p1_issue_log.md` | Empty export files |
| I189 | `../log/phase1/p1_issue_log.md` | Stale output + test-DB pollution |
| I192 | `../log/phase1/p1_issue_log.md` | UUID folder names not human-readable |
| I193 | `../log/phase1/p1_issue_log.md` | Hardcoded 11-field export |
| I227–I233 | `../log/phase1/p1_issue_log.md` | Pipeline audit issues — 6 resolved/aligned, 1 open (see §5.1) |

### 6.5 Update Log

| Update | Date | Issues | Summary |
|:---|:---|:---|:---|
| U183 | 2026-07-18 | I126 | I126 RESOLVED: L22 DataExporter + EKS wiring (T1.99.87–94) |
| U190 | 2026-07-19 | I188 | I188 RESOLVED: Empty export files fixed (T1.99.147–151) |
| U191 | 2026-07-19 | I189 | I189 RESOLVED: Test-DB pollution + stale output fixed (T1.99.153–156) |
| U192 | 2026-07-19 | I164–I175, I192, I193 | 15 metadata columns + I192 root-level copies + I193 schema-driven export |
| U193 | 2026-07-19 | I194 | 11-gap closure sweep (I192/I193 referenced in gap analysis) |

---

## Revision History

| Version | Date | Author | Changes |
|:---|:---|:---|:---|
| **1.3** | 2026-07-23 | opencode | Updated §5.1 caveat: 6/7 pipeline issues resolved (I227/I229–I233 ✅; I228 🔴 remains open). I233 status changed from `install_eks_deps()` description to module split. Added Status column to caveat table. Updated status line and §6.3 cross-reference. |
| **1.2** | 2026-07-22 | AI Agent (SSOT alignment) | §5.3–§5.5 root cause/fix narrative removed (I188 Discovery + Root Causes & Fixes, I189 Discovery + Root Causes + Fix Design, I192 Problem/Fix/Result). Only task tables + SC checklists retained per SSOT rule (issue detail lives only in `issue_log.md`). §5 intro updated. |
| **1.1** | 2026-07-21 | AI Agent (layout restructure) | Major restructure for design-first flow: fixed Document ID (`A1.3` → `APX-1.3`), changed status to 🔷 IN PROGRESS, added §1 Design Features Overview (1.1–1.3), merged current §2+§3 → §2 Export Architecture & Design, consolidated §5–§11+§14 into single §5 master table with collapsible `<details>` blocks per issue, added §5.1 I227–I233 scope caveat, added §6 Cross-Reference Index, added Revision History. 14 sections → 6 sections. No content loss. |
| **1.0** | 2026-07-20 | AI Agent (initial) | Initial creation: integrated §32 and §47 content from main workplan, restored export design from source code analysis, `issue_log.md`, and `update_log.md`. Documented L22 DataExporter, EKS wiring, 4 post-implementation fixes (I188/I189/I192/I193), API endpoint, and source code reference. |

---

*End of Appendix P1.3*
