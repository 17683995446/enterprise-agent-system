"""
Agent Routes - API endpoints for agent management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime


router = APIRouter()


class CreateAgentRequest(BaseModel):
    agent_name: str = Field(..., min_length=1, max_length=100, description="Agent名称")
    agent_mode: str = Field(default="dual", description="Agent模式")


class AgentResponse(BaseModel):
    agent_id: str
    agent_name: str
    agent_mode: str
    status: str
    created_at: str
    total_tasks: int
    completed_tasks: int
    success_rate: float


# In-memory storage
agents_db: Dict[str, Dict[str, Any]] = {}


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(request: CreateAgentRequest):
    """创建新Agent"""
    agent_id = str(uuid.uuid4())
    agent = {
        "agent_id": agent_id,
        "agent_name": request.agent_name,
        "agent_mode": request.agent_mode,
        "status": "idle",
        "created_at": datetime.now().isoformat(),
        "total_tasks": 0,
        "completed_tasks": 0,
        "success_rate": 0.0,
    }
    agents_db[agent_id] = agent
    return AgentResponse(**agent)


@router.get("", response_model=List[AgentResponse])
async def list_agents():
    """列出所有Agent"""
    return [AgentResponse(**a) for a in agents_db.values()]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """获取单个Agent详情"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(**agents_db[agent_id])


@router.post("/{agent_id}/start")
async def start_agent(agent_id: str):
    """启动Agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    agents_db[agent_id]["status"] = "running"
    return {"status": "started", "agent_id": agent_id}


@router.post("/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """停止Agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    agents_db[agent_id]["status"] = "idle"
    return {"status": "stopped", "agent_id": agent_id}
