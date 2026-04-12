# Project Setup Validation Guide

## Purpose

`project_setup_validation.py` is the project structure checker for the DCC workspace.

Its job is to:

- confirm the required project folders exist
- confirm required root files, schema files, workflow files, tool files, and environment files exist
- detect the operating system explicitly
- automatically create missing folders defined in `project_setup.json`
- report whether the project is ready for use

This script is intended as the main folder and file setup validator for the DCC project.

---

## Script Location

File:

- `dcc/workflow/project_setup_validation.py`

Schema used by default:

- `dcc/config/schemas/project_setup.json`

Schema validation is handled separately by:

- `dcc/workflow/schema_validation.py`

This means:

- `project_setup_validation.py` checks project structure only
- `schema_validation.py` checks schema structure and schema references after setup validation

---

## How Root Path Is Determined

The validator does not depend on the terminal's current working directory.

By default, it uses the parent folder of the `workflow` directory where the script is stored.

Example:

- script path: `dcc/workflow/project_setup_validation.py`
- workflow folder: `dcc/workflow`
- detected base path: `dcc`

This means the validator will treat `dcc/` as the project root when no `--base-path` is provided.

---

## Main Class

## `ProjectSetupValidator`

This class loads the setup schema, applies validation rules, and returns a structured result.

### Constructor

```python
ProjectSetupValidator(base_path=None, schema_path=None)
```

### Inputs

- `base_path`
  Project root to validate. If omitted, the script uses the parent of its own `workflow` folder.
- `schema_path`
  Optional override for the setup schema JSON file. If omitted, the default is:
  `base_path / "config" / "schemas" / "project_setup.json"`

### Internal Data Loaded

- `schema_document`
  Full JSON content of `project_setup.json`
- `project_setup`
  The first object inside the `project_setup` list in the schema
- `validation_rules`
  Rule toggles loaded from `project_setup.json`
- `os_info`
  Detected operating system details

---

## Key Functions

### `_default_base_path()`

Determines the project root automatically.

Behavior:

- gets the directory of `project_setup_validation.py`
- if that directory is `workflow`, it uses the parent folder as root
- otherwise it uses the script directory itself

### `_detect_os()`

Detects the current operating system.

Returned format:

```python
{
  "system": "Linux",
  "normalized": "linux"
}
```

Known normalized values:

- `windows`
- `linux`
- `macos`

### `_validate_folders(results)`

Checks all folders listed in `project_setup.json`.

Behavior:

- builds each folder path relative to the detected project root
- checks whether the folder exists
- if missing and the OS is supported, automatically creates the folder
- records whether the folder existed already or was created during validation

Folder output fields:

- `name`
- `path`
- `required`
- `exists`
- `description`
- `item_type`
- `auto_created`
- `schema_auto_created`

### `_validate_named_files(...)`

Checks file existence for:

- root files
- schema files
- workflow files
- tool files

### `_validate_environment(results)`

Checks environment specification files defined in the schema.

It also includes:

- `setup_commands`
- `key_dependencies`

### `validate()`

Runs the full validation workflow and returns a structured result dictionary.

### `format_report(results)`

Converts the validation result into a readable text report for terminal output.

---

## Validation Flow

When `validate()` runs, the script performs these steps:

1. confirm `project_setup.json` exists
2. load the `project_setup` configuration
3. validate folders
4. validate files
5. validate environment files
6. determine final readiness status

If required items are missing, readiness becomes `False`.

---

## Inputs From `project_setup.json`

The validator reads these main sections from the schema:

- `folders`
- `root_files`
- `schema_files`
- `workflow_files`
- `tool_files`
- `environment`
- `validation_rules`

Important workflow file note:

- `workflow_files` now includes `schema_validation.py` as a required workflow module
- this script checks that `schema_validation.py` exists, but it does not run it

Example folder entry:

```json
{
  "name": "output",
  "required": false,
  "purpose": "Generated output",
  "auto_created": true
}
```

Important note:

- the current validator records `auto_created` from runtime behavior
- it also records `schema_auto_created` from the schema definition
- missing folders are currently auto-created on supported operating systems during validation

---

## Outputs

The `validate()` function returns a dictionary like this:

```json
{
  "base_path": "/path/to/dcc",
  "schema_path": "/path/to/dcc/config/schemas/project_setup.json",
  "os": {
    "system": "Linux",
    "normalized": "linux"
  },
  "folders": [],
  "root_files": [],
  "schema_files": [],
  "workflow_files": [],
  "tool_files": [],
  "environment": [],
  "errors": [],
  "ready": true
}
```

### Important Output Fields

- `base_path`
  Root folder being validated
- `schema_path`
  Path to the setup schema file
- `os`
  Detected operating system
- `errors`
  High-level blocking problems such as missing schema file
- `ready`
  Final yes/no project readiness result

---

## Command Line Usage

This script performs project setup validation only.

For schema validation, run the separate schema-validation pipeline after setup validation.

Recommended sequence:

1. run `python dcc/workflow/project_setup_validation.py`
2. confirm the setup report is ready
3. run `schema_validation.py` as the next pipeline step

Run text report:

```bash
python dcc/workflow/project_setup_validation.py
```

Run JSON output:

```bash
python dcc/workflow/project_setup_validation.py --json
```

Validate a custom root path:

```bash
python dcc/workflow/project_setup_validation.py --base-path /path/to/project
```

Validate using a custom schema:

```bash
python dcc/workflow/project_setup_validation.py --schema-path /path/to/project_setup.json
```

---

## Command Line Arguments

### `--base-path`

Overrides the automatically detected project root.

Use this when:

- validating another DCC project copy
- testing a temporary project directory
- checking a packaged distribution

### `--schema-path`

Overrides the default schema location.

Use this when:

- testing a modified setup schema
- validating against an alternative configuration

### `--json`

Prints structured JSON instead of a human-readable text report.

Use this when:

- integrating with automation
- calling the script from another tool
- debugging exact result fields

---

## Readiness Rules

The project is considered ready only when:

- there are no top-level validation errors
- all required folders exist
- all required files exist
- all required environment files exist

If any required item is missing, `ready` becomes `False`.

---

## Auto-Creation Behavior

The validator now includes automatic folder creation.

Current behavior:

- supported OS values: `windows`, `linux`, `macos`
- when a folder listed in `project_setup.json` is missing, the validator creates it
- the folder result includes `auto_created: true` if it was created during validation

This helps make first-time setup smoother, especially for optional output or data folders.

---

## Example Use Cases

### First-time project setup check

Use the validator to confirm a fresh project copy contains the required structure.

### Packaging or deployment validation

Run the validator before sharing the project with another user or machine.

### Automated checks

Use `--json` in scripts or CI pipelines to inspect the `ready` field programmatically.

### Pre-schema-validation gate

Use this script before running `schema_validation.py` so the required project folders and files are confirmed first.

### Troubleshooting missing files

Use the text report to quickly see which folder or file is missing and where it should be located.

---

## What This Script Does Not Do

This script does not:

- validate the actual contents of Excel data files
- process DCC document data
- reorder schema columns
- analyze workflow business logic

Those responsibilities belong to other workflow or tool scripts.

---

## Recommended User Workflow

1. run `project_setup_validation.py`
2. review the folder and file report
3. confirm `ready` is `YES` or `true`
4. if needed, fix missing required files
5. rerun validation before processing project data

---

## Summary

`project_setup_validation.py` is the DCC setup gatekeeper.

It defines the project root correctly, reads `project_setup.json`, checks the expected project structure, confirms required workflow files such as `schema_validation.py` exist, creates missing folders when possible, and tells the user whether the project is ready for the next pipeline step.
