# EKS Phase 1 — Entry-Point & Cross-Platform Discovery (I098 / T1.99.17–26) — Test Report

**Report ID**: RP-EKS-P1-ENTRY-001  
**Current Version**: 1.0  
**Status**: ✅ Complete — I098 closed; T1.99.17–26 implemented and tested  
**Last Updated**: 2026-07-15  
**Parent Workplan**: [phase_1_foundation_workplan.md](../phase_1_foundation_workplan.md)

---

## 1. Title and Description

Test report for the EKS Phase 1 entry-point cross-platform discovery remediation (issue **I098**, tasks **T1.99.17–26**), which aligns the EKS pipeline entry point `eks/engine/eks_engine_pipeline.py` with the universal design pattern **L17** (Pipeline Entry-Point & Cross-Platform Discovery, `common/universal_pipeline_architecture_design.md` §3.19) and with DCC's faithful anchor-folder discovery.

Validates that: the entry detects the OS up front (`detect_os`, L12); resolves the project root from `cwd`/`--base-path` with a `==pipeline_dir` strip; verifies the `eks` anchor and raises (not silent `cwd`) when missing; routes **all** sub-paths through the schema-driven `resolve_paths()` (L16) honouring `eks_root` (fixing the default `data_dir` bug); gates folder auto-create by OS (`should_auto_create_folders`); and serializes emitted paths via `safe_posix()`.

---

## 2. Revision Control & Version History

| Version | Date | Author | Summary of Changes |
| :------ | :--- | :----- | :----------------- |
| 1.0 | 2026-07-15 | opencode | Initial report for I098 / T1.99.17–26 closure. Covers the new `common/library/paths/root_discovery.py`, the `should_auto_create_folders` addition to L12, and the EKS entry wiring. 8 new entry-point tests; full EKS suite 275/275 green. |

---

## 3. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Revision Control & Version History](#2-revision-control--version-history)
- [3. Index of Content](#3-index-of-content)
- [4. Test Objective](#4-test-objective)
- [5. Scope and Execution Summary](#5-scope-and-execution-summary)
- [6. Test Methodology, Environment, and Tools](#6-test-methodology-environment-and-tools)
- [7. Test Phases, Steps, Cases, and Results](#7-test-phases-steps-cases-and-results)
- [8. Test Success Criteria and Checklist](#8-test-success-criteria-and-checklist)
- [9. Files Archived, Modified, and Version Controlled](#9-files-archived-modified-and-version-controlled)
- [10. Recommendations for Future Actions](#10-recommendations-for-future-actions)
- [11. Lessons Learned](#11-lessons-learned)
- [12. References](#12-references)

---

## 4. Test Objective

Verify that the EKS entry point implements the universal L17 ordered entry sequence and closes all five I098 residual issues versus DCC's anchor pattern, without regression to the rest of the Phase 1 suite.

**Key areas (1:1 with L17):**

- **T1.99.17** — `detect_os()` (L12) invoked at the EKS entry before any path work.
- **T1.99.18** — `default_base_path("eks")` walks the entry module's parents for the `eks` anchor and returns the project root (parent of anchor); no hardcoded `parent.parent.parent`.
- **T1.99.19** — `resolve_pipeline_base_path()` returns `--base-path` (expanded/resolved) else `cwd`; no silent `__file__` walk.
- **T1.99.20** — `discover_project_root()` + `--base-path` CLI + `==pipeline_dir` strip (DCC `dcc_engine_pipeline.py:483-484`).
- **T1.99.21** — All sub-paths (incl. default `data_dir`) routed via `resolve_paths()` honouring `eks_root`; fixes the `project_root/data` vs `project_root/eks/data` bug (I098 #1).
- **T1.99.22** — `should_auto_create_folders(os_info)` gates `validate_all(auto_create=...)`; emitted paths use `safe_posix()`.
- **T1.99.23** — `default_base_path` raises `FileNotFoundError` when the anchor is missing (no silent `cwd` fallback, I098 #3).
- **T1.99.24** — Entry-point resolution tests (cwd, `--base-path`, strip, default `data_dir`, `detect_os`, raise).
- **T1.99.25** — EKS runtime consumes `common.library` (`detect_os`/`safe_posix`/`should_auto_create_folders`/`root_discovery`); advances I078.
- **T1.99.26** — Workplan / logs / issue updated; I098 → Resolved.

---

## 5. Scope and Execution Summary

| Metric | Value |
| :----- | :---- |
| Issue closed | I098 (🔴 High → ✅ Resolved) |
| Tasks delivered | T1.99.17–26 (10 tasks, all ✅ COMPLETE) |
| New shared module | `common/library/paths/root_discovery.py` (L17) |
| L12 change | `should_auto_create_folders` added to `common/library/core/paths/path_utils.py` |
| EKS module modified | `eks/engine/eks_engine_pipeline.py` (→ v0.3) |
| Test files exercised | `eks/test/test_eks_engine_pipeline.py` (+8 new entry-point tests) |
| EKS tests run | 275 |
| EKS tests passed | 275 |
| EKS tests failed | 0 |
| Duration (full suite) | ~20s |
| Environment | `eks` conda env, Python 3.13, Windows 11 |

### Test Distribution (entry-point focus)

| Area | Tests | Status |
| :--- | :---: | :----: |
| `TestEntryPointDiscovery` (T1.99.17–26, 8 new) | 8 | ✅ All pass |
| `test_eks_engine_pipeline.py` total | 16 | ✅ All pass |
| Full EKS suite (`eks/test/`) | 275 | ✅ All pass |

---

## 6. Test Methodology, Environment, and Tools

### Methodology

- **Unit tests (entry-point)**: `eks/test/test_eks_engine_pipeline.py::TestEntryPointDiscovery` exercises `discover_project_root`, `resolve_pipeline_base_path`, `default_base_path`, `should_auto_create_folders`, and the `detect_os()` call inside `run()` using `unittest` + `unittest.mock` (cwd/Path patches, `detect_os` spy).
- **Integration smoke**: `run(["--data-dir", <dir>, "--json"])` executed from the repo root verifies the full L17 path through `discover_project_root` → `resolve_paths` → `run_pipeline`, asserting exit code 0.
- **No regression**: Full `eks/test/` suite (275 tests) run via `pytest` from the repo root.
- **Schema-driven verification**: Confirmed `resolve_paths(project_root, config).resolve(project_root)["data_dir"]` equals `project_root/eks/data` (the former bug case).

### Environment

| Component | Detail |
| :-------- | :----- |
| OS | Windows 11 |
| Python | 3.13 (conda env `eks`) |
| Test framework | pytest / unittest |
| Linter / type | n/a for this phase (docstring + revision metadata only) |

---

## 7. Test Phases, Steps, Cases, and Results

### 7.1 Entry-Point Discovery (`TestEntryPointDiscovery`) — 8 tests

| ID | Test Name | Status |
| :- | :-------- | :----: |
| T1.99.17-a | `test_discover_project_root_finds_anchor` — resolves repo root with `eks/` + `common/` present, not `engine/` | ✅ |
| T1.99.19-a | `test_resolve_pipeline_base_path_uses_cwd` — defaults to `cwd` (no `__file__` walk) | ✅ |
| T1.99.19-b | `test_resolve_pipeline_base_path_honors_base_path` — honours explicit `--base-path` | ✅ |
| T1.99.20-a | `test_resolve_pipeline_base_path_strips_pipeline_dir` — launched from inside `engine/` steps up (DCC 483-484) | ✅ |
| T1.99.23-a | `test_default_base_path_raises_when_missing` — `FileNotFoundError` when anchor absent | ✅ |
| T1.99.18-a | `test_default_base_path_finds_anchor` — walk locates project root via `eks` anchor | ✅ |
| T1.99.22-a | `test_should_auto_create_folders` — windows/linux/macos True, others False | ✅ |
| T1.99.24-a | `test_detect_os_called_in_run` — `run()` invokes `detect_os()` and resolves `eks_root`-aware `data_dir` | ✅ |

### 7.2 Full Suite Regression

| Suite | Tests | Status |
| :---- | :---: | :----: |
| `eks/test/` (all) | 275 | ✅ All pass |

---

## 8. Test Success Criteria and Checklist

| # | Criterion (workplan §30 success criteria) | Status |
| :- | :-------- | :----: |
| 1 | `detect_os()` invoked at EKS entry; `os_info` captured (T1.99.17) | ✅ |
| 2 | `default_base_path("eks")` returns parent of anchor; no hardcoded depth (T1.99.18) | ✅ |
| 3 | `resolve_pipeline_base_path()` = `--base-path` else `cwd` (T1.99.19) | ✅ |
| 4 | `discover_project_root()` + `--base-path` CLI + `==pipeline_dir` strip; deterministic root (T1.99.20) | ✅ |
| 5 | Default `data_dir` → `project_root/eks/data` via `resolve_paths()` (T1.99.21) | ✅ |
| 6 | Auto-create OS-gated; paths serialized via `safe_posix()` (T1.99.22) | ✅ |
| 7 | Anchor-missing raises `FileNotFoundError` (T1.99.23) | ✅ |
| 8 | Entry-point resolution tests green (T1.99.24) | ✅ |
| 9 | EKS consumes common L12/L17 (I078 advanced) (T1.99.25) | ✅ |
| 10 | I098 → Resolved; workplan/logs updated (T1.99.26) | ✅ |
| 11 | No regression — full EKS suite 275/275 green | ✅ |

---

## 9. Files Archived, Modified, and Version Controlled

### Files Created

| File | Version | Date | Author |
| :--- | :------ | :--- | :----- |
| `common/library/paths/root_discovery.py` | 1.0 | 2026-07-15 | opencode |

### Files Modified

| File | Version | Date | Author | Change |
| :--- | :------ | :--- | :----- | :----- |
| `common/library/core/paths/path_utils.py` | 1.1 | 2026-07-15 | opencode | Added `should_auto_create_folders()` (L12) de-duplicating DCC's triple `detect_os`; docstring revision note |
| `common/library/paths/__init__.py` | 1.1 | 2026-07-15 | opencode | Re-exported `should_auto_create_folders` + `discover_project_root` / `resolve_pipeline_base_path` / `default_base_path` / `DEFAULT_PIPELINE_DIR` |
| `eks/engine/eks_engine_pipeline.py` | 0.3 | 2026-07-15 | opencode | Entry now calls `detect_os()` (L12); `discover_project_root()` (anchor `eks`) replaces legacy resolver; `--base-path` CLI added; all sub-paths via `resolve_paths()` honouring `eks_root`; `auto_create` threaded through `bootstrap_pipeline`/`run_pipeline` and gated by `should_auto_create_folders`; `safe_posix()` for emitted paths; docstring revision |
| `eks/test/test_eks_engine_pipeline.py` | 0.4 | 2026-07-15 | opencode | Replaced anchor-folder tests with `TestEntryPointDiscovery` (8 tests); imports from `common.library.paths` |
| `eks/workplan/phase_1_foundation_workplan.md` | 3.67 | 2026-07-15 | opencode | T1.99.17–26 ✅ COMPLETE; §8 index + §30 task table + success-criteria checkboxes; status note; revision 3.67 |
| `eks/log/issue_log.md` | — | 2026-07-15 | opencode | I098 → ✅ Resolved with resolution text |
| `eks/log/update_log.md` | — | 2026-07-15 | opencode | U154 added (I098/T1.99.17–26 completion); Last Updated → 2026-07-15 |

### Files Archived

None (archive-before-delete not required; existing `resolve_pipeline_base_path` was replaced in place, no orphan left behind).

---

## 10. Recommendations for Future Actions

1. **Phase 2–5 entry points** — Apply the same `common.library.paths.root_discovery` L17 sequence to Phases 2–5 backends when their workplans are executed (tasks tracked in `phase_2/3/4/5` workplans).
2. **Universal runner extraction** — Promote `eks/engine/eks_engine_pipeline.py`'s `bootstrap_pipeline`/`run_pipeline` funnel into `common.library` (as flagged in I078 / T1.99.8/T1.99.12) so DCC and code_tracer can reuse one entry runtime.
3. **Anchor config** — Consider promoting `anchor`/`pipeline_dir` to a config value so nested projects declare their marker folder instead of hardcoding `"eks"` in the entry module.
4. **Report cross-link** — Add a pointer from `phase_1_foundation_report.md` to this report for traceability.

---

## 11. Lessons Learned

1. **Anchor vs pipeline_dir are distinct** — EKS nests code two levels deep (`project_root/eks/engine/...`) while related folders live under `project_root/eks/`. The natural EKS anchor is `eks` (project marker), not `engine` (module folder). Modelling both `anchor` and `pipeline_dir` separately keeps flat (DCC `workflow`) and nested (EKS `eks/engine`) projects correct under one L17 contract.
2. **`cwd`/`--base-path` must be the primary start** — DCC's operator-controlled start (cwd or `--base-path`) is more robust than an `__file__` walk; the walk should be a *last-resort fallback* that **raises** when the anchor is genuinely missing, eliminating silent wrong-root runs.
3. **`eks_root` must flow through `resolve_paths`** — Hardcoding `project_root / data_dir` bypassed `eks_root` and pointed the default run at a non-existent folder. Routing everything through the schema-driven resolver (L16) is the single fix for I098 #1.
4. **De-duplicate OS logic in `common`** — `detect_os`/`should_auto_create_folders` existed 3× in DCC; centralizing in L12 (`common.library.core.paths.path_utils`) is the SSOT the architecture calls for (AGENTS.md §10).
5. **`safe_posix()` for all serialized paths** — Cross-platform backslash risk (T1.74 class) is removed by serializing emitted telemetry/paths with `safe_posix()` rather than `str(Path)`.

---

## 12. References

- [Phase 1 Foundation Workplan](../phase_1_foundation_workplan.md)
- [Universal Pipeline Architecture Design](../../common/universal_pipeline_architecture_design.md) (§3.19 L17, §3.18 L16, §3.13 L12)
- [Update Log](../log/update_log.md) (U154)
- [Issue Log](../log/issue_log.md) (I098)
- DCC reference: `dcc/workflow/core_engine/paths/path_resolvers.py:9-45`, `dcc/workflow/core_engine/paths/path_core.py:78-93`, `dcc/workflow/dcc_engine_pipeline.py:483-484`

---

**End of Report**
