"""
Decision Confidence Engine.
Calculates overall decision confidence score combining model, evidence, and match scores.
"""

from app.matching.schemas.match_models import CandidateMatchReport
from core.logging import get_logger

logger = get_logger("decision_confidence")


class DecisionConfidenceEngine:
    """Decision Confidence Evaluator."""

    def compute_decision_confidence(self, match: CandidateMatchReport) -> float:
        confidence = match.overall_score
        if len(match.critical_gaps) > 0:
            confidence -= 0.15
        return round(max(0.40, min(1.0, confidence)), 2)
