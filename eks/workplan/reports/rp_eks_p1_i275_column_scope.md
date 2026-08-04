# EKS Phase 1 — Per-Concept Column Scope (I275) — Test Report

**Report ID**: RP-EKS-P1-I275
**Current Version**: 1.0
**Status**: ✅ COMPLETE
**Last Updated**: 2026-08-04
**Parent Workplan**: [phase_1_foundation_workplan.md](../phase_1_foundation_workplan.md) — I275 / T1.203–T1.205 (depends on I279 / T1.214 for concepts/bindings)

## 1. Test Objective

Verify that the `column_processing` registry is scoped by **document type concept × format category**, so a column that is only meaningful for a given document type or only populateable from a native (non-PDF) delivery is filtered accordingly during column processing. This closes the "per-concept column scope" gap in the native/PDF-print model.

## 2. Scope

- **Schema**: `eks/config/schemas/eks_doc_base_schema.json` v1.11.0 → v1.12.0 — `column_processing_entry_def` extended with:
  - `applies_to_document_types` — array of `$ref` to `document_type_concept_def/properties/concept_id`; **absent = applies to all concepts**.
  - `native_only` — boolean; when true the column can only be populated from a native (non-print) delivery.
- **Code** (T1.204): `common/library/column_processor/base.py` — new `_applies(col_name, col_entry, context)` guard invoked inside `BaseColumnProcessor.process()` after the `is_calculated` filter; skips a column when `applies_to_document_types` excludes the resolved `concept_id`, or when `native_only` conflicts with `format_category == "print"`. `eks/engine/core/column_processor.py` — `EKSColumnProcessor.__init__` accepts `document_type_registry`; new `resolve_scope(document_type)` (looks up the I279-projected `document_type_registry` → `{concept_id, format_category}`); `from_doc_config` passes the registry. `eks/engine/core/pipeline_orchestrator.py` — Phase B injects `concept_id` + `format_category` into the `process()` context.
- **Config** (T1.205): `eks/config/schemas/eks_doc_config.json` — 10 `embedded_*` columns flagged `native_only: true` (embedded_title/subject/created_date/modified_date/creator_app/producer/last_modified_by/keywords/sheet_count/revision_number); `total_sheets` scoped `applies_to_document_types: ["DRAWING"]`.
- **Tests**: new `TestDocumentTypeScopeFilter` in `eks/test/test_column_processing.py` (7 tests); version assertion updated in `eks/test/test_t132_modules.py`.

## 3. Test Execution Summary

| Test group | Coverage | Result |
| :--------- | :------- | :----: |
| native_only → print | column skipped when `format_category=print` | ✅ PASS |
| native_only → native | column included when native | ✅ PASS |
| applies_to excludes | DRAWING-only column skipped for SPECIFICATION | ✅ PASS |
| applies_to includes | DRAWING-only column included for DRAWING | ✅ PASS |
| absent scope keys | no `applies_to_document_types` / `native_only` → applies to all | ✅ PASS |
| unresolved scope | no concept/format in context → unrestricted (never raises) | ✅ PASS |
| EKS resolve_scope | `from_doc_config` carries projected registry; `resolve_scope` maps code → concept+format | ✅ PASS |
| Full suite | `eks/test/` — 498 passed / 4 pre-existing (unchanged) | ✅ PASS |

**Result**: 7/7 new scope tests passed; `test_column_processing.py` 32/32; combined column+t132+ssot 112/112. Full suite **498 passed / 4 failed** — the 4 pre-existing baseline failures unchanged (bootstrap catalog, bootstrap readiness, doc_type ontology, folder error code); `491 → 498` (I279 close) then `+7` I275 tests, zero new regressions.

## 4. Files Modified

| File | Action |
| :--- | :----- |
| `eks/config/schemas/eks_doc_base_schema.json` | v1.11.0 → v1.12.0: `column_processing_entry_def` gains `applies_to_document_types` + `native_only` |
| `common/library/column_processor/base.py` | NEW `_applies()` guard in `BaseColumnProcessor.process()` |
| `eks/engine/core/column_processor.py` | `resolve_scope()` + `document_type_registry` injection via `from_doc_config` |
| `eks/engine/core/pipeline_orchestrator.py` | Phase B injects `concept_id` + `format_category` into process context |
| `eks/config/schemas/eks_doc_config.json` | 10 `embedded_*` `native_only: true`; `total_sheets` DRAWING-scoped |
| `eks/test/test_column_processing.py` | NEW `TestDocumentTypeScopeFilter` — 7 tests |
| `eks/test/test_t132_modules.py` | base schema version assertion 1.11.0 → 1.12.0 |

## 5. Logs Updated

- `eks/log/phase1/p1_issue_log.md` — I275: 🔴 Open → 📐 Aligned; v58 → v59; status summary recounted (aligned 84→85, open 13→12); Priority Resolution Sequence row for I275 removed (I276–I278 renumbered 5–7; outstanding 28→27)
- `eks/log/phase1/p1_task_log.md` — T1.203–T1.205: 🔷 Planned → ✅ COMPLETE; status summary recounted (complete 373→376, planned 37→34)
- `eks/log/phase1/p1_update_log.md` — U255 added
- `eks/log/phase1/p1_test_log.md` — TL037 added

## 6. Design Notes

- **Unresolved scope is unrestricted.** If the process context lacks `concept_id`/`format_category`, `_applies()` returns True (never silently drops a column). Phase A/C leaf passes carry empty context → full column set, preserving I274 `COLUMN_ALLOWLIST` union invariant.
- **`embedded_*` columns are `native_only` by declaration** — they are populated by `FilePropertyExtractor` in the native path; the filter is the runtime guard and is exercised via tests on the calculated column path. SSOT for availability is the schema, not code.
- **I274 unaffected** — `COLUMN_ALLOWLIST` is untouched; per-type/per-format availability is handled entirely in processing scope.

## 7. Recommendations

1. When I276 (two-axis parser routing) lands, pass a real `project`-resolved context (not just document type) into `process()` so `applies_to_document_types` can be combined with project binding resources for full column-routing parity.
2. Consider extending `_applies()` to accept a project id/org for cross-project column availability, if ever needed beyond concept scope.
3. The pre-existing `test_doc_type_enum_matches_ontology` failure remains independently tracked; re-evaluate against the new enum mirror drift-guard introduced with I279.