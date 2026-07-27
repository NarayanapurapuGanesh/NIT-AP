import re
from typing import Tuple

from llm.qwen_callback import QwenCallbackLLM
from extractors.deterministic_extractor import DeterministicEntities, ProjectEntity
from schemas.enterprise_profile import FieldConfidenceScores
from engines.schemas import SpatialLayoutDocument


class CallbackLLMEngine:
    """Engine 5: Callback LLM Engine.
    
    Targeted fallback orchestrator. It uses the local Qwen2.5 model to recover 
    information specifically from structurally broken sections or low confidence documents.
    """
    
    def __init__(self):
        self.qwen_llm = QwenCallbackLLM()

    async def recover_entities(
        self,
        entities: DeterministicEntities,
        confidence: FieldConfidenceScores,
        layout_doc: SpatialLayoutDocument
    ) -> DeterministicEntities:
        """Invokes the LLM callback if confidence is below threshold or sections are missing."""
        
        # Determine if recovery is needed
        needs_recovery = (
            confidence.overall_average < 85.0 or 
            bool(entities.uncertain_sections) or 
            len(layout_doc.sections) == 0 or
            len(entities.skills) < 3 or
            not entities.experience
        )
        
        if not needs_recovery:
            return entities

        # Gather texts to process
        target_paragraphs = list(entities.uncertain_sections) if entities.uncertain_sections else []
        
        # Add UNKNOWN sections from layout_doc that might contain missing entities
        for sec in layout_doc.sections:
            if sec.section_name == "UNKNOWN":
                content = "\n".join(sec.content_lines)
                if content and len(content) > 30:
                    target_paragraphs.append(content[:2000]) # Cap at 2000 chars per block to avoid token limits
                    
        # Remove exact duplicates
        unique_paras = []
        for p in target_paragraphs:
            if p not in unique_paras:
                unique_paras.append(p)

        # Target paragraphs sequentially
        if unique_paras:
            from extractors.deterministic_extractor import DeterministicExtractor
            
            for uncertain_para in unique_paras[:5]:
                print(f"[DEBUG Engine 5] Processing paragraph of length {len(uncertain_para)}")
                # Force deterministic skill matching for large unrecognized blocks
                try:
                    text_words = [re.sub(r'[^a-zA-Z0-9+#.-]', '', w).lower() for w in uncertain_para.split()]
                    found_skills = [w.title() for w in text_words if w in DeterministicExtractor.COMMON_SKILLS]
                    if found_skills:
                        entities.skills = list(set(entities.skills + found_skills))
                        print(f"[DEBUG Engine 5] Found deterministic skills: {found_skills}")
                except Exception as e:
                    print(f"[DEBUG Engine 5] Deterministic skill matching error: {e}")
                    pass
                
                try:
                    llm_res = await self.qwen_llm.classify_uncertain_paragraph(uncertain_para)
                    
                    if llm_res.classification == "Skills" and llm_res.extracted_entities:
                        # Merge new skills
                        entities.skills = list(set(entities.skills + llm_res.extracted_entities))
                        
                    elif llm_res.classification == "Projects" and llm_res.extracted_entities:
                        # Merge new projects
                        for p_title in llm_res.extracted_entities:
                            if not any(p.title.lower() == p_title.lower() for p in entities.projects):
                                entities.projects.append(
                                    ProjectEntity(title=p_title, description=uncertain_para[:200])
                                )
                                
                    elif llm_res.classification == "Responsibilities" and llm_res.extracted_entities:
                        # Merge new experience/soft skills
                        if not hasattr(entities, "soft_skills") or entities.soft_skills is None:
                            entities.soft_skills = []
                        entities.soft_skills = list(set(entities.soft_skills + llm_res.extracted_entities))
                        
                except Exception as e:
                    # Fail gracefully if Ollama is unreachable
                    import structlog
                    logger = structlog.get_logger()
                    logger.warning("CallbackLLMEngine failed to reach Qwen", error=str(e))
                    break
        
        return entities
