"""
Ranking Feature Generator Engine.
Compiles candidate strengths, weaknesses, and competitive advantages.
"""

from typing import List, Tuple
from app.matching.schemas.match_models import ScoreBreakdown
from core.logging import get_logger

logger = get_logger("ranking_features")


class RankingFeatureGenerator:
    """Ranking Feature Generator Engine."""

    def generate_ranking_features(self, breakdown: ScoreBreakdown) -> Tuple[List[str], List[str]]:
        strengths: List[str] = []
        weaknesses: List[str] = []

        if breakdown.qualification_score >= 0.90:
            strengths.append("Meets highest academic qualification requirements (Ph.D. degree present).")

        if breakdown.research_score >= 0.80:
            strengths.append("Strong scholarly publication record with high research output.")

        if breakdown.experience_score < 0.60:
            weaknesses.append("Experience duration below optimal threshold for target rank.")

        if breakdown.skills_score < 0.60:
            weaknesses.append("Missing core mandatory technical skills specified in JD.")

        logger.debug("Ranking features generated", strengths_count=len(strengths), weaknesses_count=len(weaknesses))
        return strengths, weaknesses
