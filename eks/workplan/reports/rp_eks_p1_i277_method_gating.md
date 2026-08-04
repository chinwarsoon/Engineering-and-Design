# EKS Phase 1 — Extraction-Method Gating (I277) — Test Report

**Report ID**: RP-EKS-P1-I277
**Current Version**: 1.0
**Status**: ✅ COMPLETE
**Last Updated**: 2026-08-04
**Parent Workplan**: [phase_1_foundation_workplan.md](../phase_1_foundation_workplan.md) — I277 / T1.209–T1.210 (depends on I279 / T1.214–T1.215 for `format_category` + profile resolution)

## 1. Test Objective

Verify that Phase B extraction is gated by the resolved parsing profile's declared `extraction_methods` intersected with the binding's `format_category`, so native formats run `parser_metadata` while PDF prints run only `cover_page_element` + file properties — eliminating the declarative-only gap where every handler ran for every document.

## 2. Scope

- **Gate location:** `BaseColumnProcessor._extraction_applies()` — a per-column capability gate invoked in `process()` alongside the I275 scope filter. When the context carries no `extraction_methods` capability set, the column is unrestricted (pre-I277 behaviour preserved).
- **Method resolution:** `EKSColumnProcessor.resolve_extraction_methods(document_type, format_category)` — resolves the binding's `default_parsing_profile` → its `extraction_methods`, then drops `parser_metadata` for `print` deliveries (flattened PDFs carry no embedded metadata).
- **Direct-handler gating:** `EKSColumnProcessor._required_extraction_method()` returns `calculation.type` for direct `parser_metadata` / `cover_page_element` columns; `priority_chain` columns are not blocked at the column level (their sources are filtered individually).
- **Source-level filtering:** `_resolve_priority_chain()` skips a source whose method is not in the capability set, so a chain keeps its remaining (admitted) sources.
- **Config injection:** `from_doc_config()` passes `parsing_profiles`; PipelineOrchestrator Phase B context gains `extraction_methods`.

## 3. Files Modified

| File | Change |
| :--- | :----- |
| `common/library/column_processor/base.py` | `_extraction_applies()` gate + `_required_extraction_method()` hook in the dispatch loop |
| `eks/engine/core/column_processor.py` | `resolve_extraction_methods()`, `_required_extraction_method()` override, priority-chain source filtering, `parsing_profiles` injection (rev 0.4) |
| `eks/engine/core/pipeline_orchestrator.py` | Phase B context gains `extraction_methods` |
| `eks/test/test_column_processing.py` | `TestExtractionMethodGating` — 10 new tests |

## 4. Test Execution Summary

| Test group | Coverage | Result |
| :--------- | :------- | :----: |
| Profile method resolution | print drops parser_metadata; native keeps it; no-profile → empty set | ✅ PASS |
| cover_page_element gate | skipped when not declared / runs when declared | ✅ PASS |
| parser_metadata gate | skipped for print / runs native | ✅ PASS |
| priority_chain | gated meta source skipped; remaining source wins | ✅ PASS |
| robustness | unknown method not fatal; no-capability context unrestricted | ✅ PASS |

**Result**: 10/10 new tests passed; all 32 prior column-processing tests + parser routing + runtime slice + t132 green. Full suite **522 passed / 4 failed** — the 4 pre-existing baseline failures unchanged (bootstrap catalog, bootstrap readiness, doc-type enum ontology, folder error code); `512 → 522` (+10 I277 tests), zero new regressions.

## 5. Logs Updated

- `eks/log/phase1/p1_issue_log.md` — I277: 🔴 Open → 📐 Aligned; v60 → v61; status summary recounted (aligned 86→87, open 11→10); Priority Resolution Sequence row for I277 removed (I278 → row 5; outstanding 26→25)
- `eks/log/phase1/p1_task_log.md` — T1.209–T1.210: 🔷 Planned → ✅ COMPLETE; status summary recounted (complete 379, planned 31→29)
- `eks/log/phase1/p1_update_log.md` — U257 added
- `eks/log/phase1/p1_test_log.md` — TL039 added

## 6. Design Notes

- **Never fails closed / never restricts absent capability.** A caller that does not supply `extraction_methods` in the context behaves identically to pre-I277 — the gate only fires when a capability set is provided.
- **Zero hardcoded method lists.** Method names (`parser_metadata`, `cover_page_element`) come from the `parsing_profiles` config `extraction_methods`; the gate SSOT is entirely schema/config.
- **priority_chain is filtered per-source, not per-column** — a chain like `project_title` (cover page > parser metadata > code lookup) keeps its file_property / code_to_title sources when `parser_metadata` is unavailable; only the gated source is skipped.
- Complements I275 (concept×format scope) and I276 (two-axis profile routing) — I277 consumes the resolved profile method set.

## 7. Recommendations

1. When I278 (cover-page presence branching) lands, the `cover_page_element` gate here should couple with the template `cover_type` so a cover-absent template skips the cover-page path entirely.
2. Consider surfacing the admitted extraction methods in Phase B telemetry for observability of which methods actually ran per document.