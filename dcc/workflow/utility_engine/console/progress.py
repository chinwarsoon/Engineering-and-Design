"""
Progress indicators for DCC pipeline operations.

Integrates tqdm progress bars with the pipeline's tiered logging system.
Progress indicators respect DEBUG_LEVEL:
- Level 0 (quiet): Disabled
- Level 1+ (normal/debug/trace): Enabled

Phase 2: Progress Bar Implementation (WP-PIPE-MSG-001-R2)
Created: 2026-05-23
Updated: 2026-05-23 - Live timer via background refresh thread
"""

import threading
from contextlib import contextmanager
from typing import Callable, Generator, Optional

from core_engine.logging import DEBUG_LEVEL
from tqdm import tqdm

# Refresh interval for the live timer (seconds)
_REFRESH_INTERVAL = 0.5


@contextmanager
def create_progress_spinner(
    desc: str = "Processing",
    disable: Optional[bool] = None,
    leave: bool = False,
    refresh_interval: float = _REFRESH_INTERVAL,
) -> Generator[tqdm, None, None]:
    """
    Create a live-timer spinner for indeterminate operations.

    Displays an incrementing elapsed-time counter (e.g. "Schema validation: 00:03")
    that ticks every second while the operation runs, giving users clear visual
    feedback that the pipeline is active.

    A background daemon thread calls spinner.refresh() at refresh_interval so the
    display updates continuously without any changes to calling code.

    Args:
        desc: Label shown before the timer (e.g. "   Schema validation")
        disable: Force disable (None = auto from DEBUG_LEVEL; level 0 = off)
        leave: Keep the final line after completion (default: False = erase)
        refresh_interval: Seconds between live refreshes (default: 0.5)

    Yields:
        tqdm spinner instance  (caller should call spinner.update(1) when done)

    Example:
        >>> with create_progress_spinner("   Schema validation") as spinner:
        ...     result = schema_validator.run()
        ...     spinner.update(1)
        # Live output while running:
        #    Schema validation: 00:01
        #    Schema validation: 00:02
        #    Schema validation: 00:03  (cleared on exit)

    Breadcrumb:
        - Called by: dcc_engine_pipeline._run_schema/mapper/export/ai
        - Called by: processor_engine.core.engine.apply_phased_processing
        - Refresh thread: daemon, stopped via threading.Event on context exit
        - Respects: DEBUG_LEVEL from core_engine.logging
    """
    if disable is None:
        disable = DEBUG_LEVEL < 1

    with tqdm(
        desc=desc,
        bar_format="{desc}: {elapsed}",
        disable=disable,
        leave=leave,
    ) as spinner:
        # Background thread: keep the timer ticking while work runs
        _stop = threading.Event()

        def _tick() -> None:
            while not _stop.wait(refresh_interval):
                spinner.refresh()

        _thread = threading.Thread(target=_tick, daemon=True)
        if not disable:
            _thread.start()

        try:
            yield spinner
        finally:
            _stop.set()
            if _thread.is_alive():
                _thread.join(timeout=refresh_interval * 2)


@contextmanager
def create_progress_bar(
    total: int,
    desc: str = "Processing",
    unit: str = "items",
    disable: Optional[bool] = None,
    leave: bool = False,
) -> Generator[tqdm, None, None]:
    """
    Create a progress bar for countable operations.

    Args:
        total: Total number of items to process
        desc: Description text shown before the bar
        unit: Unit label (e.g. "cols", "rows", "files")
        disable: Force disable (None = auto from DEBUG_LEVEL)
        leave: Keep the bar after completion (default: False)

    Yields:
        tqdm progress bar instance

    Example:
        >>> with create_progress_bar(total=45, desc="Mapping columns", unit="cols") as pbar:
        ...     for col in columns:
        ...         process_column(col)
        ...         pbar.update(1)
        Mapping columns: 100%|████████| 45/45 [00:05<00:00, 9.2cols/s]

    Breadcrumb:
        - Called by: dcc_engine_pipeline._run_mapper()
        - Respects: DEBUG_LEVEL from core_engine.logging
    """
    if disable is None:
        disable = DEBUG_LEVEL < 1

    with tqdm(
        total=total,
        desc=desc,
        unit=unit,
        disable=disable,
        leave=leave,
        ncols=80,
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
    ) as pbar:
        yield pbar


def create_progress_callback(
    pbar: tqdm,
    step_size: int = 1,
) -> Callable[..., None]:
    """
    Create a callback that advances a progress bar by step_size on each call.

    Args:
        pbar: tqdm instance to update
        step_size: Number of steps per callback invocation (default: 1)

    Returns:
        Zero-argument callable that calls pbar.update(step_size)

    Example:
        >>> with create_progress_bar(total=100) as pbar:
        ...     cb = create_progress_callback(pbar)
        ...     mapper.run(progress_callback=cb)

    Breadcrumb:
        - Called by: dcc_engine_pipeline._run_mapper()
        - Passed to: mapper_engine.core.engine.ColumnMapperEngine.run()
    """

    def callback(n: int = step_size) -> None:
        pbar.update(n)

    return callback


__all__ = [
    "create_progress_spinner",
    "create_progress_bar",
    "create_progress_callback",
]
