"""
16-State Finite State Machine Engine for Enterprise Faculty Recruitment.
"""

from typing import List, Set
from app.workflow.schemas.workflow_models import StateTransitionRecord
from core.logging import get_logger

logger = get_logger("state_machine")

VALID_STATES: Set[str] = {
    "Draft",
    "Published",
    "Applications Open",
    "Screening",
    "Matching",
    "AI Review",
    "Human Review",
    "Interview Scheduled",
    "Interview Completed",
    "Committee Review",
    "Offer Pending",
    "Offer Accepted",
    "Offer Rejected",
    "Closed",
    "Cancelled",
}

STATE_FLOW = [
    "Draft",
    "Published",
    "Applications Open",
    "Screening",
    "Matching",
    "AI Review",
    "Human Review",
    "Interview Scheduled",
    "Interview Completed",
    "Committee Review",
    "Offer Pending",
    "Offer Accepted",
    "Closed",
]


class RecruitmentStateMachine:
    """16-State Recruitment FSM Engine."""

    def get_next_state(self, current_state: str) -> str:
        if current_state in STATE_FLOW:
            idx = STATE_FLOW.index(current_state)
            if idx + 1 < len(STATE_FLOW):
                return STATE_FLOW[idx + 1]
        return "Closed"

    def transition_state(
        self, current_state: str, target_state: str, triggered_by: str = "system"
    ) -> StateTransitionRecord:
        if target_state not in VALID_STATES:
            raise ValueError(f"Invalid target state '{target_state}'.")

        record = StateTransitionRecord(
            from_state=current_state,
            to_state=target_state,
            triggered_by=triggered_by,
        )

        logger.info(
            "State transition executed",
            from_state=current_state,
            to_state=target_state,
            triggered_by=triggered_by,
        )

        return record
