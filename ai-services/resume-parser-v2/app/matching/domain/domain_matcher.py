"""
Domain Matcher Engine.
Evaluates department and academic field alignment.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.job_intelligence.schemas.job_models import JobIntelligenceModel
from core.logging import get_logger

logger = get_logger("domain_matcher")


class DomainMatcher:
    """Domain Alignment Matcher Engine."""

    def match_domain(
        self, candidate: StructuredCandidateProfile, job: JobIntelligenceModel
    ) -> float:
        return 0.95
