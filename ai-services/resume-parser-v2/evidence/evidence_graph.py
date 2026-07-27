"""
Evidence Engine Module (Module 13) — v3.0.

Tracks precise source lineage for every extracted value:
- Page Number
- Bounding Box [x0, y0, x1, y1]
- Exact Sentence / Snippet
- Section Header (v3.0: from detected section segmentation)
- Source Channel (DETERMINISTIC, LLM_CALLBACK, OCR)
- Field Confidence Score

v3.0 additions:
- Evidence nodes for: profile_summary, soft_skills, address, candidate_type, categorized_awards
- Section heading source tracking from layout segmentation
"""

from typing import List, Optional
from schemas.enterprise_profile import EvidencePackageGraph, FieldEvidenceItem
from extractors.deterministic_extractor import DeterministicEntities
from layout.layout_analyzer import StructuralAnalysisResult


class EvidenceEngine:
    """Builds audit evidence graph lineage for explainability and auditability."""

    def build_evidence_graph(
        self,
        entities: DeterministicEntities,
        layout: StructuralAnalysisResult,
        raw_text: str = ""
    ) -> EvidencePackageGraph:
        nodes: List[FieldEvidenceItem] = []

        # Build a section lookup for enhanced evidence tracking
        section_lookup = {}
        for sec in layout.sections:
            for line in sec.content_lines:
                section_lookup[line.lower()[:50]] = sec.section_name

        # Helper to locate block bounding box and section for a text snippet
        def find_bbox(term: str) -> tuple[int, list[float], str]:
            if not term:
                return 1, [0.0, 0.0, 0.0, 0.0], "Header"
            term_lower = term.lower()
            for block in layout.blocks:
                if term_lower in block.text.lower():
                    # Try to find section from section lookup
                    section = section_lookup.get(term_lower[:50], block.block_type.capitalize())
                    return block.page_number, block.bbox, section
            return 1, [0.0, 0.0, 0.0, 0.0], "General"

        # Track Name
        if entities.name:
            p, bbox, section = find_bbox(entities.name)
            nodes.append(
                FieldEvidenceItem(
                    field_name="candidate.name",
                    extracted_value=entities.name,
                    page_number=p,
                    section_header=section,
                    sentence_snippet=entities.name,
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=0.99,
                )
            )

        # Track Email
        if entities.email:
            p, bbox, section = find_bbox(entities.email)
            nodes.append(
                FieldEvidenceItem(
                    field_name="candidate.email",
                    extracted_value=entities.email,
                    page_number=p,
                    section_header=section,
                    sentence_snippet=entities.email,
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=1.0,
                )
            )

        # Track Phone
        if entities.phone:
            p, bbox, section = find_bbox(entities.phone)
            nodes.append(
                FieldEvidenceItem(
                    field_name="candidate.phone",
                    extracted_value=entities.phone,
                    page_number=p,
                    section_header=section,
                    sentence_snippet=entities.phone,
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=1.0,
                )
            )

        # v3.0: Track Address
        if entities.address:
            p, bbox, section = find_bbox(entities.address)
            nodes.append(
                FieldEvidenceItem(
                    field_name="candidate.address",
                    extracted_value=entities.address,
                    page_number=p,
                    section_header=section,
                    sentence_snippet=entities.address,
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=0.90,
                )
            )

        # v3.0: Track Profile Summary
        if entities.profile_summary:
            p, bbox, section = find_bbox(entities.profile_summary[:40])
            nodes.append(
                FieldEvidenceItem(
                    field_name="candidate.profile_summary",
                    extracted_value=entities.profile_summary[:100] + ("..." if len(entities.profile_summary) > 100 else ""),
                    page_number=p,
                    section_header="PROFILE",
                    sentence_snippet=entities.profile_summary[:80],
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=0.95,
                )
            )

        # v3.0: Track Candidate Type
        if entities.candidate_type and entities.candidate_type != "Unknown":
            nodes.append(
                FieldEvidenceItem(
                    field_name="candidate.candidate_type",
                    extracted_value=entities.candidate_type,
                    page_number=1,
                    section_header="Inferred",
                    sentence_snippet=f"Classified as {entities.candidate_type} based on experience/education analysis",
                    bounding_box=[0.0, 0.0, 0.0, 0.0],
                    extraction_source="DETERMINISTIC",
                    confidence=0.92,
                )
            )

        # Track Skills
        for skill in entities.skills[:10]:
            p, bbox, section = find_bbox(skill)
            nodes.append(
                FieldEvidenceItem(
                    field_name="skills",
                    extracted_value=skill,
                    page_number=p,
                    section_header=section if section != "Text" else "SKILLS",
                    sentence_snippet=skill,
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=0.95,
                )
            )

        # v3.0: Track Soft Skills
        for skill in entities.soft_skills[:8]:
            p, bbox, section = find_bbox(skill)
            nodes.append(
                FieldEvidenceItem(
                    field_name="soft_skills",
                    extracted_value=skill,
                    page_number=p,
                    section_header=section if section != "Text" else "SOFT_SKILLS",
                    sentence_snippet=skill,
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=0.93,
                )
            )

        # Track Education
        for edu in entities.education:
            p, bbox, section = find_bbox(edu.degree)
            nodes.append(
                FieldEvidenceItem(
                    field_name="education.degree",
                    extracted_value=f"{edu.degree} - {edu.institution}",
                    page_number=p,
                    section_header=section if section != "Text" else "EDUCATION",
                    sentence_snippet=f"{edu.degree} {edu.institution} ({edu.year or ''}) {edu.gpa or ''}".strip(),
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=0.95,
                )
            )

        # Track Projects (v3.0: include descriptions)
        for proj in entities.projects:
            p, bbox, section = find_bbox(proj.title)
            desc_snippet = proj.description[:60] if proj.description else proj.title
            nodes.append(
                FieldEvidenceItem(
                    field_name="projects.title",
                    extracted_value=proj.title,
                    page_number=p,
                    section_header=section if section != "Text" else "PROJECTS",
                    sentence_snippet=desc_snippet,
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=0.90,
                )
            )

        # Track Publications
        for pub in entities.publications:
            p, bbox, section = find_bbox(pub.title[:20])
            nodes.append(
                FieldEvidenceItem(
                    field_name="publications.title",
                    extracted_value=pub.title,
                    page_number=p,
                    section_header=section if section != "Text" else "PUBLICATIONS",
                    sentence_snippet=pub.title,
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=0.96,
                )
            )

        # v3.0: Track Categorized Achievements
        for award in entities.categorized_awards[:6]:
            p, bbox, section = find_bbox(award.title[:30])
            nodes.append(
                FieldEvidenceItem(
                    field_name=f"achievements.{award.category.lower()}",
                    extracted_value=award.title,
                    page_number=p,
                    section_header=section if section != "Text" else "ACHIEVEMENTS",
                    sentence_snippet=f"[{award.category}] {award.title}",
                    bounding_box=bbox,
                    extraction_source="DETERMINISTIC",
                    confidence=0.88,
                )
            )

        return EvidencePackageGraph(
            total_evidence_nodes=len(nodes),
            evidence_nodes=nodes,
        )
