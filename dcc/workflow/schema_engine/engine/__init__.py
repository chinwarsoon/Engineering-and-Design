"""
Schema Engine

A modular engine for schema loading, validation, and dependency resolution.
"""

from dcc.workflow.schema_engine.engine.loader import SchemaLoader

from dcc.workflow.schema_engine.engine.validator import (
    SchemaValidator,
    validate_schema_document,
    validate_scalar_record_section,
    find_record_section,
    validate_scalar_value,
    validate_record_field,
    validate_scalar_rules,
    track_unique_scalar,
    validate_array_rules,
)

from dcc.workflow.schema_engine.engine.status import (
    get_validation_status_path,
    write_validation_status,
    load_validation_status,
    validate_validation_status,
)

from dcc.workflow.schema_engine.engine.utils import (
    safe_resolve,
    safe_cwd,
    get_default_schema_path,
    default_schema_path,
)

from dcc.workflow.schema_engine.engine.core import format_report

__all__ = [
    'SchemaLoader',
    'SchemaValidator',
    'validate_schema_document',
    'validate_scalar_record_section',
    'find_record_section',
    'validate_scalar_value',
    'validate_record_field',
    'validate_scalar_rules',
    'track_unique_scalar',
    'validate_array_rules',
    'get_validation_status_path',
    'write_validation_status',
    'load_validation_status',
    'validate_validation_status',
    'safe_resolve',
    'safe_cwd',
    'get_default_schema_path',
    'default_schema_path',
    'format_report',
]
