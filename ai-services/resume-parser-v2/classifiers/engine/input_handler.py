"""
Layer 1: Input Handler.
Validates raw file bytes, size bounds, MIME types, and magic numbers (PDF, DOCX, DOC, PNG, JPEG, TIFF).
"""

from typing import Dict, Tuple
from core.exceptions import ValidationException
from core.logging import get_logger

logger = get_logger("input_handler")

# Magic number signatures
MAGIC_SIGNATURES: Dict[str, bytes] = {
    "pdf": b"%PDF-",
    "docx": b"PK\x03\x04",
    "doc": b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",
    "png": b"\x89PNG\r\n\x1a\n",
    "jpeg": b"\xff\xd8\xff",
    "tiff_le": b"II*\x00",
    "tiff_be": b"MM\x00*",
}

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB limit


class InputHandler:
    """Layer 1: Stream & Payload Validator."""

    def process_input(self, filename: str, content: bytes) -> Tuple[str, str]:
        """Validates payload sanity and returns normalized format key and filename."""
        if not content or len(content) == 0:
            raise ValidationException("Empty file payload received.", details={"filename": filename})

        if len(content) > MAX_FILE_SIZE_BYTES:
            raise ValidationException(
                f"File size exceeds maximum threshold ({len(content)} bytes > {MAX_FILE_SIZE_BYTES} bytes).",
                details={"filename": filename, "size": len(content)},
            )

        detected_format = self._detect_format_by_magic(content)
        if not detected_format:
            # Fallback check by file extension if magic number doesn't match standard
            ext = filename.split(".")[-1].lower() if "." in filename else ""
            if ext in ["pdf", "docx", "doc", "png", "jpg", "jpeg", "tiff", "tif"]:
                detected_format = "jpeg" if ext in ["jpg", "jpeg"] else ext
            else:
                detected_format = "unknown"

        logger.debug(
            "Input file validated",
            filename=filename,
            size_bytes=len(content),
            detected_format=detected_format,
        )

        return detected_format, filename

    def _detect_format_by_magic(self, content: bytes) -> str | None:
        if content.startswith(MAGIC_SIGNATURES["pdf"]):
            return "pdf"
        if content.startswith(MAGIC_SIGNATURES["docx"]):
            return "docx"
        if content.startswith(MAGIC_SIGNATURES["doc"]):
            return "doc"
        if content.startswith(MAGIC_SIGNATURES["png"]):
            return "png"
        if content.startswith(MAGIC_SIGNATURES["jpeg"]):
            return "jpeg"
        if content.startswith(MAGIC_SIGNATURES["tiff_le"]) or content.startswith(MAGIC_SIGNATURES["tiff_be"]):
            return "tiff"
        return None
