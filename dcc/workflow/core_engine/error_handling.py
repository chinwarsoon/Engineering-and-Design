"""
Error Handling Utilities - Standardized error handling patterns for DCC pipeline.
Provides thin wrappers around PipelineContext error APIs to reduce repetition 
and enforce consistency across orchestrator and engines.
"""
from typing import Any, Dict, Optional

from .context import PipelineContext


def handle_system_error(
    context: Optional[PipelineContext],
    condition: bool,
    code: str,
    message: str,
    details: Optional[str] = None,
    engine: Optional[str] = None,
    phase: Optional[str] = None,
    severity: str = "critical",
    fatal: bool = True,
    print_to_stderr: bool = True
) -> bool:
    """
    Handle a system error condition with context recording and optional stderr output.
    
    Args:
        context: PipelineContext for error recording
        condition: Boolean condition (True = success, False = error)
        code: Error code
        message: Error message
        details: Additional error details
        engine: Engine name where error occurred
        phase: Processing phase where error occurred
        severity: Error severity level
        fatal: Whether error is fatal
        print_to_stderr: Whether to print to stderr (preserves user visibility)
    
    Returns:
        True if condition is True (no error), False if condition is False (error occurred)
    """
    if condition:
        return True
    
    # Record error in context (graceful handling if context is None or missing methods)
    if context is not None and hasattr(context, 'add_system_error'):
        context.add_system_error(
            code=code,
            message=message,
            details=details,
            engine=engine or "unknown",
            phase=phase or "unknown",
            severity=severity,
            fatal=fatal
        )
    
    # Print to stderr for user visibility (preserves existing behavior)
    if print_to_stderr:
        try:
            from utility_engine.errors import system_error_print
            system_error_print(code, detail=details)
        except ImportError:
            # Fallback if utility_engine is not available
            print(f"ERROR [{code}]: {message}")
            if details:
                print(f"Details: {details}")
    
    return False


def handle_data_error(
    context: PipelineContext,
    *,
    condition: bool,
    code: str,
    message: str,
    details: Optional[str] = None,
    engine: Optional[str] = None,
    phase: Optional[str] = None,
    severity: str = "medium",
    fatal: bool = False
) -> bool:
    """
    Standardized data-handling error handling pattern.
    
    Records data validation error in context without printing to stderr
    (data errors are typically handled by processor engine reporting).
    
    Args:
        context: Pipeline context for error tracking
        condition: Validation condition (False = error)
        code: Error code from catalog
        message: Error message
        details: Additional error details
        engine: Engine name reporting the error
        phase: Processing phase where error occurred
        severity: Error severity level
        fatal: Whether error should stop pipeline
        
    Returns:
        bool: True if validation passed, False if error was recorded
    """
    if condition:
        return True
    
    # Record error in context
    context.add_data_error(
        code=code,
        message=message,
        details=details,
        severity=severity,
        engine=engine,
        phase=phase,
        fatal=fatal
    )
    
    return False


def handle_engine_failure(
    context: PipelineContext,
    engine: str,
    phase: Optional[str] = None,
    exception: Optional[Exception] = None,
    code: Optional[str] = None,
    message: Optional[str] = None
) -> None:
    """
    Standardized engine failure handling pattern.
    
    Records engine failure status and captures exception details.
    
    Args:
        context: Pipeline context for error tracking
        engine: Engine name that failed
        phase: Pipeline phase where failure occurred
        exception: Exception that caused failure
        code: Optional custom error code
        message: Optional custom error message
    """
    context.record_engine_failure(
        engine=engine,
        phase=phase,
        exception=exception
    )
    
    # Optional additional error recording
    if code or message:
        context.add_system_error(
            code=code or f"E-ENG-{engine.upper()}-FAIL",
            message=message or f"Engine {engine} failed",
            details=str(exception) if exception else None,
            severity="critical",
            engine=engine,
            phase=phase,
            fatal=True
        )


def check_fail_fast_and_raise(
    context: PipelineContext,
    domain: str = "system",
    exception_message: Optional[str] = None
) -> None:
    """
    Check fail-fast conditions and raise exception if needed.
    
    Args:
        context: Pipeline context for error checking
        domain: Error domain to check ("system" or "data")
        exception_message: Custom message for raised exception
        
    Raises:
        ValueError: If fail-fast conditions are met
    """
    if context.should_fail_fast(domain):
        message = exception_message or f"Fail-fast triggered for {domain} errors"
        raise ValueError(message)


def wrap_engine_execution(
    context: PipelineContext,
    engine_name: str,
    execution_func: callable,
    phase: Optional[str] = None,
    *args,
    **kwargs
) -> Any:
    """
    Wrapper for engine execution with standardized error handling.
    
    Sets engine status, executes function, and handles exceptions consistently.
    
    Args:
        context: Pipeline context for error tracking
        engine_name: Name of the engine being executed
        phase: Pipeline phase for execution
        execution_func: Function to execute
        *args: Arguments to pass to execution function
        **kwargs: Keyword arguments to pass to execution function
        
    Returns:
        Any: Result from execution function
        
    Raises:
        Exception: Re-raises original exception after recording in context
    """
    # Set engine status to running
    context.state.engine_status[engine_name] = "running"
    
    try:
        result = execution_func(*args, **kwargs)
        
        # Set engine status to completed
        context.state.engine_status[engine_name] = "completed"
        
        return result
        
    except Exception as exc:
        # Handle engine failure
        handle_engine_failure(
            context=context,
            engine=engine_name,
            phase=phase,
            exception=exc
        )
        
        # Re-raise original exception
        raise


def generate_error_report(context: PipelineContext) -> Dict[str, Any]:
    """
    Generate comprehensive error report for pipeline completion.
    
    Args:
        context: Pipeline context with error information
        
    Returns:
        Dict[str, Any]: Comprehensive error report
    """
    error_summary = context.get_error_summary()
    system_errors = context.get_system_status_errors()
    data_errors = context.get_data_handling_errors()
    
    return {
        "pipeline_status": "failed" if error_summary["fatal_errors"] > 0 else "completed",
        "error_summary": error_summary,
        "system_status_errors": {
            "count": len(system_errors),
            "errors": system_errors
        },
        "data_handling_errors": {
            "count": len(data_errors),
            "errors": data_errors
        },
        "engine_status": context.state.engine_status,
        "fail_fast_triggered": {
            "system": context.should_fail_fast("system"),
            "data": context.should_fail_fast("data")
        }
    }


# Convenience functions for common patterns

def validate_file_exists(
    context: PipelineContext,
    file_path: Any,  # Path object or string
    error_code: str,
    engine: Optional[str] = None,
    phase: Optional[str] = None
) -> bool:
    """
    Validate that a file exists and record error if not.
    
    Args:
        context: Pipeline context for error tracking
        file_path: Path to validate
        error_code: Error code to use if file doesn't exist
        engine: Engine name performing validation
        phase: Pipeline phase for validation
        
    Returns:
        bool: True if file exists, False otherwise
    """
    from pathlib import Path
    
    path_obj = Path(file_path) if isinstance(file_path, str) else file_path
    
    return handle_system_error(
        context=context,
        condition=path_obj.exists(),
        code=error_code,
        message=f"Required file not found: {file_path}",
        details=f"File path: {path_obj.absolute()}",
        engine=engine,
        phase=phase,
        severity="critical",
        fatal=True
    )


def validate_schema_ready(
    context: PipelineContext,
    schema_results: Dict[str, Any],
    engine: Optional[str] = None,
    phase: Optional[str] = None
) -> bool:
    """
    Validate schema readiness and record error if not ready.
    
    Args:
        context: Pipeline context for error tracking
        schema_results: Schema validation results
        engine: Engine name performing validation
        phase: Pipeline phase for validation
        
    Returns:
        bool: True if schema is ready, False otherwise
    """
    is_ready = schema_results.get("ready", False)
    
    return handle_system_error(
        context=context,
        condition=is_ready,
        code="S-C-S-0303",
        message="Schema validation failed",
        details=str(schema_results) if not is_ready else None,
        engine=engine,
        phase=phase,
        severity="critical",
        fatal=True
    )


def validate_setup_ready(
    context: PipelineContext,
    setup_results: Dict[str, Any],
    engine: Optional[str] = None,
    phase: Optional[str] = None
) -> bool:
    """
    Validate project setup readiness and record error if not ready.
    
    Args:
        context: Pipeline context for error tracking
        setup_results: Setup validation results
        engine: Engine name performing validation
        phase: Pipeline phase for validation
        
    Returns:
        bool: True if setup is ready, False otherwise
    """
    is_ready = setup_results.get("ready", False)
    
    return handle_system_error(
        context=context,
        condition=is_ready,
        code="S-C-S-0305",
        message="Project setup validation failed",
        details=str(setup_results) if not is_ready else None,
        engine=engine,
        phase=phase,
        severity="critical",
        fatal=True
    )
