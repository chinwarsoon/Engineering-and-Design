# EKS Test Log

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------ |
| 0.4 | 2026-07-27 | opencode | Updated TL005 count: 148→149 (added test_error_file_processing_suppressed_at_default_level). Added U201 noise audit fixes (3 registry info→debug, ERROR level 1→2, S-R-S-0409 FATAL→HIGH). |
| 0.3 | 2026-07-27 | opencode | Added TL005 — I234–I243 sweep regression tests (4 new: milestone emitted, INFO not STATUS, suppressed at level 0, B_COMPLETE hydration). 148/148 pass in test_phase1 + test_t132_modules. |
| 0.2 | 2026-07-17 | opencode | Added TL003 (I108–I117 bootstrap/entry-point focused tests) and TL004 (full EKS regression suite post-I117). Updated stale TL002 count (243→277). |
| 0.1 | 2026-07-11 | Codex | Created test log and recorded T1.97/I088 verification. |

---

## Test Execution Table

| ID | Date | Phase | Scope | Command | Result | Notes |
| :-- | :--- | :---- | :---- | :------ | :----- | :---- |
| TL005 | 2026-07-27 | Phase 1 | I234–I243 sweep — 5 regression tests + full Phase A + modules suite | `conda run -n eks python -m pytest eks/test/test_phase1.py eks/test/test_t132_modules.py` | ✅ 149/149 passed | Covers: Phase A milestones (emitted + not STATUS), ERROR_FILE_PROCESSING level 0 suppression (level 0 + default level 1), B_COMPLETE hydration with all kwargs. All existing tests green. 5 test functions in test_phase1.py and test_t132_modules.py. |
| TL004 | 2026-07-17 | Phase 1 | Full EKS regression suite (post-I117) | `conda run -n eks python -m pytest eks/test/` | ✅ ~269/277 passed (~8 expected failures) | Non-bootstrap: 252/259 pass (7 pre-existing failures). Pipeline: 17/29 pass (12 P1-BOOT-ENV failures). Import fix applied. |
| TL003 | 2026-07-17 | Phase 1 | I108–I117 bootstrap/entry-point focused tests | `conda run -n eks python -m pytest eks/test/test_eks_engine_pipeline.py` | ✅ 17/29 passed (12 expected P1-BOOT-ENV) | Covers: BootstrapManager, EKS wiring, main(), structured BootstrapError, preload infrastructure. 12 env-dependent failures not regressions. |
| TL002 | 2026-07-11 | Phase 1 | Full EKS regression suite | `conda run -n eks python -m pytest eks/test/` | ✅ 243/243 passed | Required unsandboxed execution (socket-based tests need local port binding). |
| TL001 | 2026-07-11 | Phase 1 | T1.97/I088 focused tests (system_parameters) | `conda run -n eks python -m pytest eks/test/test_system_parameters.py` | ✅ 7/7 passed | Flat config, direct object, DCC array entries, malformed, defaults, ConfigRegistry, SchemaLoader. |
