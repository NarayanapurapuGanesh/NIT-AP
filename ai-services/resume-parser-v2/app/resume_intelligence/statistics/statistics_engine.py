"""
Intelligence Statistics Engine.
Compiles metric counters (Years Experience, Research Years, Teaching Years, Skill Count, Project Count, Publication Count, Gap Count).
"""

from typing import Any, Dict
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_intelligence.schemas.intelligence_report import TimelineAnalysis
from core.logging import get_logger

logger = get_logger("intelligence_statistics")


class IntelligenceStatisticsEngine:
    """Metric Statistics Aggregator Engine."""

    def compile_statistics(
        self, profile: StructuredCandidateProfile, timeline: TimelineAnalysis
    ) -> Dict[str, Any]:
        total_skills = sum(len(cat.skills) for cat in profile.skills)

        return {
            "years_experience": timeline.total_experience_years,
            "research_years": timeline.research_experience_years,
            "teaching_years": timeline.teaching_experience_years,
            "industry_years": timeline.industry_experience_years,
            "number_of_skills": total_skills,
            "projects_count": len(profile.projects),
            "publications_count": len(profile.publications),
            "certifications_count": len(profile.certifications),
            "awards_count": len(profile.awards),
            "languages_count": len(profile.languages),
            "average_job_duration_months": timeline.average_job_tenure_months,
            "career_gap_count": timeline.career_gap_count,
        }
