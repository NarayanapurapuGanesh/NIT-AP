from pathlib import Path
from typing import Union
from loguru import logger

from app.models.evidence import EvidencePacket
from app.models.ocr import OCRResult
from app.models.scene import SceneDetectionResult
from app.models.teaching import TeachingAnalysisResult
from app.models.transcription import TranscriptionResult
from app.models.validation import VideoMetadata
from app.models.visual import FaceMetrics, GestureMetrics, PoseMetrics
from app.models.voice import VoiceAnalysisResult


class EvidenceBuilder:
    """Phase 9: Evidence Packet Assembly Engine."""

    def build_evidence_packet(
        self,
        candidate_id: str,
        video_metadata: VideoMetadata,
        transcription: TranscriptionResult,
        voice_analysis: VoiceAnalysisResult,
        scene_detection: SceneDetectionResult,
        ocr: OCRResult,
        face_analysis: FaceMetrics,
        pose_analysis: PoseMetrics,
        gesture_analysis: GestureMetrics,
        teaching_analysis: TeachingAnalysisResult,
    ) -> EvidencePacket:
        logger.info(f"Building Phase 9 EvidencePacket for candidate '{candidate_id}'...")

        out_dir = Path(transcription.json_path).parent
        json_p = out_dir / "evidence_packet.json"

        packet = EvidencePacket(
            candidate_id=candidate_id,
            video_metadata=video_metadata,
            transcription=transcription,
            voice_analysis=voice_analysis,
            scene_detection=scene_detection,
            ocr=ocr,
            face_analysis=face_analysis,
            pose_analysis=pose_analysis,
            gesture_analysis=gesture_analysis,
            teaching_analysis=teaching_analysis,
            evidence_json_path=str(json_p),
        )

        with open(json_p, "w", encoding="utf-8") as f:
            f.write(packet.model_dump_json(indent=2))

        return packet
