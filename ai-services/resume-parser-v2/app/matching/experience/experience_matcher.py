"""
Experience Matcher Engine.
Compares total experience years and teaching/research experience against job thresholds.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.job_intelligence.schemas.job_models import JobIntelligenceModel
from core.logging import get_logger

logger = get_logger("experience_matcher")


class ExperienceMatcher:
    """Experience Matcher Engine."""

    def match_experience(
        self, candidate: StructuredCandidateProfile, job: JobIntelligenceModel
    ) -> float:
        min_required = job.experience.min_total_experience_years
        if min_required == 0.0:
            return 1.0

        # Estimate experience
        cand_exp_years = len(candidate.experience) * 2.0  # 2 years per listed position
        ratio = cand_exp_years / min_required
        score = min(1.0, max(0.20, ratio))

        logger.debug("Experience matching complete", cand_years=cand_exp_years, req_years=min_required, score=score)
        return round(score, 2)
