"""
Project Setup Validator - Validates project setup and auto-creates missing folders.

Thin adapter that delegates to the universal common.library.validation.ValidationManager
while preserving the EKS-specific public API and P1-SETUP-* error code wiring.

Revision: 0.7
Date: 2026-07-09
Author: opencode
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from common.library.utility.validation.manager import ValidationManager
from common.library.loader import discover_schema_files


def _load_setup_error_codes() -> Dict[str, str]:
    """Load P1-SETUP-* error codes from the error catalog (SSOT)."""
    codes = {
        "ERR_MISSING_FOLDER": "P1-SETUP-F001",
        "ERR_MISSING_FILE": "P1-SETUP-F002",
        "ERR_MISSING_EKS_YML": "P1-SETUP-F003",
        "ERR_MISSING_DEP": "P1-SETUP-D001",
        "ERR_OUTPUT_PATH": "P1-SETUP-O001",
        "ERR_PYTHON_MISMATCH": "P1-SETUP-E001",
    }
    try:
        base = Path(__file__).parent.parent.parent / "config"
        err_path = None
        for cand in (base / "schemas" / "eks_error_config.json", base / "eks_error_config.json"):
            if cand.exists():
                err_path = cand
                break
        if err_path:
            with open(err_path, "r", encoding="utf-8") as f:
                cat = json.load(6)
            sys_err = cat.get("system_errors", {})
            code_to_const = {
                "P1-SETUP-F001": "ERR_MISSING_FOLDER",
                "P1-SETUP-F002": "ERR_MISSING_FILE",
                "P1-SETUP-F003": "ERR_MISSING_EKS_YML",
                "P1-SETUP-D001": "ERR_MISSING_DEP",
                "P1-SETUP-O001": "ERR_OUTPUT_PATH",
                "P1-SETUP-E001": "ERR_PYTHON_MISMATCH",
            }
            for code, const in code_to_const.items():
                if code in sys_err:
                    codes[const] = code
    except Exception:
        pass
    return codes


_SETUP_ERR = _load_setup_error_codes()
ERR_PREFIX = "P1-SETUP"
ERR_MISSING_FOLDER = _SETUP_ERR["ERR_MISSING_FOLDER"]
ERR_MISSING_FILE = _SETUP_ERR["ERR_MISSING_FILE"]
ERR_MISSING_EKS_YML = _SETUP_ERR["ERR_MISSING_EKS_YML"]
ERR_MISSING_DEP = _SETUP_ERR["ERR_MISSING_DEP"]
ERR_OUTPUT_PATH = _SETUP_ERR["ERR_OUTPUT_PATH"]
ERR_PYTHON_MISMATCH = _SETUP_ERR["ERR_PYTHON_MISMATCH"]

_GENERIC_TO_EKS = {
    "MISSING_FOLDER": ERR_MISSING_FOLDER,
    "MISSING_FILE": ERR_MISSING_FILE,
    "MISSING_ENV_FILE": ERR_MISSING_EKS_YML,
    "MISSING_DEPENDENCY": ERR_MISSING_DEP,
    "FOLDER_CREATE_FAILED": ERR_MISSING_FOLDER,
    "MISSING_OPTIONAL_FOLDER": ERR_MISSING_FOLDER,
    "MISSING_OPTIONAL_FILE": ERR_MISSING_FILE,
    "PYTHON_MISMATCH": ERR_PYTHON_MISMATCH,
}


def _eks_code(generic_code: str) -> str:
    """Map generic error code to EKS P1-SETUP-* code."""
    return _GENERIC_TO_EKS.get(generic_code, generic_code)


def _convert_flat_to_object(flat_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert old flat-array project_setup format to DCC-aligned object model.

    Handles backward compatibility for tests and legacy callers.
    """
    obj = {}

    # Folders: convert required_folders + required_engine_subfolders
    required_folders = flat_config.get("required_folders", [])
    obj["folders"] = [
        {"name": f, "required": True, "purpose": f"Required folder: {f}", "auto_created": True}
        for f in required_folders
    ]
    engine_subfolders = flat_config.get("required_engine_subfolders", [])
    for sf in engine_subfolders:
        obj["folders"].append({
            "name": f"engine/{sf}", "required": True,
            "purpose": f"Engine subfolder: {sf}", "auto_created": True,
        })

    # Root files
    required_files = flat_config.get("required_files", [])
    obj["root_files"] = [
        {"name": f, "required": True, "purpose": f"Required file: {f}"}
        for f in required_files if "config/schemas" not in f
    ]
    obj["schema_files"] = [
        {"filename": f, "required": True, "description": f"Schema file: {f}"}
        for f in required_files if "config/schemas" in f
    ]

    # Environment
    env = flat_config.get("environment", {})
    if isinstance(env, dict) and "python_version" in env:
        obj["environment"] = [{
            "name": "conda",
            "required": True,
            "file": "eks/eks.yml",
            "location": "root",
            "python_version": env.get("python_version", ""),
            "conda_env": env.get("conda_env", ""),
            "key_dependencies": env.get("dependencies", []),
        }]
        obj["dependencies"] = {
            "required": env.get("dependencies", []),
            "optional": [],
            "engines": [],
        }
    elif isinstance(env, list):
        obj["environment"] = env
        obj["dependencies"] = {"required": [], "optional": [], "engines": []}

    # Project metadata (minimal)
    obj["project_metadata"] = {
        "project_id": "EKS-001",
        "project_name": "Engineering Knowledge System",
        "version": "1.0.0",
    }

    return obj


class ProjectSetupValidator:
    """
    Validates project setup — thin adapter delegating to universal ValidationManager.

    Preserves validate_all() and get_missing_items() public API (used by phase1_server.py)
    and the P1-SETUP-* error code + ErrorManager wiring (T1.79).
    """

    def __init__(self, project_root: Path, config_registry: Optional[Dict[str, Any]] = None, verbose: bool = False):
        self.project_root = Path(project_root) if isinstance(project_root, str) else project_root
        self.verbose = verbose
        self.validation_results: Dict[str, Any] = {}
        self._vm = ValidationManager()

        # Load setup config (T1.90): setup values are top-level in the config
        # (DCC project_config pattern). For backward compatibility, a legacy
        # `project_setup` wrapper is still accepted and preferred if present.
        full = {}
        if config_registry is not None:
            if hasattr(config_registry, "config") and isinstance(getattr(config_registry, "config"), dict):
                full = config_registry.config
            elif isinstance(config_registry, dict):
                full = config_registry
            elif hasattr(config_registry, "_config") and isinstance(config_registry._config, dict):
                full = config_registry._config

        setup = full.get("project_setup", full) if isinstance(full, dict) else {}

        if not setup:
            raise ValueError(
                "ProjectSetupValidator requires a 'project_setup' config section (SSOT). "
                "Provide config_registry with setup values (top-level or under 'project_setup')."
            )

        # Detect format: old flat-array or new DCC-aligned object model
        if "required_folders" in setup:
            self._setup_config = _convert_flat_to_object(setup)
        else:
            self._setup_config = setup

        self._folders = self._setup_config.get("folders", [])
        self._root_files = self._setup_config.get("root_files", [])
        self._schema_files = self._setup_config.get("schema_files", [])
        self._workflow_files = self._setup_config.get("workflow_files", [])
        self._tool_files = self._setup_config.get("tool_files", [])
        self._env = self._setup_config.get("environment", [])
        self._deps = self._setup_config.get("dependencies", {})
        self._discovery_rules = self._setup_config.get("discovery_rules", [])

        # Store global_paths from full config registry
        self.global_paths = full.get("global_paths", {}) if isinstance(full, dict) else {}

    def validate_all(self, auto_create: bool = True) -> Dict[str, Any]:
        """
        Run all validation checks — delegates to universal ValidationManager.

        Args:
            auto_create: Whether to auto-create missing folders

        Returns:
            Validation results with readiness status
        """
        result = self._vm.validate_project_setup(
            base_path=self.project_root,
            config=self._setup_config,
            auto_create_override=auto_create,
        )

        # Validate discovery_rules if present (T1.96.4)
        if self._discovery_rules:
            disc_result = self._vm.validate_discovery_rules(
                self._discovery_rules,
                base_path=self.project_root,
            )
            result["discovery_rules"] = disc_result
            if not disc_result.get("all_valid", True):
                for rule in disc_result.get("rules", []):
                    if rule.get("error_code"):
                        result.setdefault("error_codes", []).append({
                            "code": _eks_code(rule["error_code"]),
                            "message": f"Discovery rule directory missing: {rule.get('directory', '')}/{rule.get('pattern', '')}",
                        })
                result["readiness"] = "NO"

        # T1.98.7: validate workflow_files / tool_files (DCC project_config parity)
        result["workflow_files"] = self._validate_named_files(self._workflow_files)
        result["tool_files"] = self._validate_named_files(self._tool_files)

        # Map generic error codes to P1-SETUP-* codes
        for ec in result.get("error_codes", []):
            ec["code"] = _eks_code(ec["code"])

        # Map error codes in sub-results
        for entry in result.get("folders", {}).get("missing", []):
            entry["error_code"] = _eks_code(entry.get("error_code", "MISSING_FOLDER"))
        for entry in result.get("root_files", {}).get("missing", []):
            entry["error_code"] = _eks_code(entry.get("error_code", "MISSING_FILE"))
        for entry in result.get("schema_files", {}).get("missing", []):
            entry["error_code"] = _eks_code(entry.get("error_code", "MISSING_FILE"))
        for entry in result.get("workflow_files", {}).get("missing", []):
            entry["error_code"] = _eks_code(entry.get("error_code", "MISSING_FILE"))
        for entry in result.get("tool_files", {}).get("missing", []):
            entry["error_code"] = _eks_code(entry.get("error_code", "MISSING_FILE"))
        for entry in result.get("environment", {}).get("missing_files", []):
            entry["error_code"] = _eks_code(entry.get("error_code", "MISSING_ENV_FILE"))
        for entry in result.get("dependencies", {}).get("missing", []):
            entry["error_code"] = _eks_code(entry.get("error_code", "MISSING_DEPENDENCY"))

        # Rebuild the legacy-style validation_results for backward compat
        self.validation_results = self._build_legacy_result(result)

        if self.verbose:
            self._print_results()

        return self.validation_results

    def _validate_named_files(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check existence of named pipeline files (workflow_files / tool_files)."""
        found: List[Dict[str, Any]] = []
        missing: List[Dict[str, Any]] = []
        for f in files or []:
            if not isinstance(f, dict):
                continue
            name = f.get("filename") or f.get("name")
            if not name:
                continue
            path = self.project_root / name
            if path.exists():
                found.append({"name": name, "path": str(path), "exists": True})
            else:
                missing.append({
                    "name": name,
                    "path": str(path),
                    "exists": False,
                    "error_code": "MISSING_FILE",
                })
        return {"found": found, "missing": missing, "all_exist": not missing}

    def _build_legacy_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build backward-compatible validation_results dict from universal result."""
        folders = result.get("folders", {})
        root_files = result.get("root_files", {})
        schema_files = result.get("schema_files", {})
        workflow_files = result.get("workflow_files", {})
        tool_files = result.get("tool_files", {})
        env = result.get("environment", {})
        deps = result.get("dependencies", {})
        combined_files = {
            "missing": (
                root_files.get("missing", [])
                + schema_files.get("missing", [])
                + workflow_files.get("missing", [])
                + tool_files.get("missing", [])
            ),
            "all_exist": (
                root_files.get("all_exist", True)
                and schema_files.get("all_exist", True)
                and workflow_files.get("all_exist", True)
                and tool_files.get("all_exist", True)
            ),
        }
        has_env_file = all(e.get("file_exists", False) if e.get("file") else True for e in env.get("entries", []))
        eks_yml_candidates = [f for f in root_files.get("found", []) + root_files.get("missing", []) if "eks.yml" in f.get("name", "")]
        eks_yml_path = self.project_root
        eks_fn = ""
        for f in root_files.get("found", []):
            if "eks.yml" in f.get("name", ""):
                eks_fn = f.get("name", "")
                eks_yml_path = eks_yml_path / eks_fn
        if not eks_fn:
            for f in root_files.get("missing", []):
                if "eks.yml" in f.get("name", ""):
                    eks_fn = f.get("name", "")
                    eks_yml_path = eks_yml_path / eks_fn

        # Output paths (legacy check from global_paths)
        output_rel = self.global_paths.get("output_dir", "output")
        eks_root_val = self.global_paths.get("eks_root", "eks")
        output_path = self.project_root / eks_root_val / output_rel
        out_writable = False
        if output_path.exists():
            out_writable = os.access(str(output_path), os.W_OK)
        else:
            try:
                output_path.mkdir(parents=True, exist_ok=True)
                out_writable = True
            except (OSError, PermissionError):
                out_writable = False

        output_paths = {
            "paths": [{"path": str(output_path), "exists": output_path.exists(), "writable": out_writable}],
            "unwritable": [] if out_writable else [{"path": str(output_path), "error_code": ERR_OUTPUT_PATH}],
            "all_writable": out_writable,
        }

        all_valid = (
            folders.get("all_exist", True)
            and combined_files["all_exist"]
            and has_env_file
        )

        return {
            "project_root": str(self.project_root),
            "folders": folders,
            "files": combined_files,
            "environment": {
                "eks_yml_exists": has_env_file,
                "eks_yml_path": str(eks_yml_path),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "error_code": None if has_env_file else ERR_MISSING_EKS_YML,
            },
            "dependencies": deps,
            "output_paths": output_paths,
            "workflow_files": workflow_files,
            "tool_files": tool_files,
            "readiness": "YES" if all_valid else "NO",
            "error_codes": result.get("error_codes", []),
        }

    def get_readiness_status(self) -> str:
        if not self.validation_results:
            self.validate_all()
        return self.validation_results["readiness"]

    def get_missing_items(self) -> Dict[str, List[str]]:
        if not self.validation_results:
            self.validate_all(auto_create=False)

        def _extract_paths(entries):
            return [e["path"] if isinstance(e, dict) else e for e in entries]

        return {
            "folders": _extract_paths(self.validation_results.get("folders", {}).get("missing", [])),
            "files": _extract_paths(self.validation_results.get("files", {}).get("missing", [])),
        }

    def _print_results(self):
        """Print validation results (compat method — delegates to VM details)."""
        print("\n" + "=" * 60)
        print("PROJECT SETUP VALIDATION RESULTS")
        print("=" * 60)
        print(f"Project Root: {self.validation_results['project_root']}")
        print(f"Readiness: {self.validation_results['readiness']}")
        print()
        r = self.validation_results
        f_r = r.get("folders", {})
        print(f"Folders: {'✓ All exist' if f_r.get('all_exist') else '✗ Missing folders'}")
        for m in f_r.get("missing", []):
            print(f"    - [{m.get('error_code','')}] {m.get('path','')}")
        fi_r = r.get("files", {})
        print(f"Files: {'✓ All exist' if fi_r.get('all_exist') else '✗ Missing files'}")
        for m in fi_r.get("missing", []):
            print(f"    - [{m.get('error_code','')}] {m.get('path','')}")
        e_r = r.get("environment", {})
        print(f"Environment:\n  eks.yml: {'✓' if e_r.get('eks_yml_exists') else '✗'}")
        d_r = r.get("dependencies", {})
        print(f"Dependencies: {'✓ All available' if d_r.get('all_available') else '✗ Missing'}")
        for m in d_r.get("missing", []):
            print(f"    - [{m.get('error_code','')}] {m.get('package','')}")
        print("=" * 60 + "\n")
