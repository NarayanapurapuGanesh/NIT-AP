"""
Admin Pipeline Orchestrator.
Orchestrates enterprise admin operations across Authentication, Authorization, User Management,
Tenant Management, Feature Flags, and Audit Logging.
"""

from typing import Any, Dict, List, Optional
from app.admin.schemas.admin_models import (
    AuditCategory,
    LoginRequest,
    LoginResponse,
    TenantRecord,
    UserAccount,
    UserProfile,
)
from app.admin.services.admin_service import AdminServiceRegistry
from core.logging import get_logger

logger = get_logger("admin_pipeline")


class AdminPipeline:
    """Enterprise Admin Operations Pipeline."""

    def __init__(self) -> None:
        self.registry = AdminServiceRegistry.get_instance()

    def login_user(self, request: LoginRequest, ip_address: Optional[str] = None) -> LoginResponse:
        if ip_address and self.registry.security_engine.is_ip_blocked(ip_address):
            raise ValueError("Access blocked due to security policy.")

        user = self.registry.user_engine.get_user_by_email(request.email)
        response = self.registry.auth_engine.authenticate_user(request, user)

        if not response.mfa_required:
            self.registry.audit_engine.record_log(
                category=AuditCategory.LOGIN,
                action="user_login_success",
                performed_by=user.user_id if user else "unknown",
                user_email=request.email,
                tenant_id=request.tenant_id,
                ip_address=ip_address,
            )

        return response

    def create_user_account(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        performed_by_user_id: str,
        roles: Optional[List[str]] = None,
        tenant_id: str = "default_university",
    ) -> UserAccount:
        if not self.registry.security_engine.validate_password_complexity(password):
            raise ValueError("Password does not meet complexity requirements.")

        profile = UserProfile(first_name=first_name, last_name=last_name)
        user = self.registry.user_engine.create_user(
            email=email, raw_password=password, profile=profile, tenant_id=tenant_id, roles=roles
        )

        self.registry.audit_engine.record_log(
            category=AuditCategory.USER_ACTIVITY,
            action="create_user",
            performed_by=performed_by_user_id,
            user_email=email,
            tenant_id=tenant_id,
            details={"created_user_id": user.user_id, "roles": roles},
        )

        return user
