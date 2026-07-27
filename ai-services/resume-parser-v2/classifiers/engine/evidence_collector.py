"""
Layer 8: Evidence Collector.
Aggregates matched rules, reasons, and weight contributions into structured EvidenceItem objects.
"""

from typing import List, Tuple
from classifiers.engine.rule_engine import RuleMatchResult
from schemas.classification import EvidenceItem
from core.logging import get_logger

logger = get_logger("evidence_collector")


class EvidenceCollector:
    """Layer 8: Evidence & Reason Collector."""

    def collect_evidence(
        self, winning_matches: List[RuleMatchResult]
    ) -> Tuple[List[str], List[EvidenceItem]]:
        reasons: List[str] = []
        evidence_items: List[EvidenceItem] = []

        for match in winning_matches:
            reasons.append(match.reason)
            evidence_items.append(
                EvidenceItem(
                    rule=match.rule_id,
                    weight=match.weight,
                    matched_text=match.matched_text,
                    source_layer="rule_engine" if not match.rule_id.startswith("pat_") else "pattern_engine",
                )
            )

        if not reasons:
            reasons.append("No specific rule or keyword pattern matches were identified.")

        logger.debug("Collected classification evidence", reason_count=len(reasons))
        return reasons, evidence_items
