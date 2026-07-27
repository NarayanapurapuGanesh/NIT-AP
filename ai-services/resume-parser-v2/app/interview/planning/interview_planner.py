"""
Interview Planning Engine.
Generates multi-round interview workflows: Technical Interview, Teaching Demonstration, Research Presentation, Panel Discussion.
"""

from typing import List
from app.interview.schemas.interview_models import InterviewRoundPlan, PanelMember
from core.logging import get_logger

logger = get_logger("interview_planner")


class InterviewPlannerEngine:
    """Multi-Round Interview Workflow Planner Engine."""

    def build_interview_rounds(self, position_title: str) -> List[InterviewRoundPlan]:
        default_panel = [
            PanelMember(name="Prof. HOD", role="Panel Chair"),
            PanelMember(name="Dr. Tech Expert", role="Department Expert"),
        ]

        rounds = [
            InterviewRoundPlan(round_name="Technical Interview", duration_mins=45, panel=default_panel),
            InterviewRoundPlan(round_name="Teaching Demonstration", duration_mins=30, panel=default_panel),
            InterviewRoundPlan(round_name="Research Presentation", duration_mins=45, panel=default_panel),
            InterviewRoundPlan(round_name="Panel Discussion & HR", duration_mins=30, panel=default_panel),
        ]

        logger.debug("Interview rounds planned", rounds_count=len(rounds))
        return rounds
