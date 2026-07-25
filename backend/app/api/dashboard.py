from fastapi import APIRouter
from app.dashboard.dashboard_routes import router as dashboard_router

router = APIRouter()
router.include_router(dashboard_router, tags=["dashboard"])
