@echo off
REM DCC Pipeline Debug Test Runner (Windows)
REM This script runs the comprehensive test suite for dcc_engine_pipeline.py

echo ==================================
echo DCC Pipeline Debug Test Runner
echo ==================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set DCC_DIR=%SCRIPT_DIR%..

REM Change to DCC directory
cd /d "%DCC_DIR%" || exit /b 1

echo Current Directory: %CD%
echo Pipeline File: workflow\dcc_engine_pipeline.py
echo Test Script: test\test_pipeline_debug.py
echo.

REM Check if Python is available
where python3 >nul 2>nul
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=python3
    goto :run_test
)

where python >nul 2>nul
if %ERRORLEVEL% == 0 (
    set PYTHON_CMD=python
    goto :run_test
)

echo Error: Python is not installed or not in PATH
echo Please install Python 3.8+ to run this test suite
exit /b 1

:run_test
echo Using Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Check if verbose flag is passed
if "%1"=="--verbose" goto :verbose
if "%1"=="-v" goto :verbose
goto :normal

:verbose
echo Running in VERBOSE mode...
echo.
%PYTHON_CMD% test\test_pipeline_debug.py --verbose
goto :check_result

:normal
echo Running tests... (use --verbose for detailed output)
echo.
%PYTHON_CMD% test\test_pipeline_debug.py
goto :check_result

:check_result
set EXIT_CODE=%ERRORLEVEL%

echo.
if %EXIT_CODE% == 0 (
    echo All tests passed!
) else (
    echo Some tests failed. See details above.
    echo    Run with --verbose for more information:
    echo    test\run_pipeline_debug_test.bat --verbose
)

exit /b %EXIT_CODE%
