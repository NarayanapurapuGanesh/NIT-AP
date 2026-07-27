"""
Panel Management Engine.
Assigns Department Experts, Research Experts, Teaching Experts, External Experts, and Panel Chair.
"""

from typing import List
from app.interview.schemas.interview_models import PanelMember
from core.logging import get_logger

logger = get_logger("panel_manager")


class PanelManagerEngine:
    """Panel Member Assignment & Management Engine."""

    def assign_panel(self, department_name: str) -> List[PanelMember]:
        panel = [
            PanelMember(name="Prof. HOD", role="Panel Chair", institution="NIT AP"),
            PanelMember(name="Dr. CSE Expert", role="Department Expert", institution="NIT AP"),
            PanelMember(name="Prof. External Dean", role="External Expert", institution="IIT Madras"),
            PanelMember(name="Dr. Industry Lead", role="Industry Expert", institution="Research Labs"),
        ]

        logger.debug("Interview panel assigned", members_count=len(panel))
        return panel
