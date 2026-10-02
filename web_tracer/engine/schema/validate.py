"""engine/schema/validate.py — validators + proposal compatibility shim (workplan §8.3).

Single place that knows the JSON Schemas. Adapters, the backend, the CI contract
checker (T06) and the clean-environment script (T08) all import from here.

``compat_load`` implements the workplan §8.3.1 compatibility note: the original
proposal placed ``class`` / ``method`` at the top level; we move them into
``source.class_name`` and ``name`` so legacy examples validate unchanged.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
from jsonschema.exceptions import ValidationError

_SCHEMA_DIR = Path(__file__).resolve().parent

_SPAN_SCHEMA = json.loads((_SCHEMA_DIR / "span_schema.json").read_text(encoding="utf-8"))
_TREE_SCHEMA = json.loads((_SCHEMA_DIR / "execution_tree_schema.json").read_text(encoding="utf-8"))
_GRAPH_SCHEMA = json.loads((_SCHEMA_DIR / "unified_graph_schema.json").read_text(encoding="utf-8"))

_SPAN_VALIDATOR = jsonschema.Draft202012Validator(_SPAN_SCHEMA)
_TREE_VALIDATOR = jsonschema.Draft202012Validator(_TREE_SCHEMA)
_GRAPH_VALIDATOR = jsonschema.Draft202012Validator(_GRAPH_SCHEMA)


def compat_load(obj: dict) -> dict:
    """Normalise a legacy proposal span (top-level ``class``/``method``) to v1.0.

    Moves ``class`` -> ``source.class_name`` and ``method`` -> ``name``. No-op for
    already-compliant spans. Mutates and returns ``obj``.
    """
    if "class" in obj:
        obj.setdefault("source", {})
        if isinstance(obj["source"], dict) and "class_name" not in obj["source"]:
            obj["source"]["class_name"] = obj.pop("class")
        else:
            obj.pop("class", None)
    if "method" in obj:
        if "name" not in obj:
            obj["name"] = obj.pop("method")
        else:
            obj.pop("method", None)
    return obj


def validate_span(obj: dict, compat: bool = True) -> None:
    if compat:
        compat_load(obj)
    _SPAN_VALIDATOR.validate(obj)


def validate_execution_tree(obj: dict) -> None:
    _TREE_VALIDATOR.validate(obj)


def validate_unified_graph(obj: dict) -> None:
    _GRAPH_VALIDATOR.validate(obj)


def validate_path(path: str | Path) -> str:
    """Validate a JSON file, dispatching by shape. Returns the detected kind."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        for span in data:
            validate_span(span)
        return "span[]"
    if "root" in data and "stats" in data:
        validate_execution_tree(data)
        return "execution_tree"
    if "nodes" in data and "edges" in data:
        validate_unified_graph(data)
        return "unified_graph"
    if "trace_id" in data and "span_id" in data:
        validate_span(data)
        return "span"
    raise ValidationError(f"Cannot classify schema kind for {path}")


def main(argv: list[str] | None = None) -> int:
    files = argv if argv is not None else sys.argv[1:]
    if not files:
        print("usage: python -m engine.schema.validate FILE [FILE ...]", file=sys.stderr)
        return 2
    rc = 0
    for f in files:
        try:
            kind = validate_path(f)
            print(f"OK   {f}  [{kind}]")
        except (ValidationError, ValueError) as e:
            msg = e.message if isinstance(e, ValidationError) else str(e)
            print(f"FAIL {f}: {msg}", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
