"""
Path resolution functions with system context.
"""
from pathlib import Path
from typing import Optional, Union, Dict, Any

from utility_engine.paths.path_models import PathResolutionResult
from utility_engine.paths.path_core import (
    get_system_context,
    normalize_path_separators,
    resolve_relative_to_base,
)


def resolve_with_system_context(
    path: Union[str, Path],
    base_path: Optional[Path] = None,
    system_context: Optional[str] = None
) -> PathResolutionResult:
    """
    Resolve path considering current system context.

    Args:
        path: Path to resolve
        base_path: Base path for relative resolution
        system_context: System context (auto-detected if None)

    Returns:
        PathResolutionResult with comprehensive information
    """
    original_path = path
    system_context = system_context or get_system_context()

    # Normalize path separators
    normalized_path = normalize_path_separators(path, system_context)

    # Resolve relative to base path
    resolved_path = resolve_relative_to_base(normalized_path, base_path)

    # Determine resolution method
    if str(path) == str(resolved_path):
        resolution_method = "direct"
    elif base_path is not None:
        resolution_method = "relative_to_base"
    else:
        resolution_method = "relative_to_cwd"

    # Check path existence and type
    exists = resolved_path.exists()
    is_file = resolved_path.is_file() if exists else False
    is_directory = resolved_path.is_dir() if exists else False

    # Collect errors
    errors = []
    if not exists:
        errors.append(f"Path does not exist: {resolved_path}")

    return PathResolutionResult(
        resolved_path=resolved_path,
        original_path=original_path,
        system_context=system_context,
        resolution_method=resolution_method,
        is_absolute=resolved_path.is_absolute(),
        exists=exists,
        is_file=is_file,
        is_directory=is_directory,
        errors=errors
    )


def safe_resolve(
    path: Union[str, Path],
    base_path: Optional[Path] = None,
    create_if_missing: bool = False,
    system_context: Optional[str] = None
) -> Path:
    """
    Safely resolve path with system context consideration.

    Args:
        path: Path to resolve
        base_path: Base path for relative resolution
        create_if_missing: Whether to create parent directories if missing
        system_context: System context (auto-detected if None)

    Returns:
        Resolved Path object

    Raises:
        ValueError: If path cannot be resolved or created
    """
    result = resolve_with_system_context(path, base_path, system_context)

    # Check for resolution errors
    if result.errors and not create_if_missing:
        raise ValueError(f"Path resolution failed: {'; '.join(result.errors)}")

    # Create parent directories if requested
    if create_if_missing and not result.exists:
        try:
            result.resolved_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create parent directory: {e}")

    return result.resolved_path


def safe_resolve_batch(
    paths: list[Union[str, Path]],
    base_path: Optional[Path] = None,
    create_if_missing: bool = False,
    system_context: Optional[str] = None
) -> Dict[Union[str, Path], PathResolutionResult]:
    """
    Resolve multiple paths with system context consideration.

    Args:
        paths: List of paths to resolve
        base_path: Base path for relative resolution
        create_if_missing: Whether to create parent directories if missing
        system_context: System context (auto-detected if None)

    Returns:
        Dictionary mapping original paths to resolution results
    """
    results = {}

    for path in paths:
        try:
            result = resolve_with_system_context(path, base_path, system_context)

            # Create parent directories if requested
            if create_if_missing and not result.exists:
                try:
                    result.resolved_path.parent.mkdir(parents=True, exist_ok=True)
                    # Update result after creation
                    result.exists = result.resolved_path.exists()
                    result.errors = []  # Clear errors after successful creation
                except Exception as e:
                    result.errors.append(f"Cannot create parent directory: {e}")

            results[path] = result
        except Exception as e:
            # Create error result
            results[path] = PathResolutionResult(
                resolved_path=Path(path),
                original_path=path,
                system_context=system_context or get_system_context(),
                resolution_method="failed",
                is_absolute=False,
                exists=False,
                is_file=False,
                is_directory=False,
                errors=[str(e)]
            )

    return results


def validate_path_resolutions(
    results: Dict[Union[str, Path], PathResolutionResult],
    require_existence: bool = True
) -> Dict[str, Any]:
    """
    Validate path resolution results.

    Args:
        results: Dictionary of path resolution results
        require_existence: Whether paths must exist

    Returns:
        Validation summary with errors and warnings
    """
    validation = {
        "total_paths": len(results),
        "resolved_successfully": 0,
        "exist": 0,
        "missing": 0,
        "errors": [],
        "warnings": [],
        "details": []
    }

    for original_path, result in results.items():
        detail = {
            "original": str(original_path),
            "resolved": str(result.resolved_path),
            "method": result.resolution_method,
            "exists": result.exists,
            "errors": result.errors
        }
        validation["details"].append(detail)

        if result.errors:
            if require_existence:
                validation["errors"].extend(result.errors)
            else:
                validation["warnings"].extend(result.errors)
        else:
            validation["resolved_successfully"] += 1

        if result.exists:
            validation["exist"] += 1
        else:
            validation["missing"] += 1
            if require_existence:
                validation["errors"].append(f"Path does not exist: {result.resolved_path}")

    return validation


def get_path_info(path: Union[str, Path], base_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Get comprehensive path information.

    Args:
        path: Path to analyze
        base_path: Base path for relative resolution

    Returns:
        Dictionary with comprehensive path information
    """
    result = resolve_with_system_context(path, base_path)

    info = {
        "original_path": str(result.original_path),
        "resolved_path": str(result.resolved_path),
        "system_context": result.system_context,
        "resolution_method": result.resolution_method,
        "is_absolute": result.is_absolute,
        "exists": result.exists,
        "is_file": result.is_file,
        "is_directory": result.is_directory,
        "parent_exists": result.resolved_path.parent.exists(),
        "suffix": result.resolved_path.suffix,
        "stem": result.resolved_path.stem,
        "name": result.resolved_path.name,
        "errors": result.errors
    }

    # Add additional system-specific information
    if result.system_context == "windows":
        info["drive"] = result.resolved_path.drive if result.is_absolute else ""
        info["unc_path"] = str(result.resolved_path).startswith("\\\\")
    else:
        info["is_symlink"] = result.resolved_path.is_symlink() if result.exists else False

    return info

