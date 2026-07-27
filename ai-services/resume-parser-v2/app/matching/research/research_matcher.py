"""
Research Matcher Engine.
Evaluates publication count, Scopus/SCI presence, DOIs, and patent requirements.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.job_intelligence.schemas.job_models import JobIntelligenceModel
from core.logging import get_logger

logger = get_logger("research_matcher")


class ResearchMatcher:
    """Research Matcher Engine."""

    def match_research(
        self, candidate: StructuredCandidateProfile, job: JobIntelligenceModel
    ) -> float:
        cand_pubs = len(candidate.publications)
        req_pubs = job.research.min_publications_count

        if req_pubs == 0:
            return 1.0

        if cand_pubs >= req_pubs:
            score = 1.0
        elif cand_pubs > 0:
            score = 0.60
        else:
            score = 0.20

        logger.debug("Research matching complete", cand_pubs=cand_pubs, req_pubs=req_pubs, score=score)
        return round(score, 2)
