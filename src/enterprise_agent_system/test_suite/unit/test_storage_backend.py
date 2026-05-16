"""
Test Suite - Unit Tests for Storage Backend
测试套件 - 存储后端单元测试
"""

from enterprise_agent_system.core.in_memory_data_storage_backend import (
    get_storage_backend_instance,
    reset_storage_backend_instance,
)
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
    TaskExecutionStatusEnumeration,
)


def test_task_creation_and_retrieval():
    """测试任务创建和检索"""
    passed = 0
    failed = 0

    try:
        reset_storage_backend_instance()
        storage = get_storage_backend_instance()

        task = storage.create_new_task_entry(
            "Test Task",
            "Test Description",
            TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL
        )

        retrieved = storage.retrieve_task_by_id(task.unique_entity_id)
        assert retrieved is not None
        assert retrieved.task_title == "Test Task"

        passed += 1
        print("  ✓ test_task_creation_and_retrieval")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_task_creation_and_retrieval: {e}")

    return passed, failed


def test_task_priority_ordering():
    """测试任务优先级排序"""
    passed = 0
    failed = 0

    try:
        reset_storage_backend_instance()
        storage = get_storage_backend_instance()

        storage.create_new_task_entry("Low Priority", priority_level=TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL)
        storage.create_new_task_entry("High Priority", priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL)
        storage.create_new_task_entry("Urgent Priority", priority_level=TaskPriorityLevelEnumeration.URGENT_PRIORITY_LEVEL)

        pending = storage.retrieve_pending_tasks_sorted_by_priority()

        assert len(pending) == 3
        assert pending[0].priority_level == TaskPriorityLevelEnumeration.URGENT_PRIORITY_LEVEL
        assert pending[1].priority_level == TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL
        assert pending[2].priority_level == TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL

        passed += 1
        print("  ✓ test_task_priority_ordering")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_task_priority_ordering: {e}")

    return passed, failed


def test_memory_creation_and_search():
    """测试记忆创建和搜索"""
    passed = 0
    failed = 0

    try:
        reset_storage_backend_instance()
        storage = get_storage_backend_instance()

        storage.create_new_memory_entry(
            "Python programming basics",
            category_type=MemoryCategoryTypeEnumeration.TECHNICAL_MEMORY_CATEGORY,
            tags_list=["python"],
        )
        storage.create_new_memory_entry(
            "JavaScript for web",
            category_type=MemoryCategoryTypeEnumeration.TECHNICAL_MEMORY_CATEGORY,
            tags_list=["javascript"],
        )

        results = storage.search_memories_by_text_content("python")

        assert len(results) >= 1

        passed += 1
        print("  ✓ test_memory_creation_and_search")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_memory_creation_and_search: {e}")

    return passed, failed


def test_knowledge_graph_operations():
    """测试知识图谱操作"""
    passed = 0
    failed = 0

    try:
        reset_storage_backend_instance()
        storage = get_storage_backend_instance()

        node1 = storage.add_node_to_knowledge_graph("python")
        node2 = storage.add_node_to_knowledge_graph("programming")

        storage.add_edge_to_knowledge_graph(
            node1, node2, "is_used_for"
        )

        stats = storage.retrieve_knowledge_graph_statistics()

        assert stats["total_nodes"] == 2
        assert stats["total_edges"] == 1

        passed += 1
        print("  ✓ test_knowledge_graph_operations")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_knowledge_graph_operations: {e}")

    return passed, failed


def test_statistics_generation():
    """测试统计生成"""
    passed = 0
    failed = 0

    try:
        reset_storage_backend_instance()
        storage = get_storage_backend_instance()

        storage.create_new_task_entry("Task 1")
        storage.create_new_memory_entry("Memory 1")

        stats = storage.generate_system_statistics_snapshot()

        assert stats.total_tasks_count == 1
        assert stats.total_memories_count == 1

        passed += 1
        print("  ✓ test_statistics_generation")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_statistics_generation: {e}")

    return passed, failed


def run_storage_backend_tests():
    """运行所有存储后端测试"""
    print("\nUnit Tests - Storage Backend")

    total_passed = 0
    total_failed = 0

    test_functions = [
        test_task_creation_and_retrieval,
        test_task_priority_ordering,
        test_memory_creation_and_search,
        test_knowledge_graph_operations,
        test_statistics_generation,
    ]

    for test_func in test_functions:
        passed, failed = test_func()
        total_passed += passed
        total_failed += failed

    print(f"  Results: {total_passed} passed, {total_failed} failed")

    return total_passed, total_failed


if __name__ == "__main__":
    run_storage_backend_tests()
