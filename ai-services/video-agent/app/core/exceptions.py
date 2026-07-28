from typing import Any, Dict, Optional


class VideoAgentError(Exception):
    """Base domain exception for FacultyIQ Video Evaluation Agent."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(VideoAgentError):
    """Raised when Phase 1 video upload validation fails."""
    pass


class PreprocessingError(VideoAgentError):
    """Raised when Phase 2 video/audio preprocessing fails."""
    pass


class TranscriptionError(VideoAgentError):
    """Raised when Phase 3 speech transcription fails."""
    pass


class SceneDetectionError(VideoAgentError):
    """Raised when Phase 4 scene detection fails."""
    pass


class OCRError(VideoAgentError):
    """Raised when Phase 5 OCR extraction fails."""
    pass


class VisualAnalysisError(VideoAgentError):
    """Raised when Phase 6 MediaPipe analysis fails."""
    pass


class VoiceAnalysisError(VideoAgentError):
    """Raised when Phase 7 signal voice analysis fails."""
    pass


class TeachingAnalysisError(VideoAgentError):
    """Raised when Phase 8 teaching intelligence analysis fails."""
    pass


class EvaluationError(VideoAgentError):
    """Raised when Phase 9 evidence assembly, scoring, or report generation fails."""
    pass
