"""
Exports visual gallery to PDF.
"""

from fpdf import FPDF
import os

def export_to_pdf(visuals_data: list, output_path: str) -> str:
    """
    Generates a Teaching_Visuals_Report.pdf from the extracted visuals.
    visuals_data is a list of dicts:
    [{"image_path": "...", "timestamp": "...", "ocr": "...", "topic": "..."}]
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FacultyIQ Teaching Visuals Report", ln=True, align="C")
    pdf.ln(10)
    
    for visual in visuals_data:
        image_path = visual.get("image_path")
        if not os.path.exists(image_path):
            continue
            
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"Timestamp: {visual.get('timestamp_str', '')}", ln=True)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, f"Topic: {visual.get('topic', 'General')} | Type: {visual.get('diagram_type', 'None')}", ln=True)
        
        # Insert image
        try:
            pdf.image(image_path, x=15, w=180)
            pdf.ln(10) # spacing
        except Exception:
            pdf.cell(0, 10, "[Image could not be loaded]", ln=True)
            
        # OCR
        pdf.set_font("Arial", '', 10)
        ocr_text = visual.get("ocr", "")
        # Very basic ascii encoding fallback for FPDF
        ocr_text = ocr_text.encode('ascii', 'replace').decode('ascii')
        pdf.multi_cell(0, 8, f"Extracted Text:\n{ocr_text[:500]}...")
        pdf.ln(15)
        
    pdf.output(output_path)
    return output_path
