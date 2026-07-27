"""
Component 7: Reading Order Engine.
Reconstructs actual visual reading order for single-column, multi-column academic CVs, sidebars, and headers/footers.
"""

from typing import List
from app.document.schemas.normalized_document import BlockNode, PageNode
from core.logging import get_logger

logger = get_logger("reading_order_engine")


class ReadingOrderEngine:
    """Component 7: Reading Order Reconstruction Engine."""

    def reconstruct_reading_order(self, pages: List[PageNode]) -> List[BlockNode]:
        ordered_blocks: List[BlockNode] = []
        global_order = 1

        for page in pages:
            page_width = page.width
            col_threshold = page_width / 2.0

            left_column_blocks: List[BlockNode] = []
            right_column_blocks: List[BlockNode] = []
            full_width_blocks: List[BlockNode] = []

            for block in page.blocks:
                box = block.coordinates
                if box.width > page_width * 0.75:
                    full_width_blocks.append(block)
                elif box.x0 < col_threshold and box.x1 <= col_threshold + 50:
                    left_column_blocks.append(block)
                else:
                    right_column_blocks.append(block)

            # Sort blocks top-to-bottom ($Y_0$), then left-to-right ($X_0$)
            left_column_blocks.sort(key=lambda b: (b.coordinates.y0, b.coordinates.x0))
            right_column_blocks.sort(key=lambda b: (b.coordinates.y0, b.coordinates.x0))
            full_width_blocks.sort(key=lambda b: (b.coordinates.y0, b.coordinates.x0))

            # Combine page blocks according to visual column layout
            page_ordered = []
            for b in full_width_blocks:
                if b.coordinates.y0 < page.height * 0.15:  # Header blocks
                    page_ordered.append(b)

            page_ordered.extend(left_column_blocks)
            page_ordered.extend(right_column_blocks)

            for b in full_width_blocks:
                if b not in page_ordered:
                    page_ordered.append(b)

            for block in page_ordered:
                block.reading_order = global_order
                ordered_blocks.append(block)
                global_order += 1

        logger.debug("Reading order reconstructed across document blocks", total_blocks=len(ordered_blocks))
        return ordered_blocks
