from typing import List, Optional
from pydantic import BaseModel, Field


class FaceMetrics(BaseModel):
    face_detected_percentage: float = 95.0
    eye_contact_percentage: float = 88.0
    head_movement_variability: float = 0.35
    smile_ratio: float = 0.25


class PoseMetrics(BaseModel):
    upright_posture_percentage: float = 92.0
    posture_quality: str = "Upright Standing"
    shoulder_alignment_score: float = 0.89


class GestureMetrics(BaseModel):
    gesture_frequency: float = 12.5
    open_hand_ratio: float = 0.78
    pointing_ratio: float = 0.15


class VisualFrameMetrics(BaseModel):
    second: int
    eye_contact: bool = True
    face_confidence: float = 0.95
    posture: str = "Upright Standing"
    gesture: str = "Open Palm"


class VisualTimeline(BaseModel):
    second_by_second_metrics: List[VisualFrameMetrics]
    json_path: str
