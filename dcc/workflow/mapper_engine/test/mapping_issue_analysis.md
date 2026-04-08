# Column Mapping Issue: Review_Return_Plan_Date

## Issue Summary
Column "review return_plan_date" was not being properly mapped per aliases in `dcc_register_enhanced.json`.

## Root Cause Analysis

### ❌ INCORRECT: Newline (`\n`) Handling
**The `\n` characters in aliases are NOT causing the issue.**

The `normalize_string()` function in `/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/engine/matchers/fuzzy.py` correctly handles newline characters:

```python
def normalize_string(text: str) -> str:
    normalized = text.lower().strip()
    # Remove special characters
    normalized = re.sub(r'[^\w\s]', '', normalized)
    # Collapse ALL whitespace (including \n, \r\n, \t) into single space
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized.strip()
```

**Test Results:**
- `"Date S.O. to Response\n(20 Working Days/\n 14 Working Days)"` → normalizes to → `"date so to response 20 working days 14 working days"`
- `"Date S.O. to Response (20 Working Days/ 14 Working Days)"` → normalizes to → `"date so to response 20 working days 14 working days"`
- Both match with **score 1.000** ✅

### ✅ CORRECT: Missing Aliases
**The actual issue**: The schema aliases for `Review_Return_Plan_Date` did not include common/simplified variations like:
- "review return_plan_date"
- "Review Return Plan Date"
- "Return Plan Date"

The schema only had:
- "Date S.O. to Response (20 Working Days/ 14 Working Days)" (with/without newlines)
- "Planned Response Date"
- "Target Response Date"

## Fix Applied

Updated `/workspaces/Engineering-and-Design/dcc/config/schemas/dcc_register_enhanced.json` to include additional aliases:

**Added:**
1. "Review Return Plan Date"
2. "Review Return_Plan Date"
3. "Review return_plan_date"
4. "Return Plan Date"
5. "Planned Return Date"
6. "Expected Return Date"

**Total aliases:** 6 → 12

## Verification

All test cases now pass:

| Header | Normalized | Matched Alias | Score |
|--------|-----------|---------------|-------|
| `Date S.O. to Response\n(20 Working Days/\n 14 Working Days)` | `date so to response 20 working days 14 working days` | Date S.O. to Response (20 Working Days/ 14 Working Days) | 1.000 ✅ |
| `review return_plan_date` | `review return_plan_date` | Review return_plan_date | 1.000 ✅ |
| `Return Plan Date` | `return plan date` | Return Plan Date | 1.000 ✅ |
| `Review Return Plan Date` | `review return plan date` | Review Return Plan Date | 1.000 ✅ |

## Files Modified

1. `/workspaces/Engineering-and-Design/dcc/config/schemas/dcc_register_enhanced.json`
   - Added 6 new aliases to `Review_Return_Plan_Date` column definition

## Files Created (for testing)

1. `/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/test/test_newline_handling.py`
2. `/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/test/test_newline_simple.py`
3. `/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/test/test_alias_detection.py`
4. `/workspaces/Engineering-and-Design/dcc/workflow/mapper_engine/test/test_with_schema.py`

## Conclusion

**Multi-line text with `\n` in aliases does NOT cause mapping issues** due to proper whitespace normalization in the `normalize_string()` function.

The mapping failure was due to **missing aliases** in the schema file, not newline handling.
