# Workplan: Fix Launch Assets and Reorganize Project

## Goal
Resolve 404 errors for CSS assets in `launch.py` and reorganize the dashboard serving logic to align with user preferences (moving `serve.py` to root and consolidating HTML in `ui/`).

## Context
- `launch.py` is the standalone entry point.
- `serve.py` is the dashboard file server.
- Assets are currently split between `engine/` and `ui/`, causing pathing issues.

## Proposed Changes
1. **Move `engine/serve.py`** to the project root `code_tracer/`.
2. **Move `engine/static_dashboard.html`** to `code_tracer/ui/`.
3. **Update `serve.py`** to serve from the root directory so it can resolve the `ui/` folder.
4. **Update `launch.py`** to find the relocated `serve.py`.

## Success Criteria
- Running `launch.py` starts the dashboard without 404 errors for `ui/dcc-design-system.css`.
- The dashboard is accessible at `http://localhost:5000`.
- All HTML files are consolidated in the `ui/` folder.

## Timeline
- [Phase 1]: Logging and Infrastructure (Reorganization)
- [Phase 2]: Code Updates (Path Fixes)
- [Phase 3]: Verification
