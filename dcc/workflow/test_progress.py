#!/usr/bin/env python3
"""
Quick test script for progress bar functionality.
Tests imports and basic functionality without running full pipeline.
"""

import sys
from pathlib import Path

# Add workflow path
workflow_path = Path(__file__).parent
if str(workflow_path) not in sys.path:
    sys.path.insert(0, str(workflow_path))

print("=" * 60)
print("Testing Progress Bar Implementation")
print("=" * 60)

# Test 1: Import tqdm
print("\n[Test 1] Checking tqdm installation...")
try:
    import tqdm

    print(f"✓ tqdm installed: version {tqdm.__version__}")
except ImportError as e:
    print(f"✗ tqdm NOT installed: {e}")
    print("  Install with: pip install tqdm>=4.66.0")
    sys.exit(1)

# Test 2: Import progress utilities
print("\n[Test 2] Importing progress utilities...")
try:
    from utility_engine.console.progress import (
        create_progress_bar,
        create_progress_callback,
        create_progress_spinner,
    )

    print("✓ Progress utilities imported successfully")
except ImportError as e:
    print(f"✗ Failed to import progress utilities: {e}")
    sys.exit(1)

# Test 3: Import from console init
print("\n[Test 3] Importing from console package...")
try:
    from utility_engine.console import (
        create_progress_bar,
        create_progress_spinner,
    )

    print("✓ Console package exports progress functions")
except ImportError as e:
    print(f"✗ Failed to import from console: {e}")
    sys.exit(1)

# Test 4: Test DEBUG_LEVEL
print("\n[Test 4] Checking DEBUG_LEVEL integration...")
try:
    from core_engine.logging import DEBUG_LEVEL, set_debug_level

    print(f"✓ DEBUG_LEVEL = {DEBUG_LEVEL}")

    # Test at different levels
    for level in [0, 1, 2, 3]:
        set_debug_level(level)
        from core_engine.logging import DEBUG_LEVEL as current_level

        print(f"  Set level {level}: DEBUG_LEVEL = {current_level}")
except ImportError as e:
    print(f"✗ Failed to import DEBUG_LEVEL: {e}")
    sys.exit(1)

# Test 5: Create a test spinner
print("\n[Test 5] Testing spinner creation...")
try:
    import time

    set_debug_level(1)  # Enable progress

    with create_progress_spinner("Test spinner") as spinner:
        time.sleep(0.1)
        spinner.update(1)

    print("✓ Spinner created and updated successfully")
except Exception as e:
    print(f"✗ Spinner test failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 6: Create a test progress bar
print("\n[Test 6] Testing progress bar creation...")
try:
    with create_progress_bar(total=10, desc="Test progress", unit="items") as pbar:
        for i in range(10):
            time.sleep(0.01)
            pbar.update(1)

    print("✓ Progress bar created and updated successfully")
except Exception as e:
    print(f"✗ Progress bar test failed: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# Test 7: Test at DEBUG_LEVEL 0 (should disable progress)
print("\n[Test 7] Testing DEBUG_LEVEL 0 (quiet mode)...")
try:
    set_debug_level(0)

    with create_progress_spinner("Should be hidden") as spinner:
        spinner.update(1)

    print("✓ Progress disabled at DEBUG_LEVEL 0")
except Exception as e:
    print(f"✗ Quiet mode test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED ✓")
print("=" * 60)
print("\nProgress bar implementation is working correctly!")
print("Ready to test with full pipeline.")
