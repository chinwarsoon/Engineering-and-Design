| `ProjectSetupValidator.validate_all` | Run folder + file + environment checks; auto-create missing folders; compute `readiness` | `auto_create: bool = True` | `Dict` with keys `folders`, `files`, `environment`, `readiness` (`YES`/`NO`) | `_validate_folders`, `_validate_files`, `_validate_environment` | Missing items collected (not raised); `readiness='NO'` on gap | Verbose print of results |
| `ProjectSetupValidator.get_readiness_status` | Return `YES`/`NO` readiness gate used by pipeline start (T1.77) | (none) | `str` | `validate_all()` | Triggers `validate_all()` if not yet run | N/A |
| `ProjectSetupValidator.get_missing_items` | List missing folders/files for fail-fast 4xx/5xx report (T1.77) | (none) | `Dict[str, List[str]]` | `validate_all(auto_create=False)` | N/A | N/A |

> **T1.77 ✅:** `validate_all()` + `get_readiness_status()` wired into `phase1_server._run()` (fail-fast before any phase execution); `--debug`/`--level` CLI flags with effective-level logic; `data_dir` existence + `recursive` bool validated in `_handle_pipeline_start()` before concurrency guard. 8 `ProjectSetupValidator` unit tests + 3 T1.77 server integration tests created. 202/202 tests pass. Mirrors DCC `initiation_engine`.
> **T1.78 (✅ DONE):** Remediation of DCC gaps in T1.77 — fixed `eks.yml`→`eks/eks.yml` path (gate now passes), added input-file readability (G2), dependency probe + output-path validation (G3/G4), `--skip-readiness` override (G5), error code constants (G7). Also fixed pre-existing `_LogCapture.level` bug. See review gaps G1–G7. 207/207 tests pass.

---

## 16. References

1. [eks_system_workplan.md](eks_system_workplan.md) — Master workplan
2. [AGENTS.md](../AGENTS.md) — Repository guidelines
3. [eks/readme.md](../readme.md) — EKS project overview
4. [dcc/config/schemas](../../dcc/config/schemas) — Schema pattern reference
4b. [dcc/workflow/initiation_engine](../../dcc/workflow/initiation_engine) — DCC initiation integrity reference: `core/validator.py` (ProjectSetupValidator), `utils/parameters.py` (effective param resolution CLI→schema→default), `core/init_overrides.py` (PathSelection/ParameterOverride contracts, `validate_and_resolve`). Basis for T1.77; T1.78 closed gaps (input readability, env probe, dependency/output-path validation, `--skip-readiness` override, error codes).
5. [appendix_a_asset_schema.md](appendix_a_asset_schema.md) — Universal Plant Item Schema appendix
6. [appendix_c_ontology.md](appendix_c_ontology.md) — Dynamic ISO 15926-Aligned Ontology
7. [appendix_d_pipeline_messages_errors.md](appendix_d_pipeline_messages_errors.md) — Pipeline Messages & Error Codes (v0.3)
8. [appendix_e_schema_design.md](appendix_e_schema_design.md) — EKS Schema Design (v0.1)
