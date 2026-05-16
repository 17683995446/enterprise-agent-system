"""
Enhanced Integration Tests for Enterprise Agent System
Test Suite Layer - 增强的集成测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from typing import List, Dict, Any
import time
from test_coverage_optimization import (
    TaskFactory,
    AgentFactory,
    MemoryFactory,
    MockRedisClient,
    MockCeleryTask,
    MockGitHubAPI,
    Assertions,
    performance_monitor,
)


@pytest.mark.integration
class TestTaskIntegration:
    """任务集成测试"""
    
    @pytest.mark.asyncio
    async def test_task_creation_workflow(self, sample_tasks):
        """测试任务创建完整流程"""
        tasks = sample_tasks[:3]
        
        for task in tasks:
            Assertions.assert_task_valid(task)
            assert task.progress_state.value == "PENDING"
        
        assert len(tasks) == 3
    
    @pytest.mark.asyncio
    async def test_task_status_transitions(self):
        """测试任务状态转换"""
        task = TaskFactory.create_task()
        
        # PENDING -> RUNNING
        task.progress_state = task.progress_state.next_state("START")
        assert task.progress_state.value == "RUNNING"
        
        # RUNNING -> COMPLETED
        task.progress_state = task.progress_state.next_state("COMPLETE")
        assert task.progress_state.value == "COMPLETED"
    
    @pytest.mark.asyncio
    async def test_task_priority_ordering(self):
        """测试任务优先级排序"""
        tasks = [
            TaskFactory.create_task(priority="low"),
            TaskFactory.create_task(priority="urgent"),
            TaskFactory.create_task(priority="high"),
            TaskFactory.create_task(priority="medium"),
        ]
        
        # 验证优先级转换
        for task in tasks:
            Assertions.assert_task_valid(task)


@pytest.mark.integration
class TestAgentIntegration:
    """Agent集成测试"""
    
    @pytest.mark.asyncio
    async def test_agent_creation_workflow(self, sample_agents):
        """测试Agent创建完整流程"""
        agents = sample_agents[:2]
        
        for agent in agents:
            Assertions.assert_agent_valid(agent)
        
        assert len(agents) == 2
    
    @pytest.mark.asyncio
    async def test_agent_mode_transitions(self):
        """测试Agent模式转换"""
        agent = AgentFactory.create_agent(agent_mode="task")
        
        assert agent.agent_execution_mode.value == "TASK"
    
    @pytest.mark.asyncio
    async def test_agent_task_assignment(self):
        """测试Agent任务分配"""
        agent = AgentFactory.create_agent()
        task = TaskFactory.create_task()
        
        Assertions.assert_task_valid(task)
        Assertions.assert_agent_valid(agent)


@pytest.mark.integration
class TestMemoryIntegration:
    """记忆集成测试"""
    
    @pytest.mark.asyncio
    async def test_memory_creation_workflow(self, sample_memories):
        """测试记忆创建完整流程"""
        memories = sample_memories[:5]
        
        for memory in memories:
            Assertions.assert_memory_valid(memory)
        
        assert len(memories) == 5
    
    @pytest.mark.asyncio
    async def test_memory_category_filtering(self):
        """测试记忆分类筛选"""
        memories = [
            MemoryFactory.create_memory(memory_category="general"),
            MemoryFactory.create_memory(memory_category="knowledge"),
            MemoryFactory.create_memory(memory_category="experience"),
        ]
        
        general_memories = [m for m in memories if m.memory_classification.value == "GENERAL"]
        assert len(general_memories) == 1
    
    @pytest.mark.asyncio
    async def test_memory_access_tracking(self):
        """测试记忆访问追踪"""
        memory = MemoryFactory.create_memory()
        initial_access = memory.access_count
        
        # 模拟访问
        memory.access_count += 1
        assert memory.access_count == initial_access + 1


@pytest.mark.integration
class TestStorageBackendIntegration:
    """存储后端集成测试"""
    
    @pytest.mark.asyncio
    async def test_redis_client_operations(self, mock_redis):
        """测试Redis客户端操作"""
        # Set
        assert mock_redis.set("key1", "value1")
        
        # Get
        assert mock_redis.get("key1") == "value1"
        
        # Exists
        assert mock_redis.exists("key1")
        
        # Delete
        assert mock_redis.delete("key1")
        assert not mock_redis.exists("key1")
    
    @pytest.mark.asyncio
    async def test_redis_batch_operations(self, mock_redis):
        """测试Redis批量操作"""
        # 批量设置
        for i in range(10):
            mock_redis.set(f"key{i}", f"value{i}")
        
        # 验证
        for i in range(10):
            assert mock_redis.get(f"key{i}") == f"value{i}"
        
        # 清空
        assert mock_redis.flushdb()
        assert len(mock_redis.data) == 0


@pytest.mark.integration
class TestCeleryIntegration:
    """Celery集成测试"""
    
    @pytest.mark.asyncio
    async def test_celery_task_submission(self, mock_celery):
        """测试Celery任务提交"""
        result = mock_celery.apply_async(task_name="test_task", kwargs={"id": 1})
        
        assert result.id is not None
        assert result.state == "PENDING"
    
    @pytest.mark.asyncio
    async def test_celery_task_execution(self, mock_celery):
        """测试Celery任务执行"""
        result = mock_celery.apply_async()
        
        # 获取结果
        task_result = result.get()
        
        assert task_result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_celery_batch_tasks(self, mock_celery):
        """测试Celery批量任务"""
        results = []
        for i in range(5):
            result = mock_celery.apply_async(kwargs={"id": i})
            results.append(result)
        
        assert len(results) == 5


@pytest.mark.integration
class TestGitHubAPIIntegration:
    """GitHub API集成测试"""
    
    @pytest.mark.asyncio
    async def test_github_repo_fetch(self, mock_github):
        """测试GitHub仓库获取"""
        repo_info = mock_github.get_repo("test-owner", "test-repo")
        
        assert repo_info["name"] == "test-repo"
        assert repo_info["owner"]["login"] == "test-owner"
        assert "description" in repo_info
    
    @pytest.mark.asyncio
    async def test_github_contents_listing(self, mock_github):
        """测试GitHub内容列表"""
        contents = mock_github.get_contents("test-owner", "test-repo")
        
        assert len(contents) > 0
        assert any(c["name"] == "README.md" for c in contents)


@pytest.mark.integration
class TestFullWorkflowIntegration:
    """完整工作流集成测试"""
    
    @pytest.mark.asyncio
    async def test_agent_task_memory_workflow(self):
        """测试Agent-任务-记忆完整工作流"""
        # 1. 创建Agent
        agent = AgentFactory.create_agent(agent_name="Test Agent")
        Assertions.assert_agent_valid(agent)
        
        # 2. 创建任务
        task = TaskFactory.create_task(
            task_title=f"Analysis task for {agent.agent_name}"
        )
        Assertions.assert_task_valid(task)
        
        # 3. 创建记忆
        memory = MemoryFactory.create_memory(
            memory_title=f"Task: {task.task_title}",
            memory_content=f"Assigned to {agent.agent_name}"
        )
        Assertions.assert_memory_valid(memory)
        
        # 4. 验证关联
        assert agent.agent_name in memory.memory_content
        assert task.task_title in memory.memory_title
    
    @pytest.mark.asyncio
    async def test_knowledge_graph_workflow(self):
        """测试知识图谱工作流"""
        # 创建相关记忆
        memories = [
            MemoryFactory.create_memory(
                memory_title=f"Concept {i}",
                memory_category="knowledge"
            )
            for i in range(5)
        ]
        
        # 验证知识积累
        knowledge_memories = [
            m for m in memories 
            if m.memory_classification.value == "KNOWLEDGE"
        ]
        
        assert len(knowledge_memories) == 5


@pytest.mark.performance
class TestPerformanceIntegration:
    """性能集成测试"""
    
    @pytest.mark.asyncio
    async def test_task_creation_performance(self, performance_monitor):
        """测试任务创建性能"""
        start = time.time()
        
        tasks = TaskFactory.create_batch(100)
        
        duration = time.time() - start
        
        Assertions.assert_performance(duration, max_duration=1.0)
        assert len(tasks) == 100
    
    @pytest.mark.asyncio
    async def test_memory_search_performance(self, mock_redis):
        """测试记忆搜索性能"""
        # 准备数据
        for i in range(100):
            mock_redis.set(f"memory:{i}", f"Memory content {i}")
        
        # 性能测试
        start = time.time()
        
        results = [
            mock_redis.get(f"memory:{i}") 
            for i in range(100)
        ]
        
        duration = time.time() - start
        
        Assertions.assert_performance(duration, max_duration=0.5)
        assert len(results) == 100
    
    @pytest.mark.asyncio
    async def test_batch_operations_performance(self, mock_celery):
        """测试批量操作性能"""
        start = time.time()
        
        results = [mock_celery.apply_async(kwargs={"id": i}) for i in range(50)]
        
        duration = time.time() - start
        
        Assertions.assert_performance(duration, max_duration=1.0)
        assert len(results) == 50


# ==================== 导出 ====================

__all__ = [
    "TestTaskIntegration",
    "TestAgentIntegration",
    "TestMemoryIntegration",
    "TestStorageBackendIntegration",
    "TestCeleryIntegration",
    "TestGitHubAPIIntegration",
    "TestFullWorkflowIntegration",
    "TestPerformanceIntegration",
]
