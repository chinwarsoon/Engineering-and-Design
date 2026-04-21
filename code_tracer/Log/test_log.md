# Code Tracer — Test Log

## Instructions
1. Always log new test results immediately after completion.
2. Add a timestamp at the beginning of each log entry.
3. Summarize results and link to issue log where applicable.

---

# Section 2. Test Log Entries

*(none — see dcc/Log/test_log.md for pre-migration history)*

## 2026-04-19 07:00:00

### launch.py + Backend Endpoint Test — Post-Migration

**Method:** Direct uvicorn start + curl endpoint tests against `dcc/workflow` target (754 Python files)

| # | Test | Result | Detail |
|---|------|--------|--------|
| T1 | `/health` | PASS | `status=healthy version=0.2.0` |
| T2 | `/static/analyze` | PASS | `nodes=754 edges=737 entry_points=383` |
| T3 | `/static/report` | PASS | `total=754 top=apply_validation CC=100` |
| T4 | `/static/graph` | PASS | `nodes=754 edges=737` |
| T5 | `/file/read` relative path | PASS | `size=13931 chars` |
| T6 | `/file/read` security block | PASS | `/etc/passwd` → `Access denied` |
| T7 | `/file/validate` | PASS | `valid=True` |
| T8 | `launch.py --help` | PASS | Help text rendered correctly |

**Issues found and fixed:**
- CT-01: `ModuleNotFoundError: No module named 'tracer'` → fixed import paths
- CT-02: `edges=0` → installed `networkx==3.6.1`

**Final result:** 8/8 PASS
