"""
FastAPI Server for Enterprise Agent System
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from enterprise_agent_system.infrastructure.api.task_routes import router as task_router
from enterprise_agent_system.infrastructure.api.agent_routes import router as agent_router
from enterprise_agent_system.infrastructure.api.memory_routes import router as memory_router
from enterprise_agent_system.infrastructure.api.project_analyzer_routes import router as project_router
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance


logger = get_logger_instance(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager"""
    logger.info("🚀 Enterprise Agent System API Starting...")
    yield
    logger.info("👋 Enterprise Agent System API Shutting Down...")


app = FastAPI(
    title="Enterprise Agent System API",
    description="Enterprise-level Dual-Mode Agent System with Knowledge Graph Memory",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(task_router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(agent_router, prefix="/api/agents", tags=["Agents"])
app.include_router(memory_router, prefix="/api/memory", tags=["Memory"])
app.include_router(project_router, prefix="/api/projects", tags=["Projects"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Enterprise Agent System",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "tasks": "/api/tasks",
            "agents": "/api/agents",
            "memory": "/api/memory",
            "projects": "/api/projects",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/statistics")
async def get_statistics():
    """Get system statistics"""
    return {
        "total_tasks": 0,
        "completed_tasks": 0,
        "success_rate": "0.00%",
        "total_memories": 0,
        "knowledge_graph_nodes": 0,
        "active_agents": 0,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


def start_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the API server"""
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_api_server()
