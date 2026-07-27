"""
Component 2: Document Classification Engine.
Determines physical document sub-type: Native PDF, Scanned PDF, Hybrid PDF, DOCX, Image Document, Text Document.
"""

from typing import Any, Dict
from core.logging import get_logger

logger = get_logger("ingestion_classification")


class ClassificationDetail:
    def __init__(self, doc_class: str, confidence: float, reason: str, metadata: Dict[str, Any]) -> None:
        self.doc_class = doc_class
        self.confidence = confidence
        self.reason = reason
        self.metadata = metadata


class IngestionClassificationEngine:
    """Component 2: Physical Document Type Classifier."""

    def classify_physical_document(
        self, format_type: str, raw_pages: list[str], images_count: int, is_scanned_flag: bool
    ) -> ClassificationDetail:
        total_text = "".join(raw_pages).strip()
        text_length = len(total_text)
        page_count = max(1, len(raw_pages))
        avg_text_per_page = text_length / page_count

        if format_type == "docx":
            return ClassificationDetail(
                doc_class="DOCX",
                confidence=1.0,
                reason="Native OpenXML document structure detected.",
                metadata={"avg_chars_per_page": avg_text_per_page},
            )

        if format_type in ["png", "jpeg", "tiff"]:
            return ClassificationDetail(
                doc_class="Image Document",
                confidence=0.98,
                reason="Raster image binary stream.",
                metadata={"format": format_type},
            )

        if format_type == "txt" or format_type == "rtf":
            return ClassificationDetail(
                doc_class="Text Document",
                confidence=1.0,
                reason="Plain text / RTF stream.",
                metadata={"char_count": text_length},
            )

        if format_type == "pdf":
            if text_length > 300 and not is_scanned_flag:
                return ClassificationDetail(
                    doc_class="Native PDF",
                    confidence=0.95,
                    reason=f"Vector PDF with embedded fonts ({int(avg_text_per_page)} chars/page).",
                    metadata={"avg_chars_per_page": avg_text_per_page},
                )
            elif text_length < 50 or is_scanned_flag:
                return ClassificationDetail(
                    doc_class="Scanned PDF",
                    confidence=0.92,
                    reason="Low embedded text density; raster page scans detected.",
                    metadata={"scanned": True, "embedded_chars": text_length},
                )
            else:
                return ClassificationDetail(
                    doc_class="Hybrid PDF",
                    confidence=0.85,
                    reason="Mixed vector text and raster image scans detected across pages.",
                    metadata={"avg_chars_per_page": avg_text_per_page},
                )

        return ClassificationDetail(
            doc_class="Unknown Document",
            confidence=0.20,
            reason="Unrecognized physical format.",
            metadata={},
        )
