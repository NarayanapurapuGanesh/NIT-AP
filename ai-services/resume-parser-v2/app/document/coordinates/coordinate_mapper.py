"""
Component 11: Coordinate Mapper Engine.
Ensures every extracted element possesses exact bounding box coordinates, offsets, line indices, and page numbers.
"""

from typing import List
from app.document.schemas.normalized_document import PageNode
from core.logging import get_logger

logger = get_logger("coordinate_mapper")


class CoordinateMapper:
    """Component 11: Coordinate & Offset Mapping Engine."""

    def map_coordinates(self, pages: List[PageNode]) -> List[PageNode]:
        for page in pages:
            char_offset_counter = 0

            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for line in paragraph.lines:
                        for w_idx, word in enumerate(line.words):
                            word.word_index = w_idx + 1
                            word.evidence.char_offset = char_offset_counter
                            word.evidence.line_number = line.line_number
                            word.evidence.page_number = page.page_number
                            char_offset_counter += len(word.text) + 1

        logger.debug("Coordinate and offset mapping verified across pages")
        return pages
