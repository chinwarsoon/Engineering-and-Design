"""
Registry-driven CLI functions (Phase 3).
These functions use ParameterTypeRegistry for type-driven CLI generation.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from utility_engine.console import status_print, debug_print
from core_engine.paths import default_base_path, default_schema_path


def get_registry_for_cli(
    global_params_path: Optional[Path] = None,
    base_path: Optional[Path] = None
) -> Any:
    """
    Get parameter registry for CLI operations.

    Args:
        global_params_path: Path to global_parameters.json
        base_path: Project base path

    Returns:
        ParameterTypeRegistry instance or None if not available
    """
    try:
        from utility_engine.validation import get_parameter_registry, ParameterTypeRegistry

        if global_params_path is None:
            if base_path is None:
                base_path = default_base_path()
            global_params_path = base_path / "config" / "global_parameters.json"

        if not global_params_path.exists():
            debug_print(f"Global parameters file not found: {global_params_path}")
            return None

        return get_parameter_registry(str(global_params_path))

    except ImportError:
        debug_print("ParameterTypeRegistry not available")
        return None
    except Exception as exc:
        debug_print(f"Error loading parameter registry: {exc}")
        return None


def create_parser_from_registry(
    base_path: Path,
    registry: Any = None
) -> Any:
    """
    Create CLI argument parser using registry definitions.

    Args:
        base_path: Project base path
        registry: ParameterTypeRegistry instance (loaded if None)

    Returns:
        Configured ArgumentParser
    """
    import argparse

    if registry is None:
        registry = get_registry_for_cli(base_path=base_path)

    parser = argparse.ArgumentParser(
        description="DCC Engine Pipeline - Registry-driven CLI"
    )

    # Add verbose flag
    parser.add_argument(
        "--verbose", "-v",
        choices=["quiet", "normal", "debug", "trace"],
        default="normal",
        help="Output verbosity level"
    )

    # If registry available, add schema-driven arguments
    if registry and hasattr(registry, 'parameters'):
        for param_name, param_def in registry.parameters.items():
            if not param_def.get('cli_visible', True):
                continue

            arg_name = f"--{param_name.replace('_', '-')}"
            param_type = param_def.get('type', 'string')
            default_val = param_def.get('default')
            help_text = param_def.get('description', f'{param_name} parameter')
            required = param_def.get('required', False)

            # Map parameter types to argparse types
            type_map = {
                'integer': int,
                'float': float,
                'boolean': lambda x: x.lower() in ('true', '1', 'yes'),
                'string': str,
            }
            arg_type = type_map.get(param_type, str)

            parser.add_argument(
                arg_name,
                type=arg_type,
                default=default_val,
                help=help_text,
                required=required
            )

    return parser


def parse_cli_args_from_registry(
    base_path: Optional[Path] = None,
    registry: Any = None
) -> Tuple[Any, Dict[str, Any], bool]:
    """
    Parse CLI arguments using registry-driven parser.

    Args:
        base_path: Project base path
        registry: ParameterTypeRegistry instance

    Returns:
        Tuple of (args_namespace, cli_args_dict, cli_overrides_provided)
    """
    if base_path is None:
        base_path = default_base_path()

    if registry is None:
        registry = get_registry_for_cli(base_path=base_path)

    parser = create_parser_from_registry(base_path, registry)
    args, unknown_args = parser.parse_known_args()

    cli_args = {}
    verbose_explicitly_set = "--verbose" in sys.argv or "-v" in sys.argv

    if verbose_explicitly_set:
        cli_args["verbose_level"] = args.verbose

    # Map args back to parameter names
    if registry and hasattr(registry, 'parameters'):
        for param_name in registry.parameters.keys():
            attr_name = param_name.replace('-', '_')
            if hasattr(args, attr_name):
                value = getattr(args, attr_name)
                if value is not None:
                    cli_args[param_name] = value

    cli_overrides_provided = bool(cli_args)

    return args, cli_args, cli_overrides_provided


def validate_cli_args_against_registry(
    cli_args: Dict[str, Any],
    registry: Any,
    strict: bool = False
) -> Tuple[bool, List[str]]:
    """
    Validate CLI arguments against registry schema.

    Args:
        cli_args: Parsed CLI arguments
        registry: ParameterTypeRegistry instance
        strict: If True, reject unknown parameters

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if registry is None:
        return True, []

    errors = []

    if not hasattr(registry, 'parameters'):
        return True, []

    # Check for unknown parameters if strict mode
    if strict:
        known_params = set(registry.parameters.keys())
        unknown_params = set(cli_args.keys()) - known_params
        if unknown_params:
            errors.append(f"Unknown parameters: {', '.join(unknown_params)}")

    # Validate each parameter
    for param_name, value in cli_args.items():
        if param_name not in registry.parameters:
            continue

        param_def = registry.parameters[param_name]
        param_type = param_def.get('type', 'string')

        # Type validation
        type_validators = {
            'integer': lambda x: isinstance(x, int) or (isinstance(x, str) and x.isdigit()),
            'float': lambda x: isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.', '').isdigit()),
            'boolean': lambda x: isinstance(x, bool) or str(x).lower() in ('true', 'false', '1', '0', 'yes', 'no'),
            'string': lambda x: isinstance(x, str),
        }

        validator = type_validators.get(param_type, lambda x: True)
        if not validator(value):
            errors.append(f"Invalid type for {param_name}: expected {param_type}, got {type(value).__name__}")

    return len(errors) == 0, errors


def get_unregistered_parameters_report(
    cli_args: Dict[str, Any],
    registry: Any
) -> Dict[str, Any]:
    """
    Generate report of CLI parameters not in registry.

    Args:
        cli_args: Parsed CLI arguments
        registry: ParameterTypeRegistry instance

    Returns:
        Report dictionary with unregistered and registered parameters
    """
    if registry is None or not hasattr(registry, 'parameters'):
        return {
            "unregistered": list(cli_args.keys()),
            "registered": [],
            "total_cli_params": len(cli_args),
            "total_registry_params": 0
        }

    registry_params = set(registry.parameters.keys())
    cli_params = set(cli_args.keys())

    return {
        "unregistered": list(cli_params - registry_params),
        "registered": list(cli_params & registry_params),
        "total_cli_params": len(cli_args),
        "total_registry_params": len(registry_params)
    }


def parse_cli_args_enhanced(
    base_path: Optional[Path] = None,
    use_registry: bool = True
) -> Tuple[Any, Dict[str, Any], bool, Any]:
    """
    Enhanced CLI parsing with registry integration.

    Args:
        base_path: Project base path
        use_registry: Whether to use registry-driven parsing

    Returns:
        Tuple of (args, cli_args, overrides_provided, registry)
    """
    if use_registry:
        registry = get_registry_for_cli(base_path=base_path)
        if registry:
            args, cli_args, overrides = parse_cli_args_from_registry(base_path, registry)
            return args, cli_args, overrides, registry

    # Fallback to legacy parsing
    from utility_engine.cli.cli_parser import parse_cli_args
    args, cli_args, overrides = parse_cli_args(base_path)
    return args, cli_args, overrides, None
