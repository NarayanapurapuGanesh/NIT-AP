"""
Role-Based Access Control (RBAC) Engine.
Manages dynamic roles, permission inheritance, custom permissions, and role-permission resolution.
Supports 12 default seeded roles without hardcoding permissions.
"""

from typing import Dict, List, Optional, Set
from app.admin.schemas.admin_models import DefaultRole, PermissionDefinition, RoleDefinition
from core.logging import get_logger

logger = get_logger("rbac_engine")


class RBACEngine:
    """Enterprise RBAC Engine."""

    def __init__(self) -> None:
        self._roles: Dict[str, RoleDefinition] = {}
        self._permissions: Dict[str, PermissionDefinition] = {}
        self._seed_default_permissions_and_roles()

    def _seed_default_permissions_and_roles(self) -> None:
        """Seed all granular system permissions and default roles."""
        perms = [
            ("users:read", "users", "read", "global", "Read user accounts"),
            ("users:write", "users", "write", "global", "Manage user accounts"),
            ("roles:read", "roles", "read", "global", "Read role definitions"),
            ("roles:write", "roles", "write", "global", "Manage role definitions"),
            ("tenants:read", "tenants", "read", "global", "Read tenants"),
            ("tenants:write", "tenants", "write", "global", "Manage tenants"),
            ("resumes:read", "resumes", "read", "tenant", "Read candidate resumes"),
            ("resumes:write", "resumes", "write", "tenant", "Upload and parse resumes"),
            ("matching:execute", "matching", "execute", "tenant", "Run candidate job matching"),
            ("workflow:approve", "workflow", "approve", "department", "Approve recruitment workflow state"),
            ("interview:conduct", "interview", "conduct", "department", "Conduct candidate interviews"),
            ("analytics:view", "analytics", "view", "tenant", "View recruitment analytics"),
            ("settings:manage", "settings", "manage", "tenant", "Manage system settings"),
        ]

        for p_id, res, act, scp, desc in perms:
            p = PermissionDefinition(name=p_id, resource=res, action=act, scope=scp, description=desc)
            self._permissions[p_id] = p

        default_roles = [
            (DefaultRole.SUPER_ADMIN.value, "Super Admin with full platform permissions", list(self._permissions.keys())),
            (DefaultRole.PLATFORM_ADMIN.value, "Platform Administrator", ["users:read", "users:write", "roles:read", "roles:write", "tenants:read", "settings:manage"]),
            (DefaultRole.UNIVERSITY_ADMIN.value, "University Admin", ["users:read", "users:write", "resumes:read", "resumes:write", "matching:execute", "analytics:view", "settings:manage"]),
            (DefaultRole.HR_ADMIN.value, "HR Administrator", ["users:read", "resumes:read", "resumes:write", "matching:execute", "workflow:approve", "analytics:view"]),
            (DefaultRole.DEAN.value, "Faculty Dean", ["resumes:read", "matching:execute", "workflow:approve", "analytics:view"]),
            (DefaultRole.DEPARTMENT_HEAD.value, "Department Head", ["resumes:read", "matching:execute", "workflow:approve", "interview:conduct", "analytics:view"]),
            (DefaultRole.RECRUITMENT_COMMITTEE.value, "Recruitment Committee Member", ["resumes:read", "matching:execute", "workflow:approve", "interview:conduct"]),
            (DefaultRole.FACULTY_REVIEWER.value, "Faculty Reviewer", ["resumes:read", "interview:conduct"]),
            (DefaultRole.INTERVIEWER.value, "Interviewer", ["resumes:read", "interview:conduct"]),
            (DefaultRole.OBSERVER.value, "Observer", ["resumes:read"]),
            (DefaultRole.CANDIDATE.value, "Candidate", ["resumes:read"]),
            (DefaultRole.GUEST.value, "Guest", []),
        ]

        for role_name, desc, role_perms in default_roles:
            role = RoleDefinition(name=role_name, description=desc, is_system_role=True, permissions=role_perms)
            self._roles[role_name] = role

        logger.info("Seeded default RBAC roles and permissions", role_count=len(self._roles), perm_count=len(self._permissions))

    def get_role(self, role_name: str) -> Optional[RoleDefinition]:
        return self._roles.get(role_name)

    def list_roles(self) -> List[RoleDefinition]:
        return list(self._roles.values())

    def list_permissions(self) -> List[PermissionDefinition]:
        return list(self._permissions.values())

    def create_role(self, role_def: RoleDefinition) -> RoleDefinition:
        self._roles[role_def.name] = role_def
        logger.info("Custom role created", role_name=role_def.name)
        return role_def

    def resolve_user_permissions(self, roles: List[str]) -> Set[str]:
        """Resolves all permissions granted across a user's assigned roles, including role inheritance."""
        resolved: Set[str] = set()
        for role_name in roles:
            role = self._roles.get(role_name)
            if role:
                resolved.update(role.permissions)
                for inherited in role.inherited_roles:
                    inherited_role = self._roles.get(inherited)
                    if inherited_role:
                        resolved.update(inherited_role.permissions)
        return resolved

    def has_permission(self, roles: List[str], required_permission: str) -> bool:
        if DefaultRole.SUPER_ADMIN.value in roles:
            return True
        user_perms = self.resolve_user_permissions(roles)
        return required_permission in user_perms
