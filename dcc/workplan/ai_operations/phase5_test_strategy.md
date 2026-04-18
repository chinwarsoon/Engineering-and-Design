# Phase 5 Test Strategy — AI Ops Engine

**Date:** 2026-04-19

---

## Test Scope

| Area | Test File | Coverage |
|------|-----------|----------|
| Context builder | `test/test_ai_ops_engine.py` | build_ai_context() with real output files |
| Ollama provider | `test/test_ai_ops_engine.py` | Live call + fallback when unavailable |
| Risk analyzer | `test/test_ai_ops_engine.py` | Risk classification from mock error data |
| Run store | `test/test_ai_reporting_pack.py` | DuckDB save/load round-trip |
| Dashboard contract | `test/test_ai_dashboard_contract.py` | ai_insight_summary.json schema validation |

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

## Fallback Test

When `ollama` is not running:
- Provider catches `ConnectionError` / `httpx.ConnectError`
- Falls back to `RuleBasedProvider` which generates summary from error stats
- `fallback_used: true` in AiInsight output
- Pipeline continues normally — AI step is non-blocking
