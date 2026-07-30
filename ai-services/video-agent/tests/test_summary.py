"""Tests for Module 9: Teaching Summary Generator."""

import pytest

from app.models.summary import TeachingSummary
from app.models.transcription import Segment, TranscriptionResult
from app.services.summary_generator import SummaryGenerator


class TestSummaryGenerator:
    """Tests for SummaryGenerator NLP extraction."""

    def setup_method(self):
        self.generator = SummaryGenerator()

    def test_generate_summary_from_transcript(self, tmp_path, sample_text):
        """Summary generated from transcript text."""
        transcription = TranscriptionResult(
            full_text=sample_text,
            segments=[
                Segment(id=1, start=0.0, end=30.0, text=sample_text),
            ],
            json_path=str(tmp_path / "t.json"),
            txt_path=str(tmp_path / "t.txt"),
        )
        output = str(tmp_path / "summary.json")
        summary = self.generator.generate(
            transcription=transcription,
            ocr=None,
            output_path=output,
        )
        assert summary.short_summary != ""
        assert len(summary.keywords) > 0

    def test_extract_programming_languages(self, tmp_path, sample_text):
        """Programming languages are detected in text."""
        transcription = TranscriptionResult(
            full_text=sample_text,
            segments=[Segment(id=1, start=0.0, end=10.0, text=sample_text)],
            json_path=str(tmp_path / "t.json"),
            txt_path=str(tmp_path / "t.txt"),
        )
        output = str(tmp_path / "summary.json")
        summary = self.generator.generate(transcription, None, output)
        assert "Python" in summary.programming_languages

    def test_extract_algorithms(self, tmp_path, sample_text):
        """Algorithms are detected in text."""
        transcription = TranscriptionResult(
            full_text=sample_text,
            segments=[Segment(id=1, start=0.0, end=10.0, text=sample_text)],
            json_path=str(tmp_path / "t.json"),
            txt_path=str(tmp_path / "t.txt"),
        )
        output = str(tmp_path / "summary.json")
        summary = self.generator.generate(transcription, None, output)
        algo_names = [a.lower() for a in summary.algorithms]
        assert any("merge sort" in a for a in algo_names) or any(
            "dynamic programming" in a for a in algo_names
        )

    def test_extract_subjects(self, tmp_path, sample_text):
        """Academic subjects are detected in text."""
        transcription = TranscriptionResult(
            full_text=sample_text,
            segments=[Segment(id=1, start=0.0, end=10.0, text=sample_text)],
            json_path=str(tmp_path / "t.json"),
            txt_path=str(tmp_path / "t.txt"),
        )
        output = str(tmp_path / "summary.json")
        summary = self.generator.generate(transcription, None, output)
        subject_lower = [s.lower() for s in summary.subjects]
        assert any("computer science" in s for s in subject_lower) or any(
            "machine learning" in s for s in subject_lower
        )

    def test_empty_text_summary(self, tmp_path):
        """Summary handles empty text gracefully."""
        output = str(tmp_path / "summary.json")
        summary = self.generator.generate(None, None, output)
        assert "no text evidence" in summary.short_summary.lower()

    def test_summary_model(self):
        """TeachingSummary model construction."""
        summary = TeachingSummary(
            short_summary="A lecture on data structures.",
            topics_covered=["Binary Trees", "Hash Tables"],
            keywords=["tree", "hash", "search"],
            json_path="/output/summary.json",
        )
        assert len(summary.topics_covered) == 2
        assert summary.short_summary != ""
