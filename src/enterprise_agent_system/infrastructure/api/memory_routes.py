"""
Memory Routes - API endpoints for knowledge graph memory management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime


router = APIRouter()


class CreateMemoryRequest(BaseModel):
    memory_title: str = Field(..., min_length=1, max_length=200, description="记忆标题")
    memory_content: str = Field(..., min_length=1, description="记忆内容")
    memory_category: str = Field(default="general", description="记忆分类")
    memory_tags: Optional[List[str]] = Field(default=None, description="记忆标签")


class MemoryResponse(BaseModel):
    memory_id: str
    memory_title: str
    memory_content: str
    memory_category: str
    memory_tags: List[str]
    created_at: str
    access_count: int
    last_accessed: str


# In-memory storage
memory_db: Dict[str, Dict[str, Any]] = {}
knowledge_graph: Dict[str, List[str]] = {}


@router.post("", response_model=MemoryResponse, status_code=201)
async def create_memory(request: CreateMemoryRequest):
    """创建新记忆"""
    memory_id = str(uuid.uuid4())
    memory = {
        "memory_id": memory_id,
        "memory_title": request.memory_title,
        "memory_content": request.memory_content,
        "memory_category": request.memory_category,
        "memory_tags": request.memory_tags or [],
        "created_at": datetime.now().isoformat(),
        "access_count": 0,
        "last_accessed": datetime.now().isoformat(),
    }
    memory_db[memory_id] = memory
    return MemoryResponse(**memory)


@router.get("", response_model=List[MemoryResponse])
async def list_memories(category: Optional[str] = None, tag: Optional[str] = None):
    """列出所有记忆，支持筛选"""
    memories = list(memory_db.values())
    
    if category:
        memories = [m for m in memories if m["memory_category"] == category]
    if tag:
        memories = [m for m in memories if tag in m["memory_tags"]]
    
    return [MemoryResponse(**m) for m in memories]


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str):
    """获取单个记忆详情"""
    if memory_id not in memory_db:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    memory = memory_db[memory_id]
    memory["access_count"] += 1
    memory["last_accessed"] = datetime.now().isoformat()
    
    return MemoryResponse(**memory)


@router.get("/search")
async def search_memories(query: str):
    """搜索记忆"""
    results = []
    query_lower = query.lower()
    
    for memory in memory_db.values():
        if (query_lower in memory["memory_title"].lower() or
            query_lower in memory["memory_content"].lower() or
            any(query_lower in tag.lower() for tag in memory["memory_tags"])):
            results.append(memory)
    
    return [MemoryResponse(**m) for m in results]


@router.get("/knowledge-graph/summary")
async def get_knowledge_graph_summary():
    """获取知识图谱摘要"""
    categories = {}
    for memory in memory_db.values():
        cat = memory["memory_category"]
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    return {
        "total_memories": len(memory_db),
        "categories": categories,
        "total_nodes": len(knowledge_graph),
        "total_edges": sum(len(edges) for edges in knowledge_graph.values()),
    }
