"""
Academic Taxonomy & Schema Ontology Abstractions.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class IOntologyProvider(ABC):
    """Abstract interface for taxonomy and entity relationship definitions."""

    @abstractmethod
    def resolve_academic_rank(self, title: str) -> Optional[str]:
        pass

    @abstractmethod
    def get_supported_categories(self) -> List[str]:
        pass
