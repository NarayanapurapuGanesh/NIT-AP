from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.v1.endpoints import router as api_router
from app.config.settings import settings
from app.core.exceptions import VideoAgentError
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Initializing FacultyIQ Video Evaluation Agent (Phases 1-9)...")
    yield
    logger.info("Shutting down FacultyIQ Video Evaluation Agent...")


app = FastAPI(
    title="FacultyIQ Video Evaluation Agent",
    description="Offline-first, enterprise-ready Video Evaluation Service (Phases 1-9)",
    version="1.0.0",
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


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "FacultyIQ Video Evaluation Agent",
        "version": "1.0.0",
    }


@app.exception_handler(VideoAgentError)
async def video_agent_exception_handler(request: Request, exc: VideoAgentError):
    logger.error(f"Domain exception on {request.url.path}: {exc.message}")
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
    uvicorn.run("app.main:app", host=settings.host, port=8005, reload=True)
