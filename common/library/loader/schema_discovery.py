"""
Schema discovery utilities extracted from DCC ref_resolver.py.

Provides:
  - discover_schema_files() — glob-based schema file discovery
  - find_schema_file() — multi-directory file lookup
  - safe_resolve() — absolute path without filesystem I/O
"""
from pathlib import Path
from typing import Dict, Any, List, Optional


def safe_resolve(path: Path) -> Path:
    """Return an absolute path without filesystem I/O (no resolve, no expanduser)."""
    return Path(path).absolute()


def find_schema_file(
    filename: str, search_directories: List[Path]
) -> Path:
    """Find a schema file in the given search directories.

    Args:
        filename: Schema filename to find.
        search_directories: Directories to search in order.

    Returns:
        Resolved path to schema file.

    Raises:
        FileNotFoundError: If not found in any directory.
    """
    for directory in search_directories:
        candidate = directory / filename
        if candidate.exists():
            return safe_resolve(candidate)
    search_paths = [str(d / filename) for d in search_directories]
    raise FileNotFoundError(
        f"Schema file '{filename}' not found. Searched:\n"
        + "\n".join(f"  - {p}" for p in search_paths)
    )


def discover_schema_files(
    project_setup: Dict[str, Any],
    project_root: Path,
) -> Dict[str, Dict[str, Any]]:
    """Extract schema catalog from project_setup config, including discovery_rules.

    Handles:
      1. Explicit schema_files: [{"filename": "...", "required": bool, ...}]
      2. discovery_rules: [{"pattern": "*.json", "directory": "...", ...}]

    Explicit entries always win over discovered entries when names collide.

    Args:
        project_setup: Config dict with optional ``schema_files`` and ``discovery_rules`` keys.
        project_root: Base path for resolving relative discovery directories.

    Returns:
        Dict mapping schema name (stem) to registration metadata::

            {
                "eks_base_schema": {
                    "filename": "eks/config/schemas/eks_base_schema.json",
                    "required": True,
                    "description": "...",
                    "registered": True,
                    "source": "explicit"
                },
                ...
            }
    """
    registry: Dict[str, Dict[str, Any]] = {}

    # ---- Phase 1: Explicit schema_files ----
    schema_files = project_setup.get("schema_files", [])
    for entry in schema_files:
        filename = entry.get("filename", "")
        if filename:
            schema_name = Path(filename).stem
            registry[schema_name] = {
                "filename": filename,
                "required": entry.get("required", False),
                "description": entry.get("description", ""),
                "registered": True,
                "source": "explicit",
            }

    # ---- Phase 2: discovery_rules (glob-based) ----
    discovery_rules = project_setup.get("discovery_rules", [])
    for rule in discovery_rules:
        pattern = rule.get("pattern")
        directory_rel = rule.get("directory", ".")
        recursive = rule.get("recursive", False)
        auto_register = rule.get("auto_register", True)
        exclude_patterns = rule.get("exclude_patterns", [])

        if not pattern or not auto_register:
            continue

        search_dir = safe_resolve(project_root / directory_rel)
        if not search_dir.exists():
            continue

        glob_pattern = f"**/{pattern}" if recursive else pattern
        for schema_file in search_dir.glob(glob_pattern):
            is_excluded = False
            for exclude in exclude_patterns:
                if schema_file.match(exclude):
                    is_excluded = True
                    break
            if is_excluded:
                continue

            schema_name = schema_file.stem
            if schema_name not in registry:
                registry[schema_name] = {
                    "filename": schema_file.name,
                    "path": str(safe_resolve(schema_file)),
                    "required": False,
                    "description": rule.get("category", "discovered"),
                    "registered": True,
                    "source": "discovery",
                }

    return registry
