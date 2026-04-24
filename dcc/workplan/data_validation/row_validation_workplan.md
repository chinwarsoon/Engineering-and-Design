# Row Validation Workplan (Finalized)

**Based on:** dcc_register_rule.md, dcc_engine_pipeline.py, and processor_engine implementation.
**Last Updated:** 2026-04-18

---

## Overview

Row-level validation ensures internal consistency across columns within each row. This workplan defines the implementation of cross-field business logic, temporal sequence checks, and relational invariants for the DCC Register.

**Validation Strategy:**
- **Execution Timing:** Phase 4 (Validation), performed after all columns are mapped and calculated.
- **Engine Integration:** Logic resides in `processor_engine/calculations/validation.py` and specialized detectors in `processor_engine/error_handling/detectors/`.
- **Integrity Level:** Focuses on relationships (e.g., "If A then B") rather than individual values.

---

## Phase 1: Anchor & Composite Integrity

This phase validates the fundamental relationships that define a document's identity and its place in the project.

### 1.1 Scope & Functions
- **Functions to Review/Update:**
  - `validate_document_id`: Verify the composite match between `Document_ID` and its 5 constituent fields.
  - `extract_document_id_affixes`: Ensure suffixes are correctly extracted and stored in `Document_ID_Affixes`.
- **Validation Rules:**
  - **Composite Identity:** `Document_ID` segments MUST match `Project`, `Facility`, `Type`, `Discipline`, and `Sequence`.
  - **Anchor Completeness:** Ensure no "Anchor" row is missing its primary relationship keys.

### 1.2 Target Achievement & Success Factors
- **Target:** 100% agreement between composite keys and their segments.
- **Success Factors:**
  - Correct handling of 1,600+ extracted affixes without flagging them as errors.
  - Identification of all 100+ legacy format mismatches in `Document_ID`.

### 1.3 Deliverables
- Robust `Document_ID` cross-validation logic.
- Affix-aware pattern matcher.
- Phase 1 integrity report (Row-level mismatches).

### 1.4 Potential Issues
- Varied delimiters in legacy `Document_ID` values (e.g., `_` vs `-`).
- Leading/trailing whitespace in constituent columns causing mismatch.

---

## Phase 2: Temporal & Logical Sequence

This phase ensures the document workflow follows a logical chronological and status-based progression.

### 2.1 Scope & Functions
- **Functions to Review/Update:**
  - `validate_date_sequence`: Check for "Date Inversion" (e.g., Review Date < Submission Date).
  - `validate_status_closure`: Verify `Submission_Closed` logic against `Approval_Code`.
  - `validate_closed_resubmission`: Verify `Resubmission_Required=NO` when `Submission_Closed=YES`.
- **Validation Rules:**
  - **Temporal Logic:** `Submission_Date <= Review_Return_Actual_Date`.
  - **Conditional Closure:** `Resubmission_Plan_Date` MUST be NULL if `Submission_Closed=YES`.
  - **Closed Resubmission:** `Resubmission_Required` MUST be NO if `Submission_Closed=YES`.
  - **Status Inter-dependency:** `Review_Status` containing "REJ" must trigger `Resubmission_Required=YES`.

### 2.2 Target Achievement & Success Factors
- **Target:** Zero logical contradictions in date and status fields.
- **Success Factors:**
  - Detection of all 239 negative `Delay_of_Resubmission` values.
  - Validation of 241 `Overdue` status flags against current date.

### 2.3 Deliverables
- Logic-gate validation module in `validation.py`.
- Suite of "Business Rule" test cases (Positive/Negative).
- Phase 2 logical consistency report.

### 2.4 Potential Issues
- Handling of "NA" or placeholder dates in temporal calculations.
- Timezone discrepancies between `today()` and historical date strings.

---

## Phase 3: Relational Invariants & Aggregation

This phase validates the consistency of data within logical groups, such as Submission Sessions and Document Histories.

### 3.1 Scope & Functions
- **Functions to Review/Update:**
  - `validate_group_consistency`: Ensure `Submission_Date` and `Transmittal_Number` are uniform within a `Submission_Session`.
  - `validate_revision_progression`: Check for version regression per `Document_ID`.
- **Validation Rules:**
  - **Group Invariants:** All rows in a `Submission_Session` must share the same `Subject` and `Date`.
  - **Version Integrity:** `Document_Revision` must not decrease for subsequent submissions of the same `Document_ID`.
  - **Aggregate Accuracy:** Verify `Count_of_Submissions` matches the actual row count per `Document_ID`.

### 3.2 Target Achievement & Success Factors
- **Target:** 100% consistency within submission packages and document histories.
- **Success Factors:**
  - Identifying `REVISION_GAP` or `VERSION_REGRESSION` in historical data.
  - Successful validation of all 11,099 rows against group-level rules.

### 3.3 Deliverables
- Group-based validation logic (using Pandas `groupby` and `transform`).
- History-aware revision validator.
- Phase 3 relational integrity report.

### 3.4 Potential Issues
- Performance hit when performing multiple `groupby` operations on large datasets.
- Ambiguous revision formats (e.g., `A` vs `01`) complicating comparison logic.

---

## Final Phase Reports (Summary)

Each phase will produce a report within the `dcc/workplan/data_validation` directory:
1. `row_validation_p1_identity.md`: Results of composite key and anchor checks.
2. `row_validation_p2_logic.md`: Results of date sequence and status transition checks.
3. `row_validation_p3_relational.md`: Results of group consistency and revision checks.
