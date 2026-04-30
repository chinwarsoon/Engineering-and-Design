"""
CLI argument parsing and parameter resolution for the DCC pipeline.

Phase 3 Enhancement: Registry-driven CLI generation with backward compatibility.
Uses ParameterTypeRegistry from global_parameters.json for type-driven validation.
"""
import argparse
import os
import sys
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

from core_engine.logging import set_debug_level
from utility_engine.console import status_print, debug_print
from core_engine.paths import default_base_path, default_schema_path

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


# Feature toggle for gradual migration (Phase 3 backward compatibility)
def _use_registry_validation() -> bool:
    """
    Check if registry-driven validation should be used.
    
    Breadcrumb: Environment variable check -> registry validation toggle
    
    Returns:
        True if DCC_USE_REGISTRY_VALIDATION env var is set to "1" or "true"
    """
    return os.environ.get("DCC_USE_REGISTRY_VALIDATION", "").lower() in ("1", "true", "yes")

VERBOSE_LEVELS = {
    "quiet": 0,
    "normal": 1,
    "debug": 2,
    "trace": 3,
}

def create_parser(base_path: Path) -> argparse.ArgumentParser:
    """
    Create CLI argument parser.
    
    Breadcrumb: base_path -> create ArgumentParser -> add arguments from schema
    
    Note: Argument names should match global_parameters.json schema definitions.
    For schema-driven CLI, use create_parser_from_registry() instead.
    
    Args:
        base_path: Project root path for defaults
        
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(description="DCC Engine Pipeline - Modular processing workflow.")
    parser.add_argument("--base-path", default=str(base_path), help="Project root path.")
    parser.add_argument("--schema-file", default=None, help="Alternative schema register JSON file.")
    parser.add_argument("--excel-file", "-e", default=None, help="Input Excel file (maps to upload_file_name).")
    parser.add_argument("--upload-sheet", default=None, help="Input Excel sheet name (maps to upload_sheet_name).")
    parser.add_argument("--output-path", default=None, help="Output directory path (maps to download_file_path).")
    parser.add_argument("--output-file", default=None, help="Final output file name (not full path).")
    parser.add_argument("--start-col", default=None, help="Input Excel start column.")
    parser.add_argument("--end-col", default=None, help="Input Excel end column.")
    parser.add_argument("--header-row", type=int, default=None, help="Header row index (maps to header_row_index).")
    parser.add_argument("--overwrite", choices=["True", "False"], default=None, help="Overwrite existing output (maps to overwrite_existing_downloads).")
    parser.add_argument("--verbose", "-v", choices=["quiet", "normal", "debug", "trace"], default="normal", help="Output verbosity level.")
    parser.add_argument("--debug-mode", choices=["True", "False"], default=None, help="Enable debug mode (maps to debug_dev_mode). DEPRECATED: Use --verbose debug instead.")
    parser.add_argument("--nrows", type=int, default=None, help="Optional row limit.")
    parser.add_argument("--json", action="store_true", help="Print final result as JSON.")
    return parser


def parse_cli_args(base_path: Path | None = None) -> Tuple[argparse.Namespace, Dict[str, Any], bool]:
    """Parse CLI arguments and return the namespace, override dict, and a status boolean."""
    if base_path is None:
        base_path = default_base_path()
        
    parser = create_parser(base_path)
    args, unknown_args = parser.parse_known_args()
    
    verbose_level = VERBOSE_LEVELS.get(args.verbose, 1)
    set_debug_level(verbose_level)
    
    raw_argv = sys.argv[1:]
    verbose_explicitly_set = "--verbose" in raw_argv or "-v" in raw_argv

    cli_args: Dict[str, Any] = {}

    if verbose_explicitly_set:
        cli_args["verbose_level"] = args.verbose
    if args.schema_file:
        cli_args["schema_register_file"] = args.schema_file
    if args.excel_file:
        cli_args["upload_file_name"] = args.excel_file
    if args.upload_sheet:
        cli_args["upload_sheet_name"] = args.upload_sheet
    # Handle output path (directory) from schema
    if args.output_path:
        cli_args["download_file_path"] = args.output_path
    # Handle output file name from schema (separate from directory)
    if args.output_file:
        cli_args["output_file"] = args.output_file
        # Only derive download_file_path from output_file if output_path not explicitly set
        if not args.output_path:
            cli_args["download_file_path"] = str(Path(args.output_file).resolve().parent)
    if args.start_col:
        cli_args["start_col"] = args.start_col
    if args.end_col:
        cli_args["end_col"] = args.end_col
    if args.header_row is not None:
        cli_args["header_row_index"] = args.header_row
    if args.overwrite:
        cli_args["overwrite_existing_downloads"] = args.overwrite == "True"
    if args.debug_mode:
        cli_args["debug_dev_mode"] = args.debug_mode == "True"
    
    if unknown_args:
        debug_print(f"Ignoring unknown CLI arguments: {unknown_args}")
    
    cli_overrides_provided = bool(cli_args)

    return args, cli_args, cli_overrides_provided


# =============================================================================
# Phase 3: Registry-Driven CLI Functions (NEW - Backward Compatible)
# =============================================================================

def create_parser_from_registry(
    registry: ParameterTypeRegistry,
    base_path: Path
) -> argparse.ArgumentParser:
    """
    Create CLI argument parser from ParameterTypeRegistry.
    
    Auto-generates CLI arguments based on registry entries with cli_arg_name defined.
    
    Breadcrumb: registry.get_cli_parameters() -> create argparse arguments
    
    Args:
        registry: ParameterTypeRegistry with loaded global_parameters.json
        base_path: Base path for default values
        
    Returns:
        Configured ArgumentParser with registry-driven arguments
        
    Example:
        >>> registry = get_parameter_registry("config/schemas/global_parameters.json")
        >>> parser = create_parser_from_registry(registry, base_path)
        >>> args = parser.parse_args()
    """
    parser = argparse.ArgumentParser(
        description="DCC Engine Pipeline - Registry-driven CLI (Phase 3)"
    )
    
    # Always add base-path (not in registry)
    parser.add_argument("--base-path", default=str(base_path), help="Project root path.")
    
    # Add verbose (not in registry, but commonly used)
    parser.add_argument(
        "--verbose", "-v", 
        choices=["quiet", "normal", "debug", "trace"], 
        default="normal", 
        help="Output verbosity level."
    )
    
    # Auto-generate arguments from registry
    cli_params = registry.get_cli_parameters()
    for param_name, param in cli_params.items():
        if not param.cli_arg_name:
            continue
            
        # Build argument specification
        argspec = {
            "help": param.description,
        }
        
        # Add short argument if defined
        if param.cli_arg_short:
            args = [param.cli_arg_name, param.cli_arg_short]
        else:
            args = [param.cli_arg_name]
        
        # Type-specific handling
        if param.param_type == "boolean":
            argspec["choices"] = ["True", "False"]
            argspec["default"] = None
        elif param.param_type == "integer":
            argspec["type"] = int
            argspec["default"] = None
        else:
            argspec["default"] = None
            
        parser.add_argument(*args, **argspec)
    
    return parser


def parse_cli_args_from_registry(
    registry: ParameterTypeRegistry,
    base_path: Path | None = None
) -> Tuple[argparse.Namespace, Dict[str, Any], bool, List[Any]]:
    """
    Parse CLI arguments using registry-driven parser with type validation.
    
    Breadcrumb: registry -> create_parser_from_registry() -> parse_args() -> ParameterValidator.validate_parameters()
    
    Args:
        registry: ParameterTypeRegistry with loaded parameters
        base_path: Project base path (uses default if None)
        
    Returns:
        Tuple of (namespace, cli_args dict, has_overrides flag, validation_results)
        where validation_results is List[ParameterValidationResult]
        
    Raises:
        SystemExit: If validation fails in strict mode
        
    Example:
        >>> registry = get_parameter_registry("config/schemas/global_parameters.json")
        >>> args, cli_args, has_overrides, results = parse_cli_args_from_registry(registry)
        >>> if results and not all(r.is_valid for r in results):
        ...     print("Validation failed")
    """
    if base_path is None:
        base_path = default_base_path()
    
    # Create parser from registry
    parser = create_parser_from_registry(registry, base_path)
    
    # Parse arguments
    args, unknown_args = parser.parse_known_args()
    
    # Handle verbose level
    verbose_level = VERBOSE_LEVELS.get(args.verbose, 1)
    set_debug_level(verbose_level)
    
    raw_argv = sys.argv[1:]
    verbose_explicitly_set = "--verbose" in raw_argv or "-v" in raw_argv
    
    # Build CLI args dict from parsed values
    cli_args: Dict[str, Any] = {}
    
    if verbose_explicitly_set:
        cli_args["verbose_level"] = args.verbose
    
    # Map parsed args to parameter names
    cli_params = registry.get_cli_parameters()
    for param_name, param in cli_params.items():
        if not param.cli_arg_name:
            continue
            
        # Get attribute from parsed args (cli_arg_name is like --excel-file)
        attr_name = param.cli_arg_name.lstrip("-").replace("-", "_")
        value = getattr(args, attr_name, None)
        
        if value is not None:
            # Convert boolean strings to bool
            if param.param_type == "boolean":
                value = value == "True"
            cli_args[param_name] = value
    
    # Validate CLI arguments using ParameterValidator
    validation_results = []
    if cli_args:
        validator = ParameterValidator(registry, base_path)
        validation_results = validator.validate_parameters(cli_args, source="cli")
        
        # Check for validation errors
        if validator.has_errors():
            status_print("CLI argument validation errors:", min_level=1)
            for result in validator.get_errors():
                status_print(f"  - {result.parameter_name}: {result.error_message}", min_level=1)
            
            # Fail fast in strict mode (DCC_STRICT_MODE env var)
            if os.environ.get("DCC_STRICT_MODE", "").lower() in ("1", "true", "yes"):
                sys.exit(1)
    
    if unknown_args:
        debug_print(f"Unknown CLI arguments (not in registry): {unknown_args}")
        
        # In strict mode, unknown args are errors
        if os.environ.get("DCC_STRICT_MODE", "").lower() in ("1", "true", "yes"):
            status_print(f"Error: Unknown arguments not registered in global_parameters.json: {unknown_args}", min_level=1)
            sys.exit(1)
    
    cli_overrides_provided = bool(cli_args)
    
    return args, cli_args, cli_overrides_provided, validation_results


def validate_cli_args_against_registry(
    cli_args: Dict[str, Any],
    registry: ParameterTypeRegistry,
    strict: bool = False
) -> Tuple[bool, List[str]]:
    """
    Validate CLI argument names against registered parameters.
    
    Breadcrumb: cli_args.keys() -> registry.validate_parameter_name() -> errors list
    
    Args:
        cli_args: Dictionary of CLI argument names to values
        registry: ParameterTypeRegistry with registered parameters
        strict: If True, unknown parameters are errors; if False, warnings
        
    Returns:
        Tuple of (is_valid, list_of_errors)
        
    Example:
        >>> is_valid, errors = validate_cli_args_against_registry(cli_args, registry)
        >>> if not is_valid:
        ...     print(f"Unknown parameters: {errors}")
    """
    errors = []
    
    for name in cli_args.keys():
        if not registry.validate_parameter_name(name):
            errors.append(f"CLI parameter '{name}' not registered in global_parameters.json")
    
    if errors:
        status_print("Parameter contract validation warnings:", min_level=2)
        for error in errors:
            status_print(f"  - {error}", min_level=2)
        
        if strict:
            status_print("Strict mode: Exiting due to unregistered parameters", min_level=1)
            return False, errors
    
    return len(errors) == 0, errors


def validate_parameter_contract(
    registry: ParameterTypeRegistry,
    cli_args: Optional[Dict[str, Any]] = None,
    schema_params: Optional[Dict[str, Any]] = None,
    native_defaults: Optional[Dict[str, Any]] = None,
    strict: bool = False,
) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Comprehensive parameter contract validation across all sources.
    
    Validates that all parameter keys from CLI, schema, and native defaults
    are registered in global_parameters.json.
    
    Breadcrumb: registry + cli_args + schema_params + native_defaults -> validation per source
    
    Args:
        registry: ParameterTypeRegistry with registered parameters
        cli_args: CLI argument parameters (optional)
        schema_params: Schema-loaded parameters (optional)
        native_defaults: Native default parameters (optional)
        strict: If True, fail on any unregistered parameters
        
    Returns:
        Tuple of (is_valid, errors_by_source) where errors_by_source has keys:
        - 'cli': List of unregistered CLI parameter errors
        - 'schema': List of unregistered schema parameter errors
        - 'native': List of unregistered native default errors
        
    Example:
        >>> registry = get_parameter_registry("config/schemas/global_parameters.json")
        >>> is_valid, errors = validate_parameter_contract(
        ...     registry,
        ...     cli_args={"upload_file_name": "data.xlsx"},
        ...     native_defaults={"debug_dev_mode": False}
        ... )
        >>> if not is_valid:
        ...     print(f"CLI errors: {errors['cli']}")
        ...     print(f"Native errors: {errors['native']}")
    """
    errors_by_source = {
        "cli": [],
        "schema": [],
        "native": [],
    }
    
    # Validate CLI parameters
    if cli_args:
        for name in cli_args.keys():
            if not registry.validate_parameter_name(name):
                errors_by_source["cli"].append(
                    f"CLI parameter '{name}' not registered in global_parameters.json"
                )
    
    # Validate schema parameters
    if schema_params:
        for name in schema_params.keys():
            if not registry.validate_parameter_name(name):
                errors_by_source["schema"].append(
                    f"Schema parameter '{name}' not registered in global_parameters.json"
                )
    
    # Validate native default parameters
    if native_defaults:
        for name in native_defaults.keys():
            # Skip internal/platform-specific keys that are not meant to be validated
            if name in ("platform_defaults", "platform_defaults_reference"):
                continue
            if not registry.validate_parameter_name(name):
                errors_by_source["native"].append(
                    f"Native default '{name}' not registered in global_parameters.json"
                )
    
    # Check if any errors exist
    total_errors = sum(len(errs) for errs in errors_by_source.values())
    is_valid = total_errors == 0
    
    # Print warnings/errors
    if total_errors > 0:
        status_print("Parameter Contract Validation Issues:", min_level=1)
        for source, errors in errors_by_source.items():
            if errors:
                status_print(f"  [{source.upper()}] {len(errors)} unregistered parameters:", min_level=1)
                for error in errors:
                    status_print(f"    - {error}", min_level=1)
        
        if strict:
            status_print("Strict mode enabled: Failing due to parameter contract violations", min_level=1)
            return False, errors_by_source
        else:
            status_print("Non-strict mode: Continuing despite unregistered parameters", min_level=2)
    else:
        status_print("✓ Parameter contract validation passed - all parameters registered", min_level=3)
    
    return is_valid, errors_by_source


def get_unregistered_parameters_report(
    registry: ParameterTypeRegistry,
    cli_args: Optional[Dict[str, Any]] = None,
    schema_params: Optional[Dict[str, Any]] = None,
    native_defaults: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a detailed report of parameter registration status.
    
    Useful for debugging and auditing parameter coverage.
    
    Args:
        registry: ParameterTypeRegistry with registered parameters
        cli_args: CLI argument parameters (optional)
        schema_params: Schema-loaded parameters (optional)
        native_defaults: Native default parameters (optional)
        
    Returns:
        Dictionary with registration statistics and details
    """
    all_registered = registry.get_all_parameters()
    
    report = {
        "total_registered": len(all_registered),
        "registered_parameter_names": sorted(all_registered.keys()),
        "cli": {
            "provided_count": len(cli_args) if cli_args else 0,
            "registered_count": 0,
            "unregistered": [],
        },
        "schema": {
            "provided_count": len(schema_params) if schema_params else 0,
            "registered_count": 0,
            "unregistered": [],
        },
        "native": {
            "provided_count": len(native_defaults) if native_defaults else 0,
            "registered_count": 0,
            "unregistered": [],
        },
    }
    
    # Check CLI parameters
    if cli_args:
        for name in cli_args.keys():
            if registry.validate_parameter_name(name):
                report["cli"]["registered_count"] += 1
            else:
                report["cli"]["unregistered"].append(name)
    
    # Check schema parameters
    if schema_params:
        for name in schema_params.keys():
            if registry.validate_parameter_name(name):
                report["schema"]["registered_count"] += 1
            else:
                report["schema"]["unregistered"].append(name)
    
    # Check native defaults
    if native_defaults:
        for name in native_defaults.keys():
            if name in ("platform_defaults", "platform_defaults_reference"):
                report["native"]["registered_count"] += 1  # Count as registered (internal)
            elif registry.validate_parameter_name(name):
                report["native"]["registered_count"] += 1
            else:
                report["native"]["unregistered"].append(name)
    
    return report


def get_registry_for_cli(base_path: Path) -> Optional[ParameterTypeRegistry]:
    """
    Get ParameterTypeRegistry for CLI operations with fallback.
    
    Breadcrumb: Check availability -> load registry or return None
    
    Args:
        base_path: Project base path for locating schema
        
    Returns:
        ParameterTypeRegistry if available, None otherwise
    """
    if not _REGISTRY_AVAILABLE:
        return None
    
    try:
        schema_path = base_path / "config" / "schemas" / "global_parameters.json"
        return get_parameter_registry(schema_path)
    except Exception as exc:
        debug_print(f"Could not load ParameterTypeRegistry: {exc}")
        return None


# =============================================================================
# Phase 3: Enhanced parse_cli_args with registry toggle
# =============================================================================

def parse_cli_args_enhanced(
    base_path: Path | None = None
) -> Tuple[argparse.Namespace, Dict[str, Any], bool]:
    """
    Enhanced CLI argument parsing with optional registry-driven validation.
    
    Backward compatible: Uses legacy parsing by default, registry when enabled.
    
    Breadcrumb: Check toggle -> legacy or registry path
    
    Args:
        base_path: Project base path (uses default if None)
        
    Returns:
        Tuple of (namespace, cli_args dict, has_overrides flag)
        
    Environment Variables:
        DCC_USE_REGISTRY_VALIDATION: Set to "1" or "true" to enable registry mode
        DCC_STRICT_MODE: Set to "1" or "true" to fail on validation errors
    """
    if base_path is None:
        base_path = default_base_path()
    
    # Check if registry validation should be used
    if _use_registry_validation() and _REGISTRY_AVAILABLE:
        registry = get_registry_for_cli(base_path)
        if registry:
            status_print("Using Phase 3 registry-driven CLI parsing", min_level=3)
            args, cli_args, has_overrides, _ = parse_cli_args_from_registry(registry, base_path)
            return args, cli_args, has_overrides
        else:
            status_print("Registry not available, falling back to legacy CLI parsing", min_level=2)
    
    # Legacy path (backward compatible)
    return parse_cli_args(base_path)


# =============================================================================
# Legacy Functions (Backward Compatible - Phase 1/2)
# =============================================================================

def build_native_defaults(base_path: Path, registry: Optional[Any] = None) -> Dict[str, Any]:
    """
    Build native default parameters for DCC processing pipeline.
    Precedence: CLI args → Schema params → Native defaults
    
    Uses schema-driven parameter keys from registry when available.
    """
    status_print("Building native default parameters...", min_level=3)
    
    # Helper to get canonical key from registry or use fallback
    def key(param_name: str) -> str:
        if registry and hasattr(registry, 'get_canonical_key'):
            return registry.get_canonical_key(param_name)
        return param_name
    
    # Platform-specific defaults (for reference, not used in precedence)
    platform_defaults = {
        key("win_upload_file"): r"K:\J Submission\Submittal and RFI Tracker Lists.xlsx",
        key("win_download_path"): r"K:\J Submission\AI Tools and Report\data_output",
        key("linux_upload_file"): str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        key("linux_download_path"): str(base_path / "output"),
        key("colab_upload_file"): "/content/sample_data/Submittal and RFI Tracker Lists.xlsx",
        key("colab_download_path"): "/content/output",
    }
    
    # Standardized native defaults using schema-driven keys
    return {
        # Core processing parameters (consistent with CLI and schema)
        key("debug_dev_mode"): False,
        key("overwrite_existing_downloads"): True,
        key("start_col"): "P",
        key("end_col"): "AP",
        key("header_row_index"): 4,
        key("upload_sheet_name"): "Prolog Submittals ",
        key("schema_register_file"): str(default_schema_path(base_path)),
        key("upload_file_name"): str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        key("download_file_path"): str(base_path / "output"),
        
        # Infrastructure directory parameters (schema-driven, not hardcoded)
        key("data_dir"): "data",
        key("config_dir"): "config",
        key("schema_dir"): "schemas",
        
        # Platform-specific defaults (kept for reference, not used in precedence)
        key("platform_defaults"): platform_defaults,
        
        # Legacy fallback keys (for backward compatibility)
        key("win_upload_file_fallback"): str(base_path / "data" / "Submittal and RFI Tracker Lists.xlsx"),
        key("win_download_path_fallback"): str(base_path / "output"),
    }


def resolve_effective_parameters(
    schema_path: Path,
    cli_args: Dict[str, Any],
    native_defaults: Dict[str, Any],
    load_schema_params_fn: Any = None,
    registry: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Resolve effective parameters with precedence: CLI → Schema → Native.
    
    Uses schema-driven parameter keys from registry when available.
    """
    status_print("Resolving effective parameters...", min_level=3)
    effective_parameters = native_defaults.copy()
    
    # Helper to get canonical key from registry or use fallback
    def key(param_name: str) -> str:
        if registry and hasattr(registry, 'get_canonical_key'):
            return registry.get_canonical_key(param_name)
        return param_name
    
    if load_schema_params_fn:
        try:
            schema_parameters = load_schema_params_fn(schema_path)
            effective_parameters.update(schema_parameters)
            status_print(f"Loaded schema parameters from {schema_path}", min_level=3)
        except Exception as exc:
            status_print(f"WARNING: Could not load schema parameters: {exc}", min_level=2)
    
    effective_parameters.update(cli_args)
    effective_parameters[key("schema_register_file")] = str(schema_path)
    debug_print(f"Effective parameters: {effective_parameters}")
    return effective_parameters


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Legacy functions (Phase 1/2 - backward compatible)
    "create_parser",
    "parse_cli_args",
    "build_native_defaults",
    "resolve_effective_parameters",
    "VERBOSE_LEVELS",
    
    # Phase 3: Registry-driven functions (NEW)
    "create_parser_from_registry",
    "parse_cli_args_from_registry",
    "validate_cli_args_against_registry",
    "validate_parameter_contract",
    "get_unregistered_parameters_report",
    "get_registry_for_cli",
    "parse_cli_args_enhanced",
    
    # Toggles and utilities
    "_use_registry_validation",
    "_REGISTRY_AVAILABLE",
]
