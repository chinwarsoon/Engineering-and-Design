# Phase 2 Issue Log

**Project**: Engineering Knowledge System (EKS)  
**Location**: `eks/log/phase2/p2_issue_log.md`  
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
| Deferred (study/review/planned) | 🔷 | 21 |
| Deferred | ⏸️ | 1 |
| In Progress | ⏳ | 0 |
| Won't Implement | ⛔ | 0 |
| Open (partial) | 🔶 | 1 |
| **Total** | | **23** |

---

## Priority Resolution Sequence

Issues below are ordered by resolution priority for Phase 2 completion. Each group should be resolved before moving to the next.

| Seq | Priority | Issue IDs | Count | Theme |
| :-: | :------: | :-------- | :---: | :---- |
| **1** | 🔴 P0 — Immediate | I016, I019 | 2 | **Folder hierarchy + project codes** — FileScanner extension, FilenameParser enhancement |
| **2** | 🟠 P1 — This Sprint | I182, I183, I184, I185, I186 | 5 | **File registration improvements** — hash computation, composite-key check, UUID migration |
| **3** | 🟡 P1 — This Sprint | I176, I177, I178, I179, I180, I181 | 6 | **Metadata gaps Phase 2** — asset registry, CAD parser, size detection, review UI, workflow engine, scheduling |
| **4** | 🟢 P2 — Phase 2 Close | I187, I216, I220, I223 | 4 | **Cross-project abstractions + deferred items** — common/library extraction, checkpoint/resume, folder restructuring, per-engine CLI |
| **5** | 🔶 P3 — Phase 3 Prep | I078 | 1 | **Common-lib wiring** — wire EKS engine modules to shared common.library.* packages |
| **6** | ⏸️ P4 — Post Phase 1.2 | I054 | 1 | **Deployment guide** — eks/deploy.py stdlib-only script |

> **Total: 23 issues** (0 critical, 0 high, 17 medium, 6 low, 0 deferred)

---

## Issue Log Table

| ID | Date | Phase | Severity | Title | Description | Status | Tasks | Resolution |
| :- | :--- | :---- | :------: | :---- | :---------- | :----: | :---- | :--------- |
| I016 | 2026-06-23 | Phase 1 | 🟢 Low | Revision folder hierarchy inconsistency | R0 revisions use 3-subfolder structure; R1+ place files directly. Some submittals have no revision folders. | 🔴 Open | — | Close: Phase 2: Extend FileScanner to traverse inconsistent folder hierarchies. |
| I019 | 2026-06-23 | Phase 1 | 🟡 Medium | Two project codes (131101 vs 131242) — metadata normalization | project_spec/ uses 131101; design_doc/ uses 131242. Both valid WSD11 project documents. | 🔴 Open | — | Close: Phase 2: FilenameParser must extract project_code from document number pattern. |
| I054 | 2026-07-02 | All | 🟢 Low | No restricted-machine deployment guide | No equivalent to code_tracer download_release.py. Must clone repo and build conda env. | ⏸️ Deferred | — | Close: Post Phase 1.2 migration. Create eks/deploy.py — stdlib-only script. Reference code_tracer R7 pattern. |
| I078 | 2026-07-08 | Phase 1 / Master | 🟡 Medium | Shared common-library structure documented but not yet wired into EKS runtime | common/library exists but EKS runtime uses local implementations, not shared packages. | 🔶 Open (partial) | T1.74/T1.99.35 | Close: Track follow-on task: wire EKS engine modules to shared common.library.* packages. |
| I176 | 2026-07-19 | Phase 2 | 🟢 Low | Metadata gap (Phase 2, 1 of 6): references_assets blocked on asset registry | Requires asset registry (future phase) — deferred. | 🔷 Deferred | — | Close: Logged for Phase 2. Blocked on asset registry implementation. |
| I177 | 2026-07-19 | Phase 2 | 🟢 Low | Metadata gap (Phase 2, 2 of 6): drawing_scale requires CAD parser | Blocked on future DGN/DWG parser implementation. | 🔷 Deferred | — | Close: Logged for Phase 2. Blocked on CAD parser (DGN/DWG). |
| I178 | 2026-07-19 | Phase 2 | 🟢 Low | Metadata gap (Phase 2, 3 of 6): paper_size requires size detection engine | Blocked on page/sheet size detection from PDF/DWG metadata. | 🔷 Deferred | — | Close: Logged for Phase 2. Blocked on size detection engine. |
| I179 | 2026-07-19 | Phase 2 | 🟢 Low | Metadata gap (Phase 2, 4 of 6): confidentiality requires review UI workflow | Requires manual review/classification UI — not built yet. | 🔷 Deferred | — | Close: Logged for Phase 2. Blocked on review UI workflow. |
| I180 | 2026-07-19 | Phase 2 | 🟢 Low | Metadata gap (Phase 2, 5 of 6): quality_status requires workflow engine | Requires quality review workflow engine — not implemented. | 🔷 Deferred | — | Close: Logged for Phase 2. Blocked on workflow engine. |
| I181 | 2026-07-19 | Phase 2 | 🟢 Low | Metadata gap (Phase 2, 6 of 6): review_due_date requires scheduling engine | Last of 6 Phase 2 gaps. Requires scheduling/workflow engine. | 🔷 Deferred | — | Close: Logged for Phase 2. Blocked on scheduling engine. |
| I182 | 2026-07-19 | Phase 1 | 🟡 Medium | File hash must be computed during scan and stored in scan result | Three-tier composite-key check (I185) depends on file_hash in scan result. Hash not yet wired into FileScanner. | 🔷 Planned | — | Close: Prerequisite for §46. Requires wiring FilePropertyExtractor into scan phase. |
| I183 | 2026-07-19 | Phase 1 | 🟡 Medium | Add file_hash column to documents table | FileScanner computes hash but documents table has no column to store it. | 🔷 Planned | — | Close: Add file_hash column to document_metadata_def; regenerate DDL; store in INSERT step. |
| I184 | 2026-07-19 | Phase 1 | 🟡 Medium | Diff logging on update_document_status() — no before/after comparison | update_document_status() updates rows blindly — no record of changes. | 🔷 Planned | T1.99.152 | Close: Query current row before UPDATE; compute field-level diff; log changes. Extract ChangeDetector to common/. |
| I185 | 2026-07-19 | Phase 1 | 🟡 Medium | Three-tier composite-key check (document_number, revision, file_hash) | Currently only checks document_number for duplicates — silent overwrite risk. | 🔷 Planned | T1.99.151 | Close: 3-tier gate comparing (document_number, revision, file_hash) before INSERT vs UPDATE vs skip. |
| I186 | 2026-07-19 | Phase 1 | 🟡 Medium | Change id from business-key to pure UUID | Current id = document_number + revision — INSERT OR REPLACE destructively overwrites. | 🔷 Planned | T1.99.150 | Close: id → UUID v4, pure INSERT, composite idx_doc_business_key for lookup. |
| I187 | 2026-07-19 | Phase 1 | 🟡 Medium | Extract 5 cross-project abstractions to common/library/ | compute_file_hash(), generate_synthetic_key(), file discovery, ChangeDetector, registration gate duplicated in EKS. | 🔷 Planned | T1.99.147–149 | Close: Extract each to common/library/utility/ and common/library/pipeline/. |
| I216 | 2026-07-19 | Phase 1 | 🟡 Medium | GAP-A9: Checkpoint/resume — checkpoint writes restored; full resume still deferred | save_checkpoint() writes per-phase checkpoints. --resume CLI not implemented. | 🔷 Deferred for further review | T1.99.187 | Close: Per-phase checkpoint writes restored. Full --resume <run_id> + cross-phase restoration deferred. |
| I220 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A13: ParserRouter lives in parsers/ not router/ per Appendix F | Appendix F proposes engine/router/. Current code has ParserRouter at engine/parsers/parser_router.py. | 🔷 Deferred for further review | T1.99.190 | Close: Tied to broader folder restructuring (I208). Relocation will occur during full folder migration. |
| I223 | 2026-07-19 | Phase 1 | 🟢 Low | GAP-A16: No per-engine CLI entry points per Appendix F §2.3.3 | Appendix F proposes independent engine CLI entry points. Only unified --phase flag exists. | 🔷 Deferred for further review | — | Close: Debate: --phase A/B/C flag provides equivalent isolation. Deferred to Phase 2 re-evaluation. |
