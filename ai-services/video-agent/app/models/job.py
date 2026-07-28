from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.validation import VideoMetadata


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PreprocessingResult(BaseModel):
    normalized_video_path: str
    audio_path: str
    frames_dir: str
    preview_480p_path: str
    frame_count: int
    metadata_cache_path: str


class TranscriptionSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str


class TranscriptionResult(BaseModel):
    full_text: str
    segments: List[TranscriptionSegment]
    json_path: str
    srt_path: str
    txt_path: str


class PipelineResult(BaseModel):
    video_metadata: VideoMetadata
    preprocessing: PreprocessingResult
    transcription: TranscriptionResult


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    result: Optional[PipelineResult] = None
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
