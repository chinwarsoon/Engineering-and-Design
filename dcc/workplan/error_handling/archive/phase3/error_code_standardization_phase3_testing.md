# Error Code Standardization — Phase 3 Testing Workplan

**Date:** 2026-04-24  
**Phase:** 3 (Testing & Validation)  
**Status:** IN PROGRESS  
**Related:** Issue #62, Phase 1 & 2 Complete  

---

## Objectives

Validate that the error code standardization implementation works correctly across the entire pipeline:
1. Schema files validate correctly
2. Error codes are properly recognized by detectors
3. Error messages display correctly (English & Chinese)
4. Health scores calculate correctly with new codes
5. No regression in existing functionality

---

## Test Scenarios

### 1. Schema Validation Tests

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| SCHEMA-01 | Validate error_code_base.json against JSON Schema draft-07 | Pass |
| SCHEMA-02 | Validate error_code_setup.json (allOf inheritance) | Pass |
| SCHEMA-03 | Validate system_error_config.json (20 codes) | Pass |
| SCHEMA-04 | Validate data_error_config.json (17 codes) | Pass |
| SCHEMA-05 | Verify URI references resolve correctly | All $refs resolve |

### 2. Error Code Format Tests

| Test ID | Test Code | Format Check | Expected |
|---------|-----------|--------------|----------|
| FORMAT-01 | L3-L-V-0302 | LL-M-F-XXXX | Valid |
| FORMAT-02 | S-C-S-0301 | S-C-S-XXXX | Valid |
| FORMAT-03 | P1-A-P-0101 | LL-M-F-XXXX | Valid |
| FORMAT-04 | V5-I-V-0501 | LL-M-F-XXXX | Valid |
| FORMAT-05 | INVALID | Invalid format | Rejected |

### 3. Detector Integration Tests

| Test ID | Error Code | Detector Method | Scenario |
|---------|------------|-----------------|----------|
| DET-01 | L3-L-V-0302 | detect_closed_submission_with_plan_date | Closed=YES, Plan Date set |
| DET-02 | L3-L-V-0303 | detect_resubmission_mismatch | REJ status without resubmit |
| DET-03 | L3-L-V-0304 | detect_overdue_mismatch | Past plan date, wrong status |
| DET-04 | L3-L-V-0305 | detect_version_regression | Rev decreases per doc |
| DET-05 | L3-L-V-0306 | detect_revision_gap | Gap in session revisions |
| DET-06 | L3-L-V-0307 | detect_closed_with_resubmission | Closed=YES, Resubmit=YES |

### 4. Message Resolution Tests

| Test ID | Locale | Code | Expected Message |
|---------|--------|------|------------------|
| MSG-01 | en | L3-L-V-0302 | "Submission_Closed=YES but Resubmission_Plan_Date is set" |
| MSG-02 | en | L3-L-V-0305 | "Current revision appears older than previous revision..." |
| MSG-03 | zh | L3-L-V-0302 | "提交已关闭但重新提交计划日期已设置" |
| MSG-04 | zh | L3-L-V-0305 | "同一文档 ID 的当前版本号小于之前的版本号" |

### 5. Health Score Calculation Tests

| Test ID | Error Codes | Expected Score Impact |
|---------|-------------|---------------------|
| HEALTH-01 | L3-L-V-0305 (x1) | -15 points |
| HEALTH-02 | L3-L-V-0302 (x2) | -20 points |
| HEALTH-03 | Multiple different codes | Sum of weights |

---

## Test Data Requirements

### Sample Data Files Needed
1. `test_closed_with_plan_date.xlsx` - Rows with Submission_Closed=YES and Resubmission_Plan_Date set
2. `test_resubmission_mismatch.xlsx` - Rows with REJ status but Resubmission_Required not YES
3. `test_version_regression.xlsx` - Rows where Document_Revision decreases per Document_ID
4. `test_revision_gap.xlsx` - Rows with non-sequential Submission_Session_Revision
5. `test_overdue_mismatch.xlsx` - Rows with past Resubmission_Plan_Date but wrong status

---

## Test Execution Plan

### Step 1: Schema Validation (15 min)
```bash
# Validate all schema files
python -m jsonschema dcc/config/schemas/error_code_base.json
python -m jsonschema dcc/config/schemas/error_code_setup.json
python -m jsonschema dcc/config/schemas/system_error_config.json
python -m jsonschema dcc/config/schemas/data_error_config.json
```

### Step 2: Unit Tests (30 min)
```bash
# Run detector tests
cd dcc/workflow/processor_engine
python -m pytest error_handling/tests/ -v
```

### Step 3: Integration Tests (30 min)
```bash
# Run end-to-end pipeline test
python dcc_engine_pipeline.py --config test_config.json
```

### Step 4: Manual Verification (15 min)
- Check output error codes in logs
- Verify message display in UI
- Confirm health score calculations

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Schema validation | 100% pass (4/4 files) |
| Detector tests | 100% pass (6/6 scenarios) |
| Message resolution | 100% correct (4/4 locales) |
| Health scores | Accurate within ±1 point |
| No regression | All existing tests pass |

---

## Rollback Plan

If critical issues found:
1. Restore error_codes.json from archive
2. Revert row_validator.py changes
3. Use original system_error_codes.json
4. Document issues for Phase 4 fix

---

## Test Results Log

| Test ID | Status | Result | Notes |
|---------|--------|--------|-------|
| | | | |

---

**Estimated Duration:** 90 minutes  
**Dependencies:** Phase 1 & 2 complete  
**Risk Level:** Low (non-breaking changes)
