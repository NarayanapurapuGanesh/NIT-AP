"""
Pytest integration & unit tests for Phase 14 Enterprise Administration Platform.
Authentication, Authorization (RBAC & ABAC), Multi-Tenancy, User Management,
Feature Flags, Settings, Audit Logging & REST API Endpoints.
"""

import pytest
from httpx import AsyncClient
from app.admin.pipeline.admin_pipeline import AdminPipeline
from app.admin.schemas.admin_models import LoginRequest, UserProfile, UserStatus
from app.admin.services.admin_service import AdminServiceRegistry


@pytest.fixture
def admin_pipeline():
    return AdminPipeline()


@pytest.fixture
def admin_registry():
    return AdminServiceRegistry.get_instance()


@pytest.mark.anyio
async def test_admin_authentication_flow(admin_pipeline: AdminPipeline):
    # Test valid login with super admin
    req = LoginRequest(email="admin@nitandhra.ac.in", password="Admin@123456", tenant_id="default_university")
    res = admin_pipeline.login_user(req)

    assert res.access_token != ""
    assert res.user_id == "admin_001"
    assert "Super Admin" in res.roles
    assert res.mfa_required is False


@pytest.mark.anyio
async def test_admin_invalid_login(admin_pipeline: AdminPipeline):
    req = LoginRequest(email="admin@nitandhra.ac.in", password="WrongPassword", tenant_id="default_university")
    with pytest.raises(ValueError, match="Invalid email or password"):
        admin_pipeline.login_user(req)


@pytest.mark.anyio
async def test_rbac_permission_resolution(admin_registry: AdminServiceRegistry):
    # Super Admin has all perms
    has_perm = admin_registry.rbac_engine.has_permission(["Super Admin"], "settings:manage")
    assert has_perm is True

    # Observer does not have write perms
    has_write = admin_registry.rbac_engine.has_permission(["Observer"], "users:write")
    assert has_write is False


@pytest.mark.anyio
async def test_abac_policy_evaluation(admin_registry: AdminServiceRegistry):
    subject_attrs = {"department_id": "cse"}
    resource_attrs = {"department_id": "cse"}
    allowed = admin_registry.abac_engine.evaluate(subject_attrs, resource_attrs, action="read")
    assert allowed is True


@pytest.mark.anyio
async def test_user_creation_and_audit_logging(admin_pipeline: AdminPipeline, admin_registry: AdminServiceRegistry):
    user = admin_pipeline.create_user_account(
        email="test_faculty@nitandhra.ac.in",
        password="Password@1234",
        first_name="Test",
        last_name="Faculty",
        performed_by_user_id="admin_001",
        roles=["Faculty Reviewer"],
    )

    assert user.email == "test_faculty@nitandhra.ac.in"
    assert user.status == UserStatus.ACTIVE

    # Check audit log
    logs = admin_registry.audit_engine.query_logs(user_email="test_faculty@nitandhra.ac.in")
    assert len(logs) > 0
    assert logs[0].action == "create_user"


@pytest.mark.anyio
async def test_feature_flag_evaluation(admin_registry: AdminServiceRegistry):
    is_enabled = admin_registry.feature_flag_engine.is_enabled("ollama_llm_agent")
    assert is_enabled is True

    # Toggle flag
    admin_registry.feature_flag_engine.toggle_flag("ollama_llm_agent", is_enabled=False)
    assert admin_registry.feature_flag_engine.is_enabled("ollama_llm_agent") is False

    # Restore
    admin_registry.feature_flag_engine.toggle_flag("ollama_llm_agent", is_enabled=True)


@pytest.mark.anyio
async def test_admin_api_login(async_client: AsyncClient):
    payload = {"email": "admin@nitandhra.ac.in", "password": "Admin@123456", "tenant_id": "default_university"}
    res = await async_client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["access_token"] != ""


@pytest.mark.anyio
async def test_admin_api_list_roles(async_client: AsyncClient):
    res = await async_client.get("/api/v1/roles")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["data"]) == 12


@pytest.mark.anyio
async def test_admin_api_org_tree(async_client: AsyncClient):
    res = await async_client.get("/api/v1/organizations/tree")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["type"] == "university"
    assert len(data["data"]["children"]) > 0


@pytest.mark.anyio
async def test_admin_api_system_health(async_client: AsyncClient):
    res = await async_client.get("/api/v1/system/health")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
