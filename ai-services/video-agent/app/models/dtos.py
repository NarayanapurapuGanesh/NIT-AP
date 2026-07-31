"""
FacultyIQ Video Evidence Extraction Service — Frontend-Ready DTOs.

Pydantic v2 models designed for React/Next.js consumption with camelCase
serialization via model_config populate_by_name and alias_generator.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


def _to_camel(name: str) -> str:
    """Converts snake_case to camelCase for JS consumption."""
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class _CamelModel(BaseModel):
    """Base DTO model that serializes fields to camelCase."""

    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class TranscriptSegmentDTO(_CamelModel):
    """Individual transcript segment for frontend display."""

    timestamp: float = Field(..., description="Segment start time in seconds")
    start: float = Field(..., description="Segment start time")
    end: float = Field(..., description="Segment end time")
    text: str = Field(..., description="Transcribed text")


class TranscriptDTO(_CamelModel):
    """Complete transcript optimized for frontend viewer."""

    full_text: str = Field(..., description="Full concatenated transcript")
    segments: List[TranscriptSegmentDTO] = Field(
        ..., description="Time-aligned segments"
    )
    language: str = Field(default="en")
    duration_seconds: float = Field(default=0.0)


class SlideDTO(_CamelModel):
    """Single slide for frontend gallery."""

    slide_id: str = Field(..., description="Slide identifier")
    timestamp: float = Field(..., description="Timestamp in seconds")
    timestamp_formatted: str = Field(
        ..., description="Human-readable timestamp"
    )
    thumbnail_url: str = Field(..., description="Thumbnail image URL/path")
    full_image_url: str = Field(
        ..., description="Full-resolution image URL/path"
    )
    ocr_text: Optional[str] = Field(
        None, description="OCR text from this slide"
    )
    visual_type: str = Field(default="Slide")
    contains_handwriting: bool = Field(default=False)
    contains_diagram: bool = Field(default=False)
    contains_flowchart: bool = Field(default=False)
    contains_code: bool = Field(default=False)
    contains_equation: bool = Field(default=False)
    contains_table: bool = Field(default=False)


class OCRDTO(_CamelModel):
    """OCR extraction for a single slide."""

    slide_id: str = Field(..., description="Slide identifier")
    timestamp: float = Field(..., description="Slide timestamp")
    text: str = Field(default="", description="Extracted text content")
    confidence: float = Field(default=0.0, description="OCR confidence")


class TimelineEntryDTO(_CamelModel):
    """Single timeline entry for frontend navigation."""

    timestamp: float = Field(..., description="Timestamp in seconds")
    timestamp_formatted: str = Field(
        ..., description="Human-readable timestamp"
    )
    slide_id: Optional[str] = None
    slide_image_url: Optional[str] = None
    transcript_text: Optional[str] = None
    ocr_text: Optional[str] = None


class TimelineDTO(_CamelModel):
    """Complete timeline for frontend display."""

    total_entries: int
    duration_seconds: float
    entries: List[TimelineEntryDTO]


class SummaryDTO(_CamelModel):
    """Teaching summary for frontend display."""

    short_summary: str = Field(..., description="Concise summary")
    topics_covered: List[str] = Field(default_factory=list)
    concepts: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    technical_terms: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    algorithms: List[str] = Field(default_factory=list)
    subjects: List[str] = Field(default_factory=list)


class VideoDTO(_CamelModel):
    """Video metadata for frontend display."""

    filename: str
    format: str
    duration_seconds: float
    resolution: str
    fps: float
    file_size_mb: float
    has_audio: bool
    video_codec: str
    audio_codec: Optional[str] = None


class FullReportDTO(_CamelModel):
    """Complete evidence report combining all extracted data."""

    job_id: str
    video: VideoDTO
    transcript: TranscriptDTO
    slides: List[SlideDTO]
    ocr: List[OCRDTO]
    timeline: TimelineDTO
    summary: SummaryDTO
    voice_metrics: Optional[dict] = None
