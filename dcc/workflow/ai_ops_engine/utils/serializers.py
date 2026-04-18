"""
AI Ops Engine — Serializers

Normalize AI engine outputs to JSON-safe formats for UI and persistence.
Breadcrumb: AiInsight → dict → JSON string
"""

from __future__ import annotations
import json
import math
from typing import Any


def to_json_safe(obj: Any) -> Any:
    """
    Recursively convert an object to JSON-safe types.

    Handles: NaN/Inf floats, non-serializable objects.

    Args:
        obj: Any Python object

    Returns:
        JSON-serializable version
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: to_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_json_safe(v) for v in obj]
    return obj


def dumps_safe(obj: Any, **kwargs) -> str:
    """
    JSON-serialize with NaN/Inf safety.

    Args:
        obj: Object to serialize
        **kwargs: Passed to json.dumps

    Returns:
        JSON string
    """
    return json.dumps(to_json_safe(obj), **kwargs)
