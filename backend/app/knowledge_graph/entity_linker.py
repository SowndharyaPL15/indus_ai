"""
INDUS AI — Entity Linker

Extracts relationships from a Decision Case and produces graph edges.

Given a DecisionCase, queries the database for related entities and
creates typed GraphEdge objects linking them. Each entity type has
a separate extraction method for modularity.

The linker does NOT persist edges — it returns them for the GraphBuilder
to persist via the GraphRepository.
"""

import logging
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision_intelligence import DecisionCase, AIResponse, ReasoningMemory
from app.models.factory_memory_record import FactoryMemoryRecord
from app.models.factory_assets import SOP, ComplianceRule
from app.models.operations import Incident
from app.knowledge_graph.graph_models import GraphEdge, NodeType, RelationshipType

logger = logging.getLogger(__name__)


class EntityLinker:
    """
    Extracts entity relationships from a Decision Case.
    Returns a list of GraphEdge objects (not yet persisted).
    """

    @classmethod
    async def extract_edges(
        cls,
        db: AsyncSession,
        decision_case: DecisionCase,
    ) -> List[GraphEdge]:
        """
        Run all entity extractors for a Decision Case.
        Returns the combined list of edges.
        """
        case_id = str(decision_case.id)
        edges: List[GraphEdge] = []

        # Machine link
        edges.extend(cls._link_machine(decision_case, case_id))

        # Engineer link
        edges.extend(cls._link_engineer(decision_case, case_id))

        # AI Responses
        ai_edges = await cls._link_ai_responses(db, decision_case.id, case_id)
        edges.extend(ai_edges)

        # Factory Memory Records
        mem_edges = await cls._link_factory_memories(db, decision_case.id, case_id)
        edges.extend(mem_edges)

        # Reasoning Memory Records
        reason_edges = await cls._link_reasoning_memories(db, decision_case.id, case_id)
        edges.extend(reason_edges)

        # Incidents (same machine)
        if decision_case.machine_id:
            inc_edges = await cls._link_incidents(db, decision_case.machine_id, case_id)
            edges.extend(inc_edges)

        # SOPs (same machine)
        if decision_case.machine_id:
            sop_edges = await cls._link_sops(db, decision_case.machine_id, case_id)
            edges.extend(sop_edges)

        # Compliance Rules (general linkage)
        comp_edges = await cls._link_compliance_rules(db, case_id)
        edges.extend(comp_edges)

        logger.info(
            "Entity linker extracted %d edges for case %s", len(edges), case_id[:8]
        )
        return edges

    # ── Private Extractors ────────────────────────────────────────────────

    @staticmethod
    def _link_machine(case: DecisionCase, case_id: str) -> List[GraphEdge]:
        """Link the Decision Case to its machine."""
        if not case.machine_id:
            return []
        return [GraphEdge(
            source_entity_id=case_id,
            source_entity_type=NodeType.DECISION_CASE,
            relationship_type=RelationshipType.RELATED_TO,
            target_entity_id=str(case.machine_id),
            target_entity_type=NodeType.MACHINE,
            properties={"auto_linked": True},
        )]

    @staticmethod
    def _link_engineer(case: DecisionCase, case_id: str) -> List[GraphEdge]:
        """Link the Decision Case to the engineer who created it."""
        return [GraphEdge(
            source_entity_id=case_id,
            source_entity_type=NodeType.DECISION_CASE,
            relationship_type=RelationshipType.SOLVED_BY,
            target_entity_id=str(case.user_id),
            target_entity_type=NodeType.ENGINEER,
            properties={"auto_linked": True},
        )]

    @staticmethod
    async def _link_ai_responses(
        db: AsyncSession, case_uuid: UUID, case_id: str
    ) -> List[GraphEdge]:
        """Link AI responses generated for this case."""
        stmt = select(AIResponse.id).where(AIResponse.decision_case_id == case_uuid)
        result = await db.execute(stmt)
        edges = []
        for (response_id,) in result.all():
            edges.append(GraphEdge(
                source_entity_id=str(response_id),
                source_entity_type=NodeType.DOCUMENT,
                relationship_type=RelationshipType.GENERATED_FROM,
                target_entity_id=case_id,
                target_entity_type=NodeType.DECISION_CASE,
                properties={"type": "ai_response", "auto_linked": True},
            ))
        return edges

    @staticmethod
    async def _link_factory_memories(
        db: AsyncSession, case_uuid: UUID, case_id: str
    ) -> List[GraphEdge]:
        """Link factory memory records created from this case."""
        stmt = select(FactoryMemoryRecord.id).where(
            FactoryMemoryRecord.decision_case_id == case_uuid
        )
        result = await db.execute(stmt)
        edges = []
        for (mem_id,) in result.all():
            edges.append(GraphEdge(
                source_entity_id=str(mem_id),
                source_entity_type=NodeType.FACTORY_MEMORY,
                relationship_type=RelationshipType.LINKED_WITH,
                target_entity_id=case_id,
                target_entity_type=NodeType.DECISION_CASE,
                properties={"auto_linked": True},
            ))
        return edges

    @staticmethod
    async def _link_reasoning_memories(
        db: AsyncSession, case_uuid: UUID, case_id: str
    ) -> List[GraphEdge]:
        """Link reasoning memory records for this case."""
        stmt = select(ReasoningMemory.id).where(
            ReasoningMemory.decision_case_id == case_uuid
        )
        result = await db.execute(stmt)
        edges = []
        for (reason_id,) in result.all():
            edges.append(GraphEdge(
                source_entity_id=str(reason_id),
                source_entity_type=NodeType.REASONING_MEMORY,
                relationship_type=RelationshipType.REFERENCES,
                target_entity_id=case_id,
                target_entity_type=NodeType.DECISION_CASE,
                properties={"auto_linked": True},
            ))
        return edges

    @staticmethod
    async def _link_incidents(
        db: AsyncSession, machine_id: UUID, case_id: str
    ) -> List[GraphEdge]:
        """Link incidents on the same machine."""
        stmt = select(Incident.id).where(Incident.machine_id == machine_id)
        result = await db.execute(stmt)
        edges = []
        for (incident_id,) in result.all():
            edges.append(GraphEdge(
                source_entity_id=case_id,
                source_entity_type=NodeType.DECISION_CASE,
                relationship_type=RelationshipType.CAUSED_BY,
                target_entity_id=str(incident_id),
                target_entity_type=NodeType.INCIDENT,
                properties={"same_machine": True, "auto_linked": True},
            ))
        return edges

    @staticmethod
    async def _link_sops(
        db: AsyncSession, machine_id: UUID, case_id: str
    ) -> List[GraphEdge]:
        """Link SOPs associated with the same machine."""
        stmt = select(SOP.id).where(SOP.machine_id == machine_id)
        result = await db.execute(stmt)
        edges = []
        for (sop_id,) in result.all():
            edges.append(GraphEdge(
                source_entity_id=case_id,
                source_entity_type=NodeType.DECISION_CASE,
                relationship_type=RelationshipType.REFERENCES,
                target_entity_id=str(sop_id),
                target_entity_type=NodeType.SOP,
                properties={"same_machine": True, "auto_linked": True},
            ))
        return edges

    @staticmethod
    async def _link_compliance_rules(
        db: AsyncSession, case_id: str
    ) -> List[GraphEdge]:
        """Link active compliance rules to the decision case."""
        stmt = select(ComplianceRule.id).where(ComplianceRule.is_active == True)  # noqa: E712
        result = await db.execute(stmt)
        edges = []
        for (rule_id,) in result.all():
            edges.append(GraphEdge(
                source_entity_id=case_id,
                source_entity_type=NodeType.DECISION_CASE,
                relationship_type=RelationshipType.DEPENDS_ON,
                target_entity_id=str(rule_id),
                target_entity_type=NodeType.COMPLIANCE_RULE,
                properties={"auto_linked": True},
            ))
        return edges
