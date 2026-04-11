# Document_ID Pattern Validation Test Report

**Date:** April 11, 2026 (Rerun: 21:05)
**Test Case:** Validation of dynamic `Document_ID` pattern derived from source columns.
**Input File:** `Submittal and RFI Tracker Lists.xlsx` (Full Dataset: 11,099 rows)

---

## 1. Test Executive Summary

The latest run on the full dataset confirms that the **Row Alignment Discrepancy** has been **RESOLVED**. Row data is now correctly preserved through the phased processing engine. Structured error codes (`[P-V-V-XXXX]`) are now visible in the `Validation_Errors` column.

- **Total Rows Processed:** 11,099
- **Validation Pass Rate for Document_ID Pattern:** ~84% (1,750 invalid patterns identified)
- **Primary Success:** Verified that data from Row 8 no longer leaks into Row 7. Every row is correctly mapped to its own project and sequence identifiers.

---

## 2. Validation Error Distribution (Full Dataset)

| Error Category | Occurrences | Impact |
| :--- | :--- | :--- |
| **Document_ID Dynamic Pattern Mismatch** | 1,750 | High - Indicates significant volume of non-standard ID formats. |
| **Project_Code Schema Violation** | 11,099 | Major - The identifier `131242` is used throughout but missing from `project_schema`. |
| **Sequence Number Pattern Mismatch** | 1,638 | Medium - Indicates "NA" or non-numeric suffixes in sequence column. |

---

## 3. Detailed Finding: Row-Level Alignment Analysis

| Row Index | Document_ID | Status / Error Signature |
| :--- | :--- | :--- |
| 7 | `#000002.0_ Reply_...-9999` | **RESOLVED**: Now correctly reflects "Reply" data. `[P-V-V-0501]` Pattern Mismatch. |
| 8 | `131242-WST00-PP-IM-0001` | **CORRECT**: ID belongs to this row. `[P-V-V-0506]` Project Code missing from schema. |
| 15 | `131242-WST00-PP-HS-0001` | **CORRECT**: Data alignment confirmed. `[P-V-V-0506]` Schema violations present. |
| 48 | `...-Reply to Comment Sheet...`| **CORRECT**: Row preserves its own specific "Reply" suffix data. |

---

## 4. Root Cause Analysis & Resolution (Issue #5)

The previously reported "takeover" of Row 7 by Row 8 was caused by two specific bugs in `aggregate.py`:
1. **Positional Overwrite**: `apply_latest_non_pending_status` was using `.values` assignment on a reset index, which "slid" results to the top of the DataFrame.
2. **Index Discarding**: `apply_latest_by_date_calculation` was losing original indices during `pd.merge` operations.

**Fix Applied:** Restored index-aware mapping and ensured that all merges preserve the original row index before assignment.

---

## 5. Next Steps and Recommendations

1. **Update Project Schema**: Add code `131242` to `project_schema.json` to resolve the 11k+ validation warnings.
2. **Refine Sequence Strategy**: Many rows have sequence numbers that do not match `[0-9]{4}`. Check if `NA` should be permitted.
3. **Aggregate Report**: Now that Row-Index 7 is fixed, proceed to aggregate these findings into the `processing_summary.txt`.

---
**Status:** ✅ TEST COMPLETE | **Result:** VERIFIED (Row Alignment Fixed)
