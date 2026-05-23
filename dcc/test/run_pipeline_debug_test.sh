#!/bin/bash

# DCC Pipeline Debug Test Runner
# This script runs the comprehensive test suite for dcc_engine_pipeline.py

echo "=================================="
echo "DCC Pipeline Debug Test Runner"
echo "=================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DCC_DIR="$(dirname "$SCRIPT_DIR")"

# Change to DCC directory
cd "$DCC_DIR" || exit 1

echo "Current Directory: $(pwd)"
echo "Pipeline File: workflow/dcc_engine_pipeline.py"
echo "Test Script: test/test_pipeline_debug.py"
echo ""

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python is not installed or not in PATH"
    echo "Please install Python 3.8+ to run this test suite"
    exit 1
fi

echo "Using Python: $PYTHON_CMD ($($PYTHON_CMD --version))"
echo ""

# Check if verbose flag is passed
if [[ "$1" == "--verbose" || "$1" == "-v" ]]; then
    echo "Running in VERBOSE mode..."
    echo ""
    "$PYTHON_CMD" test/test_pipeline_debug.py --verbose
else
    echo "Running tests... (use --verbose for detailed output)"
    echo ""
    "$PYTHON_CMD" test/test_pipeline_debug.py
fi

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "⚠️  Some tests failed. See details above."
    echo "   Run with --verbose for more information:"
    echo "   ./test/run_pipeline_debug_test.sh --verbose"
fi

exit $EXIT_CODE
