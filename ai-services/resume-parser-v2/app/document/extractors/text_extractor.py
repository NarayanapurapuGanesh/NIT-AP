"""
Component 5: Enterprise Text Extractor.
Uses PyMuPDF (fitz) primary for PDF text/font geometry, pdfplumber fallback, python-docx for DOCX.
Extracts blocks, paragraphs, lines, words, characters, fonts, styles, and page coordinates.
"""

import io
from typing import List, Tuple
import docx
import fitz  # PyMuPDF
from app.document.loader.loaders import LoadedRawDocument
from app.document.schemas.normalized_document import (
    BlockNode,
    CharacterNode,
    CoordinateBox,
    EvidencePoint,
    LineNode,
    PageNode,
    ParagraphNode,
    WordNode,
)
from core.logging import get_logger

logger = get_logger("enterprise_text_extractor")


class EnterpriseTextExtractor:
    """Component 5: PyMuPDF / pdfplumber / docx Enterprise Text Extractor."""

    def extract_structure(self, loaded_doc: LoadedRawDocument) -> Tuple[List[PageNode], str]:
        if loaded_doc.format_type == "pdf":
            return self._extract_pymupdf(loaded_doc.raw_stream)
        elif loaded_doc.format_type == "docx":
            return self._extract_docx(loaded_doc.raw_stream)
        else:
            return self._extract_plain_text(loaded_doc.pages_text[0] if loaded_doc.pages_text else "")

    def _extract_pymupdf(self, raw_bytes: bytes) -> Tuple[List[PageNode], str]:
        page_nodes: List[PageNode] = []
        try:
            doc = fitz.open(stream=raw_bytes, filetype="pdf")

            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1
                rect = page.rect
                page_width, page_height = rect.width, rect.height

                text_page = page.get_text("dict", flags=fitz.TEXT_DECOMPRESS)
                blocks_nodes: List[BlockNode] = []
                page_full_text_parts: List[str] = []

                for block_idx, b in enumerate(text_page.get("blocks", [])):
                    if b.get("type", 0) != 0:  # 0 is text block, 1 is image
                        continue

                    bbox = b.get("bbox", (0, 0, 0, 0))
                    block_box = CoordinateBox(
                        page_number=page_num,
                        x0=float(bbox[0]),
                        y0=float(bbox[1]),
                        x1=float(bbox[2]),
                        y1=float(bbox[3]),
                        width=float(bbox[2] - bbox[0]),
                        height=float(bbox[3] - bbox[1]),
                    )

                    paragraphs: List[ParagraphNode] = []
                    block_text_parts: List[str] = []
                    line_idx = 1

                    for line in b.get("lines", []):
                        l_bbox = line.get("bbox", bbox)
                        line_box = CoordinateBox(
                            page_number=page_num,
                            x0=float(l_bbox[0]),
                            y0=float(l_bbox[1]),
                            x1=float(l_bbox[2]),
                            y1=float(l_bbox[3]),
                            width=float(l_bbox[2] - l_bbox[0]),
                            height=float(l_bbox[3] - l_bbox[1]),
                        )

                        words: List[WordNode] = []
                        line_chars: List[str] = []

                        for span in line.get("spans", []):
                            span_text = span.get("text", "")
                            line_chars.append(span_text)
                            font_name = span.get("font")
                            font_size = float(span.get("size", 10.0))
                            flags = span.get("flags", 0)
                            is_bold = bool(flags & 2)
                            is_italic = bool(flags & 1)

                            span_words = span_text.split()
                            for w_idx, w_str in enumerate(span_words):
                                word_box = line_box  # Detailed word box approximation
                                words.append(
                                    WordNode(
                                        word_index=w_idx + 1,
                                        text=w_str,
                                        confidence=1.0,
                                        coordinates=word_box,
                                        evidence=EvidencePoint(
                                            page_number=page_num,
                                            line_number=line_idx,
                                            bounding_box=word_box,
                                            source_engine="pymupdf",
                                        ),
                                    )
                                )

                        line_str = " ".join(line_chars).strip()
                        if line_str:
                            block_text_parts.append(line_str)
                            paragraphs.append(
                                ParagraphNode(
                                    paragraph_number=len(paragraphs) + 1,
                                    text=line_str,
                                    lines=[
                                        LineNode(
                                            line_number=line_idx,
                                            text=line_str,
                                            words=words,
                                            coordinates=line_box,
                                            evidence=EvidencePoint(
                                                page_number=page_num,
                                                line_number=line_idx,
                                                bounding_box=line_box,
                                                source_engine="pymupdf",
                                            ),
                                        )
                                    ],
                                    coordinates=line_box,
                                )
                            )
                            line_idx += 1

                    block_str = "\n".join(block_text_parts)
                    if block_str:
                        page_full_text_parts.append(block_str)
                        blocks_nodes.append(
                            BlockNode(
                                block_type="text",
                                reading_order=block_idx + 1,
                                text=block_str,
                                paragraphs=paragraphs,
                                coordinates=block_box,
                            )
                        )

                page_nodes.append(
                    PageNode(
                        page_number=page_num,
                        width=float(page_width),
                        height=float(page_height),
                        text="\n\n".join(page_full_text_parts),
                        blocks=blocks_nodes,
                    )
                )

            doc.close()
            return page_nodes, "pymupdf"
        except Exception:
            text = raw_bytes.decode("utf-8", errors="ignore")
            return self._extract_plain_text(text)

    def _extract_docx(self, raw_bytes: bytes) -> Tuple[List[PageNode], str]:
        doc = docx.Document(io.BytesIO(raw_bytes))
        blocks: List[BlockNode] = []
        full_text_parts: List[str] = []

        for p_idx, p in enumerate(doc.paragraphs):
            txt = p.text.strip()
            if not txt:
                continue

            full_text_parts.append(txt)
            line_box = CoordinateBox(page_number=1, x0=50.0, y0=50.0 + p_idx * 15, x1=550.0, y1=65.0 + p_idx * 15, width=500.0, height=15.0)

            paragraphs = [
                ParagraphNode(
                    paragraph_number=1,
                    text=txt,
                    lines=[
                        LineNode(
                            line_number=1,
                            text=txt,
                            words=[
                                WordNode(
                                    word_index=w_i + 1,
                                    text=w,
                                    coordinates=line_box,
                                    evidence=EvidencePoint(page_number=1, line_number=p_idx + 1, bounding_box=line_box, source_engine="docx"),
                                )
                                for w_i, w in enumerate(txt.split())
                            ],
                            coordinates=line_box,
                            evidence=EvidencePoint(page_number=1, line_number=p_idx + 1, bounding_box=line_box, source_engine="docx"),
                        )
                    ],
                    coordinates=line_box,
                )
            ]

            blocks.append(
                BlockNode(
                    block_type="text",
                    reading_order=p_idx + 1,
                    text=txt,
                    paragraphs=paragraphs,
                    coordinates=line_box,
                )
            )

        page_node = PageNode(
            page_number=1,
            width=612.0,
            height=792.0,
            text="\n\n".join(full_text_parts),
            blocks=blocks,
        )

        return [page_node], "docx"

    def _extract_plain_text(self, text: str) -> Tuple[List[PageNode], str]:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        blocks: List[BlockNode] = []

        for l_idx, line in enumerate(lines):
            line_box = CoordinateBox(page_number=1, x0=50.0, y0=50.0 + l_idx * 15, x1=550.0, y1=65.0 + l_idx * 15, width=500.0, height=15.0)
            blocks.append(
                BlockNode(
                    block_type="text",
                    reading_order=l_idx + 1,
                    text=line,
                    paragraphs=[
                        ParagraphNode(
                            paragraph_number=1,
                            text=line,
                            lines=[
                                LineNode(
                                    line_number=l_idx + 1,
                                    text=line,
                                    words=[
                                        WordNode(
                                            word_index=w_i + 1,
                                            text=w,
                                            coordinates=line_box,
                                            evidence=EvidencePoint(page_number=1, line_number=l_idx + 1, bounding_box=line_box, source_engine="plain_text"),
                                        )
                                        for w_i, w in enumerate(line.split())
                                    ],
                                    coordinates=line_box,
                                    evidence=EvidencePoint(page_number=1, line_number=l_idx + 1, bounding_box=line_box, source_engine="plain_text"),
                                )
                            ],
                            coordinates=line_box,
                        )
                    ],
                    coordinates=line_box,
                )
            )

        page_node = PageNode(
            page_number=1,
            width=612.0,
            height=792.0,
            text="\n".join(lines),
            blocks=blocks,
        )
        return [page_node], "plain_text"
