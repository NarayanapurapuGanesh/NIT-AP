"""
FacultyIQ Video Evidence Extraction Service — Validation Models.

Pydantic v2 models for video validation results and metadata extraction.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    """Complete video file metadata extracted via FFprobe."""

    filename: str = Field(..., description="Original filename")
    format: str = Field(..., description="Video file extension (e.g. mp4)")
    mime_type: Optional[str] = Field(None, description="Detected MIME type")
    file_size_bytes: int = Field(..., description="File size in bytes")
    file_size_mb: float = Field(..., description="File size in megabytes")
    duration_seconds: float = Field(..., description="Video duration in seconds")
    width: int = Field(..., description="Frame width in pixels")
    height: int = Field(..., description="Frame height in pixels")
    fps: float = Field(..., description="Frames per second")
    bitrate: Optional[int] = Field(None, description="Overall bitrate in bps")
    video_codec: str = Field(..., description="Video codec (e.g. h264)")
    audio_codec: Optional[str] = Field(None, description="Audio codec (e.g. aac)")
    has_audio: bool = Field(..., description="True if audio stream exists")
    audio_channels: Optional[int] = Field(None, description="Number of audio channels")
    sample_rate: Optional[int] = Field(None, description="Audio sample rate in Hz")

    @property
    def resolution(self) -> str:
        """Human-readable resolution string."""
        return f"{self.width}x{self.height}"


class ValidationResult(BaseModel):
    """Result of Module 1 video validation."""

    validation_passed: bool = Field(
        ..., description="True if all validation checks passed"
    )
    metadata: Optional[VideoMetadata] = Field(
        None, description="Extracted video metadata when validation passes"
    )
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
