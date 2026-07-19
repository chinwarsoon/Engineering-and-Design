"""
Pipeline Orchestrator for EKS - Coordinates Phase A/B/C pipeline workflow.
T1.39: Pre-parse → parse → score → review pipeline coordinator.
T1.63: Enhanced with checkpoints and telemetry heartbeat integration per Appendix F.
T1.64: Added phase rollback capability per Appendix F.
T1.68: Wired ErrorManager/MessageManager calls at phase boundaries and per-file failures.
T1.71: Replaced raw duckdb.connect in _update_doc_status with registry.update_document_status().

Revision: 0.2
Date: 2026-07-18
Author: opencode
Summary: 0.1: Initial orchestrator with checkpoint/telemetry/rollback/messaging integration.
0.2: T1.99.85/I124 — commented out per-phase checkpoint writes in run_full_pipeline()
     _after() closure; checkpoint unused by resume logic; context held in-memory.
"""
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from ..logging.logger import EKSLogger, log_depth
from .file_scanner import FileScanner
from .health_scorer import HealthScorer
from .structure_detector import StructureDetector
from ..parsers.parser_router import ParserRouter
from .context import EKSPipelineContext, EKSPaths
from .telemetry import TelemetryHeartbeat
from .error_manager import ErrorManager
from .message_manager import MessageManager
from .io_contracts import DiscoveryInput, DiscoveryOutput, HealthInput, HealthOutput
from ..parsers.io_contracts import ParserInput, ParserOutput
from .base import ErrorRecord, ValidationResult
from .filename_parser import FilenameParser
from .file_property_parser import FilePropertyExtractor


class PipelineOrchestrator:
    """
    Coordinates the 3-phase EKS pipeline with checkpoints and telemetry:
    - Phase A: Scan directory → register placeholder documents
    - Phase B: Route → parse → detect structure → score → update metadata
    - Phase C: Flag documents for manual review
    
    Enhanced per Appendix F with:
    - 5 clear phases (A-E) with telemetry heartbeat integration
    - Checkpoint state serialization for resume capability
    - Phase rollback mechanism for failed phases
    """

    def __init__(self, config: Dict[str, Any], doc_config: Dict[str, Any],
                 registry: Any, logger: Optional[EKSLogger] = None,
                 use_telemetry: bool = True,
                 error_manager: Optional[ErrorManager] = None,
                 message_manager: Optional[MessageManager] = None):
        """
        Initialize pipeline orchestrator.
        
        Args:
            config: Pipeline configuration
            doc_config: Document configuration
            registry: Document registry instance
            logger: Optional logger instance
            use_telemetry: Whether to enable telemetry heartbeat (default True)
            error_manager: Optional ErrorManager instance (T1.68)
            message_manager: Optional MessageManager instance (T1.68)
        """
        self.config = config
        self.doc_config = doc_config
        self.registry = registry
        self.logger = logger or EKSLogger("PipelineOrchestrator", level=1)
        self.use_telemetry = use_telemetry
        self.error_manager = error_manager
        self.message_manager = message_manager
        
        # Initialize components
        self.scanner = FileScanner(config, doc_config=doc_config, logger=self.logger)
        self.router = ParserRouter(doc_config, logger=self.logger, use_factory=True)
        self.scorer = HealthScorer(logger=self.logger)
        self.detector = StructureDetector(logger=self.logger)

        # T1.99.116: Shared FilenameParser for Phase B inline replacements
        filename_patterns = doc_config.get("filename_patterns", {})
        document_type_registry = doc_config.get("document_type_registry", [])
        self._parser = FilenameParser(
            filename_patterns=filename_patterns,
            project_code=None,
            document_type_registry=document_type_registry,
        )

        # T1.99.134: FilePropertyExtractor for Phase B property extraction (Appendix J)
        file_property_patterns = doc_config.get("file_property_patterns", {})
        self._property_extractor = FilePropertyExtractor(
            file_property_patterns=file_property_patterns,
            logger=self.logger,
        )
        
        # Initialize telemetry heartbeat
        self.telemetry = TelemetryHeartbeat(enabled=use_telemetry, verbose=False)
        
        # Initialize pipeline context
        self.context: Optional[EKSPipelineContext] = None
        self.checkpoint_states: Dict[str, Dict[str, Any]] = {}
    
    def initialize_context(self, data_dir: Path, schema_dir: Path, output_dir: Path,
                          archive_dir: Path, config_dir: Path, log_dir: Path,
                          parameters: Optional[Dict[str, Any]] = None,
                          config_registry: Optional[Any] = None,
                          schema_registry: Optional[Any] = None,
                          checkpoint_state: Optional[Dict[str, Any]] = None):
        """
        Initialize pipeline context with paths, parameters, and registries (T1.99.41).
        
        Args:
            data_dir: Data directory path
            schema_dir: Schema directory path
            output_dir: Output directory path
            archive_dir: Archive directory path
            config_dir: Config directory path
            log_dir: Log directory path
            parameters: Pipeline parameters from EngineInput
            config_registry: ConfigRegistry instance (SSOT)
            schema_registry: Schema loader instance
            checkpoint_state: Optional checkpoint state for resume
        """
        paths = EKSPaths(
            data_dir=data_dir,
            schema_dir=schema_dir,
            output_dir=output_dir,
            archive_dir=archive_dir,
            config_dir=config_dir,
            log_dir=log_dir
        )
        
        # Populate context with bootstrap data (T1.99.41)
        from .context import EKSData
        data = EKSData()
        if checkpoint_state:
            # Restore data from checkpoint if resuming
            if "documents" in checkpoint_state:
                data.documents = checkpoint_state["documents"]
            if "extracted_content" in checkpoint_state:
                data.extracted_content = checkpoint_state["extracted_content"]
            if "metadata" in checkpoint_state:
                data.metadata = checkpoint_state["metadata"]
        
        self.context = EKSPipelineContext(
            paths=paths,
            data=data,
            parameters=parameters or {},
            config_registry=config_registry,
            schema_registry=schema_registry
        )
    
    def save_checkpoint(self, phase: str, checkpoint_path: Optional[Path] = None):
        """
        Save checkpoint state for a phase.
        
        Args:
            phase: Phase name (A, B, C, D, E)
            checkpoint_path: Optional path to save checkpoint file
        """
        if self.context:
            state = self.context.to_dict()
            self.checkpoint_states[phase] = state
            
            if checkpoint_path:
                self.context.save_checkpoint(checkpoint_path)
                self.logger.status(f"Checkpoint saved for phase {phase} to {checkpoint_path}")
    
    def rollback_to_checkpoint(self, phase: str, checkpoint_path: Optional[Path] = None) -> bool:
        """
        Rollback pipeline state to a previous checkpoint.
        
        Args:
            phase: Phase name to rollback to
            checkpoint_path: Optional path to load checkpoint from
            
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            if checkpoint_path and self.context:
                self.context = EKSPipelineContext.load_checkpoint(checkpoint_path)
                self.logger.status(f"Rolled back to checkpoint: {checkpoint_path}")
                return True
            elif phase in self.checkpoint_states:
                # Restore from in-memory checkpoint
                state = self.checkpoint_states[phase]
                self.context = EKSPipelineContext.from_dict(state)
                self.logger.status(f"Rolled back to phase {phase} checkpoint")
                return True
            else:
                self.logger.warning(f"No checkpoint found for phase {phase}")
                return False
        except Exception as e:
            self.logger.error(f"Rollback failed for phase {phase}: {e}")
            return False

    @log_depth
    def run_phase_a(self, root_dir: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        Phase A: Scan project directory and register placeholder documents.
        Enhanced with DiscoveryInput/Output contract per T1.72.

        Returns summary dict with keys:
            - discovered: count of files discovered
            - valid: count of files with recognized extensions
            - unknown: count of files with unrecognized extensions
            - registered: count of new placeholder documents registered
        """
        # T1.72: Construct DiscoveryInput contract
        inp = DiscoveryInput(
            run_id=str(getattr(self.logger, 'run_id', '')),
            data_dir=root_dir,
            config_file=Path(""),
            schema_dir=Path(""),
            output_dir=Path(""),
            parameters={"recursive": recursive},
        )
        inv = self._validate_discovery_input(inp)
        if not inv.is_valid:
            self.logger.error(f"DiscoveryInput validation failed: {inv.errors}", context="run_phase_a")
            return {"discovered": 0, "valid": 0, "unknown": 0, "registered": 0, "error": inv.errors}

        if self.use_telemetry:
            self.telemetry.start()
        
        self.logger.status(f"Phase A: Scanning {root_dir}")
        
        if self.message_manager:
            self.message_manager.show("STATUS_PHASE_A_START", phase="A", root_dir=str(root_dir))
        
        if self.context:
            self.context.update_phase("A", "IN_PROGRESS")

        discovered = self.scanner.scan(root_dir, recursive=recursive)
        valid, unknown = self.scanner.validate_file_types(discovered)
        try:
            registered = self.scanner.register_placeholders(valid, self.registry)
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("D5-REG-001", detail=f"Placeholder registration failed: {e}")
            raise

        summary = {
            "discovered": len(discovered),
            "valid": len(valid),
            "unknown": len(unknown),
            "registered": registered,
        }
        
        if self.use_telemetry:
            self.telemetry.add_checkpoint(
                phase="A",
                details=summary,
                document_count=registered
            )
            self.save_checkpoint("A")
        
        if self.context:
            self.context.state.documents_processed = registered
            self.context.update_phase("A", "COMPLETE")
        
        self.logger.status(f"Phase A complete: {summary}")
        
        if self.message_manager:
            self.message_manager.show("STATUS_PHASE_A_COMPLETE", registered=registered)
        
        # T1.72: Wrap return in DiscoveryOutput contract
        dout = DiscoveryOutput(
            run_id=inp.run_id,
            status="SUCCESS",
            discovered=summary["discovered"],
            valid=summary["valid"],
            unknown=summary["unknown"],
            registered=summary["registered"],
            files=summary.get("files", []),
            metadata={"phase": "A", "completed_at": str(datetime.now())},
        )
        if self.logger.level >= 2:
            self.logger.debug(f"DiscoveryOutput: {dout.to_dict()}", context="run_phase_a")
        return dout.to_dict()

    def _validate_discovery_input(self, inp: DiscoveryInput) -> ValidationResult:
        """Validate DiscoveryInput before processing."""
        errors = []
        if not inp.data_dir or not inp.data_dir.exists():
            errors.append(f"data_dir does not exist: {inp.data_dir}")
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    @log_depth
    def run_phase_b(self, root_dir: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        Phase B: For each discovered file, route → parse → detect → score → update.
        Enhanced with telemetry checkpoint per Appendix F.

        Returns summary dict with keys:
            - total: count of files processed
            - success: count parsed successfully
            - partial: count with partial success
            - failed: count that failed
            - results: list of per-file result dicts
        """
        self.logger.status(f"Phase B: Parsing files in {root_dir}")
        
        if self.message_manager:
            self.message_manager.show("STATUS_PHASE_B_START", phase="B", root_dir=str(root_dir))
        
        if self.context:
            self.context.update_phase("B", "IN_PROGRESS")

        discovered = self.scanner.scan(root_dir, recursive=recursive)
        valid, _ = self.scanner.validate_file_types(discovered)

        results = []
        success = 0
        partial = 0
        failed = 0

        for file_info in valid:
            file_path = file_info["file_path"]
            file_type = file_info["file_type"]
            try:
                result = self._process_file(file_path, file_type)
            except Exception as e:
                result = {"file_path": file_path, "file_type": file_type, "status": "failed", "error": str(5)}
                if self.error_manager:
                    self.error_manager.handle_system_error("S-PIP-001", detail=f"Unhandled error in _process_file for {file_path}: {e}")
                    if self.message_manager:
                        self.message_manager.show("ERROR_FILE_PROCESSING", filename=file_path, error=str(5))

            results.append(result)

            status = result.get("status", "failed")
            if status == "success":
                success += 1
            elif status == "partial":
                partial += 1
            else:
                failed += 1
                if self.error_manager:
                    self.error_manager.handle_data_error("P5-F-V-0001", doc_id=str(file_path),
                                                          detail=f"File processing failed with status: {status}")
            
            # Add telemetry checkpoint for each file processed
            if self.use_telemetry:
                self.telemetry.add_checkpoint(
                    phase=f"B-{file_path}",
                    details={"file": file_path, "status": status},
                    document_count=success + partial + failed
                )

        summary = {
            "total": len(valid),
            "success": success,
            "partial": partial,
            "failed": failed,
            "results": results,
        }
        
        if self.use_telemetry:
            self.telemetry.add_checkpoint(
                phase="B",
                details=summary,
                document_count=success + partial
            )
            self.save_checkpoint("B")
        
        if self.context:
            self.context.state.documents_processed = success + partial
            self.context.state.documents_succeeded = success
            self.context.state.documents_failed = failed
            self.context.update_phase("B", "COMPLETE")
        
        self.logger.status(f"Phase B complete: {success} success, {partial} partial, {failed} failed")
        
        if self.message_manager:
            self.message_manager.show("STATUS_PHASE_B_COMPLETE",
                                       success=success, partial=partial, failed=failed)
        
        return summary

    @log_depth
    def run_phase_c(self) -> Dict[str, Any]:
        """
        Phase C: Flag documents for manual review.
        Enhanced with telemetry checkpoint per Appendix F.
        Queries documents where extract_status != 'success' or
        extraction_confidence < 0.70.

        Returns summary dict with keys:
            - flagged: count of documents flagged
            - documents: list of flagged document metadata dicts
        """
        self.logger.status("Phase C: Flagging documents for review")
        
        if self.message_manager:
            self.message_manager.show("STATUS_PHASE_C_START", phase="C")
        
        if self.context:
            self.context.update_phase("C", "IN_PROGRESS")

        all_docs = self.registry.list_documents(latest_only=False)
        flagged = []
        for doc in all_docs:
            needs_review = False
            if doc.get("extract_status") != "success":
                needs_review = True
            conf = doc.get("extraction_confidence")
            if conf is not None and conf < 0.70:
                needs_review = True
            if needs_review:
                flagged.append(doc)

        summary = {
            "flagged": len(flagged),
            "documents": flagged,
        }
        
        if self.use_telemetry:
            self.telemetry.add_checkpoint(
                phase="C",
                details=summary,
                document_count=len(flagged)
            )
            self.save_checkpoint("C")
        
        if self.context:
            self.context.update_phase("C", "COMPLETE")
        
        self.logger.status(f"Phase C complete: {len(flagged)} documents flagged for review")
        
        if self.message_manager:
            self.message_manager.show("STATUS_PHASE_C_COMPLETE", flagged=len(flagged))
        
        return summary

    @log_depth
    def run_full_pipeline(
        self,
        root_dir: Path,
        recursive: bool = True,
        on_phase: Optional[Callable[[str], None]] = None,
        checkpoint_dir: Optional[Path] = None,
        job_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run all three phases in sequence: A → B → C.
        Enhanced with telemetry heartbeat integration per Appendix F.

        Single coordination loop for the whole pipeline. Progress and checkpoint
        callbacks (``on_phase`` / ``checkpoint_dir`` + ``job_id``) are forwarded by
        the shared ``run_pipeline`` funnel so servers keep their progress/checkpoint
        behavior (T1.99.10). Per-phase separability (R60 / Appendix F §2.3.3) is also
        available via the public ``run_phase_a/b/c`` methods.

        Args:
            root_dir: Root directory containing documents to process.
            recursive: Recurse into subdirectories.
            on_phase: Optional callback invoked with the phase letter ("A"/"B"/"C")
                after each phase completes.
            checkpoint_dir: Directory for per-phase checkpoint JSON artifacts.
            job_id: Job id used to name checkpoint files.

        Returns:
            Combined summary dict with keys phase_a / phase_b / phase_c.
        """
        self.logger.status(f"Starting full pipeline for {root_dir}")

        if self.message_manager:
            self.message_manager.show("STATUS_PIPELINE_START", root_dir=str(root_dir))

        if self.use_telemetry:
            self.telemetry.start()

        if self.context:
            self.context.state.status = "IN_PROGRESS"

        def _after(phase: str) -> None:
            if on_phase:
                on_phase(phase)
            # T1.99.85/I124: Per-phase checkpoint writes removed — unused by resume logic;
            # context held in-memory via self.checkpoint_states. Restore from git
            # history if future resume-from-checkpoint support is needed.
            # if checkpoint_dir is not None and job_id is not None:
            #     self.save_checkpoint(
            #         phase,
            #         checkpoint_path=Path(checkpoint_dir) / f"checkpoint_{job_id}_{phase}.json",
            #     )

        try:
            phase_a = self.run_phase_a(root_dir, recursive=recursive)
            _after("A")
            phase_b = self.run_phase_b(root_dir, recursive=recursive)
            _after("B")
            phase_c = self.run_phase_c()
            _after("C")

            summary = {
                "phase_a": phase_a,
                "phase_b": phase_b,
                "phase_c": phase_c,
            }

            if self.use_telemetry:
                self.telemetry.stop()

            if self.context:
                self.context.complete()

            self.logger.status("Full pipeline complete")

            if self.message_manager:
                self.message_manager.show("STATUS_PIPELINE_COMPLETE")

            return summary
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_system_error("S-PIP-002", detail=f"Pipeline failed: {e}")
            raise

    def _process_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Process a single file through the parse → detect → score pipeline.
        Wraps with ParserInput/ParserOutput contracts per T1.72.
        """
        # T1.72: Construct ParserInput contract
        pinp = ParserInput(
            run_id=str(getattr(self.logger, 'run_id', '')),
            data_dir=Path(file_path).parent,
            config_file=Path(""),
            schema_dir=Path(""),
            output_dir=Path(""),
            parameters={},
            file_path=str(file_path),
            file_type=file_type,
        )
        pout = ParserOutput(
            run_id=pinp.run_id,
            status="FAILED",
            content_blocks=[],
            metadata={},
            elements=[],
            confidence=0.0,
        )

        result = {
            "file_path": file_path,
            "file_type": file_type,
            "parse_status": "pending",
            "elements": [],
            "score": None,
            "status": "pending",
            "error": None,
        }

        try:
            parse_result = self.router.route(file_path, file_type)
            result["parse_status"] = parse_result.get("status", "failed")
            result["error"] = parse_result.get("error")

            if parse_result["status"] == "failed":
                result["status"] = "failed"
                pout.status = "FAILED"
                if self.error_manager:
                    self.error_manager.handle_data_error("P5-F-S-0002", doc_id=str(file_path),
                                                          detail=parse_result.get("error", "Parse failed"))
                self._update_doc_status(file_path, "failed", notes=result["error"])
                return result

            content_blocks = parse_result.get("content_blocks", [])
            metadata = parse_result.get("metadata", {})

            try:
                pages = self._adapt_content_for_detector(content_blocks)
                elements = self.detector.detect(file_path, pages=pages)
                result["elements"] = elements

                # T1.99.143: Extract revision_description from revision_table elements
                revision_desc = None
                for el in elements:
                    if el.get("element_type") == "revision_table" and el.get("content"):
                        # Use the first revision_table element's content as the description
                        content = el.get("content", "")
                        if isinstance(content, dict):
                            # Try common keys: description, change_summary, revision_notes
                            revision_desc = (
                                content.get("description")
                                or content.get("change_summary")
                                or content.get("revision_notes")
                                or str(content)
                            )
                        elif isinstance(content, str) and content.strip():
                            revision_desc = content.strip()
                        if revision_desc:
                            break
            except Exception as e:
                self.logger.warning(
                    f"Structure detection failed for {file_path}: {e}",
                    context="PipelineOrchestrator._process_file"
                )
                if self.error_manager:
                    self.error_manager.handle_data_error("D5-DETECT-001", doc_id=str(file_path),
                                                          detail=f"Structure detection failed: {e}")

            # T1.99.116: Use shared FilenameParser instead of inline one-liner
            parse_result = self._parser.parse(Path(file_path).name)
            doc_number = parse_result.document_number or Path(file_path).stem
            doc = self.registry.get_document(doc_number)
            if doc:
                try:
                    score = self.scorer.score(doc, elements)
                    result["score"] = score
                    pout.confidence = score.get("overall", 0.0)
                    pout.content_blocks = content_blocks
                    pout.metadata = metadata
                    pout.elements = elements

                    # T1.99.135: Extract file properties (OS stat + embedded metadata)
                    # and persist to registry via update_document_status(extra_properties=...)
                    prop_result = self._property_extractor.extract(
                        str(file_path), file_type, parser_metadata=metadata
                    )
                    registry_props = prop_result.to_registry_dict()
                    # T1.99.143: Attach revision_description from element extraction
                    if revision_desc:
                        registry_props["revision_description"] = revision_desc
                    self.logger.debug(
                        f"File properties extracted for {Path(file_path).name}: "
                        f"size={prop_result.file_size}, status={prop_result.extract_status}, "
                        f"props={len(registry_props)} fields",
                        context="PipelineOrchestrator._process_file",
                    )

                    self._update_doc_status(
                        file_path, "success",
                        confidence=score.get("overall"),
                        notes=f"Auto-parsed via pipeline",
                        extra_properties=registry_props,
                    )
                    result["status"] = "success"
                    pout.status = "SUCCESS"
                except Exception as e:
                    if self.error_manager:
                        self.error_manager.handle_data_error("D5-SCORE-001", doc_id=str(file_path),
                                                              detail=f"Health scoring failed: {e}")
                    result["status"] = "partial"
                    result["error"] = str(5)
            else:
                result["status"] = "partial"
                result["error"] = f"Document not registered: {doc_number}"
                if self.error_manager:
                    self.error_manager.handle_data_error("P5-R-P-0003", doc_id=str(file_path),
                                                          detail=f"Document not registered: {doc_number}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(5)
            pout.status = "FAILED"
            pout.errors.append(ErrorRecord("PipelineError", str(5), context={"file_path": file_path}))
            self.logger.error(
                f"Pipeline processing failed for {file_path}: {e}",
                context="PipelineOrchestrator._process_file"
            )
            if self.error_manager:
                self.error_manager.handle_system_error("S-PIP-003", detail=f"Pipeline processing failed for {file_path}: {e}")

        # T1.72: Attach pout state to result for traceability
        result["_parser_output_status"] = pout.status
        result["_parser_output_confidence"] = pout.confidence
        result["_parser_output_errors"] = [e.to_dict() for e in pout.errors]
        if self.logger.level >= 2:
            self.logger.debug(f"ParserOutput for {file_path}: status={pout.status}, errors={len(pout.errors)}",
                              context="PipelineOrchestrator._process_file")
        return result

    def _adapt_content_for_detector(self, content_blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adapt parser content blocks to the page format expected by StructureDetector.detect().
        Groups blocks by page number into page dicts with 'text', 'tables', 'images'.
        """
        pages: Dict[int, Dict[str, Any]] = {}
        for block in content_blocks:
            meta = block.get("metadata", {})
            page_num = meta.get("page", 1)
            if page_num not in pages:
                pages[page_num] = {"text": "", "tables": [], "images": []}

            block_type = block.get("type", "text")
            content = block.get("content", "")
            if block_type == "text":
                pages[page_num]["text"] += content + "\n"
            elif block_type == "table":
                pages[page_num]["tables"].append(content)
            elif block_type == "image":
                pages[page_num]["images"].append(content)

        return [pages[pn] for pn in sorted(pages.keys())] if pages else [{"text": "", "tables": [], "images": []}]

    def _update_doc_status(self, file_path: str, status: str,
                           confidence: Optional[float] = None,
                           notes: Optional[str] = None,
                           extra_properties: Optional[Dict[str, Any]] = None) -> None:
        """Update document extraction status in registry using registry.update_document_status()."""
        # T1.99.116: Use shared FilenameParser instead of inline one-liner
        parse_result = self._parser.parse(Path(file_path).name)
        doc_number = parse_result.document_number or Path(file_path).stem
        doc = self.registry.get_document(doc_number)
        if doc:
            self.registry.update_document_status(
                doc["id"], status, confidence=confidence, notes=notes,
                extra_properties=extra_properties,
            )
