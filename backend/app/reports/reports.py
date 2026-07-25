import uuid
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.users import User
from app.api.auth import get_current_user
from app.reports.report_models import ReportResponse
from app.reports.report_service import ReportService

router = APIRouter()

@router.get("/decision-case/{case_id}", response_model=ReportResponse)
async def generate_decision_case_report(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ReportService(db)
    return await service.generate_decision_case_report(case_id, current_user.id)

@router.get("/maintenance/{machine_id}", response_model=ReportResponse)
async def generate_maintenance_report(
    machine_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ReportService(db)
    return await service.generate_maintenance_report(machine_id, current_user.id)

@router.get("/compliance", response_model=ReportResponse)
async def generate_compliance_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ReportService(db)
    return await service.generate_compliance_report(current_user.id)

@router.get("/executive-summary", response_model=ReportResponse)
async def generate_executive_summary_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ReportService(db)
    return await service.generate_executive_summary(current_user.id)

@router.get("/download/{report_id}")
async def download_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ReportService(db)
    file_path = await service.get_report_download_path(report_id)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found on disk")
        
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type='application/pdf'
    )
