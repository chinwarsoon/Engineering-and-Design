# Pipeline Messaging Workplan (Redesigned)

**Status:** COMPLETE ✅  
**Date:** 2026-04-19  
**Lead:** Franklin Song  
**Supersedes:** Previous version (marked COMPLETE but not implemented)

**Completion Log:** See `dcc/Log/update_log.md` entry `#pipeline-messaging-complete`

---

## 1. Problem Statement

The current default level (normal/level 1) still outputs:

- Internal function call trees: `[validator] ▶ validate`, `[validators] [OK] config/schemas ...`
- Full absolute paths: `/home/franklin/dsai/Engineering-and-Design/dcc/config/schemas/...`
- Step bracket notation: `[pipeline] ▶ step1_initiation`, `[pipeline] ◀ step1_initiation (0.9ms)`
- CLI override messages: `CLI overrides detected. CLI values: {'verbose_level': 'normal'}`
- Detailed sub-step messages: `Validating 7 folders...`, `Validating 3 root files...`
- Third-party library warnings: `UserWarning: Print area cannot be set...`
- WARNING messages for non-critical issues: `WARNING: Required input column missing...`
- Malformed banner: misaligned box-drawing characters

**Root cause:** The `status_print()` and `debug_print()` functions in `logging.py` are called throughout the codebase without level guards. The previous "fix" only suppressed error messages from `StructuredLogger`, not the general `status_print()` calls in validators, schema loaders, and engine steps.

---

## 2. Level Definitions (Confirmed)

| Level | Argument | Intent | Who uses it |
|-------|----------|--------|-------------|
| 0 | `--verbose quiet` | Errors + final result only | CI/CD, automation, scripts |
| 1 | (default, no flag) | Clean milestone summary | Normal user running pipeline |
| 2 | `--verbose debug` | Warnings + step detail | Developer debugging |
| 3 | `--verbose trace` | All internal calls + paths | Deep troubleshooting |

**Key rule:** Level 1 (default) must show ONLY what a non-technical user needs to know. No function names, no paths, no warnings, no internal state.

---

## 3. Message Samples Per Level

### Level 0 — quiet

Absolute minimum. One line of result + output path. Nothing else.

```
DCC Pipeline v3.0 | Submittal and RFI Tracker Lists.xlsx | quiet
Processing complete: 11,099 rows → 44 cols | Health: 95.7% (A) | 2,862 errors
Output: output/processed_dcc_universal.csv
```

If pipeline fails:
```
DCC Pipeline v3.0 | Submittal and RFI Tracker Lists.xlsx | quiet
ERROR: Schema validation failed — dcc_register_config.json missing required column: Document_ID
Exit code: 1
```

---

### Level 1 — normal (DEFAULT)

Clean milestone summary. No paths, no function names, no warnings, no internal state.
Each step shows a single ✓ or ✗ line. Final summary block at the end.

```
DCC Register Processing Pipeline  v3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓  Setup validated          7 folders, 11 files
  ✓  Schema loaded            44 columns, 6 references
  ✓  Columns mapped           26 / 26  (100%)
  ✓  Data processed           11,099 rows → 44 columns
  ✓  Exported                 CSV + Excel + Summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Health Score:  95.7%  (Grade A)
  Errors:        2,862 rows affected  |  2,184 row-level  |  678 fill warnings
  Output:        output/processed_dcc_universal.xlsx
  Details:       output/error_dashboard_data.json
  Hint:          Run with --verbose debug for full error list
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If a step fails at level 1:
```
DCC Register Processing Pipeline  v3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓  Setup validated          7 folders, 11 files
  ✗  Schema failed            dcc_register_config.json — missing required column: Document_ID

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FAILED  |  Run with --verbose debug for details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What is NOT shown at level 1:**
- `CLI overrides detected. CLI values: {'verbose_level': 'normal'}`
- `Building native default parameters...`
- `Testing environment and required libraries...`
- `Loading schema from: /home/.../project_setup.json for validation`
- `[pipeline] ▶ step1_initiation`
- `[validator] ▶ validate`
- `[validators] [OK] config/schemas (required) -> /home/.../config/schemas`
- `Validating 7 folders...`
- `Validating 3 root files...`
- `[validator] OS: Linux (linux)`
- `Resolving effective parameters...`
- `Resolving platform paths...`
- `Using Linux path: /home/.../Submittal and RFI Tracker Lists.xlsx`
- `Output directory: /home/.../output`
- `CSV path: /home/.../output/processed_dcc_universal.csv`
- `Validating field_definitions in schema: ...`
- `Validated calculation sequence for 26 columns.`
- `[processor] ▶ process_data`
- `WARNING: Required input column missing during mapping detection: Document_Title`
- `UserWarning: Print area cannot be set to Defined name...`
- Any `[ERROR]` or `[WARNING]` lines from StructuredLogger
- Any `[Phase X]` processing step lines

---

### Level 2 — debug

Step-level detail with context. Shows warnings, column details, phase breakdown. No deep internal call trees.

```
DCC Register Processing Pipeline  v3.0  [debug]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Step 1] Setup validation
  ✓ Folders: 7/7 | Files: 11/11 | Environment: OK

[Step 2] Schema loading
  ✓ Schema: dcc_register_config.json
  ✓ Columns: 44 | References: 6 resolved
  ⚠ Missing optional columns: Document_Title, Reviewer

[Step 3] Column mapping
  ✓ 26/26 headers matched (100%)
  ✓ Sheet: 'Prolog Submittals' | Header row: 5 | Range: P:AP

[Step 4] Data processing
  ✓ Phase 1 (Meta):        10 columns | 0 errors
  ✓ Phase 2 (Transactional): 5 columns | 72 fill warnings
  ✓ Phase 2.5 (Anomaly):   8 columns | 1,238 fill events
  ✓ Phase 3 (Calculated):  18 columns | 0 errors
  ✓ Phase 4 (Validation):  44 columns | 2,862 rows with errors
  ✓ Row validation:        2,184 cross-field issues

[Step 5] Export
  ✓ CSV:     output/processed_dcc_universal.csv
  ✓ Excel:   output/processed_dcc_universal.xlsx
  ✓ Summary: output/processing_summary.txt
  ✓ Debug:   output/debug_log.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Health Score:  95.7%  (Grade A)  |  11,099 rows  |  44 columns
  Top errors:    VERSION_REGRESSION (213)  |  P2-I-V-0204 (1,683)  |  GROUP_INCONSISTENT (112)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Level 3 — trace

Full internal detail. All current output is acceptable at this level, including:
- `[pipeline] ▶ step1_initiation` / `◀ step1_initiation (0.9ms)`
- `[validator] ▶ validate` / `[validators] [OK] config/schemas ...`
- `[Phase 1] Project_Code: Applying default_value`
- `[Strategy-Calc] Resubmission_Plan_Date: Applying ... with overwrite_existing`
- Full absolute paths
- All WARNING and ERROR messages from StructuredLogger
- Third-party library warnings (openpyxl etc.)

```
DCC Register Processing Pipeline  v3.0  [trace]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[trace] All internal calls, paths, and warnings visible
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLI overrides detected. CLI values: {'verbose_level': 'trace'}
Building native default parameters...
Testing environment and required libraries...
Loading schema from: /home/franklin/.../project_setup.json for validation
Environment test passed.
[pipeline] ▶ step1_initiation
  [validator] ▶ validate
    [validator] OS: Linux (linux)
    [validator] Validating 7 folders...
    [validators] [OK] config/schemas (required) -> /home/franklin/.../config/schemas
    ...
  [validator] ◀ validate (0.7ms)
  ✓ Project setup validation passed
[pipeline] ◀ step1_initiation (0.9ms)
...
```

---

## 4. What Needs to Change in Code

### 4.1 `status_print()` — the core fix

Every `status_print()` call in the codebase currently prints regardless of level. The fix is to assign each call a minimum level. Calls that are internal detail must require level ≥ 2.

| Current call | Minimum level needed |
|---|---|
| `status_print("Building native default parameters...")` | 3 |
| `status_print("Testing environment and required libraries...")` | 2 |
| `status_print(f"Loading schema from: {schema_path}...")` | 3 |
| `status_print("Resolving effective parameters...")` | 3 |
| `status_print("Resolving platform paths...")` | 3 |
| `status_print(f"Using Linux path: {path}")` | 3 |
| `status_print(f"Output directory: {dir}")` | 3 |
| `status_print(f"CSV path: {path}")` | 3 |
| `status_print(f"[validator] OS: Linux")` | 3 |
| `status_print(f"[validators] [OK] {folder}...")` | 3 |
| `status_print(f"Validating {n} folders...")` | 3 |
| `status_print(f"Validated calculation sequence...")` | 3 |
| `status_print(f"[Phase X] {col}: Applying {strategy}")` | 3 |
| `status_print(f"[Strategy-Calc] {col}: ...")` | 3 |
| `status_print(f"✓ Project setup validation passed")` | → replace with milestone |
| `status_print(f"✓ Schema validation passed")` | → replace with milestone |
| `status_print(f"✓ Column mapping complete: {rate}")` | → replace with milestone |
| `status_print(f"✓ Processing complete")` | → replace with milestone |

### 4.2 New `milestone_print()` function

A new function that always prints at level 1+, formatted as a clean milestone line:

```python
def milestone_print(step: str, detail: str, ok: bool = True) -> None:
    """Print a pipeline milestone — visible at level 1+."""
    icon = "✓" if ok else "✗"
    print(f"  {icon}  {step:<22} {detail}", flush=True)
```

### 4.3 Banner redesign

The current banner has misaligned box-drawing characters. New design uses `━` (U+2501) for clean horizontal lines, no box corners:

```python
def print_banner(input_file: str, mode: str, version: str = "3.0") -> None:
    fname = Path(input_file).name if input_file else "—"
    print(f"\nDCC Register Processing Pipeline  v{version}")
    print("━" * 76)
```

### 4.4 Suppress third-party warnings

openpyxl warnings must be suppressed at levels 0 and 1:

```python
import warnings
if DEBUG_LEVEL < 2:
    warnings.filterwarnings("ignore")
```

### 4.5 `debug_print()` — already level 2+

`debug_print()` already checks `DEBUG_LEVEL >= 2`. No change needed.

### 4.6 `log_error()` / `StructuredLogger`

Already suppressed at level 1 (from previous fix). Confirmed working.

---

## 5. Files to Modify

| File | Change |
|------|--------|
| `initiation_engine/utils/logging.py` | Add `milestone_print()`, update `status_print()` to accept `min_level` param, add warning suppression |
| `initiation_engine/utils/cli.py` | Confirm `--verbose` argument exists |
| `dcc_engine_pipeline.py` | Replace `status_print()` calls with `milestone_print()` for step completions; move detail calls to level 3 |
| `initiation_engine/core/validator.py` | Wrap all `status_print()` calls with `min_level=3` |
| `schema_engine/loader/schema_loader.py` | Wrap `status_print()` calls with `min_level=3` |
| `mapper_engine/core/engine.py` | Wrap `status_print()` calls with `min_level=2` |
| `processor_engine/core/engine.py` | Wrap `_print_processing_step()` with `min_level=3` |

---

## 6. Completion Criteria

- [ ] Default run shows ONLY the level 1 sample above — nothing more
- [ ] No function call trees at level 1
- [ ] No absolute paths at level 1
- [ ] No WARNING messages at level 1
- [ ] No third-party library warnings at level 1
- [ ] No `[pipeline] ▶` / `◀` notation at level 1
- [ ] No `[Phase X]` / `[Strategy-Calc]` lines at level 1
- [ ] Banner renders cleanly with `━` separator
- [ ] `--verbose debug` shows level 2 sample above
- [ ] `--verbose trace` shows all current output (no suppression)
- [ ] `--verbose quiet` shows level 0 sample above
- [ ] All suppressed messages still saved to `debug_log.json`

---

## 7. Approval Required

**Awaiting approval before implementation.**

Changes affect output across all 7 engine modules. Once approved, implementation will proceed in this order:
1. `logging.py` — add `milestone_print()`, update `status_print()` signature
2. `dcc_engine_pipeline.py` — replace step completion messages
3. Validator, schema loader, mapper, processor — wrap detail calls with `min_level=3`
4. Warning suppression
5. Banner fix
6. End-to-end test

---

*Last updated: 2026-04-19*
