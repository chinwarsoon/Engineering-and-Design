# EKS Phase 2 — I313 Phase 2 (T1.306) — §24 Cross-Source Audit + Doc/Schema Drift Fix — Test Report

**Report ID**: RP-EKS-P1-I313-AUDIT-24
**Current Version**: 1.0
**Status**: ✅ COMPLETE (audit executed; D1–D6 + O1 closed; validation green)
**Last Updated**: 2026-08-14
**Parent Workplan**: [i313_audit_verification_workplan.md](../i313_audit_verification_workplan.md) — Phase 2 (T1.306). Issue: **I313** — Audit & verification (materialization matrix, §24 cross-source audit, output-name schema coverage, full test suite).

## 1. Test Objective

Execute the **§24 cross-source alignment audit** for the schema-driven DB-layer concept set (I306 umbrella) and close every flagged drift in one grep-driven edit cycle (AGENTS §12). Every concept that spans 5+ independent sources must agree across all sources on: version numbers, view column counts/formats, FK names, FK source columns, and the `db_manifest` provenance table documentation. The audit is **fixing** (unlike Phase 1, which was verification-only): stale documentation references and schema-declaration drifts are corrected in the same edit cycle they were identified.

## 2. Scope

- **In scope (drift fixes)**:
  - **D1** — `appendix_b_document_registry.md:1023,1066` — `review_flags` export formats `csv` → `csv + xlsx`.
  - **D2** — `appendix_b_document_registry.md:1021` + `appendix_b.2_db_table_design.md:1333` — `extraction_results` columns 49 → 50.
  - **D3** — 5 current-state stale `eks_export_view_config.json v1.1.0` references → **v1.2.0**.
  - **D4** — `eks_doc_base_schema.json:1656–1726` — 6 `registry_relations` descriptions: legacy FK names → actual config FK names.
  - **D5** — `eks_doc_base_schema.json:1689` — `fk_project_code` `source_columns` → `["project_definition"]`.
  - **D6** — `eks_doc_base_schema.json:1643–1656` — `fk_doc_type_composite` downgrade from composite to single-column per decision **D-2 option (b)**.
  - **O1** — document `db_manifest` in `appendix_b.2_db_table_design.md` metadata-table list (successor of `_eks_schema_meta`).
- **Version-alignment matrix** cross-referenced into this report (base 1.22.0, setup 1.13.0, db_config 1.1.1, view 1.2.0, doc_base 1.21.0, doc_config 1.14.0, eks_config 1.14.0, error `total_codes` 140).
- **Out of scope**: O3 (runtime version-mismatch warning — optional hardening, deferred); Phase 3 output-name literal removal (T1.307, BLOCK-1–4); Phase 4 full-suite closure (T1.308). Decision D-1 (keep 53 tables incl. `_eks_table_relations`) and D-3 (phase1_server filter alignment) are deferred to Phase 3.

## 3. Test Execution Summary

| Audit item | Coverage | Result |
| :--------- | :------- | :----: |
| D1 review_flags formats | 2 doc sites → `csv + xlsx` (matches config `formats` = 2) | ✅ FIXED |
| D2 extraction_results columns | 2 doc sites 49 → 50 (matches config `columns` count = 50) | ✅ FIXED |
| D3 view-config version refs | 5 current-state sites v1.1.0 → v1.2.0 | ✅ FIXED |
| D4 legacy FK description names | 6 descriptions → actual config FK names | ✅ FIXED |
| D5 fk_project_code source column | `["project_code"]` → `["project_definition"]` | ✅ FIXED |
| D6 fk_doc_type_composite shape | composite → single-column (D-2 option b) | ✅ FIXED |
| O1 db_manifest documentation | GROUP 12 lists + TABLE SUMMARY in B.2 | ✅ FIXED |
| Version-pin tests | `test_i307_db_schema_set`, `test_t132_modules`, `test_i308_default_views`, `test_i309_exports` | ✅ 139 PASS |
| registry_relations consumers | `test_i291`, `test_phase1` (manifest), `test_i310_materialization` | ✅ 8 PASS |
| Schema validation | `eks_doc_base_schema.json` valid JSON; SchemaLoader load OK | ✅ PASS |
| Post-fix grep | zero current-state stale `v1.1.0` / `49 columns` / legacy `fk_*` refs | ✅ PASS |

## 4. Version-Alignment Matrix (§24)

Cross-referenced across schema files, config files, and docs. All sources agree on the pinned versions below.

| Concept | Version / Value | Sources checked | Agrees |
| :------ | :-------------- | :-------------- | :----: |
| eks_base_schema.json | 1.22.0 | config `version`, setup `$ref`, version-pin test (`test_t132_modules`) | ✅ |
| eks_setup_schema.json | 1.13.0 | config `version`, doc_base `$ref`, version-pin test | ✅ |
| eks_db_config.json | 1.1.1 | config `version`, `test_i307_db_schema_set`, Phase 1 report | ✅ |
| eks_export_view_config.json | **1.2.0** | config `version`, docs (D3 fix), `test_i308_default_views` | ✅ |
| eks_doc_base_schema.json | 1.21.0 | config `version`, `test_t132_modules:897` pin | ✅ |
| eks_doc_config.json | 1.14.0 | config `version`, version-pin test | ✅ |
| eks_config.json | 1.14.0 | config `version`, version-pin test | ✅ |
| error `total_codes` | 140 | `eks_error_config.json` + catalog | ✅ |

**View-shape agreement (D1/D2 verified against `eks_export_view_config.json` v1.2.0):**

| View ID (`view_id` = `export_artifact.artifact_type`) | Columns (config) | Formats (config) | Docs after fix |
| :------ | :---------------- | :--------------- | :------------- |
| `discovery_inventory` | 46 | csv + xlsx | 46 — matches |
| `extraction_results` | **50** | csv + xlsx | 50 — matches (D2) |
| `review_flags` | 12 | csv + xlsx | 12, csv + xlsx — matches (D1) |

**FK name agreement (D4 — `registry_relations` description → config `db_tables[documents].foreign_keys[].fk_name`):**

| `registry_relations` relation | Description referenced (legacy) | Actual config FK name | Fixed to |
| :------ | :------------------------------- | :-------------------- | :------- |
| `fk_doc_type_composite` | `fk_doc_pdt` | `fk_doc_type_composite` | ✅ |
| `fk_supersedes` | `fk_doc_supersedes` | `fk_supersedes` | ✅ |
| `fk_superseded_by` | `fk_doc_superseded_by` | `fk_superseded_by` | ✅ |
| `fk_project_code` | `fk_doc_project_def` | `fk_project_code` | ✅ |
| `fk_discipline` | `fk_doc_discipline` | `fk_discipline` | ✅ |
| `fk_file_type` | `fk_doc_filetype` | `fk_file_type` | ✅ |

**FK source-column agreement (D5 — `fk_project_code`):**

| Source | `source_columns` / `column` |
| :----- | :-------------------------- |
| Config `eks_db_config.json` `fk_project_code` | `documents.project_definition` |
| `eks_doc_base_schema.json` `fk_project_code` **after D5** | `["project_definition"]` |
| Live `documents` schema | has both `project_code` and `project_definition` columns | ✅ AGREED |

## 5. Detailed Results

### 5.1 D1 — `review_flags` formats csv → csv + xlsx (2 sites)

`eks_export_view_config.json` v1.2.0 declares `review_flags.formats` = 2 items (csv + xlsx). Docs still claimed csv-only.

| Site | Before | After |
| :--- | :----- | :---- |
| `appendix_b_document_registry.md:1023` (outputs list) | `review_flags.csv` | `review_flags.csv/.xlsx` |
| `appendix_b_document_registry.md:1066` (Pipeline Export) | `and review_flags (csv)` | `and review_flags` within "(all csv + xlsx)" |

### 5.2 D2 — `extraction_results` columns 49 → 50 (2 sites)

`eks_export_view_config.json` v1.2.0 `views[1].extraction_results.columns` = 50. Docs claimed 49.

| Site | Before | After |
| :--- | :----- | :---- |
| `appendix_b_document_registry.md:1021` (view model) | `v_extraction_results` (49 columns) | (50 columns) |
| `appendix_b.2_db_table_design.md:1333` (Column provenance) | `extraction_results: 49 ordered columns` | `50 ordered columns` |

Verified: `discovery_inventory` (46) and `review_flags` (12) were already correct — unchanged.

### 5.3 D3 — stale `eks_export_view_config.json v1.1.0` → v1.2.0 (5 current-state sites)

5 **current-state** references corrected:

| Site | Context |
| :--- | :------ |
| `appendix_b.1_cross_relationship_chart.md:1021` | GAP-016 RESOLVED row |
| `appendix_b.2_db_table_design.md:1311` | EXPORT VIEW MODEL SSOT note |
| `appendix_b_document_registry.md:16` | Doc-map SSOT entry `(I308, v1.1.0)` |
| `appendix_b_document_registry.md:1021` | Schema-driven export view model |
| `appendix_b_document_registry.md:1066` | Pipeline Export description |

**Preserved as historical records (not stale — timestamped revision history, AGENTS §13):** `appendix_b.1:13` (rev 1.7), `appendix_b.2:16` (rev 1.8), `appendix_b_document_registry.md:23` (v2.1.6 migration note), `appendix_b_document_registry.md:110` (rev 2.1.6). These document the config version at the time of the I308 change and must not be rewritten.

### 5.4 D4 — 6 legacy FK description names → actual config FK names

All 6 `registry_relations` descriptions in `eks_doc_base_schema.json` referenced legacy config FK names; the actual `eks_db_config.json` FK names equal the relation names (see §4 table). All 6 corrected; no other legacy `fk_doc_*` reference remains in the schema file (post-fix grep clean).

### 5.5 D5 — `fk_project_code` source column → `["project_definition"]`

`eks_doc_base_schema.json` declared `source_columns: ["project_code"]` but the config FK `fk_project_code` maps `documents.project_definition → project_definition.project_code`. Corrected to `["project_definition"]`; description updated to note the correction (I313 Phase 2 D5). `documents.project_definition` exists as a live column.

### 5.6 D6 — `fk_doc_type_composite` downgrade per D-2 option (b)

Config declares `fk_doc_type_composite` as a **single-column** FK (`documents.document_type → project_doc_type.local_code`), but `registry_relations` declared a composite `(project_code, document_type) → (project_code, local_code)`. Per decision D-2 option (b) (lowest risk): downgraded to single-column with a uniqueness caveat.

| Field | Before | After |
| :---- | :----- | :---- |
| `source_columns` | `["project_code", "document_type"]` | `["document_type"]` |
| `target_columns` | `["project_code", "local_code"]` | `["local_code"]` |
| `relation_type` | `composite` | `simple` |
| `description` | composite candidate-key claim | single-column + `local_code` non-UNIQUE caveat (I315) |

Rationale (D-2): `project_doc_type` has **no UNIQUE (project_code, local_code) constraint** — the table is in the I315 composite-UNIQUE gap (14 tables), so `local_code` is not guaranteed unique today (current 15 rows happen to be distinct, but nothing enforces it). A composite FK target is not enforceable; the logical lookup semantics are preserved in the description.

### 5.7 O1 — `db_manifest` documented in B.2

`db_manifest` (I312/T1.301–T1.304, schema-driven DB provenance key-value table, **replaces `_eks_schema_meta`**) was undocumented in `appendix_b.2_db_table_design.md`. Added to:
- GROUP 12 "DB Table | Schema Source | Load Method | Issue / Task" table — schema source `eks_db_config.json` → `db_tables[]`, load method `_init_db()` + `manifest.py`, issue I312.
- GROUP 12 SCHEMA SOURCE MAPPING table — with the key-value provenance row description (`config_version`, `table_stats:*`, `validation`).
- TABLE SUMMARY — new row **52. db_manifest** (GROUP 12; I312/T1.301–T1.304; replaces `_eks_schema_meta`).

## 6. Test Methodology, Environment, Tools

- **Method**: grep-driven sweep (AGENTS §12 fix-breadth) — `v1\.1\.0`, `49`/`extraction_results`, legacy `fk_doc_*` names across `eks/workplan/**/*.md` and `eks/config/schemas/*.json`; each occurrence classified as current-state (fix) vs historical revision record (preserve). Config `eks_export_view_config.json` and `eks_db_config.json` used as the SSOT for view shapes and FK specs.
- **Environment**: Windows 11, conda env `eks`, Python 3.13, DuckDB.
- **Tools**: `python -m pytest`, JSON loader (`json.load`), targeted `edit` operations (no full-file rewrites).

## 7. Test Cases, Steps, Status

| ID | Step | Expected | Result |
| :-- | :--- | :------- | :----: |
| A1 | Apply D1–D6, O1 edits | All 7 drift items corrected in one cycle | ✅ |
| A2 | `json.load` of `eks_doc_base_schema.json` | valid JSON; relation shapes correct | ✅ |
| A3 | SchemaLoader discovery/validation (`test_i307`) | 53 db_tables, 3 views, relations declared | ✅ |
| A4 | Version-pin tests (i307, t132, i308, i309) | all green | ✅ 139 PASS |
| A5 | registry_relations consumers (i291, phase1 manifest, i310) | all green | ✅ 8 PASS |
| A6 | Post-fix grep | zero current-state stale refs; only historical records remain | ✅ |
| A7 | `validate_relationships` review | reads config FK specs (unchanged); unaffected by D5/D6 | ✅ |

## 8. Test Success Criteria — Checklist

- [x] §24 audit green: every concept agrees across 5+ sources (version matrix §4).
- [x] Zero current-state stale `v1.1.0` / `49 columns` / legacy `fk_*` references remain (grep returns only historical revision records + workplan task text).
- [x] Affected tests pass (139 version-pin + 8 consumer).
- [x] Schema edits validated via SchemaLoader load.
- [x] Report generated at `<project>/workplan/reports/` (this file).
- [x] Logs updated: T1.306 complete (task log), TL060 (test log), U302 (update log), I313 issue-log note.

## 9. Files Modified (version-controlled)

| File | Change |
| :--- | :----- |
| `eks/workplan/appendix_b_document_registry.md` | D1 (2 sites), D2 (1 site), D3 (3 sites) |
| `eks/workplan/appendix_b.2_db_table_design.md` | D2 (1 site), D3 (1 site), O1 (3 additions) |
| `eks/workplan/appendix_b.1_cross_relationship_chart.md` | D3 (1 site) |
| `eks/config/schemas/eks_doc_base_schema.json` | D4 (6 descriptions), D5 (source column), D6 (relation downgrade) |
| `eks/workplan/reports/rp_eks_p1_i313_audit_24.md` | Created — this report |

## 10. Recommendations for Future Actions

1. **I315 (composite-UNIQUE gap)** — add composite `UNIQUE (natural-key columns)` emission to `SchemaToDDL` + declare a `unique_keys` array in `eks_db_config.json` for the 14 affected tables (incl. `project_doc_type`); re-run the Phase 1 matrix. Closes the D-2 caveat foundationally.
2. **I316 (FK orphan data)** — align source configs (`eks_asset_config.json` asset_type_code values, `discipline='multi'`, project codes) to registered codes; raise FK-violation reporting to an explicit message at default log level.
3. **Phase 3 (T1.307)** — proceed with output-name literal removal (BLOCK-1–4) per decisions D-3/D-4.
4. **O3 (optional)** — emit a runtime version-mismatch warning from `manifest._schema_version()` when a consumer version pin is stale, closing the post-I312 version registry gap.

## 11. Lessons Learned

- **Historical revision records must be distinguished from current-state references** when sweeping a version bump: timestamped revision-table rows (e.g., "rev 1.7: `...config.json v1.1.0`") document the version at the time of the change and must be preserved (AGENTS §13); only current-state SSOT/description/doc-map references are stale.
- **Config is the SSOT for view shapes and FK specs** — doc claims (49 columns, csv-only, legacy FK names) were confirmed stale against `eks_export_view_config.json` v1.2.0 and `eks_db_config.json` before any edit.
- **Composite vs single FK shape drift** (D6) is a schema-truth issue, not just a doc issue: `registry_relations` declared a composite candidate key that the DB does not enforce (no UNIQUE on `project_doc_type`). Downgrading to single-column with an explicit caveat keeps the schema honest until the composite-UNIQUE mechanism lands (I315).
- **One grep-driven edit cycle** (AGENTS §12) kept the 7 drift fixes coherent and verifiable with a single post-fix grep.

---
*Report generated 2026-08-14. Phase 2 (T1.306) of I313 audit & verification. Next: Phase 3 (T1.307) output-name schema coverage.*
