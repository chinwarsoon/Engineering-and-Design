# Archive Cleanup Proposal

**Date:** 2026-04-24  
**Status:** PENDING APPROVAL  
**Scope:** Identify files to archive and consolidate legacy/deprecated items

---

## Executive Summary

After reviewing `dcc_engine_pipeline.py` and related files, identified **deprecated patterns, legacy schema formats, and outdated test files** that should be moved to archive. This cleanup will streamline the active codebase and reduce confusion.

---

## 1. Current Archive Status

### Existing Archive Structure
```
dcc/archive/
├── Log/                          # (1 item)
├── config/
│   ├── common_json_tools.py     # Old JSON tool implementation
│   └── schemas/
│       ├── archive/             # (18 legacy schema files)
│       └── backup/               # (8 backup schema files)
├── tracer/                      # (57 items) - Code tracer moved from dcc/tracer/
├── workflow/
│   └── backup/                 # (14 items)
└── workplan/
    ├── archive/                # (1 item)
    ├── universal-column-mapping-workflow.md
    ├── universal-document-processing-workflow.md
    └── universal-processing-workflow.md
```

---

## 2. Files to Archive (Proposed)

### 2.1 Legacy Schema Files (ACTIVE → ARCHIVE)

| File | Location | Reason | Archive Destination |
|------|----------|--------|---------------------|
| `dcc_register_enhanced.json` | `config/schemas/` | Uses legacy `enhanced_schema` format | `archive/config/schemas/legacy/` |

**Evidence:**
- Code references show legacy `enhanced_schema.columns` pattern (lines 80-81 in `mapper_engine/core/engine.py`)
- Current active schema is `dcc_register_config.json` (top-level `columns` key)
- All production code has fallback support for `enhanced_schema` that can be removed post-archival

### 2.2 Legacy Test Files (ACTIVE → ARCHIVE)

| File | Location | Reason | Archive Destination |
|------|----------|--------|---------------------|
| `test_with_schema.py` | `workflow/mapper_engine/test/` | References archived `dcc_register_enhanced.json` | `archive/workflow/mapper_engine/test/` |
| `test_end_to_end.py` | `workflow/mapper_engine/test/` | References archived schema + hardcoded paths | `archive/workflow/mapper_engine/test/` |
| `update_schema.py` | `workflow/mapper_engine/test/` | Legacy schema update utility | `archive/workflow/mapper_engine/test/` |

**Evidence:**
```python
# test_with_schema.py:37-40
with open('/workspaces/Engineering-and-Design/dcc/config/schemas/dcc_register_enhanced.json', 'r') as f:
    schema = json.load(f)
aliases = schema['enhanced_schema']['columns']['Review_Return_Plan_Date']['aliases']
```

### 2.3 Deprecated Code Patterns (MARK FOR REMOVAL)

**In `workflow/processor_engine/core/engine.py`:**
```python
# Lines 65-66 - Legacy fallback support
# Support new top-level 'columns' key and legacy 'enhanced_schema.columns'
_schema_root = schema_data if 'columns' in schema_data else schema_data.get('enhanced_schema', {})
```

**In `workflow/mapper_engine/core/engine.py`:**
```python
# Lines 80-81 - Legacy fallback support
# Support new top-level 'columns' key and legacy 'enhanced_schema.columns'
_schema_root = self.resolved_schema if 'columns' in self.resolved_schema else self.resolved_schema.get('enhanced_schema', {})
```

**In `workflow/processor_engine/core/base.py`:**
```python
# Lines 44-47 - Legacy _data suffix support
# Legacy: _data suffix keys (e.g., schema_data['approval_code_schema_data'])
```

### 2.4 Deprecated Methods (MARK FOR REMOVAL)

| Method | File | Status | Action |
|--------|------|--------|--------|
| `apply_null_handling()` | `processor_engine/core/engine.py` | [DEPRECATED for direct use] | Remove after verifying no external calls |
| `apply_calculations()` | `processor_engine/core/engine.py` | [DEPRECATED for direct use] | Remove after verifying no external calls |
| `set_debug_mode()` | `initiation_engine/utils/logging.py` | Legacy debug mode setter | Mark for removal in v2.0 |
| `debug_print()` | `initiation_engine/utils/logging.py` | Legacy debug print | Mark for removal in v2.0 |
| `status_print()` | `initiation_engine/utils/logging.py` | Legacy status print | Keep for backward compat (actively used) |

### 2.5 Legacy Workplan Files (ACTIVE → ARCHIVE)

| File | Location | Reason | Archive Destination |
|------|----------|--------|---------------------|
| `universal-column-mapping-workflow.md` | `workplan/` | Superseded by newer workplans | `archive/workplan/legacy/` |
| `universal-document-processing-workflow.md` | `workplan/` | Superseded by newer workplans | `archive/workplan/legacy/` |
| `universal-processing-workflow.md` | `workplan/` | Superseded by newer workplans | `archive/workplan/legacy/` |

---

## 3. Files to Update (Post-Archive Cleanup)

### 3.1 Remove Legacy Fallback Code

| File | Lines | Change |
|------|-------|--------|
| `processor_engine/core/engine.py` | 65-66 | Remove `enhanced_schema` fallback |
| `processor_engine/core/engine.py` | 163-165 | Remove `enhanced_schema.column_sequence` fallback |
| `mapper_engine/core/engine.py` | 80-81 | Remove `enhanced_schema` fallback |
| `mapper_engine/mappers/detection.py` | 150-153 | Remove `_data` suffix fallback |
| `schema_engine/validator/schema_validator.py` | 57-58 | Remove `enhanced_schema` fallback |
| `processor_engine/core/base.py` | 44-47, 80-82 | Remove `_data` suffix fallback |
| `processor_engine/error_handling/detectors/identity.py` | 199-200, 262-263, 301-302 | Remove `enhanced_schema` fallback |
| `processor_engine/schema/processor.py` | 21-22 | Remove `enhanced_schema` fallback |
| `initiation_engine/core/validator.py` | 147-157 | Remove legacy `project_setup` format handling |

### 3.2 Update References

| File | Current | Update To |
|------|---------|-----------|
| All test files | `dcc_register_enhanced.json` | `dcc_register_config.json` |
| Documentation | `enhanced_schema['columns']` | `columns` (top-level) |

---

## 4. Implementation Plan

### Phase 1: Archive Files (30 min)
1. Create `archive/config/schemas/legacy/` folder
2. Move `dcc_register_enhanced.json` → `archive/config/schemas/legacy/`
3. Create `archive/workflow/mapper_engine/test/` folder
4. Move 3 test files → archive
5. Create `archive/workplan/legacy/` folder
6. Move 3 workplan files → archive

### Phase 2: Remove Legacy Fallbacks (2 hours)
1. Update `processor_engine/core/engine.py` - 3 locations
2. Update `mapper_engine/core/engine.py` - 1 location
3. Update `mapper_engine/mappers/detection.py` - 1 location
4. Update `schema_engine/validator/schema_validator.py` - 1 location
5. Update `processor_engine/core/base.py` - 2 locations
6. Update `processor_engine/error_handling/detectors/identity.py` - 3 locations
7. Update `processor_engine/schema/processor.py` - 1 location
8. Update `initiation_engine/core/validator.py` - 1 location

### Phase 3: Test & Verify (1 hour)
1. Run pipeline with current schema
2. Verify no `enhanced_schema` references remain in active code
3. Verify all tests pass (remaining active tests)
4. Verify `dcc_register_config.json` loads correctly

### Phase 4: Documentation (30 min)
1. Update `processor_engine/readme.md` - Remove deprecated method warnings
2. Update `mapper_engine/readme.md` - Remove `enhanced_schema` references
3. Update `schema_engine/readme.md` - Remove `_data` suffix references
4. Create migration guide for future schema changes

---

## 5. Impact Assessment

### Risk Level: **LOW**

**Rationale:**
- All production code uses new `columns` top-level format
- Legacy fallbacks are defensive code only, never executed with current schemas
- Test files that use legacy format are standalone scripts, not part of CI/CD
- Archive folder already exists and is in active use

### Breaking Changes: **NONE**

No breaking changes for production use. Only removes:
- Unused defensive code paths
- Outdated test files
- Superseded workplan documentation

---

## 6. Files Summary

| Category | Count | Action |
|----------|-------|--------|
| Schema files to archive | 1 | Move to `archive/config/schemas/legacy/` |
| Test files to archive | 3 | Move to `archive/workflow/mapper_engine/test/` |
| Workplan files to archive | 3 | Move to `archive/workplan/legacy/` |
| Code files to update | 8 | Remove legacy fallback code |
| Documentation to update | 3 | Remove legacy references |

**Total effort:** ~4 hours  
**Total files affected:** 18 (3 moved, 8 updated, 3 docs, 4 new archive folders)

---

## 7. Post-Cleanup Benefits

1. **Cleaner codebase** - No dead code paths
2. **Faster loading** - No fallback checks for non-existent legacy formats
3. **Less confusion** - New developers won't see dual-format support
4. **Smaller repository** - Archive folder contains only truly legacy items
5. **Clearer documentation** - No references to deprecated formats

---

**Awaiting approval to proceed with Phase 1.**
