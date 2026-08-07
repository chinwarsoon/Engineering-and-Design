"""
Parser Router for EKS - Maps file_type to parser class, orchestrates parse flow.
T1.38: Phase B of pipeline workflow.
T1.62: Updated to use ParserFactory for Dependency Injection pattern per Appendix F.
T1.194 (I265): Added optional runtime_slice injection (Appendix L D1) — the
caller (PipelineOrchestrator) supplies the resolved config slice; ParserRouter
never holds the ProjectConfigurationRegistry itself. Parser routing rules
remain schema-driven via file_type_registry (L.14.7 backward compatibility).
I276 (T1.207): Two-axis parser routing. Routing unit is the project binding:
axis 1 resolves the parsing profile from the projected document_type_registry
entry (code -> default_parsing_profile, from eks_document_type_schema.json
project_document_types); axis 2 resolves the reader by file_type. Falls back
to file-type-only routing when no per-binding profile exists. The default
profile is determined at route() time from the document_type (project-local
code); caller passes the document_type when known.
"""
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..logging.logger import EKSLogger, log_depth
from ..core.factories import ParserFactory


class ParserRouter:
    """
    Routes files to the correct parser based on file_type from file_type_registry.
    Orchestrates: parse() → extract_metadata() → StructureDetector.detect().
    Uses ParserFactory for Dependency Injection pattern per Appendix F.
    """

    def __init__(self, doc_config: Dict[str, Any], logger: Optional[EKSLogger] = None,
                 use_factory: bool = True, runtime_slice: Optional[Dict[str, Any]] = None,
                 processing_config: Optional[Dict[str, Any]] = None):
        """
        Initialize parser router.
        
        Args:
            doc_config: Document configuration with file_type_registry
            logger: Optional logger instance
            use_factory: Whether to use ParserFactory (default True for Appendix F pattern)
            runtime_slice: Optional injected config slice (T1.194/I265, Appendix L D1).
                Retained for traceability; routing rules remain schema-driven via
                file_type_registry (L.14.7 backward compatibility).
            processing_config: I281 (T1.224) — eks_processing_config.json values
                SSOT. Extraction profiles come from ``extraction_profiles``,
                superseding the removed doc_config parsing_profiles section (full
                repoint, Q2).
        """
        self.doc_config = doc_config
        self.logger = logger or EKSLogger("ParserRouter", level=1)
        self.file_type_registry = doc_config.get("file_type_registry", [])
        self.use_factory = use_factory
        # T1.194 (I265): Injected config slice (Appendix L D1).
        self.runtime_slice = runtime_slice or {}
        # I276 (T1.207): two-axis routing sources — projected document_type_registry
        # (code -> default_parsing_profile) and the parsing_profiles library
        # (profile_id -> parser_class / supported_extensions).
        # I281 (T1.224): extraction profiles from eks_processing_config.json.
        self.document_type_registry = doc_config.get("document_type_registry", [])
        self.parsing_profiles = (
            (processing_config or {}).get("extraction_profiles", {})
            or doc_config.get("parsing_profiles", {})
        )
        
        if use_factory:
            # Use ParserFactory for Dependency Injection
            self.parser_factory = ParserFactory(
                config_registry=doc_config, processing_config=processing_config)
            # I287 (T1.242): register parsers from extraction_profiles —
            # parser_class single-sourced there (removed from file_type_registry).
            for profile in self.parsing_profiles.values():
                parser_class = profile.get("parser_class", "")
                for ext in profile.get("supported_extensions", []):
                    if ext and parser_class:
                        self.parser_factory.register_parser(ext, parser_class)
        else:
            # Legacy mode: build parser map directly
            self._ext_parser_map = self._build_parser_map()

    def _build_parser_map(self) -> Dict[str, str]:
        """Map file extension to parser_class string (legacy mode).

        I287 (T1.242): source is extraction_profiles parser_class +
        supported_extensions — parser_class removed from file_type_registry.
        """
        result = {}
        for profile in self.parsing_profiles.values():
            parser_class = profile.get("parser_class", "")
            for ext in profile.get("supported_extensions", []):
                if ext and parser_class:
                    result[ext] = parser_class
        return result

    @log_depth
    def get_parser_class(self, file_type: str) -> Optional[str]:
        """Look up parser class path for a given file extension."""
        if self.use_factory:
            # Factory mode: check if parser is registered
            if file_type.lower() in self.parser_factory.get_supported_types():
                return f"ParserFactory.{file_type.lower()}"
            return None
        else:
            # Legacy mode
            return self._ext_parser_map.get(file_type.lower())

    @log_depth
    def resolve_parsing_profile(self, document_type: Optional[str]) -> Optional[str]:
        """
        I276 (T1.207): axis 1 — resolve the parsing profile for a document type.

        Looks up ``document_type`` (the project-local code stored in the registry
        DB) in the projected ``document_type_registry`` (derived from
        ``eks_document_type_schema.json#/project_document_types``). Returns the
        ``default_parsing_profile`` id declared on the binding, or ``None`` when
        the code is unknown or the binding declares no profile (caller falls back
        to file-type-only routing).
        """
        if not document_type:
            return None
        for entry in self.document_type_registry:
            if entry.get("code") == document_type:
                return entry.get("default_parsing_profile") or None
        return None

    @log_depth
    def resolve_reader(self, file_type: str,
                       document_type: Optional[str] = None) -> Optional[str]:
        """
        I276 (T1.207): two-axis routing resolution.

        Axis 1 (profile): document_type -> default_parsing_profile -> parser_class.
        Axis 2 (reader): file_type -> parser_class (existing file_type_registry /
        ParserFactory mapping).

        Precedence:
          1. If the binding's parsing profile declares a parser_class AND the
             profile's ``supported_extensions`` (or binding expected file types)
             admit the given file_type, use the profile's parser_class.
          2. Otherwise fall back to file-type-only routing (returns ``None`` to
             signal the caller to use the factory / extension map).

        Returns the fully-qualified parser class path, or ``None`` for fallback.
        """
        profile_id = self.resolve_parsing_profile(document_type)
        if profile_id:
            profile = self.parsing_profiles.get(profile_id, {})
            parser_class = profile.get("parser_class", "")
            if parser_class:
                supported = set(profile.get("supported_extensions", []))
                if not supported or file_type.lower() in supported:
                    self.logger.debug(
                        f"I276: profile '{profile_id}' -> {parser_class} for "
                        f"document_type={document_type}, file_type={file_type}",
                        context="ParserRouter.resolve_reader",
                    )
                    return parser_class
                self.logger.debug(
                    f"I276: profile '{profile_id}' does not support file_type "
                    f"'{file_type}' (supported={sorted(supported)}) — falling back",
                    context="ParserRouter.resolve_reader",
                )
        self.logger.debug(
            f"I276: no binding profile for document_type={document_type}, "
            f"file_type={file_type} — file-type-only routing",
            context="ParserRouter.resolve_reader",
        )
        return None

    @log_depth
    def instantiate_parser(self, parser_class_path: str, file_path: str) -> Any:
        """
        Dynamically import and instantiate a parser class.
        Returns the parser instance.
        """
        try:
            # Direct instantiation from class path string
            module_path, class_name = parser_class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            parser_cls = getattr(module, class_name)
            return parser_cls(file_path)
        except (ValueError, ImportError, AttributeError, TypeError) as e:
            self.logger.error(
                f"Failed to instantiate parser '{parser_class_path}' for {file_path}: {e}",
                context="ParserRouter.instantiate_parser"
            )
            raise

    @log_depth
    def route(self, file_path: str, file_type: str,
              document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Route a file through the parser pipeline:
        1. Resolve parser (I276: two-axis — binding profile x file_type reader;
           falls back to file-type-only when no per-binding profile exists)
        2. Instantiate parser
        3. Call parse() for content blocks
        4. Call extract_metadata() for file-level metadata
        5. Return structured results

        Returns a dict with keys:
            - file_path: source file path
            - file_type: extension code
            - parser_class: fully qualified class path used
            - content_blocks: list of parsed content blocks
            - metadata: file-level metadata dict
            - status: 'success', 'partial', or 'failed'
            - error: error message if status != 'success'
        """
        result = {
            "file_path": file_path,
            "file_type": file_type,
            "document_type": document_type,
            "parser_class": "",
            "content_blocks": [],
            "metadata": {},
            "status": "pending",
            "error": None,
        }

        parser = None
        parser_class_path = None

        # I276 (T1.207): axis 1 — try the binding's parsing profile reader first.
        profile_reader = self.resolve_reader(file_type, document_type)
        if profile_reader:
            parser_class_path = profile_reader
            result["parser_class"] = parser_class_path

        if self.use_factory and not parser_class_path:
            # Factory mode: get parser directly by file_type (axis 2 / fallback)
            try:
                parser = self.parser_factory.create(file_type, file_path=file_path)
                parser_class_path = f"ParserFactory.{file_type}"
                result["parser_class"] = parser_class_path
            except ValueError:
                parser_class_path = None
        elif not parser_class_path:
            # Legacy mode: get parser class path from extension map
            parser_class_path = self._ext_parser_map.get(file_type)
            result["parser_class"] = parser_class_path or ""
        
        if not parser_class_path and not parser:
            result["status"] = "failed"
            result["error"] = f"No parser registered for file type: {file_type}"
            self.logger.warning(
                f"No parser for file type '{file_type}': {file_path}",
                context="ParserRouter.route"
            )
            return result

        try:
            if not parser and parser_class_path:
                # Instantiate from resolved class path (profile reader or legacy map)
                if parser_class_path.startswith("ParserFactory."):
                    parser = self.parser_factory.create(
                        file_type, file_path=file_path
                    )
                else:
                    parser = self.instantiate_parser(parser_class_path, file_path)

            try:
                content = parser.parse()
                result["content_blocks"] = content if isinstance(content, list) else [content]
            except Exception as e:
                self.logger.warning(
                    f"Parse failed for {file_path}: {e}",
                    context="ParserRouter.route"
                )
                result["content_blocks"] = []
                result["status"] = "partial"
                result["error"] = f"Parse error: {e}"

            try:
                metadata = parser.extract_metadata()
                result["metadata"] = metadata if isinstance(metadata, dict) else {}
            except Exception as e:
                self.logger.warning(
                    f"Metadata extraction failed for {file_path}: {e}",
                    context="ParserRouter.route"
                )

            if result["status"] != "partial":
                result["status"] = "success"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(
                f"Parser routing failed for {file_path}: {e}",
                context="ParserRouter.route"
            )

        return result

    @log_depth
    def route_batch(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Route multiple files through the parser pipeline.
        Each file dict should have 'file_path' and 'file_type' keys.

        Returns list of result dicts.
        """
        self.logger.status(f"Routing {len(files)} files through parsers")
        results = []
        for file_info in files:
            file_path = file_info.get("file_path", "")
            file_type = file_info.get("file_type", "")
            result = self.route(file_path, file_type)
            results.append(result)

        success_count = sum(1 for r in results if r["status"] == "success")
        self.logger.status(
            f"Batch routing complete: {success_count}/{len(results)} succeeded"
        )
        return results
