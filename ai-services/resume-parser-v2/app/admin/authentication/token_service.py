"""
JWT Token and Session Management Service.
Handles JWT creation, verification, refresh token rotation, and token blacklisting.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Set
import jwt
from app.admin.schemas.admin_models import TokenPayload
from core.config import settings
from core.logging import get_logger

logger = get_logger("token_service")


class TokenService:
    """JWT Token Management Service."""

    def __init__(self) -> None:
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60
        self.refresh_token_expire_days = 7
        self._blacklisted_tokens: Set[str] = set()

    def create_access_token(self, user_id: str, email: str, tenant_id: str, roles: list[str]) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self.access_token_expire_minutes)
        payload = TokenPayload(
            sub=user_id,
            email=email,
            tenant_id=tenant_id,
            roles=roles,
            iat=int(now.timestamp()),
            exp=int(expires_at.timestamp()),
        )
        token = jwt.encode(payload.model_dump(), self.secret_key, algorithm=self.algorithm)
        logger.debug("Access token created", user_id=user_id, expires_at=expires_at.isoformat())
        return token

    def create_refresh_token(self, user_id: str, email: str, tenant_id: str) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=self.refresh_token_expire_days)
        payload = TokenPayload(
            sub=user_id,
            email=email,
            tenant_id=tenant_id,
            roles=[],
            iat=int(now.timestamp()),
            exp=int(expires_at.timestamp()),
        )
        return jwt.encode(payload.model_dump(), self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[TokenPayload]:
        if token in self._blacklisted_tokens:
            logger.warning("Attempted use of blacklisted token")
            return None
        try:
            payload_dict = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return TokenPayload(**payload_dict)
        except jwt.PyJWTError as e:
            logger.warning("Token decoding failed", error=str(e))
            return None

    def blacklist_token(self, token: str) -> None:
        self._blacklisted_tokens.add(token)
        logger.info("Token blacklisted")
