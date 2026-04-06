"""
Validation status persistence and checking.
Extracted from schema_validation.py status functions.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

from dcc.workflow.schema_engine.engine.utils.paths import safe_resolve

logger = logging.getLogger(__name__)


def get_validation_status_path(schema_file: str | Path) -> Path:
    """Return the default persisted schema-validation status path."""
    schema_path = safe_resolve(Path(schema_file))
    project_root = schema_path.parents[2] if len(schema_path.parents) >= 3 else schema_path.parent
    return project_root / "output" / "schema_validation_status.json"


def _tracked_schema_files(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build tracked schema file metadata for pipeline enforcement."""
    tracked_files: List[Dict[str, Any]] = []
    main_schema_path = safe_resolve(Path(results["main_schema_path"]))
    if main_schema_path.exists():
        tracked_files.append(
            {
                "path": str(main_schema_path),
                "mtime_ns": main_schema_path.stat().st_mtime_ns,
            }
        )

    seen_paths = {str(main_schema_path)}
    for item in results.get("references", []):
        resolved_path = item.get("resolved_path")
        if not resolved_path or resolved_path in seen_paths:
            continue
        path = safe_resolve(Path(resolved_path))
        if not path.exists():
            continue
        tracked_files.append(
            {
                "path": str(path),
                "mtime_ns": path.stat().st_mtime_ns,
            }
        )
        seen_paths.add(str(resolved_path))

    return tracked_files


def write_validation_status(results: Dict[str, Any], status_path: str | Path | None = None) -> Path:
    """Persist schema-validation status for downstream pipeline steps."""
    destination = safe_resolve(Path(status_path)) if status_path else get_validation_status_path(results["main_schema_path"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "main_schema_path": results["main_schema_path"],
        "ready": bool(results.get("ready", False)),
        "errors": results.get("errors", []),
        "dependency_cycle": results.get("dependency_cycle", []),
        "tracked_files": _tracked_schema_files(results),
    }
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination


def load_validation_status(schema_file: str | Path, status_path: str | Path | None = None) -> Dict[str, Any]:
    """Load the persisted schema-validation status for a schema file."""
    source = safe_resolve(Path(status_path)) if status_path else get_validation_status_path(schema_file)
    with source.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_validation_status(schema_file: str | Path, status_path: str | Path | None = None) -> tuple[bool, str]:
    """Check whether a persisted validation status is present and current."""
    schema_path = safe_resolve(Path(schema_file))
    try:
        status = load_validation_status(schema_path, status_path)
    except FileNotFoundError:
        return False, (
            f"Schema validation status not found for {schema_path}. "
            f"Run `python dcc/workflow/schema_validation.py --schema-file {schema_path}` first."
        )
    except Exception as exc:
        return False, f"Could not read schema validation status for {schema_path}: {exc}"

    if safe_resolve(Path(status.get("main_schema_path", ""))) != schema_path:
        return False, (
            f"Schema validation status does not match {schema_path}. "
            f"Run `python dcc/workflow/schema_validation.py --schema-file {schema_path}` first."
        )

    if not status.get("ready", False):
        return False, (
            f"Schema validation status for {schema_path} is not ready. "
            f"Fix schema validation errors and rerun schema_validation.py."
        )

    for item in status.get("tracked_files", []):
        tracked_path = safe_resolve(Path(item["path"]))
        if not tracked_path.exists():
            return False, (
                f"Schema validation status is stale because {tracked_path} is missing. "
                f"Rerun schema_validation.py."
            )
        if tracked_path.stat().st_mtime_ns != item.get("mtime_ns"):
            return False, (
                f"Schema validation status is stale because {tracked_path} changed. "
                f"Rerun schema_validation.py."
            )

    return True, ""
