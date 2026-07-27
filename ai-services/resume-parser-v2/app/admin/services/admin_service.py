"""
Admin Platform Repository & Service Registry.
Provides singleton access to all Enterprise Administration Platform engines.
"""

from typing import Optional
from app.admin.audit.audit_engine import AuditEngine
from app.admin.authentication.auth_engine import AuthenticationEngine
from app.admin.authorization.permission_engine import AuthorizationEngine
from app.admin.configuration.configuration_engine import ConfigurationEngine
from app.admin.feature_flags.feature_flag_engine import FeatureFlagEngine
from app.admin.notifications.notification_engine import NotificationEngine
from app.admin.organizations.organization_engine import OrganizationEngine
from app.admin.rbac.rbac_engine import RBACEngine
from app.admin.security.security_engine import SecurityLayerEngine
from app.admin.system.system_admin_engine import SystemAdminEngine
from app.admin.tenants.tenant_engine import MultiTenantEngine
from app.admin.users.user_engine import UserManagementEngine
from core.logging import get_logger

logger = get_logger("admin_service")


class AdminServiceRegistry:
    """Central Admin Service Registry Singleton."""

    _instance: Optional["AdminServiceRegistry"] = None

    def __init__(self) -> None:
        self.auth_engine = AuthenticationEngine()
        self.authz_engine = AuthorizationEngine()
        self.rbac_engine = self.authz_engine.rbac_engine
        self.abac_engine = self.authz_engine.abac_engine
        self.tenant_engine = MultiTenantEngine()
        self.org_engine = OrganizationEngine()
        self.user_engine = UserManagementEngine()
        self.feature_flag_engine = FeatureFlagEngine()
        self.config_engine = ConfigurationEngine()
        self.security_engine = SecurityLayerEngine()
        self.audit_engine = AuditEngine()
        self.system_engine = SystemAdminEngine()
        self.notification_engine = NotificationEngine()

    @classmethod
    def get_instance(cls) -> "AdminServiceRegistry":
        if cls._instance is None:
            cls._instance = AdminServiceRegistry()
        return cls._instance
