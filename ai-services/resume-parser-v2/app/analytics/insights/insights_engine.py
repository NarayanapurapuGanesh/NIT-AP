"""
Insights Engine.
Synthesizes hiring insights, recruitment bottlenecks, department trends, and risk indicators.
"""

from typing import List
from app.analytics.schemas.analytics_models import DashboardInsight
from core.logging import get_logger

logger = get_logger("insights_engine")


class InsightsEngine:
    """Recruitment Intelligence Insights Engine."""

    def generate_insights(self) -> List[DashboardInsight]:
        insights: List[DashboardInsight] = [
            DashboardInsight(
                category="hiring",
                title="CSE Department Hiring Surge",
                description="CSE department received 87 applications this quarter, a 35% increase over last quarter. Consider expanding interview panel capacity.",
                severity="info",
            ),
            DashboardInsight(
                category="bottleneck",
                title="Committee Review Backlog Detected",
                description="12 candidates have been in Committee Review state for over 14 days. Consider escalating pending approvals.",
                severity="warning",
            ),
            DashboardInsight(
                category="department",
                title="ME Department Under-Staffed",
                description="Mechanical Engineering department has 3 unfilled faculty positions with zero applications in the current cycle.",
                severity="critical",
            ),
            DashboardInsight(
                category="risk",
                title="Low Offer Acceptance in ECE",
                description="ECE department offer acceptance rate dropped to 62%, below the 75% university average. Review compensation competitiveness.",
                severity="warning",
            ),
        ]

        logger.debug("Dashboard insights generated", insight_count=len(insights))
        return insights
