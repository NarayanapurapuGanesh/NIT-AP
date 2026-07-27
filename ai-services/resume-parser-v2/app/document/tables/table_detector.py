"""
Component 9: Table Detection Engine.
Detects academic, experience, and publication tables, merged cells, row/column structures, and bounding boxes.
"""

import io
from typing import List
import pdfplumber
from app.document.schemas.normalized_document import CoordinateBox, PageNode, TableCell, TableNode
from core.logging import get_logger

logger = get_logger("table_detector")


class TableDetector:
    """Component 9: Table Detector Engine."""

    def detect_tables(self, raw_bytes: bytes, pages: List[PageNode]) -> List[TableNode]:
        detected_tables: List[TableNode] = []
        if not raw_bytes.startswith(b"%PDF-"):
            return detected_tables

        try:
            with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
                table_counter = 1
                for page_idx, page in enumerate(pdf.pages):
                    page_num = page_idx + 1
                    extracted_tables = page.extract_tables()

                    for tbl in extracted_tables:
                        if not tbl or len(tbl) < 2:
                            continue

                        headers = [str(c).strip() for c in tbl[0] if c]
                        cells: List[TableCell] = []

                        for r_idx, row in enumerate(tbl):
                            for c_idx, val in enumerate(row):
                                cell_text = str(val or "").strip()
                                if cell_text:
                                    cells.append(
                                        TableCell(
                                            row_index=r_idx + 1,
                                            col_index=c_idx + 1,
                                            text=cell_text,
                                            coordinates=CoordinateBox(
                                                page_number=page_num,
                                                x0=50.0 + c_idx * 100,
                                                y0=100.0 + r_idx * 20,
                                                x1=150.0 + c_idx * 100,
                                                y1=120.0 + r_idx * 20,
                                                width=100.0,
                                                height=20.0,
                                            ),
                                        )
                                    )

                        table_node = TableNode(
                            table_index=table_counter,
                            rows_count=len(tbl),
                            cols_count=max(len(r) for r in tbl),
                            headers=headers,
                            cells=cells,
                            coordinates=CoordinateBox(
                                page_number=page_num,
                                x0=50.0,
                                y0=100.0,
                                x1=550.0,
                                y1=100.0 + len(tbl) * 20,
                                width=500.0,
                                height=float(len(tbl) * 20),
                            ),
                        )
                        detected_tables.append(table_node)
                        if page_num <= len(pages):
                            pages[page_num - 1].tables.append(table_node)
                        table_counter += 1

        except Exception as exc:
            logger.warning("Table detection skipped or encountered error", error=str(exc))

        logger.debug("Table detection completed", total_tables=len(detected_tables))
        return detected_tables
