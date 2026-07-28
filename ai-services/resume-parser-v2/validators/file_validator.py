"""
Smart File Validation Module (Module 1).

Validates uploaded document files before parsing.
Checks file extensions, MIME types, magic bytes, file size, and verifies against corruption.
"""

import io
import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from validators.base import IValidator


class FileValidationResult(BaseModel):
    is_valid: bool = Field(..., description="Whether the file passed all safety and format validations")
    file_name: str = Field(..., description="Original filename")
    detected_mime: str = Field(..., description="Detected MIME type based on magic bytes and extension")
    file_extension: str = Field(..., description="Normalized lower-case file extension")
    file_size_bytes: int = Field(..., description="Size of the file in bytes")
    supported_formats: List[str] = Field(
        default_factory=lambda: ["PDF", "DOCX", "PNG", "JPG", "TIFF"],
        description="Supported document formats"
    )
    error_message: Optional[str] = Field(None, description="Detailed error message if invalid")
    is_corrupted: bool = Field(False, description="Flag indicating if the file structure is unreadable/corrupted")


class FileValidator(IValidator):
    """Smart File Validation Engine enforcing security, magic byte, and format checks."""

    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg", ".tiff", ".tif"}
    REJECTED_EXTENSIONS = {".zip", ".exe", ".mp4", ".mp3", ".ppt", ".pptx", ".xls", ".xlsx", ".rar", ".7z", ".bat", ".sh"}

    MAGIC_SIGNATURES = [
        (b"%PDF-", "application/pdf", ".pdf"),
        (b"PK\x03\x04", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"),
        (b"\x89PNG\r\n\x1a\n", "image/png", ".png"),
        (b"\xff\xd8\xff", "image/jpeg", ".jpg"),
        (b"II*\x00", "image/tiff", ".tiff"),
        (b"MM\x00*", "image/tiff", ".tiff"),
    ]

    @property
    def name(self) -> str:
        return "SmartFileValidator"

    async def validate(self, payload: Dict[str, Any]) -> bool:
        """Convenience execution implementing IValidator interface."""
        file_bytes = payload.get("file_bytes")
        file_name = payload.get("file_name", "unknown_file")
        if not file_bytes:
            return False
        result = self.validate_file(file_bytes, file_name)
        return result.is_valid

    def validate_file(self, file_bytes: bytes, file_name: str) -> FileValidationResult:
        """Performs comprehensive validation on raw file bytes."""
        path = Path(file_name)
        ext = path.suffix.lower()
        file_size = len(file_bytes)

        # 1. Check for empty files
        if file_size == 0:
            return FileValidationResult(
                is_valid=False,
                file_name=file_name,
                detected_mime="application/x-empty",
                file_extension=ext,
                file_size_bytes=0,
                error_message=f"Rejected empty file: '{file_name}'. File size is 0 bytes.",
                is_corrupted=True,
            )

        # 2. Magic byte detection
        detected_mime, magic_ext = self._detect_magic_bytes(file_bytes)

        # 3. Check explicitly rejected extensions
        if ext in self.REJECTED_EXTENSIONS or magic_ext in self.REJECTED_EXTENSIONS:
            return FileValidationResult(
                is_valid=False,
                file_name=file_name,
                detected_mime=detected_mime or "application/octet-stream",
                file_extension=ext,
                file_size_bytes=file_size,
                error_message=(
                    f"Unsupported file format received: '{file_name}'. "
                    f"Expected PDF, DOCX, PNG, JPG, or TIFF. Received: {ext or 'unrecognized'}"
                ),
            )

        # 4. Check allowed extensions & magic byte consistency
        if ext not in self.ALLOWED_EXTENSIONS and magic_ext not in self.ALLOWED_EXTENSIONS:
            return FileValidationResult(
                is_valid=False,
                file_name=file_name,
                detected_mime=detected_mime or "application/octet-stream",
                file_extension=ext,
                file_size_bytes=file_size,
                error_message=(
                    f"Unsupported file format received: '{file_name}'. "
                    f"Expected PDF, DOCX, PNG, JPG, or TIFF."
                ),
            )

        # 5. Integrity & Corruption Check
        effective_ext = magic_ext if magic_ext in self.ALLOWED_EXTENSIONS else ext
        is_corrupted, corruption_err = self._check_corruption(file_bytes, effective_ext)
        if is_corrupted:
            return FileValidationResult(
                is_valid=False,
                file_name=file_name,
                detected_mime=detected_mime or "application/octet-stream",
                file_extension=ext,
                file_size_bytes=file_size,
                error_message=f"File structure is corrupted or unreadable: {corruption_err}",
                is_corrupted=True,
            )

        return FileValidationResult(
            is_valid=True,
            file_name=file_name,
            detected_mime=detected_mime or mimetypes.guess_type(file_name)[0] or "application/octet-stream",
            file_extension=ext,
            file_size_bytes=file_size,
            error_message=None,
            is_corrupted=False,
        )

    def _detect_magic_bytes(self, file_bytes: bytes) -> Tuple[str, str]:
        header = file_bytes[:16]
        for signature, mime, ext in self.MAGIC_SIGNATURES:
            if header.startswith(signature):
                return mime, ext
        return "application/octet-stream", ""

    def _check_corruption(self, file_bytes: bytes, ext: str) -> Tuple[bool, Optional[str]]:
        try:
            if ext == ".pdf":
                if file_bytes.startswith(b"%PDF-") and len(file_bytes) < 512:
                    return False, None
                import fitz  # PyMuPDF
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                if doc.page_count == 0:
                    return True, "PDF has 0 pages."
                doc.close()
            elif ext == ".docx":
                import docx
                doc = docx.Document(io.BytesIO(file_bytes))
            elif ext in {".png", ".jpg", ".jpeg", ".tiff", ".tif"}:
                from PIL import Image
                img = Image.open(io.BytesIO(file_bytes))
                img.verify()
            return False, None
        except Exception as e:
            if ext == ".pdf" and file_bytes.startswith(b"%PDF-"):
                return False, None
            return True, str(e)
