"""
FacultyIQ Video Evidence Extraction Service — Storage Service.

Manages output directory structure and file persistence for all pipeline outputs.
"""

import json
import zipfile
from pathlib import Path
from typing import Optional, Union

from fpdf import FPDF

from app.config.settings import settings
from app.core.logging import get_module_logger
from app.models.dtos import (
    FullReportDTO, OCRDTO, SlideDTO, SummaryDTO, TimelineDTO,
    TimelineEntryDTO, TranscriptDTO, TranscriptSegmentDTO, VideoDTO,
)
from app.models.gallery import SlideGallery, SlideGalleryItem
from app.models.ocr import OCRResult
from app.models.scene import SceneDetectionResult
from app.models.summary import TeachingSummary
from app.models.timeline import Timeline
from app.models.transcription import TranscriptionResult
from app.models.validation import VideoMetadata
from app.models.voice import VoiceAnalysisResult
from app.utils.file_utils import ensure_directory, format_timestamp, write_json

log = get_module_logger("pipeline")


class StorageService:
    """Manages output directory structure and generates consolidated report."""

    def get_workspace(self, job_id: str) -> Path:
        """Returns the workspace directory for a job, creating it if needed."""
        workspace = ensure_directory(
            settings.base_dir / settings.storage.output_dir / job_id
        )
        return workspace

    def build_gallery(
        self,
        visuals: Optional[list[SlideDTO]],
        output_path: str,
    ) -> SlideGallery:
        """Builds a slide gallery JSON from extracted visuals."""
        items: list[SlideGalleryItem] = []

        if visuals:
            for slide in visuals:
                items.append(
                    SlideGalleryItem(
                        slide_id=slide.slide_id,
                        timestamp=slide.timestamp,
                        timestamp_formatted=slide.timestamp_formatted,
                        thumbnail=slide.thumbnail_url,
                        full_image=slide.full_image_url,
                        ocr_text=slide.ocr_text,
                        visual_type=slide.visual_type,
                        contains_handwriting=slide.contains_handwriting,
                        contains_diagram=slide.contains_diagram,
                        contains_flowchart=slide.contains_flowchart,
                        contains_code=slide.contains_code,
                        contains_equation=slide.contains_equation,
                        contains_table=slide.contains_table
                    )
                )

        gallery = SlideGallery(
            total_slides=len(items),
            slides=items,
            json_path=output_path,
        )
        write_json(output_path, gallery)
        return gallery

    def export_gallery_zip(self, visuals: list[SlideDTO], output_path: str) -> Optional[str]:
        """Exports the visuals to a ZIP archive."""
        if not visuals:
            return None
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for slide in visuals:
                    if slide.full_image_url and Path(slide.full_image_url).exists():
                        # We use the filename as the archive name
                        arcname = Path(slide.full_image_url).name
                        zf.write(slide.full_image_url, arcname)
            return output_path
        except Exception as e:
            log.error(f"Failed to export ZIP gallery: {e}")
            return None

    def export_gallery_pdf(self, visuals: list[SlideDTO], output_path: str) -> Optional[str]:
        """Exports the visuals to a PDF document."""
        if not visuals:
            return None
        try:
            pdf = FPDF(orientation="landscape", unit="mm", format="A4")
            for slide in visuals:
                if slide.full_image_url and Path(slide.full_image_url).exists():
                    pdf.add_page()
                    # A4 Landscape is 297 x 210 mm
                    pdf.image(slide.full_image_url, x=0, y=0, w=297, h=210)
            pdf.output(output_path)
            return output_path
        except Exception as e:
            log.error(f"Failed to export PDF gallery: {e}")
            return None

    def build_full_report(
        self,
        job_id: str,
        metadata: Optional[VideoMetadata],
        transcription: Optional[TranscriptionResult],
        visuals: Optional[list[SlideDTO]],
        timeline: Optional[Timeline],
        summary: Optional[TeachingSummary],
        voice: Optional[VoiceAnalysisResult],
        output_path: str,
    ) -> FullReportDTO:
        """Builds a consolidated report DTO combining all evidence."""
        video_dto = VideoDTO(
            filename=metadata.filename if metadata else "unknown",
            format=metadata.format if metadata else "unknown",
            duration_seconds=metadata.duration_seconds if metadata else 0.0,
            resolution=metadata.resolution if metadata else "0x0",
            fps=metadata.fps if metadata else 0.0,
            file_size_mb=metadata.file_size_mb if metadata else 0.0,
            has_audio=metadata.has_audio if metadata else False,
            video_codec=metadata.video_codec if metadata else "unknown",
            audio_codec=metadata.audio_codec if metadata else None,
        )

        transcript_dto = TranscriptDTO(
            full_text=transcription.full_text if transcription else "",
            segments=[
                TranscriptSegmentDTO(
                    timestamp=s.start, start=s.start, end=s.end, text=s.text
                )
                for s in (transcription.segments if transcription else [])
            ],
            language=transcription.language if transcription else "en",
            duration_seconds=transcription.duration_seconds if transcription else 0.0,
        )

        slide_dtos: list[SlideDTO] = visuals if visuals else []

        ocr_dtos: list[OCRDTO] = []
        if visuals:
            for slide in visuals:
                ocr_dtos.append(
                    OCRDTO(
                        slide_id=slide.slide_id,
                        timestamp=slide.timestamp,
                        text=slide.ocr_text or "",
                        confidence=0.0,
                    )
                )

        timeline_dto = TimelineDTO(
            total_entries=timeline.total_entries if timeline else 0,
            duration_seconds=timeline.duration_seconds if timeline else 0.0,
            entries=[
                TimelineEntryDTO(
                    timestamp=e.timestamp,
                    timestamp_formatted=e.timestamp_formatted,
                    slide_id=e.slide_id,
                    slide_image_url=e.slide_image_path,
                    transcript_text=e.transcript_text,
                    ocr_text=e.ocr_text,
                )
                for e in (timeline.entries if timeline else [])
            ],
        )

        summary_dto = SummaryDTO(
            short_summary=summary.short_summary if summary else "",
            topics_covered=summary.topics_covered if summary else [],
            concepts=summary.concepts if summary else [],
            keywords=summary.keywords if summary else [],
            technical_terms=summary.technical_terms if summary else [],
            programming_languages=summary.programming_languages if summary else [],
            algorithms=summary.algorithms if summary else [],
            subjects=summary.subjects if summary else [],
        )

        voice_dict = None
        if voice and voice.enabled and voice.metrics:
            voice_dict = voice.metrics.model_dump()

        report = FullReportDTO(
            job_id=job_id,
            video=video_dto,
            transcript=transcript_dto,
            slides=slide_dtos,
            ocr=ocr_dtos,
            timeline=timeline_dto,
            summary=summary_dto,
            voice_metrics=voice_dict,
        )

        write_json(output_path, report)
        return report
