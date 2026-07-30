# FacultyIQ Video Evidence Extraction Service

> **Enterprise-grade, offline-first video evidence extraction service** for the FacultyIQ faculty recruitment platform. Extracts transcripts, slides, OCR text, teaching timelines, and summaries from faculty teaching demonstration videos.

---

## Architecture Overview

```
video-agent/
├── app/
│   ├── api/                    # FastAPI endpoints & dependency injection
│   │   ├── dependencies.py     # DI providers (singleton orchestrator)
│   │   └── v1/endpoints.py     # All REST API endpoints
│   ├── config/                 # Configuration system
│   │   ├── config.yaml         # YAML configuration file
│   │   └── settings.py         # Pydantic v2 hierarchical settings
│   ├── core/                   # Core infrastructure
│   │   ├── exceptions.py       # Domain exception hierarchy
│   │   ├── gpu.py              # GPU detection (CUDA/CPU fallback)
│   │   └── logging.py          # Module-specific Loguru logging
│   ├── models/                 # Pydantic v2 data models
│   │   ├── validation.py       # Video metadata & validation result
│   │   ├── transcription.py    # Segments, word timestamps
│   │   ├── scene.py            # Scenes, slides, keyframes
│   │   ├── ocr.py              # OCR entries (titles, bullets, code, equations)
│   │   ├── timeline.py         # Unified teaching timeline
│   │   ├── summary.py          # Teaching summary (topics, keywords, algorithms)
│   │   ├── gallery.py          # Slide gallery for frontend
│   │   ├── voice.py            # Voice metrics (optional)
│   │   ├── job.py              # Job status & processing steps
│   │   └── dtos.py             # Frontend-ready DTOs (camelCase)
│   ├── validators/             # Module 1: Video validation
│   ├── preprocessing/          # Module 2: Audio extraction, preview generation
│   ├── transcription/          # Module 3: Faster-Whisper speech-to-text
│   ├── scene_detection/        # Module 4: Smart frame/slide extraction
│   ├── ocr/                    # Module 5: Tesseract OCR
│   ├── voice_analysis/         # Module 10: Optional voice metrics
│   ├── services/               # Service layer
│   │   ├── pipeline_orchestrator.py  # Master async pipeline
│   │   ├── timeline_builder.py       # Module 6: Timeline merger
│   │   ├── summary_generator.py      # Module 9: Offline NLP summary
│   │   └── storage_service.py        # Output & report management
│   ├── utils/                  # Shared utilities
│   └── main.py                 # FastAPI application entry point
├── output/                     # Generated outputs per job
├── tests/                      # Pytest test suite
├── Dockerfile                  # Docker build
├── docker-compose.yml          # Docker Compose stack
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Technology Stack

| Component | Technology |
|:---|:---|
| Language | Python 3.12 |
| API Framework | FastAPI + Uvicorn |
| Video Processing | OpenCV + FFmpeg |
| Speech-to-Text | Faster-Whisper (CTranslate2) |
| OCR | Tesseract OCR + Pillow |
| Scene Detection | PySceneDetect |
| Voice Analysis | librosa + scipy |
| Configuration | PyYAML + Pydantic v2 |
| Logging | Loguru |
| Containerization | Docker |

**All processing runs locally. No cloud APIs. No OpenAI. No Gemini.**

---

## Quick Start

### Prerequisites

- Python 3.12+
- FFmpeg (system-installed)
- Tesseract OCR (system-installed)
- CUDA GPU (optional, CPU fallback is automatic)

### Installation

```bash
cd ai-services/video-agent

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Run the Server

```bash
python -m app.main
```

Server starts at `http://localhost:8005`. API docs at `http://localhost:8005/docs`.

### Run with Docker

```bash
docker-compose up --build
```

---

## API Endpoints

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/video/upload` | Upload and validate a video |
| `POST` | `/video/process` | Run complete evidence extraction pipeline |
| `POST` | `/video/transcript` | Generate transcript only |
| `POST` | `/video/slides` | Extract slides only |
| `POST` | `/video/ocr` | Extract OCR text from slides |
| `POST` | `/video/timeline` | Generate unified timeline |
| `POST` | `/video/summary` | Generate teaching summary |
| `GET` | `/video/status/{jobId}` | Get job processing status |
| `GET` | `/video/report/{jobId}` | Get complete evidence report |
| `GET` | `/video/slides/{jobId}/images/{slideId}` | Serve slide image |
| `GET` | `/health` | Service health check |

---

## Pipeline Modules

| Module | Function | Configurable |
|:---|:---|:---|
| 1. Validation | Format, MIME, duration, resolution, audio, codec checks | Limits via config.yaml |
| 2. Preprocessing | Audio extraction (16kHz WAV), 480p preview | Always runs |
| 3. Transcription | Faster-Whisper with word timestamps | `pipeline.transcription` |
| 4. Frame Extraction | PySceneDetect + smart keyframe extraction | `pipeline.frame_extraction` |
| 5. OCR | Tesseract with structural analysis | `pipeline.ocr` |
| 6. Timeline | Unified timeline merging transcript + slides + OCR | `pipeline.timeline` |
| 9. Summary | Offline NLP-based teaching summary | `pipeline.summary` |
| 10. Voice Analysis | Speech rate, pitch, volume, pauses | `pipeline.voice_analysis` |

### Module Toggling

Edit `app/config/config.yaml`:

```yaml
pipeline:
  transcription: true
  frame_extraction: true
  ocr: true
  timeline: true
  summary: true
  voice_analysis: false  # Enable/disable
```

---

## Output Structure

Each processed video generates outputs in `output/{jobId}/`:

```
output/{jobId}/
├── metadata.json       # Video metadata
├── audio.wav           # Extracted audio (16kHz mono)
├── preview.mp4         # 480p preview video
├── transcript.json     # Full transcript with word timestamps
├── transcript.txt      # Plain text transcript
├── slides/             # Extracted slide images
│   ├── slide_001.jpg
│   ├── slide_001_thumb.jpg
│   ├── slide_002.jpg
│   └── ...
├── scenes.json         # Scene detection results
├── ocr.json            # OCR extraction per slide
├── ocr.txt             # Plain text OCR
├── timeline.json       # Unified teaching timeline
├── summary.json        # Teaching summary
├── gallery.json        # Slide gallery for frontend
├── voice_analysis.json # Voice metrics (if enabled)
└── report.json         # Consolidated evidence report
```

---

## Configuration Guide

All configuration is in `app/config/config.yaml`. Key sections:

### Whisper Model Selection

```yaml
whisper:
  model_size: small   # tiny, base, small, medium, large-v3
  device: auto        # auto, cuda, cpu
  compute_type: auto  # auto, float16, int8
```

### GPU Acceleration

```yaml
gpu:
  enabled: true
  prefer_cuda: true
  ffmpeg_hwaccel: auto  # auto, cuda, none
```

### Scene Detection Sensitivity

```yaml
scene_detection:
  threshold: 27.0         # Lower = more sensitive
  min_scene_duration: 2.0 # Minimum seconds per scene
```

---

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_summary.py -v
```

---

## Logging

Module-specific log files are generated in `logs/`:

| Log File | Module |
|:---|:---|
| `video_agent.log` | Master log (all modules) |
| `validation.log` | Video validation |
| `transcription.log` | Whisper transcription |
| `ocr.log` | Tesseract OCR |
| `timeline.log` | Timeline builder |
| `summary.log` | Summary generator |
| `voice.log` | Voice analysis |
| `pipeline.log` | Pipeline orchestrator |

---

## Integration with FacultyIQ

This service exposes REST APIs consumed by:
- **FacultyIQ Frontend** (Next.js) — via frontend-ready DTOs with camelCase JSON
- **Decision Agent** — via `GET /video/report/{jobId}` for evidence-based evaluation
- **Backend API** (ASP.NET Core) — via HTTP client calling pipeline endpoints

---

## License

MIT License. See `LICENSE` for details.
