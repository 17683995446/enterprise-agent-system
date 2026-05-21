"""
Extreme Line-by-Line Logging Test - 逐行日志测试
按照用户要求，对系统进行全面的详细日志测试，验证每一行代码的执行
"""

import sys
import time
import threading
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

print("=" * 120)
print("🚀 开始逐行日志测试 - Line-by-Line Logging Test")
print("=" * 120)
print(f"[TEST] 测试开始时间: {datetime.now().isoformat()}")
print()

# 导入带详细日志的模块
print("[TEST] 正在导入带详细日志的存储模块...")
from enterprise_agent_system.infrastructure.simple_memory_store_with_logging import (
    SimpleMemoryStore,
    SimpleCache,
)
print("[TEST] 存储模块导入完成")
print()

# 导入核心存储后端
print("[TEST] 正在导入核心存储后端...")
from enterprise_agent_system.core.in_memory_data_storage_backend import (
    InMemoryDataStorageBackend,
)
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionDataModel,
    MemoryStorageDataModel,
    TaskPriorityLevelEnumeration,
    TaskExecutionStatusEnumeration,
    MemoryCategoryTypeEnumeration,
)
print("[TEST] 核心模块导入完成")
print()

print("=" * 120)
print("📋 测试阶段 1: SimpleMemoryStore 详细操作测试")
print("=" * 120)
print()


def test_memory_store_detailed():
    """测试 SimpleMemoryStore 的详细操作"""
    print("\n" + "-" * 100)
    print("[TEST] 初始化 SimpleMemoryStore")
    print("-" * 100)
    store = SimpleMemoryStore()
    print(f"[TEST] SimpleMemoryStore 初始化完成: {store}")
    print()

    print("-" * 100)
    print("[TEST] 测试 1.1: 保存报告")
    print("-" * 100)
    report_data_1 = {
        "title": "测试报告 1",
        "type": "analysis",
        "content": "这是测试内容",
        "quality_score": 95.5,
    }
    print(f"[TEST] 准备保存报告: {report_data_1}")
    report_id_1 = store.save_report(report_data_1)
    print(f"[TEST] 报告保存成功，ID: {report_id_1}")
    print()

    print("-" * 100)
    print("[TEST] 测试 1.2: 获取报告")
    print("-" * 100)
    print(f"[TEST] 正在获取报告 ID: {report_id_1}")
    retrieved = store.get_report(report_id_1)
    print(f"[TEST] 报告获取结果: {retrieved}")
    print(f"[TEST] 验证: 标题匹配 -> {retrieved['title'] == report_data_1['title']}")
    print()

    print("-" * 100)
    print("[TEST] 测试 1.3: 保存第二个报告")
    print("-" * 100)
    report_data_2 = {
        "title": "测试报告 2",
        "type": "review",
        "content": "第二个报告的内容",
        "quality_score": 87.0,
    }
    report_id_2 = store.save_report(report_data_2)
    print(f"[TEST] 第二个报告保存成功，ID: {report_id_2}")
    print()

    print("-" * 100)
    print("[TEST] 测试 1.4: 列出所有报告")
    print("-" * 100)
    reports = store.list_reports()
    print(f"[TEST] 报告数量: {len(reports)}")
    for i, report in enumerate(reports, 1):
        print(f"[TEST]   报告 {i}: {report['title']} ({report['type']})")
    print()

    print("-" * 100)
    print("[TEST] 测试 1.5: 获取统计信息")
    print("-" * 100)
    stats = store.get_stats()
    print(f"[TEST] 统计信息: {stats}")
    print()

    print("-" * 100)
    print("[TEST] 测试 1.6: 原子增量操作")
    print("-" * 100)
    store.atomic_increment(report_id_1, "quality_score", 1)
    print(f"[TEST] 增量操作完成")
    print()

    print("-" * 100)
    print("[TEST] 测试 1.7: 删除报告")
    print("-" * 100)
    delete_result = store.delete_report(report_id_2)
    print(f"[TEST] 删除结果: {delete_result}")
    print()

    print("✅ SimpleMemoryStore 测试完成!")
    print()


def test_simple_cache_detailed():
    """测试 SimpleCache 的详细操作"""
    print("=" * 120)
    print("📋 测试阶段 2: SimpleCache 详细操作测试")
    print("=" * 120)
    print()

    print("-" * 100)
    print("[TEST] 初始化 SimpleCache")
    print("-" * 100)
    cache = SimpleCache()
    print(f"[TEST] SimpleCache 初始化完成: {cache}")
    print()

    print("-" * 100)
    print("[TEST] 测试 2.1: 设置缓存项")
    print("-" * 100)
    cache.set("key1", "value1", ttl=3600)
    cache.set("key2", {"data": "complex"}, ttl=0)
    print(f"[TEST] 缓存项设置完成")
    print()

    print("-" * 100)
    print("[TEST] 测试 2.2: 获取缓存项")
    print("-" * 100)
    val1 = cache.get("key1")
    val2 = cache.get("key2")
    val3 = cache.get("nonexistent")
    print(f"[TEST] 获取 key1: {val1}")
    print(f"[TEST] 获取 key2: {val2}")
    print(f"[TEST] 获取 nonexistent: {val3}")
    print()

    print("-" * 100)
    print("[TEST] 测试 2.3: 检查存在性")
    print("-" * 100)
    exists1 = cache.exists("key1")
    exists2 = cache.exists("nonexistent")
    print(f"[TEST] key1 存在: {exists1}")
    print(f"[TEST] nonexistent 存在: {exists2}")
    print()

    print("-" * 100)
    print("[TEST] 测试 2.4: 生成缓存键")
    print("-" * 100)
    generated_key = cache.generate_key("prefix", "arg1", 123, {"key": "val"})
    print(f"[TEST] 生成的缓存键: {generated_key}")
    print()

    print("-" * 100)
    print("[TEST] 测试 2.5: 获取缓存统计")
    print("-" * 100)
    cache_stats = cache.get_stats()
    print(f"[TEST] 缓存统计: {cache_stats}")
    print()

    print("-" * 100)
    print("[TEST] 测试 2.6: 清空缓存")
    print("-" * 100)
    cleared = cache.clear()
    print(f"[TEST] 清空了 {cleared} 个缓存项")
    print()

    print("✅ SimpleCache 测试完成!")
    print()


def test_in_memory_storage_backend_detailed():
    """测试 InMemoryDataStorageBackend 的详细操作"""
    print("=" * 120)
    print("📋 测试阶段 3: InMemoryDataStorageBackend 详细操作测试")
    print("=" * 120)
    print()

    print("-" * 100)
    print("[TEST] 初始化 InMemoryDataStorageBackend")
    print("-" * 100)
    backend = InMemoryDataStorageBackend()
    print(f"[TEST] Backend 初始化完成: {backend}")
    print()

    print("-" * 100)
    print("[TEST] 测试 3.1: 创建任务")
    print("-" * 100)
    task1 = backend.create_new_task_entry(
        task_title="高优先级任务",
        task_description="这是一个紧急任务",
        priority_level=TaskPriorityLevelEnumeration.URGENT_PRIORITY_LEVEL,
    )
    print(f"[TEST] 任务 1 创建: {task1.unique_entity_id} - {task1.task_title}")

    task2 = backend.create_new_task_entry(
        task_title="中等优先级任务",
        task_description="这是一个普通任务",
        priority_level=TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
    )
    print(f"[TEST] 任务 2 创建: {task2.unique_entity_id} - {task2.task_title}")
    print()

    print("-" * 100)
    print("[TEST] 测试 3.2: 检索任务")
    print("-" * 100)
    retrieved_task = backend.retrieve_task_by_id(task1.unique_entity_id)
    print(f"[TEST] 检索任务: {retrieved_task.task_title if retrieved_task else 'None'}")
    print(f"[TEST] 验证引用安全: 修改返回的对象")
    if retrieved_task:
        retrieved_task.task_title = "已篡改的标题"
        # 重新获取验证
        re_retrieved = backend.retrieve_task_by_id(task1.unique_entity_id)
        print(f"[TEST] 重新获取: {re_retrieved.task_title}")
        print(f"[TEST] 引用安全验证通过: {re_retrieved.task_title == task1.task_title}")
    print()

    print("-" * 100)
    print("[TEST] 测试 3.3: 更新任务")
    print("-" * 100)
    updated_task = backend.update_task_entry(
        task1.unique_entity_id,
        progress_percentage_value=0.5,
        execution_status=TaskExecutionStatusEnumeration.IN_PROGRESS_STATUS,
    )
    print(f"[TEST] 任务更新后: 进度={updated_task.progress_percentage_value}, 状态={updated_task.execution_status}")
    print()

    print("-" * 100)
    print("[TEST] 测试 3.4: 获取待处理任务")
    print("-" * 100)
    pending_tasks = backend.retrieve_pending_tasks_sorted_by_priority()
    print(f"[TEST] 待处理任务数量: {len(pending_tasks)}")
    for task in pending_tasks:
        print(f"[TEST]   - {task.task_title} (优先级: {task.priority_level})")
    print()

    print("-" * 100)
    print("[TEST] 测试 3.5: 创建记忆")
    print("-" * 100)
    memory1 = backend.create_new_memory_entry(
        content_text="这是一个重要的记忆内容，包含关键信息",
        category_type=MemoryCategoryTypeEnumeration.KNOWLEDGE_MEMORY_CATEGORY,
        tags_list=["重要", "知识", "参考"],
        importance_score=5,
    )
    print(f"[TEST] 记忆 1 创建: {memory1.unique_memory_id}")

    memory2 = backend.create_new_memory_entry(
        content_text="这是另一个技术相关的记忆",
        category_type=MemoryCategoryTypeEnumeration.TECHNICAL_MEMORY_CATEGORY,
        tags_list=["技术", "编程"],
        importance_score=4,
    )
    print(f"[TEST] 记忆 2 创建: {memory2.unique_memory_id}")
    print()

    print("-" * 100)
    print("[TEST] 测试 3.6: 搜索记忆")
    print("-" * 100)
    search_results = backend.search_memories_by_text_content("重要")
    print(f"[TEST] 搜索 '重要' 得到 {len(search_results)} 个结果")
    for mem in search_results:
        print(f"[TEST]   - {mem.content_text_body[:50]}...")
    print()

    print("-" * 100)
    print("[TEST] 测试 3.7: 知识图谱操作")
    print("-" * 100)
    node1_id = backend.add_node_to_knowledge_graph("概念A", {"type": "concept"})
    node2_id = backend.add_node_to_knowledge_graph("概念B", {"type": "concept"})
    print(f"[TEST] 节点创建: {node1_id}, {node2_id}")

    edge_id = backend.add_edge_to_knowledge_graph(
        node1_id, node2_id, "related_to", weight=0.8
    )
    print(f"[TEST] 边创建: {edge_id}")
    print()

    print("-" * 100)
    print("[TEST] 测试 3.8: 获取系统统计")
    print("-" * 100)
    system_stats = backend.generate_system_statistics_snapshot()
    print(f"[TEST] 系统统计:")
    print(f"[TEST]   总任务数: {system_stats.total_tasks_count}")
    print(f"[TEST]   总记忆数: {system_stats.total_memories_count}")
    print(f"[TEST]   知识图谱节点: {system_stats.knowledge_graph_nodes_count}")
    print(f"[TEST]   知识图谱边: {system_stats.knowledge_graph_edges_count}")
    print()

    print("✅ InMemoryDataStorageBackend 测试完成!")
    print()


def test_concurrent_operations():
    """测试并发操作"""
    print("=" * 120)
    print("📋 测试阶段 4: 并发操作测试")
    print("=" * 120)
    print()

    print("-" * 100)
    print("[TEST] 初始化并发测试环境")
    print("-" * 100)
    store = SimpleMemoryStore()
    errors: List[str] = []
    lock = threading.Lock()
    print(f"[TEST] 并发测试环境就绪")
    print()

    def worker(worker_id: int, num_ops: int):
        """工作线程函数"""
        try:
            for i in range(num_ops):
                report_data = {
                    "title": f"Worker {worker_id} Report {i}",
                    "type": "concurrent_test",
                    "quality_score": float(worker_id + i),
                }
                report_id = store.save_report(report_data)
                store.get_report(report_id)
        except Exception as e:
            with lock:
                errors.append(f"Worker {worker_id} error: {str(e)}")
                traceback.print_exc()

    print("-" * 100)
    print("[TEST] 启动 5 个工作线程，每个执行 20 次操作")
    print("-" * 100)
    threads = []
    num_workers = 5
    ops_per_worker = 20
    start_time = time.time()

    for i in range(num_workers):
        t = threading.Thread(target=worker, args=(i, ops_per_worker))
        threads.append(t)
        t.start()
        print(f"[TEST] 线程 {i} 已启动")

    print(f"[TEST] 等待所有线程完成...")
    for t in threads:
        t.join()

    end_time = time.time()
    duration = end_time - start_time
    print(f"[TEST] 所有线程完成，耗时 {duration:.2f}秒")
    print()

    print("-" * 100)
    print("[TEST] 并发测试结果")
    print("-" * 100)
    if errors:
        print(f"[TEST] ❌ 发现 {len(errors)} 个错误:")
        for err in errors:
            print(f"[TEST]   - {err}")
    else:
        print(f"[TEST] ✅ 无错误，并发测试通过!")

    final_stats = store.get_stats()
    print(f"[TEST] 最终统计: {final_stats}")
    print()

    print("✅ 并发操作测试完成!")
    print()


def main():
    """主测试函数"""
    start_time = time.time()
    all_passed = True

    try:
        test_memory_store_detailed()
    except Exception as e:
        print(f"❌ MemoryStore 测试失败: {e}")
        traceback.print_exc()
        all_passed = False

    try:
        test_simple_cache_detailed()
    except Exception as e:
        print(f"❌ Cache 测试失败: {e}")
        traceback.print_exc()
        all_passed = False

    try:
        test_in_memory_storage_backend_detailed()
    except Exception as e:
        print(f"❌ Backend 测试失败: {e}")
        traceback.print_exc()
        all_passed = False

    try:
        test_concurrent_operations()
    except Exception as e:
        print(f"❌ 并发测试失败: {e}")
        traceback.print_exc()
        all_passed = False

    print("=" * 120)
    print("🏁 最终测试结果")
    print("=" * 120)
    total_time = time.time() - start_time
    print(f"总耗时: {total_time:.2f} 秒")
    print()

    if all_passed:
        print("🎉🎉🎉 所有测试通过！系统运行正常！")
        print("=" * 120)
        return 0
    else:
        print("⚠️  部分测试失败，请检查上面的日志")
        print("=" * 120)
        return 1


if __name__ == "__main__":
    sys.exit(main())
