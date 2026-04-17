# Phase 10 Test 5 Remedy Workplan: Column Optimization Pattern Coverage

**Issue:** Phase 10 Test 5 (Column Optimization Testing) failed with 0/47 pattern coverage  
**Target:** ≥25/47 columns using reusable pattern references  
**Status:** Remediation Required  
**Date:** 2026-04-17

---

## Problem Analysis

### Current State
- `dcc_register_config.json` has reusable pattern definitions:
  - `column_types` array: id_column, code_column, date_column, sequence_column, status_column (5 types)
  - `column_patterns` array: pattern_validation, schema_validation, range_validation
  - `column_strategies` array: forward_fill_with_padding, multi_level_forward_fill

- Individual column definitions (47 total) do NOT reference these reusable patterns
- Each column currently has inline definitions for:
  - `data_type` (numeric, string, categorical, date, text)
  - `validation` (array of validation rules)
  - `null_handling` (strategy)
  - `processing_phase`

### Additional Column Types Required
To achieve higher pattern coverage, add the following column types to `column_types` array:
- **numeric_column**: For numeric data types (Duration_of_Review, Delay_of_Resubmission, Row_Index)
- **text_column**: For free-text fields (Document_Title, Review_Comments, Notes, etc.)
- **boolean_column**: For boolean flags (Resubmission_Required, Submission_Closed)
- **score_column**: For calculated scores (Data_Health_Score)
- **json_column**: For JSON array fields (All_Submission_Sessions, All_Submission_Dates, All_Approval_Code)

### Root Cause
Columns in `dcc_register_config.json` lack nested pattern reference keys to the reusable patterns defined in `column_types`, `column_patterns`, and `column_strategies`.

---

## Remedy Strategy

### Approach: Add Nested Pattern Reference Keys

**Step 1: Expand column_types array in dcc_register_config.json**

Add the following column type definitions to the `column_types` array:
```json
"column_types": [
  {
    "id_column": {
      "data_type": "string",
      "is_calculated": true,
      "create_if_missing": true
    },
    "code_column": {
      "data_type": "categorical",
      "is_calculated": false
    },
    "date_column": {
      "data_type": "date",
      "is_calculated": false
    },
    "sequence_column": {
      "data_type": "string",
      "is_calculated": false
    },
    "status_column": {
      "data_type": "categorical",
      "is_calculated": false
    },
    "numeric_column": {
      "data_type": "numeric",
      "is_calculated": false
    },
    "text_column": {
      "data_type": "text",
      "is_calculated": false
    },
    "boolean_column": {
      "data_type": "boolean",
      "is_calculated": false
    },
    "score_column": {
      "data_type": "numeric",
      "is_calculated": true
    },
    "json_column": {
      "data_type": "string",
      "is_calculated": true
    }
  }
]
```

**Step 2: Add nested keys to each column definition**

Add the `column_type` nested key to each column definition in `dcc_register_config.json`:
1. **`column_type`**: Reference to expanded `column_types` (10 types total)
2. **`pattern`**: Reference to `column_patterns` (pattern_validation, schema_validation, range_validation)
3. **`strategy`**: Reference to `column_strategies` (forward_fill_with_padding, multi_level_forward_fill)

### Column-to-Pattern Mapping

Based on column characteristics, map columns to appropriate patterns:

| Column Type | Columns | Pattern Key |
|-------------|---------|-------------|
| **code_column** | Project_Code, Facility_Code, Document_Type, Discipline, Department, Approval_Code, Review_Status_Code, Submitted_By, Reviewer | `column_type: "code_column"` |
| **sequence_column** | Document_Sequence_Number, Submission_Session, Submission_Session_Revision, Document_Revision, Latest_Revision | `column_type: "sequence_column"` |
| **date_column** | Submission_Date, First_Submission_Date, Latest_Submission_Date, Review_Return_Actual_Date, Review_Return_Plan_Date, Resubmission_Plan_Date, Resubmission_Forecast_Date | `column_type: "date_column"` |
| **status_column** | Review_Status, Latest_Approval_Status, Resubmission_Required, Submission_Closed, Resubmission_Overdue_Status, This_Submission_Approval_Code | `column_type: "status_column"` |
| **id_column** | Document_ID, Row_Index, Transmittal_Number | `column_type: "id_column"` |
| **numeric_column** | Duration_of_Review, Delay_of_Resubmission, Count_of_Submissions | `column_type: "numeric_column"` |
| **text_column** | Document_Title, Review_Comments, Notes, Submission_Session_Subject, Consolidated_Submission_Session_Subject, Submission_Reference_1, Internal_Reference, Document_ID_Affixes | `column_type: "text_column"` |
| **boolean_column** | Resubmission_Required, Submission_Closed (can be mapped from status_column) | `column_type: "boolean_column"` |
| **score_column** | Data_Health_Score | `column_type: "score_column"` |
| **json_column** | All_Submission_Sessions, All_Submission_Dates, All_Submission_Session_Revisions, All_Approval_Code, Validation_Errors | `column_type: "json_column"` |

**Expected Coverage:** 41/48 columns (85.4%) - significantly exceeds target of 25/48 (52.1%)

### Comprehensive Column Definition Table

| Column | Data Type | Column Group | Column Type Pattern | Validation Strategy | Processing Phase | Null Handling Strategy |
|--------|-----------|--------------|---------------------|---------------------|------------------|----------------------|
| Row_Index | numeric | - | id_column | min_value | P1 | create_if_missing |
| Transmittal_Number | string | submission_info | id_column | pattern | P1 | forward_fill |
| Submission_Session | string | submission_info | sequence_column | pattern | P1 | forward_fill_with_padding |
| Submission_Session_Revision | string | submission_info | sequence_column | pattern | P1 | forward_fill_with_padding |
| Submission_Session_Subject | string | submission_info | text_column | pattern | P1 | forward_fill |
| Department | categorical | submission_info, metadata | code_column | schema_reference_check | P1 | forward_fill |
| Submitted_By | categorical | submission_info | code_column | pattern | P1 | forward_fill |
| Submission_Date | date | submission_info | date_column | pattern | P1 | multi_level_forward_fill |
| Project_Code | categorical | document_info, metadata | code_column | pattern, schema_reference_check | P1 | default_value |
| Facility_Code | categorical | document_info, metadata | code_column | pattern, schema_reference_check | P1 | default_value |
| Document_Type | categorical | document_info | code_column | schema_reference_check | P1 | default_value |
| Discipline | categorical | document_info, metadata | code_column | schema_reference_check | P1 | default_value |
| Document_Sequence_Number | string | document_info | sequence_column | pattern | P1 | forward_fill_with_padding |
| Document_ID | string | document_info | id_column | pattern, derived_pattern, starts_with_schema_reference | P2.5 | default_value |
| Document_ID_Affixes | string | - | text_column | pattern | P2.5 | default_value |
| Document_Revision | string | document_info | sequence_column | pattern | P2 | forward_fill |
| Document_Title | text | document_info | text_column | pattern | P2 | leave_null |
| Reviewer | categorical | - | code_column | pattern | P2 | forward_fill |
| Review_Return_Actual_Date | date | review_info | date_column | pattern | P2 | leave_null |
| Review_Return_Plan_Date | date | - | date_column | pattern | P2 | leave_null |
| Review_Status | categorical | review_info | status_column | schema_reference_check | P2 | default_value |
| Review_Status_Code | categorical | - | code_column | schema_reference_check | P2 | default_value |
| Review_Comments | text | - | text_column | pattern | P2 | leave_null |
| Duration_of_Review | numeric | - | numeric_column | range_validation | P2 | leave_null |
| Approval_Code | categorical | review_info | code_column | schema_reference_check | P2 | forward_fill |
| First_Submission_Date | date | - | date_column | pattern | P2 | leave_null |
| Latest_Submission_Date | date | - | date_column | pattern | P2 | leave_null |
| Latest_Revision | string | - | sequence_column | pattern | P2 | forward_fill |
| All_Submission_Sessions | string | - | json_column | pattern | P3 | leave_null |
| All_Submission_Dates | string | - | json_column | pattern | P3 | leave_null |
| All_Submission_Session_Revisions | string | - | json_column | pattern | P3 | leave_null |
| Count_of_Submissions | numeric | - | numeric_column | range_validation | P2 | leave_null |
| Latest_Approval_Status | categorical | - | status_column | schema_reference_check | P3 | default_value |
| Latest_Approval_Code | categorical | - | code_column | schema_reference_check | P3 | default_value |
| All_Approval_Code | string | - | json_column | pattern | P3 | leave_null |
| Consolidated_Submission_Session_Subject | text | - | text_column | pattern | P3 | leave_null |
| Submission_Closed | categorical | - | status_column, boolean_column | schema_reference_check | P3 | default_value |
| Resubmission_Required | categorical | - | status_column, boolean_column | schema_reference_check | P3 | default_value |
| Resubmission_Plan_Date | date | - | date_column | pattern | P3 | leave_null |
| Resubmission_Forecast_Date | date | - | date_column | pattern | P3 | leave_null |
| Resubmission_Overdue_Status | categorical | - | status_column | schema_reference_check | P3 | default_value |
| Delay_of_Resubmission | numeric | - | numeric_column | range_validation | P3 | leave_null |
| Notes | text | - | text_column | pattern | P3 | leave_null |
| Submission_Reference_1 | text | - | text_column | pattern | P3 | leave_null |
| Internal_Reference | text | - | text_column | pattern | P3 | leave_null |
| This_Submission_Approval_Code | categorical | - | status_column | schema_reference_check | P3 | default_value |
| Validation_Errors | string | - | json_column | pattern | P3 | default_value |
| Data_Health_Score | numeric | - | score_column | range_validation | P3 | default_value |

**Note:** All 48 columns now mapped to pattern types (Data_Health_Score added to schema, Row_Index mapped to id_column)

---

## Implementation Steps

### Step 1: Expand column_types Array

Update the `column_types` array in `dcc_register_config.json` to include 5 new column types:
- numeric_column
- text_column
- boolean_column
- score_column
- json_column

### Step 2: Add Nested Keys to Code Columns (9 columns)

Add `column_type: "code_column"` to:
- Project_Code
- Facility_Code
- Document_Type
- Discipline
- Department
- Approval_Code
- Review_Status_Code
- Submitted_By
- Reviewer

**Example for Project_Code:**
```json
"Project_Code": {
  "aliases": ["Proj. Code", "Project Code", "Proj Code"],
  "data_type": "categorical",
  "required": true,
  "allow_null": false,
  "is_calculated": false,
  "create_if_missing": true,
  "schema_reference": "project_code_schema",
  "column_type": "code_column",  // <-- ADD THIS
  "null_handling": {
    "strategy": "default_value",
    "default_value": "NA"
  },
  "validation": [...],
  "processing_phase": "P1"
}
```

### Step 3: Add Nested Keys to Sequence Columns (5 columns)

Add `column_type: "sequence_column"` to:
- Document_Sequence_Number
- Submission_Session
- Submission_Session_Revision
- Document_Revision
- Latest_Revision

### Step 4: Add Nested Keys to Date Columns (7 columns)

Add `column_type: "date_column"` to:
- Submission_Date
- First_Submission_Date
- Latest_Submission_Date
- Review_Return_Actual_Date
- Review_Return_Plan_Date
- Resubmission_Plan_Date
- Resubmission_Forecast_Date

### Step 5: Add Nested Keys to Status Columns (6 columns)

Add `column_type: "status_column"` to:
- Review_Status
- Latest_Approval_Status
- Resubmission_Required
- Submission_Closed
- Resubmission_Overdue_Status
- This_Submission_Approval_Code

### Step 6: Add Nested Keys to ID Columns (3 columns)

Add `column_type: "id_column"` to:
- Document_ID
- Row_Index
- Transmittal_Number

### Step 7: Add Nested Keys to Numeric Columns (3 columns)

Add `column_type: "numeric_column"` to:
- Duration_of_Review
- Delay_of_Resubmission
- Count_of_Submissions

### Step 8: Add Nested Keys to Text Columns (9 columns)

Add `column_type: "text_column"` to:
- Document_Title
- Review_Comments
- Notes
- Submission_Session_Subject
- Consolidated_Submission_Session_Subject
- Submission_Reference_1
- Internal_Reference
- Document_ID_Affixes
- Validation_Errors

### Step 9: Add Nested Keys to Boolean Columns (2 columns)

Add `column_type: "boolean_column"` to:
- Resubmission_Required (optional - can use status_column)
- Submission_Closed (optional - can use status_column)

### Step 10: Add Nested Keys to Score Column (1 column)

Add `column_type: "score_column"` to:
- Data_Health_Score

### Step 11: Add Nested Keys to JSON Columns (5 columns)

Add `column_type: "json_column"` to:
- All_Submission_Sessions
- All_Submission_Dates
- All_Submission_Session_Revisions
- All_Approval_Code
- Validation_Errors

---

## Validation Criteria

After implementing the nested pattern reference keys, verify:

1. **Pattern Coverage:** Count columns with `column_type` key → should be ≥25/48
2. **Schema Validation:** Run schema validation to ensure JSON structure is valid
3. **Pipeline Test:** Run `dcc_engine_pipeline.py` to ensure processing still works
4. **Phase 10 Re-test:** Re-run Phase 10 Test 5 to confirm pattern coverage ≥25/48

---

## Success Metrics

| Metric | Target | Expected |
|--------|--------|----------|
| Pattern Coverage | ≥25/48 | 41/48 (85.4%) |
| Code Columns | - | 9 columns |
| Sequence Columns | - | 5 columns |
| Date Columns | - | 7 columns |
| Status Columns | - | 6 columns |
| ID Columns | - | 3 columns |
| Numeric Columns | - | 3 columns |
| Text Columns | - | 8 columns |
| Boolean Columns | - | 2 columns (optional) |
| Score Columns | - | 1 column |
| JSON Columns | - | 5 columns |

**Expected Result:** 41/48 pattern coverage (85.4%) - significantly exceeds target of 25/48 (52.1%)

---

## Estimated Effort

- **Analysis:** 30 minutes
- **column_types Array Expansion:** 15 minutes (add 5 new column type definitions)
- **Implementation:** 3-4 hours (41 column updates across 10 column types)
- **Validation:** 30 minutes
- **Total:** 4-5.5 hours

---

## Risks and Mitigations

### Risk 1: Breaking Pipeline
- **Mitigation:** Test pipeline after each batch of 5-10 column updates
- **Fallback:** Revert to previous version if pipeline fails

### Risk 2: Incorrect Pattern Mapping
- **Mitigation:** Review each column's characteristics before assigning pattern
- **Fallback:** Adjust mapping based on validation results

### Risk 3: Schema Validation Errors
- **Mitigation:** Validate JSON structure after each batch update
- **Fallback:** Fix syntax errors before proceeding

---

## Next Steps

1. **Review and Approve:** Review this workplan and approve implementation
2. **Expand column_types Array:** Add 5 new column type definitions (numeric_column, text_column, boolean_column, score_column, json_column)
3. **Implementation:** Add nested pattern reference keys to 41 columns across 10 column types
4. **Validation:** Run schema validation and pipeline test
5. **Re-test Phase 10:** Re-run Phase 10 Test 5 to confirm pattern coverage ≥25/48
6. **Update Report:** Regenerate Phase 10 report with updated results

---

**Workplan Status:** Pending Approval  
**Created:** 2026-04-17  
**Location:** workplan/schema_processing/rebuild_schema_workplan/phase_10_test_5_remedy_workplan.md
