"""
FacultyIQ Video Evidence Extraction Service — Job Models.

Pydantic v2 models for job tracking, status, and pipeline results.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Pipeline job execution status."""

    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class ModuleStatus(str, Enum):
    """Individual module execution status."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"


class ProcessingStep(BaseModel):
    """Tracks the status of an individual pipeline module."""

    module_name: str = Field(..., description="Module identifier")
    status: ModuleStatus = Field(
        default=ModuleStatus.PENDING, description="Current module status"
    )
    started_at: Optional[str] = Field(None, description="ISO timestamp when started")
    completed_at: Optional[str] = Field(
        None, description="ISO timestamp when completed"
    )
    duration_seconds: Optional[float] = Field(
        None, description="Execution duration in seconds"
    )
    error: Optional[str] = Field(
        None, description="Error message if module failed"
    )


class JobOutputPaths(BaseModel):
    """Paths to all generated output files for a completed job."""

    metadata_json: Optional[str] = None
    transcript_json: Optional[str] = None
    transcript_txt: Optional[str] = None
    slides_dir: Optional[str] = None
    ocr_json: Optional[str] = None
    ocr_txt: Optional[str] = None
    timeline_json: Optional[str] = None
    summary_json: Optional[str] = None
    gallery_json: Optional[str] = None
    gallery_pdf: Optional[str] = None
    gallery_zip: Optional[str] = None
    voice_json: Optional[str] = None
    report_json: Optional[str] = None


class JobResponse(BaseModel):
    """Complete job status response including per-module progress and output paths."""

    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Overall job status")
    message: str = Field(default="", description="Human-readable status message")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Job creation timestamp",
    )
    completed_at: Optional[str] = Field(
        None, description="Job completion timestamp"
    )
    video_filename: Optional[str] = Field(
        None, description="Original uploaded video filename"
    )
    steps: List[ProcessingStep] = Field(
        default_factory=list, description="Per-module processing status"
    )
    output: Optional[JobOutputPaths] = Field(
        None, description="Output file paths when job completes"
    )
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
