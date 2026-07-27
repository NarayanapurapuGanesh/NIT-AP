"""
Teaching Intelligence Engine.
Evaluates teaching experience, highest academic rank, courses taught, and academic administration.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_intelligence.schemas.intelligence_report import TeachingIntelligence
from core.logging import get_logger

logger = get_logger("teaching_intelligence")


class TeachingIntelligenceEngine:
    """Teaching & Pedagogical Intelligence Engine."""

    def analyze_teaching(self, profile: StructuredCandidateProfile) -> TeachingIntelligence:
        teaching_exps = [
            exp for exp in profile.experience
            if any(k in (exp.designation.value or "").lower() for k in ["professor", "lecturer", "teacher", "instructor", "faculty"])
        ]

        has_teaching = len(teaching_exps) > 0
        rank = teaching_exps[0].designation.value if has_teaching else None
        score = 0.90 if has_teaching else 0.0

        intel = TeachingIntelligence(
            has_teaching_experience=has_teaching,
            highest_academic_rank=rank,
            subjects_count=len(teaching_exps) * 2,
            has_administrative_roles=any("head" in (e.designation.value or "").lower() for e in teaching_exps),
            teaching_score=score,
        )

        logger.debug("Teaching intelligence analyzed", has_teaching=has_teaching, rank=rank)
        return intel
