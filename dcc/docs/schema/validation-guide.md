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

| Component | Path | Link |
|:---|:---|:---|
| Schema Validator | `workflow/schema_engine/validator/schema_validator.py` | [`SchemaValidator`](../../workflow/schema_engine/validator/schema_validator.py) |
| Schema Loader | `workflow/schema_engine/loader/schema_loader.py` | [`SchemaLoader`](../../workflow/schema_engine/loader/schema_loader.py) |
| Error Handling | `workflow/core_engine/error_handling.py` | [`validate_schema_ready()`](../../workflow/core_engine/error_handling.py) |
| Legacy Validator | `workflow/schema_validation.py` | [`schema_validation.py`](../../workflow/schema_validation.py) |

### Default Main Schema

- `config/schemas/dcc_register_config.json` [`[link]`](../../config/schemas/dcc_register_config.json)

---

## What It Validates

`schema_validation.py` checks:

- the main schema file
- first-level schema references
- nested schema references inside referenced schema files
- circular dependency paths such as:

```text
dcc_register_config.json -> schema_a.json -> schema_b.json -> schema_a.json
```

---

## Validation Callers

| Caller | Location | Function | Purpose | Schema File Validated |
|:---|:---|:---|:---|:---|
| Pipeline Step 2 | [`dcc_engine_pipeline.py:192`](../../workflow/dcc_engine_pipeline.py:192) | `SchemaValidator.validate()` | Validates schema structure and references before processing | `dcc_register_config.json` |
| Pipeline Step 2 | [`dcc_engine_pipeline.py:204`](../../workflow/dcc_engine_pipeline.py:204) | `load_resolved_schema()` | Loads resolved schema after validation passes | `dcc_register_config.json` + fragment schemas |
| Bootstrap Phase 7 | [`bootstrap.py:851`](../../workflow/utility_engine/bootstrap.py:851) | `_bootstrap_schema()` | Validates schema file path exists (not content) | `dcc_register_config.json` |
| Error Handler | [`error_handling.py:303`](../../workflow/core_engine/error_handling.py:303) | `validate_schema_ready()` | Checks validation results and records errors if failed | Validation results dict |

**Note:** Bootstrap Phase 7 validates that the schema file path exists and is accessible, but does not validate the schema content. Full schema validation (structure, references, circular dependencies) occurs in Pipeline Step 2 via `SchemaValidator.validate()`.

## Main Classes

### `SchemaLoader` ([`schema_loader.py`](../../workflow/schema_engine/loader/schema_loader.py))

Shared loader for:

- loading JSON schema files
- resolving relative reference paths
- resolving nested schema dependencies via `RefResolver`
- managing `SchemaCache` (L1/L2/L3 caching)
- detecting circular dependencies via `SchemaDependencyGraph`

### `SchemaValidator` ([`schema_validator.py`](../../workflow/schema_engine/validator/schema_validator.py))

Validator for:

- main schema structure (top-level `columns` or legacy `enhanced_schema`)
- schema reference existence via URI `$ref` or legacy `schema_references` dict
- JSON parse validity
- circular dependency detection
- column count validation

---

## Validation Return

### Return Structure

The validator returns a dictionary:

```json
{
  "main_schema_path": "/path/to/dcc_register_config.json",
  "column_count": 48,
  "references": [
    {
      "reference": "department_schema",
      "configured_path": "department_schema.json",
      "source_path": "/path/to/dcc_register_config.json",
      "resolved_path": "/path/to/department_schema.json",
      "exists": true
    }
  ],
  "dependency_cycle": [],
  "errors": [],
  "ready": true
}
```

### Field Descriptions

| Field | Type | Description |
|:---|:---:|:---|
| `main_schema_path` | string | Absolute path to the main schema file being validated |
| `column_count` | int | Number of columns found in schema (from `columns` object) |
| `references` | array | List of reference objects (see below) |
| `dependency_cycle` | array | Circular dependency path if detected, empty otherwise |
| `errors` | array | List of error message strings |
| `ready` | bool | Final validation status - `true` if no errors |

### Reference Object Structure

| Field | Type | Description |
|:---|:---:|:---|
| `reference` | string | Reference name (e.g., `"department_schema"`) |
| `configured_path` | string | Path as configured in the schema file |
| `source_path` | string | Path to the file containing this reference |
| `resolved_path` | string | Fully resolved absolute path |
| `exists` | bool | Whether the referenced file exists |
| `error` | string | Error message if reference failed (optional) |

## Error Handling

### Error Types and Codes

| Error Type | Error Code | Severity | Description | Handler |
|:---|:---|:---:|:---|:---|
| Main schema not found | `S-F-S-0204` | critical | Schema file doesn't exist | `context.add_system_error()` |
| Invalid JSON in main schema | `S-C-S-0302` | critical | JSON parse error in main file | `context.capture_exception()` |
| Missing 'columns' object | `S-C-S-0301` | critical | Schema structure invalid (no columns key) | `context.add_system_error()` |
| Schema validation failed | `S-C-S-0303` | critical | Generic validation failure | `validate_schema_ready()` |
| Circular dependency | `S-C-S-0304` | critical | Circular `$ref` detected | `context.add_system_error()` |
| Reference file not found | — | error | Referenced schema missing | Recorded in reference object |
| Invalid JSON in reference | — | error | Reference file corrupt | Recorded in reference object |

### Error Recording

Errors are recorded in the `PipelineContext` via:

```python
# For system errors (file not found, invalid JSON, etc.)
context.add_system_error(
    code="S-C-S-0301",
    message="Main schema is missing a valid 'columns' object",
    details=str(schema_file),
    engine="schema_engine",
    phase="schema_validation",
    severity="critical",
    fatal=True
)

# For exceptions during loading
context.capture_exception(
    code="S-C-S-0302",
    exception=exc,
    engine="schema_engine",
    phase="schema_validation"
)
```

### Fail-Fast Behavior

The pipeline uses fail-fast mode to stop on critical errors:

```python
if not validate_schema_ready(context, schema_results, engine="schema_engine"):
    if context.should_fail_fast("system"):
        raise ValueError(json.dumps(schema_results, indent=2))
```

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

## Status Tracking

### Pipeline State

Validation status is tracked at multiple levels:

| Location | Variable | Values |
|:---|:---|:---|
| Context State | `context.state.schema_results` | Full validation results dict |
| Engine Status | `context.state.engine_status["schema_engine"]` | `"running"` → `"completed"` or `"failed"` |
| Persistence | `validation_status.json` | Written by `write_validation_status()` |

### Status Persistence

The `write_validation_status()` function persists results:

```python
from schema_engine import write_validation_status
write_validation_status(schema_results)
# Writes to: <base_path>/output/validation_status.json
```

### Status Check Helper

```python
from core_engine.error_handling import validate_schema_ready

is_ready = validate_schema_ready(
    context=context,
    schema_results=schema_results,
    engine="schema_engine",
    phase="step2_schema_validation"
)
# Returns: True if ready, False if errors recorded
# Side effect: Records error in context if not ready
```

## Dual Architecture Support

The validator supports both new and legacy schema architectures:

| Architecture | Detection | Resolution Method | Fragment Loading |
|:---|:---|:---|:---|
| **New (V2)** | Top-level `"columns"` key present | `_load_resolved_schema_v2()` | URI `$ref` via `RefResolver` |
| **Legacy** | No `"columns"`, uses `schema_references` dict | `resolve_schema_dependencies()` | Manual dict resolution |

### URI Stem Mapping (V2)

Fragment schemas are resolved via URI mapping:

```python
uri_stem_map = {
    "department_schema": "department_schema.json",
    "discipline_schema": "discipline_schema.json",
    "facility_schema": "facility_schema.json",
    "document_type_schema": "document_type_schema.json",
    "project_code_schema": "project_code_schema.json",
    "approval_code_schema": "approval_code_schema.json",
    "global_parameters": "global_parameters.json",  # ⚠️ See Issues
}
```

## Known Issues and Pending Actions

### Issue 1: URI Stem Map References Deprecated File

**Problem:** `uri_stem_map` references `"global_parameters"` which maps to `global_parameters.json` (archived).

**Current:**
```python
"global_parameters": "global_parameters.json",  # File archived
```

**Should be:**
```python
"dcc_global_parameters": "dcc_global_parameters.json",  # Current file
```

**Action Required:** Update [`schema_validator.py:260`](../../workflow/schema_engine/validator/schema_validator.py:260) to use new filename.

**Priority:** High

### Issue 2: Legacy Schema Support

**Problem:** Legacy `schema_references` dict pattern still supported but deprecated.

**Action:** All schemas should migrate to URI `$ref` pattern per `agent_rule.md` Section 2.

**Status:** Migration complete for `dcc_register_config.json`. Remove legacy support in future release.

### Issue 3: Schema Validation Guide Outdated References

**Problem:** Guide referenced deleted `dcc_register_enhanced.json`.

**Status:** ✅ Fixed - Updated to `dcc_register_config.json`.

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
