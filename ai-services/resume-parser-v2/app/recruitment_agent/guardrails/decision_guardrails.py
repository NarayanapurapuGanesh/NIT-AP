"""
Decision Guardrails Engine.
Enforces strict alignment with deterministic match scores and rejects unsupported claims.
"""

from app.matching.schemas.match_models import CandidateMatchReport
from core.logging import get_logger

logger = get_logger("decision_guardrails")


class DecisionGuardrailsEngine:
    """Anti-Hallucination Decision Guardrails Engine."""

    def enforce_guardrails(self, recommendation: str, match: CandidateMatchReport) -> str:
        # Strict Guardrail: If candidate has critical gaps, recommendation CANNOT be Highly Recommended
        if len(match.critical_gaps) > 0 and recommendation in ["Highly Recommended", "Recommended"]:
            logger.info("Decision Guardrail triggered: Overriding recommendation due to critical gap Presence.", original=recommendation)
            return "Requires Manual Review"
        return recommendation
