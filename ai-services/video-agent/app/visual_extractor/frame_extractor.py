"""
Extracts frames from video files.
"""

import cv2
import os
import numpy as np
from loguru import logger
from typing import List, Tuple

def extract_frames(video_path: str, output_dir: str, interval_seconds: int = 2) -> List[Tuple[str, float]]:
    """
    Extracts representative key-frames from the video using scene detection (histogram comparison).
    Falls back to a minimum time interval to avoid extracting too many frames in high-motion scenes.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    logger.info(f"Extracting frames from {video_path} using scene detection")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0
        
    extracted_frames = []
    
    # We will compute the histogram of the last saved frame to compare
    last_saved_hist = None
    last_saved_timestamp = -999.0
    
    # Threshold for correlation (1.0 = identical, lower = more different)
    # A value below 0.85 indicates a >=15% difference (new slide, board updates)
    correlation_threshold = 0.85
    
    # Minimum seconds between frames to prevent bursting
    min_interval_sec = interval_seconds
    
    frame_count = 0
    success, frame = cap.read()
    
    while success:
        # We only check every N frames to save CPU (e.g. check twice a second)
        check_interval = max(1, int(fps / 2))
        
        if frame_count % check_interval == 0:
            timestamp_sec = frame_count / fps
            
            # Compute histogram for the current frame
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
            cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
            
            should_save = False
            reason = ""
            
            if last_saved_hist is None:
                should_save = True
                reason = "first_frame"
            else:
                correlation = cv2.compareHist(last_saved_hist, hist, cv2.HISTCMP_CORREL)
                time_since_last = timestamp_sec - last_saved_timestamp
                
                if correlation < correlation_threshold and time_since_last >= min_interval_sec:
                    should_save = True
                    reason = f"scene_change (correl={correlation:.2f})"
                elif time_since_last > 30.0:
                    # Force save a frame every 30 seconds just in case of long static scenes
                    should_save = True
                    reason = "force_interval (30s)"
            
            if should_save:
                filename = f"frame_{frame_count:06d}.jpg"
                out_path = os.path.join(output_dir, filename)
                cv2.imwrite(out_path, frame)
                extracted_frames.append((out_path, timestamp_sec))
                
                last_saved_hist = hist
                last_saved_timestamp = timestamp_sec
                logger.debug(f"Extracted frame at {timestamp_sec:.2f}s | Reason: {reason}")
            
        success, frame = cap.read()
        frame_count += 1
        
    cap.release()
    logger.info(f"Extracted {len(extracted_frames)} representative frames.")
    return extracted_frames
