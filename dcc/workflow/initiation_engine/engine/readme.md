# Initiation Engine

A modular, comprehensive engine for project setup validation, initialization, and environment management. This engine provides tools for validating project structure, detecting system configurations, managing paths across platforms, and generating detailed validation reports.

---

## Table of Contents

- [Module Structure](#module-structure)
- [Workflow Overview](#workflow-overview)
- [Core Functions](#core-functions)
- [Validator Functions](#validator-functions)
- [Utility Functions](#utility-functions)
  - [Path Utilities](#path-utilities)
  - [CLI Utilities](#cli-utilities)
  - [Logging Utilities](#logging-utilities)
  - [System Utilities](#system-utilities)
- [System Detection](#system-detection)
- [Report Formatting](#report-formatting)
- [Usage Examples](#usage-examples)
  - [Basic Validation](#basic-validation)
  - [Custom Validation](#custom-validation)
  - [CLI Usage](#cli-usage)
  - [Environment Testing](#environment-testing)

---

## Module Structure

```
initiation_engine/engine/
├── __init__.py              # Main engine exports (all public functions)
├── readme.md                # This documentation file
├── core/                    # Core validation and reporting components
│   ├── __init__.py          # Core module exports
│   ├── validator.py         # ProjectSetupValidator orchestrator class
│   └── reports.py           # Report formatting functions
├── validators/              # Validation logic implementations
│   ├── __init__.py          # Validators module exports
│   └── items.py             # Folder/file/environment validation functions
├── utils/                   # Utility functions
│   ├── __init__.py          # Utils module exports
│   ├── paths.py             # Path normalization and resolution
│   ├── cli.py               # CLI argument parsing
│   ├── logging.py           # Logging and status output utilities
│   └── system.py            # Environment testing utilities
└── system/                  # System detection and OS-specific logic
    ├── __init__.py          # System module exports
    └── os_detect.py         # OS detection and auto-creation logic
```

---

## Workflow Overview

The initiation engine follows a structured validation workflow:

```
┌─────────────────────────────────────────────────────────────┐
│                    INITIATION ENGINE WORKFLOW               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌────────────────────────────────────────┐
        │  1. Initialize ProjectSetupValidator   │
        │     - Load base_path & schema_path     │
        │     - Detect operating system          │
        │     - Load project_setup.json schema   │
        └────────────────────────────────────────┘
                              │
                              ▼
        ┌────────────────────────────────────────┐
        │  2. Run validate() Method              │
        │     ┌──────────────────────────────┐   │
        │     │ Check: Validation Rules      │   │
        │     │  - check_folders (rule)      │   │
        │     │  - check_files (rule)        │   │
        │     └──────────────────────────────┘   │
        └────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌─────────────────────┐       ┌─────────────────────┐
    │ validate_folders()  │       │ validate_named_     │
    │   - Auto-create if  │       │   files()           │
    │     enabled         │       │   - root_files      │
    │   - Record results  │       │   - schema_files    │
    └─────────────────────┘       │   - workflow_files  │
                                  │   - tool_files      │
                                  └─────────────────────┘
                                              │
                                  ┌─────────────────────┐
                                  │ validate_           │
                                  │ environment()       │
                                  │   - env files       │
                                  │   - setup commands  │
                                  └─────────────────────┘
                                              │
                              ┌───────────────▼───────────────┐
                              │  3. check_ready()              │
                              │     - Verify all required      │
                              │       items exist              │
                              └───────────────────────────────┘
                                              │
                              ┌───────────────▼───────────────┐
                              │  4. format_report()            │
                              │     - Generate human-readable  │
                              │       validation summary       │
                              └───────────────────────────────┘
```

### Validation Rule System

The engine supports configurable validation rules from `project_setup.json`:

```json
{
  "project_setup": {
    "validation_rules": [
      {"rule": "check_folders", "enabled": true},
      {"rule": "check_files", "enabled": true}
    ]
  }
}
```

Rules can be dynamically enabled/disabled, allowing flexible validation workflows.

---

## Core Functions

### ProjectSetupValidator Class

**File:** `core/validator.py`

The main orchestrator class that coordinates all validation activities.

| Attribute | Details |
|-----------|---------|
| **Input** | `base_path` (str/Path, optional): Project root directory<br>`schema_path` (str/Path, optional): Path to schema JSON file |
| **Output** | Validator instance with loaded schema and OS info |
| **Function** | Initializes validator, loads schema, detects OS, prepares validation rules |
| **Dependencies** | `normalize_path()`, `default_base_path()`, `get_schema_path()`, `detect_os()` |

#### Methods

##### `validate()`

| Attribute | Details |
|-----------|---------|
| **Input** | None (uses instance attributes) |
| **Output** | `Dict[str, Any]` - Validation results dictionary |
| **Function** | Runs full project setup validation including folders, files, and environment checks |
| **Returns** | Dictionary with keys: `base_path`, `schema_path`, `os`, `folders`, `root_files`, `schema_files`, `workflow_files`, `tool_files`, `environment`, `errors`, `ready` |
| **Workflow** | 1. Check schema exists<br>2. Run `validate_folders()` if rule enabled<br>3. Run `validate_named_files()` for each category<br>4. Run `validate_environment()`<br>5. Run `check_ready()` |

##### `format_report(results)`

| Attribute | Details |
|-----------|---------|
| **Input** | `results` (Dict): Validation results from `validate()` |
| **Output** | `str` - Formatted report string |
| **Function** | Formats validation results for terminal display |
| **Dependencies** | `core/reports.py:format_report()` |

---

## Validator Functions

### validate_folders(results, folders, base_path, os_info)

**File:** `validators/items.py`

| Attribute | Details |
|-----------|---------|
| **Input** | `results` (Dict): Results accumulator<br>`folders` (Iterable[Dict]): Folder specifications<br>`base_path` (Path): Project root<br>`os_info` (Dict): OS detection results |
| **Output** | Modifies `results['folders']` in-place |
| **Function** | Validates project folders, auto-creates if OS supports it |
| **Workflow** | 1. Iterate folder specs<br>2. Check if exists<br>3. Auto-create if missing & OS supported<br>4. Record validation result |

**Folder Specification:**
```python
{
    "name": "data",           # Folder name
    "required": True,         # Is it required?
    "purpose": "Input data",  # Description
    "auto_created": True      # Can it be auto-created?
}
```

---

### validate_named_files(results, category, items, parent_dir, name_key, description_key)

**File:** `validators/items.py`

| Attribute | Details |
|-----------|---------|
| **Input** | `results` (Dict): Results accumulator<br>`category` (str): Result key (e.g., "root_files")<br>`items` (Iterable[Dict]): File specifications<br>`parent_dir` (Path): Directory to check<br>`name_key` (str): Key for file name in spec<br>`description_key` (str): Key for description in spec |
| **Output** | Modifies `results[category]` in-place |
| **Function** | Validates existence of named files in a category |

**File Specification:**
```python
{
    "name": "config.json",      # File name (or "filename" key)
    "required": True,           # Is it required?
    "purpose": "Config file"    # Description (or "description" key)
}
```

---

### validate_environment(results, environment, base_path)

**File:** `validators/items.py`

| Attribute | Details |
|-----------|---------|
| **Input** | `results` (Dict): Results accumulator<br>`environment` (Iterable[Dict]): Environment file specs<br>`base_path` (Path): Project root |
| **Output** | Modifies `results['environment']` in-place |
| **Function** | Validates environment specification files with location resolution |

**Environment Specification:**
```python
{
    "file": ".env",                    # Filename
    "name": "Environment file",        # Display name
    "location": "root",                # Location relative to base_path
    "required": True,                  # Is it required?
    "setup_commands": [],              # Setup commands for this env
    "key_dependencies": []             # Required API keys
}
```

---

### check_ready(results)

**File:** `validators/items.py`

| Attribute | Details |
|-----------|---------|
| **Input** | `results` (Dict): Complete validation results |
| **Output** | `bool` - True if all required items exist |
| **Function** | Checks if all required items across all categories exist |
| **Workflow** | 1. Check for errors<br>2. Iterate all sections<br>3. Verify required items exist |

---

### record_path_check(results, category, name, path, required, exists, description, item_type)

**File:** `validators/items.py`

| Attribute | Details |
|-----------|---------|
| **Input** | `results` (Dict): Results accumulator<br>`category` (str): Result section key<br>`name` (str): Item name<br>`path` (Path): Item path<br>`required` (bool): Is it required?<br>`exists` (bool): Does it exist?<br>`description` (str): Item description<br>`item_type` (str): "folder" or "file" |
| **Output** | Appends to `results[category]` |
| **Function** | Records a single path validation result |

---

### ensure_folder(path)

**File:** `validators/items.py`

| Attribute | Details |
|-----------|---------|
| **Input** | `path` (Path): Directory path to create |
| **Output** | `bool` - True if directory exists after operation |
| **Function** | Creates directory (and parents) if it doesn't exist |
| **Dependencies** | `path.mkdir(parents=True, exist_ok=True)` |

---

## Utility Functions

### Path Utilities

**File:** `utils/paths.py`

#### get_homedir()

| Attribute | Details |
|-----------|---------|
| **Input** | None (reads from environment) |
| **Output** | `Path` - Validated home directory |
| **Function** | Returns home directory with Windows network drive fallback |
| **Workflow** | 1. Read HOME env var<br>2. On Windows, check if reachable<br>3. Fall back to LOCALAPPDATA if broken<br>4. Final fallback to `Path.home()` |

---

#### normalize_path(value)

| Attribute | Details |
|-----------|---------|
| **Input** | `value` (str/Path): Path to normalize |
| **Output** | `Path` - Absolute path |
| **Function** | Converts path to absolute form |

---

#### default_base_path()

| Attribute | Details |
|-----------|---------|
| **Input** | None (uses file location) |
| **Output** | `Path` - Default project base path |
| **Function** | Determines base path from script location |
| **Workflow** | 1. Search parents for "workflow" directory<br>2. Return parent of "workflow"<br>3. Fallback to script parent directory |

---

#### get_schema_path(base_path)

| Attribute | Details |
|-----------|---------|
| **Input** | `base_path` (Path): Project root |
| **Output** | `Path` - Schema file path |
| **Function** | Returns default schema path: `{base_path}/config/schemas/project_setup.json` |

---

#### resolve_platform_paths(effective_parameters, base_path, status_print_fn)

| Attribute | Details |
|-----------|---------|
| **Input** | `effective_parameters` (dict): Merged parameters<br>`base_path` (Path): Project root<br>`status_print_fn` (callable): Status output function |
| **Output** | `dict` - Updated parameters with resolved paths |
| **Function** | Resolves platform-specific paths with precedence: CLI → Schema → Native defaults |
| **Workflow** | 1. Detect OS platform<br>2. Check platform-specific path keys<br>3. Validate path existence<br>4. Resolve relative paths<br>5. Create download directory |

**Platform Keys:**
- Windows: `win_upload_file`, `win_download_path`
- Linux/Mac: `linux_upload_file`, `linux_download_path`

---

#### resolve_output_paths(base_path, effective_parameters, safe_resolve_fn)

| Attribute | Details |
|-----------|---------|
| **Input** | `base_path` (Path): Project root<br>`effective_parameters` (dict): Output configuration<br>`safe_resolve_fn` (callable, optional): Custom path resolver |
| **Output** | `dict` - Resolved output paths with keys: `output_dir`, `csv_path`, `excel_path`, `summary_path` |
| **Function** | Resolves output file paths for processed data |
| **Workflow** | 1. Check for explicit `output_file`<br>2. Fallback to `download_file_path` + default name<br>3. Generate CSV, Excel, and summary paths |

---

#### validate_export_paths(export_paths, overwrite_existing)

| Attribute | Details |
|-----------|---------|
| **Input** | `export_paths` (dict): Output path dictionary<br>`overwrite_existing` (bool): Allow overwrite? |
| **Output** | None (raises `FileExistsError` if files exist) |
| **Function** | Validates output paths and checks for existing files |
| **Workflow** | 1. Create output directory<br>2. If no overwrite, check file existence<br>3. Raise error if files exist |

---

### CLI Utilities

**File:** `utils/cli.py`

#### create_parser(base_path)

| Attribute | Details |
|-----------|---------|
| **Input** | `base_path` (Path): Default project path |
| **Output** | `argparse.ArgumentParser` |
| **Function** | Creates CLI argument parser with all supported options |

**Supported Arguments:**
- `--base-path`: Project root path
- `--schema-file`: Alternative schema file
- `--excel-file`: Input Excel file
- `--upload-sheet`: Excel sheet name
- `--output-file`: Output CSV path
- `--start-col`, `--end-col`: Column range
- `--header-row`: Header row index
- `--overwrite`: Overwrite output file
- `--debug-mode`: Enable debug output
- `--nrows`: Row limit
- `--json`: Print result as JSON

---

#### parse_cli_args(base_path)

| Attribute | Details |
|-----------|---------|
| **Input** | `base_path` (Path, optional): Default project path |
| **Output** | `Tuple[argparse.Namespace, Dict[str, Any]]` - Parsed args and CLI overrides |
| **Function** | Parses CLI arguments and converts to parameter dictionary |
| **Workflow** | 1. Create parser<br>2. Parse known args<br>3. Map CLI args to parameter keys<br>4. Report overrides |

---

### Logging Utilities

**File:** `utils/logging.py`

#### set_debug_mode(enabled)

| Attribute | Details |
|-----------|---------|
| **Input** | `enabled` (bool): Enable debug mode? |
| **Output** | None (sets global `DEBUG_DEV_MODE`) |
| **Function** | Enables/disables debug print output |

---

#### setup_logger(debug_mode)

| Attribute | Details |
|-----------|---------|
| **Input** | `debug_mode` (bool, default=False): Enable debug logging? |
| **Output** | None (configures global logging) |
| **Function** | Configures Python logging settings |
| **Workflow** | 1. Set log level (DEBUG/INFO)<br>2. Configure format: `%(asctime)s [%(levelname)s] %(message)s`<br>3. Set date format: `%H:%M:%S` |

---

#### status_print(*args, **kwargs)

| Attribute | Details |
|-----------|---------|
| **Input** | `*args`: Message components<br>`**kwargs`: Print options (default: `flush=True`) |
| **Output** | None (prints to stdout) |
| **Function** | Prints status messages with flush enabled |

---

#### debug_print(*args, **kwargs)

| Attribute | Details |
|-----------|---------|
| **Input** | `*args`: Message components<br>`**kwargs`: Print options |
| **Output** | None (prints to stdout only in debug mode) |
| **Function** | Prints debug messages only when `DEBUG_DEV_MODE=True` |

---

### System Utilities

**File:** `utils/system.py`

#### test_environment(base_path)

| Attribute | Details |
|-----------|---------|
| **Input** | `base_path` (Path, optional): Project root |
| **Output** | `Dict[str, Any]` - Environment test results |
| **Function** | Tests Python environment and required libraries |
| **Workflow** | 1. Load project_setup.json<br>2. Extract dependencies<br>3. Test required modules<br>4. Test optional modules<br>5. Test engine modules |

**Returns:**
```python
{
    "python_version": "3.x.x",
    "platform": "Linux/Windows/Darwin",
    "required_modules": {"numpy": "ok", ...},
    "optional_modules": {"pandas": "ok", ...},
    "engine_modules": {"module_name": "ok", ...},
    "errors": [],
    "ready": True/False
}
```

**Dependencies Schema Format:**
```json
{
  "dependencies": {
    "required": ["numpy", "pandas"],
    "optional": ["openpyxl"],
    "engines": [
      {"module": "some_module", "members": ["func1", "Class1"]}
    ]
  }
}
```

---

## System Detection

**File:** `system/os_detect.py`

### detect_os()

| Attribute | Details |
|-----------|---------|
| **Input** | None (uses `platform.system()`) |
| **Output** | `Dict[str, str]` - OS information |
| **Function** | Detects operating system and normalizes name |
| **Returns** | `{"system": "Windows/Linux/Darwin", "normalized": "windows/linux/macos"}` |

---

### should_auto_create_folders(os_info)

| Attribute | Details |
|-----------|---------|
| **Input** | `os_info` (Dict): OS detection results from `detect_os()` |
| **Output** | `bool` - Should folders be auto-created? |
| **Function** | Checks if OS supports automatic folder creation |
| **Logic** | Returns `True` for: windows, linux, macos |

---

## Report Formatting

**File:** `core/reports.py`

### format_report(results)

| Attribute | Details |
|-----------|---------|
| **Input** | `results` (Dict): Validation results from `validate()` |
| **Output** | `str` - Formatted terminal report |
| **Function** | Generates human-readable validation report |

**Report Format:**
```
========================================================================
PROJECT SETUP VALIDATION
========================================================================
Base Path: /path/to/project
Schema Path: /path/to/config/schemas/project_setup.json
Operating System: Linux (linux)

Required Folders:
  [OK] data (required) -> /path/to/project/data
  [MISS] output (optional) -> /path/to/project/output [created]

Root Files:
  [OK] config.json (required) -> /path/to/project/config.json

Summary:
  Ready: YES
```

**Status Codes:**
- `[OK]`: Item exists
- `[MISS]`: Required item missing
- `[WARN]`: Optional item missing

---

## Usage Examples

### Basic Validation

```python
from dcc.workflow.initiation_engine.engine import ProjectSetupValidator

# Create validator with defaults
validator = ProjectSetupValidator()

# Run validation
results = validator.validate()

# Display report
print(validator.format_report(results))

# Check readiness
if results['ready']:
    print("✓ Project is ready!")
else:
    print("✗ Project setup incomplete")
```

---

### Custom Validation

```python
from pathlib import Path
from dcc.workflow.initiation_engine.engine import (
    ProjectSetupValidator,
    validate_folders,
    detect_os,
)

# Custom base path
custom_path = Path("/custom/project/path")
validator = ProjectSetupValidator(base_path=custom_path)

# Access loaded schema
print(validator.project_setup)
print(validator.validation_rules)

# Manual folder validation
results = {'folders': [], 'errors': []}
folders = [
    {'name': 'data', 'required': True, 'purpose': 'Input data'},
    {'name': 'output', 'required': False, 'purpose': 'Output files', 'auto_created': True},
]
os_info = detect_os()

validate_folders(results, folders, custom_path, os_info)
```

---

### CLI Usage

```python
from dcc.workflow.initiation_engine.engine import parse_cli_args

# Parse CLI arguments
args, cli_overrides = parse_cli_args()

# Access parameters
if cli_overrides.get('upload_file_name'):
    print(f"Processing: {cli_overrides['upload_file_name']}")

# Use with argparse namespace
if args.json:
    import json
    print(json.dumps(cli_overrides, indent=2))
```

**CLI Example:**
```bash
python script.py --base-path /my/project --excel-file data.xlsx --debug-mode True --overwrite True
```

---

### Environment Testing

```python
from dcc.workflow.initiation_engine.engine import test_environment

# Test environment
env_results = test_environment()

# Check Python version
print(f"Python: {env_results['python_version']}")
print(f"Platform: {env_results['platform']}")

# Check modules
for module, status in env_results['required_modules'].items():
    print(f"  {module}: {status}")

# Check readiness
if env_results['ready']:
    print("✓ All dependencies satisfied")
else:
    print("✗ Missing dependencies:")
    for error in env_results['errors']:
        print(f"  - {error}")
```

---

## Import Quick Reference

### Full Engine Import
```python
from dcc.workflow.initiation_engine.engine import (
    # Core
    ProjectSetupValidator,
    format_report,
    
    # Validators
    validate_folders,
    validate_named_files,
    validate_environment,
    check_ready,
    record_path_check,
    ensure_folder,
    
    # Path Utils
    normalize_path,
    default_base_path,
    get_schema_path,
    get_homedir,
    resolve_platform_paths,
    resolve_output_paths,
    validate_export_paths,
    
    # CLI Utils
    create_parser,
    parse_cli_args,
    
    # Logging Utils
    status_print,
    debug_print,
    setup_logger,
    set_debug_mode,
    
    # System Utils
    test_environment,
    
    # OS Detection
    detect_os,
    should_auto_create_folders,
)
```

### Module-Specific Imports
```python
# Core only
from dcc.workflow.initiation_engine.engine.core import ProjectSetupValidator, format_report

# Validators only
from dcc.workflow.initiation_engine.engine.validators import validate_folders, check_ready

# Utils only
from dcc.workflow.initiation_engine.engine.utils import (
    normalize_path,
    parse_cli_args,
    status_print,
    test_environment,
)

# System only
from dcc.workflow.initiation_engine.engine.system import detect_os
```

---

## Error Handling

The engine provides comprehensive error handling:

1. **Schema Errors**: Caught during validator initialization
2. **Path Errors**: Handled during path resolution
3. **Validation Errors**: Recorded in results, don't halt execution
4. **Environment Errors**: Logged but don't prevent validation
5. **File Conflicts**: Raised as `FileExistsError` in `validate_export_paths()`

---

## Best Practices

1. **Always check `results['ready']`** before proceeding with workflows
2. **Use `format_report()`** for user-friendly output
3. **Enable debug mode** during development: `set_debug_mode(True)`
4. **Validate export paths** before writing: `validate_export_paths(paths, overwrite=False)`
5. **Test environment** early: `test_environment()` to catch dependency issues

---

## Dependencies

The engine itself has minimal dependencies:
- Python 3.10+ (uses type hints with `|` syntax)
- Standard library only: `pathlib`, `platform`, `argparse`, `logging`, `json`, `importlib`

Project-specific dependencies are defined in `project_setup.json` and tested via `test_environment()`.
