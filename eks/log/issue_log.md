# EKS Issue Log

**Project**: Engineering Knowledge System (EKS)  
**Location**: `eks/log/issue_log.md`  
**Last Updated**: 2026-06-19  

---

## Issue Log Table

| ID | Date | Phase | Severity | Title | Description | Status | Resolution |
| :- | :--- | :---- | :------: | :---- | :---------- | :----: | :--------- |
| I001 | 2026-06-15 | Phase 1 | 🟠 High | Missing `__init__.py` files in engine packages | `engine/__init__.py`, `engine/core/__init__.py`, `engine/parsers/__init__.py`, `engine/logging/__init__.py` not created per agent_rule §4.2 and workplan Section 9. Imports work via implicit namespace packages, but convention violated. | ✅ Resolved | Created 4 `__init__.py` files with import statements and version info (U011) |
| I002 | 2026-06-15 | Phase 1 | 🟠 High | Missing Phase 1 test report | `eks/workplan/reports/phase_1_foundation_report.md` not created per workplan Section 13 and agent_rule §9. Reports folder contains only `.gitkeep`. | ✅ Resolved | Generated `phase_1_foundation_report.md` (U014) |
| I003 | 2026-06-15 | Phase 1 | 🟡 Medium | Deprecated `jsonschema.RefResolver` API | `schema_loader.py:7` and `verify_schema_metadata.py:3` use deprecated `RefResolver` (deprecated since jsonschema v4.18.0). Runtime deprecation warning emitted. | ✅ Resolved | Migrated to `referencing` library API (U012) |
| I004 | 2026-06-15 | Phase 1 | 🟢 Low | Schema metadata fields in `properties` | `eks_setup_schema.json` lists `$schema, $id, version, title, description` as data properties. These are schema metadata keywords, not config data. Validates correctly but semantically imprecise. | ✅ Resolved | U013 removed these fields from `eks_setup_schema.json` properties; config strips them before validation. Confirmed in v0.9 workplan review. |
| I005 | 2026-06-18 | Phase 1 | 🟢 Low | `eks_config.json` contains placeholder project data | `project_rules_registry` and `discipline_registry` contain dummy entries (P123, P456) — test data from initial implementation. Not a blocker but misleading for future developers. | ⏸️ Deferred | Entries clearly labelled as examples in config comment. Replace with WSD11 real project data when project discipline list is confirmed. |
| I006 | 2026-06-16 | Phase 1 | 🟠 High | Document Registry Technical Gaps (G1-G3) & Extended Metadata | Critical gaps identified in Phase 1 registry: missing `source_type` (G1) for P&ID references; SQL injection risk in filters (G2); Python-side sorting in `get_revision_history` (G3). Added 11 extended metadata fields for extraction/verification workflow. | ✅ Resolved | Fixed in T1.21/T1.22: Added `source_type` and 11 extended fields to schema/DB; implemented COLUMN_ALLOWLIST for filters; migrated sorting to SQL ORDER BY; added JSON array support for asset_tags. |
| I007 | 2026-06-18 | Phase 1 | 🟠 High | Ontology Schema Refactor to Triple-File Pattern | `eks_ontology_schema.json` did not follow the Base/Setup/Config pattern required by `agent_rule.md`. Modular inheritance was missing. | ✅ Resolved | Split into `eks_ontology_base_schema.json` and `eks_ontology_setup_schema.json` with explicit `allOf` inheritance. Updated `SchemaLoader`. |
| I008 | 2026-06-18 | Phase 1 | 🟡 Medium | Inconsistent Ontology Config Filename | `eks_ontology.json` name was inconsistent with the `_config.json` suffix used by other schema components. | ✅ Resolved | Renamed to `eks_ontology_config.json` and updated all internal/external references across code, tests, and docs. |
| I009 | 2026-06-19 | Phase 3 Prep | 🟠 High | Pre-ingestion metadata extraction gap — 572 TWRP documents not registered | Document registry contains 7 test records only; 0 of 572 real TWRP documents ingested. 7 components missing before bulk ingestion can proceed: (1) FilenameParser — extract discipline/doc_type/area/doc_number from filenames; (2) CoverSheetParser — extract 8 fields from PDF cover sheets (Type A/B/D/E); (3) ScannedPDFHandler — detect/handle Type C image-only PDFs; (4) DatadropCrossRef — fuzzy match asset_tags to datadrop KEYTAGs; (5) WSD11 project config — replace P123/P456 placeholders (linked to I005); (6) Bulk ingestion script — walk directory tree, register all documents; (7) Extraction confidence scoring — compute quality score per document. | ⏸️ Deferred | To be evaluated as sub-phase workplan for Phase 3. Blocks Phase 3 bulk ingestion. See Appendix B B6.3 for TWRP ingestion steps. |

---

## Severity Legend
- 🔴 Critical — blocks phase completion
- 🟠 High — significant impact, workaround needed
- 🟡 Medium — moderate impact, can proceed
- 🟢 Low — minor, cosmetic, or deferred
