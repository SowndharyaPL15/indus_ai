from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from app.db.base import BaseModel

class KnowledgeGraphEdge(BaseModel):
    __tablename__ = "knowledge_graph_edges"
    source_entity_id: Mapped[str] = mapped_column(String, index=True)
    source_entity_type: Mapped[str] = mapped_column(String)
    relationship_type: Mapped[str] = mapped_column(String, index=True)
    target_entity_id: Mapped[str] = mapped_column(String, index=True)
    target_entity_type: Mapped[str] = mapped_column(String)
    properties: Mapped[str | None] = mapped_column(Text, nullable=True) # JSON stored as string or JSONB
