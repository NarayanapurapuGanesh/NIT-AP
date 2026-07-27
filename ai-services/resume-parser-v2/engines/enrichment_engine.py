from typing import List, Tuple
from pydantic import BaseModel

from extractors.link_discovery import ProfileLinkDiscoveryEngine, ProfileLinks
from services.profile_collector import ProfileCollectorService, ProfileEvidencePackage

class EnrichmentEngine:
    """Engine 3: Enrichment Engine.
    
    Discovers social/professional links and fetches external evidence from those platforms.
    """
    
    def __init__(self, offline_mode: bool = False):
        self.link_discovery = ProfileLinkDiscoveryEngine()
        self.profile_collector = ProfileCollectorService(offline_mode=offline_mode)

    async def enrich_profile(self, raw_text: str, pdf_annotation_links: List[str] = None) -> Tuple[ProfileLinks, ProfileEvidencePackage]:
        """Discovers links and collects external evidence concurrently if possible."""
        
        # 1. Discover Links (from text regex and raw PDF hyperlinks)
        profiles = self.link_discovery.discover_links(raw_text, pdf_annotation_links=pdf_annotation_links or [])
        
        # 2. Collect External Evidence (GitHub, LinkedIn)
        external_evidence = await self.profile_collector.collect_profiles(profiles)
        
        return profiles, external_evidence
