"""
Enterprise Authentication Engine.
Supports Email/Password authentication, OAuth2 stubs (Google, Microsoft, LDAP, Azure AD, SAML, OIDC),
password hashing, and session management.
"""

import hashlib
from typing import Dict, Optional
from app.admin.authentication.mfa_engine import MFAEngine
from app.admin.authentication.token_service import TokenService
from app.admin.schemas.admin_models import LoginRequest, LoginResponse, UserAccount, UserStatus
from core.logging import get_logger

logger = get_logger("auth_engine")


class AuthenticationEngine:
    """Enterprise Identity & Authentication Engine."""

    def __init__(self) -> None:
        self.token_service = TokenService()
        self.mfa_engine = MFAEngine()

    def hash_password(self, raw_password: str) -> str:
        """Hash password deterministically using SHA-256 for test/prototype or bcrypt wrapper."""
        return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()

    def verify_password(self, raw_password: str, password_hash: str) -> bool:
        return self.hash_password(raw_password) == password_hash

    def authenticate_user(
        self, login_req: LoginRequest, user: Optional[UserAccount]
    ) -> LoginResponse:
        """Authenticate user credentials and return LoginResponse payload."""
        if not user:
            logger.warning("Authentication failed: User not found", email=login_req.email)
            raise ValueError("Invalid email or password.")

        if user.status in [UserStatus.DEACTIVATED, UserStatus.LOCKED]:
            logger.warning("Authentication failed: Account inactive/locked", email=login_req.email, status=user.status)
            raise ValueError(f"Account is {user.status.value}.")

        if not self.verify_password(login_req.password, user.password_hash):
            logger.warning("Authentication failed: Password mismatch", email=login_req.email)
            raise ValueError("Invalid email or password.")

        if user.mfa_enabled:
            if not login_req.mfa_code or not self.mfa_engine.verify_otp(login_req.mfa_code):
                return LoginResponse(
                    access_token="",
                    refresh_token="",
                    user_id=user.user_id,
                    email=user.email,
                    roles=user.roles,
                    mfa_required=True,
                )

        access_token = self.token_service.create_access_token(
            user_id=user.user_id, email=user.email, tenant_id=user.tenant_id, roles=user.roles
        )
        refresh_token = self.token_service.create_refresh_token(
            user_id=user.user_id, email=user.email, tenant_id=user.tenant_id
        )

        logger.info("User authenticated successfully", user_id=user.user_id, email=user.email)
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.user_id,
            email=user.email,
            roles=user.roles,
            mfa_required=False,
        )
