"""
Token Bucket Rate Limiting Engine.
Supports Per-User, Per-Tenant, Per-IP, and Per-API rate limits with burst protection.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict
from app.platform.schemas.platform_models import RateLimitStatus
from core.logging import get_logger

logger = get_logger("rate_limiter")


class RateLimiterEngine:
    """Enterprise Token Bucket Rate Limiter."""

    def __init__(self) -> None:
        self._tokens: Dict[str, float] = {}
        self._last_refill: Dict[str, datetime] = {}

    def is_allowed(self, client_key: str, max_requests: int = 100, window_seconds: int = 60) -> RateLimitStatus:
        now = datetime.now(timezone.utc)
        refill_rate = max_requests / float(window_seconds)

        if client_key not in self._tokens:
            self._tokens[client_key] = float(max_requests)
            self._last_refill[client_key] = now

        # Refill tokens based on elapsed time
        elapsed = (now - self._last_refill[client_key]).total_seconds()
        self._tokens[client_key] = min(float(max_requests), self._tokens[client_key] + elapsed * refill_rate)
        self._last_refill[client_key] = now

        if self._tokens[client_key] >= 1.0:
            self._tokens[client_key] -= 1.0
            allowed = True
        else:
            allowed = False
            logger.warning("Rate limit exceeded for client", client_key=client_key)

        remaining = int(self._tokens[client_key])
        reset_at = now + timedelta(seconds=window_seconds)

        return RateLimitStatus(
            client_key=client_key,
            remaining_requests=remaining if allowed else 0,
            total_limit=max_requests,
            window_seconds=window_seconds,
            reset_at=reset_at,
        )
