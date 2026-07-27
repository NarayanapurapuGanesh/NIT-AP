"""
Plugin SDK.
Defines base abstract plugin interfaces for Recruitment, Evaluation, Interview,
Analytics, Workflow, Notification, AI Provider, and Document Parser plugins.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from app.integration.schemas.integration_models import PluginMetadata
from core.logging import get_logger

logger = get_logger("plugin_sdk")


class BaseFacultyIQPlugin(ABC):
    """Abstract Base Class for all FacultyIQ Plugins."""

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass


class RecruitmentPlugin(BaseFacultyIQPlugin):
    """Base class for recruitment extensions."""
    pass


class EvaluationPlugin(BaseFacultyIQPlugin):
    """Base class for candidate evaluation extensions."""
    pass


class InterviewPlugin(BaseFacultyIQPlugin):
    """Base class for interview assessment extensions."""
    pass


class AnalyticsPlugin(BaseFacultyIQPlugin):
    """Base class for analytics reporting extensions."""
    pass


class AIProviderPlugin(BaseFacultyIQPlugin):
    """Base class for custom AI provider extensions."""
    pass


class DocumentParserPlugin(BaseFacultyIQPlugin):
    """Base class for document parsing extensions."""
    pass
