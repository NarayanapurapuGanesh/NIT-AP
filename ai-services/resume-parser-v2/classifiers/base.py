"""
Classifiers Interface Package - Extension Point for Document & Section Classifiers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IClassifier(ABC):
    """Abstract interface for classification models and rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def classify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Classifies target input document or layout block."""
        pass
