"""
Resume Type Detection Module (Module 2).

Automatically classifies uploaded documents into specialized processing channels:
- Digital PDF
- Scanned PDF
- Image Resume
- Modern Resume
- Academic CV
- Faculty CV
- Research CV
"""

import io
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from classifiers.base import IClassifier


class ResumeCategory(str, Enum):
    DIGITAL_PDF = "Digital PDF"
    SCANNED_PDF = "Scanned PDF"
    IMAGE_RESUME = "Image Resume"
    MODERN_RESUME = "Modern Resume"
    ACADEMIC_CV = "Academic CV"
    FACULTY_CV = "Faculty CV"
    RESEARCH_CV = "Research CV"


class ResumeTypeResult(BaseModel):
    category: ResumeCategory = Field(..., description="Primary classification category")
    secondary_category: Optional[ResumeCategory] = Field(None, description="Secondary subtype tag if applicable")
    requires_ocr: bool = Field(False, description="Flag indicating if OCR must be scheduled")
    is_academic: bool = Field(False, description="Flag indicating if document is an academic/research/faculty CV")
    text_density: float = Field(0.0, description="Extracted characters per page ratio")
    detected_keywords: List[str] = Field(default_factory=list, description="Keywords driving category classification")
    confidence: float = Field(1.0, description="Classification confidence score [0.0 - 1.0]")


class ResumeTypeDetector(IClassifier):
    """Resume Type Classifier using heuristic analysis and keyword density scoring."""

    ACADEMIC_KEYWORDS = {
        "publications", "citations", "h-index", "peer-reviewed", "journal", "conference",
        "grant", "nsf", "nih", "patent", "abstract", "proceedings", "co-author", "doi", "orcid"
    }

    FACULTY_KEYWORDS = {
        "associate professor", "assistant professor", "professor", "tenure", "lecturer",
        "department of", "dean", "chair", "courses taught", "teaching assistant", "syllabus",
        "doctoral thesis", "thesis advisor", "faculty"
    }

    RESEARCH_KEYWORDS = {
        "principal investigator", "postdoctoral", "fellowship", "laboratory", "experimental",
        "researchgate", "arxiv", "methodology", "r&d", "dataset", "workbench"
    }

    @property
    def name(self) -> str:
        return "ResumeTypeDetector"

    async def classify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Classifies payload dictionary."""
        file_bytes = payload.get("file_bytes", b"")
        file_extension = payload.get("file_extension", ".pdf").lower()
        extracted_text = payload.get("extracted_text", "")

        result = self.detect_type(file_bytes, file_extension, extracted_text)
        return result.model_dump()

    def detect_type(self, file_bytes: bytes, file_extension: str, extracted_text: str = "") -> ResumeTypeResult:
        # 1. Image check
        if file_extension in {".png", ".jpg", ".jpeg", ".tiff", ".tif"}:
            return ResumeTypeResult(
                category=ResumeCategory.IMAGE_RESUME,
                requires_ocr=True,
                is_academic=False,
                text_density=0.0,
                confidence=1.0,
            )

        # 2. PDF extractability check if text not pre-provided
        text_content = extracted_text
        page_count = 1

        if file_extension == ".pdf" and file_bytes and not text_content:
            try:
                import fitz
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                page_count = max(1, doc.page_count)
                extracted_pages = [page.get_text("text") for page in doc]
                text_content = "\n".join(extracted_pages)
                doc.close()
            except Exception:
                pass

        total_chars = len(text_content.strip())
        char_per_page = total_chars / page_count if page_count > 0 else 0

        # Scanned PDF check
        if file_extension == ".pdf" and char_per_page < 100:
            return ResumeTypeResult(
                category=ResumeCategory.SCANNED_PDF,
                requires_ocr=True,
                is_academic=False,
                text_density=char_per_page,
                confidence=0.95,
            )

        # Keyword density scoring
        text_lower = text_content.lower()
        academic_matches = [k for k in self.ACADEMIC_KEYWORDS if k in text_lower]
        faculty_matches = [k for k in self.FACULTY_KEYWORDS if k in text_lower]
        research_matches = [k for k in self.RESEARCH_KEYWORDS if k in text_lower]

        all_matches = academic_matches + faculty_matches + research_matches

        # Categorization logic
        if len(faculty_matches) >= 2:
            return ResumeTypeResult(
                category=ResumeCategory.FACULTY_CV,
                secondary_category=ResumeCategory.ACADEMIC_CV,
                requires_ocr=False,
                is_academic=True,
                text_density=char_per_page,
                detected_keywords=all_matches,
                confidence=0.95,
            )

        if len(academic_matches) >= 3 or (len(academic_matches) >= 1 and len(research_matches) >= 2):
            return ResumeTypeResult(
                category=ResumeCategory.ACADEMIC_CV,
                secondary_category=ResumeCategory.RESEARCH_CV if research_matches else None,
                requires_ocr=False,
                is_academic=True,
                text_density=char_per_page,
                detected_keywords=all_matches,
                confidence=0.92,
            )

        if len(research_matches) >= 3:
            return ResumeTypeResult(
                category=ResumeCategory.RESEARCH_CV,
                secondary_category=None,
                requires_ocr=False,
                is_academic=True,
                text_density=char_per_page,
                detected_keywords=all_matches,
                confidence=0.90,
            )

        # Standard modern resume default
        return ResumeTypeResult(
            category=ResumeCategory.DIGITAL_PDF if file_extension == ".pdf" else ResumeCategory.MODERN_RESUME,
            secondary_category=ResumeCategory.MODERN_RESUME,
            requires_ocr=False,
            is_academic=False,
            text_density=char_per_page,
            detected_keywords=all_matches,
            confidence=0.88,
        )
