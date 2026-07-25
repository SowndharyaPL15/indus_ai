from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.dashboard.dashboard_service import DashboardService
from app.dashboard.dashboard_models import (
    ExecutiveSummaryResponse,
    KnowledgeGrowthResponse,
    MachineIntelligenceResponse,
    AIPerformanceResponse,
    ComplianceDashboardResponse,
    LiveActivityFeedResponse
)

router = APIRouter()

@router.get("/summary", response_model=ExecutiveSummaryResponse)
async def get_executive_summary(
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_executive_summary()

@router.get("/knowledge-growth", response_model=KnowledgeGrowthResponse)
async def get_knowledge_growth(
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_knowledge_growth()

@router.get("/machine-intelligence", response_model=MachineIntelligenceResponse)
async def get_machine_intelligence(
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_machine_intelligence()

@router.get("/ai-performance", response_model=AIPerformanceResponse)
async def get_ai_performance(
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_ai_performance()

@router.get("/compliance", response_model=ComplianceDashboardResponse)
async def get_compliance(
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_compliance()

@router.get("/activity", response_model=LiveActivityFeedResponse)
async def get_activity(
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService(db)
    return await service.get_activity()
