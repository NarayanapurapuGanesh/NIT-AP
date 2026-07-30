"""Tests for Module 3: Speech Transcription models."""

import pytest

from app.models.transcription import Segment, TranscriptionResult, WordTimestamp


class TestTranscriptionModels:
    """Tests for transcription Pydantic models."""

    def test_word_timestamp_model(self):
        """WordTimestamp model construction."""
        wt = WordTimestamp(word="hello", start=0.0, end=0.5, probability=0.95)
        assert wt.word == "hello"
        assert wt.probability == 0.95

    def test_segment_model(self):
        """Segment model construction with word timestamps."""
        words = [
            WordTimestamp(word="hello", start=0.0, end=0.5, probability=0.95),
            WordTimestamp(word="world", start=0.5, end=1.0, probability=0.88),
        ]
        seg = Segment(
            id=1, start=0.0, end=1.0, text="hello world",
            confidence=0.915, words=words,
        )
        assert seg.id == 1
        assert len(seg.words) == 2
        assert seg.confidence == 0.915

    def test_transcription_result_model(self):
        """TranscriptionResult model construction."""
        result = TranscriptionResult(
            full_text="hello world",
            segments=[
                Segment(id=1, start=0.0, end=1.0, text="hello world"),
            ],
            language="en",
            model_used="small",
            duration_seconds=1.0,
            json_path="/tmp/transcript.json",
            txt_path="/tmp/transcript.txt",
        )
        assert result.full_text == "hello world"
        assert len(result.segments) == 1
        assert result.language == "en"

    def test_segment_default_confidence(self):
        """Segment confidence defaults to 0.0."""
        seg = Segment(id=1, start=0.0, end=1.0, text="test")
        assert seg.confidence == 0.0
        assert seg.speaker is None
        assert seg.words == []
