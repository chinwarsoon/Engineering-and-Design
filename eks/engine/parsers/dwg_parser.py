"""
DWG Parser Stub for EKS - Placeholder for Phase 3 AutoCAD DWG support.
"""
from typing import Any, Dict, List
from eks.engine.parsers.base_parser import BaseParser


class DWGParserStub(BaseParser):
    """Stub parser for DWG (AutoCAD) files. Full implementation deferred to Phase 3."""

    SUPPORTED_EXTENSIONS = [".dwg"]

    def parse(self) -> List[Dict[str, Any]]:
        """Stub parse method."""
        return [{
            "content": "[DWG stub — implementation pending Phase 3]",
            "type": "text",
            "metadata": {"file_path": str(self.file_path)},
        }]

    def extract_metadata(self) -> Dict[str, Any]:
        """Stub metadata extraction."""
        return {
            "file_path": str(self.file_path),
            "format": "dwg",
            "status": "stub",
        }
