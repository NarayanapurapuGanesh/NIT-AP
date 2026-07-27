"""
Workflow Rule Engine.
Evaluates configurable workflow policies (minimum score thresholds, mandatory qualifications).
"""

from core.logging import get_logger

logger = get_logger("workflow_rule_engine")


class WorkflowRuleEngine:
    """Configurable Workflow Rule Engine."""

    def evaluate_advance_rule(self, score: float, min_required: float = 70.0) -> bool:
        return score >= min_required
