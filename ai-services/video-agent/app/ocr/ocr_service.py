"""
FacultyIQ Video Evidence Extraction Service — OCR Service (Module 5).

Runs Tesseract OCR on every extracted slide image and performs structural
analysis to detect titles, paragraphs, bullets, tables, equations, code, etc.
"""

import re
from pathlib import Path
from typing import List, Optional, Union

import pytesseract
from PIL import Image, ImageFilter

from app.config.settings import settings
from app.core.exceptions import OCRError
from app.core.logging import get_module_logger
from app.models.ocr import OCREntry, OCRResult
from app.models.scene import SlideImage
from app.utils.file_utils import write_json, write_text

log = get_module_logger("ocr")


class OCRService:
    """Extracts text from slide images using Tesseract OCR with structural analysis."""

    def __init__(
        self,
        language: Optional[str] = None,
        psm: Optional[int] = None,
        min_confidence: Optional[float] = None,
    ) -> None:
        self._language = language or settings.ocr.language
        self._psm = psm or settings.ocr.psm
        self._min_confidence = min_confidence or settings.ocr.min_confidence
        self._preprocess = settings.ocr.preprocessing

    def process_slides(
        self,
        slides: List[SlideImage],
        output_dir: Union[str, Path],
    ) -> OCRResult:
        """Runs OCR on all extracted slides and generates ocr.json and ocr.txt."""
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        log.info("Processing OCR for {} slides...", len(slides))

        entries: List[OCREntry] = []
        all_text_parts: List[str] = []
        confidence_scores: List[float] = []

        for slide in slides:
            if slide.is_duplicate:
                log.debug("Skipping duplicate slide: {}", slide.slide_id)
                continue

            entry = self._process_single_slide(slide)
            entries.append(entry)
            confidence_scores.append(entry.confidence)

            if entry.cleaned_text:
                all_text_parts.append(
                    f"--- {slide.slide_id} ({slide.timestamp}s) ---\n{entry.cleaned_text}"
                )

        avg_conf = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.0
        )

        json_path = out_dir / "ocr.json"
        txt_path = out_dir / "ocr.txt"

        result = OCRResult(
            total_slides=len(entries),
            average_confidence=round(avg_conf, 2),
            entries=entries,
            json_path=str(json_path),
            txt_path=str(txt_path),
        )

        write_json(json_path, result)
        write_text(txt_path, "\n\n".join(all_text_parts))

        log.info(
            "OCR complete: {} slides processed, average confidence: {:.1f}%",
            len(entries), avg_conf,
        )
        return result

    def _process_single_slide(self, slide: SlideImage) -> OCREntry:
        """Runs OCR on a single slide image with structural extraction."""
        image_path = Path(slide.image_path)

        if not image_path.exists():
            log.warning("Slide image not found: {}", image_path)
            return OCREntry(
                slide_id=slide.slide_id,
                timestamp=slide.timestamp,
                image_path=str(image_path),
            )

        try:
            img = Image.open(image_path)
            if self._preprocess:
                img = self._preprocess_image(img)

            custom_config = f"--psm {self._psm} --oem 3"
            raw_text = pytesseract.image_to_string(
                img, lang=self._language, config=custom_config
            )

            confidence = self._compute_confidence(img)
            cleaned = self._clean_text(raw_text)
            lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

            titles = self._extract_titles(lines)
            paragraphs = self._extract_paragraphs(lines)
            bullets = self._extract_bullets(lines)
            tables = self._extract_tables(lines)
            equations = self._extract_equations(lines)
            code_blocks = self._extract_code(lines)
            algorithms = self._extract_algorithms(lines)
            diagrams = self._extract_diagrams(lines)

            return OCREntry(
                slide_id=slide.slide_id,
                timestamp=slide.timestamp,
                image_path=str(image_path),
                raw_text=raw_text,
                cleaned_text=cleaned,
                confidence=round(confidence, 2),
                titles=titles,
                paragraphs=paragraphs,
                bullets=bullets,
                tables=tables,
                equations=equations,
                code_blocks=code_blocks,
                algorithms=algorithms,
                diagrams=diagrams,
            )

        except Exception as exc:
            log.error("OCR failed for {}: {}", slide.slide_id, exc)
            return OCREntry(
                slide_id=slide.slide_id,
                timestamp=slide.timestamp,
                image_path=str(image_path),
            )

    def _preprocess_image(self, img: Image.Image) -> Image.Image:
        """Preprocesses image for better OCR accuracy."""
        gray = img.convert("L")
        
        # Check if background is dark
        import numpy as np
        img_array = np.array(gray)
        median_val = np.median(img_array)
        
        if median_val < 127:
            # It's a dark background (e.g. glassboard, blackboard) -> invert it
            from PIL import ImageOps
            gray = ImageOps.invert(gray)

        sharpened = gray.filter(ImageFilter.SHARPEN)
        return sharpened

    def _compute_confidence(self, img: Image.Image) -> float:
        """Computes average OCR confidence from Tesseract data output."""
        try:
            data = pytesseract.image_to_data(
                img, output_type=pytesseract.Output.DICT, lang=self._language
            )
            confs = [
                int(c) for c in data.get("conf", [])
                if str(c).lstrip("-").isdigit() and int(c) > 0
            ]
            return sum(confs) / len(confs) if confs else 0.0
        except Exception:
            return 0.0

    def _clean_text(self, text: str) -> str:
        """Cleans and normalizes OCR text."""
        cleaned = re.sub(r"\s+", " ", text).strip()
        cleaned = re.sub(r"[^\x20-\x7E\n]", "", cleaned)
        return cleaned

    def _extract_titles(self, lines: List[str]) -> List[str]:
        """Heuristic: first non-bullet line or lines in ALL CAPS."""
        titles: List[str] = []
        for line in lines[:3]:
            if not line.startswith(("•", "-", "*", "–")):
                if line.isupper() or (len(line) < 80 and not line.endswith(".")):
                    titles.append(line)
        return titles

    def _extract_paragraphs(self, lines: List[str]) -> List[str]:
        """Extracts lines that look like paragraphs (longer sentences)."""
        return [
            l for l in lines
            if len(l) > 50 and not l.startswith(("•", "-", "*", "–"))
        ]

    def _extract_bullets(self, lines: List[str]) -> List[str]:
        """Extracts bullet-pointed lines."""
        return [l for l in lines if l.startswith(("•", "-", "*", "–", "►", "▪"))]

    def _extract_tables(self, lines: List[str]) -> List[str]:
        """Heuristic: lines with multiple pipe delimiters or tab-aligned columns."""
        return [l for l in lines if l.count("|") >= 2 or l.count("\t") >= 2]

    def _extract_equations(self, lines: List[str]) -> List[str]:
        """Heuristic: lines containing mathematical operators or notation."""
        equation_pattern = re.compile(r"[=∑∏∫√±×÷∞≈≤≥]+|[a-z]\^[0-9]|\d+\s*[+\-*/]\s*\d+")
        return [l for l in lines if equation_pattern.search(l)]

    def _extract_code(self, lines: List[str]) -> List[str]:
        """Heuristic: lines with code-like patterns."""
        code_patterns = re.compile(
            r"(def |class |import |from |return |if |for |while |print\(|"
            r"public |private |void |int |string |var |let |const |function )"
        )
        return [l for l in lines if code_patterns.search(l)]

    def _extract_algorithms(self, lines: List[str]) -> List[str]:
        """Heuristic: lines mentioning algorithm names or pseudocode."""
        algo_pattern = re.compile(
            r"(algorithm|procedure|input|output|step\s*\d|begin|end|"
            r"quicksort|mergesort|binary search|dijkstra|bfs|dfs|"
            r"dynamic programming|greedy|backtracking)",
            re.IGNORECASE,
        )
        return [l for l in lines if algo_pattern.search(l)]

    def _extract_diagrams(self, lines: List[str]) -> List[str]:
        """Heuristic: lines containing diagram-related labels."""
        diagram_pattern = re.compile(
            r"(figure|diagram|chart|graph|flowchart|tree|node|edge|"
            r"→|←|↑|↓|--\>|<--|\.\.\.)",
            re.IGNORECASE,
        )
        return [l for l in lines if diagram_pattern.search(l)]
