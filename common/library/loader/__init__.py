"""
Common loader library — schema discovery, file resolution, and $id URI registry.
"""
from .schema_discovery import discover_schema_files, discover_schema_files_tier3, find_schema_file, safe_resolve
from .ref_resolver import build_uri_registry

__all__ = [
    "discover_schema_files",
    "discover_schema_files_tier3",
    "find_schema_file",
    "safe_resolve",
    "build_uri_registry",
]
