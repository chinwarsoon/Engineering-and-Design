"""
Parameter resolution functions for CLI.
"""
from pathlib import Path
from typing import Dict, Any, Optional

from utility_engine.console import status_print, debug_print


def resolve_effective_parameters(
    dcc_schema_path: Path,
    cli_args: Dict[str, Any],
    native_defaults: Dict[str, Any],
    load_schema_params_fn = None,
    registry: Optional[Any] = None,
    system_params_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Resolve effective parameters with precedence: CLI → Schema → Native.

    Supports dual domain loading:
    - System parameters from project_config.json (if system_params_path provided)
    - DCC parameters from dcc_register_config.json (via dcc_schema_path)

    Uses schema-driven parameter keys from registry when available.
    """
    status_print("Resolving effective parameters...", min_level=3)
    effective_parameters = native_defaults.copy()

    # Helper to get canonical key from registry or use fallback
    def key(param_name: str) -> str:
        if registry and hasattr(registry, 'get_canonical_key'):
            return registry.get_canonical_key(param_name)
        return param_name

    # Load system parameters first (lower precedence)
    if system_params_path and load_schema_params_fn:
        try:
            system_parameters = load_schema_params_fn(system_params_path, key="system_parameters")
            effective_parameters.update(system_parameters)
            status_print(f"Loaded system parameters from {system_params_path}", min_level=3)
        except Exception as exc:
            status_print(f"WARNING: Could not load system parameters: {exc}", min_level=2)

    # Load DCC parameters (higher precedence than system, lower than CLI)
    if load_schema_params_fn:
        try:
            dcc_parameters = load_schema_params_fn(dcc_schema_path, key="dcc_parameters")
            effective_parameters.update(dcc_parameters)
            status_print(f"Loaded DCC parameters from {dcc_schema_path}", min_level=3)
        except Exception as exc:
            status_print(f"WARNING: Could not load DCC parameters: {exc}", min_level=2)

    effective_parameters.update(cli_args)
    effective_parameters[key("schema_register_file")] = str(dcc_schema_path)
    debug_print(f"Effective parameters: {effective_parameters}")
    return effective_parameters
