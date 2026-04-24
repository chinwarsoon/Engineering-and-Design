# DCC Error Handling Documentation

**Version:** 2.0  
**Last Updated:** 2026-04-24  
**Status:** All Phases Complete (1-3), Phase 4 Consolidation in Progress

---

## Quick Links

| Document | Purpose | Status |
|----------|---------|--------|
| [Error Handling Taxonomy](error_handling_taxonomy.md) | Complete error code reference | NEW |
| [Consolidated Implementation Report](reports/consolidated_implementation_report.md) | All phases summary | NEW |
| [Error Catalog Consolidation Plan](error_catalog_consolidation_plan.md) | Master workplan | ACTIVE |
| [Data Error Handling](data_error_handling.md) | Implementation guide | REFERENCE |
| [System Error Handling Workplan](system_error_handling_workplan.md) | System error details | REFERENCE |
| [Error Handling Module Workplan](error_handling_module_workplan.md) | Module architecture | REFERENCE |
| [Pipeline Messaging Plan](pipeline_messaging_plan.md) | Message handling | REFERENCE |

---

## Overview

The DCC (Document Control Center) error handling system provides comprehensive validation and error reporting across the entire document processing pipeline. This documentation covers:

- **37 Error Codes** (20 system + 17 data/logic)
- **2 Language Support** (English + Chinese)
- **4-Layer Architecture** (base → setup → config)
- **100% Test Coverage** (28/28 tests passed)

---

## Error Code Taxonomy

### System Errors (S-C-S-XXXX)

| Range | Category | Count | Description |
|-------|----------|-------|-------------|
| S-E-S-01xx | Environment | 4 | Python, packages, imports |
| S-F-S-02xx | File/IO | 5 | Not found, unreadable, permissions |
| S-C-S-03xx | Config | 5 | Schema, parameters, setup |
| S-R-S-04xx | Runtime | 6 | Exceptions, memory, fail-fast |
| S-A-S-05xx | AI/Optional | 3 | AI service errors |

### Data/Logic Errors (LL-M-F-XXXX)

| Range | Layer/Phase | Count | Description |
|-------|-------------|-------|-------------|
| P1-A-P-01xx | Phase 1 - Anchor | 1 | Anchor column processing |
| P2-I-V-02xx | Phase 2 - Identity | 1 | Identity/Transaction validation |
| L3-L-V-03xx | Layer 3 - Logic | 7 | Logic/Temporal validation |
| V5-I-V-05xx | Validation - Schema | 4 | Schema validation errors |
| S1-I-F-08xx | System Input - File | 2 | File handling |
| S1-I-V-05xx | System Input - Valid. | 2 | Input validation |

**See [Error Handling Taxonomy](error_handling_taxonomy.md) for complete code list.**

---

## Architecture

### Schema Files (config/schemas/)

```
error_code_base.json      → 8 reusable definitions
error_code_setup.json     → Properties structure (allOf)
system_error_config.json  → 20 system error codes
data_error_config.json    → 17 data/logic error codes
```

### Inheritance Chain

```
error_code_base.json ($ref definitions)
    ↓
error_code_setup.json (allOf + properties)
    ↓
system_error_config.json / data_error_config.json (actual values)
```

### URI Registry

| URI | File |
|-----|------|
| `https://dcc-pipeline.internal/schemas/error-code/base` | error_code_base.json |
| `https://dcc-pipeline.internal/schemas/error-code/setup` | error_code_setup.json |
| `https://dcc-pipeline.internal/schemas/error-code/system-config` | system_error_config.json |
| `https://dcc-pipeline.internal/schemas/error-code/data-config` | data_error_config.json |

---

## Implementation Phases

| Phase | Description | Status | Report |
|-------|-------------|--------|--------|
| Phase 1 | Schema Architecture | ✅ Complete | [Phase 1 Report](archive/phase1/phase1_completion_report.md) |
| Phase 2 | Code Migration | ✅ Complete | [Phase 2 Report](archive/phase2/phase2_completion_report.md) |
| Phase 3 | Testing & Validation | ✅ Complete | [Phase 3 Report](archive/phase3/phase3_testing_report.md) |
| Phase 4 | Documentation Consolidation | 🔄 In Progress | This workplan |

---

## Migration History

### String Codes → Standardized Codes

| Old String Code | New Standard Code | Status |
|-----------------|-------------------|--------|
| CLOSED_WITH_PLAN_DATE | L3-L-V-0302 | ✅ Migrated |
| RESUBMISSION_MISMATCH | L3-L-V-0303 | ✅ Migrated |
| OVERDUE_MISMATCH | L3-L-V-0304 | ✅ Migrated |
| VERSION_REGRESSION | L3-L-V-0305 | ✅ Migrated |
| REVISION_GAP | L3-L-V-0306 | ✅ Migrated |

---

## How to Add New Error Codes

1. **Check Format:** Use LL-M-F-XXXX for data/logic, S-C-S-XXXX for system
2. **Add to Schema:** Update appropriate config file in `config/schemas/`
3. **Add Messages:** Add entries to `messages/en.json` and `messages/zh.json`
4. **Update Detector:** Use standardized code in `row_validator.py`
5. **Add Weight:** Update `ROW_ERROR_WEIGHTS` if health score impact needed
6. **Document:** Add to `error_handling_taxonomy.md`

**See [Error Handling Taxonomy](error_handling_taxonomy.md) for detailed format specification.**

---

## Files by Category

### Schema Definition Files
- `dcc/config/schemas/error_code_base.json`
- `dcc/config/schemas/error_code_setup.json`
- `dcc/config/schemas/system_error_config.json`
- `dcc/config/schemas/data_error_config.json`

### Implementation Files
- `dcc/workflow/processor_engine/error_handling/detectors/row_validator.py`
- `dcc/workflow/processor_engine/error_handling/config/messages/en.json`
- `dcc/workflow/processor_engine/error_handling/config/messages/zh.json`

### Archived Files
- `dcc/workflow/processor_engine/error_handling/config/error_codes.json` → `archive/`
- `dcc/workflow/initiation_engine/error_handling/config/system_error_codes.json` → `archive/`

---

## Test Results

| Category | Tests | Passed | Failed |
|----------|-------|--------|--------|
| Schema Validation | 4 | 4 | 0 |
| Format Validation | 5 | 5 | 0 |
| Migration | 5 | 5 | 0 |
| Messages | 4 | 4 | 0 |
| Integration | 5 | 5 | 0 |
| Health Scores | 5 | 5 | 0 |
| **Total** | **28** | **28** | **0** |

**Pass Rate:** 100%

---

## Compliance

This implementation follows **agent_rule.md Section 2.3**:

- ✅ Base schema (definitions)
- ✅ Setup schema (properties)
- ✅ Config schema (actual values)
- ✅ Unified Schema Registry (URIs)
- ✅ Inheritance via allOf
- ✅ additionalProperties: false
- ✅ Required fields defined

---

## Related Issues

- Issue #62: Error Code Standardization (COMPLETE)
- Issue #61: Resubmission_Required Logic (COMPLETE)

---

**Maintained by:** Engineering Team  
**Questions:** See Issue #62 in log/issue_log.md
