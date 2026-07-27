"""
Pytest configuration and fixtures.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client():
    """Async test HTTP client fixture for FastAPI endpoint verification."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
