"""
common.library.utility — Interface modules shared across all pipeline projects.

Modules
-------
validation/     L13 ValidationManager, ValidationItem, ValidationResult
factories/      L09 Factory ABC and config-driven create() pattern
ui/             L14 UIRequest, UIResponse, UIContractManager
file_hash       compute_file_hash(), FileHasher — SSOT streaming file hashing
synthetic_key   generate_synthetic_key() — stable UNRESOLVED-{hash} keys
file_discovery  FileDiscovery — extension-based file walking
change_detector FieldDiff, detect_changes() — before/after field-level diff
"""

from . import file_hash, synthetic_key, file_discovery, change_detector

__all__ = [
    "file_hash",
    "synthetic_key",
    "file_discovery",
    "change_detector",
]
