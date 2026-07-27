"""
Domain exception hierarchy for Document Ingestion & Extraction Engine.
"""

from typing import Any, Dict, Optional
from core.exceptions import BaseAppException


class DocumentIngestionException(BaseAppException):
    """Base exception for all document ingestion and extraction pipeline errors."""

    def __init__(
        self,
        message: str = "Document ingestion failed.",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message=message, status_code=status_code, details=details)


class DocumentValidationException(DocumentIngestionException):
    """Raised when file validation fails (corrupted file, password protected, size/page limit exceeded)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=400, details=details)


class DocumentClassificationException(DocumentIngestionException):
    """Raised when document classification fails or encounters an unhandled file type."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=422, details=details)


class ExtractionException(DocumentIngestionException):
    """Raised when primary/fallback text extraction fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)


class OcrException(DocumentIngestionException):
    """Raised when OCR fallback processing encounters an error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)


class LayoutException(DocumentIngestionException):
    """Raised when layout analysis or reading order reconstruction fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)
