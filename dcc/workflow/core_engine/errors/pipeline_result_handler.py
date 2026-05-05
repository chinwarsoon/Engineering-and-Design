"""
Pipeline Result Handler - Decouples result formatting and error messaging.
"""
import json
from datetime import datetime
from typing import Dict, Any

from core_engine.context.context_pipeline import PipelineContext
from core_engine.errors.error_manager import generate_error_report
from utility_engine.console import status_print
from reporting_engine import print_summary

def handle_pipeline_results(context: PipelineContext, results: Dict[str, Any], json_output: bool = False) -> None:
    """
    Handle and display pipeline execution results.
    
    Breadcrumb: results → generate_error_report → print_summary → display_error_summary
    """
    # Generate final error report
    error_report = generate_error_report(context)
    
    # Add error report and timestamp to results
    results["error_report"] = error_report
    results["timestamp"] = datetime.now().isoformat()
    
    if json_output:
        print(json.dumps(results, indent=2))
    else:
        # Standard summary display
        print_summary(results, status_print_fn=status_print)
        display_error_summary(error_report)

def display_error_summary(error_report: Dict[str, Any]) -> None:
    """
    Print a human-readable error summary to the console.
    """
    summary = error_report.get('error_summary', {})
    if summary.get('total_errors', 0) > 0:
        print("\n=== Error Summary ===")
        print(f"Total errors: {summary['total_errors']}")
        print(f"Fatal errors: {summary['fatal_errors']}")
        
        if summary.get('by_domain'):
            print("By domain:", summary['by_domain'])
        if summary.get('by_severity'):
            print("By severity:", summary['by_severity'])
        
        # System errors
        system_report = error_report.get('system_status_errors', {})
        system_errors = system_report.get('errors', [])
        if system_errors:
            print(f"\nSystem-status errors ({len(system_errors)}):")
            for error in system_errors[:3]:
                print(f"  - [{error['code']}] {error['message']}")
            if len(system_errors) > 3:
                print(f"  ... and {len(system_errors) - 3} more")
        
        # Data errors
        data_report = error_report.get('data_handling_errors', {})
        data_errors = data_report.get('errors', [])
        if data_errors:
            print(f"\nData-handling errors ({len(data_errors)}):")
            for error in data_errors[:3]:
                print(f"  - [{error['code']}] {error['message']}")
            if len(data_errors) > 3:
                print(f"  ... and {len(data_errors) - 3} more")

def handle_pipeline_error(exc: Exception, json_output: bool = False) -> int:
    """
    Handle and display pipeline initialization or execution errors.
    
    Breadcrumb: Exception → error resolution → formatted output (JSON/Console)
    """
    # Dynamic import to avoid circular dependency
    from utility_engine.bootstrap.boot_pipeline import BootstrapError
    from utility_engine.errors import system_error_print
    
    if isinstance(exc, BootstrapError):
        code, message = exc.to_system_error()
        phase = exc.phase
    else:
        # Default to generic system runtime error
        code = "S-R-S-0401"
        message = str(exc)
        phase = "execution"
        
    if json_output:
        print(json.dumps({
            "ready": False,
            "error": message,
            "code": code,
            "phase": phase,
            "timestamp": datetime.now().isoformat()
        }, indent=2))
    else:
        system_error_print(code, detail=message)
        
    return 1
