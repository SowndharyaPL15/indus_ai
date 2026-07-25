"""
INDUS AI — Knowledge Graph Models

Enums for node types and relationship types, plus Pydantic schemas
for API request/response contracts.

Node types and relationship types are defined as string enums so they
map cleanly to both PostgreSQL strings and future Neo4j labels.
"""

import enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# ── Node Type Enum ────────────────────────────────────────────────────────────

class NodeType(str, enum.Enum):
    MACHINE = "MACHINE"
    DOCUMENT = "DOCUMENT"
    DECISION_CASE = "DECISION_CASE"
    INCIDENT = "INCIDENT"
    SOP = "SOP"
    ENGINEER = "ENGINEER"
    FACTORY_MEMORY = "FACTORY_MEMORY"
    REASONING_MEMORY = "REASONING_MEMORY"
    COMPLIANCE_RULE = "COMPLIANCE_RULE"


# ── Relationship Type Enum ────────────────────────────────────────────────────

class RelationshipType(str, enum.Enum):
    RELATED_TO = "RELATED_TO"
    USES = "USES"
    REFERENCES = "REFERENCES"
    SOLVED_BY = "SOLVED_BY"
    LINKED_WITH = "LINKED_WITH"
    CAUSED_BY = "CAUSED_BY"
    GENERATED_FROM = "GENERATED_FROM"
    SIMILAR_TO = "SIMILAR_TO"
    DEPENDS_ON = "DEPENDS_ON"


# ── Graph Primitives ──────────────────────────────────────────────────────────

class GraphNode(BaseModel):
    """Represents a node in the knowledge graph."""
    entity_id: str
    entity_type: NodeType
    label: str = ""
    properties: Optional[Dict[str, Any]] = None


class GraphEdge(BaseModel):
    """Represents a directed edge between two nodes."""
    id: Optional[UUID] = None
    source_entity_id: str
    source_entity_type: NodeType
    relationship_type: RelationshipType
    target_entity_id: str
    target_entity_type: NodeType
    properties: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── API Request Schemas ───────────────────────────────────────────────────────

class GraphEdgeCreateRequest(BaseModel):
    """Input for POST /api/graph/edges — manual edge creation."""
    source_entity_id: str = Field(..., description="UUID of the source entity")
    source_entity_type: NodeType
    relationship_type: RelationshipType
    target_entity_id: str = Field(..., description="UUID of the target entity")
    target_entity_type: NodeType
    properties: Optional[Dict[str, Any]] = None


# ── API Response Schemas ──────────────────────────────────────────────────────

class GraphEdgeResponse(BaseModel):
    """Single edge in the response."""
    id: UUID
    source_entity_id: str
    source_entity_type: str
    relationship_type: str
    target_entity_id: str
    target_entity_type: str
    properties: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConnectedEntity(BaseModel):
    """An entity discovered via graph traversal."""
    entity_id: str
    entity_type: NodeType
    relationship_type: RelationshipType
    direction: str = Field(
        ..., description="'outgoing' if this entity is a target, 'incoming' if source"
    )
    depth: int = Field(..., description="Hop distance from the origin entity")
    properties: Optional[Dict[str, Any]] = None


class GraphSearchResponse(BaseModel):
    """Search results with connected entities."""
    query: str
    edges: List[GraphEdgeResponse]
    connected_entities: List[ConnectedEntity]
    total_edges: int
    depth: int


class CaseContextGroup(BaseModel):
    """A group of related entities for a decision case, by type."""
    entity_type: NodeType
    entities: List[ConnectedEntity]
    count: int


class CaseContextResponse(BaseModel):
    """Full context for a decision case — all connected entities grouped by type."""
    decision_case_id: str
    groups: List[CaseContextGroup]
    total_connections: int
