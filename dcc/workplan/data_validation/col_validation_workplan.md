# Column Validation Workplan (Finalized)

**Based on:** dcc_register_rule.md, dcc_engine_pipeline.py, and processor_engine implementation.
**Last Updated:** 2026-04-18

---

## Overview

Column-level validation ensures each of the 48 columns adheres to data type, format, schema references, and business rule constraints. This workplan defines the implementation and verification steps for Phase 4 (Validation) of the DCC Engine Pipeline.

**Validation Strategy:** 
- **Execution Timing:** MUST be performed AFTER Phase 3 (Calculations) to ensure all derived and filled values are present.
- **Engine Integration:** Implemented within `processor_engine/calculations/validation.py` and called by `CalculationEngine`.
- **Error Aggregation:** All failures are recorded in the `Validation_Errors` column and summarized for the UI Dashboard.

---

## Phase 1: Integrity Gate (Types, Nulls, Patterns)

This phase focuses on the fundamental structural integrity of the dataset, ensuring all "Anchor" and "Identity" columns are present and correctly formatted.

### 1.1 Scope & Functions
- **Functions to Review/Update:**
  - `apply_validation`: Ensure it correctly iterates over all 48 columns.
  - `_normalize_validation_rules`: Verify it supports all rule types defined in `dcc_register_rule.md`.
  - `collect_raw_pattern_errors`: Validate it captures pre-transformation errors for pattern-sensitive fields.
- **Validation Rules:**
  - **Null Checks:** Critical for `Document_ID`, `Project_Code`, `Document_Type`, `Submission_Date`, and `Document_Sequence_Number`.
  - **Pattern Matching:** Regex validation for `Project_Code`, `Document_Sequence_Number` (4-digit), `Submission_Session` (6-digit).
  - **Type Enforcement:** Numeric checks for `Row_Index`, `Duration_of_Review`, and `Count_of_Submissions`.

### 1.2 Target Achievement & Success Factors
- **Target:** 100% detection of null anchor columns and pattern mismatches in identity fields.
- **Success Factors:**
  - `Document_ID` null rate < 0.1% after processing.
  - All `Project_Code` values match `^[A-Z0-9-]+$`.
  - Zero-padding correctly applied before pattern validation.

### 1.3 Deliverables
- Updated `validation.py` with enhanced integrity checks.
- Unit tests for null and pattern validation.
- Phase 1 validation report (integrated into pipeline output).

### 1.4 Potential Issues
- Column name mismatches between raw data and schema.
- Data type coercion errors for numeric columns containing non-numeric strings.
- Over-aggressive pattern matching blocking valid but unusual codes.

---

## Phase 2: Domain Gate (Schemas, Ranges, Categorical)

This phase validates the data against business domain rules, including external schema references and logical value ranges.

### 2.1 Scope & Functions
- **Functions to Review/Update:**
  - `_apply_schema_reference_validation`: Ensure robust lookup against all 6 master schemas (Project, Facility, Type, Discipline, Department, Approval).
  - `_get_schema_reference_allowed_codes`: Handle multi-level schema lookups (e.g., Department, Submitted_By).
- **Validation Rules:**
  - **Schema Reference:** Validate 9 code columns against their respective JSON schemas.
  - **Range Validation:** `Duration_of_Review` and `Delay_of_Resubmission` must be within 0-365 days.
  - **Categorical Enum:** `Submission_Closed` (YES/NO), `Resubmission_Required` (4 states).

### 2.2 Target Achievement & Success Factors
- **Target:** 98% match rate for all schema-referenced columns.
- **Success Factors:**
  - Accurate detection of `Review_Status` values not in `approval_code_schema`.
  - Validation of `Department` and `Submitted_By` against `department_schema`.
  - Elimination of negative `Delay_of_Resubmission` values.

### 2.3 Deliverables
- Enhanced schema lookup logic in `validation.py`.
- Integration tests with real schema JSON files.
- Domain validation summary in `processing_summary.txt`.

### 2.4 Potential Issues
- Missing or outdated schema files in `dcc/config/schemas/`.
- Schema aliases or case-sensitivity causing false negatives.
- Logical contradictions in manual inputs (e.g., `Submission_Closed=YES` but with a plan date).

---

## Phase 3: Reporting & Health Score

The final phase aggregates all detected errors and computes the overall data quality metrics.

### 3.1 Scope & Functions
- **Functions to Review/Update:**
  - `record_errors`: Ensure consistent error code application from `ERROR_CODES` map.
  - `CalculationEngine.get_error_summary`: Structure the summary for the `reporting_engine`.
  - `ErrorReporter.export_dashboard_json`: Verify JSON structure for `error_diagnostic_dashboard.html`.
- **Calculation Rules:**
  - **Error Aggregation:** Concatenate all errors into `Validation_Errors` using `; ` separator.
  - **Health Scoring:** Apply weighted scoring (e.g., Anchor Null = 25 pts) to compute `Data_Health_Score`.

### 3.2 Target Achievement & Success Factors
- **Target:** Accurate and actionable data health report for every run.
- **Success Factors:**
  - `Data_Health_Score` reflects actual data quality (Grade A-F).
  - Dashboard JSON contains complete error localization (Row, Column, Error Code).
  - Summary report provides clear "Top Issues" section.

### 3.3 Deliverables
- Finalized `Validation_Errors` and `Data_Health_Score` implementation.
- Automated health scoring module.
- Phase 3 report: Data Health Dashboard preview.

### 3.4 Potential Issues
- Performance overhead of aggregating errors for very large datasets (10k+ rows).
- JSON serialization errors for complex error objects.
- Misleading health scores due to unweighted error counts.

---

## Final Phase Reports (Summary)

Each phase will produce a report within the `dcc/output/` directory:
1. `col_validation_p1_integrity.json`: Statistics on nulls and pattern failures.
2. `col_validation_p2_domain.json`: Schema match rates and range violations.
3. `col_validation_p3_final.json`: Final health scores and aggregated error summary.