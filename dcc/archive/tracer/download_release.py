"""
download_release.py — DCC Tracer distribution packager.

Packages all files required for static tracing into a versioned zip archive
under the workspace releases/ folder. Version is auto-incremented based on
existing releases (e.g. dcc-tracer-v1.0.0.zip → dcc-tracer-v1.0.1.zip).

Usage:
    python dcc/tracer/download_release.py
    python dcc/tracer/download_release.py --bump minor
    python dcc/tracer/download_release.py --bump major
"""

import argparse
import re
import sys
import zipfile
from pathlib import Path

# CSS is always sourced from dcc/ui/ — single source of truth
CSS_SRC = Path(__file__).resolve().parents[1] / "ui" / "dcc-design-system.css"
CSS_DEST = "ui/dcc-design-system.css"

# Files required for static tracing, relative to this script's directory
MANIFEST = [
    "USER_GUIDE.md",
    "static_dashboard.html",
    "backend/__init__.py",
    "backend/server.py",
    "static/__init__.py",
    "static/crawler.py",
    "static/graph.py",
    "static/metrics.py",
    "static/parser.py",
    "static/visualizer.py",
    "launch.py",
    "serve.py",
    "pyproject.toml",
    "MANIFEST.in",
    "__init__.py",
]

REQUIREMENTS = "fastapi>=0.100\nuvicorn>=0.23\nnetworkx>=3.0\n"
RELEASES_DIR = Path(__file__).resolve().parents[2] / "releases"
VERSION_RE = re.compile(r"dcc-tracer-v(\d+)\.(\d+)\.(\d+)\.zip")


def _latest_version():
    """Return (major, minor, patch) of the highest existing release, or (1, 0, 0)."""
    versions = []
    if RELEASES_DIR.exists():
        for f in RELEASES_DIR.glob("dcc-tracer-v*.zip"):
            m = VERSION_RE.match(f.name)
            if m:
                versions.append(tuple(int(x) for x in m.groups()))
    return max(versions) if versions else (1, 0, 0)


def _next_version(bump):
    major, minor, patch = _latest_version()
    if bump == "major":
        return major + 1, 0, 0
    elif bump == "minor":
        return major, minor + 1, 0
    else:  # patch
        # If no releases exist yet, use 1.0.0 as the first release
        if not any(RELEASES_DIR.glob("dcc-tracer-v*.zip") if RELEASES_DIR.exists() else []):
            return 1, 0, 0
        return major, minor, patch + 1


def main():
    parser = argparse.ArgumentParser(
        description="Package DCC Tracer files into a versioned zip in releases/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dcc/tracer/download_release.py              # patch bump (or v1.0.0 if first)
  python dcc/tracer/download_release.py --bump minor
  python dcc/tracer/download_release.py --bump major
        """,
    )
    parser.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Version segment to increment (default: patch)",
    )
    args = parser.parse_args()

    major, minor, patch = _next_version(args.bump)
    version = f"{major}.{minor}.{patch}"
    src_root = Path(__file__).parent.resolve()
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RELEASES_DIR / f"dcc-tracer-v{version}.zip"

    packed, skipped = [], []
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # CSS always from dcc/ui/ — single source of truth
        if CSS_SRC.exists():
            zf.write(CSS_SRC, CSS_DEST)
            packed.append(CSS_DEST)
        else:
            skipped.append(CSS_DEST)
        for rel in MANIFEST:
            src = src_root / rel
            if not src.exists():
                skipped.append(rel)
                continue
            zf.write(src, rel)
            packed.append(rel)
        zf.writestr("requirements.txt", REQUIREMENTS)

    print(f"\nRelease v{version} created: {out_path}")
    print(f"  {len(packed)} file(s) packed, {len(skipped)} skipped")
    if skipped:
        print("  Skipped (not found):")
        for f in skipped:
            print(f"    - {f}")

    # Append entry to RELEASE_HISTORY.md
    history_path = RELEASES_DIR / "RELEASE_HISTORY.md"
    from datetime import date
    entry = (
        f"## v{version} — {date.today()}\n\n"
        f"**File:** [`dcc-tracer-v{version}.zip`](dcc-tracer-v{version}.zip)\n"
        f"**Type:** {'Major release' if args.bump == 'major' else 'Minor release' if args.bump == 'minor' else 'Patch release'}\n"
        f"**Packaged from:** `dcc/tracer/`\n\n"
        f"{len(packed)} file(s) packed, {len(skipped)} skipped.\n\n"
        "### Changes\n\n"
        "_Update this section with a summary of changes in this release._\n\n"
        "### Log References\n\n"
        "| Log | Entry |\n"
        "|-----|-------|\n"
        "| `dcc/Log/update_log.md` | _link to relevant entry_ |\n"
        "| `dcc/Log/test_log.md` | _link to relevant entry_ |\n\n"
        "---\n"
    )
    if history_path.exists():
        history_path.write_text(
            history_path.read_text(encoding="utf-8") + "\n" + entry,
            encoding="utf-8",
        )

    print("\nNext steps:")
    print("  1. Download the zip from Codespaces to your Windows machine")
    print(f"  2. Extract to C:\\Users\\<user>\\dcc\\tools")
    print("  3. pip install -r requirements.txt")
    print("  4. python launch.py C:\\path\\to\\your\\project")


if __name__ == "__main__":
    main()
