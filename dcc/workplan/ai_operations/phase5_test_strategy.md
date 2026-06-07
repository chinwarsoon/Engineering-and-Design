# Phase 5 Test Strategy — AI Ops Engine

**Date:** 2026-04-19 (Updated 2026-06-07 for Phase 5.6)

---

## Test Scope

| Area | Test File | Coverage |
|------|-----------|----------|
| Context builder | `test/test_ai_ops_engine.py` | build_ai_context() with real output files |
| Ollama provider | `test/test_ai_ops_engine.py` | Live call + fallback when unavailable |
| Risk analyzer | `test/test_ai_ops_engine.py` | Risk classification from mock error data |
| Run store | `test/test_ai_reporting_pack.py` | DuckDB save/load round-trip |
| Dashboard contract | `test/test_ai_dashboard_contract.py` | ai_insight_summary.json schema validation |
| **Phase 5.6: Schema-driven model pool** | `test/test_phase5_6_model_selection.py` | model_entry schema, selector, provider metadata-free, RunStore columns |

## Phase 5.6 Test Cases

| Test ID | Description | Target |
|---------|-------------|--------|
| TC-5.6.1 | `model_entry` definition accepts valid entries; rejects malformed `name` | PASS |
| TC-5.6.1 | `dcc_parameter_entry` extended with `model_pool` / `embed_model_pool` / `model_memory_headroom_gb` | PASS |
| TC-5.6.1 | `gemma4:e4b` has `enabled: false` in `dcc_global_parameters.json` | PASS |
| TC-5.6.2 | `_select_model_by_memory()` skips `enabled: false` entries | PASS |
| TC-5.6.2 | Selector returns `None` + `reason="no_model_fits"` when nothing fits | PASS |
| TC-5.6.3 | `OllamaProvider` contains no hardcoded model-name strings (`grep` guard) | PASS |
| TC-5.6.3 | `_DEFAULT_MODEL` constant removed from provider | PASS |
| TC-5.6.4 | `AiInsight` carries `model_family` / `model_capability` / `free_ram_mb` / `required_ram_mb` / `selection_reason` | PASS |
| TC-5.6.5 | `RunStore` adds 5 new columns to `ai_insights` table on init (idempotent ALTER) | PASS |
| TC-5.6.5 | `save_insight()` persists all 13 columns including new telemetry | PASS |

## Acceptance Criteria

| Criterion | Target |
|-----------|--------|
| Context builds without error from real output files | PASS |
| Ollama provider returns structured AiInsight | PASS |
| Fallback produces valid AiInsight when Ollama down | PASS |
| Risk level assigned for all error severity bands | PASS |
| DuckDB run record persisted and retrievable | PASS |
| ai_insight_summary.json valid JSON with required keys | PASS |
| SSE events emitted for all 6 pipeline steps | PASS |
| Dashboard loads ai_insight_summary.json without errors | PASS |
| **(5.6)** Model selection is fully schema-driven (no hardcoded model names in provider) | PASS |
| **(5.6)** Selector honors `enabled: false` (gemma4:e4b never selected) | PASS |
| **(5.6)** `ai_insights` DuckDB table records memory + family + selection reason | PASS |

## Fallback Test

When `ollama` is not running:
- Provider catches `ConnectionError` / `httpx.ConnectError`
- Falls back to `RuleBasedProvider` which generates summary from error stats
- `fallback_used: true` in AiInsight output
- Pipeline continues normally — AI step is non-blocking

When **no model fits available RAM** (Phase 5.6):
- Selector returns `None` with `selection_reason="no_model_fits"`
- `AiOpsEngine._run_provider` skips Ollama and uses `RuleBasedProvider`
- `insight.selection_reason == "no_model_fits"` is persisted to DuckDB
- Pipeline continues normally — AI step is non-blocking
