"""
Education Intelligence Engine.
Analyzes academic progression, highest qualification (Ph.D. > Master > Bachelor), and degree hierarchy.
"""

from typing import Any, Dict, List
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from core.logging import get_logger

logger = get_logger("education_intelligence")

DEGREE_HIERARCHY = {
    "Ph.D.": 4,
    "M.Tech": 3,
    "M.S.": 3,
    "M.Sc.": 3,
    "M.B.A.": 3,
    "B.Tech": 2,
    "B.E.": 2,
    "B.S.": 2,
    "B.Sc.": 2,
}


class EducationIntelligenceEngine:
    """Education & Academic Qualification Intelligence Engine."""

    def analyze_education(self, profile: StructuredCandidateProfile) -> Dict[str, Any]:
        degrees = [edu.degree.value for edu in profile.education if edu.degree.value]

        highest_degree = "Bachelor"
        highest_rank = 1

        for deg in degrees:
            rank = DEGREE_HIERARCHY.get(deg, 1)
            if rank > highest_rank:
                highest_rank = rank
                highest_degree = deg

        return {
            "total_degrees": len(degrees),
            "highest_qualification": highest_degree,
            "has_phd": highest_degree == "Ph.D.",
        }
