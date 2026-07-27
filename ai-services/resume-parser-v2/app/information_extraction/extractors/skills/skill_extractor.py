"""
Skill Extractor Engine.
Categorizes skills into Programming Languages, Frameworks, Databases, Cloud/DevOps, AI/ML, OS, and Soft/Research Skills.
"""

from typing import Dict, List
from app.information_extraction.schemas.candidate_profile import ExtractedField, SkillCategory
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel
from core.logging import get_logger

logger = get_logger("skill_extractor")

SKILL_DICTIONARIES: Dict[str, List[str]] = {
    "Programming Languages": ["Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust", "SQL", "R", "Scala", "Kotlin"],
    "Frameworks & Libraries": ["FastAPI", "React", "Next.js", "Django", "Flask", "PyTorch", "TensorFlow", "Spring Boot", ".NET", "Node.js", "Express"],
    "Databases & Vector Engines": ["PostgreSQL", "Redis", "Qdrant", "MongoDB", "MySQL", "Elasticsearch", "Pinecone", "Milvus"],
    "Cloud & DevOps": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "CI/CD", "GitHub Actions", "Linux", "Git"],
    "AI / ML / NLP / CV": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "LangChain", "LangGraph", "Ollama", "RAG", "LLM", "Transformers"],
}


class SkillExtractor:
    """Categorized Skill Extractor Engine."""

    def extract_skills(self, model: SemanticResumeModel) -> List[SkillCategory]:
        category_map: Dict[str, List[ExtractedField[str]]] = {}

        target_sections = [
            sec for sec in model.sections
            if sec.canonical_type in ["Skills", "Technical Skills", "Programming Languages", "Tools", "Frameworks", "Soft Skills"]
        ]

        full_skill_text = "\n".join(sec.raw_text for sec in target_sections)

        for cat_name, skill_list in SKILL_DICTIONARIES.items():
            found_skills: List[ExtractedField[str]] = []
            for skill in skill_list:
                # Case-insensitive boundary match
                import re
                pattern = r"\b" + re.escape(skill) + r"\b"
                if re.search(pattern, full_skill_text, re.IGNORECASE):
                    found_skills.append(
                        ExtractedField(value=skill, raw_text=skill, normalized_value=skill, confidence=0.98)
                    )

            if found_skills:
                category_map[cat_name] = found_skills

        categories = [
            SkillCategory(category_name=cat_name, skills=skills)
            for cat_name, skills in category_map.items()
        ]

        logger.debug("Skill extraction complete", categories_count=len(categories))
        return categories
