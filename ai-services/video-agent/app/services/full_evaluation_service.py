import uuid
from pathlib import Path
from typing import Dict, Optional, Union
from loguru import logger

from app.core.exceptions import VideoAgentError, ValidationError
from app.evaluation.evidence_builder import EvidenceBuilder
from app.evaluation.report_generator import ReportGenerator
from app.evaluation.scoring_engine import TeachingScoringEngine
from app.models.evidence import EvidencePacket
from app.models.report import EvaluationReport
from app.preprocessing.video_preprocessor import VideoPreprocessor
from app.teaching_analysis.teaching_analyzer import TeachingAnalysisService
from app.transcription.whisper_transcriber import WhisperTranscriber
from app.validators.video_validator import VideoValidator
from app.voice_analysis.voice_analyzer import VoiceAnalysisService
from app.services.visual_pipeline_service import VisualPipelineService


class FullEvaluationService:
    """Master service running complete end-to-end Video Evaluation Pipeline across all 9 phases."""

    def __init__(
        self,
        validator: Optional[VideoValidator] = None,
        preprocessor: Optional[VideoPreprocessor] = None,
        transcriber: Optional[WhisperTranscriber] = None,
        visual_service: Optional[VisualPipelineService] = None,
        voice_analyzer: Optional[VoiceAnalysisService] = None,
        teaching_analyzer: Optional[TeachingAnalysisService] = None,
        evidence_builder: Optional[EvidenceBuilder] = None,
        scoring_engine: Optional[TeachingScoringEngine] = None,
        report_generator: Optional[ReportGenerator] = None,
    ) -> None:
        self.validator = validator or VideoValidator()
        self.preprocessor = preprocessor or VideoPreprocessor()
        self.transcriber = transcriber or WhisperTranscriber()
        self.visual_service = visual_service or VisualPipelineService()
        self.voice_analyzer = voice_analyzer or VoiceAnalysisService()
        self.teaching_analyzer = teaching_analyzer or TeachingAnalysisService()
        self.evidence_builder = evidence_builder or EvidenceBuilder()
        self.scoring_engine = scoring_engine or TeachingScoringEngine()
        self.report_generator = report_generator or ReportGenerator()

        self.evidence_store: Dict[str, EvidencePacket] = {}
        self.report_store: Dict[str, EvaluationReport] = {}

    def evaluate_video_full(
        self,
        video_path: Union[str, Path],
        job_id: Optional[str] = None,
    ) -> EvaluationReport:
        """Executes full end-to-end Video Evaluation pipeline (Phases 1 through 9)."""
        j_id = job_id or str(uuid.uuid4())
        v_path = Path(video_path).resolve()

        logger.info(f"[{j_id}] Starting Master Video Evaluation Pipeline (Phases 1-9) for: {v_path.name}")

        # PHASE 1: Video Validation
        logger.info(f"[{j_id}] Phase 1: Video Validation")
        val_res = self.validator.validate(v_path)
        if not val_res.validationPassed or not val_res.metadata:
            raise ValidationError(f"Video validation failed: {'; '.join(val_res.errors)}")
        video_metadata = val_res.metadata

        # PHASE 2: Video Preprocessing
        logger.info(f"[{j_id}] Phase 2: Video Preprocessing")
        prep_res = self.preprocessor.process(v_path, job_id=j_id, metadata=video_metadata)

        # PHASE 3: Speech Transcription
        logger.info(f"[{j_id}] Phase 3: Speech Transcription")
        out_base_dir = Path(prep_res.metadata_cache_path).parent
        trans_res = self.transcriber.transcribe(prep_res.audio_path, out_base_dir)

        # PHASES 4-6: Scene Detection, OCR & MediaPipe Visual Analysis
        logger.info(f"[{j_id}] Phases 4-6: Scene Detection, OCR & MediaPipe Visual Analysis")
        visual_res = self.visual_service.analyze_visual_pipeline(prep_res.normalized_video_path, job_id=j_id)

        # PHASE 7: Voice Analysis
        logger.info(f"[{j_id}] Phase 7: Signal Processing Voice Analysis")
        full_transcript_text = "\n".join(seg.text for seg in trans_res.segments)
        words_count = len(full_transcript_text.split())
        voice_res = self.voice_analyzer.analyze_audio(prep_res.audio_path, out_base_dir, word_count=words_count)

        # PHASE 8: Teaching Intelligence Analysis (Ollama LLM)
        logger.info(f"[{j_id}] Phase 8: Teaching Intelligence Analysis (Ollama LLM)")
        full_ocr_text = "\n".join(page.cleaned_text for page in visual_res.ocr.frame_results)
        teaching_res = self.teaching_analyzer.analyze_teaching(
            transcript_text=full_transcript_text,
            ocr_text=full_ocr_text,
            total_scenes=visual_res.sceneDetection.total_scenes,
            speech_rate=voice_res.speechRate,
            voice_clarity=voice_res.clarity,
            voice_confidence=voice_res.confidence,
            eye_contact=visual_res.faceAnalysis.eye_contact_percentage,
            posture=visual_res.poseAnalysis.posture_quality,
            gesture_freq=visual_res.gestureAnalysis.gesture_frequency,
            output_dir=out_base_dir,
        )

        # PHASE 9: Evidence Packet Builder, Scoring Engine & Report Generator
        logger.info(f"[{j_id}] Phase 9: Evidence Packet Assembly & Scoring Engine")
        evidence_packet = self.evidence_builder.build_evidence_packet(
            candidate_id=j_id,
            video_metadata=video_metadata,
            transcription=trans_res,
            voice_analysis=voice_res,
            scene_detection=visual_res.sceneDetection,
            ocr=visual_res.ocr,
            face_analysis=visual_res.faceAnalysis,
            pose_analysis=visual_res.poseAnalysis,
            gesture_analysis=visual_res.gestureAnalysis,
            teaching_analysis=teaching_res,
        )
        self.evidence_store[j_id] = evidence_packet

        scores = self.scoring_engine.calculate_scores(evidence_packet)

        logger.info(f"[{j_id}] Phase 9: Report Generation (HTML, MD, JSON)")
        report = self.report_generator.generate_report(
            job_id=j_id,
            evidence=evidence_packet,
            scores=scores,
            output_dir=out_base_dir,
        )
        self.report_store[j_id] = report

        logger.info(f"[{j_id}] Master Video Evaluation Pipeline COMPLETED successfully. Recommendation: {report.recommendation.recommendation.value}")
        return report

    def get_report(self, job_id: str) -> Optional[EvaluationReport]:
        return self.report_store.get(job_id)

    def get_evidence(self, job_id: str) -> Optional[EvidencePacket]:
        return self.evidence_store.get(job_id)
