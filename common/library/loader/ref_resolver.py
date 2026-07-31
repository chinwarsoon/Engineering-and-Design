"""
URI-to-file registry extracted from DCC ref_resolver.py.

Provides:
  - build_uri_registry() — scan directories for $id declarations

Revision: 0.1
Date: 2026-07-29
Author: opencode
Summary: Extracted from dcc/workflow/schema_engine/loader/ref_resolver.py for cross-project reuse (I262/T1.178).
"""
import json
from pathlib import Path
from typing import Dict, List

from .schema_discovery import safe_resolve


def build_uri_registry(schema_directories: List[Path]) -> Dict[str, Path]:
    """Build URI-to-file registry by scanning schema directories for $id declarations.

    Args:
        schema_directories: Directories to scan for JSON schema files.

    Returns:
        Dict mapping $id URI (e.g., https://eks.engineering/schemas/name)
        to resolved file path.

    Raises:
        ValueError: If the same $id is declared in multiple files (duplicate).
    """
    uri_registry: Dict[str, Path] = {}

    for directory in schema_directories:
        if not directory.exists():
            continue
        for schema_file in directory.glob("*.json"):
            try:
                with schema_file.open("r", encoding="utf-8") as f:
                    schema_data = json.load(f)
                schema_id = schema_data.get("$id")
                if schema_id:
                    if schema_id in uri_registry:
                        raise ValueError(
                            f"Duplicate $id '{schema_id}' in '{schema_file}' "
                            f"(first declared in '{uri_registry[schema_id]}')"
                        )
                    uri_registry[schema_id] = safe_resolve(schema_file)
            except (json.JSONDecodeError, IOError):
                continue

    return uri_registry
