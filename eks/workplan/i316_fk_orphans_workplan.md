# EKS I316 — FK Orphan Rows Resolution Workplan

**Document ID**: WP-EKS-I316-001
**Current Version**: 0.3
**Status**: ✅ COMPLETE — ALL PHASES EXECUTED AND VERIFIED
**Created**: 2026-08-20
**Author**: opencode
**Issue**: I316 — FK orphan rows (5 pairs / 336 rows) flagged by `validate_relationships()` but suppressed at default log level
**Priority**: 🟠 P3 — Phase 1 Design Alignment
**Related Phase**: Phase 1 (Foundation) — DB-layer materialization closure (I306 umbrella)

> **Approval note**: Plan Q1–Q6 approved by user 2026-08-20 (Q3 = Option B — register `MULTI` sentinel). Implementation proceeds per §5.2; final diff presented for review before closure. **Review sign-off 2026-08-20 (user directive: "make sure all logs are updated for i316 and its related tasks")** — Q7 doc/log sync executed; all logs updated; I316 → ✅ Resolved; workplan closed.

---

## Revision History

| Revision | Date | Author | Summary |
| :------- | :--- | :----- | :------- |
| 0.3 | 2026-08-20 | opencode | Review sign-off (user directive) + Q7 doc/log sync COMPLETE — appendix_b.2 TABLE SUMMARY (53→55 tables, ontology_relation 18→21, pipeline_message 52→53); issue log v128 (I316 → ✅ Resolved, Status Summary Resolved 167→168 / Aligned 100→99, priority re-sequenced 2–5→1–4, outstanding 14→13); update log U308 (U306/U307 table rows added — pre-existing gap); test log TL064 (rev 1.34); task log T1.313/T1.314 ✅ COMPLETE (Complete 464→466, Planned 31 unchanged, Total 498→500); knowledge.json v2.14.1→v2.15.0 (I316 resolved, total_issues_resolved 42→43). Workplan status → ✅ COMPLETE. |
| 0.2 | 2026-08-20 | opencode | Implementation executed — Q1–Q6 all done; 0 FK orphans on fresh build + live rebuild; full suite 806 pass / 4 fail (3 pre-existing I288 + 1 flaky lock race that passes on rerun). Added I315 regression fix (unique_keys declared in table_spec_def, v1.22.0→v1.23.0) found during Q6 — I315 commit added unique_keys to 14 config tables without declaring the property; also corrected `column_class` unique_keys to the composite `[column_name, class_id]` (I315 had declared single-column on an M:N junction). Q3 decision taken at implementation: `eks_project_definition_config.json` discipline normalized `multi`→`MULTI` (v1.6.0) for exact-match integrity. Q7 doc/log sync pending review. |
| 0.1 | 2026-08-20 | opencode | Initial DRAFT FOR REVIEW — scope from I316 + I313 Phase 1 matrix findings; approved Q1–Q6 plan (Q1 Option A lookup tables, Q2 re-point fk_pdt_project, Q3 Option B MULTI sentinel, Q4 3 new ontology relations, Q5 level-1 FK-orphan message, Q6 rebuild + regression). |

---

## Object

Resolve the 5 FK orphan pairs (336 rows) identified by I313 Phase 1 verification so that `validate_relationships()` returns 0 violations on a fresh build, and surface FK-orphan detection at the default log level (level 1) instead of the suppressed level 2.

1. **Q1** — Introduce `asset_sheet` + `asset_trigger_scope` lookup tables; re-point `fk_acn_type` → `asset_sheet.sheet_name` and `fk_atrig_type` → `asset_trigger_scope.scope_name`. (Option A — approved)
2. **Q2** — Re-point `fk_pdt_project` → `target_table: project_code`, `target_column: proj_code`.
3. **Q3** — Register `MULTI` sentinel code in `eks_discipline_schema.json` (Option B — approved; keep string semantics).
4. **Q4** — Register `CONTROLLED_BY`, `FLOWS_FROM`, `HAS_ACTUATOR` (inverse `ACTUATES`) in `eks_ontology_config.json` (18→21).
5. **Q5** — Add `WARNING_FK_ORPHANS` message (level 1) + `logger.status` summary with level-2 per-pair detail.
6. **Q6** — Rebuild DB, verify 0 orphans across all 59 FK pairs, add regression test, run full suite.

---

## Scope Summary

| ID | Details | Category | Status |
| :- | :------ | :------- | :-----: |
| S1.316.1 | Q1 — `asset_sheet` + `asset_trigger_scope` lookup tables + registry sections + FK re-points | Code / Schema | ✅ EXECUTED |
| S1.316.2 | Q2 — `fk_pdt_project` re-point to `project_code.proj_code` | Schema | ✅ EXECUTED |
| S1.316.3 | Q3 — `MULTI` sentinel in discipline schema + config normalize (Option B) | Schema | ✅ EXECUTED |
| S1.316.4 | Q4 — 3 new ontology relations (18→21) | Schema | ✅ EXECUTED |
| S1.316.5 | Q5 — `WARNING_FK_ORPHANS` message + logger level fix | Code / Schema | ✅ EXECUTED |
| S1.316.6 | Q6 — DB rebuild + regression test + full suite | Testing | ✅ EXECUTED |
| S1.316.7 | Q7 — doc/log sync (appendix_b.2, issue log, update log, test log, knowledge.json) | Docs / Logs | ✅ EXECUTED |
| S1.316.8 | I315 regression fix — `unique_keys` declared in `table_spec_def` (v1.23.0) + `column_class` composite key correction | Schema / Testing | ✅ EXECUTED |

**Related Phase**: Phase 1 (Foundation) — closure of the I306 schema-driven DB-layer umbrella.

---

## Content Index

1. [Object](#object)
2. [Scope Summary](#scope-summary)
3. [Dependencies](#dependencies)
4. [Evaluation & Alignment with Existing Architecture](#evaluation--alignment-with-existing-architecture)
5. [Decision Points (approved)](#decision-points-approved)
6. [Implementation Phases](#implementation-phases)
7. [Risks & Mitigation](#risks--mitigation)
8. [Potential Future Issues](#potential-future-issues)
9. [Success Criteria](#success-criteria)
10. [References](#references)

---

## Dependencies

| Depends on | Type | Notes |
| :--------- | :--- | :---- |
| I313 (audit), I315 (composite UNIQUE) | ✅ Completed | I316 findings source; I315 resolved separately (composite-UNIQUE DDL gap — not a row-level defect). |
| `eks/config/schemas/eks_db_config.json` v1.1.1 (53 tables, 59 FK pairs) | SSOT | 5 FK pairs re-pointed or re-targeted; 2 new tables added (55 total). |
| `eks/config/schemas/eks_asset_config.json` v1.4.0 | SSOT | New `sheet_registry` + `trigger_scope_registry` sections. |
| `eks/config/schemas/eks_asset_setup_schema.json` v1.3.0 | Schema | `additionalProperties: false` + `required` → must add the two new registry properties. |
| `eks/config/schemas/eks_discipline_schema.json` v1.0.0 (21 codes) | Schema | `MULTI` sentinel appended (22). |
| `eks/config/schemas/eks_ontology_config.json` v1.9.0 (18 relations) | SSOT | 3 relations appended (21). |
| `eks/config/schemas/eks_message_config.json` v1.2.0 (52 messages) | SSOT | `WARNING_FK_ORPHANS` added (53). |
| `eks/engine/core/registry.py` (rev 1.7) | Code | Q5 logger-level change at lines 318-324. |
| `eks/engine/core/definition_loader.py` (rev 1.x) | Code | `validate_relationships()` + natural-key / transform mechanics. |

---

## Evaluation & Alignment with Existing Architecture

- **Aligns with** AGENTS §8 (data column priority), §13 (revision control — cross-reference version bumps), §19 (error/message catalog lifecycle), §24 (cross-source alignment — version pins in 5+ sources), §26 (issue lifecycle → ✅ Resolved), §15 (workplan-driven task execution).
- **New tables** (`asset_sheet`, `asset_trigger_scope`) are reference/lookup tables in DB group 10, sourced from new `sheet_registry` / `trigger_scope_registry` sections in `eks_asset_config.json`. They mirror the existing `relationship_triggers`/`column_normalization` natural-key mechanics (no loader changes required — pure array-of-objects transforms).
- **Column names unchanged** on `asset_column_normalization.asset_type_code` / `asset_trigger.asset_type_code` — the FK target is re-pointed only; the loader's natural-key inference (`_keys[0]` = sheet name / section name) keeps producing the same values, which now resolve against the lookup tables.
- **No behavioural change** to `SchemaToDDL` or `DefinitionLoader`; only config data + FK target declarations.
- **Pre-existing failures**: 3 I288 real-PDF fixture absences + 1 flaky phase1_server lock race remain out of scope; recorded as baseline.

---

## Decision Points (approved)

| # | Question | Options | Decision | Status |
| :- | :------- | :------- | :-------- | :----: |
| Q1 | `asset_column_normalization.asset_type_code` (sheet names) + `asset_trigger.asset_type_code` (section names) have no FK target | (a) new lookup tables `asset_sheet` + `asset_trigger_scope`; (b) drop the FKs | **(a) new lookup tables** — retains FK integrity, no data loss | ✅ Approved |
| Q2 | `project_doc_type.fk_pdt_project` → `project.project_code` has no matching column | (a) re-point to `project_code.proj_code`; (b) drop the FK | **(a) re-point to `project_code.proj_code`** — `proj_code` holds the synthetic project key | ✅ Approved |
| Q3 | `project_definition.discipline` = `'multi'` has no discipline_code | (a) register `MULTI` sentinel; (b) convert to boolean | **(a) register `MULTI` sentinel (Option B)** — keeps string semantics, matches data value | ✅ Approved |
| Q4 | 3 `edge_type` values (`CONTROLLED_BY`, `FLOWS_FROM`, `HAS_ACTUATOR`) missing from ontology relations | (a) register 3 relations; (b) drop those trigger rows | **(a) register 3 relations** — semantically valid, inverse pairs added | ✅ Approved |
| Q5 | FK-orphan warning suppressed at default log level 1 | (a) level-1 status summary + level-2 detail; (b) keep level-2 | **(a) level-1 summary + level-2 detail** — visible by default | ✅ Approved |
| Q6 | Post-fix verification | (a) rebuild + regression + full suite; (b) in-place migration | **(a) fresh rebuild** — live DB predates I315 UNIQUE DDL | ✅ Approved |

---

## Implementation Phases

### Phase 1 — Q1 Lookup Tables + FK Re-points ✅ EXECUTED 2026-08-20

**Timeline**: day 1.
**Milestone**: `asset_sheet` + `asset_trigger_scope` tables exist; `fk_acn_type` / `fk_atrig_type` re-pointed; configs valid.
**Deliverable**: updated `eks_asset_config.json`, `eks_asset_setup_schema.json`, `eks_db_config.json`.

**What will be updated/created**:
- `eks_asset_config.json` (v1.4.0 → v1.5.0): add `sheet_registry` (7 sheet names) + `trigger_scope_registry` (`relationship_triggers`, `document_triggers`).
- `eks_asset_setup_schema.json` (v1.3.0 → v1.4.0): add both properties + required entries.
- `eks_db_config.json` (v1.1.1 → v1.2.0): add `asset_sheet` + `asset_trigger_scope` table specs (group 10, uuid5 id, natural key `sheet_name` / `scope_name`); re-point `fk_acn_type` / `fk_atrig_type`.

**Risks & mitigation**: `additionalProperties: false` on asset setup schema → both registry properties must be declared or config validation fails; verified in Phase 1 execution.

**Potential future issues**: `asset_type_code` column name on `asset_column_normalization` is now semantically a sheet name — flagged for a future column rename (non-blocking).

### Phase 2 — Q2 fk_pdt_project Re-point ✅ EXECUTED 2026-08-20

**What will be updated**: `eks_db_config.json` — `project_doc_type.fk_pdt_project` `target_table`/`target_column` → `project_code`/`proj_code`.

**Risks & mitigation**: verified `project_code` table has `proj_code` column and the FK values are synthetic keys (e.g. `PROJ-...`) that match `proj_code`; validated post-rebuild.

### Phase 3 — Q3 MULTI Sentinel ✅ EXECUTED 2026-08-20

**What will be updated**: `eks_discipline_schema.json` (v1.0.0 → v1.1.0) — append `{"code": "MULTI", "description": "Multi-discipline project (not a single engineering discipline)"}`.

**Risks & mitigation**: discipline codes remain strings; the FK join is case-sensitive (DuckDB) so a lowercase `'multi'` value could not resolve against an uppercase `'MULTI'` code. **Decision taken at implementation**: normalize `eks_project_definition_config.json` (v1.5.0 → v1.6.0) discipline `multi` → `MULTI` for both projects (131101/131242) in the same edit cycle — exact-match integrity (AGENTS §13 same-cycle cross-reference). Verified post-rebuild: `project_definition.discipline` values = `{'MULTI'}`.

### Phase 4 — Q4 New Ontology Relations ✅ EXECUTED 2026-08-20

**What will be updated**: `eks_ontology_config.json` (v1.9.0 → v1.10.0) — add `CONTROLLED_BY` (inverse `CONTROLS`), `FLOWS_FROM` (inverse `FLOWS_TO`), `HAS_ACTUATOR` (inverse `ACTUATES`); update description + `eks_db_config.json:303` "(18 rows)" → "(21 rows)".

### Phase 5 — Q5 Message + Logger Level ✅ EXECUTED 2026-08-20

**What will be updated**: `eks_message_config.json` (v1.2.0 → v1.3.0, total 53) — add `WARNING_FK_ORPHANS` (level 1, category warning, icon ⚠); `registry.py:318-324` — replace `logger.warning` with `logger.status` (level 1) summary + `logger.warning` (level 2) per-pair detail.

### Phase 6 — Q6 Rebuild + Regression + Full Suite ✅ EXECUTED 2026-08-20

**What will be updated**: fresh `DocumentRegistry()` rebuild of `eks_registry.db`; regression test asserting 0 FK violations; version-pin test updates (test_i298_i305, test_i300, test_i307_db_schema_set, test_i310_materialization); full suite run.

**I315 regression fix (found during Q6)**: the I315 commit (`6e8ec365`) added `unique_keys` to 14 tables in `eks_db_config.json` but never declared the property in `table_spec_def` (`additionalProperties: false`) — every config-validating test failed at `_validate_db_config` and the DB could not be built. Fixed by declaring `unique_keys` (array of column-name arrays) in `table_spec_def`, `eks_base_schema.json` v1.22.0→v1.23.0; synced 3 test pins (test_i307_db_schema_set:58, test_i309_exports:79, test_t132_modules:904). Also corrected `column_class.unique_keys` `[["column_name"]]` → `[["column_name","class_id"]]` — the I315 single-column UNIQUE was invalid for an M:N junction (a column maps to many classes) and broke `load_all` with a PK/UNIQUE violation.

**Verification**: fresh-build `validate_relationships()` = **0 violations** (all 59 FK pairs); live `eks/output/eks_registry.db` rebuilt (55/55 tables, asset_sheet 7 rows, asset_trigger_scope 2 rows, asset_column_normalization 297, asset_trigger 18); full suite **806 passed / 4 failed** (3 pre-existing I288 real-PDF fixture absences + 1 known flaky phase1_server lock race that passes on rerun) — zero new regressions.

### Phase 7 — Q7 Doc/Log Sync ✅ EXECUTED 2026-08-20 (review sign-off)

**What was updated**: `appendix_b.2_db_table_design.md` TABLE SUMMARY (53→55 tables, ontology_relation 18→21, pipeline_message 52→53); `p1_issue_log.md` (I316 → ✅ Resolved, status summary, v128 header); `update_log.md` (U308); test log (TL064); task log (T1.313/T1.314); `knowledge.json:234` (v2.15.0). Executed after review sign-off per user directive 2026-08-20.

---

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--------- | :----- | :--------- |
| Case mismatch (`multi` vs `MULTI`) | Medium | FK still orphaned | **Resolved**: `project_definition.discipline` normalized to `MULTI` in same edit cycle (v1.6.0); verified post-rebuild |
| Schema validation failure on new asset sections | Low | Config invalid | Add properties to `eks_asset_setup_schema.json` before config — done (v1.4.0) |
| I315 `unique_keys` schema gap (regression) | High | Config fails validation; DB build blocked | **Resolved**: `unique_keys` declared in `table_spec_def` (v1.23.0); `column_class` composite key corrected |
| Version-pin drift in tests | Low | CI failure | Update all pinned test files in same edit cycle (AGENTS §13) — done (base 1.23.0 pins ×3) |
| Live DB rebuild loss | Low | Dev DB reset | DB is derived; rebuilt from configs via fresh `DocumentRegistry()` — done |

---

## Potential Future Issues

- Column rename `asset_column_normalization.asset_type_code` → `sheet_name` (semantic drift).
- `discipline` case normalization across config/docs/tests.
- I288 real-PDF fixture absences (3 tests) — pre-existing, tracked separately.

---

## Success Criteria

- `validate_relationships()` returns 0 violations on a fresh build (all 59 FK pairs). ✅ 0 violations verified
- Config JSON validates against setup schemas. ✅ all configs JSON-valid + setup-schema validated (incl. I315 `unique_keys` fix)
- All version-pin tests updated and passing. ✅ base 1.23.0 pins + db_config 1.2.0 + ontology 1.10.0 + pd config 1.6.0 + message 53 + table count 55
- Full suite green (relative to pre-existing 4-failure baseline: 3 I288 + 1 flaky lock race). ✅ 806 passed / 4 failed (identical pre-existing set; flaky passes on rerun)
- Logs/docs/knowledge.json updated; I316 → ✅ Resolved. ✅ **Q7 executed 2026-08-20** (review sign-off) — appendix_b.2 TABLE SUMMARY, issue log v128, update log U308, test log TL064, task log T1.313/T1.314, knowledge.json v2.15.0

---

## References

- `eks/config/schemas/eks_db_config.json` (v1.1.1 → v1.2.0)
- `eks/config/schemas/eks_asset_config.json` (v1.4.0 → v1.5.0)
- `eks/config/schemas/eks_asset_setup_schema.json` (v1.3.0 → v1.4.0)
- `eks/config/schemas/eks_discipline_schema.json` (v1.0.0 → v1.1.0)
- `eks/config/schemas/eks_ontology_config.json` (v1.9.0 → v1.10.0)
- `eks/config/schemas/eks_message_config.json` (v1.2.0 → v1.3.0)
- `eks/engine/core/registry.py` (rev 1.7 → 1.8)
- `eks/workplan/i313_audit_verification_workplan.md` (Phase 1 matrix findings)
- `eks/workplan/appendix_b.2_db_table_design.md` (TABLE SUMMARY)
- `eks/log/phase1/p1_issue_log.md` (I316 row)
- Tests: `eks/test/test_i298_i305.py`, `eks/test/test_i300.py`, `eks/test/test_i307_db_schema_set.py`, `eks/test/test_i310_materialization.py`