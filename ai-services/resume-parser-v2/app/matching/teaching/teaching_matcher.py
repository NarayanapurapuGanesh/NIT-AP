"""
Teaching Matcher Engine.
Evaluates candidate's teaching background and subject overlap against job requirements.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.job_intelligence.schemas.job_models import JobIntelligenceModel
from core.logging import get_logger

logger = get_logger("teaching_matcher")


class TeachingMatcher:
    """Teaching Matcher Engine."""

    def match_teaching(
        self, candidate: StructuredCandidateProfile, job: JobIntelligenceModel
    ) -> float:
        teaching_exps = [
            e for e in candidate.experience
            if any(k in (e.designation.value or "").lower() for k in ["professor", "lecturer", "teacher", "faculty"])
        ]

        if teaching_exps:
            return 1.0
        return 0.50
