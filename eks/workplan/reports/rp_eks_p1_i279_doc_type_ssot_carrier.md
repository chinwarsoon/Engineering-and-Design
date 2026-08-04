# EKS Phase 1 — Document-Type SSOT Carrier (I279) — Test Report

**Report ID**: RP-EKS-P1-I279  
**Current Version**: 1.0  
**Status**: ✅ COMPLETE  
**Last Updated**: 2026-08-04  
**Parent Workplan**: [phase_1_foundation_workplan.md](../phase_1_foundation_workplan.md) — I279 / T1.213–T1.217 (enabling issue for I275–I278)

## 1. Test Objective

Verify that `eks_document_type_schema.json` v2.0.0 — restructured as a **three-section carrier** (`document_type_concepts` + `project_document_types` + `document_templates`) — becomes the single runtime SSOT for document types, eliminating the dead-duplicate violation (AGENTS.md §10/§16) where runtime consumers (`file_scanner.py`, `schema_loader.py`, `filename_parser.py`, `health_scorer.py`) read `eks_doc_config.json#/document_type_registry` instead of the schema file.

## 2. Scope

- **Schema**: `eks/config/schemas/eks_document_type_schema.json` v1.0.0 → v2.0.0 — three-section carrier (6 concepts, 2 project bindings / 15 local codes, 6 templates).
- **Base schema**: `eks/config/schemas/eks_doc_base_schema.json` v1.10.0 → v1.11.0 — `document_type_concept_def` / `project_document_type_def` / `document_template_entry_def` added; `document_type_entry_def` extended (concept_id/template/format_category/native_source).
- **Config**: `eks/config/schemas/eks_doc_config.json` v1.8.0 → v1.9.0 — `document_type_registry` array and `element_expectations` removed; `file_type_registry` gains `format_category` (pdf=print, dgn/docx/xlsx/dwg=native); native `parsing_profiles` added (`technip_dwg`/`technip_dgn`/`technip_xlsx` — GAP-N4); `document_type_schema_ref` added.
- **Setup schema**: `eks/config/schemas/eks_doc_setup_schema.json` v1.9.0 — `document_templates` + `document_type_schema_ref` properties; `element_expectations` re-keyed to template_id.
- **Code repoints** (T1.213): `schema_loader.py` — `_derive_doc_type_projection()` derives `document_type_registry` (15) + `document_templates` + `element_expectations` from the carrier at load; `_validate_doc_registries` rewritten to validate carrier sections. `health_scorer.py` — constructor accepts `document_templates`, derives expected-elements map (hardcoded map → `_EXPECTED_ELEMENTS_BY_TYPE_FALLBACK`, `"sections"` → `"section"`). `pipeline_orchestrator.py` — passes `document_templates` into HealthScorer. `file_scanner.py` / `filename_parser.py` / `column_processor` / `project_definition.py` read the derived registry (comments mark the carrier as SSOT source).
- **Tests**: new `eks/test/test_document_type_ssot.py` (14 tests); version assertions updated in `eks/test/test_t132_modules.py`.

## 3. Test Execution Summary

| Test group | Coverage | Result |
| :--------- | :------- | :----: |
| Carrier projection | v2.0.0 loads; projection produces a single parent-project binding (no resolution drift) | ✅ PASS |
| Format-category agreement | `file_type_registry.format_category` values agree with binding `format_category` | ✅ PASS |
| Enum mirror drift-guard | `document_type_code` enum == union of all `local_code` values across `project_document_types` | ✅ PASS |
| Registry-array removal | `eks_doc_config.json` no longer commits `document_type_registry` / `element_expectations` | ✅ PASS |
| Loader projection | SchemaLoader derives `document_type_registry` (15) / `document_templates` / `element_expectations` from carrier | ✅ PASS |
| §24 seven-source audit | `document_type_concepts` / `project_document_types` / `document_templates` / `file_type_registry` / `parsing_profiles` / `column_processing` / `document_type_code` enum | ✅ PASS |
| HealthScorer injection | `document_templates` injected → derived expected-elements map (not fallback) | ✅ PASS |
| Version assertions | `test_t132_modules.py` — doc config 1.9.0, doc base 1.11.0 | ✅ PASS |

**Result**: 14/14 new SSOT tests passed. Focused I279 suites green (test_phase1 + test_eks_engine_pipeline + test_runtime_slice_injection). Full suite **491 passed / 4 failed** — the 4 pre-existing baseline failures unchanged (verified via `git stash` baseline; `477 → 491`, zero new regressions).

## 4. Files Modified

| File | Action |
| :--- | :----- |
| `eks/config/schemas/eks_document_type_schema.json` | v1.0.0 → v2.0.0: three-section carrier |
| `eks/config/schemas/eks_doc_base_schema.json` | v1.10.0 → v1.11.0: 3 new defs + extended entry def + enum sync |
| `eks/config/schemas/eks_doc_config.json` | v1.8.0 → v1.9.0: registry arrays removed, format_category, native profiles, schema ref |
| `eks/config/schemas/eks_doc_setup_schema.json` | v1.9.0: document_templates + document_type_schema_ref + element_expectations re-key |
| `eks/engine/core/schema_loader.py` | `_derive_doc_type_projection()` + rewritten `_validate_doc_registries()` |
| `eks/engine/core/health_scorer.py` | `document_templates` injection + derived expected-elements map |
| `eks/engine/core/pipeline_orchestrator.py` | passes `document_templates` into HealthScorer |
| `eks/engine/core/file_scanner.py` | consumer comment: carrier is SSOT source |
| `eks/engine/core/project_definition.py` | consumer comment: carrier is SSOT source |
| `eks/test/test_document_type_ssot.py` | NEW — 14 SSOT tests |
| `eks/test/test_t132_modules.py` | version assertions updated (1.9.0 / 1.11.0) |

## 5. Logs Updated

- `eks/log/phase1/p1_issue_log.md` — I279: 🔴 Open → 📐 Aligned; v57 → v58; status summary recounted (resolved 142→143, aligned 83→84, open 14→13); Priority Resolution Sequence row for I279 removed (I275–I278 renumbered 5–8; outstanding 29→28)
- `eks/log/phase1/p1_task_log.md` — T1.213–T1.217: 🔷 Planned → ✅ COMPLETE; status summary recounted (complete 368→373, planned 42→37)
- `eks/log/phase1/p1_update_log.md` — U254 added
- `eks/log/phase1/p1_test_log.md` — TL036 added

## 6. Enabling Effect

I279 was the enabling issue for the native/PDF-print model (I275–I278). With the carrier implemented, the follow-up chains are unblocked and remain 🔷 Planned pending approval:

| Issue | Tasks | Status |
| :---- | :---- | :---- |
| I275 — Per-concept column scope | T1.203–T1.205 | 🔷 Planned |
| I276 — Two-axis parser routing | T1.206–T1.208 | 🔷 Planned |
| I277 — Extraction-method gating | T1.209–T1.210 | 🔷 Planned |
| I278 — Cover-page presence branching | T1.211–T1.212 | 🔷 Planned |

## 7. Recommendations

1. Before starting I276 (parser routing), verify native reader profiles (`technip_dwg`/`technip_dgn`/`technip_xlsx`) have real reader implementations — GAP-N4 reader code is not yet delivered.
2. When I276/I277 land, run a fresh §24 cross-source audit including the new `default_parsing_profile` on bindings.
3. The pre-existing `test_doc_type_enum_matches_ontology` failure should be re-evaluated against the new enum mirror drift-guard in `test_document_type_ssot.py`.
