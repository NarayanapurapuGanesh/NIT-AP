"""
Layout Processing Interface Package.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ILayoutAnalyzer(ABC):
    """Abstract interface for document layout decomposition."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def analyze_layout(self, document_bytes: bytes) -> Dict[str, Any]:
        """Decomposes PDF/document into structured layout bounding boxes and blocks."""
        pass
