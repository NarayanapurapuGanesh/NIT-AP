"""
FacultyIQ Video Evidence Extraction Service — FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.api.v1.endpoints import router as api_router
from app.config.settings import settings
from app.core.exceptions import VideoAgentError
from app.core.logging import setup_logging
from app.utils.file_utils import ensure_directory


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    setup_logging()
    logger.info(
        "Initializing {} v{}...",
        settings.app.name,
        settings.app.version,
    )

    ensure_directory(settings.base_dir / settings.storage.output_dir)
    ensure_directory(settings.base_dir / settings.storage.temp_dir)
    ensure_directory(settings.base_dir / settings.storage.uploads_dir)

    yield

    logger.info("Shutting down {}...", settings.app.name)


app = FastAPI(
    title=settings.app.name,
    description=(
        "Offline-first, enterprise-ready Video Evidence Extraction Service. "
        "Extracts transcripts, slides, OCR text, teaching timelines, and summaries "
        "from faculty teaching demonstration videos."
    ),
    version=settings.app.version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

output_dir = settings.base_dir / settings.storage.output_dir
if output_dir.exists():
    app.mount(
        "/static/output",
        StaticFiles(directory=str(output_dir)),
        name="output_files",
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app.name,
        "version": settings.app.version,
    }


@app.exception_handler(VideoAgentError)
async def video_agent_exception_handler(
    request: Request, exc: VideoAgentError
):
    """Handles all domain exceptions with structured error responses."""
    logger.error("Domain exception on {}: {}", request.url.path, exc.message)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
    )
