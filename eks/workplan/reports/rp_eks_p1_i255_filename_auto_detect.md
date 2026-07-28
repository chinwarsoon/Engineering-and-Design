# EKS Phase 1 — FilenameParser Auto-Pattern Detection (I255) — Test Report

**Report ID**: RP-EKS-P1-I255  
**Current Version**: 1.0  
**Status**: ✅ COMPLETE  
**Last Updated**: 2026-07-28  
**Parent Workplan**: [phase_1_foundation_workplan.md](../phase_1_foundation_workplan.md) §71  

## 1. Test Objective

Verify that `FilenameParser` auto-detects the project code pattern per filename by trying each registered project code's pattern against the stem's first segment, falling back to `"*"` (0 segments) when no code matches. This unblocks I252 (Phase B identity field write-back) by enabling real Phase A identity field extraction.

## 2. Scope

- **Fix**: `eks/engine/core/filename_parser.py` rev 1.0.0 → 1.1.0 — replaced `project_code` param with `project_code_registry`; added `_detect_pattern(stem)` method; moved pattern selection from `__init__` to per-`parse()` call; fixed pre-existing finalization bug where 0-segment `"*"` pattern produced `parse_status="ok"` instead of `"unresolvable"`.
- **Call sites**: `eks/engine/core/file_scanner.py` rev 1.5.0 → 1.6.0, `eks/engine/core/pipeline_orchestrator.py` rev 0.7 → 0.8 — both derive `project_code_registry` from `filename_patterns` keys (minus `"*"`).
- **Tests**: 2 new regression tests in `eks/test/test_phase1.py`.

## 3. Test Execution Summary

| Test | Status |
| :--- | :----: |
| `test_filename_parser_auto_detects_131101_pattern` — `project_code_registry=["131101"]`, parses `"131101-AREA-SPC-CV-0001_rev01.pdf"`: asserts all 4 identity fields extracted (project_number=131101, area=AREA, document_type=SPC, discipline=CV, sequence_number=0001), document_number rejoin, revision=01, parse_status=ok | ✅ PASS |
| `test_filename_parser_falls_back_to_star_pattern` — `project_code_registry=["131101"]`, parses `"random_name.pdf"` (no known pattern): asserts all 5 identity fields `None`, document_number=full_stem, revision=00 (fallback), parse_status=unresolvable | ✅ PASS |

**Result**: 2/2 passed (326/331 full suite; 5 pre-existing unrelated failures).

## 4. Files Modified

| File | Action |
| :--- | :----- |
| `eks/engine/core/filename_parser.py` | rev 1.0.0 → 1.1.0: Added `_detect_pattern(stem)`, `_precompile_doc_type_codes()`; replaced `project_code` → `project_code_registry`; moved pattern selection to per-parse; fixed finalization bug |
| `eks/engine/core/file_scanner.py` | rev 1.5.0 → 1.6.0: Derives `project_code_registry` from `filename_patterns` keys |
| `eks/engine/core/pipeline_orchestrator.py` | rev 0.7 → 0.8: Derives `project_code_registry` from `filename_patterns` keys |
| `eks/test/test_phase1.py` | Added 2 regression tests for I255 |

## 5. Logs Updated

- `eks/log/phase1/p1_issue_log.md` — I255: 🔴 Open → ✅ Resolved
- `eks/log/phase1/p1_task_log.md` — T1.157, T1.158: 🔷 PLANNED → ✅ COMPLETE
- `eks/log/phase1/p1_update_log.md` — U222 added
- `eks/log/phase1/p1_test_log.md` — TL020 added
- `eks/workplan/phase_1_foundation_workplan.md` — v5.8→v5.9, §71 status updated to ✅
