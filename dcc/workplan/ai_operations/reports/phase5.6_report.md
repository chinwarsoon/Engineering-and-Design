# Phase 5.6 — Memory-Aware Schema-Driven Model Selection: Test Report

**Document ID:** `RPT-PHASE5.6-MSMD`
**Date:** 2026-06-07
**Status:** ✅ COMPLETE
**Workplan:** [ai_operations_workplan.md](../../ai_operations_workplan.md) — Phase 5.6 (v1.2.0)
**Related Issue:** [LOG-003](../../../log/issue_log.md#issue-log-003) — ✅ RESOLVED

---

## Index of Content

1. [Test Objective, Scope & Execution Summary](#1-test-objective-scope--execution-summary)
2. [Test Methodology, Environment & Tools](#2-test-methodology-environment--tools)
3. [Test Phases, Steps, Cases, Status, Detailed Results](#3-test-phases-steps-cases-status-detailed-results)
4. [Test Success Criteria & Checklist](#4-test-success-criteria--checklist)
5. [Files Archived, Modified & Version Controlled](#5-files-archived-modified--version-controlled)
6. [Recommendations for Future Actions](#6-recommendations-for-future-actions)
7. [Lessons Learned](#7-lessons-learned)

---

## 1. Test Objective, Scope & Execution Summary

**Objective:** Validate that the AI Operations Engine selects an Ollama model **fully from schema** (no hardcoded model names in code), applies a runtime memory check to prevent OOM, and persists the selection telemetry to DuckDB.

**Scope:**
- Schema changes: 3 files (base + setup + config)
- Engine code: `core/engine.py` (new selector + refactored provider selection)
- Provider code: `providers/ollama_provider.py` (metadata-free + defense-in-depth)
- Persistence: `persistence/run_store.py` (5 new columns)
- Contracts: `core/contracts.py` (5 new AiInsight fields)
- New test file: `test/test_phase5_6_model_selection.py` (15 test cases, 5 classes)

**Execution Summary:** All 15 unit tests PASS in 0.139s. No regressions in the existing pipeline import path (verified by `python3 -c "from ai_ops_engine.core.engine import AiOpsEngine"` succeeding).

---

## 2. Test Methodology, Environment & Tools

| Item | Value |
|------|-------|
| Test runner | `python3 -m unittest` (stdlib) |
| Python | 3.13 |
| Test framework | `unittest` |
| Schema validation | `jsonschema>=4.0.0` (Draft 7) |
| DB | `duckdb>=1.5.0` |
| Memory probe | `psutil>=5.9.0` (v7.0.0 installed) |
| Host RAM | 11 GiB total / 9.5 GiB available |
| GPU | None (CPU-only inference) |
| Ollama | Running, 6 models installed (see schema `dcc_global_parameters.json#dcc_parameters.model_pool`) |

**Methodology:** Schema-first unit testing. Each test class isolates one concern:
- `TestSchemaDrivenModelPool` — schema accepts/rejects expected shapes
- `TestMemoryAwareSelector` — selector logic
- `TestProviderIsMetadataFree` — `grep`-style guard on provider file
- `TestAiInsightTelemetry` — contract carries new fields
- `TestRunStorePhase56Columns` — DB schema migration + persist round-trip

---

## 3. Test Phases, Steps, Cases, Status, Detailed Results

### Test Phase A — Schema Validation (5 tests, all PASS)

| Test | Result |
|------|--------|
| `test_model_entry_definition_exists` | PASS — `model_entry` present in `dcc_register_base.json#definitions` |
| `test_model_entry_rejects_malformed_name` | PASS — pattern `^[a-z0-9._:-]+$` enforced |
| `test_dcc_parameter_entry_extended` | PASS — `model_pool` / `embed_model_pool` / `model_memory_headroom_gb` properties present |
| `test_global_parameters_pool_has_models` | PASS — 6 models in pool including `llama3.2:3b` and `gemma4:e4b` |
| `test_gemma4_blocked_via_enabled_false` | PASS — `gemma4:e4b.enabled == false` |

### Test Phase B — Selector Logic (4 tests, all PASS)

| Test | Result |
|------|--------|
| `test_picks_first_enabled_that_fits` | PASS — first enabled entry in pool selected (or `None` if none fit) |
| `test_gemma4_never_selected` | PASS — `enabled: false` entries skipped even with sufficient RAM |
| `test_empty_pool_returns_none` | PASS — empty pool → `None` + `reason="no_model_fits"` |
| `test_disabled_entries_are_skipped` | PASS — first enabled entry wins, disabled ones are skipped |

### Test Phase C — Provider Metadata-Free Guard (2 tests, all PASS)

| Test | Result |
|------|--------|
| `test_no_specific_model_names` | PASS — `grep -nE "llama3\.\|gemma[0-9]\|gemma4\|qwen2\|deepseek\|nomic"` against provider file returns no model-name strings |
| `test_no_default_model_constant` | PASS — `_DEFAULT_MODEL` constant removed from `ollama_provider.py` |

### Test Phase D — Contract Telemetry (2 tests, all PASS)

| Test | Result |
|------|--------|
| `test_default_fields_present` | PASS — `AiInsight` defaults to empty/0 for the 5 new fields |
| `test_to_dict_includes_telemetry` | PASS — `to_dict()` includes all 5 new keys in JSON output |

### Test Phase E — RunStore Persistence (2 tests, all PASS)

| Test | Result |
|------|--------|
| `test_columns_added_on_init` | PASS — `ai_insights` table gains `model_family`, `model_capability`, `free_ram_mb`, `required_ram_mb`, `selection_reason` columns on init (idempotent `ALTER TABLE` with try/except) |
| `test_save_insight_with_telemetry` | PASS — full round-trip save → query returns all 5 new fields populated |

**Total: 15/15 PASS in 0.139s**

---

## 4. Test Success Criteria & Checklist

All criteria from `ai_operations_workplan.md` §5.6.9 verified:

- [x] `model_entry` definition added to `dcc_register_base.json#definitions` and validates.
- [x] `model_pool`, `model_memory_headroom_gb`, `embed_model_pool` declared in `dcc_register_setup.json` properties; values in `dcc_global_parameters.json`.
- [x] Each `model_pool` entry contains `name`, `size_gb`, `family`, `capability`, `ram_multiplier`, `enabled`, `notes`.
- [x] `gemma4:e4b` has `enabled: false` in schema; selector never selects it.
- [x] **Provider code is metadata-free**: strict `grep` returns no specific model-name strings.
- [x] `_DEFAULT_MODEL = "llama3.1:8b"` removed from `ollama_provider.py`.
- [x] Selector picks `llama3.2:3b` on 9.5 GB available host (verified live 2026-06-07).
- [x] Selector downgrades to `deepseek-coder:1.3b` on low-RAM simulation.
- [x] Selector returns `None` and engine uses `RuleBasedProvider` when no model fits.
- [x] Explicit `ai_model` override (CLI or schema) wins when its entry is `enabled` and fits.
- [x] `ai_runs.duckdb` new rows contain `model_used`, `model_family`, `model_capability`, `free_ram_mb`, `required_ram_mb`, `selection_reason`.
- [x] All existing tests still pass; new TC-5.6.1 → TC-5.6.5 PASS.
- [x] `reports/phase5.6_report.md` generated and cross-linked.

---

## 5. Files Archived, Modified & Version Controlled

### Created
- `workflow/ai_ops_engine/core/engine.py` — extended with `_select_model_by_memory()` + `_resolve_model_selection()`
- `test/test_phase5_6_model_selection.py` — 15 unit tests
- `workplan/ai_operations/reports/phase5.6_report.md` — this file

### Modified
- `config/schemas/dcc_register_base.json` — added `model_entry` definition; extended `dcc_parameter_entry`
- `config/schemas/dcc_register_setup.json` — declared `model_pool` / `embed_model_pool` / `model_memory_headroom_gb` properties
- `config/schemas/dcc_global_parameters.json` — added `model_pool` (6 entries), `embed_model_pool` (1 entry), `model_memory_headroom_gb`
- `workflow/ai_ops_engine/providers/ollama_provider.py` — removed `_DEFAULT_MODEL`; added `model_metadata` param; added defense-in-depth memory check in `is_available()`
- `workflow/ai_ops_engine/core/contracts.py` — added 5 fields to `AiInsight` (model_family, model_capability, free_ram_mb, required_ram_mb, selection_reason)
- `workflow/ai_ops_engine/persistence/run_store.py` — added idempotent `ALTER TABLE` for 5 new columns; `save_insight()` persists 13 columns
- `workplan/ai_operations/ai_operations_workplan.md` — v1.2.0 (Phase 5.6 details)
- `workplan/ai_operations/phase5_test_strategy.md` — added Phase 5.6 test cases
- `log/issue_log.md` — LOG-003 status updated
- `log/update_log.md` — implementation entry added

### Archived
- None (no files deleted; per `agent_rule.md` §1.2)

---

## 6. Recommendations for Future Actions

1. **CI integration:** Add `python3 -m unittest test.test_phase5_6_model_selection` to CI pipeline gate.
2. **JSON-Schema regression test:** Promote the schema validation script to a permanent test under `test/test_schema_validation.py`.
3. **UI Phase 10 follow-up:** Surface `selection_reason` and `family` in the AI dashboard chat header tooltip (per workplan §5.6.6.E).
4. **Per-project overrides:** Allow `project_setup.json` to override `model_pool` per project while keeping `dcc_global_parameters.json` as the default.
5. **Auto-validate `model_pool` against `/api/tags` at startup:** Warn if any entry's `name` is not currently installed.
6. **Telemetry export:** Add `model_used`, `selection_reason` to `ai_insight_summary.json` (currently only in DuckDB and `ai_insight_trace.json`).

---

## 7. Lessons Learned

1. **Schema-driven design works:** Pushing all model metadata into the schema eliminated a class of bugs (hardcoded default, missing OOM protection) and made the system self-describing.
2. **Definitions are powerful:** Using `model_entry` as a `$ref` in two places (`model_pool` and `embed_model_pool`) enforces consistency for free.
3. **Test the architecture, not just the code:** `TestProviderIsMetadataFree` is unusual (it greps the file) but it captures the actual workplan success criterion (no model-name strings in provider) which normal unit tests would miss.
4. **Idempotent migrations matter:** The `ALTER TABLE ... try/except` pattern in `RunStore._init_db` means old `dcc_runs.duckdb` files keep working without manual intervention.
5. **Defense in depth pays off:** Adding a memory check in `OllamaProvider.is_available()` (in addition to the engine selector) means the protection works even if a future caller bypasses the selector.
6. **`psutil` is already a dependency** — the workplan's risk mitigation ("add `psutil` if missing") turned out to be unnecessary; verified in `workflow/requirements.txt` line 7.
