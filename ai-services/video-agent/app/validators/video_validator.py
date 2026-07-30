"""
FacultyIQ Video Evidence Extraction Service — Video Validator (Module 1).

Validates video files for supported formats, MIME type, duration, resolution,
audio presence, corruption, and codec compatibility via FFprobe.
"""

import mimetypes
import subprocess
from pathlib import Path
from typing import Optional, Union

from app.config.settings import settings
from app.core.logging import get_module_logger
from app.models.validation import ValidationResult, VideoMetadata

log = get_module_logger("validation")


class VideoValidator:
    """Validates uploaded video files and extracts comprehensive metadata."""

    def __init__(self) -> None:
        self._allowed_extensions = set(settings.validation.allowed_extensions)
        self._allowed_mimes = set(settings.validation.allowed_mime_types)
        self._max_size = settings.validation.max_file_size_mb * 1024 * 1024
        self._min_duration = settings.validation.min_duration_seconds
        self._max_duration = settings.validation.max_duration_seconds

    def validate(self, video_path: Union[str, Path]) -> ValidationResult:
        """Performs comprehensive video validation and metadata extraction."""
        v_path = Path(video_path).resolve()
        errors: list[str] = []
        warnings: list[str] = []

        if not v_path.exists():
            return ValidationResult(
                validation_passed=False,
                errors=[f"File does not exist: {v_path}"],
            )

        ext = v_path.suffix.lower()
        if ext not in self._allowed_extensions:
            return ValidationResult(
                validation_passed=False,
                errors=[
                    f"Unsupported format '{ext}'. Allowed: {sorted(self._allowed_extensions)}"
                ],
            )

        mime_type, _ = mimetypes.guess_type(str(v_path))
        if mime_type and mime_type not in self._allowed_mimes:
            warnings.append(
                f"MIME type '{mime_type}' not in allowed list. Proceeding with caution."
            )

        file_size = v_path.stat().st_size
        if file_size == 0:
            return ValidationResult(
                validation_passed=False,
                errors=["Uploaded file is empty (0 bytes)."],
            )
        if file_size > self._max_size:
            return ValidationResult(
                validation_passed=False,
                errors=[
                    f"File size ({file_size / (1024 * 1024):.1f} MB) exceeds "
                    f"maximum {settings.validation.max_file_size_mb} MB limit."
                ],
            )

        probe_data = self._probe_video(v_path)
        if probe_data is None:
            return ValidationResult(
                validation_passed=False,
                errors=["Corrupted video file or unreadable media stream."],
            )

        duration = probe_data.get("duration", 0.0)
        if duration < self._min_duration:
            errors.append(
                f"Video duration ({duration:.1f}s) is shorter than "
                f"minimum required {self._min_duration}s."
            )
        if duration > self._max_duration:
            errors.append(
                f"Video duration ({duration:.1f}s) exceeds "
                f"maximum allowed {self._max_duration}s."
            )

        has_audio = probe_data.get("has_audio", False)
        if not has_audio:
            errors.append("No audio stream detected in video file.")

        metadata = VideoMetadata(
            filename=v_path.name,
            format=ext.lstrip("."),
            mime_type=mime_type,
            file_size_bytes=file_size,
            file_size_mb=round(file_size / (1024 * 1024), 2),
            duration_seconds=round(duration, 2),
            width=probe_data.get("width", 0),
            height=probe_data.get("height", 0),
            fps=probe_data.get("fps", 0.0),
            bitrate=probe_data.get("bitrate"),
            video_codec=probe_data.get("video_codec", "unknown"),
            audio_codec=probe_data.get("audio_codec"),
            has_audio=has_audio,
            audio_channels=probe_data.get("audio_channels"),
            sample_rate=probe_data.get("sample_rate"),
        )

        passed = len(errors) == 0
        log.info(
            "Validation {} for '{}': duration={:.1f}s, resolution={}x{}, audio={}",
            "PASSED" if passed else "FAILED",
            v_path.name,
            duration,
            metadata.width,
            metadata.height,
            has_audio,
        )

        return ValidationResult(
            validation_passed=passed,
            metadata=metadata,
            warnings=warnings,
            errors=errors,
        )

    def _probe_video(self, v_path: Path) -> Optional[dict]:
        """Extracts video metadata using FFprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries",
                "format=duration,size,bit_rate:"
                "stream=codec_type,codec_name,width,height,r_frame_rate,"
                "channels,sample_rate",
                "-of", "default=noprint_wrappers=1",
                str(v_path),
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=30
            )
            return self._parse_ffprobe_output(result.stdout.strip())
        except subprocess.TimeoutExpired:
            log.error("FFprobe timed out for '{}'", v_path.name)
            return None
        except Exception as exc:
            log.error("FFprobe execution failed for '{}': {}", v_path.name, exc)
            return None

    def _parse_ffprobe_output(self, output: str) -> dict:
        """Parses FFprobe key=value output into a structured dict."""
        data: dict = {
            "duration": 0.0,
            "width": 0,
            "height": 0,
            "fps": 0.0,
            "bitrate": None,
            "video_codec": "unknown",
            "audio_codec": None,
            "has_audio": False,
            "audio_channels": None,
            "sample_rate": None,
        }

        current_codec_type: Optional[str] = None
        video_codec_found = False

        for line in output.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()

            if not value or value == "N/A":
                continue

            if key == "codec_type":
                current_codec_type = value
                if value == "audio":
                    data["has_audio"] = True

            elif key == "codec_name":
                if current_codec_type == "video" and not video_codec_found:
                    data["video_codec"] = value
                    video_codec_found = True
                elif current_codec_type == "audio" and data["audio_codec"] is None:
                    data["audio_codec"] = value

            elif key == "duration":
                try:
                    data["duration"] = float(value)
                except ValueError:
                    pass

            elif key == "width":
                try:
                    data["width"] = int(value)
                except ValueError:
                    pass

            elif key == "height":
                try:
                    data["height"] = int(value)
                except ValueError:
                    pass

            elif key == "r_frame_rate":
                try:
                    if "/" in value:
                        num, den = value.split("/")
                        den_val = int(den)
                        if den_val > 0:
                            data["fps"] = round(int(num) / den_val, 2)
                    else:
                        data["fps"] = round(float(value), 2)
                except (ValueError, ZeroDivisionError):
                    pass

            elif key == "bit_rate":
                try:
                    data["bitrate"] = int(value)
                except ValueError:
                    pass

            elif key == "channels":
                try:
                    data["audio_channels"] = int(value)
                except ValueError:
                    pass

            elif key == "sample_rate":
                try:
                    data["sample_rate"] = int(value)
                except ValueError:
                    pass

        return data
