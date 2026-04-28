# Error Handling Taxonomy

**Complete Reference for All DCC Error Codes**  
**Version:** 2.0  
**Date:** 2026-04-24  
**Total Codes:** 37 (20 System + 17 Data/Logic)

---

## Table of Contents

1. [System Errors](#system-errors-s-c-s-xxxx)
2. [Data/Logic Errors](#datalogic-errors-ll-m-f-xxxx)
3. [Code Format Specification](#code-format-specification)
4. [Layer/Phase Codes](#layerphase-codes)
5. [Module Codes](#module-codes)
6. [Function Codes](#function-codes)
7. [Migration Table](#migration-table)

---

## System Errors (S-C-S-XXXX)

**Format:** `S-C-S-XXXX`  
**Namespace:** S (System)  
**Description:** Pipeline execution errors that cause immediate hard stop

### Environment Errors (S-E-S-01xx)

| Code | Name | Severity | Stops Pipeline | Path/File/Function | Description |
|------|------|----------|----------------|--------------------|-------------|
| S-E-S-0101 | MISSING_PACKAGE | FATAL | Yes | `initiation_engine/environment_checker.py::check_packages()` | Required Python package not installed |
| S-E-S-0102 | WRONG_PYTHON_VERSION | FATAL | Yes | `initiation_engine/environment_checker.py::check_python_version()` | Python version does not meet requirements |
| S-E-S-0103 | ENV_TEST_FAILED | FATAL | Yes | `initiation_engine/environment_checker.py::run_validation_tests()` | Environment validation test failed |
| S-E-S-0104 | IMPORT_ERROR | FATAL | Yes | `initiation_engine/error_handling/system_error_handler.py::import_guard()` | Failed to import required module |

### File/IO Errors (S-F-S-02xx)

| Code | Name | Severity | Stops Pipeline | Path/File/Function | Description |
|------|------|----------|----------------|--------------------|-------------|
| S-F-S-0201 | INPUT_FILE_NOT_FOUND | FATAL | Yes | `initiation_engine/file_handler.py::validate_input_file()` | Input file not found at path |
| S-F-S-0202 | INPUT_FILE_UNREADABLE | FATAL | Yes | `initiation_engine/file_handler.py::read_input_file()` | Input file exists but cannot be read |
| S-F-S-0203 | OUTPUT_DIR_NOT_WRITABLE | FATAL | Yes | `initiation_engine/file_handler.py::validate_output_dir()` | Output directory not writable |
| S-F-S-0204 | SCHEMA_FILE_NOT_FOUND | FATAL | Yes | `initiation_engine/schema_loader.py::load_schema()` | Schema configuration file not found |
| S-F-S-0205 | CONFIG_FILE_NOT_FOUND | FATAL | Yes | `initiation_engine/config_loader.py::load_config()` | Configuration file not found |

### Configuration Errors (S-C-S-03xx)

| Code | Name | Severity | Stops Pipeline | Path/File/Function | Description |
|------|------|----------|----------------|--------------------|-------------|
| S-C-S-0301 | INVALID_PARAMETER | FATAL | Yes | `initiation_engine/pipeline_initiator.py::validate_parameters()` | Invalid parameter provided to pipeline |
| S-C-S-0302 | SCHEMA_PARSE_ERROR | FATAL | Yes | `initiation_engine/schema_loader.py::parse_schema_json()` | Failed to parse schema JSON |
| S-C-S-0303 | SCHEMA_VALIDATION_FAILED | FATAL | Yes | `initiation_engine/schema_validator.py::validate_against_schema()` | Schema validation failed |
| S-C-S-0304 | MISSING_REQUIRED_CONFIG | FATAL | Yes | `initiation_engine/config_loader.py::validate_required()` | Required configuration missing |
| S-C-S-0305 | PROJECT_SETUP_FAILED | FATAL | Yes | `initiation_engine/project_setup.py::validate_setup()` | Project setup validation failed |

### Runtime Errors (S-R-S-04xx)

| Code | Name | Severity | Stops Pipeline | Path/File/Function | Description |
|------|------|----------|----------------|--------------------|-------------|
| S-R-S-0401 | STEP_EXCEPTION_INIT | FATAL | Yes | `initiation_engine/pipeline_initiator.py::initiate()` | Exception during initiation step |
| S-R-S-0402 | FAIL_FAST_TRIGGERED | FATAL | Yes | `processor_engine/core/pipeline.py::fail_fast_check()` | Fail-fast condition triggered |
| S-R-S-0403 | MEMORY_ERROR | FATAL | Yes | `processor_engine/core/memory_manager.py::allocate()` | Memory allocation failed |
| S-R-S-0404 | STEP_EXCEPTION_SCHEMA | FATAL | Yes | `processor_engine/validators/schema_validator.py::validate()` | Exception during schema validation |
| S-R-S-0405 | STEP_EXCEPTION_MAPPING | FATAL | Yes | `processor_engine/mappers/column_mapper.py::apply_mapping()` | Exception during column mapping |
| S-R-S-0406 | STEP_EXCEPTION_PROC | FATAL | Yes | `processor_engine/engine.py::apply_processing()` | Exception during processing |

### AI/Optional Errors (S-A-S-05xx)

| Code | Name | Severity | Stops Pipeline | Path/File/Function | Description |
|------|------|----------|----------------|--------------------|-------------|
| S-A-S-0501 | AI_OPS_FAILED | WARNING | No | `processor_engine/ai/ai_operations.py::execute()` | AI operations failed to complete |
| S-A-S-0502 | DUCKDB_UNAVAILABLE | WARNING | No | `processor_engine/ai/duckdb_connector.py::connect()` | DuckDB not available for AI operations |
| S-A-S-0503 | OLLAMA_UNAVAILABLE | WARNING | No | `processor_engine/ai/ollama_client.py::check_availability()` | Ollama service not available |

---

## Data/Logic Errors (LL-M-F-XXXX)

**Format:** `LL-M-F-XXXX`  
**Description:** Data validation and logic sequence errors

### Phase 1 - Anchor (P1-A-P-01xx)

| Code | Name | Severity | Column(s) | Path/File/Function | Description |
|------|------|----------|-----------|--------------------|-------------|
| P1-A-P-0101 | ANCHOR_COLUMN_NULL | CRITICAL | Project_Code, Facility_Code, Document_Type, Discipline | `processor_engine/validators/row_validator.py::detect_anchor_errors()` | Anchor column is null or empty |

### Phase 2 - Identity (P2-I-V-02xx)

| Code | Name | Severity | Column(s) | Path/File/Function | Description |
|------|------|----------|-----------|--------------------|-------------|
| P2-I-V-0201 | DOCUMENT_ID_UNCERTAIN | CRITICAL | Document_ID | `processor_engine/validators/row_validator.py::detect_identity_errors()` | Document_ID could not be resolved |
| P2-I-V-0202 | REVISION_MISSING | CRITICAL | Document_Revision | `processor_engine/validators/row_validator.py::detect_identity_errors()` | No Revision found for this row |
| P2-I-V-0203 | DUPLICATE_TRANSMITTAL | HIGH | Document_ID, Submission_Session | `processor_engine/validators/row_validator.py::detect_identity_errors()` | Multiple identical Document IDs in same session |
| P2-I-V-0204 | DOCUMENT_ID_INVALID | HIGH | Document_ID | `processor_engine/validators/row_validator.py::detect_identity_errors()` | Document_ID has invalid format or composite mismatch |

### Layer 3 - Logic (L3-L-V-03xx)

| Code | Name | Severity | Column(s) | Health Impact | Path/File/Function | Description |
|------|------|----------|-----------|---------------|--------------------|-------------|
| L3-L-P-0301 | DATE_INVERSION | HIGH | Review_Return_Actual_Date, Submission_Date | -15 | `processor_engine/validators/row_validator.py::detect_logic_errors()` | Review_Return_Actual_Date before Submission_Date |
| L3-L-V-0302 | CLOSED_WITH_PLAN_DATE | HIGH | Submission_Closed, Resubmission_Plan_Date | -10 | `processor_engine/validators/row_validator.py::detect_logic_errors()` | Submission_Closed=YES but Resubmission_Plan_Date is set |
| L3-L-V-0303 | RESUBMISSION_MISMATCH | MEDIUM | Review_Status, Resubmission_Required | -10 | `processor_engine/validators/row_validator.py::detect_logic_errors()` | REJ status without Resubmission_Required=YES/RESUBMITTED |
| L3-L-V-0304 | OVERDUE_MISMATCH | MEDIUM | Resubmission_Plan_Date, Resubmission_Overdue_Status | -5 | `processor_engine/validators/row_validator.py::detect_logic_errors()` | Past plan date but status not overdue/resubmitted |
| L3-L-V-0305 | VERSION_REGRESSION | HIGH | Document_Revision | -15 | `processor_engine/validators/row_validator.py::detect_logic_errors()` | Current revision older than previous for same Document_ID |
| L3-L-V-0306 | REVISION_GAP | MEDIUM | Submission_Session, Document_Revision | -5 | `processor_engine/validators/row_validator.py::detect_logic_errors()` | Revision gap in Submission_Session sequence |
| L3-L-V-0307 | CLOSED_WITH_RESUBMISSION | HIGH | Submission_Closed, Resubmission_Required | -10 | `processor_engine/validators/row_validator.py::detect_logic_errors()` | Submission_Closed=YES but Resubmission_Required=YES (should be NO) |

### Validation - Schema (V5-I-V-05xx)

| Code | Name | Severity | Path/File/Function | Description |
|------|------|----------|--------------------|-------------|
| V5-I-V-0501 | PATTERN_MISMATCH | HIGH | `processor_engine/validators/schema_validator.py::validate_pattern()` | Field value does not match expected pattern |
| V5-I-V-0502 | LENGTH_VIOLATION | HIGH | `processor_engine/validators/schema_validator.py::validate_length()` | Field value length violates min/max constraints |
| V5-I-V-0503 | INVALID_ENUM_VALUE | HIGH | `processor_engine/validators/schema_validator.py::validate_enum()` | Field value is not in allowed values list |
| V5-I-V-0504 | TYPE_MISMATCH | HIGH | `processor_engine/validators/schema_validator.py::validate_type()` | Field value type does not match expected type |

### System Input - File (S1-I-F-08xx)

| Code | Name | Severity | Path/File/Function | Description |
|------|------|----------|--------------------|-------------|
| S1-I-F-0804 | FILE_NOT_FOUND | CRITICAL | `initiation_engine/file_handler.py::validate_input_file()` | Input file not found |
| S1-I-F-0805 | FILE_FORMAT_INVALID | CRITICAL | `initiation_engine/file_handler.py::validate_file_format()` | Unsupported file format or file too large |

### System Input - Validation (S1-I-V-05xx)

| Code | Name | Severity | Path/File/Function | Description |
|------|------|----------|--------------------|-------------|
| S1-I-V-0501 | ENCODING_ERROR | HIGH | `initiation_engine/file_handler.py::detect_encoding()` | File encoding error (expected UTF-8) |
| S1-I-V-0502 | MISSING_REQUIRED_COLUMNS | CRITICAL | `initiation_engine/validators/column_validator.py::validate_required()` | Required columns are missing from input |

---

## Code Format Specification

### LL-M-F-XXXX Format (Data/Logic Errors)

| Position | Component | Description | Values |
|----------|-----------|-------------|--------|
| 1-2 | Layer (LL) | Processing phase/layer | P1, P2, L3, V5, S1 |
| 4 | Module (M) | Module within layer | A, I, L, F, V |
| 6 | Function (F) | Function type | P, V, C, F, S |
| 8-11 | ID (XXXX) | Unique sequential number | 0001-9999 |

**Pattern:** `^[A-Z0-9]{2}-[A-Z]-[A-Z]-[0-9]{4}$`

### S-C-S-XXXX Format (System Errors)

| Position | Component | Description | Values |
|----------|-----------|-------------|--------|
| 1 | System (S) | System namespace | S |
| 3 | Category (C) | Error category | E, F, C, R, A |
| 5 | System (S) | System identifier | S |
| 7-10 | ID (XXXX) | Unique sequential number | 0001-9999 |

**Pattern:** `^S-[A-Z]-S-[0-9]{4}$`

---

## Layer/Phase Codes

| Code | Name | Description |
|------|------|-------------|
| P1 | Phase 1 | Input/Anchor processing phase |
| P2 | Phase 2 | Identity/Transaction validation phase |
| L3 | Layer 3 | Logic/Temporal validation layer |
| V5 | Validation 5 | Schema validation layer |
| S1 | System Input | Input/Initialization layer |

## Module Codes

| Code | Name | Description |
|------|------|-------------|
| A | Anchor | Anchor column processing |
| I | Identity/Input | Identity validation, input handling |
| L | Logic | Logic/temporal validation |
| F | File | File operations |
| V | Validation | Schema validation |

## Function Codes

| Code | Name | Description |
|------|------|-------------|
| P | Process | Main processing function |
| V | Validate | Validation function |
| C | Calculate | Calculation function |
| F | Fill | Fill/default handling |
| S | System | System-level function |

---

## Migration Table

### String Codes → Standardized Codes (Phase 2)

| Old String Code | New Standard Code | Migration Date | Status |
|-----------------|-------------------|----------------|--------|
| CLOSED_WITH_PLAN_DATE | L3-L-V-0302 | 2026-04-24 | ✅ Complete |
| RESUBMISSION_MISMATCH | L3-L-V-0303 | 2026-04-24 | ✅ Complete |
| OVERDUE_MISMATCH | L3-L-V-0304 | 2026-04-24 | ✅ Complete |
| VERSION_REGRESSION | L3-L-V-0305 | 2026-04-24 | ✅ Complete |
| REVISION_GAP | L3-L-V-0306 | 2026-04-24 | ✅ Complete |

**Backward Compatibility:** Old string codes retained in `error_key` field for reference.

---

## Health Score Weights

### Current Weights (ROW_ERROR_WEIGHTS)

| Error Code/Key | Weight | Description |
|----------------|--------|-------------|
| ANCHOR_NULL | 25 | Critical anchor column missing |
| COMPOSITE_MISMATCH | 20 | Document_ID composite mismatch |
| GROUP_INCONSISTENT | 15 | Submission_Date inconsistent within session |
| L3-L-V-0305 | 15 | Version regression |
| INCONSISTENT_CLOSURE | 10 | Closure status conflict |
| L3-L-V-0302 | 10 | Closed with plan date |
| L3-L-V-0307 | 10 | Closed with resubmission (NEW) |
| INCONSISTENT_SUBJECT | 5 | Subject inconsistent within session |
| L3-L-V-0304 | 5 | Overdue mismatch |
| L3-L-V-0306 | 5 | Revision gap |

---

## Message Locations

| Language | File | Count |
|----------|------|-------|
| English | `messages/en.json` | 17 codes |
| Chinese | `messages/zh.json` | 17 codes |

---

## File Locations

### Schema Files
```
dcc/config/schemas/
├── error_code_base.json      (definitions)
├── error_code_setup.json     (properties)
├── system_error_config.json  (20 system codes)
└── data_error_config.json    (17 data/logic codes)
```

### Implementation Files
```
dcc/workflow/processor_engine/error_handling/
├── detectors/row_validator.py
└── config/messages/
    ├── en.json
    └── zh.json
```

### Archived Files
```
dcc/archive/workflow/
├── processor_engine/error_handling/config/error_codes.json
└── initiation_engine/error_handling/config/system_error_codes.json
```

---

## Related Documentation

- [README](README.md) - Master documentation index
- [Consolidated Implementation Report](error_catalog_consolidation/reports/consolidated_implementation_report.md) - All phases summary
- [Error Catalog Consolidation Workplan](error_catalog_consolidation/error_catalog_consolidation_plan.md) - Master workplan
- [Data Error Handling Workplan](data_error_handling/data_error_handling_workplan.md) - Implementation guide

---

**Maintained by:** Engineering Team  
**Last Updated:** 2026-04-25 (Added Path/File/Function column to all error code tables)  
**Issue Reference:** #62
