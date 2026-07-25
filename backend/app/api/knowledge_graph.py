"""
INDUS AI — Knowledge Graph API

GET  /api/graph/search                   — Search graph and return connected entities.
GET  /api/graph/context/{decision_case_id} — Full case context for IDIE integration.
POST /api/graph/edges                     — Manually create a graph edge.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.knowledge_graph.graph_models import (
    GraphEdgeCreateRequest,
    GraphEdgeResponse,
    GraphSearchResponse,
    CaseContextResponse,
)
from app.knowledge_graph.graph_service import GraphService

router = APIRouter()


@router.get("/search", response_model=GraphSearchResponse)
async def search_graph(
    q: str = Query(..., min_length=1, description="Search query for graph entities"),
    depth: int = Query(1, ge=1, le=4, description="Traversal depth (1-4 hops)"),
    limit: int = Query(50, ge=1, le=200, description="Max edges to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search the knowledge graph by text query.

    Returns matching edges and connected entities discovered via
    breadth-first traversal up to the specified depth.
    """
    return await GraphService.search_graph(db, q, depth=depth, limit=limit)


@router.get("/context/{decision_case_id}", response_model=CaseContextResponse)
async def get_case_context(
    decision_case_id: str = Path(..., description="UUID of the Decision Case"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get full context for a Decision Case from the Knowledge Graph.

    Returns all connected entities grouped by type:
    Machine, Documents, Incidents, Factory Memory, Reasoning Memory,
    Compliance Rules, and neighboring Decision Cases.

    This is the IDIE integration endpoint.
    """
    result = await GraphService.get_case_context(db, decision_case_id)

    if result.total_connections == 0:
        # Still return the empty response — no 404, the case may just have no graph yet
        pass

    return result


@router.post("/edges", response_model=GraphEdgeResponse)
async def create_edge(
    payload: GraphEdgeCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually create a graph edge between two entities.

    An audit log entry is created for every edge creation.
    """
    try:
        return await GraphService.create_edge(db, current_user, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
