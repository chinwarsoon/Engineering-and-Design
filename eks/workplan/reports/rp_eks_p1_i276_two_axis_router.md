# EKS Phase 1 — Two-Axis Parser Routing (I276) — Test Report

**Report ID**: RP-EKS-P1-I276
**Current Version**: 1.0
**Status**: ✅ COMPLETE
**Last Updated**: 2026-08-04
**Parent Workplan**: [phase_1_foundation_workplan.md](../phase_1_foundation_workplan.md) — I276 / T1.206–T1.208 (depends on I279 / T1.214 for `default_parsing_profile`)

## 1. Test Objective

Verify that parser selection is routed along **two axes** so different document types (and native vs PDF-print deliveries of the same document) use genuinely different parsing processes, instead of resolving solely by file extension. The routing unit is the **project binding**.

## 2. Scope

- **Axis 1 — profile (document type → parsing profile):** `document_type` (project-local code) → `default_parsing_profile` (declared on the binding in the I279 carrier) → profile parser_class. The binding profile is carried into the flat `document_type_registry` runtime projection.
- **Axis 2 — reader (file_type):** the profile's `parser_class`, admitted only when its `supported_extensions` accept the file (or when the profile is the PDF reader for print bindings); otherwise falls back to the file-type-only `file_type_registry` / `ParserFactory` mapping.
- **Fallback:** a document type with no binding profile, an unknown code, or a profile that rejects the file_type degrades to file-type-only routing (never fails closed).
- **Native readers (GAP-N4):** `technip_dwg` / `technip_dgn` / `technip_xlsx` parse profiles wired to DWGParserStub / DGNParserStub / XLSXParser so declared native file types have real readers.

## 3. Files Modified

| File | Change |
| :--- | :----- |
| `eks/config/schemas/eks_doc_base_schema.json` | `document_type_entry_def` extended with `default_parsing_profile` (validates the projected flat registry; base v1.12.0) |
| `eks/engine/core/schema_loader.py` | `_derive_doc_type_projection()` carries `default_parsing_profile` into the flat `document_type_registry` |
| `eks/engine/parsers/parser_router.py` | `resolve_parsing_profile()` (axis 1) + `resolve_reader()` (axis 2); `route()` accepts/records `document_type` and prefers the profile reader |
| `eks/engine/core/pipeline_orchestrator.py` | `_process_file()` passes the registry/Phase-A `document_type` into `route()` |
| `eks/test/test_parser_two_axis_routing.py` | NEW — 14 tests |

## 4. Test Execution Summary

| Test group | Coverage | Result |
| :--------- | :------- | :----: |
| Profile resolution | DWG→technip_pdf, CAD→technip_dwg, unknown/missing→None | ✅ PASS |
| Two-axis reader | native dwg/CAD→DWGParserStub; pdf print→PDFParser; unsupported ext→fallback | ✅ PASS |
| route() integration | unknown-type failure preserved; document_type carried in result | ✅ PASS |
| §24 capability consistency | every binding profile referenced exists; supported_extensions vs expected_file_types; 3 native profiles present | ✅ PASS |

**Result**: 14/14 new tests passed; existing 5 router tests in `test_phase1.py` + runtime-slice router test still green (factory/legacy modes preserved). Full suite **512 passed / 4 failed** — the 4 pre-existing baseline failures unchanged (bootstrap catalog, bootstrap readiness, doc-type enum ontology, folder error code); `498 → 512` (+14 I276 tests), zero new regressions.

## 5. Logs Updated

- `eks/log/phase1/p1_issue_log.md` — I276: 🔴 Open → 📐 Aligned; v59 → v60; status summary recounted (aligned 85→86, open 12→11); Priority Resolution Sequence row for I276 removed (I277–I278 renumbered 5–6; outstanding 27→26)
- `eks/log/phase1/p1_task_log.md` — T1.206–T1.208: 🔷 Planned → ✅ COMPLETE; status summary recounted (complete 376→379, planned 34→31)
- `eks/log/phase1/p1_update_log.md` — U256 added
- `eks/log/phase1/p1_test_log.md` — TL038 added

## 6. Design Notes

- **Never fails closed** — `resolve_reader()` returns `None` (not an error) when no binding profile matches; `route()` then uses the existing file-type-only factory/legacy path. The `test_route_unknown_type_still_fails` test confirms unknown types still surface the original "No parser registered" failure.
- **Default profile is a routing hint, not a hard constraint.** An unsupported extension falls back rather than raising, keeping the reader mapping authoritative for capability checks (per `parsing_profile_def`).
- The native reader *profiles* are declared and wired in config; reader *implementations* remain stubs (DWG/DGN) — consistent with the I279 report §7 caveat that GAP-N4-native-parser code is not yet delivered. This issue delivers the routing, not the readers.

## 7. Recommendations

1. Before treating native DWG/DGN as fully supported, deliver real DWG/DGN reader implementations (GAP-N4) — the profiles exist but the classes are stubs.
2. When I277 (extraction-method gating) lands, combine binding `format_category` ∩ template detection ∩ profile `extraction_methods` with the resolved profile from `resolve_reader()` for unified gates.
3. Consider threading a resolved project-binding context (not just doc_type) through the router when I277/I278 add template/cover branching.