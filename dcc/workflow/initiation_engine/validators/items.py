"""
Validation functions for project setup items.
Extracted from project_setup_validation.py validation methods.
"""

from pathlib import Path
from typing import Dict, Any, Iterable

from ..system.os_detect import should_auto_create_folders
from ..utils.logging import log_status, log_warning


def record_path_check(
    results: Dict[str, Any],
    category: str,
    name: str,
    path: Path,
    required: bool,
    exists: bool,
    description: str,
    item_type: str,
) -> None:
    """
    Record a path check result in the results accumulator.

    This helper function standardizes the recording of validation results
    across all validation categories (folders, files, environment).

    Args:
        results: Validation results accumulator dictionary.
        category: Category key in results (e.g., 'folders', 'root_files').
        name: Display name of the item being validated.
        path: Resolved Path object for the item.
        required: Whether this item is required (True) or optional (False).
        exists: Whether the item exists on disk.
        description: Human-readable description of the item.
        item_type: Type of item ('folder' or 'file').

    Breadcrumb Comments:
        - results: Initialized in ProjectSetupValidator.validate().
                   Passed here and modified by appending validation results.
                   Accumulates entries for format_report() consumption.
        - category: Determines which results section receives the entry.
        - path: Resolved by validation functions before calling this.
        - exists: Determined by is_dir() or is_file() checks.
    """
    results[category].append(
        {
            "name": name,
            "path": str(path),
            "required": required,
            "exists": exists,
            "description": description,
            "item_type": item_type,
        }
    )


def ensure_folder(path: Path) -> bool:
    """
    Create folder if it doesn't exist.

    Args:
        path: Path object for the folder to create.

    Returns:
        True if the folder exists after the operation.

    Breadcrumb Comments:
        - path: Received from validate_folders() for folders that don't exist.
                Modified here by mkdir() to create the directory structure.
                Validated by is_dir() check before returning.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path.is_dir()


def validate_folders(
    results: Dict[str, Any],
    folders: Iterable[Dict[str, Any]],
    base_path: Path,
    os_info: Dict[str, str],
) -> None:
    """
    Validate project folders, auto-creating if enabled.

    Iterates through folder specifications from project_setup.json,
    checks existence, and auto-creates if OS supports it.

    Args:
        results: Validation results accumulator to populate.
        folders: Iterable of folder specification dictionaries from schema.
        base_path: Project root directory for resolving relative paths.
        os_info: OS detection info to determine auto-creation capability.

    Breadcrumb Comments:
        - results: Initialized in ProjectSetupValidator.validate().
                   Modified here via record_path_check() for each folder.
                   Also adds 'auto_created' and 'schema_auto_created' flags.
        - folders: Extracted from project_setup['folders'] in validate().
                   Consumed here to iterate and validate each folder spec.
        - base_path: Initialized in __init__ via normalize_path().
                     Consumed here to resolve relative folder paths.
        - os_info: Initialized in __init__ via detect_os().
                   Passed to should_auto_create_folders() to check capability.
    """
    auto_create_enabled = should_auto_create_folders(os_info)
    if auto_create_enabled:
        log_warning("Auto-creation enabled for this OS", "validators", "validate_folders")

    for folder in folders:
        if not isinstance(folder, dict):
            continue
        name = folder.get("name", "")
        if not name:
            continue
        required = bool(folder.get("required", True))
        path = base_path / name
        exists = path.is_dir()
        auto_created = False
        if not exists and should_auto_create_folders(os_info):
            auto_created = ensure_folder(path)
            exists = path.is_dir()

        record_path_check(
            results,
            "folders",
            name,
            path,
            required,
            exists,
            folder.get("purpose", ""),
            "folder",
        )
        results["folders"][-1]["auto_created"] = auto_created
        results["folders"][-1]["schema_auto_created"] = bool(folder.get("auto_created", False))

        # Log folder status with indentation (2 spaces per depth level)
        symbol = "[OK]" if exists else ("[MISS]" if required else "[WARN]")
        req_text = "required" if required else "optional"
        auto_text = " [created]" if auto_created else ""
        log_status(f"{symbol} {name} ({req_text}) -> {path}{auto_text}", "validators")


def validate_named_files(
    results: Dict[str, Any],
    category: str,
    items: Iterable[Dict[str, Any]],
    parent_dir: Path,
    name_key: str,
    description_key: str,
) -> None:
    """
    Validate named files in a category.

    Generic validator for file categories (root_files, schema_files,
    workflow_files, tool_files). Checks existence of each file.

    Args:
        results: Validation results accumulator to populate.
        category: Results key to store validation entries (e.g., 'root_files').
        items: Iterable of file specification dictionaries from schema.
        parent_dir: Base directory for resolving relative file paths.
        name_key: Dictionary key for the filename (e.g., 'name', 'filename').
        description_key: Dictionary key for the description (e.g., 'purpose', 'description').

    Breadcrumb Comments:
        - results: Initialized in ProjectSetupValidator.validate().
                   Modified here via record_path_check() for each file.
        - category: Passed from validate() for each file category.
                    Used as key in results dictionary.
        - items: Extracted from project_setup[category] in validate().
                 Categories: root_files, schema_files, workflow_files, tool_files.
        - parent_dir: Resolved from base_path in validate() for each category.
                      root_files -> base_path, others -> base_path / subdir.
    """
    log_warning(f"Validating {category} in {parent_dir}", "validators", "validate_named_files")

    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get(name_key, "")
        if not name:
            continue
        required = bool(item.get("required", True))
        path = parent_dir / name
        exists = path.is_file()
        record_path_check(
            results,
            category,
            name,
            path,
            required,
            exists,
            item.get(description_key, ""),
            "file",
        )

        # Log file status with indentation
        symbol = "[OK]" if exists else ("[MISS]" if required else "[WARN]")
        req_text = "required" if required else "optional"
        log_status(f"{symbol} {name} ({req_text}) -> {path}", "validators")


def validate_environment(
    results: Dict[str, Any],
    environment: Iterable[Dict[str, Any]],
    base_path: Path,
) -> None:
    """
    Validate environment specification files.

    Checks existence of environment files and records their
    setup commands and key dependencies.

    Args:
        results: Validation results accumulator to populate.
        environment: Iterable of environment specification dictionaries.
        base_path: Project root directory for resolving file paths.

    Breadcrumb Comments:
        - results: Initialized in ProjectSetupValidator.validate().
                   Modified here directly for each environment item.
        - environment: Extracted from project_setup['environment'] in validate().
        - base_path: Initialized in __init__ via normalize_path().
                     Used to resolve 'root' and subdirectory paths.
    """
    log_warning(f"Validating environment files in {base_path}", "validators", "validate_environment")

    for item in environment:
        if not isinstance(item, dict):
            continue
        filename = item.get("file", "")
        if not filename:
            continue
        location = item.get("location", "root")
        if location == "root":
            path = base_path / filename
        else:
            path = base_path / location / filename

        exists = path.is_file()
        required = bool(item.get("required", True))

        results["environment"].append(
            {
                "name": item.get("name", filename),
                "path": str(path),
                "required": required,
                "exists": exists,
                "location": location,
                "setup_commands": item.get("setup_commands", []),
                "key_dependencies": item.get("key_dependencies", []),
            }
        )

        # Log environment file status
        symbol = "[OK]" if exists else ("[MISS]" if required else "[WARN]")
        log_status(f"{symbol} {filename} ({location})", "validators")


def check_ready(results: Dict[str, Any]) -> bool:
    """
    Check if all required items exist.

    Scans all validation sections to verify that every required
    folder, file, and environment item exists on disk.

    Args:
        results: Validation results dictionary containing all categories.

    Returns:
        True if all required items exist, False otherwise.

    Breadcrumb Comments:
        - results: Initialized in ProjectSetupValidator.validate().
                   Populated by validate_folders(), validate_named_files(),
                   validate_environment() before this check.
                   Used here to scan 'required' and 'exists' flags.
                   Modified here to set results['ready'] boolean.
        - Required sections scanned: folders, root_files, schema_files,
          workflow_files, tool_files, environment.
    """
    if results["errors"]:
        return False

    required_sections = ["folders", "root_files", "schema_files", "workflow_files", "tool_files", "environment"]
    for section in required_sections:
        for item in results.get(section, []):
            if item.get("required") and not item.get("exists"):
                return False

    return True
