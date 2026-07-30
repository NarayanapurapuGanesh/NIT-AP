"""Tests for Module 5: OCR Extraction models and structural analysis."""

import pytest

from app.models.ocr import OCREntry, OCRResult


class TestOCRModels:
    """Tests for OCR Pydantic models."""

    def test_ocr_entry_model(self):
        """OCREntry model construction with all fields."""
        entry = OCREntry(
            slide_id="slide_001",
            timestamp=15.5,
            image_path="/slides/slide_001.jpg",
            raw_text="Title\n• Bullet 1\n• Bullet 2",
            cleaned_text="Title Bullet 1 Bullet 2",
            confidence=87.5,
            titles=["Title"],
            bullets=["• Bullet 1", "• Bullet 2"],
        )
        assert entry.slide_id == "slide_001"
        assert entry.confidence == 87.5
        assert len(entry.bullets) == 2

    def test_ocr_entry_defaults(self):
        """OCREntry fields default to empty lists."""
        entry = OCREntry(
            slide_id="slide_001",
            timestamp=0.0,
            image_path="/slides/slide_001.jpg",
        )
        assert entry.raw_text == ""
        assert entry.titles == []
        assert entry.tables == []
        assert entry.code_blocks == []

    def test_ocr_result_model(self):
        """OCRResult model construction."""
        result = OCRResult(
            total_slides=2,
            average_confidence=85.0,
            entries=[
                OCREntry(
                    slide_id="slide_001",
                    timestamp=10.0,
                    image_path="/slides/slide_001.jpg",
                    confidence=90.0,
                ),
                OCREntry(
                    slide_id="slide_002",
                    timestamp=25.0,
                    image_path="/slides/slide_002.jpg",
                    confidence=80.0,
                ),
            ],
            json_path="/output/ocr.json",
            txt_path="/output/ocr.txt",
        )
        assert result.total_slides == 2
        assert result.average_confidence == 85.0
        assert len(result.entries) == 2
