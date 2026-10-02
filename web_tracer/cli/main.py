"""cli/main.py — web_tracer command line entry point (Phase 1 skeleton, T09).

Usage:
    python -m cli.main version
    python -m cli.main check            # dependency capability probe
    python -m cli.main serve            # start the server + open dashboard
    python -m cli.main schema FILE...    # validate JSON against the frozen schemas
"""
from __future__ import annotations

import argparse
import sys

from engine import capability, config
from engine.schema import validate as schema_validate


def _serve() -> None:
    from launch import main as launch_main

    launch_main()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=config.PROJECT_ABBREV, description=config.PROJECT_NAME)
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("version", help="Print the project version")
    sub.add_parser("check", help="Run the dependency capability probe")
    sub.add_parser("serve", help="Start the web server and open the dashboard")
    sv = sub.add_parser("schema", help="Validate JSON file(s) against the frozen schemas")
    sv.add_argument("file", nargs="+", help="JSON file(s) to validate")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cmd = args.cmd
    if cmd == "version":
        print(f"{config.PROJECT_NAME} {config.PROJECT_VERSION}")
        return 0
    if cmd == "check":
        rc = 0
        for c in capability.capabilities():
            print(f"{c['level']:5} {c['name']} {c.get('version') or ''}  {c['message']}")
            if c["level"] == "FATAL":
                rc = 1
        return rc
    if cmd == "serve":
        _serve()
        return 0
    if cmd == "schema":
        return schema_validate.main(args.file)
    build_parser().print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
