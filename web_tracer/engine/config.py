"""engine/config.py — single source of truth for web_tracer constants.

Every module, CLI help text, README, `pyproject.toml` and the UI must read the
canonical values from here (AGENTS.md §1, §19). Never hardcode the project name,
abbreviation or port elsewhere. The values below MUST stay aligned with
`knowledge.json` `project_metadata` and the workplan (cross-source audit, §5.13).
"""

# ── Canonical project identity ────────────────────────────────────────────────
# Must match knowledge.json project_metadata.name and the workplan §9 table.
PROJECT_NAME = "Web Application Tracer"
PROJECT_ABBREV = "web_tracer"
# Mirrors knowledge.json version at T00; bump together when the charter changes.
PROJECT_VERSION = "0.1.0"

# ── Service / network ──────────────────────────────────────────────────────────
# web_tracer dashboard port. The code_tracer line keeps :8000 (do not collide).
SERVICE_HOST = "127.0.0.1"
SERVICE_PORT = 8100

# ── Single source of error / message catalogue (AGENTS.md §19) ─────────────────
# id -> (severity, template). severity in {INFO, WARN, FATAL}. Expanded per phase.
# Keep keys stable; the UI and logs reference them by id.
ERROR_CODES = {
    "WT-CAP-001": ("FATAL", "Required dependency '{pkg}' is missing; install it (see requirements.txt)."),
    "WT-PATH-001": ("FATAL", "Resolved path '{path}' escapes the allowed root."),
    "WT-CT-001": ("FATAL", "Endpoint contract drift: front end calls '{url}' the backend does not expose."),
}

# ── Known endpoint surface (single source of truth; CI checks against this) ──────
# Hard contract rule (workplan §8.5): every endpoint path string exists ONLY here.
# The front end must use these constants; scripts/check_contracts.py asserts
#   (front-end fetch URLs) ⊆ (FastAPI routes) ⊆ (this contract).
HEALTH = "/health"
# The dashboard is a single page served by this service (T10 shell, T39 tree tab).
DASHBOARD = "/"
UI_ASSETS = "/ui"          # concrete route is /ui/{filename}
CAPABILITIES = "/api/capabilities"
TARGET = "/api/target"
TARGET_SET = "/api/target/set"
FILE_READ = "/file/read"

# Phase 2 contract (workplan §9 rows 6-10, T28 / WT-10..WT-16).
BROWSER_RECORD_START = "/browser/record/start"
BROWSER_RECORD_STOP = "/browser/record/stop"
BROWSER_RECORD_STATUS = "/browser/record/status"
BROWSER_TRACE = "/browser/trace"          # concrete route is /browser/trace/{run_id}
BROWSER_IMPORT = "/browser/import"

# Phase 3 contract (workplan §9 rows 11-17, T29-T33 / WT-20..WT-25).
JAVA_RECEIVER_START = "/java/receiver/start"
JAVA_RECEIVER_STOP = "/java/receiver/stop"
JAVA_RECEIVER_STATUS = "/java/receiver/status"
JAVA_TRACE = "/java/trace"                # concrete route is /java/trace/{run_id}
JAVA_IMPORT = "/java/import"
JAVA_INSTR_STRATEGIES = "/java/instrumentation/strategies"
JAVA_INSTR_CONFIG = "/java/instrumentation/config"
# Standard OTLP/HTTP traces export path (OTel agents POST here). This service receives it
# on the same :8100 port; the receiver channel is protobuf|json (T29).
OTLP_TRACES = "/v1/traces"
# OTel default OTLP/HTTP port (agents may export directly here too; documented in agent_configs).
OTLP_DEFAULT_PORT = 4318

# Phase 4 contract (workplan §8.5 rows 18-20, T34-T38 / WT-30..WT-33).
CORRELATE = "/correlate"
CORRELATION_REPORT = "/correlation/report"    # concrete route is /correlation/report/{run_id}
EXECUTION_TREE = "/execution_tree"            # concrete route is /execution_tree/{run_id}

# Layer taxonomy (workplan §8.4). Single source for adapters + UI colour band (T54).
LAYERS = ("user", "browser", "http", "java", "db", "external")

# Contract: Phase 1 rows 1-5 + Phase 2 rows 6-10 + Phase 3 rows 11-17 + Phase 4 rows 18-20.
# Method -> list of paths.
ENDPOINTS = {
    "GET": [
        HEALTH, CAPABILITIES, TARGET, BROWSER_RECORD_STATUS, BROWSER_TRACE,
        JAVA_RECEIVER_STATUS, JAVA_TRACE, JAVA_INSTR_STRATEGIES,
        CORRELATION_REPORT, EXECUTION_TREE, DASHBOARD, UI_ASSETS,
    ],
    "POST": [
        TARGET_SET, FILE_READ, BROWSER_RECORD_START, BROWSER_RECORD_STOP, BROWSER_IMPORT,
        JAVA_RECEIVER_START, JAVA_RECEIVER_STOP, JAVA_IMPORT, JAVA_INSTR_CONFIG, OTLP_TRACES,
        CORRELATE,
    ],
}
# Flat set of every contract path (template prefixes), for the contract checker (T06).
CONTRACT_PATHS = {p for paths in ENDPOINTS.values() for p in paths}


def error_template(code: str) -> tuple[str, str] | None:
    """Return (severity, template) for an error code, or None if unknown."""
    return ERROR_CODES.get(code)
