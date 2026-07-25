from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.copilot import router as copilot_router
from app.api.idie import router as idie_router
from app.api.memory import router as memory_router
from app.api.reasoning import router as reasoning_router
from app.api.knowledge_graph import router as knowledge_graph_router
from app.api.confidence import router as confidence_router
from app.api.conflicts import router as conflicts_router
from app.api.reports import router as reports_router
from app.api.dashboard import router as dashboard_router
from app.api.approvals import router as approvals_router

from contextlib import asynccontextmanager
from app.db.init_db import initialize_database
from app.core.config import APP_ENV

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await initialize_database()
        print("=========================")
        print("INDUS AI Backend Started")
        print("Database Connected ✓")
        print(f"Environment: {APP_ENV.capitalize()}")
        print("=========================")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        # Optionally exit or handle
    yield
    # Shutdown
    print("INDUS AI Backend Shutting Down")

# Initialize the app
app = FastAPI(
    title="INDUS AI API",
    description="Backend API for INDUS AI - Industrial Cognitive Memory System",
    version="1.0.0",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Health Check endpoint
@app.get("/health")
async def health_check():
    from app.db.init_db import check_database_connection
    db_status = "connected" if await check_database_connection() else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "environment": APP_ENV,
        "version": "1.0.0"
    }

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the exception here if we had a logger
    print(f"Global error handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred on the server.", "type": type(exc).__name__},
    )

# ── Active Routers ────────────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(copilot_router, prefix="/api/copilot", tags=["copilot"])
app.include_router(idie_router, prefix="/api/idie", tags=["idie"])
app.include_router(memory_router, prefix="/api/memory", tags=["memory"])
app.include_router(reasoning_router, prefix="/api/reasoning", tags=["reasoning"])
app.include_router(knowledge_graph_router, prefix="/api/graph", tags=["knowledge-graph"])
app.include_router(confidence_router, prefix="/api/confidence", tags=["confidence"])
app.include_router(conflicts_router, prefix="/api/conflicts", tags=["conflicts"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(approvals_router, prefix="/api/approvals", tags=["approvals"])

# Placeholder Routers (To be implemented in app/api)
# app.include_router(maintenance.router, prefix="/api/maintenance", tags=["maintenance"])
# app.include_router(compliance.router, prefix="/api/compliance", tags=["compliance"])
# app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
# app.include_router(audit.router, prefix="/api/audit", tags=["audit"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
