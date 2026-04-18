# Phase 5 Engine Design — AI Ops Engine Architecture

**Date:** 2026-04-19

---

## Module Boundaries

```
dcc/workflow/ai_ops_engine/
├── __init__.py                    # Package exports
├── core/
│   ├── engine.py                  # Main orchestrator
│   ├── contracts.py               # Typed I/O contracts (dataclasses)
│   ├── context_builder.py         # Build model-ready context from pipeline outputs
│   └── evidence.py                # Link AI findings to row/column/phase evidence
├── providers/
│   ├── base.py                    # Abstract provider interface
│   └── ollama_provider.py         # Ollama local LLM adapter
├── analyzers/
│   ├── risk_analyzer.py           # Risk clusters and severity bands
│   ├── trend_analyzer.py          # Recurring issue pattern detection
│   └── summary_generator.py      # Executive summary generation
├── persistence/
│   ├── run_store.py               # Save/load run metadata (DuckDB)
│   └── duckdb_repository.py       # DuckDB schema and queries
├── streaming/
│   ├── event_stream.py            # Standard SSE event payloads
│   └── sse_bridge.py              # SSE generator for dashboard clients
└── utils/
    ├── logging.py                 # Tiered logging helpers
    └── serializers.py             # JSON-safe output normalizers
```

## Dependency Map

```
dcc_engine_pipeline.py
    └── ai_ops_engine.core.engine.AiOpsEngine
            ├── context_builder.build_ai_context()
            │       ├── reads: output/error_dashboard_data.json
            │       ├── reads: output/processing_summary.txt
            │       └── reads: processed_dcc_universal.csv (sample)
            ├── providers.ollama_provider.OllamaProvider
            │       └── POST http://localhost:11434/api/chat
            ├── analyzers.risk_analyzer.RiskAnalyzer
            ├── analyzers.trend_analyzer.TrendAnalyzer
            ├── analyzers.summary_generator.SummaryGenerator
            ├── evidence.attach_evidence_links()
            ├── persistence.run_store.RunStore  →  DuckDB
            └── streaming.event_stream.EventStream  →  SSE
```

## Integration Point in Pipeline

Phase 5 runs as **Step 7** after Step 6 (export), non-blocking:
```python
# Step 7: AI Operations (optional, non-blocking)
with log_context("pipeline", "step7_ai_ops"):
    ai_results = run_ai_ops(df_processed, export_paths, pipeline_schema_results)
```

## LLM Model Selection

| Task | Model | Reason |
|------|-------|--------|
| Risk analysis + summary | `llama3.1:8b` | Best reasoning in available models |
| Embedding (future) | `nomic-embed-text` | Already available |
| Fallback | Rule-based summary | When Ollama unavailable |
