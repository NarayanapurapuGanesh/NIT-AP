"""
Detectors Interface Package - Extension Point for Section & Table Bounding Box Detection.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IDetector(ABC):
    """Abstract interface for detection modules (e.g. section boundaries, tables)."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def detect(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detects region boundaries or section headers."""
        pass
