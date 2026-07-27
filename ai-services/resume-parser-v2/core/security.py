"""
Security utilities and HTTP security headers middleware configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing standard security response headers."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Relax CSP for Swagger UI CDN assets on docs pages
        if request.url.path.endswith("/docs") or request.url.path.endswith("/openapi.json") or request.url.path.endswith("/redoc"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://cdn.jsdelivr.net;"
            )
        else:
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


def setup_security(app: FastAPI) -> None:
    """Applies security middlewares (CORS, Trusted Host, Security Headers) to FastAPI instance."""
    # CORS
    origins = (
        [str(origin) for origin in settings.ALLOWED_ORIGINS]
        if isinstance(settings.ALLOWED_ORIGINS, list)
        else [settings.ALLOWED_ORIGINS]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted Host
    hosts = (
        [str(host) for host in settings.ALLOWED_HOSTS]
        if isinstance(settings.ALLOWED_HOSTS, list)
        else [settings.ALLOWED_HOSTS]
    )
    if "*" not in hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)

    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)
