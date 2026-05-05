"""
CLI argument parsing and parameter resolution for the DCC pipeline.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
from pathlib import Path
from typing import Tuple, Dict, Any

from utility_engine.console import status_print, debug_print
from core_engine.paths import default_base_path, default_schema_path

# Import from submodules (barrel pattern)
from utility_engine.cli.cli_parser import (
    create_parser,
    parse_cli_args,
    VERBOSE_LEVELS,
)
from utility_engine.cli.cli_defaults import (
    build_native_defaults,
)
from utility_engine.cli.cli_resolver import (
    resolve_effective_parameters,
)
from utility_engine.cli.cli_registry import (
    get_registry_for_cli,
    create_parser_from_registry,
    parse_cli_args_from_registry,
    validate_cli_args_against_registry,
    get_unregistered_parameters_report,
    parse_cli_args_enhanced,
)


__all__ = [
    "create_parser",
    "parse_cli_args",
    "build_native_defaults",
    "resolve_effective_parameters",
    "VERBOSE_LEVELS",
    "get_registry_for_cli",
    "create_parser_from_registry",
    "parse_cli_args_from_registry",
    "validate_cli_args_against_registry",
    "get_unregistered_parameters_report",
    "parse_cli_args_enhanced",
]
