"""
FacultyIQ Video Evidence Extraction Service — Scene Detector (Module 4).

Detects scene changes (slide transitions, whiteboard changes, screen shares)
using PySceneDetect's ContentDetector and extracts representative keyframes.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union

from app.config.settings import settings
from app.core.exceptions import SceneDetectionError
from app.core.logging import get_module_logger
from app.models.scene import Scene, SceneDetectionResult, SlideImage
from app.scene_detection.keyframe_extractor import KeyframeExtractor
from app.utils.file_utils import write_json

log = get_module_logger("scene_detection")


class SceneDetector:
    """Detects scene boundaries and extracts representative slide images."""

    def __init__(
        self,
        keyframe_extractor: Optional[KeyframeExtractor] = None,
        threshold: Optional[float] = None,
        min_scene_duration: Optional[float] = None,
    ) -> None:
        self._keyframe_extractor = keyframe_extractor or KeyframeExtractor()
        self._threshold = threshold or settings.scene_detection.threshold
        self._min_scene_duration = (
            min_scene_duration or settings.scene_detection.min_scene_duration
        )

    def detect_scenes(
        self,
        video_path: Union[str, Path],
        output_dir: Union[str, Path],
    ) -> SceneDetectionResult:
        """Detects scenes and extracts slide images."""
        v_path = Path(video_path).resolve()
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        log.info("Detecting scenes in video: {}", v_path.name)

        scene_bounds = self._detect_boundaries(v_path)

        if not scene_bounds:
            log.warning(
                "No scene boundaries detected; creating single scene spanning entire video."
            )
            duration = self._get_video_duration(v_path)
            scene_bounds = [(0.0, duration)]

        scene_bounds = self._filter_short_scenes(scene_bounds)

        slides = self._keyframe_extractor.extract_keyframes(
            v_path, scene_bounds, out_dir
        )

        unique_slides = [s for s in slides if not s.is_duplicate]

        scenes = self._build_scenes(scene_bounds, slides)

        slides_dir = out_dir / "slides"
        json_path = out_dir / "scenes.json"

        result = SceneDetectionResult(
            total_scenes=len(scenes),
            total_slides=len(unique_slides),
            scenes=scenes,
            slides_dir=str(slides_dir),
            json_path=str(json_path),
        )

        write_json(json_path, result)

        log.info(
            "Scene detection complete: {} scenes, {} slides ({} unique)",
            len(scenes), len(slides), len(unique_slides),
        )
        return result

    def _detect_boundaries(self, video_path: Path) -> List[Tuple[float, float]]:
        """Uses PySceneDetect ContentDetector to find scene boundaries."""
        try:
            from scenedetect import SceneManager, open_video
            from scenedetect.detectors import ContentDetector

            video = open_video(str(video_path))
            scene_manager = SceneManager()
            scene_manager.add_detector(
                ContentDetector(threshold=self._threshold)
            )
            scene_manager.detect_scenes(video)
            scene_list = scene_manager.get_scene_list()

            bounds: List[Tuple[float, float]] = []
            for scene_start, scene_end in scene_list:
                bounds.append(
                    (scene_start.get_seconds(), scene_end.get_seconds())
                )

            log.info(
                "PySceneDetect found {} scene boundaries.", len(bounds)
            )
            return bounds

        except ImportError:
            log.error(
                "PySceneDetect not installed. Install with: pip install scenedetect[opencv]"
            )
            raise SceneDetectionError(
                "PySceneDetect is required but not installed."
            )
        except Exception as exc:
            log.error("Scene detection failed: {}", exc)
            raise SceneDetectionError(
                f"Scene detection failed: {exc}"
            ) from exc

    def _filter_short_scenes(
        self, bounds: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        """Filters out scenes shorter than the minimum duration."""
        filtered = [
            (s, e) for s, e in bounds
            if (e - s) >= self._min_scene_duration
        ]
        removed = len(bounds) - len(filtered)
        if removed > 0:
            log.info(
                "Filtered {} scenes shorter than {:.1f}s",
                removed, self._min_scene_duration,
            )
        return filtered if filtered else bounds[:1]

    def _build_scenes(
        self,
        bounds: List[Tuple[float, float]],
        slides: List[SlideImage],
    ) -> List[Scene]:
        """Associates extracted slides with their parent scenes."""
        scenes: List[Scene] = []
        for idx, (start_t, end_t) in enumerate(bounds):
            scene_id = idx + 1
            scene_slides = [s for s in slides if s.scene_id == scene_id]

            scenes.append(
                Scene(
                    scene_id=scene_id,
                    start_time=round(start_t, 2),
                    end_time=round(end_t, 2),
                    duration=round(end_t - start_t, 2),
                    scene_type="slide_change",
                    slides=scene_slides,
                )
            )
        return scenes

    def _get_video_duration(self, video_path: Path) -> float:
        """Gets video duration using OpenCV."""
        try:
            import cv2

            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
            cap.release()
            return frame_count / fps if fps > 0 else 0.0
        except Exception:
            return 60.0
