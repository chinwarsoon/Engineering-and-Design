"""
Utility functions for the initiation engine.
"""

from .paths import (
    normalize_path,
    default_base_path,
    get_schema_path,
    get_homedir,
    resolve_platform_paths,
    resolve_output_paths,
    validate_export_paths,
)
from .cli import (
    create_parser,
    parse_cli_args,
)
from .logging import (
    # Tiered logging
    set_debug_level,
    log_status,
    log_warning,
    log_trace,
    log_error,
    # Debug object
    init_debug_object,
    get_debug_object,
    save_debug_log,
    trace_parameter,
    track_global_param,
    # Hierarchical context
    log_context,
    # Legacy compatibility
    status_print,
    debug_print,
    setup_logger,
    set_debug_mode,
)

from .system import (
    test_environment,
)

from .parameters import (
    build_native_defaults,
    resolve_effective_parameters,
)

__all__ = [
    # Paths
    'normalize_path',
    'default_base_path',
    'get_schema_path',
    'get_homedir',
    'resolve_platform_paths',
    'resolve_output_paths',
    'validate_export_paths',
    # CLI
    'create_parser',
    'parse_cli_args',
    # Tiered logging
    'set_debug_level',
    'log_status',
    'log_warning',
    'log_trace',
    'log_error',
    # Debug object
    'init_debug_object',
    'get_debug_object',
    'save_debug_log',
    'trace_parameter',
    'track_global_param',
    # Hierarchical context
    'log_context',
    # Legacy logging
    'status_print',
    'debug_print',
    'setup_logger',
    'set_debug_mode',
    # System
    'test_environment',
    # Parameters
    'build_native_defaults',
    'resolve_effective_parameters',
]
