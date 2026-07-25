"""
INDUS AI — Graph Service

High-level service facade for the Knowledge Graph Engine.
Consumed by the API router and exposed for future IDIE integration.

Key methods:
  - search_graph()              — Search and traverse the graph
  - get_case_context()          — IDIE integration point
  - build_for_*()               — Graph construction hooks
  - create_edge()               — Manual edge creation with audit
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision_intelligence import DecisionCase, ReasoningMemory
from app.models.documents import Document
from app.models.factory_memory_record import FactoryMemoryRecord
from app.models.system import AuditLog
from app.models.users import User
from app.knowledge_graph.graph_models import (
    GraphEdge,
    GraphEdgeCreateRequest,
    GraphEdgeResponse,
    GraphSearchResponse,
    CaseContextResponse,
)
from app.knowledge_graph.graph_repository import GraphRepository
from app.knowledge_graph.graph_builder import GraphBuilder
from app.knowledge_graph.graph_search import GraphSearch, _edge_to_response

logger = logging.getLogger(__name__)

# Module-level repository
_repo = GraphRepository()


class GraphService:
    """Facade for all Knowledge Graph operations."""

    # ── Search & Traversal ────────────────────────────────────────────────

    @staticmethod
    async def search_graph(
        db: AsyncSession,
        query: str,
        depth: int = 1,
        limit: int = 50,
    ) -> GraphSearchResponse:
        """Search the knowledge graph by text query with traversal depth."""
        return await GraphSearch.search(db, query, depth=depth, limit=limit)

    @staticmethod
    async def get_case_context(
        db: AsyncSession,
        decision_case_id: str,
    ) -> CaseContextResponse:
        """
        Get full context for a Decision Case.

        IDIE integration point — returns all connected entities
        (machine, documents, incidents, memories, reasoning, compliance, neighbors)
        grouped by type.
        """
        return await GraphSearch.get_case_context(db, decision_case_id)

    # ── Graph Construction Hooks ──────────────────────────────────────────

    @staticmethod
    async def build_for_document(
        db: AsyncSession,
        document: Document,
    ) -> int:
        """Build graph edges when a document is created. Returns edge count."""
        edges = await GraphBuilder.on_document_created(db, document)
        await db.commit()
        return len(edges)

    @staticmethod
    async def build_for_decision_case(
        db: AsyncSession,
        decision_case: DecisionCase,
    ) -> int:
        """Build graph edges when a Decision Case is created. Returns edge count."""
        edges = await GraphBuilder.on_decision_case_created(db, decision_case)
        await db.commit()
        return len(edges)

    @staticmethod
    async def build_for_factory_memory(
        db: AsyncSession,
        memory: FactoryMemoryRecord,
    ) -> int:
        """Build graph edges when a Factory Memory is created. Returns edge count."""
        edges = await GraphBuilder.on_factory_memory_created(db, memory)
        await db.commit()
        return len(edges)

    @staticmethod
    async def build_for_reasoning(
        db: AsyncSession,
        reasoning: ReasoningMemory,
    ) -> int:
        """Build graph edges when Reasoning Memory is stored. Returns edge count."""
        edges = await GraphBuilder.on_reasoning_stored(db, reasoning)
        await db.commit()
        return len(edges)

    # ── Manual Edge Creation ──────────────────────────────────────────────

    @staticmethod
    async def create_edge(
        db: AsyncSession,
        user: User,
        request: GraphEdgeCreateRequest,
    ) -> GraphEdgeResponse:
        """
        Manually create a graph edge. Used by the API for ad-hoc linking.
        Creates an audit log entry.
        """
        edge = GraphEdge(
            source_entity_id=request.source_entity_id,
            source_entity_type=request.source_entity_type,
            relationship_type=request.relationship_type,
            target_entity_id=request.target_entity_id,
            target_entity_type=request.target_entity_type,
            properties=request.properties,
        )

        db_edge = await _repo.create_edge(db, edge)

        # Audit
        audit = AuditLog(
            user_id=user.id,
            action="GRAPH_EDGE_MANUALLY_CREATED",
            details={
                "edge_id": str(db_edge.id),
                "source": f"{request.source_entity_type.value}:{request.source_entity_id}",
                "target": f"{request.target_entity_type.value}:{request.target_entity_id}",
                "relationship": request.relationship_type.value,
            },
        )
        db.add(audit)
        await db.commit()
        await db.refresh(db_edge)

        logger.info(
            "Manual edge created by user %s: %s -[%s]-> %s",
            str(user.id)[:8],
            request.source_entity_id[:8],
            request.relationship_type.value,
            request.target_entity_id[:8],
        )

        return _edge_to_response(db_edge)
