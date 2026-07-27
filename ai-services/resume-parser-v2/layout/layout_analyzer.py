"""
Resume Structure Intelligence Module (Module 4) — v3.0 Layout-Aware Engine.

Advanced document layout analysis with:
- Smart column detection using block density clustering
- Heading detection via font size, bold weight, uppercase, and isolation heuristics
- Section segmentation — groups content blocks under semantic section headings
- Reading order reconstruction — correct left-to-right, top-to-bottom ordering
  for multi-column layouts (sidebar first, then main content)
- Visual element detection — icons, decorative separators, profile photos
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from layout.base import ILayoutAnalyzer


class LayoutBlock(BaseModel):
    block_type: str = Field(..., description="Block type: text, header, footer, table, sidebar, image")
    bbox: List[float] = Field(default_factory=list, description="Bounding box coordinates [x0, y0, x1, y1]")
    text: str = Field("", description="Text content within the block")
    column_index: int = Field(0, description="Column index (0-indexed)")
    page_number: int = Field(1, description="Page number (1-indexed)")
    font_size: float = Field(0.0, description="Dominant font size in the block")
    is_bold: bool = Field(False, description="Whether the block text is predominantly bold")
    is_heading: bool = Field(False, description="Whether this block is detected as a section heading")


class SectionBlock(BaseModel):
    """A semantically segmented resume section with its heading and grouped content."""
    section_name: str = Field(..., description="Normalized section: PROFILE, EDUCATION, SKILLS, SOFT_SKILLS, PROJECTS, EXPERIENCE, ACHIEVEMENTS, LANGUAGES, CONTACT, INTERESTS, CERTIFICATIONS, PUBLICATIONS, UNKNOWN")
    heading_text: str = Field("", description="Original heading text detected from the document")
    content_lines: List[str] = Field(default_factory=list, description="All text lines grouped under this section")
    column_index: int = Field(0, description="0=left/sidebar, 1=right/main")
    bbox: List[float] = Field(default_factory=list, description="Enclosing bounding box of the section")
    page_number: int = Field(1, description="Page number where this section starts")


class StructuralAnalysisResult(BaseModel):
    is_two_column: bool = Field(False, description="Flag indicating if two-column or sidebar layout was detected")
    column_count: int = Field(1, description="Detected column count")
    has_tables: bool = Field(False, description="Flag indicating table structure detection")
    has_sidebar: bool = Field(False, description="Flag indicating distinct sidebar detection")
    has_header_footer: bool = Field(False, description="Flag indicating explicit headers/footers")
    has_images: bool = Field(False, description="Flag indicating embedded photos/graphics")
    blocks: List[LayoutBlock] = Field(default_factory=list, description="Extracted structural layout blocks")
    total_pages: int = Field(1, description="Total document page count")
    # v3.0 additions
    sections: List[SectionBlock] = Field(default_factory=list, description="Semantically segmented sections")
    reading_order_text: str = Field("", description="Full document text in correct reading order")
    sidebar_sections: List[SectionBlock] = Field(default_factory=list, description="Sections from sidebar/left column")
    main_sections: List[SectionBlock] = Field(default_factory=list, description="Sections from main/right column")
    detected_split_x: float = Field(0.0, description="Calculated column split x-coordinate")


# Section heading classification patterns
SECTION_HEADING_MAP: Dict[str, List[str]] = {
    "PROFILE": ["profile", "about me", "about", "summary", "objective", "career objective", "professional summary", "personal profile", "professional profile", "career summary"],
    "EDUCATION": ["education", "educational", "academic", "qualifications", "academic qualifications", "educational background", "educational qualifications", "academics", "scholastic", "ssc", "intermediate", "secondary school", "higher secondary"],
    "SKILLS": ["skills", "technical skills", "tech skills", "technologies", "tools", "tech stack", "core competencies", "competencies", "programming", "technical competencies", "tools & technologies", "tools and technologies"],
    "SOFT_SKILLS": ["soft skills", "interpersonal skills", "personal skills", "key strengths", "strengths", "core skills", "professional skills"],
    "PROJECTS": ["projects", "key projects", "academic projects", "personal projects", "notable projects", "project work", "major projects"],
    "EXPERIENCE": ["experience", "work experience", "professional experience", "employment", "employment history", "career history", "teaching experience", "internship", "internships", "practical experience"],
    "ACHIEVEMENTS": ["achievements", "achievements & certifications", "achievements and certifications", "honors", "awards", "accomplishments", "recognitions", "honors & awards", "honors and awards", "awards & achievements", "extracurricular achievements"],
    "CERTIFICATIONS": ["certifications", "certificates", "professional certifications", "courses", "training", "trainings & certifications"],
    "LANGUAGES": ["languages", "language proficiency", "languages known"],
    "PUBLICATIONS": ["publications", "papers", "research papers", "journals", "conference proceedings", "research"],
    "CONTACT": ["contact", "contact info", "contact information", "contact details", "personal details", "personal information", "address"],
    "INTERESTS": ["interests", "hobbies", "hobbies & interests", "extracurricular", "extra curricular", "extracurricular activities"],
}


class LayoutAnalyzer(ILayoutAnalyzer):
    """Layout analysis engine with section segmentation and reading order reconstruction."""

    @property
    def name(self) -> str:
        return "ResumeLayoutAnalyzer"

    async def analyze_layout(self, document_bytes: bytes) -> Dict[str, Any]:
        """Implements ILayoutAnalyzer async method."""
        result = self.analyze_document_structure(document_bytes)
        return result.model_dump()

    def analyze_document_structure(self, document_bytes: bytes, file_extension: str = ".pdf", raw_text: str = "") -> StructuralAnalysisResult:
        if file_extension != ".pdf" or not document_bytes:
            # Fall back to text-based section segmentation if raw_text provided
            sections = self._segment_sections_from_text(raw_text) if raw_text else []
            return StructuralAnalysisResult(
                is_two_column=False,
                column_count=1,
                has_tables=False,
                has_sidebar=False,
                has_header_footer=False,
                has_images=False,
                blocks=[],
                total_pages=1,
                sections=sections,
                reading_order_text=raw_text,
            )

        try:
            import fitz
            doc = fitz.open(stream=document_bytes, filetype="pdf")
            total_pages = doc.page_count
            all_blocks: List[LayoutBlock] = []

            has_tables = False
            has_images = False
            is_two_column = False
            has_sidebar = False
            has_header_footer = False
            detected_split_x = 0.0

            for page_idx in range(total_pages):
                page = doc[page_idx]
                page_width = page.rect.width
                page_height = page.rect.height

                # Image detection
                images = page.get_images()
                if len(images) > 0:
                    has_images = True

                # --- Extract blocks with font metadata ---
                raw_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
                page_blocks: List[LayoutBlock] = []

                for block in raw_dict.get("blocks", []):
                    if block.get("type") == 1:  # Image block
                        has_images = True
                        continue
                    if block.get("type") != 0:  # Only text blocks
                        continue

                    block_bbox = block.get("bbox", [0, 0, 0, 0])
                    x0, y0, x1, y1 = block_bbox

                    # Aggregate text and font info from spans
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
                                # Check bold: flag bit 4 (weight >= 700) or "bold" in font name
                                if (flags & (1 << 4)) or "bold" in font_name or "black" in font_name:
                                    bold_count += 1

                    block_text = " ".join(block_text_parts).strip()
                    if not block_text:
                        continue

                    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0
                    is_bold = (bold_count / total_spans) > 0.5 if total_spans > 0 else False

                    # Header/Footer check
                    if y0 < page_height * 0.06 or y1 > page_height * 0.94:
                        has_header_footer = True
                        b_type = "header" if y0 < page_height * 0.06 else "footer"
                    else:
                        b_type = "text"

                    page_blocks.append(
                        LayoutBlock(
                            block_type=b_type,
                            bbox=[float(x0), float(y0), float(x1), float(y1)],
                            text=block_text,
                            column_index=0,  # Will be set after split detection
                            page_number=page_idx + 1,
                            font_size=round(avg_font_size, 1),
                            is_bold=is_bold,
                            is_heading=False,  # Will be set in heading detection
                        )
                    )

                # --- Column detection using block x-coordinate clustering ---
                content_blocks = [b for b in page_blocks if b.block_type not in ("header", "footer")]
                split_x = self._detect_column_split(content_blocks, page_width)

                if split_x > 0:
                    is_two_column = True
                    detected_split_x = split_x
                    left_width = split_x
                    right_width = page_width - split_x
                    # If left column is narrower, or right column is narrower, it's a sidebar layout
                    has_sidebar = (left_width < right_width * 0.85) or (right_width < left_width * 0.85)

                    for b in page_blocks:
                        bx_center = (b.bbox[0] + b.bbox[2]) / 2
                        b.column_index = 0 if bx_center < split_x else 1

                # --- Heading detection ---
                self._detect_headings(page_blocks)

                all_blocks.extend(page_blocks)

            doc.close()

            # --- Section segmentation ---
            sections = self._segment_sections(all_blocks)

            # Fallback to text-based section segmentation if block segmentation yielded no sections
            if not sections and raw_text:
                sections = self._segment_sections_from_text(raw_text)

            # --- Classify sidebar vs main sections ---
            sidebar_sections = [s for s in sections if s.column_index == 0] if is_two_column else []
            main_sections = [s for s in sections if s.column_index == 1] if is_two_column else sections

            # --- Reading order reconstruction ---
            reading_order_text = self._build_reading_order_text(sections, is_two_column) if sections else raw_text

            return StructuralAnalysisResult(
                is_two_column=is_two_column,
                column_count=2 if is_two_column else 1,
                has_tables=has_tables,
                has_sidebar=has_sidebar,
                has_header_footer=has_header_footer,
                has_images=has_images,
                blocks=all_blocks,
                total_pages=total_pages,
                sections=sections,
                reading_order_text=reading_order_text,
                sidebar_sections=sidebar_sections,
                main_sections=main_sections,
                detected_split_x=detected_split_x,
            )
        except Exception:
            return StructuralAnalysisResult(
                is_two_column=False,
                column_count=1,
                has_tables=False,
                has_sidebar=False,
                has_header_footer=False,
                has_images=False,
                blocks=[],
                total_pages=1,
            )

    def _detect_column_split(self, blocks: List[LayoutBlock], page_width: float) -> float:
        """Detects column split point using block x-coordinate spatial clustering.

        Excludes full-width header/title blocks (> 65% page width) and evaluates candidate
        split points from 20% to 65% of page width to find clear vertical gaps separating
        left-column and right-column blocks.
        """
        if len(blocks) < 3:
            return 0.0

        # Filter out blocks that span almost the entire page width (e.g. top banner or header)
        col_candidate_blocks = [b for b in blocks if (b.bbox[2] - b.bbox[0]) < page_width * 0.65]

        if len(col_candidate_blocks) < 3:
            return 0.0

        best_gap = 0.0
        best_split = 0.0

        # Test candidate split points x from 20% to 65% of page width
        for pct in range(20, 66, 2):
            candidate_x = page_width * (pct / 100)

            # Partition blocks by center x-coordinate
            left_blocks = [b for b in col_candidate_blocks if (b.bbox[0] + b.bbox[2]) / 2 < candidate_x]
            right_blocks = [b for b in col_candidate_blocks if (b.bbox[0] + b.bbox[2]) / 2 >= candidate_x]

            if len(left_blocks) >= 2 and len(right_blocks) >= 2:
                # Check spatial separation: right edge of left blocks vs left edge of right blocks
                max_left_x1 = max(b.bbox[2] for b in left_blocks)
                min_right_x0 = min(b.bbox[0] for b in right_blocks)
                gap = min_right_x0 - max_left_x1

                # Allow small line overlaps if blocks are clearly centered on opposite sides
                if gap > best_gap and gap > -15:
                    # Count how many left blocks cross candidate_x significantly (> 30pt)
                    crossings = sum(1 for b in left_blocks if b.bbox[2] > candidate_x + 30) + \
                                sum(1 for b in right_blocks if b.bbox[0] < candidate_x - 30)
                    if crossings <= 1:
                        best_gap = gap
                        best_split = candidate_x

        return best_split

    def _detect_headings(self, blocks: List[LayoutBlock]) -> None:
        """Identifies section headings using font size, bold, uppercase, and section taxonomies."""
        if not blocks:
            return

        content_blocks = [b for b in blocks if b.block_type not in ("header", "footer")]
        if not content_blocks:
            return

        font_sizes = [b.font_size for b in content_blocks if b.font_size > 0]
        if not font_sizes:
            return

        size_counts: Dict[float, int] = {}
        for s in font_sizes:
            rounded = round(s, 0)
            size_counts[rounded] = size_counts.get(rounded, 0) + 1
        body_font_size = max(size_counts, key=size_counts.get) if size_counts else 10.0

        for block in content_blocks:
            text = block.text.strip()
            if not text or len(text) > 80:
                continue

            is_heading = False

            # Check if block matches known section heading pattern
            sec_type = self._classify_section_name(text)
            if sec_type != "UNKNOWN":
                is_heading = True

            # Heuristic 1: Font size larger than body
            if block.font_size >= body_font_size + 1.2:
                is_heading = True

            # Heuristic 2: ALL CAPS short text (< 45 chars)
            alpha_chars = [c for c in text if c.isalpha()]
            if alpha_chars and len(alpha_chars) >= 3 and all(c.isupper() for c in alpha_chars) and len(text) < 45:
                is_heading = True

            # Heuristic 3: Bold + short line (< 6 words)
            word_count = len(text.split())
            if block.is_bold and word_count <= 6 and len(text) < 50:
                is_heading = True

            block.is_heading = is_heading

    def _classify_section_name(self, heading_text: str) -> str:
        """Maps a detected heading text to a normalized section name. Handles OCR artifact noise prefixes."""
        clean = re.sub(r'^[a-z0-9\W_]{1,3}\s+', '', heading_text.strip().lower())
        clean = re.sub(r'[^a-z\s&]', '', clean).strip()

        all_patterns = []
        for sec_name, patterns in SECTION_HEADING_MAP.items():
            for p in patterns:
                all_patterns.append((p, sec_name))
        all_patterns.sort(key=lambda item: len(item[0]), reverse=True)

        for pattern, section_name in all_patterns:
            if clean == pattern or clean.startswith(pattern) or pattern in clean:
                return section_name

        return "UNKNOWN"

    def _segment_sections(self, all_blocks: List[LayoutBlock]) -> List[SectionBlock]:
        """Groups consecutive blocks under detected headings into semantic sections."""
        col0_blocks = sorted(
            [b for b in all_blocks if b.column_index == 0 and b.block_type not in ("header", "footer")],
            key=lambda b: (b.page_number, b.bbox[1])
        )
        col1_blocks = sorted(
            [b for b in all_blocks if b.column_index == 1 and b.block_type not in ("header", "footer")],
            key=lambda b: (b.page_number, b.bbox[1])
        )

        sections: List[SectionBlock] = []
        sections.extend(self._segment_column(col0_blocks, column_index=0))
        sections.extend(self._segment_column(col1_blocks, column_index=1))

        return sections

    def _segment_column(self, blocks: List[LayoutBlock], column_index: int) -> List[SectionBlock]:
        """Segments a single column's blocks into sections based on detected headings."""
        if not blocks:
            return []

        sections: List[SectionBlock] = []
        current_heading = ""
        current_section_name = "UNKNOWN"
        current_lines: List[str] = []
        current_bbox = [9999.0, 9999.0, 0.0, 0.0]
        current_page = 1

        for block in blocks:
            # Re-verify heading status during column segmentation
            is_heading_block = block.is_heading or (self._classify_section_name(block.text) != "UNKNOWN")

            if is_heading_block:
                # Save previous section if it has content
                if current_lines:
                    sections.append(SectionBlock(
                        section_name=current_section_name,
                        heading_text=current_heading,
                        content_lines=current_lines,
                        column_index=column_index,
                        bbox=current_bbox,
                        page_number=current_page,
                    ))

                # Start new section
                current_heading = block.text.strip()
                current_section_name = self._classify_section_name(current_heading)
                current_lines = []
                current_bbox = list(block.bbox)
                current_page = block.page_number
            else:
                # Accumulate content under current section
                text = block.text.strip()
                if text:
                    for line in text.split("\n"):
                        line = line.strip()
                        if line:
                            current_lines.append(line)

                    current_bbox[0] = min(current_bbox[0], block.bbox[0])
                    current_bbox[1] = min(current_bbox[1], block.bbox[1])
                    current_bbox[2] = max(current_bbox[2], block.bbox[2])
                    current_bbox[3] = max(current_bbox[3], block.bbox[3])

        # Save last section
        if current_lines:
            sections.append(SectionBlock(
                section_name=current_section_name,
                heading_text=current_heading,
                content_lines=current_lines,
                column_index=column_index,
                bbox=current_bbox,
                page_number=current_page,
            ))

        return sections


    def _build_reading_order_text(self, sections: List[SectionBlock], is_two_column: bool) -> str:
        """Builds the complete document text in correct reading order.

        For two-column layouts: sidebar (col 0) sections first, then main (col 1) sections.
        Within each column, sections are ordered top-to-bottom by their y-coordinate.
        """
        if not sections:
            return ""

        if is_two_column:
            col0 = sorted([s for s in sections if s.column_index == 0], key=lambda s: (s.page_number, s.bbox[1]))
            col1 = sorted([s for s in sections if s.column_index == 1], key=lambda s: (s.page_number, s.bbox[1]))
            ordered = col0 + col1
        else:
            ordered = sorted(sections, key=lambda s: (s.page_number, s.bbox[1]))

        text_parts = []
        for section in ordered:
            if section.heading_text:
                text_parts.append(section.heading_text)
            text_parts.extend(section.content_lines)

        return "\n".join(text_parts)

    def _segment_sections_from_text(self, text: str) -> List[SectionBlock]:
        """Fallback section segmentation using text line analysis for OCR/scanned text."""
        if not text:
            return []

        lines = [re.sub(r'^[^\w\s\(\)]+\s*', '', line.strip()) for line in text.split("\n") if line.strip()]
        sections: List[SectionBlock] = []
        current_heading = ""
        current_section_name = "UNKNOWN"
        current_lines: List[str] = []

        for line in lines:
            section_name = self._classify_section_name(line)

            # Check if line is a section heading
            is_heading = False
            if section_name != "UNKNOWN" and len(line) < 45 and not line.startswith("•") and not line.startswith("*") and not line.startswith("-"):
                is_heading = True

            if is_heading:
                if current_lines:
                    sections.append(SectionBlock(
                        section_name=current_section_name,
                        heading_text=current_heading,
                        content_lines=current_lines,
                        column_index=0,
                        bbox=[0.0, 0.0, 0.0, 0.0],
                        page_number=1,
                    ))
                current_heading = line
                current_section_name = section_name
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines:
            sections.append(SectionBlock(
                section_name=current_section_name,
                heading_text=current_heading,
                content_lines=current_lines,
                column_index=0,
                bbox=[0.0, 0.0, 0.0, 0.0],
                page_number=1,
            ))

        return sections
