"""
Field-Level Change Detector — common.library.utility.change_detector.

Compares two flat dictionaries and reports every field whose value differs.
Used by registry update routines (e.g. ``update_document_status``) to produce
auditable diffs before committing changes.

Revision: 0.1
Date: 2026-07-19
Author: CodeBuddy
Summary: Extracted from eks issue I184 — diff logging on update_document_status()
         (T1.99.149 — I187).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Set

__all__ = ["FieldDiff", "detect_changes"]


@dataclass
class FieldDiff:
    """A single field-level change between two rows or states."""

    field: str
    """Name of the changed field."""

    old_value: Any
    """Previous value (may be ``None``)."""

    new_value: Any
    """New value."""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dict for JSON output."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FieldDiff":
        """Reconstruct from a plain dict."""
        return cls(**data)


def detect_changes(
    old_dict: Dict[str, Any],
    new_dict: Dict[str, Any],
    track_fields: Optional[Set[str]] = None,
) -> List[FieldDiff]:
    """
    Compare *old_dict* and *new_dict* and return a diff for every field
    whose value has changed.

    Args:
        old_dict: Previous state (typically a DB row as a dict).
        new_dict: Proposed new values keyed by column name.
        track_fields: If provided, only these fields are compared.
                      If ``None``, all keys present in either dict are compared.

    Returns:
        A list of ``FieldDiff`` objects, one per changed field. An empty
        list means no changes were detected.

    Example::

        >>> detect_changes({"a": 1, "b": "x"}, {"a": 2, "b": "x"})
        [FieldDiff(field="a", old_value=1, new_value=2)]
    """
    diffs: List[FieldDiff] = []

    keys_to_check: Set[str]
    if track_fields is not None:
        keys_to_check = track_fields
    else:
        keys_to_check = set(old_dict.keys()) | set(new_dict.keys())

    for key in sorted(keys_to_check):
        old_val = old_dict.get(key)
        new_val = new_dict.get(key)

        # Normalize for comparison — treat "same" values as no-change
        if _values_equal(old_val, new_val):
            continue

        diffs.append(FieldDiff(field=key, old_value=old_val, new_value=new_val))

    return diffs


def _values_equal(a: Any, b: Any) -> bool:
    """Return True if two values are semantically equivalent."""
    # Fast path — identity / simple equality
    if a is b:
        return True
    if a == b:
        return True
    # Normalize None vs empty string (common in DB column defaults)
    if a is None and b == "":
        return True
    if b is None and a == "":
        return True
    # Float comparison with a small epsilon
    if isinstance(a, float) and isinstance(b, float):
        return abs(a - b) < 1e-9
    return False
