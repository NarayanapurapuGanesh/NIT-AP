"""
Unified Authorization & Permission Engine.
Combines RBAC (role resolution) and ABAC (attribute checking) into a single decision authority.
"""

from typing import Any, Dict, List, Optional
from app.admin.abac.abac_engine import ABACEngine
from app.admin.rbac.rbac_engine import RBACEngine
from app.admin.schemas.admin_models import UserAccount
from core.logging import get_logger

logger = get_logger("permission_engine")


class AuthorizationEngine:
    """Unified RBAC + ABAC Authorization Engine."""

    def __init__(self) -> None:
        self.rbac_engine = RBACEngine()
        self.abac_engine = ABACEngine()

    def is_authorized(
        self,
        user: UserAccount,
        required_permission: str,
        resource_attrs: Optional[Dict[str, Any]] = None,
        action: str = "read",
    ) -> bool:
        """Determines if a user is authorized using RBAC and ABAC checks."""
        # 1. RBAC Check
        if not self.rbac_engine.has_permission(user.roles, required_permission):
            logger.warning(
                "Authorization denied by RBAC",
                user_id=user.user_id,
                required_permission=required_permission,
            )
            return False

        # 2. ABAC Check (if resource attributes provided)
        if resource_attrs:
            subject_attrs = {
                "user_id": user.user_id,
                "tenant_id": user.tenant_id,
                "department_id": user.profile.department_id,
                "roles": user.roles,
            }
            if not self.abac_engine.evaluate(subject_attrs, resource_attrs, action):
                logger.warning(
                    "Authorization denied by ABAC policy",
                    user_id=user.user_id,
                    action=action,
                )
                return False

        logger.debug(
            "Authorization granted",
            user_id=user.user_id,
            permission=required_permission,
        )
        return True
