"""
Research Requirement Extractor Engine.
Parses publication expectations (Scopus, SCI, UGC CARE), patents, and funded project requirements.
"""

from app.job_intelligence.schemas.job_models import ResearchRequirement
from core.logging import get_logger

logger = get_logger("research_extractor")


class ResearchExtractor:
    """Research Requirement Extractor Engine."""

    def extract_research(self, text_raw: str) -> ResearchRequirement:
        clean = text_raw.lower()

        scopus_sci = "scopus" in clean or "sci" in clean or "peer-reviewed" in clean
        patents = "patent" in clean
        funded = "funded" in clean or "grant" in clean or "project" in clean

        req = ResearchRequirement(
            min_publications_count=3 if scopus_sci else 1,
            scopus_sci_mandatory=scopus_sci,
            patents_required=patents,
            funded_projects_required=funded,
            preferred_research_domains=["Computer Science", "Artificial Intelligence"],
        )

        logger.debug("Extracted research requirement", scopus_sci=scopus_sci)
        return req
