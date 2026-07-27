"""
Component 12: Evidence Builder Engine.
Preserves 100% lineage traceability for every extracted word and line.
"""

from typing import List
from app.document.schemas.normalized_document import EvidencePoint, PageNode
from core.logging import get_logger

logger = get_logger("evidence_builder")


class EvidenceBuilder:
    """Component 12: Lineage Traceability & Evidence Builder Engine."""

    def build_evidence_registry(self, pages: List[PageNode]) -> List[EvidencePoint]:
        evidence_points: List[EvidencePoint] = []

        for page in pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for line in paragraph.lines:
                        evidence_points.append(line.evidence)
                        for word in line.words:
                            evidence_points.append(word.evidence)

        logger.debug("Evidence registry populated", total_evidence_points=len(evidence_points))
        return evidence_points
