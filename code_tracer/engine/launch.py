"""
launch.py — DCC Tracer standalone launcher.

Usage:
    python engine/launch.py /path/to/any/python/project
    python engine/launch.py /path/to/project --port 8000 --no-browser

Starts the FastAPI backend (which also serves the dashboard) on a single port,
then opens the dashboard in the default browser.
"""

import argparse
import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path


def _validate_target(target: str) -> Path:
    path = Path(target).resolve()
    if not path.exists():
        print(f"Error: Target directory does not exist: {path}")
        sys.exit(1)
    if not path.is_dir():
        print(f"Error: Target is not a directory: {path}")
        sys.exit(1)
    py_files = list(path.rglob("*.py"))
    if not py_files:
        print(f"Warning: No .py files found in {path}")
    else:
        print(f"Target: {path}  ({len(py_files)} Python files found)")
    return path


def _write_target_file(target: Path) -> None:
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / ".target").write_text(str(target), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="DCC Static Tracer — analyse any Python project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tracer/launch.py /path/to/project
  python tracer/launch.py /path/to/project --port 8000 --serve-port 5000
  python tracer/launch.py /path/to/project --no-browser
        """,
    )
    parser.add_argument("target", help="Path to the Python project to analyse")
    parser.add_argument("--port", type=int, default=8000, help="Port for backend + dashboard (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    target = _validate_target(args.target)
    _write_target_file(target)

    env = os.environ.copy()
    env["TRACER_TARGET"] = str(target)

    tracer_dir = Path(__file__).parent
    python = sys.executable

    print(f"\nStarting backend  → http://localhost:{args.port}")
    backend = subprocess.Popen(
        [python, "-m", "uvicorn", "backend.server:app",
         "--host", "0.0.0.0", "--port", str(args.port)],
        cwd=str(tracer_dir),
        env=env,
    )

    dashboard_url = f"http://localhost:{args.port}"
    print(f"\nDashboard ready at {dashboard_url}")
    print("Press Ctrl+C to stop.\n")

    if not args.no_browser:
        for _ in range(20):
            time.sleep(1)
            try:
                urllib.request.urlopen(f"http://localhost:{args.port}/health", timeout=2)
                break
            except Exception:
                pass
        webbrowser.open(dashboard_url)

    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
