# ==============================================================================
# FacultyIQ Video Evidence Extraction Service — Dockerfile
# ==============================================================================
# Multi-stage build with FFmpeg + Tesseract system dependencies.
# Supports both GPU (CUDA) and CPU-only execution.
# ==============================================================================

FROM python:3.12-slim AS base

# System dependencies: FFmpeg, Tesseract OCR, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY tests/ ./tests/

# Create output directories
RUN mkdir -p output temp logs temp/uploads

# Expose API port
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
