"""
Project Setup Validator - Validates project setup and auto-creates missing folders.

This module implements the Project Setup Validator pattern per Appendix F,
providing validation of required folders, files, and environment configuration.
Loads validation rules from the ConfigRegistry schema chain (T1.67),
falling back to hardcoded defaults if no config is provided.

Revision: 0.2
Date: 2026-06-30
Author: System
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json


class ProjectSetupValidator:
    """
    Validates project setup and auto-creates missing folders.
    
    This class implements the Project Setup Validator pattern per Appendix F,
    providing validation of required folders, files, and environment configuration.
    Loads validation rules from ConfigRegistry (project_setup section) with
    hardcoded fallback for backward compatibility.
    """
    
    def __init__(self, project_root: Path, config_registry: Optional[Dict[str, Any]] = None, verbose: bool = False):
        """
        Initialize project setup validator.
        
        Args:
            project_root: Root directory of the EKS project
            config_registry: ConfigRegistry or dict with project_setup section (T1.67)
            verbose: Whether to print verbose output
        """
        self.project_root = Path(project_root) if isinstance(project_root, str) else project_root
        self.verbose = verbose
        self.validation_results: Dict[str, Any] = {}
        
        # Load from config registry if provided (T1.67 schema-driven)
        config = {}
        if config_registry:
            if hasattr(config_registry, 'get'):
                config = config_registry.get("project_setup", {})
            elif isinstance(config_registry, dict):
                config = config_registry.get("project_setup", {})
        
        self.required_folders = config.get("required_folders", [
            "archive", "config", "data", "output", "engine",
            "log", "docs", "workplan", "test", "ui"
        ])
        self.required_engine_subfolders = config.get("required_engine_subfolders", [
            "core", "parsers", "chunking", "embedding",
            "vector_store", "graph", "extractors", "retrieval",
            "cache", "logging"
        ])
        self.required_files = config.get("required_files", [
            "eks.yml",
            "eks/config/schemas/eks_base_schema.json",
            "eks/config/schemas/eks_setup_schema.json"
        ])
        self.environment_config = config.get("environment", {})
        self.validation_options = config.get("validation_options", {})
    
    def validate_all(self, auto_create: bool = True) -> Dict[str, Any]:
        """
        Run all validation checks.
        
        Args:
            auto_create: Whether to auto-create missing folders
            
        Returns:
            Validation results with readiness status
        """
        self.validation_results = {
            "project_root": str(self.project_root),
            "folders": self._validate_folders(auto_create),
            "files": self._validate_files(),
            "environment": self._validate_environment(),
            "readiness": "UNKNOWN"
        }
        
        # Determine overall readiness
        all_valid = (
            self.validation_results["folders"]["all_exist"] and
            self.validation_results["files"]["all_exist"] and
            self.validation_results["environment"]["eks_yml_exists"]
        )
        
        self.validation_results["readiness"] = "YES" if all_valid else "NO"
        
        if self.verbose:
            self._print_results()
        
        return self.validation_results
    
    def _validate_folders(self, auto_create: bool) -> Dict[str, Any]:
        """
        Validate required folders.
        
        Args:
            auto_create: Whether to auto-create missing folders
            
        Returns:
            Folder validation results
        """
        results = {
            "missing": [],
            "created": [],
            "all_exist": True
        }
        
        # Validate top-level folders
        for folder in self.required_folders:
            folder_path = self.project_root / folder
            if not folder_path.exists():
                results["missing"].append(str(folder_path))
                results["all_exist"] = False
                
                if auto_create:
                    folder_path.mkdir(parents=True, exist_ok=True)
                    results["created"].append(str(folder_path))
                    if self.verbose:
                        print(f"[SETUP] Created missing folder: {folder_path}")
        
        # Validate engine subfolders
        engine_path = self.project_root / "engine"
        if engine_path.exists():
            for subfolder in self.required_engine_subfolders:
                subfolder_path = engine_path / subfolder
                if not subfolder_path.exists():
                    results["missing"].append(str(subfolder_path))
                    results["all_exist"] = False
                    
                    if auto_create:
                        subfolder_path.mkdir(parents=True, exist_ok=True)
                        results["created"].append(str(subfolder_path))
                        if self.verbose:
                            print(f"[SETUP] Created missing engine subfolder: {subfolder_path}")
        
        return results
    
    def _validate_files(self) -> Dict[str, Any]:
        """
        Validate required files.
        
        Returns:
            File validation results
        """
        results = {
            "missing": [],
            "all_exist": True
        }
        
        for file_path in self.required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                results["missing"].append(str(full_path))
                results["all_exist"] = False
        
        return results
    
    def _validate_environment(self) -> Dict[str, Any]:
        """
        Validate environment configuration.
        
        Returns:
            Environment validation results
        """
        results = {
            "eks_yml_exists": False,
            "eks_yml_path": str(self.project_root / "eks.yml"),
            "python_version": None,
            "expected_python": self.environment_config.get("python_version"),
            "expected_conda_env": self.environment_config.get("conda_env"),
            "dependencies": []
        }
        
        # Check for eks.yml
        eks_yml_path = self.project_root / "eks.yml"
        if eks_yml_path.exists():
            results["eks_yml_exists"] = True
        
        # Get Python version
        import sys
        results["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Check Python version match
        if results["expected_python"]:
            actual = f"{sys.version_info.major}.{sys.version_info.minor}"
            results["python_match"] = actual.startswith(results["expected_python"])
        
        return results
    
    def _print_results(self):
        """Print validation results."""
        print("\n" + "="*60)
        print("PROJECT SETUP VALIDATION RESULTS")
        print("="*60)
        print(f"Project Root: {self.validation_results['project_root']}")
        print(f"Readiness: {self.validation_results['readiness']}")
        print()
        
        # Folder results
        folder_results = self.validation_results["folders"]
        print(f"Folders: {'✓ All exist' if folder_results['all_exist'] else '✗ Missing folders'}")
        if folder_results["missing"]:
            print(f"  Missing: {len(folder_results['missing'])}")
            for folder in folder_results["missing"]:
                print(f"    - {folder}")
        if folder_results["created"]:
            print(f"  Created: {len(folder_results['created'])}")
            for folder in folder_results["created"]:
                print(f"    - {folder}")
        print()
        
        # File results
        file_results = self.validation_results["files"]
        print(f"Files: {'✓ All exist' if file_results['all_exist'] else '✗ Missing files'}")
        if file_results["missing"]:
            print(f"  Missing: {len(file_results['missing'])}")
            for file in file_results["missing"]:
                print(f"    - {file}")
        print()
        
        # Environment results
        env_results = self.validation_results["environment"]
        print(f"Environment:")
        print(f"  eks.yml: {'✓' if env_results['eks_yml_exists'] else '✗'}")
        print(f"  Python: {env_results['python_version']}")
        print()
        
        print("="*60 + "\n")
    
    def get_readiness_status(self) -> str:
        """
        Get project readiness status.
        
        Returns:
            "YES" if project is ready, "NO" otherwise
        """
        if not self.validation_results:
            self.validate_all()
        
        return self.validation_results["readiness"]
    
    def get_missing_items(self) -> Dict[str, List[str]]:
        """
        Get list of missing folders and files.
        
        Returns:
            Dictionary with "folders" and "files" keys containing missing items
        """
        if not self.validation_results:
            self.validate_all(auto_create=False)
        
        return {
            "folders": self.validation_results["folders"]["missing"],
            "files": self.validation_results["files"]["missing"]
        }
