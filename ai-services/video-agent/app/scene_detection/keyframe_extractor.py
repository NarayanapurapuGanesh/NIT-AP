from pathlib import Path
from typing import List, Union
import cv2
from loguru import logger
from app.models.scene import Keyframe


class KeyframeExtractor:
    """Extracts keyframes for detected scenes and computes perceptual hash (pHash) for deduplication."""

    def extract_keyframes(
        self,
        video_path: Union[str, Path],
        scene_bounds: List[tuple],
        output_dir: Union[str, Path],
    ) -> List[Keyframe]:
        import imagehash
        from PIL import Image

        v_path = Path(video_path).resolve()
        out_dir = Path(output_dir).resolve() / "keyframes"
        out_dir.mkdir(parents=True, exist_ok=True)

        cap = cv2.VideoCapture(str(v_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        keyframes = []

        for idx, (start_t, end_t) in enumerate(scene_bounds):
            mid_t = (start_t + end_t) / 2.0
            mid_frame = int(mid_t * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
            ret, frame = cap.read()
            if not ret:
                continue

            kf_filename = f"scene_{idx+1:03d}_keyframe.jpg"
            kf_path = out_dir / kf_filename
            cv2.imwrite(str(kf_path), frame)

            try:
                pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                phash_val = str(imagehash.phash(pil_img))
            except Exception:
                phash_val = "0000000000000000"

            keyframes.append(
                Keyframe(
                    keyframe_id=f"scene_{idx+1}_kf_1",
                    timestamp=round(mid_t, 2),
                    frame_number=mid_frame,
                    file_path=str(kf_path),
                    phash=phash_val,
                    is_duplicate=False,
                )
            )

        cap.release()
        return keyframes
