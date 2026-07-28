# EKS Update Log

**Project**: Engineering Knowledge System (EKS)  
**Location**: `eks/log/update_log.md`  
**Last Updated**: 2026-07-27 (U201 — I244 created: default-level verbosity noise audit. I242 level 0→1→2. 4 info→debug fixes, 1 error config severity change, 1 bare logger.error→MessageManager, 1 new test. Tasks T1.131–T1.133 added; T1.134–T1.137 planned.)

---

## Update History

| ID | Date | Phase | Task(s) | Summary | Author | Status |
| :- | :--- | :---- | :------ | :------ | :----- | :----: |
| U201 | 2026-07-27 | Phase 1 | T1.127–T1.133 | **Default-level verbosity noise audit**: I242 level 0→1→2 (ERROR_FILE_PROCESSING now suppressed at default `--level 1`, visible at `--level 2+`). Replaced bare `logger.error()` at `pipeline_orchestrator.py:916` with `message_manager.show("ERROR_FILE_PROCESSING")` (level 2). Changed 3 `logger.info()`→`logger.debug()` in `registry.py` (Registering document, Revision chain, registered successfully). Changed S-R-S-0409 severity `FATAL→HIGH` so per-file errors route through `logger.warning()` (level 2) instead of `logger.error()` (level 0); also set `stops_pipeline: false`. Added `test_error_file_processing_suppressed_at_default_level` test. **New issue I244**: 7 remaining per-document `info()` calls at level 1, 3 WARNING-severity error codes that map to `logger.info()` (not `warning()`) in `handle_data_error`, and MessageManager verbosity hardcoded to 1. | opencode | ✅ Done |
| U200 | 2026-07-27 | Phase 1 | T1.102–T1.130 | **I234–I243 sweep**: 7 ✅ Resolved, 2 ⛔ Won't Implement. Changes: `pipeline_orchestrator.py` (CLI arg, milestone ordering, ERROR kwarg, telemetry_verbose, B_COMPLETE total=, batch milestones), `file_scanner.py` (BATCH_MILESTONES loop + pct=processed/total), `eks_message_config.json` (STR_PHASE_B_MILESTONE template, ERROR_FILE_PROCESSING level 1). Tests: 4 new (milestone emitted, INFO not STATUS, suppressed at level 0, B_COMPLETE hydration). 148/148 pass. I242 severity bumped 🟢→🟡. Issue log v33: §51 added with I234–I243. Workplan v5.9: §62–§63 added. | opencode | ✅ Done |
| U199 | 2026-07-20 | Phase 1 | — | Status re-audit: I211/I212/I214/I217/I225 reclassified from ✅ Resolved → 🔷 Deferred for further study | System | ✅ Done |
| U198 | 2026-07-20 | Phase 1 | T1.99.194–197 | Pipeline audit sweep I226–I233. All 13 `str(5)`→`str(e)` fixed. New issues logged for follow-up. | opencode | ✅ Done |
| U197 | 2026-07-22 | Phase 1 | §5.3–§5.5 | I188/I189/I192 root cause/fix narrative stripped to align with SSOT. Only task tables + SC checklists retained. P1.3 v1.1→v1.2. | opencode | ✅ Done |
| U196 | 2026-07-22 | Phase 1 | — | P1.5 retired: appendix archived. Foundation workplan §9, §10.2, §11, TOC updated. P1.x migration complete. | opencode | ✅ Done |
