"""
Confidence Engine.
Calculates deterministic field-level confidence scores based on pattern precision and evidence provenance.
"""

from typing import Any
from app.information_extraction.schemas.candidate_profile import ExtractedField
from core.logging import get_logger

logger = get_logger("confidence_engine")


class ConfidenceEngine:
    """Field Confidence Evaluator."""

    def evaluate_confidence(self, field: ExtractedField[Any], base_rule_precision: float) -> float:
        if field.value is None:
            return 0.0

        score = base_rule_precision
        if field.evidence:
            score += 0.05
        if field.normalized_value:
            score += 0.05

        final_score = min(1.0, max(0.0, round(score, 2)))
        field.confidence = final_score
        return final_score
