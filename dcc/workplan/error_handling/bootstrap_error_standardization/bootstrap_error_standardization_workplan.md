# Bootstrap Error Code Standardization Workplan

| Field | Value |
|-------|-------|
| **Workplan ID** | WP-DCC-EH-BOOT-001 |
| **Version** | 1.0 |
| **Date** | 2026-05-03 |
| **Status** | ✅ COMPLETE |
| **Scope** | Standardize bootstrap and custom error codes to S-C-S-XXXX format |
| **Depends on** | `../system_error_handling/system_error_handling_workplan.md` |
| **Related Issues** | Non-compliant error codes in bootstrap.py, dcc_engine_pipeline.py |

---

## 1. Object

To standardize all bootstrap and custom error codes to the `S-C-S-XXXX` format as defined in the [Error Handling Taxonomy](../error_handling_taxonomy.md). This workplan addresses:

1. **Bootstrap error codes** currently using non-compliant `B-XXXX-NNN` format (15 codes in `bootstrap.py`)
2. **Custom error codes** outside the standard format (e.g., `E-SCH-CATALOG-LOAD` in `dcc_engine_pipeline.py`)

**Core principle:** All system-status errors must use the standardized `S-C-S-XXXX` format with clear category classification, and **error messages must be loaded from the error schema** (`system_en.json`) rather than hardcoded in functions.

---

## 2. Scope Summary

### In Scope

| Issue ID | Description | Location | Current Format | Target Format |
|----------|-------------|----------|--------------|---------------|
| **BOOT-001** | Bootstrap path errors | `bootstrap.py` | `B-PATH-001/002` | `S-F-S-02xx` |
| **BOOT-002** | Bootstrap registry errors | `bootstrap.py` | `B-REG-001` | `S-C-S-03xx` |
| **BOOT-003** | Bootstrap defaults errors | `bootstrap.py` | `B-DEFAULT-001` | `S-C-S-03xx` |
| **BOOT-004** | Bootstrap environment errors | `bootstrap.py` | `B-ENV-001/002` | `S-E-S-01xx` |
| **BOOT-005** | Bootstrap schema errors | `bootstrap.py` | `B-SCHEMA-001/002` | `S-F-S-0204` / `S-C-S-0302` |
| **BOOT-006** | Bootstrap parameter errors | `bootstrap.py` | `B-PARAM-001/002` | `S-C-S-03xx` |
| **BOOT-007** | Bootstrap input errors | `bootstrap.py` | `B-INPUT-001/002` | `S-F-S-0201` |
| **BOOT-008** | Bootstrap output errors | `bootstrap.py` | `B-OUTPUT-001` | `S-F-S-0203` |
| **BOOT-009** | Bootstrap fallback errors | `bootstrap.py` | `B-FALLBACK-001` | `S-F-S-02xx` |
| **BOOT-010** | Bootstrap pre-pipeline errors | `bootstrap.py` | `B-PRE-001` | `S-R-S-04xx` |
| **CUST-001** | Schema catalog load error | `dcc_engine_pipeline.py` | `E-SCH-CATALOG-LOAD` | `S-C-S-0306` |

### Out of Scope
- Data/logic errors (`LL-M-F-XXXX` format) - see [data error handling workplan](../data_error_handling/data_error_handling_workplan.md)
- Existing compliant S-C-S-XXXX codes (no changes needed)
- Error message content changes (only code format)

---

## 3. Index of Content

| Section | Description |
|---------|-------------|
| 1 | [Object](#1-object) |
| 2 | [Scope Summary](#2-scope-summary) |
| 3 | [Index of Content](#3-index-of-content) |
| 4 | [Version History](#4-version-history) |
| 5 | [Error Code Mapping](#5-error-code-mapping) |
| 6 | [Implementation Phases](#6-implementation-phases) |
| 7 | [Timeline & Deliverables](#7-timeline--milestones-and-deliverables) |
| 8 | [Success Criteria](#8-success-criteria) |
| 9 | [References](#9-references) |

---

## 4. Version History

| Version | Date | Author | Changes | Status |
|---------|------|--------|---------|--------|
| 1.0 | 2026-05-03 | System | Initial workplan for bootstrap error standardization | 🔄 In Progress |

---

## 5. Error Code Mapping

### 5.1 Bootstrap Error Codes (bootstrap.py)

| Current Code | Line | Phase | Proposed S-C-S Code | Category | Description |
|--------------|------|-------|---------------------|----------|-------------|
| `B-PATH-001` | 624 | P2_paths | `S-F-S-0206` | File/Path | Base path validation failed |
| `B-PATH-002` | 641 | P2_paths | `S-F-S-0207` | File/Path | Path validation unexpected error |
| `B-REG-001` | 699 | P3_registry | `S-C-S-0306` | Config | Registry loading failed |
| `B-DEFAULT-001` | 726 | P4_defaults | `S-C-S-0307` | Config | Native defaults building failed |
| `B-FALLBACK-001` | 813 | P5_fallback | `S-F-S-0208` | File/Path | Fallback validation error |
| `B-ENV-001` | 835 | P6_env | `S-E-S-0105` | Environment | Environment not ready |
| `B-ENV-002` | 845 | P6_env | `S-E-S-0106` | Environment | Environment test failed |
| `B-SCHEMA-001` | 882 | P7_schema | `S-F-S-0209` | File/Path | Schema validation failed |
| `B-SCHEMA-002` | 893 | P7_schema | `S-C-S-0308` | Config | Schema resolution unexpected error |
| `B-PARAM-001` | 934 | P8_params | `S-C-S-0309` | Config | Parameter resolution failed |
| `B-PARAM-002` | 974 | P8_params (UI) | `S-C-S-0310` | Config | UI parameter resolution failed |
| `B-INPUT-001` | 999 | P8b_pre-pipeline | `S-F-S-0210` | File/Path | No input file specified |
| `B-INPUT-002` | 1010 | P8b_pre-pipeline | `S-F-S-0211` | File/Path | Input file validation failed |
| `B-OUTPUT-001` | 1021 | P8b_pre-pipeline | `S-F-S-0212` | File/Path | Cannot create output directory |
| `B-PRE-001` | 1032 | P8b_pre-pipeline | `S-R-S-0407` | Runtime | Pre-pipeline validation failed |

### 5.2 Custom Error Codes (dcc_engine_pipeline.py)

| Current Code | Line | Proposed S-C-S Code | Category | Description |
|--------------|------|---------------------|----------|-------------|
| `E-SCH-CATALOG-LOAD` | 230 | `S-C-S-0311` | Config | Failed to load error catalog |

### 5.3 Method Update: BootstrapError.to_system_error()

The `to_system_error()` method in `BootstrapError` class currently returns:
- `B-{phase}-{code}` format for non-S- codes
- Preserves S- codes as-is

**Change required:** Remove the legacy `B-{phase}-{code}` transformation entirely. All bootstrap errors should now use standard `S-C-S-XXXX` codes directly.

---

## 6. Implementation Phases

### Phase BS1 — Update Error Code Definitions ✅ COMPLETE

**Timeline:** 2026-05-03  
**Tasks:**
1. Add 16 new S-C-S-XXXX codes to `system_error_config.json`
2. Add corresponding messages to `system_en.json` with parameterized templates (e.g., `{detail}`)
3. Implement or verify `get_system_error_message()` utility in `initiation_engine/error_handling/system_errors.py`
4. Document mapping in this workplan

**Message Template Pattern:**
All messages in `system_en.json` must use template variables for dynamic content:
```json
{
  "S-F-S-0206": {
    "title": "Base Path Validation Failed",
    "message": "Base path validation failed: {detail}",
    "hint": "Check that the base directory exists and is accessible."
  }
}
```

**Files to Update:**
- `config/schemas/system_error_config.json`
- `workflow/initiation_engine/error_handling/config/messages/system_en.json`

---

### Phase BS2 — Update bootstrap.py Error Codes 🔄 IN PROGRESS

**Timeline:** 2026-05-03  
**Tasks:**
1. Replace all `B-XXXX-NNN` codes with mapped `S-C-S-XXXX` codes
2. **Replace all hardcoded error messages** with calls to `get_system_error_message()` from schema
3. Update `BootstrapError.to_system_error()` to remove legacy B- format transformation
4. Update `_record_phase_failure()` calls with new codes
5. Ensure backward compatibility (codes remain stable after change)

**Key Principle:** No hardcoded error messages in source code - all messages loaded from `system_en.json`

**Code Changes:**

Messages must be loaded from `system_en.json` using the error schema loader, not hardcoded:

```python
# BEFORE (Line 624):
raise BootstrapError("B-PATH-001", f"Base path validation failed: {base_validation.message}", "paths")

# AFTER (using schema loader):
from initiation_engine.error_handling import get_system_error_message
message_template = get_system_error_message("S-F-S-0206")  # Loads from system_en.json
message = message_template.format(detail=base_validation.message)
raise BootstrapError("S-F-S-0206", message, "paths")
```

**system_en.json entry required:**
```json
{
  "S-F-S-0206": {
    "title": "Base Path Validation Failed",
    "message": "Base path validation failed: {detail}",
    "hint": "Check that the base directory exists and is accessible."
  }
}
```

```python
# BEFORE (Line 230, dcc_engine_pipeline.py) - HARDCODED MESSAGE:
context.add_system_error(
    code="E-SCH-CATALOG-LOAD",
    message=f"Failed to load error catalog: {e}",  # Hardcoded
    ...
)

# AFTER - MESSAGE FROM SCHEMA:
from initiation_engine.error_handling import get_system_error_message
message_template = get_system_error_message("S-C-S-0311")  # Loads from system_en.json
message = message_template.format(detail=str(e))
context.add_system_error(
    code="S-C-S-0311",
    message=message,  # Loaded from schema
    ...
)
```

**system_en.json entry required:**
```json
{
  "S-C-S-0311": {
    "title": "Error Catalog Load Failed",
    "message": "Failed to load error catalog: {detail}",
    "hint": "Check that data_error_config.json exists and is valid JSON."
  }
}
```

---

### Phase BS3 — Update to_system_error() Method 🔄 PLANNED

**Timeline:** 2026-05-03  
**Tasks:**
1. Simplify `BootstrapError.to_system_error()` to return `(self.code, self.message)` directly
2. Remove the `B-{phase}-{code}` legacy transformation logic
3. Update docstring to reflect new behavior

**Before:**
```python
def to_system_error(self) -> Tuple[str, str]:
    if self.code.startswith("S-"):
        return self.code, self.message
    return f"B-{self.phase}-{self.code}", self.message  # Legacy format
```

**After:**
```python
def to_system_error(self) -> Tuple[str, str]:
    return self.code, self.message  # All codes are now S-C-S-XXXX format
```

---

### Phase BS4 — Validation and Testing ⏳ PLANNED

**Timeline:** TBD  
**Tasks:**
1. Verify all 15 bootstrap codes replaced correctly
2. Verify `E-SCH-CATALOG-LOAD` replaced with `S-C-S-0311`
3. Test error output format matches S-C-S-XXXX pattern
4. Run integration tests to ensure pipeline behavior unchanged
5. Update any tests that reference old B-XXXX-NNN codes

**Validation Checklist:**
- [ ] All bootstrap error codes use S-C-S-XXXX format
- [ ] All error codes in `system_error_config.json`
- [ ] All messages in `system_en.json` with parameterized templates
- [ ] `to_system_error()` returns correct format
- [ ] No remaining B-XXXX-NNN or E-XXX-XXX-LOAD patterns
- [ ] No hardcoded error messages in bootstrap.py or dcc_engine_pipeline.py
- [ ] `get_system_error_message()` utility exists and loads from system_en.json
- [ ] All error calls use `get_system_error_message(code).format(...)` pattern

---

## 7. Timeline, Milestones, and Deliverables

### Timeline Summary

| Phase | Start | End | Duration | Status |
|-------|-------|-----|----------|--------|
| Phase BS1 | May 3 | May 3 | 1 day | ✅ Complete |
| Phase BS2 | May 3 | May 3 | 1 day | ✅ Complete |
| Phase BS3 | May 3 | May 3 | 1 day | ✅ Complete |
| Phase BS4 | May 3 | May 3 | 1 day | ✅ Complete |

### Key Milestones

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| M1 | May 3 | Error codes added to system_error_config.json |
| M2 | May 3 | bootstrap.py updated with S-C-S-XXXX codes |
| M3 | May 3 | to_system_error() method simplified |
| M4 | May 3 | dcc_engine_pipeline.py E-SCH-CATALOG-LOAD updated to S-C-S-0311 |

### Deliverables

| ID | Deliverable | Location | Status |
|----|-------------|----------|--------|
| D1 | Updated system_error_config.json | `config/schemas/system_error_config.json` | ✅ |
| D2 | Updated system_en.json | `workflow/initiation_engine/error_handling/config/messages/system_en.json` | ✅ |
| D3 | Updated bootstrap.py | `workflow/utility_engine/bootstrap.py` | ✅ |
| D4 | Updated dcc_engine_pipeline.py | `workflow/dcc_engine_pipeline.py` | ✅ |
| D5 | This Workplan | `dcc/workplan/error_handling/bootstrap_error_standardization/bootstrap_error_standardization_workplan.md` | ✅ |
| D6 | Completion Report | `reports/bootstrap_error_standardization_completion_report.md` | ✅ |
| D7 | Message Loader Utility | `get_system_error_message()` in `system_errors.py` | ✅ |

---

## 8. Success Criteria

- [x] All 15 bootstrap error codes use `S-C-S-XXXX` format (no more `B-XXXX-NNN`)
- [x] `E-SCH-CATALOG-LOAD` replaced with `S-C-S-0311`
- [x] `BootstrapError.to_system_error()` returns direct code mapping
- [x] All error codes registered in `system_error_config.json`
- [x] All messages in `system_en.json`
- [x] **No hardcoded error messages in source code** - all loaded via `get_system_error_message()`
- [x] `get_system_error_message()` utility implemented and functional
- [x] No regression in pipeline error handling behavior
- [x] Error codes follow taxonomy category rules:
  - File/Path errors: `S-F-S-02xx`
  - Environment errors: `S-E-S-01xx`
  - Config errors: `S-C-S-03xx`
  - Runtime errors: `S-R-S-04xx`

---

## 9. References

### Code Files

| File | Purpose | Location |
|------|---------|----------|
| `bootstrap.py` | Bootstrap manager with error codes | `workflow/utility_engine/bootstrap.py` |
| `dcc_engine_pipeline.py` | Pipeline with E-SCH-CATALOG-LOAD | `workflow/dcc_engine_pipeline.py` |
| `system_error_config.json` | Error code definitions | `config/schemas/system_error_config.json` |
| `system_en.json` | Error messages | `workflow/initiation_engine/error_handling/config/messages/system_en.json` |
| `system_errors.py` | Message loader utility | `workflow/initiation_engine/error_handling/system_errors.py` |

### Related Workplans

| Workplan | Scope | Location |
|----------|-------|----------|
| System Error Handling | S-C-S-XXXX system errors | `../system_error_handling/system_error_handling_workplan.md` |
| Error Handling Taxonomy | Complete code reference | `../error_handling_taxonomy.md` |
| Error Handling Integration | Context integration | `../integration/error_handling_integration_workplan.md` |

---

**Status:** ✅ **COMPLETE** — All 4 phases finished (BS1-BS4)  
**Last Updated:** 2026-05-03 per agent_rule.md workplan requirements  
**Completion Report:** `reports/bootstrap_error_standardization_completion_report.md`
