# Schema Engine

A modular engine for schema loading, validation, and dependency resolution.

## Module Structure

```
schema_engine/engine/
├── __init__.py          # Main engine exports
├── readme.md            # This file
├── core/                # Core components
│   ├── __init__.py
│   └── reports.py       # Report formatting
├── loader/              # Schema loading
│   ├── __init__.py
│   └── schema_loader.py # SchemaLoader class
├── validator/           # Schema validation
│   ├── __init__.py
│   ├── schema_validator.py  # SchemaValidator class
│   └── fields.py        # Field-level validation
├── status/              # Validation status persistence
│   ├── __init__.py
│   └── persistence.py   # Status read/write/check
└── utils/               # Utilities
    ├── __init__.py
    └── paths.py         # Safe path operations
```

## Quick Start

```python
from dcc.workflow.schema_engine.engine import SchemaLoader, SchemaValidator, format_report

# Load and validate schema
validator = SchemaValidator('config/schema.json')
results = validator.validate()

# Check if ready
if results['ready']:
    print(format_report(results))
    # Load resolved schema with dependencies
    resolved = validator.load_resolved_schema()
```

## Components

### Loader (`loader/schema_loader.py`)
- `SchemaLoader` - Load JSON schemas and resolve dependencies
  - `load_json_file()` - Load JSON from disk
  - `load_schema()` - Load by stem name
  - `load_schema_from_path()` - Load by path
  - `resolve_schema_dependencies()` - Resolve all schema_references

### Validator (`validator/schema_validator.py`)
- `SchemaValidator` - Main orchestrator class
  - `validate()` - Validate main schema and references
  - `load_main_schema()` - Load after validation
  - `load_resolved_schema()` - Load with dependencies

### Field Validation (`validator/fields.py`)
- `validate_schema_document()` - Validate field definitions
- `validate_scalar_record_section()` - Validate scalar lists
- `find_record_section()` - Auto-detect record section
- `validate_scalar_value()` - Validate single scalar
- `validate_record_field()` - Validate field in record
- `validate_scalar_rules()` - Check min/max/pattern
- `track_unique_scalar()` - Track unique values
- `validate_array_rules()` - Check array constraints

### Status (`status/persistence.py`)
- `get_validation_status_path()` - Get status file path
- `write_validation_status()` - Persist validation results
- `load_validation_status()` - Load persisted status
- `validate_validation_status()` - Check if status is current

### Utils (`utils/paths.py`)
- `safe_resolve()` - Get absolute path without I/O
- `safe_cwd()` - Get working directory safely
- `get_default_schema_path()` - Default schema location

### Core (`core/reports.py`)
- `format_report()` - Format results for terminal output

## Usage Example

```python
from dcc.workflow.schema_engine.engine import (
    SchemaLoader,
    SchemaValidator,
    write_validation_status,
    validate_validation_status,
    format_report,
)

# Validate schema
validator = SchemaValidator('config/schema.json')
results = validator.validate()

# Write status for downstream pipeline
write_validation_status(results)

# Later, check if status is current
is_valid, message = validate_validation_status('config/schema.json')
if not is_valid:
    print(f"Status stale: {message}")

# Load with dependencies
loader = SchemaLoader()
loader.set_main_schema_path('config/schema.json')
main = loader.load_json_file('config/schema.json')
resolved = loader.resolve_schema_dependencies(main)
```
