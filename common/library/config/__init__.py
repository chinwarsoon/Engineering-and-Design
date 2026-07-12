"""Shared configuration helpers.

Revision: 0.1
Date: 2026-07-11
Author: Codex
Summary: Add universal system parameter normalization and lookup helpers.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


def normalize_system_parameters(config: Any) -> Dict[str, Any]:
    """Return system parameters as a flat key/value mapping.

    Parameters:
        config: Either a full config dict containing ``system_parameters``, a
            direct flat parameter dict, or an array of parameter-entry dicts.

    Returns:
        A normalized dictionary keyed by canonical parameter name.
    """
    if not config:
        return {}

    source = config.get("system_parameters", config) if isinstance(config, Mapping) else config

    if isinstance(source, Mapping):
        return {str(key): value for key, value in source.items()}

    if isinstance(source, list):
        normalized: Dict[str, Any] = {}
        for entry in source:
            if not isinstance(entry, Mapping):
                continue
            key = entry.get("key") or entry.get("name")
            if not key:
                continue
            if "value" in entry:
                value = entry["value"]
            elif "default_value" in entry:
                value = entry["default_value"]
            elif "default" in entry:
                value = entry["default"]
            else:
                continue
            normalized[str(key)] = value
        return normalized

    return {}


def get_system_param(config: Any, key: str, default: Any = None) -> Any:
    """Read one normalized system parameter.

    Parameters:
        config: Full config or direct system parameter payload.
        key: Canonical parameter key.
        default: Value returned when the parameter is absent.

    Returns:
        The configured value, or ``default`` when missing.
    """
    return normalize_system_parameters(config).get(key, default)


__all__ = ["get_system_param", "normalize_system_parameters"]
