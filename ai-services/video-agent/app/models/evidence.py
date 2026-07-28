from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.ocr import OCRResult
from app.models.scene import SceneDetectionResult
from app.models.transcription import TranscriptionResult
from app.models.validation import VideoMetadata
from app.models.visual import FaceMetrics, GestureMetrics, PoseMetrics
from app.models.voice import VoiceAnalysisResult
from app.models.teaching import TeachingAnalysisResult


class EvidencePacket(BaseModel):
    candidate_id: str
    video_metadata: VideoMetadata
    transcription: TranscriptionResult
    voice_analysis: VoiceAnalysisResult
    scene_detection: SceneDetectionResult
    ocr: OCRResult
    face_analysis: FaceMetrics
    pose_analysis: PoseMetrics
    gesture_analysis: GestureMetrics
    teaching_analysis: TeachingAnalysisResult
    evidence_json_path: str
