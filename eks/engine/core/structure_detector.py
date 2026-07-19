"""
EKS Structure Detector - PDF structural element detection.
Detects cover pages, revision tables, section headings, data tables,
images, links, legends, and notes from parsed PDF content.
"""
import re
from typing import Any, Dict, List, Optional
from ..logging.logger import EKSLogger, log_depth

COVER_PAGE_PATTERNS = {
    "project_number": re.compile(r'(?:Project|Contract)\s*(?:No|Number|#)[.:]\s*(\S+)', re.IGNORECASE),
    "project_title": re.compile(r'(?:Project|Contract)\s*(?:Title|Name)[.:]\s*(.+)', re.IGNORECASE),
    "document_number": re.compile(r'(?:Doc(?:ument)?\s*(?:No|Number|#)|Drawing\s*(?:No|Number|#))[.:]\s*(\S+)', re.IGNORECASE),
    "revision": re.compile(r'(?:Revision|Rev)[.:]\s*(\S+)', re.IGNORECASE),
    "discipline": re.compile(r'(?:Discipline)[.:]\s*(\S+)', re.IGNORECASE),
    "status": re.compile(r'(?:Status)[.:]\s*(\S+)', re.IGNORECASE),
    # T1.99.162 (I196): Best-effort asset tag detection from title block.
    # Matches patterns like "Tag: P-101, V-202" or "Equipment No: E-301A"
    "asset_tags": re.compile(r'(?:Tag|Asset|Equipment)\s*(?:s|No|Number|#)?[.:]\s*([\w\-,\s]+)', re.IGNORECASE),
}

REVISION_ROW_PATTERN = re.compile(r'^\s*(\d+)\s+(\S+)\s+(\S+)')
SECTION_PATTERN = re.compile(r'^(\d+(?:\.\d+)*)\s+(.+)$')
LINK_PATTERN = re.compile(r'(https?://\S+|file://\S+|\\\\[^\\]+\\.+)', re.IGNORECASE)


class StructureDetector:
    """
    Detects structural elements within parsed PDF content.
    Operates on the output of pdf_parser.py (text + table + image extraction).
    """

    def __init__(self, logger: Optional[EKSLogger] = None):
        self.logger = logger or EKSLogger("StructureDetector", level=2)

    @log_depth
    def detect(self, filename: str, pages: Optional[List[Dict[str, Any]]] = None,
               full_text: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Detect all structural elements in a document.

        Parameters
        ----------
        filename : str
            The source filename (used for cover type heuristics).
        pages : list of dict, optional
            List of page dicts from pdf_parser, each containing 'text', 'tables', 'images'.
        full_text : str, optional
            Concatenated text of all pages (alternative to pages).

        Returns
        -------
        list of dict, each with keys: element_type, element_id, title, content,
                                       confidence, source
        """
        elements: List[Dict[str, Any]] = []
        text = full_text or ""
        page_texts: List[str] = []
        page_tables: List[List[Any]] = []
        page_images: List[Any] = []

        if pages:
            for i, page in enumerate(pages):
                page_num = i + 1
                page_text = page.get("text", "")
                page_texts.append(page_text)
                page_tables.append(page.get("tables", []))
                page_images.append(page.get("images", []))
                text += page_text
        else:
            page_texts = [text]

        # Detect cover page (page 1)
        cover = self._detect_cover_page(page_texts[0] if page_texts else text)
        if cover:
            elements.append(cover)

        # Detect revision table
        rev_table = self._detect_revision_table(page_texts[0] if page_texts else text)
        if rev_table:
            elements.append(rev_table)

        # Detect sections across all pages
        for page_num, pt in enumerate(page_texts, 1):
            sections = self._detect_sections(pt)
            for sec in sections:
                sec["element_id"] = str(page_num)
                elements.append(sec)

        # Detect tables in all pages
        for page_num, tables in enumerate(page_tables, 1):
            for table in tables:
                elements.append({
                    "element_type": "table",
                    "element_id": str(page_num),
                    "title": "",
                    "content": str(table)[:500],
                    "confidence": 0.9,
                    "source": "heuristic",
                })

        # Detect images in all pages
        for page_num, images in enumerate(page_images, 1):
            for img in images:
                elements.append({
                    "element_type": "image",
                    "element_id": str(page_num),
                    "title": img.get("alt", "") if isinstance(img, dict) else "",
                    "content": str(img)[:200],
                    "confidence": 0.9,
                    "source": "heuristic",
                })

        # Detect links
        links = self._detect_links(text)
        for link in links:
            elements.append(link)

        # Detect legend (page 1)
        legend = self._detect_legend(page_texts[0] if page_texts else text)
        if legend:
            elements.append(legend)

        # Detect notes (page 1)
        notes = self._detect_notes(page_texts[0] if page_texts else text)
        for note in notes:
            elements.append(note)

        self.logger.debug(f"Detected {len(elements)} structural elements in {filename}",
                          context="StructureDetector.detect")
        return elements

    def _detect_cover_page(self, text: str) -> Optional[Dict[str, Any]]:
        """Detect cover page / title block content on first page."""
        if not text.strip():
            return None
        fields_found = {}
        total_fields = 0
        for field, pattern in COVER_PAGE_PATTERNS.items():
            match = pattern.search(text)
            if match:
                fields_found[field] = match.group(1)
                total_fields += 1
        if total_fields < 2:
            return None
        confidence = min(1.0, total_fields / len(COVER_PAGE_PATTERNS) + 0.3)
        return {
            "element_type": "cover_page",
            "element_id": "1",
            "title": "Cover Page / Title Block",
            "content": str(fields_found),
            "confidence": round(confidence, 2),
            "source": "regex",
        }

    def _detect_revision_table(self, text: str) -> Optional[Dict[str, Any]]:
        """Detect revision history table by looking for revision rows."""
        rows = []
        for line in text.split("\n"):
            match = REVISION_ROW_PATTERN.match(line)
            if match:
                rows.append({"num": match.group(1), "date": match.group(2), "by": match.group(3)})
        if len(rows) < 1:
            return None
        confidence = min(1.0, len(rows) / 5 + 0.5)
        return {
            "element_type": "revision_table",
            "element_id": "1",
            "title": f"Revision History ({len(rows)} rows)",
            "content": str(rows),
            "confidence": round(confidence, 2),
            "source": "regex",
        }

    def _detect_sections(self, text: str) -> List[Dict[str, Any]]:
        """Detect section headings like '1.0', '2.1 Scope', etc."""
        sections = []
        for line in text.split("\n"):
            line = line.strip()
            match = SECTION_PATTERN.match(line)
            if match:
                sections.append({
                    "element_type": "section",
                    "element_id": "",
                    "title": line,
                    "content": match.group(2),
                    "confidence": 0.8,
                    "source": "regex",
                })
        return sections

    def _detect_links(self, text: str) -> List[Dict[str, Any]]:
        """Detect hyperlinks and file paths."""
        links = []
        for match in LINK_PATTERN.finditer(text):
            url = match.group(1)
            links.append({
                "element_type": "link",
                "element_id": "",
                "title": url,
                "content": url,
                "confidence": 0.9,
                "source": "regex",
            })
        return links

    def _detect_legend(self, text: str) -> Optional[Dict[str, Any]]:
        """Detect legend blocks by keyword heuristics."""
        legend_keywords = ["legend", "symbol", "abbreviation"]
        text_lower = text.lower()
        for kw in legend_keywords:
            if kw in text_lower:
                idx = text_lower.find(kw)
                start = max(0, idx - 20)
                end = min(len(text), idx + 200)
                snippet = text[start:end]
                return {
                    "element_type": "legend",
                    "element_id": "1",
                    "title": "Legend / Abbreviations",
                    "content": snippet,
                    "confidence": 0.6,
                    "source": "heuristic",
                }
        return None

    def _detect_notes(self, text: str) -> List[Dict[str, Any]]:
        """Detect annotation / note blocks."""
        notes = []
        note_keywords = ["note:", "notes:", "remark:", "remarks:"]
        for line in text.split("\n"):
            line_stripped = line.strip().lower()
            for kw in note_keywords:
                if line_stripped.startswith(kw):
                    notes.append({
                        "element_type": "note",
                        "element_id": "",
                        "title": line.strip()[:60],
                        "content": line.strip(),
                        "confidence": 0.7,
                        "source": "heuristic",
                    })
                    break
        return notes

    def classify_cover_type(self, filename: str, text: str) -> str:
        """
        Classify the cover sheet type (A, B, C, D, E) based on content heuristics.
        """
        text_lower = text.lower()
        is_scanned = len(text.strip()) < 50
        has_standard_keywords = bool(re.search(r'dwg|drawing|detail|plan', text_lower))
        has_spec_keywords = bool(re.search(r'specification|spec|standard', text_lower))

        if is_scanned:
            return "C"
        if has_spec_keywords:
            return "E"
        if "volume" in text_lower or "part" in text_lower:
            return "D"
        if has_standard_keywords:
            return "A"
        return "B"
