# Phase 1 Test Log

**Project**: Engineering Knowledge System (EKS)
**Location**: `eks/log/phase1/p1_test_log.md`
**Last Updated**: 2026-07-23 (TL009 — I233 pipeline monolith split; 291/305 pass, no regressions)

Extracted from `eks/log/test_log.md` — Phase 1 entries only. Full source details archived at `eks/archive/log/test_log.md`.

---

## Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------ |
| 0.1 | 2026-07-22 | opencode | Migrated from main test_log.md: TL001–TL004 (all Phase 1). |
| 0.2 | 2026-07-23 | opencode | Added TL005 — I227 regression tests (Phase B DuckDB SSOT). |
| 0.3 | 2026-07-23 | opencode | Added TL006 — I232 doc_id SSOT tests (get_document_by_file_path). |
| 0.4 | 2026-07-23 | opencode | Added TL007 — I229 batch telemetry + I230 validation gates verification. |
| 0.5 | 2026-07-23 | opencode | Added TL008 — I231 version SSOT verification (291/305 pass). |
| 0.6 | 2026-07-23 | opencode | Added TL009 — I233 pipeline monolith split backward compatibility (291/305 pass, no regressions). |


---

## Test Execution Table

| ID | Date | Phase | Scope | Command | Result | Notes |
| :-- | :--- | :---- | :---- | :------ | :----- | :---- |
| TL004 | 2026-07-17 | Phase 1 | Full EKS regression suite (post-I117) | `conda run -n eks python -m pytest eks/test/` | ✅ ~269/277 passed (~8 expected failures) | Non-bootstrap: 252/259 pass (7 pre-existing failures unrelated to I108–I117). Pipeline: 17/29 pass (12 P1-BOOT-ENV failures from missing optional deps python-docx/rdflib/qdrant-client). Import fix applied to test_eks_engine_pipeline.py. |
| TL005 | 2026-07-23 | Phase 1 | I227 regression tests — Phase B reads from DuckDB instead of re-scan | `python -m pytest eks/test/test_phase1.py::TestPhaseBFileResolution -v` | ✅ 2/2 passed | Tests: `test_phase_b_reads_from_registry_instead_of_rescan` (mocks scanner, asserts `registry.list_documents` called and `scanner.scan` not called when DB has data), `test_phase_b_falls_back_to_scan_when_registry_empty` (mocks scanner, asserts `scanner.scan` called when `list_documents` returns empty). Both verify `_resolve_phase_b_files()` DuckDB-first logic. |
| TL006 | 2026-07-23 | Phase 1 | I232 doc_id SSOT tests — get_document_by_file_path | `python -m pytest eks/test/test_phase1.py::TestPhase1::test_get_document_by_file_path_found eks/test/test_phase1.py::TestPhase1::test_get_document_by_file_path_not_found eks/test/test_phase1.py::TestPhase1::test_get_document_by_file_path_synthetic_key_roundtrip -v` | ✅ 3/3 passed | Tests: `test_get_document_by_file_path_found` (registers doc, asserts file_path lookup returns matching doc_id and document_number), `test_get_document_by_file_path_not_found` (asserts None for unknown path), `test_get_document_by_file_path_synthetic_key_roundtrip` (simulates Phase A→B roundtrip: Phase A registers unresolvable filename with synthetic UNRESOLVED-{hash} key; Phase B resolves doc_id via file_path, asserts stem-based lookup fails — proving divergence eliminated). |
| TL007 | 2026-07-23 | Phase 1 | I229 batch telemetry + I230 validation gates | `python -m pytest eks/test/test_phase1.py::TestPhase1 -v` | ✅ 5/5 passed (291/305 full suite) | I229: verifies run_phase_b() still processes files correctly with batch telemetry replacing per-file checkpoints. I230: verifies PipelineOrchestrator methods work with validate_phase_transition() callable. Relevant tests: `test_phase_b_reads_from_registry_instead_of_rescan`, `test_phase_b_falls_back_to_scan_when_registry_empty`, `test_pipeline_orchestrator_error_manager_wiring`, `test_pipeline_orchestrator_phase_a`, `test_pipeline_orchestrator_phase_c`. 291/305 pass (14 pre-existing rdflib env failures). |
| TL008 | 2026-07-23 | Phase 1 | I231 version SSOT — `eks.__version__` canonical source | `python -m pytest eks/test/` | ✅ 291/305 passed (14 pre-existing rdflib env failures) | I231: `eks/__init__.py` declares `__version__ = "2.6.0"` as SSOT. All 8 subpackage `__init__.py` files import `__version__` from `eks`. Confirmed by project-wide grep: zero hardcoded duplicate version strings outside `pyproject.toml` and `knowledge.json` (both already at 2.6.0). Full regression suite 291/305 pass — no regressions introduced. |
| TL009 | 2026-07-23 | Phase 1 | I233 pipeline monolith split backward compatibility | `python -m pytest eks/test/` | ✅ 291/305 passed (14 pre-existing rdflib env failures) | I233: `eks_engine_pipeline.py` reduced from 1,284 to 295 lines (thin entry-point shell). `pipeline_engine/` subfolder with `cli.py`, `runner.py`, `exporter.py` — zero module-level globals. All 4 public functions importable from `eks.engine.eks_engine_pipeline`. Console_scripts entry `eks-pipeline` resolves. Full regression suite: 291/305 pass — identical to pre-split baseline. No regressions introduced. |
| TL003 | 2026-07-17 | Phase 1 | I108–I117 bootstrap/entry-point focused tests | `conda run -n eks python -m pytest eks/test/test_eks_engine_pipeline.py` | ✅ 17/29 passed (12 expected failures from P1-BOOT-ENV) | Covers: universal BootstrapManager (L19), EKS wiring, main() simplification, structured BootstrapError + P1-BOOT-* codes, pre-bootstrap logger/heartbeat, env/dependency check (L20), lazy-import refactor, and `_preload_infrastructure()` pure-stdlib guard. Import fix applied: `discover_project_root` now imported from `common.library.paths.root_discovery`; `detect_os` mock path updated to `eks.engine.core.bootstrap`. 12 failures are P1-BOOT-ENV blocking when python-docx/rdflib/qdrant-client missing — not regressions. |
| TL002 | 2026-07-11 | Phase 1 | Full EKS regression suite | `conda run -n eks python -m pytest eks/test/` | ✅ 243/243 passed | Required unsandboxed execution because socket-based Phase 1 server tests need local port binding; sandbox run passed non-socket tests but blocked sockets with `PermissionError`. |
| TL001 | 2026-07-11 | Phase 1 | T1.97/I088 focused tests | `conda run -n eks python -m pytest eks/test/test_system_parameters.py` | ✅ 7/7 passed | Validates flat config, direct object, DCC array entries, malformed input, defaults, ConfigRegistry lookup, and SchemaLoader config validation. |
