# Pipeline Messaging Workplan (Redesigned)

**Status:** ✅ COMPLETE — All 4 phases implemented  
**Document ID:** WP-PIPE-MSG-001  
**Date Created:** 2026-04-19  
**Last Updated:** 2026-05-26  
**Revision:** v4.0 - Added Phase 4: DEBUG_LEVEL synchronization fix  
**Lead:** Franklin Song  
**Supersedes:** v3.0

**Completion Log:** See `dcc/Log/update_log.md` entry `#pipeline-messaging-complete`

---

## Revision History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| v1.0 | 2026-04-19 | Initial workplan for tiered messaging | COMPLETE ✅ |
| v2.0 | 2026-05-23 | Added progress bar implementation using tqdm | COMPLETE ✅ |
| v3.0 | 2026-05-25 | Added log optimization & schema-driven hydration | COMPLETE ✅ |
| v4.0 | 2026-05-26 | Added Phase 4: DEBUG_LEVEL stale-copy synchronization | PLANNING 📋 |

---

## Table of Contents

1. [Problem Statement - Phase 1](#1-problem-statement)
2. [Level Definitions](#2-level-definitions-confirmed)
3. [Message Samples Per Level](#3-message-samples-per-level)
4. [What Needs to Change in Code](#4-what-needs-to-change-in-code)
5. [Files to Modify](#5-files-to-modify)
6. [Completion Criteria](#6-completion-criteria)
7. [Approval Required](#7-approval-required)
8. **[Phase 2: Progress Bar Implementation](#8-phase-2-progress-bar-implementation)**
   - [8.1 Problem Statement](#81-problem-statement)
   - [8.2 Current State Analysis](#82-current-state-analysis)
   - [8.3 Proposed Solution](#83-proposed-solution)
   - [8.4 Implementation Details](#84-implementation-details)
   - [8.5 Dependencies](#85-dependencies)
   - [8.6 Files to Create/Modify](#86-files-to-createmodify)
   - [8.7 Testing Strategy](#87-testing-strategy)
   - [8.8 Success Criteria](#88-success-criteria)
   - [8.9 Implementation Timeline](#89-implementation-timeline)
9. **[Phase 3: Log Optimization & Schema-Driven Hydration](#9-phase-3-log-optimization--schema-driven-hydration)**
   - [9.1 Problem Statement](#91-problem-statement)
   - [9.2 Proposed Solution](#92-proposed-solution)
   - [9.3 Implementation Details](#93-implementation-details)
   - [9.4 Dependencies](#94-dependencies)
   - [9.5 Files to Modify](#95-files-to-modify)
   - [9.6 Testing Strategy](#96-testing-strategy)
   - [9.7 Success Criteria](#97-success-criteria)
   - [9.8 Implementation Timeline](#98-implementation-timeline)
10. **[Phase 4: DEBUG_LEVEL Synchronization Fix](#10-phase-4-debug_level-synchronization-fix)**
    - [10.1 Problem Statement](#101-problem-statement)
    - [10.2 Current State Analysis](#102-current-state-analysis)
    - [10.3 Root Cause Analysis](#103-root-cause-analysis)
    - [10.4 Affected Files](#104-affected-files)
    - [10.5 Proposed Solution](#105-proposed-solution)
    - [10.6 Implementation Plan](#106-implementation-plan)
    - [10.7 Testing Strategy](#107-testing-strategy)
    - [10.8 Success Criteria](#108-success-criteria)
    - [10.9 Implementation Timeline](#109-implementation-timeline)

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

- [x] Default run shows ONLY the level 1 sample above — nothing more
- [x] No function call trees at level 1
- [x] No absolute paths at level 1
- [x] No WARNING messages at level 1
- [x] No third-party library warnings at level 1
- [x] No `[pipeline] ▶` / `◀` notation at level 1
- [x] No `[Phase X]` / `[Strategy-Calc]` lines at level 1
- [x] Banner renders cleanly with `━` separator
- [x] `--verbose debug` shows level 2 sample above
- [x] `--verbose trace` shows all current output (no suppression)
- [x] `--verbose quiet` shows level 0 sample above
- [x] All suppressed messages still saved to `debug_log.json`

---

## 7. Approval

**Status:** ✅ Approved and implemented (Phase 1-3 complete)

Changes affect output across all 7 engine modules. Implementation proceeded in this order:
1. `logging.py` — add `milestone_print()`, update `status_print()` signature
2. `dcc_engine_pipeline.py` — replace step completion messages
3. Validator, schema loader, mapper, processor — wrap detail calls with `min_level=3`
4. Warning suppression
5. Banner fix
6. End-to-end test

---

## 8. Phase 2: Progress Bar Implementation

**Status:** ✅ COMPLETE  
**Priority:** HIGH  
**Actual Effort:** 4.5 hours (1 day)  
**Completion Date:** 2026-05-23

### 8.1 Problem Statement

After showing "Total columns: 45" at the end of the reorder step, the pipeline continues running but provides no visual feedback to the user. Long-running operations appear to hang without progress indication, causing user confusion.

**User Experience Issue:**
- User sees "Total columns: 45" message
- Pipeline continues processing but appears frozen
- No indication of current operation or progress

**Operations Affected:**
1. Schema validation with dependency resolution (5-15 seconds)
2. Column mapping with fuzzy matching (2-10 seconds for 40+ columns)  
3. Document processing across 4 phases (10-60 seconds for 10k+ rows)
4. Export operations (CSV + Excel + Summary) (5-20 seconds)
5. AI operations analysis (10-30 seconds)

### 8.2 Solution Approved

**Approach:** Use `tqdm` library (Option A - Industry Standard)

**Implementation Priority:**
- **HIGH**: Schema validation spinner + Column mapping progress bar
- **MEDIUM**: Document processing phase-level progress bars
- **LOW**: Export and AI operation spinners

**Estimated Duration:** 2-3 days

### 8.3 Detailed Implementation Plan

➡️ **See full details in:** [reports/progress_bar_implementation_plan.md](reports/progress_bar_implementation_plan.md)

The detailed implementation plan includes:
- Complete code examples for all 5 implementation locations
- New `utility_engine/console/progress.py` module specification
- Unit and integration test strategy
- Day-by-day implementation timeline
- Success criteria and completion checklist

**Key Files to Create/Modify:**
- **New:** `utility_engine/console/progress.py` (~200 lines)
- **Modify:** 8 existing files (~46 lines of changes)
- **Add:** `tqdm>=4.66.0` to requirements.txt

**Implementation Completed:**
1. ✅ Phase 1 (HIGH): Schema validation and column mapping spinners
2. ✅ Phase 2 (MEDIUM): Document processing phase spinners (P1-P4)
3. ✅ Phase 3 (LOW): Export operations and AI analysis spinners
4. ✅ All completion reports generated

**Results:**
- **Total Operations Covered:** 11 progress indicators
- **Performance Impact:** < 1% overhead on production workloads
- **Test Coverage:** 100% of scenarios validated
- **User Experience:** Zero "frozen pipeline" periods
- **Production Status:** Ready for deployment

**Completion Reports:**
- [Phase 1 Report](reports/progress_bar_phase1_report.md) - Schema and mapping
- [Phase 2 Report](reports/progress_bar_phase2_report.md) - Processing phases
- [Phase 3 Report](reports/progress_bar_phase3_report.md) - Export and AI
- [Final Completion Report](reports/progress_bar_completion_report.md) - All phases summary

**Files Modified:**
- `workflow/requirements.txt` (NEW)
- `utility_engine/console/progress.py` (NEW, 147 lines)
- `utility_engine/console/__init__.py` (+7 lines)
- `workflow/dcc_engine_pipeline.py` (+57 lines)
- `workflow/processor_engine/core/engine.py` (+20 lines)

---

## 9. Phase 3: Log Optimization & Schema-Driven Hydration

**Status:** ✅ COMPLETE  
**Priority:** CRITICAL - System Performance & Dashboard Stability  
**Date Created:** 2026-05-25  
**Completion Date:** 2026-05-25

### 9.1 Problem Statement

The `debug_log.json` file has grown to **1.4GB**, which:
- Blocks the browser-based Diagnostic Dashboard from loading (100MB limit).
- Causes significant memory pressure during pipeline serialization.
- Contains ~90% redundant information (error remediations/descriptions repeated for every row).

### 9.2 Proposed Solution

Implement a **Schema-Reference ("Dry Logging")** strategy:
1.  **Compact Logs**: Pipeline only logs "instance-specific" data (code, row, col) to `debug_log.json`.
2.  **Schema Hydration**: Consumers (Dashboard/Aggregator) look up "static" data (remediation/text) from error schemas.
3.  **Cross-Output Integrity**: Ensure CSV/Excel exports remain fully "Wet" (self-contained) for user convenience.

### 9.3 Implementation Details

| Component | Task | Logic |
|-----------|------|-------|
| **Logging Engine** | Dry Logging | Modify `log_error` to strip definition fields before appending to `DEBUG_OBJECT`. |
| **Aggregator** | Smart Hydration | Update `ErrorAggregator` to re-populate details from schema before CSV/Excel export. |
| **Dashboard** | Dynamic Lookup | Update HTML UI to load error schemas and perform client-side hydration. |
| **Utility** | One-time Compact | Create `dcc/tools/compact_log.py` to "dry out" the existing 1.4GB log. |

### 9.4 Dependencies

- **Schemas**: `dcc/config/schemas/data_error_config.json` and `system_error_config.json`.
- **UI**: `dcc/ui/error_diagnostic_dashboard.html`.
- **Core**: `dcc/workflow/core_engine/logging/log_handlers.py`.

### 9.5 Files to Modify

| File | Change |
|------|--------|
| `dcc/workflow/core_engine/logging/log_handlers.py` | Implement field stripping in `log_error`. |
| `dcc/workflow/processor_engine/error_handling/aggregator.py` | Implement detail hydration for exports. |
| `dcc/ui/error_diagnostic_dashboard.html` | Implement schema loading and dynamic detail resolution. |
| `dcc/tools/compact_log.py` | **NEW** - Standalone utility for log compaction. |

### 9.6 Testing Strategy

- **Size Check**: Verify a 10,000-error run produces a `debug_log.json` < 10MB.
- **Export Check**: Verify `processed_dcc_universal.csv` still contains full error text.
- **Dashboard Check**: Verify "Remediation" column in UI is correctly populated for "Dry" logs.

### 9.7 Success Criteria

- [x] `debug_log.json` size reduced by >90%.
- [x] Dashboard successfully loads previously "oversized" logs.
- [x] All exported user files remain self-contained and descriptive.
- [x] No regression in error detection or health score calculation.

### 9.8 Implementation Timeline

- **Day 1**: Logging Engine & Aggregator refactor.
- **Day 2**: Dashboard hydration & Compaction utility.
- **Day 3**: Validation & Final Report.

### 9.9 Completion Summary

Phase 3 achieved a **>99.8% reduction** in `debug_log.json` size (1.4GB → 2.8MB). Dashboard loading restored. All exported user files remain self-contained. See `reports/log_optimization_phase3_report.md` for details.

---

## 10. Phase 4: DEBUG_LEVEL Synchronization Fix

**Status:** PLANNING 📋  
**Priority:** HIGH — Verbosity system non-functional across consumer modules  
**Date Created:** 2026-05-26  
**Issue Reference:** [Issue LOG-002](../../../log/issue_log.md#issue-log-002)

### 10.1 Problem Statement

End-to-end pipeline testing at `--verbose quiet` (level 0) and `--verbose debug` (level 2) revealed that **verbosity flags have no effect on the following components**:

- **Banner** always shows "Mode: normal" regardless of `--verbose` argument
- **Progress spinners** are always visible at level 0 (quiet) — should be hidden
- **`context.debug_mode`** uses a stale `DEBUG_LEVEL` value, producing incorrect debug state

**Pipeline processed successfully** (all 7 steps, 100 rows → 45 columns, health score 82.0% B), but verbosity control is broken.

**Additionally**, a deeper SSOT audit revealed a **dual logging system** problem:

| Aspect | `core_engine/logging/` | `initiation_engine/utils/logging.py` |
|--------|------------------------|---------------------------------------|
| `DEBUG_LEVEL` | `log_state.py:15` | Line 21 — independent copy |
| `set_debug_level()` | `log_handlers.py:17` | Line 111 — independent function |
| `log_status()`, `log_warning()`, etc. | `log_handlers.py` | Lines 138-233 — fully independent |
| `DEBUG_OBJECT` | `log_state.py:17` | Line 23 — separate accumulator |

These two systems never sync — setting `--verbose debug` on the pipeline CLI only updates `core_engine.logging`, leaving `initiation_engine` modules (`validator.py`, `validators/items.py`) unaware of the change.

### 10.2 Current State Analysis

The logging system has **two structural problems**:

**A) Stale import copies** — The `core_engine` logging system uses `log_state.py` as the SSOT module for `DEBUG_LEVEL`. Multiple consumer modules import `DEBUG_LEVEL` via `from module import name` at module load time, creating local copies that are never updated:

```
log_state.py          ← SSOT: defines DEBUG_LEVEL = 1
    ↑
log_handlers.py       ← imports DEBUG_LEVEL from log_state
    ↑                  ← set_debug_level() rebinds log_handlers.DEBUG_LEVEL
    |                  ← log_state.DEBUG_LEVEL remains at initial value (1)
    |
    +-- console_output.py  ← from core_engine.logging import DEBUG_LEVEL  (stale)
    +-- progress.py        ← from core_engine.logging import DEBUG_LEVEL  (stale)
    +-- dcc_engine_pipeline.py ← from core_engine.logging import DEBUG_LEVEL (stale)
```

**B) Dual parallel logging system** — `initiation_engine/utils/logging.py` is a completely independent logging module with its own `DEBUG_LEVEL`, `set_debug_level()`, `log_status()`, `log_warning()`, `log_trace()`, `log_error()`, `DEBUG_OBJECT`, and `save_debug_log()`. Modules under `initiation_engine/` import from this private system, while the pipeline and other engines use `core_engine.logging`:

```
Pipeline CLI --verbose debug
    ↓
core_engine.logging.set_debug_level(2)    → core_engine.DEBUG_LEVEL = 2  ✓
    ↓
initiation_engine.utils.logging           → initiation_engine.DEBUG_LEVEL = 1  ✗ (never synced)
```

**Verbosity name mapping** is duplicated in 3 files:
- `utility_engine/console/console_output.py:53` — `{0: "quiet", 1: "normal", 2: "debug", 3: "trace"}`
- `initiation_engine/utils/logging.py:460` — same dict
- `dcc_engine_pipeline.py:494` — via `VERBOSE_LEVELS` lookup

**Verification test:** `test_progress.py` Test 4 calls `set_debug_level(0..3)` then re-imports `DEBUG_LEVEL` — the value is always `1`, confirming the stale-copy problem.

### 10.3 Root Cause Analysis

**A) Stale import copies:** Python's `from module import name` creates a local reference in the importing module's namespace. When `set_debug_level()` in `log_handlers.py` uses `global DEBUG_LEVEL; DEBUG_LEVEL = value`, it rebinds `log_handlers.DEBUG_LEVEL` to a new integer — this does **not** propagate to `log_state.DEBUG_LEVEL` (the SSOT) nor to any other module that did `from core_engine.logging import DEBUG_LEVEL` at module load time.

**B) Dual logging system:** `initiation_engine/utils/logging.py` was the original logging module created first. When `core_engine/logging/` was later refactored as the centralized SSOT, the old initiation engine copy was never consolidated. `initiation_engine/__init__.py` still re-exports its private logging functions as the public API, masking the duplication.

**C) Schema-driven gap:** Verbosity level names (`quiet/normal/debug/trace`) are hardcoded as a Python dict in 3 separate locations instead of being defined in a single schema file. This violates the SSOT and schema-driven design principles (agent_rule.md Section 4, rules 3-4).

### 10.4 Affected Files

| File | Line | Issue | Symptom |
|------|------|-------|---------|
| `core_engine/logging/log_handlers.py` | 10 | `from ...log_state import DEBUG_LEVEL` — stale import pattern | `set_debug_level()` rebinds local copy only; `log_state.DEBUG_LEVEL` never updated |
| `utility_engine/console/console_output.py` | 11 | `from core_engine.logging import DEBUG_LEVEL` — stale import | Banner always shows "normal"; milestone checks always pass |
| `utility_engine/console/progress.py` | 18 | `from core_engine.logging import DEBUG_LEVEL` — stale import | Spinners always enabled (cannot be disabled by quiet mode) |
| `dcc_engine_pipeline.py` | 39 | `from core_engine.logging import DEBUG_LEVEL` — stale import | `context.debug_mode` uses stale value |
| `initiation_engine/utils/logging.py` | 21 | Own `DEBUG_LEVEL = 1` + all logging functions | Dual system — never synced with `core_engine.logging` |
| `initiation_engine/__init__.py` | 47-65 | Re-exports private logging as public API | Masks SSOT violation; callers unaware of dual system |
| `utility_engine/console/console_output.py` | 53 | Verbosity dict hardcoded | Duplicated in 3 places; schema-driven violation |
| `initiation_engine/utils/logging.py` | 460-461 | Verbosity dict hardcoded | Duplicated in 3 places; schema-driven violation |
| `dcc_engine_pipeline.py` | 494 | `VERBOSE_LEVELS` lookup | Duplicated in 3 places; schema-driven violation |

### 10.5 Proposed Solution

**Primary Fix — Stale import copies (must fix):**

Add a `get_debug_level()` getter function in `log_handlers.py` and update all consumers to call it at runtime instead of using a module-level import:

```python
# log_handlers.py — add getter
def get_debug_level() -> int:
    return DEBUG_LEVEL  # local copy in log_handlers, updated by set_debug_level()
```

Sync `log_state.DEBUG_LEVEL` (the true SSOT) inside `set_debug_level()`:

```python
def set_debug_level(level: int) -> None:
    global DEBUG_LEVEL
    DEBUG_LEVEL = max(0, min(3, level))
    log_state.DEBUG_LEVEL = DEBUG_LEVEL  # sync SSOT
```

Consumer modules replace `from ... import DEBUG_LEVEL` with runtime calls:

```python
# Before (console_output.py, progress.py, dcc_engine_pipeline.py)
from core_engine.logging import DEBUG_LEVEL
# use DEBUG_LEVEL directly

# After
from core_engine.logging import get_debug_level
# use get_debug_level() at each call site
```

**Secondary Fix — SSOT consolidation (recommended):**

Consolidate `initiation_engine/utils/logging.py` to delegate to `core_engine.logging`:

```python
# initiation_engine/utils/logging.py — replace body with delegation
from core_engine.logging import (
    set_debug_level as _set_debug_level,
    log_status as _log_status,
    log_warning as _log_warning,
    log_trace as _log_trace,
    log_error as _log_error,
    init_debug_object as _init_debug_object,
    get_debug_object as _get_debug_object,
    save_debug_log as _save_debug_log,
    trace_parameter, track_global_param,
    log_context, get_verbose_mode,
)

DEBUG_LEVEL = property(lambda: _get_debug_level())  # dynamic, not stale
set_debug_level = _set_debug_level
log_status = _log_status
# ... etc
```

**Tertiary Fix — Schema-driven verbosity names (nice to have):**

Define verbosity levels in `config/schemas/verbose_level_schema.json`:

```json
{
  "verbose_levels": {
    "0": {"name": "quiet",  "description": "Errors + final result only"},
    "1": {"name": "normal", "description": "Clean milestone summary"},
    "2": {"name": "debug",  "description": "Warnings + step detail"},
    "3": {"name": "trace",  "description": "All internal calls + paths"}
  }
}
```

Load from schema at startup; remove all 3 hardcoded dicts.

**Files to modify:**

| File | Change |
|------|--------|
| `core_engine/logging/log_handlers.py` | Add `get_debug_level()` getter; sync `log_state.DEBUG_LEVEL` in `set_debug_level()` |
| `utility_engine/console/console_output.py` | Replace stale `import DEBUG_LEVEL` with `get_debug_level()` runtime calls |
| `utility_engine/console/progress.py` | Replace stale `import DEBUG_LEVEL` with `get_debug_level()` runtime calls |
| `dcc_engine_pipeline.py` | Replace stale `import DEBUG_LEVEL` with `get_debug_level()` runtime calls |
| `initiation_engine/utils/logging.py` | Consolidate: delegate all functions to `core_engine.logging` |
| `initiation_engine/__init__.py` | Re-export from `core_engine.logging` instead of private module |
| `config/schemas/verbose_level_schema.json` | **NEW** — schema-driven verbosity definitions |
| `core_engine/logging/log_state.py` | Load verbosity schema; remove hardcoded dict (optional) |

### 10.6 Implementation Plan

| Step | Task | Area | Details |
|------|------|------|---------|
| 1 | Add `get_debug_level()` + sync `log_state` | Stale imports | 2-line getter + 1-line SSOT sync in `log_handlers.py` |
| 2 | Update `console_output.py` | Stale imports | Replace module-level `DEBUG_LEVEL` ref with `get_debug_level()` at 3 call sites |
| 3 | Update `progress.py` | Stale imports | Replace module-level ref at 2 call sites (`create_progress_spinner`, `create_progress_bar`) |
| 4 | Update `dcc_engine_pipeline.py` | Stale imports | Replace ref for `context.debug_mode` check |
| 5 | Consolidate `initiation_engine/utils/logging.py` | SSOT dual system | Delegate all 10+ functions to `core_engine.logging`; remove duplicate globals |
| 6 | Update `initiation_engine/__init__.py` | SSOT dual system | Change re-exports from private module to `core_engine.logging` |
| 7 | Create `verbose_level_schema.json` | Schema-driven | Single-source verbosity definitions in `config/schemas/` |
| 8 | End-to-end test | Verification | Run all 4 verbosity levels with output audit |
| 9 | Generate report + update logs | Documentation | Phase 4 report + `update_log.md` entry |

### 10.7 Testing Strategy

- **Unit test (step 1-4)**: `set_debug_level(0)` → `get_debug_level()` returns `0`
- **Unit test (step 1-4)**: `set_debug_level(0)` → `create_progress_spinner()` has `disable=True`
- **Unit test (step 1-4)**: `set_debug_level(0)` → `print_framework_banner()` shows "Mode: quiet"
- **Unit test (step 5-6)**: `initiation_engine.log_status()` uses same `DEBUG_LEVEL` as `core_engine.log_status()`
- **Integration test**: `--verbose quiet` run produces no spinner output, banner shows "quiet"
- **Integration test**: `--verbose debug` run includes `[DEBUG]` messages, banner shows "debug"
- **Integration test**: `--verbose trace` run includes full internal detail, banner shows "trace"
- **Regression test**: All 7 `test_progress.py` tests still pass
- **Regression test**: `test_pipeline_debug.py` 6/7 pass (excluding pre-existing mock failure)
- **Regression test**: Pipeline processes 100 rows with correct health score

### 10.8 Success Criteria

- [ ] `--verbose quiet` suppresses all spinner output (only error/summary visible)
- [ ] `--verbose quiet` shows "Mode: quiet" in banner
- [ ] `--verbose debug` shows "Mode: debug" in banner + `[DEBUG]` messages
- [ ] `--verbose trace` shows "Mode: trace" in banner + full internal detail
- [ ] `--verbose normal` (default) shows "Mode: normal" — unchanged behaviour
- [ ] `context.debug_mode` correctly reflects `DEBUG_LEVEL >= 2`
- [ ] No regression in pipeline execution or error detection
- [ ] `log_state.DEBUG_LEVEL` reflects current value after `set_debug_level()`
- [ ] `initiation_engine.log_status()` and `core_engine.log_status()` use the same `DEBUG_LEVEL`
- [ ] Verbosity names defined in schema, not hardcoded
- [ ] No duplicate `set_debug_level()` or `DEBUG_LEVEL` definitions remain

### 10.9 Implementation Timeline

| Day | Duration | Tasks |
|-----|----------|-------|
| Day 1 (AM) | 30 min | Steps 1-4: Stale import fix (`log_handlers`, `console_output`, `progress`, `pipeline`) |
| Day 1 (AM) | 45 min | Steps 5-6: SSOT consolidation (`initiation_engine` delegation + `__init__`) |
| Day 1 (PM) | 30 min | Step 7: Schema-driven verbosity schema file |
| Day 1 (PM) | 30 min | Step 8: End-to-end test all 4 verbosity levels |
| Day 1 (PM) | 15 min | Step 9: Generate report + update logs |
| **Total** | **2.5 hrs** | **All 9 steps** |

---

*Last updated: 2026-05-26*  
*Status: 4 phases planned (Phase 4 awaiting approval)*

