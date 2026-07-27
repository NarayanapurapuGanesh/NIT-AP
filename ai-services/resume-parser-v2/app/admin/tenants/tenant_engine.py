"""
Multi-Tenant Architecture Engine.
Manages university tenants, tenant isolation, branding, and multi-tenant configurations.
"""

from typing import Dict, List, Optional
from app.admin.schemas.admin_models import TenantRecord
from core.logging import get_logger

logger = get_logger("tenant_engine")


class MultiTenantEngine:
    """Enterprise Multi-Tenant Engine."""

    def __init__(self) -> None:
        self._tenants: Dict[str, TenantRecord] = {}
        self._seed_default_tenant()

    def _seed_default_tenant(self) -> None:
        default_tenant = TenantRecord(
            tenant_id="default_university",
            name="NIT Andhra Pradesh",
            domain="nitandhra.ac.in",
            branding={"primary_color": "#1E3A8A", "logo_url": "/assets/nit_logo.png"},
            is_active=True,
        )
        self._tenants[default_tenant.tenant_id] = default_tenant

    def get_tenant(self, tenant_id: str) -> Optional[TenantRecord]:
        return self._tenants.get(tenant_id)

    def list_tenants(self) -> List[TenantRecord]:
        return list(self._tenants.values())

    def create_tenant(self, tenant: TenantRecord) -> TenantRecord:
        self._tenants[tenant.tenant_id] = tenant
        logger.info("Tenant created", tenant_id=tenant.tenant_id, name=tenant.name)
        return tenant

    def update_tenant_status(self, tenant_id: str, is_active: bool) -> Optional[TenantRecord]:
        tenant = self._tenants.get(tenant_id)
        if tenant:
            tenant.is_active = is_active
            logger.info("Tenant status updated", tenant_id=tenant_id, is_active=is_active)
        return tenant
