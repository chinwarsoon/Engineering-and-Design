# DCC Pipeline: Data Error Coding & Validation Framework - Workplan

| Field | Value |
|-------|-------|
| **Workplan ID** | WP-DCC-EH-DATA-001 |
| **Version** | 2.0 |
| **Date** | 2026-04-24 |
| **Status** | ✅ COMPLETE (Phases 1-4) |
| **Scope** | **DATA ERRORS ONLY** - Logic errors, validation errors, calculation errors in processed data |
| **System Errors** | See [system error handling workplan](../system_error_handling/system_error_handling_workplan.md) for environment/pipeline failures |
| **Issue Ref** | #62 (Error Code Standardization) |
| **Related** | [Taxonomy](../error_handling_taxonomy.md) \| [Consolidated Report](../error_catalog_consolidation/reports/consolidated_implementation_report.md) \| [README](../README.md) |

---

## 1. Object

To establish a comprehensive error coding and validation framework for the DCC pipeline that:
- Standardizes all error codes using the LL-M-F-XXXX format (Layer-Module-Function-UniqueID)
- Provides consistent error detection across all pipeline phases (P1, P2, P2.5, P3)
- Enables health score calculation based on error severity
- Supports bilingual error messages (English and Chinese)
- Creates traceability from error codes to detector functions
- Maintains backward compatibility with legacy error codes

---

## 2. Scope Summary

### In Scope (Data Errors Only)
- **17 Data/Logic Error Codes** in LL-M-F-XXXX format
- **6 Data Error Categories:** 
  - P1-A (Anchor): Column nulls, format errors
  - P2-I (Identity): Document ID, revision errors
  - L3-L (Logic): Date inversions, status conflicts
  - F4-C (Fill): Forward fill warnings
  - V5-I (Validation): Schema pattern/enum/type errors
  - C6-C (Calculation): Dependency, circular reference errors
- **Data Error Schema Files**: `error_code_base.json`, `error_code_setup.json`, `data_error_config.json`
- **Bilingual Messages** (EN, ZH) for data errors
- **Health Score Integration** with weighted error impact per data error
- **Migration Path** from legacy P1xx/P2xx/L3xx codes to LL-M-F-XXXX format

### Out of Scope (See Other Workplans)
| Topic | Location |
|-------|----------|
| **System Errors** (S-C-S-XXXX) | [`../system_error_handling/system_error_handling_workplan.md`](../system_error_handling/system_error_handling_workplan.md) |
| **Real-time error reporting UI** | [`../pipeline_messaging/pipeline_messaging_plan.md`](../pipeline_messaging/pipeline_messaging_plan.md) |
| **Error remediation workflows** | [`../module/error_handling_module_workplan.md`](../module/error_handling_module_workplan.md) |
| **System error messages** | `initiation_engine/error_handling/config/messages/system_en.json` |

---

## 3. Index of Content

| Section | Description | Link |
|---------|-------------|------|
| 1 | [Object](#1-object) | Purpose of data error framework |
| 2 | [Scope Summary](#2-scope-summary) | Data errors only; system errors separate |
| 3 | [Index of Content](#3-index-of-content) | This table |
| 4 | [Version History](#4-version-history) | Revision tracking |
| 5 | [Evaluation & Architecture](#5-evaluation--alignment-with-existing-architecture) | agent_rule.md compliance |
| 6 | [Dependencies](#6-dependencies-with-other-tasks) | Related workplans & files |
| 7 | [Implementation Phases](#7-implementation-phases) | Phase 1-4 breakdown |
| 8 | [Timeline & Deliverables](#8-timeline-milestones-and-deliverables) | Schedule & 11 deliverables |
| 9 | [Risks & Mitigation](#9-risks-and-mitigation) | 5 risks with status |
| 10 | [Future Issues](#10-potential-issues-to-be-addressed-in-the-future) | 5 improvement areas |
| 11 | [Success Criteria](#11-success-criteria) | 8 measurable targets |
| 12 | [Technical Implementation](#12-technical-implementation-details) | 12.1-12.11 subsections |
| 13 | [Migration Table](#13-migration-table) | Legacy → Standardized mapping |
| 14 | [Summary & Status](#14-summary--current-status) | Current state & related docs |
| 15 | [References](#15-references) | Links to code, reports, schemas |

---

## 4. Version History

| Version | Date | Author | Changes | Status |
|---------|------|--------|---------|--------|
| 2.0 | 2026-04-24 | System | Major update to standardized LL-M-F-XXXX format, added Phase 1-3 completion status, migration table | ✅ Complete |
| 1.2 | 2026-04-09 | System | Added implementation guide and integration specs | ✅ Complete |
| 1.1 | 2026-04-09 | System | Added V5xx (Validation) and C6xx (Calculation) error codes | ✅ Complete |
| 1.0 | 2026-04-09 | System | Initial framework with P1xx-P2xx-L3xx-F4xx format | ✅ Complete |

---

## 5. Evaluation & Alignment with Existing Architecture

### Schema Architecture Compliance (agent_rule.md Section 2)

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Base schema for definitions | `error_code_base.json` - 8 reusable definitions | ✅ Compliant |
| Setup schema for properties | `error_code_setup.json` - allOf inheritance | ✅ Compliant |
| Config schema for values | `system_error_config.json`, `data_error_config.json` | ✅ Compliant |
| One-to-one match across files | Properties match, $refs validated | ✅ Compliant |
| URI Registry | All schemas have unique digital IDs | ✅ Compliant |
| additionalProperties: false | Set on critical schemas | ✅ Compliant |

### Data Column Priority Alignment (agent_rule.md Section 1)

| Priority | Error Codes | Alignment |
|----------|-------------|-----------|
| P1 (Meta Data) | P1-A-P/V-01xx | Detects null anchor columns (Project_Code, Facility_Code, etc.) |
| P2 (Transactional) | P2-I-P/V-02xx | Validates Document_ID, Revision before logic |
| P2.5/P3 (Calculated) | L3-L, C6-C, V5-I | Runs after P1/P2 validation |

### Documentation Requirements (agent_rule.md Section 7)

| Requirement | Location | Status |
|-------------|----------|--------|
| Overall summary | Section 1 (Object) | ✅ |
| Content index | Section 3 | ✅ |
| Quick start | Section 12 (Technical Implementation) | ✅ |
| Module structure | Section 12 | ✅ |
| I/O table | Error tables per category | ✅ |
| Debugging/troubleshooting | Section 9 (Risks) | ✅ |
| Usage examples | Code samples throughout | ✅ |

---

## 6. Dependencies with Other Tasks

### Internal Dependencies

| Task | Relationship | Status |
|------|--------------|--------|
| [System Error Handling](../system_error_handling_workplan.md) | S-C-S-XXXX codes complement LL-M-F-XXXX | ✅ Complete |
| [Error Handling Taxonomy](../error_handling_taxonomy.md) | Master reference for all codes | ✅ Complete |
| [Pipeline Messaging](../pipeline_messaging_plan.md) | UI display of error messages | ✅ Complete |

### External Dependencies

| Component | Usage | Status |
|-----------|-------|--------|
| `row_validator.py` | Uses L3-L-V-03xx codes | ✅ Implemented |
| `messages/en.json` | English translations | ✅ Complete |
| `messages/zh.json` | Chinese translations | ✅ Complete |
| `core/registry.py` | ErrorRegistry class | ✅ Implemented |

---

## 7. Implementation Phases

### Phase 1: Schema Architecture (COMPLETE)
**Objective:** Create 4-file schema structure per agent_rule.md

| Task | Deliverable | Status |
|------|-------------|--------|
| EC1.1 | Create `error_code_base.json` (definitions) | ✅ |
| EC1.2 | Create `error_code_setup.json` (properties) | ✅ |
| EC1.3 | Create `system_error_config.json` (20 codes) | ✅ |
| EC1.4 | Create `data_error_config.json` (17 codes) | ✅ |
| EC1.5 | Validate schema inheritance chain | ✅ |

### Phase 2: Code Migration (COMPLETE)
**Objective:** Migrate 5 legacy string codes to standardized format

| Task | Deliverable | Status |
|------|-------------|--------|
| EC2.1 | Update `row_validator.py` with new codes | ✅ |
| EC2.2 | Update `ROW_ERROR_WEIGHTS` dict | ✅ |
| EC2.3 | Update messages/en.json | ✅ |
| EC2.4 | Update messages/zh.json | ✅ |

### Phase 3: Testing & Validation (COMPLETE)
**Objective:** Verify all components work together

| Task | Deliverable | Status |
|------|-------------|--------|
| EC3.1 | Schema validation tests (4) | ✅ 100% |
| EC3.2 | Format validation tests (5) | ✅ 100% |
| EC3.3 | Code integration tests (5) | ✅ 100% |
| EC3.4 | Message resolution tests (4) | ✅ 100% |
| EC3.5 | Health score calculation tests (5) | ✅ 100% |
| EC3.6 | Migration verification tests (5) | ✅ 100% |

### Phase 4: Documentation Consolidation (COMPLETE)
**Objective:** Align documentation with agent_rule.md requirements

| Task | Deliverable | Status |
|------|-------------|--------|
| EC4.1 | Update this workplan per agent_rule.md | ✅ Current task |
| EC4.2 | Create master README.md | ✅ |
| EC4.3 | Archive obsolete phase files | ✅ |

---

## 8. Timeline, Milestones, and Deliverables

### Timeline Summary

| Phase | Start | End | Duration | Status |
|-------|-------|-----|----------|--------|
| Phase 1 | Apr 20 | Apr 22 | 3 days | ✅ Complete |
| Phase 2 | Apr 22 | Apr 23 | 2 days | ✅ Complete |
| Phase 3 | Apr 23 | Apr 24 | 1 day | ✅ Complete |
| Phase 4 | Apr 24 | Apr 25 | 1 day | ✅ Complete |

### Key Milestones

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| M1 | Apr 22 | 4 schema files validated |
| M2 | Apr 23 | 5 codes migrated, messages updated |
| M3 | Apr 24 | 28 tests passing (100%) |
| M4 | Apr 25 | Documentation consolidated |

### Deliverables

| ID | Deliverable | Location | Status |
|----|-------------|----------|--------|
| D1 | Error Code Base Schema | `config/schemas/error_code_base.json` | ✅ |
| D2 | Error Code Setup Schema | `config/schemas/error_code_setup.json` | ✅ |
| D3 | System Error Config | `config/schemas/system_error_config.json` | ✅ |
| D4 | Data Error Config | `config/schemas/data_error_config.json` | ✅ |
| D5 | English Messages | `workflow/processor_engine/error_handling/config/messages/en.json` | ✅ |
| D6 | Chinese Messages | `workflow/processor_engine/error_handling/config/messages/zh.json` | ✅ |
| D7 | Updated row_validator.py | `workflow/processor_engine/error_handling/detectors/row_validator.py` | ✅ |
| D8 | This Workplan | `workplan/error_handling/data_error_handling_workplan.md` | ✅ |
| D9 | Taxonomy Guide | `workplan/error_handling/error_handling_taxonomy.md` | ✅ |
| D10 | Consolidated Report | `workplan/error_handling/reports/consolidated_implementation_report.md` | ✅ |
| D11 | Master README | `workplan/error_handling/README.md` | ✅ |

---

## 9. Risks and Mitigation

| Risk | Probability | Impact | Mitigation | Status |
|------|-------------|--------|------------|--------|
| R1 | Legacy code references remain | Medium | Medium | Legacy mapping table, backward compatibility layer | Resolved |
| R2 | Message lookup performance | Low | Low | Cached registry, O(1) lookup | Resolved |
| R3 | Schema validation failures | Low | High | 4 schema files, 100% test pass | Resolved |
| R4 | Health score calculation errors | Low | Medium | Weight validation tests | Resolved |
| R5 | Missing bilingual messages | Low | Medium | All 37 codes have EN+ZH | Resolved |

---

## 10. Potential Issues to be Addressed in the Future

| Issue | Priority | Description | Proposed Solution |
|-------|----------|-------------|-------------------|
| F1 | Low | Add more language support | Extend messages/ folder structure |
| F2 | Low | Real-time error streaming | WebSocket integration for UI |
| F3 | Low | Error trend analytics | Time-series database for error rates |
| F4 | Medium | Auto-remediation for certain errors | Rule-based error correction engine |
| F5 | Low | Error code versioning | Schema versioning for breaking changes |

---

## 11. Success Criteria

| Criterion | Target | Measurement | Status |
|-----------|--------|-------------|--------|
| SC1 | All 37 error codes standardized | LL-M-F-XXXX or S-C-S-XXXX format | ✅ 100% |
| SC2 | Schema architecture compliant | agent_rule.md Section 2.3 | ✅ Pass |
| SC3 | 5 legacy codes migrated | row_validator.py updated | ✅ Complete |
| SC4 | 100% test pass rate | 28/28 tests passing | ✅ 100% |
| SC5 | Bilingual message support | EN + ZH messages | ✅ Complete |
| SC6 | Documentation complete | This workplan + taxonomy + README | ✅ Complete |
| SC7 | Health score integration | Weighted error impact | ✅ Implemented |
| SC8 | Backward compatibility | LEGACY_TO_STANDARDIZED mapping | ✅ Complete |

---

## 12. Technical Implementation Details

### 12.1 Error Code Structure (Standardized)

All errors follow the standardized **LL-M-F-XXXX** format (Layer-Module-Function-UniqueID) defined in [Error Handling Taxonomy](error_handling_taxonomy.md). This format enables:
- Rapid SQL filtering by layer/module
- Categorical dashboarding by function
- Clear traceability to source code location
- Consistent health score weighting

#### Format Specification

| Format | Pattern | Example | Used For |
|--------|---------|---------|----------|
| **LL-M-F-XXXX** | `^[A-Z0-9]{2}-[A-Z]-[A-Z]-[0-9]{4}$` | `L3-L-V-0302` | Data/Logic errors |
| **S-C-S-XXXX** | `^S-[A-Z]-S-[0-9]{4}$` | `S-C-S-0301` | System errors |

#### Layer/Phase Codes

| Code | Name | Criticality | Action Required |
| :--- | :--- | :--- | :--- |
| **P1** | Phase 1 - Anchor | CRITICAL | Hard fix in Excel Source |
| **P2** | Phase 2 - Identity | CRITICAL | Verify Mapping or Logic |
| **L3** | Layer 3 - Logic | HIGH | Engineering/DCC Review |
| **F4** | Layer 4 - Fill | MEDIUM | Audit Trail / Review |
| **V5** | Validation 5 - Schema | HIGH | Fix data quality issues |
| **S1** | System Input | CRITICAL | Fix input files |
| **S** | System (S-C-S) | FATAL | Stop pipeline, fix env |

---

### 12.2 Priority 1: Structural Anchor Errors (P1-A-P-01xx)
*Errors in columns that define the "container" of the data.*

| Standardized Code | Legacy Code | Description | Severity |
| :--- | :--- | :--- | :--- |
| **P1-A-P-0101** | P101 | **ANCHOR_COLUMN_NULL** - A Priority 1 column (Project_Code, Facility_Code, Document_Type, Discipline) is null and cannot be forward-filled | CRITICAL |
| **P1-A-V-0102** | P102 | **INVALID_SESSION_FORMAT** - `Submission_Session` does not match the required 6-digit pattern (`^[0-9]{6}$`) | HIGH |
| **P1-A-V-0103** | P103 | **INVALID_DATE_FORMAT** - The `Submission_Date` is missing or in an unrecognizable format | HIGH |

**Migration Note:** Legacy P1xx codes mapped to standardized P1-A-P/V-01xx format. See [Migration Table](#migration-table).

---

### 12.3 Priority 2: Identity & Transactional Errors (P2-I-V-02xx)
*Errors in identifying the specific document or revision.*

| Standardized Code | Legacy Code | Description | Severity |
| :--- | :--- | :--- | :--- |
| **P2-I-P-0201** | P201 | **DOCUMENT_ID_UNCERTAIN** - `Document_ID` could not be resolved from columns or calculated from the schema pattern | CRITICAL |
| **P2-I-P-0202** | P202 | **REVISION_MISSING** - No Revision found for this row; identity is incomplete | CRITICAL |
| **P2-I-V-0203** | P203 | **DUPLICATE_TRANSMITTAL** - Multiple identical Document IDs found within the same `Submission_Session` | HIGH |
| **P2-I-V-0204** | - | **DOCUMENT_ID_INVALID** - `Document_ID` has invalid format or composite mismatch | HIGH |

**Migration Note:** Legacy P2xx codes mapped to standardized P2-I-P/V-02xx format.

---

### 12.4 Priority 3: Logical & Chronological Errors (L3-L-V-03xx)
*Data exists, but the timeline or status is physically impossible.*

| Standardized Code | Legacy Code | Description | Severity | Health Impact |
| :--- | :--- | :--- | :--- | :--- |
| **L3-L-P-0301** | L301 | **DATE_INVERSION** - `Review_Return_Actual_Date` is before `Submission_Date` | HIGH | -15 |
| **L3-L-V-0302** | L302 | **CLOSED_WITH_PLAN_DATE** - `Submission_Closed=YES` but `Resubmission_Plan_Date` is set | HIGH | -10 |
| **L3-L-V-0303** | - | **RESUBMISSION_MISMATCH** - `Review_Status` contains REJ but `Resubmission_Required` is not YES/RESUBMITTED | MEDIUM | -10 |
| **L3-L-V-0304** | L304 | **OVERDUE_MISMATCH** - `Resubmission_Plan_Date` is past but status not overdue/resubmitted | MEDIUM | -5 |
| **L3-L-V-0305** | L302 | **VERSION_REGRESSION** - Current revision older than previous for same Document_ID | HIGH | -15 |
| **L3-L-V-0306** | - | **REVISION_GAP** - Revision gap in `Submission_Session` sequence | MEDIUM | -5 |
| **L3-L-V-0307** | L303 | **CLOSED_WITH_RESUBMISSION** - `Submission_Closed=YES` but `Resubmission_Required=YES` (should be NO) | HIGH | -10 |

**Migration Note:** Legacy L3xx codes migrated to L3-L-P/V-03xx format. L302 split into 0302 (CLOSED_WITH_PLAN_DATE) and 0305 (VERSION_REGRESSION). L303 became 0307.

---

### 12.5 Priority 4: Imputation & Boundary Warnings (F4-C-F-04xx)
*Audit trail codes indicating where the script "guessed" or "filled" values.*

| Standardized Code | Legacy Code | Description | Severity |
| :--- | :--- | :--- | :--- |
| **F4-C-F-0401** | F401 | **FILL_JUMP_LIMIT** - Forward fill exceeded the 20-row threshold | HIGH |
| **F4-C-F-0402** | F402 | **FILL_BOUNDARY_CROSS** - Forward fill attempted to bridge across different `Submission_Sessions` | HIGH |
| **F4-C-F-0403** | F403 | **FILL_INFERRED** - A blank cell was populated via calculation logic | WARNING |
| **F4-C-F-0404** | - | **FILL_EXCESSIVE_NULLS** - Too many null values in group | WARNING |
| **F4-C-F-0405** | - | **FILL_INVALID_GROUPING** - Invalid grouping for fill operation | ERROR |

**Migration Note:** Legacy F4xx codes mapped to F4-C-F-04xx format.

---

### 12.6 Priority 5: Schema Validation Errors (V5-I-V-05xx)
*Errors detected during schema validation against field definitions.*

| Standardized Code | Legacy Code | Error | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| **V5-I-V-0501** | V501 | **PATTERN_MISMATCH** | Value doesn't match regex pattern | `Document_Sequence_Number` fails `^[0-9]{1,4}$` |
| **V5-I-V-0502** | V502 | **LENGTH_VIOLATION** | String exceeds max_length | `Document_Title` > 200 characters |
| **V5-I-V-0503** | V503 | **INVALID_ENUM_VALUE** | Value not in allowed_values | `Document_Type` not in schema enum |
| **V5-I-V-0504** | V504 | **TYPE_MISMATCH** | Data type doesn't match schema | Date column contains text |
| **V5-I-V-0505** | V505 | **REQUIRED_MISSING** | Required field is null | `Project_Code` is empty |
| **V5-I-V-0506** | V506 | **FOREIGN_KEY_FAIL** | Reference value doesn't exist | `Discipline` not in discipline_schema |

**Migration Note:** Legacy V5xx codes mapped to V5-I-V-05xx format.

---

### 12.7 Priority 6: Calculation & Engine Errors (C6-C-C-06xx)
*Errors occurring during phased processing (P1→P2→P2.5→P3).*

| Standardized Code | Legacy Code | Error | Description | Phase |
| :--- | :--- | :--- | :--- | :--- |
| **C6-C-C-0601** | C601 | **DEPENDENCY_FAIL** | Required input column for calculation is missing | P2.5 |
| **C6-C-C-0602** | C602 | **CIRCULAR_DEPENDENCY** | Calculation order has circular references | P3 |
| **C6-C-C-0603** | C603 | **DIVISION_BY_ZERO** | Mathematical operation impossible | P3 |
| **C6-C-C-0604** | C604 | **AGGREGATE_EMPTY** | Aggregation returned no valid data | P3 |
| **C6-C-C-0605** | C605 | **DATE_ARITHMETIC_FAIL** | Unable to add/subtract days from date | P3 |
| **C6-C-C-0606** | C606 | **MAPPING_NO_MATCH** | Value not found in mapping schema | P2.5/P3 |

**Migration Note:** Legacy C6xx codes mapped to C6-C-C-06xx format.

---

### 12.8 Complete Error Code Reference

### By Processing Phase (Standardized)

| Phase | Applicable Error Codes |
|-------|------------------------|
| **P1 (Meta Data)** | P1-A-P-0101, P1-A-V-0102, P1-A-V-0103, V5-I-V-0501-0506, F4-C-F-0401-0403 |
| **P2 (Transactional)** | P2-I-P-0201, P2-I-P-0202, P2-I-V-0203, P2-I-V-0204, V5-I-V-0501-0506, F4-C-F-0401-0403 |
| **P2.5 (Anomaly)** | C6-C-C-0601-0606, F4-C-F-0403-0405, V5-I-V-0501-0506 |
| **P3 (Calculated)** | L3-L-P-0301, L3-L-V-0302-0307, C6-C-C-0601-0606, V5-I-V-0501-0506 |
| **Validation** | V5-I-V-0501-0506 |
| **System** | S-E-S-0101-0104, S-F-S-0201-0205, S-C-S-0301-0305, S-R-S-0401-0406, S-A-S-0501-0503 |

### By Criticality

| Criticality | Standardized Codes | Action |
|-------------|-------------------|--------|
| **CRITICAL** | P1-A-P/V-01xx, P2-I-P/V-02xx, S1-I-F/V-0xxx | Stop processing, fix source data |
| **HIGH** | L3-L-P/V-03xx, C6-C-C-0601-0603 | Review and correct logic/data |
| **MEDIUM** | V5-I-V-05xx, F4-C-F-04xx | Fix data quality issues |
| **WARNING** | S-A-S-05xx | Informational, non-blocking |
| **FATAL** | S-E-S, S-F-S, S-C-S, S-R-S | Stop pipeline, fix environment |

---

### 12.9 Implementation Guide

### Data Storage
- Store codes as a **comma-separated string** in the `validation_errors` column (e.g., `P1-A-V-0102, L3-L-V-0302, F4-C-F-0401`).
- This allows SQL queries like:
  ```sql
  -- Query by layer (P1, P2, L3, etc.)
  SELECT * FROM results WHERE validation_errors LIKE '%P1%'
  SELECT * FROM results WHERE validation_errors LIKE '%L3%'
  SELECT * FROM results WHERE validation_errors IS NULL  -- Clean rows
  
  -- Query by module (A=Anchor, I=Identity, L=Logic, V=Validation)
  SELECT * FROM results WHERE validation_errors LIKE '%-V-%'
  
  -- Query specific error code
  SELECT * FROM results WHERE validation_errors LIKE '%L3-L-V-0302%'
  ```

### Schema Files Location
All error code definitions are in:
```
dcc/config/schemas/
├── error_code_base.json          → 8 reusable definitions
├── error_code_setup.json         → Properties structure (allOf)
├── system_error_config.json      → 20 system error codes
└── data_error_config.json        → 17 data/logic error codes
```

### Error Aggregation per Row (Updated)
The `Validation_Errors` column aggregates all errors for that row using **standardized codes**:

```python
# Pseudocode for error aggregation with standardized codes
def aggregate_row_errors(df, row_index):
    errors = []
    
    # Check P1-A-P/V-01xx errors (Anchor)
    if df.loc[row_index, 'Project_Code'] is None:
        errors.append('P1-A-P-0101')
    
    # Check P2-I-P/V-02xx errors (Identity)
    if df.loc[row_index, 'Document_ID'] is None:
        errors.append('P2-I-P-0201')
    
    # Check L3-L-P/V-03xx errors (Logic)
    if date_inversion_detected(row_index):
        errors.append('L3-L-P-0301')
    if closed_with_plan_date(row_index):
        errors.append('L3-L-V-0302')
    
    # Check F4-C-F-04xx warnings (Fill)
    if forward_fill_jump_exceeded(row_index, threshold=20):
        errors.append('F4-C-F-0401')
    
    # Check V5-I-V-05xx errors (Validation)
    if pattern_mismatch_detected(row_index, 'Document_Sequence_Number'):
        errors.append('V5-I-V-0501')
    
    # Check C6-C-C-06xx errors (Calculation)
    if calculation_failed(row_index, 'Latest_Revision'):
        errors.append('C6-C-C-0604')
    
    return ', '.join(errors) if errors else None
```

### Integration with Phased Processing

```python
# In engine.py apply_phased_processing()
def _apply_phase_with_error_tracking(df, phase_columns, phase_name):
    errors = []
    
    for col in phase_columns:
        try:
            result = process_column(df, col)
            # Check for warnings
            if forward_fill_jump > 20:
                errors.append(('F401', col, f'Jump of {forward_fill_jump} rows'))
        except Exception as e:
            # Map exception to error code
            error_code = map_exception_to_code(e, phase_name)
            errors.append((error_code, col, str(e)))
    
    return df, errors
```

### Error Code Mapping Functions (Standardized)

```python
ERROR_CODE_MAP = {
    # Anchor errors (P1-A-P/V-01xx)
    'NULL_PROJECT_CODE': 'P1-A-P-0101',
    'NULL_FACILITY_CODE': 'P1-A-P-0101',
    'NULL_DOCUMENT_TYPE': 'P1-A-P-0101',
    'NULL_DISCIPLINE': 'P1-A-P-0101',
    'INVALID_SESSION_FORMAT': 'P1-A-V-0102',
    'INVALID_DATE_FORMAT': 'P1-A-V-0103',
    
    # Identity errors (P2-I-P/V-02xx)
    'DOCUMENT_ID_CALCULATION_FAILED': 'P2-I-P-0201',
    'MISSING_REVISION': 'P2-I-P-0202',
    'DUPLICATE_DOCUMENT_ID': 'P2-I-V-0203',
    'DOCUMENT_ID_FORMAT_INVALID': 'P2-I-V-0204',
    
    # Logic errors (L3-L-P/V-03xx)
    'RETURN_BEFORE_SUBMISSION': 'L3-L-P-0301',
    'CLOSED_WITH_PLAN_DATE': 'L3-L-V-0302',
    'RESUBMISSION_MISMATCH': 'L3-L-V-0303',
    'OVERDUE_MISMATCH': 'L3-L-V-0304',
    'VERSION_REGRESSION': 'L3-L-V-0305',
    'REVISION_GAP': 'L3-L-V-0306',
    'CLOSED_WITH_RESUBMISSION': 'L3-L-V-0307',
    
    # Fill warnings (F4-C-F-04xx)
    'FORWARD_FILL_JUMP_EXCEEDED': 'F4-C-F-0401',
    'BOUNDARY_CROSS_DETECTED': 'F4-C-F-0402',
    'VALUE_INFERRED_BY_CALCULATION': 'F4-C-F-0403',
    'EXCESSIVE_NULLS': 'F4-C-F-0404',
    'INVALID_GROUPING': 'F4-C-F-0405',
    
    # Validation errors (V5-I-V-05xx)
    'PATTERN_MISMATCH': 'V5-I-V-0501',
    'MAX_LENGTH_EXCEEDED': 'V5-I-V-0502',
    'NOT_IN_ALLOWED_VALUES': 'V5-I-V-0503',
    'TYPE_CONVERSION_FAILED': 'V5-I-V-0504',
    'REQUIRED_FIELD_NULL': 'V5-I-V-0505',
    'FOREIGN_KEY_INVALID': 'V5-I-V-0506',
    
    # Calculation errors (C6-C-C-06xx)
    'DEPENDENCY_NOT_FOUND': 'C6-C-C-0601',
    'CIRCULAR_DEPENDENCY': 'C6-C-C-0602',
    'DIVISION_BY_ZERO': 'C6-C-C-0603',
    'AGGREGATE_NO_DATA': 'C6-C-C-0604',
    'DATE_ARITHMETIC_ERROR': 'C6-C-C-0605',
    'MAPPING_NOT_FOUND': 'C6-C-C-0606',
}
```

### Legacy Code Mapping (For Reference)

```python
# Mapping from legacy P1xx/P2xx/L3xx codes to new standardized format
LEGACY_TO_STANDARDIZED = {
    # P1xx → P1-A-P/V-01xx
    'P101': 'P1-A-P-0101',
    'P102': 'P1-A-V-0102',
    'P103': 'P1-A-V-0103',
    
    # P2xx → P2-I-P/V-02xx
    'P201': 'P2-I-P-0201',
    'P202': 'P2-I-P-0202',
    'P203': 'P2-I-V-0203',
    
    # L3xx → L3-L-P/V-03xx (split/renamed)
    'L301': 'L3-L-P-0301',
    'L302': ['L3-L-V-0302', 'L3-L-V-0305'],  # Split into two codes
    'L303': 'L3-L-V-0307',  # Renamed from STATUS_CONFLICT
    'L304': 'L3-L-V-0304',  # Renamed from OVERDUE_PENDING
    
    # F4xx → F4-C-F-04xx
    'F401': 'F4-C-F-0401',
    'F402': 'F4-C-F-0402',
    'F403': 'F4-C-F-0403',
    
    # V5xx → V5-I-V-05xx
    'V501': 'V5-I-V-0501',
    'V502': 'V5-I-V-0502',
    'V503': 'V5-I-V-0503',
    'V504': 'V5-I-V-0504',
    'V505': 'V5-I-V-0505',
    'V506': 'V5-I-V-0506',
    
    # C6xx → C6-C-C-06xx
    'C601': 'C6-C-C-0601',
    'C602': 'C6-C-C-0602',
    'C603': 'C6-C-C-0603',
    'C604': 'C6-C-C-0604',
    'C605': 'C6-C-C-0605',
    'C606': 'C6-C-C-0606',
}
```

---

### 12.10 UI/Tooltip Integration

### Error Display Format (Standardized)
```json
{
  "error_code": "P1-A-V-0102",
  "error_key": "INVALID_SESSION_FORMAT",
  "severity": "HIGH",
  "layer": "P1",
  "module": "A",
  "function": "V",
  "message": "Session ID format invalid",
  "details": "Expected 6 digits, got 'ABC123'",
  "column": "Submission_Session",
  "row_index": 42,
  "health_score_impact": -15,
  "action": "Fix in Excel source - must be 6 digits (e.g., '001234')"
}
```

**Note:** The `error_key` field preserves the legacy error name for backward compatibility.

### Tooltip Priority (By Standardized Severity)
1. Show **CRITICAL** errors first (P1-A, P2-I, S1-I)
2. Show **HIGH** priority second (L3-L, C6-C-C-0601-0603)
3. Show **MEDIUM** priority third (V5-I-V, F4-C-F)
4. Show **FATAL** system errors (S-E-S, S-F-S, S-C-S, S-R-S)
5. Collapse **WARNING** priority (S-A-S) under "Non-Blocking Warnings"

---

### 12.11 Testing Error Detection

### Unit Test Examples
```python
def test_P1_A_P_0101_null_anchor():
    """Test detection of null Project_Code (standardized P1-A-P-0101)"""
    row = {'Project_Code': None, 'Facility_Code': 'FC001'}
    errors = detect_anchor_errors(row)
    assert 'P1-A-P-0101' in errors

def test_P1_A_V_0102_invalid_session_format():
    """Test detection of invalid session format (standardized P1-A-V-0102)"""
    row = {'Submission_Session': 'ABC123'}  # Not 6 digits
    errors = detect_anchor_errors(row)
    assert 'P1-A-V-0102' in errors

def test_L3_L_P_0301_date_inversion():
    """Test detection of return before submission (standardized L3-L-P-0301)"""
    row = {
        'Submission_Date': '2024-01-15',
        'Review_Return_Actual_Date': '2024-01-10'  # Before submission!
    }
    errors = detect_logic_errors(row)
    assert 'L3-L-P-0301' in errors

def test_L3_L_V_0302_closed_with_plan_date():
    """Test detection of closed submission with plan date (standardized L3-L-V-0302)"""
    row = {
        'Submission_Closed': 'YES',
        'Resubmission_Plan_Date': '2024-02-01'  # Should be null if closed!
    }
    errors = detect_logic_errors(row)
    assert 'L3-L-V-0302' in errors

def test_F4_C_F_0401_jump_limit():
    """Test warning for forward fill exceeding 20 rows (standardized F4-C-F-0401)"""
    # Simulate 25 rows with same value
    jump_size = 25
    warning = detect_fill_warnings(jump_size)
    assert warning == 'F4-C-F-0401'
```

---

## 13. Migration Table

### Legacy → Standardized Code Mapping

| Legacy Code | Standardized Code | Description | Migration Status |
|-------------|-------------------|-------------|------------------|
| P101 | P1-A-P-0101 | NULL_ANCHOR → ANCHOR_COLUMN_NULL | ✅ Complete |
| P102 | P1-A-V-0102 | SESSION_ID_FORMAT → INVALID_SESSION_FORMAT | ✅ Complete |
| P103 | P1-A-V-0103 | DATE_INVALID → INVALID_DATE_FORMAT | ✅ Complete |
| P201 | P2-I-P-0201 | ID_UNCERTAIN → DOCUMENT_ID_UNCERTAIN | ✅ Complete |
| P202 | P2-I-P-0202 | REV_MISSING → REVISION_MISSING | ✅ Complete |
| P203 | P2-I-V-0203 | DUPLICATE_TRANS → DUPLICATE_TRANSMITTAL | ✅ Complete |
| L301 | L3-L-P-0301 | DATE_INVERSION | ✅ Complete |
| L302 | L3-L-V-0302 | Split: CLOSED_WITH_PLAN_DATE | ✅ Complete |
| L302 | L3-L-V-0305 | Split: VERSION_REGRESSION | ✅ Complete |
| L303 | L3-L-V-0307 | STATUS_CONFLICT → CLOSED_WITH_RESUBMISSION | ✅ Complete |
| L304 | L3-L-V-0304 | CLOSED_RESUBMISSION → OVERDUE_MISMATCH | ✅ Complete |
| F401 | F4-C-F-0401 | JUMP_LIMIT → FILL_JUMP_LIMIT | ✅ Complete |
| F402 | F4-C-F-0402 | BOUNDARY_CROSS → FILL_BOUNDARY_CROSS | ✅ Complete |
| F403 | F4-C-F-0403 | FILL_INFERRED | ✅ Complete |
| V501 | V5-I-V-0501 | PATTERN_MISMATCH | ✅ Complete |
| V502 | V5-I-V-0502 | LENGTH_EXCEEDED → LENGTH_VIOLATION | ✅ Complete |
| V503 | V5-I-V-0503 | INVALID_ENUM → INVALID_ENUM_VALUE | ✅ Complete |
| V504 | V5-I-V-0504 | TYPE_MISMATCH | ✅ Complete |
| V505 | V5-I-V-0505 | REQUIRED_MISSING → REQUIRED_MISSING | ✅ Complete |
| V506 | V5-I-V-0506 | FOREIGN_KEY_FAIL → FOREIGN_KEY_FAIL | ✅ Complete |
| C601 | C6-C-C-0601 | CALC_DEPENDENCY_FAIL → DEPENDENCY_FAIL | ✅ Complete |
| C602 | C6-C-C-0602 | CIRCULAR_DEPENDENCY | ✅ Complete |
| C603 | C6-C-C-0603 | DIVISION_BY_ZERO | ✅ Complete |
| C604 | C6-C-C-0604 | AGGREGATE_EMPTY → AGGREGATE_EMPTY | ✅ Complete |
| C605 | C6-C-C-0605 | DATE_ARITHMETIC_FAIL → DATE_ARITHMETIC_FAIL | ✅ Complete |
| C606 | C6-C-C-0606 | MAPPING_NO_MATCH → MAPPING_NO_MATCH | ✅ Complete |

---

## 14. Summary & Current Status

### What Was Accomplished (Phases 1-3)

| Phase | Description | Deliverables | Status |
|-------|-------------|--------------|--------|
| **Phase 1** | Schema Architecture | 4 schema files, 37 error codes defined | ✅ COMPLETE |
| **Phase 2** | Code Migration | 5 string codes migrated, messages in 2 languages | ✅ COMPLETE |
| **Phase 3** | Testing | 28 tests, 100% pass rate | ✅ COMPLETE |
| **Phase 4** | Documentation Consolidation | This file updated, README created | ✅ COMPLETE |

### Current Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| Schema Files | ✅ Complete | `dcc/config/schemas/` |
| Error Codes | ✅ Complete | 20 system + 17 data/logic |
| Messages (EN) | ✅ Complete | `messages/en.json` |
| Messages (ZH) | ✅ Complete | `messages/zh.json` |
| row_validator.py | ✅ Updated | Uses standardized codes |
| Health Weights | ✅ Updated | `ROW_ERROR_WEIGHTS` dict |

### Implemented Functions

- ✅ `detect_anchor_errors()` - Returns P1-A-P/V-01xx codes
- ✅ `detect_identity_errors()` - Returns P2-I-P/V-02xx codes
- ✅ `detect_logic_errors()` - Returns L3-L-P/V-03xx codes
- ✅ `detect_fill_warnings()` - Returns F4-C-F-04xx codes
- ✅ `detect_validation_errors()` - Returns V5-I-V-05xx codes
- ✅ `detect_calculation_errors()` - Returns C6-C-C-06xx codes

### Related Documentation

- [Error Handling Taxonomy](error_handling_taxonomy.md) - Complete error code reference
- [Consolidated Implementation Report](reports/consolidated_implementation_report.md) - All phases summary
- [README.md](README.md) - Master documentation index
- [Error Catalog Consolidation Plan](error_catalog_consolidation_plan.md) - Master workplan

---

## 15. References

### Code Files

| File | Purpose | Location |
|------|---------|----------|
| `row_validator.py` | Data error detection with L3-L-V-03xx codes | [`workflow/processor_engine/error_handling/detectors/row_validator.py`](../../workflow/processor_engine/error_handling/detectors/row_validator.py) |
| `error_code_base.json` | Base schema definitions (8 defs) | [`config/schemas/error_code_base.json`](../../config/schemas/error_code_base.json) |
| `error_code_setup.json` | Properties structure (allOf) | [`config/schemas/error_code_setup.json`](../../config/schemas/error_code_setup.json) |
| `data_error_config.json` | 17 data error code values | [`config/schemas/data_error_config.json`](../../config/schemas/data_error_config.json) |
| `system_error_config.json` | 20 system error codes (S-C-S-XXXX) | [`config/schemas/system_error_config.json`](../../config/schemas/system_error_config.json) |
| `en.json` | English error messages | [`workflow/processor_engine/error_handling/config/messages/en.json`](../../workflow/processor_engine/error_handling/config/messages/en.json) |
| `zh.json` | Chinese error messages | [`workflow/processor_engine/error_handling/config/messages/zh.json`](../../workflow/processor_engine/error_handling/config/messages/zh.json) |

### Reports

| Report | Description | Location |
|--------|-------------|----------|
| Consolidated Implementation Report | All phases summary | [`reports/consolidated_implementation_report.md`](reports/consolidated_implementation_report.md) |
| System Error Handling Report | System error completion | [`reports/system_error_handling_completion_report.md`](reports/system_error_handling_completion_report.md) |

### Related Workplans

| Workplan | Scope | Location |
|----------|-------|----------|
| System Error Handling | S-C-S-XXXX environment/pipeline errors | [system_error_handling_workplan.md](system_error_handling_workplan.md) |
| Error Handling Taxonomy | Complete error code reference | [error_handling_taxonomy.md](error_handling_taxonomy.md) |
| Pipeline Messaging Plan | UI/UX error display | [pipeline_messaging_plan.md](pipeline_messaging_plan.md) |
| Error Handling Module | Remediation workflows | [error_handling_module_workplan.md](error_handling_module_workplan.md) |
| Error Catalog Consolidation | Master workplan | [error_catalog_consolidation_plan.md](error_catalog_consolidation_plan.md) |

### Logs

| Log | Purpose | Location |
|-----|---------|----------|
| Issue Log | Issue #62 tracking | [`../../log/issue_log.md`](../../log/issue_log.md) |
| Update Log | Phase completion entries | [`../../log/update_log.md`](../../log/update_log.md) |

---

**Status:** ✅ **UP TO DATE** - All standardized error codes implemented (Issue #62)  
**Last Updated:** 2026-04-25 per agent_rule.md workplan requirements  
**File:** `data_error_handling_workplan.md` (renamed from `data_error_handling.md`)