"""
INDUS AI — Graph Builder

Entry points for building knowledge graph nodes and edges when
entities are created in the system.

Each method:
  1. Creates typed edges via the GraphRepository
  2. Writes an AuditLog entry

The builder does NOT modify any existing modules — it is called
by the GraphService, which is in turn called by API routes.
"""

import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_graph import KnowledgeGraphEdge
from app.models.decision_intelligence import DecisionCase, ReasoningMemory
from app.models.factory_memory_record import FactoryMemoryRecord
from app.models.documents import Document
from app.models.system import AuditLog
from app.knowledge_graph.graph_models import GraphEdge, NodeType, RelationshipType
from app.knowledge_graph.graph_repository import GraphRepository
from app.knowledge_graph.entity_linker import EntityLinker

logger = logging.getLogger(__name__)

# Module-level repository instance
_repo = GraphRepository()


class GraphBuilder:
    """Builds knowledge graph structure when entities are created."""

    # ── Document Created ──────────────────────────────────────────────────

    @staticmethod
    async def on_document_created(
        db: AsyncSession,
        document: Document,
        user_id: str | None = None,
    ) -> List[KnowledgeGraphEdge]:
        """
        Build graph edges when a new document is uploaded.
        Links: DOCUMENT → ENGINEER (uploader)
        """
        edges: List[GraphEdge] = []

        # Link document to its uploader
        if document.uploaded_by:
            edges.append(GraphEdge(
                source_entity_id=str(document.id),
                source_entity_type=NodeType.DOCUMENT,
                relationship_type=RelationshipType.GENERATED_FROM,
                target_entity_id=str(document.uploaded_by),
                target_entity_type=NodeType.ENGINEER,
                properties={"title": document.title, "file_type": document.file_type},
            ))

        if not edges:
            return []

        created = await _repo.create_edges_bulk(db, edges)

        # Audit
        audit = AuditLog(
            user_id=document.uploaded_by,
            action="GRAPH_DOCUMENT_NODE_CREATED",
            details={
                "document_id": str(document.id),
                "title": document.title,
                "edges_created": len(created),
            },
        )
        db.add(audit)

        logger.info(
            "Graph builder: document %s → %d edges", str(document.id)[:8], len(created)
        )
        return created

    # ── Decision Case Created ─────────────────────────────────────────────

    @staticmethod
    async def on_decision_case_created(
        db: AsyncSession,
        decision_case: DecisionCase,
    ) -> List[KnowledgeGraphEdge]:
        """
        Build graph edges when a Decision Case is created.
        Runs the full EntityLinker to extract all relationships.
        """
        # Extract edges via entity linker
        edges = await EntityLinker.extract_edges(db, decision_case)

        if not edges:
            return []

        created = await _repo.create_edges_bulk(db, edges)

        # Audit
        audit = AuditLog(
            user_id=decision_case.user_id,
            decision_case_id=decision_case.id,
            action="GRAPH_DECISION_CASE_NODE_CREATED",
            details={
                "decision_case_id": str(decision_case.id),
                "edges_created": len(created),
                "entity_types_linked": list({e.target_entity_type.value for e in edges}),
            },
        )
        db.add(audit)

        logger.info(
            "Graph builder: decision case %s → %d edges",
            str(decision_case.id)[:8],
            len(created),
        )
        return created

    # ── Factory Memory Created ────────────────────────────────────────────

    @staticmethod
    async def on_factory_memory_created(
        db: AsyncSession,
        memory: FactoryMemoryRecord,
    ) -> List[KnowledgeGraphEdge]:
        """
        Build graph edges when a Factory Memory Record is created.
        Links: FACTORY_MEMORY → DECISION_CASE, MACHINE, ENGINEER
        """
        edges: List[GraphEdge] = []
        mem_id = str(memory.id)

        # Link to decision case
        edges.append(GraphEdge(
            source_entity_id=mem_id,
            source_entity_type=NodeType.FACTORY_MEMORY,
            relationship_type=RelationshipType.LINKED_WITH,
            target_entity_id=str(memory.decision_case_id),
            target_entity_type=NodeType.DECISION_CASE,
        ))

        # Link to machine
        if memory.machine_id:
            edges.append(GraphEdge(
                source_entity_id=mem_id,
                source_entity_type=NodeType.FACTORY_MEMORY,
                relationship_type=RelationshipType.RELATED_TO,
                target_entity_id=str(memory.machine_id),
                target_entity_type=NodeType.MACHINE,
            ))

        # Link to engineer
        edges.append(GraphEdge(
            source_entity_id=mem_id,
            source_entity_type=NodeType.FACTORY_MEMORY,
            relationship_type=RelationshipType.SOLVED_BY,
            target_entity_id=str(memory.engineer_id),
            target_entity_type=NodeType.ENGINEER,
        ))

        created = await _repo.create_edges_bulk(db, edges)

        # Audit
        audit = AuditLog(
            user_id=memory.engineer_id,
            decision_case_id=memory.decision_case_id,
            action="GRAPH_FACTORY_MEMORY_NODE_CREATED",
            details={
                "memory_id": mem_id,
                "edges_created": len(created),
            },
        )
        db.add(audit)

        logger.info(
            "Graph builder: factory memory %s → %d edges", mem_id[:8], len(created)
        )
        return created

    # ── Reasoning Memory Stored ───────────────────────────────────────────

    @staticmethod
    async def on_reasoning_stored(
        db: AsyncSession,
        reasoning: ReasoningMemory,
    ) -> List[KnowledgeGraphEdge]:
        """
        Build graph edges when a Reasoning Memory is stored.
        Links: REASONING_MEMORY → DECISION_CASE
        """
        edges: List[GraphEdge] = []
        reason_id = str(reasoning.id)

        # Link to decision case
        edges.append(GraphEdge(
            source_entity_id=reason_id,
            source_entity_type=NodeType.REASONING_MEMORY,
            relationship_type=RelationshipType.REFERENCES,
            target_entity_id=str(reasoning.decision_case_id),
            target_entity_type=NodeType.DECISION_CASE,
            properties={
                "case_title": reasoning.case_title,
                "outcome": reasoning.outcome_status.value if reasoning.outcome_status else None,
            },
        ))

        created = await _repo.create_edges_bulk(db, edges)

        # Audit
        audit = AuditLog(
            decision_case_id=reasoning.decision_case_id,
            action="GRAPH_REASONING_NODE_CREATED",
            details={
                "reasoning_id": reason_id,
                "case_title": reasoning.case_title,
                "edges_created": len(created),
            },
        )
        db.add(audit)

        logger.info(
            "Graph builder: reasoning %s → %d edges", reason_id[:8], len(created)
        )
        return created
