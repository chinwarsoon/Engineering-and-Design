# Phase 3 Issue Log

**Project**: Engineering Knowledge System (EKS)  
**Location**: `eks/log/phase3/p3_issue_log.md`  
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
| Deferred (study/review/planned) | 🔷 | 0 |
| Deferred | ⏸️ | 4 |
| In Progress | ⏳ | 0 |
| Won't Implement | ⛔ | 0 |
| Open (partial) | 🔶 | 0 |
| **Total** | | **4** |

---

## Priority Resolution Sequence

Issues below are ordered by resolution priority for Phase 3 completion. Each group should be resolved before moving to the next.

| Seq | Priority | Issue IDs | Count | Theme |
| :-: | :------: | :-------- | :---: | :---- |
| **1** | 🔴 P0 — Immediate | I009 | 1 | **Pre-ingestion metadata extraction** — 572 TWRP documents not registered, 7 components missing |
| **2** | 🟠 P1 — This Sprint | I015, I228 | 2 | **Asset integration** — DGN parser, asset schema runtime integration |
| **3** | 🟡 P1 — This Sprint | I020, I021 | 2 | **Datadrop validation** — column range coverage, data incompleteness handling |

> **Total: 4 issues** (0 critical, 2 high, 2 medium, 0 low, 0 deferred)

---

## Issue Log Table

| ID | Date | Phase | Severity | Title | Description | Status | Tasks | Resolution |
| :- | :--- | :---- | :------: | :---- | :---------- | :----: | :---- | :--------- |
| I009 | 2026-06-19 | Phase 3 Prep | 🟠 High | Pre-ingestion metadata extraction gap — 572 TWRP documents not registered | Document registry contains 7 test records only; 0 of 572 real TWRP documents ingested. 7 components missing: (1) FilenameParser; (2) CoverSheetParser; (3) ScannedPDFHandler; (4) DatadropCrossRef; (5) WSD11 project config; (6) Bulk ingestion script; (7) Extraction confidence scoring. | ⏸️ Deferred | — | Close: Deferred to Phase 3 evaluation as sub-phase workplan. Blocks Phase 3 bulk ingestion. See Appendix B B6.3. |
| I015 | 2026-06-23 | Phase 1 | 🟡 Medium | DGN parser stub — 48 CAD files unparseable | DGNParserStub returns "Format supported - Implementation Pending" for all .dgn files. 48 DGN files identified. | 🔴 Open | — | Close: Phase 3: Evaluate OpenDesign SDK, LibreCAD, or commercial parser. Mitigated by ManualReviewManager. |
| I020 | 2026-06-23 | Phase 1 | 🟡 Medium | Datadrop column range (33–112) — fragment mapping coverage | 7 datadrop sheets have varying column counts (33–112). Some columns unique to specific asset types. | 🔴 Open | — | Close: Phase 3: Validate fragment coverage against all 7 sheets. |
| I021 | 2026-06-23 | Phase 1 | 🟠 High | 22–64% data incompleteness across datadrop sheets | Equipment 59.9% pending, Inline Component 44.1%, Instrument 63.5%, Motor 45.1%, Pipeline 22.8%, etc. | 🔴 Open | — | Close: Phase 3: Asset loader must handle null fields gracefully. Health scoring applied per-asset. |
| I228 | 2026-07-20 | Phase 1 | 🟠 High | Asset schema (Appendix A) has zero runtime pipeline integration | eks_asset schemas exist and validate. No pipeline phase loads asset data, applies fragment composition, or validates records. | 🔴 Open | — | Close: Phase 3 plans asset loaders. Phase 1 has no asset extraction engine — risks Phase 3 being blocked. |
