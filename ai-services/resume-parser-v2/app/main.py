"""
FastAPI Application Bootstrap & Lifespan Controller.
Academic Resume Intelligence Engine - Phase 1 Production Foundation.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI

from app.api.v1.router import api_v1_router
from app.services.registry import service_registry
from core.config import settings
from core.constants import API_DESCRIPTION, API_TITLE, API_VERSION
from core.logging import get_logger, setup_logging
from core.middleware import GlobalExceptionMiddleware, RequestIdMiddleware
from core.security import setup_security


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Asynchronous application lifecycle context manager for startup and shutdown events."""
    # 1. Startup Lifecycle
    setup_logging()
    logger = get_logger("app_lifecycle")
    logger.info(
        "Initializing application engine",
        app_name=settings.APP_NAME,
        env=settings.APP_ENV.value,
        version=API_VERSION,
    )

    yield

    # 2. Shutdown Lifecycle
    logger.info("Initiating graceful shutdown sequence...")
    await service_registry.shutdown_all()
    logger.info("Application shutdown complete.")


def create_application() -> FastAPI:
    """Factory function for instantiating the enterprise FastAPI app."""
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if not settings.is_production else None,
        docs_url=f"{settings.API_V1_STR}/docs" if not settings.is_production else None,
        redoc_url=f"{settings.API_V1_STR}/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Attach Core Middlewares
    app.add_middleware(GlobalExceptionMiddleware)
    app.add_middleware(RequestIdMiddleware)

    # Attach Security Configurations (CORS, Trusted Host, Security Headers)
    setup_security(app)

    # Include Versioned API Routes
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    @app.get("/", include_in_schema=False)
    async def root_redirect():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
    )
