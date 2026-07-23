# Phase 5 Issue Log

**Project**: Engineering Knowledge System (EKS)  
**Location**: `eks/log/phase5/p5_issue_log.md`  
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
| Deferred (study/review/planned) | 🔷 | 2 |
| Deferred | ⏸️ | 0 |
| In Progress | ⏳ | 0 |
| Won't Implement | ⛔ | 0 |
| Open (partial) | 🔶 | 0 |
| **Total** | | **2** |

---

## Priority Resolution Sequence

Issues below are ordered by resolution priority for Phase 5 completion. Each group should be resolved before moving to the next.

| Seq | Priority | Issue IDs | Count | Theme |
| :-: | :------: | :-------- | :---: | :---- |
| **1** | 🔴 P0 — Immediate | I213, I224 | 2 | **Review workflow** — interactive review UI, Phase C write-back to registry |

> **Total: 2 issues** (0 critical, 0 high, 2 medium, 0 low, 0 deferred)

---

## Issue Log Table

| ID | Date | Phase | Severity | Title | Description | Status | Tasks | Resolution |
| :- | :--- | :---- | :------: | :---- | :---------- | :----: | :---- | :--------- |
| I213 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A6: ReviewManager exists but Phase C only flags docs — no review workflow triggered | Phase C queries flagged docs and exports CSV — never calls ReviewManager methods. Read-only. | 🔷 Deferred for further review | — | Close: ManualReviewManager initialized; auto-approved docs get recalculate_score(). Full interactive review deferred to Phase 5. |
| I217 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A10: UI contracts not implemented per Appendix F spec | Appendix F proposes HTTP endpoints for independent engine execution + DocumentSelectionContract / PipelineConfigContract. | 🔷 Deferred for further study | T1.99.188 | Close: UI contract stubs created. Full endpoint implementation deferred to Phase 5. |
| I224 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A17: Phase C is read-only — no mechanism to update review status back to registry | Phase C queries flagged docs and exports — never writes review_status, reviewed_by, reviewed_at back. | 🔷 Deferred for further review | T1.99.181 | Close: Debate: ManualReviewManager initialized; recalculate_score() used for clean docs. Full write-back deferred to Phase 5. |
