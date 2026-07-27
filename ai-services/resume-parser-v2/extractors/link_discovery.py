"""
Profile Link Discovery Engine (Module 5).

Automatically scans document text AND embedded PDF hyperlink annotations to discover candidate professional links:
- LinkedIn (e.g. linkedin.com/in/username or embedded link)
- GitHub (e.g. github.com/username or embedded link)
- CodeChef (e.g. codechef.com/users/username or codechef.com/username)
- Google Scholar (e.g. scholar.google.com/citations?user=...)
- ResearchGate (e.g. researchgate.net/profile/username)
- Kaggle (e.g. kaggle.com/username)
- LeetCode (e.g. leetcode.com/u/username or leetcode.com/username)
- HackerRank (e.g. hackerrank.com/username)
- Portfolio / Personal website
- ORCID
- Medium
"""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProfileLinks(BaseModel):
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio: Optional[str] = Field(None, description="Personal website or portfolio URL")
    orcid: Optional[str] = Field(None, description="ORCID profile URL or ID")
    google_scholar: Optional[str] = Field(None, description="Google Scholar profile URL")
    researchgate: Optional[str] = Field(None, description="ResearchGate profile URL")
    kaggle: Optional[str] = Field(None, description="Kaggle profile URL")
    codechef: Optional[str] = Field(None, description="CodeChef profile URL")
    codeforces: Optional[str] = Field(None, description="Codeforces profile URL")
    leetcode: Optional[str] = Field(None, description="LeetCode profile URL")
    hackerrank: Optional[str] = Field(None, description="HackerRank profile URL")
    medium: Optional[str] = Field(None, description="Medium profile URL")
    other_urls: List[str] = Field(default_factory=list, description="Other web links discovered")


class ProfileLinkDiscoveryEngine:
    """Bulletproof link discovery engine parsing plaintext and PDF annotation hyperlink URIs."""

    URL_REGEX = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+|(?:github|linkedin|codechef|leetcode|hackerrank|kaggle|researchgate|orcid)\.com/[^\s<>"]+', re.IGNORECASE)

    PATTERNS = {
        "linkedin": re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/(?:in|pub|profile)/[a-zA-Z0-9_-]+/?', re.IGNORECASE),
        "github": re.compile(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?', re.IGNORECASE),
        "codechef": re.compile(r'(?:https?://)?(?:www\.)?codechef\.com/(?:users/)?[a-zA-Z0-9_-]+/?', re.IGNORECASE),
        "google_scholar": re.compile(r'(?:https?://)?scholar\.google\.[a-z.]+/citations\?[^\s<>"]+', re.IGNORECASE),
        "researchgate": re.compile(r'(?:https?://)?(?:www\.)?researchgate\.net/profile/[a-zA-Z0-9_-]+/?', re.IGNORECASE),
        "kaggle": re.compile(r'(?:https?://)?(?:www\.)?kaggle\.com/[a-zA-Z0-9_-]+/?', re.IGNORECASE),
        "leetcode": re.compile(r'(?:https?://)?(?:www\.)?leetcode\.com/(?:u/)?[a-zA-Z0-9_-]+/?', re.IGNORECASE),
        "hackerrank": re.compile(r'(?:https?://)?(?:www\.)?hackerrank\.com/(?:profile/)?[a-zA-Z0-9_-]+/?', re.IGNORECASE),
        "codeforces": re.compile(r'(?:https?://)?(?:www\.)?codeforces\.com/profile/[a-zA-Z0-9_-]+/?', re.IGNORECASE),
        "orcid": re.compile(r'(?:https?://)?(?:www\.)?orcid\.org/\d{4}-\d{4}-\d{4}-\d{3}[\dX]', re.IGNORECASE),
        "medium": re.compile(r'(?:https?://)?(?:www\.)?medium\.com/@[a-zA-Z0-9_-]+/?', re.IGNORECASE),
    }

    # Backup text patterns like "GitHub: ganesh", "LinkedIn: ganesh", "CodeChef: ganesh"
    HANDLE_PATTERNS = {
        "github": re.compile(r'\bgithub\s*[:\-=]\s*([a-zA-Z0-9_-]+)', re.IGNORECASE),
        "linkedin": re.compile(r'\blinkedin\s*[:\-=]\s*([a-zA-Z0-9_-]+)', re.IGNORECASE),
        "codechef": re.compile(r'\bcodechef\s*[:\-=]\s*([a-zA-Z0-9_-]+)', re.IGNORECASE),
        "leetcode": re.compile(r'\bleetcode\s*[:\-=]\s*([a-zA-Z0-9_-]+)', re.IGNORECASE),
        "hackerrank": re.compile(r'\bhackerrank\s*[:\-=]\s*([a-zA-Z0-9_-]+)', re.IGNORECASE),
        "kaggle": re.compile(r'\bkaggle\s*[:\-=]\s*([a-zA-Z0-9_-]+)', re.IGNORECASE),
    }

    def discover_links(self, text: str, pdf_annotation_links: Optional[List[str]] = None) -> ProfileLinks:
        """Discovers candidate social & research profiles across text and PDF hyperlinked annotations."""
        combined_text = text
        if pdf_annotation_links:
            combined_text += "\n" + "\n".join(pdf_annotation_links)

        raw_urls = self.URL_REGEX.findall(combined_text)
        links = ProfileLinks()
        matched_urls = set()

        # 1. Regex URL matching
        for key, pattern in self.PATTERNS.items():
            match = pattern.search(combined_text)
            if match:
                url = match.group(0)
                if not url.startswith("http"):
                    url = "https://" + url
                setattr(links, key, url)
                matched_urls.add(match.group(0))

        # 2. Handle pattern matching fallback (e.g. "GitHub: username")
        for key, pattern in self.HANDLE_PATTERNS.items():
            if not getattr(links, key):
                match = pattern.search(text)
                if match:
                    username = match.group(1)
                    if key == "linkedin":
                        setattr(links, key, f"https://linkedin.com/in/{username}")
                    elif key == "codechef":
                        setattr(links, key, f"https://codechef.com/users/{username}")
                    else:
                        setattr(links, key, f"https://{key}.com/{username}")

        # 3. Personal portfolio / other links
        other = []
        for url in raw_urls:
            if not any(m in url for m in matched_urls):
                clean_url = url if url.startswith("http") else "https://" + url
                if not links.portfolio and not any(domain in url.lower() for domain in ["linkedin", "github", "google", "researchgate", "orcid", "codechef", "leetcode", "kaggle"]):
                    links.portfolio = clean_url
                else:
                    other.append(clean_url)

        links.other_urls = other
        return links
