from typing import List, Optional
from pydantic import BaseModel, Field


class Keyframe(BaseModel):
    keyframe_id: str
    timestamp: float
    frame_number: int
    file_path: str
    phash: Optional[str] = None
    is_duplicate: bool = False


class Scene(BaseModel):
    scene_id: int
    start_time: float
    end_time: float
    duration: float
    start_frame: int
    end_frame: int
    scene_type: str = "teaching_transition"
    keyframes: List[Keyframe] = Field(default_factory=list)


class SceneDetectionResult(BaseModel):
    total_scenes: int
    total_keyframes: int
    scenes: List[Scene]
    timeline_path: str
