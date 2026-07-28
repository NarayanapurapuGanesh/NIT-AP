from pathlib import Path
from typing import Union
from loguru import logger
from app.preprocessing.ffmpeg_wrapper import FFmpegWrapper


class AudioExtractor:
    """Extracts 16kHz mono WAV audio stream from video."""

    def __init__(self, ffmpeg_wrapper: Union[FFmpegWrapper, None] = None) -> None:
        self.ffmpeg = ffmpeg_wrapper or FFmpegWrapper()

    def extract_audio(self, video_path: Union[str, Path], output_audio_path: Union[str, Path]) -> Path:
        v_path = Path(video_path).resolve()
        a_path = Path(output_audio_path).resolve()
        a_path.parent.mkdir(parents=True, exist_ok=True)

        args = [
            "-y",
            "-i", str(v_path),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            str(a_path),
        ]
        self.ffmpeg.run_command(args, description="16kHz Audio Extraction")
        return a_path
