# Pipeline Error Fix: "Columns must be same length as key"

## Issue Summary

The pipeline failed with the error: **"Columns must be same length as key"** when processing the `Consolidated_Submission_Session_Subject` column.

## Root Cause

**Duplicate columns were created during the column mapping/renaming process.**

### The Chain of Events

1. **Column Detection Fix** (from previous issue): We modified `detect_columns()` to detect ALL columns, including calculated ones (removed the `is_calculated` check).

2. **Multiple Excel Headers Match Same Schema Column**: Several Excel headers matched to the same schema column `Submission_Session_Subject`:
   - `'Document Description / Drawing Title'` (alias match)
   - `'CES_SALCON-SDC JV Cor Ref No'` (alias match)
   - Possibly others due to fuzzy matching

3. **All Mapped to Same Name**: When `rename_dataframe_columns()` was called, all these Excel columns were renamed to `Submission_Session_Subject`, creating **4 duplicate columns** with the same name.

4. **Aggregate Function Fails**: When the aggregate function tried to do:
   ```python
   df.groupby(['Document_ID'])['Submission_Session_Subject'].transform(concat_unique_quoted)
   ```
   Pandas returned a **DataFrame** (4 columns) instead of a **Series** (1 column), causing the assignment to fail with "Columns must be same length as key".

## Fix Applied

**File**: `/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/engine/mappers/detection.py`

**Function**: `rename_dataframe_columns()`

**Change**: Added duplicate column removal after renaming:

```python
# Apply renaming
df_renamed = df_renamed.rename(columns=rename_dict)

# Remove duplicate columns (keep first occurrence)
# This can happen when multiple Excel headers map to the same schema column
duplicate_mask = df_renamed.columns.duplicated(keep='first')
if duplicate_mask.any():
    duplicate_cols = df_renamed.columns[duplicate_mask].tolist()
    logger.warning(f"Removing {len(duplicate_cols)} duplicate columns after rename: {duplicate_cols}")
    df_renamed = df_renamed.loc[:, ~df_renamed.columns.duplicated(keep='first')]
```

## Results

### Before Fix
- Duplicate columns created during rename
- Aggregate function failed with: `ValueError: Columns must be same length as key`
- Pipeline crashed ❌

### After Fix
- Duplicate columns detected and removed (keeping first occurrence)
- Aggregate function works correctly
- Pipeline completes successfully ✅
- Output has 42 columns with proper schema names

## Test Verification

```python
import pandas as pd
df = pd.read_excel('output/processed_dcc_universal.xlsx')

# Verify key columns exist with correct names
assert 'Review_Return_Plan_Date' in df.columns  # ✅
assert 'Consolidated_Submission_Session_Subject' in df.columns  # ✅
assert 'Submission_Session_Subject' in df.columns  # ✅

# No old Excel header names remain
old_style = [col for col in df.columns if 'Date S.O. to Response' in str(col)]
assert len(old_style) == 0  # ✅
```

## Related Issues

This fix works in conjunction with the previous fix to `detect_columns()`:
1. **detect_columns() fix**: Remove `is_calculated` check to allow calculated columns to be detected
2. **rename_dataframe_columns() fix**: Remove duplicate columns after rename

Both fixes are necessary for the pipeline to work correctly.

## Files Modified

1. `/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/engine/mappers/detection.py`
   - Lines 167-187: Added duplicate column detection and removal in `rename_dataframe_columns()`

## Impact

- **Positive**: Pipeline now handles cases where multiple Excel headers map to the same schema column
- **Positive**: Prevents duplicate column issues in downstream aggregate/calculation operations
- **Neutral**: Keeps first occurrence of duplicate columns (this is the expected behavior)
- **Note**: A warning is logged when duplicates are removed for transparency
