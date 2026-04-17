# Column Validation Workplan

**Based on:** dcc_register_config.json schema, pipeline execution results (11,099 rows, 44 columns)
**Last Updated:** 2026-04-17

---

## Overview

Column-level validation ensures each column adheres to data type, format, and business rule constraints.
Pipeline execution revealed: 1,238 row-level errors (HIGH: 172, WARNING: 1,066), 98.5% health score.

---

## Gate 1: Integrity Gate (Data Type & Structure)

### 1.1 Type Matching
Validate declared data_type matches actual values:

| Column Type | Data Type | Columns | Validation Rule |
|-------------|-----------|---------|---------------|
| id_column | string | Document_ID, Row_Index, Transmittal_Number | Non-null, unique pattern |
| code_column | categorical | Project_Code, Facility_Code, Document_Type, Discipline, Department, Approval_Code, Review_Status_Code, Submitted_By, Reviewer | Schema reference validation |
| date_column | date | Submission_Date, Review_Return_Actual_Date, Review_Return_Plan_Date, Resubmission_Plan_Date, Resubmission_Forecast_Date, First_Submission_Date, Latest_Submission_Date | ISO 8601 format (YYYY-MM-DD) |
| sequence_column | string | Document_Sequence_Number, Submission_Session, Submission_Session_Revision, Document_Revision, Latest_Revision | Zero-padded numeric pattern |
| status_column | categorical | Review_Status, Latest_Approval_Status, Resubmission_Required, Submission_Closed, Resubmission_Overdue_Status | Allowed values enumeration |
| numeric_column | numeric | Duration_of_Review, Delay_of_Resubmission, Count_of_Submissions | Numeric range check |
| text_column | text | Document_Title, Review_Comments, Notes, Submission_Session_Subject | String length constraints |
| score_column | numeric | Data_Health_Score | Range 0-100 |
| json_column | string | All_Submission_Sessions, All_Submission_Dates, All_Submission_Session_Revisions, All_Approval_Code, Validation_Errors | Concatenated format validation |

### 1.2 Null Check (Required vs Optional)

**Critical Required Columns (cannot be null):**
- Document_ID, Project_Code, Document_Type, Submission_Date
- Document_Sequence_Number (zero-padded 4 digits)
- Submission_Session (zero-padded 6 digits)
- Document_Revision (zero-padded 2 digits)

**Optional Columns (allow null with handling):**
- Transmittal_Number (default: "NA")
- Review_Comments (forward_fill strategy)
- Duration_of_Review (calculated from dates)
- Resubmission_Forecast_Date (conditional)

**Null Summary from Pipeline (high priority fixes):**
- Document_ID: 41 nulls (critical - composite identity anchor)
- Project_Code: 4 nulls (critical - project reference)
- Submission_Date: 3 nulls (critical - temporal anchor)
- Document_Sequence_Number: 63 nulls
- Document_Type: 71 nulls

### 1.3 Pattern Validation (Regex-based)

| Column | Pattern | Example | Pipeline Failures |
|--------|---------|---------|-------------------|
| Project_Code | `^[A-Z0-9-]+$` | 131242, 131244-WSW | 43 invalid values |
| Document_Sequence_Number | `^[0-9]{4}$` | 0001, 1234 | 1,638 invalid values |
| Submission_Session | `^[0-9]{6}$` | 000123, 456789 | Group consistency check |
| Submission_Session_Revision | `^[0-9]{2}$` | 00, 01 | Sequential within session |
| Document_Revision | `^[0-9]{2}$` | 00, 01 | 80 invalid values |
| Document_ID | Dynamic from constituents | {Project}-{Facility}-{Type}-{Discipline}-{Seq} | 100 invalid values (with affixes) |

---

## Gate 2: Domain Gate (Business Rules)

### 2.1 Schema Reference Validation
Cross-reference codes against master schemas:

| Column | Reference Schema | Pipeline Failures |
|--------|------------------|-------------------|
| Project_Code | project_schema codes | Validate against 2 projects |
| Facility_Code | facility_schema (97 entries) | 69 nulls detected |
| Document_Type | document_type_schema (15 entries) | 71 nulls |
| Discipline | discipline_schema (15 entries) | 67 nulls |
| Department | department_schema (17 entries) | 8,132 nulls (81% missing) |
| Approval_Code | approval_code_schema (7 entries) | Auto-populated |
| Review_Status | approval_code_schema | 20 values not in schema |
| Submitted_By | department_schema | 8,167 nulls (74% missing) |
| Reviewer | department_schema | Not in source data (missing column) |

### 2.2 Range Validation (Numeric Columns)

| Column | Min | Max | Pipeline Findings |
|--------|-----|-----|-------------------|
| Duration_of_Review | 0 | 365 | 4 values > 365 days |
| Delay_of_Resubmission | 0 | 365 | 239 values < 0 (invalid), 347 values > 365 |
| Count_of_Submissions | 1 | 100 | Aggregate count |
| Data_Health_Score | 0 | 100 | Calculated metric |

### 2.3 Categorical Validation (Allowed Values)

| Column | Allowed Values | Default |
|--------|----------------|---------|
| Submission_Closed | YES, NO | NO |
| Resubmission_Required | YES, NO, RESUBMITTED, PENDING | Evaluate from Review_Status |
| Resubmission_Overdue_Status | Resubmitted, Overdue, NO | Calculate from dates |
| Latest_Approval_Status | From approval_code_schema | 14 values not in schema |

---

## Gate 3: Logic Gate (Calculated & Derived Values)

### 3.1 Composite Identity Validation
**Document_ID** must match constituent fields:
```
Pattern: {Project_Code}-{Facility_Code}-{Document_Type}-{Discipline}-{Document_Sequence_Number}
Example: 131242-WSW41-LT-PM-0001
```

Validation Rules:
1. Extract 5 segments from Document_ID
2. Validate each segment matches corresponding column
3. Extract and validate affixes (Document_ID_Affixes column)
4. Pipeline found: 100 invalid values with sample affixes like '_Reply', '_ST607'

### 3.2 Cross-Reference Validation

| Validation | Rule | Implementation |
|------------|------|----------------|
| Review_Status_Code | Derived from Review_Status | Map status to code schema |
| Latest_Approval_Code | Last non-null Approval_Code | Forward fill within Document_ID |
| This_Submission_Approval_Code | Current row Approval_Code | Conditional on submission state |
| All_Approval_Code | Concatenated unique codes | Aggregate across Document_ID history |

### 3.3 Date Consistency Validation

| Validation | Rule | Priority |
|------------|------|----------|
| Group Consistency | Submission_Date must be same within (Submission_Session, Submission_Session_Revision) | HIGH |
| First_Submission_Date | MIN(Submission_Date) per Document_ID | Calculated |
| Latest_Submission_Date | MAX(Submission_Date) per Document_ID | Calculated |
| Resubmission_Plan_Date | NULL if Submission_Closed = YES | Conditional |
| Date Format | YYYY-MM-DD ISO 8601 | Pipeline: 305 invalid dates in Resubmission_Forecast_Date |

### 3.4 Calculated Field Integrity

| Column | Calculation Method | Validation |
|--------|-------------------|------------|
| Duration_of_Review | Business days between Submission_Date and Review_Return_Actual_Date | Must be non-negative |
| Delay_of_Resubmission | Days between Resubmission_Plan_Date and actual resubmission | Negative values flagged (239 found) |
| Count_of_Submissions | COUNT(Document_ID) GROUP BY Document_ID | Min 1, max 100 |
| Data_Health_Score | Weighted sum of validation errors | 0-100 range (no handler warning in pipeline) |

---

## Gate 4: Error Handling & Logging

### 4.1 Validation Severity Levels

| Severity | Count | Example Issues |
|----------|-------|----------------|
| HIGH | 172 | Missing required columns (Document_ID nulls), pattern validation failures |
| WARNING | 1,066 | Schema reference failures, range violations, format issues |
| INFO | - | Null handling notifications, calculated field updates |

### 4.2 Error Aggregation (Validation_Errors Column)

Auto-populated by processor during validation:
- Aggregate all column-level errors per row
- Store as concatenated string (e.g., "Project_Code: invalid; Document_ID: pattern_fail")
- Used for Data_Health_Score calculation

### 4.3 Logging Requirements

```python
# Per validation gate logging
[Integrity] {column}: {validation_type} {result} (duration_ms)
[Domain] {column}: {schema_reference} {match_status}
[Logic] {column}: {calculation_method} {input_columns} -> {result}
```

---

## Implementation Phases

### Phase 1: Critical Validations (Required for data integrity)
- Document_ID composite pattern validation
- Project_Code schema reference
- Submission_Date null check
- Document_ID constituent field matching

### Phase 2: Domain Validations (Business rule compliance)
- All schema reference validations (9 code columns)
- Numeric range validations (3 columns)
- Categorical allowed values (6 status columns)

### Phase 3: Logic Validations (Calculated field integrity)
- Date sequence validations (7 date columns)
- Cross-reference validations (Latest_Approval_Code, All_Approval_Code)
- Group consistency checks (Submission_Session + Submission_Date)

### Phase 4: Quality Metrics (Data health monitoring)
- Data_Health_Score calculation implementation
- Validation_Errors aggregation
- Error dashboard integration

---

## Success Metrics

| Metric | Target | Current (Pipeline) |
|--------|--------|-------------------|
| Column-level error rate | < 1% | ~11% (1,238 errors / 11,099 rows) |
| Pattern validation pass rate | > 95% | ~85% (Project_Code, Document_Sequence_Number issues) |
| Schema reference match rate | > 98% | ~95% (Review_Status, Latest_Approval_Status issues) |
| Data Health Score | > 95% | 98.5% (A grade) |

---

## Files Affected

- **Schema:** `dcc/config/schemas/dcc_register_config.json` (47 columns with validation rules)
- **Pipeline:** `dcc/workflow/dcc_engine_pipeline.py` (validation phase P4)
- **Output:** `dcc/output/processing_summary.txt` (validation results)
- **Dashboard:** `dcc/output/error_dashboard_data.json` (error aggregation)