"""
Duplicate filter using perceptual hashing (imagehash).
"""

import imagehash
from PIL import Image
from loguru import logger
import os

def filter_duplicates(frames: list[tuple[str, float]], hash_threshold: int = 5) -> list[tuple[str, float]]:
    """
    Removes nearly identical images using perceptual hashing.
    """
    unique_frames = []
    seen_hashes = []
    
    for path, timestamp in frames:
        if not os.path.exists(path):
            continue
            
        try:
            with Image.open(path) as img:
                # Use perceptual hash
                current_hash = imagehash.phash(img)
                
            is_duplicate = False
            for seen_hash in seen_hashes:
                # If the difference between hashes is less than threshold, it's a duplicate
                if current_hash - seen_hash <= hash_threshold:
                    is_duplicate = True
                    break
                    
            if not is_duplicate:
                unique_frames.append((path, timestamp))
                seen_hashes.append(current_hash)
            else:
                # Delete duplicate file to save space
                try:
                    os.remove(path)
                except Exception as e:
                    logger.warning(f"Failed to remove duplicate frame {path}: {e}")
                    
        except Exception as e:
            logger.error(f"Error hashing image {path}: {e}")
            
    logger.info(f"Duplicate filter: {len(unique_frames)}/{len(frames)} unique frames kept.")
    return unique_frames
