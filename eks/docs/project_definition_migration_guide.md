# Project Definition Migration Guide

| Revision | Date | Author | Summary |
| :--- | :--- | :--- | :--- |
| 1.0 | 2026-07-31 | Franklin | Initial guide — documents the I265 Project Definition refactoring (T1.189–T1.196) and the migration path for consumers of the retired legacy configuration. |

## 1. Purpose

This guide explains how EKS configuration ownership migrated from the legacy
`eks_project_rules_config.json` + scattered schema keys to the **Project
Definition** — `eks_project_definition_config.json` — resolved into an immutable
**RuntimeProjectConfiguration** by `ProjectDefinitionResolver` (I265).

It is the traceability companion to [Appendix L](../workplan/appendix_l_project_definition.md)
and the [Phase 1 Task Log §T1.189–T1.197](../log/phase1/p1_task_log.md#implementation-tasks).

## 2. Migration Path (L.11 Stages → Tasks)

| Stage | What | Task | Status |
| :---: | :--- | :--- | :---: |
| 1 | Project Definition architecture defined (Appendix L) | T1.189 | ✅ |
| 2 | Schema + config created; reusable libraries refactored | T1.190, T1.191 | ✅ |
| 3 | SchemaLoader compatibility verified; resolver implemented | T1.192, T1.193 | ✅ |
| 4 | Runtime modules migrated to configuration slices | T1.194 | ✅ |
| 5 | Configuration validation (V1/V2/V3) | T1.195 | ✅ |
| 6 | `$ref` consumers migrated; legacy config retired | T1.196 | ✅ |
| 7 | Docs/traceability/alignment | T1.197 | ✅ |

## 3. What Changed

### 3.1 Retired (T1.196)

- **`eks_project_rules_config.json`** — archived to `eks/archive/config/`.
- **`project_rules_registry`** — property + `required` entry removed from
  `eks_setup_schema.json` (v1.9.0); `$ref` removed from `eks_config.json` (v1.10.0).
- **`project_rules_def`** — removed from `eks_base_schema.json` (v1.15.0).
- **`compatibility.legacy_project_rules`** flag — removed (was dead config; no reader).
- **`_validate_project_rules()`** in `schema_loader.py` — removed.
- **`revision_validation`** doc_config reconstruction — removed (no consumers;
  RevisionManager consumes runtime slices since T1.194).

### 3.2 Kept (functional, not legacy)

- **`filename_patterns` reconstruction** in `schema_loader._extract()` (T1.191) —
  FilenameParser still needs the materialized patterns; the filename_parser slice
  carries only the pattern *name*. Re-evaluate when the slice carries resolved
  patterns.
- **Dict-based fallback params** in FileScanner / PipelineOrchestrator / FilenameParser
  (L.14.7) — no-registry mode remains a supported path for tests and standalone use.

### 3.3 New

- **`eks_project_definition_config.json`** (v1.3.0) — per-project SSOT:
  `project_identity`, `project_lifecycle`, `engineering_convention`,
  `engineering_standards`, `document_profile`, profile refs, `security_profile`,
  `runtime_profiles`, `fragment_required_fields`.
- **`ProjectDefinitionResolver`** (`engine/core/project_definition.py`) — 6-step
  workflow: load → resolve → validate → merge → construct → register; emits
  `errors` (system, hard-fail) and `data_errors` (non-blocking) per T1.195 V1.
- **`RuntimeProjectConfiguration`** — 17 immutable domain dataclasses; per-module
  `slice_for()` accessor (L.9.6). `fragment_required_fields` is carried in the
  AssetExtractor slice via `AssetsDomain.resolved` (I266).
- **`ProjectConfigurationRegistry`** — frozen dict keyed by project code; injected
  into FileScanner / PipelineOrchestrator (T1.194 D1 caller-injection contract).
- Error codes `S-C-S-0901..0904` (system) and `P1-C-V-0001..0003` (data) registered
  in `eks_error_config.json` v1.7.0.

## 4. Consumer Migration Checklist

| Consumer | Before (legacy) | After (T1.194/T1.196) |
| :--- | :--- | :--- |
| FileScanner | `doc_config["filename_patterns"]` keys | `project_config_registry.project_codes` (auto-detect, D2) |
| PipelineOrchestrator | `doc_config` dicts | injected registry + `_slice_for_orchestrator()` |
| FilenameParser | `project_code_registry` param | registry-derived codes; patterns via reconstruction |
| ColumnProcessor | dict config | `runtime_slice` param |
| FilePropertyExtractor / ParserRouter | dict config | optional `runtime_slice` |
| RevisionManager | `doc_config["revision_validation"]` | `runtime_slice` + per-call override |
| ConfigRegistry | `project_rules_registry` $ref reads | `get_project_rules` / `get_fragment_required_fields` / `resolve_required_fields` read `project_definition_config` (I266) |

## 5. Onboarding a New Project (config only)

1. Add a `project_code` entry under `project_definition` in
   `eks_project_definition_config.json`.
2. Reference reusable profiles by exact key (e.g. `parsing_profile: "technip_pdf"`).
3. Declare `fragment_required_fields` for asset validation rules (optional).
4. Bootstrap resolves + validates; system errors fail init, data errors are
   reported via `resolver.data_errors` (non-blocking).

## 6. Verification

- `python -m pytest eks/test/` — full suite 474 passed / 4 pre-existing
  (after T1.197 regression cleanup).
- Focused: `test_project_definition.py` (76), `test_runtime_slice_injection.py` (21),
  `test_t132_modules.py` (66).
- Cross-source audit per AGENTS.md §24: error codes, message IDs, paths, naming
  verified across config, code, and appendices (D, E, F, G, H, L).

## 7. References

- [Appendix L — Project Definition Architecture](../workplan/appendix_l_project_definition.md)
- [I265 issue](../log/phase1/p1_issue_log.md) (Project Definition Schema Refactoring)
- [I266–I272 issues](../log/phase1/p1_issue_log.md) (migration gaps)
- [U239–U246 updates](../log/phase1/p1_update_log.md)
- [TL028–TL032 tests](../log/phase1/p1_test_log.md)
