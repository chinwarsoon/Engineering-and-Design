# Quick Start - Pipeline Testing

## 🚀 Run the Test Suite

### Option 1: Direct Python (Recommended)
```bash
# From the dcc directory
cd /home/franklin/dsai/Engineering-and-Design/dcc
python3 test/test_pipeline_debug.py
```

### Option 2: Using Shell Script (Linux/WSL/Mac)
```bash
# Make executable (first time only)
chmod +x test/run_pipeline_debug_test.sh

# Run tests
./test/run_pipeline_debug_test.sh

# Verbose mode
./test/run_pipeline_debug_test.sh --verbose
```

### Option 3: Using Batch File (Windows)
```cmd
REM From the dcc directory
test\run_pipeline_debug_test.bat

REM Verbose mode
test\run_pipeline_debug_test.bat --verbose
```

## 📊 What Gets Tested

| Test | Description | Requires Data Files? |
|------|-------------|---------------------|
| 1. Syntax Validation | Checks Python syntax | ❌ No |
| 2. Import Resolution | Validates module imports | ❌ No |
| 3. Mock Pipeline Context | Tests data structures | ❌ No |
| 4. Mock Pipeline Steps | Tests step execution | ❌ No |
| 5. Main Function Test | Tests entry point | ❌ No |
| 6. Pipeline Registration | Verifies 7 engine steps | ❌ No |
| 7. Error Handling | Validates error patterns | ❌ No |

**All tests use mocks - no actual data files needed!**

## ✅ Success Criteria

```
================================================================================
TEST SUMMARY
================================================================================
Total Tests: 7
Passed: 7
Failed: 0
Success Rate: 100.0%
================================================================================
```

## ⚠️ Common Issues

### Issue: "Pipeline file not found"
**Solution:** Run from the `dcc` directory
```bash
cd /home/franklin/dsai/Engineering-and-Design/dcc
python3 test/test_pipeline_debug.py
```

### Issue: "Python not found"
**Solution:** Install Python 3.8+ or use correct command
```bash
# Check Python version
python3 --version

# Or try
python --version
```

### Issue: "Import Resolution fails"
**Expected:** Some imports may be missing in minimal environments
- Test passes if ≥70% of imports are available
- Main function test skips if <70% available
- This is normal and safe

### Issue: "Main Function Test fails"
**Expected:** Requires most dependencies to be available
- Gracefully skips if environment is insufficient
- Run with `--verbose` to see which imports are missing
- Not critical if other tests pass

## 🔍 Verbose Mode

Get detailed information about each test:
```bash
python3 test/test_pipeline_debug.py --verbose
```

Shows:
- Individual import check results
- Detailed error messages
- Stack traces for failures
- Debug-level logging

## 📁 Files Created

- `test/test_pipeline_debug.py` - Main test script (733 lines)
- `test/TEST_PIPELINE_DEBUG_README.md` - Full documentation
- `test/run_pipeline_debug_test.sh` - Linux/Mac runner
- `test/run_pipeline_debug_test.bat` - Windows runner
- `test/QUICK_START_TESTING.md` - This file

## 🎯 Test Philosophy

1. **No infrastructure required** - Uses only mocks
2. **Fails gracefully** - Missing dependencies don't break tests
3. **Clear messages** - Know exactly what failed and why
4. **Quick to run** - Completes in seconds
5. **Safe** - Never modifies actual data or files

## 📖 Next Steps

- **Full docs:** See `TEST_PIPELINE_DEBUG_README.md`
- **Integration testing:** See `test_dcc_engine_pipeline_di.py`
- **With real data:** See `test_pipeline_integration.py`

## 🐛 Reporting Issues

If tests fail unexpectedly:

1. Run with `--verbose` flag
2. Check which specific test failed
3. Review the error message and details
4. Check if the pipeline file has been modified
5. Verify you're in the correct directory

## 🔗 Related Documentation

- Pipeline file: `workflow/dcc_engine_pipeline.py`
- Project structure: `PROJECT_STRUCTURE.md`
- Main README: `README.md`

---

**Last Updated:** 2026-05-23  
**Python Version:** 3.8+  
**Platform:** Cross-platform (Linux, Windows, macOS)
