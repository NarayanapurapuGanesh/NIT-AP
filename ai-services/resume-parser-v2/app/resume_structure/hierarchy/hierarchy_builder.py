"""
Section Hierarchy Tree Builder.
Constructs hierarchical tree representation (Resume -> Primary Section -> Sub-Section -> Block Nodes).
"""

from typing import List
from app.resume_structure.schemas.semantic_resume import HierarchyNode, SectionNode
from core.logging import get_logger

logger = get_logger("hierarchy_builder")


class SectionHierarchyBuilder:
    """Composite Hierarchy Tree Builder Engine."""

    def build_hierarchy_tree(self, sections: List[SectionNode]) -> HierarchyNode:
        root = HierarchyNode(name="Resume", level=0, section_type="Root")

        # Map sections into H1 vs H2 children
        current_h1_node: HierarchyNode | None = None

        for sec in sections:
            block_ids = [b.block_id for b in sec.blocks]
            node = HierarchyNode(
                name=sec.original_heading,
                level=sec.heading_level,
                section_type=sec.canonical_type,
                block_ids=block_ids,
            )

            if sec.heading_level == 1:
                root.children.append(node)
                current_h1_node = node
            elif sec.heading_level == 2:
                if current_h1_node:
                    current_h1_node.children.append(node)
                else:
                    root.children.append(node)
            else:
                if current_h1_node and current_h1_node.children:
                    current_h1_node.children[-1].children.append(node)
                elif current_h1_node:
                    current_h1_node.children.append(node)
                else:
                    root.children.append(node)

        logger.debug("Section hierarchy tree generated", root_children=len(root.children))
        return root
