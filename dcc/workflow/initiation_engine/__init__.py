"""
Initiation Engine

A modular engine for project setup validation and initialization.
"""

from .core.validator import ProjectSetupValidator
from .core.reports import format_report

from .validators.items import (
    validate_folders,
    validate_named_files,
    validate_environment,
    check_ready,
    record_path_check,
    ensure_folder,
)

from .utils.paths import (
    normalize_path,
    default_base_path,
    get_schema_path,
    get_homedir,
    resolve_platform_paths,
    resolve_output_paths,
    validate_export_paths,
)

from .utils.parameters import (
    build_native_defaults,
    resolve_effective_parameters,
)

from .utils.cli import (
    create_parser,
    parse_cli_args,
)

from .utils.logging import (
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
    milestone_print,
    debug_print,
    setup_logger,
    set_debug_mode,
    # Framework banner
    print_framework_banner,
    get_verbose_mode,
)

from .utils.system import (
    test_environment,
)

from .system.os_detect import (
    detect_os,
    should_auto_create_folders,
)

__all__ = [
    # Core
    'ProjectSetupValidator',
    'format_report',
    # Validators
    'validate_folders',
    'validate_named_files',
    'validate_environment',
    'check_ready',
    'record_path_check',
    'ensure_folder',
    # Paths
    'normalize_path',
    'default_base_path',
    'get_schema_path',
    'get_homedir',
    'resolve_platform_paths',
    'resolve_output_paths',
    'validate_export_paths',
    # Parameters
    'build_native_defaults',
    'resolve_effective_parameters',
    # System
    'detect_os',
    'should_auto_create_folders',
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
    'milestone_print',
    'debug_print',
    'setup_logger',
    'set_debug_mode',
    # Framework banner
    'print_framework_banner',
    'get_verbose_mode',
    # System
    'test_environment',
]
