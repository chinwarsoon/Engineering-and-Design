# DCC Pipeline Debug Test Suite

## Overview

Comprehensive test script for `dcc/workflow/dcc_engine_pipeline.py` that validates the pipeline without requiring actual data files.

**Test Script:** `test/test_pipeline_debug.py`

## Test Coverage

The test suite performs 7 comprehensive tests:

### 1. **Syntax Validation** ✓
- Uses Python AST parsing to check for syntax errors
- Validates the pipeline file is syntactically correct
- Counts functions, classes, and imports
- **No dependencies required**

### 2. **Import Resolution** ✓
- Checks all required module imports can be resolved
- Validates both standard library and custom engine imports
- Provides detailed report of available vs. missing modules
- **Tolerates 30% missing imports** (allows partial environment)

### 3. **Mock Pipeline Context** ✓
- Creates mock `PipelineContext` data structure
- Validates all required attributes are present
- Tests context initialization
- **No actual data files required**

### 4. **Mock Pipeline Steps** ✓
- Tests pipeline step execution with mocked dependencies
- Validates step runner functions work correctly
- Ensures proper data flow through pipeline steps
- **Fully mocked - no external dependencies**

### 5. **Main Function Test** ⚠️
- Tests the `main()` entry point with mocked CLI arguments
- Mocks all external dependencies (BootstrapManager, logger, etc.)
- Validates end-to-end execution flow
- **Requires at least 70% of imports to be available**
- Gracefully skips if environment is insufficient

### 6. **Pipeline Step Registration** ✓
- Verifies all 7 pipeline steps are properly defined:
  - `initiation_engine`
  - `schema_engine`
  - `mapper_engine`
  - `processor_engine`
  - `reorder_engine`
  - `export_engine`
  - `ai_ops_engine`
- **No dependencies required**

### 7. **Error Handling Mechanisms** ✓
- Validates error handling patterns are present:
  - Try/except blocks
  - Error manager integration
  - BootstrapError handling
  - File not found errors
  - Value errors
  - Fail-fast mechanisms
  - Error reporting
- **No dependencies required**

## Usage

### Basic Run

```bash
# From the dcc directory
python test/test_pipeline_debug.py
```

### Verbose Output

```bash
# Shows detailed debug information
python test/test_pipeline_debug.py --verbose
```

### From WSL (Recommended for this project)

```bash
# Navigate to the project
cd /home/franklin/dsai/Engineering-and-Design/dcc

# Run the test
python3 test/test_pipeline_debug.py
```

## Expected Output

```
================================================================================
DCC Engine Pipeline - Comprehensive Test Suite
================================================================================
Pipeline: dcc/workflow/dcc_engine_pipeline.py
Test Script: /path/to/test_pipeline_debug.py
================================================================================

================================================================================
TEST 1: Syntax Validation
================================================================================
✅ PASS: Syntax Validation - Pipeline syntax is valid

================================================================================
TEST 2: Import Resolution
================================================================================
✅ PASS: Import Resolution - Import availability: 18/18 (100.0%)

================================================================================
TEST 3: Mock Pipeline Context
================================================================================
✅ PASS: Mock Pipeline Context - Successfully created and validated mock context

... (and so on)

================================================================================
TEST SUMMARY
================================================================================
Total Tests: 7
Passed: 7
Failed: 0
Success Rate: 100.0%
================================================================================
```

## Test Results Interpretation

### All Tests Pass ✅
- Pipeline file is syntactically valid
- All required imports are available
- Mock structures work correctly
- Main function can execute with mocks
- All pipeline steps are registered
- Error handling is comprehensive

### Some Tests Fail ⚠️

**Syntax Validation Fails:**
- There's a syntax error in the pipeline file
- Check the error message for line number and details

**Import Resolution Fails:**
- Missing critical dependencies (>30% unavailable)
- Check which modules are missing in the details
- Install missing dependencies or run in correct environment

**Mock Tests Fail:**
- Data structure definitions may have changed
- Update mock classes to match actual implementation

**Main Function Test Fails:**
- Too many imports missing (>50%)
- Complex dependency issue
- Try running with `--verbose` for more details

**Pipeline Steps Fail:**
- PIPELINE_STEPS definition is incomplete
- One or more engine steps are missing

**Error Handling Fails:**
- Less than 4/7 error handling patterns found
- Consider adding more robust error handling

## Dependencies

### Required (for full test suite):
- Python 3.8+
- Standard library only (ast, sys, pathlib, etc.)
- unittest.mock (Python standard library)

### Optional (for pipeline execution):
- All custom engine modules (core_engine, utility_engine, etc.)
- These are NOT required for the test to run
- Tests gracefully handle missing dependencies

## Design Philosophy

This test suite follows the principle of **"Test Early, Test Often, Test Without Infrastructure"**:

1. **No Data Files Required** - All tests use mocks
2. **Graceful Degradation** - Tests that can run will run
3. **Clear Error Messages** - Failed tests explain what's wrong
4. **Progressive Validation** - Tests build on each other
5. **Environment Agnostic** - Works even with missing dependencies

## Troubleshooting

### "Pipeline file not found"
```bash
# Check you're running from the correct directory
pwd
# Should be: /path/to/Engineering-and-Design/dcc

# Or use absolute path
python3 /full/path/to/test/test_pipeline_debug.py
```

### "Too many missing imports"
```bash
# Check your Python environment
python3 -c "import sys; print(sys.path)"

# Add workflow to path if needed
export PYTHONPATH="/path/to/Engineering-and-Design/dcc/workflow:$PYTHONPATH"
```

### "Main function test fails"
This is expected in minimal environments. The test will:
1. Check if enough imports are available (>70%)
2. Skip gracefully if not
3. Report which imports are missing

## Integration with CI/CD

This test can be integrated into continuous integration:

```yaml
# Example GitHub Actions
- name: Run Pipeline Debug Tests
  run: |
    cd dcc
    python3 test/test_pipeline_debug.py
  continue-on-error: true  # Allow partial success
```

## Extending the Tests

To add new tests:

1. Create a new test function following the pattern:
```python
def test_your_feature(runner: TestRunner) -> bool:
    logger.info("\n" + "=" * 80)
    logger.info("TEST X: Your Feature")
    logger.info("=" * 80)
    
    try:
        # Your test logic here
        runner.add_result(
            "Your Feature",
            True,
            "Success message",
            "Optional details"
        )
        return True
    except Exception as e:
        runner.add_result(
            "Your Feature",
            False,
            f"Error: {str(e)}",
            str(type(e))
        )
        return False
```

2. Add it to `main()`:
```python
def main():
    # ... existing tests ...
    test_your_feature(runner)
    # ...
```

## Related Files

- **Pipeline:** `dcc/workflow/dcc_engine_pipeline.py`
- **Test Data:** `data/Submittal and RFI Tracker Lists.xlsx` (not required for tests)
- **Schema:** `config/schemas/dcc_register_enhanced.json` (not required for tests)
- **Other Tests:** 
  - `test/test_dcc_engine_pipeline_di.py` - DI integration test
  - `test/test_pipeline_integration.py` - Full integration test

## License

This test suite is part of the DCC Engine Pipeline project.

## Author

Generated for the Engineering and Design DSAI project.

## Last Updated

2026-05-23
