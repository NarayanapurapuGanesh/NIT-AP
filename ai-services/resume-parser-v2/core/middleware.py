"""
Global FastAPI middlewares for request tracking and exception handling.
"""

import time
import uuid
from typing import Any, Dict
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import structlog

from core.constants import REQUEST_ID_HEADER, RESPONSE_TIME_HEADER
from core.exceptions import BaseAppException
from core.logging import get_logger

logger = get_logger("middleware")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Injects or propagates unique X-Request-ID headers across HTTP context."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid.uuid4()))
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[RESPONSE_TIME_HEADER] = f"{process_time_ms}ms"

        structlog.contextvars.unbind_contextvars("request_id")
        return response


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """Catches unhandled exceptions and formats consistent JSON error responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except BaseAppException as exc:
            logger.warning(
                "Handled domain exception",
                error=exc.message,
                status_code=exc.status_code,
                details=exc.details,
            )
            payload: Dict[str, Any] = {
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "details": exc.details,
                }
            }
            return JSONResponse(status_code=exc.status_code, content=payload)
        except Exception as exc:
            logger.error("Unhandled server exception", error=str(exc), exc_info=True)
            payload = {
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected server error occurred.",
                    "details": {},
                }
            }
            return JSONResponse(status_code=500, content=payload)
