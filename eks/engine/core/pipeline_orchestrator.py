"""
Pipeline Orchestrator for EKS - Coordinates Phase A/B/C pipeline workflow.
T1.39: Pre-parse → parse → score → review pipeline coordinator.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..logging.logger import EKSLogger, log_depth
from .file_scanner import FileScanner
from .health_scorer import HealthScorer
from .structure_detector import StructureDetector
from ..parsers.parser_router import ParserRouter


class PipelineOrchestrator:
    """
    Coordinates the 3-phase EKS pipeline:
    - Phase A: Scan directory → register placeholder documents
    - Phase B: Route → parse → detect structure → score → update metadata
    - Phase C: Flag documents for manual review
    """

    def __init__(self, config: Dict[str, Any], doc_config: Dict[str, Any],
                 registry: Any, logger: Optional[EKSLogger] = None):
        self.config = config
        self.doc_config = doc_config
        self.registry = registry
        self.logger = logger or EKSLogger("PipelineOrchestrator", level=1)
        self.scanner = FileScanner(config, doc_config=doc_config, logger=self.logger)
        self.router = ParserRouter(doc_config, logger=self.logger)
        self.scorer = HealthScorer(logger=self.logger)
        self.detector = StructureDetector(logger=self.logger)

    @log_depth
    def run_phase_a(self, root_dir: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        Phase A: Scan project directory and register placeholder documents.

        Returns summary dict with keys:
            - discovered: count of files discovered
            - valid: count of files with recognized extensions
            - unknown: count of files with unrecognized extensions
            - registered: count of new placeholder documents registered
        """
        self.logger.status(f"Phase A: Scanning {root_dir}")

        discovered = self.scanner.scan(root_dir, recursive=recursive)
        valid, unknown = self.scanner.validate_file_types(discovered)
        registered = self.scanner.register_placeholders(valid, self.registry)

        summary = {
            "discovered": len(discovered),
            "valid": len(valid),
            "unknown": len(unknown),
            "registered": registered,
        }
        self.logger.status(f"Phase A complete: {summary}")
        return summary

    @log_depth
    def run_phase_b(self, root_dir: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        Phase B: For each discovered file, route → parse → detect → score → update.

        Returns summary dict with keys:
            - total: count of files processed
            - success: count parsed successfully
            - partial: count with partial success
            - failed: count that failed
            - results: list of per-file result dicts
        """
        self.logger.status(f"Phase B: Parsing files in {root_dir}")

        discovered = self.scanner.scan(root_dir, recursive=recursive)
        valid, _ = self.scanner.validate_file_types(discovered)

        results = []
        success = 0
        partial = 0
        failed = 0

        for file_info in valid:
            file_path = file_info["file_path"]
            file_type = file_info["file_type"]
            result = self._process_file(file_path, file_type)
            results.append(result)

            status = result.get("status", "failed")
            if status == "success":
                success += 1
            elif status == "partial":
                partial += 1
            else:
                failed += 1

        summary = {
            "total": len(valid),
            "success": success,
            "partial": partial,
            "failed": failed,
            "results": results,
        }
        self.logger.status(f"Phase B complete: {success} success, {partial} partial, {failed} failed")
        return summary

    @log_depth
    def run_phase_c(self) -> Dict[str, Any]:
        """
        Phase C: Flag documents for manual review.
        Queries documents where extract_status != 'success' or
        extraction_confidence < 0.70.

        Returns summary dict with keys:
            - flagged: count of documents flagged
            - documents: list of flagged document metadata dicts
        """
        self.logger.status("Phase C: Flagging documents for review")

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
        self.logger.status(f"Phase C complete: {len(flagged)} documents flagged for review")
        return summary

    @log_depth
    def run_full_pipeline(self, root_dir: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        Run all three phases in sequence: A → B → C.

        Returns combined summary dict.
        """
        self.logger.status(f"Starting full pipeline for {root_dir}")

        phase_a = self.run_phase_a(root_dir, recursive=recursive)
        phase_b = self.run_phase_b(root_dir, recursive=recursive)
        phase_c = self.run_phase_c()

        summary = {
            "phase_a": phase_a,
            "phase_b": phase_b,
            "phase_c": phase_c,
        }
        self.logger.status("Full pipeline complete")
        return summary

    def _process_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Process a single file through the parse → detect → score pipeline.
        """
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
                self._update_doc_status(file_path, "failed", error=result["error"])
                return result

            content_blocks = parse_result.get("content_blocks", [])
            metadata = parse_result.get("metadata", {})

            try:
                pages = self._adapt_content_for_detector(content_blocks)
                elements = self.detector.detect(file_path, pages=pages)
                result["elements"] = elements
            except Exception as e:
                self.logger.warning(
                    f"Structure detection failed for {file_path}: {e}",
                    context="PipelineOrchestrator._process_file"
                )

            doc_number = Path(file_path).stem.split("_rev")[0].rsplit("-", 1)[0]
            doc = self.registry.get_document(doc_number)
            if doc:
                score = self.scorer.score(doc, elements)
                result["score"] = score
                self._update_doc_status(
                    file_path, "success",
                    confidence=score.get("overall"),
                    notes=f"Auto-parsed via pipeline"
                )
                result["status"] = "success"
            else:
                result["status"] = "partial"
                result["error"] = f"Document not registered: {doc_number}"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.logger.error(
                f"Pipeline processing failed for {file_path}: {e}",
                context="PipelineOrchestrator._process_file"
            )

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
                           error: Optional[str] = None) -> None:
        """Update document extraction status in registry."""
        doc_number = Path(file_path).stem.split("_rev")[0].rsplit("-", 1)[0]
        doc = self.registry.get_document(doc_number)
        if doc:
            conn = __import__('duckdb').connect(str(self.registry.db_path))
            try:
                conn.execute(
                    "UPDATE documents SET extract_status = ?, extraction_confidence = ?, extraction_notes = ? WHERE id = ?",
                    [status, confidence, error, doc["id"]]
                )
            finally:
                conn.close()
