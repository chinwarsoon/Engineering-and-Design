# Pipeline Messaging Workplan (Redesigned)

**Status:** ACTIVE - Phase 3 Planning 🚧  
**Document ID:** WP-PIPE-MSG-001  
**Date Created:** 2026-04-19  
**Last Updated:** 2026-05-25  
**Revision:** v3.0 - Added log optimization and schema hydration  
**Lead:** Franklin Song  
**Supersedes:** v2.0

**Completion Log:** See `dcc/Log/update_log.md` entry `#pipeline-messaging-complete`

---

## Revision History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| v1.0 | 2026-04-19 | Initial workplan for tiered messaging | COMPLETE ✅ |
| v2.0 | 2026-05-23 | Added progress bar implementation using tqdm | COMPLETE ✅ |
| v3.0 | 2026-05-25 | Added log optimization & schema-driven hydration | PLANNING 📋 |

---

## Table of Contents

1. [Problem Statement - Phase 1](#1-problem-statement)
2. [Level Definitions](#2-level-definitions-confirmed)
3. [Message Samples Per Level](#3-message-samples-per-level)
4. [What Needs to Change in Code](#4-what-needs-to-change-in-code)
5. [Files to Modify](#5-files-to-modify)
6. [Completion Criteria](#6-completion-criteria)
7. [Approval Required](#7-approval-required)
8. **[Phase 2: Progress Bar Implementation](#8-phase-2-progress-bar-implementation)** ⭐ NEW
   - [8.1 Problem Statement](#81-problem-statement)
   - [8.2 Current State Analysis](#82-current-state-analysis)
   - [8.3 Proposed Solution](#83-proposed-solution)
   - [8.4 Implementation Details](#84-implementation-details)
   - [8.5 Dependencies](#85-dependencies)
   - [8.6 Files to Create/Modify](#86-files-to-createmodify)
   - [8.7 Testing Strategy](#87-testing-strategy)
   - [8.8 Success Criteria](#88-success-criteria)
   - [8.9 Implementation Timeline](#89-implementation-timeline)

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

*Last updated: 2026-05-25*  
*Status: ✅ COMPLETE*

---

## 9. Phase 3: Log Optimization & Schema-Driven Hydration ⭐ NEW

**Status:** PLANNING 📋  
**Priority:** CRITICAL - System Performance & Dashboard Stability  
**Date Created:** 2026-05-25

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

- [ ] `debug_log.json` size reduced by >90%.
- [ ] Dashboard successfully loads previously "oversized" logs.
- [ ] All exported user files remain self-contained and descriptive.
- [ ] No regression in error detection or health score calculation.

### 9.8 Implementation Timeline

- **Day 1**: Logging Engine & Aggregator refactor.
- **Day 2**: Dashboard hydration & Compaction utility.
- **Day 3**: Validation & Final Report.

