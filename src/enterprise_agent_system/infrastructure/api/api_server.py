"""
Enhanced FastAPI Server with Unified Response and Authentication
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import time
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from enterprise_agent_system.infrastructure.api.task_routes import router as task_router
from enterprise_agent_system.infrastructure.api.agent_routes import router as agent_router
from enterprise_agent_system.infrastructure.api.memory_routes import router as memory_router
from enterprise_agent_system.infrastructure.api.project_analyzer_routes import router as project_router
from enterprise_agent_system.infrastructure.api.llm_analysis_routes import router as llm_analysis_router
from enterprise_agent_system.infrastructure.api.report_routes import router as report_router
from enterprise_agent_system.infrastructure.api_unified_models import ApiResponse, ResponseStatus, ErrorCode, HealthStatus, SystemInfo
from enterprise_agent_system.infrastructure.api_auth_middleware import rate_limit_middleware, get_current_user
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance(__name__)
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager"""
    logger.info("🚀 Enterprise Agent System API Starting...")
    yield
    logger.info("👋 Enterprise Agent System API Shutting Down...")


app = FastAPI(
    title="Enterprise Agent System API",
    description="Enterprise-level Dual-Mode Agent System with Knowledge Graph Memory and LLM Analysis",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit middleware
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(task_router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(agent_router, prefix="/api/agents", tags=["Agents"])
app.include_router(memory_router, prefix="/api/memory", tags=["Memory"])
app.include_router(project_router, prefix="/api/projects", tags=["Projects"])
app.include_router(llm_analysis_router, prefix="/api/v1/llm", tags=["LLM Analysis"])
app.include_router(report_router, prefix="/api/v1/reports", tags=["Reports"])


@app.get("/", response_model=ApiResponse[Dict[str, Any]])
async def root():
    """Root endpoint with unified response"""
    return ApiResponse.success({
        "name": "Enterprise Agent System",
        "version": "2.1.0",
        "status": "running",
        "endpoints": {
            "tasks": "/api/tasks",
            "agents": "/api/agents",
            "memory": "/api/memory",
            "projects": "/api/projects",
            "llm_analysis": "/api/v1/llm",
            "docs": "/docs",
        }
    })


@app.get("/health", response_model=ApiResponse[HealthStatus])
async def health_check():
    """Health check endpoint"""
    uptime = time.time() - start_time
    return ApiResponse.success(
        HealthStatus(
            status="healthy",
            version="2.1.0",
            uptime=uptime,
            services={"database": True, "llm": True, "api": True}
        )
    )


@app.get("/api/system/info", response_model=ApiResponse[SystemInfo])
async def get_system_info(current_user: Dict = Depends(get_current_user)):
    """Get system information"""
    from enterprise_agent_system.infrastructure.llm_integration import get_llm_manager
    
    llm = get_llm_manager()
    stats = llm.get_stats()
    
    return ApiResponse.success(
        SystemInfo(
            version="2.1.0",
            model="Qwen/Qwen2.5-7B-Instruct",
            cache_size=stats.get("cache_size", 0),
            cache_hits=stats.get("cached_requests", 0),
            cache_misses=stats.get("total_requests", 0) - stats.get("cached_requests", 0),
            total_analysis=stats.get("total_requests", 0)
        )
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Unified exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return ApiResponse.error(
        error_code=ErrorCode.INTERNAL_ERROR,
        message="Internal server error",
        details=str(exc)
    ).dict()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    error_code = ErrorCode.INTERNAL_ERROR
    if exc.status_code == 404:
        error_code = ErrorCode.NOT_FOUND
    elif exc.status_code == 401:
        error_code = ErrorCode.UNAUTHORIZED
    elif exc.status_code == 403:
        error_code = ErrorCode.FORBIDDEN
    elif exc.status_code == 429:
        error_code = ErrorCode.RATE_LIMITED
    elif 400 <= exc.status_code < 500:
        error_code = ErrorCode.BAD_REQUEST
    
    return ApiResponse.error(
        error_code=error_code,
        message=exc.detail,
        details={"status_code": exc.status_code}
    ).dict()


def start_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the API server"""
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    start_api_server()
