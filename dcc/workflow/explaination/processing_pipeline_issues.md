# Processing Pipeline Issues & Discussion Notes

**Date:** April 8, 2026  
**Topic:** Null Handling vs Calculation Order Conflict

---

## 1. Current Processing Pipeline Order

```
1. Column Mapping → Initialize Missing → Apply Null Handling → Apply Calculations → Apply Validation
```

## 2. The Conflict: Null Handling vs Calculations

### Problem Description

Current order creates a conflict:

| Step | Action | Result |
|------|--------|--------|
| 1 | `apply_null_handling` | Fills nulls with defaults (e.g., "NA", forward fill) |
| 2 | `apply_calculations` | Sees values exist (not null), **skips calculation** |

### Example Problem Scenario

```yaml
# Schema config for Approval_Code:
null_handling:
  strategy: "default_value"
  default_value: "NA"  # ← Fills nulls first
is_calculated: true
calculation:
  type: "mapping"
  source_column: "Review_Status"  # ← Never runs because already filled!
```

**Result:** `Approval_Code` = "NA" (default) instead of calculated value from `Review_Status`

### Root Cause

The calculation handlers were modified to **only fill null values**:
- If column has existing data → Calculation is skipped
- Null handling fills data before calculations run
- Calculations see "not null" and skip

## 3. Proposed Solutions

### Option 1: Change Processing Order (Recommended)

**New Order:**
```
1. Column Mapping
2. Initialize Missing Columns (create with nulls)
3. Apply Calculations (fill nulls with calculated values)
4. Apply Null Handling (fill remaining nulls with defaults)
5. Apply Validation
```

**Pros:**
- Calculations get first priority
- Null handling acts as fallback
- No schema changes needed

**Cons:**
- Requires code change in `engine.py`
- Need to verify no other dependencies break

### Option 2: Schema-Level Fix

For `is_calculated: true` columns, set:
```yaml
null_handling:
  strategy: "leave_null"  # Don't touch, let calculation handle it
```

**Pros:**
- No code changes needed
- Explicit intent in schema

**Cons:**
- Requires updating many schema entries
- Easy to forget for new columns
- Mix of strategies becomes confusing

### Option 3: Modify Calculation to Override (Not Recommended)

Change calculations to **always overwrite** existing values:
```python
# Instead of:
if df[column_name].isna().any():
    df.loc[null_mask, column_name] = calculated_value

# Do:
df[column_name] = calculated_value  # Always overwrite
```

**Cons:**
- Loses ability to preserve input data
- Defeats purpose of `is_calculated` flag
- Could break existing workflows

## 4. Affected Columns (From Recent Test Run)

Based on pipeline output, these columns showed the "Preserving existing values" pattern:

| Column | Status |
|--------|--------|
| `Consolidated_Submission_Session_Subject` | Skipped (all values present) |
| `Submission_Closed` | Preserved 10,228 values |
| `Resubmission_Required` | Preserved 10,229 values |
| `Resubmission_Plan_Date` | Preserved 8,554 values |
| `Resubmission_Overdue_Status` | Preserved 8,331 values |
| `Delay_of_Resubmission` | Preserved 3,665 values |

## 5. Decision Needed

**Which solution should be implemented?**

- [ ] **Option 1:** Change processing order (calculations before null handling)
- [ ] **Option 2:** Update schema to use `leave_null` for calculated columns
- [ ] **Option 3:** Keep current behavior (calculations only fill nulls, null handling fills first)
- [ ] **Other:** Hybrid approach?

## 6. Additional Context

### Calculation Handlers Modified (April 8, 2026)

The following calculation files were updated to only fill null values:

| File | Functions |
|------|-----------|
| `calculations/mapping.py` | `apply_mapping_calculation` |
| `calculations/conditional.py` | `apply_current_row_calculation`, `apply_update_resubmission_required`, `apply_submission_closure_status`, `apply_calculate_overdue_status` |
| `calculations/aggregate.py` | `apply_aggregate_calculation`, `apply_latest_by_date_calculation`, `apply_latest_non_pending_status` |
| `calculations/composite.py` | `apply_composite_calculation`, `apply_row_index`, `apply_delay_of_resubmission`, `apply_copy_calculation` |
| `calculations/date.py` | `calculate_working_days`, `calculate_date_difference`, `apply_resubmission_plan_date`, `apply_conditional_date_calculation`, `apply_conditional_business_day_calculation` |

### Schema Configuration Pattern

Currently, many columns have both:
```json
{
  "is_calculated": true,
  "null_handling": {
    "strategy": "default_value",
    "default_value": "NA"
  }
}
```

This creates the conflict described above.

---

## 7. Next Steps (Pending Discussion)

1. Decide which solution to implement
2. If Option 1: Modify `engine.py` processing order
3. If Option 2: Update schema JSON for affected columns
4. Test with actual data to verify behavior
5. Update documentation

---

**Status:** Awaiting decision  
**Priority:** High - affects data accuracy
