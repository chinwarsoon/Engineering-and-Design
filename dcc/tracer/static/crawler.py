"""
crawler.py — Directory walker for the static analysis module.
Recursively collects .py files from a root path, respecting agent_rule.md
Section 3 exclusions (backup, dot-folders, test folders, archive).

Public API:
    crawl(root)          -> list[FileRecord]
    FileCrawler(root)    -> iterable of FileRecord
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

# ── agent_rule.md §3 exclusion patterns ──────────────────────────────────────
_SKIP_DIRS: set = {
    "__pycache__", ".git", ".github", ".venv", "venv", "env",
    "node_modules", "archive", "backup", "backups", ".idx", ".qwen",
    ".continue",
}
_SKIP_DIR_PREFIXES: tuple = ("test", ".")


@dataclass
class FileRecord:
    """Metadata for a single discovered .py file."""
    path: Path                  # absolute path
    rel_path: str               # path relative to crawl root
    module_name: str            # dot-separated module name
    package: str                # top-level package name
    size_bytes: int = 0
    lines: int = 0


def _should_skip_dir(name: str) -> bool:
    """Return True if a directory should be excluded from crawling.

    Breadcrumb: agent_rule.md §3 — ignore backup, dot, test, archive folders.
    """
    if name in _SKIP_DIRS:
        return True
    for prefix in _SKIP_DIR_PREFIXES:
        if name.startswith(prefix):
            return True
    return False


def _count_lines(path: Path) -> int:
    """Count non-empty lines in a file; return 0 on read error."""
    try:
        return sum(1 for ln in path.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip())
    except OSError:
        return 0


def _to_module_name(rel_path: str) -> str:
    """Convert a relative file path to a dot-separated module name.

    Breadcrumb: strips .py suffix, replaces os.sep with '.'.
    """
    return rel_path.replace(os.sep, ".").replace("/", ".").removesuffix(".py")


class FileCrawler:
    """Recursively discovers .py files under *root*, skipping excluded dirs.

    Args:
        root: Root directory to crawl (str or Path).

    Usage::

        for record in FileCrawler("/path/to/project"):
            print(record.module_name)
    """

    def __init__(self, root: str | Path):
        # Breadcrumb: resolve to absolute path for consistent comparisons
        self.root = Path(root).resolve()

    def crawl(self) -> List[FileRecord]:
        """Walk the directory tree and return a list of FileRecord objects.

        Breadcrumb: uses os.walk with topdown=True so we can prune dirs in-place.
        Returns:
            Sorted list of FileRecord (by rel_path).
        """
        records: List[FileRecord] = []

        for dirpath, dirnames, filenames in os.walk(self.root, topdown=True):
            # Prune excluded directories in-place (modifies os.walk iteration)
            dirnames[:] = [d for d in dirnames if not _should_skip_dir(d)]

            for fname in filenames:
                if not fname.endswith(".py"):
                    continue

                abs_path = Path(dirpath) / fname
                rel = abs_path.relative_to(self.root)
                rel_str = str(rel)

                # Derive package from first path component
                parts = rel.parts
                package = parts[0].removesuffix(".py") if parts else ""

                record = FileRecord(
                    path=abs_path,
                    rel_path=rel_str,
                    module_name=_to_module_name(rel_str),
                    package=package,
                    size_bytes=abs_path.stat().st_size,
                    lines=_count_lines(abs_path),
                )
                records.append(record)

        records.sort(key=lambda r: r.rel_path)
        return records

    def __iter__(self):
        return iter(self.crawl())


def crawl(root: str | Path) -> List[FileRecord]:
    """Convenience wrapper: crawl *root* and return FileRecord list.

    Args:
        root: Root directory path.

    Returns:
        List of FileRecord sorted by relative path.
    """
    return FileCrawler(root).crawl()
