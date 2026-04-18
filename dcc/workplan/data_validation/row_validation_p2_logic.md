# Row Validation Phase 2 Report — Temporal & Logical Sequence

**Phase:** 2 of 3  
**Workplan Reference:** row_validation_workplan.md § Phase 2  
**Date:** 2026-04-19  
**Status:** COMPLETE — Implementation delivered, pipeline run pending

---

## 1. Scope

Phase 2 ensures the document workflow follows a logical chronological and status-based progression. It validates date ordering, closure rules, resubmission inter-dependencies, and overdue status accuracy.

---

## 2. Functions Implemented

| Function | File | Description |
|----------|------|-------------|
| `_validate_date_sequence` | `row_validator.py` | Submission_Date ≤ Review_Return_Actual_Date |
| `_validate_status_closure` | `row_validator.py` | Closed=YES → Resubmission_Plan_Date must be NULL |
| `_validate_resubmission_logic` | `row_validator.py` | REJ status → Resubmission_Required=YES/RESUBMITTED |
| `_validate_overdue_status` | `row_validator.py` | today > Plan_Date → Resubmission_Overdue_Status=Overdue |

---

## 3. Validation Rules Applied

### 3.1 Date Sequence — `L3-L-P-0301` (HIGH)

**Rule:** `Submission_Date <= Review_Return_Actual_Date`

**Logic:**
1. Filter rows where both dates are non-null.
2. Parse each date via `_parse_date()` (supports YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, YYYY/MM/DD).
3. If `Review_Return_Actual_Date < Submission_Date` → emit `L3-L-P-0301`.
4. Context includes `days_inverted` for diagnostic reporting.

**Pipeline target:** Zero logical contradictions in date fields.

---

### 3.2 Status Closure — `CLOSED_WITH_PLAN_DATE` (HIGH)

**Rule:** If `Submission_Closed = YES` then `Resubmission_Plan_Date` MUST be NULL.

**Logic:**
1. Build mask: `Submission_Closed.str.upper() == 'YES'`.
2. Build mask: `Resubmission_Plan_Date.notna() AND not empty`.
3. Intersection → emit `CLOSED_WITH_PLAN_DATE` per row.

**Pipeline context:** 1,707 rows had `Resubmission_Plan_Date` set to null when closed — this check verifies the calculation was applied correctly.

---

### 3.3 Resubmission Logic — `RESUBMISSION_MISMATCH` (MEDIUM)

**Rule:** `Review_Status` containing `REJ` must have `Resubmission_Required` in `{YES, RESUBMITTED}`.

**Logic:**
1. Build mask: `Review_Status.str.upper().str.contains('REJ')`.
2. Build mask: `Resubmission_Required.str.upper()` NOT in `{YES, RESUBMITTED}`.
3. Intersection → emit `RESUBMISSION_MISMATCH` per row.

**Pipeline context:** Targets rows where rejection was recorded but resubmission flag was not updated.

---

### 3.4 Overdue Status — `OVERDUE_MISMATCH` (MEDIUM)

**Rule:** If `today > Resubmission_Plan_Date` AND `Submission_Closed != YES` → `Resubmission_Overdue_Status` must equal `Overdue`.

**Logic:**
1. Filter rows with non-null `Resubmission_Plan_Date` and not closed.
2. Parse plan date; compare against `datetime.now()`.
3. If past due and `Resubmission_Overdue_Status != 'Overdue'` (case-insensitive) → emit `OVERDUE_MISMATCH`.
4. Context includes `days_overdue` for triage.

**Pipeline target:** Validation of 241 `Overdue` status flags against current date.

---

## 4. Target Achievement

| Metric | Target (Workplan) | Implementation |
|--------|-------------------|----------------|
| Zero date inversions | 100% detection | Row-by-row date parse + compare |
| Closure rule | NULL plan date when closed | Mask intersection check |
| REJ → resubmission | 100% inter-dependency | String contains 'REJ' + allowed values check |
| 241 Overdue flags | Validated against today | `datetime.now()` comparison per row |
| 239 negative Delay_of_Resubmission | Flagged as errors | Covered by OVERDUE_MISMATCH + CLOSED_WITH_PLAN_DATE |

---

## 5. Error Output

| Error Code | Severity | Column | Context Keys |
|------------|----------|--------|--------------|
| `L3-L-P-0301` | HIGH | `Review_Return_Actual_Date` | `submission_date`, `return_date`, `days_inverted` |
| `CLOSED_WITH_PLAN_DATE` | HIGH | `Resubmission_Plan_Date` | `plan_date` |
| `RESUBMISSION_MISMATCH` | MEDIUM | `Resubmission_Required` | `review_status`, `resubmission_required` |
| `OVERDUE_MISMATCH` | MEDIUM | `Resubmission_Overdue_Status` | `plan_date`, `overdue_status`, `days_overdue` |

**Health score deductions:**
- `CLOSED_WITH_PLAN_DATE`: −10 pts per row
- `OVERDUE_MISMATCH`: −5 pts per row

---

## 6. Potential Issues Addressed

| Issue | Handling |
|-------|----------|
| "NA" or placeholder dates in temporal calculations | `_parse_date()` returns `None` for "NA", "NaT", empty strings — row skipped |
| Timezone discrepancies | All comparisons use naive `datetime` objects; timezone normalization deferred |
| Case variations in status values (e.g. "yes", "YES") | `.str.upper()` applied before all comparisons |
| Null `Resubmission_Overdue_Status` | `str(value).strip()` used; null → empty string → mismatch detected |

---

## 7. Integration

- **Trigger:** `RowValidator.detect()` → Phase 2 methods called in sequence after Phase 1.
- **Class:** `RowValidator` in `processor_engine/error_handling/detectors/row_validator.py`
- **Helper:** `_parse_date()` module-level function (supports 4 date formats)
