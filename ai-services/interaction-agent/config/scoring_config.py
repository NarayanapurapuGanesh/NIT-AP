"""Scoring configuration for the Teaching Interaction Agent.

All evaluation weights, thresholds, and scoring rules are configurable here.
Do NOT hard-code business scoring rules into LLM prompts.
"""

import os


class ScoringConfig:
    """Configurable scoring weights and thresholds."""

    # ─── Primary Teaching Score Weights (must sum to 1.0) ─────────

    WEIGHT_TECHNICAL_ACCURACY: float = 0.20
    WEIGHT_CONCEPT_CLARITY: float = 0.20
    WEIGHT_DOUBT_RESOLUTION: float = 0.20
    WEIGHT_PEDAGOGICAL_ADAPTABILITY: float = 0.15
    WEIGHT_EXPLANATION_STRUCTURE: float = 0.10
    WEIGHT_EXAMPLE_QUALITY: float = 0.05
    WEIGHT_BLOOM_DEPTH: float = 0.05
    WEIGHT_MISCONCEPTION_HANDLING: float = 0.05

    # ─── Recommendation Thresholds ────────────────────────────────

    THRESHOLD_STRONG: float = 0.80
    THRESHOLD_GOOD: float = 0.65
    THRESHOLD_AVERAGE: float = 0.45
    # Below AVERAGE → NEEDS_IMPROVEMENT

    # ─── Bloom Progression ────────────────────────────────────────

    BLOOM_ORDER = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

    # Minimum turn before allowing Bloom advancement
    MIN_TURNS_BEFORE_BLOOM_ADVANCE: int = 2

    # Understanding threshold to advance Bloom level
    UNDERSTANDING_ADVANCE_THRESHOLD: float = 0.65

    # ─── Session End Criteria ─────────────────────────────────────

    # End session if understanding is very high and enough turns have passed
    UNDERSTANDING_COMPLETION_THRESHOLD: float = 0.92
    MIN_TURNS_FOR_COMPLETION: int = 8

    # ─── Adaptive Difficulty ──────────────────────────────────────

    # After N consecutive good responses, increase difficulty
    GOOD_RESPONSE_THRESHOLD: float = 0.70
    CONSECUTIVE_GOOD_TO_ADVANCE: int = 2

    # After N consecutive weak responses, decrease or maintain difficulty
    WEAK_RESPONSE_THRESHOLD: float = 0.40
    CONSECUTIVE_WEAK_TO_REDUCE: int = 2

    # ─── Evidence Collection ──────────────────────────────────────

    # Minimum score to register as a notable strength
    STRENGTH_THRESHOLD: float = 0.75

    # Maximum score to register as a notable weakness
    WEAKNESS_THRESHOLD: float = 0.40

    # ─── Question Quality ─────────────────────────────────────────

    # Maximum semantic similarity allowed between questions (0-1)
    MAX_QUESTION_SIMILARITY: float = 0.85

    # Maximum consecutive questions at the same Bloom level
    MAX_SAME_BLOOM_QUESTIONS: int = 3

    def get_recommendation(self, overall_score: float) -> str:
        """Determine recommendation based on overall score."""
        if overall_score >= self.THRESHOLD_STRONG:
            return "STRONG"
        elif overall_score >= self.THRESHOLD_GOOD:
            return "GOOD"
        elif overall_score >= self.THRESHOLD_AVERAGE:
            return "AVERAGE"
        else:
            return "NEEDS_IMPROVEMENT"

    def calculate_overall_score(
        self,
        technical_accuracy: float,
        concept_clarity: float,
        doubt_resolution: float,
        pedagogical_adaptability: float,
        explanation_structure: float,
        example_quality: float,
        bloom_depth: float,
        misconception_handling: float,
    ) -> float:
        """Calculate weighted overall teaching score."""
        score = (
            technical_accuracy * self.WEIGHT_TECHNICAL_ACCURACY
            + concept_clarity * self.WEIGHT_CONCEPT_CLARITY
            + doubt_resolution * self.WEIGHT_DOUBT_RESOLUTION
            + pedagogical_adaptability * self.WEIGHT_PEDAGOGICAL_ADAPTABILITY
            + explanation_structure * self.WEIGHT_EXPLANATION_STRUCTURE
            + example_quality * self.WEIGHT_EXAMPLE_QUALITY
            + bloom_depth * self.WEIGHT_BLOOM_DEPTH
            + misconception_handling * self.WEIGHT_MISCONCEPTION_HANDLING
        )
        return round(min(1.0, max(0.0, score)), 4)

    def should_advance_bloom(
        self, understanding: float, turns_at_level: int
    ) -> bool:
        """Determine if the Bloom level should advance."""
        return (
            understanding >= self.UNDERSTANDING_ADVANCE_THRESHOLD
            and turns_at_level >= self.MIN_TURNS_BEFORE_BLOOM_ADVANCE
        )


scoring_config = ScoringConfig()
