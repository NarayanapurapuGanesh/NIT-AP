"""
Organization Management Engine.
Manages Campuses, Departments, Research Centers, Recruitment Committees, and Organization Hierarchy Tree.
"""

from typing import Dict, List, Optional
from app.admin.schemas.admin_models import CampusRecord, CommitteeRecord, DepartmentRecord, OrganizationNode
from core.logging import get_logger

logger = get_logger("organization_engine")


class OrganizationEngine:
    """Enterprise Organization Structure Engine."""

    def __init__(self) -> None:
        self._campuses: Dict[str, CampusRecord] = {}
        self._departments: Dict[str, DepartmentRecord] = {}
        self._committees: Dict[str, CommitteeRecord] = {}
        self._seed_default_org_structure()

    def _seed_default_org_structure(self) -> None:
        c1 = CampusRecord(campus_id="main_campus", tenant_id="default_university", name="Tadepalligudem Main Campus", location="Andhra Pradesh")
        self._campuses[c1.campus_id] = c1

        deps = [
            ("CSE", "Computer Science & Engineering"),
            ("ECE", "Electronics & Communication Engineering"),
            ("ME", "Mechanical Engineering"),
            ("CE", "Civil Engineering"),
            ("EEE", "Electrical & Electronics Engineering"),
        ]
        for code, name in deps:
            d = DepartmentRecord(department_id=code.lower(), tenant_id="default_university", campus_id="main_campus", name=name, code=code)
            self._departments[d.department_id] = d

        comm = CommitteeRecord(committee_id="cse_hiring_comm", tenant_id="default_university", department_id="cse", name="CSE Faculty Search Committee")
        self._committees[comm.committee_id] = comm

        logger.info("Seeded default organization structure")

    def get_organization_tree(self, tenant_id: str = "default_university") -> OrganizationNode:
        dept_nodes = [
            OrganizationNode(id=d.department_id, name=d.name, type="department")
            for d in self._departments.values()
            if d.tenant_id == tenant_id
        ]
        campus_nodes = [
            OrganizationNode(id=c.campus_id, name=c.name, type="campus", children=dept_nodes)
            for c in self._campuses.values()
            if c.tenant_id == tenant_id
        ]
        return OrganizationNode(id=tenant_id, name="NIT Andhra Pradesh", type="university", children=campus_nodes)

    def list_departments(self) -> List[DepartmentRecord]:
        return list(self._departments.values())

    def list_committees(self) -> List[CommitteeRecord]:
        return list(self._committees.values())
