"""
FacultyIQ Video Evidence Extraction Service — Timeline Builder (Module 6).

Merges transcript segments, slide images, and OCR text into a unified
chronological teaching timeline.
"""

from typing import List, Optional

from app.core.logging import get_module_logger
from app.models.timeline import Timeline, TimelineEntry
from app.models.transcription import TranscriptionResult
from app.utils.file_utils import format_timestamp, write_json
from app.models.dtos import SlideDTO
from app.utils.file_utils import format_timestamp, write_json

log = get_module_logger("timeline")


class TimelineBuilder:
    """Merges transcript, slides, and OCR into a unified teaching timeline."""

    def build(
        self,
        transcription: Optional[TranscriptionResult],
        visuals: Optional[List[SlideDTO]],
        output_path: str,
        duration_seconds: float = 0.0,
    ) -> Timeline:
        """Builds a unified timeline from all available evidence sources."""
        log.info("Building unified teaching timeline...")

        entries: List[TimelineEntry] = []

        if visuals:
            for slide in visuals:
                entries.append(
                    TimelineEntry(
                        timestamp=slide.timestamp,
                        timestamp_formatted=slide.timestamp_formatted,
                        event_type="slide",
                        slide_id=slide.slide_id,
                        slide_image_path=slide.full_image_url,
                        transcript_text=None,
                        ocr_text=slide.ocr_text,
                    )
                )

        if transcription:
            for seg in transcription.segments:
                entries.append(
                    TimelineEntry(
                        timestamp=seg.start,
                        timestamp_formatted=format_timestamp(seg.start),
                        event_type="transcript",
                        slide_id=None,
                        slide_image_path=None,
                        transcript_text=seg.text,
                        ocr_text=None,
                    )
                )

        entries.sort(key=lambda e: e.timestamp)
        entries = self._merge_nearby_entries(entries)

        if duration_seconds == 0.0 and entries:
            duration_seconds = max(e.timestamp for e in entries)

        timeline = Timeline(
            total_entries=len(entries),
            duration_seconds=round(duration_seconds, 2),
            entries=entries,
            json_path=output_path,
        )

        write_json(output_path, timeline)

        log.info(
            "Timeline built: {} entries over {:.1f}s",
            len(entries), duration_seconds,
        )
        return timeline

    def _merge_nearby_entries(
        self, entries: List[TimelineEntry], threshold: float = 2.0
    ) -> List[TimelineEntry]:
        """Merges slide and transcript entries that are within threshold seconds."""
        if len(entries) < 2:
            return entries

        merged: List[TimelineEntry] = []
        i = 0

        while i < len(entries):
            current = entries[i]

            if i + 1 < len(entries):
                next_entry = entries[i + 1]
                time_diff = abs(next_entry.timestamp - current.timestamp)

                if time_diff <= threshold:
                    if current.event_type == "slide" and next_entry.event_type == "transcript":
                        merged.append(
                            TimelineEntry(
                                timestamp=current.timestamp,
                                timestamp_formatted=current.timestamp_formatted,
                                event_type="slide_and_transcript",
                                slide_id=current.slide_id,
                                slide_image_path=current.slide_image_path,
                                transcript_text=next_entry.transcript_text,
                                ocr_text=current.ocr_text,
                            )
                        )
                        i += 2
                        continue
                    elif current.event_type == "transcript" and next_entry.event_type == "slide":
                        merged.append(
                            TimelineEntry(
                                timestamp=next_entry.timestamp,
                                timestamp_formatted=next_entry.timestamp_formatted,
                                event_type="slide_and_transcript",
                                slide_id=next_entry.slide_id,
                                slide_image_path=next_entry.slide_image_path,
                                transcript_text=current.transcript_text,
                                ocr_text=next_entry.ocr_text,
                            )
                        )
                        i += 2
                        continue

            merged.append(current)
            i += 1

        return merged
