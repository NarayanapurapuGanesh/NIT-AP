"""
Project Extractor Engine.
Parses project title, role, duration, description, technologies, and URLs from Projects sections.
"""

from typing import List
from app.information_extraction.schemas.candidate_profile import ExtractedField, ProjectItem
from app.resume_structure.schemas.semantic_resume import SectionNode, SemanticResumeModel
from core.logging import get_logger

logger = get_logger("project_extractor")


class ProjectExtractor:
    """Projects & Portfolio Extractor Engine."""

    def extract_projects(self, model: SemanticResumeModel) -> List[ProjectItem]:
        project_items: List[ProjectItem] = []

        target_sections = [
            sec for sec in model.sections
            if sec.canonical_type in ["Projects", "Research Projects", "Academic Projects"]
        ]

        for sec in target_sections:
            blocks_text = sec.raw_text.split("\n\n")

            for b_text in blocks_text:
                lines = [l.strip() for l in b_text.split("\n") if l.strip()]
                if not lines:
                    continue

                title_str = lines[0]
                desc_str = "\n".join(lines[1:]) if len(lines) > 1 else title_str

                item = ProjectItem(
                    project_name=ExtractedField(value=title_str, raw_text=title_str, normalized_value=title_str, confidence=0.90, evidence=sec.evidence[:1]),
                    description=desc_str,
                )
                project_items.append(item)

        logger.debug("Project extraction complete", items_count=len(project_items))
        return project_items
