"""
Resume Quality Engine.
Calculates deterministic mathematical scores for Completeness, Data Quality, Evidence Strength, Research, Teaching, Industry, Technical, and Overall Resume Quality.
"""

from app.information_extraction.schemas.candidate_profile import StructuredCandidateProfile
from app.resume_intelligence.schemas.intelligence_report import ProfileQualityScores, ResearchIntelligence, TeachingIntelligence, TimelineAnalysis
from core.logging import get_logger

logger = get_logger("quality_engine")


class ResumeQualityEngine:
    """Deterministic Resume Quality & Scoring Engine."""

    def compute_quality_scores(
        self,
        profile: StructuredCandidateProfile,
        timeline: TimelineAnalysis,
        research: ResearchIntelligence,
        teaching: TeachingIntelligence,
        errors_count: int,
    ) -> ProfileQualityScores:
        # Completeness
        c_score = 0.0
        if profile.contact.full_name.value: c_score += 0.20
        if profile.contact.email.value: c_score += 0.20
        if profile.education: c_score += 0.20
        if profile.experience: c_score += 0.20
        if profile.skills: c_score += 0.20
        completeness = round(c_score, 2)

        # Data Quality
        data_qual = 1.0 - (errors_count * 0.10)
        data_qual = max(0.20, round(data_qual, 2))

        # Evidence Strength
        evidence_strength = 0.95

        # Research Strength
        res_strength = min(1.0, round(research.publication_count * 0.20 + (0.30 if research.doi_count > 0 else 0.0), 2))

        # Teaching Strength
        teach_strength = 0.90 if teaching.has_teaching_experience else 0.0

        # Industry Strength
        ind_strength = min(1.0, round(timeline.industry_experience_years * 0.15, 2))

        # Technical Strength
        tech_skills_count = sum(len(cat.skills) for cat in profile.skills)
        tech_strength = min(1.0, round(tech_skills_count * 0.10, 2))

        # Overall Resume Quality
        overall_quality = round((completeness + data_qual + evidence_strength) / 3.0, 2)

        scores = ProfileQualityScores(
            completeness_score=completeness,
            data_quality_score=data_qual,
            evidence_strength_score=evidence_strength,
            resume_quality_score=overall_quality,
            research_strength_score=res_strength,
            teaching_strength_score=teach_strength,
            industry_strength_score=ind_strength,
            technical_strength_score=tech_strength,
            validation_score=data_qual,
        )

        logger.debug("Computed profile quality scores", overall_quality=overall_quality, completeness=completeness)
        return scores
