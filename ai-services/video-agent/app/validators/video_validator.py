import subprocess
from pathlib import Path
from typing import Union
from loguru import logger

from app.core.exceptions import ValidationError
from app.models.validation import ValidationResult, VideoMetadata


class VideoValidator:
    """Phase 1: Video Upload Validator using FFprobe."""

    ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB limit
    MIN_DURATION_SECONDS = 10.0  # 10s minimum

    def validate(self, video_path: Union[str, Path]) -> ValidationResult:
        """Inspects video file metadata, duration, streams, and codecs."""
        v_path = Path(video_path).resolve()
        errors = []
        warnings = []

        if not v_path.exists():
            return ValidationResult(validationPassed=False, errors=[f"File does not exist: {v_path}"])

        if v_path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            return ValidationResult(validationPassed=False, errors=[f"Unsupported file format '{v_path.suffix}'. Allowed: {self.ALLOWED_EXTENSIONS}"])

        file_size = v_path.stat().st_size
        if file_size == 0:
            return ValidationResult(validationPassed=False, errors=["Uploaded file is empty (0 bytes)."])

        if file_size > self.MAX_FILE_SIZE_BYTES:
            return ValidationResult(validationPassed=False, errors=[f"File size exceeds maximum 500MB limit: {file_size / (1024*1024):.1f} MB"])

        # Probe video using FFprobe
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate",
                "-of", "default=noprint_wrappers=1",
                str(v_path),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = res.stdout.strip()
        except Exception as e:
            logger.error(f"FFprobe execution failed for {v_path.name}: {e}")
            return ValidationResult(validationPassed=False, errors=[f"Corrupted video file or unreadable media stream: {e}"])

        # Parse FFprobe output
        duration = 0.0
        width, height = 1280, 720
        fps = 30.0
        v_codec = "h264"
        a_codec = None
        has_audio = False

        for line in output.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if k == "duration":
                    try: duration = float(v)
                    except ValueError: pass
                elif k == "width":
                    try: width = int(v)
                    except ValueError: pass
                elif k == "height":
                    try: height = int(v)
                    except ValueError: pass
                elif k == "codec_type" and v == "audio":
                    has_audio = True
                elif k == "codec_name" and has_audio and not a_codec:
                    a_codec = v
                elif k == "codec_name" and not v_codec:
                    v_codec = v

        if duration < self.MIN_DURATION_SECONDS:
            errors.append(f"Video duration ({duration:.1f}s) is shorter than minimum required 10 seconds.")

        if not has_audio:
            errors.append("No audio stream detected in video file.")

        metadata = VideoMetadata(
            format=v_path.suffix.lower().lstrip("."),
            file_size_bytes=file_size,
            file_size_mb=round(file_size / (1024 * 1024), 2),
            duration_seconds=round(duration, 2),
            width=width,
            height=height,
            fps=fps,
            video_codec=v_codec,
            audio_codec=a_codec,
            has_audio=has_audio,
        )

        passed = len(errors) == 0
        return ValidationResult(
            validationPassed=passed,
            metadata=metadata,
            warnings=warnings,
            errors=errors,
        )
