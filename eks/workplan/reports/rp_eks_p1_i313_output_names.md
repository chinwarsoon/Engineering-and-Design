# EKS Phase 3 — I313 Phase 3 (T1.307) — Output-File-Name Schema Coverage + Runtime Literal Removal — Test Report

**Report ID**: RP-EKS-P1-I313-OUTPUT-NAMES
**Current Version**: 1.0
**Status**: ✅ COMPLETE (BLOCK-1–4 executed; extended literal guard green; full suite green except documented pre-existing baseline)
**Last Updated**: 2026-08-14
**Parent Workplan**: [i313_audit_verification_workplan.md](../i313_audit_verification_workplan.md) — Phase 3 (T1.307). Issue: **I313** — Audit & verification (materialization matrix, §24 cross-source audit, output-name schema coverage, full test suite).

## 1. Test Objective

Eliminate every live output-name / artifact-type literal from the runtime export paths so that all export file names, sheet names, view identifiers, and `export_artifact.artifact_type` values flow from schema-driven config (`eks_export_view_config.json` + `system_parameters`), per decision **D-4**. Zero runtime (non-config, non-test) occurrences of the 3 view_ids, `"artifact_type"` literal values, sheet-name literals, or `eks_export_` fallback defaults remain across `eks/engine` + `eks/ui`.

## 2. Scope

- **BLOCK-1** — `eks/engine/eks_engine_pipeline.py` export phase: replace literal-indexed columns (`export_config["discovery_inventory"]` etc.) and literal `"artifact_type"` values with a config-driven loop iterating `resolve_export_views()` keys; `artifact_type` derived from each view's `view_id`; row-builder dispatched off the config column set (`flag_reason` in columns ⇒ `_build_flagged_rows`), not a literal view_id.
- **BLOCK-2** — `eks/ui/backend/phase1_server.py` export endpoint: phase→view map derived from the export view catalog order (phase `a/b/c` ↔ first/second/third view) — no literal view_id values; `_mk_rows_fn` dispatch keyed off the config column set instead of `view_id == "review_flags"`.
- **BLOCK-3** — `eks/ui/backend/phase1_server.py` download file-name resolution: `get_system_param(..., default)` fallback literals (`"eks_export_{phase}.{ext}"`, `"eks_export.xlsx"`) removed; new module-level `_require_system_param()` raises `FAIL_FAST [S-C-S-0304]` when `export_download_file_name_template` / `export_workbook_file_name` are missing (consistent with the pipeline export path).
- **BLOCK-4** — `eks/ui/backend/phase1_server.py` artifact tracking: `insert_artifact` records the export **view_id(s)** as `artifact_type` (I306 model) — never the phase letter `a/b/c/all`.
- **Test extension** — `test_i308_default_views.py:169` no-hardcoded-literal guard extended to reject bare view_id/artifact_type literal assignments, `"eks_export_"` fallback defaults, and phase-letter artifact_type values across both files.
- **§24 test fix** — `test_i307_db_schema_set.py` `test_view_ids_consistent_across_sources` updated: pipeline view-id cross-check now asserts config-driven resolution (`resolve_export_views`/`resolve_export_columns`) and rejects literal `artifact_type` values / column indices instead of requiring literal view_ids in the pipeline source.

## 3. Test Execution Summary

| Block / item | Change | Result |
| :----------- | :----- | :----: |
| BLOCK-1 | `eks_engine_pipeline.py` export loop config-driven (view_id keys, no literals) | ✅ DONE |
| BLOCK-2 | `phase1_server.py` phase→view catalog-order derivation; `_mk_rows_fn` config-keyed | ✅ DONE |
| BLOCK-3 | `phase1_server.py` `_require_system_param()` fail-fast (S-C-S-0304), fallback literals removed | ✅ DONE |
| BLOCK-4 | `phase1_server.py` `insert_artifact` records view_id(s) as artifact_type | ✅ DONE |
| Literal guard | `test_i308_default_views.py` extended (BLOCK-1–4 patterns, both files) | ✅ 28 PASS |
| §24 test fix | `test_i307_db_schema_set.py` view-id cross-check updated | ✅ PASS |
| Focused tests | `test_i308` + `test_i309` | ✅ 28 PASS |
| Pipeline/registry/server tests | `test_eks_engine_pipeline` + `test_i298_i305` + `test_phase1` | ✅ 169 PASS |
| DB-layer tests | `test_i307_db_schema_set` + `test_i291` + `test_i310_materialization` | ✅ 48 PASS |
| Full suite | `python -m pytest eks/test/` | ✅ **788 PASS / 3 FAIL** (pre-existing I288 real-PDF fixture absences only) |
| Runtime literal grep | `eks/engine` + `eks/ui` for view_ids / `"artifact_type"` values / sheet names / `eks_export_` fallbacks | ✅ ZERO runtime literals |

## 4. Implementation Detail

### 4.1 BLOCK-1 — pipeline export loop (`eks/engine/eks_engine_pipeline.py`)

**Before** (literal-indexed columns + literal artifact_type values):

```python
export_config = resolve_export_columns(...)
discovery_cols = export_config["discovery_inventory"]
extraction_cols = export_config["extraction_results"]
review_cols = export_config["review_flags"]
...
export_views = [
    {"artifact_type": "discovery_inventory", "rows": discovery_rows, ...},
    {"artifact_type": "extraction_results", "rows": extraction_rows, ...},
    {"artifact_type": "review_flags", "rows": flagged_rows, ...},
]
```

**After** (config-driven iteration over `resolve_export_views()` keys; row-builder keyed off the config column set):

```python
view_specs = resolve_export_views(Path(safe_posix(config_dir)) / "schemas")
export_views = []
for _view_id, _vspec in view_specs.items():
    _cols = list(_vspec["columns"])
    if "flag_reason" in _cols:
        _rows = _build_flagged_rows(run_docs, _cols)
    else:
        _rows = _build_export_rows(run_docs, None, _cols)
    export_views.append({"view_id": _view_id, "rows": _rows, "columns": _cols, **_vspec})
```

`_view_columns(spec)` now reads `spec["view_id"]`. `resolve_export_columns` retained as a deliberate re-export (test_phase1.py:568 contract).

### 4.2 BLOCK-2 — server phase→view map + row-builder dispatch (`eks/ui/backend/phase1_server.py`)

**Before**:

```python
_phase_view = {"a": "discovery_inventory", "b": "extraction_results", "c": "review_flags"}
def _mk_rows_fn(view_id, status_filter):
    if view_id == "review_flags":
        return lambda: _build_flagged_rows(all_docs, _view_columns(view_id))
    return lambda: _build_export_rows(all_docs, status_filter, _view_columns(view_id))
```

**After** (catalog-order derivation; config-column-set dispatch):

```python
_phase_view = {chr(ord("a") + i): view_id for i, view_id in enumerate(view_specs)}
def _mk_rows_fn(view_id, status_filter):
    cols = _view_columns(view_id)
    if "flag_reason" in cols:
        return lambda: _build_flagged_rows(all_docs, cols)
    return lambda: _build_export_rows(all_docs, status_filter, cols)
```

Verified: catalog order is `discovery_inventory, extraction_results, review_flags` ⇒ `a→discovery_inventory, b→extraction_results, c→review_flags` (identical to the removed literal map).

### 4.3 BLOCK-3 — fail-fast download file names (`eks/ui/backend/phase1_server.py`)

New module-level helper `_require_system_param(cfg, key, purpose)` raises `FAIL_FAST [S-C-S-0304]` when a required system parameter is missing — no fallback literal. The three `get_system_param(cfg, key, "eks_export_...")` call sites now use it. Config still declares both keys (`export_download_file_name_template = "eks_export_{phase}.{ext}"`, `export_workbook_file_name = "eks_export.xlsx"`), so normal operation is unchanged; a missing key now fails loudly instead of silently defaulting (AGENTS §16).

### 4.4 BLOCK-4 — artifact_type = view_id (`eks/ui/backend/phase1_server.py`)

`insert_artifact(export_job_id, phase, ...)` replaced with one insert per exported view_id:

```python
for _view_id in (phase_defs[p]["name"] for p in phases_to_export):
    reg.insert_artifact(export_job_id, _view_id, str(file_path), row_count=0)
```

This matches the I306 model (`view_id` doubles as `export_artifact.artifact_type`) and the pipeline path — never the phase letter `a/b/c/all`.

## 5. Grep Audit (§24 runtime-literal sweep)

Scanned `eks/engine/**/*.py` + `eks/ui/**/*.py` for the forbidden patterns. Result:

- **Zero** runtime (executed) occurrences of the 3 view_ids, `"artifact_type"` literal values, sheet-name literals (`"Discovery"`/`"Extraction"`/`"Review Flags"`), or `eks_export_*` fallback defaults in the export path.
- The only remaining pattern hits are benign and pre-existing:
  - **Config-file name references** (`eks_export_view_config.json`) — required to *load* the SSOT config (schema_loader, schema_to_ddl, exporter, phase1_server) — 29 sites.
  - **Docstrings / comments** — narrative references to the config/view names.
  - **`health_scorer.py` `extraction_results`** — a function-parameter/variable name for extraction-results *data* (unrelated to the export view identifier).
- The extended guard test (`test_i308_default_views.py::test_i308_export_path_has_no_hardcoded_literals`) locks this contract; the §24 test (`test_i307_db_schema_set.py::test_view_ids_consistent_across_sources`) now asserts the config-driven pipeline contract.

## 6. Test Success Criteria & Checklist

| # | Criterion | Result |
| :- | :-------- | :----: |
| 1 | Zero runtime view_id / `"artifact_type"` / sheet-name / `eks_export_` fallback literals in `eks/engine` + `eks/ui` export paths | ✅ |
| 2 | Extended no-hardcoded-literal guard (`test_i308_default_views.py`) rejects BLOCK-1–4 patterns | ✅ |
| 3 | `test_i309_exports.py` (18 tests) stays green (workbook/CSV behavior unchanged) | ✅ |
| 4 | phase1_server tests green | ✅ |
| 5 | Full suite = documented pre-existing baseline with no new failures (788 passed / 3 failed — I288 real-PDF fixture absences) | ✅ |
| 6 | Grep audit recorded in report | ✅ |

## 7. Files Modified

| File | Change |
| :--- | :----- |
| `eks/engine/eks_engine_pipeline.py` | rev 2.3 → **2.4** — BLOCK-1 config-driven export loop; `_view_columns` uses `view_id`. |
| `eks/ui/backend/phase1_server.py` | rev 0.13 → **0.14** — BLOCK-2 phase→view catalog derivation + `_mk_rows_fn` config-keyed; BLOCK-3 `_require_system_param()` fail-fast; BLOCK-4 view_id artifact tracking. |
| `eks/test/test_i308_default_views.py` | rev 0.1 → **0.2** — extended no-hardcoded-literal guard (pipeline + server). |
| `eks/test/test_i307_db_schema_set.py` | docstring + `test_view_ids_consistent_across_sources` — config-driven §24 cross-check. |

## 8. Recommendations for Future Actions

- **Phase 4 (T1.308)**: full-suite closure — record the post-fix baseline, generate `I306-I313_impl_test_report.md`, write TLxxx/Uxxx entries, close I313 → ✅ Resolved and I306 → 📐 Aligned.
- Legacy `export_artifact.artifact_type` rows already stored as phase letters (a/b/c) in dev DBs are legacy data — no backfill unless required (per workplan "Potential future issues").
- O3 (runtime version-mismatch warning) remains deferred as optional hardening.

## 9. Lessons Learned

- Config-driven iteration over `resolve_export_views()` keys cleanly removes view_id/artifact_type literals while preserving exact row-builder behavior by dispatching on the config column set (`flag_reason` presence) — the same principle used for the server's `_mk_rows_fn`.
- The `resolve_export_columns` re-export must be preserved even when no longer called in the pipeline body (test_phase1.py:568 imports it from the pipeline module).
- Catalog-order-based phase derivation (`chr(ord("a")+i)`) is a safe config-driven substitute for the literal `a/b/c → view` map only while the view catalog order is the phase contract; a future explicit phase↔view config field would be more robust if the mapping ever needs to diverge from order.
