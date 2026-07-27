"""
Component 8: Layout Analysis Engine.
Detects margins, section headers, column structures, headers/footers, whitespace, and visual hierarchy.
"""

from typing import List
from app.document.schemas.normalized_document import BlockNode, PageNode
from core.logging import get_logger

logger = get_logger("layout_analysis_engine")


class LayoutAnalysisEngine:
    """Component 8: Visual & Structural Layout Analyzer."""

    def analyze_layout(self, pages: List[PageNode]) -> List[PageNode]:
        for page in pages:
            top_margin = page.height * 0.08
            bottom_margin = page.height * 0.92

            for block in page.blocks:
                y0 = block.coordinates.y0
                y1 = block.coordinates.y1

                if y1 <= top_margin:
                    block.block_type = "header"
                elif y0 >= bottom_margin:
                    block.block_type = "footer"
                elif len(block.text) < 60 and not block.text.endswith("."):
                    if block.text.isupper() or block.text.istitle():
                        block.block_type = "heading"
                else:
                    block.block_type = "text"

        logger.debug("Layout analysis completed across pages")
        return pages
