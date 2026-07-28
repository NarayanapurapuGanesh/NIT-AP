from loguru import logger
from app.models.evidence import EvidencePacket
from app.models.report import ScoreBreakdown


class TeachingScoringEngine:
    """Phase 9: Multi-Dimensional Teaching Scoring Engine."""

    def calculate_scores(self, evidence: EvidencePacket) -> ScoreBreakdown:
        logger.info(f"Calculating weighted teaching evaluation scores for candidate '{evidence.candidate_id}'...")

        v_score = min(100.0, (evidence.voice_analysis.clarity * 0.5) + (evidence.voice_analysis.confidence * 0.5))
        vis_score = min(100.0, (evidence.face_analysis.eye_contact_percentage * 0.5) + (evidence.pose_analysis.upright_posture_percentage * 0.5))
        ped_score = min(100.0, (evidence.teaching_analysis.pedagogy_score * 0.6) + (evidence.ocr.average_confidence * 0.4))

        overall = round((v_score * 0.35) + (vis_score * 0.35) + (ped_score * 0.30), 1)

        scores = ScoreBreakdown(
            clarity_and_delivery=round(v_score, 1),
            visual_and_engagement=round(vis_score, 1),
            content_and_pedagogy=round(ped_score, 1),
            overall_score=overall,
        )

        logger.info(f"Scoring calculation completed for '{evidence.candidate_id}': Overall Score = {overall}/100")
        return scores
