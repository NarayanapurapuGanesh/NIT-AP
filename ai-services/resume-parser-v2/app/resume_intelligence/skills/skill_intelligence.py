"""
Skill Intelligence Engine.
Analyzes skill diversity, tech stack maturity, core vs supporting skills, and skill category counts.
"""

from typing import Any, Dict
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from core.logging import get_logger

logger = get_logger("skill_intelligence")


class SkillIntelligenceEngine:
    """Skill Intelligence Engine."""

    def analyze_skills(self, profile: StructuredCandidateProfile) -> Dict[str, Any]:
        total_skills = sum(len(cat.skills) for cat in profile.skills)
        cat_count = len(profile.skills)

        diversity_score = min(1.0, round(total_skills / 15.0, 2))

        return {
            "total_skills_count": total_skills,
            "category_count": cat_count,
            "skill_diversity_score": diversity_score,
        }
