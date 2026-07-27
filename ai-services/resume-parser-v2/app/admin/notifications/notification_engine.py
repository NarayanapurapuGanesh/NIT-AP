"""
Admin Notification Engine.
Manages Email Templates, System Notifications, and Admin Alerts.
"""

from typing import Dict, List, Optional
from core.logging import get_logger

logger = get_logger("notification_engine")


class NotificationEngine:
    """Enterprise Notification Engine."""

    def __init__(self) -> None:
        self._templates: Dict[str, str] = {
            "user_invitation": "Hello {{name}}, You have been invited to FacultyIQ as {{role}}. Click here to join: {{link}}",
            "password_reset": "Hello {{name}}, Click here to reset your password: {{link}}",
            "security_alert": "Alert: Suspicious login attempt detected on your account.",
        }

    def send_notification(self, recipient_email: str, template_name: str, params: Dict[str, str]) -> bool:
        template = self._templates.get(template_name)
        if not template:
            logger.warning("Notification template not found", template_name=template_name)
            return False

        message = template
        for k, v in params.items():
            message = message.replace(f"{{{{{k}}}}}", v)

        logger.info("Notification dispatched", recipient=recipient_email, template=template_name, body=message[:50])
        return True
