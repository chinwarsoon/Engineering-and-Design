"""engine/browser — browser runtime capture (workplan Phase 2, T22-T28, §8.4).

Every collector (Playwright, the CI MockBrowserAdapter, later CDP/BiDi) implements the
``BrowserTracer`` ABC in ``base.py`` so the recorder and backend routes stay adapter-agnostic.
"""
from engine.browser.base import (
    Action,
    BrowserTracer,
    RecordConfig,
    make_span,
    new_run_id,
)

__all__ = ["Action", "BrowserTracer", "RecordConfig", "make_span", "new_run_id"]
