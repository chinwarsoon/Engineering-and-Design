# Document Processor Engine

A modular engine for processing documents with schema-driven calculations, null handling, and validation.

## Module Structure

```
processor_engine/engine/
├── __init__.py          # Main engine exports
├── readme.md            # This file
├── core/                # Core engine components
│   ├── __init__.py
│   ├── base.py          # BaseProcessor with shared utilities
│   ├── engine.py        # CalculationEngine orchestrator
│   └── registry.py      # Handler registries for calculations and null handling
├── calculations/        # Calculation implementations
│   ├── __init__.py
│   ├── aggregate.py     # Grouping/aggregation calculations
│   ├── composite.py     # Composite, row index, delay calculations
│   ├── conditional.py   # Conditional logic calculations
│   ├── date.py          # Date arithmetic calculations
│   ├── mapping.py       # Value mapping calculations
│   ├── null_handling.py # Null handling strategies
│   └── validation.py    # Data validation functions
├── schema/              # Schema utilities
│   ├── __init__.py
│   ├── dependency.py    # Dependency resolution and calculation ordering
│   └── processor.py     # Schema processing utilities
└── utils/               # Utility functions
    ├── __init__.py
    ├── dateframe.py     # DataFrame manipulation utilities
    └── logging.py       # Logging utilities
```

## Quick Start

```python
from dcc.workflow.processor_engine.engine import CalculationEngine
from dcc.workflow.processor_engine.engine.calculations import (
    apply_forward_fill,
    apply_aggregate_calculation,
    apply_mapping_calculation,
)

# Create engine with schema data
engine = CalculationEngine(schema_data)

# Process DataFrame
df_processed = engine.process_data(df)
```

## Calculation Types

### Aggregate Calculations (`aggregate.py`)
- `apply_aggregate_calculation` - Standard grouping (count, min, max, concatenate)
- `apply_latest_by_date_calculation` - Latest value by date
- `apply_latest_non_pending_status` - Latest non-pending status

### Composite Calculations (`composite.py`)
- `apply_composite_calculation` - Format string composition
- `apply_row_index` - Auto-increment row indexing
- `apply_delay_of_resubmission` - Delay calculation with vectorized approach
- `apply_copy_calculation` - Direct column copy

### Conditional Calculations (`conditional.py`)
- `apply_current_row_calculation` - Current row value extraction
- `apply_update_resubmission_required` - Resubmission logic with short-circuit
- `apply_submission_closure_status` - Submission closure determination
- `apply_calculate_overdue_status` - Overdue status calculation

### Date Calculations (`date.py`)
- `apply_date_calculation` - Standard date calculations
- `calculate_working_days` - Working days addition
- `calculate_date_difference` - Date difference in days
- `apply_resubmission_plan_date` - Conditional resubmission date
- `apply_conditional_date_calculation` - First vs subsequent submission dates
- `apply_conditional_business_day_calculation` - Business day calculations

### Mapping Calculations (`mapping.py`)
- `apply_mapping_calculation` - Status to code mapping
- `apply_status_to_code` - Status code resolution

### Null Handling (`null_handling.py`)
- `apply_forward_fill` - Forward fill with grouping
- `apply_multi_level_forward_fill` - Multi-level forward fill
- `apply_copy_from` - Copy from source column
- `apply_calculate_if_null` - Calculate if null (legacy)
- `apply_default_value` - Default value with formatting
- `apply_lookup_if_null` - Group-based lookup

### Validation (`validation.py`)
- `collect_raw_pattern_errors` - Raw input validation
- `apply_validation` - Full schema validation

## Registry System

The registry system maps calculation types to handler functions:

```python
from dcc.workflow.processor_engine.engine.core import (
    get_null_handler,
    get_calculation_handler,
    register_calculation_handler,
)

# Get a handler
handler = get_calculation_handler('aggregate', 'latest_by_date')

# Register a custom handler
register_calculation_handler('my_type', 'my_method', my_function)
```

## Schema Dependency Resolution

```python
from dcc.workflow.processor_engine.engine.schema import resolve_calculation_order

# Get validated calculation order
calculation_order = resolve_calculation_order(columns_schema)
```
