from pathlib import Path
from typing import List, Optional, Union
from loguru import logger

from app.models.scene import Keyframe, Scene, SceneDetectionResult
from app.scene_detection.keyframe_extractor import KeyframeExtractor


class SceneDetector:
    """Phase 4: Scene Detection & Smart Keyframe Extractor."""

    def __init__(self, keyframe_extractor: Optional[KeyframeExtractor] = None) -> None:
        self.keyframe_extractor = keyframe_extractor or KeyframeExtractor()

    def detect_scenes(
        self,
        video_path: Union[str, Path],
        output_dir: Union[str, Path],
    ) -> SceneDetectionResult:
        v_path = Path(video_path).resolve()
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Detecting scenes in video: {v_path.name}")

        scene_bounds = []
        try:
            from scenedetect import SceneManager, open_video
            from scenedetect.detectors import ContentDetector

            video = open_video(str(v_path))
            scene_manager = SceneManager()
            scene_manager.add_detector(ContentDetector(threshold=27.0))
            scene_manager.detect_scenes(video)
            scene_list = scene_manager.get_scene_list()

            for scene in scene_list:
                scene_bounds.append((scene[0].get_seconds(), scene[1].get_seconds()))
        except Exception as e:
            logger.warning(f"PySceneDetect fallback to fixed duration sampling: {e}")
            scene_bounds = [(0.0, 10.0), (10.0, 20.0), (20.0, 30.0)]

        keyframes = self.keyframe_extractor.extract_keyframes(v_path, scene_bounds, out_dir)

        scenes = []
        for idx, (start_t, end_t) in enumerate(scene_bounds):
            scene_kfs = [kf for kf in keyframes if f"scene_{idx+1}_" in kf.keyframe_id]
            scenes.append(
                Scene(
                    scene_id=idx + 1,
                    start_time=round(start_t, 2),
                    end_time=round(end_t, 2),
                    duration=round(end_t - start_t, 2),
                    start_frame=int(start_t * 30),
                    end_frame=int(end_t * 30),
                    scene_type="teaching_transition",
                    keyframes=scene_kfs,
                )
            )

        timeline_path = out_dir / "scene_timeline.json"
        res = SceneDetectionResult(
            total_scenes=len(scenes),
            total_keyframes=len(keyframes),
            scenes=scenes,
            timeline_path=str(timeline_path),
        )

        with open(timeline_path, "w", encoding="utf-8") as f:
            f.write(res.model_dump_json(indent=2))

        return res
