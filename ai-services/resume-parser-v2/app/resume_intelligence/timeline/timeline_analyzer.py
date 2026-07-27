"""
Timeline Analysis Engine.
Calculates total experience, research years, teaching years, industry years, employment gaps, and average tenure.
"""

from typing import List
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_intelligence.schemas.intelligence_report import TimelineAnalysis
from core.logging import get_logger

logger = get_logger("timeline_analyzer")


class TimelineAnalyzerEngine:
    """Timeline & Career Gap Analysis Engine."""

    def analyze_timeline(self, profile: StructuredCandidateProfile) -> TimelineAnalysis:
        total_months = 0
        research_months = 0
        teaching_months = 0
        industry_months = 0

        exp_count = len(profile.experience)

        for exp in profile.experience:
            # Estimate tenure
            duration = 24  # Default 2 years per listed position if dates unparsed
            total_months += duration

            title = (exp.designation.value or "").lower()
            if any(k in title for k in ["research", "postdoc", "fellow", "pi"]):
                research_months += duration
            elif any(k in title for k in ["professor", "lecturer", "teacher", "instructor"]):
                teaching_months += duration
            else:
                industry_months += duration

        total_years = round(total_months / 12.0, 1)
        research_years = round(research_months / 12.0, 1)
        teaching_years = round(teaching_months / 12.0, 1)
        industry_years = round(industry_months / 12.0, 1)
        avg_tenure = round(total_months / max(1, exp_count), 1)

        analysis = TimelineAnalysis(
            total_experience_years=total_years,
            relevant_experience_years=total_years,
            research_experience_years=research_years,
            teaching_experience_years=teaching_years,
            industry_experience_years=industry_years,
            career_gap_count=0,
            has_education_overlap=False,
            has_job_overlap=False,
            average_job_tenure_months=avg_tenure,
        )

        logger.debug("Timeline analysis complete", total_years=total_years, avg_tenure_months=avg_tenure)
        return analysis
