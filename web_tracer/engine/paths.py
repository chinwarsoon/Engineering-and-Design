"""engine/paths.py — single path-resolution point for web_tracer.

All target-root resolution and path-safety checks go through this module
(AGENTS.md §5.16: no hardcoded fallback duplicates; one SSOT). Ported from
``code_tracer/engine/backend/server.py::_resolve_base`` but split into a dedicated
module so T02+ never recomputes the base and never inlines a ``.parent`` chain.

Priority (highest first), see workplan §8.4 / line 833:
  1. ``output/.target`` file (path written by launch.py / CLI when a target is chosen)
  2. ``TRACER_TARGET`` environment variable
  3. current working directory
"""
from __future__ import annotations

import os
from pathlib import Path

# Marker file location relative to the web_tracer project root.
_TARGET_FILE = Path(__file__).resolve().parent.parent / "output" / ".target"


class PathEscapeError(Exception):
    """Raised when a resolved path would escape the configured target base.

    Surfaces the offending path so callers/logging can report it (AGENTS.md §19:
    the id lives in ``engine.config.ERROR_CODES["WT-PATH-001"]``). Never silent.
    """

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Resolved path '{path}' escapes the allowed target root.")


def resolve_base() -> Path:
    """Resolve the analysis target directory using the three-level priority.

    1. ``output/.target`` file if it exists and is non-empty (path on its first line)
    2. ``TRACER_TARGET`` environment variable if set
    3. current working directory
    """
    if _TARGET_FILE.exists():
        text = _TARGET_FILE.read_text(encoding="utf-8").strip()
        if text:
            return Path(text).resolve()
    env = os.environ.get("TRACER_TARGET")
    if env:
        return Path(env).resolve()
    return Path.cwd()


def target_source() -> str:
    """Return which priority level currently decides the base.

    One of ``"target_file"`` | ``"env"`` | ``"cwd"`` — used by the
    ``GET /api/target`` route so the UI can show where the base came from.
    """
    if _TARGET_FILE.exists() and _TARGET_FILE.read_text(encoding="utf-8").strip():
        return "target_file"
    if os.environ.get("TRACER_TARGET"):
        return "env"
    return "cwd"


def write_target(path: str | Path) -> Path:
    """Persist ``path`` to ``output/.target`` so later runs default to it.

    Returns the resolved base. Called by launch.py / CLI (T09); never at import.
    The file is git-ignored (runtime state), so it must not be committed.
    """
    resolved = Path(path).resolve()
    _TARGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    _TARGET_FILE.write_text(str(resolved) + "\n", encoding="utf-8")
    return resolved


def assert_within_base(p: str | Path) -> Path:
    """Resolve ``p`` against the base and guarantee it stays within the base.

    Absolute ``p`` is taken as-is (then checked); relative ``p`` is joined to the
    base. Raises :class:`PathEscapeError` if the result is not within
    :func:`resolve_base`.
    """
    base = resolve_base()
    candidate = Path(p)
    full = candidate if candidate.is_absolute() else base / candidate
    full = full.resolve()
    if not full.is_relative_to(base):
        raise PathEscapeError(str(full))
    return full


def runs_root() -> Path:
    """Return the per-recording workspace: ``<base>/output/runs`` (workplan §8.6).

    Single source for the recorder and correlation output — never inline this path
    (AGENTS.md §5.15). Created on first use so ``output/runs/.gitkeep`` stays tracked.
    """
    root = resolve_base() / "output" / "runs"
    root.mkdir(parents=True, exist_ok=True)
    return root


def run_dir(run_id: str) -> Path:
    """Return (and create) the directory for a single recording run ``<run_id>``."""
    d = runs_root() / run_id
    d.mkdir(parents=True, exist_ok=True)
    return d
