# EKS Phase 1.3 — Initiation Schema & Validation Harmonization (Universal Pattern)

**Document ID**: WP-EKS-P1.3-001  
**Current Version**: 1.0  
**Status**: ✅ COMPLETE — T1.84–T1.89 all implemented. Universal `ValidationManager` in `common/library/utility/validation/`. EKS `project_setup` schema reshaped to DCC-aligned object model. DCC itself NOT modified (deferred follow-up).  
**Last Updated**: 2026-07-09  
**Parent Workplan**: [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md)  
**Phase Dependency**: Phase 1 (Foundation) — ✅ COMPLETE; Phase 1.2 (Interactive UI) — independent  

---

## 1. Title and Description

Harmonize EKS's `project_setup` schema definition and setup-validation code with DCC's universal initiation pattern, in support of the project goal: **maintain universal codes, functions, and modules across pipeline projects, and keep schema-file design consistent** (AGENTS.md §9; `common/universal_pipeline_architecture_design.md` §3.9).

This phase:
1. Establishes a reusable, path-agnostic `ValidationManager` in `common/library/validation/` (modeled on DCC's mature `validation_manager.py` + `initiation_engine/validators/items.py`), so both EKS and (later) DCC can share one implementation.
2. Reshapes EKS's per-project `project_setup` schema (in `eks/config/schemas/`) from flat **string arrays** to DCC's richer **object-array** model (`folders` / `root_files` / `schema_files` / `discovery_rules` / `environment` / `dependencies` / `validation_rules` / `project_metadata`), each entry carrying `name` / `required` / `purpose` / `auto_created` metadata.
3. Extracts the `project_setup` instance data out of `eks_config.json` into a dedicated `eks_project_setup_config.json`, mirroring the `eks_project_rules_config.json` (T1.67) pattern.
4. Refactors `eks/engine/core/setup_validator.py` into a thin adapter that delegates to the universal module, while preserving the public `validate_all()` API, the `P1-SETUP-*` error codes, and the `ErrorManager.handle_system_error("P1-SETUP-READINESS")` wiring that `phase1_server.py` depends on.

**Out of scope (deferred):** DCC migration to the shared module/schema; renaming EKS folders to match DCC's `workflow`/`tools`/`Log` names (AGENTS.md §6 fixes EKS folder names).

---

## 2. Revision Control & Version History

| Version | Date | Author | Summary |
| :------ | :--- | :----- | :------ |
| 1.0 | 2026-07-09 | opencode | Initial workplan for Phase 1.3 initiation harmonization. Scoped from a re-audit finding that EKS `project_setup` diverges from DCC (flat string arrays vs rich object arrays with metadata). Decisions (confirmed with user): (a) create shared `ValidationManager` in `common/library/utility/validation/`; (b) keep schemas per-project but align their shape to DCC (no repo-root shared schema); (c) migrate EKS only now, DCC in a later follow-up. Logged I085 for the schema-design inconsistency. |
| 1.1 | 2026-07-09 | opencode | Phase 1.3 COMPLETE — all T1.84–T1.89 implemented. Universal ValidationManager in common/library/utility/validation/manager.py (DCC-aligned methods). eks_base_schema v1.7.0 (8 new object defs), eks_setup_schema v1.4.0, eks_project_setup_config.json v1.0.0. setup_validator.py v0.7 thin adapter. 39 tests added/updated (19 + 20). 235/235 pass. I085 resolved. Workplan, knowledge.json, logs updated. |

---

## 3. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Revision Control & Version History](#2-revision-control--version-history)
- [3. Index of Content](#3-index-of-content)
- [4. Objective](#4-objective)
- [5. Scope Summary](#5-scope-summary)
- [6. Evaluation and Alignment with Existing Architecture](#6-evaluation-and-alignment-with-existing-architecture)
- [7. Dependencies](#7-dependencies)
- [8. Implementation Phases / Task Breakdown (T1.84–T1.89)](#8-implementation-phases--task-breakdown-t1.84t1.89)
- [9. Files and Modules to Create/Update](#9-files-and-modules-to-createupdate)
- [10. Risks and Mitigation](#10-risks-and-mitigation)
- [11. Success Criteria](#11-success-criteria)
- [12. References](#12-references)

---

## 4. Objective

Achieve **schema-design consistency** and **code-module universality** for project-setup validation, so that EKS and (later) DCC validate project structure through one shared, well-tested module and through schemas that follow the same shape. EKS's AGENTS.md §6-mandated folder names are preserved — only the *schema shape* (not the folder names) aligns with DCC.

---

## 5. Scope Summary

| ID | Category | Title | Details | Status | Related |
| :-- | :------- | :---- | :------ | :----: | :------ |
| R99 | Foundation & Compliance | Initiation Harmonization | Universal `ValidationManager` + EKS `project_setup` reshape to DCC object model | T1.84–T1.89 | T1.67, T1.77, T1.78, T1.79–T1.83 |
| T1.84 | Foundation | Universal ValidationManager | Create `common/library/utility/validation/manager.py` (path-agnostic) — added `validate_folders`, `validate_named_files`, `validate_environment`, `validate_dependencies`, `validate_discovery_rules`, `validate_project_setup` | ✅ DONE | R99 |
| T1.85 | Schema | EKS schema reshape | Replaced flat-array defs with DCC-aligned object defs (8 new defs) in `eks_base_schema.json` v1.7.0 + `eks_setup_schema.json` v1.4.0 | ✅ DONE | T1.84, T1.67 |
| T1.86 | Schema | Extract project_setup config | Created `eks_project_setup_config.json` v1.0.0; eks_config.json v1.5.0 inlines project_setup data (schema validation requires concrete props) | ✅ DONE | T1.85, T1.67 |
| T1.87 | Code | EKS validator adapter | `setup_validator.py` v0.7 refactored as thin adapter delegating to universal module; preserves `P1-SETUP-*` + ErrorManager wiring; `_convert_flat_to_object()` for backward compat | ✅ DONE | T1.84, T1.86 |
| T1.88 | Testing | Test migration + coverage | Rewrote `test_setup_validator.py` (19 tests) for object arrays; created `test_validation_manager.py` (20 tests); full suite 235/235 green | ✅ DONE | T1.87 |
| T1.89 | Docs | Workplan/log/knowledge update | Updated workplan, knowledge.json v2.3.0, update_log (U130), issue_log (I085 resolved), phase report | ✅ DONE | T1.84–T1.88 |

---

## 6. Evaluation and Alignment with Existing Architecture

- **Mirrors DCC `initiation_engine`** (`dcc/workflow/initiation_engine/core/validator.py`, `validators/items.py`) and the mature `dcc/utility_engine/validation/validation_manager.py` (`validate_file_exists`, `validate_directory_exists`, `validate_parameter`, `validate_paths_and_parameters`, `validate_pipeline_prerequisites`, folder-creation support).
- **Aligns with `common/universal_pipeline_architecture_design.md` §3.9** (Project Setup Validation Pattern) and §3.9.1 (Initiation Integrity Layers). The universal doc already maps EKS `setup_validator.py` ↔ DCC `initiation_engine` and recommends capturing all initiation layers in one universal pattern.
- **Reuses `common/library/core/errors/error_manager.py`** for error-code emission (the universal layer already provides this; `common/library/validation/` is currently only an `__init__.py`).
- **`global_paths` is preserved** as a separate concern (runtime data/output/archive/config/log/eks_root resolution); `project_setup` is purely structure validation. The two are not merged.
- **AGENTS.md §6 folder names are fixed for EKS** (`archive/ config/ data/ output/ test/ ui/ engine/ log/ docs/ workplan/`). EKS keeps `log` (not DCC's `Log`). Engine subfolders (`engine/core`, `engine/parsers`, …) become `folders` entries with relative `name` values rather than a separate `required_engine_subfolders` list.

---

## 7. Dependencies

- `common/library/` universal layer — `core/errors/error_manager.py`, `core/logging/`, `core/paths/path_utils.py` (available, reusable).
- EKS `SchemaLoader` / `ConfigRegistry` — must continue to surface `project_setup` after extraction (same `$ref` mechanism as `eks_project_rules_config.json`, T1.67).
- DCC reference only (files read for pattern alignment; **not modified**).
- `phase1_server.py` — depends on `setup_validator.validate_all()`, `get_missing_items()`, and the `P1-SETUP-*` codes; its behavior must be unchanged.

---

## 8. Implementation Phases / Task Breakdown (T1.84–T1.89)

### T1.84 — Create universal `ValidationManager` in `common/library/validation/`
- **Scope**: R99
- **Definition**: Create `common/library/validation/validation_manager.py` (path-agnostic — takes `base_path`), modeled on DCC's mature `validation_manager.py` + `initiation_engine/validators/items.py`. Provide:
  - `validate_folders(base_path, folders[], auto_create_override=None)` — iterate `{name, required, purpose, auto_created}`; check existence; auto-create when `entry.auto_created` (or global override).
  - `validate_named_files(base_path, category, entries[], name_key, desc_key)` — generic for `root_files` / `schema_files`.
  - `validate_environment(env_entries[])` — location-aware (`root`/`config`/`tools`); checks env file existence + `key_dependencies`.
  - `validate_dependencies(deps)` — `required` / `optional` / `engines[{module, members, optional}]` probe.
  - `validate_discovery_rules(rules[])` — optional.
  - Structured result `{readiness, folders, files, environment, dependencies, error_codes[]}`; emit codes via `common/library/core/errors/error_manager.py`.
  - Export from `__init__.py`.
- **Related**: R99
- **Success criteria**: `[ ]` Universal `ValidationManager` exists in `common/library/validation/`, path-agnostic, covered by unit tests; reusable by EKS and DCC.

### T1.85 — Reshape EKS base/setup schema defs to DCC-aligned object model
- **Scope**: R99
- **Definition**: In `eks_base_schema.json`, replace the flat-array defs (`required_folder_setup_def`, `required_engine_subfolder_setup_def`, `required_file_setup_def`) and `environment_setup_def` / `validation_options_def` with DCC-aligned definitions:
  - `folder_entry_def` `{name, required, purpose, auto_created}`
  - `root_file_entry_def` `{name, required, purpose, extension}`
  - `schema_file_entry_def` `{filename, required, description}`
  - `discovery_rule_def` `{pattern, directory, recursive, auto_register, category, exclude_patterns[]}`
  - `environment_entry_def` `{name, required, file, location(enum root/config/tools), setup_commands[], key_dependencies[]}`
  - `dependency_config_def` `{required[], optional[], engines[{module, members[], optional}]}`
  - `validation_rule_def` `{rule, enabled, description, severity, parameters}`
  - `project_metadata_def` `{project_id, project_name, version, created_date, last_modified}`
  - Keep `global_paths_def` untouched. `validation_options_def` retained only for `strict_file_validation` / `verbose` if desired (global `auto_create_folders` bool is replaced by per-folder `auto_created`).
  In `eks_setup_schema.json`, reshape `project_setup` to properties `folders`, `root_files`, `schema_files`, `discovery_rules`, `environment` (array), `dependencies`, `validation_rules`, `project_metadata`; update `required` array; keep `additionalProperties: false`.
- **Related**: T1.84, T1.67
- **Success criteria**: `[ ]` EKS `project_setup` schema shape matches DCC (object arrays with metadata); schema validates against the reshaped base/setup.

### T1.86 — Extract `project_setup` instance data to `eks_project_setup_config.json`
- **Scope**: R99
- **Definition**: Create `eks/config/schemas/eks_project_setup_config.json` containing the instance data currently inline in `eks_config.json#/project_setup`, converted to the new object model: `folders[]` (objects, engine subfolders expressed as `name: "engine/core"` etc.), `root_files[]`, `schema_files[]`, `discovery_rules[]`, `environment[]`, `dependencies{}`, `validation_rules[]`, `project_metadata{}`. Remove the inline `project_setup` block from `eks_config.json`; wire it via the existing `$ref` / `ConfigRegistry` mechanism used by `eks_project_rules_config.json` (T1.67). `global_paths` stays in `eks_config.json`.
- **Related**: T1.85, T1.67
- **Success criteria**: `[ ]` `project_setup` lives in dedicated config file; `eks_config.json` no longer carries an inline `project_setup`; loader still exposes `project_setup` to consumers.

### T1.87 — Refactor `setup_validator.py` to delegate to the universal module
- **Scope**: R99
- **Definition**: Make `eks/engine/core/setup_validator.py` `ProjectSetupValidator` a **thin adapter** that loads `project_setup` config and delegates validation to `common.library.validation.ValidationManager`. Preserve:
  - Public `validate_all()` and `get_missing_items()` signatures (used by `phase1_server.py` and tests).
  - The EKS-specific `P1-SETUP-*` error codes — the universal module emits generic codes that EKS maps to `P1-SETUP-*`.
  - `ErrorManager.handle_system_error("P1-SETUP-READINESS")` readiness-gate behavior (unchanged externally).
  `phase1_server.py` changes only in how it accesses `config.project_setup` (now from the extracted config); readiness-gate logic unchanged.
- **Related**: T1.84, T1.86
- **Success criteria**: `[ ]` EKS validation runs through `common/library/validation/ValidationManager`; `phase1_server.py` readiness gate + `P1-SETUP-*` codes + ErrorManager wiring behavior unchanged.

### T1.88 — Test migration + universal-module coverage
- **Scope**: R99
- **Definition**: Rewrite `eks/test/test_setup_validator.py` to the new object-array config shape (entries carry `name`/`required`/`purpose`/`auto_created`); keep the 7 `P1-SETUP-*` error-code tests + SSOT `ValueError` test. Add unit tests for `common/library/validation/validation_manager.py` (folders/files/environment/dependencies, auto-create, readiness). Run the full EKS suite — target **215+ passing, zero regression**.
- **Related**: T1.87
- **Success criteria**: `[ ]` All tests migrated; universal module has its own tests; full EKS suite green.

### T1.89 — Documentation, logs, knowledge update
- **Scope**: R99
- **Definition**: Update `phase_1_foundation_workplan.md` (add cross-reference to this Phase 1.3 workplan + revision entry); update `eks/knowledge.json` (note Phase 1.3 planned/status); update `eks/log/update_log.md` (U128+); update `eks/log/issue_log.md` (I085 resolved by this phase); update `common/universal_pipeline_architecture_design.md` to record that the universal `ValidationManager` now exists in `common/library/validation/`. Generate a phase test report under `eks/workplan/reports/`.
- **Related**: T1.84–T1.88
- **Success criteria**: `[ ]` All docs/logs updated; consistency achieved for EKS recorded; DCC deferred noted.

---

## 9. Files and Modules to Create/Update

| File/Folder | Action | Purpose |
| :---------- | :----- | :------ |
| `common/library/validation/validation_manager.py` | Create | Universal, path-agnostic `ValidationManager` |
| `common/library/validation/__init__.py` | Update | Export `ValidationManager` |
| `eks/config/schemas/eks_project_setup_config.json` | Create | Instance data for `project_setup` (object model) |
| `eks/config/schemas/eks_base_schema.json` | Update | Replace flat-array defs with DCC-aligned object defs |
| `eks/config/schemas/eks_setup_schema.json` | Update | Reshape `project_setup` property to object model |
| `eks/config/schemas/eks_config.json` | Update | Remove inline `project_setup`; keep `global_paths` + `$ref` |
| `eks/engine/core/setup_validator.py` | Update | Thin adapter delegating to universal `ValidationManager` |
| `eks/test/test_setup_validator.py` | Update | Migrate to object-array config; keep `P1-SETUP-*` + SSOT tests |
| `eks/test/test_validation_manager.py` | Create | Unit tests for universal module |
| `eks/workplan/phase_1.3_initiation_harmonization_workplan.md` | Create | This workplan |
| `eks/workplan/reports/phase_1.3_report.md` | Create | Phase test report (on completion) |
| `eks/knowledge.json` | Update | Phase 1.3 status note |
| `eks/log/update_log.md` | Update | U128+ entries |
| `eks/log/issue_log.md` | Update | I085 logged/resolved |
| `common/universal_pipeline_architecture_design.md` | Update | Record universal `ValidationManager` exists |

---

## 10. Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
| :--- | :-------- | :----- | :--------- |
| `ConfigRegistry` fails to surface `project_setup` after extraction | Medium | High | Reuse exact `$ref`/loader mechanism from `eks_project_rules_config.json` (T1.67); add a test asserting `config["project_setup"]` is populated. |
| Backward-compat test breakage (`test_setup_validator.py` asserts string arrays) | High | Medium | Rewrite tests in T1.88 alongside the schema change; run suite before/after. |
| Behavior change in readiness gate (`phase1_server.py`) | Medium | High | Keep `validate_all()` + `get_missing_items()` signatures and `P1-SETUP-*` codes; add an integration test that the gate still raises via `ErrorManager`. |
| Over-engineering the universal module | Low | Medium | Limit to DCC-proven methods only; keep it path-agnostic and dependency-light. |
| Folder-name confusion (`log` vs `Log`, `engine` vs `workflow`) | Low | Low | Do NOT rename EKS folders (AGENTS.md §6); only align schema *shape*. |

---

## 11. Success Criteria

- [x] EKS `project_setup` schema shape matches DCC's (`folders` / `root_files` / `schema_files` / `discovery_rules` / `environment` / `dependencies` / `validation_rules` / `project_metadata` as object arrays with metadata; per-folder `auto_created`).
- [x] A reusable `ValidationManager` exists in `common/library/utility/validation/` and is path-agnostic (usable by EKS and later DCC).
- [x] EKS validation logic runs through the universal module; `phase1_server.py` readiness gate, `P1-SETUP-*` codes, and `ErrorManager` wiring are behaviorally unchanged.
- [x] Full EKS test suite green (235/235 passing); universal module has its own tests (20).
- [x] DCC left untouched (deferred follow-up).
- [x] Workplan, knowledge.json, update_log, issue_log, and universal architecture doc updated.

---

## 12. References

- [Phase 1 Foundation Workplan](../phase_1_foundation_workplan.md) — WP-EKS-P1-001 (parent; ✅ COMPLETE through T1.83)
- [Phase 1.2 Interactive UI Workplan](../phase_1.2_interactive_ui_workplan.md) — WP-EKS-P1.2-001
- [Universal Pipeline Architecture Design](../../common/universal_pipeline_architecture_design.md) — §3.9 Project Setup Validation, §3.9.1 Initiation Integrity Layers
- DCC reference (not modified): `dcc/config/schemas/project_setup_base.json`, `project_setup.json`, `project_config.json`; `dcc/workflow/initiation_engine/core/validator.py`; `dcc/workflow/initiation_engine/validators/items.py`; `dcc/utility_engine/validation/validation_manager.py`
- EKS current: `eks/config/schemas/eks_config.json` (`project_setup`), `eks_base_schema.json`, `eks_setup_schema.json`; `eks/engine/core/setup_validator.py`; `eks/ui/backend/phase1_server.py`
- EKS issue: I085 (schema-design divergence between EKS and DCC `project_setup`)
- AGENTS.md §6 (EKS folder convention), §9 (3-layer schema pattern), §15 (follow-up phase workplan)

---

**End of Workplan**
