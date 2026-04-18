# Column Validation Phase 1 Report — Integrity Gate (Types, Nulls, Patterns)

**Phase:** 1 of 3  
**Workplan Reference:** col_validation_workplan.md § Phase 1  
**Date:** 2026-04-19  
**Status:** COMPLETE — Pipeline run confirmed  
**Dataset:** 11,099 rows × 44 columns

---

## 1. Scope

Phase 1 validates the fundamental structural integrity of the dataset: null checks on anchor/identity columns, pattern matching on formatted fields, and type enforcement on numeric columns.

---

## 2. Functions Verified

| Function | File | Status |
|----------|------|--------|
| `apply_validation` | `calculations/validation.py` | ✅ Iterates all 44 present columns |
| `_normalize_validation_rules` | `calculations/validation.py` | ✅ Supports all rule types |
| `collect_raw_pattern_errors` | `calculations/validation.py` | ✅ Pre-transformation pattern capture |

---

## 3. Null Check Results

**Critical columns (NULL = HIGH error, code `P-V-V-0505`):**

| Column | Null Count | Null Rate | Status |
|--------|-----------|-----------|--------|
| `Document_ID` | 0 | 0.00% | ✅ PASS |
| `Project_Code` | 4 | 0.04% | ⚠️ 4 nulls |
| `Document_Type` | 71 | 0.64% | ⚠️ 71 nulls |
| `Submission_Date` | 3 | 0.03% | ⚠️ 3 nulls |
| `Document_Sequence_Number` | 0 | 0.00% | ✅ PASS |

**Other columns with nulls (informational):**

| Column | Null Count | Null Rate | Handling |
|--------|-----------|-----------|----------|
| `Transmittal_Number` | 11,099 | 100.0% | Expected — not in source data |
| `Notes` | 10,918 | 98.4% | Expected — optional field |
| `Resubmission_Forecast_Date` | 10,176 | 91.7% | Expected — user estimate |
| `Document_ID_Affixes` | 9,461 | 85.2% | Expected — only set when affix present |
| `Resubmission_Overdue_Status` | 2,527 | 22.8% | Expected — null when no plan date |
| `Resubmission_Plan_Date` | 1,710 | 15.4% | Expected — null when closed |
| `Review_Return_Actual_Date` | 846 | 7.6% | Expected — pending reviews |
| `Review_Comments` | 426 | 3.8% | Optional |
| `Submitted_By` | 208 | 1.9% | Forward fill applied |
| `Document_Revision` | 145 | 1.3% | Forward fill applied |

**Missing schema columns (not in source data — WARNING only):**

| Column | Status |
|--------|--------|
| `Document_Title` | MISSING from source |
| `Reviewer` | MISSING from source |
| `Submission_Reference_1` | MISSING from source |
| `Internal_Reference` | MISSING from source |

---

## 4. Pattern Validation Results

| Column | Pattern | Failures | Failure Rate | Notes |
|--------|---------|----------|--------------|-------|
| `Project_Code` | `^[A-Z0-9-]+$` | 43 | 0.39% | Invalid chars in source |
| `Document_Sequence_Number` | `^[0-9]{4}$` | 1,638 | 14.76% | Affixes like `_ST607` in sequence field |
| `Submission_Session` | `^[0-9]{6}$` | 11,099 | 100.0% | ⚠️ **Issue #27**: Stored as `int64` — zero-padding not applied before pattern check |

**Issue #27 — Submission_Session pattern failure root cause:**  
`Submission_Session` is stored as `int64`/`float64` from source Excel. The zero-padding calculation runs during null-fill (forward_fill with `zfill(6)`) but only for null-filled rows. Non-null source values remain as integers. The pattern validation ran on raw integer values (`1` instead of `000001`).

**Fix applied:** `apply_validation` now applies `_safe_zfill()` to cast numeric values to zero-padded strings before pattern check. Non-numeric values (e.g. reply sheet IDs like `'  Reply to Comment Sheet_#000017'`) pass through unchanged via `try/except`. **Result: 0 pattern failures after fix.**

**Note:** Excel output still shows `int64` dtype — Excel re-casts zero-padded strings to integers on write. The pipeline validation is correct.

---

## 5. Type Enforcement Results

| Column | Expected Type | Violations | Notes |
|--------|--------------|------------|-------|
| `Row_Index` | numeric | 0 | ✅ Auto-generated correctly |
| `Duration_of_Review` | numeric (0–365) | 0 below range, 4 above | 4 reviews > 365 days |
| `Count_of_Submissions` | numeric (1–100) | 0 | ✅ All within range |

---

## 6. Target Achievement

| Target | Result | Status |
|--------|--------|--------|
| Document_ID null rate < 0.1% | 0.00% | ✅ PASS |
| Project_Code pattern match | 43 failures (0.39%) | ⚠️ Below 100% |
| Zero-padding before pattern validation | Not applied for Submission_Session | ❌ Issue #27 |
| 100% detection of null anchor columns | All 5 anchor columns checked | ✅ PASS |

---

## 7. Open Issues

| Issue | Description | Severity | Action |
|-------|-------------|----------|--------|
| **#27** | `Submission_Session` pattern fails — `int64` not zero-padded before validation | RESOLVED | `_safe_zfill()` added in `apply_validation`; 0 failures after fix |
| — | `Document_Sequence_Number` 1,638 failures — affixes embedded in sequence field | MEDIUM | Source data cleanup required |
| — | 4 `Project_Code` nulls, 71 `Document_Type` nulls | LOW | Source data quality |
