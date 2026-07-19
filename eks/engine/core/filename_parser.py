"""
Schema-Driven Filename Parser — Universal Class (Appendix I)

Revision 1.0.0 — T1.99.113: Initial implementation.
Single shared class across all 4 EKS call sites.
Extracts 7 filename-derived fields per Appendix B §B3.
Schema-driven via filename_patterns block in eks_doc_config.json.

Date: 2026-07-18
Author: CodeBuddy
Summary: FilenameParser + FilenameParseResult dataclass,
         segment-based field extraction, null-tolerant output,
         P5-format error codes.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set
import re


@dataclass
class FilenameParseResult:
    """
    Immutable result of parsing a single filename.

    All filename-derived fields are Optional[str] — null means
    "not extractable from this filename."  The Registry always
    receives a complete result; null fields trigger per-segment
    null_handling defaults downstream.

    Fields are ordered per Appendix B §B3 column priority.
    """
    document_number: Optional[str] = None
    revision: Optional[str] = None
    project_number: Optional[str] = None
    area: Optional[str] = None
    document_type: Optional[str] = None
    discipline: Optional[str] = None
    sequence_number: Optional[str] = None
    parse_status: str = "unresolvable"   # "ok" | "partial" | "unresolvable"
    parse_errors: List[str] = field(default_factory=list)

    def to_metadata_dict(self) -> Dict[str, Any]:
        """
        Convert to the flat dict expected by register_document().

        Excludes parse_status and parse_errors (internal fields).
        Excludes None-valued fields so the registry's schema defaults apply.
        """
        return {
            k: v for k, v in {
                "document_number": self.document_number,
                "revision": self.revision,
                "project_number": self.project_number,
                "area": self.area,
                "document_type": self.document_type,
                "discipline": self.discipline,
                "sequence_number": self.sequence_number,
            }.items() if v is not None
        }


class FilenameParser:
    """
    Schema-driven filename parser — universal class shared by all EKS call sites.

    Design:
      - Instantiated once per project per pipeline run.
      - Caches compiled regex patterns and resolved schema references.
      - .parse(file_name) → FilenameParseResult (never raises).
      - Call sites: FileScanner (Phase A), PipelineOrchestrator (Phase B),
                    phase1_server.py (UI endpoint).

    Revision: 1.0.0
    Date: 2026-07-18
    Author: CodeBuddy
    Summary: Universal class with segment-based field extraction,
             FilenameParseResult dataclass, cached validators, P5-format error codes.
    """

    # Hardcoded default when no config is available (backward compat)
    _HARDCODED_DEFAULT: Dict[str, Any] = {
        "description": "Hardcoded default (backward-compatible)",
        "parser_type": "delimited",
        "separator": "-",
        "min_segments": 1,
        "max_segments": None,
        "segments": [],
        "rejoin_separator": "-",
        "strip_suffixes": [],
        "revision_separators": ["_rev"],
        "dash_revision_max_len": 3,
        "output": {
            "document_number_source": "rejoin_segments",
            "fallback_doc_number": "full_stem",
            "fallback_revision": "00",
            "preservation_mode": "overwrite_existing",
        },
        "error_subcodes": {},
        "processing_phase": "P0",
    }

    # P5-format default error codes (fallback when config has no error_subcodes)
    _DEFAULT_ERROR_CODES: Dict[str, str] = {
        "too_few_segments": "P5-F-V-0004",
        "too_many_segments": "P5-F-V-0005",
        "segment_validation_failed": "P5-F-V-0006",
        "unresolvable": "P5-F-P-0007",
    }

    def __init__(
        self,
        filename_patterns: Optional[Dict[str, Any]] = None,
        project_code: Optional[str] = None,
        document_type_registry: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Args:
            filename_patterns: The 'filename_patterns' block from eks_doc_config.json.
                               If None, use _HARDCODED_DEFAULT.
            project_code: Optional project code to select project-specific pattern.
                          Falls back to '*' pattern if not found.
            document_type_registry: Optional list of document type entries for
                                    schema_reference validation (maps_to: "document_type").
        """
        self._patterns = filename_patterns or {}
        self._project_code = project_code
        self._doc_type_registry = document_type_registry or []
        self._pattern = self._resolve_pattern()
        self._compiled_validators: Dict[int, re.Pattern] = {}
        self._doc_type_codes: Optional[Set[str]] = None
        self._precompile_validators()

    # ---- Pattern Resolution ----

    def _resolve_pattern(self) -> Dict[str, Any]:
        """Resolve the active pattern: project_code → '*' → hardcoded default."""
        if not self._patterns:
            return dict(self._HARDCODED_DEFAULT)
        pattern = self._patterns.get(self._project_code) if self._project_code else None
        if pattern is None:
            pattern = self._patterns.get("*", self._HARDCODED_DEFAULT)
        # Merge with hardcoded default for any missing keys
        merged = dict(self._HARDCODED_DEFAULT)
        merged.update(pattern)
        return merged

    def _precompile_validators(self) -> None:
        """Pre-compile regex patterns for segment validation to avoid re-compile per file."""
        for seg in self._pattern.get("segments", []):
            validation = seg.get("validation", {})
            if validation.get("type") == "pattern" and validation.get("pattern"):
                self._compiled_validators[seg["position"]] = re.compile(validation["pattern"])
        # Pre-build document_type lookup set for schema_reference validation
        if self._doc_type_registry:
            self._doc_type_codes = {entry.get("code", "") for entry in self._doc_type_registry}

    def _get_error_code(self, key: str) -> str:
        """Get error code from pattern's error_subcodes or fallback to P5-format default."""
        error_subcodes = self._pattern.get("error_subcodes", {})
        return error_subcodes.get(key, self._DEFAULT_ERROR_CODES.get(key, "UNKNOWN"))

    # ---- Main Entry Point ----

    def parse(self, file_name: str) -> FilenameParseResult:
        """
        Parse a single filename into structured metadata.

        Never raises — always returns FilenameParseResult
        with parse_status indicating extraction quality.

        Args:
            file_name: Full filename (basename or path; Path.stem will be used).

        Returns:
            FilenameParseResult with all extractable fields populated.
        """
        result = FilenameParseResult()
        stem = Path(file_name).stem

        # Step 3: Strip known non-revision suffixes
        stem = self._strip_suffixes(stem)

        # Step 4: Revision separator split
        doc_stem, revision = self._extract_revision(stem)
        if revision is not None:
            result.revision = revision

        # Step 6: Segment extraction (on the stem after revision removal)
        segments_extracted = self._extract_segments(doc_stem, result)

        # Step 7: Construct document_number
        self._build_document_number(doc_stem, segments_extracted, result)

        # Finalize parse_status
        if not result.parse_errors:
            result.parse_status = "ok"
        elif result.parse_status == "unresolvable":
            pass  # keep unresolvable
        else:
            result.parse_status = "partial"

        return result

    # ---- Step 3: Suffix Stripping ----

    def _strip_suffixes(self, stem: str) -> str:
        """Strip the first matching non-revision suffix from the stem."""
        for suffix in self._pattern.get("strip_suffixes", []):
            if stem.endswith(suffix):
                return stem[:-len(suffix)]
        return stem

    # ---- Step 4: Revision Extraction ----

    def _extract_revision(self, stem: str) -> Tuple[str, Optional[str]]:
        """
        Try to extract a revision from the stem.

        Returns (remaining_stem, revision_or_None).
        """
        # 4a: Check explicit revision separators
        for sep in self._pattern.get("revision_separators", []):
            if sep in stem:
                parts = stem.split(sep, 1)
                return parts[0], parts[1]

        # 4b: Dash-suffix revision detection
        max_len = self._pattern.get("dash_revision_max_len", 0)
        if max_len > 0:
            parts = stem.rsplit("-", 1)
            if len(parts) == 2 and len(parts[1]) <= max_len:
                return parts[0], parts[1]

        return stem, None

    # ---- Step 6: Segment Extraction ----

    def _extract_segments(self, stem: str, result: FilenameParseResult) -> bool:
        """
        Split stem by separator and extract mapped fields into result.

        Returns True if at least one segment was successfully extracted.
        """
        segments = self._pattern.get("segments", [])
        if not segments:
            return False

        parts = stem.split(self._pattern.get("separator", "-"))

        # Check segment count bounds
        min_seg = self._pattern.get("min_segments", 1)
        max_seg = self._pattern.get("max_segments")

        if len(parts) < min_seg:
            err_code = self._get_error_code("too_few_segments")
            result.parse_errors.append(
                f"{err_code}: Expected >= {min_seg} segments, got {len(parts)} in '{stem}'"
            )
            result.parse_status = "partial"

        if max_seg is not None and len(parts) > max_seg:
            err_code = self._get_error_code("too_many_segments")
            result.parse_errors.append(
                f"{err_code}: Expected <= {max_seg} segments, got {len(parts)} in '{stem}'"
            )
            result.parse_status = "partial"

        any_extracted = False
        for seg_def in segments:
            pos = seg_def["position"]
            maps_to = seg_def.get("maps_to")
            label = seg_def.get("label", f"seg_{pos}")

            if pos >= len(parts):
                # Segment not present — apply null_handling
                self._apply_null_handling(seg_def, result, maps_to, label, reason="missing")
                continue

            raw_value = parts[pos]

            # Validate
            if not self._validate_segment(seg_def, raw_value):
                err_code = self._get_error_code("segment_validation_failed")
                result.parse_errors.append(
                    f"{err_code}: Segment validation failed at position {pos} "
                    f"('{label}' = '{raw_value}')"
                )
                result.parse_status = "partial"
                self._apply_null_handling(seg_def, result, maps_to, label,
                                          reason=f"validation_failed:{raw_value}")
                continue

            # Store the value
            if maps_to:
                setattr(result, maps_to, raw_value)
                any_extracted = True
            else:
                # maps_to is null — value used only in rejoined document_number
                result.sequence_number = raw_value
                any_extracted = True

        if not any_extracted:
            result.parse_status = "unresolvable"

        return any_extracted

    def _validate_segment(self, seg_def: Dict[str, Any], value: str) -> bool:
        """Validate a single segment value against its validation rule."""
        validation = seg_def.get("validation", {})
        vtype = validation.get("type")

        if vtype == "pattern":
            compiled = self._compiled_validators.get(seg_def["position"])
            if compiled:
                return bool(compiled.match(value))
            # Fallback: compile on the fly
            pattern = validation.get("pattern", "")
            if pattern:
                return bool(re.match(pattern, value))
            return True  # no pattern = no validation

        if vtype == "schema_reference":
            reference = validation.get("reference", "")
            if reference == "document_type_registry" and self._doc_type_codes is not None:
                return value in self._doc_type_codes
            # If registry not available, skip validation
            return True

        return True  # unknown validation type → pass

    def _apply_null_handling(
        self,
        seg_def: Dict[str, Any],
        result: FilenameParseResult,
        maps_to: Optional[str],
        label: str,
        reason: str,
    ) -> None:
        """Apply the segment's null_handling strategy."""
        nh = seg_def.get("null_handling", {})
        strategy = nh.get("strategy", "default_value")

        if strategy == "default_value":
            default = nh.get("default_value", "UNKNOWN")
            if maps_to:
                setattr(result, maps_to, default)
        elif strategy == "skip_segment":
            pass  # leave field as None
        elif strategy == "error":
            # Degrade gracefully — log as error but don't raise
            result.parse_errors.append(
                f"error strategy triggered for segment '{label}' ({reason})"
            )

    # ---- Step 7: Document Number Construction ----

    def _build_document_number(
        self, stem: str, segments_extracted: bool, result: FilenameParseResult
    ) -> None:
        """Build the final document_number from segments or fallback."""
        output = self._pattern.get("output", {})

        if segments_extracted and output.get("document_number_source") == "rejoin_segments":
            # Use the stem as-is since it's already cleaned of suffixes and revisions
            result.document_number = stem
        else:
            # Fallback
            if output.get("fallback_doc_number") == "full_stem":
                result.document_number = stem
            else:
                result.document_number = None

        # Apply fallback revision if none extracted
        if result.revision is None:
            result.revision = output.get("fallback_revision")


# ---- Module-Level Convenience Function ----

def parse_filename(
    file_name: str,
    filename_patterns: Optional[Dict[str, Any]] = None,
    project_code: Optional[str] = None,
    document_type_registry: Optional[List[Dict[str, Any]]] = None,
) -> FilenameParseResult:
    """
    One-shot convenience wrapper — instantiates FilenameParser per call.

    Prefer instantiating FilenameParser once and calling .parse() in a loop
    for batch operations (Phase A scan, pipeline processing).
    """
    parser = FilenameParser(filename_patterns, project_code, document_type_registry)
    return parser.parse(file_name)
