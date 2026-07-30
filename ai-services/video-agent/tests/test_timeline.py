"""Tests for Module 6: Timeline Builder."""

import pytest

from app.models.timeline import Timeline, TimelineEntry
from app.models.transcription import Segment, TranscriptionResult
from app.models.scene import Scene, SceneDetectionResult, SlideImage
from app.models.ocr import OCREntry, OCRResult
from app.services.timeline_builder import TimelineBuilder


class TestTimelineBuilder:
    """Tests for TimelineBuilder merging logic."""

    def setup_method(self):
        self.builder = TimelineBuilder()

    def test_build_with_transcription_only(self, tmp_path):
        """Timeline built from transcription only."""
        transcription = TranscriptionResult(
            full_text="Hello world. This is a test.",
            segments=[
                Segment(id=1, start=0.0, end=5.0, text="Hello world."),
                Segment(id=2, start=5.0, end=10.0, text="This is a test."),
            ],
            json_path=str(tmp_path / "t.json"),
            txt_path=str(tmp_path / "t.txt"),
        )
        output = str(tmp_path / "timeline.json")
        timeline = self.builder.build(
            transcription=transcription,
            scene_detection=None,
            ocr=None,
            output_path=output,
            duration_seconds=10.0,
        )
        assert timeline.total_entries == 2
        assert timeline.entries[0].transcript_text == "Hello world."

    def test_build_empty_sources(self, tmp_path):
        """Timeline handles no sources gracefully."""
        output = str(tmp_path / "timeline.json")
        timeline = self.builder.build(
            transcription=None,
            scene_detection=None,
            ocr=None,
            output_path=output,
        )
        assert timeline.total_entries == 0

    def test_timeline_entry_model(self):
        """TimelineEntry model construction."""
        entry = TimelineEntry(
            timestamp=15.5,
            timestamp_formatted="00:00:15",
            event_type="slide_and_transcript",
            slide_id="slide_001",
            transcript_text="Key concept explained.",
            ocr_text="Data Structures",
        )
        assert entry.event_type == "slide_and_transcript"
        assert entry.slide_id == "slide_001"

    def test_timeline_model(self):
        """Timeline model construction."""
        timeline = Timeline(
            total_entries=1,
            duration_seconds=60.0,
            entries=[
                TimelineEntry(
                    timestamp=0.0,
                    timestamp_formatted="00:00:00",
                    event_type="transcript",
                    transcript_text="Welcome.",
                ),
            ],
            json_path="/output/timeline.json",
        )
        assert timeline.total_entries == 1
        assert timeline.duration_seconds == 60.0
