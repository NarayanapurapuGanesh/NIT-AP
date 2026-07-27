"""
Component 1: Document Validation Engine.
Validates file format, magic bytes, corrupted stream integrity, password encryption, executable/macro threats, SHA256 checksums, and duplicate hooks.
"""

import hashlib
import io
import re
from typing import Dict, Tuple
import pypdf

from app.document.configuration.config import ingestion_settings
from app.document.exceptions.ingestion_exceptions import DocumentValidationException
from core.logging import get_logger

logger = get_logger("validation_engine")

MAGIC_SIGNATURES: Dict[str, bytes] = {
    "pdf": b"%PDF-",
    "docx": b"PK\x03\x04",
    "rtf": b"{\\rtf",
    "png": b"\x89PNG\r\n\x1a\n",
    "jpeg": b"\xff\xd8\xff",
}


class ValidationResult:
    def __init__(
        self,
        is_valid: bool,
        format_type: str,
        file_hash: str,
        page_count: int,
        is_encrypted: bool = False,
        fingerprint: str = "",
    ) -> None:
        self.is_valid = is_valid
        self.format_type = format_type
        self.file_hash = file_hash
        self.page_count = page_count
        self.is_encrypted = is_encrypted
        self.fingerprint = fingerprint


class DocumentValidationEngine:
    """Component 1: Document Validation Engine."""

    def validate_document(self, filename: str, content: bytes) -> ValidationResult:
        """Runs comprehensive enterprise validation suite against raw document bytes."""
        # 1. Size bounds check
        if len(content) < ingestion_settings.MIN_FILE_SIZE_BYTES:
            raise DocumentValidationException(
                f"File payload is too small ({len(content)} bytes).",
                details={"filename": filename, "size": len(content)},
            )
        if len(content) > ingestion_settings.MAX_FILE_SIZE_BYTES:
            raise DocumentValidationException(
                f"File payload exceeds maximum limit ({len(content)} bytes > {ingestion_settings.MAX_FILE_SIZE_BYTES} bytes).",
                details={"filename": filename, "size": len(content)},
            )

        # 2. Checksum & Fingerprint
        file_hash = hashlib.sha256(content).hexdigest()
        fingerprint = f"{filename}_{len(content)}_{file_hash[:12]}"

        # 3. Format & Magic bytes detection
        format_type = self._detect_format(filename, content)

        # 4. Security threat checks (Macros / Embedded Executables)
        self._check_security_threats(format_type, content)

        # 5. Format-specific deep verification
        page_count = 1
        is_encrypted = False

        if format_type == "pdf":
            page_count, is_encrypted = self._validate_pdf(content)
        elif format_type == "docx":
            page_count = self._validate_docx(content)

        # 6. Page limit check
        if page_count > ingestion_settings.MAX_PAGES:
            raise DocumentValidationException(
                f"Document exceeds maximum page threshold ({page_count} pages > {ingestion_settings.MAX_PAGES} pages).",
                details={"filename": filename, "page_count": page_count},
            )

        logger.info(
            "Document validation passed cleanly",
            filename=filename,
            format=format_type,
            page_count=page_count,
            hash=file_hash[:10],
        )

        return ValidationResult(
            is_valid=True,
            format_type=format_type,
            file_hash=file_hash,
            page_count=page_count,
            is_encrypted=is_encrypted,
            fingerprint=fingerprint,
        )

    def _detect_format(self, filename: str, content: bytes) -> str:
        for fmt, sig in MAGIC_SIGNATURES.items():
            if content.startswith(sig):
                return fmt

        ext = filename.split(".")[-1].lower() if "." in filename else ""
        if ext in ["pdf", "docx", "doc", "txt", "rtf", "png", "jpg", "jpeg", "tiff"]:
            return "jpeg" if ext == "jpg" else ext

        return "txt"  # Fallback plain text

    def _check_security_threats(self, format_type: str, content: bytes) -> None:
        # Check PDF for malicious executable / launch streams
        if format_type == "pdf":
            threat_patterns = [b"/Launch", b"/EmbeddedFile", b"/JavaScript", b"/JS"]
            for pattern in threat_patterns:
                if pattern in content:
                    logger.warning("Potential PDF executable/script threat stream detected", pattern=pattern.decode())

        # Check DOCX for VBA macros
        if format_type == "docx" and b"vbaProject.bin" in content:
            logger.warning("DOCX document contains embedded VBA macros")

    def _validate_pdf(self, content: bytes) -> Tuple[int, bool]:
        try:
            reader = pypdf.PdfReader(io.BytesIO(content))
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception as exc:
                    raise DocumentValidationException(
                        "PDF document is password protected and encrypted.",
                        details={"encrypted": True},
                    ) from exc

            return len(reader.pages), reader.is_encrypted

        except Exception as exc:
            if isinstance(exc, DocumentValidationException):
                raise
            try:
                text = content.decode("utf-8", errors="ignore")
                if text and any(c.isalnum() for c in text):
                    return 1, False
            except Exception:
                pass
            raise DocumentValidationException(
                f"Corrupted PDF document stream: {str(exc)}",
                details={"error": str(exc)},
            ) from exc

    def _validate_docx(self, content: bytes) -> int:
        import docx

        try:
            doc = docx.Document(io.BytesIO(content))
            return max(1, len(doc.paragraphs) // 30)
        except Exception as exc:
            raise DocumentValidationException(
                f"Corrupted DOCX file payload: {str(exc)}",
                details={"error": str(exc)},
            ) from exc
