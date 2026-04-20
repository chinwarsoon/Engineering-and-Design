"""
metrics.py — AST-based code complexity helpers for the static analysis module.
All functions accept an ast.FunctionDef (or ast.AsyncFunctionDef) node and
return integer counts.

Public API:
    cyclomatic_complexity(node) -> int
    count_try_except(node)      -> int
    count_loops(node)           -> int
    logic_summary(node)         -> dict
"""

import ast
from typing import Union

_FuncNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]


def cyclomatic_complexity(node: _FuncNode) -> int:
    """Compute McCabe cyclomatic complexity for a function node.

    Formula: CC = 1 + number of decision branches.
    Decision nodes counted: If, For, While, BoolOp (And/Or), ExceptHandler,
    comprehension ifs, conditional expressions (IfExp), Assert.

    Breadcrumb: walks the entire subtree of *node* using ast.walk.

    Args:
        node: ast.FunctionDef or ast.AsyncFunctionDef.

    Returns:
        Integer complexity score (minimum 1).
    """
    complexity = 1  # base path
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                               ast.ExceptHandler, ast.Assert, ast.IfExp)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            # Each additional operand in and/or adds a branch
            complexity += len(child.values) - 1
        elif isinstance(child, ast.comprehension):
            complexity += len(child.ifs)
    return complexity


def count_try_except(node: _FuncNode) -> int:
    """Count the number of except handlers inside a function.

    Breadcrumb: counts ast.ExceptHandler nodes (each except clause = 1).

    Args:
        node: ast.FunctionDef or ast.AsyncFunctionDef.

    Returns:
        Integer count of except handlers.
    """
    return sum(1 for child in ast.walk(node) if isinstance(child, ast.ExceptHandler))


def count_loops(node: _FuncNode) -> int:
    """Count for/while loops inside a function.

    Breadcrumb: counts ast.For, ast.AsyncFor, ast.While nodes.

    Args:
        node: ast.FunctionDef or ast.AsyncFunctionDef.

    Returns:
        Integer count of loop statements.
    """
    return sum(
        1 for child in ast.walk(node)
        if isinstance(child, (ast.For, ast.AsyncFor, ast.While))
    )


def logic_summary(node: _FuncNode) -> dict:
    """Return a dict with all logic metrics for a function node.

    Breadcrumb: aggregates cyclomatic_complexity, count_try_except, count_loops,
    plus raw if/for/while/try counts.

    Args:
        node: ast.FunctionDef or ast.AsyncFunctionDef.

    Returns:
        Dict with keys: cyclomatic_complexity, try_except_count, loop_count,
        if_count, for_count, while_count, try_count.
    """
    if_count = sum(1 for c in ast.walk(node) if isinstance(c, ast.If))
    for_count = sum(1 for c in ast.walk(node) if isinstance(c, (ast.For, ast.AsyncFor)))
    while_count = sum(1 for c in ast.walk(node) if isinstance(c, ast.While))
    try_count = sum(1 for c in ast.walk(node) if isinstance(c, ast.Try))

    return {
        "cyclomatic_complexity": cyclomatic_complexity(node),
        "try_except_count": count_try_except(node),
        "loop_count": count_loops(node),
        "if_count": if_count,
        "for_count": for_count,
        "while_count": while_count,
        "try_count": try_count,
    }
