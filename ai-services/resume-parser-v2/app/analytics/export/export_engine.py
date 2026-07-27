"""
Multi-Format Export Engine.
Generates CSV and JSON dashboard report exports.
"""

import csv
import io
import json
from typing import Any, Dict
from app.analytics.schemas.analytics_models import AnalyticsDashboardReport
from core.logging import get_logger

logger = get_logger("export_engine")


class ExportEngine:
    """Multi-Format Dashboard Export Engine."""

    def export_to_json(self, report: AnalyticsDashboardReport) -> str:
        return report.model_dump_json(indent=2)

    def export_kpis_to_csv(self, report: AnalyticsDashboardReport) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["KPI Name", "Value", "Unit", "Trend", "Period"])
        for kpi in report.kpis:
            writer.writerow([kpi.name, kpi.value, kpi.unit, kpi.trend, kpi.period])
        csv_content = output.getvalue()
        output.close()

        logger.debug("KPIs exported to CSV format", kpi_count=len(report.kpis))
        return csv_content
