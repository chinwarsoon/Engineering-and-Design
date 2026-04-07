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
)

from .utils.cli import (
    create_parser,
    parse_cli_args,
)

from .utils.logging import (
    status_print,
    debug_print,
    setup_logger,
    set_debug_mode,
)

from .utils.system import (
    test_environment,
)

from .system.os_detect import (
    detect_os,
    should_auto_create_folders,
)

__all__ = [
    'ProjectSetupValidator',
    'format_report',
    'validate_folders',
    'validate_named_files',
    'validate_environment',
    'check_ready',
    'record_path_check',
    'ensure_folder',
    'normalize_path',
    'default_base_path',
    'get_schema_path',
    'detect_os',
    'should_auto_create_folders',
    'get_homedir',
    'create_parser',
    'parse_cli_args',
    'status_print',
    'debug_print',
    'setup_logger',
    'set_debug_mode',
    'test_environment',
]
