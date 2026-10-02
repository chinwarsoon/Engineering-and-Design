"""scripts/check_undefined_functions.py — CI static check (workplan §8.5, T07).

Scans ``ui/*.html`` <script> blocks for bare function calls (``identifier(...)``
not preceded by ``.``) that are neither defined in the scanned code nor on a curated
allowlist of browser/JS globals. Exits non-zero (naming the call) on a genuine
undefined call; the existing dashboard must produce zero false positives.

Heuristic by design: it is a CI guard, not a parser. Allowlist tuning lives in
``ALLOWED`` below.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Browser/JS globals and standard-library calls that are always "defined".
ALLOWED = {
    "console", "document", "window", "fetch", "setTimeout", "setInterval",
    "clearTimeout", "clearInterval", "requestAnimationFrame", "cancelAnimationFrame",
    "queueMicrotask", "alert", "confirm", "prompt", "parseInt", "parseFloat",
    "isNaN", "isFinite", "decodeURI", "decodeURIComponent", "encodeURI",
    "encodeURIComponent", "escape", "unescape", "eval", "Function", "Object",
    "Array", "String", "Number", "Boolean", "Symbol", "BigInt", "Math", "JSON",
    "Date", "RegExp", "Map", "Set", "WeakMap", "WeakSet", "Promise", "Proxy",
    "Reflect", "Error", "TypeError", "RangeError", "SyntaxError", "ReferenceError",
    "Event", "CustomEvent", "addEventListener", "removeEventListener",
    "getElementById", "querySelector", "querySelectorAll", "createElement",
    "createTextNode", "appendChild", "removeChild", "setAttribute", "getAttribute",
    "localStorage", "sessionStorage", "navigator", "location", "history",
    "performance", "structuredClone", "WeakRef", "FinalizationRegistry",
    "AggregateError", "requestIdleCallback", "cancelIdleCallback",
    # CSS / layout functions referenced inside style strings
    "getComputedStyle", "rgba", "minmax", "rotate", "translate", "scale",
    "matrix", "cubicBezier", "linearGradient", "hsl", "hsla",
}
KEYWORDS = {
    "if", "for", "while", "switch", "catch", "function", "return", "new",
    "typeof", "instanceof", "await", "async", "do", "else", "throw", "void",
    "delete", "in", "of", "with", "case", "yield", "import", "export", "from",
    "class", "extends", "super", "this", "var", "let", "const",
}

CALL_RE = re.compile(r"(?<![\w.$])([A-Za-z_$][\w$]*)\s*\(")
DEF_RE = re.compile(
    r"(?:function\s+([A-Za-z_$][\w$]*))"
    r"|(?:([A-Za-z_$][\w$]*)\s*=\s*(?:function|\([^)]*\)\s*=>))"
    r"|(?:([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{)"
    r"|(?:class\s+([A-Za-z_$][\w$]*))"
)
PARAM_RE = re.compile(r"function\s*\(([^)]*)\)|\(([^)]*)\)\s*=>")


def extract_js(html: str) -> str:
    """Return the concatenated inline <script> bodies (raw, unstripped)."""
    blocks = [
        m.group(1)
        for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", html, re.S)
    ]
    return "\n".join(blocks)


def strip_comments_strings(js: str) -> str:
    """Remove comments and string/template literals so UI-label text like
    "Complexity (1-4)" inside strings/comments is not mistaken for a call site.

    Definitions are computed from the RAW script (see main) so this stripping can
    never delete a real function definition.
    """
    js = re.sub(r"/\*.*?\*/", " ", js, flags=re.S)  # block comments
    js = re.sub(r"//[^\n]*", " ", js)  # line comments
    js = re.sub(r"`[^`]*`", " ", js, flags=re.S)  # template literals (span lines)
    js = re.sub(r"\"[^\"]*\"", " ", js)  # double-quoted strings
    js = re.sub(r"'[^']*'", " ", js)  # single-quoted strings
    return js


def defined_names(js: str) -> set[str]:
    names: set[str] = set()
    for m in DEF_RE.finditer(js):
        for g in m.groups():
            if g:
                names.add(g)
    for m in PARAM_RE.finditer(js):
        params = m.group(1) or m.group(2) or ""
        for p in params.split(","):
            p = p.strip().split("=")[0].split(":")[0].strip()
            if p:
                names.add(p)
    for m in re.finditer(r"import\s*\{([^}]*)\}", js):
        for part in m.group(1).split(","):
            nm = part.strip().split(" as ")[-1].strip()
            if nm:
                names.add(nm)
    return names


def main() -> int:
    errors: list[str] = []
    for html in (ROOT / "ui").glob("*.html"):
        raw = extract_js(html.read_text(encoding="utf-8", errors="ignore"))
        stripped = strip_comments_strings(raw)
        # Definitions come from the RAW script (robust); calls are scanned on the
        # stripped version (avoids comment/string false positives).
        defined = defined_names(raw) | ALLOWED | KEYWORDS
        for m in CALL_RE.finditer(stripped):
            name = m.group(1)
            if name in defined:
                continue
            # skip `new Something(` — the constructor is a type, not a call site
            before = stripped[max(0, m.start() - 5) : m.start()].rstrip()
            if before.endswith("new"):
                continue
            errors.append(f"{html.name}: call to undefined function '{name}'")
    if errors:
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print(f"UNDEFINED-FUNCTION CHECK FAILED: {len(errors)} issue(s)", file=sys.stderr)
        return 1
    print("UNDEFINED-FUNCTION CHECK OK: no undefined bare calls in ui/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
