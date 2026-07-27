"""
Deterministic Extraction Module (Module 3) — v3.0 Section-Aware Engine.

LLM-free entity extraction engine using regex patterns, Python libraries (PyMuPDF, pdfplumber, python-docx, pytesseract),
dictionary taxonomies, and rule-based heuristics to extract:
- Name, Email, Phone, Address
- Profile Summary
- Skills (Technical + Soft)
- Education (with percentage, CGPA, expected year)
- Work Experience
- Publications, Projects (with descriptions), Patents
- Awards/Achievements (categorized: Hackathon, Certification, Coding, Internship)
- Languages, Certifications
- Candidate Type classification (Fresher / Experienced / Academic)

v3.0 adds section-aware extraction: entities are extracted from semantically
segmented SectionBlock objects produced by the LayoutAnalyzer, eliminating
cross-contamination between resume sections.
"""

import re
import io
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from extractors.base import IExtractor


class EducationEntity(BaseModel):
    degree: str = Field(..., description="Extracted degree (e.g. B.Tech, M.S., Ph.D.)")
    institution: str = Field("", description="University or college name")
    year: Optional[str] = Field(None, description="Graduation year or date range")
    gpa: Optional[str] = Field(None, description="Extracted GPA/Marks/Percentage")


class ExperienceEntity(BaseModel):
    title: str = Field(..., description="Job role or academic title")
    organization: str = Field("", description="Company, university, or lab name")
    start_date: Optional[str] = Field(None, description="Start date / Date range")
    end_date: Optional[str] = Field(None, description="End date / Present")
    description: str = Field("", description="Key responsibilities")


class PublicationEntity(BaseModel):
    title: str = Field(..., description="Paper or publication title")
    venue: Optional[str] = Field(None, description="Journal or conference name")
    year: Optional[str] = Field(None, description="Publication year")
    doi: Optional[str] = Field(None, description="DOI link or identifier")


class ProjectEntity(BaseModel):
    title: str = Field(..., description="Project name")
    description: str = Field("", description="Project details and features")
    technologies: List[str] = Field(default_factory=list, description="Extracted tech stack")
    project_links: List[str] = Field(default_factory=list, description="URLs found in or near project description")


class AchievementEntity(BaseModel):
    title: str = Field(..., description="Achievement description")
    category: str = Field("Other", description="Category: Hackathon, Certification, Coding, Internship, Award, Other")


class DeterministicEntities(BaseModel):
    name: Optional[str] = Field(None, description="Candidate full name")
    email: Optional[str] = Field(None, description="Candidate email address")
    phone: Optional[str] = Field(None, description="Candidate phone number")
    address: Optional[str] = Field(None, description="Candidate address/city/locality")
    profile_summary: Optional[str] = Field(None, description="Profile/objective/summary text")
    skills: List[str] = Field(default_factory=list, description="Extracted technical/domain skills")
    soft_skills: List[str] = Field(default_factory=list, description="Extracted soft/interpersonal skills")
    coding_skills: List[str] = Field(default_factory=list, description="Programming languages and frameworks for coding test generation")
    core_interview_points: List[str] = Field(default_factory=list, description="Key talking points for the interview panel")
    education: List[EducationEntity] = Field(default_factory=list, description="Education records")
    experience: List[ExperienceEntity] = Field(default_factory=list, description="Work experience records")
    publications: List[PublicationEntity] = Field(default_factory=list, description="Publication records")
    projects: List[ProjectEntity] = Field(default_factory=list, description="Project records")
    patents: List[str] = Field(default_factory=list, description="Patent titles/numbers")
    awards: List[str] = Field(default_factory=list, description="Honors and awards (flat list)")
    categorized_awards: List[AchievementEntity] = Field(default_factory=list, description="Categorized achievements")
    languages: List[str] = Field(default_factory=list, description="Spoken/written languages")
    certifications: List[str] = Field(default_factory=list, description="Professional certifications")
    candidate_type: str = Field("Unknown", description="Fresher / Experienced / Academic")
    uncertain_sections: List[str] = Field(default_factory=list, description="Unrecognized/ambiguous text paragraphs requiring LLM fallback")


class DeterministicExtractor(IExtractor):
    """Deterministic Entity Extractor with high-precision regex & structural layout parsing."""

    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?(?:\d{5}[-.\s]?\d{5}|\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\b\d{10}\b)')
    DOI_REGEX = re.compile(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', re.IGNORECASE)
    YEAR_REGEX = re.compile(r'\b(19\d\d|20\d\d)\b')
    DATE_RANGE_REGEX = re.compile(r'\b(?:19\d\d|20\d\d)\s*[-–—\to]\s*(?:19\d\d|20\d\d|Present|Expected|\d{4}\s*\(Expected\))\b', re.IGNORECASE)
    PROJECT_URL_REGEX = re.compile(r'https?://[^\s<>"\)]+', re.IGNORECASE)

    # Coding skills: programming languages / frameworks that can be tested in a coding exam
    CODING_SKILLS_SET = {
        "python", "java", "c++", "c#", "c", "javascript", "typescript", "go", "rust",
        "kotlin", "swift", "dart", "ruby", "php", "perl", "scala", "r", "matlab",
        "sql", "html", "css", "react", "next.js", "node.js", "angular", "vue.js",
        "django", "flask", "fastapi", "spring boot", "express",
        "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "keras",
        "docker", "kubernetes", "git", "linux",
        "flutter", "solidity", "graphql", "rest api",
    }

    TITLE_BLACKLIST = {
        "student", "engineer", "developer", "intern", "researcher", "professor", "manager",
        "associate", "candidate", "architect", "analyst", "computer science", "curriculum", "vitae", "resume",
        "good morning", "good afternoon", "good evening", "welcome", "everyone", "privilege", "respected", "honour"
    }

    COMMON_SKILLS = {
        "python", "java", "c++", "c#", "javascript", "typescript", "react", "next.js", "node.js",
        "fastapi", "django", "flask", "postgresql", "mongodb", "redis", "docker", "kubernetes",
        "aws", "azure", "gcp", "pytorch", "tensorflow", "scikit-learn", "spacy", "opencv",
        "machine learning", "deep learning", "natural language processing", "nlp", "computer vision",
        "data science", "git", "ci/cd", "microservices", "rest api", "graphql", "sql", "linux",
        "express", "supabase", "tailwind", "redux", "pandas", "numpy", "keras", "openai", "gemini",
        "figma", "figjam", "html", "css", "ui/ux", "nano banana", "canva", "adobe xd",
        "spring boot", "angular", "vue.js", "flutter", "dart", "swift", "kotlin", "go", "rust",
        "matlab", "r", "tableau", "power bi", "excel", "mysql", "sqlite", "firebase",
        "arduino", "raspberry pi", "iot", "blockchain", "solidity", "web3",
    }

    SOFT_SKILLS_DICT = {
        "teamwork", "time management", "adaptability", "effective communication", "communication",
        "critical thinking", "problem solving", "problem-solving", "leadership", "creativity",
        "collaboration", "decision making", "decision-making", "work ethic", "interpersonal",
        "negotiation", "conflict resolution", "emotional intelligence", "public speaking",
        "presentation", "attention to detail", "self-motivated", "multitasking", "flexibility",
        "active listening", "empathy", "patience", "analytical thinking", "initiative",
        "organizational", "strategic thinking", "mentoring", "coaching",
    }

    COMMON_LANGUAGES = {
        "english", "hindi", "spanish", "french", "german", "chinese", "japanese", "telugu", "tamil", "kannada", "marathi", "bengali", "urdu", "malayalam", "gujarati", "odia", "punjabi"
    }

    DEGREE_PATTERNS = [
        r'\b(Ph\.?D\.?|Doctor of Philosophy)\b',
        r'\b(M\.?Tech\.?|M\.?S\.|Master of Technology|Master of Science)\b',
        r'\b(Bachelor of Technology\s*\([^)]+\)|B\.?Tech\.?|B\.?S\.|B\.?E\.|Bachelor of Technology|Bachelor of Science)\b',
        r'\b(Intermediate\s*\([^)]+\)|Higher Secondary|12th Grade|12th|Intermediate)\b',
        r'\b(Secondary\s*\([^)]+\)|Secondary|10th Grade|10th|SSC|SSLC)\b',
        r'\b(B\.?A\.|M\.?A\.|MBA|BBA|BCA|MCA)\b',
    ]

    ACHIEVEMENT_CATEGORIES = {
        "Hackathon": ["hackathon", "hackatho", "smart india hackathon", "sih", "code jam", "ideathon"],
        "Certification": ["certification", "certificate", "certified", "workshop", "coursera", "edx", "udemy"],
        "Coding": ["codechef", "leetcode", "hackerrank", "codeforces", "competitive programming", "coding", "code chef"],
        "Internship": ["internship", "intern", "training program", "apprentice"],
        "Award": ["award", "winner", "runner-up", "first place", "gold medal", "silver medal", "scholarship", "fellowship", "best paper", "topper"],
    }

    # Indian cities and common address patterns
    ADDRESS_PATTERNS = re.compile(
        r'\b(?:Chodimella|Eluru|Tadepalligudem|Hyderabad|Bangalore|Chennai|Mumbai|Delhi|Kolkata|Pune|Visakhapatnam|Vijayawada|Guntur|Tirupati|Kakinada|Rajahmundry|Nellore|Kurnool|Anantapur|Warangal|Karimnagar|Nizamabad)\b',
        re.IGNORECASE
    )

    @property
    def name(self) -> str:
        return "DeterministicExtractor"

    async def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        text_content = data.get("text_content", "")
        file_bytes = data.get("file_bytes", b"")
        file_extension = data.get("file_extension", ".pdf")

        if not text_content and file_bytes:
            text_content = self._extract_raw_text(file_bytes, file_extension)

        entities = self.extract_entities(text_content)
        return entities.model_dump()

    def extract_entities_from_sections(self, sections, raw_text: str = "") -> DeterministicEntities:
        """v3.0 Section-aware extraction: extracts entities from segmented SectionBlocks.

        This method receives pre-segmented sections from the LayoutAnalyzer and extracts
        entities from the correct section context, preventing cross-contamination.
        """
        from layout.layout_analyzer import SectionBlock

        # Collect section content by type
        section_map: Dict[str, List[str]] = {}
        for sec in sections:
            key = sec.section_name
            if key not in section_map:
                section_map[key] = []
            section_map[key].extend(sec.content_lines)

        # Also keep all sections' text for fallback
        all_text = raw_text if raw_text else "\n".join(
            line for sec in sections for line in sec.content_lines
        )

        # Un-wrap split email lines
        unwrapped_text = self._unwrap_split_emails(all_text)
        clean_all = self._clean_pdf_dict_garbage(unwrapped_text)

        # --- Extract contact info from full text (contact info can appear anywhere) ---
        email = self._extract_email(clean_all)
        phone = self._extract_phone(clean_all)
        all_lines = [line.strip() for line in clean_all.split("\n") if line.strip()]
        name = self._extract_name(all_lines, email)

        # --- Address extraction ---
        address = self._extract_address(clean_all, section_map.get("CONTACT", []))

        # --- Profile summary from PROFILE section ---
        profile_summary = self._extract_profile_summary(section_map.get("PROFILE", []))

        # --- Technical skills from SKILLS section ---
        skills_text = "\n".join(section_map.get("SKILLS", []))
        skills = self._extract_skills(skills_text) if skills_text else self._extract_skills(clean_all)

        # --- Soft skills from SOFT_SKILLS section (or SKILLS section) ---
        soft_skills_text = "\n".join(section_map.get("SOFT_SKILLS", []))
        if not soft_skills_text:
            soft_skills_text = skills_text  # Check SKILLS section for soft skills too
        soft_skills = self._extract_soft_skills(soft_skills_text) if soft_skills_text else self._extract_soft_skills(clean_all)

        # --- Languages ---
        lang_text = "\n".join(section_map.get("LANGUAGES", []))
        languages = self._extract_languages(lang_text) if lang_text else self._extract_languages(clean_all)

        # --- Education from EDUCATION section ---
        edu_lines = section_map.get("EDUCATION", [])
        edu_text = "\n".join(edu_lines)
        education = self._extract_education(edu_text, edu_lines) if edu_lines else self._extract_education(clean_all, all_lines)

        # --- Experience from EXPERIENCE section ---
        exp_lines = section_map.get("EXPERIENCE", [])
        experience = self._extract_experience(exp_lines) if exp_lines else self._extract_experience(all_lines)

        # --- Publications from PUBLICATIONS section ---
        pub_lines = section_map.get("PUBLICATIONS", [])
        publications = self._extract_publications_from_section(pub_lines) if pub_lines else self._extract_publications(all_lines)

        # --- Projects from PROJECTS section (enhanced with descriptions) ---
        proj_lines = section_map.get("PROJECTS", [])
        projects = self._extract_projects_from_section(proj_lines) if proj_lines else self._extract_projects(all_lines)

        # --- Awards/Achievements from ACHIEVEMENTS section (categorized) ---
        award_lines = section_map.get("ACHIEVEMENTS", [])
        awards_flat, categorized_awards = self._extract_categorized_awards(award_lines) if award_lines else self._extract_categorized_awards_from_text(all_lines)

        # --- Certifications ---
        cert_lines = section_map.get("CERTIFICATIONS", [])
        certifications = self._extract_certifications(cert_lines) if cert_lines else self._extract_certifications(all_lines)

        # --- Patents ---
        patents = self._extract_patents(all_lines)

        # --- Candidate type classification ---
        candidate_type = self._classify_candidate_type(experience, education, publications)

        # --- Coding skills (subset for coding test generation) ---
        coding_skills = self._extract_coding_skills(skills)

        # --- Core interview points ---
        core_interview_points = self._generate_core_interview_points(
            name=name, education=education, experience=experience,
            skills=skills, publications=publications, projects=projects,
            awards=awards_flat, candidate_type=candidate_type,
            profile_summary=profile_summary,
        )

        # --- Uncertain sections (for LLM callback) ---
        uncertain = []
        for sec in sections:
            if sec.section_name == "UNKNOWN" and sec.content_lines:
                combined = " ".join(sec.content_lines)
                if len(combined) > 40:
                    uncertain.append(combined)

        # --- Populate project_links from URLs inside project descriptions ---
        self._enrich_project_links(projects)

        return DeterministicEntities(
            name=name,
            email=email,
            phone=phone,
            address=address,
            profile_summary=profile_summary,
            skills=skills,
            soft_skills=soft_skills,
            coding_skills=coding_skills,
            core_interview_points=core_interview_points,
            education=education,
            experience=experience,
            publications=publications,
            projects=projects,
            patents=patents,
            awards=awards_flat,
            categorized_awards=categorized_awards,
            languages=languages,
            certifications=certifications,
            candidate_type=candidate_type,
            uncertain_sections=uncertain[:5],
        )

    def extract_entities(self, text_content: str) -> DeterministicEntities:
        """Legacy v2.0 fallback: flat text extraction without section awareness."""
        # Un-wrap split email lines BEFORE any extraction
        unwrapped_text = self._unwrap_split_emails(text_content)

        # Clean out raw PDF dictionary stream tags safely
        clean_content = self._clean_pdf_dict_garbage(unwrapped_text)
        lines = [line.strip() for line in clean_content.split("\n") if line.strip()]

        email = self._extract_email(clean_content)
        phone = self._extract_phone(clean_content)
        name = self._extract_name(lines, email)
        address = self._extract_address(clean_content, [])
        profile_summary = None  # Cannot reliably extract without section info
        skills = self._extract_skills(clean_content)
        soft_skills = self._extract_soft_skills(clean_content)
        languages = self._extract_languages(clean_content)
        education = self._extract_education(clean_content, lines)
        experience = self._extract_experience(lines)
        publications = self._extract_publications(lines)
        projects = self._extract_projects(lines)
        patents = self._extract_patents(lines)
        awards_flat, categorized_awards = self._extract_categorized_awards_from_text(lines)
        certifications = self._extract_certifications(lines)
        candidate_type = self._classify_candidate_type(experience, education, publications)
        uncertain = self._find_uncertain_sections(lines)

        # --- Coding Skills ---
        coding_skills = self._extract_coding_skills(skills)

        # --- Core Interview Points ---
        core_interview_points = self._generate_core_interview_points(
            name=name,
            education=education,
            experience=experience,
            skills=skills,
            publications=publications,
            projects=projects,
            awards=awards_flat,
            candidate_type=candidate_type,
            profile_summary=profile_summary,
        )

        # --- Populate project_links ---
        self._enrich_project_links(projects)

        return DeterministicEntities(
            name=name,
            email=email,
            phone=phone,
            address=address,
            profile_summary=profile_summary,
            skills=skills,
            soft_skills=soft_skills,
            coding_skills=coding_skills,
            core_interview_points=core_interview_points,
            education=education,
            experience=experience,
            publications=publications,
            projects=projects,
            patents=patents,
            awards=awards_flat,
            categorized_awards=categorized_awards,
            languages=languages,
            certifications=certifications,
            candidate_type=candidate_type,
            uncertain_sections=uncertain,
        )

    def _enrich_project_links(self, projects: List[ProjectEntity]):
        """Helper to scan project descriptions for links."""
        for p in projects:
            if not p.project_links:
                p.project_links = self._extract_urls_from_text(p.description)

    def _extract_urls_from_text(self, text: str) -> List[str]:
        """Extract all http/https URLs from a text string."""
        if not text:
            return []
        return self.PROJECT_URL_REGEX.findall(text)

    def _extract_coding_skills(self, skills: List[str]) -> List[str]:
        """Filter the extracted skills list to isolate programming languages and frameworks
        suitable for automated coding test question generation."""
        coding = []
        for skill in skills:
            # Normalize to lowercase for matching against the canonical set
            if skill.lower() in self.CODING_SKILLS_SET:
                coding.append(skill)
        return sorted(set(coding))

    def _generate_core_interview_points(
        self,
        skills: List[str] = None,
        coding_skills: List[str] = None,
        education: List['EducationEntity'] = None,
        experience: List['ExperienceEntity'] = None,
        projects: List['ProjectEntity'] = None,
        publications: List['PublicationEntity'] = None,
        certifications: List[str] = None,
        candidate_type: str = "Unknown",
        # Accept but ignore extra kwargs for flexibility
        **kwargs,
    ) -> List[str]:
        """Generate heuristic-based core interview talking points for the faculty interview panel.

        Produces 5-8 structured points covering the candidate's strongest angles:
        education depth, technical breadth, project complexity, research output, and growth areas.
        """
        points: List[str] = []
        skills = skills or []
        coding_skills = coding_skills or []
        education = education or []
        experience = experience or []
        projects = projects or []
        publications = publications or []
        certifications = certifications or []

        # 1. Candidate classification context
        if candidate_type and candidate_type != "Unknown":
            points.append(f"Candidate is classified as '{candidate_type}' — tailor interview depth accordingly.")

        # 2. Education highlights
        highest_degrees = []
        for edu in education:
            deg_info = edu.degree
            if edu.institution:
                deg_info += f" from {edu.institution}"
            if edu.gpa:
                deg_info += f" (GPA/Marks: {edu.gpa})"
            highest_degrees.append(deg_info)
        if highest_degrees:
            points.append(f"Education: {'; '.join(highest_degrees[:3])}. Probe depth of coursework and academic rigor.")

        # 3. Technical skill breadth
        if skills:
            top_skills = skills[:8]
            points.append(f"Technical skill breadth: {', '.join(top_skills)}. Assess practical proficiency vs. listing.")

        # 4. Coding ability — key for automated test generation
        if coding_skills:
            points.append(f"Coding proficiency claimed in: {', '.join(coding_skills[:6])}. Recommend hands-on coding round in these languages.")

        # 5. Project depth
        if projects:
            project_titles = [p.title for p in projects[:4]]
            points.append(f"Has {len(projects)} project(s): {', '.join(project_titles)}. Investigate design decisions, scalability, and individual contribution.")

        # 6. Research / Publications
        if publications:
            points.append(f"Published {len(publications)} paper(s). Verify originality and discuss methodology in depth.")

        # 7. Work experience
        if experience:
            roles = [f"{e.title} at {e.organization}" for e in experience[:3] if e.organization]
            if roles:
                points.append(f"Professional roles: {'; '.join(roles)}. Probe real-world impact and measurable outcomes.")

        # 8. Certifications / continuous learning
        if certifications:
            points.append(f"Holds {len(certifications)} certification(s). Verify relevance and recency.")

        # 9. Growth / gap areas
        if not publications and candidate_type == "Academic":
            points.append("No publications detected despite academic profile — explore research aspirations.")
        if not experience and candidate_type != "Fresher":
            points.append("No work experience found — clarify career gaps or undocumented roles.")

        return points[:10]

    def _clean_pdf_dict_garbage(self, text: str) -> str:
        if not text:
            return ""
        return re.sub(
            r'/(BaseFont|FontDescriptor|FontName|Encoding|WinAnsiEncoding|DeviceRGB|BitsPerComponent|ProcSet|CIDSystemInfo|Subtype|Type|Length|Filter|Widths)\b',
            '',
            text
        )

    # =====================================================================
    #  TEXT EXTRACTION & EMAIL UNWRAPPING
    # =====================================================================

    def _unwrap_split_emails(self, text: str) -> str:
        # 1. TLD unwrap across lines (e.g. @gmail.c\nom, @gmail.co\nm, @domain.e\ndu)
        text = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{1,3})\s*[\r\n]+\s*([a-zA-Z]{1,3}\b)', r'\1\2', text)
        # 2. Join domain split after dot (e.g., @gmail.\ncom, @domain.\nedu)
        text = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.)\s*[\r\n]+\s*([a-zA-Z]{2,4}\b)', r'\1\2', text)
        # 3. Join split after @ (e.g., user@\ngmail.com)
        text = re.sub(r'([a-zA-Z0-9._%+-]+@)\s*[\r\n]+\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}\b)', r'\1\2', text)

        lines = text.split("\n")
        cleaned_lines = []
        i = 0
        while i < len(lines):
            curr = lines[i].strip()
            if i + 1 < len(lines):
                nxt = lines[i + 1].strip()
                if "@" in nxt and "@" not in curr and " " not in curr and len(curr) >= 3 and re.match(r'^[a-zA-Z0-9._%+-]+$', curr):
                    candidate = curr + nxt
                    if self.EMAIL_REGEX.match(candidate) or re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', candidate):
                        cleaned_lines.append(candidate)
                        i += 2
                        continue
                if (nxt.startswith("@") or re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', nxt)) and "@" not in curr and " " not in curr and re.match(r'^[a-zA-Z0-9._%+-]+$', curr):
                    if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', curr + nxt):
                        cleaned_lines.append(curr + nxt)
                        i += 2
                        continue
                if re.search(r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{1,2}$', curr) and re.match(r'^[a-zA-Z]{1,4}$', nxt):
                    cleaned_lines.append(curr + nxt)
                    i += 2
                    continue
            cleaned_lines.append(curr)
            i += 1
        return "\n".join(cleaned_lines)

    def extract_raw_text_and_links(self, file_bytes: bytes, ext: str) -> tuple[str, List[str]]:
        annotation_links: List[str] = []
        try:
            if ext == ".pdf":
                import fitz
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                pages_text = []

                for page in doc:
                    page_width = page.rect.width
                    blocks = page.get_text("blocks")

                    header_blocks = []
                    left_blocks = []
                    right_blocks = []
                    split_x = page_width * 0.42

                    for b in blocks:
                        x0, y0, x1, y1, text = b[:5]
                        clean = text.strip() if isinstance(text, str) else ""
                        if not clean:
                            continue
                        if x1 - x0 > page_width * 0.75 or (y0 < 60 and (x1 - x0) > page_width * 0.5):
                            header_blocks.append((y0, clean))
                        elif x0 < split_x:
                            left_blocks.append((y0, clean))
                        else:
                            right_blocks.append((y0, clean))

                    header_blocks.sort(key=lambda item: item[0])
                    left_blocks.sort(key=lambda item: item[0])
                    right_blocks.sort(key=lambda item: item[0])

                    ordered_text = "\n".join(
                        [t for _, t in header_blocks] + [t for _, t in left_blocks] + [t for _, t in right_blocks]
                    )
                    pages_text.append(ordered_text)

                    for link in page.get_links():
                        if "uri" in link and link["uri"]:
                            annotation_links.append(link["uri"])

                extracted = "\n".join(pages_text).strip()

                # Check if PyMuPDF extracted raw PDF font dictionary garbage or empty text
                is_pdf_garbage = any(
                    keyword in extracted
                    for keyword in [
                        "/BaseFont",
                        "/WinAnsiEncoding",
                        "/DeviceRGB",
                        "/BitsPerComponent",
                        "/FontDescriptor",
                        "/FontName",
                        "/Encoding",
                    ]
                )

                if is_pdf_garbage or len(extracted) < 800:
                    # Run High-Res Pytesseract OCR Fallback for visual/scanned PDF
                    import pytesseract
                    from PIL import Image

                    ocr_pages = []
                    for page in doc:
                        pix = page.get_pixmap(dpi=300)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        ocr_text = pytesseract.image_to_string(img)
                        if ocr_text.strip():
                            ocr_pages.append(ocr_text)

                    if ocr_pages:
                        extracted = "\n".join(ocr_pages).strip()

                doc.close()
                if extracted:
                    return extracted, annotation_links
                return file_bytes.decode("utf-8", errors="ignore"), annotation_links
            elif ext == ".docx":
                import docx
                doc = docx.Document(io.BytesIO(file_bytes))
                return "\n".join([p.text for p in doc.paragraphs]), []
            elif ext in {".png", ".jpg", ".jpeg", ".tiff", ".tif"}:
                import pytesseract
                from PIL import Image
                img = Image.open(io.BytesIO(file_bytes))
                return pytesseract.image_to_string(img), []
        except Exception:
            return file_bytes.decode("utf-8", errors="ignore"), []
        return "", []

    def _extract_raw_text(self, file_bytes: bytes, ext: str) -> str:
        text, _ = self.extract_raw_text_and_links(file_bytes, ext)
        return text

    # =====================================================================
    #  CONTACT EXTRACTION
    # =====================================================================

    def _extract_email(self, text: str) -> Optional[str]:
        clean_text = self._clean_pdf_dict_garbage(text)
        clean_text = self._unwrap_split_emails(clean_text)

        # 1. First check explicit "Email Address:" or "Email:" label match
        label_match = re.search(
            r'(?:email\s*address|email|e-mail|mail)\s*[:\-]?\s*([a-zA-Z0-9._%+\-\s\r\n]+@[a-zA-Z0-9.\-\s\r\n]+\.[a-zA-Z]{2,4})',
            clean_text,
            re.IGNORECASE
        )
        if label_match:
            raw_cand = label_match.group(1)
            cleaned_cand = re.sub(r'\s+', '', raw_cand)
            m = self.EMAIL_REGEX.search(cleaned_cand)
            if m and any(m.group(0).lower().endswith(domain) for domain in [".com", ".in", ".edu", ".ac.in", ".org", ".net", ".io"]):
                return m.group(0)

        # 2. Standard regex search
        matches = self.EMAIL_REGEX.findall(clean_text)
        for m in matches:
            if not m.startswith("+") and not re.search(r'\+[A-Za-z0-9_.-]+@', m):
                if any(m.lower().endswith(domain) for domain in [".com", ".in", ".edu", ".ac.in", ".org", ".net", ".io"]):
                    username = m.split("@")[0]
                    if len(username) <= 3 or username.isdigit():
                        prefix_match = re.search(r'([a-zA-Z0-9._%+-]{2,})[^a-zA-Z0-9]+' + re.escape(m), clean_text)
                        if prefix_match:
                            prefix_word = prefix_match.group(1)
                            excluded_words = {"email", "e-mail", "mail", "contact", "address", "phone", "mobile", "gmail", "yahoo", "outlook", "http", "https"}
                            if prefix_word.lower() not in excluded_words:
                                return prefix_word + m
                            else:
                                two_words_match = re.search(r'([a-zA-Z0-9._%+-]{2,})[^a-zA-Z0-9]+' + re.escape(prefix_word) + r'[^a-zA-Z0-9]+' + re.escape(m), clean_text)
                                if two_words_match:
                                    real_prefix = two_words_match.group(1)
                                    if real_prefix.lower() not in excluded_words:
                                        return real_prefix + m
                    return m

        if matches:
            return matches[0]

        split_match = re.search(r'([a-zA-Z0-9._%+-]+\s*@\s*[a-zA-Z0-9.-]+\s*\.\s*[a-zA-Z]{2,4})', clean_text)
        if split_match:
            return re.sub(r'\s+', '', split_match.group(1))

        # 3. OCR Fallback: Check lines with @ and . and strip spaces to try matching a valid email
        for line in clean_text.split('\n'):
            if '@' in line and '.' in line:
                no_space_line = re.sub(r'\s+', '', line)
                m = self.EMAIL_REGEX.search(no_space_line)
                if m:
                    return m.group(0)

        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        match = self.PHONE_REGEX.search(text)
        if match:
            raw = match.group(0).strip()
            clean_digits = re.sub(r'\D', '', raw)
            if len(clean_digits) >= 10:
                return raw
        return None

    def _extract_name(self, lines: List[str], email: Optional[str]) -> Optional[str]:
        if not lines:
            return None

        candidate_words = []
        for line in lines[:6]:
            if any(b in line.lower() for b in self.TITLE_BLACKLIST):
                continue
            if any(k in line.lower() for k in ["contact", "phone", "email", "address", "profile", "summary"]):
                continue

            cleaned = re.sub(r'[^a-zA-Z\s.]', '', line).strip()
            if not cleaned or cleaned.startswith(".") or len(cleaned.replace(".", "").strip()) < 2:
                continue

            words = [w.strip(".") for w in cleaned.split() if len(w.strip(".")) > 1]
            if words:
                candidate_words.extend(words)
                if len(candidate_words) >= 2:
                    return " ".join(candidate_words[:3]).title()

        return None

    def _extract_address(self, text: str, contact_lines: List[str]) -> Optional[str]:
        """Extracts city/locality/address from text or contact section."""
        # First check contact section lines
        for line in contact_lines:
            match = self.ADDRESS_PATTERNS.search(line)
            if match:
                # Clean out emails and urls
                clean_line = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', line)
                clean_line = re.sub(r'https?://[^\s]+', '', clean_line)
                
                # Split by common contact separators
                parts = re.split(r'\s*[|•\-\u2022]\s*', clean_line)
                for part in parts:
                    if self.ADDRESS_PATTERNS.search(part):
                        clean_part = part.strip()
                        if len(clean_part) < 80:
                            return clean_part

                # Fallback
                clean = clean_line.strip()
                if len(clean) < 80:
                    return clean
                return match.group(0)

        # Fallback: scan full text for address patterns
        match = self.ADDRESS_PATTERNS.search(text)
        if match:
            # Try to capture surrounding context (city, state)
            pos = match.start()
            snippet = text[max(0, pos - 30):min(len(text), pos + 60)]
            # Extract a clean address line
            addr_lines = snippet.split("\n")
            for addr_line in addr_lines:
                if match.group(0).lower() in addr_line.lower():
                    # Clean out emails and urls
                    clean_line = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', addr_line)
                    clean_line = re.sub(r'https?://[^\s]+', '', clean_line)
                    
                    # Split by common contact separators
                    parts = re.split(r'\s*[|•\-\u2022]\s*', clean_line)
                    for part in parts:
                        if self.ADDRESS_PATTERNS.search(part):
                            clean = part.strip()
                            clean = re.sub(r'^[^a-zA-Z]+', '', clean)
                            if clean and len(clean) < 80:
                                return clean

                    # If parts splitting doesn't work, just clean the line
                    clean = clean_line.strip()
                    clean = re.sub(r'^[^a-zA-Z]+', '', clean)
                    if clean and len(clean) < 80:
                        return clean

            return match.group(0)

        return None

    # =====================================================================
    #  PROFILE SUMMARY
    # =====================================================================

    def _extract_profile_summary(self, profile_lines: List[str]) -> Optional[str]:
        """Extracts profile/objective/summary from PROFILE section lines."""
        if not profile_lines:
            return None

        # Join all profile section lines into a coherent paragraph
        summary_parts = []
        for line in profile_lines:
            clean = line.strip()
            # Skip very short lines that are likely labels
            if clean and len(clean) > 5:
                # Remove bullet points
                clean = re.sub(r'^[•\-▪■●◆]\s*', '', clean)
                summary_parts.append(clean)

        if summary_parts:
            return " ".join(summary_parts)
        return None

    # =====================================================================
    #  SKILLS EXTRACTION
    # =====================================================================

    def _extract_skills(self, text: str) -> List[str]:
        clean_text = self._clean_pdf_dict_garbage(text)
        text_lower = clean_text.lower()
        found_skills = []
        for skill in self.COMMON_SKILLS:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.title() if len(skill) > 3 else skill.upper())
        return list(set(found_skills))

    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extracts soft/interpersonal skills from text."""
        text_lower = text.lower()
        found = []
        for skill in self.SOFT_SKILLS_DICT:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.append(skill.title())
        return list(set(found))

    # =====================================================================
    #  LANGUAGES
    # =====================================================================

    def _extract_languages(self, text: str) -> List[str]:
        text_lower = text.lower()
        found = []
        for lang in self.COMMON_LANGUAGES:
            pattern = r'\b' + re.escape(lang) + r'\b'
            if re.search(pattern, text_lower):
                found.append(lang.capitalize())
        return list(set(found))

    # =====================================================================
    #  EDUCATION EXTRACTION (Enhanced)
    # =====================================================================

    def _extract_education(self, text: str, lines: List[str]) -> List[EducationEntity]:
        results = []
        seen_degrees = set()

        for pattern in self.DEGREE_PATTERNS:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for m in matches:
                raw_degree = m.group(0).strip()
                deg_lower = raw_degree.lower()

                # Normalize degree names
                if "bachelor of technology" in deg_lower or "b.tech" in deg_lower or "b.e." in deg_lower:
                    degree_key = "btech"
                    degree_name = "Bachelor of Technology (B.Tech)"
                elif "intermediate" in deg_lower or "higher secondary" in deg_lower or "12th" in deg_lower:
                    degree_key = "intermediate"
                    degree_name = "Intermediate"
                elif "secondary" in deg_lower or "10th" in deg_lower or "ssc" in deg_lower:
                    degree_key = "secondary"
                    degree_name = "Secondary (SSC)"
                elif "master" in deg_lower or "m.tech" in deg_lower or "m.s" in deg_lower:
                    degree_key = "mtech"
                    degree_name = raw_degree
                elif "ph.d" in deg_lower or "doctor" in deg_lower:
                    degree_key = "phd"
                    degree_name = "Ph.D."
                else:
                    degree_key = deg_lower
                    degree_name = raw_degree

                if degree_key in seen_degrees or any(k in deg_lower for k in ["font", "encoding", "bits"]):
                    continue
                seen_degrees.add(degree_key)

                line_idx = -1
                in_edu_context = False
                for idx, l in enumerate(lines):
                    if "education" in l.lower():
                        in_edu_context = True
                    if in_edu_context and any(h in l.lower() for h in ["projects", "skills", "experience", "achievements", "languages"]):
                        in_edu_context = False

                    if raw_degree.lower() in l.lower() or degree_key in l.lower():
                        if any(sk in l.lower() for sk in ["html", "css", "python", "intermediate)", "skill"]):
                            if not any(y in l for y in ["201", "202", "199", "200"]):
                                continue
                        line_idx = idx
                        if in_edu_context:
                            break

                # Build a degree-bounded snippet that stops at the next degree name
                snippet = text[max(0, m.start() - 40): min(len(text), m.end() + 250)]
                # Bounding check: truncate snippet if another degree pattern appears after m.end()
                sub_text = text[m.end():min(len(text), m.end() + 250)]
                for next_pat in self.DEGREE_PATTERNS:
                    next_m = re.search(next_pat, sub_text, re.IGNORECASE)
                    if next_m and next_m.start() > 5:
                        snippet = text[max(0, m.start() - 40): m.end() + next_m.start()]
                        break

                # Year extraction (enhanced for "Expected" and ranges like "2023 - Present")
                range_match = self.DATE_RANGE_REGEX.search(snippet)
                years = self.YEAR_REGEX.findall(snippet)
                year_str = range_match.group(0) if range_match else None

                if not year_str and years:
                    if len(years) >= 2:
                        year_str = f"{years[0]} - {years[1]}"
                    else:
                        year_str = years[0]

                # Check for "Expected" graduation
                expected_match = re.search(r'(?:expected|pursuing|ongoing|present)\s*(?:in\s+)?(\d{4})?', snippet, re.IGNORECASE)
                if expected_match:
                    exp_year = expected_match.group(1)
                    if exp_year and not year_str:
                        year_str = f"Expected {exp_year}"
                    elif exp_year and year_str and "present" not in year_str.lower():
                        year_str = f"{year_str} (Expected)"

                # Check for "Present" indicator
                if years and not year_str:
                    if re.search(r'\bpresent\b', snippet, re.IGNORECASE):
                        year_str = f"{years[0]} - Present"

                # GPA/Percentage extraction (enhanced)
                gpa_val = None
                gpa_patterns = [
                    r'(?:percentage|cgpa|gpa|grade|marks|score)\s*[:\-=]?\s*(\d{1,2}(?:\.\d{1,2})?\s*%|\d{1,2}\.\d{1,2}\s*cgpa|\d{1,2}\.\d{1,2})',
                    r'(\d{1,2}\.\d{1,2})\s*(?:cgpa|gpa)',
                    r'(\d{2,3}(?:\.\d{1,2})?)\s*%',
                    r'(?:percentage|cgpa|gpa)\s*[:\-=]?\s*(\d{1,2}\.\d{1,2})',
                ]
                for gpa_pat in gpa_patterns:
                    gpa_match = re.search(gpa_pat, snippet, re.IGNORECASE)
                    if gpa_match:
                        gpa_val = gpa_match.group(1).strip()
                        # Normalize: add % if it looks like a percentage (>10)
                        if gpa_val and not gpa_val.endswith('%') and "cgpa" not in gpa_val.lower() and "gpa" not in gpa_val.lower():
                            try:
                                val = float(gpa_val.replace('%', ''))
                                if val > 10:
                                    gpa_val = f"{gpa_val}%"
                            except ValueError:
                                pass
                        break

                # Institution extraction
                inst = ""
                if line_idx >= 0:
                    for offset in range(1, 5):
                        if line_idx + offset < len(lines):
                            cand_line = lines[line_idx + offset].strip()
                            if any(u in cand_line.lower() for u in ["university", "institute", "college", "school", "iit", "nit", "sasi", "chaitanya", "academy", "vidyalaya", "engineering"]):
                                inst = cand_line
                                break

                # Also check surrounding text in snippet
                if not inst:
                    inst_match = re.search(
                        r'((?:Sasi|Sri|St\.|Saint|IIT|NIT|IIIT|BITS|VIT|SRM)\s+[A-Z][a-zA-Z\s,]+)',
                        snippet
                    )
                    if inst_match:
                        inst = inst_match.group(1).strip()
                        inst = re.sub(r'\s+\d{4}.*', '', inst).strip()

                results.append(EducationEntity(degree=degree_name, institution=inst or "Recognized Institution", year=year_str, gpa=gpa_val))
        return results[:5]

    # =====================================================================
    #  EXPERIENCE EXTRACTION
    # =====================================================================

    def _extract_experience(self, lines: List[str]) -> List[ExperienceEntity]:
        exp_list = []
        in_exp_section = False
        i = 0
        while i < len(lines):
            line = lines[i]
            if any(h in line.lower() for h in ["work experience", "professional experience", "employment", "teaching experience"]):
                in_exp_section = True
                i += 1
                continue
            if in_exp_section and any(h in line.lower() for h in ["education", "publications", "projects", "skills", "certifications", "achievements"]):
                in_exp_section = False
                break

            if in_exp_section:
                years = self.YEAR_REGEX.findall(line)
                range_match = self.DATE_RANGE_REGEX.search(line)
                if years or any(role in line.lower() for role in ["engineer", "developer", "professor", "manager", "lead", "researcher", "intern", "associate"]):
                    title = line.strip()
                    org = ""
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if not any(role in next_line.lower() for role in ["engineer", "developer", "intern", "manager"]) and not next_line.startswith("•") and not next_line.startswith("-"):
                            org = re.sub(r'\b(Remote|Hybrid|Onsite|Full-time|Part-time)\b', '', next_line, flags=re.IGNORECASE).strip()
                            i += 1

                    dates = range_match.group(0) if range_match else (" - ".join(years) if len(years) >= 2 else (years[0] if years else None))
                    exp_list.append(ExperienceEntity(title=title, organization=org or "Organization", start_date=dates))
            i += 1
        return exp_list[:6]

    # =====================================================================
    #  PUBLICATIONS EXTRACTION
    # =====================================================================

    def _extract_publications(self, lines: List[str]) -> List[PublicationEntity]:
        pubs = []
        in_pub_section = False
        for line in lines:
            if any(h in line.lower() for h in ["publications", "papers", "journals", "conference proceedings", "patents"]):
                in_pub_section = True
                cleaned_line = re.sub(r'^(publications|papers|journals|conference proceedings|patents)\s*:?\s*', '', line, flags=re.IGNORECASE).strip()
                if len(cleaned_line) > 15:
                    doi_match = self.DOI_REGEX.search(cleaned_line)
                    doi = doi_match.group(0) if doi_match else None
                    years = self.YEAR_REGEX.findall(cleaned_line)
                    year = years[0] if years else None
                    pubs.append(PublicationEntity(title=cleaned_line, year=year, doi=doi))
                continue
            if in_pub_section and any(h in line.lower() for h in ["education", "experience", "projects", "skills", "awards", "achievements"]):
                in_pub_section = False
                break
            if in_pub_section:
                doi_match = self.DOI_REGEX.search(line)
                doi = doi_match.group(0) if doi_match else None
                years = self.YEAR_REGEX.findall(line)
                year = years[0] if years else None
                if len(line) > 15:
                    pubs.append(PublicationEntity(title=line, year=year, doi=doi))
        return pubs[:10]

    def _extract_publications_from_section(self, lines: List[str]) -> List[PublicationEntity]:
        """Extract publications from pre-segmented section lines."""
        pubs = []
        for line in lines:
            if len(line.strip()) > 15:
                doi_match = self.DOI_REGEX.search(line)
                doi = doi_match.group(0) if doi_match else None
                years = self.YEAR_REGEX.findall(line)
                year = years[0] if years else None
                pubs.append(PublicationEntity(title=line.strip(), year=year, doi=doi))
        return pubs[:10]

    # =====================================================================
    #  PROJECTS EXTRACTION (Enhanced with clean titles and descriptions)
    # =====================================================================

    def _extract_projects(self, lines: List[str]) -> List[ProjectEntity]:
        """Legacy project extraction for flat text."""
        projects = []
        in_proj_section = False
        i = 0
        while i < len(lines):
            line = lines[i]
            if any(h in line.lower() for h in ["projects", "key projects", "academic projects"]):
                in_proj_section = True
                i += 1
                continue
            if in_proj_section and any(h in line.lower() for h in ["education", "experience", "publications", "skills", "achievements", "certifications"]):
                in_proj_section = False
                break

            if in_proj_section:
                clean_l = line.strip()
                if "PROJECT TITLE" in clean_l.upper() or "PROJECT:" in clean_l.upper() or "TITLE:" in clean_l.upper():
                    title = re.sub(r'^(?:PROJECT\s*)?(?:TITLE|NAME)?\s*[:\-=]\s*', '', clean_l, flags=re.IGNORECASE).strip()
                    if not title and i + 1 < len(lines):
                        i += 1
                        title = re.sub(r'^(?:PROJECT\s*)?(?:TITLE|NAME)?\s*[:\-=]\s*', '', lines[i].strip(), flags=re.IGNORECASE).strip()

                    if title:
                        tech = []
                        desc_parts = []
                        for offset in range(1, 6):
                            if i + offset < len(lines):
                                next_l = lines[i + offset].strip()
                                if "TECHNOLOGY USED" in next_l.upper() or "TECH USED" in next_l.upper():
                                    tech_str = re.sub(r'TECHNOLOG(?:Y|IES)\s*USED?\s*[:\-=]?\s*', '', next_l, flags=re.IGNORECASE).strip()
                                    tech = [t.strip() for t in tech_str.split(",") if t.strip()]
                                elif next_l.startswith("•") or next_l.startswith("-") or next_l.startswith("–"):
                                    desc_parts.append(re.sub(r'^[•\-–]\s*', '', next_l))
                                elif any(k.upper() in next_l.upper() for k in ["PROJECT TITLE", "PROJECT:"]):
                                    break
                        full_desc = " | ".join(desc_parts) if desc_parts else title
                        projects.append(ProjectEntity(title=title, description=full_desc, technologies=tech, project_links=self._extract_urls_from_text(full_desc)))
                elif len(clean_l) > 6 and not clean_l.startswith("-") and not clean_l.startswith("•") and not any(k in clean_l.lower() for k in ["demonstrates", "mindset", "practices", "application", "technologies", "technology used"]):
                    parts = clean_l.split("|")
                    title = re.sub(r'^(?:PROJECT\s*)?(?:TITLE|NAME)?\s*[:\-=]\s*', '', parts[0].strip(), flags=re.IGNORECASE).strip()
                    tech = [t.strip() for t in parts[1].split(",")] if len(parts) > 1 else []
                    projects.append(ProjectEntity(title=title, description=clean_l, technologies=tech, project_links=self._extract_urls_from_text(clean_l)))
            i += 1

        return projects[:6]

    def _extract_projects_from_section(self, lines: List[str]) -> List[ProjectEntity]:
        """Enhanced project extraction from pre-segmented section with clean titles and full descriptions."""
        projects = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue

            title = ""
            is_title_line = False

            # Pattern 1: "PROJECT TITLE: ..." or "Project Title -..." or "TITLE: ..."
            if "PROJECT TITLE" in line.upper() or "PROJECT:" in line.upper() or "TITLE:" in line.upper():
                title = re.sub(r'^(?:PROJECT\s*)?(?:TITLE|NAME)?\s*[:\-=]\s*', '', line, flags=re.IGNORECASE).strip()
                if not title and i + 1 < len(lines):
                    i += 1
                    title = re.sub(r'^(?:PROJECT\s*)?(?:TITLE|NAME)?\s*[:\-=]\s*', '', lines[i].strip(), flags=re.IGNORECASE).strip()
                is_title_line = True
            # Pattern 2: Lines that are short, capitalized or bold-looking (project names)
            elif len(line) > 4 and len(line) < 100 and not line.startswith("•") and not line.startswith("-"):
                words = line.split()
                if len(words) <= 10:
                    has_description_below = False
                    for check_offset in range(1, 4):
                        if i + check_offset < len(lines):
                            next_l = lines[i + check_offset].strip()
                            if next_l.startswith("•") or next_l.startswith("-") or "TECHNOLOGY" in next_l.upper():
                                has_description_below = True
                                break
                    if has_description_below:
                        title = line
                        is_title_line = True

            if is_title_line and title:
                tech = []
                desc_parts = []
                j = i + 1

                while j < len(lines):
                    next_l = lines[j].strip()
                    if not next_l:
                        j += 1
                        continue

                    # If line looks like another project title, stop
                    if "PROJECT TITLE" in next_l.upper() or "PROJECT:" in next_l.upper() or "TITLE:" in next_l.upper():
                        break

                    # Technology line
                    if "TECHNOLOGY USED" in next_l.upper() or "TECH USED" in next_l.upper() or "TECHNOLOGIES" in next_l.upper():
                        tech_str = re.sub(r'TECHNOLOG(?:Y|IES)\s*USED?\s*[:\-=]?\s*', '', next_l, flags=re.IGNORECASE).strip()
                        tech = [t.strip() for t in tech_str.split(",") if t.strip()]
                        j += 1
                        continue

                    # Clean any OCR bullet noise symbols
                    cleaned_desc = re.sub(r'^[^\w\s\(\)]+\s*', '', next_l).strip()
                    if cleaned_desc and len(cleaned_desc) > 3:
                        desc_parts.append(cleaned_desc)
                        j += 1
                        continue

                    break

                description = " | ".join(desc_parts) if desc_parts else title
                proj_urls = []
                for dp in desc_parts:
                    proj_urls.extend(self.PROJECT_URL_REGEX.findall(dp))
                projects.append(ProjectEntity(title=title, description=description, technologies=tech, project_links=proj_urls))
                i = j
                continue

            i += 1

        return projects[:6]

    # =====================================================================
    #  AWARDS / ACHIEVEMENTS (Categorized)
    # =====================================================================

    def _categorize_achievement(self, text: str) -> str:
        """Classifies an achievement into a category."""
        text_lower = text.lower()
        for category, keywords in self.ACHIEVEMENT_CATEGORIES.items():
            if any(kw in text_lower for kw in keywords):
                return category
        return "Other"

    def _clean_award_line(self, line: str) -> str:
        """Cleans award/achievement text."""
        clean_l = re.sub(r'^[^\w\s\(\)]+\s*', '', line.strip())
        clean_l = re.sub(r'^(?:[mnaouvw@#$%\^&*+=~`▪■•]|â€¢)\s+(?=[A-Z0-9])', '', clean_l, flags=re.IGNORECASE).strip()
        if clean_l and clean_l[0].islower():
            clean_l = clean_l[0].upper() + clean_l[1:]
        return clean_l

    def _extract_categorized_awards(self, lines: List[str]) -> tuple[List[str], List[AchievementEntity]]:
        """Extracts and categorizes awards from pre-segmented ACHIEVEMENTS section lines."""
        awards_flat = []
        categorized = []

        for line in lines:
            clean_l = self._clean_award_line(line)
            if clean_l and not clean_l.startswith("|") and len(clean_l) > 4:
                category = self._categorize_achievement(clean_l)
                awards_flat.append(clean_l)
                categorized.append(AchievementEntity(title=clean_l, category=category))

        return awards_flat[:8], categorized[:8]

    def _extract_categorized_awards_from_text(self, lines: List[str]) -> tuple[List[str], List[AchievementEntity]]:
        """Legacy: extract and categorize awards from flat text lines."""
        awards_flat = []
        categorized = []
        in_sec = False
        for line in lines:
            if any(h in line.lower() for h in ["achievements & certifications", "achievements", "certifications", "awards"]):
                in_sec = True
                continue
            if in_sec and any(h in line.lower() for h in ["education", "experience", "projects", "skills"]):
                in_sec = False
                break
            if in_sec:
                clean_l = self._clean_award_line(line)
                if clean_l and not clean_l.startswith("|") and len(clean_l) > 4:
                    category = self._categorize_achievement(clean_l)
                    awards_flat.append(clean_l)
                    categorized.append(AchievementEntity(title=clean_l, category=category))
            elif any(w in line.lower() for w in ["award", "honor", "grant", "fellowship", "scholarship", "best paper", "runner-up", "prayatna", "hackathon", "winner", "quiz", "certification"]):
                clean_l = self._clean_award_line(line)
                if clean_l:
                    category = self._categorize_achievement(clean_l)
                    awards_flat.append(clean_l)
                    categorized.append(AchievementEntity(title=clean_l, category=category))

        return awards_flat[:8], categorized[:8]

    # =====================================================================
    #  PATENTS & CERTIFICATIONS
    # =====================================================================

    def _extract_patents(self, lines: List[str]) -> List[str]:
        patents = []
        for line in lines:
            if "patent" in line.lower() or "uspto" in line.lower():
                patents.append(line)
        return patents

    def _extract_certifications(self, lines: List[str]) -> List[str]:
        certs = []
        for line in lines:
            if any(c in line.lower() for c in ["certified", "certification", "aws certified", "coursera", "edx", "cognitive class", "certificate"]):
                certs.append(line)
        return certs

    # =====================================================================
    #  CANDIDATE TYPE CLASSIFICATION
    # =====================================================================

    def _classify_candidate_type(
        self,
        experience: List[ExperienceEntity],
        education: List[EducationEntity],
        publications: List[PublicationEntity]
    ) -> str:
        """Classifies candidate as Fresher, Experienced, or Academic."""
        has_experience = len(experience) > 0
        has_publications = len(publications) > 0

        if has_publications and len(publications) >= 3:
            return "Academic"
        if has_experience:
            return "Experienced"

        # Check if education suggests student (ongoing, present, expected)
        for edu in education:
            if edu.year:
                year_lower = edu.year.lower()
                if any(k in year_lower for k in ["present", "expected", "ongoing", "pursuing"]):
                    return "Fresher"

        # No experience = likely fresher
        if not has_experience:
            return "Fresher"

        return "Unknown"

    # =====================================================================
    #  UNCERTAIN SECTIONS (for LLM callback)
    # =====================================================================

    def _find_uncertain_sections(self, lines: List[str]) -> List[str]:
        uncertain = []
        for line in lines:
            if len(line) > 60 and not any(k in line.lower() for k in ["degree", "university", "email", "phone", "http"]):
                if not any(h in line.lower() for h in ["experience", "education", "skills", "projects", "publications"]):
                    uncertain.append(line)
        return uncertain[:5]

    # =====================================================================
    #  CODING SKILLS EXTRACTION (for coding test question generation)
    # =====================================================================

    def _extract_coding_skills(self, all_skills: List[str]) -> List[str]:
        """Filters programming languages and frameworks from the full skills list
        that can be used to generate coding test questions in the next module."""
        coding = []
        for skill in all_skills:
            skill_lower = skill.lower().strip()
            if skill_lower in self.CODING_SKILLS_SET:
                coding.append(skill)
        return list(set(coding))

    # =====================================================================
    #  URL EXTRACTION FROM TEXT (for project links)
    # =====================================================================

    def _extract_urls_from_text(self, text: str) -> List[str]:
        """Extracts HTTP/HTTPS URLs from a given text block."""
        if not text:
            return []
        return list(set(self.PROJECT_URL_REGEX.findall(text)))

    # =====================================================================
    #  CORE INTERVIEW POINTS GENERATION
    # =====================================================================

    def _generate_core_interview_points(
        self,
        name: Optional[str],
        education: List[EducationEntity],
        experience: List[ExperienceEntity],
        skills: List[str],
        publications: List[PublicationEntity],
        projects: List[ProjectEntity],
        awards: List[str],
        candidate_type: str,
        profile_summary: Optional[str],
    ) -> List[str]:
        """Generates key talking points for the faculty interview panel based on
        the candidate's extracted profile. These are heuristic summaries that
        highlight the candidate's strongest attributes and areas to probe."""
        points: List[str] = []

        # 1. Highest qualification
        if education:
            top_edu = education[0]
            points.append(
                f"Highest Qualification: {top_edu.degree}"
                + (f" from {top_edu.institution}" if top_edu.institution else "")
                + (f" ({top_edu.year})" if top_edu.year else "")
                + (f" — GPA/Marks: {top_edu.gpa}" if top_edu.gpa else "")
            )

        # 2. Candidate type
        points.append(f"Candidate Profile Type: {candidate_type}")

        # 3. Teaching / Industry experience summary
        if experience:
            exp_titles = [e.title for e in experience[:3]]
            points.append(f"Key Experience Roles: {', '.join(exp_titles)}")
            if any(kw in ' '.join(exp_titles).lower() for kw in ['professor', 'lecturer', 'teaching', 'faculty', 'instructor']):
                points.append("Has prior teaching/faculty experience — probe pedagogical approach and course design skills.")
            if any(kw in ' '.join(exp_titles).lower() for kw in ['engineer', 'developer', 'architect', 'analyst', 'lead']):
                points.append("Has industry engineering experience — probe practical problem-solving and system design capabilities.")

        # 4. Research output
        if publications:
            points.append(f"Research Output: {len(publications)} publication(s) detected. Probe research methodology, domain expertise, and publication quality.")
            venues = [p.venue for p in publications if p.venue]
            if venues:
                points.append(f"Publication Venues: {', '.join(venues[:3])}")

        # 5. Technical depth
        if skills:
            top_skills = skills[:8]
            points.append(f"Core Technical Competencies ({len(skills)} total): {', '.join(top_skills)}")
            # Detect specialization areas
            skill_lower_set = {s.lower() for s in skills}
            if skill_lower_set & {'machine learning', 'deep learning', 'pytorch', 'tensorflow', 'nlp', 'computer vision'}:
                points.append("Specialization Area: AI/ML — probe depth of understanding in model architectures, training pipelines, and real-world deployment.")
            if skill_lower_set & {'distributed systems', 'microservices', 'kubernetes', 'docker', 'aws', 'azure', 'gcp'}:
                points.append("Specialization Area: Cloud/Systems — probe scalability thinking, infrastructure design, and DevOps maturity.")
            if skill_lower_set & {'react', 'next.js', 'angular', 'vue.js', 'flutter'}:
                points.append("Specialization Area: Frontend/Full-Stack — probe UI/UX sensibility, state management, and performance optimization.")

        # 6. Project highlights
        if projects:
            points.append(f"Projects Built: {len(projects)} project(s). Probe technical decision-making and architecture choices.")
            for proj in projects[:2]:
                point = f"Project: \"{proj.title}\""
                if proj.technologies:
                    point += f" (Tech: {', '.join(proj.technologies[:4])})"
                if proj.project_links:
                    point += f" — Live/Repo Links: {', '.join(proj.project_links[:2])}"
                points.append(point)

        # 7. Awards & achievements
        if awards:
            points.append(f"Notable Achievements: {', '.join(awards[:3])}")

        # 8. Profile summary if available
        if profile_summary and len(profile_summary) > 20:
            points.append(f"Self-Described Summary: \"{profile_summary[:200]}\"")

        return points[:15]
