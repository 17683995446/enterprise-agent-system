"""
Test Suite - Unit Tests for Domain Models
测试套件 - 领域模型单元测试
"""

from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionDataModel,
    MemoryStorageDataModel,
    ExperienceLearningDataModel,
    SystemStatisticsSnapshotModel,
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
    AgentOperatingModeEnumeration,
    generate_unique_entity_identifier,
    get_current_utc_timestamp,
)


def test_task_model_creation():
    """测试任务模型创建"""
    passed = 0
    failed = 0

    try:
        task = TaskExecutionDataModel(
            task_title="Test Task",
            task_description="Test Description"
        )
        assert task.unique_entity_id is not None
        assert task.task_title == "Test Task"
        assert task.execution_status == TaskExecutionStatusEnumeration.PENDING_STATUS
        passed += 1
        print("  ✓ test_task_model_creation")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_task_model_creation: {e}")

    return passed, failed


def test_task_progress_validation():
    """测试任务进度验证"""
    passed = 0
    failed = 0

    try:
        task = TaskExecutionDataModel(task_title="Validation Test")
        task.progress_percentage_value = 1.5
        assert task.progress_percentage_value == 1.0

        task.progress_percentage_value = -0.5
        assert task.progress_percentage_value == 0.0

        passed += 1
        print("  ✓ test_task_progress_validation")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_task_progress_validation: {e}")

    return passed, failed


def test_memory_model_creation():
    """测试记忆模型创建"""
    passed = 0
    failed = 0

    try:
        memory = MemoryStorageDataModel(
            content_text_body="This is a test memory",
            category_type=MemoryCategoryTypeEnumeration.TECHNICAL_MEMORY_CATEGORY,
            tags_list=["test", "example"],
            importance_score=5,
        )

        assert memory.unique_memory_id is not None
        assert memory.content_text_body == "This is a test memory"
        assert memory.category_type == MemoryCategoryTypeEnumeration.TECHNICAL_MEMORY_CATEGORY
        passed += 1
        print("  ✓ test_memory_model_creation")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_memory_model_creation: {e}")

    return passed, failed


def test_experience_model_creation():
    """测试经验模型创建"""
    passed = 0
    failed = 0

    try:
        experience = ExperienceLearningDataModel(
            task_reference_id="task_123",
            task_type_label="data_analysis",
            was_successful_flag=True,
            duration_seconds_value=10.5,
            lessons_learned_list=["Lesson 1", "Lesson 2"],
        )

        assert experience.unique_experience_id is not None
        assert experience.task_reference_id == "task_123"
        assert experience.was_successful_flag is True
        passed += 1
        print("  ✓ test_experience_model_creation")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_experience_model_creation: {e}")

    return passed, failed


def test_unique_identifier_generation():
    """测试唯一标识符生成"""
    passed = 0
    failed = 0

    try:
        id1 = generate_unique_entity_identifier("test")
        id2 = generate_unique_entity_identifier("test")

        assert id1 != id2
        assert id1.startswith("test_")

        passed += 1
        print("  ✓ test_unique_identifier_generation")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_unique_identifier_generation: {e}")

    return passed, failed


def test_enumeration_values():
    """测试枚举值"""
    passed = 0
    failed = 0

    try:
        assert TaskExecutionStatusEnumeration.PENDING_STATUS.value == "pending"
        assert TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL.value == 3
        assert MemoryCategoryTypeEnumeration.EXPERIENCE_MEMORY_CATEGORY.value == "experience"
        assert AgentOperatingModeEnumeration.IDLE_IMPROVEMENT_MODE.value == "idle_improvement"

        passed += 1
        print("  ✓ test_enumeration_values")
    except Exception as e:
        failed += 1
        print(f"  ✗ test_enumeration_values: {e}")

    return passed, failed


def run_domain_model_tests():
    """运行所有领域模型测试"""
    print("\nUnit Tests - Domain Models")

    total_passed = 0
    total_failed = 0

    test_functions = [
        test_task_model_creation,
        test_task_progress_validation,
        test_memory_model_creation,
        test_experience_model_creation,
        test_unique_identifier_generation,
        test_enumeration_values,
    ]

    for test_func in test_functions:
        passed, failed = test_func()
        total_passed += passed
        total_failed += failed

    print(f"  Results: {total_passed} passed, {total_failed} failed")

    return total_passed, total_failed


if __name__ == "__main__":
    run_domain_model_tests()
