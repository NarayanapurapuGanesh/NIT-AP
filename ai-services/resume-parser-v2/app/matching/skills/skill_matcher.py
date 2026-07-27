"""
Skills Matcher Engine.
Evaluates mandatory and preferred skill coverage percentages.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.job_intelligence.schemas.job_models import JobIntelligenceModel
from core.logging import get_logger

logger = get_logger("skill_matcher")


class SkillMatcher:
    """Skills Matcher Engine."""

    def match_skills(
        self, candidate: StructuredCandidateProfile, job: JobIntelligenceModel
    ) -> float:
        cand_skills = {sk.value.lower() for cat in candidate.skills for sk in cat.skills if sk.value}
        mandatory = [s.lower() for s in job.skills.mandatory_skills]

        if not mandatory:
            return 1.0

        matches = [s for s in mandatory if s in cand_skills]
        score = len(matches) / len(mandatory)

        logger.debug("Skills matching complete", matched=len(matches), total_mandatory=len(mandatory), score=score)
        return round(score, 2)
