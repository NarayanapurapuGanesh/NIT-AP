"""
Job Description Section Detector Engine.
Segments raw JD text into structural sections: Qualifications, Skills, Experience, Research, Teaching, Responsibilities.
"""

from typing import Dict, List
from core.logging import get_logger

logger = get_logger("job_section_detector")

SECTION_KEYWORDS: Dict[str, List[str]] = {
    "qualifications": ["qualification", "eligibility", "education", "degree"],
    "experience": ["experience", "tenure", "years"],
    "skills": ["skills", "technical skills", "programming", "tools"],
    "research": ["research", "publications", "scopus", "sci", "patents", "projects"],
    "teaching": ["teaching", "courses", "subjects", "pedagogy"],
    "responsibilities": ["duties", "responsibilities", "role", "expectations"],
}


class JobSectionDetector:
    """JD Section Segmentation Engine."""

    def detect_sections(self, raw_text: str) -> Dict[str, str]:
        sections: Dict[str, str] = {}
        lines = raw_text.split("\n")
        current_section = "general"
        buffer: List[str] = []

        for line in lines:
            clean_l = line.strip().lower()
            found_sec = None
            for sec_name, keywords in SECTION_KEYWORDS.items():
                if any(kw in clean_l for kw in keywords) and len(line.strip()) < 50:
                    found_sec = sec_name
                    break

            if found_sec:
                if buffer:
                    sections[current_section] = "\n".join(buffer)
                    buffer = []
                current_section = found_sec
            else:
                buffer.append(line)

        if buffer:
            sections[current_section] = "\n".join(buffer)

        logger.debug("JD Section detection complete", sections_found=list(sections.keys()))
        return sections
