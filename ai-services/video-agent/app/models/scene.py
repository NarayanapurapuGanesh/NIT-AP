"""
FacultyIQ Video Evidence Extraction Service — Scene / Slide Models.

Pydantic v2 models for scene detection, keyframes, and extracted slides.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SlideImage(BaseModel):
    """A single extracted slide image with metadata."""

    slide_id: str = Field(..., description="Unique slide identifier (e.g. slide_001)")
    scene_id: int = Field(..., description="Parent scene index")
    timestamp: float = Field(
        ..., description="Timestamp in seconds when this slide appears"
    )
    frame_number: int = Field(..., description="Source frame number in original video")
    image_path: str = Field(..., description="Path to full-resolution slide image")
    thumbnail_path: Optional[str] = Field(
        None, description="Path to thumbnail image"
    )
    phash: Optional[str] = Field(
        None, description="Perceptual hash for deduplication"
    )
    is_duplicate: bool = Field(
        default=False, description="True if this slide duplicates another"
    )


class Scene(BaseModel):
    """A detected scene boundary with associated slides."""

    scene_id: int = Field(..., description="Scene sequence number")
    start_time: float = Field(..., description="Scene start time in seconds")
    end_time: float = Field(..., description="Scene end time in seconds")
    duration: float = Field(..., description="Scene duration in seconds")
    scene_type: str = Field(
        default="slide_change", description="Scene transition type"
    )
    slides: List[SlideImage] = Field(
        default_factory=list, description="Slides extracted from this scene"
    )


class SceneDetectionResult(BaseModel):
    """Complete scene detection and slide extraction output."""

    total_scenes: int = Field(..., description="Number of detected scenes")
    total_slides: int = Field(
        ..., description="Number of extracted slide images"
    )
    scenes: List[Scene] = Field(..., description="Detected scenes with slides")
    slides_dir: str = Field(..., description="Directory containing slide images")
    json_path: str = Field(..., description="Path to scene detection JSON output")
