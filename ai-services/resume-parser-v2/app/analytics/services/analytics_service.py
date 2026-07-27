"""
Analytics Storage Repository Service.
In-memory and persistent repository storing dashboard snapshots and historical analytics.
"""

from typing import Dict, Optional
from app.analytics.schemas.analytics_models import AnalyticsDashboardReport
from core.logging import get_logger

logger = get_logger("analytics_service")


class AnalyticsRepositoryService:
    """Analytics Storage Service."""

    _instance: Optional["AnalyticsRepositoryService"] = None

    def __init__(self) -> None:
        self._dashboards_by_id: Dict[str, AnalyticsDashboardReport] = {}

    @classmethod
    def get_instance(cls) -> "AnalyticsRepositoryService":
        if cls._instance is None:
            cls._instance = AnalyticsRepositoryService()
        return cls._instance

    def save_dashboard(self, report: AnalyticsDashboardReport) -> None:
        self._dashboards_by_id[report.dashboard_id] = report
        logger.info("Saved analytics dashboard to repository", dashboard_id=report.dashboard_id)

    def get_dashboard(self, dashboard_id: str) -> Optional[AnalyticsDashboardReport]:
        return self._dashboards_by_id.get(dashboard_id)
