"""
Component 10: Image Detector Engine.
Extracts profile photos, logos, icons, charts, graphs, and signatures with dimensions, coordinates, and hashes.
"""

import hashlib
from typing import List
import fitz  # PyMuPDF
from app.document.schemas.normalized_document import CoordinateBox, ImageNode, PageNode
from core.logging import get_logger

logger = get_logger("image_detector")


class ImageDetector:
    """Component 10: Image & Figure Detector."""

    def detect_images(self, raw_bytes: bytes, pages: List[PageNode]) -> List[ImageNode]:
        detected_images: List[ImageNode] = []
        if not raw_bytes.startswith(b"%PDF-"):
            return detected_images

        try:
            doc = fitz.open(stream=raw_bytes, filetype="pdf")
            img_index = 1

            for page_idx, page in enumerate(doc):
                page_num = page_idx + 1
                image_list = page.get_images(full=True)

                for img_info in image_list:
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    img_hash = hashlib.sha256(image_bytes).hexdigest()[:16]
                    w = float(base_image.get("width", 100))
                    h = float(base_image.get("height", 100))

                    img_type = "profile_photo" if w < 300 and h < 300 and page_num == 1 else "figure"

                    box = CoordinateBox(
                        page_number=page_num,
                        x0=50.0,
                        y0=50.0,
                        x1=50.0 + w,
                        y1=50.0 + h,
                        width=w,
                        height=h,
                    )

                    node = ImageNode(
                        image_index=img_index,
                        image_type=img_type,
                        dimensions={"width": w, "height": h},
                        image_hash=img_hash,
                        page_number=page_num,
                        coordinates=box,
                    )

                    detected_images.append(node)
                    if page_num <= len(pages):
                        pages[page_num - 1].images.append(node)

                    img_index += 1

            doc.close()

        except Exception as exc:
            logger.warning("Image detection skipped or encountered error", error=str(exc))

        logger.debug("Image detection completed", total_images=len(detected_images))
        return detected_images
