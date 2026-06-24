# EKS Workplan Remediation — Cross-Cutting Fixes

**Document ID**: WP-EKS-RM-001  
**Current Version**: 1.0  
**Status**: ✅ COMPLETE — All items implemented  
**Last Updated**: 2026-06-24  
**Parent Workplan**: [eks_system_workplan.md](eks_system_workplan.md)  

---

## 1. Revision Control & Version History

| Version | Date | Author | Summary |
| :------ | :--- | :----- | :------ |
| 1.0 | 2026-06-24 | opencode | Initial — all remediation items from system review |

---

## 2. Objective

Remediate all cross-cutting issues identified during the eks/workplan and AGENTS.md review. Fixes span 7 workplan files and address broken references, stale statuses, content gaps, and formatting inconsistencies.

---

## 3. Scope Summary

| ID | Category | Issue | Details | Status |
| :- | :------- | :---- | :------ | :----: |
| A1 | References | `agent_rule.md` → `AGENTS.md` | 7 files reference non-existent `agent_rule.md` (as markdown links, bold text, and inline references). Replace all with `AGENTS.md`. | ✅ |
| A2 | Paths | Linux absolute paths → relative | 7 files use `/home/franklin/dsai/...` absolute paths. Replace with repo-relative paths from `eks/workplan/`. | ✅ |
| A3 | Status | T1.33 stuck at 🔷 | `phase_1_foundation_workplan.md` T1.33 marked pending despite v2.2 confirming completion. | ✅ |
| B1 | Status | Master workplan DRAFT | `eks_system_workplan.md` header `DRAFT — PENDING APPROVAL` despite Phase 1 complete and 4 other phases planned. | ✅ |
| B2 | Formatting | Section ordering reversed | `eks_system_workplan.md` §9 (References) appears after §11. Renumber to match index. | ✅ |
| B3 | History | Date ordering | `phase_2_chunking_embedding_workplan.md` v0.4 dated 2026-06-16 appears after v0.3 (2026-06-18). | ✅ |
| B4 | Status | Appendix D stale | `appendix_d_pipeline_messages_errors.md` status `🔷 PLANNED` — should be `✅ Implemented & Tested` (R51 is PASS). | ✅ |
| B5 | Content | Phase 3 placeholders | `phase_3_knowledge_graph_workplan.md` has `...` in §4, §10, §14 and missing §11–12. Fill content. | ✅ |
| B6 | Content | Phase 4 reranker vague | No decision criteria for rule-based vs cross-encoder reranker. | ✅ |
| B7 | Content | Phase 5 tech choice | Frontend technology (HTML/JS vs React) undecided. | ✅ |
| C1 | Content | Phase 4 eval metrics | Missing evaluation metrics (precision@k, recall@k) in success criteria. | ✅ |
| C2 | Content | Phase 5 auth | No mention of authentication/authorization or multi-user concerns. | ✅ |
| C3 | Content | Phase 5 Mermaid | Phase 5 pipeline diagram too simple (3 nodes). Expand with sub-components. | ✅ |

---

## 4. Files to Modify

| File | Items |
| :--- | :---- |
| `eks/workplan/eks_system_workplan.md` | A1, A2, B1, B2 |
| `eks/workplan/phase_1_foundation_workplan.md` | A1, A2, A3 |
| `eks/workplan/phase_2_chunking_embedding_workplan.md` | A1, A2, B3 |
| `eks/workplan/phase_3_knowledge_graph_workplan.md` | B5 |
| `eks/workplan/phase_4_retrieval_pipeline_workplan.md` | A1, A2, B6, C1 |
| `eks/workplan/phase_5_ui_integration_workplan.md` | A1, A2, B7, C2, C3 |
| `eks/workplan/appendix_d_pipeline_messages_errors.md` | B4 |

Note: `eks/log/update_log.md` and `eks/log/issue_log.md` are historical records — references to `agent_rule.md` in log entries are preserved as-is.

---

## 5. Implementation Phases

### Phase A — Critical Path (A1, A2, A3)
- Search & replace `agent_rule.md` → `AGENTS.md` (inline text and markdown links)
- Convert `/home/franklin/dsai/Engineering-and-Design/` absolute paths to repo-relative paths
- Fix T1.33 status from 🔷 to ✅

### Phase B — Housekeeping (B1–B5)
- Update master status, reorder sections
- Fix Phase 2 date ordering
- Update Appendix D status
- Fill Phase 3 placeholders

### Phase C — Content Gaps (B6, B7, C1–C3)
- Add reranker decision criteria to Phase 4
- Resolve frontend tech choice for Phase 5
- Add evaluation metrics to Phase 4
- Add auth note to Phase 5
- Expand Phase 5 Mermaid diagram

---

## 6. Dependencies

- None — all edits are to workplan documents only; no code, schema, or test changes

## 7. Success Criteria

- [x] Zero references to `agent_rule.md` in any active workplan document
- [x] Zero `/home/franklin/` absolute paths in any active workplan document
- [x] T1.33 status corrected to ✅
- [x] Master workplan status reflects accurate phase state
- [x] All section ordering consistent with table of contents
- [x] All placeholders (`...`) in Phase 3 resolved
- [x] Appendix D status matches actual implementation state
- [x] All decision points (reranker, frontend) resolved in text
- [x] Evaluation metrics added to Phase 4 success criteria
- [x] Auth considerations noted in Phase 5
- [x] Phase 5 Mermaid diagram expanded with sub-components
- [x] No regressions to existing content

---

## 8. References

1. [eks_system_workplan.md](eks_system_workplan.md)
2. [phase_1_foundation_workplan.md](phase_1_foundation_workplan.md)
