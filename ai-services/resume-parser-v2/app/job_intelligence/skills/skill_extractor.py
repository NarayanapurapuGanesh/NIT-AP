"""
Skill Requirement Extractor Engine.
Parses mandatory and preferred technical/academic skills.
"""

from typing import List
from app.job_intelligence.schemas.job_models import SkillRequirement
from core.logging import get_logger

logger = get_logger("skill_extractor")

KNOWN_SKILLS = ["Python", "Java", "C++", "PyTorch", "FastAPI", "React", "Docker", "Kubernetes", "PostgreSQL", "Machine Learning", "NLP"]


class SkillExtractor:
    """Skill Requirement Extractor Engine."""

    def extract_skills(self, text_raw: str) -> SkillRequirement:
        mandatory = []
        preferred = []

        import re
        for sk in KNOWN_SKILLS:
            pattern = r"\b" + re.escape(sk) + r"\b"
            if re.search(pattern, text_raw, re.IGNORECASE):
                mandatory.append(sk)

        req = SkillRequirement(
            mandatory_skills=mandatory,
            preferred_skills=preferred,
        )

        logger.debug("Extracted skill requirements", count=len(mandatory))
        return req
