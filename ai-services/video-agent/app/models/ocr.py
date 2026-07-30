"""
FacultyIQ Video Evidence Extraction Service — OCR Models.

Pydantic v2 models for Tesseract OCR extraction per slide.
"""

from typing import List

from pydantic import BaseModel, Field


class OCREntry(BaseModel):
    """OCR extraction for a single slide image."""

    slide_id: str = Field(..., description="Matching slide identifier")
    timestamp: float = Field(..., description="Slide timestamp in seconds")
    image_path: str = Field(..., description="Path to the source slide image")
    raw_text: str = Field(default="", description="Raw OCR text output")
    cleaned_text: str = Field(
        default="", description="Cleaned and normalized OCR text"
    )
    confidence: float = Field(
        default=0.0, description="Average OCR confidence (0–100)"
    )
    titles: List[str] = Field(default_factory=list, description="Detected titles")
    paragraphs: List[str] = Field(
        default_factory=list, description="Detected paragraphs"
    )
    bullets: List[str] = Field(
        default_factory=list, description="Detected bullet points"
    )
    tables: List[str] = Field(
        default_factory=list, description="Detected table content"
    )
    equations: List[str] = Field(
        default_factory=list, description="Detected equations"
    )
    code_blocks: List[str] = Field(
        default_factory=list, description="Detected code snippets"
    )
    algorithms: List[str] = Field(
        default_factory=list, description="Detected algorithm descriptions"
    )
    diagrams: List[str] = Field(
        default_factory=list, description="Detected diagram labels"
    )


class OCRResult(BaseModel):
    """Complete OCR extraction output across all slides."""

    total_slides: int = Field(
        ..., description="Number of slides processed"
    )
    average_confidence: float = Field(
        ..., description="Average OCR confidence across all slides"
    )
    entries: List[OCREntry] = Field(
        ..., description="Per-slide OCR extraction results"
    )
    json_path: str = Field(
        ..., description="Path to ocr.json output file"
    )
    txt_path: str = Field(
        ..., description="Path to ocr.txt output file"
    )
