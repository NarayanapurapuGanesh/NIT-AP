"""
Institutional Knowledge RAG Engine.
Retrieves evidence-linked academic hiring policies, minimum faculty qualifications, and department regulations.
"""

from typing import List
from core.logging import get_logger

logger = get_logger("policy_rag")

INSTITUTIONAL_POLICIES = [
    "NIT AP Policy 101: Assistant Professor applicants require Ph.D. with minimum 3 years post-Ph.D. research/teaching experience.",
    "NIT AP Policy 102: Minimum 3 peer-reviewed SCI/Scopus journal publications required for senior academic grade consideration.",
    "NIT AP Policy 103: Teaching load requires candidates to demonstrate expertise in core Computer Science fundamentals.",
]


class InstitutionalKnowledgeRAG:
    """RAG Policy Retrieval Engine."""

    def retrieve_context(self, department_name: str) -> str:
        relevant_policies = INSTITUTIONAL_POLICIES
        context_str = "\n".join([f"- {p}" for p in relevant_policies])
        logger.debug("Retrieved RAG policy context", department=department_name)
        return context_str
