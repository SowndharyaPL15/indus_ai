"""
INDUS AI — Graph Repository

Data access layer for the knowledge_graph_edges table.

Architecture:
  - GraphStorageBackend (Protocol) — abstract interface for graph storage
  - PostgresGraphBackend           — current SQLAlchemy implementation
  - GraphRepository                — facade that delegates to the configured backend

To migrate to Neo4j later, implement Neo4jGraphBackend and swap it in
GraphRepository without changing the service, builder, or search layers.
"""

import json
import logging
from typing import List, Optional, Protocol, runtime_checkable
from uuid import UUID

from sqlalchemy import select, or_, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_graph import KnowledgeGraphEdge
from app.knowledge_graph.graph_models import GraphEdge

logger = logging.getLogger(__name__)


# ── Storage Backend Protocol ──────────────────────────────────────────────────

@runtime_checkable
class GraphStorageBackend(Protocol):
    """
    Abstract interface for graph storage operations.
    Implement this to swap in Neo4j or another graph database.
    """

    async def create_edge(
        self, db: AsyncSession, edge: GraphEdge
    ) -> KnowledgeGraphEdge: ...

    async def get_edges_for_entity(
        self, db: AsyncSession, entity_id: str, entity_type: Optional[str] = None
    ) -> List[KnowledgeGraphEdge]: ...

    async def get_edges_by_relationship(
        self, db: AsyncSession, relationship_type: str
    ) -> List[KnowledgeGraphEdge]: ...

    async def search_edges(
        self, db: AsyncSession, query: str, limit: int = 50
    ) -> List[KnowledgeGraphEdge]: ...

    async def delete_edge(
        self, db: AsyncSession, edge_id: UUID
    ) -> bool: ...


# ── PostgreSQL Backend ────────────────────────────────────────────────────────

class PostgresGraphBackend:
    """SQLAlchemy-based implementation using the knowledge_graph_edges table."""

    async def create_edge(
        self, db: AsyncSession, edge: GraphEdge
    ) -> KnowledgeGraphEdge:
        properties_str = json.dumps(edge.properties) if edge.properties else None

        db_edge = KnowledgeGraphEdge(
            source_entity_id=edge.source_entity_id,
            source_entity_type=edge.source_entity_type.value,
            relationship_type=edge.relationship_type.value,
            target_entity_id=edge.target_entity_id,
            target_entity_type=edge.target_entity_type.value,
            properties=properties_str,
        )
        db.add(db_edge)
        await db.flush()
        await db.refresh(db_edge)

        logger.info(
            "Edge created: %s -[%s]-> %s",
            edge.source_entity_id[:8],
            edge.relationship_type.value,
            edge.target_entity_id[:8],
        )
        return db_edge

    async def get_edges_for_entity(
        self, db: AsyncSession, entity_id: str, entity_type: Optional[str] = None
    ) -> List[KnowledgeGraphEdge]:
        """Get all edges where the entity is either source or target."""
        conditions = [
            or_(
                KnowledgeGraphEdge.source_entity_id == entity_id,
                KnowledgeGraphEdge.target_entity_id == entity_id,
            )
        ]
        if entity_type:
            conditions.append(
                or_(
                    KnowledgeGraphEdge.source_entity_type == entity_type,
                    KnowledgeGraphEdge.target_entity_type == entity_type,
                )
            )

        stmt = select(KnowledgeGraphEdge).where(and_(*conditions))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_edges_by_relationship(
        self, db: AsyncSession, relationship_type: str
    ) -> List[KnowledgeGraphEdge]:
        stmt = select(KnowledgeGraphEdge).where(
            KnowledgeGraphEdge.relationship_type == relationship_type
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def search_edges(
        self, db: AsyncSession, query: str, limit: int = 50
    ) -> List[KnowledgeGraphEdge]:
        """Search edges by entity ID prefix or properties content."""
        pattern = f"%{query}%"
        stmt = (
            select(KnowledgeGraphEdge)
            .where(
                or_(
                    KnowledgeGraphEdge.source_entity_id.ilike(pattern),
                    KnowledgeGraphEdge.target_entity_id.ilike(pattern),
                    KnowledgeGraphEdge.properties.ilike(pattern),
                    KnowledgeGraphEdge.source_entity_type.ilike(pattern),
                    KnowledgeGraphEdge.target_entity_type.ilike(pattern),
                    KnowledgeGraphEdge.relationship_type.ilike(pattern),
                )
            )
            .order_by(KnowledgeGraphEdge.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def delete_edge(
        self, db: AsyncSession, edge_id: UUID
    ) -> bool:
        stmt = delete(KnowledgeGraphEdge).where(KnowledgeGraphEdge.id == edge_id)
        result = await db.execute(stmt)
        return result.rowcount > 0


# ── Repository Facade ─────────────────────────────────────────────────────────

class GraphRepository:
    """
    Facade that delegates to the configured storage backend.
    Service and search layers call this — never the backend directly.
    """

    def __init__(self, backend: GraphStorageBackend | None = None):
        self._backend = backend or PostgresGraphBackend()

    async def create_edge(
        self, db: AsyncSession, edge: GraphEdge
    ) -> KnowledgeGraphEdge:
        return await self._backend.create_edge(db, edge)

    async def create_edges_bulk(
        self, db: AsyncSession, edges: List[GraphEdge]
    ) -> List[KnowledgeGraphEdge]:
        """Create multiple edges in a single transaction."""
        created = []
        for edge in edges:
            db_edge = await self._backend.create_edge(db, edge)
            created.append(db_edge)
        logger.info("Bulk created %d edges", len(created))
        return created

    async def get_edges_for_entity(
        self, db: AsyncSession, entity_id: str, entity_type: Optional[str] = None
    ) -> List[KnowledgeGraphEdge]:
        return await self._backend.get_edges_for_entity(db, entity_id, entity_type)

    async def get_edges_by_relationship(
        self, db: AsyncSession, relationship_type: str
    ) -> List[KnowledgeGraphEdge]:
        return await self._backend.get_edges_by_relationship(db, relationship_type)

    async def search_edges(
        self, db: AsyncSession, query: str, limit: int = 50
    ) -> List[KnowledgeGraphEdge]:
        return await self._backend.search_edges(db, query, limit)

    async def delete_edge(
        self, db: AsyncSession, edge_id: UUID
    ) -> bool:
        return await self._backend.delete_edge(db, edge_id)
