"""
Orchestrates the Teaching Visual Extraction pipeline and DB persistence.
"""

from loguru import logger
import os
from sqlalchemy.orm import Session
from app.db.models import VideoVisual, VisualOCR, VisualMetadata, VisualTopics, VisualTimeline
from app.db.repositories.visual_repository import VisualRepository
from app.visual_extractor.frame_extractor import extract_frames
from app.visual_extractor.quality_filter import filter_quality
from app.visual_extractor.duplicate_filter import filter_duplicates
from app.visual_extractor.ocr_engine import perform_ocr
from app.visual_extractor.diagram_detector import analyze_visual_content
from app.visual_extractor.content_classifier import classify_topic
from app.visual_extractor.metadata_generator import generate_smart_name, rename_image
from app.visual_extractor.timeline_builder import generate_timeline_event_name
from app.visual_extractor.evidence_linker import link_visual_to_transcript
import cv2
from app.models.dtos import SlideDTO

def extract_representative_frames(video_path: str, output_dir: str) -> list[tuple[str, float]]:
    """Extracts, filters quality, and removes duplicate frames."""
    logger.info(f"Extracting representative frames from {video_path}")
    frames = extract_frames(video_path, output_dir, interval_seconds=2)
    frames = filter_quality(frames)
    frames = filter_duplicates(frames, hash_threshold=5)
    return frames


def run_diagram_ai(frames: list[tuple[str, float]]) -> dict[str, dict]:
    """Runs diagram and whiteboard classification independently."""
    logger.info(f"Running Diagram & Whiteboard AI on {len(frames)} frames")
    results = {}
    for path, _ in frames:
        # OCR data is empty dict because this runs in parallel with OCR
        analysis = analyze_visual_content(path, {})
        results[path] = analysis
    return results


def run_ocr_ai(frames: list[tuple[str, float]]) -> dict[str, dict]:
    """Runs OCR extraction independently."""
    logger.info(f"Running OCR AI on {len(frames)} frames")
    results = {}
    for path, _ in frames:
        ocr_result = perform_ocr(path)
        results[path] = ocr_result
    return results


def assemble_visual_evidence(
    video_id: str, 
    frames: list[tuple[str, float]], 
    diagram_results: dict[str, dict], 
    ocr_results: dict[str, dict], 
    transcript_data: list, 
    db: Session
) -> tuple[list[SlideDTO], int]:
    """Assembles independent pipeline results into a unified visual gallery."""
    processed_visuals = []
    db_error_count = 0
    
    for path, timestamp_sec in frames:
        ocr_result = ocr_results.get(path, {})
        analysis = diagram_results.get(path, {
            "visual_type": "Unknown", "contains_diagram": False, 
            "contains_handwriting": False, "contains_flowchart": False,
            "contains_code": False, "contains_equation": False, "contains_table": False
        })
        
        # Topic Classification
        topic = classify_topic(ocr_result.get("raw_text", ""))
        
        smart_name = generate_smart_name(video_id, timestamp_sec)
        final_path = rename_image(path, smart_name)
        
        # Generate Thumbnail
        img = cv2.imread(final_path)
        thumb_filename = None
        if img is not None:
            thumb_img = cv2.resize(img, (320, 180))
            thumb_filename = f"thumb_{os.path.basename(final_path)}"
            thumb_path = os.path.join(os.path.dirname(final_path), thumb_filename)
            cv2.imwrite(thumb_path, thumb_img)
        
        minutes = int(timestamp_sec // 60)
        seconds = int(timestamp_sec % 60)
        timestamp_str = f"{minutes:02d}:{seconds:02d}"
        
        # Evidence Linking
        linked_id = link_visual_to_transcript(timestamp_sec, transcript_data)
        
        # Timeline Name
        timeline_name = generate_timeline_event_name(analysis.get("visual_type", "Unknown"), topic, ocr_result.get("keywords", ""))
        
        # Database Persistence (Idempotent Upsert decoupled from Filesystem via Repository)
        try:
            repo = VisualRepository(db)
            filename = os.path.basename(final_path)
            visual_data = {
                "thumbnail_filename": thumb_filename,
                "timestamp_str": timestamp_str,
                "timestamp_sec": timestamp_sec,
                "width": 1920,
                "height": 1080
            }
            ocr_data = {
                "raw_text": ocr_result.get("raw_text", ""),
                "keywords": ocr_result.get("keywords", ""),
                "confidence": ocr_result.get("confidence", 0.0)
            }
            meta_data = {
                "visual_type": analysis.get("visual_type", "Slide"),
                "contains_handwriting": analysis.get("contains_handwriting", False),
                "contains_diagram": analysis.get("contains_diagram", False),
                "contains_flowchart": analysis.get("contains_flowchart", False),
                "contains_code": analysis.get("contains_code", False),
                "contains_equation": analysis.get("contains_equation", False),
                "contains_table": analysis.get("contains_table", False),
                "rank_score": analysis.get("rank_score", 0.0),
                "detection_confidence": analysis.get("detection_confidence", 0.0)
            }
            topic_data = {
                "primary_topic": topic
            }
            timeline_data = {
                "video_id": video_id,
                "timeline_event_name": timeline_name,
                "transcript_segment_id": linked_id
            }
            
            repo.upsert_visual(video_id, filename, visual_data, ocr_data, meta_data, topic_data, timeline_data)
        except Exception as e:
            db_error_count += 1
            logger.error(f"Failed to persist visual {final_path} to DB: {e}")
        
        processed_visuals.append(SlideDTO(
            slide_id=f"slide_{len(processed_visuals)+1:03d}",
            timestamp=timestamp_sec,
            timestamp_formatted=timestamp_str,
            thumbnail_url=thumb_path if thumb_filename else final_path,
            full_image_url=final_path,
            ocr_text=ocr_result.get("raw_text", ""),
            visual_type=analysis.get("visual_type", "Slide"),
            contains_handwriting=analysis.get("contains_handwriting", False),
            contains_diagram=analysis.get("contains_diagram", False),
            contains_flowchart=analysis.get("contains_flowchart", False),
            contains_code=analysis.get("contains_code", False),
            contains_equation=analysis.get("contains_equation", False),
            contains_table=analysis.get("contains_table", False)
        ))
        
    logger.info(f"Visual pipeline assembled {len(processed_visuals)} independent visuals.")
    return processed_visuals, db_error_count

def rebuild_gallery_from_disk(video_id: str, images: list, db: Session):
    """Rebuilds basic DB records for a gallery from existing files on disk."""
    logger.info(f"Rebuilding {len(images)} visual records for {video_id} via Repository")
    repo = VisualRepository(db)
    for img_path in images:
        try:
            thumb_filename = f"thumb_{img_path.name}"
            has_thumb = (img_path.parent / thumb_filename).exists()
            
            visual_data = {
                "thumbnail_filename": thumb_filename if has_thumb else None,
                "timestamp_str": "00:00",
                "timestamp_sec": 0.0,
                "width": 1920,
                "height": 1080
            }
            ocr_data = {"raw_text": "Rebuilt from disk", "keywords": "", "confidence": 1.0}
            meta_data = {
                "visual_type": "Recovered", "contains_handwriting": False, 
                "contains_diagram": False, "contains_flowchart": False, "contains_code": False, 
                "contains_equation": False, "contains_table": False, "rank_score": 0.0, "detection_confidence": 1.0
            }
            topic_data = {"primary_topic": "Recovered"}
            timeline_data = {"video_id": video_id, "timeline_event_name": "Recovered Visual", "transcript_segment_id": None}
            
            repo.upsert_visual(video_id, img_path.name, visual_data, ocr_data, meta_data, topic_data, timeline_data)
        except Exception as e:
            logger.error(f"Failed to rebuild visual {img_path.name} from disk: {e}")
