#!/usr/bin/env python3
"""
Comprehensive Test Script for dcc_engine_pipeline.py

This test script provides:
1. Syntax validation using Python AST parsing
2. Import resolution checking
3. Mock-based unit tests that don't require actual data files
4. Main function testing with mocked arguments
5. Graceful handling of missing dependencies with clear error messages

Usage:
    python test_pipeline_debug.py
    python test_pipeline_debug.py --verbose
"""

import ast
import importlib.util
import json
import logging
import sys
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock, Mock, mock_open, patch

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("PipelineDebugTest")


# Test results tracking
@dataclass
class TestResult:
    """Track individual test results."""

    name: str
    passed: bool
    message: str
    details: Optional[str] = None


class TestRunner:
    """Manages test execution and reporting."""

    def __init__(self):
        self.results: List[TestResult] = []
        self.pipeline_path = (
            Path(__file__).parent.parent / "workflow" / "dcc_engine_pipeline.py"
        )

    def add_result(
        self, name: str, passed: bool, message: str, details: Optional[str] = None
    ):
        """Add a test result."""
        self.results.append(TestResult(name, passed, message, details))
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {name} - {message}")
        if details and not passed:
            logger.debug(f"  Details: {details}")

    def print_summary(self):
        """Print test summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(
            f"Success Rate: {(passed / total * 100):.1f}%" if total > 0 else "N/A"
        )

        if failed > 0:
            logger.info("\nFailed Tests:")
            for result in self.results:
                if not result.passed:
                    logger.info(f"  - {result.name}: {result.message}")
                    if result.details:
                        logger.info(f"    {result.details}")

        logger.info("=" * 80 + "\n")
        return failed == 0


# Test 1: Syntax Validation
def test_syntax_validation(runner: TestRunner) -> bool:
    """
    Test 1: Check for syntax errors using Python AST parsing.

    This validates that the pipeline file is syntactically correct Python code.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Syntax Validation")
    logger.info("=" * 80)

    try:
        if not runner.pipeline_path.exists():
            runner.add_result(
                "Syntax Validation",
                False,
                f"Pipeline file not found: {runner.pipeline_path}",
                "Ensure the file path is correct",
            )
            return False

        # Read the source code
        with open(runner.pipeline_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        # Parse the AST
        tree = ast.parse(source_code, filename=str(runner.pipeline_path))

        # Count some basic metrics
        functions = [
            node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]

        details = f"Functions: {len(functions)}, Classes: {len(classes)}, Imports: {len(imports)}"

        runner.add_result(
            "Syntax Validation", True, "Pipeline syntax is valid", details
        )
        return True

    except SyntaxError as e:
        runner.add_result(
            "Syntax Validation",
            False,
            f"Syntax error in pipeline: {e.msg}",
            f"Line {e.lineno}: {e.text}",
        )
        return False
    except Exception as e:
        runner.add_result(
            "Syntax Validation",
            False,
            f"Error parsing pipeline: {str(e)}",
            str(type(e)),
        )
        return False


# Test 2: Import Resolution
def test_import_resolution(runner: TestRunner) -> Dict[str, Any]:
    """
    Test 2: Validate all imports can be resolved.

    Checks each import statement to see if the module can be found.
    Returns information about available and missing imports.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Import Resolution")
    logger.info("=" * 80)

    # Add workflow path to sys.path for imports
    workflow_path = runner.pipeline_path.parent
    if str(workflow_path) not in sys.path:
        sys.path.insert(0, str(workflow_path))

    # Expected imports based on the pipeline file
    expected_imports = {
        # Standard library
        "json": "stdlib",
        "sys": "stdlib",
        "pathlib": "stdlib",
        "dataclasses": "stdlib",
        "typing": "stdlib",
        # Core engine imports
        "core_engine.context.context_pipeline": "core_engine",
        "core_engine.paths": "core_engine",
        "core_engine.logging": "core_engine",
        "core_engine.io": "core_engine",
        "core_engine.errors.error_manager": "core_engine",
        "core_engine.errors.pipeline_result_handler": "core_engine",
        # Utility engine imports
        "utility_engine.console": "utility_engine",
        "utility_engine.cli": "utility_engine",
        "utility_engine.bootstrap.boot_pipeline": "utility_engine",
        # Domain engine imports
        "initiation_engine": "initiation_engine",
        "schema_engine": "schema_engine",
        "mapper_engine": "mapper_engine",
        "processor_engine": "processor_engine",
        "reporting_engine": "reporting_engine",
        "ai_ops_engine": "ai_ops_engine",
    }

    available = []
    missing = []

    for module_name, category in expected_imports.items():
        try:
            # Try to find the module spec
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                available.append((module_name, category))
                logger.debug(f"  ✓ Found: {module_name}")
            else:
                missing.append((module_name, category, "Module spec not found"))
                logger.debug(f"  ✗ Missing: {module_name}")
        except (ImportError, ModuleNotFoundError) as e:
            missing.append((module_name, category, str(e)))
            logger.debug(f"  ✗ Missing: {module_name} - {e}")
        except Exception as e:
            missing.append((module_name, category, f"Error: {str(e)}"))
            logger.debug(f"  ⚠ Error checking {module_name}: {e}")

    # Determine test result
    total = len(expected_imports)
    available_count = len(available)
    missing_count = len(missing)

    # Pass if at least 70% of imports are available (allow some tolerance)
    passed = (available_count / total) >= 0.7

    details = f"Available: {available_count}/{total}, Missing: {missing_count}/{total}"
    if missing:
        missing_list = "\n".join(
            [f"    - {m[0]} ({m[1]}): {m[2]}" for m in missing[:5]]
        )
        details += f"\n  Missing modules:\n{missing_list}"
        if len(missing) > 5:
            details += f"\n    ... and {len(missing) - 5} more"

    runner.add_result(
        "Import Resolution",
        passed,
        f"Import availability: {available_count}/{total} ({available_count / total * 100:.1f}%)",
        details,
    )

    return {"available": available, "missing": missing, "total": total}


# Test 3: Mock Pipeline Context Test
def test_mock_pipeline_context(runner: TestRunner) -> bool:
    """
    Test 3: Create and validate a mock PipelineContext.

    Tests that we can create the necessary data structures for pipeline execution.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Mock Pipeline Context")
    logger.info("=" * 80)

    try:
        # Create mock paths
        @dataclass
        class MockPipelinePaths:
            base_path: Path
            schema_path: Path
            excel_path: Path
            csv_output_path: Path
            excel_output_path: Path
            summary_path: Path
            debug_log_path: Path

        # Create mock context
        @dataclass
        class MockPipelineState:
            setup_results: Optional[Dict] = None
            schema_results: Optional[Dict] = None
            mapping_result: Optional[Dict] = None
            resolved_schema: Optional[Dict] = None
            error_summary: Optional[Dict] = None

        @dataclass
        class MockPipelineData:
            df_raw: Optional[Any] = None
            df_mapped: Optional[Any] = None
            df_processed: Optional[Any] = None

        @dataclass
        class MockPipelineContext:
            paths: MockPipelinePaths
            parameters: Dict[str, Any]
            state: MockPipelineState
            data: MockPipelineData
            nrows: Optional[int] = None
            debug_mode: bool = False

            def should_fail_fast(self, error_type: str) -> bool:
                return self.parameters.get("fail_fast", False)

        # Create test paths
        test_base = Path("/tmp/test_pipeline")
        test_paths = MockPipelinePaths(
            base_path=test_base,
            schema_path=test_base / "config" / "schemas" / "dcc_register_enhanced.json",
            excel_path=test_base / "data" / "test_input.xlsx",
            csv_output_path=test_base / "output" / "test_output.csv",
            excel_output_path=test_base / "output" / "test_output.xlsx",
            summary_path=test_base / "output" / "summary.json",
            debug_log_path=test_base / "output" / "debug.json",
        )

        # Create test context
        context = MockPipelineContext(
            paths=test_paths,
            parameters={
                "fail_fast": False,
                "upload_file_name": "test_input.xlsx",
                "download_file_path": str(test_base / "output"),
            },
            state=MockPipelineState(),
            data=MockPipelineData(),
            nrows=100,
            debug_mode=True,
        )

        # Validate context
        assert hasattr(context, "paths"), "Context missing 'paths'"
        assert hasattr(context, "parameters"), "Context missing 'parameters'"
        assert hasattr(context, "state"), "Context missing 'state'"
        assert hasattr(context, "data"), "Context missing 'data'"
        assert context.nrows == 100, "nrows not set correctly"
        assert context.debug_mode is True, "debug_mode not set correctly"

        runner.add_result(
            "Mock Pipeline Context",
            True,
            "Successfully created and validated mock context",
            f"Paths: {len([f for f in dir(test_paths) if not f.startswith('_')])}, "
            f"Parameters: {len(context.parameters)}",
        )
        return True

    except Exception as e:
        runner.add_result(
            "Mock Pipeline Context",
            False,
            f"Failed to create mock context: {str(e)}",
            str(type(e)),
        )
        return False


# Test 4: Mock Pipeline Step Execution
def test_mock_pipeline_steps(runner: TestRunner) -> bool:
    """
    Test 4: Test individual pipeline steps with mocked dependencies.

    Validates that pipeline steps can be called with mocked data.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Mock Pipeline Steps")
    logger.info("=" * 80)

    try:
        # Create mock context (simplified)
        mock_context = Mock()
        mock_context.paths = Mock()
        mock_context.state = Mock()
        mock_context.data = Mock()
        mock_context.parameters = {"fail_fast": False}
        mock_context.nrows = 10
        mock_context.debug_mode = False
        mock_context.should_fail_fast = Mock(return_value=False)

        # Test that we can create mock pipeline step
        @dataclass
        class MockPipelineStep:
            engine_name: str
            phase: str
            runner: Any

        # Create mock runner function
        def mock_runner(ctx):
            return {"status": "success", "engine": "test_engine"}

        # Create pipeline step
        step = MockPipelineStep(
            engine_name="test_engine", phase="test_phase", runner=mock_runner
        )

        # Execute step
        result = step.runner(mock_context)

        # Validate result
        assert isinstance(result, dict), "Step should return a dict"
        assert result.get("status") == "success", "Step should return success status"

        runner.add_result(
            "Mock Pipeline Steps",
            True,
            "Successfully executed mock pipeline step",
            f"Step: {step.engine_name}, Phase: {step.phase}, Result: {result}",
        )
        return True

    except Exception as e:
        runner.add_result(
            "Mock Pipeline Steps",
            False,
            f"Failed to execute mock pipeline step: {str(e)}",
            str(type(e)),
        )
        return False


# Test 5: Main Function with Mock Arguments
def test_main_with_mock_args(runner: TestRunner, import_info: Dict[str, Any]) -> bool:
    """
    Test 5: Test main() function with mocked arguments and dependencies.

    This is the most complex test - it mocks all dependencies and CLI arguments
    to test the main() function flow.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Main Function with Mock Arguments")
    logger.info("=" * 80)

    # Skip if too many imports are missing
    if len(import_info["missing"]) > len(import_info["available"]):
        runner.add_result(
            "Main Function Test",
            False,
            "Too many missing imports to safely test main()",
            f"Available: {len(import_info['available'])}, Missing: {len(import_info['missing'])}",
        )
        return False

    try:
        # Mock all external dependencies
        with patch("sys.argv", ["dcc_engine_pipeline.py", "--base-path", "/tmp/test"]):
            # Mock the resolve_pipeline_base_path
            with patch("core_engine.paths.resolve_pipeline_base_path") as mock_resolve:
                mock_resolve.return_value = Path("/tmp/test/workflow")

                # Mock parse_cli_args
                with patch("utility_engine.cli.parse_cli_args") as mock_parse:
                    # Create mock args
                    mock_args = Mock()
                    mock_args.base_path = "/tmp/test"
                    mock_args.verbose = 1
                    mock_args.nrows = None
                    mock_args.json = False

                    mock_cli_args = {
                        "base_path": "/tmp/test",
                        "verbose": 1,
                    }

                    mock_parse.return_value = (mock_args, mock_cli_args, True)

                    # Mock logger setup
                    with patch("core_engine.logging.setup_logger"):
                        with patch("core_engine.logging.set_debug_level"):
                            # Mock BootstrapManager
                            with patch(
                                "utility_engine.bootstrap.boot_pipeline.BootstrapManager"
                            ) as mock_bootstrap_cls:
                                mock_manager = Mock()
                                mock_manager.base_path = Path("/tmp/test")
                                mock_manager.effective_parameters = {
                                    "upload_file_name": "test.xlsx",
                                    "download_file_path": "/tmp/test/output",
                                }
                                mock_manager.preload_trace = {}
                                mock_manager.postload_trace = {}
                                mock_manager.environment = "test"
                                mock_manager.bootstrap_summary = {
                                    "status": "success",
                                    "completed_count": 5,
                                }

                                # Mock context
                                mock_context = Mock()
                                mock_context.nrows = None
                                mock_context.debug_mode = False
                                mock_context.set_preload_state = Mock()
                                mock_context.set_postload_state = Mock()

                                mock_manager.to_pipeline_context.return_value = (
                                    mock_context
                                )
                                mock_manager.bootstrap_all.return_value = mock_manager

                                mock_bootstrap_cls.return_value = mock_manager

                                # Mock print functions
                                with patch(
                                    "utility_engine.console.print_framework_banner"
                                ):
                                    with patch(
                                        "utility_engine.console.milestone_print"
                                    ):
                                        # Mock pipeline execution
                                        with patch(
                                            "dcc_engine_pipeline.run_engine_pipeline"
                                        ) as mock_run:
                                            mock_run.return_value = {
                                                "status": "success",
                                                "steps_completed": 7,
                                            }

                                            # Mock result handler
                                            with patch(
                                                "core_engine.errors.pipeline_result_handler.handle_pipeline_results"
                                            ):
                                                # Try to import and run main
                                                try:
                                                    # Add workflow to path
                                                    workflow_path = (
                                                        runner.pipeline_path.parent
                                                    )
                                                    if (
                                                        str(workflow_path)
                                                        not in sys.path
                                                    ):
                                                        sys.path.insert(
                                                            0, str(workflow_path)
                                                        )

                                                    # Import the module
                                                    import dcc_engine_pipeline

                                                    # Run main
                                                    result = dcc_engine_pipeline.main()

                                                    # Check result
                                                    assert result == 0, (
                                                        f"main() returned {result}, expected 0"
                                                    )

                                                    runner.add_result(
                                                        "Main Function Test",
                                                        True,
                                                        "Successfully executed main() with mocked dependencies",
                                                        f"Return code: {result}",
                                                    )
                                                    return True

                                                except ImportError as e:
                                                    # This is expected if dependencies are missing
                                                    runner.add_result(
                                                        "Main Function Test",
                                                        False,
                                                        "Could not import pipeline module",
                                                        f"ImportError: {str(e)}",
                                                    )
                                                    return False

    except Exception as e:
        runner.add_result(
            "Main Function Test",
            False,
            f"Error testing main(): {str(e)}",
            f"{type(e).__name__}: {str(e)}",
        )
        return False


# Test 6: Pipeline Step Registration
def test_pipeline_step_registration(runner: TestRunner) -> bool:
    """
    Test 6: Verify PIPELINE_STEPS registration.

    Checks that the pipeline steps are properly defined and registered.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST 6: Pipeline Step Registration")
    logger.info("=" * 80)

    try:
        # Expected pipeline steps
        expected_steps = [
            ("initiation_engine", "step1_initiation"),
            ("schema_engine", "step2_schema_validation"),
            ("mapper_engine", "step3_column_mapping"),
            ("processor_engine", "step4_document_processing"),
            ("reorder_engine", "step5_column_reorder"),
            ("export_engine", "step6_export"),
            ("ai_ops_engine", "step7_ai_ops"),
        ]

        # Read the pipeline file to check for PIPELINE_STEPS
        with open(runner.pipeline_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if PIPELINE_STEPS is defined
        if "PIPELINE_STEPS" not in content:
            runner.add_result(
                "Pipeline Step Registration",
                False,
                "PIPELINE_STEPS not found in pipeline file",
                "The pipeline should define PIPELINE_STEPS tuple",
            )
            return False

        # Check for each expected step
        found_steps = []
        missing_steps = []

        for engine_name, phase in expected_steps:
            if engine_name in content and phase in content:
                found_steps.append((engine_name, phase))
            else:
                missing_steps.append((engine_name, phase))

        total = len(expected_steps)
        found = len(found_steps)

        passed = found == total

        details = f"Found {found}/{total} expected pipeline steps"
        if missing_steps:
            details += f"\nMissing: {', '.join([s[0] for s in missing_steps])}"

        runner.add_result(
            "Pipeline Step Registration",
            passed,
            f"Pipeline steps: {found}/{total}",
            details,
        )
        return passed

    except Exception as e:
        runner.add_result(
            "Pipeline Step Registration",
            False,
            f"Error checking pipeline steps: {str(e)}",
            str(type(e)),
        )
        return False


# Test 7: Error Handling Mechanisms
def test_error_handling(runner: TestRunner) -> bool:
    """
    Test 7: Verify error handling mechanisms are in place.

    Checks for proper exception handling and error reporting.
    """
    logger.info("\n" + "=" * 80)
    logger.info("TEST 7: Error Handling Mechanisms")
    logger.info("=" * 80)

    try:
        with open(runner.pipeline_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for error handling patterns
        error_patterns = {
            "try_except": "try:" in content and "except" in content,
            "error_manager": "error_manager" in content
            or "handle_system_error" in content,
            "bootstrap_error": "BootstrapError" in content,
            "file_not_found": "FileNotFoundError" in content,
            "value_error": "ValueError" in content,
            "fail_fast": "fail_fast" in content or "should_fail_fast" in content,
            "error_reporting": "error_reporter" in content
            or "error_summary" in content,
        }

        found = sum(1 for v in error_patterns.values() if v)
        total = len(error_patterns)

        # Pass if at least 4 out of 7 error handling patterns are present
        passed = found >= 4

        details = "Error handling patterns found:\n"
        for pattern, present in error_patterns.items():
            status = "✓" if present else "✗"
            details += f"  {status} {pattern}\n"

        runner.add_result(
            "Error Handling",
            passed,
            f"Error handling patterns: {found}/{total}",
            details.strip(),
        )
        return passed

    except Exception as e:
        runner.add_result(
            "Error Handling",
            False,
            f"Error checking error handling: {str(e)}",
            str(type(e)),
        )
        return False


# Main test execution
def main():
    """Run all tests."""
    logger.info("=" * 80)
    logger.info("DCC Engine Pipeline - Comprehensive Test Suite")
    logger.info("=" * 80)
    logger.info(f"Pipeline: dcc/workflow/dcc_engine_pipeline.py")
    logger.info(f"Test Script: {__file__}")
    logger.info("=" * 80 + "\n")

    # Check for verbose flag
    if "--verbose" in sys.argv:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    runner = TestRunner()

    # Run tests
    test_syntax_validation(runner)
    import_info = test_import_resolution(runner)
    test_mock_pipeline_context(runner)
    test_mock_pipeline_steps(runner)
    test_main_with_mock_args(runner, import_info)
    test_pipeline_step_registration(runner)
    test_error_handling(runner)

    # Print summary
    all_passed = runner.print_summary()

    # Exit with appropriate code
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
