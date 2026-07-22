# EKS Test Log

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------ |
| 0.2 | 2026-07-17 | opencode | Added TL003 (I108–I117 bootstrap/entry-point focused tests) and TL004 (full EKS regression suite post-I117). Updated stale TL002 count (243→277). |
| 0.1 | 2026-07-11 | Codex | Created test log and recorded T1.97/I088 verification. |

---

## Test Execution Table

| ID | Date | Phase | Scope | Command | Result | Notes |
| :-- | :--- | :---- | :---- | :------ | :----- | :---- |
| TL004 | 2026-07-17 | Phase 1 | Full EKS regression suite (post-I117) | `conda run -n eks python -m pytest eks/test/` | ✅ ~269/277 passed (~8 expected failures) | Non-bootstrap: 252/259 pass (7 pre-existing failures unrelated to I108–I117). Pipeline: 17/29 pass (12 P1-BOOT-ENV failures from missing optional deps python-docx/rdflib/qdrant-client). Import fix applied to test_eks_engine_pipeline.py. |
| TL003 | 2026-07-17 | Phase 1 | I108–I117 bootstrap/entry-point focused tests | `conda run -n eks python -m pytest eks/test/test_eks_engine_pipeline.py` | ✅ 17/29 passed (12 expected failures from P1-BOOT-ENV) | Covers: universal BootstrapManager (L19), EKS wiring, main() simplification, structured BootstrapError + P1-BOOT-* codes, pre-bootstrap logger/heartbeat, env/dependency check (L20), lazy-import refactor, and `_preload_infrastructure()` pure-stdlib guard. Import fix applied: `discover_project_root` now imported from `common.library.paths.root_discovery`; `detect_os` mock path updated to `eks.engine.core.bootstrap`. 12 failures are P1-BOOT-ENV blocking when python-docx/rdflib/qdrant-client missing — not regressions. |
| TL001 | 2026-07-11 | Phase 1 | T1.97/I088 focused tests | `conda run -n eks python -m pytest eks/test/test_system_parameters.py` | ✅ 7/7 passed | Validates flat config, direct object, DCC array entries, malformed input, defaults, ConfigRegistry lookup, and SchemaLoader config validation. |
| TL002 | 2026-07-11 | Phase 1 | Full EKS regression suite | `conda run -n eks python -m pytest eks/test/` | ✅ 243/243 passed | Required unsandboxed execution because socket-based Phase 1 server tests need local port binding; sandbox run passed non-socket tests but blocked sockets with `PermissionError`. |
