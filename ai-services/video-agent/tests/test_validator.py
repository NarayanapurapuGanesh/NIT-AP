"""Tests for Module 1: Video Validation."""

from pathlib import Path

import pytest

from app.models.validation import ValidationResult, VideoMetadata
from app.validators.video_validator import VideoValidator


class TestVideoValidator:
    """Tests for VideoValidator validation logic."""

    def setup_method(self):
        self.validator = VideoValidator()

    def test_validate_nonexistent_file(self, tmp_path: Path):
        """Validation fails for a file that does not exist."""
        result = self.validator.validate(tmp_path / "nonexistent.mp4")
        assert result.validation_passed is False
        assert any("does not exist" in e for e in result.errors)

    def test_validate_unsupported_extension(self, tmp_path: Path):
        """Validation fails for unsupported file formats."""
        bad_file = tmp_path / "video.xyz"
        bad_file.write_bytes(b"\x00" * 100)
        result = self.validator.validate(bad_file)
        assert result.validation_passed is False
        assert any("Unsupported format" in e for e in result.errors)

    def test_validate_empty_file(self, tmp_path: Path):
        """Validation fails for empty files."""
        empty_file = tmp_path / "empty.mp4"
        empty_file.write_bytes(b"")
        result = self.validator.validate(empty_file)
        assert result.validation_passed is False
        assert any("empty" in e.lower() for e in result.errors)

    def test_validate_oversized_file(self, tmp_path: Path):
        """Validation fails for files exceeding the max size limit."""
        large_file = tmp_path / "large.mp4"
        large_file.write_bytes(b"\x00" * (501 * 1024 * 1024))
        result = self.validator.validate(large_file)
        assert result.validation_passed is False
        assert any("exceeds" in e.lower() for e in result.errors)

    def test_validation_result_model(self):
        """ValidationResult model can be instantiated correctly."""
        result = ValidationResult(
            validation_passed=True,
            metadata=VideoMetadata(
                filename="test.mp4",
                format="mp4",
                file_size_bytes=1024,
                file_size_mb=0.001,
                duration_seconds=30.0,
                width=1920,
                height=1080,
                fps=30.0,
                video_codec="h264",
                has_audio=True,
            ),
        )
        assert result.validation_passed is True
        assert result.metadata is not None
        assert result.metadata.resolution == "1920x1080"

    def test_video_metadata_resolution(self):
        """VideoMetadata resolution property works correctly."""
        meta = VideoMetadata(
            filename="test.mp4",
            format="mp4",
            file_size_bytes=1024,
            file_size_mb=0.001,
            duration_seconds=60.0,
            width=1280,
            height=720,
            fps=24.0,
            video_codec="h264",
            has_audio=False,
        )
        assert meta.resolution == "1280x720"
