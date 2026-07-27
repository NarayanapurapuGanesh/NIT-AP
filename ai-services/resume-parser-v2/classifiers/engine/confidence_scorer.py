"""
Layer 7: Confidence Scorer.
Aggregates positive weights and negative penalties per candidate document type and produces a normalized confidence score (0.00 to 1.00).
"""

import math
from typing import Dict, List, Tuple
from classifiers.engine.rule_engine import RuleMatchResult
from core.logging import get_logger

logger = get_logger("confidence_scorer")


class TypeConfidenceScore:
    def __init__(self, doc_type: str, confidence: float, matched_rules: List[RuleMatchResult]) -> None:
        self.doc_type = doc_type
        self.confidence = confidence
        self.matched_rules = matched_rules


class ConfidenceScorer:
    """Layer 7: Normalized Confidence Scorer."""

    def compute_confidence(self, all_matches: List[RuleMatchResult]) -> Tuple[str, float, List[RuleMatchResult]]:
        if not all_matches:
            return "Unknown", 0.0, []

        scores_by_type: Dict[str, float] = {}
        matches_by_type: Dict[str, List[RuleMatchResult]] = {}

        for match in all_matches:
            doc_type = match.doc_type
            if doc_type not in scores_by_type:
                scores_by_type[doc_type] = 0.0
                matches_by_type[doc_type] = []

            scores_by_type[doc_type] += match.weight
            matches_by_type[doc_type].append(match)

        # Normalize score bounds between 0.00 and 1.00
        best_type = "Unknown"
        best_confidence = 0.0

        for doc_type, raw_score in scores_by_type.items():
            # Asymptotic normalization formula: 1 - exp(-raw_score * 1.2)
            # score = 0.40 -> ~0.38, 0.70 -> ~0.57, 1.2 -> ~0.76, 2.0 -> ~0.91
            normalized_score = round(1.0 - math.exp(-max(0.0, raw_score) * 1.5), 2)
            if raw_score >= 0.85:
                normalized_score = min(0.98, max(normalized_score, 0.90))

            if normalized_score > best_confidence:
                best_confidence = normalized_score
                best_type = doc_type

        if best_confidence < 0.25:
            best_type = "Unknown"
            best_confidence = 0.15

        logger.debug(
            "Confidence scoring complete",
            winning_type=best_type,
            confidence=best_confidence,
        )

        winning_matches = matches_by_type.get(best_type, [])
        return best_type, best_confidence, winning_matches
