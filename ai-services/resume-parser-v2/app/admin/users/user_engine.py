"""
User Management Engine.
Handles User Accounts, Invitations, Activation, Deactivation, Password Reset, and Bulk Import.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import uuid
from app.admin.authentication.auth_engine import AuthenticationEngine
from app.admin.schemas.admin_models import DefaultRole, UserAccount, UserInvitation, UserProfile, UserStatus
from core.logging import get_logger

logger = get_logger("user_engine")


class UserManagementEngine:
    """Enterprise User Management Engine."""

    def __init__(self) -> None:
        self.auth_engine = AuthenticationEngine()
        self._users: Dict[str, UserAccount] = {}
        self._invitations: Dict[str, UserInvitation] = {}
        self._seed_default_users()

    def _seed_default_users(self) -> None:
        admin_user = UserAccount(
            user_id="admin_001",
            email="admin@nitandhra.ac.in",
            password_hash=self.auth_engine.hash_password("Admin@123456"),
            tenant_id="default_university",
            status=UserStatus.ACTIVE,
            profile=UserProfile(first_name="Platform", last_name="Administrator", designation="System Administrator", department_id="cse"),
            roles=[DefaultRole.SUPER_ADMIN.value],
        )
        self._users[admin_user.user_id] = admin_user
        logger.info("Seeded super admin user", email=admin_user.email)

    def get_user_by_id(self, user_id: str) -> Optional[UserAccount]:
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[UserAccount]:
        for u in self._users.values():
            if u.email == email:
                return u
        return None

    def list_users(self, tenant_id: Optional[str] = None) -> List[UserAccount]:
        if tenant_id:
            return [u for u in self._users.values() if u.tenant_id == tenant_id]
        return list(self._users.values())

    def create_user(
        self,
        email: str,
        raw_password: str,
        profile: UserProfile,
        tenant_id: str = "default_university",
        roles: Optional[List[str]] = None,
    ) -> UserAccount:
        if self.get_user_by_email(email):
            raise ValueError(f"User with email '{email}' already exists.")

        user = UserAccount(
            email=email,
            password_hash=self.auth_engine.hash_password(raw_password),
            tenant_id=tenant_id,
            status=UserStatus.ACTIVE,
            profile=profile,
            roles=roles or [DefaultRole.FACULTY_REVIEWER.value],
        )
        self._users[user.user_id] = user
        logger.info("User created", user_id=user.user_id, email=email)
        return user

    def update_user_status(self, user_id: str, status: UserStatus) -> Optional[UserAccount]:
        user = self._users.get(user_id)
        if user:
            user.status = status
            logger.info("User status updated", user_id=user_id, status=status)
        return user

    def create_invitation(self, email: str, roles: List[str], invited_by: str, tenant_id: str = "default_university") -> UserInvitation:
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        invite = UserInvitation(
            email=email, tenant_id=tenant_id, assigned_roles=roles, invited_by=invited_by, expires_at=expires_at
        )
        self._invitations[invite.invitation_id] = invite
        logger.info("User invitation created", invitation_id=invite.invitation_id, email=email)
        return invite
