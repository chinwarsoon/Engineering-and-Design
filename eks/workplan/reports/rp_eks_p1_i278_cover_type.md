# EKS Phase 1 — Cover-Type Absence Branching (I278) — Test Report

**Report ID**: RP-EKS-P1-I278
**Current Version**: 1.0
**Status**: ✅ COMPLETE
**Last Updated**: 2026-08-04
**Parent Workplan**: [phase_1_foundation_workplan.md](../phase_1_foundation_workplan.md) — I278 / T1.211–T1.212 (depends on I279 / T1.216 template registry)

## 1. Test Objective

Verify that parsing branches on the template's `cover_type`: a no-cover (`C`) template — e.g. `twrp_spec_c` for SPC/CL/BQ — must skip cover-page detection and `cover_page_element`-based columns (relying on parser metadata + file properties), while cover-bearing templates (A/B/D/E) process them normally.

## 2. Scope

- **Cover-type is a template property, format-independent** (I279 carrier `document_templates[template_id].cover_type`). Only the *detection mechanism* differs between native (embedded structure) and PDF print (page-1 OCR) — the branching decision is identical.
- **Detection skip:** `StructureDetector.detect(..., skip_cover_page=True)` does not emit a `cover_page` element.
- **Method gating (reuses I277):** `EKSColumnProcessor.resolve_cover_type(document_type)` resolves the binding's template cover_type from the injected `document_templates`; `resolve_extraction_methods()` discards `cover_page_element` from the admitted method set when cover_type is `C`. Both direct `cover_page_element` columns (`_extraction_applies`) and priority-chain cover sources (`_resolve_priority_chain`) are gated out by the existing I277 mechanism.
- **Orchestrator:** `_process_file` resolves cover_type and passes `skip_cover_page=(cover_type == "C")` into `detect()`.
- **SSOT:** no hardcoded cover types — the carrier template registry is the single source. Unknown/absent template id defaults to `C` (safe no-cover).

## 3. Files Modified

| File | Change |
| :--- | :----- |
| `eks/engine/core/structure_detector.py` | `detect()` gains `skip_cover_page` param — skips cover-page detection when set |
| `eks/engine/core/column_processor.py` | `resolve_cover_type()` new method; `resolve_extraction_methods()` discards `cover_page_element` for cover_type `C`; `document_templates` injected via `from_doc_config()` (rev 0.5) |
| `eks/engine/core/pipeline_orchestrator.py` | `_process_file` resolves cover_type and passes `skip_cover_page` to the detector |
| `eks/test/test_column_processing.py` | `TestCoverTypeBranching` — 9 new tests |
| `eks/test/test_t132_modules.py` | `TestStructureDetector.test_skip_cover_page_no_cover_template` |

## 4. Test Execution Summary

| Test group | Coverage | Result |
| :--------- | :------- | :----: |
| cover_type resolution | cover-bearing (A) / no-cover (C) / unknown-default (C) | ✅ PASS |
| method gating | C discards `cover_page_element`; A keeps it | ✅ PASS |
| direct cover column | skipped for C / runs for A | ✅ PASS |
| priority-chain cover source | skipped for C; remaining source wins | ✅ PASS |
| parser_metadata preservation | no-cover doc still runs parser_metadata where format admits | ✅ PASS |
| detector skip | `skip_cover_page=True` emits no `cover_page` element | ✅ PASS |

**Result**: 118/118 focused tests passed (test_column_processing + test_t132_modules). Full suite **532 passed / 4 failed** — the 4 pre-existing baseline failures unchanged (bootstrap catalog, bootstrap readiness, doc-type enum ontology, folder error code); `522 → 532` (+9 I278 tests), zero new regressions.

## 5. Logs Updated

- `eks/log/phase1/p1_issue_log.md` — I278: 🔴 Open → 📐 Aligned; v61 → v62; status summary recounted (aligned 87→88, open 10→9); Priority Resolution Sequence row for I278 removed (outstanding 25→24)
- `eks/log/phase1/p1_task_log.md` — T1.211–T1.212: 🔷 Planned → ✅ COMPLETE; status summary recounted (complete → 383, planned 29→27)
- `eks/log/phase1/p1_update_log.md` — U258 added
- `eks/log/phase1/p1_test_log.md` — TL040 added

## 6. Design Notes

- **Reuses the I277 gate** rather than introducing a parallel branching path. Removing `cover_page_element` from the admitted extraction-method set is the single control that gates both direct columns and priority-chain sources — one mechanism, no duplicated logic.
- **SSOT via carrier.** Cover type is never hardcoded; it is read from `document_templates[template_id].cover_type` (projected from `eks_document_type_schema.json` v2.0.0 by SchemaLoader, I279). `resolve_cover_type` defaults unknown/missing bindings to `C` — the safe direction (a doc without a declared cover is treated as cover-less).
- **HealthScorer untouched.** Scoring already tolerates cover absence (`_score_source_quality` / `COVER_TYPE_SOURCE_SCORES`), so I278 only branches extraction, per the approved scope.
- Format-independence verified: the SPC binding (`twrp_spec_c`, cover `C`) gates `cover_page_element` in both the print (technip_pdf) and hypothetical native cases; the DWG binding (`twrp_drawing`, cover `A`) admits it in both.

## 7. Recommendations

1. The `classify_cover_type()` runtime heuristic (structure_detector.py:246) remains available for diagnostics; consider surfacing the resolved cover_type in Phase B telemetry for observability of which documents were treated as no-cover.
2. When the P1 queue moves to UI work, the cover-type branch should be reflected in the document detail view (e.g. a "no cover expected" indicator for SPC/CL/BQ).