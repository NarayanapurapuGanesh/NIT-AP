"""
FacultyIQ Video Evidence Extraction Service — Transcription Models.

Pydantic v2 models for speech transcription segments, word timestamps, and results.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class WordTimestamp(BaseModel):
    """Individual word-level timestamp from Whisper."""

    word: str = Field(..., description="Transcribed word")
    start: float = Field(..., description="Word start time in seconds")
    end: float = Field(..., description="Word end time in seconds")
    probability: float = Field(..., description="Word-level confidence probability")


class Segment(BaseModel):
    """A single transcription segment with timing and confidence."""

    id: int = Field(..., description="Segment sequence number")
    start: float = Field(..., description="Segment start time in seconds")
    end: float = Field(..., description="Segment end time in seconds")
    text: str = Field(..., description="Transcribed text content")
    confidence: float = Field(
        default=0.0, description="Average segment confidence (0.0–1.0)"
    )
    speaker: Optional[str] = Field(
        None, description="Speaker label (reserved for diarization)"
    )
    words: List[WordTimestamp] = Field(
        default_factory=list, description="Word-level timestamps"
    )


class TranscriptionResult(BaseModel):
    """Complete transcription output for a video."""

    full_text: str = Field(..., description="Full concatenated transcript text")
    segments: List[Segment] = Field(..., description="Time-aligned segments")
    language: str = Field(default="en", description="Detected or configured language")
    model_used: str = Field(default="small", description="Whisper model size used")
    duration_seconds: float = Field(
        default=0.0, description="Audio duration in seconds"
    )
    json_path: str = Field(..., description="Path to transcript.json output file")
    txt_path: str = Field(..., description="Path to transcript.txt output file")
