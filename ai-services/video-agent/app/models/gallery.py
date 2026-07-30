"""
FacultyIQ Video Evidence Extraction Service — Slide Gallery Models.

Pydantic v2 models for the frontend slide gallery display.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SlideGalleryItem(BaseModel):
    """A single slide gallery entry optimized for frontend display."""

    slide_id: str = Field(..., description="Unique slide identifier")
    timestamp: float = Field(..., description="Timestamp in seconds")
    timestamp_formatted: str = Field(
        ..., description="Human-readable timestamp (HH:MM:SS)"
    )
    thumbnail: str = Field(..., description="Path to slide thumbnail image")
    full_image: str = Field(..., description="Path to full-resolution slide image")
    ocr_text: Optional[str] = Field(
        None, description="OCR text extracted from this slide"
    )


class SlideGallery(BaseModel):
    """Complete slide gallery for frontend rendering."""

    total_slides: int = Field(..., description="Total number of slides")
    slides: List[SlideGalleryItem] = Field(
        ..., description="Gallery items for each slide"
    )
    json_path: str = Field(..., description="Path to gallery.json output file")
