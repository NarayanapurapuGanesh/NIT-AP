"""
Evidence Graph & Lineage Tracking Base Interface.
Tracks exact document locations, bounding boxes, and source confidence for extracted facts.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class EvidenceSpan:
    page_number: int
    bounding_box: Optional[List[float]] = None
    source_text: str = ""
    confidence: float = 1.0


class IEvidenceTracker(ABC):
    """Abstract contract for recording lineage and evidence provenance."""

    @abstractmethod
    def record_evidence(self, entity_id: str, span: EvidenceSpan) -> None:
        pass

    @abstractmethod
    def get_evidence_graph(self, entity_id: str) -> Dict[str, Any]:
        pass
