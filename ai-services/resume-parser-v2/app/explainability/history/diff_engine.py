"""
Evaluation Diff Engine.
Compares current vs previous evaluation reports and explains changed scores, evidence, or recommendations.
"""

from typing import Any, Dict
from app.recruitment_agent.schemas.decision_models import RecruitmentDecisionReport
from core.logging import get_logger

logger = get_logger("diff_engine")


class EvaluationDiffEngine:
    """Evaluation Diff & History Comparator Engine."""

    def compare_decisions(
        self, prev: RecruitmentDecisionReport, curr: RecruitmentDecisionReport
    ) -> Dict[str, Any]:
        changed_rec = prev.recommendation != curr.recommendation
        return {
            "changed_recommendation": changed_rec,
            "previous_recommendation": prev.recommendation,
            "current_recommendation": curr.recommendation,
        }
