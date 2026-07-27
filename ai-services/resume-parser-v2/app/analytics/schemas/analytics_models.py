"""
Canonical Pydantic v2 Models for Enterprise Recruitment Analytics & Executive Dashboard Platform.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class KPIMetric(BaseModel):
    kpi_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    value: float
    unit: str = "%"  # %, count, days, score
    trend: str = "stable"  # up, down, stable
    period: str = "monthly"
    department: Optional[str] = None


class ChartDataset(BaseModel):
    chart_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chart_type: str  # bar, line, area, pie, radar, heatmap, timeline
    title: str
    labels: List[str] = Field(default_factory=list)
    datasets: List[Dict[str, Any]] = Field(default_factory=list)


class DashboardInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str  # hiring, bottleneck, department, risk
    title: str
    description: str
    severity: str = "info"  # info, warning, critical


class WorkloadForecast(BaseModel):
    forecast_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str
    current_value: float
    predicted_value: float
    forecast_period: str = "next_quarter"
    confidence: float = 0.85


class AlertItem(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alert_type: str  # threshold_breach, deadline, anomaly
    message: str
    severity: str = "warning"


class AnalyticsDashboardReport(BaseModel):
    dashboard_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dashboard_type: str = "University Dashboard"
    kpis: List[KPIMetric] = Field(default_factory=list)
    charts: List[ChartDataset] = Field(default_factory=list)
    insights: List[DashboardInsight] = Field(default_factory=list)
    forecasts: List[WorkloadForecast] = Field(default_factory=list)
    alerts: List[AlertItem] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processing_time_ms: float = 0.0
