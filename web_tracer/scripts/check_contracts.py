"""scripts/check_contracts.py — CI contract checker (workplan §8.5, T06).

Asserts two invariants:
  1. Every FastAPI route path is declared in ``engine.config.ENDPOINTS`` (no drift).
  2. Every front-end ``fetch`` URL that targets the web_tracer API is served by a route.

Exits non-zero (and names the offending URL) on any violation, so injecting a
mismatched endpoint fails CI (acceptance: "injecting a mismatched endpoint fails
CI and names the URL").
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import re
from engine import config
from backend.web_server import app

# FastAPI's own documentation/auto routes are not part of our contract.
_BUILTIN = {"/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect", "*"}
# Front-end fetches that are NOT web_tracer API calls (legacy code_tracer dashboard
# endpoints, static assets, later-phase routes not yet implemented).
# /correlate and /execution_tree became real Phase 4 routes, so they are enforced now.
_IGNORE_PREFIXES = ("/static/", "/trace", "/unified", "/ws/")

# A contract/path may carry a path parameter, e.g. ``/browser/trace/{run_id}``.
# Normalise both sides to their parameter-free prefix before comparing.
_PARAM = re.compile(r"\{[^}]+\}")


def _prefix(path: str) -> str:
    """Strip ``{param}`` segments: ``/browser/trace/{run_id}`` -> ``/browser/trace``."""
    return _PARAM.sub("", path).rstrip("/")


def _iter_routes(app):
    """Yield leaf routes. FastAPI >=0.116 wraps included routers in an
    ``_IncludedRouter`` whose real routes live on ``.original_router``; recurse there."""
    for route in app.routes:
        if getattr(route, "methods", None):
            yield route
        elif hasattr(route, "original_router"):
            yield from _iter_routes(route.original_router)
        elif hasattr(route, "routes"):
            yield from _iter_routes(route)


def backend_routes() -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for route in _iter_routes(app):
        if getattr(route, "path", None) in _BUILTIN:
            continue
        for m in route.methods:
            if m in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                out.add((m, route.path))
    return out


def _matches_prefix(path: str, prefixes: set[str]) -> bool:
    """True if ``path`` is exactly a prefix or lives under one (concrete id form)."""
    if path in prefixes:
        return True
    return any(path == p or path.startswith(p + "/") for p in prefixes)


def frontend_fetch_paths() -> list[str]:
    urls: list[str] = []
    for html in (ROOT / "ui").glob("*.html"):
        text = html.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"""fetch\(\s*['"]([^'"]+)['"]""", text):
            urls.append(m.group(1))
    return urls


def main() -> int:
    errors: list[str] = []
    routes = backend_routes()
    route_paths = {p for _, p in routes}
    route_prefixes = {_prefix(p) for p in route_paths}
    contract_prefixes = {_prefix(p) for p in config.CONTRACT_PATHS}

    # 1. backend drift: a route whose parameter-free prefix is not in the contract
    for method, path in routes:
        if _prefix(path) not in contract_prefixes:
            errors.append(f"backend route {method} {path} is not in the contract (engine.config.ENDPOINTS)")

    # 2. contract completeness: every contract prefix is implemented by a route
    for path in config.CONTRACT_PATHS:
        if _prefix(path) not in route_prefixes:
            errors.append(f"contract endpoint {path} is not implemented by the backend")

    # 3. front-end fetch URLs ⊆ backend routes (for web_tracer API calls only)
    for url in frontend_fetch_paths():
        if url.startswith(_IGNORE_PREFIXES) or url.startswith("http") or url.startswith("//"):
            continue
        path = url.split("?", 1)[0].split("#", 1)[0]
        if path in ("", "/"):
            continue
        if not _matches_prefix(path, route_prefixes):
            errors.append(f"front end fetches '{url}' but the backend has no matching route")

    if errors:
        print("CONTRACT CHECK FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(
        f"CONTRACT OK: {len(routes)} backend route(s), "
        f"{len(config.CONTRACT_PATHS)} contract path(s); frontend fetches consistent."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
