# Document Classification Engine Guide (`resume-parser-v2`)

> Production-ready, deterministic, 9-layer Clean Architecture document classification engine for FacultyIQ.

---

## 🏛️ Architecture Overview

The Document Classification Engine operates completely offline using deterministic pattern matching, regex rules, structural layout heuristics, and weighted confidence scoring.

```
Upload Payload (PDF / DOCX / DOC / PNG / JPEG / TIFF)
                       │
                       ▼
           [Layer 1: Input Handler]          <-- Magic Bytes & Payload Verification
                       │
                       ▼
          [Layer 2: Document Reader]         <-- Format Readers (pypdf, python-docx, Pillow)
                       │
                       ▼
        [Layer 3: Metadata Extractor]        <-- Pages, Chars, Words, Dimensions, Scanned state
                       │
                       ▼
           [Layer 4: Text Sampler]           <-- Header block, Footer block, Headings
                       │
                       ▼
            [Layer 5: Rule Engine]           <-- Loads config/rules/v1/classification_rules.json
                       │
                       ▼
          [Layer 6: Pattern Engine]          <-- Structural & Density Heuristics
                       │
                       ▼
         [Layer 7: Confidence Scorer]        <-- Asymptotic Normalized Score [0.00 - 1.00]
                       │
                       ▼
        [Layer 8: Evidence Collector]        <-- Reasons & Rule Evidence Accumulation
                       │
                       ▼
    [Layer 9: Classification Result Builder] <-- Payload Assembly & Next Stage Routing
                       │
                       ▼
         Final JSON Classification Payload
```

---

## 📋 Supported Document Types (17 Categories)

1. **Resume** (`accepted: true`, `next_stage: "TextExtraction"`)
2. **Academic Resume** (`accepted: true`, `next_stage: "TextExtraction"`)
3. **Faculty CV** (`accepted: true`, `next_stage: "TextExtraction"`)
4. **Curriculum Vitae** (`accepted: true`, `next_stage: "TextExtraction"`)
5. **Research CV** (`accepted: true`, `next_stage: "TextExtraction"`)
6. **Student Resume** (`accepted: true`, `next_stage: "TextExtraction"`)
7. **Invoice** (`accepted: false`, `next_stage: "SpecializedHandler"`)
8. **Certificate** (`accepted: false`, `next_stage: "Rejected"`)
9. **Research Paper** (`accepted: false`, `next_stage: "SpecializedHandler"`)
10. **Book** (`accepted: false`, `next_stage: "Rejected"`)
11. **Course Syllabus** (`accepted: false`, `next_stage: "SpecializedHandler"`)
12. **Question Paper** (`accepted: false`, `next_stage: "SpecializedHandler"`)
13. **Marksheet** (`accepted: false`, `next_stage: "SpecializedHandler"`)
14. **Cover Letter** (`accepted: false`, `next_stage: "Rejected"`)
15. **Recommendation Letter** (`accepted: false`, `next_stage: "Rejected"`)
16. **Identity Document** (`accepted: false`, `next_stage: "Rejected"`)
17. **Unknown** (`accepted: false`, `next_stage: "Rejected"`)

---

## 🔌 API Documentation

### `POST /api/v1/classify`

**Content-Type**: `multipart/form-data`  
**Body Parameter**: `file` (Binary File Stream)

#### Example Request (cURL):

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/classify' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@faculty_cv.pdf;type=application/pdf'
```

#### Example Response (JSON):

```json
{
  "success": true,
  "message": "Document classified as 'Faculty CV' with 91% confidence.",
  "data": {
    "document_type": "Faculty CV",
    "confidence": 0.91,
    "accepted": true,
    "reasons": [
      "Header contains explicit 'Curriculum Vitae' / 'Faculty CV' title",
      "Mentions faculty academic rank (Professor / Associate / Assistant Professor)",
      "Contains scholarly publication section",
      "Mentions research grants, patents, or PhD supervision"
    ],
    "evidence": [
      {
        "rule": "fcv_title",
        "weight": 0.35,
        "matched_text": "CURRICULUM VITAE",
        "source_layer": "rule_engine"
      },
      {
        "rule": "fcv_academic_rank",
        "weight": 0.25,
        "matched_text": "Professor",
        "source_layer": "rule_engine"
      },
      {
        "rule": "fcv_publications",
        "weight": 0.20,
        "matched_text": "PUBLICATIONS",
        "source_layer": "rule_engine"
      },
      {
        "rule": "fcv_grants",
        "weight": 0.15,
        "matched_text": "Research Grants",
        "source_layer": "rule_engine"
      }
    ],
    "next_stage": "TextExtraction",
    "metadata": {
      "page_count": 4,
      "char_count": 5210,
      "line_count": 142,
      "word_count": 780,
      "title": null,
      "author": null,
      "is_scanned": false
    },
    "processing_time_ms": 28.45
  },
  "timestamp": "2026-07-21T21:00:00Z"
}
```

---

## 🛠️ Developer Guide: Adding New Document Types & Rules

To introduce a new document type (e.g. `Grant Application`) without modifying python code:

1. Open `config/rules/v1/classification_rules.json`.
2. Add a new rule definition block under `"document_rules"`:
```json
{
  "type": "Grant Application",
  "priority": 85,
  "min_score": 0.40,
  "rules": [
    {
      "id": "grant_header",
      "type": "header_regex",
      "pattern": "(?i)grant\\s+proposal|research\\s+grant\\s+application",
      "weight": 0.40,
      "reason": "Header contains explicit 'Grant Proposal' or 'Grant Application' title"
    }
  ]
}
```
3. If the type should be accepted for resume ingestion, add `"Grant Application"` to `"accepted_types"` in `classification_rules.json` or `DocumentTypeEnum`.
