"""
Pytest integration & unit tests for Phase 13 Enterprise Recruitment Analytics & Executive Dashboard Platform.
"""

import pytest
from httpx import AsyncClient
from app.analytics.pipeline.analytics_pipeline import AnalyticsPipeline


@pytest.fixture
def analytics_pipeline():
    return AnalyticsPipeline()


@pytest.mark.anyio
async def test_analytics_pipeline_dashboard_generation(analytics_pipeline: AnalyticsPipeline):
    report = await analytics_pipeline.generate_dashboard("University Dashboard")

    assert report.dashboard_type == "University Dashboard"
    assert len(report.kpis) == 12
    assert len(report.charts) == 5
    assert len(report.insights) == 4
    assert len(report.forecasts) == 3
    assert report.processing_time_ms > 0


@pytest.mark.anyio
async def test_kpi_computation(analytics_pipeline: AnalyticsPipeline):
    kpis = analytics_pipeline.get_kpis()
    assert len(kpis) == 12
    kpi_names = [k.name for k in kpis]
    assert "Applications Received" in kpi_names
    assert "Average Match Score" in kpi_names
    assert "Offer Acceptance Rate" in kpi_names


@pytest.mark.anyio
async def test_chart_generation(analytics_pipeline: AnalyticsPipeline):
    charts = analytics_pipeline.get_charts()
    assert len(charts) == 5
    chart_types = [c.chart_type for c in charts]
    assert "bar" in chart_types
    assert "line" in chart_types
    assert "pie" in chart_types
    assert "radar" in chart_types
    assert "heatmap" in chart_types


@pytest.mark.anyio
async def test_analytics_api_dashboard_endpoint(async_client: AsyncClient):
    res = await async_client.get("/api/v1/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]["kpis"]) == 12
    assert len(data["data"]["charts"]) == 5


@pytest.mark.anyio
async def test_analytics_api_kpi_endpoint(async_client: AsyncClient):
    res = await async_client.get("/api/v1/analytics/kpi")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) == 12


@pytest.mark.anyio
async def test_analytics_api_charts_endpoint(async_client: AsyncClient):
    res = await async_client.get("/api/v1/analytics/charts")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) == 5
