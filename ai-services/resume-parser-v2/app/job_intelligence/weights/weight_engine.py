"""
Weight Calculation Engine.
Calculates deterministic relative weight percentages for matching based on academic rank and position requirements.
"""

from app.job_intelligence.schemas.job_models import PositionInfo, QualificationRequirement, RequirementWeightMap
from core.logging import get_logger

logger = get_logger("weight_engine")


class WeightCalculationEngine:
    """Requirement Weight Distribution Engine."""

    def calculate_weights(
        self, position: PositionInfo, qual: QualificationRequirement
    ) -> RequirementWeightMap:
        rank = position.academic_rank.lower()

        if "professor" in rank and "assistant" not in rank and "associate" not in rank:
            # Full Professor: Heavy research & experience weight
            weights = RequirementWeightMap(
                education_weight=0.20,
                experience_weight=0.25,
                research_weight=0.35,
                teaching_weight=0.10,
                skills_weight=0.10,
            )
        elif "associate" in rank:
            weights = RequirementWeightMap(
                education_weight=0.20,
                experience_weight=0.25,
                research_weight=0.30,
                teaching_weight=0.15,
                skills_weight=0.10,
            )
        else:
            # Assistant Professor: Balanced education, research, teaching & skills weight
            weights = RequirementWeightMap(
                education_weight=0.30,
                experience_weight=0.15,
                research_weight=0.25,
                teaching_weight=0.15,
                skills_weight=0.15,
            )

        logger.debug("Computed requirement weights", rank=position.academic_rank, research_weight=weights.research_weight)
        return weights
