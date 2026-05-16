"""
Test Suite - Integration Tests for Agent
测试套件 - Agent 集成测试
"""

import pytest
import asyncio

from enterprise_agent_system.core.agent_orchestrator_and_executor import (
    AgentOrchestratorAndExecutor,
)
from enterprise_agent_system.core.storage_backend_factory import (
    reset_storage_backend_instance,
    get_storage_factory,
)
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskPriorityLevelEnumeration,
    TaskExecutionStatusEnumeration,
)


def test_agent_initialization():
    """Test Agent initialization"""
    reset_storage_backend_instance()
    agent = AgentOrchestratorAndExecutor("Test Agent")

    assert agent.agent_name == "Test Agent"
    assert "idle" in agent.current_operating_mode.value


def test_agent_task_creation():
    """Test Agent task creation"""
    reset_storage_backend_instance()
    agent = AgentOrchestratorAndExecutor("Test Agent")

    task_id = agent.create_and_queue_task(
        "Test Task",
        "Test Description",
        priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL
    )

    assert task_id is not None

    task = agent.storage_backend.retrieve_task_by_id(task_id)
    assert task is not None
    assert task.task_title == "Test Task"
    assert task.priority_level == TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL


@pytest.mark.asyncio
async def test_agent_task_execution():
    """Test Agent task execution"""
    reset_storage_backend_instance()
    agent = AgentOrchestratorAndExecutor("Test Agent")

    task_id = agent.create_and_queue_task(
        "Execution Test",
        "",
        priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL
    )

    task = await agent.execute_task_by_id(task_id)

    assert task.execution_status == TaskExecutionStatusEnumeration.COMPLETED_STATUS
    assert len(task.execution_steps_list) > 0


def test_agent_statistics():
    """Test Agent statistics"""
    reset_storage_backend_instance()
    agent = AgentOrchestratorAndExecutor("Test Agent")

    agent.create_and_queue_task("Task 1")
    agent.create_and_queue_task("Task 2")

    stats = agent.current_system_statistics

    assert stats.total_tasks_count == 2
    assert stats.pending_tasks_count == 2


@pytest.mark.asyncio
async def test_agent_full_workflow():
    """Test Agent full workflow"""
    reset_storage_backend_instance()
    agent = AgentOrchestratorAndExecutor("Workflow Test")

    agent.create_and_queue_task(
        "Task 1",
        "",
        priority_level=TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL
    )
    agent.create_and_queue_task(
        "Task 2",
        "",
        priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL
    )

    await agent.run_main_execution_loop(max_iteration_count=5)

    stats = agent.current_system_statistics

    assert stats.completed_tasks_count >= 1
    assert stats.total_memories_count >= 1


def run_agent_integration_tests():
    """Run all Agent integration tests"""
    print("\nIntegration Tests - Agent")

    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "not test_agent_task_execution and not test_agent_full_workflow"
    ])

    print("\nRunning async tests...")
    asyncio.run(pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-k", "test_agent_task_execution or test_agent_full_workflow"
    ]))


if __name__ == "__main__":
    run_agent_integration_tests()
