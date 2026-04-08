# Root Cause Analysis: Review_Return_Plan_Date Not Mapped

## Issue
The final Excel output still shows the original column header `"Date S.O. to Response\n(20 Working Days/\n 14 Working Days)"` instead of the schema column name `"Review_Return_Plan_Date"`.

## Root Cause

**The column was being skipped during detection due to `is_calculated: True`**

In `/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/engine/mappers/detection.py`, line 65:

```python
for column_name, column_def in columns.items():
    if not isinstance(column_def, dict) or column_def.get('is_calculated', False):
        continue  # ← SKIPS calculated columns!
```

**The flawed logic**: The code assumed that calculated columns don't need to be detected/mapped from the input data. However:

1. The Excel file **DOES contain** this column (with the original header)
2. Because it was skipped, the column was **never detected**
3. Because it wasn't detected, it was **never renamed** to `Review_Return_Plan_Date`
4. The final output retained the original Excel header

## Why This is Wrong

**Calculated columns can exist in the input data!** The `is_calculated` flag means:
- The column's **values** will be computed/overwritten by the processor
- It does NOT mean the column won't exist in the input data

The column still needs to be:
1. ✅ **Detected** (matched from Excel header to schema name)
2. ✅ **Renamed** (Excel header → schema column name)
3. ✅ **Calculated** (values computed/overwritten if needed)

## Fix Applied

**File**: `/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/engine/mappers/detection.py`

**Change**: Removed the `is_calculated` check from the detection loop (line 65):

```python
# BEFORE (WRONG):
for column_name, column_def in columns.items():
    if not isinstance(column_def, dict) or column_def.get('is_calculated', False):
        continue

# AFTER (CORRECT):
for column_name, column_def in columns.items():
    if not isinstance(column_def, dict):
        continue
```

**The `is_calculated` check remains in the "missing required columns" check** (line 88-91), which is correct - we don't warn about missing calculated columns because they'll be computed.

## Test Results

### Before Fix
- Detected: 24 columns
- Unmatched: 3 headers
- `Review_Return_Plan_Date`: ❌ NOT DETECTED
- Final output: Original header `"Date S.O. to Response\n(20 Working Days/\n 14 Working Days)"`

### After Fix
- Detected: 27 columns
- Unmatched: 0 headers  
- `Review_Return_Plan_Date`: ✅ DETECTED (score: 1.000)
- Final output: Schema name `"Review_Return_Plan_Date"` ✅

## Newline (`\n`) Handling

**The `\n` characters in aliases are NOT the issue.** The `normalize_string()` function correctly handles all whitespace (including `\n`, `\r\n`, etc.) by collapsing them into single spaces:

```python
def normalize_string(text: str) -> str:
    normalized = text.lower().strip()
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized)  # ← Handles \n correctly
    return normalized.strip()
```

Both the Excel header and schema alias normalize to the same string:
- Excel: `"Date S.O. to Response\n(20 Working Days/\n 14 Working Days)"` → `"date so to response 20 working days 14 working days"`
- Schema: `"Date S.O. to Response (20 Working Days/ 14 Working Days)"` → `"date so to response 20 working days 14 working days"`
- Match score: **1.000** ✅

## Files Modified

1. `/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/engine/mappers/detection.py`
   - Line 65-68: Removed `is_calculated` check from column detection loop

## Impact

This fix ensures **ALL schema columns** (including calculated ones) are properly detected and renamed from input data headers. The `is_calculated` flag only affects:
- Whether the column is **computed** by the processor engine
- Whether missing columns trigger a **warning** (calculated columns don't)

It does NOT affect:
- Whether the column is **detected/matched** from input headers
- Whether the column is **renamed** to the schema name
