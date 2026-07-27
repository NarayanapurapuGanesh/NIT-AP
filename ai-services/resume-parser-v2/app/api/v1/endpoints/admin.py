"""
Enterprise Administration Platform REST API Endpoints.
Auth, Users, Roles, Permissions, Multi-Tenancy, Organization Tree, Feature Flags, Settings, Audit & System Health.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Query, status
from app.admin.pipeline.admin_pipeline import AdminPipeline
from app.admin.schemas.admin_models import (
    AuditLogEntry,
    ConfigurationEntry,
    FeatureFlagRecord,
    LoginRequest,
    LoginResponse,
    OrganizationNode,
    PermissionDefinition,
    RoleDefinition,
    SecurityEvent,
    SystemHealthRecord,
    TenantRecord,
    UserAccount,
)
from app.admin.services.admin_service import AdminServiceRegistry
from schemas.base import BaseResponse

router = APIRouter()

admin_pipeline = AdminPipeline()
admin_registry = AdminServiceRegistry.get_instance()


# --- Auth Endpoints ---

@router.post(
    "/auth/login",
    response_model=BaseResponse[LoginResponse],
    summary="Authenticate User",
    description="Authenticates user credentials and returns JWT access + refresh tokens.",
)
async def login(request: LoginRequest, x_forwarded_for: Optional[str] = Header(None)) -> BaseResponse[LoginResponse]:
    try:
        res = admin_pipeline.login_user(request, ip_address=x_forwarded_for)
        return BaseResponse(success=True, message="Login successful.", data=res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post(
    "/auth/logout",
    response_model=BaseResponse[Dict[str, str]],
    summary="User Logout",
    description="Revokes current session access token.",
)
async def logout(authorization: Optional[str] = Header(None)) -> BaseResponse[Dict[str, str]]:
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        admin_registry.auth_engine.token_service.blacklist_token(token)
    return BaseResponse(success=True, message="Logged out successfully.", data={"status": "revoked"})


# --- User Endpoints ---

@router.post(
    "/users",
    response_model=BaseResponse[UserAccount],
    summary="Create User Account",
    description="Creates a new user account within a tenant.",
)
async def create_user(
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    roles: Optional[List[str]] = Query(None),
    tenant_id: str = "default_university",
) -> BaseResponse[UserAccount]:
    try:
        user = admin_pipeline.create_user_account(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            performed_by_user_id="admin_001",
            roles=roles,
            tenant_id=tenant_id,
        )
        return BaseResponse(success=True, message="User created successfully.", data=user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/users",
    response_model=BaseResponse[List[UserAccount]],
    summary="List Users",
    description="Returns all users for a given tenant.",
)
async def list_users(tenant_id: Optional[str] = Query("default_university")) -> BaseResponse[List[UserAccount]]:
    users = admin_registry.user_engine.list_users(tenant_id=tenant_id)
    return BaseResponse(success=True, message=f"Retrieved {len(users)} users.", data=users)


# --- Roles & Permissions Endpoints ---

@router.get(
    "/roles",
    response_model=BaseResponse[List[RoleDefinition]],
    summary="List Roles",
    description="Returns all system and custom role definitions.",
)
async def list_roles() -> BaseResponse[List[RoleDefinition]]:
    roles = admin_registry.rbac_engine.list_roles()
    return BaseResponse(success=True, message=f"Retrieved {len(roles)} roles.", data=roles)


@router.get(
    "/permissions",
    response_model=BaseResponse[List[PermissionDefinition]],
    summary="List Permissions",
    description="Returns all granular system permissions.",
)
async def list_permissions() -> BaseResponse[List[PermissionDefinition]]:
    perms = admin_registry.rbac_engine.list_permissions()
    return BaseResponse(success=True, message=f"Retrieved {len(perms)} permissions.", data=perms)


# --- Multi-Tenancy & Org Structure ---

@router.get(
    "/tenants",
    response_model=BaseResponse[List[TenantRecord]],
    summary="List Tenants",
    description="Returns all registered university tenants.",
)
async def list_tenants() -> BaseResponse[List[TenantRecord]]:
    tenants = admin_registry.tenant_engine.list_tenants()
    return BaseResponse(success=True, message=f"Retrieved {len(tenants)} tenants.", data=tenants)


@router.get(
    "/organizations/tree",
    response_model=BaseResponse[OrganizationNode],
    summary="Get Organization Tree",
    description="Returns full hierarchical tree (University -> Campus -> Department -> Units).",
)
async def get_org_tree(tenant_id: str = Query("default_university")) -> BaseResponse[OrganizationNode]:
    tree = admin_registry.org_engine.get_organization_tree(tenant_id)
    return BaseResponse(success=True, message="Organization tree retrieved.", data=tree)


# --- Configuration & Feature Flags ---

@router.post(
    "/settings",
    response_model=BaseResponse[ConfigurationEntry],
    summary="Update Setting",
    description="Updates or sets a global or tenant configuration parameter.",
)
async def set_setting(key: str, value: Any, scope: str = "global") -> BaseResponse[ConfigurationEntry]:
    entry = admin_registry.config_engine.set_setting(key=key, value=value, scope=scope)
    return BaseResponse(success=True, message=f"Setting '{key}' updated.", data=entry)


@router.get(
    "/settings",
    response_model=BaseResponse[List[ConfigurationEntry]],
    summary="Get All Settings",
    description="Returns all system configurations.",
)
async def list_settings() -> BaseResponse[List[ConfigurationEntry]]:
    settings_list = admin_registry.config_engine.list_settings()
    return BaseResponse(success=True, message=f"Retrieved {len(settings_list)} configuration entries.", data=settings_list)


@router.get(
    "/feature-flags",
    response_model=BaseResponse[List[FeatureFlagRecord]],
    summary="List Feature Flags",
    description="Returns all feature flags and per-tenant overrides.",
)
async def list_feature_flags() -> BaseResponse[List[FeatureFlagRecord]]:
    flags = admin_registry.feature_flag_engine.list_flags()
    return BaseResponse(success=True, message=f"Retrieved {len(flags)} feature flags.", data=flags)


# --- System & Audit Endpoints ---

@router.get(
    "/audit/logs",
    response_model=BaseResponse[List[AuditLogEntry]],
    summary="Query Audit Logs",
    description="Returns immutable audit trail logs.",
)
async def query_audit_logs() -> BaseResponse[List[AuditLogEntry]]:
    logs = admin_registry.audit_engine.query_logs()
    return BaseResponse(success=True, message=f"Retrieved {len(logs)} audit log entries.", data=logs)


@router.get(
    "/system/health",
    response_model=BaseResponse[SystemHealthRecord],
    summary="Get System Diagnostics",
    description="Returns real-time health and system diagnostic metrics.",
)
async def get_system_health() -> BaseResponse[SystemHealthRecord]:
    health = admin_registry.system_engine.get_system_health()
    return BaseResponse(success=True, message="System health OK.", data=health)
