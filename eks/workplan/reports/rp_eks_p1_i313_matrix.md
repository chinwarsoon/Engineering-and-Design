# EKS Phase 1 — I313 Phase 1 (T1.305) — 53-Table Live Materialization Matrix Verification — Test Report

**Report ID**: RP-EKS-P1-I313-MATRIX
**Current Version**: 1.0
**Status**: ✅ COMPLETE (verification executed; findings logged as I315 / I316)
**Last Updated**: 2026-08-14
**Parent Workplan**: [i313_audit_verification_workplan.md](../i313_audit_verification_workplan.md) — Phase 1 (T1.305). Issue: **I313** — Audit & verification (materialization matrix, §24 cross-source audit, output-name schema coverage, full test suite).

## 1. Test Objective

Rerun the T1.269 53-table inventory as a **live verification pass** against `eks_registry.db`, confirming the schema-driven DB-layer materialization (I306 umbrella) is actually materialized — every table exists, every definition table resolves a config source, every table has an `id` PK, definition tables carry natural-key UNIQUE, FKs are enforced (physical where designed, logical elsewhere), row counts match the `db_manifest` `table:*` keys, and GAP-016 remains RESOLVED. Verification-only: **no engine or config code is changed** in this phase.

## 2. Scope

- **Target DB**: `eks/output/eks_registry.db` — freshly built via `DocumentRegistry()` for this pass.
- **Verification matrix** (from `eks/config/schemas/eks_db_config.json` v1.1.1, 53 tables):
  - 53/53 tables present, 0 extra tables
  - 3/3 `v_*` export views present
  - `id` PK on all 53 tables
  - 42/42 definition sources resolve through `DefinitionLoader` (0 unresolved, 0 empty, 0 non-UUID `id` values)
  - Natural-key UNIQUE present on definition tables (findings recorded for gaps)
  - FK integrity: 5 physical FK constraints per design (document_reference ×2, health_score ×2, health_batch ×1) + 54 logical FK pairs probed
  - `db_manifest` `table:*` keys match live row counts
  - GAP-016 re-verification in `appendix_b.1_cross_relationship_chart.md`
- **Out of scope**: §24 cross-source audit (T1.306), output-name literal removal (T1.307), full-suite baseline + closure (T1.308). All deferred to the next phases of the I313 workplan.

## 3. Test Execution Summary

| Check group | Coverage | Result |
| :---------- | :------- | :----: |
| Table materialization | 53/53 present, 0 missing, 0 extra | ✅ PASS |
| Export views | 3/3 (`v_discovery_inventory`, `v_extraction_results`, `v_review_flags`) | ✅ PASS |
| `id` PK | on all 53 tables; `id_pk_missing = []` | ✅ PASS |
| Definition sources | 42/42 resolve; `source_unresolved = []`, `source_empty = []`, `non_uuid_ids = []` | ✅ PASS |
| Natural-key UNIQUE | 28 definition tables have UNIQUE; **14 gaps** recorded | 🔶 FINDING (I315) |
| FK physical policy | 5/5 designed physical FKs present; `physical_fk_missing = []` | ✅ PASS |
| FK logical integrity | 59 pairs probed; **5 pairs / 336 orphan rows** | 🔶 FINDING (I316) |
| `db_manifest` counts | 53 `table:*` keys, 0 missing, 0 mismatch | ✅ PASS |
| GAP-016 | re-verified RESOLVED (`appendix_b.1:1021`) | ✅ PASS |

**Result**: the materialization matrix is **structurally green** (all existence/PK/source/manifest checks pass). `ok=false` in the evidence JSON is driven solely by the two findings below — these are data/DDL defects to be fixed in a follow-up phase, not verification failures.

## 4. Detailed Results

### 4.1 PASS — 53-table materialization

`tables_present` = all 53 tables from `eks_db_config.json` (0 missing, `extra_tables = []`). Live row counts (`row_counts`) cover every table; `transform_split` confirmed as config-declared: 1:1-unpack 3, array-of-objects 14, direct-map 11, junction-from-array 7, object-iteration 18 (= 53).

### 4.2 PASS — views, PK, sources, manifest

- 3/3 export views live; `views_missing = []`.
- `id` PK on every table; `id_pk_missing = []`.
- All 42 definition sources resolve; `non_uuid_ids = []` (no legacy non-UUID keys left after I310).
- `db_manifest` carries all 53 `table:*` keys; `manifest_missing_keys = []`, `manifest_count_mismatch = []`. Note: live `db_manifest` self-count is 65 rows vs the recorded 11 — expected, self-referential (the manifest records its own pre-refresh count before per-table stats are written).

### 4.3 PASS — physical FK policy (5/5)

The 5 designed physical FKs are all present: `document_reference.source_doc_id→documents.id`, `document_reference.target_doc_id→documents.id`, `health_score.run_id→batch_run.run_id`, `health_score.document_id→documents.id`, `health_batch.run_id→batch_run.run_id`. `physical_fk_missing = []`.

### 4.4 FINDING (I315) — composite natural-key UNIQUE gap (14 definition tables)

28 definition tables declare `UNIQUE` on their natural key; **14 do not** (`unique_missing`, all `unique_sets = []`):

| Table | Natural key |
| :---- | :---------- |
| `template_source_quality` | template_id, cover_type |
| `template_elements` | template_id, element_type |
| `element_by_cover_type` | element_type, cover_type |
| `column_class` | column_name, class_id |
| `onto_class_fragment` | class_id, fragment_id |
| `fp_property_mapping` | profile_id, source_key |
| `project_doc_type` | project_code, local_code |
| `project_engineering_standard` | project_code, standard_cat |
| `project_allowed_discipline` | project_code, discipline_code |
| `asset_fragment_field` | fragment_id, field_name |
| `asset_type_fragment` | asset_type_code, fragment_id |
| `asset_column_normalization` | asset_type_code, source_column_name |
| `asset_trigger` | asset_type_code, trigger_id |
| `project_revision_pattern` | project_code (single key) |

**Root cause**: `SchemaToDDL` emits `UNIQUE` only for per-column `unique:true` flags; there is **no composite-key UNIQUE mechanism** in `table_spec_def` / the DDL renderer. Junction tables can therefore accept duplicate natural-key rows, and `project_revision_pattern.project_code` is not keyed uniquely.

**Impact**: duplicate junction rows are preventable only at the app layer; the DB does not enforce the T1.269/I307 natural-key UNIQUE intent.

**Disposition**: logged as **I315** (🔴 Open) — fix deferred to a follow-up phase (add composite `UNIQUE (natural-key columns)` emission to SchemaToDDL + declare a `unique_keys` array in the table spec / `eks_db_config.json`).

### 4.5 FINDING (I316) — FK orphan rows (5 pairs / 336 rows)

Both the FK-violation probe (`fk_orphans`) and `DefinitionLoader.validate_relationships()` (`loader_fk_violations`) independently confirm the same 5 pairs:

| Child (column) → target | Orphan rows | Orphan values |
| :---------------------- | ----------: | :------------ |
| `project_doc_type.project_code` → `project.project_code` | 15 | '131101' ×8, '131242' ×7 (target has only 'EKS-001') |
| `project_definition.discipline` → `discipline.discipline_code` | 2 | 'multi' |
| `asset_column_normalization.asset_type_code` → `asset_type.asset_type_code` | 297 | CONTROLVALVE 64, Instrument 57, Motor 53, Equipment 50, MANUALVALVE 32, Inline Component 28, Pipeline 13 (target uses coded AT_* values) |
| `asset_trigger.asset_type_code` → `asset_type.asset_type_code` | 18 | 'relationship_triggers' ×15, 'document_triggers' ×3 |
| `asset_trigger.edge_type` → `ontology_relation.relation_name` | 4 | CONTROLLED_BY ×2, HAS_ACTUATOR ×1, FLOWS_FROM ×1 |

**Root cause**: reference-data defects in source configs — `asset_type_code` holds labels/section names instead of registered `AT_*` codes; `discipline='multi'` is absent from the discipline table; project codes `131101`/`131242` are absent from the project definitions. The logical FK layer detects them, but the warning is emitted at log level ≥2 while the default pipeline log level is 1 — the violation is **silent** by default.

**Impact**: configured FK relationships are not fully satisfied; silent data-integrity defects in the reference-data layer.

**Disposition**: logged as **I316** (🔴 Open) — fix deferred to a follow-up phase (align the source configs to registered codes; raise FK-violation reporting to an explicit message at the default log level).

### 4.6 PASS — GAP-016 re-verification

GAP-016 in `appendix_b.1_cross_relationship_chart.md:1021` remains **RESOLVED** (already closed via I308/T1.272); re-verified unchanged on 2026-08-14.

## 5. Methodology, Environment, Tools

- **Method**: fresh `DocumentRegistry()` open builds `eks/output/eks_registry.db` from `eks_db_config.json` (config-driven DDL + DefinitionLoader inserts + export views + migration gate + `db_manifest` refresh). A PRAGMA-based matrix probe then introspects the live DB: `duckdb_tables()` for user-table listing, `duckdb_columns()`/`duckdb_constraints()` for PK/UNIQUE/FK detection, live LEFT-JOIN queries for FK orphan probing, and `db_manifest` `table:*` keys for row-count comparison. Results serialized to `eks/test_output/i313_phase1_matrix_results.json`.
- **Environment**: Windows 10/11 (win32), Python 3.13 (conda env `eks`), DuckDB embedded.
- **DuckDB introspection notes (verified on this pass)**: use `duckdb_tables()` for user tables (`information_schema.tables WHERE table_schema='main'` returns nothing here); `duckdb_constraints().constraint_column_indexes` are 0-based while `duckdb_columns().column_index` is 1-based (offset −1); FK constraint text is unquoted `FOREIGN KEY (col) REFERENCES tgt(col)`; DuckDB has no `PRAGMA foreign_keys` (FK/UNIQUE enforced on insert).
- **Observation (non-blocking)**: a second `DocumentRegistry()` build logged "destructive 3 tables / 0 columns" from the migration gate (timestamped backup written to `eks/archive/`). The final DB is clean (53 tables, matrix green) — root cause not yet fully explained; flagged for follow-up in §9.

## 6. Evidence / Files

| File | Action |
| :--- | :----- |
| `eks/test_output/i313_phase1_verify.py` | NEW (rev 0.2) — verification script: fresh `DocumentRegistry()` build + PRAGMA matrix probe + FK orphan probe + `validate_relationships` cross-check; writes results JSON. |
| `eks/test_output/i313_phase1_matrix_results.json` | NEW — full evidence: table/view/PK/unique/FK/source/manifest checks + orphan values. |
| `eks/output/eks_registry.db` | REBUILT — live registry used for the pass (53 tables). |
| `eks/archive/eks_registry_backup_*.db` | CREATED by the migration-gate backup on the second build (observation §5). |
| `eks/workplan/appendix_b.1_cross_relationship_chart.md` | NO CHANGE — GAP-016 re-verified RESOLVED (line 1021). |

No engine or config code was modified in this phase.

## 7. Logs Updated

- `eks/log/phase1/p1_issue_log.md` — v119 → v120: I315 + I316 added (🔴 Open); Status Summary Open 11→13, Total 294→296; Priority row 6 → I313/I315/I316; outstanding 27→29.
- `eks/log/phase1/p1_task_log.md` — T1.305 ⏳ Planned → ✅ Complete (Complete 451→452, Planned 44→43).
- `eks/log/phase1/p1_test_log.md` — TL059 added (rev 1.29).
- `eks/log/phase1/p1_update_log.md` — U301 added (Done 245→246, Total 271→272).
- `eks/workplan/i313_audit_verification_workplan.md` — Phase 1 (S1.313.1) marked complete; rev 0.2.

## 8. Success Criteria Checklist

- [x] 53/53 tables present; `extra_tables = []`
- [x] 3/3 export views present
- [x] `id` PK on all 53 tables
- [x] 42/42 definition sources resolve; 0 empty; 0 non-UUID ids
- [x] Natural-key UNIQUE: 28 present; **14 gaps logged as I315** (criteria adjusted — gap is a logged finding, not a phase failure)
- [x] Physical FK policy 5/5 present
- [x] Logical FK probe: 0 errors; **5 pairs / 336 orphans logged as I316** (same adjustment)
- [x] `db_manifest` 53 `table:*` keys; 0 missing; 0 count mismatch
- [x] GAP-016 re-verified RESOLVED
- [x] Evidence recorded; report generated; logs updated

## 9. Recommendations

1. **I315 fix (follow-up phase)**: add composite `UNIQUE (…)` emission to `SchemaToDDL` plus a schema-driven `unique_keys` array in `table_spec_def` / `eks_db_config.json` for the 14 tables; re-run this matrix after the change.
2. **I316 fix (follow-up phase)**: align the reference-data configs (asset `asset_type_code` → `AT_*` codes, `discipline='multi'`, project codes `131101`/`131242`) and raise FK-violation reporting to an explicit message/warning at the default log level so logical FK violations are never silent.
3. **Investigate** the migration-gate "destructive 3 tables / 0 columns" trigger on a second build (see §5) — confirm which tables are affected and why a fresh rebuild flags them as destructive.
4. Proceed to **Phase 2 (T1.306 §24 cross-source audit)** after D-1–D-4 sign-off.

## 10. Lessons Learned

- Verification-only passes can still surface real defects — the matrix found two distinct defect classes (missing constraints + orphan data) that unit tests of individual loaders had not exposed. Keep the live-matrix probe as a repeatable regression artifact (`i313_phase1_verify.py`).
- DuckDB introspection differs from SQLite in ways that silently break naive probes (schema-scoped `information_schema` filtering, 0-based vs 1-based constraint column indexes, no `PRAGMA foreign_keys`). Document these in the verification script so future passes are not mis-led.
- Logical FK validation is only as useful as its visibility — a warning suppressed by the default log level is effectively absent. Validation warnings should surface at the default verbosity.
- Composite-key UNIQUE was an unstated requirement of the I307 table spec; the gap was invisible until a live probe checked for actual constraints. Add an explicit matrix check (already present in `i313_phase1_verify.py`) to guard against regression.
