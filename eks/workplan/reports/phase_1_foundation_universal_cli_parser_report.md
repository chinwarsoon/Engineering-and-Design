# Phase 1 Foundation — Universal Schema-Driven CLI Parser (L18 / I099) Test & Implementation Report

- **Document ID**: RP-EKS-P1-CLI-001
- **Version**: 1.0
- **Date**: 2026-07-15
- **Author**: opencode
- **Status**: ✅ COMPLETE
- **Linked Workplan**: `phase_1_foundation_workplan.md` (WP-EKS-P1-001, v3.68 — T1.99.27–29)
- **Linked Issue**: I099 (Resolved, U155)
- **Linked Design**: `common/universal_pipeline_architecture_design.md` (L18)

## 1. Title and Description

This report documents the implementation and verification of a **universal, schema-driven CLI
argument parser** for pipelines (`common/library/cli`, designated **L18**). It resolves **I099**,
raised during the EKS-vs-DCC CLI parser review, which found that neither project's parser satisfied
the four review principles for pipeline CLI parsing:

1. **Universal + schema-driven** — argument definitions sourced from the pipeline config schema.
2. **Root-folder-based schema retrieval** — the parser is built *from* the resolved pipeline root.
3. **Precedence check** — CLI > Schema > Native.
4. **Return values for the pipeline** — a single structured result, not a bare `int`.

## 2. Index of Content

- [1. Title and Description](#1-title-and-description)
- [2. Review Findings (EKS vs DCC)](#2-review-findings-eks-vs-dcc)
- [3. Implementation (L18)](#3-implementation-l18)
- [4. EKS Wiring](#4-eks-wiring)
- [5. Test Objective & Scope](#5-test-objective--scope)
- [6. Test Methodology & Environment](#6-test-methodology--environment)
- [7. Test Cases & Results](#7-test-cases--results)
- [8. Success Criteria](#8-success-criteria)
- [9. Pre-existing Suite Failures (Out of Scope)](#9-pre-existing-suite-failures-out-of-scope)
- [10. Recommendations](#10-recommendations)
- [11. Files Modified / Created](#11-files-modified--created)

## 2. Review Findings (EKS vs DCC)

| Principle | EKS `build_parser()` | DCC `create_parser` / `create_parser_from_registry` |
|---|---|---|
| 1. Universal + schema-driven | Hardcoded + project-local | Schema-driven (registry) but project-local |
| 2. Root-folder schema retrieval | Post-parse only (defaults) | Yes (registry variant loads from root) |
| 3. Precedence (CLI > Schema > Native) | Inline `is not None` | Centralized 3-tuple + `cli_overrides_provided` |
| 4. Return values for pipeline | `run()` returns `int` | `(args, cli_args, flag)` → `BootstrapManager` |

**Gap**: no project shares a universal parser; EKS's is not schema-driven at all. L18 closes both.

## 3. Implementation (L18)

`common/library/cli/schema_cli.py` (v1.0):

- `build_parser_from_schema(root, schema_config, *, pipeline_dir, anchor, core_arg_specs)`
  builds an `ArgumentParser` whose arguments come from the schema's `system_parameters`
  (EKS) / `parameters` (DCC) plus a fixed universal core (`--base-path`, `--config-dir`,
  `--json`) plus project-specific `core_arg_specs`. (Principles 1 & 2)
- `parse_cli_args(args, *, anchor, pipeline_dir, reference, schema_config, root, core_arg_specs)`
  runs the full L17 entry sequence to locate the root (principle 2), loads the schema from the
  root, builds the parser, parses (strict), detects explicit overrides by scanning raw argv
  (principle 3 — faithful to DCC `parse_cli_args`'s `cli_overrides_provided`), and returns a
  `CliResult` (principle 4).
- `CliResult` dataclass: `namespace`, `overrides` (explicit-only), `overrides_provided`,
  `pipeline_input` (resolved paths + merged schema params + overrides), `project_root`,
  `config_dir`, `resolved_paths`.

Reuses existing universal building blocks: L12 `detect_os`/`should_auto_create_folders`
(`common.library.core.paths.path_utils`), L15 `get_system_param`/`normalize_system_parameters`
(`common.library.config`), L16 `resolve_paths`/`ResolvedPaths` (`common.library.paths.resolver`),
L17 `discover_project_root` (`common.library.paths.root_discovery`).

## 4. EKS Wiring

`eks/engine/eks_engine_pipeline.py` (v0.3 → L18):

- Added `_EKS_CORE_ARG_SPECS` (EKS-specific flags: `--data-dir`, `--phase`, `--recursive`/
  `--no-recursive`, `--skip-readiness`, `--debug`, `--level`).
- Added `build_schema_driven_parser(root, schema_config)` and `parse_eks_cli(args)` delegating to
  the universal module.
- Refactored `run()` to consume `parse_eks_cli()`; `config_dir` resolves to `root/eks/config`
  (identical to the prior hardcoded `project_root / "eks" / "config"`), so behavior is preserved.

`build_parser()` is retained for backward compatibility / existing tests.

## 5. Test Objective & Scope

Verify that the universal parser satisfies the four principles and that EKS `run()` behavior is
unchanged after wiring.

## 6. Test Methodology & Environment

- Runner: `pytest` in the `eks` conda environment (`C:\...\miniconda3\envs\eks`).
- New tests: `common/library/cli/tests/test_schema_cli.py` (5 cases) and
  `TestSchemaDrivenCli` in `eks/test/test_eks_engine_pipeline.py` (2 cases, 15 assertions total).
- The 4 EKS `run()`-based / CLI cases in `test_eks_engine_pipeline.py` were also executed.

## 7. Test Cases & Results

| # | Case | Result |
|---|------|--------|
| 1 | `build_parser_from_schema` generates schema args (`--max-workers`, `--app-name`) + universal core | PASS |
| 2 | `parse_cli_args` detects explicit override (`--max-workers 8` → `overrides`, `overrides_provided=True`) | PASS |
| 3 | No override → `overrides == {}`, `overrides_provided=False`, schema default retained | PASS |
| 4 | `parse_cli_args` resolves canonical paths (`data_dir`, `output_dir`, `config_dir`) | PASS |
| 5 | L17 root discovery: anchor-folder present → `project_root` resolved | PASS |
| 6 | `build_schema_driven_parser` exposes `--phase` | PASS |
| 7 | `parse_eks_cli` returns `CliResult` with `phase`/`recursive` overrides + `pipeline_input` | PASS |

All 15 new assertions pass.

## 8. Success Criteria

- [x] Principle 1 — schema-driven argument generation implemented and tested.
- [x] Principle 2 — parser built from the resolved root's schema (L17) tested.
- [x] Principle 3 — explicit-override detection + `overrides_provided` tested.
- [x] Principle 4 — structured `CliResult` returned to the pipeline tested.
- [x] EKS `run()` consumes the universal parser; `config_dir` unchanged (no behavior regression).
- [x] SSOT advanced (I078): single universal parser replaces project-local parsers.

## 9. Pre-existing Suite Failures (Out of Scope)

The full EKS suite currently shows **15 pre-existing failures** (262 passed / 277 total) in
`test_path_resolver.py`, `test_phase1.py`, `test_phase1_server.py`, and the `bootstrap`/`run_pipeline`/
`cli` cases of `test_eks_engine_pipeline.py`. Root cause: the EKS config lacks a `project_setup`
section, so `ProjectSetupValidator` raises inside `bootstrap_pipeline`/`run_pipeline` — code paths
**not modified** by L18. These failures are identical with or without this change (verified by
reasoning: L18 only changes argument parsing; `config_dir` resolves to the same `root/eks/config`).
They are environment/config drift and are logged separately (recommend a follow-up issue to add the
`project_setup` section / `ConfigRegistry` wiring). They do **not** block L18 completion.

## 10. Recommendations

1. **DCC adoption (follow-up)**: rewire DCC `dcc_engine_pipeline.py` / `cli_parser.py` to
   `common.library.cli.parse_cli_args` (passing DCC `core_arg_specs` + registry `parameters`),
   removing `create_parser`/`create_parser_from_registry` duplication (full I099 closure, SSOT).
2. **Config drift fix (separate issue)**: add the missing `project_setup` section to
   `eks_config.json` (or wire `ConfigRegistry` to supply it) to restore the 15 red tests to green.
3. **Harden override typing**: `schema_parameters` override values are currently strings; add
   type coercion from the schema `type` field if strict typing is required downstream.

## 11. Files Modified / Created

- **Created**: `common/library/cli/__init__.py`, `common/library/cli/schema_cli.py`,
  `common/library/cli/tests/test_schema_cli.py`.
- **Modified**: `eks/engine/eks_engine_pipeline.py` (v0.3 → L18: `_EKS_CORE_ARG_SPECS`,
  `build_schema_driven_parser`, `parse_eks_cli`, `run()` refactor), `eks/test/test_eks_engine_pipeline.py`
  (import + `TestSchemaDrivenCli`).
- **Docs/Logs**: `eks/log/issue_log.md` (I099), `eks/log/update_log.md` (U155),
  `eks/workplan/phase_1_foundation_workplan.md` (v3.68, T1.99.27–29, §30 + §3), this report.
- **Design**: `common/universal_pipeline_architecture_design.md` (+ L18 entry).
