# Column Mapper Engine

A modular engine for fuzzy header detection and schema-driven column mapping.

## Module Structure

```
mapper_engine/engine/
├── __init__.py          # Main engine exports
├── readme.md            # This file
├── core/                # Core engine components
│   ├── __init__.py
│   └── engine.py        # ColumnMapperEngine orchestrator
├── matchers/            # Fuzzy matching algorithms
│   ├── __init__.py
│   └── fuzzy.py         # String normalization and fuzzy matching
├── mappers/             # Column mapping logic
│   ├── __init__.py
│   └── detection.py     # Column detection and renaming
└── utils/               # Utility functions
    ├── __init__.py
    └── columns.py       # Column bounds and coverage analysis
```

## Quick Start

```python
from dcc.workflow.mapper_engine.engine import ColumnMapperEngine
from dcc.workflow.schema_validation import SchemaLoader

# Create engine with schema
schema_loader = SchemaLoader()
engine = ColumnMapperEngine(schema_loader=schema_loader, schema_file='path/to/schema.json')

# Map DataFrame columns
result = engine.map_dataframe(df)
mapped_df = result['renamed_df']
mapping_info = result['mapping_result']
```

## Components

### Core Engine (`core/engine.py`)
- `ColumnMapperEngine` - Main orchestrator class
  - `load_main_schema()` - Load and resolve schema dependencies
  - `detect_columns()` - Detect and map input headers to schema columns
  - `rename_dataframe_columns()` - Rename DataFrame based on detected mapping
  - `get_column_bounds()` - Get non-null bounds for each column
  - `map_dataframe()` - Complete pipeline (detect + rename)

### Matchers (`matchers/fuzzy.py`)
- `normalize_string()` - Normalize strings for comparison
- `fuzzy_match_column()` - Fuzzy match header against target columns
- `fuzzy_match_with_aliases()` - Match header against column aliases
- `batch_fuzzy_match()` - Batch fuzzy matching for multiple headers

### Mappers (`mappers/detection.py`)
- `flatten_multiindex_headers()` - Flatten tuple headers from MultiIndex
- `detect_columns()` - Main column detection logic
- `extract_categorical_choices()` - Extract choices for categorical columns
- `rename_dataframe_columns()` - Rename DataFrame columns based on mapping

### Utils (`utils/columns.py`)
- `get_column_bounds()` - Get non-null bounds for each column
- `analyze_column_coverage()` - Analyze column coverage statistics

## Usage Example

```python
from dcc.workflow.mapper_engine.engine import ColumnMapperEngine, fuzzy_match_column
from dcc.workflow.schema_validation import SchemaLoader

# Initialize
schema_loader = SchemaLoader()
engine = ColumnMapperEngine()
engine.load_main_schema('config/schema.json', schema_loader)

# Sample headers
headers = ["Doc Type", "Revision", "Date Submit", "SO Review Status"]

# Detect columns
result = engine.detect_columns(headers, threshold=0.6)
print(f"Matched: {result['matched_count']}/{result['total_headers']}")

# Rename DataFrame
mapped_df = engine.rename_dataframe_columns(df, result)
```
