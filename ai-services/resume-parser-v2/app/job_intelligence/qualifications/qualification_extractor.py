"""
Qualification Requirement Extractor Engine.
Parses minimum and preferred degrees (Ph.D., M.Tech, B.Tech) and branch specializations.
"""

from app.job_intelligence.ontology.job_ontology import JobOntologyResolver
from app.job_intelligence.schemas.job_models import QualificationRequirement
from core.logging import get_logger

logger = get_logger("qualification_extractor")


class QualificationExtractor:
    """Qualification Extractor Engine."""

    def extract_qualification(self, text_raw: str) -> QualificationRequirement:
        is_phd = JobOntologyResolver.is_phd_required(text_raw)

        min_deg = "Ph.D." if is_phd else "M.Tech"
        pref_deg = "Ph.D."

        branches = []
        clean = text_raw.lower()
        if "computer science" in clean or "cse" in clean:
            branches.append("Computer Science & Engineering")
        if "artificial intelligence" in clean or "ai" in clean:
            branches.append("Artificial Intelligence & Data Science")

        req = QualificationRequirement(
            minimum_degree=min_deg,
            preferred_degree=pref_deg,
            branch_or_specialization=branches or ["Computer Science & Engineering"],
            is_phd_mandatory=is_phd,
        )

        logger.debug("Extracted qualification requirement", min_degree=min_deg, is_phd=is_phd)
        return req
