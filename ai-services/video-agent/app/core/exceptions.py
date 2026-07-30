"""
FacultyIQ Video Evidence Extraction Service — Domain Exceptions.

Each exception maps to a specific pipeline module for precise error handling.
"""

from typing import Any, Dict, Optional


class VideoAgentError(Exception):
    """Base domain exception for FacultyIQ Video Evidence Extraction Service."""

    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(VideoAgentError):
    """Raised when video upload validation fails (format, size, duration, codecs, audio)."""

    pass


class PreprocessingError(VideoAgentError):
    """Raised when video or audio preprocessing fails."""

    pass


class TranscriptionError(VideoAgentError):
    """Raised when speech transcription via Faster-Whisper fails."""

    pass


class SceneDetectionError(VideoAgentError):
    """Raised when scene detection or keyframe extraction fails."""

    pass


class OCRError(VideoAgentError):
    """Raised when Tesseract OCR extraction fails."""

    pass


class TimelineError(VideoAgentError):
    """Raised when timeline merging fails."""

    pass


class SummaryError(VideoAgentError):
    """Raised when teaching summary generation fails."""

    pass


class VoiceAnalysisError(VideoAgentError):
    """Raised when voice metrics analysis fails."""

    pass


class StorageError(VideoAgentError):
    """Raised when output file storage operations fail."""

    pass


class GPUDetectionError(VideoAgentError):
    """Raised when GPU detection encounters an unrecoverable error."""

    pass


class PipelineError(VideoAgentError):
    """Raised when the pipeline orchestrator encounters a fatal error."""

    pass
