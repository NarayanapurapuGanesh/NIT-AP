"""
Teaching Requirement Extractor Engine.
Parses subjects, courses, lab guidance, and curriculum development requirements.
"""

from app.job_intelligence.schemas.job_models import TeachingRequirement
from core.logging import get_logger

logger = get_logger("teaching_extractor")


class TeachingExtractor:
    """Teaching Requirement Extractor Engine."""

    def extract_teaching(self, text_raw: str) -> TeachingRequirement:
        subjects = []
        clean = text_raw.lower()

        if "data structures" in clean or "algorithms" in clean:
            subjects.append("Data Structures & Algorithms")
        if "operating systems" in clean:
            subjects.append("Operating Systems")
        if "machine learning" in clean:
            subjects.append("Machine Learning")

        req = TeachingRequirement(
            subjects=subjects or ["Computer Science Fundamentals"],
            course_levels=["UG", "PG"],
            lab_guidance_required="lab" in clean or "laboratory" in clean,
        )

        logger.debug("Extracted teaching requirement", subjects_count=len(req.subjects))
        return req
