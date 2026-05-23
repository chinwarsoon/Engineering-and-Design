"""
Standalone test for the live-timer spinner.
Run from the workflow directory:  python3 test_spinner_timer.py
"""

import sys
import threading
import time

# ── minimal stubs so progress.py can be imported without the full stack ──
import types
from pathlib import Path

_ce = types.ModuleType("core_engine")
_log = types.ModuleType("core_engine.logging")
_log.DEBUG_LEVEL = 1
sys.modules.setdefault("core_engine", _ce)
sys.modules.setdefault("core_engine.logging", _log)

sys.path.insert(0, str(Path(__file__).parent))

from utility_engine.console.progress import create_progress_spinner  # noqa: E402

# ── test ────────────────────────────────────────────────────────────────────
print("=" * 55)
print("Live-timer spinner test  (should tick every second)")
print("=" * 55)

DURATION = 5  # seconds to simulate a slow operation

print(f"\nSimulating a {DURATION}s operation…")
with create_progress_spinner("   Schema validation") as spinner:
    time.sleep(DURATION)
    spinner.update(1)

print("\n✓ Spinner closed cleanly.")
print("If the timer ticked (00:01 … 00:05) the fix is working.")
