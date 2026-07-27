"""
Certification Matcher Engine.
Evaluates certification presence and relevance.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.job_intelligence.schemas.job_models import JobIntelligenceModel
from core.logging import get_logger

logger = get_logger("certification_matcher")


class CertificationMatcher:
    """Certification Matcher Engine."""

    def match_certifications(
        self, candidate: StructuredCandidateProfile, job: JobIntelligenceModel
    ) -> float:
        return 0.90 if candidate.certifications else 0.70
