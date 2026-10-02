"""backend/routes/system.py — Phase 1 system endpoints (workplan §9 rows 1-5, T21).

Every path constant is imported from ``engine.config`` (single source, workplan §8.5
hard contract rule). Later phases add browser/java/correlation route modules and
register them in ``backend/web_server.py``.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from engine import capability, config, paths

router = APIRouter()

# The single front end lives at <project>/ui/ (workplan §7.2). Served by this service so
# the one-command entry point (launch.py) actually opens a usable dashboard (T10/T39).
_UI_DIR = Path(__file__).resolve().parent.parent.parent / "ui"
_DASHBOARD_FILE = "static_dashboard.html"


class TargetSetReq(BaseModel):
    path: str


class FileReadReq(BaseModel):
    path: str
    start: int | None = None
    end: int | None = None


@router.get(config.HEALTH)
def health() -> dict:
    return {"status": "ok", "version": config.PROJECT_VERSION, "schema_version": "1.0"}


@router.get(config.DASHBOARD)
def dashboard():
    """Serve the single-page dashboard (T10 shell, T39 execution tree tab)."""
    page = _UI_DIR / _DASHBOARD_FILE
    if not page.exists():
        raise HTTPException(status_code=404, detail=f"dashboard not found at {page}")
    return FileResponse(page)


@router.get(config.UI_ASSETS + "/{filename}")
def ui_asset(filename: str):
    """Serve a dashboard asset (``/ui/web-tracer.css``, ``/ui/code-tracer.css``).

    The name is taken as a bare filename only, so a traversal such as
    ``/ui/../../etc/passwd`` cannot escape the ``ui/`` folder.
    """
    safe = Path(filename).name
    asset = _UI_DIR / safe
    if not asset.exists() or not asset.is_file():
        raise HTTPException(status_code=404, detail=f"asset not found: {safe}")
    return FileResponse(asset)


@router.get(config.CAPABILITIES)
def capabilities() -> list[dict]:
    # capability.capabilities() returns the canonical {name, available, version, level, message} list.
    return capability.capabilities()


@router.get(config.TARGET)
def get_target() -> dict:
    return {"base": str(paths.resolve_base()), "source": paths.target_source()}


@router.post(config.TARGET_SET)
def set_target(req: TargetSetReq) -> dict:
    base = paths.write_target(req.path)
    return {"base": str(base)}


@router.post(config.FILE_READ)
def file_read(req: FileReadReq) -> dict:
    try:
        full = paths.assert_within_base(req.path)  # raises PathEscapeError if out of bounds
    except paths.PathEscapeError as e:
        raise HTTPException(status_code=403, detail=str(e))
    if not full.exists():
        raise HTTPException(status_code=404, detail="File not found")
    text = full.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if req.start is not None or req.end is not None:
        start = (req.start or 1) - 1
        end = req.end or len(lines)
        lines = lines[start:end]
    return {"content": "\n".join(lines)}
