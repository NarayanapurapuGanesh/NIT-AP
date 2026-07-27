"""
Normalizers Interface Package.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class INormalizer(ABC):
    """Abstract interface for canonicalizing extracted features (e.g. dates, institutions, degree ranks)."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes entity attributes to standardized ontology types."""
        pass
