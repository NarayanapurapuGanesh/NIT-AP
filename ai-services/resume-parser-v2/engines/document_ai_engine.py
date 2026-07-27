import re
from typing import Dict, List, Optional
from engines.schemas import LayoutBlock, SectionBlock, SpatialLayoutDocument

SECTION_HEADING_MAP: Dict[str, List[str]] = {
    "PROFILE": ["profile", "about me", "about", "summary", "objective", "career objective"],
    "EDUCATION": ["education", "academic", "qualifications", "academics"],
    "SKILLS": ["skills", "technical skills", "technologies", "tools", "tech stack"],
    "SOFT_SKILLS": ["soft skills", "interpersonal skills", "strengths"],
    "PROJECTS": ["projects", "personal projects", "academic projects"],
    "EXPERIENCE": ["experience", "work experience", "employment", "internship"],
    "ACHIEVEMENTS": ["achievements", "honors", "awards", "accomplishments"],
    "CERTIFICATIONS": ["certifications", "certificates", "courses", "training"],
    "LANGUAGES": ["languages"],
    "PUBLICATIONS": ["publications", "papers", "research"],
    "CONTACT": ["contact", "contact info", "address"],
    "INTERESTS": ["interests", "hobbies", "extracurricular"],
}

class DocumentAIEngine:
    """Engine 1: Layout Detection & Bounding Boxes using PyMuPDF (fitz)"""
    
    def analyze_document(self, document_bytes: bytes, file_extension: str, raw_text: str = "") -> SpatialLayoutDocument:
        if file_extension != ".pdf" or not document_bytes:
            sections = self._segment_sections_from_text(raw_text) if raw_text else []
            return SpatialLayoutDocument(sections=sections, reading_order_text=raw_text)

        try:
            import fitz
            doc = fitz.open(stream=document_bytes, filetype="pdf")
            total_pages = doc.page_count
            all_blocks: List[LayoutBlock] = []
            
            is_two_column = False
            has_sidebar = False
            detected_split_x = 0.0
            has_images = False

            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_width = page.rect.width
                page_height = page.rect.height

                if len(page.get_images()) > 0:
                    has_images = True

                raw_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                page_blocks: List[LayoutBlock] = []

                for block in raw_dict.get("blocks", []):
                    if block.get("type") != 0:
                        continue

                    x0, y0, x1, y1 = block.get("bbox", [0, 0, 0, 0])
                    
                    block_text_parts = []
                    font_sizes = []
                    bold_count = 0
                    total_spans = 0

                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            span_text = span.get("text", "").strip()
                            if span_text:
                                block_text_parts.append(span_text)
                                font_sizes.append(span.get("size", 0))
                                total_spans += 1
                                font_name = span.get("font", "").lower()
                                flags = span.get("flags", 0)
                                if (flags & (1 << 4)) or "bold" in font_name or "black" in font_name:
                                    bold_count += 1

                    block_text = " ".join(block_text_parts).strip()
                    if not block_text:
                        continue

                    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0
                    is_bold = (bold_count / total_spans) > 0.5 if total_spans > 0 else False
                    
                    b_type = "header" if y0 < page_height * 0.06 else ("footer" if y1 > page_height * 0.94 else "text")

                    page_blocks.append(LayoutBlock(
                        block_type=b_type,
                        bbox=[float(x0), float(y0), float(x1), float(y1)],
                        text=block_text,
                        column_index=0,
                        page_number=page_idx + 1,
                        font_size=round(avg_font_size, 1),
                        is_bold=is_bold
                    ))

                # Spatial Column Split
                content_blocks = [b for b in page_blocks if b.block_type not in ("header", "footer")]
                split_x = self._detect_column_split(content_blocks, page_width)

                if split_x > 0:
                    is_two_column = True
                    detected_split_x = split_x
                    left_width = split_x
                    right_width = page_width - split_x
                    has_sidebar = (left_width < right_width * 0.85) or (right_width < left_width * 0.85)

                    for b in page_blocks:
                        bx_center = (b.bbox[0] + b.bbox[2]) / 2
                        b.column_index = 0 if bx_center < split_x else 1

                self._detect_headings(page_blocks)
                all_blocks.extend(page_blocks)

            doc.close()

            sections = self._segment_sections(all_blocks)
            if not sections and raw_text:
                sections = self._segment_sections_from_text(raw_text)

            sidebar_sections = [s for s in sections if s.column_index == 0] if is_two_column else []
            main_sections = [s for s in sections if s.column_index == 1] if is_two_column else sections
            reading_order_text = self._build_reading_order_text(sections, is_two_column) if sections else raw_text

            return SpatialLayoutDocument(
                is_two_column=is_two_column,
                column_count=2 if is_two_column else 1,
                has_sidebar=has_sidebar,
                has_images=has_images,
                blocks=all_blocks,
                total_pages=total_pages,
                sections=sections,
                reading_order_text=reading_order_text,
                sidebar_sections=sidebar_sections,
                main_sections=main_sections,
                detected_split_x=detected_split_x
            )
        except Exception:
            return SpatialLayoutDocument(sections=self._segment_sections_from_text(raw_text) if raw_text else [], reading_order_text=raw_text)

    def _detect_column_split(self, blocks: List[LayoutBlock], page_width: float) -> float:
        col_candidate_blocks = [b for b in blocks if (b.bbox[2] - b.bbox[0]) < page_width * 0.65]
        if len(col_candidate_blocks) < 3: return 0.0

        best_gap = 0.0
        best_split = 0.0

        for pct in range(20, 66, 2):
            candidate_x = page_width * (pct / 100)
            left_blocks = [b for b in col_candidate_blocks if (b.bbox[0] + b.bbox[2]) / 2 < candidate_x]
            right_blocks = [b for b in col_candidate_blocks if (b.bbox[0] + b.bbox[2]) / 2 >= candidate_x]

            if len(left_blocks) >= 2 and len(right_blocks) >= 2:
                gap = min(b.bbox[0] for b in right_blocks) - max(b.bbox[2] for b in left_blocks)
                if gap > best_gap and gap > -15:
                    crossings = sum(1 for b in left_blocks if b.bbox[2] > candidate_x + 30) + \
                                sum(1 for b in right_blocks if b.bbox[0] < candidate_x - 30)
                    if crossings <= 1:
                        best_gap = gap
                        best_split = candidate_x
        return best_split

    def _detect_headings(self, blocks: List[LayoutBlock]) -> None:
        content_blocks = [b for b in blocks if b.block_type not in ("header", "footer")]
        if not content_blocks: return
        font_sizes = [b.font_size for b in content_blocks if b.font_size > 0]
        if not font_sizes: return
        size_counts = {round(s, 0): font_sizes.count(s) for s in set(font_sizes)}
        body_font_size = max(size_counts, key=size_counts.get) if size_counts else 10.0

        for block in content_blocks:
            text = block.text.strip()
            if not text or len(text) > 80: continue
            
            is_heading = self._classify_section_name(text) != "UNKNOWN"
            if block.font_size >= body_font_size + 1.2: is_heading = True
            alpha_chars = [c for c in text if c.isalpha()]
            if alpha_chars and len(alpha_chars) >= 3 and all(c.isupper() for c in alpha_chars) and len(text) < 45: is_heading = True
            if block.is_bold and len(text.split()) <= 6 and len(text) < 50: is_heading = True
            block.is_heading = is_heading

    def _classify_section_name(self, heading_text: str) -> str:
        clean = re.sub(r'^[a-z0-9\W_]{1,3}\s+', '', heading_text.strip().lower())
        clean = re.sub(r'[^a-z\s&]', '', clean).strip()
        all_patterns = [(p, sn) for sn, pats in SECTION_HEADING_MAP.items() for p in pats]
        all_patterns.sort(key=lambda item: len(item[0]), reverse=True)
        for pattern, section_name in all_patterns:
            if clean == pattern or clean.startswith(pattern) or pattern in clean:
                return section_name
        return "UNKNOWN"

    def _segment_sections(self, all_blocks: List[LayoutBlock]) -> List[SectionBlock]:
        col0_blocks = sorted([b for b in all_blocks if b.column_index == 0 and b.block_type not in ("header", "footer")], key=lambda b: (b.page_number, b.bbox[1]))
        col1_blocks = sorted([b for b in all_blocks if b.column_index == 1 and b.block_type not in ("header", "footer")], key=lambda b: (b.page_number, b.bbox[1]))
        sections = self._segment_column(col0_blocks, 0) + self._segment_column(col1_blocks, 1)
        return sections

    def _segment_column(self, blocks: List[LayoutBlock], column_index: int) -> List[SectionBlock]:
        if not blocks: return []
        sections = []
        current_heading, current_section_name, current_lines, current_bbox = "", "UNKNOWN", [], [9999.0, 9999.0, 0.0, 0.0]
        current_page = 1

        for block in blocks:
            if block.is_heading or (self._classify_section_name(block.text) != "UNKNOWN"):
                if current_lines:
                    sections.append(SectionBlock(section_name=current_section_name, heading_text=current_heading, content_lines=current_lines, column_index=column_index, bbox=current_bbox, page_number=current_page))
                current_heading, current_section_name, current_lines, current_bbox = block.text.strip(), self._classify_section_name(block.text.strip()), [], list(block.bbox)
                current_page = block.page_number
            else:
                text = block.text.strip()
                if text:
                    for line in text.split("\n"):
                        if line.strip(): current_lines.append(line.strip())
                    current_bbox[0], current_bbox[1] = min(current_bbox[0], block.bbox[0]), min(current_bbox[1], block.bbox[1])
                    current_bbox[2], current_bbox[3] = max(current_bbox[2], block.bbox[2]), max(current_bbox[3], block.bbox[3])
        if current_lines:
            sections.append(SectionBlock(section_name=current_section_name, heading_text=current_heading, content_lines=current_lines, column_index=column_index, bbox=current_bbox, page_number=current_page))
        return sections

    def _build_reading_order_text(self, sections: List[SectionBlock], is_two_column: bool) -> str:
        if not sections: return ""
        ordered = sorted([s for s in sections if s.column_index == 0], key=lambda s: (s.page_number, s.bbox[1])) + \
                  sorted([s for s in sections if s.column_index == 1], key=lambda s: (s.page_number, s.bbox[1])) if is_two_column else \
                  sorted(sections, key=lambda s: (s.page_number, s.bbox[1]))
        return "\n".join([s.heading_text + "\n" + "\n".join(s.content_lines) if s.heading_text else "\n".join(s.content_lines) for s in ordered])

    def _segment_sections_from_text(self, text: str) -> List[SectionBlock]:
        if not text: return []
        lines = [re.sub(r'^[^\w\s\(\)]+\s*', '', line.strip()) for line in text.split("\n") if line.strip()]
        sections, current_heading, current_section_name, current_lines = [], "", "UNKNOWN", []
        for line in lines:
            section_name = self._classify_section_name(line)
            if section_name != "UNKNOWN" and len(line) < 45 and not line.startswith(("•", "*", "-")):
                if current_lines: sections.append(SectionBlock(section_name=current_section_name, heading_text=current_heading, content_lines=current_lines, column_index=0, bbox=[0,0,0,0], page_number=1))
                current_heading, current_section_name, current_lines = line, section_name, []
            else: current_lines.append(line)
        if current_lines: sections.append(SectionBlock(section_name=current_section_name, heading_text=current_heading, content_lines=current_lines, column_index=0, bbox=[0,0,0,0], page_number=1))
        return sections
