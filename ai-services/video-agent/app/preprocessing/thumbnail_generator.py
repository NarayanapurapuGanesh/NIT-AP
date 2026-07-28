from pathlib import Path
from typing import Union
from loguru import logger
from app.preprocessing.ffmpeg_wrapper import FFmpegWrapper


class ThumbnailGenerator:
    """Generates frame thumbnails (0.2 fps) and 480p low-res preview video."""

    def __init__(self, ffmpeg_wrapper: Union[FFmpegWrapper, None] = None) -> None:
        self.ffmpeg = ffmpeg_wrapper or FFmpegWrapper()

    def extract_frames(self, video_path: Union[str, Path], output_frames_dir: Union[str, Path], fps: float = 0.2) -> int:
        v_path = Path(video_path).resolve()
        f_dir = Path(output_frames_dir).resolve()
        f_dir.mkdir(parents=True, exist_ok=True)
        pattern = f_dir / "frame_%04d.jpg"

        args = [
            "-y",
            "-i", str(v_path),
            "-vf", f"fps={fps}",
            "-q:v", "3",
            str(pattern),
        ]
        self.ffmpeg.run_command(args, description=f"Frame extraction ({fps} fps)")
        extracted = list(f_dir.glob("frame_*.jpg"))
        return len(extracted)

    def generate_480p_preview(self, video_path: Union[str, Path], output_preview_path: Union[str, Path]) -> Path:
        v_path = Path(video_path).resolve()
        p_path = Path(output_preview_path).resolve()
        p_path.parent.mkdir(parents=True, exist_ok=True)

        args = [
            "-y",
            "-i", str(v_path),
            "-vf", "scale=-2:480",
            "-c:v", "libx264",
            "-crf", "30",
            "-preset", "ultrafast",
            "-c:a", "aac",
            "-b:a", "64k",
            str(p_path),
        ]
        self.ffmpeg.run_command(args, description="480p Preview Generation")
        return p_path
