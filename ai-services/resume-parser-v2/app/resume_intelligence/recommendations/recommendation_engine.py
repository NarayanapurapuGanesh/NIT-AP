"""
Recommendation Engine.
Generates deterministic actionable recommendations based on quality gaps, missing links, or unbacked evidence.
"""

from typing import List
from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_intelligence.schemas.intelligence_report import ProfileQualityScores, TimelineAnalysis
from core.logging import get_logger

logger = get_logger("recommendation_engine")


class RecommendationEngine:
    """Deterministic Recommendation Engine."""

    def generate_recommendations(
        self,
        profile: StructuredCandidateProfile,
        timeline: TimelineAnalysis,
        scores: ProfileQualityScores,
        unbacked_fields: List[str],
    ) -> List[str]:
        recommendations: List[str] = []

        if not profile.contact.linkedin_url.value:
            recommendations.append("Add LinkedIn profile URL to improve candidate contact completeness.")

        if not profile.contact.google_scholar_url.value and len(profile.publications) > 0:
            recommendations.append("Link Google Scholar or ORCID profile to verify scholarly publications.")

        if timeline.career_gap_count > 0:
            recommendations.append(f"Clarify candidate's {timeline.career_gap_count} career gap period(s).")

        if scores.evidence_strength_score < 0.90 or unbacked_fields:
            recommendations.append("Attach missing line-by-line bounding box evidence points to unverified fields.")

        if not profile.education:
            recommendations.append("Add formal degree education records to meet minimum institutional requirements.")

        logger.debug("Generated recommendations", recs_count=len(recommendations))
        return recommendations
