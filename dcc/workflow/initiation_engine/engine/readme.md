# Initiation Engine

A modular engine for project setup validation and initialization.

## Module Structure

```
initiation_engine/engine/
├── __init__.py          # Main engine exports
├── readme.md            # This file
├── core/                # Core components
│   ├── __init__.py
│   ├── validator.py     # ProjectSetupValidator orchestrator
│   └── reports.py       # Report formatting
├── validators/          # Validation logic
│   ├── __init__.py
│   └── items.py         # Folder/file/environment validation
├── utils/               # Utilities
│   ├── __init__.py
│   └── paths.py         # Path normalization
└── system/              # System detection
    ├── __init__.py
    └── os_detect.py     # OS detection and auto-creation logic
```

## Quick Start

```python
from dcc.workflow.initiation_engine.engine import ProjectSetupValidator

# Validate project setup
validator = ProjectSetupValidator(base_path='/path/to/project')
results = validator.validate()

# Check if ready
if results['ready']:
    print("Project setup is valid!")
else:
    print(validator.format_report(results))
```

## Components

### Core (`core/validator.py`)
- `ProjectSetupValidator` - Main orchestrator class
  - `validate()` - Run full project setup validation
  - `format_report()` - Format results for terminal output

### Validators (`validators/items.py`)
- `validate_folders()` - Validate project folders with auto-creation
- `validate_named_files()` - Validate named files in categories
- `validate_environment()` - Validate environment specification files
- `check_ready()` - Check if all required items exist
- `record_path_check()` - Record a path check result
- `ensure_folder()` - Create folder if it doesn't exist

### Utils (`utils/paths.py`)
- `normalize_path()` - Normalize path to absolute form
- `default_base_path()` - Get default base path
- `get_schema_path()` - Get default schema path

### System (`system/os_detect.py`)
- `detect_os()` - Detect operating system
- `should_auto_create_folders()` - Check if folders should be auto-created

### Core (`core/reports.py`)
- `format_report()` - Format validation results for terminal output

## Usage Example

```python
from dcc.workflow.initiation_engine.engine import (
    ProjectSetupValidator,
    validate_folders,
    validate_named_files,
    detect_os,
)

# Full validation
validator = ProjectSetupValidator()
results = validator.validate()
print(validator.format_report(results))

# Custom validation
from pathlib import Path
from dcc.workflow.initiation_engine.engine.utils import default_base_path

base_path = default_base_path()
os_info = detect_os()
results = {'folders': [], 'errors': []}

folders = [
    {'name': 'data', 'required': True, 'purpose': 'Input data files'},
    {'name': 'output', 'required': False, 'purpose': 'Generated output', 'auto_created': True},
]

validate_folders(results, folders, base_path, os_info)
```
