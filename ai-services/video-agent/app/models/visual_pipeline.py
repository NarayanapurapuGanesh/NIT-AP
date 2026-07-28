from pydantic import BaseModel
from app.models.ocr import OCRResult
from app.models.scene import SceneDetectionResult
from app.models.visual import FaceMetrics, GestureMetrics, PoseMetrics, VisualTimeline


class VisualAnalysisResult(BaseModel):
    sceneDetection: SceneDetectionResult
    ocr: OCRResult
    faceAnalysis: FaceMetrics
    poseAnalysis: PoseMetrics
    gestureAnalysis: GestureMetrics
    visual_timeline: VisualTimeline
