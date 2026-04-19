import importlib
import platform
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

from .logging import (
    status_print,
    debug_print,
)

def test_environment(base_path: Path | None = None) -> Dict[str, Any]:
    """Test environment and required libraries."""
    status_print("Testing environment and required libraries...", min_level=2)

    # Ensure workflow/ is in sys.path so engine module imports resolve
    # regardless of the working directory the pipeline is launched from.
    if base_path is not None:
        workflow_dir = str(Path(base_path) / "workflow")
    else:
        workflow_dir = str(Path(__file__).parent.parent.parent)
    if workflow_dir not in sys.path:
        sys.path.insert(0, workflow_dir)

    # Import inside function to avoid circular imports if any
    from ..core.validator import ProjectSetupValidator

    # Use ProjectSetupValidator to load dependencies from project_config.json
    try:
        validator = ProjectSetupValidator(base_path=base_path)
        project_setup_data = validator.project_setup
        dependencies = project_setup_data.get("dependencies", {})

        required_modules = dependencies.get("required", [])
        optional_modules = dependencies.get("optional", [])

        # Engine modules are internal — import failures are warnings, not errors
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

    # Test required external modules — failures block the pipeline
    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
            results["required_modules"][module_name] = "ok"
        except Exception as exc:
            results["required_modules"][module_name] = f"error: {exc}"
            results["errors"].append(f"{module_name}: {exc}")

    # Test optional modules — failures are warnings only
    for module_name in optional_modules:
        try:
            importlib.import_module(module_name)
            results["optional_modules"][module_name] = "ok"
        except Exception as exc:
            results["optional_modules"][module_name] = f"warning: {exc}"

    # Test internal engine modules — failures are warnings, not pipeline blockers
    # These depend on sys.path being set up correctly, which is guaranteed above.
    for module_name, attributes in engine_modules:
        try:
            module = importlib.import_module(module_name)
            for attr in attributes:
                getattr(module, attr)
            results["engine_modules"][module_name] = "ok"
        except Exception as exc:
            # Engine import failures are non-fatal: log as warning, do not add to errors
            results["engine_modules"][module_name] = f"warning: {exc}"
            debug_print(f"Engine module warning ({module_name}): {exc}")

    results["ready"] = not results["errors"]
    if results["ready"]:
        status_print("Environment test passed.", min_level=3)
    else:
        status_print("Environment test failed. Missing required packages:", min_level=2)
        for err in results["errors"]:
            status_print(f"  ✗ {err}", min_level=2)
        status_print("Run: pip install " + " ".join(
            m for m in required_modules
            if results["required_modules"].get(m, "").startswith("error")
        ), min_level=2)

    debug_print(f"Environment details: {results}")
    return results