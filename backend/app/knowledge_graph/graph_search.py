"""
INDUS AI — Graph Search

Graph traversal and search operations for the Knowledge Graph.

Key methods:
  - search()            — Find edges matching a query, return connected entities
  - get_neighbors()     — BFS traversal returning entities within N hops
  - get_case_context()  — IDIE integration point: full context for a decision case
"""

import json
import logging
from collections import defaultdict
from typing import List, Set, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_graph import KnowledgeGraphEdge
from app.knowledge_graph.graph_models import (
    NodeType,
    RelationshipType,
    ConnectedEntity,
    GraphEdgeResponse,
    GraphSearchResponse,
    CaseContextGroup,
    CaseContextResponse,
)
from app.knowledge_graph.graph_repository import GraphRepository

logger = logging.getLogger(__name__)

# Module-level repository
_repo = GraphRepository()


class GraphSearch:
    """Graph traversal and search operations."""

    # ── Text Search ───────────────────────────────────────────────────────

    @staticmethod
    async def search(
        db: AsyncSession,
        query: str,
        depth: int = 1,
        limit: int = 50,
    ) -> GraphSearchResponse:
        """
        Search for edges matching the query, then traverse to discover
        connected entities up to the specified depth.
        """
        # Phase 1: Find matching edges
        raw_edges = await _repo.search_edges(db, query, limit=limit)

        # Collect seed entity IDs from matching edges
        seed_ids: Set[str] = set()
        for edge in raw_edges:
            seed_ids.add(edge.source_entity_id)
            seed_ids.add(edge.target_entity_id)

        # Phase 2: BFS traversal from seeds
        connected: List[ConnectedEntity] = []
        if depth > 1 and seed_ids:
            for entity_id in list(seed_ids)[:10]:  # Limit seeds to prevent explosion
                neighbors = await GraphSearch._bfs_traverse(db, entity_id, depth - 1)
                connected.extend(neighbors)

        # Deduplicate connected entities
        seen: Set[str] = set()
        unique_connected: List[ConnectedEntity] = []
        for entity in connected:
            key = f"{entity.entity_id}:{entity.entity_type.value}"
            if key not in seen:
                seen.add(key)
                unique_connected.append(entity)

        # Format edge responses
        edge_responses = [_edge_to_response(e) for e in raw_edges]

        return GraphSearchResponse(
            query=query,
            edges=edge_responses,
            connected_entities=unique_connected,
            total_edges=len(edge_responses),
            depth=depth,
        )

    # ── Neighbor Traversal ────────────────────────────────────────────────

    @staticmethod
    async def get_neighbors(
        db: AsyncSession,
        entity_id: str,
        entity_type: str | None = None,
        depth: int = 1,
    ) -> List[ConnectedEntity]:
        """BFS traversal returning all entities within N hops."""
        return await GraphSearch._bfs_traverse(db, entity_id, depth, entity_type)

    # ── Case Context (IDIE Integration) ───────────────────────────────────

    @staticmethod
    async def get_case_context(
        db: AsyncSession,
        decision_case_id: str,
    ) -> CaseContextResponse:
        """
        Full context for a Decision Case — all connected entities grouped by type.

        This is the IDIE integration point. Returns:
          - Machine
          - Related Documents
          - Past Incidents
          - Factory Memory
          - Reasoning Memory
          - Compliance Rules
          - Neighbor Decision Cases

        Grouped by NodeType for easy consumption.
        """
        # Get all edges touching this case (2-hop for richer context)
        neighbors = await GraphSearch._bfs_traverse(
            db, decision_case_id, depth=2, source_type=NodeType.DECISION_CASE.value
        )

        # Group by entity type
        type_groups: defaultdict[NodeType, List[ConnectedEntity]] = defaultdict(list)
        for entity in neighbors:
            type_groups[entity.entity_type].append(entity)

        # Build response groups
        groups: List[CaseContextGroup] = []
        for node_type in NodeType:
            entities = type_groups.get(node_type, [])
            if entities:
                groups.append(CaseContextGroup(
                    entity_type=node_type,
                    entities=entities,
                    count=len(entities),
                ))

        total = sum(g.count for g in groups)

        logger.info(
            "Case context for %s: %d connections across %d types",
            decision_case_id[:8],
            total,
            len(groups),
        )

        return CaseContextResponse(
            decision_case_id=decision_case_id,
            groups=groups,
            total_connections=total,
        )

    # ── Private BFS ───────────────────────────────────────────────────────

    @staticmethod
    async def _bfs_traverse(
        db: AsyncSession,
        start_id: str,
        depth: int,
        source_type: str | None = None,
    ) -> List[ConnectedEntity]:
        """
        Breadth-first traversal from a start entity.
        Returns all discovered entities (excluding the start) within `depth` hops.
        """
        visited: Set[str] = {start_id}
        frontier: List[Tuple[str, str | None, int]] = [(start_id, source_type, 0)]
        result: List[ConnectedEntity] = []

        while frontier:
            next_frontier: List[Tuple[str, str | None, int]] = []

            for entity_id, entity_type, current_depth in frontier:
                if current_depth >= depth:
                    continue

                edges = await _repo.get_edges_for_entity(db, entity_id, entity_type)

                for edge in edges:
                    # Determine the neighbor (the entity on the other side)
                    if edge.source_entity_id == entity_id:
                        neighbor_id = edge.target_entity_id
                        neighbor_type = edge.target_entity_type
                        direction = "outgoing"
                    else:
                        neighbor_id = edge.source_entity_id
                        neighbor_type = edge.source_entity_type
                        direction = "incoming"

                    if neighbor_id in visited:
                        continue

                    visited.add(neighbor_id)

                    # Parse properties
                    props = None
                    if edge.properties:
                        try:
                            props = json.loads(edge.properties) if isinstance(edge.properties, str) else edge.properties
                        except (json.JSONDecodeError, TypeError):
                            props = None

                    # Safely parse relationship type
                    try:
                        rel_type = RelationshipType(edge.relationship_type)
                    except ValueError:
                        rel_type = RelationshipType.RELATED_TO

                    # Safely parse node type
                    try:
                        node_type = NodeType(neighbor_type)
                    except ValueError:
                        continue  # Skip unknown node types

                    result.append(ConnectedEntity(
                        entity_id=neighbor_id,
                        entity_type=node_type,
                        relationship_type=rel_type,
                        direction=direction,
                        depth=current_depth + 1,
                        properties=props,
                    ))

                    next_frontier.append((neighbor_id, neighbor_type, current_depth + 1))

            frontier = next_frontier

        return result


# ── Helper ────────────────────────────────────────────────────────────────────

def _edge_to_response(edge: KnowledgeGraphEdge) -> GraphEdgeResponse:
    """Convert a SQLAlchemy edge to a Pydantic response."""
    props = None
    if edge.properties:
        try:
            props = json.loads(edge.properties) if isinstance(edge.properties, str) else edge.properties
        except (json.JSONDecodeError, TypeError):
            props = None

    return GraphEdgeResponse(
        id=edge.id,
        source_entity_id=edge.source_entity_id,
        source_entity_type=edge.source_entity_type,
        relationship_type=edge.relationship_type,
        target_entity_id=edge.target_entity_id,
        target_entity_type=edge.target_entity_type,
        properties=props,
        created_at=edge.created_at,
    )
