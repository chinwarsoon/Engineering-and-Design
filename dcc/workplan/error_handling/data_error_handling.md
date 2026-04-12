# DCC Pipeline: Error Coding & Validation Framework

**Version:** 1.0  
**Status:** Implementation Ready  
**Scope:** logic for `validation_errors` column and UI tooltips.

---

## 1. Error Code Structure
All errors follow a **Prefix + 3-Digit** format to allow for rapid SQL filtering and categorical dashboarding.

| Prefix | Source Engine | Criticality | Action Required |
| :--- | :--- | :--- | :--- |
| **P1xx** | Initiation / Anchor | High | Hard fix in Excel Source |
| **P2xx** | Identity / Mapper | High | Verify Mapping or Logic |
| **L3xx** | Logic / Calculation | Medium | Engineering/DCC Review |
| **F4xx** | Imputation / Fill | Low | Audit Trail / Info Only |

---

## 2. Priority 1: Structural Anchor Errors (P1xx)
*Errors in columns that define the "container" of the data.*

- **P101 - NULL_ANCHOR:** A Priority 1 column (e.g., Project Code) is null and cannot be forward-filled.
- **P102 - SESSION_ID_FORMAT:** `Submission_Session` does not match the required 6-digit pattern (`^[0-9]{6}$`).
- **P103 - DATE_INVALID:** The `Submission_Date` is missing or in an unrecognizable format.

---

## 3. Priority 2: Identity & Transactional Errors (P2xx)
*Errors in identifying the specific document or revision.*

- **P201 - ID_UNCERTAIN:** `Document_ID` could not be resolved from columns or calculated from the schema pattern.
- **P202 - REV_MISSING:** No Revision found for this row; identity is incomplete.
- **P203 - DUPLICATE_TRANS:** Multiple identical Document IDs found within the same `Submission_Session`.

---

## 4. Priority 3: Logical & Chronological Errors (L3xx)
*Data exists, but the timeline or status is physically impossible.*

- **L301 - DATE_INVERSION:** `Review_Return_Actual_Date` is recorded as being earlier than the `Submission_Date`.
- **L302 - REV_REGRESSION:** A newer submission date carries a lower revision index than an older record (e.g., Rev B after Rev C).
- **L303 - STATUS_CONFLICT:** Manual `Submission_Closed` is marked "YES" but the document is not yet the latest revision or approved.
- **L304 - OVERDUE_PENDING:** Document is marked as the latest submission but has exceeded its `Review_Due_Date` without return.

---

## 5. Priority 4: Imputation & Boundary Warnings (F4xx)
*Audit trail codes indicating where the script "guessed" or "filled" values.*

- **F401 - JUMP_LIMIT:** Forward fill exceeded the 20-row threshold defined in Rule 6.
- **F402 - BOUNDARY_CROSS:** Forward fill attempted to bridge across different `Submission_Sessions`.
- **F403 - FILL_INFERRED:** A blank cell was populated via Priority 2.5 calculation logic (e.g., inferred `Document_ID`).

---

## 6. Priority 5: Schema Validation Errors (V5xx)
*Errors detected during schema validation against field definitions.*

| Code | Error | Description | Example |
|------|-------|-------------|---------|
| **V501 - PATTERN_MISMATCH** | Value doesn't match regex pattern | `Document_Sequence_Number` fails `^[0-9]{1,4}$` | "ABC" instead of "0123" |
| **V502 - LENGTH_EXCEEDED** | String exceeds max_length | `Document_Title` > 200 characters | Title with 250 chars |
| **V503 - INVALID_ENUM** | Value not in allowed_values | `Document_Type` not in schema enum | "XYZ" instead of "DRW" |
| **V504 - TYPE_MISMATCH** | Data type doesn't match schema | Date column contains text | "N/A" in `Submission_Date` |
| **V505 - REQUIRED_MISSING** | Required field is null | `Project_Code` is empty | null value |
| **V506 - FOREIGN_KEY_FAIL** | Reference value doesn't exist | `Discipline` not in discipline_schema | "ZZ" not in allowed list |

---

## 7. Priority 6: Calculation & Engine Errors (C6xx)
*Errors occurring during phased processing (P1→P2→P2.5→P3).*

| Code | Error | Description | Phase |
|------|-------|-------------|-------|
| **C601 - CALC_DEPENDENCY_FAIL** | Required input column for calculation is missing | `Document_ID` calculation needs `Project_Code` | P2.5 |
| **C602 - CIRCULAR_DEPENDENCY** | Calculation order has circular references | Column A depends on B, B depends on A | P3 |
| **C603 - DIVISION_BY_ZERO** | Mathematical operation impossible | Date difference with null values | P3 |
| **C604 - AGGREGATE_EMPTY** | Aggregation returned no valid data | `Latest_Revision` found no valid revisions | P3 |
| **C605 - DATE_ARITHMETIC_FAIL** | Unable to add/subtract days from date | Invalid date format for business day calc | P3 |
| **C606 - MAPPING_NO_MATCH** | Value not found in mapping schema | `Review_Status` value has no code mapping | P2.5/P3 |

---

## 8. Complete Error Code Reference

### By Processing Phase

| Phase | Applicable Error Codes |
|-------|------------------------|
| **P1 (Meta Data)** | P101, P102, P103, V501-V506, F401, F402 |
| **P2 (Transactional)** | P201, P202, P203, V501-V506, F401, F402 |
| **P2.5 (Anomaly)** | C601-C606, F403, V501-V506 |
| **P3 (Calculated)** | L301-L304, C601-C606, V501-V506 |
| **Validation** | V501-V506 |

### By Criticality

| Criticality | Codes | Action |
|-------------|-------|--------|
| **Critical** | P101-P103, P201-P203 | Stop processing, fix source data |
| **High** | L301-L304, C601-C603 | Review and correct logic/data |
| **Medium** | V501-V506 | Fix data quality issues |
| **Low** | F401-F403 | Informational, audit only |

---

## 9. Implementation Guide

### Data Storage
- Store codes as a **comma-separated string** in the `validation_errors` column (e.g., `P102, L301, F401`).
- This allows SQL queries like:
  ```sql
  SELECT * FROM results WHERE validation_errors LIKE '%P1%'
  SELECT * FROM results WHERE validation_errors LIKE '%L3%'
  SELECT * FROM results WHERE validation_errors IS NULL  -- Clean rows
  ```

### Error Aggregation per Row
The `Validation_Errors` column (Step 46 in processing) aggregates all errors for that row:

```python
# Pseudocode for error aggregation
def aggregate_row_errors(df, row_index):
    errors = []
    
    # Check P1xx errors (Anchor)
    if df.loc[row_index, 'Project_Code'] is None:
        errors.append('P101')
    
    # Check P2xx errors (Identity)
    if df.loc[row_index, 'Document_ID'] is None:
        errors.append('P201')
    
    # Check L3xx errors (Logic)
    if date_inversion_detected(row_index):
        errors.append('L301')
    
    # Check F4xx warnings (Fill)
    if forward_fill_jump_exceeded(row_index, threshold=20):
        errors.append('F401')
    
    # Check V5xx errors (Validation)
    if pattern_mismatch_detected(row_index, 'Document_Sequence_Number'):
        errors.append('V501')
    
    # Check C6xx errors (Calculation)
    if calculation_failed(row_index, 'Latest_Revision'):
        errors.append('C604')
    
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

### Error Code Mapping Functions

```python
ERROR_CODE_MAP = {
    # Anchor errors
    'NULL_PROJECT_CODE': 'P101',
    'NULL_FACILITY_CODE': 'P101',
    'NULL_DOCUMENT_TYPE': 'P101',
    'NULL_DISCIPLINE': 'P101',
    'INVALID_SESSION_FORMAT': 'P102',
    'INVALID_DATE_FORMAT': 'P103',
    
    # Identity errors
    'DOCUMENT_ID_CALCULATION_FAILED': 'P201',
    'MISSING_REVISION': 'P202',
    'DUPLICATE_DOCUMENT_ID': 'P203',
    
    # Logic errors
    'RETURN_BEFORE_SUBMISSION': 'L301',
    'REVISION_REGRESSION': 'L302',
    'CLOSURE_STATUS_CONFLICT': 'L303',
    'OVERDUE_WITHOUT_RETURN': 'L304',
    
    # Fill warnings
    'FORWARD_FILL_JUMP_EXCEEDED': 'F401',
    'BOUNDARY_CROSS_DETECTED': 'F402',
    'VALUE_INFERRED_BY_CALCULATION': 'F403',
    
    # Validation errors
    'PATTERN_MISMATCH': 'V501',
    'MAX_LENGTH_EXCEEDED': 'V502',
    'NOT_IN_ALLOWED_VALUES': 'V503',
    'TYPE_CONVERSION_FAILED': 'V504',
    'REQUIRED_FIELD_NULL': 'V505',
    'FOREIGN_KEY_INVALID': 'V506',
    
    # Calculation errors
    'DEPENDENCY_NOT_FOUND': 'C601',
    'CIRCULAR_DEPENDENCY': 'C602',
    'DIVISION_BY_ZERO': 'C603',
    'AGGREGATE_NO_DATA': 'C604',
    'DATE_ARITHMETIC_ERROR': 'C605',
    'MAPPING_NOT_FOUND': 'C606',
}
```

---

## 10. UI/Tooltip Integration

### Error Display Format
```json
{
  "error_code": "P102",
  "severity": "High",
  "message": "Session ID format invalid",
  "details": "Expected 6 digits, got 'ABC123'",
  "column": "Submission_Session",
  "row_index": 42,
  "action": "Fix in Excel source - must be 6 digits (e.g., '001234')"
}
```

### Tooltip Priority
1. Show **Critical** errors first (P1xx, P2xx)
2. Show **High** priority second (L3xx, C601-C603)
3. Show **Medium** priority third (V5xx)
4. Collapse **Low** priority (F4xx) under "Audit Warnings"

---

## 11. Testing Error Detection

### Unit Test Examples
```python
def test_P101_null_anchor():
    """Test detection of null Project_Code"""
    row = {'Project_Code': None, 'Facility_Code': 'FC001'}
    errors = detect_anchor_errors(row)
    assert 'P101' in errors

def test_P102_invalid_session_format():
    """Test detection of invalid session format"""
    row = {'Submission_Session': 'ABC123'}  # Not 6 digits
    errors = detect_anchor_errors(row)
    assert 'P102' in errors

def test_L301_date_inversion():
    """Test detection of return before submission"""
    row = {
        'Submission_Date': '2024-01-15',
        'Review_Return_Actual_Date': '2024-01-10'  # Before submission!
    }
    errors = detect_logic_errors(row)
    assert 'L301' in errors

def test_F401_jump_limit():
    """Test warning for forward fill exceeding 20 rows"""
    # Simulate 25 rows with same value
    jump_size = 25
    warning = detect_fill_warnings(jump_size)
    assert warning == 'F401'
```

---

## 12. Summary & Next Steps

### Current Status
- ✅ Error code structure defined (P1xx, P2xx, L3xx, F4xx, V5xx, C6xx)
- ✅ Critical errors identified for each processing phase
- ✅ Implementation guide provided
- ✅ UI integration specs outlined

### Pending Implementation
- [ ] Create `error_registry.py` with ERROR_CODE_MAP
- [ ] Implement `detect_anchor_errors()` function
- [ ] Implement `detect_identity_errors()` function  
- [ ] Implement `detect_logic_errors()` function
- [ ] Implement `detect_fill_warnings()` function
- [ ] Implement `detect_validation_errors()` function
- [ ] Implement `detect_calculation_errors()` function
- [ ] Integrate error aggregation into `Validation_Errors` column (Step 46)
- [ ] Add error display to reporting engine

### Integration Points
1. **processor_engine/core/engine.py** - Add error tracking to phased processing
2. **processor_engine/validations/field_validator.py** - Add V5xx error detection
3. **processor_engine/calculations/*.py** - Add C6xx error handling
4. **reporting_engine/** - Add error summary reports

---

**Version History:**
- **v1.0** (April 9, 2026) - Initial framework with P1xx-P2xx-L3xx-F4xx
- **v1.1** (April 9, 2026) - Added V5xx (Validation) and C6xx (Calculation) error codes
- **v1.2** (April 9, 2026) - Added implementation guide and integration specs

**Status:** ✅ Framework Complete - Ready for Implementation