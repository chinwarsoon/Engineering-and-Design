"""
Core Engine - Central pipeline components and context management.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""

# Context management
from .context.context_pipeline import (
    PipelinePaths,
    PipelineBlueprint,
    PipelineTelemetry,
    PipelineErrorEvent,
    PipelinePhaseStatus,
    PipelineState,
    PipelineData,
    ContextTraceItem,
    ContextLoadState,
    PipelineContext,
)

# Schema utilities
from .schema_utils import (
    resolve_schema_root,
)

# Error handling
from .errors.error_manager import (
    handle_system_error,
    handle_data_error,
    handle_engine_failure,
    check_fail_fast_and_raise,
    wrap_engine_execution,
    generate_error_report,
    validate_file_exists,
    validate_schema_ready,
    validate_setup_ready,
)

from .errors.pipeline_result_handler import (
    handle_pipeline_results,
    handle_pipeline_error,
)

# Schema paths
from .paths.path_schema import (
    SchemaPaths,
    get_schema_paths,
    get_schema_path,
    default_schema_path,
)

# Telemetry
from .logging.log_telemetry import (
    HeartbeatPayload,
    TelemetryHeartbeat,
    create_heartbeat,
)

# UI contract
from .ui.ui_contract import (
    UIRequest,
    UIResponse,
    UIContractManager,
    create_api_response,
)

# Submodule exports (already barrel pattern compliant)
from .paths import (
    resolve_pipeline_base_path,
    get_schema_path,
    default_schema_path,
    resolve_platform_paths,
    resolve_output_paths,
    validate_export_paths,
    detect_os,
    should_auto_create_folders,
    safe_resolve,
    normalize_path,
    safe_cwd,
    get_homedir,
    default_base_path,
)

from .logging import (
    DEBUG_LEVEL,
    CALL_DEPTH,
    DEBUG_OBJECT,
    init_debug_object,
    get_debug_object,
    save_debug_log,
    set_debug_level,
    log_status,
    log_warning,
    log_trace,
    log_error,
    setup_logger,
    set_debug_mode,
    get_verbose_mode,
    trace_parameter,
    track_global_param,
    log_context,
)

from .io import (
    load_excel_data,
    HAS_PANDAS,
)

from .data import (
    prepare_dataframe_for_processing,
    flatten_columns,
    ensure_columns_are_strings,
    initialize_missing_columns,
    verify_required_columns,
)

from .system import (
    detect_os,
    should_auto_create_folders,
    test_environment,
)

from .base import (
    BaseEngine,
    BaseProcessor,
)

__all__ = [
    # Context classes
    "PipelinePaths",
    "PipelineBlueprint",
    "PipelineTelemetry",
    "PipelineErrorEvent",
    "PipelinePhaseStatus",
    "PipelineState",
    "PipelineData",
    "ContextTraceItem",
    "ContextLoadState",
    "PipelineContext",
    # Schema utilities
    "resolve_schema_root",
    # Error handling functions
    "handle_system_error",
    "handle_data_error",
    "handle_engine_failure",
    "check_fail_fast_and_raise",
    "wrap_engine_execution",
    "generate_error_report",
    "validate_file_exists",
    "validate_schema_ready",
    "validate_setup_ready",
    # Result handling
    "handle_pipeline_results",
    "handle_pipeline_error",
    # Schema paths
    "SchemaPaths",
    "get_schema_paths",
    "get_schema_path",
    "default_schema_path",
    # Telemetry
    "HeartbeatPayload",
    "TelemetryHeartbeat",
    "create_heartbeat",
    # UI contract
    "UIRequest",
    "UIResponse",
    "UIContractManager",
    "create_api_response",
    # Submodule exports (paths)
    "resolve_pipeline_base_path",
    "get_schema_path",
    "default_schema_path",
    "resolve_platform_paths",
    "resolve_output_paths",
    "validate_export_paths",
    "detect_os",
    "should_auto_create_folders",
    "safe_resolve",
    "normalize_path",
    "safe_cwd",
    "get_homedir",
    "default_base_path",
    # Submodule exports (logging)
    "DEBUG_LEVEL",
    "CALL_DEPTH",
    "DEBUG_OBJECT",
    "init_debug_object",
    "get_debug_object",
    "save_debug_log",
    "set_debug_level",
    "log_status",
    "log_warning",
    "log_trace",
    "log_error",
    "setup_logger",
    "set_debug_mode",
    "get_verbose_mode",
    "trace_parameter",
    "track_global_param",
    "log_context",
    # Submodule exports (io)
    "load_excel_data",
    "HAS_PANDAS",
    # Submodule exports (data)
    "prepare_dataframe_for_processing",
    "flatten_columns",
    "ensure_columns_are_strings",
    "initialize_missing_columns",
    "verify_required_columns",
    # Submodule exports (system)
    "detect_os",
    "should_auto_create_folders",
    "test_environment",
    # Submodule exports (base)
    "BaseEngine",
    "BaseProcessor",
]
