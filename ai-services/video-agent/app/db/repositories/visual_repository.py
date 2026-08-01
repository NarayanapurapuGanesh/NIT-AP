"""
Repository for Visual Assembly persistence operations.
Provides idempotent Upsert functionality for VideoVisuals and related entities.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.sqlite import insert
from app.db.models import VideoVisual, VisualOCR, VisualMetadata, VisualTopics, VisualTimeline
from loguru import logger
import threading

class VisualRepository:
    def __init__(self, db: Session):
        self.db = db
        self._lock = threading.Lock()

    def upsert_visual(self, video_id: str, filename: str, visual_data: dict, ocr_data: dict, meta_data: dict, topic_data: dict, timeline_data: dict) -> VideoVisual:
        """
        Idempotent Upsert for a visual and all its relationships using SQLite native ON CONFLICT DO UPDATE.
        Locks per repository instance to prevent concurrent race conditions.
        """
        with self._lock:
            try:
                # 1. Upsert VideoVisual
                visual_insert_data = {
                    "video_id": video_id,
                    "filename": filename,
                    **visual_data
                }
                stmt = insert(VideoVisual).values(**visual_insert_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['video_id', 'filename'],
                    set_=visual_data
                )
                self.db.execute(stmt)
                self.db.flush()

                # Get the ID of the visual we just inserted or updated
                visual = self.db.query(VideoVisual).filter(
                    VideoVisual.video_id == video_id,
                    VideoVisual.filename == filename
                ).first()
                
                logger.debug(f"Upserted visual record: {video_id} / {filename} (ID: {visual.id})")

                # 2. Upsert VisualOCR
                ocr_stmt = insert(VisualOCR).values(visual_id=visual.id, **ocr_data)
                ocr_stmt = ocr_stmt.on_conflict_do_update(
                    index_elements=['visual_id'],
                    set_=ocr_data
                )
                self.db.execute(ocr_stmt)

                # 3. Upsert VisualMetadata
                meta_stmt = insert(VisualMetadata).values(visual_id=visual.id, **meta_data)
                meta_stmt = meta_stmt.on_conflict_do_update(
                    index_elements=['visual_id'],
                    set_=meta_data
                )
                self.db.execute(meta_stmt)

                # 4. Upsert VisualTopics
                topic_stmt = insert(VisualTopics).values(visual_id=visual.id, **topic_data)
                topic_stmt = topic_stmt.on_conflict_do_update(
                    index_elements=['visual_id'],
                    set_=topic_data
                )
                self.db.execute(topic_stmt)

                # 5. Upsert VisualTimeline
                timeline_stmt = insert(VisualTimeline).values(visual_id=visual.id, **timeline_data)
                timeline_stmt = timeline_stmt.on_conflict_do_update(
                    index_elements=['visual_id'],
                    set_=timeline_data
                )
                self.db.execute(timeline_stmt)

                self.db.commit()
                return visual
                
            except Exception as e:
                self.db.rollback()
                logger.error(f"Failed to upsert visual {filename} for {video_id}: {e}")
                raise
