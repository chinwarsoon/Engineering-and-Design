"""
Initiation Engine

A modular engine for project setup validation and initialization.
"""

from dcc.workflow.initiation_engine.engine.core.validator import ProjectSetupValidator
from dcc.workflow.initiation_engine.engine.core.reports import format_report

from dcc.workflow.initiation_engine.engine.validators.items import (
    validate_folders,
    validate_named_files,
    validate_environment,
    check_ready,
    record_path_check,
    ensure_folder,
)

from dcc.workflow.initiation_engine.engine.utils.paths import (
    normalize_path,
    default_base_path,
    get_schema_path,
)

from dcc.workflow.initiation_engine.engine.system.os_detect import (
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
]
