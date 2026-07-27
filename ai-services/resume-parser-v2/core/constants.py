"""
System constants and immutable operational configurations for resume-parser-v2.
"""

from enum import Enum


class EnvironmentOption(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LogLevelOption(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# Header names
REQUEST_ID_HEADER = "X-Request-ID"
RESPONSE_TIME_HEADER = "X-Process-Time-MS"

# API Information
API_TITLE = "Academic Resume Intelligence Engine API"
API_DESCRIPTION = (
    "Production-grade foundation for multi-agent faculty recruitment and candidate analysis."
)
API_VERSION = "2.0.0"
