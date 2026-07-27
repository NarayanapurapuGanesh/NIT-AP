"""
Rubric Generator Engine.
Generates 5-level evaluation rubrics (Knowledge, Teaching Ability, Research Ability, Technical Skill, Communication, Leadership).
"""

from typing import List
from app.interview.schemas.interview_models import EvaluationRubric
from core.logging import get_logger

logger = get_logger("rubric_generator")

DEFAULT_DIMENSIONS = [
    "Subject Matter Knowledge",
    "Teaching & Pedagogical Ability",
    "Research Depth & Publication Impact",
    "Problem Solving & Technical Skill",
    "Communication & Academic Leadership",
]


class RubricGeneratorEngine:
    """5-Level Evaluation Rubric Generator Engine."""

    def generate_rubrics(self) -> List[EvaluationRubric]:
        rubrics = [
            EvaluationRubric(
                dimension_name=dim,
                description=f"Evaluates candidate's level of {dim.lower()}.",
            )
            for dim in DEFAULT_DIMENSIONS
        ]

        logger.debug("Evaluation rubrics generated", count=len(rubrics))
        return rubrics
