"""
Component 4: Metadata Extractor.
Extracts document metadata properties into DocumentMetadata model.
"""

from app.document.loader.loaders import LoadedRawDocument
from app.document.schemas.normalized_document import DocumentMetadata
from core.logging import get_logger

logger = get_logger("metadata_extractor")


class MetadataExtractor:
    """Component 4: Document Metadata Extractor."""

    def extract_metadata(
        self, loaded_doc: LoadedRawDocument, file_hash: str, page_count: int
    ) -> DocumentMetadata:
        raw_meta = loaded_doc.metadata_dict

        author = raw_meta.get("Author") or raw_meta.get("author") or raw_meta.get("dc:creator")
        title = raw_meta.get("Title") or raw_meta.get("title") or raw_meta.get("dc:title")
        subject = raw_meta.get("Subject") or raw_meta.get("subject")
        producer = raw_meta.get("Producer") or raw_meta.get("producer")
        creator = raw_meta.get("Creator") or raw_meta.get("creator")
        creation_date = raw_meta.get("CreationDate") or raw_meta.get("creation_date")
        mod_date = raw_meta.get("ModDate") or raw_meta.get("modification_date")

        pdf_version = None
        if loaded_doc.raw_stream.startswith(b"%PDF-"):
            try:
                pdf_version = loaded_doc.raw_stream[:8].decode("utf-8", errors="ignore").replace("%PDF-", "")
            except Exception:
                pass

        metadata = DocumentMetadata(
            file_hash=file_hash,
            author=author,
            title=title,
            subject=subject,
            producer=producer,
            creator=creator,
            creation_date=creation_date,
            modification_date=mod_date,
            page_count=page_count,
            language="en",
            encoding="utf-8",
            pdf_version=pdf_version,
        )

        logger.debug(
            "Extracted document metadata",
            author=author,
            title=title,
            page_count=page_count,
            pdf_version=pdf_version,
        )

        return metadata
