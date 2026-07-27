"""
Publication Matcher Engine.
Evaluates paper volume and DOI presence.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.job_intelligence.schemas.job_models import JobIntelligenceModel
from core.logging import get_logger

logger = get_logger("publication_matcher")


class PublicationMatcher:
    """Publication Matcher Engine."""

    def match_publications(
        self, candidate: StructuredCandidateProfile, job: JobIntelligenceModel
    ) -> float:
        if not candidate.publications:
            return 0.30
        doi_count = sum(1 for p in candidate.publications if p.doi.value)
        if doi_count > 0:
            return 1.0
        return 0.70
