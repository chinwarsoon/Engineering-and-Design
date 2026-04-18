# Column Validation Phase 2 Report — Domain Gate (Schemas, Ranges, Categorical)

**Phase:** 2 of 3  
**Workplan Reference:** col_validation_workplan.md § Phase 2  
**Date:** 2026-04-19  
**Status:** COMPLETE — Pipeline run confirmed  
**Dataset:** 11,099 rows × 44 columns

---

## 1. Scope

Phase 2 validates data against business domain rules: schema reference lookups for code columns, numeric range constraints, and categorical enum enforcement.

---

## 2. Functions Verified

| Function | File | Status |
|----------|------|--------|
| `_apply_schema_reference_validation` | `calculations/validation.py` | ✅ Validates against all 6 master schemas |
| `_get_schema_reference_allowed_codes` | `calculations/validation.py` | ✅ Multi-level lookup supported |
| `_get_ref_data` | `calculations/validation.py` | ✅ New architecture + legacy fallback |

---

## 3. Schema Reference Validation Results

| Column | Schema Reference | Non-null Rows | Status |
|--------|-----------------|---------------|--------|
| `Project_Code` | `project_code_schema` | 11,095 | Validated |
| `Facility_Code` | `facility_schema` | 11,030 | Validated |
| `Document_Type` | `document_type_schema` | 11,028 | Validated |
| `Discipline` | `discipline_schema` | 11,032 | Validated |
| `Department` | `department_schema` | 10,997 | Validated |
| `Approval_Code` | `approval_code_schema` | 11,099 | Validated |
| `Review_Status` | `approval_code_schema` | 11,099 | 20 values not in schema (known) |
| `Submitted_By` | `department_schema` | 10,891 | Validated |
| `Latest_Approval_Status` | `approval_code_schema` | 11,099 | 14 values not in schema (known) |

**Known schema failures (pre-existing, from pipeline history):**
- `Review_Status`: 20 values not in `approval_code_schema` — non-standard status strings in source data
- `Latest_Approval_Status`: 14 values not in schema — inherited from `Review_Status` mapping

---

## 4. Range Validation Results

| Column | Rule | Violations Below | Violations Above | Status |
|--------|------|-----------------|-----------------|--------|
| `Duration_of_Review` | 0 ≤ value ≤ 365 | 0 | **4** | ⚠️ 4 reviews > 365 days |
| `Delay_of_Resubmission` | 0 ≤ value ≤ 365 | **239** | **347** | ❌ 239 negative, 347 excessive |
| `Count_of_Submissions` | 1 ≤ value ≤ 100 | 0 | 0 | ✅ PASS |
| `Data_Health_Score` | 0 ≤ value ≤ 100 | 0 | 0 | ✅ PASS |

**Delay_of_Resubmission analysis:**
- 239 negative values: Plan date is in the future relative to the calculation date — indicates rows where resubmission has not yet occurred but plan date was set. These are legitimate data states, not calculation errors.
- 347 values > 365: Extreme delays in resubmission, likely legacy data with very old plan dates.

---

## 5. Categorical Enum Results

| Column | Allowed Values | Invalid Count | Status |
|--------|---------------|---------------|--------|
| `Submission_Closed` | YES, NO | 0 | ✅ PASS — {YES: 6,381, NO: 4,718} |
| `Resubmission_Required` | YES, NO, RESUBMITTED, PENDING | 0 | ✅ PASS (fixed from 816 'PEN' → 'PENDING') |
| `Resubmission_Overdue_Status` | Overdue, Resubmitted, NO | 0 | ✅ PASS |

**Bug fixed (Issue #28):** `Resubmission_Required` was outputting `'PEN'` instead of `'PENDING'` — 816 rows affected. Fixed in `conditional.py` line 147.

**Resubmission_Required distribution after fix:**
- YES: 8,568 (77.2%)
- NO: 1,715 (15.5%)
- PENDING: 816 (7.4%)
- RESUBMITTED: 0 (not triggered in current dataset)

---

## 6. Target Achievement

| Target | Result | Status |
|--------|--------|--------|
| 98% schema match rate | ~99.8% for most columns | ✅ PASS |
| Review_Status schema failures detected | 20 detected | ✅ PASS |
| Negative Delay_of_Resubmission detected | 239 detected | ✅ PASS |
| Categorical enum compliance | 0 invalid after fix | ✅ PASS |
| Duration_of_Review range | 4 violations > 365 | ⚠️ Known |

---

## 7. Bug Fixed This Phase

| Issue | File | Change | Impact |
|-------|------|--------|--------|
| **#28** `Resubmission_Required` value `'PEN'` → `'PENDING'` | `processor_engine/calculations/conditional.py` line 147 | Changed string literal | 816 rows now correctly categorised |
