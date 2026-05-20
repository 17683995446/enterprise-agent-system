"""
Test InMemoryDataStorageBackend Thread Safety
测试内存存储后端的线程安全性

This test intentionally tries to find race conditions
这个测试专门尝试发现竞态条件
"""

import threading
import time
import random
from typing import List
from enterprise_agent_system.core.in_memory_data_storage_backend import (
    InMemoryDataStorageBackend,
)
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
)


def test_thread_safety_task_creation():
    """测试任务创建的线程安全性"""
    storage = InMemoryDataStorageBackend()
    num_threads = 100
    tasks_per_thread = 100
    errors = []
    
    def create_tasks(thread_id):
        try:
            for i in range(tasks_per_thread):
                task = storage.create_new_task_entry(
                    task_title=f"Thread-{thread_id}-Task-{i}",
                    task_description=f"Test task from thread {thread_id}",
                    priority_level=TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL
                )
                # 立即验证任务被正确存储
                retrieved = storage.retrieve_task_by_id(task.unique_entity_id)
                if not retrieved:
                    errors.append(f"Task {task.unique_entity_id} not found after creation")
        except Exception as e:
            errors.append(f"Thread {thread_id} error: {str(e)}")
    
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        t = threading.Thread(target=create_tasks, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    all_tasks = storage.retrieve_all_tasks()
    expected_count = num_threads * tasks_per_thread
    
    print(f"\n=== Task Creation Thread Safety Test ===")
    print(f"Expected tasks: {expected_count}")
    print(f"Actual tasks: {len(all_tasks)}")
    print(f"Errors: {len(errors)}")
    print(f"Duration: {end_time - start_time:.2f}s")
    
    if errors:
        print("Errors encountered:")
        for err in errors[:10]:
            print(f"  - {err}")
    
    assert len(errors) == 0, f"Encountered {len(errors)} errors"
    assert len(all_tasks) == expected_count, f"Task count mismatch: expected {expected_count}, got {len(all_tasks)}"
    
    return len(all_tasks) == expected_count and len(errors) == 0


def test_thread_safety_concurrent_updates():
    """测试并发更新的线程安全性"""
    storage = InMemoryDataStorageBackend()
    task = storage.create_new_task_entry(
        task_title="Concurrency Test Task",
        task_description="Test concurrent updates"
    )
    task_id = task.unique_entity_id
    
    num_threads = 50
    updates_per_thread = 200
    errors = []
    
    def update_task(thread_id):
        try:
            for i in range(updates_per_thread):
                # 尝试不同的更新方式
                update_type = i % 3
                if update_type == 0:
                    storage.update_task_entry(
                        task_id,
                        progress_percentage_value=random.random(),
                        execution_result_message=f"Update from thread {thread_id}-{i}"
                    )
                elif update_type == 1:
                    storage.update_task_entry(
                        task_id,
                        execution_status=random.choice([
                            TaskExecutionStatusEnumeration.PENDING_STATUS,
                            TaskExecutionStatusEnumeration.IN_PROGRESS_STATUS,
                            TaskExecutionStatusEnumeration.COMPLETED_STATUS
                        ])
                    )
                else:
                    task_obj = storage.retrieve_task_by_id(task_id)
                    if task_obj:
                        # 直接修改对象
                        task_obj.progress_percentage_value = min(1.0, task_obj.progress_percentage_value + 0.001)
        except Exception as e:
            errors.append(f"Thread {thread_id} error: {str(e)}")
    
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        t = threading.Thread(target=update_task, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    print(f"\n=== Concurrent Updates Test ===")
    print(f"Threads: {num_threads}")
    print(f"Updates per thread: {updates_per_thread}")
    print(f"Total attempted updates: {num_threads * updates_per_thread}")
    print(f"Errors: {len(errors)}")
    print(f"Duration: {end_time - start_time:.2f}s")
    
    final_task = storage.retrieve_task_by_id(task_id)
    print(f"Final task status: {final_task.execution_status if final_task else 'None'}")
    print(f"Final progress: {final_task.progress_percentage_value if final_task else 'N/A'}")
    
    if errors:
        print("Errors encountered:")
        for err in errors[:10]:
            print(f"  - {err}")
    
    return len(errors) == 0


def test_thread_safety_memory_operations():
    """测试记忆操作的线程安全性"""
    storage = InMemoryDataStorageBackend()
    num_threads = 80
    memories_per_thread = 80
    errors = []
    created_memory_ids: List[str] = []
    lock = threading.Lock()
    
    def create_and_access_memories(thread_id):
        try:
            local_ids = []
            for i in range(memories_per_thread):
                memory = storage.create_new_memory_entry(
                    content_text=f"Memory from thread {thread_id} - content {i}",
                    category_type=MemoryCategoryTypeEnumeration.GENERAL_MEMORY_CATEGORY,
                    tags_list=[f"thread_{thread_id}", f"tag_{i}"],
                    importance_score=random.randint(1, 5)
                )
                local_ids.append(memory.unique_memory_id)
                
                # 随机访问其他记忆
                if i > 0 and random.random() < 0.3:
                    random_id = random.choice(local_ids[:-1])
                    retrieved = storage.retrieve_memory_by_id(random_id)
                    if not retrieved:
                        errors.append(f"Memory {random_id} disappeared")
            
            with lock:
                created_memory_ids.extend(local_ids)
                
        except Exception as e:
            errors.append(f"Thread {thread_id} error: {str(e)}")
    
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        t = threading.Thread(target=create_and_access_memories, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    all_memories = storage.retrieve_all_memories()
    expected_count = num_threads * memories_per_thread
    
    print(f"\n=== Memory Operations Thread Safety Test ===")
    print(f"Expected memories: {expected_count}")
    print(f"Actual memories: {len(all_memories)}")
    print(f"Tracked IDs: {len(created_memory_ids)}")
    print(f"Errors: {len(errors)}")
    print(f"Duration: {end_time - start_time:.2f}s")
    
    if errors:
        print("Errors encountered:")
        for err in errors[:10]:
            print(f"  - {err}")
    
    # 检查是否有重复ID（这会很糟糕！）
    id_set = set(created_memory_ids)
    if len(id_set) != len(created_memory_ids):
        print(f"WARNING: Duplicate memory IDs found!")
        print(f"  Unique: {len(id_set)}, Total: {len(created_memory_ids)}")
    
    return len(errors) == 0 and len(all_memories) == expected_count


def test_thread_safety_knowledge_graph():
    """测试知识图谱操作的线程安全性"""
    storage = InMemoryDataStorageBackend()
    num_threads = 60
    operations_per_thread = 50
    errors = []
    node_ids: List[str] = []
    node_lock = threading.Lock()
    
    # 先创建一些初始节点
    initial_nodes = []
    for i in range(20):
        node_id = storage.add_node_to_knowledge_graph(
            label=f"initial_node_{i}",
            properties={"index": i}
        )
        initial_nodes.append(node_id)
        node_ids.append(node_id)
    
    def graph_operations(thread_id):
        try:
            local_nodes = []
            for i in range(operations_per_thread):
                op_type = random.randint(0, 2)
                
                if op_type == 0:
                    # 添加节点
                    node_id = storage.add_node_to_knowledge_graph(
                        label=f"thread_{thread_id}_node_{i}",
                        properties={"thread_id": thread_id, "iteration": i}
                    )
                    local_nodes.append(node_id)
                    with node_lock:
                        node_ids.append(node_id)
                
                elif op_type == 1 and len(node_ids) >= 2:
                    # 添加边
                    with node_lock:
                        if len(node_ids) >= 2:
                            source_idx = random.randint(0, len(node_ids) - 1)
                            target_idx = random.randint(0, len(node_ids) - 1)
                            while target_idx == source_idx:
                                target_idx = random.randint(0, len(node_ids) - 1)
                            source_id = node_ids[source_idx]
                            target_id = node_ids[target_idx]
                    
                    try:
                        storage.add_edge_to_knowledge_graph(
                            source_node_id=source_id,
                            target_node_id=target_id,
                            relationship_type=f"rel_from_{thread_id}",
                            weight=random.random()
                        )
                    except ValueError:
                        # 节点可能被其他操作影响，这是可以接受的
                        pass
                
                else:
                    # 获取统计信息
                    stats = storage.retrieve_knowledge_graph_statistics()
                    _ = stats["total_nodes"]
                    _ = stats["total_edges"]
        
        except Exception as e:
            errors.append(f"Thread {thread_id} error: {str(e)}")
    
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        t = threading.Thread(target=graph_operations, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    final_stats = storage.retrieve_knowledge_graph_statistics()
    
    print(f"\n=== Knowledge Graph Thread Safety Test ===")
    print(f"Final nodes: {final_stats['total_nodes']}")
    print(f"Final edges: {final_stats['total_edges']}")
    print(f"Errors: {len(errors)}")
    print(f"Duration: {end_time - start_time:.2f}s")
    
    if errors:
        print("Errors encountered:")
        for err in errors[:10]:
            print(f"  - {err}")
    
    return len(errors) == 0


def test_thread_safety_mixed_workload():
    """测试混合工作负载的线程安全性 - 最严格的测试"""
    storage = InMemoryDataStorageBackend()
    num_threads = 120
    operations_per_thread = 100
    errors = []
    
    def mixed_operations(thread_id):
        try:
            for i in range(operations_per_thread):
                op_type = random.randint(0, 4)
                
                if op_type == 0:
                    # 创建任务
                    task = storage.create_new_task_entry(
                        task_title=f"Mixed-Thread-{thread_id}-Task-{i}",
                        priority_level=random.choice(list(TaskPriorityLevelEnumeration))
                    )
                
                elif op_type == 1:
                    # 创建记忆
                    storage.create_new_memory_entry(
                        content_text=f"Mixed memory from thread {thread_id}",
                        importance_score=random.randint(1, 5)
                    )
                
                elif op_type == 2:
                    # 列出待处理任务
                    _ = storage.retrieve_pending_tasks_sorted_by_priority()
                
                elif op_type == 3:
                    # 获取系统统计
                    _ = storage.generate_system_statistics_snapshot()
                
                else:
                    # 搜索记忆
                    _ = storage.search_memories_by_text_content("thread")
        
        except Exception as e:
            errors.append(f"Thread {thread_id} error: {str(e)}")
    
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        t = threading.Thread(target=mixed_operations, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    end_time = time.time()
    
    final_stats = storage.generate_system_statistics_snapshot()
    
    print(f"\n=== Mixed Workload Thread Safety Test ===")
    print(f"Threads: {num_threads}")
    print(f"Operations per thread: {operations_per_thread}")
    print(f"Total operations: {num_threads * operations_per_thread}")
    print(f"Final tasks: {final_stats.total_tasks_count}")
    print(f"Final memories: {final_stats.total_memories_count}")
    print(f"Errors: {len(errors)}")
    print(f"Duration: {end_time - start_time:.2f}s")
    
    if errors:
        print("Errors encountered:")
        for err in errors[:10]:
            print(f"  - {err}")
    
    return len(errors) == 0


def run_all_tests():
    """运行所有线程安全测试"""
    print("=" * 60)
    print("IN-MEMORY STORAGE BACKEND - THREAD SAFETY TEST SUITE")
    print("=" * 60)
    
    results = {}
    
    # 多次运行以增加发现竞态条件的机会
    for attempt in range(3):
        print(f"\n{'=' * 60}")
        print(f"TEST RUN {attempt + 1}/3")
        print('=' * 60)
        
        try:
            results[f"task_creation_{attempt}"] = test_thread_safety_task_creation()
        except Exception as e:
            print(f"Task creation test failed with exception: {e}")
            results[f"task_creation_{attempt}"] = False
        
        try:
            results[f"concurrent_updates_{attempt}"] = test_thread_safety_concurrent_updates()
        except Exception as e:
            print(f"Concurrent updates test failed with exception: {e}")
            results[f"concurrent_updates_{attempt}"] = False
        
        try:
            results[f"memory_ops_{attempt}"] = test_thread_safety_memory_operations()
        except Exception as e:
            print(f"Memory operations test failed with exception: {e}")
            results[f"memory_ops_{attempt}"] = False
        
        try:
            results[f"knowledge_graph_{attempt}"] = test_thread_safety_knowledge_graph()
        except Exception as e:
            print(f"Knowledge graph test failed with exception: {e}")
            results[f"knowledge_graph_{attempt}"] = False
        
        try:
            results[f"mixed_workload_{attempt}"] = test_thread_safety_mixed_workload()
        except Exception as e:
            print(f"Mixed workload test failed with exception: {e}")
            results[f"mixed_workload_{attempt}"] = False
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return True
    else:
        print(f"\n✗ {total - passed} tests failed!")
        print("This confirms thread safety issues in InMemoryDataStorageBackend!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
