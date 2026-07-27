"""
Core Module for resume-parser-v2.

Contains foundational configuration, structured logging, custom exception hierarchy,
security options, and middleware components.
"""

from core.config import settings
from core.exceptions import BaseAppException
from core.logging import get_logger, setup_logging

__all__ = ["settings", "setup_logging", "get_logger", "BaseAppException"]
