"""
FacultyIQ Video Evidence Extraction Service — Video Preprocessor (Module 2).

Creates temporary workspace, normalizes video, extracts audio, generates preview,
and caches metadata for downstream pipeline modules.
"""

import json
import shutil
import uuid
from pathlib import Path
from typing import Optional, Union

from app.config.settings import settings
from app.core.logging import get_module_logger
from app.models.validation import VideoMetadata
from app.preprocessing.audio_extractor import AudioExtractor
from app.preprocessing.ffmpeg_wrapper import FFmpegWrapper
from app.utils.file_utils import ensure_directory

log = get_module_logger("preprocessing")


class PreprocessingResult:
    """Holds paths and metadata generated during preprocessing."""

    def __init__(
        self,
        workspace_dir: Path,
        normalized_video_path: Path,
        audio_path: Path,
        preview_path: Path,
        metadata_path: Path,
    ) -> None:
        self.workspace_dir = workspace_dir
        self.normalized_video_path = normalized_video_path
        self.audio_path = audio_path
        self.preview_path = preview_path
        self.metadata_path = metadata_path


class VideoPreprocessor:
    """Normalizes video, extracts audio, and generates preview."""

    def __init__(
        self,
        audio_extractor: Optional[AudioExtractor] = None,
        ffmpeg_wrapper: Optional[FFmpegWrapper] = None,
    ) -> None:
        self._audio_extractor = audio_extractor or AudioExtractor()
        self._ffmpeg = ffmpeg_wrapper or FFmpegWrapper()

    def process(
        self,
        video_path: Union[str, Path],
        job_id: Optional[str] = None,
        metadata: Optional[VideoMetadata] = None,
    ) -> PreprocessingResult:
        """Runs complete preprocessing: normalize, extract audio, generate preview."""
        v_path = Path(video_path).resolve()
        j_id = job_id or str(uuid.uuid4())

        workspace = ensure_directory(
            settings.base_dir / settings.storage.output_dir / j_id
        )
        log.info("[{}] Preprocessing video: '{}' → workspace: {}", j_id, v_path.name, workspace)

        norm_path = workspace / f"input_video{v_path.suffix}"
        if not norm_path.exists():
            shutil.copy2(v_path, norm_path)
            log.info("[{}] Video copied to workspace: {}", j_id, norm_path.name)

        audio_path = workspace / "audio.wav"
        self._audio_extractor.extract_audio(norm_path, audio_path)

        preview_path = workspace / "preview.mp4"
        self._generate_preview(norm_path, preview_path)

        metadata_path = workspace / "metadata.json"
        meta_dict = metadata.model_dump() if metadata else {"source": str(v_path)}
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(meta_dict, f, indent=2, default=str)

        log.info("[{}] Preprocessing completed successfully.", j_id)

        return PreprocessingResult(
            workspace_dir=workspace,
            normalized_video_path=norm_path,
            audio_path=audio_path,
            preview_path=preview_path,
            metadata_path=metadata_path,
        )

    def _generate_preview(
        self, video_path: Path, output_path: Path
    ) -> None:
        """Generates a 480p low-resolution preview video."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        args = [
            "-y",
            "-i", str(video_path),
            "-vf", "scale=-2:480",
            "-c:v", "libx264",
            "-crf", "30",
            "-preset", "ultrafast",
            "-c:a", "aac",
            "-b:a", "64k",
            str(output_path),
        ]
        self._ffmpeg.run_command(args, description="480p Preview Generation")
