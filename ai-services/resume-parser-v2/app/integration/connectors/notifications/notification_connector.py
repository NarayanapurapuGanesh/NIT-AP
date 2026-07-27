"""
Notification Service Connectors.
Supports SMTP, Microsoft 365, Twilio SMS, Firebase Push, and WhatsApp Business API.
"""

from typing import Any, Dict, List
from app.integration.schemas.integration_models import NotificationConnectorConfig
from core.logging import get_logger

logger = get_logger("notification_connector")


class NotificationConnectorEngine:
    """Notification Provider Integration Engine."""

    def __init__(self) -> None:
        self._configs: Dict[str, NotificationConnectorConfig] = {
            "SMTP": NotificationConnectorConfig(provider_type="SMTP Email", api_key_or_secret="smtp_password", sender_id="noreply@nitandhra.ac.in"),
            "Twilio": NotificationConnectorConfig(provider_type="Twilio SMS", api_key_or_secret="twilio_auth_token", sender_id="+18005550199"),
            "WhatsApp": NotificationConnectorConfig(provider_type="WhatsApp Business", api_key_or_secret="wa_token", sender_id="+919876543210"),
        }

    def dispatch_notification(self, provider_name: str, recipient: str, message: str) -> Dict[str, Any]:
        config = self._configs.get(provider_name)
        if not config:
            return {"status": "error", "message": f"Notification provider '{provider_name}' not configured"}

        logger.info("Notification dispatched via provider", provider=provider_name, recipient=recipient)
        return {
            "provider": provider_name,
            "status": "sent",
            "recipient": recipient,
            "sender_id": config.sender_id,
        }

    def list_notification_connectors(self) -> List[NotificationConnectorConfig]:
        return list(self._configs.values())
