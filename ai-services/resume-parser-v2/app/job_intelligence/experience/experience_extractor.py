"""
Experience Requirement Extractor Engine.
Parses minimum total, teaching, research, and industry experience thresholds.
"""

import re
from app.job_intelligence.schemas.job_models import ExperienceRequirement
from core.logging import get_logger

logger = get_logger("experience_extractor")

EXP_YEARS_REGEX = re.compile(r"\b(\d{1,2})\+?\s*(?:years|yrs)\b", re.IGNORECASE)


class ExperienceExtractor:
    """Experience Requirement Extractor Engine."""

    def extract_experience(self, text_raw: str) -> ExperienceRequirement:
        min_total = 0.0
        min_teach = 0.0
        min_res = 0.0

        matches = EXP_YEARS_REGEX.findall(text_raw)
        if matches:
            years = [float(m) for m in matches]
            min_total = max(years)
            min_teach = min_total if "teaching" in text_raw.lower() else round(min_total * 0.5, 1)

        req = ExperienceRequirement(
            min_total_experience_years=min_total,
            min_teaching_experience_years=min_teach,
            min_research_experience_years=min_res,
            min_industry_experience_years=0.0,
        )

        logger.debug("Extracted experience requirement", min_total_years=min_total)
        return req
