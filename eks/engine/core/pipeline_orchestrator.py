"""
Pipeline Orchestrator for EKS - Coordinates Phase A/B/C pipeline workflow.
T1.39: Pre-parse → parse → score → review pipeline coordinator.
T1.63: Enhanced with checkpoints and telemetry heartbeat integration per Appendix F.
T1.64: Added phase rollback capability per Appendix F.
T1.68: Wired ErrorManager/MessageManager calls at phase boundaries and per-file failures.
T1.71: Replaced raw duckdb.connect in _update_doc_status with registry.update_document_status().

Revision: 1.1
Date: 2026-08-10
Author: opencode
Summary: 1.1: T1.256/T1.257/T1.258 (I293/I294/I295) — wired runtime GROUP 11
          persistence: _sync_batch_run insert/update at Phase A/B/C boundaries
          (batch_run stage stats), persist_batch_health stores score_batch()
          per-doc rows + aggregate (health_score/health_batch keyed on run_id),
          persist_document_references populates document_reference junction
          from references_documents JSON at Phase B end.
1.0: T1.194 (I265) — ProjectConfigurationRegistry injection per Appendix L
          caller-injection contract (D1). The orchestrator is the Phase B *caller*:
          it holds the injected registry, resolves each file's committed project
          identity, fetches the config slice, and passes project_code + slice to
          child modules (ColumnProcessor, FilePropertyExtractor, RevisionManager).
          Phase A stays project-agnostic (D2) — FileScanner auto-detects over
          registry.project_codes with no committed assignment.
0.9: T1.160 (I256) — FilenameParser now receives project_code_titles from
          SchemaLoader-injected doc_config.
          T1.161 (I256) — I252 block extended with project_title write-back:
          cover sheet metadata > code→title lookup > Phase A value.
0.8: T1.157 (I255) — FilenameParser now receives project_code_registry derived from
          filename_patterns keys (minus '*') instead of project_code=None, enabling auto-pattern
          detection.
          0.7: T1.118 (I236) — Fixed ERROR_FILE_PROCESSING kwarg mismatch:
          error=str(e) → detail=str(e) at show() call site.
          0.6: T1.116 (I235) — Folded 1.0 into BATCH_MILESTONES ({0.25, 0.50, 0.75, 1.0});
          removed separate pct>=1.0 block; all milestones flow through single
          sorted loop in correct order. last_milestone_pct now set to 1.0.
          0.5: T1.106 (I232) — _process_file() resolves doc_id once via
          registry.get_document_by_file_path() at entry; removed stem-based
          fallback (lines 721-724). _update_doc_status() requires doc_id;
          legacy path removed.
0.4: T1.100 (I227) — run_phase_b() reads file list from DuckDB instead of
          re-scanning filesystem. Added _resolve_phase_b_files() with DuckDB-first
          logic and filesystem fallback.
0.3: T1.99.179 (I212) — wired RevisionManager for revision-aware lookups.
     T1.99.180 (I216) — restored per-phase checkpoint writes for resume capability.
     T1.99.181 (I224) — wired ReviewManager persistence in Phase C (lock_document,
     recalculate_score). Phase C now persists review status instead of read-only flagging.
0.2: T1.99.85/I124 — commented out per-phase checkpoint writes in run_full_pipeline()
     _after() closure; checkpoint unused by resume logic; context held in-memory.
"""
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from ..logging.logger import EKSLogger, log_depth
from ..parsers.parser_router import ParserRouter
from .factories import EngineFactory
from .context import EKSPipelineContext, EKSPaths
from .telemetry import TelemetryHeartbeat
from .error_manager import ErrorManager
from .message_manager import MessageManager
from .io_contracts import DiscoveryInput, DiscoveryOutput, HealthInput, HealthOutput
from ..parsers.io_contracts import ParserInput, ParserOutput
from .base import ErrorRecord, ValidationResult, BaseEngine, EngineInput, EngineOutput
from .filename_parser import FilenameParser
from .file_property_parser import FilePropertyExtractor
from .revision import RevisionManager
from .review_manager import ManualReviewManager
# T1.187: Schema-driven column processor for Phase A/B/C calculated columns
from .column_processor import EKSColumnProcessor


class PipelineOrchestrator(BaseEngine):
    """
    Coordinates the 3-phase EKS pipeline with checkpoints and telemetry:
    - Phase A: Scan directory → register placeholder documents
    - Phase B: Route → parse → detect structure → score → update metadata
    - Phase C: Flag documents for manual review
    
    Enhanced per Appendix F with:
    - 5 clear phases (A-E) with telemetry heartbeat integration
    - Checkpoint state serialization for resume capability
    - Phase rollback mechanism for failed phases
    
    T1.99.182 (I209): Now inherits from BaseEngine for Appendix F §2.3.1 compliance.
    Provides standard execution flow: validate_input → execute → validate_output.
    Backward-compatible: direct constructor (config, doc_config, registry) still works
    alongside the EngineInput.run() pattern.
    """

    def __init__(self, config: Dict[str, Any], doc_config: Dict[str, Any],
                 registry: Any, logger: Optional[EKSLogger] = None,
                 use_telemetry: bool = True,
                 error_manager: Optional[ErrorManager] = None,
                 message_manager: Optional[MessageManager] = None,
                 external_telemetry: Any = None,
                 telemetry_verbose: bool = True,
                 project_config_registry: Optional[Any] = None,
                 processing_config: Optional[Dict[str, Any]] = None):
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
            external_telemetry: Optional external TelemetryHeartbeat from
                common.library.core.pipeline (T1.99.184/I215). When provided,
                pipeline-level checkpoints are forwarded to it alongside the
                local document-level telemetry.
            telemetry_verbose: Whether to emit milestone progress (25/50/75/100%)
                to console during Phase B (I237/T1.122). Default True matches
                system_parameters.telemetry_verbose schema default.
            project_config_registry: Optional injected ProjectConfigurationRegistry
                (T1.194/I265, Appendix L D1). The orchestrator is the Phase B
                *caller*: it holds the registry, resolves each file's committed
                project identity, and passes project_code + config slice to child
                modules. Child modules never hold the registry themselves.
                Falls back to doc_config dicts when None (L.14.7).
        """
        # T1.99.182 (I209): Call BaseEngine.__init__ with engine name
        super().__init__(name="PipelineOrchestrator")
        self.config = config
        self.doc_config = doc_config
        # I281 (T1.224): processing profile values SSOT (eks_processing_config.json)
        self.processing_config = processing_config or {}
        self.registry = registry
        self.logger = logger or EKSLogger("PipelineOrchestrator", level=1)
        self.use_telemetry = use_telemetry
        self.error_manager = error_manager
        self.message_manager = message_manager
        # T1.194 (I265): Injected Project Configuration Registry (Appendix L D1).
        self.project_config_registry = project_config_registry
        
        # Initialize components via factory for DI compliance (T1.99.183/I211)
        self._engine_factory = EngineFactory(config_registry=config)
        self.scanner = self._engine_factory.create(
            "FileScanner", config=config, doc_config=doc_config, logger=self.logger,
            project_config_registry=self.project_config_registry,
            processing_config=self.processing_config,
        )
        self.router = ParserRouter(
            doc_config, logger=self.logger, use_factory=True,
            runtime_slice=self._slice_for_orchestrator(),
            processing_config=self.processing_config,
        )
        # I284: schema-driven scorer. column_config + weight_tiers +
        # default_source_quality_scores come from doc_config so no scoring
        # policy is hardcoded in the engine.
        self.scorer = self._engine_factory.create(
            "HealthScorer", logger=self.logger,
            document_templates=doc_config.get("document_templates", {}),
            column_config=doc_config.get("column_processing", {}),
            weight_tiers=(doc_config.get("health_scoring") or {}).get("weight_tiers"),
            default_source_quality_scores=(doc_config.get("health_scoring") or {}).get("default_source_quality_scores"),
        )
        self.detector = self._engine_factory.create("StructureDetector", logger=self.logger)

        # T1.99.179 (I212): Wire RevisionManager for revision-aware document lookups
        self.revision_manager = RevisionManager(
            registry, logger=self.logger,
            runtime_slice=self._slice_for_orchestrator(),
        )

        # T1.99.181 (I224): Wire ReviewManager for Phase C persistence
        self.review_manager = ManualReviewManager(
            registry, doc_config=doc_config, logger=self.logger
        )

        # T1.187: Schema-driven column processor — dispatches calculated columns
        # by processing_phase (A/B/C) via registered handler functions.
        # Gracefully handles doc_configs without column_processing section.
        # T1.194 (I265): Runtime slice is injected so handlers can consult
        # project-specific resolved configuration (Appendix L D1).
        try:
            self._column_processor = EKSColumnProcessor.from_doc_config(
                doc_config, runtime_slice=self._slice_for_orchestrator(),
                processing_config=self.processing_config,
            )
        except Exception:
            self._column_processor = None
            self.logger.debug(
                "ColumnProcessor not available — doc_config missing 'column_processing'",
                context="PipelineOrchestrator.__init__",
            )

        # T1.157 (I255): Shared FilenameParser — auto-detects project code per filename
        # T1.160 (I256): project_code_titles derived from project_code_schema injected by SchemaLoader
        # T1.194 (I265): When a ProjectConfigurationRegistry is injected, the
        # project_code_registry and project_code_titles come from the registry
        # (mirrors FileScanner, keeping the two callers in sync).
        filename_patterns = doc_config.get("filename_patterns", {})
        # I279 (T1.213): flat document_type_registry derived from the three-section
        # carrier by SchemaLoader; document_templates sourced the same way.
        document_type_registry = doc_config.get("document_type_registry", [])
        if self.project_config_registry is not None:
            project_code_registry = list(self.project_config_registry.project_codes)
            project_code_titles = self._registry_code_titles(doc_config.get("project_code_titles", {}))
        else:
            project_code_registry = [k for k in filename_patterns if k != "*"]
            project_code_titles = doc_config.get("project_code_titles", {})
        self._parser = FilenameParser(
            filename_patterns=filename_patterns,
            project_code_registry=project_code_registry,
            project_code_titles=project_code_titles,
            document_type_registry=document_type_registry,
        )

        # T1.99.134: FilePropertyExtractor for Phase B property extraction (Appendix J)
        # I287 (T1.242): file_property config single-sourced in
        # eks_processing_config.json — os_properties (top-level) + 
        # file_property_profiles (bound to extraction_profiles). The legacy
        # doc_config file_property_patterns section is retired (T1.241).
        file_property_patterns = self._build_file_property_config()
        self._property_extractor = FilePropertyExtractor(
            file_property_patterns=file_property_patterns,
            logger=self.logger,
            runtime_slice=self._slice_for_orchestrator(),
        )
        
        # T1.99.184 (I215): Unify dual telemetry — local TelemetryHeartbeat for
        # document-level detail, optional external_telemetry for pipeline-level
        # checkpoints forwarded to common.library.core.pipeline.TelemetryHeartbeat.
        self.telemetry = TelemetryHeartbeat(enabled=use_telemetry, verbose=telemetry_verbose)
        self.external_telemetry = external_telemetry
        
        # Initialize pipeline context
        self.context: Optional[EKSPipelineContext] = None
        self.checkpoint_states: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # T1.194 (I265): Project Configuration slice resolution — Appendix L D1
    # ------------------------------------------------------------------

    def _registry_code_titles(self, doc_config_titles: Dict[str, str]) -> Dict[str, str]:
        """Build code → title map from the Project Configuration Registry.

        Registry project names (from Project Definition ``project_identity``)
        are authoritative; doc_config titles fill any gaps. Mirrors
        ``FileScanner._registry_code_titles()`` so both callers agree.
        """
        titles = dict(doc_config_titles or {})
        if self.project_config_registry is None:
            return titles
        for code in self.project_config_registry.project_codes:
            cfg = self.project_config_registry.get(code)
            if cfg is not None:
                title = getattr(getattr(cfg, "project", None), "project_name", None)
                if title:
                    titles[code] = title
        return titles

    def _build_file_property_config(self) -> Dict[str, Any]:
        """Build the FilePropertyExtractor config from eks_processing_config.json.

        I287 (T1.242): file property rules single-sourced in
        eks_processing_config.json — ``os_properties`` (top-level) + 
        ``file_property_profiles`` (keyed by profile, bound to extraction
        profiles). The legacy doc_config ``file_property_patterns`` section is
        retired (T1.241); this adapter projects the processing config into the
        extractor's ``{os_properties, by_file_type}`` shape so the extractor's
        L.14.7 backward-compatible contract is preserved.
        """
        pc = self.processing_config or {}
        os_cfg = pc.get("os_properties", {})
        by_type: Dict[str, Dict[str, Any]] = {}
        extraction_profiles = pc.get("extraction_profiles", {})
        for profile in pc.get("file_property_profiles", {}).values():
            if not isinstance(profile, dict):
                continue
            method = "os_only"
            bound = profile.get("bound_extraction_profile")
            bound_profile = extraction_profiles.get(bound, {}) if bound else {}
            methods = bound_profile.get("extraction_methods", [])
            if "parser_metadata" in methods:
                method = "parser_metadata"
            for ext in profile.get("supported_extensions", []):
                by_type[ext] = {
                    "enabled": True,
                    "extraction_method": method,
                    "property_mapping": profile.get("property_mapping", []),
                }
        return {"os_properties": os_cfg or {}, "by_file_type": by_type}

    def _slice_for_orchestrator(self) -> Dict[str, Any]:
        """Return the init-time default config slice for orchestrator children.

        With a single registered project, the Pipeline slice is known at
        construction time. With zero or multiple projects the per-file project
        identity is not yet established, so an empty slice is returned and child
        modules fall back to doc_config dicts (L.14.7).
        """
        if self.project_config_registry is not None and len(self.project_config_registry) == 1:
            code = self.project_config_registry.project_codes[0]
            cfg = self.project_config_registry.get(code)
            if cfg is not None:
                return cfg.slice_for("Pipeline")
        return {}

    def _resolve_project_context(self, project_code: Optional[str]) -> Dict[str, Any]:
        """Resolve the config slice for a file's committed project identity.

        Phase B committed identity (D1): the orchestrator looks up the project
        code in the injected registry and fetches the slice. Returns
        ``{"project_code": ..., "config_slice": {...}}``. When the code is
        missing or the registry is absent, both fall back to None / {} so child
        modules degrade to doc_config dicts (L.14.7).
        """
        ctx: Dict[str, Any] = {"project_code": None, "config_slice": {}}
        if not project_code:
            return ctx
        if self.project_config_registry is not None and project_code in self.project_config_registry:
            cfg = self.project_config_registry.get(project_code)
            if cfg is not None:
                ctx["project_code"] = project_code
                ctx["config_slice"] = cfg.slice_for("Pipeline")
        return ctx

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
    
    def _forward_telemetry(self, phase: str, details: dict, doc_count: int = 0):
        """T1.99.184 (I215): Forward checkpoint to both local and external telemetry."""
        self.telemetry.add_checkpoint(phase=phase, details=details, document_count=doc_count)
        if self.external_telemetry is not None:
            try:
                self.external_telemetry.add_checkpoint(
                    phase=phase, details=details, document_count=doc_count,
                )
            except Exception:
                pass  # External telemetry failure must not block the pipeline

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
    def _batch_run_id(self) -> str:
        """
        Resolve the current batch_run run_id (I293/T1.256).

        Priority: self.logger.run_id (set by the phase server to the job UUID)
        > a uuid persisted on this orchestrator instance for the run. Returns
        an empty string when no run context exists (unit-level scoring only).
        """
        return str(getattr(self.logger, 'run_id', '') or '')

    @log_depth
    def _sync_batch_run(self, phase: str, summary: Dict[str, Any]) -> None:
        """
        Update the batch_run row with phase-boundary stage statistics (I293).

        Called after each phase summary is computed. Inserts the row on the
        first call for the run (Phase A registered count) then updates stage
        stats at each boundary. Never raises — failures are logged so batch
        tracking never breaks the pipeline.
        """
        run_id = self._batch_run_id()
        if not run_id:
            self.logger.warning(
                "batch_run sync skipped — no run_id on logger (pipeline not "
                "invoked via phase server)",
                context="PipelineOrchestrator._sync_batch_run",
            )
            return
        try:
            if self.registry.get_batch(run_id) is None:
                self.registry.insert_batch(
                    run_id,
                    data_dir=str(getattr(self, '_last_root_dir', '') or ''),
                    status="running",
                )
            if phase == "A":
                self.registry.update_batch(
                    run_id, current_stage="A",
                    phase_a_discovered=summary.get("discovered", 0),
                    phase_a_valid=summary.get("valid", 0),
                )
            elif phase == "B":
                self.registry.update_batch(
                    run_id, current_stage="B",
                    phase_b_total=summary.get("total", 0),
                    phase_b_success=summary.get("success", 0),
                    phase_b_failed=summary.get("failed", 0),
                )
            elif phase == "C":
                self.registry.update_batch(
                    run_id, current_stage="complete",
                    phase_c_flagged=summary.get("flagged", 0),
                    status="success",
                )
        except Exception as e:
            self.logger.warning(
                f"batch_run sync failed for phase {phase}: {e}",
                context="PipelineOrchestrator._sync_batch_run",
            )

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
        self._last_root_dir = root_dir
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
            # T1.187: Process Phase A calculated columns through ColumnProcessor.
            # Currently handles filename_segment columns (document_number, project_number,
            # area, discipline, document_type, sequence_number, revision) which are already
            # populated by the scanner — the ColumnProcessor pass ensures schema-driven
            # consistency and automatically picks up any future Phase A calculated columns.
            docs = self.registry.list_documents(latest_only=False)
            if self._column_processor:
                for doc_row in docs:
                    data = dict(doc_row)
                    self._column_processor.process("A", data, {})
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_data_error("P1-D-P-0003", detail=f"Placeholder registration failed: {e}")
            raise

        summary = {
            "discovered": len(discovered),
            "valid": len(valid),
            "unknown": len(unknown),
            "registered": registered,
        }
        
        # T1.256 (I293): record Phase A boundary stats in batch_run
        self._sync_batch_run("A", summary)
        
        if self.use_telemetry:
            self._forward_telemetry("A", details=summary, doc_count=registered)
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

        I227: Reads file list from DuckDB (written by Phase A) instead of
        re-scanning the filesystem. Falls back to filesystem scan if the
        registry is empty.

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

        # I227: Read file list from DuckDB (Phase A output) — avoids redundant filesystem walk
        valid = self._resolve_phase_b_files(root_dir, recursive)

        results = []
        success = 0
        partial = 0
        failed = 0
        total = len(valid)
        # I229: Batch telemetry milestones at 25%/50%/75%/100%
        BATCH_MILESTONES = {0.25, 0.50, 0.75, 1.0}
        last_milestone_pct = 0.0

        for idx, file_info in enumerate(valid):
            file_path = file_info["file_path"]
            file_type = file_info["file_type"]
            try:
                result = self._process_file(file_path, file_type)
            except Exception as e:
                result = {"file_path": file_path, "file_type": file_type, "status": "failed", "error": str(e)}
                if self.error_manager:
                    self.error_manager.handle_system_error("S-R-S-0407", detail=f"Unhandled error in _process_file for {file_path}: {e}")
                    if self.message_manager:
                        self.message_manager.show("ERROR_FILE_PROCESSING", filename=file_path, detail=str(e))

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
            
            # I229: Batch-level telemetry — emit checkpoints at 25%/50%/75%/100%,
            # not per-file. Per-file errors still logged via ErrorManager.
            if self.use_telemetry and total > 0:
                pct = (idx + 1) / total
                for m in sorted(BATCH_MILESTONES):
                    if last_milestone_pct < m <= pct:
                        label = "100%" if m == 1.0 else f"{int(m*100)}%"
                        files = idx + 1 if m == 1.0 else int(total * m)
                        self._forward_telemetry(
                            "B-progress", details={"milestone": label, "files": files},
                            doc_count=files,
                        )
                        last_milestone_pct = m

        summary = {
            "total": len(valid),
            "success": success,
            "partial": partial,
            "failed": failed,
            "results": results,
        }

        # I248: Compute batch health summary from registry
        try:
            all_docs = self.registry.list_documents(latest_only=False)
            batch_health = self.scorer.score_batch(all_docs)
            summary["avg_document_health"] = batch_health["avg_document_health"]
            summary["batch_health"] = batch_health
            # T1.257 (I294): Persist per-document health rows + batch aggregate.
            # score_batch() now returns doc_scores carrying the documents.id UUID;
            # rows are written keyed on run_id so multiple runs stay isolated.
            run_id = self._batch_run_id()
            if run_id and batch_health.get("doc_scores"):
                doc_scores = self.persist_batch_health(run_id, batch_health)
                summary["health_docs_persisted"] = doc_scores
        except Exception as e:
            self.logger.warning(f"Batch health scoring failed: {e}", context="run_phase_b")

        # T1.258 (I295): populate document_reference junction from the
        # references_documents JSON column (extracted during Phase B parsing).
        try:
            refs_stored = self.persist_document_references()
            summary["document_references"] = refs_stored
        except Exception as e:
            self.logger.warning(
                f"document_reference population failed: {e}",
                context="run_phase_b",
            )

        # T1.256 (I293): record Phase B boundary stats in batch_run
        self._sync_batch_run("B", summary)
        
        if self.use_telemetry:
            self._forward_telemetry("B", details=summary, doc_count=success + partial)
            self.save_checkpoint("B")
        
        if self.context:
            self.context.state.documents_processed = success + partial
            self.context.state.documents_succeeded = success
            self.context.state.documents_failed = failed
            self.context.update_phase("B", "COMPLETE")
        
        self.logger.status(f"Phase B complete: {success} success, {partial} partial, {failed} failed")
        
        if self.message_manager:
            self.message_manager.show("STATUS_PHASE_B_COMPLETE",
                                       success=success, total=total, partial=partial, failed=failed)
        
        return summary

    @log_depth
    def run_phase_c(self) -> Dict[str, Any]:
        """
        Phase C: Flag documents for manual review and persist review status.
        Enhanced with telemetry checkpoint per Appendix F.
        Queries documents where extract_status != 'success' or
        extraction_confidence < 0.70.
        
        T1.99.181 (I224): Now calls ManualReviewManager to persist review
        status via recalculate_score + lock_document for clean docs,
        rather than only read-only flagging.

        Returns summary dict with keys:
            - flagged: count of documents flagged
            - reviewed: count of documents reviewed/locked
            - documents: list of flagged document metadata dicts
        """
        self.logger.status("Phase C: Flagging documents for review")
        
        if self.message_manager:
            self.message_manager.show("STATUS_PHASE_C_START", phase="C")
        
        if self.context:
            self.context.update_phase("C", "IN_PROGRESS")

        # T1.99.181 (I224): Use review_manager for consistent review logic
        flagged = self.review_manager.get_flagged_documents(confidence_threshold=0.70)
        reviewed = 0

        # Auto-approve clean documents (extract_status == 'success' and confidence >= 0.70)
        all_docs = self.registry.list_documents(latest_only=False)
        for doc in all_docs:
            if (
                doc.get("extract_status") == "success"
                and (doc.get("extraction_confidence") or 0) >= 0.70
            ):
                try:
                    self.review_manager.recalculate_score(doc["id"])
                    reviewed += 1
                except Exception as e:
                    self.logger.warning(
                        f"Review score recalc failed for {doc.get('id')}: {e}",
                        context="PipelineOrchestrator.run_phase_c",
                    )

        # T1.187: Process Phase C calculated columns through ColumnProcessor.
        # Currently no processing_phase "C" columns exist in the config, but
        # this wiring ensures schema-driven review flag columns are automatically
        # processed when added in future iterations.
        if self._column_processor:
            for doc in all_docs:
                data = dict(doc)
                self._column_processor.process("C", data, {})

        summary = {
            "flagged": len(flagged),
            "reviewed": reviewed,
            "documents": flagged,
        }
        
        # T1.256 (I293): record Phase C boundary stats + finalize batch_run
        self._sync_batch_run("C", summary)
        
        if self.use_telemetry:
            self._forward_telemetry("C", details=summary, doc_count=len(flagged))
            self.save_checkpoint("C")
        
        if self.context:
            self.context.update_phase("C", "COMPLETE")
        
        self.logger.status(
            f"Phase C complete: {len(flagged)} flagged, {reviewed} reviewed"
        )
        
        if self.message_manager:
            self.message_manager.show(
                "STATUS_PHASE_C_COMPLETE",
                flagged=len(flagged), reviewed=reviewed,
            )
        
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
            # T1.99.180 (I216): Restore per-phase checkpoint writes for resume capability.
            if checkpoint_dir is not None and job_id is not None:
                self.save_checkpoint(
                    phase,
                    checkpoint_path=Path(checkpoint_dir) / f"checkpoint_{job_id}_{phase}.json",
                )
            # I298 (T1.261): persist checkpoint snapshot to DB alongside filesystem JSON
            if job_id is not None and self.registry:
                try:
                    state_json = self._serialize_pipeline_state(phase)
                    self.registry.insert_checkpoint(job_id, phase, state_json)
                except Exception as e:
                    self.logger.warning(
                        f"DB checkpoint write failed (non-fatal): {e}",
                        context="run_full_pipeline._after",
                    )

        try:
            phase_a = self.run_phase_a(root_dir, recursive=recursive)
            _after("A")

            # I230: validate A→B transition
            ab_gate = self.validate_phase_transition("A", "B")
            if not ab_gate["passed"]:
                self.logger.warning(
                    f"Phase A→B transition warnings: {ab_gate['warnings']}; errors: {ab_gate['errors']}",
                    context="run_full_pipeline",
                )

            phase_b = self.run_phase_b(root_dir, recursive=recursive)
            _after("B")

            # I230: validate B→C transition
            bc_gate = self.validate_phase_transition("B", "C")
            if not bc_gate["passed"]:
                self.logger.warning(
                    f"Phase B→C transition warnings: {bc_gate['warnings']}; errors: {bc_gate['errors']}",
                    context="run_full_pipeline",
                )

            phase_c = self.run_phase_c()
            _after("C")

            summary = {
                "phase_a": phase_a,
                "phase_b": phase_b,
                "phase_c": phase_c,
                "gates": {"A_B": ab_gate, "B_C": bc_gate},
            }

            if self.use_telemetry:
                self.telemetry.stop()

            if self.context:
                self.context.complete()

            self.logger.status("Full pipeline complete")

            if self.message_manager:
                self.message_manager.show("STATUS_PIPELINE_COMPLETE")

            # I299 (T1.262): flush pipeline event log to DB at completion
            if job_id is not None and self.registry:
                try:
                    events = self._collect_pipeline_events(
                        job_id, {"phase_a": phase_a, "phase_b": phase_b, "phase_c": phase_c}
                    )
                    self.registry.insert_events(job_id, events)
                except Exception as e:
                    self.logger.warning(
                        f"DB event log flush failed (non-fatal): {e}",
                        context="run_full_pipeline",
                    )

            return summary
        except Exception as e:
            if self.error_manager:
                self.error_manager.handle_system_error("S-R-S-0408", detail=f"Pipeline failed: {e}")
            raise

    def _serialize_pipeline_state(self, phase: str) -> str:
        """
        I298 (T1.261): serialise current pipeline context state to JSON for DB
        checkpoint persistence. Captures the context state if available, otherwise
        a minimal phase snapshot.
        """
        import json as _json
        state = {"phase": phase, "timestamp": datetime.now().isoformat()}
        if self.context and hasattr(self.context, 'state'):
            state["status"] = str(getattr(self.context.state, 'status', 'IN_PROGRESS'))
        try:
            return _json.dumps(state, default=str)
        except Exception:
            return _json.dumps(state)

    def _collect_pipeline_events(self, job_id: str,
                                  summary: dict) -> list:
        """
        I299 (T1.262): collect structured pipeline run-level events for DB
        persistence. Captures phase outcomes and gate results.
        """
        ts = datetime.now().isoformat()
        events = [
            {
                "timestamp": ts, "level": "INFO", "category": "pipeline",
                "context": job_id, "module": "pipeline_orchestrator",
                "message": "Pipeline completed successfully",
            },
        ]
        for p in ("phase_a", "phase_b", "phase_c"):
            if p in summary:
                events.append({
                    "timestamp": ts, "level": "INFO", "category": p,
                    "context": job_id, "module": "pipeline_orchestrator",
                    "message": f"{p} result: {summary[p]}",
                })
        return events

    @log_depth
    def _resolve_phase_b_files(self, root_dir: Path, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Resolve the file list for Phase B processing.
        
        I227: Primary path reads from DuckDB (Phase A output). Falls back to
        filesystem scan if the registry is empty.
        
        Returns a list of file_info dicts with at minimum 'file_path' and 'file_type' keys.
        """
        rows = self.registry.list_documents(latest_only=False)
        if rows:
            valid = [
                {
                    "file_path": r["file_path"],
                    # T1.197 (I253 regression): derive file_type from the file
                    # extension when the stored value is NULL/empty — repairs
                    # rows registered under the static-fallback allowlist that
                    # dropped file_type (e.g. CLI runs from a non-root CWD).
                    "file_type": r.get("file_type") or Path(r["file_path"]).suffix.lstrip(".").lower(),
                    "file_name": Path(r["file_path"]).name,
                }
                for r in rows
                if r.get("file_path")
            ]
            self.logger.info(
                f"Phase B: Loaded {len(valid)} files from registry (I227) — "
                f"skipping filesystem scan",
                context="run_phase_b",
            )
            return valid

        self.logger.warning(
            "Phase B: Registry returned no documents — falling back to filesystem scan",
            context="run_phase_b",
        )
        discovered = self.scanner.scan(root_dir, recursive=recursive)
        valid, _ = self.scanner.validate_file_types(discovered)
        return valid

    @log_depth
    def validate_phase_transition(self, from_phase: str, to_phase: str) -> Dict[str, Any]:
        """I230: Validate pre-conditions before transitioning between phases.

        Returns dict with keys:
            - passed: bool
            - warnings: list[str]
            - errors: list[str]
        """
        warnings: List[str] = []
        errors: List[str] = []

        if from_phase == "A" and to_phase == "B":
            docs = self.registry.list_documents(latest_only=False)
            if not docs:
                errors.append("Phase A→B: registry has zero documents — nothing to process")
            if docs and not any(d.get("file_path") for d in docs):
                errors.append("Phase A→B: all registered documents lack file_path")

        elif from_phase == "B" and to_phase == "C":
            flagged = self.review_manager.get_flagged_documents(confidence_threshold=0.70)
            all_docs = self.registry.list_documents(latest_only=False)
            scored = [d for d in all_docs if d.get("extraction_confidence") is not None]
            if not scored:
                errors.append("Phase B→C: no documents have extraction scores")
            if not all_docs:
                errors.append("Phase B→C: registry is empty")

        passed = len(errors) == 0
        if not passed:
            for e in errors:
                self.logger.error(f"Phase transition {from_phase}→{to_phase} failed: {e}",
                                  context="PipelineOrchestrator.validate_phase_transition")
            if self.error_manager:
                for e in errors:
                    self.error_manager.handle_data_error("P5-F-V-0001", doc_id=f"{from_phase}→{to_phase}", detail=e)

        return {"passed": passed, "warnings": warnings, "errors": errors}

    @log_depth
    def _process_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Process a single file through the parse → detect → score pipeline.
        Wraps with ParserInput/ParserOutput contracts per T1.72.

        T1.99.188 (I218): Uses context paths for config_file/schema_dir/output_dir
        defaults instead of empty Path("").
        T1.99.189 (I219): Writes extracted_content to context.data.extracted_content.
        """
        # T1.99.188 (I218): Resolve ParserInput defaults from context when available
        _config_file = self.context.paths.config_dir if self.context else Path(".")
        _schema_dir = self.context.paths.schema_dir if self.context else Path(".")
        _output_dir = self.context.paths.output_dir if self.context else Path(".")
        pinp = ParserInput(
            run_id=str(getattr(self.logger, 'run_id', '')),
            data_dir=Path(file_path).parent,
            config_file=_config_file,
            schema_dir=_schema_dir,
            output_dir=_output_dir,
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

        # T1.106 (I232): Resolve doc_id once via file_path lookup (SSOT from Phase A).
        # Avoids filename-parse divergence between _process_file and _update_doc_status.
        doc = self.registry.get_document_by_file_path(file_path)
        doc_id = doc["id"] if doc else None

        # T1.194 (I265): Phase B committed project identity — resolve the config
        # slice from the injected ProjectConfigurationRegistry (Appendix L D1).
        # project_number written by Phase A (or later parser metadata) is the
        # authoritative key. Falls back to empty slice when unresolved.
        project_context = self._resolve_project_context(
            doc.get("project_number") if doc else None
        )

        try:
            # I276 (T1.207): pass the project-local document_type so the router
            # can resolve the binding parsing profile (two-axis routing) with
            # file-type-only fallback. doc_type from the registry (Phase A) or
            # the filename-derived value when not yet committed.
            route_doc_type = (doc or {}).get("document_type") or None
            parse_result = self.router.route(file_path, file_type, document_type=route_doc_type)
            result["parse_status"] = parse_result.get("status", "failed")
            result["error"] = parse_result.get("error")

            if parse_result["status"] == "failed":
                result["status"] = "failed"
                pout.status = "FAILED"
                if self.error_manager:
                    self.error_manager.handle_data_error("P5-F-S-0002", doc_id=str(file_path),
                                                          detail=parse_result.get("error", "Parse failed"))
                self._update_doc_status(file_path, "failed", doc_id, notes=result["error"])
                return result

            content_blocks = parse_result.get("content_blocks", [])
            metadata = parse_result.get("metadata", {})

            # I278 (T1.211) / I283 (T1.230): resolve the binding template's
            # cover_type schema-first so a no-cover (C) document skips
            # cover-page detection and discards cover_page_element from the
            # admitted extraction methods. cover_type is None when the schema
            # value is unavailable — content detection falls back. Also resolve
            # the template expected_elements set (element-set SSOT) to gate
            # every StructureDetector sub-detector (four-level model).
            cover_type = None
            expected_element_types = None
            if self._column_processor:
                cover_type = self._column_processor.resolve_cover_type(route_doc_type)
                expected_element_types = self._column_processor.resolve_expected_element_types(route_doc_type)

            try:
                pages = self._adapt_content_for_detector(content_blocks)
                elements = self.detector.detect(
                    file_path, pages=pages,
                    skip_cover_page=(cover_type == "C"),
                    expected_element_types=expected_element_types,
                    cover_type=cover_type,
                )
                result["elements"] = elements

                # T1.187: Extract revision_description from revision_table elements.
                # asset_tags and project_title are now calculated by ColumnProcessor.process("B")
                # using the full elements list which is passed via the context dict.
                revision_desc = None
                for el in elements:
                    if el.get("element_type") == "revision_table" and el.get("content"):
                        content = el.get("content", "")
                        if isinstance(content, dict):
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
                    self.error_manager.handle_data_error("P3-E-E-0018", doc_id=str(file_path),
                                                          detail=f"Structure detection failed: {e}")

            # T1.106 (I232): doc already resolved at top of _process_file via
            # registry.get_document_by_file_path(). No stem-based fallback needed.
            # T1.99.161 (I196): Persist detected structural elements to
            # document_elements table per Appendix B §B6.2.  This was always
            # detected but never stored before — a blocking gap since Phase 1.
            if doc and elements:
                try:
                    self.registry.store_elements(doc["id"], elements)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to store elements for {file_path}: {e}",
                        context="PipelineOrchestrator._process_file"
                    )
            if doc:
                try:
                    # T1.99.199 (I214): Use HealthInput/HealthOutput contract wrapper.
                    # I283 (T1.230): cover_type wired into HealthInput so health
                    # scoring (I284) uses the schema-first cover type.
                    # I284: resolve class_id + template_id from the flat registry
                    # so the scorer applies type-aware tiers and template-scoped
                    # source quality.
                    score_class_id = None
                    score_template_id = None
                    if self._column_processor:
                        scope = self._column_processor.resolve_scope(route_doc_type)
                        score_class_id = scope.get("class_id")
                        for _entry in self.doc_config.get("document_type_registry", []):
                            if _entry.get("code") == route_doc_type:
                                score_template_id = _entry.get("template")
                                break
                    health_input = HealthInput(
                        run_id=str(getattr(self.logger, 'run_id', '')),
                        data_dir=Path(file_path).parent,
                        config_file=_config_file,
                        schema_dir=_schema_dir,
                        output_dir=_output_dir,
                        parameters={},
                        document=doc,
                        elements=elements or [],
                        cover_type=cover_type,
                        class_id=score_class_id,
                        template_id=score_template_id,
                    )
                    hout = self.scorer.score_from_input(health_input)
                    score = hout.metadata
                    score["overall"] = hout.overall
                    result["score"] = score
                    # T1.99.168 (I201): Apply health impact penalty from accumulated
                    # error severity impacts (GAP-D7).  ErrorManager.get_health_impact()
                    # sums health_score_impact values across all errors logged for this
                    # doc_id.  Formula: adjusted = max(0.0, raw + penalty / 100).
                    if self.error_manager:
                        penalty = self.error_manager.get_health_impact(doc["id"])
                        adjusted = max(0.0, score.get("health_score", 0.0) + penalty / 100.0)
                        score["health_score"] = round(adjusted, 4)
                        score["health_impact_penalty"] = penalty
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
                    # I252: Extract identity fields from parser metadata and write back to DB.
                    # These may come from cover sheet extraction (PDF metadata) or filename parsing.
                    # Priority for document_type: parser metadata > Phase A value (filename) > extension inference.
                    for id_field in ("project_number", "area", "discipline", "document_type"):
                        meta_val = metadata.get(id_field)
                        if meta_val:
                            if id_field == "document_type":
                                # Document_type priority: cover sheet > filename > extension
                                existing_val = doc.get(id_field) if doc else None
                                if existing_val and existing_val != meta_val and existing_val not in ("UNKNOWN", None):
                                    continue  # keep Phase A filename-derived value over parser guess
                            registry_props[id_field] = meta_val
                    # T1.187: Let schema-driven ColumnProcessor handle all calculated
                    # Phase B columns (project_title priority chain, asset_tags from cover
                    # page, document_title, total_sheets) using the full pipeline context.
                    # The context carries metadata, elements, file_properties, and score
                    # so each handler can resolve its value independently.
                    if self._column_processor:
                        # I275/I282: resolve the document-class scope (class_id +
                        # format_category from the I279 carrier projection) so the
                        # column processor can apply applies_to_document_types /
                        # native_only filters. Priority: Phase B committed value,
                        # then Phase A registry value.
                        doc_type_scope = self._column_processor.resolve_scope(
                            registry_props.get("document_type")
                            or (doc or {}).get("document_type")
                        )
                        # I277: resolve the extraction-method capability set for
                        # this document so the processor gates parser_metadata /
                        # cover_page_element by profile extraction_methods ∩
                        # format_category.
                        extraction_methods = self._column_processor.resolve_extraction_methods(
                            registry_props.get("document_type")
                            or (doc or {}).get("document_type"),
                            doc_type_scope.get("format_category"),
                        )
                        self._column_processor.process("B", registry_props, {
                            "metadata": metadata,
                            "elements": elements,
                            "file_properties": dict(registry_props),
                            "project_code_titles": self._registry_code_titles(
                                self.doc_config.get("project_code_titles", {})
                            ),
                            "score": score,
                            # T1.194 (I265): Phase B committed identity + slice
                            "project_code": project_context.get("project_code"),
                            "config_slice": project_context.get("config_slice"),
                            # I275/I282: document-class scope for the column filter
                            "class_id": doc_type_scope.get("class_id"),
                            "format_category": doc_type_scope.get("format_category"),
                            # I277: extraction-method capability set for the gate
                            "extraction_methods": extraction_methods,
                        })
                    self.logger.debug(
                        f"File properties extracted for {Path(file_path).name}: "
                        f"size={prop_result.file_size}, status={prop_result.extract_status}, "
                        f"props={len(registry_props)} fields",
                        context="PipelineOrchestrator._process_file",
                    )

                    # T1.99.189 (I219): Write extracted_content to pipeline context
                    if self.context:
                        self.context.data.extracted_content[doc["id"]] = {
                            "content_blocks": content_blocks,
                            "metadata": metadata,
                            "elements": elements,
                            "score": score,
                            "properties": registry_props,
                        }

                    self._update_doc_status(
                        file_path, "success",
                        confidence=score.get("overall"),
                        notes=f"Auto-parsed via pipeline",
                        extra_properties=registry_props,
                        doc_id=doc["id"],
                    )

                    # T1.99.179 (I212): Verify supersession chain after successful parse.
                    # Use parsed revision from metadata if available (more accurate than
                    # Phase A filename-based revision), otherwise fall back to Phase A value.
                    parsed_revision = metadata.get("revision") or doc.get("revision", "00")
                    self.revision_manager.detect_supersession(
                        doc["document_number"],
                        parsed_revision,
                        # T1.194 (I265): Pass the file's committed config slice so
                        # revision-scheme awareness can be applied (Appendix L D1).
                        runtime_slice=project_context.get("config_slice"),
                    )

                    result["status"] = "success"
                    pout.status = "SUCCESS"
                except Exception as e:
                    if self.error_manager:
                        self.error_manager.handle_data_error("P3-E-E-0019", doc_id=str(file_path),
                                                              detail=f"Health scoring failed: {e}")
                    result["status"] = "partial"
                    result["error"] = str(e)
            else:
                result["status"] = "partial"
                result["error"] = f"Document not registered: {doc_number}"
                if self.error_manager:
                    self.error_manager.handle_data_error("P5-R-P-0003", doc_id=str(file_path),
                                                          detail=f"Document not registered: {doc_number}")

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            pout.status = "FAILED"
            pout.errors.append(ErrorRecord("PipelineError", str(e), context={"file_path": file_path}))
            if self.message_manager:
                self.message_manager.show("ERROR_FILE_PROCESSING", filename=file_path, detail=str(e))
            if self.error_manager:
                self.error_manager.handle_system_error("S-R-S-0409", detail=f"Pipeline processing failed for {file_path}: {e}")

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

    @log_depth
    def persist_batch_health(self, run_id: str, batch_health: Dict[str, Any]) -> int:
        """
        Persist a health_batch aggregate + per-document health_score rows (I294).

        Consumes the per-doc rows produced by ``HealthScorer.score_batch()``
        (each carrying the registry documents.id UUID) and the aggregate dict.
        Returns the number of per-document rows persisted.
        """
        persisted = 0
        for srow in batch_health.get("doc_scores", []):
            document_id = srow.get("document_id")
            if not document_id:
                continue
            try:
                self.registry.store_health_score(run_id, document_id, srow)
                persisted += 1
            except Exception as e:
                self.logger.warning(
                    f"Failed to persist health score for doc {document_id}: {e}",
                    context="PipelineOrchestrator.persist_batch_health",
                )
        try:
            self.registry.store_health_batch(run_id, batch_health)
        except Exception as e:
            self.logger.warning(
                f"Failed to persist health batch aggregate: {e}",
                context="PipelineOrchestrator.persist_batch_health",
            )
        self.logger.info(
            f"Persisted {persisted} health score row(s) + batch aggregate for run {run_id}",
            context="PipelineOrchestrator.persist_batch_health",
        )
        return persisted

    @log_depth
    def persist_document_references(self) -> int:
        """
        Populate the document_reference junction from the references_documents
        JSON column at Phase B end (I295).

        Each references_documents entry references another document by
        document_number → resolved to the target document's UUID id and stored
        as a ``references`` relation. Returns the number of junction rows stored.
        """
        import json as _json
        stored = 0
        all_docs = self.registry.list_documents(latest_only=False)
        # Build document_number → UUID lookup so references resolve reliably.
        doc_by_number: Dict[str, str] = {}
        for row in all_docs:
            num = row.get("document_number")
            if num and row.get("id"):
                doc_by_number.setdefault(str(num), str(row["id"]))

        for source_doc in all_docs:
            source_id = str(source_doc.get("id") or "")
            if not source_id:
                continue
            refs_raw = source_doc.get("references_documents")
            if not refs_raw:
                continue
            if isinstance(refs_raw, str):
                try:
                    refs = _json.loads(refs_raw)
                except Exception:
                    refs = []
            elif isinstance(refs_raw, list):
                refs = refs_raw
            else:
                refs = []
            if not isinstance(refs, list):
                continue
            for ref in refs:
                if not ref:
                    continue
                target_id = doc_by_number.get(str(ref).strip())
                if not target_id or target_id == source_id:
                    continue
                try:
                    self.registry.store_document_reference(source_id, target_id, "references")
                    stored += 1
                except Exception as e:
                    self.logger.warning(
                        f"Failed to store document_reference {source_id}→{ref}: {e}",
                        context="PipelineOrchestrator.persist_document_references",
                    )
        if stored:
            self.logger.info(
                f"Stored {stored} document_reference junction row(s)",
                context="PipelineOrchestrator.persist_document_references",
            )
        return stored

    def _update_doc_status(self, file_path: str, status: str,
                           doc_id: str,
                           confidence: Optional[float] = None,
                           notes: Optional[str] = None,
                           extra_properties: Optional[Dict[str, Any]] = None) -> None:
        """Update document extraction status in registry using registry.update_document_status().

        T1.106 (I232): doc_id is now required — resolved once in _process_file()
        via registry.get_document_by_file_path(). Legacy filename-parse fallback removed.
        """
        self.registry.update_document_status(
            doc_id, status, confidence=confidence, notes=notes,
            extra_properties=extra_properties,
        )

    # ------------------------------------------------------------------
    # T1.99.182 (I209): BaseEngine abstract method implementations.
    # PipelineOrchestrator now satisfies the Appendix F §2.3.1 BaseEngine
    # contract (validate_input → execute → validate_output).
    # ------------------------------------------------------------------

    def validate_input(self, input_data: EngineInput) -> ValidationResult:
        """Validate EngineInput before pipeline execution.

        Checks:
          - data_dir exists and is a directory
          - schema_dir exists
          - output_dir is writable (or creatable)
        """
        errors = []
        if not input_data.data_dir.exists():
            errors.append(f"data_dir does not exist: {input_data.data_dir}")
        if not input_data.schema_dir.exists():
            errors.append(f"schema_dir does not exist: {input_data.schema_dir}")
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
        )

    def execute(self, input_data: EngineInput) -> EngineOutput:
        """Execute pipeline from an EngineInput contract.

        Derives root_dir from input_data.data_dir and delegates to
        run_full_pipeline, which already handles A → B → C sequencing.
        """
        recursive = input_data.parameters.get("recursive", True)
        phase = input_data.parameters.get("phase", "full")

        if phase != "full":
            if phase == "A":
                result = self.run_phase_a(input_data.data_dir, recursive=recursive)
            elif phase == "B":
                result = self.run_phase_b(input_data.data_dir, recursive=recursive)
            else:  # C
                result = self.run_phase_c()
            summary = {f"phase_{phase.lower()}": result}
        else:
            summary = self.run_full_pipeline(
                input_data.data_dir, recursive=recursive,
            )

        # Determine status from context
        status = "SUCCESS"
        if self.context and self.context.state.status == "FAILED":
            status = "FAILED"
        elif self.context and self.context.state.status != "COMPLETE":
            status = "PARTIAL"

        return EngineOutput(
            run_id=input_data.run_id,
            status=status,
            metadata={"summary": summary},
        )

    def validate_output(self, output: EngineOutput) -> ValidationResult:
        """Validate EngineOutput after pipeline execution.

        Checks that status is a recognised value and metadata contains
        expected phase-result keys.
        """
        errors = []
        if output.status not in ("SUCCESS", "PARTIAL", "FAILED"):
            errors.append(f"Unknown status: {output.status}")
        summary = output.metadata.get("summary", {})
        if not summary:
            errors.append("EngineOutput.metadata.summary is empty")
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
        )
