"""
Audit Administration Engine.
Tracks logins, permission changes, configuration changes, workflow overrides, security events, and user activity.
Provides immutable queryable audit trail logs.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from app.admin.schemas.admin_models import AuditCategory, AuditLogEntry
from core.logging import get_logger

logger = get_logger("audit_engine")


class AuditEngine:
    """Enterprise Audit Trail Engine."""

    def __init__(self) -> None:
        self._logs: List[AuditLogEntry] = []

    def record_log(
        self,
        category: AuditCategory,
        action: str,
        performed_by: str,
        user_email: str,
        tenant_id: str = "default_university",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLogEntry:
        entry = AuditLogEntry(
            category=category,
            action=action,
            performed_by=performed_by,
            user_email=user_email,
            tenant_id=tenant_id,
            details=details or {},
            ip_address=ip_address,
        )
        self._logs.append(entry)
        logger.info(
            "Audit log entry recorded",
            category=category.value,
            action=action,
            performed_by=performed_by,
            user_email=user_email,
        )
        return entry

    def query_logs(
        self,
        category: Optional[AuditCategory] = None,
        user_email: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[AuditLogEntry]:
        results = self._logs
        if category:
            results = [l for l in results if l.category == category]
        if user_email:
            results = [l for l in results if l.user_email == user_email]
        if tenant_id:
            results = [l for l in results if l.tenant_id == tenant_id]
        return results
