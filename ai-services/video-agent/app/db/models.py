"""
SQLAlchemy database models for Teaching Visuals.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.session import Base

class VideoVisual(Base):
    """Stores the extracted image frames."""
    __tablename__ = "video_visuals"
    __table_args__ = (UniqueConstraint('video_id', 'filename', name='uix_video_filename'),)

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=False)
    timestamp_str = Column(String, nullable=False)
    timestamp_sec = Column(Float, nullable=False)
    scene_number = Column(Integer, default=0)
    width = Column(Integer)
    height = Column(Integer)
    thumbnail_filename = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ocr = relationship("VisualOCR", back_populates="visual", uselist=False, cascade="all, delete-orphan")
    metadata_ = relationship("VisualMetadata", back_populates="visual", uselist=False, cascade="all, delete-orphan")
    topics = relationship("VisualTopics", back_populates="visual", uselist=False, cascade="all, delete-orphan")
    timeline = relationship("VisualTimeline", back_populates="visual", uselist=False, cascade="all, delete-orphan")

class VisualOCR(Base):
    """Stores OCR text and keywords."""
    __tablename__ = "visual_ocrs"

    id = Column(Integer, primary_key=True, index=True)
    visual_id = Column(Integer, ForeignKey("video_visuals.id", ondelete="CASCADE"), unique=True)
    
    raw_text = Column(String, default="")
    keywords = Column(String, default="") # Comma separated
    confidence = Column(Float, default=0.0)

    visual = relationship("VideoVisual", back_populates="ocr")

class VisualMetadata(Base):
    """Stores the classification of the visual (diagram type, whiteboard, etc.)"""
    __tablename__ = "visual_metadata"

    id = Column(Integer, primary_key=True, index=True)
    visual_id = Column(Integer, ForeignKey("video_visuals.id", ondelete="CASCADE"), unique=True)

    visual_type = Column(String, default="Slide") # Whiteboard, Blackboard, Slide, etc.
    contains_handwriting = Column(Boolean, default=False)
    contains_diagram = Column(Boolean, default=False)
    contains_flowchart = Column(Boolean, default=False)
    contains_code = Column(Boolean, default=False)
    contains_equation = Column(Boolean, default=False)
    contains_table = Column(Boolean, default=False)
    rank_score = Column(Float, default=0.0)
    detection_confidence = Column(Float, default=0.0)

    visual = relationship("VideoVisual", back_populates="metadata_")

class VisualTopics(Base):
    """Stores assigned topics for the image."""
    __tablename__ = "visual_topics"

    id = Column(Integer, primary_key=True, index=True)
    visual_id = Column(Integer, ForeignKey("video_visuals.id", ondelete="CASCADE"), unique=True)

    primary_topic = Column(String, default="General") # Programming, AI, Mathematics...
    secondary_topic = Column(String, nullable=True)

    visual = relationship("VideoVisual", back_populates="topics")

class VisualTimeline(Base):
    """Tracks the visual on the teaching timeline and links to transcripts."""
    __tablename__ = "visual_timeline"

    id = Column(Integer, primary_key=True, index=True)
    visual_id = Column(Integer, ForeignKey("video_visuals.id", ondelete="CASCADE"), unique=True)
    video_id = Column(String, index=True, nullable=False)

    timeline_event_name = Column(String, nullable=False) # e.g. "Binary Tree", "Comparison Table"
    transcript_segment_id = Column(String, nullable=True) # Linked transcript segment ID for Evidence Linking

    visual = relationship("VideoVisual", back_populates="timeline")
