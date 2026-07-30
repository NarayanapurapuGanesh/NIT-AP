"""
FacultyIQ Video Evidence Extraction Service — Audio Extractor.

Extracts 16kHz mono WAV audio stream from video for transcription.
"""

from pathlib import Path
from typing import Optional, Union

from app.core.logging import get_module_logger
from app.preprocessing.ffmpeg_wrapper import FFmpegWrapper

log = get_module_logger("preprocessing")


class AudioExtractor:
    """Extracts audio from video in Whisper-compatible format (16kHz mono WAV)."""

    def __init__(
        self,
        ffmpeg_wrapper: Optional[FFmpegWrapper] = None,
        sample_rate: int = 16000,
    ) -> None:
        self._ffmpeg = ffmpeg_wrapper or FFmpegWrapper()
        self._sample_rate = sample_rate

    def extract_audio(
        self,
        video_path: Union[str, Path],
        output_path: Union[str, Path],
    ) -> Path:
        """Extracts audio as 16kHz mono PCM WAV."""
        v_path = Path(video_path).resolve()
        a_path = Path(output_path).resolve()
        a_path.parent.mkdir(parents=True, exist_ok=True)

        log.info("Extracting audio from '{}' → '{}'", v_path.name, a_path.name)

        args = [
            "-y",
            "-i", str(v_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", str(self._sample_rate),
            "-ac", "1",
            str(a_path),
        ]
        self._ffmpeg.run_command(args, description="Audio Extraction (16kHz mono WAV)")

        if not a_path.exists() or a_path.stat().st_size == 0:
            raise FileNotFoundError(f"Audio extraction produced no output: {a_path}")

        log.info(
            "Audio extracted successfully: {} ({:.1f} MB)",
            a_path.name,
            a_path.stat().st_size / (1024 * 1024),
        )
        return a_path
