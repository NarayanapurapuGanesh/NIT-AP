"""
Traceability & Citation Manager Engine.
Maps source document, page, paragraph, bounding box, rule ID, decision ID, and model version.
"""

from typing import List
from app.explainability.schemas.explainability_models import ExplanationItem
from app.recruitment_agent.schemas.decision_models import RecruitmentDecisionReport
from core.logging import get_logger

logger = get_logger("traceability_engine")


class TraceabilityEngine:
    """Traceability & Score Explanation Engine."""

    def build_explanations(self, decision: RecruitmentDecisionReport) -> List[ExplanationItem]:
        items: List[ExplanationItem] = []

        items.append(
            ExplanationItem(
                metric_name="Final Recommendation",
                score_or_value=decision.recommendation,
                explanation_text=f"Synthesized by Multi-Agent Consensus with confidence {int(decision.overall_confidence * 100)}%.",
                supporting_evidence=decision.evidence,
            )
        )

        for op in decision.specialist_opinions:
            items.append(
                ExplanationItem(
                    metric_name=op.agent_name,
                    score_or_value=op.recommendation,
                    explanation_text=op.opinion,
                    supporting_evidence=decision.evidence[:2],
                )
            )

        logger.debug("Score & decision explanations built", count=len(items))
        return items
