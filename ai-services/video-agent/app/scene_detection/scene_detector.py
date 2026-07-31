"""
FacultyIQ Video Evidence Extraction Service — Scene Detector (Module 4).

Detects scene changes (slide transitions, whiteboard changes, screen shares)
using FFmpeg with NVDEC hardware acceleration for massive speedup.
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union
import subprocess
import re
import cv2

from app.config.settings import settings
from app.core.exceptions import SceneDetectionError
from app.core.logging import get_module_logger
from app.models.scene import Scene, SceneDetectionResult, SlideImage
from app.utils.file_utils import write_json

log = get_module_logger("scene_detection")


class SceneDetector:
    """Detects scene boundaries and extracts representative slide images using FFmpeg NVDEC."""

    def __init__(
        self,
        keyframe_extractor=None,
        threshold: Optional[float] = None,
        min_scene_duration: Optional[float] = None,
    ) -> None:
        self._threshold = threshold or 0.3
        self._min_scene_duration = (
            min_scene_duration or settings.scene_detection.min_scene_duration
        )

    def detect_scenes(
        self,
        video_path: Union[str, Path],
        output_dir: Union[str, Path],
    ) -> SceneDetectionResult:
        """Detects scenes and extracts slide images."""
        v_path = Path(video_path).resolve()
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        slides_dir = out_dir / "slides"
        slides_dir.mkdir(parents=True, exist_ok=True)

        log.info("Detecting scenes with FFmpeg NVDEC in video: {}", v_path.name)

        # 1. Run FFmpeg to extract frames on scene changes
        timestamps = self._extract_frames_ffmpeg(v_path, slides_dir)
        
        # 2. Build the result objects based on the extracted frames
        slides: List[SlideImage] = []
        scenes: List[Scene] = []
        seen_hashes = set()
        
        for idx, pts_time in enumerate(timestamps):
            slide_id = f"slide_{idx + 1:03d}"
            slide_path = slides_dir / f"{slide_id}.jpg"
            thumb_path = slides_dir / f"{slide_id}_thumb.jpg"
            
            # Compute hash and thumbnail
            frame = cv2.imread(str(slide_path))
            if frame is None:
                continue
                
            self._generate_thumbnail(frame, thumb_path)
            phash_val = self._compute_phash(frame)
            is_dup = phash_val in seen_hashes
            if not is_dup and phash_val:
                seen_hashes.add(phash_val)
                
            slide_img = SlideImage(
                slide_id=slide_id,
                scene_id=idx + 1,
                timestamp=round(pts_time, 2),
                frame_number=int(pts_time * 30), # Approximate
                image_path=str(slide_path),
                thumbnail_path=str(thumb_path),
                phash=phash_val,
                is_duplicate=is_dup,
            )
            slides.append(slide_img)
            
            scenes.append(
                Scene(
                    scene_id=idx + 1,
                    start_time=round(pts_time, 2),
                    end_time=round(pts_time + 5.0, 2), # Approximated duration since we only extract keyframes now
                    duration=5.0,
                    scene_type="slide_change",
                    slides=[slide_img],
                )
            )

        unique_slides = [s for s in slides if not s.is_duplicate]
        json_path = out_dir / "scenes.json"

        result = SceneDetectionResult(
            total_scenes=len(scenes),
            total_slides=len(unique_slides),
            scenes=scenes,
            slides_dir=str(slides_dir),
            json_path=str(json_path),
        )

        write_json(json_path, result)

        log.info(
            "Scene detection complete: {} scenes, {} slides ({} unique)",
            len(scenes), len(slides), len(unique_slides),
        )
        return result

    def _extract_frames_ffmpeg(self, video_path: Path, slides_dir: Path) -> List[float]:
        """Runs FFmpeg with hardware acceleration to extract scene changes."""
        output_pattern = str(slides_dir / "slide_%03d.jpg")
        
        # We always extract the very first frame to ensure we have the starting slide
        cmd = [
            "ffmpeg",
            "-hwaccel", "cuda", # Use NVDEC for decoding
            "-i", str(video_path),
            "-vf", f"select='eq(n,0)+gt(scene,{self._threshold})',showinfo",
            "-vsync", "vfr",
            "-q:v", "2",
            output_pattern
        ]
        
        log.info(f"Running FFmpeg: {' '.join(cmd)}")
        
        try:
            # We must capture stderr because showinfo outputs to stderr
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
            )
            
            _, stderr = process.communicate()
            
            if process.returncode != 0:
                log.error(f"FFmpeg failed with return code {process.returncode}")
                # Fallback to CPU if CUDA fails
                return self._extract_frames_ffmpeg_cpu(video_path, slides_dir)
                
            # Parse showinfo from stderr to get exact timestamps of extracted frames
            timestamps = []
            for line in stderr.split('\n'):
                if 'showinfo' in line and 'pts_time:' in line:
                    match = re.search(r'pts_time:([\d\.]+)', line)
                    if match:
                        timestamps.append(float(match.group(1)))
                        
            return timestamps
            
        except Exception as e:
            log.error(f"Failed to run FFmpeg: {e}")
            raise SceneDetectionError(f"FFmpeg extraction failed: {e}")
            
    def _extract_frames_ffmpeg_cpu(self, video_path: Path, slides_dir: Path) -> List[float]:
        """Fallback to CPU FFmpeg if CUDA is unavailable."""
        output_pattern = str(slides_dir / "slide_%03d.jpg")
        cmd = [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", f"select='eq(n,0)+gt(scene,{self._threshold})',showinfo",
            "-vsync", "vfr",
            "-q:v", "2",
            output_pattern
        ]
        log.info(f"Running CPU FFmpeg fallback: {' '.join(cmd)}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        _, stderr = process.communicate()
        timestamps = []
        for line in stderr.split('\n'):
            if 'showinfo' in line and 'pts_time:' in line:
                match = re.search(r'pts_time:([\d\.]+)', line)
                if match:
                    timestamps.append(float(match.group(1)))
        return timestamps

    def _compute_phash(self, frame) -> str:
        try:
            from PIL import Image
            import imagehash
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            return str(imagehash.phash(pil_img))
        except Exception as exc:
            log.debug("pHash computation failed: {}", exc)
            return ""

    def _generate_thumbnail(self, frame, output_path: Path) -> None:
        try:
            h, w = frame.shape[:2]
            if w > 320:
                scale = 320 / w
                new_w = 320
                new_h = int(h * scale)
                thumb = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
            else:
                thumb = frame
            cv2.imwrite(str(output_path), thumb, [cv2.IMWRITE_JPEG_QUALITY, 85])
        except Exception as exc:
            log.debug("Thumbnail generation failed: {}", exc)
