"""
End-to-End Enterprise Resume Structure Intelligence Pipeline.
Orchestrates Heading Intelligence, 40+ Section Classification, Reading Flow Verification,
Hierarchy Tree Building, Resume Structure Graph, Evidence Linking, Normalization, and Structural Validation.
"""

import time
from app.document.schemas.normalized_document import NormalizedDocument
from app.resume_structure.evidence.evidence_linker import EvidenceLinker
from app.resume_structure.flow_analyzer.flow_analyzer import ReadingFlowAnalyzer
from app.resume_structure.hierarchy.hierarchy_builder import SectionHierarchyBuilder
from app.resume_structure.normalizers.structure_normalizer import StructureNormalizer
from app.resume_structure.resume_graph.graph_builder import ResumeGraphBuilder
from app.resume_structure.schemas.semantic_resume import SemanticResumeModel
from app.resume_structure.section_detector.section_detector import SectionDetectorEngine
from app.resume_structure.validators.structure_validator import StructureValidatorEngine
from core.logging import get_logger

logger = get_logger("resume_structure_pipeline")


class ResumeStructurePipeline:
    """Enterprise Resume Structure Intelligence Pipeline Engine."""

    def __init__(self) -> None:
        self.section_detector = SectionDetectorEngine()
        self.flow_analyzer = ReadingFlowAnalyzer()
        self.hierarchy_builder = SectionHierarchyBuilder()
        self.graph_builder = ResumeGraphBuilder()
        self.evidence_linker = EvidenceLinker()
        self.structure_normalizer = StructureNormalizer()
        self.validator_engine = StructureValidatorEngine()

    async def process_structure(self, normalized_doc: NormalizedDocument) -> SemanticResumeModel:
        """Processes NormalizedDocument (NDO) and converts it into a SemanticResumeModel."""
        start_time = time.perf_counter()

        # Step 1: Detect & Segment Sections
        raw_sections, header_block, summary_block = self.section_detector.detect_sections(normalized_doc.pages)

        # Step 2: Structure Normalization (Deduplication & Formatting)
        normalized_sections = self.structure_normalizer.normalize_sections(raw_sections)

        # Step 3: Reading Flow Analysis
        sections, flow_warnings = self.flow_analyzer.analyze_flow(normalized_sections)

        # Step 4: Evidence Linking
        sections = self.evidence_linker.link_evidence(sections)

        # Step 5: Build Hierarchy Tree
        hierarchy_tree = self.hierarchy_builder.build_hierarchy_tree(sections)

        # Step 6: Build Resume Structure Graph
        structure_graph = self.graph_builder.build_graph(normalized_doc.document_uuid, sections)

        # Step 7: Structural Validation
        val_report = self.validator_engine.validate_structure(sections, flow_warnings)

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        semantic_model = SemanticResumeModel(
            document_uuid=normalized_doc.document_uuid,
            filename=normalized_doc.filename,
            header_block=header_block,
            summary_block=summary_block,
            sections=sections,
            hierarchy_tree=hierarchy_tree,
            structure_graph=structure_graph,
            validation_report=val_report,
            processing_time_ms=processing_time_ms,
        )

        logger.info(
            "Resume structure intelligence pipeline complete",
            doc_uuid=normalized_doc.document_uuid,
            sections_count=len(sections),
            graph_nodes=len(structure_graph.nodes),
            duration_ms=processing_time_ms,
        )

        return semantic_model
