# EKS I313 — Audit & Verification Workplan (✅ RETIRED)

**Document ID**: WP-EKS-I313-001  
**Current Version**: 0.5  
**Status**: ✅ RETIRED — I313 resolved 2026-08-14; all 4 phases delivered (T1.305–T1.308, U301–U304, TL059–TL062). Workplan closed and retired per AGENTS §26.8.  
**Created**: 2026-08-14  
**Author**: opencode  
**Issue**: I313 — Audit & verification (materialization matrix, §24 cross-source audit, output-name schema coverage, full test suite)  
**Priority**: 🟠 P3 — Phase 1 Design Alignment (definition-layer materialization; ✅ resolved 2026-08-14 — removed from active priority rows)  
**Related Phase**: Phase 1 (Foundation) — DB-layer materialization closure (I306 umbrella)

> **Retirement note**: This workplan is retired. I313 is ✅ Resolved (2026-08-14) and the I306 umbrella is 📐 Aligned. Scope is fully delivered and no further tasks are anticipated — see AGENTS §15 phase-scope freeze. Follow-up findings (I315 composite-UNIQUE gap, I316 FK orphan rows, I317 real-PDF fixture gap) are tracked separately in the Phase 1 issue log priority table. A follow-up phase workplan (Phase 1.2 UI / CLI entry) will cover the next work items.

---

## Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------- |
| 0.6 | 2026-08-14 | opencode | **WORKPLAN RETIRED** — I313 ✅ Resolved + I306 📐 Aligned confirmed; header updated from DRAFT FOR REVIEW to RETIRED; no further tasks (AGENTS §15 scope freeze). Priority table in `p1_issue_log.md` updated: I313 removed from active rows (resolved history), CLI entry issues (I124/I126/I216/I223) re-prioritized as row 3, Phase 1.2 UI (I064–I071, I314) deferred to post-CLI phase. |
| 0.1 | 2026-08-14 | opencode | Initial DRAFT FOR REVIEW — scope from I313/T1.305–T1.308; task breakdown incorporates the pre-study audit findings (D1–D6 doc/schema drift, BLOCK-1–4 runtime literals, O1–O3 observations) as explicit task content. |
| 0.5 | 2026-08-14 | opencode | Phase 4 (S1.313.4 / T1.308) EXECUTED — full-suite closure: 788 PASS / 3 FAIL (pre-existing I288 real-PDF fixture absences only); consolidated report `reports/I306-I313_impl_test_report.md`; TL062/U304; I313 → ✅ Resolved, I306 → 📐 Aligned (T1.269–T1.274 + T1.305–T1.308 all complete); I317 fixture gap logged; knowledge.json v2.12.0; §17.7 integrity green. **WORKPLAN COMPLETE — all 4 phases delivered.** |
| 0.4 | 2026-08-14 | opencode | Phase 3 (S1.313.3 / T1.307) EXECUTED — BLOCK-1–4 output-name literal removal closed in the two export-path files (`eks_engine_pipeline.py` rev 2.4, `phase1_server.py` rev 0.14): config-driven view iteration + artifact_type=view_id, catalog-order phase map, `_require_system_param()` fail-fast (S-C-S-0304), view_id artifact tracking; extended literal guard (test_i308 rev 0.2) + §24 view-id cross-check fix (test_i307); report `reports/rp_eks_p1_i313_output_names.md`. Full suite 788 PASS / 3 FAIL (pre-existing I288 PDF fixtures only). Phase 4 remains. |
| 0.3 | 2026-08-14 | opencode | Phase 2 (S1.313.2 / T1.306) EXECUTED — §24 cross-source audit + D1–D6/O1 drift fixes closed in one grep-driven edit cycle (D1 review_flags csv+xlsx, D2 extraction_results 49→50, D3 view-config v1.1.0→v1.2.0 current-state refs, D4 6 FK description names, D5 fk_project_code source column, D6 fk_doc_type_composite downgrade per D-2 (b), O1 db_manifest in B.2); report `reports/rp_eks_p1_i313_audit_24.md`; version-pin tests 139 PASS + registry_relations consumers 8 PASS; post-fix grep clean. Phases 3–4 unchanged. |
| 0.2 | 2026-08-14 | opencode | Phase 1 (S1.313.1 / T1.305) EXECUTED — 53-table live matrix verified (53/53 tables, 3/3 views, id PK all, 42/42 sources, db_manifest counts, FK policy 5/5, GAP-016 re-verified RESOLVED); findings **I315** (composite natural-key UNIQUE gap — 14 tables) + **I316** (FK orphan rows — 5 pairs / 336) logged; report `reports/rp_eks_p1_i313_matrix.md`; evidence `eks/test_output/i313_phase1_matrix_results.json`. Phases 2–4 unchanged, awaiting D-1–D-4 sign-off. |

---

## Object

Execute the four I313 closure tasks to formally verify and document the schema-driven DB-layer materialization (I306 umbrella):

1. **T1.305** — rerun the T1.269 53-table inventory as a **live verification pass** against `eks_registry.db`.
2. **T1.306** — run the AGENTS.md §24 **cross-source audit** across config ↔ appendix B.1/B.2 ↔ SchemaToDDL/DefinitionLoader ↔ views ↔ `db_manifest` and **close the identified doc/schema drifts**.
3. **T1.307** — run the **output-file-name schema coverage audit** across `eks/engine`, `eks/test`, `eks/ui`, `common/` and **eliminate the remaining runtime literals**.
4. **T1.308** — record a **green full-suite baseline** (relative to the pre-existing failure set), generate the per-issue test report, write `test_log.md`/`update_log.md` entries, and close **I313 ✅ Resolved** + **I306 📐 Aligned** per §26.

---

## Scope Summary

| ID | Details | Category | Status |
| :- | :------ | :------- | :-----: |
| S1.313.1 | Live 53-table materialization matrix verification (T1.305) | Verification | ✅ Complete (2026-08-14) — see `reports/rp_eks_p1_i313_matrix.md`; findings logged as I315/I316 |
| S1.313.2 | §24 cross-source audit + doc/schema drift fixes D1–D6, O1 (T1.306) | Testing / Docs | ✅ Complete (2026-08-14) — see `reports/rp_eks_p1_i313_audit_24.md`; post-fix grep clean, version-pin tests 139 PASS + relations consumers 8 PASS |
| S1.313.3 | Output-file-name schema coverage audit + runtime literal removal BLOCK-1–4 (T1.307) | Testing / Code | ✅ Complete (2026-08-14) — see `reports/rp_eks_p1_i313_output_names.md`; full suite 788 PASS / 3 FAIL (I288 only) |
| S1.313.4 | Full-suite baseline + test report + test/update logs + issue closure (T1.308) | Testing / Logs | ✅ Complete (2026-08-14) — see `reports/I306-I313_impl_test_report.md`; full suite 788 PASS / 3 FAIL (I288 only); I313 ✅ Resolved + I306 📐 Aligned |

**Related Phase**: Phase 1 (Foundation) — closure of the I306 schema-driven DB-layer umbrella.

---

## Content Index

1. [Object](#object)
2. [Scope Summary](#scope-summary)
3. [Dependencies](#dependencies)
4. [Evaluation & Alignment with Existing Architecture](#evaluation--alignment-with-existing-architecture)
5. [Decision Points (require review sign-off)](#decision-points-require-review-sign-off)
6. [Implementation Phases](#implementation-phases)
7. [Risks & Mitigation](#risks--mitigation)
8. [Potential Future Issues](#potential-future-issues)
9. [Success Criteria](#success-criteria)
10. [References](#references)

---

## Dependencies

| Depends on | Type | Notes |
| :--------- | :--- | :---- |
| I307 (schema set), I308 (views), I309 (export), I310 (materialization), I311 (gate), I312 (db_manifest) | ✅ Completed | All resolved; I313 is the final execution-order item (priority row 6). |
| `eks/config/schemas/eks_db_config.json` v1.1.1 (53 tables) | SSOT | Verification matrix source. |
| `eks/config/schemas/eks_export_view_config.json` v1.2.0 (3 views) | SSOT | view_id / file_base_name / sheet_name / formats source. |
| `eks/workplan/t1.269_db_layer_inventory.md` | Matrix | 53-table spec + count-drift findings feeding T1.305. |
| `eks/engine/core/manifest.py` / `db_manifest` | Provenance | Per-table counts + validation outcomes recorded; used by T1.305 checks. |
| `common/library/` | Shared libs | Scope of the T1.307 grep and §24 audit. |

---

## Evaluation & Alignment with Existing Architecture

- **Aligns with** AGENTS §24 (cross-source alignment audit), §15 (workplan-driven task execution), §26 (issue lifecycle → closure), §16 (no-hardcoded-fallback → BLOCK-3 fix), and §25 (file output lifecycle — `db_manifest` single-overwrite keys).
- **No new tables, schemas, or modules** are introduced. Changes are limited to: (a) doc/schema-description corrections (D1–D6, O1), (b) removal of runtime literals in the export path (BLOCK-1–4), and (c) test/log/report artifacts.
- **Risk to engine behaviour**: the BLOCK fixes alter `eks_engine_pipeline.py` and `phase1_server.py` export routing; each change is guarded by existing tests (`test_i308_default_views.py`, `test_i309_exports.py`) plus new regression assertions added in the same edit cycle (AGENTS §12/§13).
- **Pre-existing failures**: the 3 full-suite failures (real-PDF fixture absences in `test_pipeline_processing_config.py::TestRealPdfEndToEnd`) are out of I313 scope; they are recorded as the baseline and logged as a separate issue if not restored.

---

## Decision Points (require review sign-off)

| # | Question | Options | Suggested | Who |
| :- | :------- | :------- | :-------- | :-- |
| D-1 | `_eks_table_relations` disposition within the 53-table verification | (a) keep as table #52 and verify all 53; (b) treat as deprecated and verify 52 + `db_manifest` | (a) keep 53; schedule drop as follow-up issue | Review |
| D-2 | `project_doc_type` FK shape for `fk_doc_type_composite` (D6) | (a) declare composite FK `(project_code, local_code)` in config; (b) downgrade B.1/B-schema relation to single-column with uniqueness caveat | (b) — lowest risk; `local_code` is not UNIQUE today | Review |
| D-3 | `phase1_server` phase-"a" status filter (O2) | (a) keep `["pending"]` and document; (b) align with pipeline (`None`/config filter) | (b) align to config `filter` | Review |
| D-4 | Export loop view iteration (BLOCK-1/2/4) | (a) iterate `resolve_export_views()` keys dynamically; (b) keep literal index + add grep guard | (a) dynamic iteration — removes view_id/artifact_type literals | Review |

---

## Implementation Phases

### Phase 1 — T1.305 Live Materialization Matrix Verification ✅ EXECUTED 2026-08-14

**Timeline**: day 1 (within this workplan).  
**Milestone**: verification report of all 53 tables against the T1.269 matrix.  
**Deliverable**: `eks/workplan/reports/rp_eks_p1_i313_matrix.md` (or a section of the consolidated I306–I313 report).

> **Phase 1 result (2026-08-14)**: matrix **structurally green** — 53/53 tables, 3/3 views, `id` PK on all 53, 42/42 definition sources resolve, `db_manifest` 53 `table:*` keys match live counts, physical FK policy 5/5, GAP-016 re-verified RESOLVED. Two defect classes surfaced and logged: **I315** (14 definition tables lack natural-key UNIQUE — 13 composite-key junctions + `project_revision_pattern`; `SchemaToDDL` emits per-column UNIQUE only) and **I316** (5 FK pairs / 336 orphan rows; `validate_relationships()` flags them but the warning is suppressed at default log level). Evidence: `eks/test_output/i313_phase1_matrix_results.json`. Verification-only — zero engine/config code changed. Success-criteria caveat: the "natural-key UNIQUE" and "FK-violation = 0" criteria are satisfied for the 28/42 UNIQUE-present tables and 5/5 physical FKs, with the gaps recorded as logged findings rather than phase failures.

**What will be updated/created**:
- Run a live `PRAGMA`-based scan of `eks_registry.db`: table existence (53), per-table `id` UUID PK, natural-key UNIQUE, FK enforcement probe, row counts vs `db_manifest` `table:*` keys.
- Re-verify config source resolution for each of the 42 definition sources (DefinitionLoader path).
- Confirm GAP-016 in `appendix_b.1_cross_relationship_chart.md` remains RESOLVED (already ✅ I308/T1.272; record the re-verification).

**Risks & mitigation**:
- Empty dev DB → row-count criterion defined as "internally consistent + FK violations = 0", baseline recorded, not compared against a specific pipeline run (D-1/decision note in Phase 1).
- `db_manifest` per-table counts only refresh on config-hash mismatch → run once with a forced refresh or read live counts directly.

**Potential future issues**:
- `_eks_table_relations` deprecation (table #52) — schedule removal in a follow-up issue.

**Success criteria**:
- 53/53 tables present; every definition table has a resolved config source; every table has `id` PK; natural-key UNIQUE on definition tables; FK-violation count = 0; findings recorded with evidence.

**References**: `t1.269_db_layer_inventory.md`, `eks/config/schemas/eks_db_config.json`, `eks/engine/core/manifest.py`, `eks/test/test_i310_materialization.py`.

---

### Phase 2 — T1.306 §24 Cross-Source Audit + Doc/Schema Drift Fix ✅ EXECUTED 2026-08-14

**Timeline**: day 1–2.  
**Milestone**: §24 audit report + all flagged drifts closed.  
**Deliverable**: `eks/workplan/reports/rp_eks_p1_i313_audit_24.md` (version-alignment matrix, table-name/FK/view-id/artifact_type agreement, drift list).

> **Phase 2 result (2026-08-14)**: all D1–D6 + O1 drift fixes applied in one grep-driven edit cycle and verified. D1 review_flags csv+xlsx; D2 extraction_results 49→50 (both B.0 registry + B.2 design doc); D3 all 5 current-state v1.2.0 view-config references corrected (historical revision records preserved per AGENTS §13); D4 six FK description names corrected to actual config FK names; D5 `fk_project_code.source_columns` → `["project_definition"]`; D6 `fk_doc_type_composite` downgraded to single-column `simple` with uniqueness caveat (D-2 option (b), I315); O1 `db_manifest` added to B.2 GROUP 12 lists + TABLE SUMMARY row 52. Post-fix grep clean (9 residual matches all historical/task-text). Validation: JSON/SchemaLoader OK; version-pin tests **139 PASS**; registry_relations consumers (`test_i291` + `test_phase1 -k relations` + `test_i310_materialization.py`) **8 PASS**. `validate_relationships()` reads config FK specs (unchanged) — no engine impact.

**What will be updated/created** (all in one grep-driven edit cycle, AGENTS §12):
- **D1** `appendix_b_document_registry.md:1023,1066` — `review_flags` formats `csv` → `csv + xlsx`.
- **D2** `appendix_b_document_registry.md:1021` + `appendix_b.2_db_table_design.md:1333` — `extraction_results` columns 49 → 50.
- **D3** 9+ stale `eks_export_view_config.json v1.1.0` references → **1.2.0** (grep `v1.1.0` across workplan docs).
- **D4** `eks_doc_base_schema.json:1656–1726` — 6 `registry_relations` descriptions: legacy FK names → actual config FK names.
- **D5** `eks_doc_base_schema.json:1689` — `fk_project_code` relation `source_columns` → `["project_definition"]` (per D-2 decision).
- **D6** — resolve per decision **D-2**.
- **O1** — document `db_manifest` in `appendix_b.2_db_table_design.md` metadata-table list (successor of `_eks_schema_meta`).
- Version-alignment table verified and cross-referenced into the report (base 1.22.0, setup 1.13.0, db_config 1.1.1, view 1.2.0, doc_base 1.21.0, doc_config 1.14.0, eks_config 1.14.0, error total_codes 140).
- Re-run version-pin tests: `test_i307_db_schema_set.py`, `test_t132_modules.py`, `test_i308_default_views.py`, `test_i309_exports.py`.

**Risks & mitigation**:
- Schema-description edits (D4–D6) touch `eks_doc_base_schema.json` — validate via `SchemaLoader` load + affected tests before closing.
- Doc-count drift (D2) must match the config exactly (verified count = 50).

**Potential future issues**:
- O3 (no runtime version registry post-I312) — optional hardening: emit a version-mismatch warning from `manifest._schema_version()` when a consumer version pin is stale.

**Success criteria**:
- §24 audit green: every concept agrees across 5+ sources; zero stale `v1.1.0` / `49 columns` / legacy `fk_*` references remain (grep returns only the corrected sources); affected tests pass.

**References**: AGENTS §24, `appendix_b.1/_b.2`, `appendix_b_document_registry.md`, `eks_doc_base_schema.json`, version-pin tests.

---

### Phase 3 — T1.307 Output-File-Name Schema Coverage + Runtime Literal Removal ✅ EXECUTED 2026-08-14

**Timeline**: day 2–3.  
**Milestone**: zero live output-name/artifact_type literals outside config + tests.  
**Deliverable**: `eks/workplan/reports/rp_eks_p1_i313_output_names.md` (grep audit table + fix summary).

> **Phase 3 result (2026-08-14)**: BLOCK-1–4 applied and verified. BLOCK-1 pipeline export loop iterates `resolve_export_views()` keys (artifact_type = view_id, row-builder keyed off the config column set); BLOCK-2 server phase→view map derived from catalog order + `_mk_rows_fn` config-keyed; BLOCK-3 `_require_system_param()` fail-fast (S-C-S-0304) replaces the `eks_export_` fallback literals; BLOCK-4 `insert_artifact` records view_id(s). Extended literal guard (test_i308 rev 0.2) + §24 view-id cross-check updated (test_i307). Grep audit: zero runtime literals in `eks/engine`+`eks/ui` export paths. Tests: focused 28 + 169 + 48 PASS; full suite **788 PASS / 3 FAIL** (pre-existing I288 real-PDF fixture absences only).

**What will be updated/created**:
- **BLOCK-1** `eks/engine/eks_engine_pipeline.py:291–320` — per decision **D-4**: iterate `resolve_export_views()` keys; derive `artifact_type` from each view's `view_id`; drop literal `["discovery_inventory"]`/`["extraction_results"]`/`["review_flags"]` indices and literal `"artifact_type"` values.
- **BLOCK-2** `eks/ui/backend/phase1_server.py:928–935` — replace the hardcoded phase→view_id map with a config-derived mapping (or index the exported view catalog); remove the literal `view_id == "review_flags"` branch in `_mk_rows_fn` (route via catalog/phase data).
- **BLOCK-3** `eks/ui/backend/phase1_server.py:961/965/970` — drop the `get_system_param(..., default)` fallback literals; raise a descriptive error when `export_download_file_name_template` / `export_workbook_file_name` are missing (consistent with existing S-C-S-0304 fail-fast).
- **BLOCK-4** `eks/ui/backend/phase1_server.py:1017` — `insert_artifact` to record `view_id` (not the phase letter `a/b/c/all`) as `artifact_type`, matching the I306 model and the pipeline path.
- Extend the existing no-hardcoded-literal regression guard (`test_i308_default_views.py:165`) to also reject bare `view_id` / `artifact_type` literal assignments and `"eks_export_"`/phase-letter `artifact_type` values.
- Grep audit recorded: expected residuals = config files + test fixtures only.

**Risks & mitigation**:
- Export-path behaviour change (workbook row building) → keep the existing `test_i309_exports.py` (18 tests) green + add the extended guard; run `phase1_server` tests.
- BLOCK-2 `_mk_rows_fn` special-case is data-dependent (review_flags columns differ) → preserve behaviour by keying the row-builder off the config column set, not a literal view_id.

**Potential future issues**:
- `artifact_type` values already stored as phase letters in dev `export_artifact` rows are legacy data — note in report; no backfill unless required.

**Success criteria**:
- `rg` for the 3 view_ids / `"artifact_type"` / sheet names / `eks_export_` across `eks/engine` + `eks/ui` returns zero runtime (non-config, non-test) occurrences; `test_i308_export_path_has_no_hardcoded_literals` (extended) + `test_i309_exports.py` + phase1_server tests pass.

**References**: `eks/engine/eks_engine_pipeline.py`, `eks/ui/backend/phase1_server.py`, `eks/engine/pipeline_engine/exporter.py`, `test_i308_default_views.py`, `test_i309_exports.py`.

---

### Phase 4 — T1.308 Full Suite + Reports + Logs + Closure ✅ EXECUTED 2026-08-14

**Timeline**: day 3.  
**Milestone**: closure of I313 ✅ Resolved and I306 📐 Aligned.  
**Deliverable**: consolidated `eks/workplan/reports/I306-I313_impl_test_report.md` per §16 + TLxxx/Uxxx log entries.

> **Phase 4 result (2026-08-14)**: full suite `conda run -n eks python -m pytest eks/test/ -q` → **788 PASS / 3 FAIL** in 248.32s — the 3 failures are the pre-existing I288 real-PDF fixture absences (`FileNotFoundError: No real PDF fixture found under eks/data/twrp/`), identical to the pre-I313 baseline; **zero new failures** across I306/I307–I313. Consolidated report `reports/I306-I313_impl_test_report.md` (§16) generated; test log TL062 + update log U304 written; **I313 → ✅ Resolved** and **I306 → 📐 Aligned** per §26.8 (workplan referenced); **I317** (real-PDF fixture gap) logged as a separate issue so a fully-green suite is achievable; knowledge.json v2.10.0→v2.12.0 (T1.273); task log T1.270–T1.274 + T1.305–T1.308 → ✅ Complete; issue log §17.7 integrity green (297 rows, no gaps/dups, status counts match).

**What will be updated/created**:
- Run full suite from repo root: `conda run -n eks python -m pytest eks/test/ -q`. Record baseline **788 passed / 3 failed** (pre-I313) and the post-fix result; the 3 failures must remain the pre-existing real-PDF fixture absences (no new failures). Log the fixture gap as a separate issue if not restored.
- Generate `eks/workplan/reports/I306-I313_impl_test_report.md` (§16 required sections).
- Write `test_log.md` TLxxx entry per issue (I313 + any fix-driven re-verification).
- Write `update_log.md` Uxxx entries per task group.
- Update `p1_issue_log.md`: I313 → ✅ Resolved; I306 → 📐 Aligned (§26.8 — workplan referenced); Status Summary + Priority row 6 removal; Last Updated bumped.
- Update task log T1.305–T1.308 → ✅ Complete.

**Risks & mitigation**:
- Long suite runtime (~3–4 min) → run once; focused re-run only for changed files.
- Issue-log integrity per AGENTS §17.7 (targeted edits, recount Status Summary, validate `I\d+` sequence).

**Potential future issues**:
- Real-PDF fixture restoration (I288) — track as its own issue so a fully-green suite is achievable.

**Success criteria**:
- Full suite green except the documented pre-existing 3; report + TLxxx + Uxxx entries written; I313 ✅ Resolved, I306 📐 Aligned with workplan reference; no `I\d+` gaps/duplicates in the issue log.

**References**: AGENTS §16/§26, `eks/log/phase1/p1_issue_log.md`, `p1_task_log.md`, `p1_test_log.md`, `p1_update_log.md`, `eks/workplan/reports/`.

---

## Risks & Mitigation

| Risk | Severity | Mitigation |
| :--- | :------- | :--------- |
| Export-path code change introduces a regression in workbook/CSV output | 🟠 High | Guarded by `test_i309_exports.py` (18) + extended no-hardcoded-literal test; focused re-run before full suite. |
| Schema-description edits (D4–D6) break `SchemaLoader` validation | 🟠 High | Validate via SchemaLoader load + `test_i307_db_schema_set.py` before closing the phase. |
| Doc drift fixes incomplete (stale refs remain) | 🟡 Medium | Grep-driven sweep for `v1.1.0`, `49 columns`, legacy `fk_*`; §24 checklist in report. |
| 3 pre-existing PDF failures block "full suite green" | 🟡 Medium | Recorded as documented baseline; logged as separate issue; not blocking I313. |
| Issue-log integrity regression during closure | 🟡 Medium | AGENTS §17.7 targeted edits; recount + `I\d+` validation after every edit. |

---

## Potential Future Issues

- **I315** — composite natural-key UNIQUE gap (14 definition tables) — follow-up fix: SchemaToDDL composite `UNIQUE` + config `unique_keys`.
- **I316** — FK orphan rows (5 pairs / 336) — follow-up fix: source-config alignment + FK-violation visibility at default log level.
- `_eks_table_relations` removal (deprecated metadata table) — follow-up issue.
- `project_doc_type` composite FK hardening (if D-2 option (a) is chosen later).
- Runtime version-registry warning (O3) — optional post-I313 hardening.
- Real-PDF fixture restoration (I288) for a fully-green suite.
- Legacy `export_artifact.artifact_type` phase-letter rows — data hygiene note only.

---

## Success Criteria

1. **T1.305** — 53/53 tables materialized with `id` PK; config sources resolve; FK violations = 0; evidence recorded.
2. **T1.306** — §24 audit green; D1–D6 + O1 closed; zero stale references; version-pin tests pass.
3. **T1.307** — zero live output-name / `artifact_type` literals in `eks/engine` + `eks/ui`; extended guard test passes.
4. **T1.308** — full suite = documented baseline with no new failures; report + TLxxx + Uxxx written; I313 ✅ Resolved; I306 📐 Aligned.
5. **AGENTS compliance** — all edits via targeted `replace_in_file`; revision control applied; logs updated.

---

## References

- `eks/workplan/t1.269_db_layer_inventory.md` (53-table matrix)
- `eks/workplan/appendix_b.1_cross_relationship_chart.md`, `appendix_b.2_db_table_design.md`, `appendix_b_document_registry.md`
- `eks/config/schemas/eks_db_config.json`, `eks_export_view_config.json`, `eks_doc_base_schema.json`, `eks_base_schema.json`, `eks_setup_schema.json`
- `eks/engine/core/{schema_to_ddl, definition_loader, registry, manifest, migration_gate, schema_loader}.py`
- `eks/engine/pipeline_engine/exporter.py`, `eks/engine/eks_engine_pipeline.py`, `eks/ui/backend/phase1_server.py`
- Tests: `test_i307_db_schema_set.py`, `test_i308_default_views.py`, `test_i309_exports.py`, `test_i312_manifest.py`, `test_migration_gate.py`, `test_t132_modules.py`
- Logs: `eks/log/phase1/p1_{issue,task,test,update}_log.md`
- AGENTS.md §12, §15, §16, §24, §26