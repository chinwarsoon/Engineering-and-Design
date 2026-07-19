"""
Synthetic Key Generator — common.library.utility.synthetic_key.

Generates stable, deterministic "UNRESOLVED-{hash}" keys for files whose
document_number cannot be parsed from the filename. The same file path always
yields the same key, enabling cross-run stability.

Revision: 0.1
Date: 2026-07-19
Author: CodeBuddy
Summary: Extracted from duplicate ad-hoc patterns at eks/engine/core/file_scanner.py L178
         and eks/engine/core/registry.py L280 (T1.99.148 — I187).
"""

from __future__ import annotations

import hashlib

__all__ = ["generate_synthetic_key", "SYNTHETIC_KEY_PREFIX"]

SYNTHETIC_KEY_PREFIX = "UNRESOLVED"


def generate_synthetic_key(
    identifier: str,
    algorithm: str = "md5",
    prefix: str = SYNTHETIC_KEY_PREFIX,
) -> str:
    """
    Generate a stable, deterministic synthetic document key.

    Args:
        identifier: A stable string (typically the absolute file path) used to
                    generate the hash portion of the key.
        algorithm: Hash algorithm name (default "md5").
        prefix: Key prefix (default "UNRESOLVED").

    Returns:
        A string of the form ``"{prefix}-{hash_truncated}"``, e.g.
        ``"UNRESOLVED-a1b2c3d4"``.

    Examples::

        >>> generate_synthetic_key("/data/doc.pdf")
        'UNRESOLVED-a1b2c3d4'
        >>> generate_synthetic_key("/data/doc.pdf", prefix="FALLBACK")
        'FALLBACK-a1b2c3d4'
    """
    digest = hashlib.new(algorithm, identifier.encode()).hexdigest()
    return f"{prefix}-{digest[:8]}"
