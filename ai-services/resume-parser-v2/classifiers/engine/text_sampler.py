"""
Layer 4: Text Sampler.
Extracts strategic structural samples: header block, footer block, candidate section headings, and first page content.
"""

from typing import List
from classifiers.engine.document_reader import RawDocumentContent
from core.logging import get_logger

logger = get_logger("text_sampler")


class TextSample:
    def __init__(
        self,
        full_text: str,
        header_text: str,
        footer_text: str,
        first_page_text: str,
        heading_candidates: List[str],
    ) -> None:
        self.full_text = full_text
        self.header_text = header_text
        self.footer_text = footer_text
        self.first_page_text = first_page_text
        self.heading_candidates = heading_candidates


class TextSampler:
    """Layer 4: Text Sampler."""

    def sample_text(self, raw_doc: RawDocumentContent) -> TextSample:
        full_text = raw_doc.full_text
        lines = [line.strip() for line in full_text.split("\n") if line.strip()]

        header_lines = lines[:10]
        header_text = "\n".join(header_lines)

        footer_lines = lines[-10:] if len(lines) >= 10 else lines
        footer_text = "\n".join(footer_lines)

        first_page_text = raw_doc.pages[0] if raw_doc.pages else ""

        # Extract heading candidates: lines < 60 chars that are not full sentences
        heading_candidates: List[str] = []
        for line in lines:
            if len(line) <= 60 and not line.endswith("."):
                # Check for capital/title case or keyword heading
                if line.isupper() or line.istitle() or len(line.split()) <= 5:
                    heading_candidates.append(line)

        logger.debug(
            "Text sampling completed",
            total_lines=len(lines),
            heading_count=len(heading_candidates),
        )

        return TextSample(
            full_text=full_text,
            header_text=header_text,
            footer_text=footer_text,
            first_page_text=first_page_text,
            heading_candidates=heading_candidates,
        )
