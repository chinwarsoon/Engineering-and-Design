"""
Schema-Driven File Property Parser — Universal Class (Appendix J Implementation).

Extracts two layers of per-file metadata:
  Layer 1 — OS-level properties via pathlib.Path.stat() + hashlib
  Layer 2 — Format-specific embedded properties from parser extract_metadata()

All extraction rules are schema-driven via ``file_property_patterns`` in
eks_doc_config.json.  No hardcoded field lists.

Revision: 0.2
Date: 2026-07-19
Author: CodeBuddy
Summary: T1.99.147 (I187) — migrated _compute_hash() to common.library.utility.file_hash.
         Removed direct hashlib import; delegates to compute_file_hash() from common.
         Original: 0.1 — Initial implementation per Appendix J §J4.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from common.library.utility.file_hash import compute_file_hash
from ..logging.logger import EKSLogger


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class FilePropertyResult:
    """Container for all extracted file properties — OS-level + embedded.

    22 fields total:
      6 OS  (file_size, fs_created, fs_modified, fs_accessed, file_mode, file_hash)
     14 embedded (per Appendix J §J5 capability matrix)
      2 diagnostics (extract_status, extract_errors)
    """

    # ---- Layer 1: OS-level (Path.stat) ----
    file_size: Optional[int] = None
    fs_created: Optional[datetime] = None
    fs_modified: Optional[datetime] = None
    fs_accessed: Optional[datetime] = None
    file_mode: Optional[int] = None
    file_hash: Optional[str] = None

    # ---- Layer 2: Embedded (parser metadata) ----
    created_by: Optional[str] = None
    embedded_title: Optional[str] = None
    embedded_subject: Optional[str] = None
    embedded_created_date: Optional[str] = None
    embedded_modified_date: Optional[str] = None
    embedded_creator_app: Optional[str] = None
    embedded_producer: Optional[str] = None
    embedded_last_modified_by: Optional[str] = None
    embedded_keywords: Optional[str] = None
    embedded_sheet_count: Optional[int] = None
    embedded_revision_number: Optional[str] = None
    page_count: Optional[int] = None

    # ---- Diagnostics ----
    extract_status: str = "pending"  # ok | partial | failed
    extract_errors: List[str] = field(default_factory=list)

    # ---- Field name → registry column mapping (no leading underscore) ----
    # Single declaration with default_factory + repr=False (merged from two declarations
    # to avoid __dataclass_fields__ override issue in __post_init__).
    _REGISTRY_MAP: Dict[str, str] = field(default_factory=lambda: {
        "file_size": "file_size",
        "fs_created": "file_created_at",
        "fs_modified": "file_modified_at",
        "file_hash": "file_hash",
        "created_by": "created_by",
        "embedded_title": "embedded_title",
        "embedded_subject": "embedded_subject",
        "embedded_created_date": "embedded_created_date",
        "embedded_modified_date": "embedded_modified_date",
        "embedded_creator_app": "embedded_creator_app",
        "embedded_producer": "embedded_producer",
        "embedded_last_modified_by": "embedded_last_modified_by",
        "embedded_keywords": "embedded_keywords",
        "embedded_sheet_count": "embedded_sheet_count",
        "embedded_revision_number": "embedded_revision_number",
        "page_count": "page_count",
    }, repr=False)

    def __post_init__(self):
        # _REGISTRY_MAP is always populated by default_factory — no re-init needed.
        pass

    def to_registry_dict(self) -> Dict[str, Any]:
        """Convert to flat dict with registry column names, omitting None values.

        OS timestamps are converted to UTC ISO 8601 strings.
        Diagnostics (extract_status, extract_errors) are excluded.
        """
        result: Dict[str, Any] = {}
        for attr_name, col_name in self._REGISTRY_MAP.items():
            value = getattr(self, attr_name)
            if value is None:
                continue
            # Timestamps → ISO strings
            if isinstance(value, datetime):
                value = value.astimezone(timezone.utc).isoformat()
            result[col_name] = value
        return result


# ---------------------------------------------------------------------------
# FilePropertyExtractor
# ---------------------------------------------------------------------------

class FilePropertyExtractor:
    """Two-layer file property extraction class.

    Instantiate once per pipeline run, reuse across all files.
    Layer 1 (OS) is always available — zero external dependencies.
    Layer 2 (embedded) is driven by ``file_property_patterns`` config.

    Parameters
    ----------
    file_property_patterns : dict or None
        The ``file_property_patterns`` block from eks_doc_config.json.
        If None, the extractor operates in no-op mode (all fields None).
    logger : EKSLogger, optional
    """

    def __init__(
        self,
        file_property_patterns: Optional[Dict[str, Any]] = None,
        logger: Optional[EKSLogger] = None,
    ):
        self._config = file_property_patterns or {}
        self.logger = logger or EKSLogger("FilePropertyExtractor", level=2)

        # Resolve OS config
        os_cfg = self._config.get("os_properties", {})
        self._os_enabled: bool = bool(os_cfg.get("enabled", False))
        self._os_collect: List[str] = os_cfg.get("collect", []) if isinstance(os_cfg.get("collect"), list) else []
        self._hash_algorithm: str = os_cfg.get("hash_algorithm", "md5")

        # Resolve by_file_type config
        self._by_type: Dict[str, Dict[str, Any]] = {}
        raw_by_type = self._config.get("by_file_type", {})
        if isinstance(raw_by_type, dict):
            for ext, cfg in raw_by_type.items():
                if isinstance(cfg, dict):
                    self._by_type[ext] = cfg

        # No-op detection
        self._noop = not self._os_enabled and not self._by_type
        if self._noop:
            self.logger.warning(
                "FilePropertyExtractor initialized in no-op mode — "
                "file_property_patterns config is empty or missing. "
                "All extractions will return empty results.",
                context="FilePropertyExtractor.__init__",
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(
        self,
        file_path: str,
        file_type: str,
        parser_metadata: Optional[Dict[str, Any]] = None,
    ) -> FilePropertyResult:
        """Run two-layer extraction and return a populated FilePropertyResult.

        Parameters
        ----------
        file_path : str
            Absolute or relative path to the file on disk.
        file_type : str
            File extension (pdf, docx, xlsx, dgn, dwg) — used to look up
            per-type property mapping config.
        parser_metadata : dict, optional
            Dictionary returned by the parser's ``extract_metadata()``.
            Required when ``extraction_method`` is ``parser_metadata`` for
            this file type.

        Returns
        -------
        FilePropertyResult
        """
        result = FilePropertyResult()

        # ---- Layer 1: OS-level ----
        if self._os_enabled:
            self._extract_os(file_path, result)

        if result.extract_status == "failed":
            return result

        # ---- Layer 2: Embedded ----
        type_cfg = self._by_type.get(file_type)
        if type_cfg and type_cfg.get("enabled", False):
            method = type_cfg.get("extraction_method", "os_only")
            if method == "parser_metadata":
                self._extract_embedded(result, type_cfg, parser_metadata)

        # ---- Finalize status ----
        if result.extract_status == "pending":
            result.extract_status = "ok"
        elif result.extract_errors and not result.file_size:
            result.extract_status = "failed"
        elif result.extract_errors:
            result.extract_status = "partial"

        return result

    # ------------------------------------------------------------------
    # Layer 1 — OS properties
    # ------------------------------------------------------------------

    def _extract_os(self, file_path: str, result: FilePropertyResult) -> None:
        """Read OS-level properties via Path.stat() and hashlib."""
        path = Path(file_path)

        # Stat
        try:
            stat = path.stat()
        except FileNotFoundError:
            msg = f"File not found: {file_path}"
            result.extract_errors.append(msg)
            result.extract_status = "failed"
            self.logger.error(
                f"P5-F-PROP-0001: {msg}",
                context="FilePropertyExtractor._extract_os",
            )
            return
        except OSError as exc:
            msg = f"OS stat failed for {file_path}: {exc}"
            result.extract_errors.append(msg)
            result.extract_status = "failed"
            self.logger.error(
                f"P5-F-PROP-0002: {msg}",
                context="FilePropertyExtractor._extract_os",
            )
            return

        for key in self._os_collect:
            if key == "file_size":
                result.file_size = stat.st_size
            elif key == "fs_created":
                result.fs_created = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
            elif key == "fs_modified":
                result.fs_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            elif key == "fs_accessed":
                result.fs_accessed = datetime.fromtimestamp(stat.st_atime, tz=timezone.utc)
            elif key == "file_mode":
                result.file_mode = stat.st_mode
            elif key == "file_hash":
                try:
                    result.file_hash = self._compute_hash(path)
                except Exception as exc:
                    msg = f"Hash computation failed for {file_path}: {exc}"
                    result.extract_errors.append(msg)
                    self.logger.error(
                        f"P5-F-PROP-0005: {msg}",
                        context="FilePropertyExtractor._extract_os",
                    )

    def _compute_hash(self, path: Path) -> str:
        """Compute file content hash via common.library.utility.file_hash (SSOT)."""
        return compute_file_hash(path, algorithm=self._hash_algorithm)

    # ------------------------------------------------------------------
    # Layer 2 — Embedded (parser metadata)
    # ------------------------------------------------------------------

    def _extract_embedded(
        self,
        result: FilePropertyResult,
        type_cfg: Dict[str, Any],
        parser_metadata: Optional[Dict[str, Any]],
    ) -> None:
        """Map parser extract_metadata() keys to FilePropertyResult fields."""
        if parser_metadata is None:
            # This is config-dependent — some types may legitimately have no metadata
            self.logger.debug(
                "P5-F-PROP-0003: No parser metadata available for embedded extraction",
                context="FilePropertyExtractor._extract_embedded",
            )
            return

        property_mapping = type_cfg.get("property_mapping", [])
        if not isinstance(property_mapping, list):
            return

        for mapping in property_mapping:
            if not isinstance(mapping, dict):
                continue
            source_key = mapping.get("source_key")
            maps_to = mapping.get("maps_to")
            null_handling = mapping.get("null_handling", {})

            if source_key is None or maps_to is None:
                continue

            value = parser_metadata.get(source_key)

            if value is None:
                strategy = null_handling.get("strategy", "skip")
                if strategy == "default_value":
                    value = null_handling.get("default_value")
                else:
                    continue

            # Apply value to result
            self._set_result_field(result, maps_to, value, source_key)

    def _set_result_field(
        self, result: FilePropertyResult, maps_to: str, value: Any, source_key: str
    ) -> None:
        """Set a field on FilePropertyResult by its registry column name."""
        # Reverse the _REGISTRY_MAP to find the dataclass attribute name
        reverse_map = {v: k for k, v in result._REGISTRY_MAP.items()}
        attr_name = reverse_map.get(maps_to)

        if attr_name is None:
            self.logger.warning(
                f"P5-F-PROP-0004: Property mapping failure — "
                f"registry column '{maps_to}' (from source_key '{source_key}') "
                f"has no corresponding FilePropertyResult field",
                context="FilePropertyExtractor._set_result_field",
            )
            return

        # Type coercion for known integer fields
        int_fields = {"page_count", "embedded_sheet_count", "file_size"}
        if maps_to in int_fields and value is not None:
            try:
                value = int(value)
            except (ValueError, TypeError):
                result.extract_errors.append(
                    f"Type coercion failed for '{maps_to}': value '{value}' is not int-compatible"
                )
                return

        setattr(result, attr_name, value)


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------

def extract_file_properties(
    file_path: str,
    file_type: str,
    file_property_patterns: Optional[Dict[str, Any]] = None,
    parser_metadata: Optional[Dict[str, Any]] = None,
    logger: Optional[EKSLogger] = None,
) -> FilePropertyResult:
    """One-shot convenience wrapper — instantiates FilePropertyExtractor per call.

    Prefer instantiating FilePropertyExtractor once and calling .extract() in a
    loop for batch operations (Phase B pipeline processing).
    """
    extractor = FilePropertyExtractor(file_property_patterns, logger)
    return extractor.extract(file_path, file_type, parser_metadata)
