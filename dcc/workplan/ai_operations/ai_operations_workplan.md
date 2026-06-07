# Phase 5 Master Workplan — AI Operations, Workplan Engine & Live Monitoring

**Phase:** 5 of 5  
**Status:** IN PROGRESS — Phase 5.6 ✅ COMPLETE  
**Date:** 2026-04-19  
**Last Updated:** 2026-06-07  
**Lead:** Franklin Song  
**Weeks:** 9–10  
**Document ID:** `WP-PHASE5-AIOPS`  
**Version:** 2.0.0 (2026-06-07 — Phase 5.6 implemented; 15/15 tests pass)

### Version History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-04-19 | Franklin Song | Initial Phase 5 master workplan (sub-phases 5.1–5.5) |
| 1.1.0 | 2026-06-07 | Franklin Song | Added Phase 5.6 — Memory-Aware Schema-Driven Model Selection (pending approval) |
| 1.2.0 | 2026-06-07 | Franklin Song | Phase 5.6 strengthening: `model_pool` is now **fully schema-driven** — per-model metadata (`size_gb`, `family`, `capability`, `ram_multiplier`, `enabled`, `notes`) defined as a `model_entry` definition in `dcc_register_base.json#definitions`; provider code is metadata-free; `_DEFAULT_MODEL` removed in favor of schema value |
| 2.0.0 | 2026-06-07 | Franklin Song | **Phase 5.6 implemented.** 10 files changed, 15/15 tests pass, LOG-003 resolved. See `reports/phase5.6_report.md`. |

---

## Overview

Phase 5 extends the DCC pipeline with an AI Operations Engine (`ai_ops_engine`) that transforms deterministic pipeline outputs into structured AI-ready insights, live run events, and governed reporting artifacts.

**Existing baseline consumed by this phase:**
- `output/error_dashboard_data.json` — structured error telemetry
- `output/processing_summary.txt` — text run summary
- `output/processed_dcc_universal.csv` — processed dataset
- `Validation_Errors` + `Data_Health_Score` columns in processed output

**Local LLM:** Ollama with model selected via schema-driven `ai_model` parameter in `config/schemas/dcc_global_parameters.json` (current runtime default: `llama3.2:3b`); hardcoded fallback `_DEFAULT_MODEL = "llama3.1:8b"` in `ai_ops_engine/providers/ollama_provider.py:33` is overridden by schema per precedence CLI > schema > native defaults. Embedding model: `nomic-embed-text` (embed).

---

## Sub-Phases

| Sub-Phase | Title | Status |
|-----------|-------|--------|
| 5.1 | Engine Architecture & Module Design | ✅ COMPLETE |
| 5.2 | AI Insight Engine | ✅ COMPLETE |
| 5.3 | AI Dashboard Integration | ✅ COMPLETE |
| 5.4 | Live Pipeline Monitoring | ✅ COMPLETE |
| 5.5 | Persistence & Governed Reporting Pack | ✅ COMPLETE |
| 5.6 | Memory-Aware Schema-Driven Model Selection | ✅ COMPLETE |

---

## Delivery Sequence

| Step | Deliverable | Location |
|------|-------------|----------|
| 5.1 | Engine package + contracts + context builder | `workflow/ai_ops_engine/` |
| 5.2 | Ollama provider + risk/trend/summary analyzers | `workflow/ai_ops_engine/` |
| 5.3 | AI analysis dashboard | `ui/ai_analysis_dashboard.html` |
| 5.4 | SSE event stream + pipeline integration | `workflow/ai_ops_engine/streaming/` |
| 5.5 | DuckDB run store + reporting pack builder | `workflow/ai_ops_engine/persistence/` |
| 5.6 | Memory-aware model selection + schema-driven `model_pool` | `workflow/ai_ops_engine/core/engine.py`, `workflow/ai_ops_engine/providers/ollama_provider.py`, `config/schemas/dcc_register_base.json`, `config/schemas/dcc_global_parameters.json` |

---

## Completion Criteria

- [x] Engine package importable and integrated into `dcc_engine_pipeline.py`
- [x] AI insights structured, explainable, traceable to source evidence
- [x] Ollama provider with graceful fallback when model unavailable
- [x] Live monitoring via SSE event stream
- [x] DuckDB persistence for run history
- [x] AI dashboard self-contained HTML tool
- [x] Phase reports created for each sub-phase
- [x] Logs updated
- [x] (5.6) Runtime memory check selects a fitting model from schema-driven `model_pool`
- [x] (5.6) `gemma4:e4b` removed from candidate list (confirmed unresponsive, `enabled=false`)
- [x] (5.6) Selected model + memory snapshot persisted to `ai_runs.duckdb`

---

## Reference Files

- `phase5_engine_design.md` — module boundaries and dependency map
- `phase5_io_contract.md` — input/output contracts and schemas
- `phase5_test_strategy.md` — test plan and acceptance criteria
- `reports/` — phase completion reports
- `reports/phase5.6_report.md` — (planned, post-approval) Phase 5.6 test/implementation report

---

# Phase 5.6 — Memory-Aware Schema-Driven Model Selection

**Document ID:** `WP-PHASE5.6-MSMD`  
**Status:** ✅ COMPLETE  
**Created:** 2026-06-07  
**Completed:** 2026-06-07  
**Author:** Franklin Song (with AI assist)  
**Related Phase:** 5.2 (Ollama provider), 5.5 (persistence)  
**Related Issue:** [LOG-003 — gemma4:e4b hang + hardcoded `llama3.1:8b` ignores schema-driven `llama3.2:3b`](../../../log/issue_log.md#issue-log-003) — ✅ RESOLVED  
**Test Report:** [phase5.6_report.md](./reports/phase5.6_report.md) — 15/15 PASS

## 5.6.1 Object

Eliminate the gap between the schema-driven `ai_model` value and the hardcoded `_DEFAULT_MODEL` in the Ollama provider, and add runtime memory-aware model selection so the pipeline never attempts to load a model larger than the host can sustain (prevents the observed `gemma4:e4b` hang on 11 GiB hosts).

## 5.6.2 Scope Summary

| ID | Task | Category | Status | Related Phase |
|---|---|---|---|---|
| 5.6.A | Define `model_entry` (base) + `model_pool`/`embed_model_pool` (base+setup+config) with per-model metadata: `name`, `size_gb`, `family`, `capability`, `ram_multiplier`, `enabled`, `notes` | Schema | ✅ Done | 5.2 |
| 5.6.B | Memory-aware selector in `core/engine.py::_run_provider` reads `model_pool` from resolved schema params; picks first `enabled` entry fitting `size_gb × ram_multiplier + headroom_gb ≤ available` | Enhancement | ✅ Done | 5.2 |
| 5.6.C | Make Ollama provider **metadata-free**: remove `_DEFAULT_MODEL = "llama3.1:8b"`, add defense-in-depth memory check in `is_available()` | Refactor | ✅ Done | 5.2 |
| 5.6.D | `gemma4:e4b` blocked via `enabled: false` in schema (not by code); `llama3.1:8b` retained as `enabled: true` for high-RAM hosts | Schema | ✅ Done | 5.2 |
| 5.6.E | Persist `model_used` + `model_family` + `model_capability` + `free_ram_mb` + `required_ram_mb` + `selection_reason` to `ai_runs.duckdb` (`run_store.py:80`) | Enhancement | ✅ Done | 5.5 |
| 5.6.F | UI: web_interface `model_selector` dropdown refresh after selection; show `family` and `selection_reason` tooltip (Phase 10 alignment) | Enhancement | ⏳ Deferred to Phase 10 | 10.x |
| 5.6.G | Update `phase5_test_strategy.md` + add `reports/phase5.6_report.md` per Section 9 | Documentation | ✅ Done | 5.6 |

## 5.6.3 Index of Content

1. Object (§5.6.1)
2. Scope Summary (§5.6.2)
3. Dependencies (§5.6.4)
4. Evaluation & Alignment (§5.6.5)
5. Implementation Phases (§5.6.6)
   - 5.6.A Schema-driven `model_pool`
   - 5.6.B Memory-aware selector
   - 5.6.C Ollama provider update
   - 5.6.D Persistence extension
   - 5.6.E UI alignment
   - 5.6.F Test strategy + report
6. Risks & Mitigation (§5.6.7)
7. Future Issues (§5.6.8)
8. Success Criteria (§5.6.9)
9. References (§5.6.10)

## 5.6.4 Dependencies

- **Upstream:** `ollama_provider.py` (Phase 5.2), `engine.py` (Phase 5.2), `run_store.py` (Phase 5.5)
- **Schema:** `dcc_register_base.json` (`dcc_parameter_entry` definition line 537; new `model_entry` definition TBD), `dcc_register_setup.json` (properties declaration), `dcc_global_parameters.json` (values, line 39)
- **UI (Phase 10):** `ui_design/web_interface/web_interface_workplan.md` — `GET /api/tags` + model selector dropdown (lines 1210, 1238, 1240, 1351–1352)
- **External:** `psutil` Python package (for runtime RAM check; verify availability in `workflow/requirements.txt`)
- **Out of scope:** Embedding model `nomic-embed-text` (registered in schema as a separate `model_entry` with `capability: "embed"`; not selected by RAM-aware logic — fixed footprint)

## 5.6.5 Evaluation & Alignment

**Alignment with existing architecture:**
- Follows SSOT principle (Section 4.3): model list lives in schema, not in code.
- Follows schema-driven design (Section 4.4): parameters never hardcoded.
- Follows base + setup + config inheritance (Section 2.3, 2.6): new `model_pool` property defined in `dcc_parameter_entry` (base), declared in `dcc_register_setup.json` (setup), valued in `dcc_global_parameters.json` (config).
- Follows tiered logging (Section 6): selection events logged at level 1 (status), headroom math at level 2 (debug).
- Complements Phase 5.2's existing "Ollama provider with graceful fallback when model unavailable" completion criterion (line 53).

**Tested ground truth (2026-06-07, host RAM 11 GiB / 9.5 GiB available, no GPU):**

| Model | Size | Est. RAM Need (~1.5×) | Test | Verdict |
|---|---|---|---|---|
| llama3.2:3b (schema default) | 2.0 GB | ~3.0 GB | OK 4.5s | Selected |
| qwen2.5-coder:3b | 1.9 GB | ~2.9 GB | OK 10s | Backup |
| deepseek-coder:1.3b | 776 MB | ~1.2 GB | OK instant | Low-RAM fallback |
| gemma3:4b | 3.3 GB | ~5.0 GB | OK 5.3s | Marginal |
| llama3.1:8b (hardcoded) | 4.9 GB | ~7.4 GB | OK 19.8s | Slow |
| gemma4:e4b | 9.6 GB | ~14 GB | **HANG 60s** | Exclude |

## 5.6.6 Implementation Phases

### 5.6.A — Fully schema-driven `model_pool` with per-model metadata

**Timeline:** 2026-06-08 (1 day)  
**Milestone:** All model metadata lives in schema — provider and selector code are metadata-free.  
**Alignment:** `agent_rule.md` §2.7 ("use 'Definitions' for repetitive objects") and §4.4 ("always consider schema driven design for 'global' parameters").

**Deliverables (three files, base+setup+config pattern per §2.3):**

**1. `dcc_register_base.json` — new `model_entry` definition** (add to `#/definitions`):
```json
"model_entry": {
  "type": "object",
  "description": "Single Ollama model descriptor. All model metadata lives here — provider code never hardcodes size/family/capability.",
  "additionalProperties": false,
  "required": ["name", "size_gb", "family", "capability"],
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z0-9._:-]+$",
      "description": "Ollama model tag, e.g. 'llama3.2:3b'. Must match `ollama list` output."
    },
    "size_gb": {
      "type": "number",
      "minimum": 0.1,
      "maximum": 100,
      "description": "On-disk model weight size in GB. Drives RAM headroom calculation."
    },
    "family": {
      "type": "string",
      "enum": ["llama", "llama3", "llama3.1", "llama3.2", "gemma", "gemma3", "gemma4", "qwen", "qwen2", "qwen2.5", "deepseek", "deepseek-coder", "nomic", "other"],
      "description": "Model family for capability/telemetry grouping."
    },
    "capability": {
      "type": "string",
      "enum": ["chat", "embed", "code", "vision"],
      "description": "What the model is used for in the pipeline."
    },
    "ram_multiplier": {
      "type": "number",
      "minimum": 1.0,
      "maximum": 3.0,
      "default": 1.5,
      "description": "Multiplier applied to `size_gb` to estimate runtime RAM. Default 1.5 reflects Ollama's typical overhead. Override per-model if measured locally."
    },
    "enabled": {
      "type": "boolean",
      "default": true,
      "description": "Per-model kill-switch without removing the entry. Used to block known-bad models (e.g. gemma4:e4b) defensively."
    },
    "notes": {
      "type": "string",
      "description": "Free-text rationale, e.g. 'hangs on 11 GiB host — do not enable'."
    }
  }
}
```

**2. `dcc_register_base.json#dcc_parameter_entry` — add `model_pool` and related properties** (extend the existing definition at line 537):
```json
"model_pool": {
  "type": "array",
  "description": "Ordered preference list of Ollama models for AI ops. The selector iterates this list and picks the first `enabled` entry whose `size_gb * ram_multiplier + model_memory_headroom_gb` fits the host's free RAM at runtime.",
  "minItems": 1,
  "items": {"$ref": "https://dcc-pipeline.internal/schemas/dcc_register_base#/definitions/model_entry"}
},
"model_memory_headroom_gb": {
  "type": "number",
  "minimum": 0,
  "maximum": 16,
  "default": 2.0,
  "description": "Fixed GB reserved for OS + Python process + Ollama runtime overhead, on top of model RAM estimate."
},
"embed_model_pool": {
  "type": "array",
  "description": "Embedding models (not RAM-selected; used by name). Same model_entry shape, but `capability: embed`.",
  "items": {"$ref": "https://dcc-pipeline.internal/schemas/dcc_register_base#/definitions/model_entry"}
}
```

**3. `dcc_register_setup.json` — declare the new properties in `properties` block** (lines 12–93):
```json
"model_pool": {
  "description": "Ordered Ollama chat model preference list (schema-driven)."
},
"model_memory_headroom_gb": {
  "description": "RAM headroom reserved for non-model processes."
},
"embed_model_pool": {
  "description": "Embedding model pool (not RAM-selected)."
}
```

**4. `dcc_global_parameters.json` — add values** (extend `dcc_parameters` near line 39):
```json
"ai_model": "llama3.2:3b",
"model_memory_headroom_gb": 2.0,
"model_pool": [
  {
    "name": "llama3.2:3b",
    "size_gb": 2.0,
    "family": "llama3.2",
    "capability": "chat",
    "ram_multiplier": 1.5,
    "enabled": true,
    "notes": "Schema default. Best fit/quality balance for 9.5 GB available RAM."
  },
  {
    "name": "qwen2.5-coder:3b",
    "size_gb": 1.9,
    "family": "qwen2.5",
    "capability": "code",
    "ram_multiplier": 1.5,
    "enabled": true,
    "notes": "Backup candidate for code-heavy prompts."
  },
  {
    "name": "deepseek-coder:1.3b",
    "size_gb": 0.776,
    "family": "deepseek-coder",
    "capability": "code",
    "ram_multiplier": 1.5,
    "enabled": true,
    "notes": "Low-RAM fallback. Tested OK on 1.2 GB available."
  },
  {
    "name": "gemma3:4b",
    "size_gb": 3.3,
    "family": "gemma3",
    "capability": "chat",
    "ram_multiplier": 1.5,
    "enabled": true,
    "notes": "Marginal headroom; use when 5+ GB free."
  },
  {
    "name": "gemma4:e4b",
    "size_gb": 9.6,
    "family": "gemma4",
    "capability": "chat",
    "ram_multiplier": 1.5,
    "enabled": false,
    "notes": "Confirmed hang on 11 GiB host (60s timeout, exceeds 14 GB requirement). Hard-blocked via enabled=false."
  },
  {
    "name": "llama3.1:8b",
    "size_gb": 4.9,
    "family": "llama3.1",
    "capability": "chat",
    "ram_multiplier": 1.5,
    "enabled": true,
    "notes": "Original hardcoded default. Slow (19.8s) but works; available if free RAM > 9.4 GB."
  }
],
"embed_model_pool": [
  {
    "name": "nomic-embed-text",
    "size_gb": 0.27,
    "family": "nomic",
    "capability": "embed",
    "ram_multiplier": 1.5,
    "enabled": true,
    "notes": "Fixed embedding model. Not RAM-selected; used by name."
  }
]
```

- **What will be updated/created:** 3 schema files.
- **Risks:** (a) Existing test suite may assert flat string `model_pool`. Mitigation: add JSON-Schema regression test asserting `model_pool[*].name` includes expected entries. (b) `enabled: false` enforcement depends on provider honoring it — see 5.6.C. (c) `family` enum is curated; new families require schema bump.
- **Future issues:** (a) `model_size_overrides` block to override `ollama list --json` size if it drifts from schema. (b) Per-project `model_pool` overrides via project_setup.json inheritance. (c) CI schema validation step.
- **Success criteria:** All 3 schema files validate; `model_pool` is the single source of truth; no model name string is hardcoded outside schema.
- **References:** [dcc_register_base.json:537](../../config/schemas/dcc_register_base.json), [dcc_register_setup.json:12-93](../../config/schemas/dcc_register_setup.json), [dcc_global_parameters.json:39](../../config/schemas/dcc_global_parameters.json), [agent_rule.md §2.7, §4.4](../../../agent_rule.md).

### 5.6.B — Memory-aware selector reading from schema (in `ai_ops_engine/core/engine.py::_run_provider`)

**Timeline:** 2026-06-09 (1 day)  
**Milestone:** Engine reads `model_pool` and `model_memory_headroom_gb` from resolved parameters (schema-driven) and picks the first `enabled` entry that fits free RAM.  
**Deliverables:**
- New helper `_select_model_by_memory(model_pool: list[dict], headroom_gb: float) -> Optional[str]` in `core/engine.py`:
  - **All inputs come from schema-resolved parameters** (no hardcoded sizes, families, or names).
  - Filters out entries where `entry["enabled"] is False`.
  - For each remaining entry, computes `required_gb = entry["size_gb"] * entry.get("ram_multiplier", 1.5)`.
  - Reads `psutil.virtual_memory().available / (1024**3)` at call time.
  - Returns `entry["name"]` of the first entry where `required_gb + headroom_gb ≤ available_gb`.
  - Returns `None` if no entry fits → caller falls back to `RuleBasedProvider` (already wired at `engine.py:156`).
- `core/engine.py::_run_provider` is refactored to:
  1. Read `model_pool` and `model_memory_headroom_gb` from `effective_parameters` (resolved by `BootstrapManager` from schema).
  2. If `ai_model` is explicitly set and its entry in `model_pool` is `enabled` and fits → use it (explicit user override wins).
  3. Otherwise, call `_select_model_by_memory()` to pick by RAM.
  4. Log decision + math at level 2 (debug).
- **What will be updated/created:** `core/engine.py` (add helper, refactor `_run_provider`).
- **Risks:** `psutil` not in `requirements.txt`. Mitigation: add as dependency; degrade to `os.sysconf('AVPHYS_PAGES')` if missing.
- **Future issues:** Could expose `selection_reason` enum in `AiInsight` for downstream UI.
- **Success criteria:** Unit test confirms correct model chosen for synthetic memory values using schema-defined `model_pool`:
  - 1.2 GB avail → `deepseek-coder:1.3b`
  - 3.0 GB avail → `qwen2.5-coder:3b` (first fit)
  - 9.5 GB avail → `llama3.2:3b` (schema default, first fit)
  - 0.5 GB avail → `None` → `RuleBasedProvider`
  - 9.5 GB avail with `gemma4:e4b.enabled=true` → still skipped (excluded by `enabled=false` default, defense in depth)
- **References:** [ai_ops_engine/core/engine.py:138](../../workflow/ai_ops_engine/core/engine.py), [ai_ops_engine/core/engine.py:150-156](../../workflow/ai_ops_engine/core/engine.py).

### 5.6.C — Ollama provider update: metadata-free (in `ai_ops_engine/providers/ollama_provider.py`)

**Timeline:** 2026-06-09 (same day as 5.6.B)  
**Milestone:** Provider contains no model-specific strings; all metadata flows from schema via the engine.  
**Deliverables:**
- **Remove `_DEFAULT_MODEL = "llama3.1:8b"`** from `ollama_provider.py:33`. The hardcoded default violates `agent_rule.md` §4.4 (schema-driven design). The provider's only default becomes "use whatever the engine passes in."
- `OllamaProvider.is_available()` — accepts an optional `model_pool: list[dict]` argument; if any `enabled` entry's name matches the requested model AND `psutil.virtual_memory().available` is less than `size_gb * ram_multiplier + headroom_gb` → return `False` (defense-in-depth memory check at the provider layer, complementing the engine selector).
- `OllamaProvider.__init__` — accept `model_metadata: dict | None = None` so the provider can log `family` / `capability` in `MILESTONE_AI_INSIGHT` for explainability — but **never uses it to make selection decisions**.
- **What will be updated/created:** `providers/ollama_provider.py`.
- **Risks:** Existing tests that pin `llama3.1:8b` as default will fail. Mitigation: update those tests to pass an explicit model name (per `agent_rule.md` §4.4, no implicit defaults allowed).
- **Future issues:** None for this phase.
- **Success criteria:** `grep -nE "llama|gemma|qwen|deepseek" workflow/ai_ops_engine/providers/ollama_provider.py` returns no model-name strings.
- **References:** [ai_ops_engine/providers/ollama_provider.py:33](../../workflow/ai_ops_engine/providers/ollama_provider.py), [agent_rule.md §4.4](../../../agent_rule.md).

### 5.6.D — Persistence extension (in `ai_ops_engine/persistence/run_store.py`)

**Timeline:** 2026-06-10 (1 day)  
**Milestone:** Memory-aware selection is auditable.  
**Deliverables:**
- `ai_runs` table (line 80) — add columns:
  - `free_ram_mb INTEGER`
  - `required_ram_mb INTEGER`
  - `selection_reason VARCHAR` (e.g., `schema_default`, `downgraded_for_memory`, `no_model_fits_fallback_rule_based`)
- Migration: `CREATE TABLE IF NOT EXISTS` style — append columns with defaults; or `ALTER TABLE` with try/except.
- **What will be updated/created:** `persistence/run_store.py`, schema bootstrap.
- **Risks:** Existing `dcc_runs.duckdb` files miss columns. Mitigation: detect + migrate on startup.
- **Future issues:** Could add a `model_pool_used` JSON column for full transparency.
- **Success criteria:** New runs record all 3 fields; old runs continue to load.
- **References:** [ai_ops_engine/persistence/run_store.py:80](../../workflow/ai_ops_engine/persistence/run_store.py).

### 5.6.E — UI alignment (Phase 10 collaboration)

**Timeline:** 2026-06-10–11 (notify Phase 10 owner; no direct edits to UI in this phase)  
**Milestone:** UI's `GET /api/tags` dropdown continues to show all installed models; selected model is reflected in KPI tiles.  
**Deliverables:** Cross-link in `workplan/ui_design/web_interface/web_interface_workplan.md` to flag that pipeline's selected model is now `llama3.2:3b` by default (was `llama3.1:8b`).
- **What will be updated/created:** Reference link only (no UI code changes).
- **Risks:** None significant.
- **Future issues:** Phase 10.5+ may want to surface "selected by memory-aware selector" badge in chat header.
- **Success criteria:** UI continues to function; default model name shown in dashboard updates after next pipeline run.
- **References:** [workplan/ui_design/web_interface/web_interface_workplan.md:1210](../ui_design/web_interface/web_interface_workplan.md).

### 5.6.F — Test strategy + report (per Section 9)

**Timeline:** 2026-06-12  
**Milestone:** Phase 5.6 implementation signed off.  
**Deliverables:**
- `phase5_test_strategy.md` — add test cases TC-5.6.1 through TC-5.6.5 (see Success Criteria).
- `reports/phase5.6_report.md` — template per Section 9.2: title, document ID, version, index, objective, methodology, phases, results, recommendations, lessons learned.
- **What will be updated/created:** `phase5_test_strategy.md`, `reports/phase5.6_report.md`.
- **Risks:** Test environment must have Ollama running with at least `llama3.2:3b` + `deepseek-coder:1.3b` installed.
- **Future issues:** CI integration of memory-mocked selector tests.
- **Success criteria:** All TC-5.6.x PASS.
- **References:** [agent_rule.md §9](../../../agent_rule.md#section-9-reports-for-workplans).

## 5.6.7 Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `psutil` not in `requirements.txt` | Med | Low | Add to requirements; degrade to `os.sysconf` if missing |
| `gemma4:e4b` already pinned in some user config | Low | Med | Excluded from default `model_pool`; warn at startup if user overrides |
| Existing tests pin `llama3.1:8b` | Med | Low | Preserve as `_DEFAULT_MODEL` fallback; log deprecation |
| DuckDB migration breaks existing DBs | Low | Med | Try/except `ALTER TABLE`; fallback to fresh `CREATE TABLE` |
| UI shows stale model name after pipeline run | Low | Low | Phase 10 already polls `/api/tags` every 20s |

## 5.6.8 Future Issues

- Per-pipeline memory budget overrides (e.g., `--max-ram-gb` CLI flag).
- `model_pool` validated against `/api/tags` at startup, with warning if any model missing.
- Auto-embed of memory snapshot in `ai_insight_report.md` for explainability.
- Phase 10.5+ UI badge: "Selected by memory-aware selector".

## 5.6.9 Success Criteria

- [ ] `model_entry` definition added to `dcc_register_base.json#definitions` and validates.
- [ ] `model_pool`, `model_memory_headroom_gb`, `embed_model_pool` declared in `dcc_register_setup.json` properties; values in `dcc_global_parameters.json`.
- [ ] Each `model_pool` entry contains `name`, `size_gb`, `family`, `capability`, `ram_multiplier`, `enabled`, `notes`.
- [ ] `gemma4:e4b` has `enabled: false` in schema; selector never selects it.
- [ ] **Provider code is metadata-free**: `grep -nE "llama|gemma|qwen|deepseek|nomic" workflow/ai_ops_engine/providers/ollama_provider.py` returns no model-name strings.
- [ ] `_DEFAULT_MODEL = "llama3.1:8b"` removed from `ollama_provider.py`.
- [ ] Selector picks `llama3.2:3b` on 9.5 GB available host (using schema-defined `size_gb`).
- [ ] Selector downgrades to `deepseek-coder:1.3b` on 1.5 GB simulated available.
- [ ] Selector returns `None` and engine uses `RuleBasedProvider` when no model fits.
- [ ] Explicit `ai_model` override (CLI or schema) wins when its entry is `enabled` and fits.
- [ ] `ai_runs.duckdb` new rows contain `model_used`, `model_family`, `model_capability`, `free_ram_mb`, `required_ram_mb`, `selection_reason`.
- [ ] All existing tests still pass; new TC-5.6.1 → TC-5.6.6 PASS.
- [ ] `reports/phase5.6_report.md` generated and cross-linked.

## 5.6.10 References

- [agent_rule.md §4 Module Design, §8 Workplan, §9 Reports](../../../agent_rule.md)
- [dcc_register_base.json](../../config/schemas/dcc_register_base.json) — `dcc_parameter_entry` definition (line 537)
- [dcc_global_parameters.json](../../config/schemas/dcc_global_parameters.json) — `ai_model` value (line 39)
- [dcc_engine_pipeline.py:307-339](../../dcc_engine_pipeline.py) — `_run_ai` step in pipeline
- [ai_ops_engine/core/engine.py](../../workflow/ai_ops_engine/core/engine.py) — provider selection logic
- [ai_ops_engine/providers/ollama_provider.py](../../workflow/ai_ops_engine/providers/ollama_provider.py) — Ollama adapter
- [ai_ops_engine/persistence/run_store.py](../../workflow/ai_ops_engine/persistence/run_store.py) — DuckDB schema (line 80)
- [workplan/ui_design/web_interface/web_interface_workplan.md](../ui_design/web_interface/web_interface_workplan.md) — Phase 10 UI alignment
- [log/issue_log.md](../../../log/issue_log.md) — Issue LOG-003 (gemma4 hang, hardcoded default)

---

**Approval requested from:** Project Lead (Franklin Song)  
**Approval date:** Pending  
**Implementation may begin only after explicit approval per `agent_rule.md` Section 1 ("always plan and wait for approval to make changes").**
