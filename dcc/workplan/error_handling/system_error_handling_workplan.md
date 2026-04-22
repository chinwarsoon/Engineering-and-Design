# System Error Handling Workplan

**Version:** 1.1
**Date:** 2026-05-01
**Status:** COMPLETE
**Depends on:** `error_handling_module_workplan.md`, `pipeline_messaging_plan.md`
**Related Issues:** `dcc/Log/issue_log.md` — Issue #55, Issue #56
**Completion Report:** `reports/system_error_handling_completion_report.md`

---

## 1. Objective

Implement system-level error handling for the DCC pipeline. Distinct from data error handling (which detects quality issues in processed data) — system errors are failures in the pipeline's own execution: environment problems, missing files, bad configuration, unexpected exceptions, and silent stops.

**Core principle:** Any system error that stops the pipeline must be visible to the user with a clear error code, description, and troubleshooting hint — regardless of verbose level.

---

## 2. Scope

| In scope | Out of scope |
|----------|-------------|
| Unhandled exceptions in `main()` and `run_engine_pipeline()` | Data quality errors (covered by `error_handling_module_workplan.md`) |
| Silent stops with no output (Issue #55) | Row-level validation errors |
| Environment / dependency failures | Schema content validation |
| File not found / unreadable | Business logic errors |
| Invalid parameters / configuration | AI ops engine internals |
| Step-level failures with no user message | |
| Integration with `pipeline_messaging_plan.md` level system | |

---

## 3. Alignment with Existing Architecture

| Aspect | Data Error Handling | System Error Handling |
|--------|--------------------|-----------------------|
| Error codes | `E-M-F-XXXX` (e.g. `P-C-P-0101`) | `S-C-X-XXXX` |
| Severity levels | CRITICAL / HIGH / MEDIUM / LOW | FATAL / WARNING |
| Definitions file | `error_codes.json` | `system_error_codes.json` (new) |
| User instructions | `messages/en.json` | `messages/system_en.json` (new) |
| Logging | `StructuredLogger` | `system_error_print()` — always visible, no logger dependency |
| Pipeline behaviour | Collect per row, continue | Hard stop immediately (all levels) |
| Messaging integration | `milestone_print()` / `status_print()` | `system_error_print()` (new) |

**Key differences from data errors:**
- System errors **always print** — bypass verbose level gate entirely
- System errors are a **hard stop** — no suppression, no remediation, no row-level collection
- `system_error_print()` writes to `stderr` directly, no dependency on structured logger

---

## 4. New Module: `initiation_engine/error_handling/`

```
initiation_engine/
├── error_handling/              <- NEW SUB-MODULE
│   ├── __init__.py
│   ├── system_errors.py         # system_error_print() + loaders
│   ├── config/
│   │   ├── system_error_codes.json
│   │   └── messages/
│   │       └── system_en.json
│   └── README.md
```

**Why `initiation_engine`:** System errors are caught at the pipeline entry point which already imports from `initiation_engine`. Keeps system error infrastructure separate from data error infrastructure (`processor_engine/error_handling/`).

---

## 5. Error Categories & Codes

Format: `S-<Category>-S-<XXXX>`

### S-E — Environment & Dependencies

| Code | Name | Hint |
|------|------|------|
| `S-E-S-0101` | MISSING_PACKAGE | `pip install <package>` |
| `S-E-S-0102` | WRONG_PYTHON_VERSION | Activate correct conda env |
| `S-E-S-0103` | ENV_TEST_FAILED | Check output for missing packages |
| `S-E-S-0104` | IMPORT_ERROR | Check `sys.path` and installation |

### S-F — File & Path Errors

| Code | Name | Hint |
|------|------|------|
| `S-F-S-0201` | INPUT_FILE_NOT_FOUND | Check `upload_file_name` in config |
| `S-F-S-0202` | INPUT_FILE_UNREADABLE | Close file in Excel; check `.xlsx` format |
| `S-F-S-0203` | OUTPUT_DIR_NOT_WRITABLE | Check folder permissions |
| `S-F-S-0204` | SCHEMA_FILE_NOT_FOUND | Check `schema_register_file` in config |
| `S-F-S-0205` | CONFIG_FILE_NOT_FOUND | Check `dcc/config/schemas/` folder |

### S-C — Configuration & Parameter Errors

| Code | Name | Hint |
|------|------|------|
| `S-C-S-0301` | INVALID_PARAMETER | Check CLI args and schema defaults |
| `S-C-S-0302` | SCHEMA_PARSE_ERROR | Validate JSON syntax in schema file |
| `S-C-S-0303` | SCHEMA_VALIDATION_FAILED | Check `schema_validation_status.json` |
| `S-C-S-0304` | MISSING_REQUIRED_CONFIG | Check `dcc_register_config.json` |
| `S-C-S-0305` | PROJECT_SETUP_FAILED | Check folder structure vs `project_config.json` |

### S-R — Runtime & Execution Errors

| Code | Name | Hint |
|------|------|------|
| `S-R-S-0401` | STEP_EXCEPTION | Run with `--verbose trace` for traceback |
| `S-R-S-0402` | FAIL_FAST_TRIGGERED | Check `Validation_Errors` column in output |
| `S-R-S-0403` | MEMORY_ERROR | Use `--nrows` to reduce dataset size |

### S-A — AI Ops Warnings (non-fatal)

| Code | Name | Hint |
|------|------|------|
| `S-A-S-0501` | AI_OPS_FAILED | AI skipped; pipeline result unaffected |
| `S-A-S-0502` | DUCKDB_UNAVAILABLE | `pip install duckdb` or delete `dcc_runs.duckdb` |
| `S-A-S-0503` | OLLAMA_UNAVAILABLE | Start Ollama or ignore (fallback used) |

---

## 6. Output Format

**Fatal error (hard stop) — all verbose levels:**
```
----------------------------------------------------------------------------
  X  PIPELINE ERROR  [S-F-S-0201]
     Input File Not Found
     Detail: data/input.xlsx
     Hint:   Check that the file exists and the path is correct.
             If using a relative path, run the pipeline from the dcc/ folder.
----------------------------------------------------------------------------
```

**Warning (non-fatal):**
```
  !  [S-A-S-0501] AI Ops Failed - connection refused
     Hint: AI analysis is optional - the pipeline result is unaffected.
```

**Milestone failure line (SE4):**
```
  X  Schema failed          dcc_register_config.json not found  [S-F-S-0204]
```

---

## 7. Implementation Phases

### Phase SE1 — New Sub-Module & Definition Files ✅ COMPLETE
- Created `initiation_engine/error_handling/` with `system_errors.py`, JSON configs, README
- 20 error codes in `system_error_codes.json`; user hints in `messages/system_en.json`
- Exported `system_error_print` from `initiation_engine/__init__.py`

### Phase SE2 — Fix Silent Stop (Issue #55) ✅ COMPLETE
- `dcc_engine_pipeline.py` `main()`: `log_error()` → `system_error_print("S-R-S-0401")`
- `dcc_engine_pipeline.py` env test: `log_error()` → `system_error_print("S-E-S-0103")`
- `ai_ops_engine/core/engine.py`: added `system_error_print("S-A-S-0501", fatal=False)`
- `ai_ops_engine/persistence/run_store.py`: added `system_error_print("S-A-S-0502", fatal=False)`

### Phase SE3 — Step-Level Error Wrapping ✅ COMPLETE
Each step in `run_engine_pipeline()` wrapped with specific error code:

| Step | Exception | Code |
|------|-----------|------|
| Step 1 — Initiation | Setup not ready | `S-C-S-0305` |
| Step 2 — Schema | `FileNotFoundError` | `S-F-S-0204` |
| Step 2 — Schema | Validation failed | `S-C-S-0303` |
| Step 2 — Schema | `json.JSONDecodeError` | `S-C-S-0302` |
| Step 3 — File load | `FileNotFoundError` | `S-F-S-0201` |
| Step 3 — File load | `PermissionError` | `S-F-S-0202` |
| Step 4 — Processing | `FailFastError` | `S-R-S-0402` |
| Step 4 — Processing | `MemoryError` | `S-R-S-0403` |
| Any step | uncaught `Exception` | `S-R-S-0401` |

### Phase SE4 — Pipeline Messaging Integration ✅ COMPLETE
- `milestone_print()` updated with optional `error_code` parameter
- Failure lines show `[S-X-S-XXXX]` at all verbose levels

---

## 8. Acceptance Criteria

- [x] Missing input file prints `[S-F-S-0201]` with hint at `--verbose quiet`
- [x] Missing schema file prints `[S-F-S-0204]` with hint
- [x] Any unhandled step exception prints `[S-R-S-0401]` with exception message
- [x] `run_ai_ops()` failure prints `[S-A-S-0501]` warning, pipeline still exits 0
- [x] All fatal system error output goes to `stderr`, visible at all verbose levels
- [x] `system_error_codes.json` contains all 20 codes
- [x] `messages/system_en.json` contains title + hint for all 20 codes
- [x] `milestone_print()` failure lines include error code
- [x] No changes to data error handling behaviour
- [x] `initiation_engine/error_handling/` sub-module importable standalone

---

## 9. Notes

**Issue #56 (Windows encoding):** Unicode symbols (`✓`, `✗`, `⚠`, `━`) cause `UnicodeEncodeError` on Windows cp1252 terminals. Replaced with ASCII: `OK`/`X`/`!`/`-`. Logged in `dcc/Log/issue_log.md`.

---

*Last updated: 2026-05-01*
*Status: COMPLETE*
