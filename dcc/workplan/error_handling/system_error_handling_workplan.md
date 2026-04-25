# DCC Pipeline: System Error Handling Framework - Workplan

| Field | Value |
|-------|-------|
| **Workplan ID** | WP-DCC-EH-SYS-001 |
| **Version** | 1.1 |
| **Date** | 2026-05-01 |
| **Status** | ✅ COMPLETE (Phases SE1-SE4) |
| **Scope** | **SYSTEM ERRORS ONLY** - Environment, file, config, runtime failures |
| **Data Errors** | See [data_error_handling_workplan.md](data_error_handling_workplan.md) for LL-M-F-XXXX data/logic errors |
| **Depends on** | `error_handling_module_workplan.md`, `pipeline_messaging_plan.md` |
| **Related Issues** | #55 (Silent Stop), #56 (Windows Encoding) |
| **Completion Report** | [`reports/system_error_handling_completion_report.md`](reports/system_error_handling_completion_report.md) |

---

## 1. Object

To implement system-level error handling for the DCC pipeline that:
- Catches environment problems, missing files, bad configuration, unexpected exceptions, and silent stops
- Provides **20 System Error Codes** in S-C-S-XXXX format (System-Category-System-UniqueID)
- Ensures all system errors are **visible at all verbose levels** (bypasses verbose gate)
- Triggers **hard stop** immediately on fatal errors (no suppression, no remediation)
- Distinct from data error handling (see [data_error_handling_workplan.md](data_error_handling_workplan.md) for data quality errors)

**Core principle:** Any system error that stops the pipeline must be visible to the user with a clear error code (S-C-S-XXXX), description, and troubleshooting hint — regardless of verbose level.

---

## 2. Scope Summary

### In Scope (System Errors Only)
| Category | Error Codes | Description |
|----------|-------------|-------------|
| **S-E-S** (Environment) | 0101-0104 | Missing packages, wrong Python version, import errors |
| **S-F-S** (File/Path) | 0201-0205 | Input file not found, unreadable, schema missing |
| **S-C-S** (Config) | 0301-0305 | Invalid parameters, schema parse/validation errors |
| **S-R-S** (Runtime) | 0401-0403 | Step exceptions, fail-fast triggered, memory errors |
| **S-A-S** (AI Ops) | 0501-0503 | AI warnings (non-fatal), DuckDB/Ollama unavailable |

### Out of Scope (See Other Workplans)
| Topic | Location |
|-------|----------|
| **Data Errors** (LL-M-F-XXXX) | [data_error_handling_workplan.md](data_error_handling_workplan.md) |
| **Data Quality Errors** | [error_handling_module_workplan.md](error_handling_module_workplan.md) |
| **Row-level Validation** | [data_error_handling_workplan.md](data_error_handling_workplan.md) Section 12.6 |
| **Schema Content Validation** | [data_error_handling_workplan.md](data_error_handling_workplan.md) |
| **Business Logic Errors** | [data_error_handling_workplan.md](data_error_handling_workplan.md) Section 12.4 |
| **AI Engine Internals** | `ai_ops_engine/` documentation |

---

## 3. Index of Content

| Section | Description | Link |
|---------|-------------|------|
| 1 | [Object](#1-object) | Purpose of system error framework |
| 2 | [Scope Summary](#2-scope-summary) | System errors only; data errors separate |
| 3 | [Index of Content](#3-index-of-content) | This table |
| 4 | [Version History](#4-version-history) | Revision tracking |
| 5 | [Alignment with Architecture](#5-alignment-with-existing-architecture) | Data vs System error comparison |
| 6 | [Dependencies](#6-dependencies-with-other-tasks) | Internal & external dependencies |
| 7 | [New Module Structure](#7-new-module-initiation_engineerror_handling) | File structure |
| 8 | [Error Categories & Codes](#8-error-categories--codes) | S-E-S, S-F-S, S-C-S, S-R-S, S-A-S |
| 9 | [Output Format](#9-output-format) | Fatal vs Warning display |
| 10 | [Implementation Phases](#10-implementation-phases) | SE1-SE4 breakdown |
| 11 | [Timeline & Deliverables](#11-timeline--milestones-and-deliverables) | Schedule & 8 deliverables |
| 12 | [Risks & Mitigation](#12-risks-and-mitigation) | 4 system-specific risks |
| 13 | [Future Issues](#13-potential-issues-to-be-addressed-in-the-future) | 3 improvement areas |
| 14 | [Success Criteria](#14-success-criteria) | 10 acceptance criteria |
| 15 | [Notes](#15-notes) | Issue #56 Windows encoding |
| 16 | [References](#16-references) | Links to code, reports, logs |

---

## 4. Version History

| Version | Date | Author | Changes | Status |
|---------|------|--------|---------|--------|
| 1.1 | 2026-05-01 | System | Added Workplan ID, References section, index with links per agent_rule.md | ✅ Complete |
| 1.0 | 2026-04-20 | System | Initial system error handling framework with 20 S-C-S-XXXX codes | ✅ Complete |

---

## 5. Alignment with Existing Architecture

| Aspect | Data Error Handling ([data_error_handling_workplan.md](data_error_handling_workplan.md)) | System Error Handling (This Workplan) |
|--------|--------------------|-----------------------|
| **Error codes** | `LL-M-F-XXXX` (e.g. `P1-A-P-0101`, `L3-L-V-0302`) | `S-C-S-XXXX` (e.g. `S-F-S-0201`, `S-R-S-0401`) |
| **Severity levels** | CRITICAL / HIGH / MEDIUM / LOW / WARNING | FATAL / WARNING |
| **Definitions file** | `data_error_config.json` | `system_error_config.json` |
| **User instructions** | `messages/en.json` + `messages/zh.json` | `messages/system_en.json` |
| **Logging** | `StructuredLogger` via `detect_error()` | `system_error_print()` — always visible, direct stderr |
| **Pipeline behaviour** | Collect per row, continue processing | Hard stop immediately (all levels) |
| **Messaging integration** | `milestone_print()` / `status_print()` | `system_error_print()` + `milestone_print()` with error_code param |
| **Workplan** | [data_error_handling_workplan.md](data_error_handling_workplan.md) (WP-DCC-EH-DATA-001) | This file (WP-DCC-EH-SYS-001) |

**Key differences from [data_error_handling_workplan.md](data_error_handling_workplan.md) (Data Errors):**
| Feature | Data Errors | System Errors |
|---------|-------------|---------------|
| Print behavior | Respects verbose level | **Always prints** — bypasses verbose gate |
| Pipeline action | Continue processing | **Hard stop** — no suppression/remediation |
| Output stream | Via logger | Direct `stderr` write |
| Collection | Per-row in `Validation_Errors` column | Immediate termination |
| Code format | LL-M-F-XXXX (17 codes) | S-C-S-XXXX (20 codes) |

---

## 6. Dependencies with Other Tasks

### Internal Dependencies

| Task | Relationship | Status |
|------|--------------|--------|
| [Data Error Handling Workplan](data_error_handling_workplan.md) | Complementary — data errors use LL-M-F-XXXX | ✅ Complete |
| [Error Handling Taxonomy](error_handling_taxonomy.md) | Master reference includes S-C-S-XXXX codes | ✅ Complete |
| [Pipeline Messaging Plan](pipeline_messaging_plan.md) | `milestone_print()` integration | ✅ Complete |
| [Error Handling Module](error_handling_module_workplan.md) | Shared error handling infrastructure | ✅ Complete |

### External Dependencies

| Component | Usage | Location |
|-----------|-------|----------|
| `dcc_engine_pipeline.py` | Entry point for system error catching | [`workflow/dcc_engine_pipeline.py`](../../workflow/dcc_engine_pipeline.py) |
| `initiation_engine/__init__.py` | Exports `system_error_print` | [`workflow/initiation_engine/__init__.py`](../../workflow/initiation_engine/__init__.py) |
| `ai_ops_engine/core/engine.py` | AI error handling | [`workflow/ai_ops_engine/core/engine.py`](../../workflow/ai_ops_engine/core/engine.py) |
| `ai_ops_engine/persistence/run_store.py` | DuckDB error handling | [`workflow/ai_ops_engine/persistence/run_store.py`](../../workflow/ai_ops_engine/persistence/run_store.py) |

---

## 7. New Module: `initiation_engine/error_handling/`

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

## 8. Error Categories & Codes

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

## 9. Output Format

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

## 10. Implementation Phases

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

## 11. Timeline, Milestones, and Deliverables

### Timeline Summary

| Phase | Start | End | Duration | Status |
|-------|-------|-----|----------|--------|
| Phase SE1 | Apr 18 | Apr 19 | 2 days | ✅ Complete |
| Phase SE2 | Apr 19 | Apr 20 | 2 days | ✅ Complete |
| Phase SE3 | Apr 20 | Apr 21 | 1 day | ✅ Complete |
| Phase SE4 | Apr 21 | Apr 22 | 1 day | ✅ Complete |

### Key Milestones

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| M1 | Apr 19 | `initiation_engine/error_handling/` sub-module created |
| M2 | Apr 20 | Silent stop fix (Issue #55) implemented |
| M3 | Apr 21 | Step-level error wrapping complete |
| M4 | Apr 22 | Pipeline messaging integration done |

### Deliverables

| ID | Deliverable | Location | Status |
|----|-------------|----------|--------|
| D1 | System Error Config | [`config/schemas/system_error_config.json`](../../config/schemas/system_error_config.json) | ✅ |
| D2 | System Messages EN | [`workflow/initiation_engine/error_handling/config/messages/system_en.json`](../../workflow/initiation_engine/error_handling/config/messages/system_en.json) | ✅ |
| D3 | system_errors.py | [`workflow/initiation_engine/error_handling/system_errors.py`](../../workflow/initiation_engine/error_handling/system_errors.py) | ✅ |
| D4 | dcc_engine_pipeline.py updates | [`workflow/dcc_engine_pipeline.py`](../../workflow/dcc_engine_pipeline.py) | ✅ |
| D5 | ai_ops_engine updates | [`workflow/ai_ops_engine/core/engine.py`](../../workflow/ai_ops_engine/core/engine.py) | ✅ |
| D6 | run_store.py updates | [`workflow/ai_ops_engine/persistence/run_store.py`](../../workflow/ai_ops_engine/persistence/run_store.py) | ✅ |
| D7 | Completion Report | [`reports/system_error_handling_completion_report.md`](reports/system_error_handling_completion_report.md) | ✅ |
| D8 | This Workplan | `workplan/error_handling/system_error_handling_workplan.md` | ✅ |

---

## 12. Risks and Mitigation

| Risk | Probability | Impact | Mitigation | Status |
|------|-------------|--------|------------|--------|
| R1 | Silent stop not caught | Medium | High | Wrapped `main()` with try/except, Issue #55 | Resolved |
| R2 | Windows encoding errors | Medium | Low | Replaced Unicode with ASCII, Issue #56 | Resolved |
| R3 | System errors hidden by verbose | Low | High | `system_error_print()` bypasses verbose gate | Resolved |
| R4 | Confusion with data errors | Medium | Medium | Clear separation in workplans, different formats | Resolved |

---

## 13. Potential Issues to be Addressed in the Future

| Issue | Priority | Description | Proposed Solution |
|-------|----------|-------------|-------------------|
| F1 | Low | Add system error messages in Chinese | Extend `system_zh.json` |
| F2 | Low | System error recovery (retry logic) | Add retry decorator for transient errors |
| F3 | Medium | System error analytics dashboard | Track S-C-S-XXXX frequency in logs |

---

## 14. Success Criteria

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

**Success Criteria Table:**

| Criterion | Target | Measurement | Status |
|-----------|--------|-------------|--------|
| SC1 | Missing input file error | `[S-F-S-0201]` at `--verbose quiet` | ✅ Pass |
| SC2 | Missing schema file error | `[S-F-S-0204]` displayed | ✅ Pass |
| SC3 | Unhandled exception error | `[S-R-S-0401]` with message | ✅ Pass |
| SC4 | AI ops warning | `[S-A-S-0501]`, exit 0 | ✅ Pass |
| SC5 | stderr output | Visible at all verbose levels | ✅ Pass |
| SC6 | 20 system error codes | `system_error_config.json` | ✅ Pass |
| SC7 | All messages defined | `system_en.json` complete | ✅ Pass |
| SC8 | Milestone integration | Error codes in failure lines | ✅ Pass |
| SC9 | No data error impact | [data_error_handling_workplan.md](data_error_handling_workplan.md) unchanged | ✅ Pass |
| SC10 | Sub-module standalone | `initiation_engine/error_handling/` importable | ✅ Pass |

---

## 15. Notes

**Issue #56 (Windows encoding):** Unicode symbols (`✓`, `✗`, `⚠`, `━`) cause `UnicodeEncodeError` on Windows cp1252 terminals. Replaced with ASCII: `OK`/`X`/`!`/`-`. Logged in [`../../log/issue_log.md`](../../log/issue_log.md).

---

## 16. References

### Code Files

| File | Purpose | Location |
|------|---------|----------|
| `system_error_config.json` | 20 S-C-S-XXXX error codes | [`config/schemas/system_error_config.json`](../../config/schemas/system_error_config.json) |
| `system_en.json` | System error messages | [`workflow/initiation_engine/error_handling/config/messages/system_en.json`](../../workflow/initiation_engine/error_handling/config/messages/system_en.json) |
| `system_errors.py` | `system_error_print()` function | [`workflow/initiation_engine/error_handling/system_errors.py`](../../workflow/initiation_engine/error_handling/system_errors.py) |
| `dcc_engine_pipeline.py` | Entry point error handling | [`workflow/dcc_engine_pipeline.py`](../../workflow/dcc_engine_pipeline.py) |
| `ai_ops_engine/core/engine.py` | AI error integration | [`workflow/ai_ops_engine/core/engine.py`](../../workflow/ai_ops_engine/core/engine.py) |

### Reports

| Report | Description | Location |
|--------|-------------|----------|
| System Error Completion Report | SE1-SE4 completion | [`reports/system_error_handling_completion_report.md`](reports/system_error_handling_completion_report.md) |
| Consolidated Implementation Report | All error handling phases | [`reports/consolidated_implementation_report.md`](reports/consolidated_implementation_report.md) |

### Related Workplans

| Workplan | Scope | Location |
|----------|-------|----------|
| Data Error Handling | LL-M-F-XXXX data/logic errors | [data_error_handling_workplan.md](data_error_handling_workplan.md) |
| Error Handling Taxonomy | Complete code reference | [error_handling_taxonomy.md](error_handling_taxonomy.md) |
| Pipeline Messaging Plan | UI/UX integration | [pipeline_messaging_plan.md](pipeline_messaging_plan.md) |
| Error Handling Module | Remediation workflows | [error_handling_module_workplan.md](error_handling_module_workplan.md) |

### Logs

| Log | Purpose | Location |
|-----|---------|----------|
| Issue Log | Issues #55, #56 | [`../../log/issue_log.md`](../../log/issue_log.md) |
| Update Log | SE phase entries | [`../../log/update_log.md`](../../log/update_log.md) |

---

**Status:** ✅ **COMPLETE** — All 20 system error codes implemented and integrated (Issues #55, #56)  
**Last Updated:** 2026-04-25 per agent_rule.md workplan requirements
