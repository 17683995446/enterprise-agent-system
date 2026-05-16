"""
Task Routes - API endpoints for task management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
from enum import Enum


router = APIRouter()


class TaskPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CreateTaskRequest(BaseModel):
    task_title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    task_description: str = Field(..., min_length=1, max_length=5000, description="任务描述")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="任务优先级")
    tags: Optional[List[str]] = Field(default=None, description="任务标签")


class TaskResponse(BaseModel):
    task_id: str
    task_title: str
    task_description: str
    priority: TaskPriority
    status: TaskStatus
    progress: float
    created_at: str
    updated_at: str
    tags: Optional[List[str]]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# In-memory storage for demo
tasks_db: Dict[str, Dict[str, Any]] = {}


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(request: CreateTaskRequest):
    """创建新任务"""
    task_id = str(uuid.uuid4())
    task = {
        "task_id": task_id,
        "task_title": request.task_title,
        "task_description": request.task_description,
        "priority": request.priority.value,
        "status": TaskStatus.PENDING.value,
        "progress": 0.0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "tags": request.tags or [],
    }
    tasks_db[task_id] = task
    return TaskResponse(**task)


@router.get("", response_model=List[TaskResponse])
async def list_tasks(status: Optional[TaskStatus] = None, priority: Optional[TaskPriority] = None):
    """列出所有任务，支持筛选"""
    tasks = list(tasks_db.values())
    
    if status:
        tasks = [t for t in tasks if t["status"] == status.value]
    if priority:
        tasks = [t for t in tasks if t["priority"] == priority.value]
    
    return [TaskResponse(**t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """获取单个任务详情"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**tasks_db[task_id])


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, request: CreateTaskRequest):
    """更新任务"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    task.update({
        "task_title": request.task_title,
        "task_description": request.task_description,
        "priority": request.priority.value,
        "tags": request.tags or [],
        "updated_at": datetime.now().isoformat(),
    })
    
    return TaskResponse(**task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str):
    """删除任务"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]


@router.post("/{task_id}/start")
async def start_task(task_id: str):
    """启动任务"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    task["status"] = TaskStatus.RUNNING.value
    task["updated_at"] = datetime.now().isoformat()
    
    return {"status": "started", "task_id": task_id}


@router.post("/{task_id}/complete")
async def complete_task(task_id: str, result: Optional[Dict[str, Any]] = None):
    """完成任务"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    task["status"] = TaskStatus.COMPLETED.value
    task["progress"] = 1.0
    task["result"] = result or {}
    task["updated_at"] = datetime.now().isoformat()
    
    return {"status": "completed", "task_id": task_id}


@router.get("/statistics/summary")
async def get_task_statistics():
    """获取任务统计"""
    total = len(tasks_db)
    pending = sum(1 for t in tasks_db.values() if t["status"] == TaskStatus.PENDING.value)
    running = sum(1 for t in tasks_db.values() if t["status"] == TaskStatus.RUNNING.value)
    completed = sum(1 for t in tasks_db.values() if t["status"] == TaskStatus.COMPLETED.value)
    failed = sum(1 for t in tasks_db.values() if t["status"] == TaskStatus.FAILED.value)
    
    return {
        "total": total,
        "pending": pending,
        "running": running,
        "completed": completed,
        "failed": failed,
        "success_rate": f"{(completed / total * 100):.2f}%" if total > 0 else "0.00%",
    }
