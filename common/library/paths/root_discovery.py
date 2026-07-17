"""
L17 — Pipeline Entry-Point & Cross-Platform Discovery.

Implements the universal ordered entry sequence
(common/universal_pipeline_architecture_design.md §3.19):

    1. detect_os()                         [L12]  — know the platform first
    2. pipeline_dir constant               — folder holding the running module
    3. resolve_pipeline_base_path()        [cwd / --base-path] — operator start
    4. == pipeline_dir strip               — step up if launched inside it
    5. project_root                        — anchor-verified parent of the project
    6. resolve_paths()                     [L16]  — schema-driven canonical paths
    7. OS-gated auto-create                — should_auto_create_folders(os_info)
    8. safe_posix() / platform overrides   — emit cross-platform path strings

Faithful to DCC's maintainable anchor discovery:
    - dcc/workflow/core_engine/paths/path_resolvers.py:9-45   (cwd / --base-path)
    - dcc/workflow/core_engine/paths/path_core.py:78-93       (anchor walk, raises)
    - dcc/workflow/dcc_engine_pipeline.py:483-484             (== pipeline_dir strip)

Key contract differences vs the legacy EKS resolver (I098):
    * cwd / --base-path is the PRIMARY (operator-controlled) start, not a silent
      fallback.
    * the ``__file__`` anchor walk is a LAST-RESORT fallback that RAISES
      ``FileNotFoundError`` when the anchor cannot be located (no silent
      ``Path.cwd()`` default) — I098 #6 / T1.99.23.

Two distinct folder concepts are modelled explicitly so nested projects
(EKS: module in ``eks/engine``, project marked by ``eks/``) work as well as
flat projects (DCC: module in ``workflow/``, project marked by ``workflow/``):
    * ``pipeline_dir`` — the folder that holds the running pipeline module
      (the ``== pipeline_dir`` strip target).
    * ``anchor``       — the folder that marks the project root; the returned
      project root is the *parent* of ``anchor``.

Revision: 1.0
Date: 2026-07-15
Author: opencode
Summary: T1.99.17–23 — universal entry-point discovery (I098 / L17).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from common.library.core.paths.path_utils import detect_os


# NOTE (I102 / T1.99.32): the shared library must not bake in any project's
# folder convention. ``pipeline_dir`` is a required, caller-supplied constant
# (EKS passes "engine", DCC passes "workflow"); there is intentionally NO
# module-level default here.


def default_base_path(
    pipeline_root_dir: str,
    reference: Optional[Path] = None,
) -> Path:
    """Walk *reference* parents for *anchor*; return the parent of *anchor*.

    Last-resort anchor discovery, faithful to DCC ``default_base_path``
    (dcc/workflow/core_engine/paths/path_core.py:78-93). Raises
    ``FileNotFoundError`` if *anchor* is not found anywhere in the directory
    tree — there is NO silent ``Path.cwd()`` fallback (I098 #6 / T1.99.23).

    Args:
        pipeline_root_dir: Folder name that marks the project location (EKS ``"eks"``,
            DCC ``"workflow"``). The returned project root is its parent.
        reference: File to start the parent walk from. Defaults to this
            module's ``__file__``. Callers MUST pass the pipeline entry
            module's ``__file__`` so the walk finds the correct anchor
            (this shared module lives under ``common/``, not the project).

    Returns:
        The project root (parent directory of *anchor*).
    """
    start = Path(reference).resolve() if reference is not None else Path(__file__).resolve()
    for parent in start.parents:
        if parent.name == pipeline_root_dir:
            return parent.parent
    raise FileNotFoundError(
        f"Anchor folder '{pipeline_root_dir}' not found in directory tree above {start}. "
        f"Run from within the project, or pass --base-path explicitly (I098)."
    )


def resolve_pipeline_base_path(
    pipeline_dir: Optional[str] = None,
    base_path: Optional[str] = None,
) -> Path:
    """Resolve the pipeline start position (operator-controlled), DCC-faithful.

    Priority (L17 §3.19 steps 3-4):
        1. ``base_path`` (from ``--base-path``) if provided.
        2. Otherwise the current working directory (``Path.cwd()``).
    If the resolved start folder *is* ``pipeline_dir`` (e.g. launched from
    inside ``engine/``), step up to its parent
    (DCC ``dcc_engine_pipeline.py:483-484``).

    This function does NOT walk ``__file__`` — anchor discovery is the job of
    :func:`default_base_path` / :func:`discover_project_root` (T1.99.23).

    Args:
        pipeline_dir: Module folder used for the ``== pipeline_dir`` strip.
        base_path: Explicit ``--base-path`` override (operator-chosen).

    Returns:
        Resolved pipeline start path (not yet verified to contain the anchor).
    """
    if base_path:
        start = Path(base_path).expanduser().resolve()
    else:
        start = Path.cwd()
    if pipeline_dir is not None and start.name == pipeline_dir:
        start = start.parent
    return start


def discover_project_root(
    pipeline_root_dir: str,
    pipeline_dir: Optional[str] = None,
    base_path: Optional[str] = None,
    reference: Optional[Path] = None,
) -> Path:
    """Run the full L17 entry sequence and return the verified project root.

    Order:
        1. detect_os()                                  [L12]
        2. pipeline_dir constant                        (caller-supplied; no project default)
        3. resolve_pipeline_base_path()                 [cwd / --base-path]
        4. == pipeline_dir strip
        5. verify the anchor lives under the start; if so, the start IS the
           project root (parent of ``anchor``).
        6. otherwise fall back to ``default_base_path(anchor, reference)`` which
           raises ``FileNotFoundError`` when the anchor is truly missing.

    Args:
        pipeline_root_dir: Project anchor folder name (EKS ``"eks"``, DCC ``"workflow"``).
        pipeline_dir: Folder holding the running module (strip target).
        base_path: Explicit ``--base-path`` override (operator-chosen).
        reference: Entry module ``__file__`` for the anchor-walk fallback.

    Returns:
        Verified project root (Path).
    """
    detect_os()  # step 1 — L12: know the platform before any path work
    start = resolve_pipeline_base_path(pipeline_dir, base_path)  # steps 3-4
    if (start / pipeline_root_dir).is_dir():
        return start
    # Anchor not under the operator-chosen start -> last-resort walk (raises
    # FileNotFoundError when the anchor is genuinely missing).
    return default_base_path(pipeline_root_dir, reference)
