import json
import uuid
from pathlib import Path
from typing import Dict, Optional, Union
import cv2
from loguru import logger

from app.config.settings import settings
from app.core.exceptions import VideoAgentError
from app.models.ocr import OCRResult
from app.models.scene import SceneDetectionResult
from app.models.visual import FaceMetrics, GestureMetrics, PoseMetrics, VisualFrameMetrics, VisualTimeline
from app.models.visual_pipeline import VisualAnalysisResult
from app.ocr.ocr_service import OCRService
from app.scene_detection.scene_detector import SceneDetector
from app.utils.file_utils import ensure_directory
from app.visual_analysis.face_analyzer import FaceAnalysisService
from app.visual_analysis.hand_analyzer import HandGestureService
from app.visual_analysis.pose_analyzer import PoseAnalysisService


class VisualPipelineService:
    """Service orchestrating Phase 4 Scene Detection, Phase 5 OCR Slide Analysis, and Phase 6 MediaPipe Visual Analysis."""

    def __init__(
        self,
        scene_detector: Optional[SceneDetector] = None,
        ocr_service: Optional[OCRService] = None,
        face_analyzer: Optional[FaceAnalysisService] = None,
        pose_analyzer: Optional[PoseAnalysisService] = None,
        hand_analyzer: Optional[HandGestureService] = None,
    ) -> None:
        self.scene_detector = scene_detector or SceneDetector()
        self.ocr_service = ocr_service or OCRService()
        self.face_analyzer = face_analyzer or FaceAnalysisService()
        self.pose_analyzer = pose_analyzer or PoseAnalysisService()
        self.hand_analyzer = hand_analyzer or HandGestureService()

        self.scene_store: Dict[str, SceneDetectionResult] = {}
        self.ocr_store: Dict[str, OCRResult] = {}

    def analyze_visual_pipeline(
        self,
        video_path: Union[str, Path],
        job_id: Optional[str] = None,
    ) -> VisualAnalysisResult:
        """Executes Phase 4, Phase 5, and Phase 6 visual analysis pipeline."""
        j_id = job_id or str(uuid.uuid4())
        v_path = Path(video_path).resolve()
        output_base_dir = ensure_directory(settings.base_dir / settings.storage.output_dir / j_id)

        logger.info(f"[{j_id}] Executing Visual Pipeline (Phases 4-6) for: {v_path.name}")

        # PHASE 4: Scene Detection & Smart Keyframe Extraction
        logger.info(f"[{j_id}] Phase 4: Executing Scene Detection")
        scene_res = self.scene_detector.detect_scenes(v_path, output_dir=output_base_dir)
        self.scene_store[j_id] = scene_res

        # Collect deduplicated keyframes
        unique_keyframes = [
            kf for scene in scene_res.scenes for kf in scene.keyframes if not kf.is_duplicate
        ]
        if not unique_keyframes and scene_res.scenes:
            unique_keyframes = [scene_res.scenes[0].keyframes[0]]

        # PHASE 5: OCR & Slide Content Extraction
        logger.info(f"[{j_id}] Phase 5: Executing OCR & Slide Structure Extraction")
        ocr_res = self.ocr_service.process_ocr(unique_keyframes, output_dir=output_base_dir)
        self.ocr_store[j_id] = ocr_res

        # PHASE 6: MediaPipe Face, Pose & Gesture Analysis (SKIPPED PER CONFIGURATION)
        logger.info(f"[{j_id}] Phase 6: Skipping MediaPipe Face Mesh, Pose, and Hands Analysis as requested.")
        face_metrics = FaceMetrics()
        pose_metrics = PoseMetrics()
        gesture_metrics = GestureMetrics()

        timeline_path = output_base_dir / "visual_timeline.json"
        v_timeline = VisualTimeline(
            second_by_second_metrics=[],
            json_path=str(timeline_path),
        )
        with open(timeline_path, "w", encoding="utf-8") as f:
            f.write(v_timeline.model_dump_json(indent=2))

        logger.info(f"[{j_id}] Visual Pipeline (Phases 4-6) completed successfully.")
        return VisualAnalysisResult(
            sceneDetection=scene_res,
            ocr=ocr_res,
            faceAnalysis=face_metrics,
            poseAnalysis=pose_metrics,
            gestureAnalysis=gesture_metrics,
            visual_timeline=v_timeline,
        )

    def get_scenes(self, job_id: str) -> Optional[SceneDetectionResult]:
        return self.scene_store.get(job_id)

    def get_ocr(self, job_id: str) -> Optional[OCRResult]:
        return self.ocr_store.get(job_id)
