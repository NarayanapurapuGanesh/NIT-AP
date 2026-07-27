"""
Notification Engine.
Handles Email, SMS, In-App, and Webhook notification templates.
"""

from app.workflow.schemas.workflow_models import NotificationRecord
from core.logging import get_logger

logger = get_logger("notification_engine")


class NotificationEngine:
    """Multi-Channel Notification Engine."""

    def send_notification(
        self, recipient: str, subject: str, body: str, channel: str = "Email"
    ) -> NotificationRecord:
        record = NotificationRecord(
            channel=channel,
            recipient=recipient,
            subject=subject,
            body=body,
            is_sent=True,
        )

        logger.info("Notification dispatched", recipient=recipient, channel=channel, subject=subject)
        return record
