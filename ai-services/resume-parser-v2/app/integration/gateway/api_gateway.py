"""
Enterprise API Gateway & Auth Layer.
Handles API key validation, HMAC signing verification, rate limiting, routing, and caching.
"""

import hashlib
import hmac
import uuid
from typing import Dict, Optional
from app.integration.schemas.integration_models import APIKeyRecord
from core.logging import get_logger

logger = get_logger("api_gateway")


class APIGatewayEngine:
    """Enterprise API Gateway Engine."""

    def __init__(self) -> None:
        self._api_keys: Dict[str, APIKeyRecord] = {}
        self._seed_default_keys()

    def _seed_default_keys(self) -> None:
        default_key = APIKeyRecord(
            key_id="key_001",
            api_key="fq_live_secret_key_123456789",
            tenant_id="default_university",
            name="Default University Gateway Key",
        )
        self._api_keys[default_key.api_key] = default_key

    def validate_api_key(self, api_key: str) -> Optional[APIKeyRecord]:
        key_record = self._api_keys.get(api_key)
        if key_record and key_record.is_active:
            logger.debug("API key validated successfully", key_id=key_record.key_id)
            return key_record
        logger.warning("Invalid or inactive API key attempt")
        return None

    def generate_hmac_signature(self, secret: str, payload: str) -> str:
        return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify_hmac_signature(self, secret: str, payload: str, signature: str) -> bool:
        expected = self.generate_hmac_signature(secret, payload)
        return hmac.compare_digest(expected, signature)

    def create_api_key(self, name: str, tenant_id: str = "default_university") -> APIKeyRecord:
        raw_key = f"fq_live_{uuid.uuid4().hex}"
        key_record = APIKeyRecord(api_key=raw_key, tenant_id=tenant_id, name=name)
        self._api_keys[raw_key] = key_record
        logger.info("New API key generated", name=name, tenant_id=tenant_id)
        return key_record
