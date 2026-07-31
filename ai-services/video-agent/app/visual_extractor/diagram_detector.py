"""
Detects educational visual types from images and OCR data.
"""

from typing import Dict, Any
import cv2
import numpy as np

def analyze_visual_content(image_path: str, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes image using OpenCV heuristics and OCR data to determine visual type.
    """
    raw_text = ocr_data.get("raw_text", "").lower()
    
    img = cv2.imread(image_path)
    content_type = "Slide"
    diagram_type = "None"
    detection_confidence = 0.5
    has_math = False
    has_handwriting = False
    has_tables = False
    
    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 1. Whiteboard Detection (Large uniform bright background)
        mean_v = np.mean(hsv[:, :, 2])
        std_v = np.std(hsv[:, :, 2])
        if mean_v > 200 and std_v < 40:
            content_type = "Whiteboard"
            detection_confidence = 0.85
            
        # 2. Code Editor / Screen-share Detection (Dark theme, structured text)
        elif mean_v < 60:
            content_type = "Code Editor"
            detection_confidence = 0.75
            
        # 3. Table Detection (Hough Lines - grid structure)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        if lines is not None and len(lines) > 15:
            # Check for orthogonality (horizontal & vertical lines)
            h_lines, v_lines = 0, 0
            for line in lines:
                if not isinstance(line, np.ndarray) or line.size != 4:
                    continue
                x1, y1, x2, y2 = line.flatten()
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi)
                if angle < 10 or angle > 170: h_lines += 1
                elif 80 < angle < 100: v_lines += 1
            if h_lines > 3 and v_lines > 3:
                has_tables = True
                diagram_type = "Table"
                detection_confidence = 0.90
                
        # 4. Diagram / Flowchart Detection (Contours, shapes)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        shape_count = 0
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            area = cv2.contourArea(cnt)
            if area > 500 and len(approx) in [3, 4, 8]:  # Triangles, Rectangles, Circles approx
                shape_count += 1
        
        if shape_count > 3 and not has_tables:
            diagram_type = "Flowchart/Diagram"
            detection_confidence = 0.85
            
        # 5. Handwriting / Equation Detection (Erratic contour properties + keywords)
        math_keywords = ['integral', 'dx', 'sum', 'sigma', 'cos', 'sin', 'tan', 'matrix', 'equation', '=']
        has_math = any(kw in raw_text for kw in math_keywords)
        
        if content_type == "Whiteboard" and len(contours) > 100:
            has_handwriting = True
            
        if has_math and has_handwriting:
            diagram_type = "Equation/Math"
            detection_confidence = 0.95
            
    # Fallback to OCR keywords if CV is ambiguous
    if diagram_type == "None":
        if any(kw in raw_text for kw in ['class', 'interface', 'implements', 'extends']):
            diagram_type = "UML"
            detection_confidence = 0.7
        elif any(kw in raw_text for kw in ['architecture', 'client', 'server', 'database']):
            diagram_type = "Architecture Diagram"
            detection_confidence = 0.7
        elif any(kw in raw_text for kw in ['node', 'edge', 'tree', 'root', 'leaf', 'binary']):
            diagram_type = "Tree/Graph"
            detection_confidence = 0.7

    rank_score = (ocr_data.get("confidence", 0) / 100) * 5.0
    if diagram_type != "None": rank_score += 3.0
    if has_tables or has_math: rank_score += 2.0
        
    return {
        "visual_type": content_type,
        "contains_handwriting": has_handwriting,
        "contains_diagram": diagram_type != "None",
        "contains_flowchart": diagram_type == "Flowchart/Diagram",
        "contains_code": content_type == "Code Editor",
        "contains_equation": has_math,
        "contains_table": has_tables,
        "rank_score": min(10.0, rank_score),
        "detection_confidence": detection_confidence
    }
