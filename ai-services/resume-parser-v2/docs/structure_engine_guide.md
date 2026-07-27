# Enterprise Resume Structure Intelligence Engine Guide (`resume-parser-v2`)

> Phase 3 Pipeline converting Normalized Document Objects (NDO) into deterministic `SemanticResumeModel` & `ResumeStructureGraph` representations without LLM dependencies.

---

## 🏛️ Pipeline Flowchart

```
                 Normalized Document Object (NDO - Phase 2 Output)
                                         │
                                         ▼
                           [1. Heading Detector Engine]             <-- Typography, bold, caps & line length heuristics
                                         │
                                         ▼
                     [2. Heading Classifier & Normalizer]           <-- Exact match, regex & Levenshtein fuzzy match
                                         │
                                         ▼
                         [3. Heading Intelligence Engine]           <-- Level depth (H1/H2/H3) & confidence
                                         │
                                         ▼
                        [4. Section Segmenter & Detector]           <-- Maps blocks to 40+ canonical sections
                                         │
                                         ▼
                           [5. Structure Normalizer]                <-- Deduplicates consecutive identical sections
                                         │
                                         ▼
                           [6. Reading Flow Analyzer]               <-- Flags broken multi-col flow & leakage
                                         │
                                         ▼
                              [7. Evidence Linker]                  <-- 100% evidence provenance attachment
                                         │
                                         ▼
                           [8. Hierarchy Tree Builder]              <-- Composite tree (Resume -> H1 -> H2)
                                         │
                                         ▼
                         [9. Resume Structure Graph DAG]            <-- Directed Graph linking nodes & provenance
                                         │
                                         ▼
                          [10. Structural Validator]                <-- Quality score & missing section checks
                                         │
                                         ▼
                       Final SemanticResumeModel JSON Payload
```

---

## 📋 40+ Canonical Section Types

- **Header & Summary**: `Header`, `Summary`, `Career Objective`
- **Academic & Professional Experience**: `Academic Experience`, `Teaching Experience`, `Research Experience`, `Professional Experience`, `Industry Experience`
- **Education & Credentials**: `Education`, `Certifications`
- **Skills Taxonomy**: `Skills`, `Technical Skills`, `Programming Languages`, `Tools`, `Frameworks`, `Soft Skills`
- **Scholarly & Research Output**: `Publications`, `Research Projects`, `Patents`, `Books`, `Conferences`, `Workshops`, `Projects`
- **Honors & Recognition**: `Achievements`, `Awards`, `Honors`, `Memberships`, `Professional Bodies`
- **Misc & Administrative**: `Languages`, `References`, `Interests`, `Declaration`, `Signature`, `Custom Sections`, `Unknown Sections`

---

## 🔌 API Endpoint

### `POST /api/v1/resume/structure`

**Content-Type**: `application/json`  
**Body Parameter**: JSON payload of `NormalizedDocument` (NDO)

#### cURL Example:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/resume/structure' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{ ... NormalizedDocument JSON ... }'
```

#### Example Output (`SemanticResumeModel` JSON):

```json
{
  "success": true,
  "message": "Resume structure for 'alice_cv.pdf' extracted successfully (4 sections).",
  "data": {
    "document_uuid": "test_doc_12345",
    "filename": "alice_cv.pdf",
    "header_block": {
      "canonical_type": "Header",
      "original_heading": "Header",
      "raw_text": "Dr. Alice Smith\nProfessor of Computer Science..."
    },
    "sections": [
      {
        "section_id": "9a8b7c6d-...",
        "canonical_type": "Education",
        "original_heading": "EDUCATION",
        "heading_level": 1,
        "confidence": 0.95,
        "page_numbers": [1],
        "reading_order_start": 2,
        "reading_order_end": 3,
        "raw_text": "EDUCATION\nPh.D. in Computer Science, Stanford University..."
      },
      {
        "section_id": "1a2b3c4d-...",
        "canonical_type": "Academic Experience",
        "original_heading": "ACADEMIC EXPERIENCE",
        "heading_level": 1,
        "confidence": 0.95,
        "page_numbers": [1],
        "reading_order_start": 4,
        "reading_order_end": 5,
        "raw_text": "ACADEMIC EXPERIENCE\nAssociate Professor, NIT AP..."
      }
    ],
    "hierarchy_tree": {
      "name": "Resume",
      "level": 0,
      "section_type": "Root",
      "children": [
        {
          "name": "EDUCATION",
          "level": 1,
          "section_type": "Education"
        },
        {
          "name": "ACADEMIC EXPERIENCE",
          "level": 1,
          "section_type": "Academic Experience"
        }
      ]
    },
    "structure_graph": {
      "nodes": [
        { "node_id": "doc_test_doc", "node_type": "document", "label": "Document Root" },
        { "node_id": "sec_9a8b7c6d", "node_type": "section", "label": "Education" }
      ],
      "edges": [
        { "source_id": "doc_test_doc", "target_id": "sec_9a8b7c6d", "relation_type": "contains" }
      ]
    },
    "validation_report": {
      "is_valid": true,
      "quality_score": 1.0,
      "missing_sections": [],
      "broken_flow_warnings": []
    },
    "processing_time_ms": 12.45
  }
}
```
