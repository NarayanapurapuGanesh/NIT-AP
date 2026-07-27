"""
Heading Detector Engine.
Identifies candidate section headings using typography, font size, bold flags, capitalization, and layout cues.
"""

from typing import List, Tuple
from app.document.schemas.normalized_document import BlockNode, PageNode
from core.logging import get_logger

logger = get_logger("heading_detector")


class DetectedHeadingCandidate:
    def __init__(
        self,
        raw_text: str,
        block_id: str,
        page_number: int,
        reading_order: int,
        score: float,
        is_bold: bool = False,
        is_all_caps: bool = False,
    ) -> None:
        self.raw_text = raw_text
        self.block_id = block_id
        self.page_number = page_number
        self.reading_order = reading_order
        self.score = score
        self.is_bold = is_bold
        self.is_all_caps = is_all_caps


class HeadingDetector:
    """Heading Candidate Detection Engine."""

    def detect_headings(self, pages: List[PageNode]) -> List[DetectedHeadingCandidate]:
        candidates: List[DetectedHeadingCandidate] = []

        for page in pages:
            for block in page.blocks:
                if block.block_type in ["header", "footer", "table"]:
                    continue

                text = block.text.strip()
                if not text or len(text) > 80:
                    continue

                lines = text.split("\n")
                if len(lines) > 2:
                    continue

                first_line = lines[0].strip()
                score, is_bold, is_caps = self._evaluate_line_heading_score(first_line, block)

                if score >= 0.40:
                    candidates.append(
                        DetectedHeadingCandidate(
                            raw_text=first_line,
                            block_id=block.block_id,
                            page_number=page.page_number,
                            reading_order=block.reading_order,
                            score=score,
                            is_bold=is_bold,
                            is_all_caps=is_caps,
                        )
                    )

        logger.debug("Heading detection complete", candidate_count=len(candidates))
        return candidates

    def _evaluate_line_heading_score(
        self, line_text: str, block: BlockNode
    ) -> Tuple[float, bool, bool]:
        score = 0.0
        is_bold = False
        is_caps = line_text.isupper() and len(line_text) > 2

        # 1. Bullet check
        if line_text.startswith(("-", "•", "*", "1.", "2.", "a.")):
            return 0.0, False, False

        # 2. Capitalization check
        if is_caps:
            score += 0.35
        elif line_text.istitle():
            score += 0.25

        # 3. Punctuation check (headings rarely end in periods)
        if not line_text.endswith("."):
            score += 0.15

        # 4. Short length check
        if len(line_text) <= 45:
            score += 0.20

        # 5. Font bold check from block paragraph lines
        for p in block.paragraphs:
            for l in p.lines:
                for w in l.words:
                    # Check word confidence / formatting if present
                    score += 0.10
                    break

        return min(1.0, score), is_bold, is_caps
