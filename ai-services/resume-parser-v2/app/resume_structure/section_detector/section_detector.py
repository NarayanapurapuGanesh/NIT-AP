"""
Section Detector & Segmenter Engine.
Converts classified heading candidates and document blocks into distinct SectionNode instances.
"""

from typing import Dict, List, Tuple
from app.document.schemas.normalized_document import BlockNode, PageNode
from app.resume_structure.heading_classifier.heading_classifier import ClassifiedHeading, HeadingClassifier
from app.resume_structure.heading_detector.heading_detector import HeadingDetector
from app.resume_structure.schemas.semantic_resume import SectionNode
from core.logging import get_logger

logger = get_logger("section_detector")


class SectionDetectorEngine:
    """Section Detector & Boundary Segmenter Engine."""

    def __init__(self) -> None:
        self.heading_detector = HeadingDetector()
        self.heading_classifier = HeadingClassifier()

    def detect_sections(self, pages: List[PageNode]) -> Tuple[List[SectionNode], SectionNode | None, SectionNode | None]:
        heading_candidates = self.heading_detector.detect_headings(pages)
        classified_headings: List[ClassifiedHeading] = [
            self.heading_classifier.classify_heading(cand) for cand in heading_candidates
        ]

        # Map block_id -> ClassifiedHeading
        heading_map: Dict[str, ClassifiedHeading] = {
            ch.candidate.block_id: ch for ch in classified_headings
        }

        all_blocks: List[BlockNode] = [b for p in pages for b in p.blocks]
        sections: List[SectionNode] = []
        header_section: SectionNode | None = None
        summary_section: SectionNode | None = None

        current_heading: ClassifiedHeading | None = None
        current_blocks: List[BlockNode] = []
        current_pages: set[int] = set()

        for page in pages:
            for block in page.blocks:
                b_id = block.block_id

                if b_id in heading_map:
                    # Flush current accumulating section
                    if current_heading and current_blocks:
                        sec_node = self._build_section_node(current_heading, current_blocks, current_pages)
                        sections.append(sec_node)

                    # Start new section
                    current_heading = heading_map[b_id]
                    current_blocks = [block]
                    current_pages = {page.page_number}
                else:
                    if current_heading:
                        current_blocks.append(block)
                        current_pages.add(page.page_number)
                    else:
                        # Unheaded leading blocks -> Implicit Header section
                        if not header_section:
                            header_section = SectionNode(
                                canonical_type="Header",
                                original_heading="Header",
                                heading_level=1,
                                confidence=0.90,
                                priority=1,
                                page_numbers=[page.page_number],
                                blocks=[block],
                                raw_text=block.text,
                            )
                        else:
                            header_section.blocks.append(block)
                            header_section.raw_text += "\n" + block.text

        # Flush final accumulating section
        if current_heading and current_blocks:
            sec_node = self._build_section_node(current_heading, current_blocks, current_pages)
            sections.append(sec_node)

        # Extract summary block if present
        for sec in sections:
            if sec.canonical_type == "Summary":
                summary_section = sec
                break

        logger.info(
            "Section detection & segmentation complete",
            detected_sections=len(sections),
            has_header=header_section is not None,
            has_summary=summary_section is not None,
        )

        return sections, header_section, summary_section

    def _build_section_node(
        self, classified: ClassifiedHeading, blocks: List[BlockNode], pages: set[int]
    ) -> SectionNode:
        raw_text = "\n\n".join(b.text for b in blocks)
        boxes = [b.coordinates for b in blocks]
        p_count = sum(len(b.paragraphs) for b in blocks)
        r_start = blocks[0].reading_order if blocks else 0
        r_end = blocks[-1].reading_order if blocks else 0

        return SectionNode(
            canonical_type=classified.canonical_type,
            original_heading=classified.candidate.raw_text,
            heading_level=1,
            confidence=classified.confidence,
            priority=classified.priority,
            page_numbers=sorted(list(pages)),
            reading_order_start=r_start,
            reading_order_end=r_end,
            bounding_boxes=boxes,
            blocks=blocks,
            paragraphs_count=p_count,
            raw_text=raw_text,
        )
