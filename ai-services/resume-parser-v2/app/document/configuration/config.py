"""
Document Ingestion & Extraction Engine Configuration Settings.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DocumentIngestionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INGEST_",
        env_file=".env",
        extra="ignore",
    )

    MAX_PAGES: int = Field(default=150, description="Maximum supported document page count (handles 100+ page CVs)")
    MAX_FILE_SIZE_BYTES: int = Field(default=100 * 1024 * 1024, description="100 MB max document size limit")
    MIN_FILE_SIZE_BYTES: int = Field(default=10, description="Minimum byte size limit")
    OCR_CONFIDENCE_THRESHOLD: float = Field(default=0.60, description="Threshold triggering OCR fallback")
    OCR_ENABLED: bool = Field(default=True, description="Enable pluggable OCR fallback engine")
    PRIMARY_PDF_ENGINE: str = Field(default="pymupdf", description="Primary PDF extraction engine")
    FALLBACK_PDF_ENGINE: str = Field(default="pdfplumber", description="Fallback PDF extraction engine")
    SUPPORTED_FORMATS: List[str] = Field(
        default=["pdf", "docx", "txt", "rtf", "png", "jpeg", "tiff"],
        description="Supported file formats",
    )
    TIMEOUT_SECONDS: int = Field(default=120, description="Document processing timeout in seconds")


ingestion_settings = DocumentIngestionSettings()
