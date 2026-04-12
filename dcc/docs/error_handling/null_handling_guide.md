# Null Handling Error Detection Documentation

## Overview

The Null Handling Error Detection module provides comprehensive monitoring and error detection for forward fill operations within the document processing pipeline. This module ensures data integrity by detecting problematic fill patterns such as excessive row jumps, session boundary crossings, and excessive null fills.

**Module Location:** `processor_engine.error_handling.detectors.fill`
**Related Files:**
- `calculations/null_handling.py` - Records fill operations
- `detectors/fill.py` - Analyzes fill history and generates errors
- `core/engine.py` - Integrates fill tracking into pipeline
- `detectors/business.py` - Orchestrates detector registration

---

## Error Code Reference (F4xx Series)

### F4-C-F-0401: Forward Fill Row Jump Limit Exceeded

| Attribute | Value |
|-----------|-------|
| **Error Code** | F4-C-F-0401 |
| **Severity** | HIGH |
| **Layer** | L3 (Business Logic) |
| **Description** | Forward fill operation spanned more rows than the configured limit |

**Detection Criteria:**
- Triggered when `row_jump > jump_limit` (default: 20 rows)
- Row jump is calculated as the difference between consecutive filled row indices

**Error Context Fields:**
```json
{
  "fill_strategy": "forward_fill",
  "column": "Reviewer",
  "group_by_columns": ["Project_Code", "Document_ID"],
  "from_row": {"Document_ID": "PRJ-FAC-DWG-ARC-0001", "row_index": 10},
  "to_row": {"Document_ID": "PRJ-FAC-DWG-ARC-0001", "row_index": 35},
  "row_jump": 25,
  "fill_percentage": 2.3,
  "limit": 20,
  "filled_value": "John Smith",
  "source_session": "2024001",
  "target_session": "2024002",
  "timestamp": "2024-01-20T14:30:00",
  "suggested_action": "Consider using multi-level fill or manual data entry"
}
```

**Remediation Strategies:**
1. **BREAK_LARGE_GROUPS**: Split large document groups into smaller batches
2. **MANUAL_ENTRY**: Require manual data entry for gaps exceeding limit
3. **EXPAND_GROUPS**: Add additional grouping columns to reduce fill distance

---

### F4-C-F-0402: Session Boundary Crossed During Fill

| Attribute | Value |
|-----------|-------|
| **Error Code** | F4-C-F-0402 |
| **Severity** | HIGH |
| **Layer** | L3 (Business Logic) |
| **Description** | Forward fill operation crossed submission session boundaries |

**Detection Criteria:**
- Triggered when `session_boundary_crossed = true`
- Detected by comparing `Submission_Session` values between source and target rows

**Error Context Fields:**
```json
{
  "fill_strategy": "forward_fill",
  "column": "Reviewer",
  "group_by_columns": ["Document_ID"],
  "from_row": {"Document_ID": "PRJ-FAC-DWG-ARC-0001", "row_index": 10},
  "to_row": {"Document_ID": "PRJ-FAC-DWG-ARC-0001", "row_index": 35},
  "row_jump": 25,
  "filled_value": "John Smith",
  "source_session": "2024001",
  "target_session": "2024002",
  "timestamp": "2024-01-20T14:30:00",
  "suggested_action": "Use group-based forward fill within sessions"
}
```

**Remediation Strategies:**
1. **ADD_SESSION_GROUPING**: Include `Submission_Session` in group_by columns
2. **SESSION_BOUNDARY_STOP**: Configure fill to stop at session boundaries
3. **MANUAL_SESSION_REVIEW**: Flag rows crossing sessions for manual review

---

### F4-C-F-0403: Multi-Level Fill Failed, Default Applied

| Attribute | Value |
|-----------|-------|
| **Error Code** | F4-C-F-0403 |
| **Severity** | WARNING |
| **Layer** | L3 (Business Logic) |
| **Description** | All levels of multi-level forward fill failed to find a value, default was applied |

**Detection Criteria:**
- Triggered when `all_levels_failed = true`
- Applies to both multi-level fills and default value operations

**Error Context Fields:**
```json
{
  "fill_strategy": "multi_level_forward_fill|default_value",
  "column": "Document_Revision",
  "group_by_columns": [["Project_Code"], ["Project_Code", "Document_ID"]],
  "from_row": {"Document_ID": "PRJ-FAC-DWG-ARC-0001", "row_index": 10},
  "to_row": {"Document_ID": "PRJ-FAC-DWG-ARC-0001", "row_index": 35},
  "row_jump": 25,
  "levels_tried": [["Project_Code"], ["Project_Code", "Document_ID"]],
  "levels_applied": 2,
  "all_levels_failed": true,
  "default_applied": true,
  "filled_value": "00",
  "timestamp": "2024-01-20T14:30:00",
  "suggested_action": "Verify data exists in higher level groupings"
}
```

**Remediation Strategies:**
1. **ADD_HIGHER_LEVELS**: Add broader grouping levels (e.g., Project-only)
2. **MANDATORY_ENTRY**: Make column mandatory at data entry time
3. **DEFAULT_REVIEW**: Review and validate default values are appropriate

---

### F4-C-F-0404: Excessive Null Fills Detected

| Attribute | Value |
|-----------|-------|
| **Error Code** | F4-C-F-0404 |
| **Severity** | WARNING |
| **Layer** | L3 (Business Logic) |
| **Description** | Column has excessive percentage of filled values (nulls filled) |

**Detection Criteria:**
- Triggered when `fill_percentage > max_fill_percentage` (default: 80%)
- Calculated as `(total_filled_rows / total_rows) * 100`

**Error Context Fields:**
```json
{
  "fill_strategy": "forward_fill",
  "column": "Reviewer",
  "group_by_columns": ["Project_Code", "Document_ID"],
  "from_row": {"Document_ID": "PRJ-FAC-DWG-ARC-0001", "row_index": 10},
  "to_row": {"Document_ID": "PRJ-FAC-DWG-ARC-0001", "row_index": 8877},
  "row_jump": 45,
  "fill_percentage": 85.5,
  "filled_rows": 8877,
  "total_rows": 11099,
  "forward_fills": 7500,
  "default_values": 1000,
  "multi_level_fills": 377,
  "max_row_jump": 45,
  "session_boundary_crosses": 12,
  "suggested_action": "Review data quality - column may have systemic missing data issues"
}
```

**Remediation Strategies:**
1. **IMPROVE_DATA_QUALITY**: Address root cause of missing data at source
2. **MANDATORY_COLUMNS**: Make high-null columns mandatory in data entry
3. **VALIDATION_RULES**: Add stricter validation to prevent nulls
4. **FILL_STRATEGY_REVIEW**: Evaluate if current fill strategy is appropriate

---

### F4-C-F-0405: Invalid Grouping Configuration

| Attribute | Value |
|-----------|-------|
| **Error Code** | F4-C-F-0405 |
| **Severity** | ERROR |
| **Layer** | L3 (Business Logic) |
| **Description** | Group-based fill configured with invalid or empty group_by columns |

**Detection Criteria:**
- Triggered when `group_by` is not empty but has length 0
- Or when specified group columns don't exist in DataFrame

**Error Context Fields:**
```json
{
  "fill_strategy": "forward_fill",
  "column": "Reviewer",
  "group_by_columns": [],
  "from_row": {"Document_ID": "PRJ-FAC-DWG-ARC-0001", "row_index": 10},
  "to_row": {"Document_ID": "PRJ-FAC-DWG-ARC-0001", "row_index": 35},
  "row_jump": 25,
  "filled_value": "John Smith",
  "timestamp": "2024-01-20T14:30:00",
  "suggested_action": "Specify valid grouping columns in schema"
}
```

**Remediation Strategies:**
1. **FIX_SCHEMA**: Update schema to specify valid grouping columns
2. **COLUMN_VALIDATION**: Validate group columns exist before processing
3. **DEFAULT_GROUPS**: Provide sensible default grouping columns

---

## Integration Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 2: Null Handling                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ apply_forward_  │  │ apply_multi_    │  │ apply_default_  │  │
│  │ fill()          │  │ level_forward_  │  │ value()         │  │
│  │                 │  │ fill()          │  │                 │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                     │                     │        │
│           └─────────────────────┼─────────────────────┘        │
│                                 ▼                              │
│                    ┌─────────────────────┐                      │
│                    │  _record_fill_      │                      │
│                    │  history()          │                      │
│                    └──────────┬──────────┘                      │
│                               │                                │
│                               ▼                                │
│                    ┌─────────────────────┐                      │
│                    │  engine.fill_history│◄─── Initialize []    │
│                    │  (List[Dict])       │                      │
│                    └──────────┬──────────┘                      │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 2.5: Anomaly Detection                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              BusinessDetector.detect()                       ││
│  │  context={"fill_history": engine.fill_history}              ││
│  └─────────────────────────────────────────────────────────────┘│
│           │                              │                      │
│           ▼                              ▼                      │
│  ┌──────────────────┐        ┌──────────────────┐              │
│  │ IdentityDetector │        │   FillDetector   │              │
│  │   (Document_ID)  │        │    (F4xx errors)   │              │
│  └────────┬─────────┘        └────────┬─────────┘              │
│           │                            │                        │
│           │                            ▼                        │
│           │              ┌─────────────────────────┐              │
│           │              │  _analyze_fill_history  │              │
│           │              │  - Route records        │              │
│           │              │  - Collect stats        │              │
│           │              └───────────┬─────────────┘              │
│           │                          │                          │
│           │          ┌───────────────┼───────────────┐           │
│           │          ▼               ▼               ▼           │
│           │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│           │  │ _check_     │ │ _check_     │ │ _check_     │    │
│           │  │ forward_    │ │ multi_      │ │ default_    │    │
│           │  │ fill_       │ │ level_      │ │ value_      │    │
│           │  │ record()    │ │ record()    │ │ record()    │    │
│           │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘    │
│           │         │               │               │            │
│           │         └───────────────┼───────────────┘            │
│           │                         │                          │
│           │                         ▼                          │
│           │         ┌─────────────────────────┐                │
│           │         │ _detect_excessive_      │                │
│           │         │ nulls_from_stats()        │                │
│           │         └─────────────┬───────────┘                │
│           │                       │                            │
│           └───────────────────────┼────────────────────────────┘
│                                   │
│                                   ▼
│                    ┌─────────────────────┐
│                    │   ErrorAggregator   │
│                    │   (F4xx errors added) │
│                    └─────────────────────┘
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              Phase 4: Validation & Error Aggregation             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Validation_Errors Column                        ││
│  │  Aggregates:                                                 ││
│  │    - F4-C-F-0401: Row jump limit exceeded                    ││
│  │    - F4-C-F-0402: Session boundary crossed                 ││
│  │    - F4-C-F-0403: Default value applied                    ││
│  │    - F4-C-F-0404: Excessive null fills                      ││
│  │    - F4-C-F-0405: Invalid grouping                         ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Configuration

### FillDetector Configuration

```python
from processor_engine.error_handling.detectors import FillDetector

# Initialize with custom settings
detector = FillDetector(
    logger=structured_logger,           # Optional: StructuredLogger instance
    enable_fail_fast=True,              # Stop on critical errors
    jump_limit=20,                      # Max row jump before error (default: 20)
    max_fill_percentage=80.0            # Max % of filled values (default: 80%)
)
```

### Schema Configuration

Configure fill behavior in `dcc_register_enhanced.json`:

```json
{
  "columns": [
    {
      "name": "Reviewer",
      "null_handling": {
        "strategy": "forward_fill",
        "group_by": ["Project_Code", "Document_ID"],
        "final_fill": "TBD"
      }
    },
    {
      "name": "Document_Revision",
      "null_handling": {
        "strategy": "multi_level_forward_fill",
        "levels": [
          {"group_by": ["Project_Code"]},
          {"group_by": ["Project_Code", "Document_ID"]}
        ],
        "final_fill": "00"
      }
    }
  ]
}
```

---

## Detection Algorithms

### Row Jump Detection

**Algorithm:**
1. Calculate `row_jump = to_row_index - from_row_index`
2. Compare against `jump_limit` (default: 20)
3. If `row_jump > jump_limit`, generate F4-C-F-0401 error

**Example:**
- From row: 10
- To row: 35
- Row jump: 25
- Limit: 20
- Result: **ERROR F4-C-F-0401** (25 > 20)

### Session Boundary Detection

**Algorithm:**
1. Extract `Submission_Session` for both from_row and to_row
2. Compare session values
3. If sessions differ and both are non-empty, set `session_boundary_crossed = true`
4. Generate F4-C-F-0402 error

**Example:**
- Source session: "2024001"
- Target session: "2024002"
- Result: **ERROR F4-C-F-0402** (boundary crossed)

### Excessive Null Detection

**Algorithm:**
1. Track total filled rows per column during fill history analysis
2. Calculate `fill_percentage = (filled_rows / total_rows) * 100`
3. Compare against `max_fill_percentage` (default: 80%)
4. If `fill_percentage > max_fill_percentage`, generate F4-C-F-0404 error

**Example:**
- Total rows: 1000
- Filled rows: 850
- Fill percentage: 85%
- Max allowed: 80%
- Result: **WARNING F4-C-F-0404** (85% > 80%)

---

## Fill History Record Schema

Each fill operation generates a record with the following structure:

```json
{
  "operation_type": "forward_fill|multi_level_forward_fill|default_value",
  "column": "Column_Name",
  "from_row": {
    "Document_ID": "PRJ-FAC-DWG-ARC-0001",
    "Submission_Date": "2024-01-15",
    "Submission_Session": "2024001",
    "row_index": 10
  },
  "to_row": {
    "Document_ID": "PRJ-FAC-DWG-ARC-0001",
    "Submission_Date": "2024-01-20",
    "Submission_Session": "2024002",
    "row_index": 35
  },
  "row_jump": 25,
  "group_by": ["Project_Code", "Document_ID"],
  "filled_value": "John Smith",
  "session_boundary_crossed": true,
  "source_session": "2024001",
  "target_session": "2024002",
  "levels_applied": 2,
  "all_levels_failed": false,
  "default_applied": false,
  "timestamp": "2024-01-20T14:30:00.000Z"
}
```

---

## Remediation Workflow

### Step 1: Identify Errors

Check `Validation_Errors` column in output:

```csv
Document_ID,Reviewer,Validation_Errors
PRJ-FAC-DWG-ARC-0001,John Smith,"[{\"code\":\"F4-C-F-0401\",\"message\":\"Forward fill row jump exceeded limit...\"}]"
```

### Step 2: Analyze Context

Review error context fields:
- Which column? → `column`
- How many rows? → `row_jump`
- Which groups? → `group_by_columns`
- Which rows? → `from_row`, `to_row`

### Step 3: Select Strategy

Based on error type:

| Error | Recommended Strategy |
|-------|---------------------|
| F4-C-F-0401 | BREAK_LARGE_GROUPS, MANUAL_ENTRY |
| F4-C-F-0402 | ADD_SESSION_GROUPING |
| F4-C-F-0403 | ADD_HIGHER_LEVELS, MANDATORY_ENTRY |
| F4-C-F-0404 | IMPROVE_DATA_QUALITY, MANDATORY_COLUMNS |
| F4-C-F-0405 | FIX_SCHEMA |

### Step 4: Apply Fix

**For Schema Issues:**
```json
{
  "null_handling": {
    "group_by": ["Project_Code", "Document_ID", "Submission_Session"]
  }
}
```

**For Data Quality:**
- Update source systems to provide complete data
- Add mandatory field validation at data entry

### Step 5: Re-run Pipeline

Execute `dcc_engine_pipeline.py` and verify errors are resolved.

---

## Testing

### Unit Tests

```python
from processor_engine.error_handling.detectors import FillDetector
import pandas as pd

# Create detector
detector = FillDetector(jump_limit=20, max_fill_percentage=80.0)

# Test fill history
fill_history = [
    {
        "operation_type": "forward_fill",
        "column": "Reviewer",
        "from_row": {"row_index": 10},
        "to_row": {"row_index": 35},
        "row_jump": 25,
        "session_boundary_crossed": True
    }
]

# Detect errors
results = detector.detect(pd.DataFrame(), context={"fill_history": fill_history})

# Verify
assert any(r.error_code == "F4-C-F-0401" for r in results)
assert any(r.error_code == "F4-C-F-0402" for r in results)
```

### Integration Tests

Run full pipeline and check Validation_Errors column:

```bash
python dcc_engine_pipeline.py
# Check output/error_dashboard_data.json for F4xx errors
```

---

## Related Documentation

- [Error Handling Module Workplan](../workplan/error_handling/error_handling_module_workplan.md)
- [Data Error Handling](../workplan/error_handling/data_error_handling.md)
- [Column Processing Logic](../explaination/column_update_logic.md)
- [Schema Definition](../config/schemas/dcc_register_enhanced.json)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-04-12 | Initial implementation - Phases A, B, C, D, E complete |

---

## Contact & Support

For issues or questions regarding the Null Handling Error Detection module:
- Check [update_log.md](../Log/update_log.md) for recent changes
- Review [issue_log.md](../Log/issue_log.md) for known issues
- Refer to [error_handling_module_workplan.md](../workplan/error_handling/error_handling_module_workplan.md) for implementation status
