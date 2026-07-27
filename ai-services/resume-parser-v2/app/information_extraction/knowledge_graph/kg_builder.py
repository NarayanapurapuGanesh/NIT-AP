"""
Candidate Knowledge Graph Builder Engine.
Assembles the complete Candidate Knowledge Graph linking Candidate, Skills, Companies, Universities, Projects, Publications, Certifications, and Awards.
"""

from typing import List
from app.information_extraction.relationship_engine.relationship_engine import RelationshipEngine
from app.information_extraction.schemas.candidate_profile import (
    CandidateKnowledgeGraph,
    EducationItem,
    ExperienceItem,
    ProjectItem,
    PublicationItem,
    SkillCategory,
)
from core.logging import get_logger

logger = get_logger("kg_builder")


class KnowledgeGraphBuilder:
    """Candidate Knowledge Graph Builder."""

    def __init__(self) -> None:
        self.relationship_engine = RelationshipEngine()

    def build_kg(
        self,
        doc_uuid: str,
        experiences: List[ExperienceItem],
        education: List[EducationItem],
        skills: List[SkillCategory],
        projects: List[ProjectItem],
        publications: List[PublicationItem],
    ) -> CandidateKnowledgeGraph:
        candidate_node_id = f"cand_{doc_uuid[:8]}"
        nodes, edges = self.relationship_engine.build_relationships(
            candidate_node_id=candidate_node_id,
            experiences=experiences,
            education=education,
            skills=skills,
            projects=projects,
            publications=publications,
        )

        kg = CandidateKnowledgeGraph(nodes=nodes, edges=edges)
        logger.debug("Candidate Knowledge Graph assembled", node_count=len(nodes), edge_count=len(edges))
        return kg
