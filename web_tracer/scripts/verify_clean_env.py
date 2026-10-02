"""scripts/verify_clean_env.py — clean-environment acceptance (workplan T08).

Verifies the project runs end to end in a clean environment:
  * required dependencies import,
  * a fresh empty target folder resolves via engine.paths,
  * the backend app imports and /health responds,
  * the contract check is consistent.

Exits non-zero if any required dependency is missing (acceptance: missing
dependency -> non-zero). With ``--fresh`` it builds a throwaway venv, installs
``requirements.txt``, and runs the same checks inside it.

Usage: python scripts/verify_clean_env.py [--fresh]
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _checks() -> list[str]:
    """Return a list of error strings (empty == pass)."""
    import os

    from engine import capability, paths

    errors: list[str] = []

    # 1. required deps present
    res = capability.probe_all()
    for pkg in res.packages:
        if not pkg.available:
            errors.append(f"missing dependency: {pkg.name}")

    # 2. fresh empty target folder + path resolution
    tmp = tempfile.mkdtemp(prefix="wt_clean_")
    try:
        base = paths.write_target(tmp)
        assert str(base) == tmp, f"write_target base mismatch: {base} != {tmp}"
        assert paths.resolve_base() == Path(tmp), "resolve_base did not pick .target"
        within = paths.assert_within_base("x.txt")
        assert within.is_relative_to(Path(tmp)), "within-base check failed"

        # 3. backend imports + /health
        from backend.web_server import app
        from fastapi.testclient import TestClient

        c = TestClient(app)
        r = c.get("/health")
        assert r.status_code == 200 and r.json().get("status") == "ok", f"/health -> {r.status_code}"

        # 4. contract consistency (T06)
        import check_contracts

        if check_contracts.main() != 0:
            errors.append("contract check failed")
    finally:
        paths._TARGET_FILE.write_text("")  # reset marker (gitignored runtime state)
        shutil.rmtree(tmp, ignore_errors=True)
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--fresh",
        action="store_true",
        help="build a throwaway venv, install requirements.txt, and run checks inside it",
    )
    args = ap.parse_args()

    if args.fresh:
        venv = Path(tempfile.mkdtemp(prefix="wt_venv_")) / "venv"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        pip = venv / "bin" / "pip"
        subprocess.run([str(pip), "install", "-r", str(ROOT / "requirements.txt")], check=True)
        py = venv / "bin" / "python"
        # run the same checks (no --fresh) inside the fresh venv
        r = subprocess.run([str(py), str(Path(__file__))], capture_output=True, text=True)
        print(r.stdout)
        print(r.stderr, file=sys.stderr)
        return r.returncode

    errors = _checks()
    if errors:
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("CLEAN-ENV CHECK FAILED", file=sys.stderr)
        return 2
    print("CLEAN-ENV CHECK OK: deps present, empty target resolves, backend + contract consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
