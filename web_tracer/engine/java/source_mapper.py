"""engine/java/source_mapper.py — map method-level spans to a source file:line (T32, §8.4).

Goal: ≥ 80 % of method-level spans resolve to ``file:line`` (workplan Phase 3 M4).

Resolution priority (highest confidence first):
  1. Runtime evidence — the span carries ``code.filepath`` + ``code.lineno`` (highest, 1.0).
  2. Static index — a scanned project gives ``(class, method) -> (file, line)`` (0.9), or
     ``(class) -> (file, line)`` (0.6). tree-sitter cannot resolve ``@Autowired`` interface
     injection (R5), so we lean on runtime evidence and lower confidence when only the class
     matches (workplan §10.3 mitigation).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# class Foo { ... }
_CLASS_RE = re.compile(r"(?:public\s+|final\s+|abstract\s+|@\w+\s*)*class\s+(\w+)")

# <modifiers> <return-type> <name>(<params>) { | throws | ;
_METHOD_RE = re.compile(
    r"(?:public|private|protected|static|final|abstract|synchronized|native|@[\w.]+|\s)*"
    r"([\w<>\[\],\.\s]+?)\s+([A-Za-z_]\w*)\s*\(([^;]*)\)\s*(?:\{|throws|;)"
)
_CONTROL = {"if", "for", "while", "switch", "catch", "return", "new", "synchronized", "try", "else", "do"}


@dataclass
class SourceLocation:
    file_path: str
    start_line: int
    class_name: Optional[str] = None
    method: Optional[str] = None
    confidence: float = 1.0
    reason: Optional[str] = None


class SourceMapper:
    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = Path(project_path) if project_path else None
        self._index: dict[tuple[str, str], tuple[str, int]] = {}  # (class, method) -> (file, line)
        self._class_index: dict[str, tuple[str, int]] = {}  # class -> (file, line)
        if self.project_path:
            self.build_index(self.project_path)

    def build_index(self, project_path: Path) -> None:
        for f in Path(project_path).rglob("*.java"):
            self._index_file(f)

    def _index_file(self, f: Path) -> None:
        try:
            lines = f.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            return
        class_name: Optional[str] = None
        for i, line in enumerate(lines, start=1):
            cm = _CLASS_RE.search(line)
            if cm:
                class_name = cm.group(1)
                self._class_index[class_name] = (str(f), i)
            mm = _METHOD_RE.search(line)
            if mm and class_name:
                ret, name = mm.group(1).strip(), mm.group(2)
                if not ret or name in _CONTROL:
                    continue
                self._index.setdefault((class_name, name), (str(f), i))

    def map_span(self, span: dict) -> Optional[SourceLocation]:
        attrs = span.get("attributes", {}) or {}
        src = span.get("source", {}) or {}
        fp = attrs.get("code.filepath") or src.get("file")
        ln = attrs.get("code.lineno") or src.get("line")
        cls = attrs.get("code.namespace") or attrs.get("class.name") or src.get("class_name")
        fn = attrs.get("code.function") or attrs.get("method.name") or src.get("symbol")
        # 1) runtime evidence
        if fp and ln is not None:
            return SourceLocation(
                file_path=fp, start_line=int(ln), class_name=cls, method=fn,
                confidence=1.0, reason="runtime code.* attributes",
            )
        simple = cls.split(".")[-1] if cls else None
        # 2) static index: class + method
        if simple and fn:
            hit = self._index.get((simple, fn))
            if hit:
                return SourceLocation(
                    file_path=hit[0], start_line=hit[1], class_name=cls, method=fn,
                    confidence=0.9, reason="static index (class+method)",
                )
        # 3) static index: class only
        if simple:
            chit = self._class_index.get(simple)
            if chit:
                return SourceLocation(
                    file_path=chit[0], start_line=chit[1], class_name=cls, method=fn,
                    confidence=0.6, reason="static index (class only)",
                )
        return None

    def resolve_rate(self, spans: list[dict]) -> float:
        """Fraction of method-level spans (layer=java, event_type!=controller) that resolve."""
        method_spans = [
            s for s in spans if s.get("layer") == "java" and s.get("event_type") in ("method", "service", "repository")
        ]
        if not method_spans:
            return 1.0
        resolved = sum(1 for s in method_spans if self.map_span(s) is not None)
        return resolved / len(method_spans)
