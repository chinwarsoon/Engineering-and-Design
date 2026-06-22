"""
Parser Router for EKS - Maps file_type to parser class, orchestrates parse flow.
T1.38: Phase B of pipeline workflow.
"""
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..logging.logger import EKSLogger, log_depth


class ParserRouter:
    """
    Routes files to the correct parser based on file_type from file_type_registry.
    Orchestrates: parse() → extract_metadata() → StructureDetector.detect().
    """

    def __init__(self, doc_config: Dict[str, Any], logger: Optional[EKSLogger] = None):
        self.doc_config = doc_config
        self.logger = logger or EKSLogger("ParserRouter", level=1)
        self.file_type_registry = doc_config.get("file_type_registry", [])
        self._ext_parser_map = self._build_parser_map()

    def _build_parser_map(self) -> Dict[str, str]:
        """Map file extension to parser_class string."""
        result = {}
        for entry in self.file_type_registry:
            ext = entry.get("extension", "").lower()
            parser_class = entry.get("parser_class", "")
            if ext and parser_class:
                result[ext] = parser_class
        return result

    @log_depth
    def get_parser_class(self, file_type: str) -> Optional[str]:
        """Look up parser class path for a given file extension."""
        return self._ext_parser_map.get(file_type.lower())

    @log_depth
    def instantiate_parser(self, parser_class_path: str, file_path: str) -> Any:
        """
        Dynamically import and instantiate a parser class.
        Returns the parser instance.
        """
        try:
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
    def route(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Route a file through the parser pipeline:
        1. Look up parser class from file_type_registry
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
            "parser_class": self._ext_parser_map.get(file_type, ""),
            "content_blocks": [],
            "metadata": {},
            "status": "pending",
            "error": None,
        }

        parser_class_path = self._ext_parser_map.get(file_type)
        if not parser_class_path:
            result["status"] = "failed"
            result["error"] = f"No parser registered for file type: {file_type}"
            self.logger.warning(
                f"No parser for file type '{file_type}': {file_path}",
                context="ParserRouter.route"
            )
            return result

        try:
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
