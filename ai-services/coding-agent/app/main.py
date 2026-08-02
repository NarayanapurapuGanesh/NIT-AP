"""
FacultyIQ Coding Intelligence Agent — FastAPI Application Entry Point.

Production-grade Coding Assessment Engine with:
  - Adaptive DSA assessment
  - Secure code execution sandbox
  - Static code analysis
  - Complexity estimation
  - AI-powered explanation evaluation
  - DSA viva engine
  - Evidence generation
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.config.settings import settings
from app.core.logging import setup_logging
from app.core.exceptions import CodingAgentError
from app.db.init_db import init_database
from app.api.v1.endpoints import router as coding_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    setup_logging()
    logger.info("=" * 60)
    logger.info("  FacultyIQ Coding Intelligence Agent v{}", settings.app.version)
    logger.info("  Environment: {}", settings.app.environment)
    logger.info("  Port: {}", settings.server.port)
    logger.info("=" * 60)

    # Initialize database and seed questions
    init_database()

    # Log sandbox mode
    from app.sandbox.sandbox_manager import SandboxManager
    sandbox = SandboxManager()
    logger.info("Sandbox mode: {} (Docker available: {})",
                sandbox.active_mode, sandbox.is_docker_available)

    yield

    logger.info("Coding Intelligence Agent shutting down.")


app = FastAPI(
    title="FacultyIQ Coding Intelligence Agent",
    description=(
        "Production-grade Coding Assessment Engine for the FacultyIQ "
        "Enterprise AI Faculty Recruitment Platform. Evaluates algorithmic "
        "thinking, code quality, and problem-solving ability."
    ),
    version=settings.app.version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for domain errors
@app.exception_handler(CodingAgentError)
async def coding_agent_error_handler(request: Request, exc: CodingAgentError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


# Health check
@app.get("/health")
def health():
    """Health check endpoint."""
    from app.sandbox.sandbox_manager import SandboxManager
    sandbox = SandboxManager()
    return {
        "status": "healthy",
        "service": "coding-intelligence-agent",
        "version": settings.app.version,
        "sandbox_mode": sandbox.active_mode,
        "docker_available": sandbox.is_docker_available,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Include routers
app.include_router(coding_router)
