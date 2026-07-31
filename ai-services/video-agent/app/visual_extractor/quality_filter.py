"""
Quality filter to remove blurred or dark frames.
"""

import cv2
import numpy as np
from loguru import logger
import os
from typing import Tuple

def is_frame_high_quality(image_path: str, blur_threshold: float = 30.0, dark_threshold: float = 5.0) -> Tuple[bool, str]:
    """
    Checks if a frame is high quality (not blurred, not too dark, not empty).
    Returns (is_high_quality, reason_for_rejection).
    """
    if not os.path.exists(image_path):
        return False, "File not found"
        
    img = cv2.imread(image_path)
    if img is None:
        return False, "Failed to read image"
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Check for dark/empty frames
    mean_brightness = np.mean(gray)
    if mean_brightness < dark_threshold:
        return False, f"Too dark (mean brightness {mean_brightness:.1f} < {dark_threshold})"
        
    # Check for blur using Variance of Laplacian
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < blur_threshold:
        return False, f"Too blurry (Laplacian var {laplacian_var:.1f} < {blur_threshold})"
        
    return True, ""

def filter_quality(frames: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """
    Filters out low-quality frames from the list.
    Deletes the file if it's low quality to save disk space.
    """
    high_quality_frames = []
    
    for path, timestamp in frames:
        is_hq, reason = is_frame_high_quality(path)
        if is_hq:
            high_quality_frames.append((path, timestamp))
        else:
            logger.info(f"Rejected frame at {timestamp:.2f}s: {reason}")
            try:
                os.remove(path)
            except Exception as e:
                logger.warning(f"Failed to remove low quality frame {path}: {e}")
                
    logger.info(f"Quality filter: {len(high_quality_frames)}/{len(frames)} frames passed.")
    return high_quality_frames
