"""
Static analysis sub-package for the Universal Interactive Python Code Tracer.
Phase 1b: AST-based code analysis without execution.

Modules:
    crawler   - Directory walker, collects .py files
    parser    - AST extractor: functions, args, calls, logic
    metrics   - Cyclomatic complexity and logic counters
    graph     - networkx call-dependency graph builder
    visualizer - pyvis interactive HTML network generator
"""

from .crawler import FileCrawler, crawl
from .parser import ModuleParser, ModuleInfo, FunctionInfo
from .metrics import cyclomatic_complexity, count_try_except, count_loops
from .graph import CallGraph
from .visualizer import GraphVisualizer

__all__ = [
    "FileCrawler", "crawl",
    "ModuleParser", "ModuleInfo", "FunctionInfo",
    "cyclomatic_complexity", "count_try_except", "count_loops",
    "CallGraph",
    "GraphVisualizer",
]
