"""
Resume Structure Graph Builder Engine.
Constructs a Directed Graph linking Sections -> Paragraphs -> Lines -> Words -> Evidence points.
"""

from typing import List
from app.resume_structure.schemas.semantic_resume import GraphEdge, GraphNode, ResumeGraph, SectionNode
from core.logging import get_logger

logger = get_logger("resume_graph_builder")


class ResumeGraphBuilder:
    """DAG Structure Graph Builder Engine."""

    def build_graph(self, doc_uuid: str, sections: List[SectionNode]) -> ResumeGraph:
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        root_id = f"doc_{doc_uuid[:8]}"
        nodes.append(
            GraphNode(
                node_id=root_id,
                node_type="document",
                label="Document Root",
                attributes={"doc_uuid": doc_uuid},
            )
        )

        for sec in sections:
            sec_node_id = f"sec_{sec.section_id[:8]}"
            nodes.append(
                GraphNode(
                    node_id=sec_node_id,
                    node_type="section",
                    label=sec.canonical_type,
                    attributes={
                        "original_heading": sec.original_heading,
                        "confidence": sec.confidence,
                        "pages": sec.page_numbers,
                    },
                    bounding_box=sec.bounding_boxes[0] if sec.bounding_boxes else None,
                )
            )

            # Edge: Document -> Section
            edges.append(
                GraphEdge(
                    source_id=root_id,
                    target_id=sec_node_id,
                    relation_type="contains",
                )
            )

            for b_idx, block in enumerate(sec.blocks):
                block_node_id = f"blk_{block.block_id[:8]}"
                nodes.append(
                    GraphNode(
                        node_id=block_node_id,
                        node_type="block",
                        label=f"Block {b_idx+1}",
                        attributes={"reading_order": block.reading_order, "type": block.block_type},
                        bounding_box=block.coordinates,
                    )
                )

                # Edge: Section -> Block
                edges.append(
                    GraphEdge(
                        source_id=sec_node_id,
                        target_id=block_node_id,
                        relation_type="contains",
                    )
                )

        logger.debug(
            "Resume structure graph generated",
            nodes_count=len(nodes),
            edges_count=len(edges),
        )

        return ResumeGraph(nodes=nodes, edges=edges)
