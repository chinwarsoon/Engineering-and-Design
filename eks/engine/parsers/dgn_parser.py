"""
DGN Parser Stub for EKS - Placeholder for Phase 3 MicroStation DGN support.
"""
from typing import Any, Dict, List
from eks.engine.parsers.base_parser import BaseParser


class DGNParserStub(BaseParser):
    """Stub parser for DGN (MicroStation) files. Full implementation deferred to Phase 3."""

    SUPPORTED_EXTENSIONS = [".dgn"]

    def parse(self) -> List[Dict[str, Any]]:
        """Stub parse method."""
        return [{
            "content": "[DGN stub — implementation pending Phase 3]",
            "type": "text",
            "metadata": {"file_path": str(self.file_path)},
        }]

    def extract_metadata(self) -> Dict[str, Any]:
        """Stub metadata extraction."""
        return {
            "file_path": str(self.file_path),
            "format": "dgn",
            "status": "stub",
        }
