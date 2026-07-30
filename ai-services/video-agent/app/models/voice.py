"""
FacultyIQ Video Evidence Extraction Service — Voice Analysis Models.

Pydantic v2 models for optional voice metrics extraction.
"""

from typing import Optional

from pydantic import BaseModel, Field


class VoiceMetrics(BaseModel):
    """Voice analysis metrics extracted from audio via librosa/scipy."""

    speech_rate_wpm: float = Field(
        ..., description="Estimated speech rate in words per minute"
    )
    pause_ratio: float = Field(
        ..., description="Ratio of silence to total duration (0.0–1.0)"
    )
    average_pitch_hz: float = Field(
        ..., description="Average fundamental frequency in Hz"
    )
    volume_stability: float = Field(
        ..., description="Standard deviation of RMS energy (lower = more stable)"
    )
    noise_level_db: float = Field(
        ..., description="Estimated background noise level in dB"
    )
    confidence: float = Field(
        ..., description="Overall confidence in metrics accuracy (0.0–1.0)"
    )


class VoiceAnalysisResult(BaseModel):
    """Complete voice analysis output."""

    enabled: bool = Field(
        ..., description="Whether voice analysis was enabled and executed"
    )
    metrics: Optional[VoiceMetrics] = Field(
        None, description="Voice metrics (None when disabled)"
    )
    json_path: Optional[str] = Field(
        None, description="Path to voice analysis JSON output"
    )
