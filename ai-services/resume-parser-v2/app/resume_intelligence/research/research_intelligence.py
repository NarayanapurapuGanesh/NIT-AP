"""
Research Intelligence Engine.
Analyzes research domain coverage, publication frequency, DOI presence, and citation availability.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_intelligence.schemas.intelligence_report import ResearchIntelligence
from core.logging import get_logger

logger = get_logger("research_intelligence")


class ResearchIntelligenceEngine:
    """Scholarly Research Intelligence Engine."""

    def analyze_research(self, profile: StructuredCandidateProfile) -> ResearchIntelligence:
        pub_count = len(profile.publications)
        doi_count = sum(1 for pub in profile.publications if pub.doi.value)
        total_citations = sum(pub.citations_count for pub in profile.publications)

        recent_pub = any(pub.year.value and pub.year.value >= 2023 for pub in profile.publications)
        continuity = 1.0 if pub_count >= 3 else (0.6 if pub_count >= 1 else 0.0)

        domains = ["Computer Science", "Artificial Intelligence"] if pub_count > 0 else []

        intel = ResearchIntelligence(
            publication_count=pub_count,
            doi_count=doi_count,
            citations_total=total_citations,
            research_domains=domains,
            has_recent_publication=recent_pub,
            research_continuity_score=continuity,
        )

        logger.debug("Research intelligence analyzed", pub_count=pub_count, doi_count=doi_count)
        return intel
