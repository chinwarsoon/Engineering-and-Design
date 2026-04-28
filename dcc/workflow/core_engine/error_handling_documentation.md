# Error Handling Documentation

**Document ID**: WP-ERR-DOC-2026-001  
**Date**: 2026-04-29  
**Version**: 1.0.0  
**Status**: ✅ COMPLETE

## Overview

This document provides comprehensive documentation for the centralized error handling system integrated into the DCC pipeline. The system provides unified error tracking, categorization, and reporting while maintaining full backward compatibility.

## Table of Contents

- [1. Architecture Overview](#1-architecture-overview)
- [2. Error Domain Separation](#2-error-domain-separation)
- [3. PipelineContext Error APIs](#3-pipelinecontext-error-apis)
- [4. Error Handling Utilities](#4-error-handling-utilities)
- [5. Fail-Fast Configuration](#5-fail-fast-configuration)
- [6. Error Reporting](#6-error-reporting)
- [7. Engine Integration Guide](#7-engine-integration-guide)
- [8. Best Practices](#8-best-practices)
- [9. Troubleshooting](#9-troubleshooting)

## 1. Architecture Overview

### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    PipelineContext                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   State         │  │   Blueprint     │  │   Data       │ │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │              │ │
│  │ │system_errors│ │  │ │validation   │ │  │              │ │
│  │ │engine_status│ │  │ │rules        │ │  │              │ │
│  │ │error_summary│ │  │ │error_catalog│ │  │              │ │
│  │ └─────────────┘ │  │ └─────────────┘ │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                Error Handling Utilities                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │handle_system_error│ │handle_data_error│ │wrap_engine   │ │
│  │validate_setup_ready│ │validate_schema_ready│ │execution    │ │
│  │capture_exception   │ │record_engine_failure│ │             │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Error Flow

```
Engine Error → Context Recording → Error Aggregation → Fail-Fast Check → User Output
     │                    │                    │                  │
     ▼                    ▼                    ▼                  ▼
Error Event → system_status_errors → Error Summary → should_fail_fast() → system_error_print()
```

## 2. Error Domain Separation

### 2.1 System-Status Errors
Environment, file system, configuration, dependency, and orchestration failures.

**Examples:**
- File not found: `S-F-S-0201`
- Schema validation: `S-C-S-0301`
- Permission denied: `S-F-S-0202`
- Memory error: `S-R-S-0403`

### 2.2 Data-Handling Errors
Validation and business-rule detection errors produced during processing.

**Examples:**
- Validation failure: `P1-A-P-0101`
- Business rule violation: `P2-B-P-0201`
- Data quality issue: `P3-D-P-0301`

### 2.3 Error Code Format

```
Domain-Type-Phase-Sequence
└─ S: System, P: Processing
   └─ F: File, C: Config, R: Runtime, A: Validation, B: Business, D: Data
      └─ S: Setup, C: Configuration, P: Processing, A: Analysis
         └─ 4-digit sequence
```

## 3. PipelineContext Error APIs

### 3.1 Core Error Recording

```python
# Add system-status error
context.add_system_error(
    code="S-F-S-0201",
    message="File not found",
    details="/path/to/file.txt",
    engine="initiation_engine",
    phase="file_validation",
    severity="critical",
    fatal=True
)

# Add data-handling error
context.add_data_error(
    code="P1-A-P-0101",
    message="Validation failed",
    details="Row 5: Invalid value",
    engine="processor_engine",
    phase="data_validation",
    severity="medium",
    fatal=False
)
```

### 3.2 Exception Handling

```python
# Capture exception with full context
context.capture_exception(
    code="S-R-S-0401",
    exception=exc,
    engine="initiation_engine",
    phase="setup_validation"
)

# Record engine failure
context.record_engine_failure("schema_engine", "schema_validation")
```

### 3.3 Fail-Fast Logic

```python
# Check if pipeline should fail fast
if context.should_fail_fast("system"):
    raise ValueError("Critical error encountered")
    
if context.should_fail_fast("data"):
    # Handle data error fail-fast
    pass
```

### 3.4 Error Reporting

```python
# Get comprehensive error summary
summary = context.get_error_summary()
# Returns: {'total_errors': 5, 'by_domain': {...}, 'by_severity': {...}}

# Get filtered errors
system_errors = context.get_system_status_errors()
data_errors = context.get_data_handling_errors()
```

## 4. Error Handling Utilities

### 4.1 Standardized Error Handling

```python
from core_engine.error_handling import handle_system_error

# Condition-based error handling
if not handle_system_error(
    context=context,
    condition=file_path.exists(),
    code="S-F-S-0201",
    message=f"File not found: {file_path}",
    details=str(file_path),
    engine="initiation_engine",
    phase="file_validation",
    severity="critical",
    fatal=True
):
    raise FileNotFoundError(f"File not found: {file_path}")
```

### 4.2 Validation Helpers

```python
from core_engine.error_handling import validate_setup_ready, validate_schema_ready

# Validate setup results
if not validate_setup_ready(context, setup_results, engine="initiation_engine"):
    # Handle setup failure
    pass

# Validate schema results
if not validate_schema_ready(context, schema_results, engine="schema_engine"):
    # Handle schema failure
    pass
```

### 4.3 Engine Execution Wrapper

```python
from core_engine.error_handling import wrap_engine_execution

def process_data_engine(context):
    def _process():
        # Engine logic here
        return result
    
    return wrap_engine_execution(
        context=context,
        engine_name="processor_engine",
        execution_func=_process,
        phase="data_processing"
    )
```

### 4.4 Error Report Generation

```python
from core_engine.error_handling import generate_error_report

# Generate comprehensive error report
report = generate_error_report(context)
# Returns: {
#   'pipeline_status': 'completed|failed',
#   'error_summary': {...},
#   'system_status_errors': {...},
#   'data_handling_errors': {...},
#   'engine_status': {...},
#   'fail_fast_triggered': True/False
# }
```

## 5. Fail-Fast Configuration

### 5.1 Blueprint Configuration

```python
# Configure fail-fast behavior in schema
{
    "parameters": {
        "fail_fast_system": {
            "enabled": True,
            "severity_threshold": "critical"
        },
        "fail_fast_data": {
            "enabled": False,
            "severity_threshold": "high"
        }
    }
}
```

### 5.2 Severity Levels

- **critical**: Immediate pipeline failure required
- **high**: Serious issue, may cause failure
- **medium**: Warning level, typically non-fatal
- **low**: Informational, non-blocking

### 5.3 Domain-Specific Policies

```python
# System errors: Fail fast on critical
context.should_fail_fast("system")  # Checks system_error_critical

# Data errors: Configurable threshold
context.should_fail_fast("data")    # Checks data_error_high (if configured)
```

## 6. Error Reporting

### 6.1 End-of-Run Summary

```python
# Automatic error summary at pipeline completion
=== Error Summary ===
Total errors: 3
Fatal errors: 1
By domain: {'system': 2, 'data': 1}
By severity: {'critical': 1, 'high': 1, 'medium': 1}

System-status errors (2):
  - [S-F-S-0201] File not found
  - [S-C-S-0301] Schema validation failed

Data-handling errors (1):
  - [P1-A-P-0101] Validation failed
```

### 6.2 JSON Output Integration

```python
# Error report included in JSON output
{
    "ready": True,
    "error_report": {
        "pipeline_status": "completed",
        "error_summary": {...},
        "system_status_errors": {...},
        "data_handling_errors": {...}
    }
}
```

### 6.3 Debug Log Integration

```python
# Error context captured in debug log
{
    "errors": [
        {
            "code": "S-F-S-0201",
            "message": "File not found",
            "engine": "initiation_engine",
            "phase": "file_validation",
            "timestamp": "2026-04-29T03:45:00Z"
        }
    ]
}
```

## 7. Engine Integration Guide

### 7.1 Initiation Engine Integration

```python
# In utils/paths.py
def validate_export_paths(export_paths, overwrite_existing, context=None):
    if not overwrite_existing:
        for file_key in ("csv_path", "excel_path", "summary_path"):
            target_path = export_paths[file_key]
            if target_path.exists():
                if context and hasattr(context, 'add_system_error'):
                    context.add_system_error(
                        code="S-F-S-0205",
                        message=f"Output file exists: {target_path}",
                        engine="initiation_engine",
                        phase="path_validation",
                        severity="critical",
                        fatal=True
                    )
                raise FileExistsError(f"Output file exists: {target_path}")
```

### 7.2 Schema Engine Integration

```python
# In validator/schema_validator.py
if not self.schema_file.is_file():
    if hasattr(self.context, 'add_system_error'):
        self.context.add_system_error(
            code="S-F-S-0204",
            message=f"Main schema file not found: {self.schema_file}",
            details=str(self.schema_file),
            engine="schema_engine",
            phase="schema_validation",
            severity="critical",
            fatal=True
        )
    return results
```

### 7.3 Mapper Engine Integration

```python
# In core/engine.py
if not self.resolved_schema:
    if hasattr(self.context, 'add_system_error'):
        self.context.add_system_error(
            code="S-C-M-0101",
            message="No schema loaded. Call load_main_schema() first.",
            engine="mapper_engine",
            phase="column_detection",
            severity="critical",
            fatal=True
        )
    raise ValueError("No schema loaded. Call load_main_schema() first.")
```

### 7.4 Processor Engine Integration

```python
# In core/engine.py
if df is None:
    df = self.context.data.df_mapped
    if df is None:
        if hasattr(self.context, 'add_system_error'):
            self.context.add_system_error(
                code="S-C-P-0101",
                message="No input DataFrame provided in context.data.df_mapped.",
                engine="processor_engine",
                phase="data_processing",
                severity="critical",
                fatal=True
            )
        raise ValueError("No input DataFrame provided in context.data.df_mapped.")
```

### 7.5 AI Ops Engine Integration

```python
# In core/engine.py (non-blocking as per R11)
except Exception as exc:
    if hasattr(context, 'add_system_error'):
        context.add_system_error(
            code="S-A-S-0501",
            message=f"AI operations failed: {exc}",
            details=str(exc),
            engine="ai_ops_engine",
            phase="ai_analysis",
            severity="medium",
            fatal=False  # Non-blocking
        )
    
    # Preserve user-visible output
    try:
        from utility_engine.errors import system_error_print
        system_error_print("S-A-S-0501", detail=str(exc), fatal=False)
    except Exception:
        pass
    return None
```

## 8. Best Practices

### 8.1 Error Code Assignment

- Use consistent prefixes: `S-*-*-*` for system, `P-*-*-*` for processing
- Maintain sequence numbers per engine
- Document new codes in engine documentation

### 8.2 Severity Classification

- **critical**: File not found, permission denied, memory errors
- **high**: Schema validation, configuration errors, dependency issues
- **medium**: AI operations, optional features, warnings
- **low**: Informational messages, non-critical issues

### 8.3 Phase Attribution

- Use descriptive phase names: `setup_validation`, `file_validation`, `data_processing`
- Be consistent across engines
- Include phase in error codes when applicable

### 8.4 Context Integration

```python
# Always check context availability
if context and hasattr(context, 'add_system_error'):
    context.add_system_error(...)

# Preserve existing error behavior
raise ValueError("Existing error message")
```

### 8.5 Performance Considerations

- Error operations are <1ms each
- Batch error recording when possible
- Use appropriate severity levels to avoid unnecessary fail-fast checks

## 9. Troubleshooting

### 9.1 Common Issues

**Issue**: Errors not appearing in context
**Solution**: Verify context is passed to error handling functions and has required methods

**Issue**: Fail-fast not triggering
**Solution**: Check blueprint configuration and severity thresholds

**Issue**: Performance degradation
**Solution**: Limit error recording to essential cases, use appropriate severity levels

### 9.2 Debug Mode

```python
# Enable debug mode for detailed error tracking
context = PipelineContext(paths=paths, parameters={}, debug_mode=True)

# Check error context
errors = context.get_system_status_errors()
for error in errors:
    print(f"Error: {error.code} in {error.engine}.{error.phase}")
```

### 9.3 Testing Error Handling

```python
# Test error recording
context.add_system_error(code="TEST-001", message="Test error")
assert len(context.state.system_status_errors) == 1

# Test fail-fast
context.add_system_error(code="TEST-002", message="Critical error", severity="critical", fatal=True)
assert context.should_fail_fast("system") is True
```

## 10. Migration Guide

### 10.1 From Direct Error Printing

**Before:**
```python
system_error_print("S-F-S-0201", detail=str(file_path))
raise FileNotFoundError(f"File not found: {file_path}")
```

**After:**
```python
if not handle_system_error(
    context=context,
    condition=file_path.exists(),
    code="S-F-S-0201",
    message=f"File not found: {file_path}",
    details=str(file_path),
    engine="engine_name",
    phase="processing_phase",
    severity="critical",
    fatal=True
):
    raise FileNotFoundError(f"File not found: {file_path}")
```

### 10.2 From Exception Handling

**Before:**
```python
except Exception as exc:
    system_error_print("S-R-S-0401", detail=str(exc))
    raise
```

**After:**
```python
except Exception as exc:
    context.capture_exception(code="S-R-S-0401", exception=exc, engine="engine_name", phase="processing_phase")
    raise
```

### 10.3 From Fail-Fast String Detection

**Before:**
```python
if "FAIL FAST" in str(exc):
    system_error_print("S-R-S-0402", detail=str(exc))
    raise
```

**After:**
```python
context.capture_exception(code="S-R-S-0402", exception=exc, engine="engine_name", phase="processing_phase")
if context.should_fail_fast("data"):
    raise
```

---

**Document Status**: ✅ COMPLETE  
**Last Updated**: 2026-04-29  
**Version**: 1.0.0
