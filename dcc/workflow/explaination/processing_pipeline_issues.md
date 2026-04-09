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

---

## 5.1 Continued Discussion (April 9, 2026)

### Key Question: What is the intended behavior?

To decide, we need to clarify the **intent** of each processing stage:

**Scenario A: Input data has column "SO Review Status"**
- User wants to preserve original value → Calculations should NOT override
- Null handling should skip this column (leave_null)

**Scenario B: Input data has column but some rows are null**
- User wants original where present, calculated where null
- Calculations fill nulls, null handling fills remaining nulls with defaults

**Scenario C: Input data missing column entirely**
- Column created during processing
- Calculations should generate values, null handling provides fallback

### Analysis of Each Option:

#### Option 1: Change Order (Calculations First)

```
Before: Mapping → Null Handling → Calculations → Validation
After:  Mapping → Calculations → Null Handling → Validation
```

**Impact:**
- Calculations run on raw mapped data
- Null values get calculated first
- Remaining nulls get defaults from null_handling
- **Risk:** Columns that previously got "NA" default may now stay null if calculation fails

**Affected files to modify:**
- `processor_engine/engine/core/engine.py` - swap `apply_null_handling` and `apply_calculations` calls

#### Option 2: Schema Update (leave_null for calculated columns)

**Files to modify:**
- `config/schemas/dcc_register_enhanced.json` - add `leave_null` strategy to all `is_calculated: true` columns

**How many columns affected?**
From schema analysis: ~20+ columns have `is_calculated: true`

**Effort:** Medium (one-time schema update)

#### Option 3: Hybrid - Skip null_handling for calculated columns in code

Instead of changing schema or order, modify `apply_null_handling` in `engine.py` to automatically skip columns where `is_calculated: true`.

```python
# In engine.py apply_null_handling method
for column_name, column_def in self.columns.items():
    if column_def.get('is_calculated'):
        logger.info(f"Skipping null handling for {column_name} (calculated column)")
        continue
    # ... rest of null handling logic
```

**Pros:**
- No schema changes
- No order changes
- Single code change in one place
- Explicit logic: calculated columns are handled by calculations, not null handling

**Cons:**
- Implicit behavior (not visible in schema)
- May surprise users reading schema

---

## 5.2 Recommendation

**Recommended: Option 4 (Hybrid - Code-level skip)**

Modify `apply_null_handling` to skip any column marked `is_calculated: true`.

**Rationale:**
1. Keeps schema clean (no need to add `leave_null` everywhere)
2. No processing order changes (less risk)
3. Logical consistency: if a column is calculated, let the calculation handler manage it
4. If user wants defaults for calculated columns, they set it in calculation config

**Implementation:**
```python
# processor_engine/engine/core/engine.py
# In apply_null_handling method, add at start of column loop:

if column_def.get('is_calculated'):
    self._print_processing_step("Null-Handling", column_name, "Skipping - calculated column")
    continue
```

**Which option do you prefer?**

- [ ] **Option 1:** Change processing order
- [ ] **Option 2:** Schema update with `leave_null`
- [x] **Option 4:** Code-level skip for calculated columns (RECOMMENDED)
- [ ] **Option 3:** Keep current behavior

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

## 8. April 9, 2026 - Implementation Complete

### 8.1 Final Rules Established

Based on detailed discussion, the following 13 rules were established in `column_priority_reference.md`:

| Rule # | Rule | Implementation |
|--------|------|----------------|
| 1 | Sort column not allowed before forward fill | Enforced in processing |
| 2 | Forward fill shall not overwrite existing values | All forward fill handlers check for existing values |
| 3 | Only Row_Index is unique | Schema `unique_fields` = `["Row_Index"]` |
| 4 | Define data column priority | P1 (Meta), P2 (Transactional), P3 (Calculated) |
| 5 | Processing Sequence: Impute P1 → Validate P2 → Calculate P3 | Implemented in `apply_phased_processing()` |
| 6 | Forward fill boundary conditions | Level 1: [Session, Revision], Level 2: [Session] |
| 7 | Pipeline handles multiple sessions/revisions | Session-based grouping implemented |
| 8 | Submission_Closed preserves user input | 2-step: forward fill if user value, else calculate |
| 9 | Resubmission_Forecast_Date is user estimate | Not calculated, forward fill within boundary allowed |
| 10 | Document_ID: calculate → null_handling | Phase 2.5 processing |
| 11 | is_calculated=true: calculation FIRST, null_handling LAST | Implemented in `_apply_phase_calculated()` |
| 12 | Manual input allowed → forward fill with boundary | P2 columns with Manual Input = YES |
| 13 | Respect column sequence in schema | Process in `column_sequence` order |

### 8.2 Schema Changes Applied

**File:** `config/schemas/dcc_register_enhanced.json`

```json
// Added to all 46 columns:
"processing_phase": "P1" | "P2" | "P2.5" | "P3"
```

**Distribution:**
- P1 (Meta Data): 11 columns
- P2 (Transactional): 11 columns  
- P2.5 (Anomaly): 3 columns (Document_ID, Latest_Revision, Review_Status_Code)
- P3 (Calculated): 21 columns

### 8.3 Code Changes Applied

**File:** `processor_engine/core/engine.py`

#### New Methods Added:
1. `apply_phased_processing(df)` - Main orchestrator (P1→P2→P2.5→P3)
2. `_apply_phase_null_handling(df, column_names)` - P1 processing
3. `_apply_phase_transactional(df, column_names)` - P2 processing with forward fill
4. `_apply_phase_calculated(df, column_names)` - P2.5/P3 processing (calc first, null last)

#### Modified Methods:
- `process_data()` - Now calls `apply_phased_processing()` instead of separate null/calc calls
- `apply_null_handling()` - Marked as deprecated for direct use
- `apply_calculations()` - Marked as deprecated for direct use

#### Key Implementation:
```python
# Rule 11: Calculation FIRST, null handling as LAST DEFENSE
def _apply_phase_calculated(df, column_names):
    # Step 1: Apply calculations FIRST
    for col in column_names:
        apply_calculation(col)
    
    # Step 2: Apply null handling only to REMAINING nulls
    for col in column_names:
        if df[col].isna().any():
            apply_null_handling(col)  # Last defense
```

### 8.4 Documentation Updated

**Files Modified:**
1. `workflow/explaination/column_priority_reference.md` - Complete column priority documentation
2. `workflow/processor_engine/readme.md` - Updated with phased processing flowchart and rules
3. `workflow/README.md` - Added link to column priority reference

### 8.5 Test Results

**Pipeline Test:**
```
Raw Shape: (11099, 26)
Mapped Shape: (11099, 26)
Processed Shape: (11099, 42)
Match Rate: 100.0%
Status: Ready: YES
```

**Phase Processing Log:**
```
[Phase 1] Meta Data: Processing 11 columns
[Phase 2] Transactional: Processing 11 columns
[P2-ForwardFill] Resubmission_Forecast_Date: Applying forward_fill
[Phase 2.5] Anomaly: Processing 3 columns
[Calculation] Document_ID: Applying composite/build_document_id
[Calculation] Review_Status_Code: Applying mapping/status_to_code
[Calculation] Latest_Revision: Applying aggregate/latest_by_date
[Phase 3] Calculated: Processing 21 columns
[Calculation] Submission_Closed: Preserving 10228 existing values
[Calculation] Resubmission_Required: Preserving 10229 existing values
```

### 8.6 Issues Resolved

| Issue | Status | Resolution |
|-------|--------|------------|
| Null handling before calculations | ✅ RESOLVED | Calculations run FIRST, null handling as LAST DEFENSE |
| Calculated columns overwriting data | ✅ RESOLVED | Calculations only fill nulls, preserve existing values |
| Document_ID processing order | ✅ RESOLVED | Phase 2.5 (after P2, before P3) |
| Forward fill boundaries | ✅ RESOLVED | Session/Revision boundaries for P1 + P2 Manual Input |
| Processing sequence | ✅ RESOLVED | Schema `column_sequence` respected |

### 8.7 Files Changed Summary

**Schema:**
- `config/schemas/dcc_register_enhanced.json` - Added `processing_phase` to 46 columns

**Code:**
- `processor_engine/core/engine.py` - Added phased processing methods

**Documentation:**
- `workflow/explaination/column_priority_reference.md` - Complete rules documentation
- `workflow/processor_engine/readme.md` - Updated workflow and methods
- `workflow/README.md` - Added reference link

---

## 9. Quick Reference Guide for Future Development

### 9.1 Key Architectural Decisions

| Decision | Rationale | Impact |
|----------|-----------|--------|
| **Phased Processing (P1→P2→P2.5→P3)** | Resolves conflict between null handling and calculations | Cleaner separation of concerns, predictable processing order |
| **Calculation FIRST, Null handling LAST** | Rule 11: Calculated columns need priority | Existing data preserved, calculations fill gaps |
| **Forward Fill Boundaries** | Rule 12: Prevent data bleeding across sessions | Session-based grouping with warnings |
| **P2.5 Anomaly Phase** | Rule 10: Document_ID, Review_Status_Code need special handling | Calculated but processed before other P3 columns |
| **Column Sequence Respect** | Rule 13: Schema order matters | Deterministic, debuggable processing |

### 9.2 When Adding New Columns

**Checklist:**
1. [ ] Determine processing phase (P1/P2/P2.5/P3)
2. [ ] Define `is_calculated` flag
3. [ ] Define `null_handling` strategy
4. [ ] Add to `column_sequence` in schema
5. [ ] Add `processing_phase` field
6. [ ] Document in `column_priority_reference.md`
7. [ ] Update `column_update_logic.md`
8. [ ] Test with actual data

**Phase Decision Tree:**
```
Is it Meta Data (Project, Facility, Session info)?
  → YES → P1
  → NO → Is it Transactional (Doc Revision, Reviewer, Status)?
    → YES → P2
    → NO → Is it Anomaly (Document_ID, Review_Status_Code, Latest_Revision)?
      → YES → P2.5
      → NO → Is it Calculated?
        → YES → P3
        → NO → Review classification
```

### 9.3 Related Documents

| Document | Purpose | Location |
|----------|---------|----------|
| **Column Priority Reference** | Complete 13 rules with detailed explanations | `workflow/explaination/column_priority_reference.md` |
| **Column Update Logic** | 46-column processing logic table | `workflow/explaination/column_update_logic.md` |
| **Error Handling Framework** | 24 error codes for validation | `workflow/explaination/error_handling.md` |
| **Processor Engine README** | Engine architecture and methods | `workflow/processor_engine/readme.md` |
| **Main Workflow README** | Pipeline overview | `workflow/README.md` |
| **Schema File** | Column definitions and phases | `config/schemas/dcc_register_enhanced.json` |
| **Engine Implementation** | Core processing logic | `workflow/processor_engine/core/engine.py` |

### 9.4 Common Patterns

**Adding a P3 Calculated Column:**
```json
{
  "column_name": "My_New_Column",
  "is_calculated": true,
  "processing_phase": "P3",
  "calculation": {
    "type": "conditional",
    "method": "my_calculation"
  },
  "null_handling": {
    "strategy": "default_value",
    "default_value": "NA"
  }
}
```
Note: Calculation runs FIRST, null handling only fills remaining nulls (Rule 11).

**Adding a P2 Transactional Column with Forward Fill:**
```json
{
  "column_name": "My_Input_Column",
  "is_calculated": false,
  "processing_phase": "P2",
  "null_handling": {
    "strategy": "forward_fill",
    "group_by": ["Submission_Session"],
    "fill_value": "NA"
  }
}
```
Note: Forward fill respects boundaries (Rule 12).

### 9.5 Testing Checklist

After any schema or engine change:
1. [ ] Run `python dcc_engine_pipeline.py --nrows 100` for quick test
2. [ ] Verify log shows P1→P2→P2.5→P3 phases
3. [ ] Check `processing_summary.txt` for errors
4. [ ] Run full dataset test (11,099 rows)
5. [ ] Verify `validation_errors` column has no unexpected codes
6. [ ] Check calculated columns preserve existing data
7. [ ] Verify forward fill boundaries work correctly

### 9.6 Debugging Tips

**Issue: Calculated column not updating**
- Check: Is it P2.5 or P3? Look for `processing_phase`
- Check: Does calculation handler only fill nulls?
- Check: Are there existing values preventing update?

**Issue: Forward fill crossing sessions**
- Check: `group_by` includes `Submission_Session`
- Check: `na_fallback` is set appropriately
- Check: Boundary rules are being applied

**Issue: Wrong processing order**
- Check: `column_sequence` in schema
- Check: `processing_phase` assignments
- Check: `resolve_calculation_order()` dependency graph

---

## 10. Changelog Summary (April 9, 2026)

### Schema Changes
- Added `processing_phase` to all 46 columns (P1=11, P2=11, P2.5=3, P3=21)
- Updated `unique_fields` to `["Row_Index"]` per Rule 3
- Verified `column_sequence` matches processing order

### Engine Changes  
- Implemented `apply_phased_processing()` (P1→P2→P2.5→P3)
- Added `_apply_phase_null_handling()` for P1
- Added `_apply_phase_transactional()` for P2
- Added `_apply_phase_calculated()` for P2.5/P3
- Modified `process_data()` to use phased processing
- Deprecated direct use of `apply_null_handling()` and `apply_calculations()`

### Documentation Changes
- Created `column_priority_reference.md` with 13 rules
- Updated `column_update_logic.md` with phases
- Updated `processor_engine/readme.md` with new workflow
- Created `error_handling.md` with 24 error codes
- Updated `README.md` with reference links

### Test Results
- Pipeline: 11,099 rows processed successfully
- Match Rate: 100%
- Status: Ready: YES
- All 5 core issues resolved

---

**Status:** ✅ IMPLEMENTATION COMPLETE - April 9, 2026  
**Priority:** High - All issues resolved, pipeline tested successfully  
**Reference Version:** v1.0 - Comprehensive development guide
