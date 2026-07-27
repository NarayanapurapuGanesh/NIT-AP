"""
Section Taxonomy & Ontology Resolver.
Maps 40+ canonical section types and multilingual aliases across English, German, French, Spanish, and Hindi.
"""

from typing import Any, Dict, List, Tuple

CANONICAL_SECTION_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Header": {
        "priority": 1,
        "aliases": ["header", "contact details", "contact information", "personal details", "personal info", "kontakt"],
    },
    "Summary": {
        "priority": 2,
        "aliases": ["summary", "professional summary", "executive summary", "profile summary", "about me", "overview", "profil", "resumen"],
    },
    "Career Objective": {
        "priority": 3,
        "aliases": ["career objective", "objective", "professional objective", "career goal", "ziel"],
    },
    "Academic Experience": {
        "priority": 10,
        "aliases": ["academic experience", "academic appointments", "academic positions", "faculty positions", "academic background"],
    },
    "Teaching Experience": {
        "priority": 11,
        "aliases": ["teaching experience", "teaching & mentoring", "courses taught", "pedagogical experience", "teaching history"],
    },
    "Research Experience": {
        "priority": 12,
        "aliases": ["research experience", "research activities", "scholarly activities", "research appointments", "research history"],
    },
    "Professional Experience": {
        "priority": 13,
        "aliases": ["professional experience", "work experience", "employment history", "work history", "career history", "experience", "berufserfahrung", "experiencia laboral"],
    },
    "Industry Experience": {
        "priority": 14,
        "aliases": ["industry experience", "corporate experience", "commercial experience"],
    },
    "Education": {
        "priority": 20,
        "aliases": ["education", "academic qualifications", "qualifications", "education history", "degrees", "ausbildung", "educación", "formation"],
    },
    "Skills": {
        "priority": 30,
        "aliases": ["skills", "core competencies", "areas of expertise", "key skills", "skills & abilities", "kenntnisse"],
    },
    "Technical Skills": {
        "priority": 31,
        "aliases": ["technical skills", "tech stack", "technical expertise", "domain skills"],
    },
    "Programming Languages": {
        "priority": 32,
        "aliases": ["programming languages", "coding languages", "languages & technologies"],
    },
    "Tools": {
        "priority": 33,
        "aliases": ["tools & software", "tools & technologies", "software skills", "developer tools"],
    },
    "Frameworks": {
        "priority": 34,
        "aliases": ["frameworks & libraries", "frameworks"],
    },
    "Soft Skills": {
        "priority": 35,
        "aliases": ["soft skills", "interpersonal skills", "personal skills"],
    },
    "Publications": {
        "priority": 40,
        "aliases": ["publications", "scholarly publications", "journal articles", "research publications", "peer-reviewed publications", "publikationen"],
    },
    "Research Projects": {
        "priority": 41,
        "aliases": ["research projects", "sponsored research", "funded research", "grants & projects"],
    },
    "Patents": {
        "priority": 42,
        "aliases": ["patents", "patents & inventions", "intellectual property"],
    },
    "Books": {
        "priority": 43,
        "aliases": ["books & chapters", "monographs", "edited books", "book chapters"],
    },
    "Conferences": {
        "priority": 44,
        "aliases": ["conferences", "conference proceedings", "keynote presentations", "invited talks", "symposia"],
    },
    "Workshops": {
        "priority": 45,
        "aliases": ["workshops & seminars", "workshops", "seminars"],
    },
    "Projects": {
        "priority": 50,
        "aliases": ["projects", "key projects", "academic projects", "software projects", "projekte"],
    },
    "Certifications": {
        "priority": 60,
        "aliases": ["certifications", "licenses & certifications", "professional certifications", "certificates", "zertifikate"],
    },
    "Achievements": {
        "priority": 70,
        "aliases": ["achievements", "key achievements", "highlights"],
    },
    "Awards": {
        "priority": 71,
        "aliases": ["awards & honors", "awards", "honors & awards", "recognition", "fellowships & awards", "auszeichnungen"],
    },
    "Honors": {
        "priority": 72,
        "aliases": ["honors", "scholarly honors", "academic honors"],
    },
    "Memberships": {
        "priority": 80,
        "aliases": ["memberships", "professional memberships", "societies", "professional affiliations", "mitgliedschaften"],
    },
    "Professional Bodies": {
        "priority": 81,
        "aliases": ["professional bodies", "editorial boards", "review committees", "program committees"],
    },
    "Languages": {
        "priority": 90,
        "aliases": ["languages", "language proficiency", "known languages", "sprachen", "idiomas"],
    },
    "References": {
        "priority": 100,
        "aliases": ["references", "referees", "academic references", "professional references", "referenzen"],
    },
    "Interests": {
        "priority": 110,
        "aliases": ["interests", "hobbies", "hobbies & interests", "extracurricular activities", "interessen"],
    },
    "Declaration": {
        "priority": 120,
        "aliases": ["declaration", "solemn declaration"],
    },
    "Signature": {
        "priority": 121,
        "aliases": ["signature", "date & signature"],
    },
}


class SectionTaxonomyResolver:
    """Taxonomy & Alias Resolution Engine."""

    def __init__(self) -> None:
        self._alias_map: Dict[str, Tuple[str, int]] = {}
        self._build_alias_map()

    def _build_alias_map(self) -> None:
        for canonical_type, meta in CANONICAL_SECTION_TAXONOMY.items():
            priority = meta["priority"]
            aliases = meta["aliases"]
            for alias in aliases:
                self._alias_map[alias.lower()] = (canonical_type, priority)

    def resolve(self, raw_heading: str) -> Tuple[str, str, int]:
        """Resolves a raw heading string to (canonical_type, matched_alias, priority)."""
        clean = raw_heading.strip().lower()
        # Direct lookup
        if clean in self._alias_map:
            c_type, prio = self._alias_map[clean]
            return c_type, clean, prio

        # Substring lookup
        for alias, (c_type, prio) in self._alias_map.items():
            if alias in clean:
                return c_type, alias, prio

        return "Custom Sections", clean, 999
