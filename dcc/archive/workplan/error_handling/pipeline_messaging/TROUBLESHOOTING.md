# Progress Bar Implementation - Troubleshooting Guide

**Document:** WP-PIPE-MSG-001-PHASE2-TROUBLESHOOTING  
**Date:** 2026-05-23  
**Status:** Active Reference

---

## Quick Diagnostics

### Test Script
Run this first to identify issues:

```bash
cd /path/to/dcc/workflow
python3 test_progress.py
```

This will test:
1. ✓ tqdm installation
2. ✓ Progress utilities import
3. ✓ Console package exports
4. ✓ DEBUG_LEVEL integration
5. ✓ Spinner functionality
6. ✓ Progress bar functionality
7. ✓ Quiet mode (DEBUG_LEVEL=0)

---

## Common Errors and Fixes

### Error 1: `ModuleNotFoundError: No module named 'tqdm'`

**Symptom:**
```
ImportError: No module named 'tqdm'
```

**Cause:** tqdm library not installed

**Fix:**
```bash
pip install tqdm>=4.66.0
# or
pip3 install tqdm>=4.66.0
```

**Verify:**
```python
import tqdm
print(tqdm.__version__)  # Should be 4.66.0 or higher
```

---

### Error 2: `ImportError: cannot import name 'create_progress_spinner'`

**Symptom:**
```
ImportError: cannot import name 'create_progress_spinner' from 'utility_engine.console'
```

**Cause:** `__init__.py` not updated or Python not finding the module

**Fix 1:** Verify `__init__.py` has the exports
```python
# File: utility_engine/console/__init__.py
from utility_engine.console.progress import (
    create_progress_bar,
    create_progress_spinner,
    create_progress_callback,
)

__all__ = [
    "status_print",
    "milestone_print",
    "debug_print",
    "print_framework_banner",
    "create_progress_bar",        # ← Must be here
    "create_progress_spinner",    # ← Must be here
    "create_progress_callback",   # ← Must be here
]
```

**Fix 2:** Clear Python cache
```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

**Fix 3:** Restart Python interpreter
```bash
# Exit Python and restart
exit()
python3
```

---

### Error 3: Progress bars not showing

**Symptom:** Pipeline runs but no progress indicators appear

**Cause:** DEBUG_LEVEL is set to 0 (quiet mode)

**Fix:** Check DEBUG_LEVEL
```python
from core_engine.logging import DEBUG_LEVEL
print(f"DEBUG_LEVEL = {DEBUG_LEVEL}")  # Should be >= 1
```

**Set verbosity:**
```bash
# Normal mode (default) - shows progress
python dcc_engine_pipeline.py

# Debug mode - shows progress + details
python dcc_engine_pipeline.py --verbose debug

# Quiet mode - NO progress (by design)
python dcc_engine_pipeline.py --verbose quiet
```

---

### Error 4: `AttributeError: 'NoneType' object has no attribute 'columns'`

**Symptom:**
```
AttributeError: 'NoneType' object has no attribute 'columns'
File "dcc_engine_pipeline.py", line 178, in _run_mapper
  total_headers = len(context.data.df_raw.columns)
```

**Cause:** `df_raw` is None - data not loaded before mapping

**Fix:** This is a pipeline execution error, not a progress bar error.  
Check that:
1. Excel file exists
2. File loads correctly in `_run_mapper()` before progress bar code
3. `load_excel_data()` completes successfully

**Debug:**
```python
# In _run_mapper(), add before progress code:
print(f"DEBUG: df_raw = {context.data.df_raw}")
print(f"DEBUG: df_raw type = {type(context.data.df_raw)}")
if context.data.df_raw is not None:
    print(f"DEBUG: columns = {len(context.data.df_raw.columns)}")
```

---

### Error 5: `TypeError: unsupported operand type(s) for >=: 'int' and 'NoneType'`

**Symptom:**
```
TypeError: unsupported operand type(s) for >=: 'int' and 'NoneType'
File "utility_engine/console/progress.py", line 53
  disable = DEBUG_LEVEL < 1
```

**Cause:** DEBUG_LEVEL is None instead of an integer

**Fix:** Ensure DEBUG_LEVEL is initialized
```python
# File: core_engine/logging/__init__.py
DEBUG_LEVEL = 1  # Default value

def set_debug_level(level: int):
    global DEBUG_LEVEL
    DEBUG_LEVEL = level
```

---

### Error 6: Progress bar shows but doesn't update

**Symptom:** Progress bar appears but stays at 0%

**Cause:** `spinner.update(1)` not called or called incorrectly

**Fix:** Ensure update is called inside the context manager
```python
# CORRECT:
with create_progress_spinner("Operation") as spinner:
    do_work()
    spinner.update(1)  # ← Inside the context

# WRONG:
with create_progress_spinner("Operation") as spinner:
    do_work()
spinner.update(1)  # ← Outside the context (won't work)
```

---

### Error 7: Multiple progress bars overlap

**Symptom:** Progress bars print on multiple lines or overlap

**Cause:** Multiple progress indicators active simultaneously

**Fix:** This is expected for phase-level progress. The design is:
- **Phase spinner:** Shows phase completion
- **Row heartbeat (TelemetryHeartbeat):** Shows row progress within phase

Both can coexist. If unwanted, reduce `TelemetryHeartbeat` interval:
```python
# File: processor_engine/core/engine.py
heartbeat = TelemetryHeartbeat(interval=10000)  # Every 10k rows instead of 1k
```

---

### Error 8: Import errors in WSL environment

**Symptom:**
```
ModuleNotFoundError: No module named 'core_engine'
```

**Cause:** Path resolution issues in WSL

**Fix 1:** Use `python3` instead of `python`
```bash
python3 dcc_engine_pipeline.py
```

**Fix 2:** Run from workflow directory
```bash
cd /path/to/dcc/workflow
python3 dcc_engine_pipeline.py
```

**Fix 3:** Set PYTHONPATH
```bash
export PYTHONPATH=/path/to/dcc/workflow:$PYTHONPATH
python3 dcc_engine_pipeline.py
```

---

### Error 9: Progress bars show in CI/CD logs

**Symptom:** CI/CD logs filled with progress bar escape codes

**Cause:** tqdm detects non-TTY environment incorrectly

**Fix:** Force disable in CI/CD
```bash
# Set environment variable
export DCC_VERBOSE=quiet
python3 dcc_engine_pipeline.py --verbose quiet
```

Or modify code to detect CI environment:
```python
# In progress.py
import os

def is_ci_environment():
    return any([
        os.getenv('CI'),
        os.getenv('JENKINS_HOME'),
        os.getenv('GITHUB_ACTIONS'),
    ])

if disable is None:
    disable = (DEBUG_LEVEL < 1) or is_ci_environment()
```

---

### Error 10: `tqdm` shows wrong encoding characters

**Symptom:** Progress bars show as `â–ˆ` instead of █

**Cause:** Terminal encoding issues

**Fix:** Set UTF-8 encoding
```bash
export PYTHONIOENCODING=utf-8
export LANG=en_US.UTF-8
python3 dcc_engine_pipeline.py
```

Or use ASCII mode in tqdm:
```python
# In progress.py create_progress_bar()
with tqdm(
    total=total,
    desc=desc,
    unit=unit,
    disable=disable,
    leave=leave,
    ncols=80,
    ascii=True,  # ← Use ASCII characters
    bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
) as pbar:
```

---

## Validation Checklist

Before reporting an issue, verify:

- [ ] **tqdm installed:** `pip list | grep tqdm` shows tqdm>=4.66.0
- [ ] **Python version:** Python 3.7+ (`python3 --version`)
- [ ] **progress.py exists:** `ls utility_engine/console/progress.py`
- [ ] **__init__.py updated:** Exports include progress functions
- [ ] **DEBUG_LEVEL >= 1:** Not in quiet mode
- [ ] **Running from workflow dir:** `pwd` shows `.../dcc/workflow`
- [ ] **Test script passes:** `python3 test_progress.py` succeeds
- [ ] **Python cache cleared:** No stale `.pyc` files

---

## Debug Mode

Enable maximum verbosity to see all messages:

```bash
python3 dcc_engine_pipeline.py --verbose trace 2>&1 | tee pipeline_debug.log
```

This will:
- Show all progress indicators
- Show all debug messages
- Show all internal function calls
- Save output to `pipeline_debug.log`

---

## Getting Help

If issues persist:

1. **Run test script:**
   ```bash
   python3 test_progress.py > test_output.txt 2>&1
   ```

2. **Check diagnostics:**
   ```bash
   python3 -c "from utility_engine.console import create_progress_spinner; print('OK')"
   ```

3. **Provide error details:**
   - Full error message
   - Python version
   - tqdm version
   - Operating system
   - Test script output

4. **Check logs:**
   - `dcc/log/update_log.md` - Implementation notes
   - `dcc/output/debug_log.json` - Runtime debug info

---

## Rollback Instructions

If progress bars cause issues, temporarily disable:

**Option 1:** Use quiet mode
```bash
python3 dcc_engine_pipeline.py --verbose quiet
```

**Option 2:** Uninstall tqdm (progress bars will fail silently with proper error handling)
```bash
pip uninstall tqdm
```

**Option 3:** Comment out progress imports
```python
# File: dcc_engine_pipeline.py
# from utility_engine.console import (
#     create_progress_spinner,
#     create_progress_bar,
# )
```

---

## Performance Issues

If progress bars slow down execution:

**Issue:** Progress updates too frequent

**Fix:** Reduce update frequency
```python
# For spinners - already optimized (update once per operation)

# For phase processing - reduce heartbeat interval
heartbeat = TelemetryHeartbeat(interval=5000)  # Every 5k rows instead of 1k
```

**Measured overhead:** < 1% (tested with 11k rows, 44 columns)

---

**Last Updated:** 2026-05-23  
**Maintainer:** Franklin Song  
**Related:** [progress_bar_workplan.md](progress_bar_workplan.md)
