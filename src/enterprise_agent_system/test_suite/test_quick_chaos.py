"""
快速混乱测试 - 发现真实的生产级bug
"""

import sys
import time
import random
import threading
import uuid
import traceback
from typing import Dict, Any

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance
from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration
)

logger = get_logger_instance('quick_chaos_test')

def test_task_priority_validation():
    """测试任务优先级验证"""
    logger.info("\n=== 测试任务优先级验证 ===")
    backend = InMemoryDataStorageBackend()
    errors = []
    
    test_cases = [
        # 正常的枚举
        TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL,
        TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
        TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL,
        TaskPriorityLevelEnumeration.URGENT_PRIORITY_LEVEL,
        # 字符串名称
        'LOW_PRIORITY_LEVEL', 'MEDIUM_PRIORITY_LEVEL', 'HIGH_PRIORITY_LEVEL', 'URGENT_PRIORITY_LEVEL',
        # 短字符串
        'low', 'medium', 'high', 'urgent',
        # 无效值
        'invalid', None, 123, []
    ]
    
    for i, priority in enumerate(test_cases):
        try:
            task = backend.create_new_task_entry(
                task_title=f'Test {i}',
                priority_level=priority
            )
            logger.info(f"  ✓ 成功: {type(priority).__name__} = {priority}")
        except Exception as e:
            logger.error(f"  ✗ 错误: {type(priority).__name__} = {priority} → {type(e).__name__}: {e}")
            errors.append((priority, e))
    
    return errors

def test_status_validation():
    """测试状态验证"""
    logger.info("\n=== 测试状态验证 ===")
    backend = InMemoryDataStorageBackend()
    errors = []
    
    task = backend.create_new_task_entry('Test')
    
    test_cases = [
        # 正常枚举
        TaskExecutionStatusEnumeration.PENDING_STATUS,
        TaskExecutionStatusEnumeration.IN_PROGRESS_STATUS,
        TaskExecutionStatusEnumeration.COMPLETED_STATUS,
        TaskExecutionStatusEnumeration.FAILED_STATUS,
        # 字符串
        'pending', 'in_progress', 'completed', 'failed',
        # 无效值
        'invalid', None, 123
    ]
    
    for i, status in enumerate(test_cases):
        try:
            backend.update_task_entry(
                task.unique_entity_id,
                execution_status=status
            )
            logger.info(f"  ✓ 成功: {type(status).__name__} = {status}")
        except Exception as e:
            logger.error(f"  ✗ 错误: {type(status).__name__} = {status} → {type(e).__name__}: {e}")
            errors.append((status, e))
    
    return errors

def test_memory_category_validation():
    """测试记忆类别验证"""
    logger.info("\n=== 测试记忆类别验证 ===")
    backend = InMemoryDataStorageBackend()
    errors = []
    
    test_cases = [
        # 正常枚举
        MemoryCategoryTypeEnumeration.GENERAL_MEMORY_CATEGORY,
        MemoryCategoryTypeEnumeration.TECHNICAL_MEMORY_CATEGORY,
        MemoryCategoryTypeEnumeration.EXPERIENCE_MEMORY_CATEGORY,
        MemoryCategoryTypeEnumeration.KNOWLEDGE_MEMORY_CATEGORY,
        # 字符串
        'general', 'technical', 'experience', 'knowledge',
        # 完整名称
        'GENERAL_MEMORY_CATEGORY', 'TECHNICAL_MEMORY_CATEGORY',
        # 无效值
        'invalid', None
    ]
    
    for i, category in enumerate(test_cases):
        try:
            backend.create_new_memory_entry(
                content_text=f'Test {i}',
                category_type=category
            )
            logger.info(f"  ✓ 成功: {type(category).__name__} = {category}")
        except Exception as e:
            logger.error(f"  ✗ 错误: {type(category).__name__} = {category} → {type(e).__name__}: {e}")
            errors.append((category, e))
    
    return errors

def test_concurrent_contention():
    """测试并发竞争"""
    logger.info("\n=== 测试并发竞争 ===")
    backend = InMemoryDataStorageBackend()
    errors = []
    error_lock = threading.Lock()
    completed = threading.Event()
    
    def worker(thread_id):
        try:
            for i in range(100):
                # 创建任务
                task = backend.create_new_task_entry(f'Thread {thread_id} Task {i}')
                
                # 更新任务
                for j in range(5):
                    backend.update_task_entry(
                        task.unique_entity_id,
                        execution_status=random.choice(list(TaskExecutionStatusEnumeration)),
                        progress_percentage_value=random.random()
                    )
                
                # 创建记忆
                for j in range(3):
                    backend.create_new_memory_entry(f'Thread {thread_id} Memory {i}-{j}')
                
                # 统计操作
                if random.random() > 0.5:
                    backend.retrieve_all_tasks()
                    backend.retrieve_all_memories()
                    backend.generate_system_statistics_snapshot()
                    backend.retrieve_pending_tasks_sorted_by_priority()
        except Exception as e:
            with error_lock:
                errors.append((thread_id, e))
    
    threads = []
    for i in range(50):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    logger.info(f"  ✓ 并发测试完成，错误数: {len(errors)}")
    return errors

def test_edge_cases():
    """测试边缘情况"""
    logger.info("\n=== 测试边缘情况 ===")
    backend = InMemoryDataStorageBackend()
    store = SimpleMemoryStore()
    cache = SimpleCache()
    errors = []
    
    # 空字符串测试
    try:
        task = backend.create_new_task_entry('')
        logger.info("  ✓ 空标题成功")
    except Exception as e:
        logger.error(f"  ✗ 空标题错误: {e}")
        errors.append(e)
    
    # None值测试
    try:
        task = backend.create_new_task_entry('Test', task_description=None)
        logger.info("  ✓ None描述成功")
    except Exception as e:
        logger.error(f"  ✗ None描述错误: {e}")
        errors.append(e)
    
    # 超大字符串
    try:
        long_str = 'x' * 10000
        task = backend.create_new_task_entry('Long', task_description=long_str)
        logger.info("  ✓ 长描述成功")
    except Exception as e:
        logger.error(f"  ✗ 长描述错误: {e}")
        errors.append(e)
    
    # 存储报告测试
    try:
        store.save_report({'id': str(uuid.uuid4()), 'title': 'Test'})
        logger.info("  ✓ 存储报告成功")
    except Exception as e:
        logger.error(f"  ✗ 存储报告错误: {e}")
        errors.append(e)
    
    # 缓存测试
    try:
        cache.set('key', None)
        cache.set('key2', [1, 2, 3])
        cache.set('key3', {'nested': {'x': 1}})
        logger.info("  ✓ 缓存各种值成功")
    except Exception as e:
        logger.error(f"  ✗ 缓存错误: {e}")
        errors.append(e)
    
    return errors

def main():
    """主函数"""
    all_errors = []
    
    # 运行所有测试
    all_errors.extend(test_task_priority_validation())
    all_errors.extend(test_status_validation())
    all_errors.extend(test_memory_category_validation())
    all_errors.extend(test_concurrent_contention())
    all_errors.extend(test_edge_cases())
    
    # 总结
    logger.info(f"\n{'='*60}")
    logger.info(f"总结: 发现 {len(all_errors)} 个问题")
    if all_errors:
        logger.error("\n问题列表:")
        for i, error in enumerate(all_errors[:20]):
            logger.error(f"  [{i+1}] {error}")
        return 1
    else:
        logger.info("🎉 没有发现问题！")
        return 0

if __name__ == '__main__':
    sys.exit(main())
