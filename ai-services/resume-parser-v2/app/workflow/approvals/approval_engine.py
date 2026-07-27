"""
Approval & Human-in-the-Loop Engine.
Manages reviewer approvals, AI recommendation overrides, re-evaluations, and comments with audit trails.
"""

from app.workflow.schemas.workflow_models import ApprovalRecord
from core.logging import get_logger

logger = get_logger("approval_engine")


class HumanApprovalEngine:
    """Human-in-the-Loop Approval Engine."""

    def record_approval_action(
        self,
        actor_id: str,
        actor_role: str,
        action: str,
        original_ai_decision: str,
        final_human_decision: str,
        comments: str = "",
    ) -> ApprovalRecord:
        record = ApprovalRecord(
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            original_ai_decision=original_ai_decision,
            final_human_decision=final_human_decision,
            comments=comments,
        )

        logger.info(
            "Approval action recorded cleanly",
            actor_id=actor_id,
            action=action,
            human_decision=final_human_decision,
        )

        return record
