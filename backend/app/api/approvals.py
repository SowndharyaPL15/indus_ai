from fastapi import APIRouter
from app.approval_engine.approval import router as approval_router

router = APIRouter()
router.include_router(approval_router, tags=["approvals"])
