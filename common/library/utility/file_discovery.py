"""
File Discovery Utility — common.library.utility.file_discovery.

Extension-based file walking with validation against an expected-type registry.
Encapsulates the glob-walking pattern used by ``FileScanner.scan()`` in EKS
so that dcc and code_tracer can reuse it without re-implementing the same loop.

Revision: 0.1
Date: 2026-07-19
Author: CodeBuddy
Summary: Extracted from eks.engine.core.file_scanner.FileScanner.scan()
         (T1.99.149 — I187).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

__all__ = ["FileDiscovery"]


class FileDiscovery:
    """
    Walk a directory tree and discover files matching a configurable
    extension map.

    Parameters
    ----------
    extension_map : dict[str, dict]
        Mapping of lower-case extension (without dot) to a metadata dict
        (e.g. ``{"pdf": {"display_name": "PDF", "parser_class": "..."}}``).
    recursive : bool
        If ``True`` (default), walk subdirectories recursively.

    Example::

        ext_map = {"pdf": {"display_name": "PDF Document", "parser_class": "pdf_parser"}}
        fd = FileDiscovery(ext_map)
        results = fd.scan("/data/project")
        # results → [{"file_path": "/data/project/doc.pdf", "file_name": "doc.pdf", ...}, ...]
    """

    def __init__(
        self,
        extension_map: Dict[str, Dict[str, Any]],
        recursive: bool = True,
    ):
        self.extension_map = {
            k.lower(): v for k, v in extension_map.items()
        }
        self.recursive = recursive

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def scan(self, root_dir: str | Path) -> List[Dict[str, Any]]:
        """
        Walk *root_dir* and return metadata for every file whose extension
        appears in ``extension_map``.

        Each result dict contains:
            - ``file_path``: absolute path as a string
            - ``file_name``: base name (including extension)
            - ``file_type``: lower-case extension without the dot
            - ``display_name``: human-readable label from extension_map
            - ``parser_class``: fully-qualified parser class path (or empty string)
        """
        root = Path(root_dir)
        if not root.is_dir():
            raise NotADirectoryError(f"Directory not found: {root}")

        discovered: List[Dict[str, Any]] = []
        pattern = "**/*" if self.recursive else "*"

        for file_path in root.glob(pattern):
            if not file_path.is_file():
                continue
            ext = file_path.suffix.lstrip(".").lower()
            if ext in self.extension_map:
                entry = self.extension_map[ext]
                discovered.append({
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "file_type": ext,
                    "display_name": entry.get("display_name", ext),
                    "parser_class": entry.get("parser_class", ""),
                })

        return discovered

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_extensions(
        self,
        discovered: List[Dict[str, Any]],
        expected_types: Set[str],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Split *discovered* items into ``(valid, unknown)`` based on whether
        their ``file_type`` is a member of *expected_types*.

        Args:
            discovered: List of file info dicts (as returned by ``scan()``).
            expected_types: Set of lower-case extensions considered valid.

        Returns:
            ``(valid_files, unknown_files)`` tuple.
        """
        valid: List[Dict[str, Any]] = []
        unknown: List[Dict[str, Any]] = []

        for item in discovered:
            ext = item.get("file_type", "")
            if ext in expected_types:
                valid.append(item)
            else:
                unknown.append(item)

        return valid, unknown
