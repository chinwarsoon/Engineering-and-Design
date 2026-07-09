"""
L13 — ValidationManager

Unified validation manager for files, directories, and parameters.
Reference implementation from dcc/workflow/utility_engine/validation/validation_manager.py,
consolidated so EKS can replace its split setup_validator.py + validator.py.

Source: dcc/workflow/utility_engine/validation/validation_manager.py
        dcc/workflow/utility_engine/validation/validation_functions.py
"""

import importlib
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from common.library.utility.validation.models import (
    ValidationItem,
    ValidationResult,
    ValidationStatus,
)


class ValidationManager:
    """
    Centralized validation manager for all pipeline projects.

    Provides
    --------
    validate_file_exists()             — single file
    validate_directory_exists()        — single directory (with optional auto-create)
    validate_parameter()               — single parameter with optional custom validator
    validate_paths_and_parameters()    — batch: files + dirs + params in one call
    validate_pipeline_prerequisites()  — full pipeline pre-flight check
    validate_folders()                 — DCC-aligned folder-entry validation
    validate_named_files()             — DCC-aligned file-entry validation
    validate_environment()             — environment-entry validation
    validate_dependencies()            — dependency probe (required/optional/engines)
    validate_discovery_rules()         — discovery-rule validation (optional)
    validate_project_setup()           — full project-setup readiness check
    """

    def __init__(self, folder_creation_config: Optional[Dict[str, Any]] = None):
        self.folder_creation_config = folder_creation_config or {}

    # ------------------------------------------------------------------
    # Single-item validators
    # ------------------------------------------------------------------

    def validate_file_exists(
        self,
        file_path: Path,
        name: Optional[str] = None,
        required: bool = True,
    ) -> ValidationItem:
        name = name or str(file_path)
        exists = file_path.exists()
        if exists:
            status, message = ValidationStatus.PASS, f"File exists: {file_path}"
        elif required:
            status, message = ValidationStatus.FAIL, f"Required file not found: {file_path}"
        else:
            status, message = ValidationStatus.WARNING, f"Optional file not found: {file_path}"
        return ValidationItem(name=name, path=file_path, status=status, message=message, exists=exists)

    def validate_directory_exists(
        self,
        dir_path: Path,
        name: Optional[str] = None,
        required: bool = True,
        create_if_missing: bool = False,
    ) -> ValidationItem:
        name = name or str(dir_path)
        should_create = create_if_missing or self.folder_creation_config.get("create_missing_parents", False)

        if should_create and not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                return ValidationItem(
                    name=name, path=dir_path,
                    status=ValidationStatus.FAIL,
                    message=f"Cannot create directory: {exc}",
                    details=str(exc), exists=False,
                )

        exists = dir_path.exists()
        if exists:
            status, message = ValidationStatus.PASS, f"Directory exists: {dir_path}"
        elif required:
            status, message = ValidationStatus.FAIL, f"Required directory not found: {dir_path}"
        else:
            status, message = ValidationStatus.WARNING, f"Optional directory not found: {dir_path}"
        return ValidationItem(name=name, path=dir_path, status=status, message=message, exists=exists)

    def validate_parameter(
        self,
        param_name: str,
        param_value: Any,
        required: bool = True,
        allow_empty: bool = False,
        validator_func: Optional[Callable] = None,
    ) -> ValidationItem:
        empty_path = Path("")

        if param_value is None:
            status = ValidationStatus.FAIL if required else ValidationStatus.WARNING
            msg = f"{'Required' if required else 'Optional'} parameter missing: {param_name}"
            return ValidationItem(name=param_name, path=empty_path, status=status, message=msg, exists=False)

        if not allow_empty and isinstance(param_value, str) and not param_value.strip():
            status = ValidationStatus.FAIL if required else ValidationStatus.WARNING
            msg = f"{'Required' if required else 'Optional'} parameter empty: {param_name}"
            return ValidationItem(name=param_name, path=empty_path, status=status, message=msg, exists=True)

        if validator_func:
            try:
                result = validator_func(param_value)
                if isinstance(result, bool):
                    status = ValidationStatus.PASS if result else ValidationStatus.FAIL
                    msg = f"Parameter {param_name} {'passed' if result else 'failed'} validation"
                elif isinstance(result, tuple):
                    passed, msg = result
                    status = ValidationStatus.PASS if passed else ValidationStatus.FAIL
                    msg = f"Parameter {param_name}: {msg}"
                else:
                    status, msg = ValidationStatus.FAIL, f"Invalid validator result for {param_name}"
            except Exception as exc:
                status, msg = ValidationStatus.FAIL, f"Validator error for {param_name}: {exc}"
            return ValidationItem(name=param_name, path=empty_path, status=status, message=msg,
                                  exists=True, details=str(param_value))

        return ValidationItem(name=param_name, path=empty_path, status=ValidationStatus.PASS,
                              message=f"Parameter valid: {param_name}", exists=True,
                              details=str(param_value))

    # ------------------------------------------------------------------
    # Batch validator
    # ------------------------------------------------------------------

    def validate_paths_and_parameters(
        self,
        files: Optional[List[Tuple[Path, str, bool, bool]]] = None,
        directories: Optional[List[Tuple[Path, str, bool, bool]]] = None,
        parameters: Optional[List[Tuple[str, Any, bool, bool, Optional[Callable]]]] = None,
    ) -> ValidationResult:
        """
        Validate multiple files, directories, and parameters in one call.

        Tuple formats
        -------------
        files       : (path, name, required, create_parent)
        directories : (path, name, required, create_if_missing)
        parameters  : (name, value, required, allow_empty, validator_func)
        """
        items, errors, warnings = [], [], []

        for file_path, name, required, _ in (files or []):
            item = self.validate_file_exists(file_path, name, required)
            items.append(item)
            (errors if item.status == ValidationStatus.FAIL else
             warnings if item.status == ValidationStatus.WARNING else []).append(item.message)

        for dir_path, name, required, create in (directories or []):
            item = self.validate_directory_exists(dir_path, name, required, create)
            items.append(item)
            (errors if item.status == ValidationStatus.FAIL else
             warnings if item.status == ValidationStatus.WARNING else []).append(item.message)

        for param_name, param_value, required, allow_empty, validator_func in (parameters or []):
            item = self.validate_parameter(param_name, param_value, required, allow_empty, validator_func)
            items.append(item)
            (errors if item.status == ValidationStatus.FAIL else
             warnings if item.status == ValidationStatus.WARNING else []).append(item.message)

        if errors:
            status = ValidationStatus.FAIL
        elif warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.PASS

        summary = {
            "total_items": len(items),
            "passed": sum(1 for i in items if i.status == ValidationStatus.PASS),
            "failed": sum(1 for i in items if i.status == ValidationStatus.FAIL),
            "warnings": sum(1 for i in items if i.status == ValidationStatus.WARNING),
            "files_validated": len(files or []),
            "directories_validated": len(directories or []),
            "parameters_validated": len(parameters or []),
        }
        return ValidationResult(status=status, items=items, summary=summary,
                                errors=errors, warnings=warnings)

    # ------------------------------------------------------------------
    # Pipeline pre-flight
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # DCC-aligned project-setup validators (T1.84)
    # ------------------------------------------------------------------

    def validate_folders(
        self,
        base_path: Path,
        folders: List[Dict[str, Any]],
        auto_create_override: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Validate DCC-aligned folder entries.

        Each folder entry: ``{name, required, purpose, auto_created}``

        Returns
        -------
        dict with ``missing``, ``created``, ``all_exist``, ``entries``.
        """
        missing = []
        created = []
        all_exist = True
        entries = []

        for entry in folders:
            folder_name = entry.get("name", "")
            is_required = entry.get("required", True)
            auto_created = entry.get("auto_created", False)
            folder_path = base_path / folder_name

            item = {
                "name": folder_name,
                "path": str(folder_path),
                "required": is_required,
                "auto_created": auto_created,
                "purpose": entry.get("purpose", ""),
            }

            if folder_path.exists():
                item["exists"] = True
                item["error_code"] = None
            elif is_required or auto_created:
                should_create = (
                    auto_created if auto_create_override is None
                    else auto_create_override
                )
                if should_create:
                    try:
                        folder_path.mkdir(parents=True, exist_ok=True)
                        item["exists"] = True
                        item["error_code"] = None
                        created.append(str(folder_path))
                    except (OSError, PermissionError) as exc:
                        item["exists"] = False
                        item["error_code"] = "FOLDER_CREATE_FAILED"
                        item["error_detail"] = str(exc)
                        all_exist = False
                        missing.append(item)
                else:
                    item["exists"] = False
                    item["error_code"] = "MISSING_FOLDER"
                    all_exist = False
                    missing.append(item)
            else:
                item["exists"] = False
                item["error_code"] = "MISSING_OPTIONAL_FOLDER"
                missing.append(item)

            entries.append(item)

        return {
            "entries": entries,
            "missing": missing,
            "created": created,
            "all_exist": all_exist,
        }

    def validate_named_files(
        self,
        base_path: Path,
        entries: List[Dict[str, Any]],
        name_key: str = "name",
    ) -> Dict[str, Any]:
        """
        Validate DCC-aligned file entries (root_files, schema_files, etc.).

        Each entry must have a field identified by ``name_key`` (default ``name``)
        containing the filename relative to ``base_path``.

        Returns
        -------
        dict with ``missing``, ``found``, ``all_exist``.
        """
        missing = []
        found = []
        all_exist = True

        for entry in entries:
            filename = entry.get(name_key, "")
            is_required = entry.get("required", True)
            file_path = base_path / filename

            item = {
                "name": filename,
                "path": str(file_path),
                "required": is_required,
                "purpose": entry.get("purpose", "") or entry.get("description", ""),
            }

            if file_path.exists():
                item["exists"] = True
                item["error_code"] = None
                found.append(item)
            elif is_required:
                item["exists"] = False
                item["error_code"] = "MISSING_FILE"
                all_exist = False
                missing.append(item)
            else:
                item["exists"] = False
                item["error_code"] = "MISSING_OPTIONAL_FILE"

            found.append(item)

        return {
            "missing": missing,
            "found": found,
            "all_exist": all_exist,
        }

    def validate_environment(
        self,
        env_entries: List[Dict[str, Any]],
        base_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Validate environment entries.

        Each entry: ``{name, required, file, location, setup_commands, key_dependencies}``

        Returns
        -------
        dict with ``entries``, ``missing_files``, ``all_valid``.
        """
        results = []
        missing_files = []
        all_valid = True

        for entry in env_entries:
            env_name = entry.get("name", "")
            is_required = entry.get("required", True)
            env_file = entry.get("file")
            raw_python = entry.get("python_version")
            key_deps = entry.get("key_dependencies", [])

            item = {
                "name": env_name,
                "required": is_required,
                "file": env_file,
                "file_exists": None,
                "python_version": None,
                "python_match": None,
                "key_dependencies": key_deps,
                "error_code": None,
            }

            # Check env file existence
            if env_file and base_path:
                env_path = base_path / env_file
                item["file_exists"] = env_path.exists()
                if not item["file_exists"] and is_required:
                    item["error_code"] = "MISSING_ENV_FILE"
                    missing_files.append(item)
                    all_valid = False
            elif env_file and not base_path:
                item["file_exists"] = None

            # Check python version
            if raw_python:
                actual = f"{sys.version_info.major}.{sys.version_info.minor}"
                item["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                item["python_match"] = actual.startswith(raw_python)
                if not item["python_match"]:
                    item["error_code"] = "PYTHON_MISMATCH"
                    all_valid = False

            results.append(item)

        return {
            "entries": results,
            "missing_files": missing_files,
            "all_valid": all_valid,
        }

    def validate_dependencies(
        self,
        deps: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate dependencies config.

        Config: ``{required[], optional[], engines[{module, members[], optional}]}``

        Returns
        -------
        dict with ``available``, ``missing``, ``all_available``.
        """
        available = []
        missing = []
        all_available = True

        required_pkgs = deps.get("required", []) if isinstance(deps, dict) else deps if isinstance(deps, list) else []

        for pkg in required_pkgs:
            try:
                importlib.import_module(pkg.replace("-", "_"))
                available.append(pkg)
            except ImportError:
                missing.append({"package": pkg, "error_code": "MISSING_DEPENDENCY"})
                all_available = False

        optional_pkgs = deps.get("optional", []) if isinstance(deps, dict) else []
        for pkg in optional_pkgs:
            try:
                importlib.import_module(pkg.replace("-", "_"))
                available.append(pkg)
            except ImportError:
                pass

        engine_modules = deps.get("engines", []) if isinstance(deps, dict) else []
        for eng in engine_modules:
            mod_name = eng.get("module", "")
            is_optional = eng.get("optional", False)
            try:
                mod = importlib.import_module(mod_name)
                for member in eng.get("members", []):
                    if not hasattr(mod, member):
                        raise ImportError(f"Module {mod_name} has no member {member}")
                available.append(mod_name)
            except ImportError:
                if not is_optional:
                    missing.append({"package": mod_name, "error_code": "MISSING_ENGINE"})
                    all_available = False

        return {
            "available": available,
            "missing": missing,
            "all_available": all_available,
        }

    def validate_discovery_rules(
        self,
        rules: List[Dict[str, Any]],
        base_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Validate discovery rules (optional).

        Each rule: ``{pattern, directory, recursive, auto_register, category, exclude_patterns[]}``

        Returns
        -------
        dict with ``rules``, ``all_valid``.
        """
        results = []
        all_valid = True

        for rule in rules:
            pattern = rule.get("pattern", "")
            directory = rule.get("directory", "")
            rule_path = base_path / directory if base_path and directory else None

            item = {
                "pattern": pattern,
                "directory": directory,
                "recursive": rule.get("recursive", False),
                "auto_register": rule.get("auto_register", False),
                "category": rule.get("category", ""),
                "directory_exists": rule_path.exists() if rule_path else None,
                "error_code": None,
            }

            if rule_path and not rule_path.exists():
                item["error_code"] = "DISCOVERY_DIR_MISSING"

            results.append(item)

        return {
            "rules": results,
            "all_valid": all_valid,
        }

    def validate_project_setup(
        self,
        base_path: Path,
        config: Dict[str, Any],
        auto_create_override: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Full project-setup readiness check combining all DCC-aligned validators.

        ``config`` should contain::

            {
                "folders": [...],
                "root_files": [...],
                "schema_files": [...],
                "environment": [...],
                "dependencies": {...} | [...],
                "discovery_rules": [...],
                "validation_rules": [...]
            }

        Returns
        -------
        dict with ``readiness``, ``folders``, ``files``, ``environment``,
        ``dependencies``, ``discovery_rules``, ``error_codes``.
        """
        folders_result = self.validate_folders(base_path, config.get("folders", []), auto_create_override)
        root_files_result = self.validate_named_files(base_path, config.get("root_files", []))
        schema_files_result = self.validate_named_files(base_path, config.get("schema_files", []))
        env_result = self.validate_environment(config.get("environment", []), base_path)
        deps_result = self.validate_dependencies(config.get("dependencies", {}))
        disc_result = self.validate_discovery_rules(config.get("discovery_rules", []), base_path)

        all_exist = (
            folders_result.get("all_exist", True)
            and root_files_result.get("all_exist", True)
            and schema_files_result.get("all_exist", True)
            and env_result.get("all_valid", True)
        )

        error_codes = []
        for entry in folders_result.get("missing", []):
            error_codes.append({"code": entry.get("error_code", "MISSING_FOLDER"), "path": entry["path"]})
        for entry in root_files_result.get("missing", []):
            error_codes.append({"code": entry.get("error_code", "MISSING_FILE"), "path": entry["path"]})
        for entry in schema_files_result.get("missing", []):
            error_codes.append({"code": entry.get("error_code", "MISSING_FILE"), "path": entry["path"]})
        for entry in env_result.get("missing_files", []):
            ec = entry.get("error_code", "MISSING_ENV_FILE")
            fp = entry.get("file", "")
            error_codes.append({"code": ec, "path": fp})
        for entry in deps_result.get("missing", []):
            error_codes.append({"code": entry.get("error_code", "MISSING_DEPENDENCY"), "package": entry.get("package", "")})

        return {
            "readiness": "YES" if all_exist else "NO",
            "folders": folders_result,
            "root_files": root_files_result,
            "schema_files": schema_files_result,
            "environment": env_result,
            "dependencies": deps_result,
            "discovery_rules": disc_result,
            "error_codes": error_codes,
        }

    def validate_pipeline_prerequisites(
        self,
        base_path: Path,
        schema_path: Path,
        input_file_path: Path,
        export_paths: Dict[str, Path],
        effective_parameters: Dict[str, Any],
        project_config: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """Full pipeline pre-flight: files, output dirs, and key parameters."""
        fc = {}
        if project_config and "folder_creation" in project_config:
            fc = project_config["folder_creation"]
            self.folder_creation_config = fc
        else:
            fc = {"auto_create_output_directories": True, "create_missing_parents": True}
            self.folder_creation_config = fc

        auto_create = fc.get("auto_create_output_directories", True) and fc.get("create_missing_parents", True)

        files = [
            (schema_path, "Schema File", True, False),
            (input_file_path, "Input File", True, False),
        ]
        directories = [
            (base_path, "Base Directory", True, False),
            (export_paths["csv_path"].parent, "CSV Output Directory", True, auto_create),
            (export_paths["excel_path"].parent, "Excel Output Directory", True, auto_create),
            (export_paths["summary_path"].parent, "Summary Output Directory", True, auto_create),
        ]
        parameters = [
            ("effective_parameters", effective_parameters, True, False,
             lambda x: isinstance(x, dict) and len(x) > 0),
            ("upload_file_name", effective_parameters.get("upload_file_name"), True, False, None),
            ("nrows", effective_parameters.get("nrows"), False, True,
             lambda x: x is None or (isinstance(x, int) and x >= 0)),
        ]
        return self.validate_paths_and_parameters(files=files, directories=directories, parameters=parameters)
