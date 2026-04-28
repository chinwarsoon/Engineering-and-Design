"""
Foundation system utilities for environment testing, OS detection, and dependency validation.
"""
import importlib
import json
import platform
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Callable

from utility_engine.console import status_print, debug_print


def detect_os() -> Dict[str, str]:
    """
    Detect operating system and return normalized info.
    """
    system_name = platform.system().strip() or "Unknown"
    normalized_name = {
        "Windows": "windows",
        "Linux": "linux",
        "Darwin": "macos",
    }.get(system_name, system_name.lower())
    return {
        "system": system_name,
        "normalized": normalized_name,
    }


def should_auto_create_folders(os_info: Dict[str, str]) -> bool:
    """
    Check if folders should be auto-created on this OS.
    """
    return os_info["normalized"] in {"windows", "linux", "macos"}


def test_environment(base_path: Path, status_print_fn: Callable = status_print) -> Dict[str, Any]:
    """
    Test environment and required libraries using the project configuration.
    """
    status_print_fn("Testing environment and required libraries...", min_level=2)

    # Ensure workflow/ is in sys.path
    workflow_dir = str(base_path / "workflow")
    if workflow_dir not in sys.path:
        sys.path.insert(0, workflow_dir)

    try:
        # Resolve project setup schema for dependencies
        setup_path = base_path / "config" / "schemas" / "project_setup.json"
        if not setup_path.exists():
             # Fallback to defaults if schema is missing
             required_modules = ["pandas", "openpyxl", "yaml", "duckdb"]
             optional_modules = ["pytest", "black"]
             engine_modules = []
        else:
            with setup_path.open("r", encoding="utf-8") as handle:
                schema_document = json.load(handle)

            project_setup_data = schema_document.get("project_setup", {})
            dependencies = project_setup_data.get("dependencies", {})

            required_modules = dependencies.get("required", [])
            optional_modules = dependencies.get("optional", [])
            engine_modules_raw = dependencies.get("engines", [])
            engine_modules = [(e["module"], e["members"]) for e in engine_modules_raw]

    except Exception as exc:
        debug_print(f"Failed to load project_setup.json: {exc}")
        required_modules = ["pandas", "openpyxl"]
        optional_modules = []
        engine_modules = []

    results: Dict[str, Any] = {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "required_modules": {},
        "optional_modules": {},
        "engine_modules": {},
        "errors": [],
        "ready": True,
    }

    # Test required external modules
    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
            results["required_modules"][module_name] = "ok"
        except Exception as exc:
            results["required_modules"][module_name] = f"error: {exc}"
            results["errors"].append(f"{module_name}: {exc}")

    # Test optional modules
    for module_name in optional_modules:
        try:
            importlib.import_module(module_name)
            results["optional_modules"][module_name] = "ok"
        except Exception as exc:
            results["optional_modules"][module_name] = f"warning: {exc}"

    # Test internal engine modules
    for module_name, attributes in engine_modules:
        try:
            module = importlib.import_module(module_name)
            for attr in attributes:
                getattr(module, attr)
            results["engine_modules"][module_name] = "ok"
        except Exception as exc:
            results["engine_modules"][module_name] = f"warning: {exc}"
            debug_print(f"Engine module warning ({module_name}): {exc}")

    results["ready"] = not results["errors"]
    if results["ready"]:
        status_print_fn("Environment ready      Required dependencies available", min_level=3)
    else:
        status_print_fn("Environment test failed. Missing required packages:", min_level=2)
        for err in results["errors"]:
            status_print_fn(f"  ✗ {err}", min_level=2)

    return results
