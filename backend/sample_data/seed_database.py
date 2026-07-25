import asyncio
import sys
import os
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

# Add the project root to sys.path so we can import 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.system import GeneratedReport
from app.models.users import User, RoleEnum
from app.models.operations import MaintenanceRecord, Incident, SeverityEnum
from app.models.documents import Document, DocumentStatusEnum
from app.models.factory_assets import SOP, ComplianceRule, Machine
from app.models.living_memory import EngineerInsight
from app.models.decision_intelligence import (
    DecisionCase, AIResponse, ConfidenceScore, 
    ApprovalRequest, ReasoningMemory, CaseStatusEnum, ApprovalStatusEnum, OutcomeStatusEnum
)
from app.models.factory_memory_record import FactoryMemoryRecord
from app.models.knowledge_graph import KnowledgeGraphEdge

fake = Faker()

DEMO_USER_EMAIL = "demo_engineer@indus.ai"
DEMO_MANAGER_EMAIL = "demo_manager@indus.ai"
DEMO_MANUFACTURER = "INDUS Demo Corp"

MACHINE_NAMES = [
    "P-101 Feed Pump", "P-102 Cooling Water Pump", "P-103 Circulation Pump",
    "C-201 Air Compressor", "C-202 Gas Compressor", "C-203 Refrigeration Compressor",
    "HX-301 Heat Exchanger", "HX-302 Condenser", "HX-303 Evaporator",
    "TK-110 Storage Tank", "TK-205 Diesel Tank", "TK-301 Water Tank",
    "CV-401 Control Valve", "CV-402 Pressure Relief Valve", "CV-403 Flow Valve",
    "BL-501 Boiler", "BL-502 Steam Generator", "BL-503 Recovery Boiler",
    "GT-601 Gas Turbine", "GT-602 Steam Turbine", "GT-603 Wind Turbine",
    "CT-701 Cooling Tower", "CT-702 Draft Tower", "CT-703 Chiller Unit",
    "AG-801 Agitator", "AG-802 Mixer", "AG-803 Blender",
    "FN-901 Exhaust Fan", "FN-902 Blower", "FN-903 Ventilation Fan"
]

MAINTENANCE_FAILURES = [
    "Bearing Replacement", "Seal Leakage", "Motor Overheating", "Vibration Issue", 
    "Pressure Drop", "Filter Clogging", "Electrical Short", "Valve Stuck"
]

INCIDENTS = [
    "Near Miss", "Safety Incident", "Equipment Failure", "Gas Leak", 
    "Electrical Fault", "Oil Spill", "Mechanical Failure"
]

SOP_NAMES = [
    "Pump Maintenance SOP", "Lockout Tagout Procedure", "Boiler Startup Procedure",
    "Compressor Shutdown SOP", "Permit to Work SOP", "Confined Space Entry",
    "Valve Calibration Procedure", "Heat Exchanger Cleaning SOP", "Turbine Inspection Guide"
]

INSIGHTS = [
    "Vibration usually reduces after coupling alignment.",
    "Always inspect seal after bearing replacement.",
    "Temperature sensor gives false alarms after calibration.",
    "Check for cavitation if pressure drops suddenly.",
    "Motor winding temp spikes during summer months.",
    "Lubricant degradation is faster in this unit.",
    "Ensure bypass valve is open before starting.",
    "Watch out for harmonic resonance at 1500 RPM."
]

DECISION_PROBLEMS = [
    "Pump vibration investigation", "Boiler pressure instability", 
    "Cooling tower efficiency loss", "Heat exchanger fouling", 
    "Compressor overheating", "Valve not responding to control signal",
    "Unusual noise from turbine gearbox", "Frequent trip of motor overload relay"
]

def random_date(days_back=730):
    start = datetime.utcnow() - timedelta(days=days_back)
    return start + timedelta(seconds=random.randint(0, int((datetime.utcnow() - start).total_seconds())))

async def seed_data():
    async with AsyncSessionLocal() as session:
        print("Starting Demo Data Seeding...")
        
        # 1. Users
        print("Creating Demo Users...")
        engineer = User(
            email=DEMO_USER_EMAIL,
            name="John Doe (Demo Engineer)",
            hashed_password="hashed",
            role=RoleEnum.MAINTENANCE_ENGINEER,
            is_active=True
        )
        manager = User(
            email=DEMO_MANAGER_EMAIL,
            name="Jane Smith (Demo Manager)",
            hashed_password="hashed",
            role=RoleEnum.PLANT_MANAGER,
            is_active=True
        )
        session.add_all([engineer, manager])
        await session.flush()
        
        # 2. Machines
        print("Creating 30 Machines...")
        machines = []
        for name in MACHINE_NAMES:
            m = Machine(
                name=f"{name} (INDUS Demo Corp)",
                location=f"Unit {random.randint(1, 5)} - {fake.word().capitalize()} Area",
                status=random.choice(["OPERATIONAL", "MAINTENANCE", "WARNING"]),
                is_active=True
            )
            machines.append(m)
        session.add_all(machines)
        await session.flush()
        
        # 3. Documents & SOPs
        print("Creating 80 SOP Documents...")
        documents = []
        sops = []
        for i in range(80):
            doc = Document(
                title=f"{random.choice(SOP_NAMES)} - V{random.randint(1, 5)}.{random.randint(0, 9)}",
                original_filename=f"sop_{i}.pdf",
                stored_filename=f"sop_{i}_{uuid.uuid4()}.pdf",
                file_type="application/pdf",
                file_size=random.randint(1024, 10485760),
                status=DocumentStatusEnum.READY,
                uploaded_by=engineer.id
            )
            documents.append(doc)
        session.add_all(documents)
        await session.flush()
        
        for doc in documents:
            sop = SOP(
                document_id=doc.id,
                machine_id=random.choice(machines).id,
                title=doc.title
            )
            sops.append(sop)
        session.add_all(sops)
        
        # 4. Maintenance Records
        print("Creating 100 Maintenance Records...")
        m_records = []
        for _ in range(100):
            mr = MaintenanceRecord(
                machine_id=random.choice(machines).id,
                technician_id=engineer.id,
                description=f"{random.choice(MAINTENANCE_FAILURES)} - {fake.sentence()}",
                status=random.choice(["COMPLETED", "IN_PROGRESS", "SCHEDULED"]),
                created_at=random_date()
            )
            m_records.append(mr)
        session.add_all(m_records)
        
        # 5. Incidents
        print("Creating 50 Incident Reports...")
        incidents = []
        for _ in range(50):
            inc = Incident(
                machine_id=random.choice(machines).id,
                severity=random.choice(list(SeverityEnum)),
                description=f"{random.choice(INCIDENTS)} reported at {fake.time()}. {fake.sentence()}",
                created_at=random_date()
            )
            incidents.append(inc)
        session.add_all(incidents)
        
        # 6. Engineer Insights
        print("Creating 120 Engineer Insights...")
        insights = []
        for _ in range(120):
            insight = EngineerInsight(
                engineer_id=engineer.id,
                machine_id=random.choice(machines).id,
                insight_text=f"{random.choice(MACHINE_NAMES).split(' ')[0]} {random.choice(INSIGHTS)}"
            )
            insights.append(insight)
        session.add_all(insights)
        
        # 7. Decision Cases
        print("Creating 50 Decision Cases & Approvals...")
        cases = []
        ai_responses = []
        confidences = []
        approvals = []
        
        for i in range(50):
            c = DecisionCase(
                user_id=engineer.id,
                machine_id=random.choice(machines).id,
                query=f"How to resolve {random.choice(DECISION_PROBLEMS)}?",
                status=random.choice(list(CaseStatusEnum)),
                created_at=random_date()
            )
            cases.append(c)
        session.add_all(cases)
        await session.flush()
        
        for c in cases:
            resp = AIResponse(
                decision_case_id=c.id,
                response_text=f"Based on historical data and SOPs, it is recommended to check the {fake.word()}."
            )
            ai_responses.append(resp)
        session.add_all(ai_responses)
        await session.flush()
        
        for resp in ai_responses:
            conf = ConfidenceScore(
                ai_response_id=resp.id,
                score=round(random.uniform(75.0, 99.9), 2),
                factors={"historical_match": True, "sop_found": True}
            )
            confidences.append(conf)
        session.add_all(confidences)
        
        # 15 Approvals
        for i in range(15):
            c = cases[i]
            appr = ApprovalRequest(
                decision_case_id=c.id,
                requested_by=engineer.id,
                approver_role="manager",
                reason="Requires shutdown of critical equipment.",
                risk_level="HIGH",
                recommendation_summary="Shutdown and replace bearing.",
                status=random.choice([ApprovalStatusEnum.PENDING, ApprovalStatusEnum.APPROVED, ApprovalStatusEnum.REJECTED, ApprovalStatusEnum.ESCALATED]),
                approved_by=manager.id if i % 2 == 0 else None
            )
            approvals.append(appr)
        session.add_all(approvals)
        
        # 8. Factory Memory Records
        print("Creating 100 Factory Memory Records...")
        memories = []
        for _ in range(100):
            fm = FactoryMemoryRecord(
                problem=random.choice(DECISION_PROBLEMS),
                solution=f"Replaced the {fake.word()} and calibrated.",
                lesson=random.choice(INSIGHTS),
                engineer_feedback="Great recommendation.",
                decision_case_id=random.choice(cases).id,
                machine_id=random.choice(machines).id,
                engineer_id=engineer.id,
                rating=random.randint(3, 5),
                useful=True,
                validated=True,
                times_reused=random.randint(0, 50)
            )
            memories.append(fm)
        session.add_all(memories)
        
        # 9. Reasoning Memory Records
        print("Creating 40 Reasoning Memory Records...")
        reasoning = []
        for i in range(40):
            rm = ReasoningMemory(
                decision_case_id=cases[i].id,
                case_title=f"Reasoning for {cases[i].query[:20]}",
                problem_summary=cases[i].query,
                reasoning_steps={"step1": "Analyze telemetry", "step2": "Check SOPs"},
                evidence_used={"docs": [str(d.id) for d in random.sample(documents, 2)]},
                final_recommendation="Proceed with maintenance.",
                confidence_score=round(random.uniform(80.0, 99.0), 2),
                outcome_status=random.choice(list(OutcomeStatusEnum)),
                success_score=round(random.uniform(70.0, 100.0), 2),
                reusable_lesson=random.choice(INSIGHTS)
            )
            reasoning.append(rm)
        session.add_all(reasoning)
        
        # 10. Compliance Violations
        print("Creating 20 Compliance Violations...")
        compliance = []
        for _ in range(20):
            cr = ComplianceRule(
                rule_code=f"COMP-{random.randint(1000, 9999)}",
                description=f"[Demo] Expired Inspection on {random.choice(MACHINE_NAMES)}",
                is_active=True
            )
            compliance.append(cr)
        session.add_all(compliance)
        
        # 11. Generated Reports
        print("Creating 30 Generated Reports...")
        reports = []
        for i in range(30):
            rep = GeneratedReport(
                title=f"Generated Report {i}",
                file_path=f"/demo/reports/report_{i}.pdf",
                report_type=random.choice(["Decision Case Report", "Compliance Report", "Maintenance Report"]),
                generated_by=manager.id,
                decision_case_id=random.choice(cases).id if i % 2 == 0 else None,
                created_at=random_date()
            )
            reports.append(rep)
        session.add_all(reports)
        
        await session.flush()
        
        # 12. Knowledge Graph Edges
        print("Creating 200 Knowledge Graph Relationships...")
        edges = []
        for _ in range(200):
            source = random.choice(machines)
            rel_type = random.choice(["HAS_SOP", "HAS_INCIDENT", "HAS_INSIGHT", "HAS_COMPLIANCE_RULE"])
            target_id = ""
            target_type = ""
            if rel_type == "HAS_SOP":
                target_id = str(random.choice(sops).id)
                target_type = "SOP"
            elif rel_type == "HAS_INCIDENT":
                target_id = str(random.choice(incidents).id)
                target_type = "Incident"
            elif rel_type == "HAS_INSIGHT":
                target_id = str(random.choice(insights).id)
                target_type = "EngineerInsight"
            else:
                target_id = str(random.choice(compliance).id)
                target_type = "ComplianceRule"
            
            edge = KnowledgeGraphEdge(
                source_entity_id=str(source.id),
                source_entity_type="Machine",
                target_entity_id=target_id,
                target_entity_type=target_type,
                relationship_type=rel_type
            )
            edges.append(edge)
        session.add_all(edges)
        
        print("Committing all demo data...")
        await session.commit()
        print("Seed Complete! INDUS AI is now populated with enterprise demo data.")

if __name__ == "__main__":
    asyncio.run(seed_data())
