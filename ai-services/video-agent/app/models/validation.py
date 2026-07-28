from typing import List, Optional
from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    format: str = Field(..., description="Video file extension (e.g. mp4)")
    file_size_bytes: int = Field(..., description="File size in bytes")
    file_size_mb: float = Field(..., description="File size in megabytes")
    duration_seconds: float = Field(..., description="Video duration in seconds")
    width: int = Field(..., description="Frame width in pixels")
    height: int = Field(..., description="Frame height in pixels")
    fps: float = Field(..., description="Frames per second")
    video_codec: str = Field(..., description="Video codec (e.g. h264)")
    audio_codec: Optional[str] = Field(None, description="Audio codec (e.g. aac)")
    has_audio: bool = Field(..., description="True if audio stream exists")


class ValidationResult(BaseModel):
    validationPassed: bool = Field(..., description="True if all validation checks passed")
    metadata: Optional[VideoMetadata] = None
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
