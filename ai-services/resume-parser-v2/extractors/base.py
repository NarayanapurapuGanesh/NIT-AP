"""
Extractors Interface Package - Extension Point for Information Extraction Modules.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class IExtractor(ABC):
    """Abstract contract for feature and entity extractors."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts structured entities from parsed text or layout blocks."""
        pass
