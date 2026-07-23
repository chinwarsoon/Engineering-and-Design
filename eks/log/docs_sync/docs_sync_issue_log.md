# Docs Sync Issue Log

**Project**: Engineering Knowledge System (EKS)  
**Location**: `eks/log/docs_sync/docs_sync_issue_log.md`  
**Last Updated**: 2026-07-23 — v1 (Created from Phase 1 issue migration)

## Legend

### Status

| Marker | Status | Meaning |
|:------:|:-------|:--------|
| ✅ | Resolved | Fixed and verified; no remaining action |
| 🔴 | Open | Not yet addressed; active in queue |
| ⏳ | In Progress | Currently being worked on |
| ⏸️ | Deferred | Moved to a future phase |
| 🔷 | Deferred for further study | Marked resolved but has unresolved pending work |
| 🔷 | Deferred for further review | Requires debate/discussion before action can proceed |
| ⛔ | Won't Implement | Explicitly rejected or out of scope |
| 🔶 | Open (partial) | Open with partial progress or conditional resolution |
| 📐 | Aligned | Issue resolved AND workplan/docs updated to reflect the change |
| 🟢 | Approved | Tasks defined and approved; awaiting implementation |

### Severity

| Marker | Severity | Meaning |
|:------:|:---------|:--------|
| 🔴 | Critical | Blocks phase completion |
| 🟠 | High | Significant impact; workaround needed |
| 🟡 | Medium | Moderate impact; can proceed |
| 🟢 | Low | Minor, cosmetic, or non-blocking |
| 🔷 | Deferred | Moved to future phase; not currently blocking |

---

### Status Summary

| Status | Marker | Count |
| :----- | :----: | ----: |
| Resolved | ✅ | 0 |
| Aligned | 📐 | 0 |
| Open | 🔴 | 0 |
| Approved | 🟢 | 0 |
| Deferred (study/review/planned) | 🔷 | 8 |
| Deferred | ⏸️ | 0 |
| In Progress | ⏳ | 0 |
| Won't Implement | ⛔ | 0 |
| Open (partial) | 🔶 | 0 |
| **Total** | | **8** |

---

## Priority Resolution Sequence

Issues below are ordered by resolution priority for docs sync completion. Each group should be resolved before moving to the next.

| Seq | Priority | Issue IDs | Count | Theme |
| :-: | :------: | :-------- | :---: | :---- |
| **1** | 🔴 P0 — Immediate | I198, I203, I204, I205, I206, I207 | 6 | **Appendix D alignment** — taxonomy mismatch, column catalog, status lifecycle, error catalog names, category ranges, file I/O codes |
| **2** | 🟠 P1 — This Sprint | I208, I220 | 2 | **Folder restructuring** — domain subdirectories, ParserRouter location |

> **Total: 8 issues** (0 critical, 1 high, 6 medium, 1 low, 0 deferred)

---

## Issue Log Table

| ID | Date | Phase | Severity | Title | Description | Status | Tasks | Resolution |
| :- | :--- | :---- | :------: | :---- | :---------- | :----: | :---- | :--------- |
| I198 | 2026-07-19 | Phase 1 | 🟠 High | GAP-D4: Appendix D D5 data error codes (P1-R/V/C) never implemented — taxonomy mismatch | Appendix D defines 8 Phase 1 data error codes. None exist in eks_error_config.json. Different taxonomy in actual config. | 🔷 Deferred for further review | — | Close: Debate: docs-sync strategy — update docs to match code (code is SSOT). No code changes needed. Deferred pending docs-sync phase. |
| I203 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-D9: Appendix D D7.1 column catalog stale (25 vs. 54+) | Appendix D lists 25 columns, 18 scorable. Actual schema has 54+ columns. | 🔷 Deferred for further review | — | Close: Debate: update Appendix D D7.1 to reflect 54+ columns with 39 scorable. Deferred pending docs-sync phase. |
| I204 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-D10: Appendix D D8 status lifecycle not in code | Appendix D defines 4-state lifecycle NEW→EXTRACTED→REGISTERED→VERIFIED. Code uses extract_status values. | 🔷 Deferred for further review | — | Close: Debate: update Appendix D D8 to document code's actual extract_status model. Deferred pending docs-sync phase. |
| I205 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-D11: System error catalog name mismatches | Appendix D names swapped vs actual config at same codes. | 🔷 Deferred for further review | — | Close: Debate: update Appendix D D4 to match actual config (SSOT). Deferred pending docs-sync phase. |
| I206 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-D12: S-D Database category (0500–0599) relocated to S-A AI services | Appendix D reserves 0500–0599 for Database errors. Config assigns 05xx to AI services. | 🔷 Deferred for further review | — | Close: Debate: update Appendix D D4.3 range allocation to match actual config. Deferred pending docs-sync phase. |
| I207 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-D13: Appendix D file I/O codes (0207–0212) + config codes (0309–0311) not implemented | Appendix D lists 12 file I/O codes but config has 6. 11 config codes but config has 8. | 🔷 Deferred for further review | — | Close: Debate: update Appendix D D4 to document actual config ranges. Deferred pending docs-sync phase. |
| I208 | 2026-07-19 | Phase 1 | 🟠 High | GAP-A1: Folder structure — 6/7 domain subdirectories missing; all code flat in core/ | Appendix F proposes 7 domain subdirectories. All 24 modules live in engine/core/ flat. | 🔷 Deferred for further review | T1.99.190 | Close: Debate: __init__.py stubs created in domain folders. Full migration deferred — 50+ import sites would break. Re-evaluate when multi-engine isolation needed. |
| I220 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A13: ParserRouter lives in parsers/ not router/ per Appendix F | Appendix F proposes engine/router/. Current code has ParserRouter at engine/parsers/parser_router.py. | 🔷 Deferred for further review | T1.99.190 | Close: Tied to broader folder restructuring (I208). Relocation will occur during full folder migration. |
