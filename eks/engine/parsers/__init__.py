"""EKS Parsers package - Plug-in document parsers for engineering formats."""
from .base_parser import BaseParser
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .xlsx_parser import XLSXParser

__version__ = "1.0.0"
