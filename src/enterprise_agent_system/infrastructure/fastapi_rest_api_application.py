"""
Infrastructure Layer - FastAPI REST API Application
基础设施层 - FastAPI REST API 应用程序

Provides REST API for agent system control, monitoring, and management.
Includes health checks, metrics endpoints, and full CRUD operations.
"""

import time
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse

from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
    AgentOperatingModeEnumeration,
    SystemHealthStatusEnumeration,
    HealthCheckResultModel,
)
from enterprise_agent_system.infrastructure.api_models_and_schemas import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
    MemoryCreateRequest,
    MemoryResponse,
    StatisticsResponse,
    HealthCheckResponse,
    MetricsResponse,
    AgentModeRequest,
    KnowledgeGraphNodeRequest,
    KnowledgeGraphEdgeRequest,
    APIResponse,
    task_router,
    memory_router,
    knowledge_router,
    stats_router,
    health_router,
    metrics_router,
    agent_router,
)
from enterprise_agent_system.infrastructure.prometheus_metrics_collector import (
    get_metrics_collector,
)
from enterprise_agent_system.core.agent_orchestrator_and_executor import (
    AgentOrchestratorAndExecutor,
)
from enterprise_agent_system.core.in_memory_data_storage_backend import (
    get_storage_backend_instance,
)
from enterprise_agent_system.infrastructure.enterprise_logging_system import (
    get_logger_instance,
)


logger = get_logger_instance(__name__)

_global_agent_instance: Optional[AgentOrchestratorAndExecutor] = None


def get_agent_instance() -> AgentOrchestratorAndExecutor:
    """
    Get global agent instance

    Returns:
        Agent orchestrator instance
    """
    global _global_agent_instance
    if _global_agent_instance is None:
        _global_agent_instance = AgentOrchestratorAndExecutor("API Agent")
    return _global_agent_instance


def set_agent_instance(agent: AgentOrchestratorAndExecutor) -> None:
    """
    Set global agent instance

    Args:
        agent: Agent instance to set
    """
    global _global_agent_instance
    _global_agent_instance = agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager

    Handles startup and shutdown events.
    """
    logger.info("Starting Enterprise Agent API Server...")
    metrics = get_metrics_collector()
    metrics.set_health_status(SystemHealthStatusEnumeration.HEALTHY_STATUS)
    yield
    logger.info("Shutting down Enterprise Agent API Server...")
    metrics.set_health_status(SystemHealthStatusEnumeration.UNHEALTHY_STATUS)


app = FastAPI(
    title="Enterprise Dual-Mode Agent System API",
    description="""
    ## Enterprise Dual-Mode Agent System REST API

    Provides comprehensive control and monitoring for the dual-mode agent system.

    ### Features
    - **Task Management**: Create, read, update, delete tasks
    - **Memory Management**: Store and retrieve agent memories
    - **Knowledge Graph**: Build and query knowledge graphs
    - **System Statistics**: Real-time system metrics
    - **Health Checks**: System health monitoring
    - **Agent Control**: Mode switching and control

    ### Authentication
    Currently using simple API key authentication via header.
    """,
    version="8.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@task_router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_task(request: TaskCreateRequest) -> APIResponse:
    """
    Create a new task

    Creates a new task with the specified title, description, and priority.
    """
    try:
        agent = get_agent_instance()
        task_id = agent.create_and_queue_task(
            task_title=request.task_title,
            task_description=request.task_description,
            priority_level=request.priority_level,
        )

        metrics = get_metrics_collector()
        metrics.record_task_created()

        return APIResponse(
            success=True,
            message="Task created successfully",
            data={"task_id": task_id},
        )
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@task_router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status_filter: Optional[TaskExecutionStatusEnumeration] = None,
    limit: int = 100,
) -> List[TaskResponse]:
    """
    List all tasks

    Optionally filter by status and limit results.
    """
    try:
        agent = get_agent_instance()
        storage = agent.storage_backend

        if status_filter:
            tasks = [
                t for t in storage.retrieve_all_tasks()
                if t.execution_status == status_filter
            ]
        else:
            tasks = storage.retrieve_all_tasks()

        tasks = tasks[:limit]

        return [
            TaskResponse(
                unique_entity_id=t.unique_entity_id,
                task_title=t.task_title,
                task_description=t.task_description,
                execution_status=t.execution_status.value,
                priority_level=t.priority_level.value,
                created_timestamp=t.created_timestamp,
                started_timestamp=t.started_timestamp,
                completed_timestamp=t.completed_timestamp,
                progress_percentage_value=t.progress_percentage_value,
                execution_result_message=t.execution_result_message,
                error_message=t.error_message,
                execution_steps_list=t.execution_steps_list,
            )
            for t in tasks
        ]
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """Get a specific task by ID"""
    try:
        agent = get_agent_instance()
        task = agent.storage_backend.retrieve_task_by_id(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

        return TaskResponse(
            unique_entity_id=task.unique_entity_id,
            task_title=task.task_title,
            task_description=task.task_description,
            execution_status=task.execution_status.value,
            priority_level=task.priority_level.value,
            created_timestamp=task.created_timestamp,
            started_timestamp=task.started_timestamp,
            completed_timestamp=task.completed_timestamp,
            progress_percentage_value=task.progress_percentage_value,
            execution_result_message=task.execution_result_message,
            error_message=task.error_message,
            execution_steps_list=task.execution_steps_list,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@task_router.patch("/{task_id}", response_model=APIResponse)
async def update_task(task_id: str, request: TaskUpdateRequest) -> APIResponse:
    """Update a specific task"""
    try:
        agent = get_agent_instance()
        storage = agent.storage_backend

        updates = {k: v for k, v in request.model_dump().items() if v is not None}

        if not updates:
            return APIResponse(success=True, message="No updates provided", data=None)

        task = storage.update_task_entry(task_id, **updates)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

        return APIResponse(
            success=True,
            message="Task updated successfully",
            data={"task_id": task.unique_entity_id},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@task_router.delete("/{task_id}", response_model=APIResponse)
async def delete_task(task_id: str) -> APIResponse:
    """Delete a specific task"""
    try:
        agent = get_agent_instance()
        storage = agent.storage_backend

        task = storage.retrieve_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

        storage.update_task_entry(
            task_id,
            execution_status=TaskExecutionStatusEnumeration.CANCELLED_STATUS,
        )

        return APIResponse(
            success=True,
            message="Task cancelled successfully",
            data={"task_id": task_id},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@memory_router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(request: MemoryCreateRequest) -> APIResponse:
    """Create a new memory"""
    try:
        agent = get_agent_instance()
        storage = agent.storage_backend

        memory = storage.create_new_memory_entry(
            content_text=request.content_text_body,
            category_type=request.category_type,
            tags_list=request.tags_list,
            importance_score=request.importance_score,
            source_task_id=request.source_task_id,
        )

        metrics = get_metrics_collector()
        metrics.record_memory_created()

        return APIResponse(
            success=True,
            message="Memory created successfully",
            data={"memory_id": memory.unique_memory_id},
        )
    except Exception as e:
        logger.error(f"Failed to create memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@memory_router.get("/", response_model=List[MemoryResponse])
async def list_memories(
    category_filter: Optional[MemoryCategoryTypeEnumeration] = None,
    search_query: Optional[str] = None,
    min_importance: int = 1,
    limit: int = 100,
) -> List[MemoryResponse]:
    """List all memories with optional filtering"""
    try:
        agent = get_agent_instance()
        storage = agent.storage_backend

        if search_query:
            memories = storage.search_memories_by_text_content(
                search_query=search_query,
                category_filter=category_filter,
                min_importance=min_importance,
            )
        else:
            memories = storage.retrieve_all_memories()

            if category_filter:
                memories = [
                    m for m in memories
                    if m.category_type == category_filter
                ]

            memories = [
                m for m in memories
                if m.importance_score >= min_importance
            ]

        memories = memories[:limit]

        return [
            MemoryResponse(
                unique_memory_id=m.unique_memory_id,
                content_text_body=m.content_text_body,
                summary_text=m.summary_text,
                category_type=m.category_type.value,
                tags_list=m.tags_list,
                importance_score=m.importance_score,
                access_count_number=m.access_count_number,
                created_timestamp=m.created_timestamp,
                updated_timestamp=m.updated_timestamp,
                source_task_id=m.source_task_id,
            )
            for m in memories
        ]
    except Exception as e:
        logger.error(f"Failed to list memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_router.post("/nodes", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_node(request: KnowledgeGraphNodeRequest) -> APIResponse:
    """Create a new knowledge graph node"""
    try:
        agent = get_agent_instance()
        storage = agent.storage_backend

        node_id = storage.add_node_to_knowledge_graph(
            label=request.label,
            properties=request.properties,
            memory_id=request.memory_id,
        )

        metrics = get_metrics_collector()
        kg_stats = storage.retrieve_knowledge_graph_statistics()
        metrics.update_knowledge_graph_stats(
            nodes=kg_stats["total_nodes"],
            edges=kg_stats["total_edges"],
        )

        return APIResponse(
            success=True,
            message="Knowledge node created successfully",
            data={"node_id": node_id},
        )
    except Exception as e:
        logger.error(f"Failed to create knowledge node: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_router.post("/edges", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_edge(request: KnowledgeGraphEdgeRequest) -> APIResponse:
    """Create a new knowledge graph edge"""
    try:
        agent = get_agent_instance()
        storage = agent.storage_backend

        edge_id = storage.add_edge_to_knowledge_graph(
            source_node_id=request.source_node_id,
            target_node_id=request.target_node_id,
            relationship_type=request.relationship_type,
            weight=request.weight,
        )

        metrics = get_metrics_collector()
        kg_stats = storage.retrieve_knowledge_graph_statistics()
        metrics.update_knowledge_graph_stats(
            nodes=kg_stats["total_nodes"],
            edges=kg_stats["total_edges"],
        )

        return APIResponse(
            success=True,
            message="Knowledge edge created successfully",
            data={"edge_id": edge_id},
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create knowledge edge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_router.get("/statistics", response_model=Dict[str, int])
async def get_knowledge_statistics() -> Dict[str, int]:
    """Get knowledge graph statistics"""
    try:
        agent = get_agent_instance()
        return agent.storage_backend.retrieve_knowledge_graph_statistics()
    except Exception as e:
        logger.error(f"Failed to get knowledge statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@stats_router.get("/", response_model=StatisticsResponse)
async def get_statistics() -> StatisticsResponse:
    """Get system statistics"""
    try:
        agent = get_agent_instance()
        stats = agent.current_system_statistics

        return StatisticsResponse(
            total_tasks_count=stats.total_tasks_count,
            completed_tasks_count=stats.completed_tasks_count,
            pending_tasks_count=stats.pending_tasks_count,
            failed_tasks_count=stats.failed_tasks_count,
            success_rate_percentage=stats.success_rate_percentage,
            total_memories_count=stats.total_memories_count,
            total_experiences_count=stats.total_experiences_count,
            knowledge_graph_nodes_count=stats.knowledge_graph_nodes_count,
            knowledge_graph_edges_count=stats.knowledge_graph_edges_count,
            uptime_seconds_value=stats.uptime_seconds_value,
            current_operating_mode=stats.current_operating_mode.value,
        )
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@health_router.get("/", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Perform health check

    Checks:
    - Agent initialization
    - Storage backend availability
    - Memory usage
    - Overall system health
    """
    try:
        agent = get_agent_instance()
        storage = agent.storage_backend

        details: Dict[str, Any] = {
            "agent_initialized": agent is not None,
            "storage_available": storage is not None,
            "total_tasks": len(storage.retrieve_all_tasks()),
            "total_memories": len(storage.retrieve_all_memories()),
        }

        agent_mode = agent.current_operating_mode
        details["agent_mode"] = agent_mode.value

        uptime = time.time() - getattr(agent, "_start_time", time.time())
        details["uptime_seconds"] = uptime

        status = SystemHealthStatusEnumeration.HEALTHY_STATUS
        message = "All systems operational"

        if details["total_tasks"] > 100:
            status = SystemHealthStatusEnumeration.DEGRADED_STATUS
            message = "High task volume"

        if not details["storage_available"]:
            status = SystemHealthStatusEnumeration.UNHEALTHY_STATUS
            message = "Storage unavailable"

        health = HealthCheckResultModel(
            health_status=status,
            status_message=message,
            details_dictionary=details,
            checked_timestamp=datetime.now(timezone.utc),
        )

        metrics = get_metrics_collector()
        metrics.set_health_status(status)

        return HealthCheckResponse(
            health_status=health.health_status.value,
            status_message=health.status_message,
            details_dictionary=health.details_dictionary,
            checked_timestamp=health.checked_timestamp,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        metrics = get_metrics_collector()
        metrics.set_health_status(SystemHealthStatusEnumeration.UNHEALTHY_STATUS)

        return HealthCheckResponse(
            health_status=SystemHealthStatusEnumeration.UNHEALTHY_STATUS.value,
            status_message=f"Health check failed: {str(e)}",
            details_dictionary={"error": str(e)},
            checked_timestamp=datetime.now(timezone.utc),
        )


@health_router.get("/live", response_model=Dict[str, str])
async def liveness_probe() -> Dict[str, str]:
    """
    Kubernetes liveness probe

    Returns 200 if the application is alive.
    """
    return {"status": "alive"}


@health_router.get("/ready", response_model=Dict[str, str])
async def readiness_probe() -> Dict[str, str]:
    """
    Kubernetes readiness probe

    Returns 200 if the application is ready to serve requests.
    """
    try:
        agent = get_agent_instance()
        if agent.storage_backend:
            return {"status": "ready"}
        raise HTTPException(status_code=503, detail="Storage not ready")
    except Exception:
        raise HTTPException(status_code=503, detail="System not ready")


@metrics_router.get("/", response_class=PlainTextResponse)
async def get_metrics() -> str:
    """
    Get Prometheus metrics

    Returns metrics in Prometheus text format.
    """
    metrics = get_metrics_collector()

    agent = get_agent_instance()
    stats = agent.current_system_statistics

    metrics.tasks_created_total = stats.total_tasks_count
    metrics.tasks_completed_total = stats.completed_tasks_count
    metrics.tasks_failed_total = stats.failed_tasks_count
    metrics.memories_created_total = stats.total_memories_count
    metrics.experiences_recorded_total = stats.total_experiences_count
    metrics.knowledge_graph_nodes_total = stats.knowledge_graph_nodes_count
    metrics.knowledge_graph_edges_total = stats.knowledge_graph_edges_count

    return PlainTextResponse(
        content=metrics.to_prometheus_format(),
        media_type="text/plain; charset=utf-8",
    )


@metrics_router.get("/json", response_model=MetricsResponse)
async def get_metrics_json() -> MetricsResponse:
    """Get metrics in JSON format"""
    metrics = get_metrics_collector()

    agent = get_agent_instance()
    stats = agent.current_system_statistics

    metrics.tasks_created_total = stats.total_tasks_count
    metrics.tasks_completed_total = stats.completed_tasks_count
    metrics.tasks_failed_total = stats.failed_tasks_count
    metrics.memories_created_total = stats.total_memories_count
    metrics.experiences_recorded_total = stats.total_experiences_count
    metrics.knowledge_graph_nodes_total = stats.knowledge_graph_nodes_count
    metrics.knowledge_graph_edges_total = stats.knowledge_graph_edges_count

    return MetricsResponse(**metrics.to_dict())


@agent_router.post("/mode", response_model=APIResponse)
async def change_agent_mode(request: AgentModeRequest) -> APIResponse:
    """Change agent operating mode"""
    try:
        agent = get_agent_instance()
        agent.current_operating_mode = request.target_mode

        metrics = get_metrics_collector()
        metrics.set_agent_mode(request.target_mode)

        logger.info(f"Agent mode changed to: {request.target_mode.value}")

        return APIResponse(
            success=True,
            message=f"Agent mode changed to {request.target_mode.value}",
            data={"mode": request.target_mode.value},
        )
    except Exception as e:
        logger.error(f"Failed to change agent mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@agent_router.get("/mode", response_model=Dict[str, str])
async def get_agent_mode() -> Dict[str, str]:
    """Get current agent mode"""
    agent = get_agent_instance()
    return {"mode": agent.current_operating_mode.value}


app.include_router(task_router)
app.include_router(memory_router)
app.include_router(knowledge_router)
app.include_router(stats_router)
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(agent_router)


@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint - API information"""
    return {
        "name": "Enterprise Dual-Mode Agent System API",
        "version": "8.0.0",
        "documentation": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
