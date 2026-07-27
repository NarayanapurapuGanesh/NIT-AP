"""
Decision Evidence Engine.
Links final decision points to matching scores, candidate extracted fields, and JD requirements.
"""

from typing import List
from app.matching.schemas.match_models import CandidateMatchReport
from core.logging import get_logger

logger = get_logger("decision_evidence")


class DecisionEvidenceEngine:
    """Decision Evidence Linker Engine."""

    def build_evidence_lines(self, match: CandidateMatchReport) -> List[str]:
        evidence: List[str] = [
            f"Matching Overall Score: {int(match.overall_score * 100)}%",
            f"Qualification Score: {int(match.score_breakdown.qualification_score * 100)}%",
            f"Research Score: {int(match.score_breakdown.research_score * 100)}%",
            f"Matched Requirements Count: {len(match.matched_requirements)}",
        ]
        return evidence
