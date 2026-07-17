"""EKS main launcher — backward-compatible shim for eks/serve.py.

The canonical AGENTS.md §18.12 launcher implementation lives in
``eks/serve.py``. This file is retained for backward compatibility
(existing references, tests, and workplan docs) and simply delegates to it.

Revision: 0.3
Date: 2026-07-11
Author: opencode
Summary: T1.99.5 — add eks/serve.py per AGENTS.md §18.12; keep server.py as a
thin launcher/proxy shim.
"""
import sys
from pathlib import Path

# Make the repo root importable so `eks.serve` resolves when run as a script
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from eks.serve import (  # noqa: F401  (re-export public API for backward compat)
    ReusableTCPServer,
    MainServerHandler,
    start_phase1_backend,
    find_free_port,
    main,
    ROOT,
    COMMON,
)

if __name__ == "__main__":
    main()
