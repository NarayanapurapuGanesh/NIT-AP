"""
Deterministic Scoring Engine.
Combines individual component matcher scores with JobIntelligenceModel weight distribution map.
"""

from app.job_intelligence.schemas.job_models import RequirementWeightMap
from app.matching.schemas.match_models import ScoreBreakdown
from core.logging import get_logger

logger = get_logger("scoring_engine")


class DeterministicScoringEngine:
    """Deterministic Score Calculator."""

    def compute_scores(
        self,
        qual_score: float,
        exp_score: float,
        res_score: float,
        teach_score: float,
        skill_score: float,
        pub_score: float,
        cert_score: float,
        domain_score: float,
        weights: RequirementWeightMap,
    ) -> ScoreBreakdown:
        overall = (
            (qual_score * weights.education_weight)
            + (exp_score * weights.experience_weight)
            + (res_score * weights.research_weight)
            + (teach_score * weights.teaching_weight)
            + (skill_score * weights.skills_weight)
        )

        overall = min(1.0, max(0.0, round(overall, 2)))

        breakdown = ScoreBreakdown(
            qualification_score=qual_score,
            experience_score=exp_score,
            research_score=res_score,
            teaching_score=teach_score,
            skills_score=skill_score,
            publication_score=pub_score,
            certification_score=cert_score,
            domain_score=domain_score,
            overall_score=overall,
        )

        logger.debug("Computed overall matching score", overall_score=overall)
        return breakdown
