"""
File Scanner for EKS - Walk project directory, validate file types, register placeholders.
T1.37: Phase A of pipeline workflow.
Revision 1.7.0 — T1.160 (I256): FilenameParser now receives project_code_titles from
SchemaLoader-injected doc_config, enabling project_title population during parse.
1.6.0: T1.157 (I255): FilenameParser now receives project_code_registry derived from
filename_patterns keys (minus '*') instead of project_code=None, enabling auto-pattern detection.
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from common.library.utility.synthetic_key import generate_synthetic_key
from common.library.utility.file_hash import compute_file_hash
from ..logging.logger import EKSLogger, log_depth
from .filename_parser import FilenameParser


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

        # T1.157 (I255): FilenameParser — shared instance, auto-detects project code per filename
        # T1.160 (I256): project_code_titles derived from project_code_schema injected by SchemaLoader
        filename_patterns = self.doc_config.get("filename_patterns", {})
        project_code_registry = [
            k for k in filename_patterns if k != "*"
        ]
        project_code_titles = self.doc_config.get("project_code_titles", {})
        self._parser = FilenameParser(
            filename_patterns=filename_patterns,
            project_code_registry=project_code_registry,
            project_code_titles=project_code_titles,
            document_type_registry=self.document_type_registry,
        )

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
        Uses schema-driven FilenameParser for field extraction (T1.99.115).
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

        # T1.99.115: Use shared FilenameParser instance
        result = self._parser.parse(file_name)
        metadata.update(result.to_metadata_dict())
        metadata["parse_status"] = result.parse_status
        metadata["parse_errors"] = result.parse_errors

        # Safety net: guarantee 'revision' key exists before downstream use. (I131)
        metadata.setdefault("revision", "00")

        return metadata

    @log_depth
    def register_placeholders(self, valid_files: List[Dict[str, Any]], registry) -> int:
        """
        Register placeholder rows in the documents table for discovered files.
        Uses DocumentRegistry.register_document() for each file.

        T1.99.151 (I185): Three-tier composite-key check:
          1. get_latest_by_key(doc_number, revision) — no row → register
          2. hash match → content unchanged → skip
          3. hash mismatch → content changed → register new row + supersedes chain

        T1.99.148 (I187): L2 null-tolerant — generates synthetic key via common library.
        T1.99.119: L2 null-tolerant — generates synthetic UNRESOLVED-{hash} key
        instead of skipping files with unresolvable document_number.

        Returns count of files registered.
        """
        self.logger.status(f"Registering {len(valid_files)} placeholder documents")
        count = 0
        skipped = 0
        superseded = 0
        total = len(valid_files)
        BATCH_MILESTONES = {0.25, 0.50, 0.75, 1.0}
        last_milestone_pct = 0.0
        for file_info in valid_files:
            metadata = self.build_placeholder_metadata(file_info)
            doc_number = metadata.get("document_number")
            revision = metadata.get("revision")

            # T1.99.148 (I187): L2 — generate synthetic key via common library
            if not doc_number:
                file_path = metadata.get("file_path", file_info.get("file_name", "unknown"))
                synthetic_key = generate_synthetic_key(file_path)
                self.logger.warning(
                    f"Unresolvable filename — generating synthetic key {synthetic_key} for: {file_info['file_name']}",
                    context="FileScanner.register_placeholders"
                )
                metadata["document_number"] = synthetic_key
                metadata["parse_status"] = "unresolvable"
                doc_number = synthetic_key
                if not revision:
                    revision = "00"
                    metadata["revision"] = revision

            # T1.99.151 (I185): Three-tier composite-key check
            # Tier 1 — key lookup: get latest row for (document_number, revision)
            existing = None
            try:
                existing = registry.get_latest_by_key(doc_number, revision)
            except AttributeError:
                # Fallback for registries that don't yet have get_latest_by_key
                existing = registry.get_document(doc_number, revision=revision)

            if existing:
                # Tier 2 — hash match: compute current file hash
                try:
                    current_hash = compute_file_hash(metadata["file_path"])
                    metadata["file_hash"] = current_hash
                except Exception:
                    # Hash computation failed — register anyway (best-effort)
                    current_hash = None

                if current_hash and current_hash == existing.get("file_hash"):
                    # Content unchanged → skip
                    self.logger.debug(
                        f"Content unchanged — skipping: {doc_number}-{revision}",
                        context="FileScanner.register_placeholders"
                    )
                    skipped += 1
                    continue

                # Tier 3 — hash mismatch: content has changed → register new row
                self.logger.warning(
                    f"Content change detected — creating supersedes chain: "
                    f"{existing.get('id')} → {doc_number}-{revision}",
                    context="FileScanner.register_placeholders"
                )
                superseded += 1
                # metadata["file_hash"] already set above; registry handles supersedes chain
            else:
                # Tier 1 result: no existing row → compute hash for first-time registration
                try:
                    metadata["file_hash"] = compute_file_hash(metadata["file_path"])
                except Exception:
                    pass  # best-effort

            # Only infer document_type from extension if filename parser didn't yield a value
            if not metadata.get("document_type") or metadata["document_type"] in ("UNKNOWN", None):
                metadata["document_type"] = self._infer_doc_type(file_info["file_type"])
            registry.register_document(metadata)
            count += 1

            processed = count + skipped + superseded
            if total > 0:
                pct = processed / total
                for m in sorted(BATCH_MILESTONES):
                    if last_milestone_pct < m <= pct:
                        label = "100%" if m == 1.0 else f"{int(m*100)}%"
                        milestone_files = count if m == 1.0 else int(total * m)
                        self.logger.status(
                            f"[TELEMETRY] A-registration: milestone={label} files={milestone_files}"
                        )
                        last_milestone_pct = m

        self.logger.status(
            f"Registered {count} new placeholder documents ({skipped} skipped, {superseded} superseded)"
        )
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
