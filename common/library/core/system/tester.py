"""
Universal environment tester (L20).

Extracted from DCC's ``dcc/workflow/core_engine/system/system_environment.py``
and made project-agnostic — accepts a ``dependencies`` dict rather than reading
``project_setup.json`` directly.

Stdlib-only — uses only ``importlib``, ``platform``, ``json``, ``sys``,
``pathlib`` — so it can run before any heavy project imports are attempted.

Revision: 0.2
Date: 2026-07-17
Author: opencode
Summary: 0.2 — Added PIP_TO_IMPORT mapping so pip distribution names like
         ``python-docx``, ``qdrant-client``, ``pymupdf`` are translated to
         their actual importable module names (``docx``, ``qdrant_client``,
         ``fitz``) before calling ``importlib.import_module()``.
         Original: 0.1 — T1.99.75 — Universal test_environment() extracted from DCC for L20.
"""
from __future__ import annotations

import importlib
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Mapping from pip distribution name → importable module name.
# Only entries that differ need to be listed here.
# ---------------------------------------------------------------------------
_PIP_TO_IMPORT: Dict[str, str] = {
    "python-docx": "docx",
    "qdrant-client": "qdrant_client",
    "pymupdf": "fitz",
    "pillow": "PIL",
    "scikit-learn": "sklearn",
    "beautifulsoup4": "bs4",
    "python-dateutil": "dateutil",
    "python-multipart": "multipart",
    "rank-bm25": "rank_bm25",
    "sentence-transformers": "sentence_transformers",
    "psycopg2-binary": "psycopg2",
}


def _resolve_import_name(pip_name: str) -> str:
    """Return the importable module name for a given pip distribution name.

    Falls back to the pip name itself (with hyphens replaced by underscores)
    when no explicit mapping is found.

    Args:
        pip_name: The pip distribution name (e.g. ``"python-docx"``).

    Returns:
        The importable module name (e.g. ``"docx"``).
    """
    return _PIP_TO_IMPORT.get(pip_name, pip_name.replace("-", "_"))


def test_environment(
    dependencies: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Test environment and required/optional/engine libraries.

    Runs ``importlib.import_module()`` on each entry in the provided
    ``dependencies`` dict, one at a time.  Failures are logged in the
    returned results dict but do **not** abort the loop — all entries
    are checked so the caller sees the full picture in one pass.

    Args:
        dependencies: A dict with optional keys:
            ``required``: List[str] of required package names.
            ``optional``: List[str] of optional package names.
            ``engines``:   List[Dict] with ``module`` (str) and ``members``
                           (List[str]) — each member is verified via
                           ``getattr()``.

    Returns:
        dict with keys:
            ``python_version``:    str — ``platform.python_version()``
            ``platform``:          str — ``platform.system()``
            ``required_modules``:  Dict[str, str] — module → "ok" or "error: ..."
            ``optional_modules``:  Dict[str, str] — module → "ok" or "warning: ..."
            ``engine_modules``:    Dict[str, str] — module → "ok" or "warning: ..."
            ``errors``:            List[str] — error messages (required only)
            ``ready``:             bool — False if any required module failed
    """
    deps = dependencies or {}

    required_modules: List[str] = deps.get("required", [])
    optional_modules: List[str] = deps.get("optional", [])
    engine_modules: List[Tuple[str, List[str]]] = [
        (e["module"], e.get("members", e.get("attributes", [])))
        if isinstance(e, dict)
        else (e, [])
        for e in deps.get("engines", [])
    ]

    results: Dict[str, Any] = {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "required_modules": {},
        "optional_modules": {},
        "engine_modules": {},
        "errors": [],
        "ready": True,
    }

    # ---- required modules ----
    for pip_name in required_modules:
        import_name = _resolve_import_name(pip_name)
        try:
            importlib.import_module(import_name)
            results["required_modules"][pip_name] = "ok"
        except Exception as exc:
            results["required_modules"][pip_name] = f"error: {exc}"
            results["errors"].append(f"{pip_name}: {exc}")

    # ---- optional modules ----
    for pip_name in optional_modules:
        import_name = _resolve_import_name(pip_name)
        try:
            importlib.import_module(import_name)
            results["optional_modules"][pip_name] = "ok"
        except Exception as exc:
            results["optional_modules"][pip_name] = f"warning: {exc}"

    # ---- engine modules (with attribute verification) ----
    for pip_name, attributes in engine_modules:
        import_name = _resolve_import_name(pip_name)
        try:
            mod = importlib.import_module(import_name)
            for attr in attributes:
                getattr(mod, attr)
            results["engine_modules"][pip_name] = "ok"
        except Exception as exc:
            results["engine_modules"][pip_name] = f"warning: {exc}"

    results["ready"] = not results["errors"]
    return results
