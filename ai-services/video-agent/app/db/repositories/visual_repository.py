"""
Repository for Visual Assembly persistence operations.
Provides idempotent Upsert functionality for VideoVisuals and related entities.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.models import VideoVisual, VisualOCR, VisualMetadata, VisualTopics, VisualTimeline
from loguru import logger
import threading

class VisualRepository:
    def __init__(self, db: Session):
        self.db = db
        self._lock = threading.Lock()

    def upsert_visual(self, video_id: str, filename: str, visual_data: dict, ocr_data: dict, meta_data: dict, topic_data: dict, timeline_data: dict) -> VideoVisual:
        """
        Idempotent Upsert for a visual and all its relationships.
        Locks per repository instance to prevent concurrent race conditions.
        """
        with self._lock:
            try:
                visual = self.db.query(VideoVisual).filter(
                    VideoVisual.video_id == video_id,
                    VideoVisual.filename == filename
                ).first()

                if visual:
                    logger.debug(f"Updating existing visual record: {video_id} / {filename}")
                    
                    for k, v in visual_data.items():
                        setattr(visual, k, v)
                    
                    if visual.ocr:
                        for k, v in ocr_data.items():
                            setattr(visual.ocr, k, v)
                    else:
                        visual.ocr = VisualOCR(visual_id=visual.id, **ocr_data)
                        
                    if visual.metadata_:
                        for k, v in meta_data.items():
                            setattr(visual.metadata_, k, v)
                    else:
                        visual.metadata_ = VisualMetadata(visual_id=visual.id, **meta_data)
                        
                    if visual.topics:
                        for k, v in topic_data.items():
                            setattr(visual.topics, k, v)
                    else:
                        visual.topics = VisualTopics(visual_id=visual.id, **topic_data)
                        
                    if visual.timeline:
                        for k, v in timeline_data.items():
                            setattr(visual.timeline, k, v)
                    else:
                        visual.timeline = VisualTimeline(visual_id=visual.id, **timeline_data)
                        
                else:
                    logger.debug(f"Inserting new visual record: {video_id} / {filename}")
                    visual = VideoVisual(video_id=video_id, filename=filename, **visual_data)
                    self.db.add(visual)
                    self.db.flush()
                    
                    visual.ocr = VisualOCR(visual_id=visual.id, **ocr_data)
                    visual.metadata_ = VisualMetadata(visual_id=visual.id, **meta_data)
                    visual.topics = VisualTopics(visual_id=visual.id, **topic_data)
                    visual.timeline = VisualTimeline(visual_id=visual.id, **timeline_data)
                    
                self.db.commit()
                return visual
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"Failed to upsert visual {filename} for {video_id}: {e}")
                raise
