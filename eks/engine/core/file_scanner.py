"""
File Scanner for EKS - Walk project directory, validate file types, register placeholders.
T1.37: Phase A of pipeline workflow.
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from ..logging.logger import EKSLogger, log_depth


class FileScanner:
    """
    Walks a project directory tree, discovers engineering documents,
    validates file extensions against file_type_registry, and registers
    placeholder rows in the documents table.
    """

    def __init__(self, config: Dict[str, Any], doc_config: Optional[Dict[str, Any]] = None,
                 logger: Optional[EKSLogger] = None):
        self.config = config
        self.doc_config = doc_config or config
        self.logger = logger or EKSLogger("FileScanner", level=1)
        self.file_type_registry = self.doc_config.get("file_type_registry", [])
        self.document_type_registry = self.doc_config.get("document_type_registry", [])
        self._ext_map = self._build_extension_map()
        self._doc_type_expected = self._build_expected_types_map()

    def _build_extension_map(self) -> Dict[str, Dict[str, Any]]:
        """Map file extension (without dot) to file_type_registry entry."""
        result = {}
        for entry in self.file_type_registry:
            ext = entry.get("extension", "").lower()
            if ext:
                result[ext] = entry
        return result

    def _build_expected_types_map(self) -> Dict[str, Set[str]]:
        """Map document_type_code to its expected_file_types set."""
        result = {}
        for entry in self.document_type_registry:
            code = entry.get("code", "")
            expected = set(entry.get("expected_file_types", []))
            result[code] = expected
        return result

    @log_depth
    def scan(self, root_dir: Path, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Walk root_dir and discover files with recognized extensions.

        Returns a list of dicts, each containing:
            - file_path: absolute path to the file
            - file_name: basename of the file
            - file_type: extension code (e.g., 'pdf', 'dgn')
            - display_name: human-readable format name
            - parser_class: fully qualified parser class path
        """
        self.logger.status(f"Scanning directory: {root_dir}")
        root_dir = Path(root_dir)
        if not root_dir.exists():
            self.logger.warning(f"Directory does not exist: {root_dir}")
            return []

        discovered = []
        pattern = "**/*" if recursive else "*"
        for file_path in root_dir.glob(pattern):
            if not file_path.is_file():
                continue
            ext = file_path.suffix.lstrip(".").lower()
            if ext in self._ext_map:
                entry = self._ext_map[ext]
                discovered.append({
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "file_type": ext,
                    "display_name": entry.get("display_name", ext),
                    "parser_class": entry.get("parser_class", ""),
                })

        self.logger.info(
            f"Discovered {len(discovered)} files with recognized extensions",
            context="FileScanner.scan"
        )
        return discovered

    @log_depth
    def validate_file_types(self, discovered: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Validate discovered files against document_type_registry expected_file_types.

        Returns (valid_files, unknown_files) where:
            - valid_files: files whose extension is expected by at least one document type
            - unknown_files: files whose extension is not expected by any document type
        """
        all_expected = set()
        for expected_set in self._doc_type_expected.values():
            all_expected.update(expected_set)

        valid = []
        unknown = []
        for item in discovered:
            ext = item["file_type"]
            if ext in all_expected:
                valid.append(item)
            else:
                unknown.append(item)
                self.logger.warning(
                    f"File type '{ext}' not expected by any document type: {item['file_name']}",
                    context="FileScanner.validate_file_types"
                )

        self.logger.info(
            f"Validation: {len(valid)} valid, {len(unknown)} unknown",
            context="FileScanner.validate_file_types"
        )
        return valid, unknown

    @log_depth
    def build_placeholder_metadata(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a placeholder metadata dict for a discovered file.
        Extracts filename-based metadata using simple heuristics.
        """
        file_name = file_info["file_name"]
        file_path = file_info["file_path"]
        file_type = file_info["file_type"]

        metadata = {
            "file_path": file_path,
            "file_type": file_type,
            "source_type": "ingested",
            "extract_status": "pending",
        }

        parsed = self._parse_filename(file_name)
        metadata.update(parsed)

        return metadata

    def _parse_filename(self, file_name: str) -> Dict[str, Any]:
        """
        Parse filename to extract document_number and revision.
        Supports patterns like:
            DOC-001-A.pdf → doc_number=DOC-001, revision=A
            DOC-001_revA.pdf → doc_number=DOC-001, revision=A
            DOC-001.pdf → doc_number=DOC-001, revision=None
        """
        stem = Path(file_name).stem
        result: Dict[str, Any] = {}

        parts = stem.split("_rev", 1)
        if len(parts) == 2:
            result["document_number"] = parts[0]
            result["revision"] = parts[1]
            return result

        parts = stem.rsplit("-", 1)
        if len(parts) == 2 and len(parts[1]) <= 3:
            result["document_number"] = parts[0]
            result["revision"] = parts[1]
            return result

        result["document_number"] = stem
        return result

    @log_depth
    def register_placeholders(self, valid_files: List[Dict[str, Any]], registry) -> int:
        """
        Register placeholder rows in the documents table for discovered files.
        Uses DocumentRegistry.register_document() for each file.

        Returns count of files registered.
        """
        self.logger.status(f"Registering {len(valid_files)} placeholder documents")
        count = 0
        for file_info in valid_files:
            metadata = self.build_placeholder_metadata(file_info)
            doc_number = metadata.get("document_number")
            revision = metadata.get("revision")
            if not doc_number:
                self.logger.warning(
                    f"Cannot register file without document_number: {file_info['file_name']}",
                    context="FileScanner.register_placeholders"
                )
                continue

            existing = registry.get_document(doc_number, revision=revision)
            if existing:
                self.logger.info(
                    f"Document already registered: {doc_number}-{revision or 'latest'}",
                    context="FileScanner.register_placeholders"
                )
                continue

            metadata["document_type"] = self._infer_doc_type(file_info["file_type"])
            registry.register_document(metadata)
            count += 1

        self.logger.status(f"Registered {count} new placeholder documents")
        return count

    def _infer_doc_type(self, file_type: str) -> Optional[str]:
        """
        Infer document_type from file_type using document_type_registry.
        Returns the first document type whose expected_file_types includes this file_type.
        """
        for entry in self.document_type_registry:
            if file_type in entry.get("expected_file_types", []):
                return entry.get("code")
        return None
