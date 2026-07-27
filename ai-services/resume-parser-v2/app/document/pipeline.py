"""
End-to-End Enterprise Document Ingestion & Extraction Pipeline.
Orchestrates Validation, Physical Classification, Loading, Metadata, Enterprise Text Extraction, OCR Fallback,
Reading Order Reconstruction, Layout Analysis, Table & Image Detection, Coordinate Mapping, Evidence Traceability,
and Statistics Computation.
"""

import time
import uuid
from app.document.classification.classification_engine import IngestionClassificationEngine
from app.document.coordinates.coordinate_mapper import CoordinateMapper
from app.document.evidence.evidence_builder import EvidenceBuilder
from app.document.extractors.text_extractor import EnterpriseTextExtractor
from app.document.images.image_detector import ImageDetector
from app.document.layout.layout_analysis import LayoutAnalysisEngine
from app.document.loader.loaders import DocumentLoaderFactory
from app.document.metadata.metadata_extractor import MetadataExtractor
from app.document.ocr.ocr_engine import OcrFallbackEngine
from app.document.reading_order.reading_order_engine import ReadingOrderEngine
from app.document.schemas.normalized_document import NormalizedDocument
from app.document.statistics.statistics_engine import StatisticsEngine
from app.document.tables.table_detector import TableDetector
from app.document.validation.validation_engine import DocumentValidationEngine
from core.logging import get_logger

logger = get_logger("document_ingestion_pipeline")


class DocumentIngestionPipeline:
    """Enterprise Document Ingestion & Extraction Pipeline Engine."""

    def __init__(self) -> None:
        self.validation_engine = DocumentValidationEngine()
        self.classification_engine = IngestionClassificationEngine()
        self.loader_factory = DocumentLoaderFactory()
        self.metadata_extractor = MetadataExtractor()
        self.text_extractor = EnterpriseTextExtractor()
        self.ocr_engine = OcrFallbackEngine()
        self.reading_order_engine = ReadingOrderEngine()
        self.layout_analysis_engine = LayoutAnalysisEngine()
        self.table_detector = TableDetector()
        self.image_detector = ImageDetector()
        self.coordinate_mapper = CoordinateMapper()
        self.evidence_builder = EvidenceBuilder()
        self.statistics_engine = StatisticsEngine()

    async def ingest_document(self, filename: str, content: bytes) -> NormalizedDocument:
        """Executes full ingestion pipeline and returns canonical NormalizedDocument object."""
        start_time = time.perf_counter()
        doc_uuid = str(uuid.uuid4())

        # Step 1: Validation
        val_result = self.validation_engine.validate_document(filename, content)

        # Step 2: Loader
        loader = self.loader_factory.get_loader(val_result.format_type)
        loaded_doc = loader.load(content)

        # Step 3: Text & Structure Extraction
        pages, primary_engine = self.text_extractor.extract_structure(loaded_doc)

        # Step 4: OCR Fallback check
        ocr_conf = 1.0
        if self.ocr_engine.should_trigger_ocr(pages):
            pages, ocr_conf = self.ocr_engine.process_ocr_fallback(content, pages)
            primary_engine = "ocr_fallback"

        # Step 5: Physical Classification
        raw_pages_text = [p.text for p in pages]
        images_count = sum(len(p.images) for p in pages)
        class_detail = self.classification_engine.classify_physical_document(
            format_type=val_result.format_type,
            raw_pages=raw_pages_text,
            images_count=images_count,
            is_scanned_flag=primary_engine == "ocr_fallback",
        )

        # Step 6: Metadata Extraction
        metadata = self.metadata_extractor.extract_metadata(
            loaded_doc=loaded_doc,
            file_hash=val_result.file_hash,
            page_count=len(pages),
        )
        metadata.document_uuid = doc_uuid

        # Step 7: Layout Analysis
        pages = self.layout_analysis_engine.analyze_layout(pages)

        # Step 8: Reading Order Reconstruction
        reading_order_blocks = self.reading_order_engine.reconstruct_reading_order(pages)

        # Step 9: Table Detection
        detected_tables = self.table_detector.detect_tables(content, pages)

        # Step 10: Image Detection
        detected_images = self.image_detector.detect_images(content, pages)

        # Step 11: Coordinate Mapping
        pages = self.coordinate_mapper.map_coordinates(pages)

        # Step 12: Evidence Traceability
        self.evidence_builder.build_evidence_registry(pages)

        # Step 13: Statistics Computation
        statistics = self.statistics_engine.compute_statistics(
            pages=pages,
            ocr_confidence=ocr_conf,
            engine_used=primary_engine,
        )

        processing_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

        normalized_doc = NormalizedDocument(
            document_uuid=doc_uuid,
            filename=filename,
            format_type=val_result.format_type,
            classification_type=class_detail.doc_class,
            metadata=metadata,
            statistics=statistics,
            pages=pages,
            reading_order_blocks=reading_order_blocks,
            tables=detected_tables,
            images=detected_images,
            processing_time_ms=processing_time_ms,
        )

        logger.info(
            "Document ingestion pipeline complete",
            doc_uuid=doc_uuid,
            filename=filename,
            classification=class_detail.doc_class,
            pages=len(pages),
            duration_ms=processing_time_ms,
        )

        return normalized_doc
