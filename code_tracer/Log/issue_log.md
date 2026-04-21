# Code Tracer — Issue Log

## Instructions
1. Always log new issues immediately after identified.
2. Add a timestamp at the beginning of each log entry.
3. When resolved, update status and link to update_log.

---

# Section 2. Pending Issues

*(none)*

---

# Section 3. Closed Issues

*(none — see dcc/Log/issue_log.md for pre-migration history)*

## 2026-04-19 07:00:00

[Issue #CT-01]: `ModuleNotFoundError: No module named 'tracer'` when running `launch.py` after migration.
- `[Status]`: **Resolved**
- `[Root Cause]`: `launch.py` used `uvicorn tracer.backend.server:app` with `cwd=tracer_dir.parent`. After migration the package root is `engine/` itself, not a `tracer/` subfolder inside a parent.
- `[Resolution]`: Changed to `backend.server:app` with `cwd=tracer_dir`. Updated `server.py` `sys.path` to add `engine/` dir. Replaced all `from tracer.X import` with `from X import`.
- `[Link to update_log]`: [update_log.md](update_log.md)

## 2026-04-19 07:00:00

[Issue #CT-02]: `edges=0, entry_points=0` in call graph — `networkx` not installed.
- `[Status]`: **Resolved**
- `[Root Cause]`: `networkx` listed in `pyproject.toml` but not installed in active conda env. `_NX_AVAILABLE=False` caused `edge_count` to return 0.
- `[Resolution]`: `pip install networkx==3.6.1`. Added to `dcc/dcc.yml` and root `dcc.yml`.
- `[Link to update_log]`: [update_log.md](update_log.md)
