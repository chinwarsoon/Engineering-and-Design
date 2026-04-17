# Row Validation Workplan

**Based on:** dcc_register_config.json schema, pipeline execution results (11,099 rows, 44 columns)
**Last Updated:** 2026-04-17

---

## Overview

Row-level validation checks internal consistency across columns within each row. Unlike column validation which inspects values in isolation, row validation ensures relationships between columns are valid.

**Pipeline Context:**
- 11,099 rows processed
- 1,238 row-level errors identified (HIGH: 172, WARNING: 1,066)
- 997 rows affected (9% error rate)
- Data Health Score: 98.5% (Grade A)

---

## Category 1: Anchor Completeness (Critical Fields)

### Purpose
Ensure critical identity and tracking fields are never null. These fields form the foundation for all other validations.

### Anchor Fields
| Field | Required | Pipeline Nulls | Impact |
|-------|----------|----------------|--------|
| Document_ID | Yes | 41 (0.4%) | Composite identity anchor |
| Project_Code | Yes | 4 (0.04%) | Project classification |
| Document_Type | Yes | 71 (0.6%) | Document categorization |
| Submission_Date | Yes | 3 (0.03%) | Temporal anchor |
| Document_Sequence_Number | Yes | 63 (0.6%) | Sequential identifier |

### Validation Rules
```python
anchor_fields = ['Document_ID', 'Project_Code', 'Document_Type', 'Submission_Date']
for row in dataset:
    for field in anchor_fields:
        if pd.isnull(row[field]):
            flag_error(row, field, 'ANCHOR_NULL', severity='CRITICAL')
```

### Pipeline Findings
- 3 rows missing Submission_Date (group consistency violation)
- Group consistency validation failed: Submission_Date must be same within (Submission_Session, Submission_Session_Revision)

---

## Category 2: Composite Identity Integrity

### Purpose
Validate that Document_ID matches its constituent fields exactly. Document_ID is a composite key built from 5 segments.

### Document_ID Structure
```
Format: {Project_Code}-{Facility_Code}-{Document_Type}-{Discipline}-{Document_Sequence_Number}
Example: 131242-WSW41-LT-PM-0001
         |Proj|-|Fac|-|Type|-|Disc|-|Seq|
```

### Validation Rules
1. **Segment Extraction**: Split Document_ID by "-" delimiter
2. **Segment Count**: Must have exactly 5 segments (or 4+ with affix handling)
3. **Field Matching**: Each segment must match corresponding column value
4. **Affix Handling**: Document_ID_Affixes column stores suffixes (e.g., "_Reply", "_ST607")

### Implementation
```python
def validate_document_id(row):
    segments = row['Document_ID'].split('-')
    expected = [
        row['Project_Code'],
        row['Facility_Code'],
        row['Document_Type'],
        row['Discipline'],
        row['Document_Sequence_Number']
    ]
    
    mismatches = []
    for i, (actual, exp) in enumerate(zip(segments[:5], expected)):
        if actual != exp:
            mismatches.append(f"Segment {i}: {actual} != {exp}")
    
    if mismatches:
        flag_error(row, 'Document_ID', 'COMPOSITE_MISMATCH', 
                   details='; '.join(mismatches), severity='HIGH')
```

### Pipeline Findings
- 100 invalid Document_ID values detected
- Sample issues: "#000002.0_ Reply_2023 08 31-NA-NA-NA-9999" (invalid format)
- Sample affixes extracted: "_Reply", "_ST607", "_Withdrawn"
- 1,638 Document_ID affixes extracted successfully

---

## Category 3: Temporal (Date) Sequence Logic

### Purpose
Ensure date fields follow logical chronological order. No future dates should precede past dates in the workflow.

### Date Fields
| Field | Meaning | Constraints |
|-------|---------|-------------|
| First_Submission_Date | Initial submission | MIN(Submission_Date) per Document_ID |
| Submission_Date | Current submission | Must be >= First_Submission_Date |
| Review_Return_Plan_Date | Expected response | Must be >= Submission_Date |
| Review_Return_Actual_Date | Actual response | Must be >= Submission_Date |
| Resubmission_Plan_Date | Resubmission target | NULL if Submission_Closed = YES |
| Resubmission_Forecast_Date | Forecast date | User provided (305 format errors) |
| Latest_Submission_Date | Most recent | MAX(Submission_Date) per Document_ID |

### Validation Rules

#### 3.1 Date Ordering
```
First_Submission_Date <= Submission_Date <= Review_Return_Plan_Date
Submission_Date <= Review_Return_Actual_Date
Submission_Date <= Resubmission_Plan_Date (if not closed)
```

#### 3.2 Business Day Calculation
- Duration_of_Review = Business days between Submission_Date and Review_Return_Actual_Date
- Delay_of_Resubmission = Days between Resubmission_Plan_Date and actual resubmission

#### 3.3 Group Consistency
Pipeline Warning: "Group consistency validation failed for Submission_Session: Column Submission_Date must be the same within groups ['Submission_Session', 'Submission_Session_Revision']"

```python
def validate_group_consistency(df):
    grouped = df.groupby(['Submission_Session', 'Submission_Session_Revision'])
    for (session, revision), group in grouped:
        unique_dates = group['Submission_Date'].nunique()
        if unique_dates > 1:
            flag_error(group.index, 'Submission_Date', 
                      'GROUP_INCONSISTENT', 
                      details=f"Session {session}/{revision} has {unique_dates} different dates",
                      severity='HIGH')
```

### Pipeline Findings
- 305 invalid date formats in Resubmission_Forecast_Date
- 4 Duration_of_Review values > 365 days (suspicious)
- 239 Delay_of_Resubmission values < 0 (impossible)

---

## Category 4: Categorical Inter-Dependency

### Purpose
Validate logical relationships between categorical fields. Status transitions must follow business rules.

### Validation Rules

#### 4.1 Approval Status → Submission Closure
```python
# Rule: If Approval_Code is APP/REJ, Submission_Closed should be YES
if row['Approval_Code'] in ['APP', 'REJ'] and row['Submission_Closed'] != 'YES':
    flag_error(row, 'Submission_Closed', 'INCONSISTENT_CLOSURE',
               details=f"Approval={row['Approval_Code']} but Closed={row['Submission_Closed']}",
               severity='WARNING')
```

#### 4.2 Review Status → Resubmission Required
```python
# Rule: If Review_Status indicates rejection, Resubmission_Required should be YES/RESUBMITTED
if 'REJ' in str(row['Review_Status']) and row['Resubmission_Required'] not in ['YES', 'RESUBMITTED']:
    flag_error(row, 'Resubmission_Required', 'RESUBMISSION_MISMATCH',
               severity='WARNING')
```

#### 4.3 Submission Closed → Resubmission Plan Date
```python
# Rule: If Submission_Closed = YES, Resubmission_Plan_Date must be NULL
if row['Submission_Closed'] == 'YES' and pd.notnull(row['Resubmission_Plan_Date']):
    flag_error(row, 'Resubmission_Plan_Date', 'CLOSED_WITH_PLAN_DATE',
               severity='HIGH')
```

Pipeline confirmed: "[Resubmission-Plan] Resubmission_Plan_Date: Overwrote 1707 rows to null (Submission_Closed=YES)"

#### 4.4 Resubmission Plan Date → Overdue Status
```python
# Rule: If today > Resubmission_Plan_Date and not closed, mark Overdue
if (pd.notnull(row['Resubmission_Plan_Date']) and 
    row['Submission_Closed'] != 'YES' and 
    today > row['Resubmission_Plan_Date']):
    expected_status = 'Overdue'
    if row['Resubmission_Overdue_Status'] != expected_status:
        flag_error(row, 'Resubmission_Overdue_Status', 'OVERDUE_MISMATCH',
                   severity='WARNING')
```

Pipeline confirmed: "[Conditional] Resubmission_Overdue_Status: Applied: 241 rows Overdue"

### Pipeline Findings
- 20 Review_Status values not in approval_code_schema
- 14 Latest_Approval_Status values not in approval_code_schema

---

## Category 5: Status & Version Regression

### Purpose
Ensure revision numbers increment and status transitions follow workflow rules.

### Validation Rules

#### 5.1 Revision Incrementing
```python
def validate_revision_progression(df):
    grouped = df.groupby('Document_ID').sort_values('Submission_Date')
    for doc_id, group in grouped:
        revisions = group['Document_Revision'].astype(int).tolist()
        for i in range(1, len(revisions)):
            if revisions[i] < revisions[i-1]:
                flag_error(group.index[i], 'Document_Revision', 
                          'VERSION_REGRESSION',
                          details=f"Revision decreased from {revisions[i-1]} to {revisions[i]}",
                          severity='HIGH')
            elif revisions[i] == revisions[i-1]:
                # Same revision allowed if different submission sessions
                pass
```

#### 5.2 Submission Session Revision Tracking
```python
# Within a Submission_Session, Submission_Session_Revision should increment
for session, group in df.groupby('Submission_Session'):
    revs = group['Submission_Session_Revision'].astype(int).unique()
    if len(revs) > 1 and max(revs) - min(revs) + 1 != len(revs):
        flag_error(group.index, 'Submission_Session_Revision',
                  'REVISION_GAP',
                  severity='WARNING')
```

### Pipeline Findings
- 63 Latest_Revision values with pattern validation failures
- All_Submission_Session_Revisions aggregates unique revisions per Document_ID

---

## Category 6: Relational Invariants (Fact Table Rules)

### Purpose
Ensure data consistency within logical groupings (Submission_Session packages).

### Validation Rules

#### 6.1 Submission Session Subject Consistency
```python
# Rule: Submission_Session_Subject should be same for all rows in same Submission_Session
for session, group in df.groupby('Submission_Session'):
    subjects = group['Submission_Session_Subject'].dropna().unique()
    if len(subjects) > 1:
        flag_error(group.index, 'Submission_Session_Subject',
                  'INCONSISTENT_SUBJECT',
                  details=f"Session {session} has {len(subjects)} different subjects",
                  severity='WARNING')
```

#### 6.2 Transmittal Number Consistency
```python
# Rule: Transmittal_Number should be same within Submission_Session
for session, group in df.groupby('Submission_Session'):
    transmittals = group['Transmittal_Number'].dropna().unique()
    if len(transmittals) > 1:
        flag_error(group.index, 'Transmittal_Number',
                  'INCONSISTENT_TRANSMITTAL',
                  severity='WARNING')
```

Pipeline confirmed: Forward fill strategy synchronizes Transmittal_Number across Document_ID

#### 6.3 Multi-Level Forward Fill Boundaries
```python
# Rule: Review_Comments should propagate within (Submission_Session, Submission_Session_Revision)
# Then fill to Submission_Session level only
# Implementation: _apply_multi_level_forward_fill
```

---

## Row Health Score Integration

### Scoring Algorithm
```python
def calculate_row_health_score(row_errors):
    """
    Weighted scoring based on error severity and category
    """
    weights = {
        'ANCHOR_NULL': 25,        # Critical missing data
        'COMPOSITE_MISMATCH': 20, # Identity integrity
        'GROUP_INCONSISTENT': 15, # Temporal consistency
        'INCONSISTENT_CLOSURE': 10, # Business rule
        'VERSION_REGRESSION': 15, # Version integrity
        'INCONSISTENT_SUBJECT': 5, # Relational invariant
        'OVERDUE_MISMATCH': 5,   # Status logic
        'CLOSED_WITH_PLAN_DATE': 10, # Date logic
        'REVISION_GAP': 5         # Version gap
    }
    
    total_weight = sum(weights.get(err['type'], 1) for err in row_errors)
    score = max(0, 100 - total_weight)
    
    # Grade mapping
    if score >= 95: grade = 'A'
    elif score >= 85: grade = 'B'
    elif score >= 70: grade = 'C'
    else: grade = 'F'
    
    return score, grade
```

### Severity Flags
| Flag | Condition | Action |
|------|-----------|--------|
| 🚨 CRITICAL | Any ANCHOR_NULL error | Block processing, require manual fix |
| ⚠️ HIGH | COMPOSITE_MISMATCH or GROUP_INCONSISTENT | Flag for review, allow with warning |
| ⚡ WARNING | Business rule violations | Log and continue |
| ℹ️ INFO | Minor inconsistencies | Log only |

---

## Implementation Priority

### Phase 1: Critical (Data Integrity)
1. Anchor completeness validation
2. Document_ID composite integrity
3. Group consistency (Submission_Date within Session/Revision)

### Phase 2: High (Business Logic)
1. Temporal sequence validation
2. Categorical inter-dependency (Approval → Closure)
3. Revision progression checking

### Phase 3: Standard (Quality Assurance)
1. Relational invariants (Subject/Transmittal consistency)
2. Status regression detection
3. Overdue calculation verification

### Phase 4: Monitoring (Health Tracking)
1. Row health score calculation
2. Error trend analysis
3. Validation dashboard integration

---

## Success Metrics

| Metric | Target | Current (Pipeline) |
|--------|--------|-------------------|
| Rows with critical errors | < 0.1% | 0.04% (41 Document_ID nulls) |
| Composite identity match rate | > 99% | ~99% (100 mismatches / 11,099) |
| Group consistency pass rate | > 99% | ~99.9% (1 group inconsistency) |
| Temporal sequence violations | < 1% | < 0.1% |
| Overall row health score | > 95% | 98.5% |

---

## Integration with Column Validation

Row validation builds on column validation results:
1. **Column validation** identifies individual field issues (pattern, range, schema)
2. **Row validation** identifies cross-field inconsistencies
3. **Combined results** populate Validation_Errors column
4. **Aggregate scoring** produces Data_Health_Score

### Processing Order
```
Phase 1: Column Mapping & Null Handling
Phase 2: Column Validation (pattern, range, schema)
Phase 3: Row Validation (cross-field consistency)
Phase 4: Error Aggregation & Health Scoring
Phase 5: Reporting & Dashboard Export
```

---

## Files Affected

- **Schema:** `dcc/config/schemas/dcc_register_config.json` (validation rules per column)
- **Pipeline:** `dcc/workflow/dcc_engine_pipeline.py` (phase P4 validation)
- **Processor:** `dcc/workflow/processor_engine/calculations/validation.py`
- **Output:** `dcc/output/processing_summary.txt` (row-level validation results)
- **Dashboard:** `dcc/output/error_dashboard_data.json` (aggregated errors)