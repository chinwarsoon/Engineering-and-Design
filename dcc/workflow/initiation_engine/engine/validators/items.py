"""
Validation functions for project setup items.
Extracted from project_setup_validation.py validation methods.
"""

from pathlib import Path
from typing import Dict, Any, Iterable

from dcc.workflow.initiation_engine.engine.system.os_detect import should_auto_create_folders


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
    """Record a path check result."""
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
    """Create folder if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path.is_dir()


def validate_folders(
    results: Dict[str, Any],
    folders: Iterable[Dict[str, Any]],
    base_path: Path,
    os_info: Dict[str, str],
) -> None:
    """Validate project folders, auto-creating if enabled."""
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


def validate_named_files(
    results: Dict[str, Any],
    category: str,
    items: Iterable[Dict[str, Any]],
    parent_dir: Path,
    name_key: str,
    description_key: str,
) -> None:
    """Validate named files in a category."""
    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get(name_key, "")
        if not name:
            continue
        required = bool(item.get("required", True))
        path = parent_dir / name
        record_path_check(
            results,
            category,
            name,
            path,
            required,
            path.is_file(),
            item.get(description_key, ""),
            "file",
        )


def validate_environment(
    results: Dict[str, Any],
    environment: Iterable[Dict[str, Any]],
    base_path: Path,
) -> None:
    """Validate environment specification files."""
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

        results["environment"].append(
            {
                "name": item.get("name", filename),
                "path": str(path),
                "required": bool(item.get("required", True)),
                "exists": path.is_file(),
                "location": location,
                "setup_commands": item.get("setup_commands", []),
                "key_dependencies": item.get("key_dependencies", []),
            }
        )


def check_ready(results: Dict[str, Any]) -> bool:
    """Check if all required items exist."""
    if results["errors"]:
        return False

    required_sections = ["folders", "root_files", "schema_files", "workflow_files", "tool_files", "environment"]
    for section in required_sections:
        for item in results.get(section, []):
            if item.get("required") and not item.get("exists"):
                return False

    return True
