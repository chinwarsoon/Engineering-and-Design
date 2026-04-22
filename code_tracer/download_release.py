"""
download_release.py — PyCode Tracer distribution packager.

Packages all files required for static tracing into a versioned zip archive
under the workspace releases/ folder. Version is auto-incremented based on
existing releases (e.g. pycode-tracer-v1.0.0.zip → pycode-tracer-v1.0.1.zip).

Usage:
    python code_tracer/download_release.py
    python code_tracer/download_release.py --bump minor
    python code_tracer/download_release.py --bump major
"""

import argparse
import re
import sys
import zipfile
from pathlib import Path

# CSS is always sourced from ui/ — single source of truth
CSS_SRC = Path(__file__).resolve().parent / "ui" / "dcc-design-system.css"
CSS_DEST = "ui/dcc-design-system.css"

# Files required for static tracing, relative to code_tracer root
MANIFEST = [
    "USER_GUIDE.md",
    "ui/static_dashboard.html",
    "engine/backend/__init__.py",
    "engine/backend/server.py",
    "engine/static/__init__.py",
    "engine/static/crawler.py",
    "engine/static/graph.py",
    "engine/static/metrics.py",
    "engine/static/parser.py",
    "engine/static/visualizer.py",
    "engine/launch.py",
    "serve.py",
    "engine/pyproject.toml",
    "engine/__init__.py",
]

REQUIREMENTS = "fastapi>=0.100\nuvicorn>=0.23\nnetworkx>=3.0\n"
RELEASES_DIR = Path(__file__).resolve().parent.parent / "releases"
VERSION_RE = re.compile(r"(pycode|dcc)-tracer-v(\d+)\.(\d+)\.(\d+)\.zip")


def _latest_version():
    """Return (major, minor, patch) of the highest existing release, or (1, 0, 0)."""
    versions = []
    if RELEASES_DIR.exists():
        for f in RELEASES_DIR.glob("*-tracer-v*.zip"):
            m = VERSION_RE.match(f.name)
            if m:
                # Groups: 0=prefix, 1=major, 2=minor, 3=patch
                versions.append(tuple(int(x) for x in m.groups()[1:]))
    return max(versions) if versions else (1, 0, 0)


def _next_version(bump):
    major, minor, patch = _latest_version()
    if bump == "major":
        return major + 1, 0, 0
    elif bump == "minor":
        return major, minor + 1, 0
    else:  # patch
        # If no releases exist yet, use 1.0.0 as the first release
        if not any(RELEASES_DIR.glob("pycode-tracer-v*.zip") if RELEASES_DIR.exists() else []):
            return 1, 0, 0
        return major, minor, patch + 1


def main():
    parser = argparse.ArgumentParser(
        description="Package PyCode Tracer files into a versioned zip in releases/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python code_tracer/download_release.py              # patch bump (or v1.0.0 if first)
  python code_tracer/download_release.py --bump minor
  python code_tracer/download_release.py --bump major
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
    out_path = RELEASES_DIR / f"pycode-tracer-v{version}.zip"

    packed, skipped = [], []
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # CSS always from ui/ — single source of truth
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
            # In the zip, engine files go to root (for backwards compatibility)
            if rel.startswith("engine/"):
                zip_path = rel[7:]  # Strip "engine/" prefix in zip
            else:
                zip_path = rel
            zf.write(src, zip_path)
            packed.append(zip_path)
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
        f"**File:** [`pycode-tracer-v{version}.zip`](pycode-tracer-v{version}.zip)\n"
        f"**Type:** {'Major release' if args.bump == 'major' else 'Minor release' if args.bump == 'minor' else 'Patch release'}\n"
        f"**Packaged from:** `code_tracer/`\n\n"
        f"{len(packed)} file(s) packed, {len(skipped)} skipped.\n\n"
        "### Changes\n\n"
        "_Update this section with a summary of changes in this release._\n\n"
        "### Log References\n\n"
        "| Log | Entry |\n"
        "|-----|-------|\n"
        "| `code_tracer/Log/update_log.md` | _link to relevant entry_ |\n"
        "| `code_tracer/Log/test_log.md` | _link to relevant entry_ |\n\n"
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
