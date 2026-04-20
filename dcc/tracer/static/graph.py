"""
graph.py — Call-dependency graph builder for the static analysis module.
Builds a networkx.DiGraph where nodes are qualified function names and
edges represent caller → callee relationships resolved across all modules.

Public API:
    CallGraph(modules)
        .build()                -> self
        .to_json()              -> dict  (nodes + edges for UI)
        .get_entry_points()     -> list[str]
        .get_complexity_hotspots(threshold) -> list[dict]
        .save_json(path)        -> Path
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import networkx as nx
    _NX_AVAILABLE = True
except ImportError:
    _NX_AVAILABLE = False
    nx = None  # type: ignore

from .parser import ModuleInfo, FunctionInfo

log = logging.getLogger(__name__)


class CallGraph:
    """Builds and queries a directed call-dependency graph.

    Nodes  : qualified function names  (module::ClassName.method or module::func)
    Edges  : caller → callee  (resolved from raw_calls across all modules)

    Args:
        modules: List of ModuleInfo produced by parse_all().

    Usage::

        cg = CallGraph(modules).build()
        print(cg.get_entry_points())
        cg.save_json("tracer/output/call_graph.json")
    """

    def __init__(self, modules: List[ModuleInfo]):
        # Breadcrumb: store modules and build lookup tables on init
        self.modules = modules
        self._func_map: Dict[str, FunctionInfo] = {}   # qualified_name -> FunctionInfo
        self._name_index: Dict[str, List[str]] = {}    # short_name -> [qualified_names]
        self.graph = nx.DiGraph() if _NX_AVAILABLE else None
        self._built = False

    # ── Build ─────────────────────────────────────────────────────────────────

    def build(self) -> "CallGraph":
        """Populate the graph from all parsed modules.

        Breadcrumb:
          1. Index all functions by qualified name and short name.
          2. Add nodes with attribute metadata.
          3. Resolve raw_calls to qualified names and add edges.

        Returns:
            self (for chaining).
        """
        self._build_index()
        self._add_nodes()
        self._add_edges()
        self._built = True
        log.info("[graph] Built: %d nodes, %d edges",
                 self.node_count, self.edge_count)
        return self

    def _build_index(self) -> None:
        """Index all FunctionInfo by qualified name and short name.

        Breadcrumb: short name index allows resolving 'foo' → 'module::foo'.
        """
        for mod in self.modules:
            for fn in mod.functions:
                self._func_map[fn.qualified_name] = fn
                # Index by bare function name for resolution
                short = fn.name
                self._name_index.setdefault(short, []).append(fn.qualified_name)
                # Also index by class.method for method calls
                if fn.class_name:
                    dotted = f"{fn.class_name}.{fn.name}"
                    self._name_index.setdefault(dotted, []).append(fn.qualified_name)

    def _add_nodes(self) -> None:
        """Add one node per function with complexity metadata."""
        if not _NX_AVAILABLE:
            return
        for qname, fn in self._func_map.items():
            self.graph.add_node(qname, **{
                "name": fn.name,
                "module": fn.module,
                "file": fn.file_path,
                "start_line": fn.start_line,
                "end_line": fn.end_line,
                "is_method": fn.is_method,
                "class_name": fn.class_name or "",
                "is_async": fn.is_async,
                "cyclomatic_complexity": fn.cyclomatic_complexity,
                "try_except_count": fn.try_except_count,
                "loop_count": fn.loop_count,
                "arg_count": len(fn.args),
            })

    def _add_edges(self) -> None:
        """Resolve raw_calls to qualified names and add directed edges.

        Breadcrumb: resolution order:
          1. Exact qualified match (module::func).
          2. Short-name index lookup (prefer same-module match).
          3. Unresolved calls are skipped (no phantom nodes).
        """
        if not _NX_AVAILABLE:
            return
        for qname, fn in self._func_map.items():
            for raw_call in fn.raw_calls:
                target = self._resolve_call(raw_call, fn.module)
                if target and target != qname:
                    self.graph.add_edge(qname, target)

    # Generic names that are too ambiguous to resolve as meaningful edges
    _SKIP_CALLS = {
        "get", "set", "add", "pop", "append", "extend", "update", "remove",
        "sort", "sorted", "items", "keys", "values", "copy", "clear",
        "join", "split", "strip", "format", "encode", "decode",
        "read", "write", "open", "close", "flush",
        "print", "len", "range", "enumerate", "zip", "map", "filter",
        "str", "int", "float", "bool", "list", "dict", "tuple",
        "isinstance", "hasattr", "getattr", "setattr", "super",
        "info", "debug", "warning", "error", "critical",
        "__init__", "__str__", "__repr__",
    }

    def _resolve_call(self, raw: str, caller_module: str) -> Optional[str]:
        """Resolve a raw call string to a qualified function name.

        Breadcrumb: skips generic built-in names, tries exact match,
        then same-module preference, then any match.

        Args:
            raw: Raw call string from AST (e.g. 'foo', 'obj.method', 'mod.func').
            caller_module: Module of the calling function (for same-module preference).

        Returns:
            Qualified name string, or None if unresolvable.
        """
        # Skip generic names that produce noisy/wrong edges
        short = raw.split(".")[-1]
        if short in self._SKIP_CALLS:
            return None

        # 1. Exact qualified match
        if raw in self._func_map:
            return raw

        # 2. Short-name index — prefer same-module
        candidates = self._name_index.get(raw, [])
        if not candidates:
            candidates = self._name_index.get(short, [])

        if not candidates:
            return None

        # Prefer same-module candidate
        for c in candidates:
            if c.startswith(caller_module + "::"):
                return c

        # Fall back to first candidate
        return candidates[0]

    # ── Queries ───────────────────────────────────────────────────────────────

    @property
    def node_count(self) -> int:
        """Number of nodes in the graph."""
        return self.graph.number_of_nodes() if _NX_AVAILABLE else len(self._func_map)

    @property
    def edge_count(self) -> int:
        """Number of edges in the graph."""
        return self.graph.number_of_edges() if _NX_AVAILABLE else 0

    def get_entry_points(self) -> List[str]:
        """Return qualified names of functions with no callers (in-degree 0).

        Breadcrumb: entry points are roots of the call tree — likely main() or
        top-level pipeline functions.

        Returns:
            Sorted list of qualified names.
        """
        if not _NX_AVAILABLE or not self._built:
            return []
        return sorted(n for n, d in self.graph.in_degree() if d == 0)

    def get_complexity_hotspots(self, threshold: int = 10) -> List[Dict[str, Any]]:
        """Return functions whose cyclomatic complexity exceeds *threshold*.

        Breadcrumb: sorted descending by complexity for heatmap display.

        Args:
            threshold: Minimum complexity to include (default 10).

        Returns:
            List of dicts with keys: qualified_name, name, module, complexity, file, line.
        """
        hotspots = []
        for qname, fn in self._func_map.items():
            if fn.cyclomatic_complexity >= threshold:
                hotspots.append({
                    "qualified_name": qname,
                    "name": fn.name,
                    "module": fn.module,
                    "complexity": fn.cyclomatic_complexity,
                    "file": fn.file_path,
                    "start_line": fn.start_line,
                })
        return sorted(hotspots, key=lambda x: x["complexity"], reverse=True)

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_json(self) -> Dict[str, Any]:
        """Serialise the graph to a JSON-compatible dict.

        Breadcrumb: nodes carry all metadata; edges carry source/target.
        Format is compatible with the static_dashboard.html UI.

        Returns:
            Dict with keys: nodes (list), edges (list), stats (dict).
        """
        nodes = []
        for qname, fn in self._func_map.items():
            nodes.append({
                "id": qname,
                "label": fn.name,
                "module": fn.module,
                "file": fn.file_path,
                "start_line": fn.start_line,
                "end_line": fn.end_line,
                "is_method": fn.is_method,
                "class_name": fn.class_name or "",
                "is_async": fn.is_async,
                "cyclomatic_complexity": fn.cyclomatic_complexity,
                "try_except_count": fn.try_except_count,
                "loop_count": fn.loop_count,
                "arg_count": len(fn.args),
                "args": [{"name": a.name, "annotation": a.annotation,
                           "default": a.default, "kind": a.kind}
                          for a in fn.args],
                "raw_calls": fn.raw_calls,
                "docstring": fn.docstring or "",
                "decorators": fn.decorators,
            })

        edges = []
        if _NX_AVAILABLE and self._built:
            for src, tgt in self.graph.edges():
                edges.append({"source": src, "target": tgt})

        entry_points = self.get_entry_points()
        hotspots = self.get_complexity_hotspots(threshold=5)

        return {
            "nodes": nodes,
            "edges": edges,
            "entry_points": entry_points,
            "hotspots": hotspots,
            "stats": {
                "total_functions": len(nodes),
                "total_edges": len(edges),
                "entry_point_count": len(entry_points),
                "hotspot_count": len(hotspots),
                "modules_analyzed": len(self.modules),
            },
        }

    def save_json(self, path: str | Path) -> Path:
        """Write the graph JSON to *path*.

        Breadcrumb: creates parent directories if needed; writes UTF-8 JSON.

        Args:
            path: Output file path.

        Returns:
            Resolved Path of the written file.
        """
        out = Path(path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(self.to_json(), indent=2, default=str), encoding="utf-8")
        log.info("[graph] Saved JSON → %s", out)
        return out
