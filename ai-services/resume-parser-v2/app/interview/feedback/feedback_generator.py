"""
Feedback Generator Engine.
Compiles interview strengths, weaknesses, panel observations, and updated hiring recommendation.
"""

from typing import Any, Dict
from app.interview.schemas.interview_models import InterviewEvaluationReport
from core.logging import get_logger

logger = get_logger("feedback_generator")


class FeedbackGeneratorEngine:
    """Feedback & Training Recommendation Generator Engine."""

    def build_feedback_summary(self, evaluation: InterviewEvaluationReport) -> Dict[str, Any]:
        return {
            "candidate_name": evaluation.candidate_name,
            "overall_score": evaluation.overall_interview_score,
            "recommendation": evaluation.updated_hiring_recommendation,
            "strengths": evaluation.strengths,
            "weaknesses": evaluation.weaknesses,
        }
