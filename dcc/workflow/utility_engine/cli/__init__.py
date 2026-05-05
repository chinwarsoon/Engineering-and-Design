"""
CLI argument parsing and parameter resolution for the DCC pipeline.

Phase 3 Enhancement: Registry-driven CLI generation with backward compatibility.
Uses ParameterTypeRegistry from global_parameters.json for type-driven validation.

This module follows the barrel pattern - it re-exports functionality from submodules.
"""
import argparse
import os
import sys
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

from core_engine.logging import set_debug_level
from utility_engine.console import status_print, debug_print
from core_engine.paths import default_base_path, default_schema_path

# Import from submodules (barrel pattern)
from utility_engine.cli.cli_parser import (
    create_parser,
    parse_cli_args,
    _use_registry_validation,
    VERBOSE_LEVELS,
    _REGISTRY_AVAILABLE,
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

# Phase 3: Registry-driven CLI imports (backward compatible)
try:
    from utility_engine.validation import (
        ParameterTypeRegistry,
        ParameterValidator,
        get_parameter_registry,
    )
    _REGISTRY_AVAILABLE = True
except ImportError:
    _REGISTRY_AVAILABLE = False
    status_print("Warning: ParameterTypeRegistry not available, using legacy CLI parsing", min_level=2)


# Note: Additional Phase 3 registry-driven functions remain in this file
# due to complex interdependencies. Future refactoring may extract these.

__all__ = [
    # Legacy functions (Phase 1/2 - backward compatible)
    "create_parser",
    "parse_cli_args",
    "build_native_defaults",
    "resolve_effective_parameters",
    "VERBOSE_LEVELS",
    # Phase 3: Registry-driven functions (NEW)
    "_use_registry_validation",
    "_REGISTRY_AVAILABLE",
    "get_registry_for_cli",
    "create_parser_from_registry",
    "parse_cli_args_from_registry",
    "validate_cli_args_against_registry",
    "get_unregistered_parameters_report",
    "parse_cli_args_enhanced",
]
