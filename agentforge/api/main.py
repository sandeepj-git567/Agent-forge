"""
AgentForge AI FastAPI Application Entry Point
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agentforge.api.routes.auth import router as auth_router
from agentforge.api.routes.documents import router as documents_router
from agentforge.api.routes.evaluations import router as evaluations_router
from agentforge.api.routes.health import router as health_router
from agentforge.api.routes.rag import router as rag_router
from agentforge.api.routes.tasks import router as tasks_router
from agentforge.api.routes.workflows import router as workflows_router
from agentforge.config.settings import settings
from agentforge.observability.middleware import ProductionObservabilityMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI Agent Orchestration, RAG, Workflow Automation & Evaluation Platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Production Middleware
app.add_middleware(ProductionObservabilityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(rag_router, prefix="/api/v1")
app.include_router(workflows_router, prefix="/api/v1")
app.include_router(evaluations_router, prefix="/api/v1")

# Serve React Frontend Dashboard static files if built
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/dashboard", StaticFiles(directory=frontend_dist, html=True), name="dashboard")


@app.get("/")
async def root():
    """Root landing endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/api/v1/health",
        "dashboard": "/dashboard"
    }
