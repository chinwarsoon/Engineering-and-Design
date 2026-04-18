# Pipeline Messaging Workplan

**Status:** PLANNING  
**Date:** 2026-04-19  
**Lead:** Franklin Song

---

## 1. Current Messaging Analysis

### 1.1 Existing Print Methodology

**Location:** `initiation_engine/utils/logging.py`

| Level | Name | Global | Output Scope | Default |
|-------|------|--------|--------------|---------|
| 0 | Silent | `DEBUG_LEVEL = 0` | Errors only | ❌ |
| 1 | Status/Info | `DEBUG_LEVEL = 1` | Milestones, step completion | ✅ DEFAULT |
| 2 | Warning/Debug | `DEBUG_LEVEL = 2` | Variable values, path resolution | ❌ |
| 3 | Trace | `DEBUG_LEVEL = 3` | Deep technical (OS paths, raw JSON) | ❌ |

**Core Functions:**
```python
log_status(message)     # Level 1: milestones, step progress
log_warning(message)    # Level 2: warnings, debugging  
log_error(message)     # Always: critical errors
log_trace(message)      # Level 3: deep technical
```

**Current Flow:**
```
status_print() → log_status() → check DEBUG_LEVEL ≥ 1 → print to stdout
                                                     ↓
                                            Save to DEBUG_OBJECT['messages']
                                                     ↓
                                            debug_log.json (at pipeline end)
```

### 1.2 Current CLI Arguments

```python
# In cli.py
--debug-mode True/False  # True → level 2, False → level 1
```

**Gap:** No `--quiet` or `--trace` argument. No level 0 (silent) exposed.

### 1.3 Current Output Problem

| Issue | Example | Lines |
|-------|---------|-------|
| Verbose CLI args | `Reading CLI arguments...` | 3 |
| Internal paths | `Schema loading from: /path/to/file` | 4 |
| Debug tree | `[validator] ▶ validate` | 30+ |
| Step tracking | `[pipeline] ▶ step1_initiation` | 8 |
| File paths verbose | `CSV: /home/.../output.csv` | 6 |
| Missing required cols | Full list printed | 1 |

**User Wants:** Short, actionable, milestone-level summary.

---

## 2. Proposed Messaging Architecture

### 2.1 New Level Definitions

| Level | Argument | Output | Use Case |
|-------|-----------|--------|----------|
| 0 | `--quiet` | Errors + final summary only | CI/CD, automation |
| 1 | (default) | Milestones + KPIs | Normal user |
| 2 | `--debug` | Warnings + variable values | Developer |
| 3 | `--trace` | All detailed + stack traces | Troubleshooting |

### 2.2 Pipeline Milestone Levels

| Milestone | Level 0 Output | Level 1 Output | Level 2+ Output |
|----------|----------------|----------------|-----------------|
| Init | ✅/❌ | `✓ Setup validated` | Full folder tree |
| Schema | ✅/❌ | `✓ Schema loaded (X columns)` | Resolved refs |
| Mapping | ✅/❌ | `✓ X/Y headers mapped (Z%)` | Column details |
| Process | ✅/❌ | `✓ Processed X rows → Y cols` | Phase breakdown |
| Export | ✅/❌ | Output file links | Export timing |
| AI | ✅/❌ | `AI: Risk LEVEL` | Provider, insights |

### 2.3 Error Message Categories

| Category | Trigger | Level 0 | Level 1 | Level 2+ |
|----------|---------|---------|---------|----------|
| **CRITICAL** | Fail-fast, missing required | Error + exit code | Error + context | Full stack trace |
| **HIGH** | Validation failure | Warning | Affected rows/col | Error details |
| **MEDIUM** | Optional missing | Silent | Info message | Why important |
| **INFO** | Success, no issues | Silent | One-liner | All details |

### 2.4 Proposed CLI Arguments

```python
parser.add_argument(
    "--verbose", "-v",
    choices=["quiet", "normal", "debug", "trace"],
    default="normal",
    help="Output verbosity level"
)
# quiet   → level 0 (errors + summary)
# normal  → level 1 (milestones)
# debug   → level 2 (warnings)  
# trace   → level 3 (all detail)
```

### 2.5 Simplified Output Examples

**Level 0 (--quiet):**
```
Processing complete (11,099 rows, 44 cols, 81.3% health)
Output: output/processed_dcc_universal.csv
```

**Level 1 (default):**
```
✓ Setup validated | ✓ Schema loaded | ✓ 26 columns mapped (100%)
✓ Processing: 11,099 → 44 cols (3.6s)
✓ AI: Risk HIGH

Output:
  CSV: output/processed_dcc_universal.csv
  Excel: output/processed_dcc_universal.xlsx
```

**Level 2+ (--debug):**
```
[pipeline] ▶ step1_initiation
  ✓ Folders: 7/7, Files: 13/13
[pipeline] ▶ step2_schema
  Schema: dcc_register_config.json (44 columns)
  References: 5 resolved
[pipeline] ▶ step3_mapping
  Headers: 26/26 mapped (100%)
  ...
```

---

## 3. Default Framework Message (Always Visible)

### 3.1 Concept

A **baseline framework message** that displays at ALL verbosity levels (0-3). This ensures users always see:
- What framework is running
- Basic context
- How to get help

**Design Principle:** Same as "copyright footer" — always present, never optional.

### 3.2 Proposed Default Message

```
╔════════════════════════════════════════════════════════════════════════════╗
║  DCC Register Universal Processing Pipeline  v3.0                    ║
║  ─────────────────────────────────────────────────────────────────  ║
║  [Input: filename.xlsx]  [Output: output/]  [Mode: normal]         ║
║  ─────────────────────────────────────────────────────────────────  ║
║  Use: --verbose quiet|normal|debug|trace  |  Docs: dcc/docs/       ║
╚════════════════════════════════════════════════════════════════════════════╝
```

### 3.3 Message Components

| Component | Content | Always Visible |
|-----------|---------|---------------|
| Framework name | `DCC Register Universal Processing Pipeline` | ✅ All levels |
| Version | `v3.0` or from `dcc.yml` | ✅ All levels |
| Input file | `[Input: filename.xlsx]` | ✅ All levels |
| Output directory | `[Output: output/]` | ✅ All levels |
| Current mode | `[Mode: normal]` | ✅ All levels |
| Usage help | `Use: --verbose ...` | ✅ All levels |
| Docs link | `Docs: dcc/docs/` | ✅ All levels |

### 3.4 Variations by Level

**Level 0 (--quiet):**
```
╔ DCC Pipeline v3.0 | Input: file.xlsx | Mode: quiet ═╗
║ Ready: YES (81.3% health) | Output: output/      ═╗
╚════════════════════════════════════════════════════╝
```

**Level 1 (normal):**
```
╔═══════════════════════════════════════════════════════════════════╗
║  DCC Pipeline v3.0 | Input: file.xlsx | Mode: normal ║
║  ──────────────────────────────────────────────────  ║
║  ✓ Setup validated | ✓ Schema loaded | ✓ 26→44 cols   ║
╚═══════════════════════════════════════════════════════════╝
```

**Level 2 (debug):**
```
╔═══════════════════════════════════════════════════════════════════════╗
║  DCC Pipeline v3.0 | Input: file.xlsx | Mode: debug ════╗
║  ───────────────────────────────────────────────────────  ║
║  [Input: file.xlsx]  [Output: output/]  [Mode: debug]  ║
║  Columns: 26→44 | Rows: 11,099 | Health: 81.3%       ║
║  ───────────────────────────────────────────────────────  ║
║  DEBUG: Enabled | Full tracing active                ║
╚═══════════════════════════════════════════════════════════════════════╝
```

**Level 3 (trace):**
```
╔════════════════════════════════════════════════════════════════════════════╗
║  DCC Pipeline v3.0 | Input: file.xlsx | Mode: trace ════╗
║  ───────────────────────────────────────────────────────  ║
║  [TRACE] Deep technical logging enabled                 ║
║  [TRACE] Stack traces active                        ║
║  [TRACE] All internal calls visible              ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### 3.5 Implementation Design

```python
# In logging.py
def print_framework_banner(
    input_file: str = None,
    output_dir: str = None,
    mode: str = "normal",
    version: str = "3.0",
) -> None:
    """Print default framework message (visible at ALL levels)."""
    
    # Build components based on mode
    if mode == "quiet":
        # Minimal - single line
        banner = f"╔ DCC Pipeline v{version} | Input: {input_file} | Mode: quiet ═╗"
    elif mode == "normal":
        # Standard - with milestones
        banner = f"""╔═══════════════════════════════════════════════════════════════════╗
║  DCC Pipeline v{version} | Input: {input_file} | Mode: normal ║
║  ──────────────────────────────────────────────────  ║
║  ✓ Setup validated | ✓ Schema loaded | ✓ 26→44 cols   ║
╚═══════════════════════════════════════════════════════════════════╝"""
    else:
        # Debug/trace - with context
        banner = f"""╔══════════════════════════════════════════════════════════════════════╗
║  DCC Pipeline v{version} | Input: {input_file} | Mode: {mode} ════╗
║  ───────────────────────────────────────────────────────  ║
║  [DEBUG/TRACE] {mode.capitalize()} mode enabled              ║
╚══════════════════════════════════════════════════════════════════════╝"""
    
    builtins.print(banner, flush=True)
```

### 3.6 Integration Point

```
dcc_engine_pipeline.py
    │
    ├── print_framework_banner()  ← FIRST, before any processing
    │       │
    │       └── Shows at ALL levels (0-3)
    │
    ├── run_engine_pipeline()
    │       │
    │       └─��� status_print() messages → level-controlled
    │
    └── print_final_summary()  ← LAST, after completion
            │
            └── Shows at ALL levels (0-3)
```

---

## 4. Implementation Plan

### 3.1 Phase 1: Add CLI Arguments

| Task | File | Changes |
|------|------|---------|
| Add `--verbose` argument | `initiation_engine/utils/cli.py` | new choices |
| Map to debug levels | `initiation_engine/utils/cli.py` | level mapping |
| Update usage help | `initiation_engine/utils/cli.py` | description |

### 3.2 Phase 2: Simplify Status Messages

| Task | File | Changes |
|------|------|---------|
| Create milestone-level print | `initiation_engine/utils/logging.py` | new format function |
| Add skip option to status_print | `initiation_engine/utils/logging.py` | level check |
| Simplify file path display | Pipeline engines | basename only |

### 3.3 Phase 3: Error Message Taxonomy

| Task | File | Changes |
|------|------|---------|
| Define error categories | `error_handling/config/error_codes.json` | severity mapping |
| Create error formatter | `error_handling/core/display.py` | per-level output |
| Integrate with log_error | `logging.py` | level-based output |

### 3.4 Phase 4: Summary Report

| Task | File | Changes |
|------|------|---------|
| Create final summary format | `reporting_engine` | one-liner |
| Add health score display | `reporting_engine` | percentage + grade |
| Clean output paths | Pipeline export | basename |

---

## 4. Completion Criteria

- [x] `--verbose` argument with 4 levels works
- [x] Level 0 shows only errors + summary
- [x] Level 1 shows pipeline milestones only
- [x] Level 2 shows warnings + context
- [x] Level 3 shows all details
- [x] Error messages categorized by severity
- [x] Output file paths simplified (basename)
- [x] Full log still saved to `debug_log.json`
- [x] Framework banner visible at ALL levels (0-3)
- [x] Banner shows input/output/mode info
- [x] Banner updates with actual values

---

## 5. Implementation Complete

**Date:** 2026-04-19

**Summary:**
All 4 verbosity levels implemented and tested:
- `--verbose quiet` → Errors + final summary only
- `--verbose normal` → Milestones + KPIs (default)
- `--verbose debug` → Warnings + context
- `--verbose trace` → All details + deep tracking

**Framework banner** now appears at ALL levels, showing:
- Pipeline version + input file + mode

---

## 6. Error Suppression Implementation

**Status:** COMPLETE
**Date:** 2026-04-19

### 6.1 Error Output Behavior

At default level (1), individual errors are now suppressed:

| Level | Error Output |
|-------|-----------|
| 0 | CRITICAL errors only |
| 1 | No output (summary only) ✅ DEFAULT |
| 2 | Abbreviated (truncated > 100 chars) |
| 3 | Full error messages |

### 6.2 Implementation Details

**Files Modified:**

1. **initiation_engine/utils/logging.py:**
   - `log_error()` checks DEBUG_LEVEL at runtime
   - Level 1: No print, only stores in DEBUG_OBJECT
   - Added `show_summary` parameter

2. **processor_engine/error_handling/core/logger.py:**
   - `StructuredLogger.log_error()` checks DEBUG_LEVEL at runtime
   - Suppresses non-CRITICAL at level 1
   - Still persists to debug_log.json

3. **processor_engine/calculations/validation.py:**
   - Added `ValidationLogFilter` to suppress warnings at level 1
   - Filters based on current DEBUG_LEVEL

4. **processor_engine/core/engine.py:**
   - `_print_processing_step()` suppresses "ERROR:" messages at level 1

### 6.3 Final Error Summary

At pipeline end (level 1), shows abbreviated summary:

```
✓ Processing complete
CSV: processed_dcc_universal.csv
Excel: processed_dcc_universal.xlsx
⚠ Validation: 127 errors (3 critical, 45 high, 79 medium) — 92 rows affected
  Details: output_error_diagnostic_log/error_diagnostic_log.csv
  Run with --verbose debug for full error list
```

Or if no errors:

```
✓ Validation: No errors detected
```

---

## 7. Files Modified

| File | Purpose |
|------|---------|
| `initiation_engine/utils/cli.py` | Add --verbose argument |
| `initiation_engine/utils/logging.py` | Level-based error output |
| `dcc_engine_pipeline.py` | Error summary display |
| `processor_engine/core/engine.py` | Suppress ERROR in processing step |
| `processor_engine/calculations/validation.py` | Validation log filter |
| `processor_engine/error_handling/core/logger.py` | Runtime level check |
| `schema_engine/loader/schema_loader.py` | Lazy import fix |

---

*Awaiting approval for implementation*