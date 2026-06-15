"""
Abstract Base Parser for EKS - Defines the interface for document parsers.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

class BaseParser(ABC):
    """
    Abstract base class for all document parsers (PDF, DOCX, XLSX, etc.).
    """
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    @abstractmethod
    def parse(self) -> List[Dict[str, Any]]:
        """
        Parses the file and returns a list of content blocks.
        Each block should contain:
        - content: str
        - metadata: dict (page, section, coordinates, etc.)
        - type: str (text, table, image, etc.)
        """
        pass

    @abstractmethod
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extracts file-level metadata (author, creation date, etc.).
        """
        pass

    def get_source_context(self) -> Dict[str, Any]:
        """
        Returns the basic source context for the file.
        """
        return {
            "file_path": str(self.file_path),
            "file_name": self.file_path.name,
            "extension": self.file_path.suffix.lower()
        }
