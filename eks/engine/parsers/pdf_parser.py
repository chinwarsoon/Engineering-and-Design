"""
PDF Parser for EKS - Uses PyMuPDF (fitz) for text and metadata extraction.
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import Any, Dict, List
from .base_parser import BaseParser

class PDFParser(BaseParser):
    """
    Parses PDF files to extract text content and metadata per page.
    """
    def parse(self) -> List[Dict[str, Any]]:
        blocks = []
        doc = fitz.open(str(self.file_path))
        try:
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                if text.strip():
                    blocks.append({
                        "content": text,
                        "type": "text",
                        "metadata": {
                            "page": page_num + 1,
                            "dimensions": (page.rect.width, page.rect.height)
                        }
                    })
            return blocks
        finally:
            doc.close()

    def extract_metadata(self) -> Dict[str, Any]:
        doc = fitz.open(str(self.file_path))
        try:
            meta = doc.metadata
            return {
                "author": meta.get("author"),
                "title": meta.get("title"),
                "subject": meta.get("subject"),
                "creator": meta.get("creator"),
                "producer": meta.get("producer"),
                "creation_date": meta.get("creationDate"),
                "mod_date": meta.get("modDate"),
                "page_count": doc.page_count
            }
        finally:
            doc.close()
