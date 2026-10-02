"""engine/capability.py — dependency probe (R12 mitigation).

`probe_all()` reports the availability of every required package. If any required
package is missing the overall status is **FATAL**, which the dashboard turns into a
red banner (wired in backend/routes/system.py, later phase). No silent failure
(AGENTS.md §5.9): a missing dependency is reported, never swallowed.

Run as a script: `python -m engine.capability` -> prints JSON, exits 1 on FATAL.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass, field
from typing import List, Optional

# Required packages for the current phase. Add entries here as phases introduce
# hard dependencies. Keep in sync with requirements.txt and web_tracer.yml.
# Phase 1 adds the FastAPI service stack (T09/T21) as required.
REQUIRED_PACKAGES = ["networkx", "jsonschema", "fastapi", "uvicorn", "httpx"]

# Optional packages (Phase 3 + later). A missing entry here is WARN, never FATAL, but it
# must still be reported so the user knows a channel degrades (e.g. OTLP protobuf -> http/json,
# T29) instead of failing silently (AGENTS.md §5.9 / workplan §8.4 rule 4).
OPTIONAL_PACKAGES = ["protobuf", "opentelemetry", "opentelemetry-sdk"]


@dataclass
class PackageStatus:
    name: str
    available: bool
    version: Optional[str] = None


@dataclass
class ProbeResult:
    packages: List[PackageStatus] = field(default_factory=list)
    status: str = "OK"  # "OK" | "FATAL"

    @property
    def fatal(self) -> bool:
        return self.status == "FATAL"


def _check(name: str) -> PackageStatus:
    spec = importlib.util.find_spec(name)
    if spec is None:
        return PackageStatus(name=name, available=False, version=None)
    version = None
    try:
        # Preferred: avoids the jsonschema.__version__ DeprecationWarning.
        from importlib.metadata import version as meta_version

        version = meta_version(name)
    except Exception:
        try:
            mod = importlib.import_module(name)
            version = getattr(mod, "__version__", None)
        except Exception:  # pragma: no cover - import side effects are rare
            version = None
    return PackageStatus(name=name, available=True, version=version)


def probe_all(packages: Optional[List[str]] = None) -> ProbeResult:
    """Probe the given (or default required) packages; return a ProbeResult.

    The overall status is FATAL if any probed package is unavailable.
    """
    names = list(packages if packages is not None else REQUIRED_PACKAGES)
    result = ProbeResult()
    for name in names:
        status = _check(name)
        result.packages.append(status)
        if not status.available:
            result.status = "FATAL"
    return result


def capabilities() -> list[dict]:
    """Return the canonical capability list for ``GET /api/capabilities`` (workplan §9).

    Each entry is ``{name, available, version, level, message}`` with
    ``level ∈ OK | WARN | FATAL`` (AGENTS.md §5.9 / workplan §8.4). A missing required
    package is FATAL; a missing optional one is WARN. No silent failure.
    """
    required = probe_all()
    optional = probe_all(OPTIONAL_PACKAGES)
    out: list[dict] = []
    for pkg in list(required.packages) + list(optional.packages):
        if pkg.available:
            level, message = "OK", "available"
        elif pkg.name in REQUIRED_PACKAGES:
            level, message = "FATAL", "Required dependency missing"
        else:
            level, message = "WARN", "Optional dependency missing (channel may downgrade)"
        out.append(
            {
                "name": pkg.name,
                "available": pkg.available,
                "version": pkg.version,
                "level": level,
                "message": message,
            }
        )
    return out


def main() -> int:
    result = probe_all()
    payload = {
        "status": result.status,
        "packages": [
            {"name": p.name, "available": p.available, "version": p.version}
            for p in result.packages
        ],
    }
    print(json.dumps(payload, indent=2))
    return 1 if result.fatal else 0


if __name__ == "__main__":
    raise SystemExit(main())
