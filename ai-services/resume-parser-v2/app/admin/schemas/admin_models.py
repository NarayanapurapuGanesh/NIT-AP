"""
Canonical Pydantic v2 Models for Enterprise Administration Platform.
Identity, Authentication, Authorization, RBAC, ABAC, Multi-Tenancy,
Organizations, User Management, Feature Flags, Configuration, Security & Audit.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Enums ---

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"
    LOCKED = "locked"
    DEACTIVATED = "deactivated"


class DefaultRole(str, Enum):
    SUPER_ADMIN = "Super Admin"
    PLATFORM_ADMIN = "Platform Admin"
    UNIVERSITY_ADMIN = "University Admin"
    HR_ADMIN = "HR Admin"
    DEAN = "Dean"
    DEPARTMENT_HEAD = "Department Head"
    RECRUITMENT_COMMITTEE = "Recruitment Committee"
    FACULTY_REVIEWER = "Faculty Reviewer"
    INTERVIEWER = "Interviewer"
    OBSERVER = "Observer"
    CANDIDATE = "Candidate"
    GUEST = "Guest"


class FeatureCategory(str, Enum):
    AI_FEATURES = "ai_features"
    INTERVIEW_FEATURES = "interview_features"
    ANALYTICS_FEATURES = "analytics_features"
    PLUGINS = "plugins"
    EXPERIMENTAL = "experimental"


class AuditCategory(str, Enum):
    LOGIN = "login"
    PERMISSION_CHANGE = "permission_change"
    CONFIG_CHANGE = "config_change"
    WORKFLOW_OVERRIDE = "workflow_override"
    SECURITY_EVENT = "security_event"
    USER_ACTIVITY = "user_activity"


# --- Identity & Auth Schemas ---

class TokenPayload(BaseModel):
    sub: str  # user_id
    email: str
    tenant_id: str
    roles: List[str] = Field(default_factory=list)
    exp: int
    iat: int
    jti: str = Field(default_factory=lambda: str(uuid.uuid4()))


class LoginRequest(BaseModel):
    email: str
    password: str
    tenant_id: str = "default_university"
    mfa_code: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user_id: str
    email: str
    roles: List[str]
    mfa_required: bool = False


class MFASetup(BaseModel):
    user_id: str
    secret: str
    qr_code_url: str
    backup_codes: List[str] = Field(default_factory=list)
    is_enabled: bool = False


class UserProfile(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[str] = None
    avatar_url: Optional[str] = None


class UserAccount(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    tenant_id: str = "default_university"
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    profile: UserProfile
    roles: List[str] = Field(default_factory=lambda: [DefaultRole.FACULTY_REVIEWER.value])
    mfa_enabled: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0


class UserInvitation(BaseModel):
    invitation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    tenant_id: str
    assigned_roles: List[str]
    invited_by: str
    token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    expires_at: datetime
    accepted: bool = False


# --- Authorization (RBAC / ABAC) ---

class PermissionDefinition(BaseModel):
    permission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    resource: str
    action: str  # create, read, update, delete, execute, approve
    scope: str = "global"  # global, tenant, department
    description: str = ""


class RoleDefinition(BaseModel):
    role_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    is_system_role: bool = False
    permissions: List[str] = Field(default_factory=list)  # list of permission names or IDs
    inherited_roles: List[str] = Field(default_factory=list)


class ABACPolicy(BaseModel):
    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    resource: str
    action: str
    effect: str = "allow"  # allow or deny
    conditions: Dict[str, Any] = Field(default_factory=dict)  # e.g., {"department_id": "$user.department_id"}


# --- Multi-Tenancy & Org Management ---

class TenantRecord(BaseModel):
    tenant_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  # e.g. NIT Andhra Pradesh
    domain: str
    branding: Dict[str, str] = Field(default_factory=lambda: {"primary_color": "#1E3A8A", "logo_url": ""})
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CampusRecord(BaseModel):
    campus_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    location: str


class DepartmentRecord(BaseModel):
    department_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    campus_id: Optional[str] = None
    name: str  # e.g. Computer Science & Engineering
    code: str  # e.g. CSE
    head_user_id: Optional[str] = None


class CommitteeRecord(BaseModel):
    committee_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    department_id: str
    name: str
    member_user_ids: List[str] = Field(default_factory=list)
    chair_user_id: Optional[str] = None


class OrganizationNode(BaseModel):
    id: str
    name: str
    type: str  # university, campus, department, unit
    children: List["OrganizationNode"] = Field(default_factory=list)


# --- Configuration & Feature Flags ---

class FeatureFlagRecord(BaseModel):
    flag_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: FeatureCategory
    description: str = ""
    is_enabled_globally: bool = False
    tenant_overrides: Dict[str, bool] = Field(default_factory=dict)


class ConfigurationEntry(BaseModel):
    config_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str
    value: Any
    scope: str = "global"  # global, tenant, department
    target_id: Optional[str] = None  # tenant_id or department_id if scope is scoped
    updated_by: str = "system"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- Security & Audit ---

class PasswordPolicy(BaseModel):
    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_char: bool = True
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30


class AuditLogEntry(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: AuditCategory
    action: str
    performed_by: str
    user_email: str
    tenant_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str  # brute_force, unauthorized_access, ip_blocked
    severity: str = "warning"  # info, warning, critical
    message: str
    source_ip: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SystemHealthRecord(BaseModel):
    status: str = "healthy"
    version: str = "2.0.0"
    active_workers: int = 4
    queue_backlog: int = 0
    storage_used_gb: float = 12.4
    cache_hit_ratio: float = 98.2
    active_sessions: int = 42
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
