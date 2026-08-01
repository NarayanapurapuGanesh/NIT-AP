"""
REST APIs for Teaching Visual Content Extractor.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import re
from loguru import logger
from pathlib import Path
import os
import json

from app.db.session import get_db
from app.db.models import VideoVisual
from app.visual_extractor.gallery_service import (
    extract_representative_frames, run_ocr_ai, run_diagram_ai, assemble_visual_evidence
)
from app.visual_extractor.pdf_export import export_to_pdf
from app.visual_extractor.zip_export import export_to_zip
from app.config.settings import settings
from app.utils.file_utils import ensure_directory
import shutil

router = APIRouter(tags=["Teaching Visuals"])

async def _resolve_file(file: Optional[UploadFile], file_path: Optional[str]) -> Path:
    if file and file.filename:
        upload_dir = ensure_directory(settings.base_dir / settings.storage.uploads_dir)
        dest = upload_dir / f"{uuid.uuid4().hex[:8]}_{file.filename}"
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return dest
    elif file_path:
        p = Path(file_path).resolve()
        if p.exists():
            return p
    raise HTTPException(status_code=400, detail="Provide valid file or file_path")

@router.post("/video/{video_id}/extract-visuals")
async def extract_visuals_endpoint(
    video_id: str,
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Extracts meaningful educational visuals from a video.
    """
    target_path = await _resolve_file(file, file_path)
    output_dir = str(settings.base_dir / settings.storage.output_dir / video_id / "visuals")
    
    # In a real app we'd fetch the transcript from the job. 
    # For now we'll pass an empty list if not available.
    transcript_file = settings.base_dir / settings.storage.output_dir / video_id / "transcript.json"
    transcript_data = []
    if transcript_file.exists():
        with open(transcript_file, "r") as f:
            transcript_data = json.load(f).get("segments", [])

    # Process sync for MVP (can be moved to background)
    frames = extract_representative_frames(str(target_path), output_dir)
    ocr_res = run_ocr_ai(frames)
    diag_res = run_diagram_ai(frames)
    visuals = assemble_visual_evidence(video_id, frames, diag_res, ocr_res, transcript_data, db)
    
    return {"status": "completed", "visuals_count": len(visuals)}

@router.get("/video/{video_id}/visuals")
async def get_visuals(video_id: str, db: Session = Depends(get_db)):
    """
    Returns all extracted visuals for a video.
    """
    try:
        # Validate jobId (basic sanity check)
        if not re.match(r'^[a-zA-Z0-9_-]+$', video_id):
            raise HTTPException(status_code=400, detail="Invalid Job ID format")
            
        job_dir = settings.base_dir / settings.storage.output_dir / video_id
        if not job_dir.exists():
            logger.warning(f"Job directory not found: {job_dir}")
            raise HTTPException(status_code=404, detail="Job directory not found")
            
        visuals_dir = job_dir / "visuals"
        
        visuals = db.query(VideoVisual).filter(VideoVisual.video_id == video_id).all()
        
        if not visuals and visuals_dir.exists():
            images = [f for f in visuals_dir.glob("*.jpg") if not f.name.startswith("thumb_")]
            if images:
                logger.info(f"Database empty but {len(images)} images exist. Rebuilding gallery automatically.")
                from app.visual_extractor.gallery_service import rebuild_gallery_from_disk
                rebuild_gallery_from_disk(video_id, images, db)
                visuals = db.query(VideoVisual).filter(VideoVisual.video_id == video_id).all()
        
        result = []
        for v in visuals:
            result.append({
                "id": v.id,
                "filename": v.filename,
                "timestamp": v.timestamp_str,
                "timestamp_sec": v.timestamp_sec,
                "ocr": v.ocr.raw_text if v.ocr else "",
                "keywords": v.ocr.keywords if v.ocr else "",
                "topic": v.topics.primary_topic if v.topics else "General",
                "diagram_type": v.metadata_.visual_type if v.metadata_ else "None",
                "detection_confidence": v.metadata_.detection_confidence if v.metadata_ else 0.0,
                "thumbnail_filename": v.thumbnail_filename,
                "linked_transcript_id": v.timeline.transcript_segment_id if v.timeline else None
            })
            
        images_on_disk = len(list(visuals_dir.glob('*.jpg'))) if visuals_dir.exists() else 0
        logger.info(f"Incoming jobId: {video_id} | Resolved folder: {job_dir} | Images found on disk: {images_on_disk} | Returned image count: {len(result)}")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching visuals for {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/video/{video_id}/visuals/debug")
async def debug_visuals(video_id: str, db: Session = Depends(get_db)):
    """
    Diagnostic endpoint to verify visual assets state.
    """
    job_dir = settings.base_dir / settings.storage.output_dir / video_id
    folderExists = job_dir.exists()
    visuals_dir = job_dir / "visuals"
    
    images = []
    if visuals_dir.exists():
        images = [f.name for f in visuals_dir.glob("*.jpg")]
        
    databaseCount = db.query(VideoVisual).filter(VideoVisual.video_id == video_id).count()
    
    return {
        "jobId": video_id,
        "folderExists": folderExists,
        "imageCount": len(images),
        "images": images,
        "databaseCount": databaseCount
    }

@router.get("/video/{video_id}/visuals/{image_id}")
async def get_visual_image(video_id: str, image_id: int, db: Session = Depends(get_db)):
    """
    Serves the actual image file.
    """
    visual = db.query(VideoVisual).filter(VideoVisual.id == image_id, VideoVisual.video_id == video_id).first()
    if not visual:
        raise HTTPException(status_code=404, detail="Image not found")
        
    image_path = settings.base_dir / settings.storage.output_dir / video_id / "visuals" / visual.filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="File missing on disk")
        
    return FileResponse(str(image_path), media_type="image/jpeg")

@router.get("/video/{video_id}/visuals/{image_id}/thumbnail")
async def get_visual_thumbnail(video_id: str, image_id: int, db: Session = Depends(get_db)):
    """
    Serves the thumbnail image file.
    """
    visual = db.query(VideoVisual).filter(VideoVisual.id == image_id, VideoVisual.video_id == video_id).first()
    if not visual or not visual.thumbnail_filename:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
        
    image_path = settings.base_dir / settings.storage.output_dir / video_id / "visuals" / visual.thumbnail_filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="File missing on disk")
        
    return FileResponse(str(image_path), media_type="image/jpeg")

@router.get("/video/{video_id}/timeline")
async def get_visual_timeline(video_id: str, db: Session = Depends(get_db)):
    """
    Returns the visual timeline events.
    """
    visuals = db.query(VideoVisual).filter(VideoVisual.video_id == video_id).order_by(VideoVisual.timestamp_sec).all()
    timeline = []
    for v in visuals:
        timeline.append({
            "timestamp": v.timestamp_str,
            "event_name": v.timeline.timeline_event_name if v.timeline else "Visual",
            "image_id": v.id
        })
    return timeline

@router.get("/video/{video_id}/download/pdf")
async def download_visuals_pdf(video_id: str, db: Session = Depends(get_db)):
    visuals = db.query(VideoVisual).filter(VideoVisual.video_id == video_id).order_by(VideoVisual.timestamp_sec).all()
    if not visuals:
        raise HTTPException(404, "No visuals found")
        
    visuals_data = []
    for v in visuals:
        image_path = str(settings.base_dir / settings.storage.output_dir / video_id / "visuals" / v.filename)
        visuals_data.append({
            "image_path": image_path,
            "timestamp_str": v.timestamp_str,
            "ocr": v.ocr.raw_text if v.ocr else "",
            "topic": v.topics.primary_topic if v.topics else "General",
            "diagram_type": v.metadata_.visual_type if v.metadata_ else "None"
        })
        
    output_pdf = str(settings.base_dir / settings.storage.output_dir / video_id / "Teaching_Visuals_Report.pdf")
    export_to_pdf(visuals_data, output_pdf)
    return FileResponse(output_pdf, media_type="application/pdf", filename="Teaching_Visuals_Report.pdf")

@router.get("/video/{video_id}/download/zip")
async def download_visuals_zip(video_id: str, db: Session = Depends(get_db)):
    visuals = db.query(VideoVisual).filter(VideoVisual.video_id == video_id).order_by(VideoVisual.timestamp_sec).all()
    if not visuals:
        raise HTTPException(404, "No visuals found")
        
    visuals_data = []
    for v in visuals:
        image_path = str(settings.base_dir / settings.storage.output_dir / video_id / "visuals" / v.filename)
        visuals_data.append({
            "image_path": image_path,
            "timestamp_sec": v.timestamp_sec,
            "timestamp_str": v.timestamp_str,
            "ocr": v.ocr.raw_text if v.ocr else "",
            "topic": v.topics.primary_topic if v.topics else "General",
            "diagram_type": v.metadata_.visual_type if v.metadata_ else "None",
            "linked_transcript_id": v.timeline.transcript_segment_id if v.timeline else None
        })
        
    output_zip = str(settings.base_dir / settings.storage.output_dir / video_id / "Visuals_Export.zip")
    export_to_zip(visuals_data, output_zip)
    return FileResponse(output_zip, media_type="application/zip", filename="Teaching_Visuals_Export.zip")
