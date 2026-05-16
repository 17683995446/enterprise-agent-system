"""
Python SDK for Enterprise Agent System
应用层 - Python SDK开发包
"""

import asyncio
import aiohttp
import json
from typing import Optional, List, Dict, Any, AsyncIterator
from dataclasses import dataclass, asdict
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class TaskPriority(str, Enum):
    """任务优先级枚举"""
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务数据模型"""
    task_id: str
    task_title: str
    task_description: str
    priority: TaskPriority
    status: TaskStatus
    progress: float
    created_at: str
    updated_at: str
    tags: List[str]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建Task实例"""
        return cls(
            task_id=data['task_id'],
            task_title=data['task_title'],
            task_description=data['task_description'],
            priority=TaskPriority(data['priority']),
            status=TaskStatus(data['status']),
            progress=data['progress'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            tags=data.get('tags', []),
            result=data.get('result'),
            error=data.get('error'),
        )


@dataclass
class Agent:
    """Agent数据模型"""
    agent_id: str
    agent_name: str
    agent_mode: str
    status: str
    created_at: str
    total_tasks: int
    completed_tasks: int
    success_rate: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """从字典创建Agent实例"""
        return cls(
            agent_id=data['agent_id'],
            agent_name=data['agent_name'],
            agent_mode=data['agent_mode'],
            status=data['status'],
            created_at=data['created_at'],
            total_tasks=data['total_tasks'],
            completed_tasks=data['completed_tasks'],
            success_rate=data['success_rate'],
        )


@dataclass
class Memory:
    """记忆数据模型"""
    memory_id: str
    memory_title: str
    memory_content: str
    memory_category: str
    memory_tags: List[str]
    created_at: str
    access_count: int
    last_accessed: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """从字典创建Memory实例"""
        return cls(
            memory_id=data['memory_id'],
            memory_title=data['memory_title'],
            memory_content=data['memory_content'],
            memory_category=data['memory_category'],
            memory_tags=data.get('memory_tags', []),
            created_at=data['created_at'],
            access_count=data['access_count'],
            last_accessed=data['last_accessed'],
        )


class EnterpriseAgentSDK:
    """
    Enterprise Agent System Python SDK
    
    Example:
        ```python
        import asyncio
        from enterprise_agent_sdk import EnterpriseAgentSDK, TaskPriority
        
        async def main():
            sdk = EnterpriseAgentSDK(
                base_url="http://localhost:8000",
                api_key="your-api-key"
            )
            
            # 创建任务
            task = await sdk.tasks.create(
                task_title="分析Vue项目",
                task_description="深度分析Vue.js响应式系统",
                priority=TaskPriority.HIGH
            )
            
            # 查询任务
            task = await sdk.tasks.get(task.task_id)
            print(f"Task status: {task.status}")
            
            # 列出所有任务
            tasks = await sdk.tasks.list(status="completed")
            
        asyncio.run(main())
        ```
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        初始化SDK
        
        Args:
            base_url: API基础URL
            api_key: API密钥
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None
        
        # 初始化子客户端
        self.tasks = TasksClient(self)
        self.agents = AgentsClient(self)
        self.memory = MemoryClient(self)
        self.projects = ProjectsClient(self)
    
    @property
    def session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self._session is None or self._session.closed:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            self._session = aiohttp.ClientSession(
                timeout=self.timeout,
                headers=headers,
            )
        return self._session
    
    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            params: 查询参数
            json_data: JSON数据
        
        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:
                        # Rate limit - wait and retry
                        await asyncio.sleep(2 ** attempt)
                        continue
                    else:
                        error_data = await response.json() if response.content_type == 'application/json' else {}
                        raise SDKError(
                            f"API request failed: {response.status}",
                            status_code=response.status,
                            error_data=error_data,
                        )
            except aiohttp.ClientError as e:
                if attempt == self.max_retries - 1:
                    raise SDKError(f"Network error: {e}")
                await asyncio.sleep(2 ** attempt)
        
        raise SDKError("Max retries exceeded")
    
    async def close(self):
        """关闭SDK会话"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()


class TasksClient:
    """任务管理客户端"""
    
    def __init__(self, sdk: EnterpriseAgentSDK):
        self.sdk = sdk
    
    async def create(
        self,
        task_title: str,
        task_description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        tags: Optional[List[str]] = None,
    ) -> Task:
        """
        创建新任务
        
        Args:
            task_title: 任务标题
            task_description: 任务描述
            priority: 优先级
            tags: 标签列表
        
        Returns:
            创建的任务
        """
        data = await self.sdk.request(
            method="POST",
            endpoint="/api/tasks",
            json_data={
                "task_title": task_title,
                "task_description": task_description,
                "priority": priority.value,
                "tags": tags or [],
            },
        )
        return Task.from_dict(data)
    
    async def get(self, task_id: str) -> Task:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务详情
        """
        data = await self.sdk.request(
            method="GET",
            endpoint=f"/api/tasks/{task_id}",
        )
        return Task.from_dict(data)
    
    async def list(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Task]:
        """
        列出任务
        
        Args:
            status: 状态筛选
            priority: 优先级筛选
            page: 页码
            page_size: 每页数量
        
        Returns:
            任务列表
        """
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status.value
        if priority:
            params["priority"] = priority.value
        
        data = await self.sdk.request(
            method="GET",
            endpoint="/api/tasks",
            params=params,
        )
        return [Task.from_dict(task) for task in data]
    
    async def update(
        self,
        task_id: str,
        task_title: Optional[str] = None,
        task_description: Optional[str] = None,
        priority: Optional[TaskPriority] = None,
    ) -> Task:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            task_title: 新标题
            task_description: 新描述
            priority: 新优先级
        
        Returns:
            更新后的任务
        """
        json_data = {}
        if task_title:
            json_data["task_title"] = task_title
        if task_description:
            json_data["task_description"] = task_description
        if priority:
            json_data["priority"] = priority.value
        
        data = await self.sdk.request(
            method="PUT",
            endpoint=f"/api/tasks/{task_id}",
            json_data=json_data,
        )
        return Task.from_dict(data)
    
    async def delete(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            是否成功
        """
        await self.sdk.request(
            method="DELETE",
            endpoint=f"/api/tasks/{task_id}",
        )
        return True
    
    async def start(self, task_id: str) -> Task:
        """启动任务"""
        data = await self.sdk.request(
            method="POST",
            endpoint=f"/api/tasks/{task_id}/start",
        )
        return await self.get(task_id)
    
    async def complete(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> Task:
        """完成任务"""
        await self.sdk.request(
            method="POST",
            endpoint=f"/api/tasks/{task_id}/complete",
            json_data={"result": result} if result else None,
        )
        return await self.get(task_id)
    
    async def statistics(self) -> Dict[str, Any]:
        """获取任务统计"""
        return await self.sdk.request(
            method="GET",
            endpoint="/api/tasks/statistics/summary",
        )


class AgentsClient:
    """Agent管理客户端"""
    
    def __init__(self, sdk: EnterpriseAgentSDK):
        self.sdk = sdk
    
    async def create(
        self,
        agent_name: str,
        agent_mode: str = "dual",
    ) -> Agent:
        """创建Agent"""
        data = await self.sdk.request(
            method="POST",
            endpoint="/api/agents",
            json_data={
                "agent_name": agent_name,
                "agent_mode": agent_mode,
            },
        )
        return Agent.from_dict(data)
    
    async def get(self, agent_id: str) -> Agent:
        """获取Agent详情"""
        data = await self.sdk.request(
            method="GET",
            endpoint=f"/api/agents/{agent_id}",
        )
        return Agent.from_dict(data)
    
    async def list(self) -> List[Agent]:
        """列出所有Agent"""
        data = await self.sdk.request(
            method="GET",
            endpoint="/api/agents",
        )
        return [Agent.from_dict(agent) for agent in data]
    
    async def start(self, agent_id: str) -> bool:
        """启动Agent"""
        await self.sdk.request(
            method="POST",
            endpoint=f"/api/agents/{agent_id}/start",
        )
        return True
    
    async def stop(self, agent_id: str) -> bool:
        """停止Agent"""
        await self.sdk.request(
            method="POST",
            endpoint=f"/api/agents/{agent_id}/stop",
        )
        return True


class MemoryClient:
    """知识图谱记忆客户端"""
    
    def __init__(self, sdk: EnterpriseAgentSDK):
        self.sdk = sdk
    
    async def create(
        self,
        memory_title: str,
        memory_content: str,
        memory_category: str = "general",
        memory_tags: Optional[List[str]] = None,
    ) -> Memory:
        """创建记忆"""
        data = await self.sdk.request(
            method="POST",
            endpoint="/api/memory",
            json_data={
                "memory_title": memory_title,
                "memory_content": memory_content,
                "memory_category": memory_category,
                "memory_tags": memory_tags or [],
            },
        )
        return Memory.from_dict(data)
    
    async def get(self, memory_id: str) -> Memory:
        """获取记忆详情"""
        data = await self.sdk.request(
            method="GET",
            endpoint=f"/api/memory/{memory_id}",
        )
        return Memory.from_dict(data)
    
    async def list(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Memory]:
        """列出记忆"""
        params = {}
        if category:
            params["category"] = category
        if tag:
            params["tag"] = tag
        
        data = await self.sdk.request(
            method="GET",
            endpoint="/api/memory",
            params=params if params else None,
        )
        return [Memory.from_dict(m) for m in data]
    
    async def search(self, query: str) -> List[Memory]:
        """搜索记忆"""
        data = await self.sdk.request(
            method="GET",
            endpoint="/api/memory/search",
            params={"query": query},
        )
        return [Memory.from_dict(m) for m in data]
    
    async def knowledge_graph_summary(self) -> Dict[str, Any]:
        """获取知识图谱摘要"""
        return await self.sdk.request(
            method="GET",
            endpoint="/api/memory/knowledge-graph/summary",
        )


class ProjectsClient:
    """项目分析客户端"""
    
    def __init__(self, sdk: EnterpriseAgentSDK):
        self.sdk = sdk
    
    async def analyze(
        self,
        project_path: str,
        analysis_type: str = "auto",
    ) -> Dict[str, Any]:
        """
        分析本地项目
        
        Args:
            project_path: 项目路径
            analysis_type: 分析类型
        
        Returns:
            分析结果
        """
        return await self.sdk.request(
            method="POST",
            endpoint="/api/projects/analyze",
            json_data={
                "project_path": project_path,
                "analysis_type": analysis_type,
            },
        )
    
    async def analyze_github(
        self,
        owner: str,
        repo: str,
    ) -> Dict[str, Any]:
        """分析GitHub仓库"""
        return await self.sdk.request(
            method="POST",
            endpoint="/api/projects/analyze-github",
            params={"owner": owner, "repo": repo},
        )
    
    async def supported_types(self) -> Dict[str, Any]:
        """获取支持的项目类型"""
        return await self.sdk.request(
            method="GET",
            endpoint="/api/projects/supported-types",
        )


class SDKError(Exception):
    """SDK异常"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data or {}


# 导出公开API
__all__ = [
    "EnterpriseAgentSDK",
    "TaskPriority",
    "TaskStatus",
    "Task",
    "Agent",
    "Memory",
    "SDKError",
]
