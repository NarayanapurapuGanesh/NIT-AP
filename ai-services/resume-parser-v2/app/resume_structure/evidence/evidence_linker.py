"""
Evidence Linker Engine.
Attaches 100% evidence provenance points to every detected SectionNode.
"""

from typing import List
from app.document.schemas.normalized_document import EvidencePoint
from app.resume_structure.schemas.semantic_resume import SectionNode
from core.logging import get_logger

logger = get_logger("evidence_linker")


class EvidenceLinker:
    """Evidence Linker & Lineage Engine."""

    def link_evidence(self, sections: List[SectionNode]) -> List[SectionNode]:
        for sec in sections:
            evidence_list: List[EvidencePoint] = []
            for block in sec.blocks:
                for paragraph in block.paragraphs:
                    for line in paragraph.lines:
                        evidence_list.append(line.evidence)
            sec.evidence = evidence_list

        logger.debug("Evidence linking completed across sections")
        return sections
