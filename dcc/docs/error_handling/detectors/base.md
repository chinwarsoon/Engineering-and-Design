# Base Detector User Instruction

## Table of Contents

1. [Overview](#overview)
2. [Base Classes](#base-classes)
3. [DetectionResult](#detectionresult)
4. [Creating Custom Detectors](#creating-custom-detectors)
5. [Function I/O Reference](#function-io-reference)
6. [Examples](#examples)
7. [Best Practices](#best-practices)

---

## Overview

The **BaseDetector** module provides abstract base classes and data structures for all error detectors in the DCC Engine Pipeline. It defines the standard interface and common functionality.

**Location:** `detectors/base.py`

**Key Components:**
- `BaseDetector` - Abstract base class for all detectors
- `DetectionResult` - Data structure for error information
- `CompositeDetector` - Combines multiple detectors
- `FailFastError` - Exception for critical errors

---

## Base Classes

### BaseDetector

Abstract base class that all detectors must inherit from.

```python
class BaseDetector(ABC):
    def __init__(self, layer: str, logger=None, enable_fail_fast=True)
    
    @abstractmethod
    def detect(self, df: pd.DataFrame, context: Dict) -> List[DetectionResult]
    
    def detect_error(self, error_code, message, row, column, 
                     severity, additional_context)
```

**Constructor Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `layer` | str | Error layer (L1, L2, L3, L4) |
| `logger` | StructuredLogger | Optional logger instance |
| `enable_fail_fast` | bool | Stop on critical errors |

### CompositeDetector

Combines multiple detectors into a single detector.

```python
composite = CompositeDetector(
    detectors=[detector1, detector2],
    layer="L3"
)
```

---

## DetectionResult

Data structure representing a detected error.

```python
@dataclass
class DetectionResult:
    error_code: str          # E.g., "F4-C-F-0401"
    message: str             # Human-readable message
    row: int                 # Row index
    column: str              # Column name
    severity: str            # ERROR, HIGH, MEDIUM, WARNING
    layer: str               # L1, L2, L3, L4
    fail_fast: bool          # Stop processing if True
    additional_context: Dict # Extra information
```

### Error Code Format

```
[CATEGORY]-[COMPONENT]-[SUBCATEGORY]-[NUMBER]

Examples:
- F4-C-F-0401    (Fill, Core, Forward Fill, 0401)
- A3-C-D-0301    (Anchor, Core, Document, 0301)
- I5-C-D-0501    (Identity, Core, Document, 0501)
```

---

## Creating Custom Detectors

### Step 1: Inherit from BaseDetector

```python
from processor_engine.error_handling.detectors.base import BaseDetector

class MyDetector(BaseDetector):
    def __init__(self, **kwargs):
        super().__init__(layer="L3", **kwargs)
        self.ERROR_CUSTOM = "CUST-C-0001"
```

### Step 2: Implement detect() Method

```python
    def detect(self, df: pd.DataFrame, context=None) -> List[DetectionResult]:
        self.clear_errors()
        
        # Detection logic
        for idx, row in df.iterrows():
            if self._is_invalid(row):
                self.detect_error(
                    error_code=self.ERROR_CUSTOM,
                    message="Invalid data detected",
                    row=idx,
                    column="MyColumn",
                    severity="WARNING",
                    fail_fast=False,
                    additional_context={
                        "value": row["MyColumn"],
                        "suggested_action": "Fix the data"
                    }
                )
        
        return self.get_errors()
```

### Step 3: Register with BusinessDetector

```python
from processor_engine.error_handling.detectors import BusinessDetector, ProcessingPhase

business_detector = BusinessDetector()
business_detector.register_phase_detector(
    ProcessingPhase.P2_5,
    MyDetector()
)
```

---

## Function I/O Reference

### BaseDetector Methods

#### `detect(df, context=None)`

**Input:**
- `df` (pd.DataFrame) - Data to validate
- `context` (dict) - Optional context data

**Output:**
- `List[DetectionResult]` - Detected errors

#### `detect_error(...)`

**Parameters:**
- `error_code` (str) - Unique error identifier
- `message` (str) - Error description
- `row` (int) - Row index
- `column` (str) - Column name
- `severity` (str) - ERROR, HIGH, MEDIUM, WARNING
- `fail_fast` (bool) - Stop on this error
- `additional_context` (dict) - Extra info

#### `get_errors()`

Returns all detected errors.

#### `clear_errors()`

Clears the error list.

#### `set_context(**kwargs)`

Sets context for error detection.

---

## Examples

### Example 1: Simple Custom Detector

```python
from processor_engine.error_handling.detectors.base import BaseDetector

class RangeDetector(BaseDetector):
    """Detects values outside acceptable range."""
    
    def __init__(self, min_val=0, max_val=100, **kwargs):
        super().__init__(layer="L3", **kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.ERROR_RANGE = "RANG-C-0001"
    
    def detect(self, df, context=None):
        self.clear_errors()
        column = context.get("column", "Value")
        
        for idx, row in df.iterrows():
            value = row.get(column)
            if pd.notna(value) and (value < self.min_val or value > self.max_val):
                self.detect_error(
                    error_code=self.ERROR_RANGE,
                    message=f"Value {value} outside range [{self.min_val}, {self.max_val}]",
                    row=idx,
                    column=column,
                    severity="WARNING",
                    fail_fast=False,
                    additional_context={
                        "value": value,
                        "min": self.min_val,
                        "max": self.max_val,
                        "suggested_action": f"Ensure value is between {self.min_val} and {self.max_val}"
                    }
                )
        
        return self.get_errors()
```

### Example 2: Composite Detector

```python
from processor_engine.error_handling.detectors.base import CompositeDetector
from processor_engine.error_handling.detectors import FillDetector, IdentityDetector

# Create individual detectors
fill_detector = FillDetector(jump_limit=15)
identity_detector = IdentityDetector()

# Combine into composite
composite = CompositeDetector(
    detectors=[fill_detector, identity_detector],
    layer="L3",
    enable_fail_fast=False
)

# Use composite
errors = composite.detect(df, context)
```

---

## Best Practices

### 1. Always Call clear_errors()

```python
def detect(self, df, context=None):
    self.clear_errors()  # Important!
    # ... detection logic
```

### 2. Use Appropriate Severity

```python
# ERROR - Pipeline stops
severity="ERROR"  # Use for critical issues

# HIGH - Requires review
severity="HIGH"   # Use for important issues

# WARNING - Informational
severity="WARNING"  # Use for minor issues
```

### 3. Provide Actionable Context

```python
additional_context={
    "value": current_value,
    "expected": expected_value,
    "suggested_action": "Specific remediation step"
}
```

### 4. Handle Missing Data Gracefully

```python
value = row.get("Column")
if pd.isna(value):
    continue  # Skip null values
```

### 5. Use Consistent Error Codes

Follow the pattern: `[CATEGORY]-[COMPONENT]-[SUBCATEGORY]-[NUMBER]`

---

## Related Documentation

- [Error Handling Module](../readme.md)
- [Fill Detector](fill.md)
- [Business Detector](business.md)

---

*Last Updated: 2024-04-12*
*Version: 1.0*
