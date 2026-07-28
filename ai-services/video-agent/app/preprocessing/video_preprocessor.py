import json
import uuid
from pathlib import Path
from typing import Optional, Union
from loguru import logger

from app.config.settings import settings
from app.models.job import PreprocessingResult
from app.models.validation import VideoMetadata
from app.preprocessing.audio_extractor import AudioExtractor
from app.preprocessing.thumbnail_generator import ThumbnailGenerator
from app.utils.file_utils import ensure_directory


class VideoPreprocessor:
    """Phase 2: Video & Audio Preprocessor."""

    def __init__(
        self,
        audio_extractor: Optional[AudioExtractor] = None,
        thumbnail_generator: Optional[ThumbnailGenerator] = None,
    ) -> None:
        self.audio_extractor = audio_extractor or AudioExtractor()
        self.thumbnail_generator = thumbnail_generator or ThumbnailGenerator()

    def process(
        self,
        video_path: Union[str, Path],
        job_id: Optional[str] = None,
        metadata: Optional[VideoMetadata] = None,
    ) -> PreprocessingResult:
        v_path = Path(video_path).resolve()
        j_id = job_id or str(uuid.uuid4())
        out_dir = ensure_directory(settings.base_dir / settings.storage.output_dir / j_id)

        # 1. Normalize video path (copy or use original)
        norm_video_path = out_dir / f"input_video{v_path.suffix}"
        if not norm_video_path.exists():
            import shutil
            shutil.copy2(v_path, norm_video_path)

        # 2. Extract 16kHz mono audio
        audio_path = out_dir / "extracted_audio.wav"
        self.audio_extractor.extract_audio(norm_video_path, audio_path)

        # 3. Extract frames thumbnails
        frames_dir = out_dir / "frames"
        frame_count = self.thumbnail_generator.extract_frames(norm_video_path, frames_dir)

        # 4. Generate 480p preview
        preview_path = out_dir / "preview_480p.mp4"
        self.thumbnail_generator.generate_480p_preview(norm_video_path, preview_path)

        # Cache metadata
        meta_cache = out_dir / "metadata.json"
        meta_dict = metadata.model_dump() if metadata else {"path": str(v_path)}
        with open(meta_cache, "w", encoding="utf-8") as f:
            json.dump(meta_dict, f, indent=2)

        return PreprocessingResult(
            normalized_video_path=str(norm_video_path),
            audio_path=str(audio_path),
            frames_dir=str(frames_dir),
            preview_480p_path=str(preview_path),
            frame_count=frame_count,
            metadata_cache_path=str(meta_cache),
        )
