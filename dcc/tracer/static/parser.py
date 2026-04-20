"""
parser.py — AST extractor for the static analysis module.
Parses every .py file collected by crawler.py and extracts structured
metadata: functions, arguments, call edges, and logic metrics.

Public API:
    ModuleParser(record)  -> parse() -> ModuleInfo
    parse_file(path)      -> ModuleInfo
    parse_all(records)    -> list[ModuleInfo]
"""

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

from .crawler import FileRecord
from .metrics import logic_summary

log = logging.getLogger(__name__)

# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class ArgInfo:
    """Metadata for a single function argument."""
    name: str
    annotation: Optional[str] = None   # type hint as string, if present
    default: Optional[str] = None      # default value as string, if present
    kind: str = "positional"           # positional | keyword | vararg | kwarg


@dataclass
class FunctionInfo:
    """Extracted metadata for one function or method."""
    name: str
    qualified_name: str          # module::class.method or module::function
    module: str                  # dot-separated module name
    file_path: str
    start_line: int
    end_line: int
    is_method: bool = False
    class_name: Optional[str] = None
    is_async: bool = False
    args: List[ArgInfo] = field(default_factory=list)
    raw_calls: List[str] = field(default_factory=list)   # unresolved callee names
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    # Logic metrics (populated by metrics.logic_summary)
    cyclomatic_complexity: int = 1
    try_except_count: int = 0
    loop_count: int = 0
    if_count: int = 0
    for_count: int = 0
    while_count: int = 0
    try_count: int = 0


@dataclass
class ModuleInfo:
    """Extracted metadata for one .py file."""
    module_name: str
    file_path: str
    rel_path: str
    package: str
    lines: int
    functions: List[FunctionInfo] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)   # imported module names
    parse_error: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _annotation_str(node: Optional[ast.expr]) -> Optional[str]:
    """Convert an annotation AST node to a readable string.

    Breadcrumb: uses ast.unparse (Python 3.9+) for clean output.
    """
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _default_str(node: Optional[ast.expr]) -> Optional[str]:
    """Convert a default-value AST node to a readable string."""
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _extract_args(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[ArgInfo]:
    """Extract argument metadata from a function definition node.

    Breadcrumb: handles positional, keyword-only, *args, **kwargs, and defaults.

    Args:
        func_node: ast.FunctionDef or ast.AsyncFunctionDef.

    Returns:
        List of ArgInfo in declaration order.
    """
    args_obj = func_node.args
    result: List[ArgInfo] = []

    # Positional args — align defaults from the right
    pos_args = args_obj.args
    n_defaults = len(args_obj.defaults)
    n_pos = len(pos_args)
    default_offset = n_pos - n_defaults

    for i, arg in enumerate(pos_args):
        default_idx = i - default_offset
        default = _default_str(args_obj.defaults[default_idx]) if default_idx >= 0 else None
        result.append(ArgInfo(
            name=arg.arg,
            annotation=_annotation_str(arg.annotation),
            default=default,
            kind="positional",
        ))

    # *args
    if args_obj.vararg:
        result.append(ArgInfo(
            name=args_obj.vararg.arg,
            annotation=_annotation_str(args_obj.vararg.annotation),
            kind="vararg",
        ))

    # keyword-only args
    for i, arg in enumerate(args_obj.kwonlyargs):
        default = _default_str(args_obj.kw_defaults[i]) if i < len(args_obj.kw_defaults) else None
        result.append(ArgInfo(
            name=arg.arg,
            annotation=_annotation_str(arg.annotation),
            default=default,
            kind="keyword",
        ))

    # **kwargs
    if args_obj.kwarg:
        result.append(ArgInfo(
            name=args_obj.kwarg.arg,
            annotation=_annotation_str(args_obj.kwarg.annotation),
            kind="kwarg",
        ))

    return result


def _extract_calls(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[str]:
    """Extract raw callee names from all ast.Call nodes inside a function.

    Breadcrumb: resolves simple names (foo), attribute calls (obj.method),
    and chained calls (a.b.c). Returns deduplicated list.

    Args:
        func_node: ast.FunctionDef or ast.AsyncFunctionDef.

    Returns:
        Deduplicated list of callee name strings.
    """
    calls: List[str] = []
    for node in ast.walk(func_node):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            calls.append(func.id)
        elif isinstance(func, ast.Attribute):
            # Build dotted name: a.b.c
            parts = []
            cur = func
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            calls.append(".".join(reversed(parts)))
    # Deduplicate while preserving order
    seen: set = set()
    unique: List[str] = []
    for c in calls:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def _extract_imports(tree: ast.Module) -> List[str]:
    """Extract imported module names from a module AST.

    Breadcrumb: handles both 'import X' and 'from X import Y' forms.

    Args:
        tree: ast.Module node.

    Returns:
        List of imported module name strings.
    """
    imports: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def _decorator_names(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[str]:
    """Return decorator names as strings."""
    names: List[str] = []
    for dec in func_node.decorator_list:
        try:
            names.append(ast.unparse(dec))
        except Exception:
            names.append("<decorator>")
    return names


# ── Main parser class ─────────────────────────────────────────────────────────

class ModuleParser:
    """Parses a single .py file and extracts structured metadata.

    Args:
        record: FileRecord from the crawler.

    Usage::

        info = ModuleParser(record).parse()
    """

    def __init__(self, record: FileRecord):
        # Breadcrumb: store record for path/module_name access throughout
        self.record = record

    def parse(self) -> ModuleInfo:
        """Parse the file and return a ModuleInfo.

        Breadcrumb: reads source → ast.parse → walk classes and functions.
        On SyntaxError, returns ModuleInfo with parse_error set.

        Returns:
            ModuleInfo with all extracted metadata.
        """
        info = ModuleInfo(
            module_name=self.record.module_name,
            file_path=str(self.record.path),
            rel_path=self.record.rel_path,
            package=self.record.package,
            lines=self.record.lines,
        )

        try:
            source = self.record.path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(self.record.path))
        except SyntaxError as exc:
            info.parse_error = f"SyntaxError at line {exc.lineno}: {exc.msg}"
            log.warning("[parser] %s — %s", self.record.rel_path, info.parse_error)
            return info
        except Exception as exc:
            info.parse_error = str(exc)
            log.warning("[parser] %s — %s", self.record.rel_path, info.parse_error)
            return info

        info.imports = _extract_imports(tree)
        info.functions = self._extract_functions(tree)
        return info

    def _extract_functions(self, tree: ast.Module) -> List[FunctionInfo]:
        """Walk the module AST and extract FunctionInfo for every function/method.

        Breadcrumb: handles top-level functions and methods inside classes.
        Nested functions (closures) are included with their enclosing context.

        Args:
            tree: Parsed ast.Module.

        Returns:
            List of FunctionInfo.
        """
        functions: List[FunctionInfo] = []
        module = self.record.module_name

        # Walk top-level nodes
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(self._build_func_info(node, module, class_name=None))
            elif isinstance(node, ast.ClassDef):
                for item in ast.iter_child_nodes(node):
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions.append(self._build_func_info(item, module, class_name=node.name))

        return functions

    def _build_func_info(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        module: str,
        class_name: Optional[str],
    ) -> FunctionInfo:
        """Build a FunctionInfo from a function AST node.

        Breadcrumb: calls _extract_args, _extract_calls, logic_summary, _decorator_names.

        Args:
            node: Function AST node.
            module: Dot-separated module name.
            class_name: Enclosing class name, or None.

        Returns:
            Populated FunctionInfo.
        """
        qualified = f"{module}::{class_name}.{node.name}" if class_name else f"{module}::{node.name}"
        metrics = logic_summary(node)

        return FunctionInfo(
            name=node.name,
            qualified_name=qualified,
            module=module,
            file_path=str(self.record.path),
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            is_method=class_name is not None,
            class_name=class_name,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            args=_extract_args(node),
            raw_calls=_extract_calls(node),
            docstring=ast.get_docstring(node),
            decorators=_decorator_names(node),
            **metrics,
        )


# ── Convenience functions ─────────────────────────────────────────────────────

def parse_file(path: str | Path) -> ModuleInfo:
    """Parse a single .py file by path (no FileRecord needed).

    Breadcrumb: builds a minimal FileRecord then delegates to ModuleParser.

    Args:
        path: Absolute or relative path to a .py file.

    Returns:
        ModuleInfo.
    """
    from .crawler import FileRecord, _count_lines
    p = Path(path).resolve()
    record = FileRecord(
        path=p,
        rel_path=str(p.name),
        module_name=p.stem,
        package=p.stem,
        size_bytes=p.stat().st_size if p.exists() else 0,
        lines=_count_lines(p),
    )
    return ModuleParser(record).parse()


def parse_all(records: list) -> List[ModuleInfo]:
    """Parse all FileRecords and return a list of ModuleInfo.

    Breadcrumb: iterates records, calls ModuleParser.parse() for each.

    Args:
        records: List of FileRecord from crawler.crawl().

    Returns:
        List of ModuleInfo (one per file).
    """
    return [ModuleParser(r).parse() for r in records]
