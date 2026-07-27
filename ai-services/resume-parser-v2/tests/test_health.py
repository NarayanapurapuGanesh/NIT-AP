"""
Tests for health, version, and readiness endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["status"] == "healthy"
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time-MS" in response.headers


@pytest.mark.anyio
async def test_version_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/version")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["version"] == "2.0.0"


@pytest.mark.anyio
async def test_readiness_endpoint(async_client: AsyncClient):
    response = await async_client.get("/api/v1/readiness")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["ready"] is True
