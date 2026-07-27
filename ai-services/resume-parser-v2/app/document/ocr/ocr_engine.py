"""
Component 6: OCR Fallback Engine.
Triggers automatically when page text density is zero or below confidence threshold.
Merges OCR extracted text blocks with native document layout.
"""

from typing import List, Tuple, Dict, Any
from app.document.configuration.config import ingestion_settings
from app.document.schemas.normalized_document import (
    BlockNode,
    CoordinateBox,
    EvidencePoint,
    LineNode,
    PageNode,
    ParagraphNode,
    WordNode,
)
from core.logging import get_logger
import io
import fitz
import pytesseract
from PIL import Image

logger = get_logger("ocr_fallback_engine")


class OcrFallbackEngine:
    """Component 6: Pluggable OCR Fallback Engine."""

    def should_trigger_ocr(self, page_nodes: List[PageNode]) -> bool:
        """Determines if OCR fallback processing is required based on text density."""
        if not ingestion_settings.OCR_ENABLED:
            return False

        total_words = sum(len(b.text.split()) for p in page_nodes for b in p.blocks)
        page_count = max(1, len(page_nodes))
        avg_words_per_page = total_words / page_count

        if avg_words_per_page < 20:
            logger.info(
                "OCR Fallback triggered due to low text density",
                avg_words_per_page=avg_words_per_page,
                page_count=page_count,
            )
            return True

        return False

    def process_ocr_fallback(
        self, raw_bytes: bytes, existing_pages: List[PageNode]
    ) -> Tuple[List[PageNode], float]:
        """Runs OCR fallback engine and merges extracted blocks into page nodes."""
        logger.info("Executing OCR Fallback processing on document pages...")

        try:
            doc = fitz.open(stream=raw_bytes)
        except Exception as e:
            logger.error(f"Failed to open document for OCR: {e}")
            return existing_pages, 0.0

        updated_pages: List[PageNode] = []
        total_confidence = 0.0
        ocr_pages_count = 0

        for idx, page in enumerate(existing_pages):
            if len(page.blocks) > 0 and len(page.text.strip()) > 50:
                updated_pages.append(page)
            else:
                if idx < doc.page_count:
                    fitz_page = doc[idx]
                    
                    # Convert fitz page to PIL Image
                    pix = fitz_page.get_pixmap(dpi=300)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    
                    # Run pytesseract OCR
                    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                    
                    # Group data into schema
                    blocks, page_conf = self._parse_ocr_data(ocr_data, page.page_number)
                    
                    page_text = "\n\n".join(b.text for b in blocks)
                    
                    ocr_page = PageNode(
                        page_number=page.page_number,
                        width=float(img.width),
                        height=float(img.height),
                        text=page_text,
                        blocks=blocks,
                        tables=page.tables,
                        images=page.images,
                    )
                    updated_pages.append(ocr_page)
                    total_confidence += page_conf
                    ocr_pages_count += 1
                else:
                    updated_pages.append(page)

        doc.close()
        
        avg_confidence = (total_confidence / ocr_pages_count) if ocr_pages_count > 0 else 1.0

        return updated_pages, avg_confidence

    def _parse_ocr_data(self, data: Dict[str, Any], page_number: int) -> Tuple[List[BlockNode], float]:
        blocks_dict = {}
        total_word_conf = 0.0
        word_count = 0
        
        # level: 1 (page), 2 (block), 3 (paragraph), 4 (line), 5 (word)
        for i in range(len(data['level'])):
            level = data['level'][i]
            if level != 5:
                continue
                
            text = str(data['text'][i]).strip()
            if not text:
                continue
                
            block_num = data['block_num'][i]
            par_num = data['par_num'][i]
            line_num = data['line_num'][i]
            
            x0 = float(data['left'][i])
            y0 = float(data['top'][i])
            width = float(data['width'][i])
            height = float(data['height'][i])
            conf = float(data['conf'][i]) / 100.0 if float(data['conf'][i]) > 0 else 0.0
            
            total_word_conf += conf
            word_count += 1
            
            if block_num not in blocks_dict:
                blocks_dict[block_num] = {}
            if par_num not in blocks_dict[block_num]:
                blocks_dict[block_num][par_num] = {}
            if line_num not in blocks_dict[block_num][par_num]:
                blocks_dict[block_num][par_num][line_num] = []
                
            blocks_dict[block_num][par_num][line_num].append({
                'word_index': word_count,
                'text': text,
                'x0': x0, 'y0': y0, 'x1': x0 + width, 'y1': y0 + height,
                'width': width, 'height': height,
                'conf': conf
            })
            
        parsed_blocks = []
        for b_idx, block_key in enumerate(sorted(blocks_dict.keys())):
            paragraphs = []
            block_x0, block_y0 = float('inf'), float('inf')
            block_x1, block_y1 = 0.0, 0.0
            
            for p_idx, par_key in enumerate(sorted(blocks_dict[block_key].keys())):
                lines = []
                par_x0, par_y0 = float('inf'), float('inf')
                par_x1, par_y1 = 0.0, 0.0
                
                for l_idx, line_key in enumerate(sorted(blocks_dict[block_key][par_key].keys())):
                    words = []
                    line_x0, line_y0 = float('inf'), float('inf')
                    line_x1, line_y1 = 0.0, 0.0
                    
                    word_dicts = blocks_dict[block_key][par_key][line_key]
                    for w_idx, w_dict in enumerate(word_dicts):
                        w_box = CoordinateBox(
                            page_number=page_number,
                            x0=w_dict['x0'], y0=w_dict['y0'],
                            x1=w_dict['x1'], y1=w_dict['y1'],
                            width=w_dict['width'], height=w_dict['height']
                        )
                        w_evidence = EvidencePoint(
                            page_number=page_number, line_number=l_idx + 1,
                            bounding_box=w_box, source_engine="ocr_tesseract",
                            word_index=w_idx + 1
                        )
                        words.append(WordNode(
                            word_index=w_idx + 1,
                            text=w_dict['text'],
                            confidence=w_dict['conf'],
                            coordinates=w_box,
                            evidence=w_evidence
                        ))
                        
                        line_x0 = min(line_x0, w_dict['x0'])
                        line_y0 = min(line_y0, w_dict['y0'])
                        line_x1 = max(line_x1, w_dict['x1'])
                        line_y1 = max(line_y1, w_dict['y1'])
                    
                    if not words:
                        continue
                        
                    l_box = CoordinateBox(
                        page_number=page_number,
                        x0=line_x0, y0=line_y0,
                        x1=line_x1, y1=line_y1,
                        width=line_x1 - line_x0, height=line_y1 - line_y0
                    )
                    l_evidence = EvidencePoint(
                        page_number=page_number, line_number=l_idx + 1,
                        bounding_box=l_box, source_engine="ocr_tesseract"
                    )
                    lines.append(LineNode(
                        line_number=l_idx + 1,
                        text=" ".join(w.text for w in words),
                        words=words,
                        coordinates=l_box,
                        evidence=l_evidence
                    ))
                    
                    par_x0 = min(par_x0, line_x0)
                    par_y0 = min(par_y0, line_y0)
                    par_x1 = max(par_x1, line_x1)
                    par_y1 = max(par_y1, line_y1)
                
                if not lines:
                    continue
                    
                p_box = CoordinateBox(
                    page_number=page_number,
                    x0=par_x0, y0=par_y0,
                    x1=par_x1, y1=par_y1,
                    width=par_x1 - par_x0, height=par_y1 - par_y0
                )
                paragraphs.append(ParagraphNode(
                    paragraph_number=p_idx + 1,
                    text="\n".join(l.text for l in lines),
                    lines=lines,
                    coordinates=p_box
                ))
                
                block_x0 = min(block_x0, par_x0)
                block_y0 = min(block_y0, par_y0)
                block_x1 = max(block_x1, par_x1)
                block_y1 = max(block_y1, par_y1)
                
            if not paragraphs:
                continue
                
            b_box = CoordinateBox(
                page_number=page_number,
                x0=block_x0, y0=block_y0,
                x1=block_x1, y1=block_y1,
                width=block_x1 - block_x0, height=block_y1 - block_y0
            )
            parsed_blocks.append(BlockNode(
                block_type="text",
                reading_order=b_idx + 1,
                text="\n\n".join(p.text for p in paragraphs),
                paragraphs=paragraphs,
                coordinates=b_box
            ))
            
        page_avg_conf = (total_word_conf / word_count) if word_count > 0 else 1.0
        return parsed_blocks, page_avg_conf
