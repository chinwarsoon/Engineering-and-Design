# Fill Detector User Instruction

## Table of Contents

1. [Overview](#overview)
2. [Error Codes](#error-codes)
3. [Detection Algorithms](#detection-algorithms)
4. [Configuration](#configuration)
5. [Function I/O Reference](#function-io-reference)
6. [Examples](#examples)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Overview

The **FillDetector** analyzes null handling operations (forward fills, multi-level fills, default values) to detect potential data quality issues. It is the primary detector for F4xx error codes.

**Location:** `detectors/fill.py`  
**Layer:** L3 (Business Logic)  
**Phase:** P2.5 (Anomaly Detection)

**Key Capabilities:**
- Detect row jumps exceeding configured limits
- Identify session boundary crossings
- Flag excessive null fills (>80% default)
- Detect invalid grouping configurations
- Track multi-level fill failures

---

## Error Codes

### F4-C-F-0401: Forward Fill Row Jump Exceeded

| Attribute | Value |
|-----------|-------|
| **Severity** | HIGH |
| **Trigger** | `row_jump > jump_limit` (default: 20) |
| **Context** | fill_strategy, row_jump, from_row, to_row, fill_percentage |

**Remediation:**
- Add more grouping columns to reduce fill distance
- Increase `jump_limit` if appropriate
- Use manual data entry for large gaps

### F4-C-F-0402: Session Boundary Crossed

| Attribute | Value |
|-----------|-------|
| **Severity** | HIGH |
| **Trigger** | `session_boundary_crossed = true` |
| **Context** | source_session, target_session, group_by_columns |

**Remediation:**
- Add `Submission_Session` to group_by columns
- Use group-based forward fill within sessions

### F4-C-F-0403: Multi-Level Fill Failed

| Attribute | Value |
|-----------|-------|
| **Severity** | WARNING |
| **Trigger** | `all_levels_failed = true` |
| **Context** | levels_tried, default_applied, filled_value |

**Remediation:**
- Add higher-level groupings (e.g., Project-only)
- Make column mandatory at data entry

### F4-C-F-0404: Excessive Null Fills

| Attribute | Value |
|-----------|-------|
| **Severity** | WARNING |
| **Trigger** | `fill_percentage > max_fill_percentage` (default: 80%) |
| **Context** | fill_percentage, filled_rows, total_rows |

**Remediation:**
- Improve data quality at source
- Review if column should be mandatory
- Evaluate alternative fill strategies

### F4-C-F-0405: Invalid Grouping Configuration

| Attribute | Value |
|-----------|-------|
| **Severity** | ERROR |
| **Trigger** | Empty or invalid `group_by` configuration |
| **Context** | group_by_columns, operation_type |

**Remediation:**
- Specify valid grouping columns in schema
- Validate group columns exist before processing

---

## Detection Algorithms

### Row Jump Detection

```python
# Calculate row jump
row_jump = to_row_index - from_row_index

# Check against limit
if row_jump > jump_limit:
    generate_error(F4-C-F-0401)
```

### Session Boundary Detection

```python
# Compare sessions
if source_session != target_session:
    session_boundary_crossed = true
    generate_error(F4-C-F-0402)
```

### Excessive Fill Detection

```python
# Calculate percentage
fill_percentage = (filled_rows / total_rows) * 100

# Check threshold
if fill_percentage > max_fill_percentage:
    generate_error(F4-C-F-0404)
```

---

## Configuration

### Constructor Parameters

```python
FillDetector(
    logger=None,                    # StructuredLogger instance
    enable_fail_fast=True,          # Stop on critical errors
    jump_limit=20,                  # Max row jump before error
    max_fill_percentage=80.0        # Max % of filled values
)
```

### Schema Configuration

```json
{
  "null_handling": {
    "strategy": "forward_fill",
    "group_by": ["Project_Code", "Document_ID", "Submission_Session"],
    "final_fill": "TBD"
  }
}
```

---

## Function I/O Reference

### Core Methods

#### `detect(df, context=None)`

**Input:**
- `df` (pd.DataFrame) - Data being processed
- `context` (dict) - Must contain `fill_history`

**Output:**
- `List[DetectionResult]` - List of detected errors

**Example:**
```python
detector = FillDetector()
errors = detector.detect(
    df,
    context={"fill_history": engine.fill_history}
)
```

#### `_analyze_fill_history(fill_history)`

**Input:**
- `fill_history` (List[Dict]) - Recorded fill operations

**Output:**
- None (populates internal errors list)

**Processing:**
1. Routes records to appropriate checker
2. Collects statistics per column
3. Generates errors based on thresholds

---

## Examples

### Example 1: Basic Usage

```python
from processor_engine.error_handling.detectors import FillDetector

# Create detector
detector = FillDetector(jump_limit=15)

# Fill history from processing
fill_history = [
    {
        "operation_type": "forward_fill",
        "column": "Reviewer",
        "from_row": {"row_index": 10, "Document_ID": "DOC-001"},
        "to_row": {"row_index": 30, "Document_ID": "DOC-001"},
        "row_jump": 20,
        "session_boundary_crossed": True,
        "source_session": "2024001",
        "target_session": "2024002",
        "group_by": ["Project_Code"]
    }
]

# Detect
errors = detector.detect(
    pd.DataFrame(),
    context={"fill_history": fill_history}
)

# Results
for error in errors:
    print(f"{error.error_code}: {error.message}")
    print(f"Row: {error.row}, Column: {error.column}")
```

### Example 2: With Engine Integration

```python
# In CalculationEngine.apply_phased_processing()

# Initialize fill history at Phase 2 start
self.fill_history = []

# ... processing fills records to fill_history ...

# Phase 2.5: Run FillDetector
fill_detector = FillDetector()
errors = fill_detector.detect(
    df,
    context={"fill_history": self.fill_history}
)

# Add to aggregator
for error in errors:
    self.error_aggregator.add_error(error)

# Clear history to prevent memory bloat
self.fill_history = []
```

---

## Troubleshooting

### No Errors Detected

**Check:** Is `fill_history` being populated?
```python
print(f"Fill history entries: {len(fill_history)}")
print(f"Sample entry: {fill_history[0] if fill_history else 'None'}")
```

### Too Many F4-C-F-0401 Errors

**Solutions:**
1. Add more grouping columns
2. Increase `jump_limit` (if appropriate)
3. Review if large gaps are valid

```python
# Stricter grouping
group_by = ["Project_Code", "Document_ID", "Submission_Session"]

# Or increase limit
detector = FillDetector(jump_limit=50)
```

### Session Boundary Errors

**Solution:** Add `Submission_Session` to grouping
```json
{
  "group_by": ["Project_Code", "Document_ID", "Submission_Session"]
}
```

---

## Best Practices

1. **Always Initialize fill_history** at Phase 2 start
2. **Use appropriate jump_limit** (20 is default, adjust per use case)
3. **Include Submission_Session** in grouping to prevent boundary issues
4. **Clear fill_history** after detection to prevent memory issues
5. **Review F4-C-F-0404 warnings** for systemic data quality issues

---

## Related Documentation

- [Null Handling Error Guide](../null_handling_guide.md)
- [Error Handling Module](../readme.md)
- [Business Detector](business.md)

---

*Last Updated: 2024-04-12*
*Version: 1.0*
