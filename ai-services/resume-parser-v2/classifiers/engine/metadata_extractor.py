"""
Layer 3: Metadata Extractor.
Extracts document structure statistics, page counts, title, author, character counts, and image dimensions.
"""

from typing import Any, Dict
from classifiers.engine.document_reader import RawDocumentContent
from core.logging import get_logger

logger = get_logger("metadata_extractor")


class DocumentMetadata:
    def __init__(
        self,
        page_count: int,
        char_count: int,
        line_count: int,
        word_count: int,
        title: str | None,
        author: str | None,
        is_scanned: bool,
        raw_meta: Dict[str, Any],
    ) -> None:
        self.page_count = page_count
        self.char_count = char_count
        self.line_count = line_count
        self.word_count = word_count
        self.title = title
        self.author = author
        self.is_scanned = is_scanned
        self.raw_meta = raw_meta

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_count": self.page_count,
            "char_count": self.char_count,
            "line_count": self.line_count,
            "word_count": self.word_count,
            "title": self.title,
            "author": self.author,
            "is_scanned": self.is_scanned,
        }


class MetadataExtractor:
    """Layer 3: Document Metadata Extractor."""

    def extract_metadata(self, raw_doc: RawDocumentContent) -> DocumentMetadata:
        full_text = raw_doc.full_text
        char_count = len(full_text)
        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        line_count = len(lines)
        words = full_text.split()
        word_count = len(words)

        page_count = raw_doc.metadata_raw.get("page_count", len(raw_doc.pages) or 1)
        title = raw_doc.metadata_raw.get("Title") or raw_doc.metadata_raw.get("title")
        author = raw_doc.metadata_raw.get("Author") or raw_doc.metadata_raw.get("author")

        metadata = DocumentMetadata(
            page_count=page_count,
            char_count=char_count,
            line_count=line_count,
            word_count=word_count,
            title=title,
            author=author,
            is_scanned=raw_doc.is_scanned,
            raw_meta=raw_doc.metadata_raw,
        )

        logger.debug(
            "Metadata extracted",
            page_count=page_count,
            char_count=char_count,
            word_count=word_count,
            is_scanned=raw_doc.is_scanned,
        )
        return metadata
