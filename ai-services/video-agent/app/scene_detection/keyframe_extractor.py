"""
FacultyIQ Video Evidence Extraction Service — Keyframe Extractor.

Extracts representative keyframes from detected scene boundaries,
saves them as slide images, and computes perceptual hashes for deduplication.
"""

from pathlib import Path
from typing import List, Tuple, Union

import cv2

from app.config.settings import settings
from app.core.logging import get_module_logger
from app.models.scene import SlideImage
from app.utils.file_utils import format_timestamp

log = get_module_logger("scene_detection")


class KeyframeExtractor:
    """Extracts keyframe images from scene boundaries with deduplication."""

    def __init__(self, output_quality: int = 95) -> None:
        self._quality = output_quality or settings.scene_detection.output_quality

    def extract_keyframes(
        self,
        video_path: Union[str, Path],
        scene_bounds: List[Tuple[float, float]],
        output_dir: Union[str, Path],
    ) -> List[SlideImage]:
        """Extracts one keyframe per scene and saves as slide images."""
        v_path = Path(video_path).resolve()
        slides_dir = Path(output_dir).resolve() / "slides"
        slides_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(v_path))
        if not cap.isOpened():
            log.error("Failed to open video for keyframe extraction: {}", v_path.name)
            return []

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        slides: List[SlideImage] = []
        seen_hashes: set = set()

        for idx, (start_t, end_t) in enumerate(scene_bounds):
            mid_t = (start_t + end_t) / 2.0
            mid_frame = int(mid_t * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
            ret, frame = cap.read()
            if not ret:
                log.warning(
                    "Failed to read frame {} for scene {}",
                    mid_frame, idx + 1,
                )
                continue

            slide_id = f"slide_{idx + 1:03d}"
            slide_filename = f"{slide_id}.jpg"
            slide_path = slides_dir / slide_filename

            cv2.imwrite(
                str(slide_path),
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, self._quality],
            )

            phash_val = self._compute_phash(frame)
            is_dup = phash_val in seen_hashes
            if not is_dup and phash_val:
                seen_hashes.add(phash_val)

            thumb_path = slides_dir / f"{slide_id}_thumb.jpg"
            self._generate_thumbnail(frame, thumb_path)

            slides.append(
                SlideImage(
                    slide_id=slide_id,
                    scene_id=idx + 1,
                    timestamp=round(mid_t, 2),
                    frame_number=mid_frame,
                    image_path=str(slide_path),
                    thumbnail_path=str(thumb_path),
                    phash=phash_val,
                    is_duplicate=is_dup,
                )
            )

            log.debug(
                "Extracted {} at {:.2f}s (frame {}), duplicate={}",
                slide_id, mid_t, mid_frame, is_dup,
            )

        cap.release()

        unique_count = sum(1 for s in slides if not s.is_duplicate)
        log.info(
            "Extracted {} slides ({} unique) from {} scenes",
            len(slides), unique_count, len(scene_bounds),
        )
        return slides

    def _compute_phash(self, frame) -> str:
        """Computes perceptual hash for frame deduplication."""
        try:
            from PIL import Image
            import imagehash

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            return str(imagehash.phash(pil_img))
        except ImportError:
            log.debug("imagehash not installed; skipping perceptual hash.")
            return ""
        except Exception as exc:
            log.debug("pHash computation failed: {}", exc)
            return ""

    def _generate_thumbnail(self, frame, output_path: Path) -> None:
        """Generates a 320px-wide thumbnail for gallery display."""
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
