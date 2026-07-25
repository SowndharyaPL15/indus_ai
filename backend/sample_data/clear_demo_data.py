import asyncio
import sys
import os

# Add the project root to sys.path so we can import 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select, delete
from app.db.database import AsyncSessionLocal
from app.models.system import Notification, GeneratedReport, AuditLog
from app.models.users import User
from app.models.operations import MaintenanceRecord, Incident, InspectionReport
from app.models.documents import Document, DocumentChunk
from app.models.factory_assets import SOP, ComplianceRule, Machine
from app.models.living_memory import EngineerInsight
from app.models.decision_intelligence import (
    DecisionCase, AIResponse, ConfidenceScore, ConflictLog, 
    ApprovalRequest, ReasoningMemory
)
from app.models.factory_memory_record import FactoryMemoryRecord
from app.models.knowledge_graph import KnowledgeGraphEdge

DEMO_USER_EMAIL = "demo_engineer@indus.ai"
DEMO_MANAGER_EMAIL = "demo_manager@indus.ai"
DEMO_MANUFACTURER_SUFFIX = "(INDUS Demo Corp)"

async def clear_data():
    async with AsyncSessionLocal() as session:
        print("Finding demo users...")
        users_result = await session.execute(
            select(User).where(User.email.in_([DEMO_USER_EMAIL, DEMO_MANAGER_EMAIL]))
        )
        demo_users = users_result.scalars().all()
        demo_user_ids = [u.id for u in demo_users]

        print("Finding demo machines...")
        machines_result = await session.execute(
            select(Machine).where(Machine.name.like(f"%{DEMO_MANUFACTURER_SUFFIX}%"))
        )
        demo_machines = machines_result.scalars().all()
        demo_machine_ids = [m.id for m in demo_machines]

        print("Finding demo documents...")
        docs_result = await session.execute(
            select(Document).where(Document.uploaded_by.in_(demo_user_ids)) if demo_user_ids else select(Document).where(False)
        )
        demo_docs = docs_result.scalars().all()
        demo_doc_ids = [d.id for d in demo_docs]

        print("Finding demo decision cases...")
        cases_result = await session.execute(
            select(DecisionCase).where(DecisionCase.user_id.in_(demo_user_ids)) if demo_user_ids else select(DecisionCase).where(False)
        )
        demo_cases = cases_result.scalars().all()
        demo_case_ids = [c.id for c in demo_cases]

        print("Finding demo AI responses...")
        responses_result = await session.execute(
            select(AIResponse).where(AIResponse.decision_case_id.in_(demo_case_ids)) if demo_case_ids else select(AIResponse).where(False)
        )
        demo_responses = responses_result.scalars().all()
        demo_response_ids = [r.id for r in demo_responses]

        if not demo_users and not demo_machines:
            print("No demo data found to clear.")
            return

        print("Clearing dependent records...")

        # Clear Knowledge Graph Edges linked to demo cases
        if demo_case_ids:
            await session.execute(delete(KnowledgeGraphEdge).where(KnowledgeGraphEdge.source_entity_id.in_([str(id) for id in demo_case_ids])))
            await session.execute(delete(KnowledgeGraphEdge).where(KnowledgeGraphEdge.target_entity_id.in_([str(id) for id in demo_case_ids])))
        if demo_machine_ids:
            await session.execute(delete(KnowledgeGraphEdge).where(KnowledgeGraphEdge.source_entity_id.in_([str(id) for id in demo_machine_ids])))
            await session.execute(delete(KnowledgeGraphEdge).where(KnowledgeGraphEdge.target_entity_id.in_([str(id) for id in demo_machine_ids])))

        # Clear decision case dependents
        if demo_response_ids:
            await session.execute(delete(ConfidenceScore).where(ConfidenceScore.ai_response_id.in_(demo_response_ids)))
        if demo_case_ids:
            await session.execute(delete(AIResponse).where(AIResponse.decision_case_id.in_(demo_case_ids)))
            await session.execute(delete(ConflictLog).where(ConflictLog.decision_case_id.in_(demo_case_ids)))
            await session.execute(delete(ApprovalRequest).where(ApprovalRequest.decision_case_id.in_(demo_case_ids)))
            await session.execute(delete(ReasoningMemory).where(ReasoningMemory.decision_case_id.in_(demo_case_ids)))
            await session.execute(delete(FactoryMemoryRecord).where(FactoryMemoryRecord.decision_case_id.in_(demo_case_ids)))
            await session.execute(delete(GeneratedReport).where(GeneratedReport.decision_case_id.in_(demo_case_ids)))
            await session.execute(delete(AuditLog).where(AuditLog.decision_case_id.in_(demo_case_ids)))

        # Clear factory memory records linked directly to machines
        if demo_machine_ids:
            await session.execute(delete(FactoryMemoryRecord).where(FactoryMemoryRecord.machine_id.in_(demo_machine_ids)))
        
        # Clear machine dependents
        if demo_machine_ids:
            await session.execute(delete(MaintenanceRecord).where(MaintenanceRecord.machine_id.in_(demo_machine_ids)))
            await session.execute(delete(Incident).where(Incident.machine_id.in_(demo_machine_ids)))
            await session.execute(delete(InspectionReport).where(InspectionReport.machine_id.in_(demo_machine_ids)))
            await session.execute(delete(EngineerInsight).where(EngineerInsight.machine_id.in_(demo_machine_ids)))
            await session.execute(delete(SOP).where(SOP.machine_id.in_(demo_machine_ids)))

        # Clear document dependents
        if demo_doc_ids:
            await session.execute(delete(SOP).where(SOP.document_id.in_(demo_doc_ids)))
            await session.execute(delete(DocumentChunk).where(DocumentChunk.document_id.in_(demo_doc_ids)))
        
        # Clear compliance rules
        if demo_machine_ids:
            await session.execute(delete(ComplianceRule).where(ComplianceRule.description.ilike("%Demo%")))

        # Clear remaining reports
        if demo_user_ids:
            await session.execute(delete(GeneratedReport).where(GeneratedReport.generated_by.in_(demo_user_ids)))
            await session.execute(delete(Notification).where(Notification.user_id.in_(demo_user_ids)))

        # Finally clear base entities
        if demo_case_ids:
            await session.execute(delete(DecisionCase).where(DecisionCase.id.in_(demo_case_ids)))
        if demo_doc_ids:
            await session.execute(delete(Document).where(Document.id.in_(demo_doc_ids)))
        if demo_machine_ids:
            await session.execute(delete(Machine).where(Machine.id.in_(demo_machine_ids)))
        if demo_user_ids:
            await session.execute(delete(User).where(User.id.in_(demo_user_ids)))
        
        await session.commit()
        print("Successfully cleared all demo data.")

if __name__ == "__main__":
    asyncio.run(clear_data())
