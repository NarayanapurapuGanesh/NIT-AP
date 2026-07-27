"""
Recruitment Analytics & Executive Dashboard Endpoints.
GET /api/v1/analytics/dashboard
GET /api/v1/analytics/kpi
GET /api/v1/analytics/charts
GET /api/v1/analytics/reports
"""

from typing import List
from fastapi import APIRouter, Query
from app.analytics.pipeline.analytics_pipeline import AnalyticsPipeline
from app.analytics.schemas.analytics_models import AnalyticsDashboardReport, ChartDataset, KPIMetric
from schemas.base import BaseResponse

router = APIRouter()

analytics_pipeline = AnalyticsPipeline()


@router.get(
    "/analytics/dashboard",
    response_model=BaseResponse[AnalyticsDashboardReport],
    summary="Get Executive Analytics Dashboard",
    description="Returns full analytics dashboard with KPIs, charts, insights, forecasts, and alerts.",
)
async def get_analytics_dashboard(
    dashboard_type: str = Query(default="University Dashboard", description="Dashboard type"),
) -> BaseResponse[AnalyticsDashboardReport]:
    report = await analytics_pipeline.generate_dashboard(dashboard_type)

    return BaseResponse(
        success=True,
        message=f"Analytics dashboard '{dashboard_type}' generated ({len(report.kpis)} KPIs, {len(report.charts)} charts).",
        data=report,
    )


@router.get(
    "/analytics/kpi",
    response_model=BaseResponse[List[KPIMetric]],
    summary="Get Recruitment KPIs",
    description="Returns all 12 core recruitment KPI metrics.",
)
async def get_kpis() -> BaseResponse[List[KPIMetric]]:
    kpis = analytics_pipeline.get_kpis()

    return BaseResponse(
        success=True,
        message=f"Computed {len(kpis)} recruitment KPIs.",
        data=kpis,
    )


@router.get(
    "/analytics/charts",
    response_model=BaseResponse[List[ChartDataset]],
    summary="Get Chart Datasets",
    description="Returns structured JSON chart datasets for Bar, Line, Pie, Radar, and Heatmap visualizations.",
)
async def get_charts() -> BaseResponse[List[ChartDataset]]:
    charts = analytics_pipeline.get_charts()

    return BaseResponse(
        success=True,
        message=f"Generated {len(charts)} chart datasets.",
        data=charts,
    )


@router.get(
    "/analytics/reports",
    response_model=BaseResponse[AnalyticsDashboardReport],
    summary="Get Analytics Export Report",
    description="Returns exportable analytics report with full KPI, chart, insight, and forecast data.",
)
async def get_analytics_report() -> BaseResponse[AnalyticsDashboardReport]:
    report = await analytics_pipeline.generate_dashboard("Export Report")

    return BaseResponse(
        success=True,
        message="Analytics export report generated.",
        data=report,
    )
