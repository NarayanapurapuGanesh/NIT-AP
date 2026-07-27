"""
End-to-End Enterprise Recruitment Analytics Pipeline.
Orchestrates KPI Calculation, Multi-Chart Generation, Insights Synthesis,
Workload Forecasting, Export Engine, and Repository Persistence.
"""

import time
from typing import List
from app.analytics.charts.chart_generator import ChartDataGeneratorEngine
from app.analytics.export.export_engine import ExportEngine
from app.analytics.forecast.forecast_engine import WorkloadForecastEngine
from app.analytics.insights.insights_engine import InsightsEngine
from app.analytics.kpi.kpi_engine import KPICalculationEngine
from app.analytics.schemas.analytics_models import AnalyticsDashboardReport, ChartDataset, KPIMetric
from app.analytics.services.analytics_service import AnalyticsRepositoryService
from core.logging import get_logger

logger = get_logger("analytics_pipeline")


class AnalyticsPipeline:
    """Enterprise Recruitment Analytics Pipeline Engine."""

    def __init__(self) -> None:
        self.kpi_engine = KPICalculationEngine()
        self.chart_generator = ChartDataGeneratorEngine()
        self.insights_engine = InsightsEngine()
        self.forecast_engine = WorkloadForecastEngine()
        self.export_engine = ExportEngine()
        self.repository_service = AnalyticsRepositoryService.get_instance()

    async def generate_dashboard(self, dashboard_type: str = "University Dashboard") -> AnalyticsDashboardReport:
        """Generates full analytics dashboard report."""
        start_time = time.perf_counter()

        kpis = self.kpi_engine.compute_kpis()
        charts = self.chart_generator.generate_charts()
        insights = self.insights_engine.generate_insights()
        forecasts = self.forecast_engine.generate_forecasts()

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        report = AnalyticsDashboardReport(
            dashboard_type=dashboard_type,
            kpis=kpis,
            charts=charts,
            insights=insights,
            forecasts=forecasts,
            processing_time_ms=processing_time_ms,
        )

        self.repository_service.save_dashboard(report)

        logger.info(
            "Analytics dashboard generated",
            dashboard_id=report.dashboard_id,
            dashboard_type=dashboard_type,
            kpi_count=len(kpis),
            chart_count=len(charts),
            insight_count=len(insights),
            forecast_count=len(forecasts),
            duration_ms=processing_time_ms,
        )

        return report

    def get_kpis(self) -> List[KPIMetric]:
        return self.kpi_engine.compute_kpis()

    def get_charts(self) -> List[ChartDataset]:
        return self.chart_generator.generate_charts()
