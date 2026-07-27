"""
Tests for configuration loader.
"""

from core.config import settings
from core.constants import EnvironmentOption


def test_configuration_defaults():
    assert settings.APP_NAME == "resume-parser-v2"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.APP_ENV in [EnvironmentOption.DEVELOPMENT, EnvironmentOption.TESTING, EnvironmentOption.PRODUCTION]


def test_cors_origins_parsing():
    parsed = settings.parse_cors_and_hosts("http://localhost:3000, http://localhost:8000")
    assert "http://localhost:3000" in parsed
    assert "http://localhost:8000" in parsed
