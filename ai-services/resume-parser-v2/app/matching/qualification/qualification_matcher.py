"""
Qualification Matcher Engine.
Compares candidate's highest degree (Ph.D. > M.Tech > B.Tech) & specialization against job requirements.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.job_intelligence.schemas.job_models import JobIntelligenceModel
from core.logging import get_logger

logger = get_logger("qualification_matcher")

DEGREE_WEIGHTS = {"Ph.D.": 1.0, "M.Tech": 0.8, "M.S.": 0.8, "B.Tech": 0.6, "B.E.": 0.6}


class QualificationMatcher:
    """Qualification Matcher Engine."""

    def match_qualification(
        self, candidate: StructuredCandidateProfile, job: JobIntelligenceModel
    ) -> float:
        candidate_degrees = [edu.degree.value for edu in candidate.education if edu.degree.value]
        min_required = job.qualification.minimum_degree

        if job.qualification.is_phd_mandatory:
            if "Ph.D." in candidate_degrees:
                score = 1.0
            else:
                score = 0.40
        else:
            cand_score = max([DEGREE_WEIGHTS.get(d, 0.5) for d in candidate_degrees] or [0.5])
            score = cand_score

        logger.debug("Qualification matching complete", score=score)
        return round(score, 2)
