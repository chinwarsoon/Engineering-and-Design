# Schema Validation Guide

## Purpose

`schema_validation.py` validates the main DCC schema and its referenced schema JSON files.

Its job is to:

- confirm the main schema file exists and is valid JSON
- confirm referenced schema files exist and are valid JSON
- walk nested `schema_references` across schema files
- detect circular dependencies across schema JSON files
- report whether schema validation is ready to proceed

This script runs after `project_setup_validation.py`.

---

## Script Location

- `dcc/workflow/schema_validation.py`

Default main schema:

- `dcc/config/schemas/dcc_register_enhanced.json`

---

## What It Validates

`schema_validation.py` checks:

- the main schema file
- first-level schema references
- nested schema references inside referenced schema files
- circular dependency paths such as:

```text
dcc_register_enhanced.json -> schema_a.json -> schema_b.json -> schema_a.json
```

---

## Main Classes

### `SchemaLoader`

Shared loader for:

- loading JSON schema files
- resolving relative reference paths
- resolving nested schema dependencies

### `SchemaValidator`

Validator for:

- main schema structure
- schema reference existence
- JSON parse validity
- circular dependency detection

---

## Validation Output

The validator returns a dictionary like:

```json
{
  "main_schema_path": "/path/to/dcc_register_enhanced.json",
  "references": [],
  "dependency_cycle": [],
  "errors": [],
  "ready": true
}
```

Important fields:

- `references`
  Each discovered schema reference with resolved path and existence status
- `dependency_cycle`
  A cycle path if a circular dependency is found
- `errors`
  Validation failures such as missing files, invalid JSON, or cycles
- `ready`
  Final pass/fail result

---

## Command Line Usage

Run with text output:

```bash
python dcc/workflow/schema_validation.py
```

Run with JSON output:

```bash
python dcc/workflow/schema_validation.py --json
```

Run against a custom schema file:

```bash
python dcc/workflow/schema_validation.py --schema-file /path/to/schema.json
```

---

## Recommended Pipeline

1. run `python dcc/workflow/project_setup_validation.py`
2. confirm the project structure is ready
3. run `python dcc/workflow/schema_validation.py`
4. confirm schema validation is ready
5. continue to column mapping and document processing

---

## Summary

`schema_validation.py` is the schema gatekeeper for the DCC workflow.

It validates referenced schema files, walks nested schema dependencies, detects circular references across schema JSON files, and provides a terminal-friendly or JSON result for the next processing step.
