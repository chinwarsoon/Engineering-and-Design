# EKS Issue Log

**Project**: Engineering Knowledge System (EKS)  
**Location**: `eks/log/issue_log.md`  
**Last Updated**: 2026-06-15  

---

## Issue Log Table

| ID | Date | Phase | Severity | Title | Description | Status | Resolution |
| :- | :--- | :---- | :------: | :---- | :---------- | :----: | :--------- |
| I001 | 2026-06-15 | Phase 1 | 🟠 High | Missing `__init__.py` files in engine packages | `engine/__init__.py`, `engine/core/__init__.py`, `engine/parsers/__init__.py`, `engine/logging/__init__.py` not created per agent_rule §4.2 and workplan Section 9. Imports work via implicit namespace packages, but convention violated. | ✅ Resolved | Created 4 `__init__.py` files with import statements and version info (U011) |
| I002 | 2026-06-15 | Phase 1 | 🟠 High | Missing Phase 1 test report | `eks/workplan/reports/phase_1_foundation_report.md` not created per workplan Section 13 and agent_rule §9. Reports folder contains only `.gitkeep`. | ✅ Resolved | Generated `phase_1_foundation_report.md` (U014) |
| I003 | 2026-06-15 | Phase 1 | 🟡 Medium | Deprecated `jsonschema.RefResolver` API | `schema_loader.py:7` and `verify_schema_metadata.py:3` use deprecated `RefResolver` (deprecated since jsonschema v4.18.0). Runtime deprecation warning emitted. | ✅ Resolved | Migrated to `referencing` library API (U012) |
| I004 | 2026-06-15 | Phase 1 | 🟢 Low | Schema metadata fields in `properties` | `eks_setup_schema.json` lists `$schema, $id, version, title, description` as data properties. These are schema metadata keywords, not config data. Validates correctly but semantically imprecise. | ⏸️ Deferred | Low priority — validation works correctly; revisit during Phase 2 |

---

## Severity Legend
- 🔴 Critical — blocks phase completion
- 🟠 High — significant impact, workaround needed
- 🟡 Medium — moderate impact, can proceed
- 🟢 Low — minor, cosmetic, or deferred
