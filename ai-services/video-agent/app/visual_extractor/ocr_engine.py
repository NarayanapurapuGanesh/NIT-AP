"""
OCR Engine for extracting text from frames.
"""

import pytesseract
from PIL import Image
import cv2
from loguru import logger
from typing import Dict, Any

def perform_ocr(image_path: str) -> Dict[str, Any]:
    """
    Extracts text from an image using Tesseract OCR.
    Returns a dictionary with raw text, keywords, and confidence.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"raw_text": "", "keywords": "", "confidence": 0.0}
            
        # Preprocessing for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Get detailed OCR output including confidence
        data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
        
        text_parts = []
        confidences = []
        
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            conf = int(data['conf'][i])
            
            if text and conf > -1:
                text_parts.append(text)
                confidences.append(conf)
                
        raw_text = " ".join(text_parts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Simple keyword extraction (just split by space and remove small words for now)
        keywords = list(set([word.lower() for word in text_parts if len(word) > 4]))
        
        return {
            "raw_text": raw_text,
            "keywords": ",".join(keywords[:10]), # Top 10 keywords
            "confidence": avg_confidence
        }
    except Exception as e:
        logger.error(f"OCR failed for {image_path}: {e}")
        return {"raw_text": "", "keywords": "", "confidence": 0.0}
