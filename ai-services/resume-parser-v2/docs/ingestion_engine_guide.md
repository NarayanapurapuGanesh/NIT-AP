# Enterprise Document Ingestion & Extraction Engine Guide (`resume-parser-v2`)

> Production-grade Phase 2 pipeline converting candidate resumes and academic CVs into canonical `NormalizedDocument` objects with 100% coordinate and evidence lineage.

---

## 🏛️ Pipeline Architecture

```
                                  Uploaded Payload (PDF / DOCX / TXT / RTF)
                                                     │
                                                     ▼
                                      [1. Document Validation Engine]       <-- Magic bytes, hashes, macro checks
                                                     │
                                                     ▼
                                      [2. Ingestion Classification]        <-- Native PDF, Scanned PDF, DOCX
                                                     │
                                                     ▼
                                        [3. Document Loader Factory]       <-- PyMuPDF, docx, txt loaders
                                                     │
                                                     ▼
                                         [4. Metadata Extractor]           <-- Author, title, dates, version
                                                     │
                                                     ▼
                                     [5. Enterprise Text Extractor]        <-- PyMuPDF fitz primary, pdfplumber
                                                     │
                                                     ▼
                                         [6. OCR Fallback Engine]          <-- Automatic trigger for low text density
                                                     │
                                                     ▼
                                      [7. Reading Order Reconstruction]    <-- Single-col, 2-col academic CVs
                                                     │
                                                     ▼
                                         [8. Layout Analysis Engine]       <-- Margins, headers, footers, sections
                                                     │
                                                     ▼
                                    [9 & 10. Table & Image Detectors]      <-- Tables, profile photos, charts
                                                     │
                                                     ▼
                                      [11. Coordinate & Offset Mapper]     <-- Exact (x0, y0, x1, y1) & offsets
                                                     │
                                                     ▼
                                       [12. Lineage Evidence Builder]      <-- 100% evidence traceability
                                                     │
                                                     ▼
                                         [14. Statistics Engine]           <-- Word/char counts, font metrics
                                                     │
                                                     ▼
                                     Final Canonical NormalizedDocument JSON
```

---

## 🔌 API Endpoint

### `POST /api/v1/ingest`

**Content-Type**: `multipart/form-data`  
**Body Parameter**: `file` (Binary File Stream)

#### Example Request:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/ingest' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@faculty_resume.pdf;type=application/pdf'
```

#### Example Output (`NormalizedDocument` JSON):

```json
{
  "success": true,
  "message": "Document 'faculty_resume.pdf' successfully ingested (Native PDF, 4 pages).",
  "data": {
    "document_uuid": "e8d64f0b-48c2-4b36-a192-3ef4861bc978",
    "filename": "faculty_resume.pdf",
    "format_type": "pdf",
    "classification_type": "Native PDF",
    "metadata": {
      "file_hash": "a1b2c3d4e5f67890...",
      "author": "Dr. Jane Doe",
      "title": "Academic CV 2026",
      "page_count": 4,
      "language": "en",
      "pdf_version": "1.7"
    },
    "statistics": {
      "word_count": 1420,
      "char_count": 9230,
      "paragraph_count": 48,
      "line_count": 112,
      "avg_font_size": 10.5,
      "extraction_confidence": 0.95
    },
    "pages": [
      {
        "page_number": 1,
        "width": 612.0,
        "height": 792.0,
        "text": "DR. JANE DOE\nProfessor of Computer Science...",
        "blocks": [
          {
            "block_id": "b1a2c3-...",
            "block_type": "heading",
            "reading_order": 1,
            "text": "DR. JANE DOE",
            "coordinates": {
              "page_number": 1,
              "x0": 50.0,
              "y0": 50.0,
              "x1": 250.0,
              "y1": 70.0,
              "width": 200.0,
              "height": 20.0
            }
          }
        ]
      }
    ],
    "processing_time_ms": 42.15
  }
}
```
