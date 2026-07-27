"""
Responsibility Requirement Extractor Engine.
Parses teaching, research, and administrative responsibilities from JD text.
"""

from app.job_intelligence.schemas.job_models import ResponsibilityRequirement
from core.logging import get_logger

logger = get_logger("responsibility_extractor")


class ResponsibilityExtractor:
    """Responsibility Extractor Engine."""

    def extract_responsibilities(self, text_raw: str) -> ResponsibilityRequirement:
        lines = [l.strip() for l in text_raw.split("\n") if l.strip()]

        teaching = []
        research = []
        admin = []

        for line in lines:
            cl = line.lower()
            if "teach" in cl or "lecture" in cl or "course" in cl:
                teaching.append(line)
            elif "research" in cl or "publish" in cl or "grant" in cl:
                research.append(line)
            elif "admin" in cl or "committee" in cl or "head" in cl:
                admin.append(line)

        req = ResponsibilityRequirement(
            teaching_responsibilities=teaching or ["Deliver undergraduate and postgraduate lectures."],
            research_responsibilities=research or ["Conduct independent research and publish in indexed journals."],
            administrative_responsibilities=admin or ["Participate in departmental committee work."],
        )

        logger.debug("Extracted responsibilities", teaching_count=len(req.teaching_responsibilities))
        return req
