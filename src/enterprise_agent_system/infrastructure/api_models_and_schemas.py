"""
Infrastructure Layer - REST API Routes and Endpoints
基础设施层 - REST API 路由和端点

Provides FastAPI routes for agent system control and monitoring.
Supports CRUD operations for tasks, memories, and system management.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
    AgentOperatingModeEnumeration,
    SystemHealthStatusEnumeration,
)


class TaskCreateRequest(BaseModel):
    """Request model for creating a task"""
    task_title: str = Field(..., min_length=1, max_length=255, description="Task title")
    task_description: str = Field(default="", max_length=2000, description="Task description")
    priority_level: TaskPriorityLevelEnumeration = Field(
        default=TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
        description="Task priority level"
    )


class TaskUpdateRequest(BaseModel):
    """Request model for updating a task"""
    task_title: Optional[str] = Field(None, min_length=1, max_length=255)
    task_description: Optional[str] = Field(None, max_length=2000)
    execution_status: Optional[TaskExecutionStatusEnumeration] = None
    priority_level: Optional[TaskPriorityLevelEnumeration] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=1.0)
    execution_result_message: Optional[str] = None
    error_message: Optional[str] = None


class TaskResponse(BaseModel):
    """Response model for task data"""
    unique_entity_id: str
    task_title: str
    task_description: str
    execution_status: str
    priority_level: int
    created_timestamp: datetime
    started_timestamp: Optional[datetime]
    completed_timestamp: Optional[datetime]
    progress_percentage_value: float
    execution_result_message: str
    error_message: str
    execution_steps_list: List[str]

    class Config:
        from_attributes = True


class MemoryCreateRequest(BaseModel):
    """Request model for creating a memory"""
    content_text_body: str = Field(..., min_length=1, description="Memory content")
    category_type: MemoryCategoryTypeEnumeration = Field(
        default=MemoryCategoryTypeEnumeration.GENERAL_MEMORY_CATEGORY,
        description="Memory category"
    )
    tags_list: List[str] = Field(default_factory=list, description="Memory tags")
    importance_score: int = Field(default=3, ge=1, le=5, description="Importance score")
    source_task_id: Optional[str] = Field(None, description="Source task ID")


class MemoryResponse(BaseModel):
    """Response model for memory data"""
    unique_memory_id: str
    content_text_body: str
    summary_text: Optional[str]
    category_type: str
    tags_list: List[str]
    importance_score: int
    access_count_number: int
    created_timestamp: datetime
    updated_timestamp: datetime
    source_task_id: Optional[str]

    class Config:
        from_attributes = True


class StatisticsResponse(BaseModel):
    """Response model for system statistics"""
    total_tasks_count: int
    completed_tasks_count: int
    pending_tasks_count: int
    failed_tasks_count: int
    success_rate_percentage: float
    total_memories_count: int
    total_experiences_count: int
    knowledge_graph_nodes_count: int
    knowledge_graph_edges_count: int
    uptime_seconds_value: float
    current_operating_mode: str


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    health_status: str
    status_message: str
    details_dictionary: Dict[str, Any]
    checked_timestamp: datetime


class MetricsResponse(BaseModel):
    """Response model for Prometheus metrics"""
    tasks_created_total: int
    tasks_completed_total: int
    tasks_failed_total: int
    tasks_in_progress: int
    memories_created_total: int
    experiences_recorded_total: int
    knowledge_graph_nodes_total: int
    knowledge_graph_edges_total: int
    uptime_seconds: float
    success_rate_percentage: float
    current_agent_mode: str
    health_status: str


class AgentModeRequest(BaseModel):
    """Request model for changing agent mode"""
    target_mode: AgentOperatingModeEnumeration = Field(
        ...,
        description="Target operating mode"
    )


class KnowledgeGraphNodeRequest(BaseModel):
    """Request model for creating knowledge graph node"""
    label: str = Field(..., min_length=1, description="Node label")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    memory_id: Optional[str] = None


class KnowledgeGraphEdgeRequest(BaseModel):
    """Request model for creating knowledge graph edge"""
    source_node_id: str = Field(..., description="Source node ID")
    target_node_id: str = Field(..., description="Target node ID")
    relationship_type: str = Field(..., min_length=1, description="Relationship type")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Edge weight")


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None


task_router = APIRouter(prefix="/tasks", tags=["Tasks"])
memory_router = APIRouter(prefix="/memories", tags=["Memories"])
knowledge_router = APIRouter(prefix="/knowledge", tags=["Knowledge Graph"])
stats_router = APIRouter(prefix="/statistics", tags=["Statistics"])
health_router = APIRouter(prefix="/health", tags=["Health"])
metrics_router = APIRouter(prefix="/metrics", tags=["Metrics"])
agent_router = APIRouter(prefix="/agent", tags=["Agent Control"])
