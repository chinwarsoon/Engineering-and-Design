import importlib
import platform
from pathlib import Path
from typing import Dict, Any, List, Tuple

from .logging import (
    status_print,
    debug_print,
)

def test_environment(base_path: Path | None = None) -> Dict[str, Any]:
    """Test environment and required libraries."""
    status_print("Testing environment and required libraries...")
    
    # Import inside function to avoid circular imports if any
    from ..core.validator import ProjectSetupValidator
    
    # Use ProjectSetupValidator to load dependencies from project_setup.json
    try:
        validator = ProjectSetupValidator(base_path=base_path)
        project_setup_data = validator.project_setup
        dependencies = project_setup_data.get("dependencies", {})
        
        required_modules = dependencies.get("required", [])
        optional_modules = dependencies.get("optional", [])
        
        # Load engine modules from schema
        engine_modules_raw = dependencies.get("engines", [])
        engine_modules = [(e["module"], e["members"]) for e in engine_modules_raw]
        
    except Exception as exc:
        debug_print(f"Failed to load project_setup.json: {exc}")
        required_modules = []
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
    
    # Test required modules
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
    
    # Test engine modules
    for module_name, attributes in engine_modules:
        try:
            module = importlib.import_module(module_name)
            for attr in attributes:
                getattr(module, attr)
            results["engine_modules"][module_name] = "ok"
        except Exception as exc:
            results["engine_modules"][module_name] = f"error: {exc}"
            results["errors"].append(f"{module_name}: {exc}")
    
    results["ready"] = not results["errors"]
    if results["ready"]:
        status_print("Environment test passed.")
    else:
        status_print("Environment test failed.")
    
    debug_print(f"Environment details: {results}")
    return results