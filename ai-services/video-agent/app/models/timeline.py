"""
FacultyIQ Video Evidence Extraction Service — Timeline Models.

Pydantic v2 models for the unified teaching timeline.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class TimelineEntry(BaseModel):
    """A single entry in the unified teaching timeline."""

    timestamp: float = Field(
        ..., description="Timestamp in seconds"
    )
    timestamp_formatted: str = Field(
        ..., description="Human-readable timestamp (HH:MM:SS)"
    )
    event_type: str = Field(
        ..., description="Type of event: 'slide', 'transcript', 'slide_and_transcript'"
    )
    slide_id: Optional[str] = Field(
        None, description="Associated slide identifier"
    )
    slide_image_path: Optional[str] = Field(
        None, description="Path to slide image"
    )
    transcript_text: Optional[str] = Field(
        None, description="Transcript text at this timestamp"
    )
    ocr_text: Optional[str] = Field(
        None, description="OCR text extracted from the slide"
    )


class Timeline(BaseModel):
    """Unified teaching timeline merging transcript, slides, and OCR."""

    total_entries: int = Field(
        ..., description="Total number of timeline entries"
    )
    duration_seconds: float = Field(
        ..., description="Total video duration in seconds"
    )
    entries: List[TimelineEntry] = Field(
        ..., description="Chronologically ordered timeline entries"
    )
    json_path: str = Field(
        ..., description="Path to timeline.json output file"
    )
