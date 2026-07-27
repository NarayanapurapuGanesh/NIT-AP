"""
Relationship Engine.
Establishes graph entity relationships between Candidate, Experience, Education, Skills, Projects, and Publications.
"""

from typing import List, Tuple
from app.information_extraction.schemas.candidate_profile import (
    EducationItem,
    ExperienceItem,
    KnowledgeGraphEdge,
    KnowledgeGraphNode,
    ProjectItem,
    PublicationItem,
    SkillCategory,
)
from core.logging import get_logger

logger = get_logger("relationship_engine")


class RelationshipEngine:
    """Relationship Builder Engine."""

    def build_relationships(
        self,
        candidate_node_id: str,
        experiences: List[ExperienceItem],
        education: List[EducationItem],
        skills: List[SkillCategory],
        projects: List[ProjectItem],
        publications: List[PublicationItem],
    ) -> Tuple[List[KnowledgeGraphNode], List[KnowledgeGraphEdge]]:
        nodes: List[KnowledgeGraphNode] = []
        edges: List[KnowledgeGraphEdge] = []

        # 1. Candidate Node
        nodes.append(
            KnowledgeGraphNode(node_id=candidate_node_id, entity_type="Candidate", name="Candidate Profile")
        )

        # 2. Experience Nodes & Edges
        for exp in experiences:
            if exp.organization.value:
                org_id = f"org_{exp.item_id[:8]}"
                nodes.append(
                    KnowledgeGraphNode(node_id=org_id, entity_type="Company", name=exp.organization.value)
                )
                edges.append(
                    KnowledgeGraphEdge(source_id=candidate_node_id, target_id=org_id, relation="WORKED_AT")
                )

        # 3. Education Nodes & Edges
        for edu in education:
            if edu.institution.value:
                univ_id = f"univ_{edu.item_id[:8]}"
                nodes.append(
                    KnowledgeGraphNode(node_id=univ_id, entity_type="University", name=edu.institution.value)
                )
                edges.append(
                    KnowledgeGraphEdge(source_id=candidate_node_id, target_id=univ_id, relation="STUDIED_AT")
                )

        # 4. Skill Nodes & Edges
        for cat in skills:
            for sk in cat.skills:
                if sk.value:
                    sk_id = f"sk_{sk.value.lower().replace(' ', '_')}"
                    nodes.append(
                        KnowledgeGraphNode(node_id=sk_id, entity_type="Skill", name=sk.value)
                    )
                    edges.append(
                        KnowledgeGraphEdge(source_id=candidate_node_id, target_id=sk_id, relation="HAS_SKILL")
                    )

        logger.debug("Relationship graph constructed", nodes_count=len(nodes), edges_count=len(edges))
        return nodes, edges
