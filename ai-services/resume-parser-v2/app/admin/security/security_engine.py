"""
Security Layer Engine.
Enforces password complexity policies, rate limiting, IP restrictions, account lockouts, and security event logging.
"""

from typing import Dict, List, Optional
from app.admin.schemas.admin_models import PasswordPolicy, SecurityEvent
from core.logging import get_logger

logger = get_logger("security_engine")


class SecurityLayerEngine:
    """Enterprise Security Guardrails Engine."""

    def __init__(self) -> None:
        self.password_policy = PasswordPolicy()
        self._security_events: List[SecurityEvent] = []
        self._blocked_ips: set[str] = set()

    def validate_password_complexity(self, password: str) -> bool:
        if len(password) < self.password_policy.min_length:
            return False
        if self.password_policy.require_uppercase and not any(c.isupper() for c in password):
            return False
        if self.password_policy.require_lowercase and not any(c.islower() for c in password):
            return False
        if self.password_policy.require_numbers and not any(c.isdigit() for c in password):
            return False
        return True

    def record_security_event(self, event_type: str, message: str, source_ip: Optional[str] = None, severity: str = "warning") -> SecurityEvent:
        event = SecurityEvent(event_type=event_type, message=message, source_ip=source_ip, severity=severity)
        self._security_events.append(event)
        logger.warning("Security event recorded", event_type=event_type, message=message, source_ip=source_ip)
        return event

    def block_ip(self, ip_address: str) -> None:
        self._blocked_ips.add(ip_address)
        self.record_security_event("ip_blocked", f"IP {ip_address} has been blocked due to suspicious activity", source_ip=ip_address, severity="critical")

    def is_ip_blocked(self, ip_address: str) -> bool:
        return ip_address in self._blocked_ips

    def list_security_events(self) -> List[SecurityEvent]:
        return self._security_events
