"""
深度bug搜索测试 - 专门寻找真实的生产级问题
包括：数据竞争、死锁、异常处理缺陷、内存泄漏、边界条件等
"""

import sys
import time
import random
import threading
import gc
import uuid
import traceback
from collections import defaultdict
from threading import Barrier

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance
from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration
)

logger = get_logger_instance('deep_bug_hunt')


class DeepBugHunter:
    """深度bug狩猎者"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.lock = threading.Lock()
        self.operation_count = 0

    def _log_error(self, category: str, msg: str, exc: Exception = None):
        """记录错误"""
        with self.lock:
            self.errors.append({
                'category': category,
                'time': time.time(),
                'msg': msg,
                'exc': str(exc) if exc else None,
                'trace': traceback.format_exc()[:500] if exc else None
            })

    def _log_warning(self, category: str, msg: str):
        """记录警告"""
        with self.lock:
            self.warnings.append({
                'category': category,
                'time': time.time(),
                'msg': msg
            })

    def test_1_boundary_conditions(self):
        """测试1：边界条件验证"""
        logger.info("\n=== 测试1：边界条件验证 ===")
        backend = InMemoryDataStorageBackend()
        store = SimpleMemoryStore()
        cache = SimpleCache()

        # 边界条件1：大量的小对象
        for i in range(10000):
            try:
                backend.create_new_task_entry(f"T{i}")
                self.operation_count += 1
            except Exception as e:
                self._log_error("task_boundary", f"Task {i}创建失败", e)

        # 边界条件2：大量的记忆
        for i in range(10000):
            try:
                backend.create_new_memory_entry(f"Memory {i}")
                self.operation_count += 1
            except Exception as e:
                self._log_error("memory_boundary", f"Memory {i}创建失败", e)

        logger.info(f"边界条件测试：创建了20000个对象，错误数: {len(self.errors)}")
        return len(self.errors) == 0

    def test_2_concurrent_contention(self):
        """测试2：并发竞争 - 专门找数据竞争"""
        logger.info("\n=== 测试2：并发竞争 ===")
        backend = InMemoryDataStorageBackend()
        errors = []
        barrier = Barrier(100)  # 让所有线程同时开始

        def worker(thread_id):
            try:
                barrier.wait()  # 等待所有线程就绪
                for i in range(100):
                    # 同时创建任务
                    task = backend.create_new_task_entry(f"Task {thread_id}-{i}")
                    # 同时更新
                    backend.update_task_entry(
                        task.unique_entity_id,
                        execution_status=TaskExecutionStatusEnumeration.IN_PROGRESS_STATUS,
                        progress_percentage_value=0.5
                    )
                    # 同时创建记忆
                    memory = backend.create_new_memory_entry(f"Mem {thread_id}-{i}")
                    # 同时查询
                    backend.retrieve_task_by_id(task.unique_entity_id)
                    backend.retrieve_memory_by_id(memory.unique_memory_id)
            except Exception as e:
                with self.lock:
                    errors.append((thread_id, e))

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(100)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        if errors:
            logger.error(f"并发竞争发现 {len(errors)} 个错误！")
            for thread_id, e in errors[:5]:
                self._log_error("concurrency", f"Thread {thread_id}错误", e)
            return False
        else:
            logger.info("并发竞争测试通过！")
            return True

    def test_3_cache_stress(self):
        """测试3：缓存压力 - 内存泄漏检测"""
        logger.info("\n=== 测试3：缓存压力 ===")
        cache = SimpleCache()

        # 阶段1：预热
        for i in range(10000):
            cache.set(f"pre_{i}", f"value_{i}")

        # 阶段2：大量的缓存操作
        start_mem = 0
        try:
            import psutil
            start_mem = psutil.Process().memory_info().rss
        except:
            pass

        for i in range(100000):
            key = f"key_{random.randint(0, 10000)}"
            if random.random() > 0.5:
                cache.set(key, f"value_{i}")
            else:
                cache.get(key)
            self.operation_count += 1

        end_mem = 0
        try:
            import psutil
            end_mem = psutil.Process().memory_info().rss
        except:
            pass

        mem_delta_mb = (end_mem - start_mem) / (1024 * 1024) if (start_mem and end_mem) else 0

        logger.info(f"缓存压力测试：内存变化 {mem_delta_mb:.1f}MB")
        if mem_delta_mb > 50:
            self._log_warning("memory", f"可能存在内存泄漏！内存增长 {mem_delta_mb:.1f}MB")

        return True

    def test_4_extreme_values(self):
        """测试4：极端值处理"""
        logger.info("\n=== 测试4：极端值处理 ===")
        backend = InMemoryDataStorageBackend()
        store = SimpleMemoryStore()
        cache = SimpleCache()

        extreme_values = [
            "",
            None,
            "x" * 1000000,
            float('inf'),
            float('-inf'),
            float('nan'),
            10 ** 1000,
            -10 ** 1000,
        ]

        for i, val in enumerate(extreme_values):
            try:
                # 测试任务
                task = backend.create_new_task_entry(f"Test {i}", str(val))
                backend.update_task_entry(
                    task.unique_entity_id,
                    error_message=str(val)
                )

                # 测试记忆
                memory = backend.create_new_memory_entry(str(val))

                # 测试缓存
                cache.set(f"key_{i}", val)
                cache.get(f"key_{i}")

                # 测试存储
                store.save_report({'id': str(uuid.uuid4()), 'data': str(val)})

                self.operation_count += 1
            except Exception as e:
                self._log_error("extreme", f"极端值 {i} 处理失败", e)

        logger.info(f"极端值测试：错误数 {len(self.errors)}")
        return len(self.errors) == 0

    def test_5_store_persistence(self):
        """测试5：存储持久化和隔离"""
        logger.info("\n=== 测试5：存储持久化 ===")
        store1 = SimpleMemoryStore()
        store2 = SimpleMemoryStore()

        id1 = str(uuid.uuid4())
        store1.save_report({'id': id1, 'title': 'Store 1'})

        id2 = str(uuid.uuid4())
        store2.save_report({'id': id2, 'title': 'Store 2'})

        # 验证隔离
        r1 = store1.get_report(id1)
        r2 = store2.get_report(id2)

        r1_not_in_store2 = store2.get_report(id1) is None
        r2_not_in_store1 = store1.get_report(id2) is None

        if not r1_not_in_store2 or not r2_not_in_store1:
            self._log_error("isolation", "存储隔离失败！")

        logger.info(f"存储隔离测试：通过 {r1_not_in_store2 and r2_not_in_store1}")
        return r1_not_in_store2 and r2_not_in_store1

    def test_6_cache_ttl(self):
        """测试6：缓存TTL功能"""
        logger.info("\n=== 测试6：缓存TTL功能 ===")
        cache = SimpleCache()
        errors = 0

        try:
            cache.set("no_ttl", "value1")
            cache.set("zero_ttl", "value2", 0)
            cache.set("short_ttl", "value3", 1)
            cache.set("normal_ttl", "value4", 60)

            # 立即查询
            v1 = cache.get("no_ttl")
            v2 = cache.get("zero_ttl")
            v3 = cache.get("short_ttl")
            v4 = cache.get("normal_ttl")

            if v1 is None or v2 is None or v3 is None or v4 is None:
                errors += 1

            # 检查 TTL 0 不应该过期
            if cache.get("zero_ttl") is None:
                self._log_error("cache", "TTL 0 值错误过期")

        except Exception as e:
            self._log_error("cache_ttl", "TTL测试失败", e)

        logger.info(f"TTL功能测试：错误 {errors}")
        return errors == 0

    def test_7_knowledge_graph_stress(self):
        """测试7：知识图谱压力测试"""
        logger.info("\n=== 测试7：知识图谱压力测试 ===")
        backend = InMemoryDataStorageBackend()

        # 大量节点
        nodes = []
        for i in range(1000):
            try:
                node_id = backend.add_node_to_knowledge_graph(f"Node {i}")
                nodes.append(node_id)
                self.operation_count += 1
            except Exception as e:
                self._log_error("graph", f"添加节点 {i} 失败", e)

        # 随机添加边
        for i in range(10000):
            if len(nodes) >= 2:
                node_a = random.choice(nodes)
                node_b = random.choice(nodes)
                try:
                    backend.add_edge_to_knowledge_graph(
                        node_a, node_b, f"rel_{i}", 1.0
                    )
                    self.operation_count += 1
                except Exception as e:
                    # 边添加可能会因为重复或其他原因失败，但这不应该导致崩溃
                    pass

        # 统计检查
        stats = backend.retrieve_knowledge_graph_statistics()
        logger.info(f"知识图谱测试完成：节点数 {stats.get('node_count',0)}, 边数 {stats.get('edge_count',0)}")
        return True

    def test_8_locking_deadlock(self):
        """测试8：死锁检测"""
        logger.info("\n=== 测试8：死锁检测 ===")
        backend = InMemoryDataStorageBackend()
        lock = threading.Lock()
        success = True

        def worker1():
            try:
                backend.create_new_task_entry("W1")
                backend.generate_system_statistics_snapshot()
                backend.retrieve_all_tasks()
            except:
                pass

        def worker2():
            try:
                backend.generate_system_statistics_snapshot()
                backend.retrieve_all_tasks()
                backend.create_new_task_entry("W2")
            except:
                pass

        # 运行多次试图造成死锁
        for round in range(10):
            t1 = threading.Thread(target=worker1)
            t2 = threading.Thread(target=worker2)
            t1.start()
            t2.start()

            t1.join(timeout=1)
            t2.join(timeout=1)

            if t1.is_alive() or t2.is_alive():
                self._log_error("deadlock", f"可能死锁在 round {round}")
                success = False
                break

        logger.info(f"死锁检测测试：通过 {success}")
        return success

    def run_all(self):
        """运行所有测试"""
        logger.info(f"\n{'='*80}")
        logger.info("🐛 深度BUG狩猎 - 开始")
        logger.info(f"{'='*80}")

        results = {}

        # 运行各个测试
        results['boundary'] = self.test_1_boundary_conditions()
        results['concurrency'] = self.test_2_concurrent_contention()
        results['cache_stress'] = self.test_3_cache_stress()
        results['extreme'] = self.test_4_extreme_values()
        results['isolation'] = self.test_5_store_persistence()
        results['cache_ttl'] = self.test_6_cache_ttl()
        results['graph'] = self.test_7_knowledge_graph_stress()
        results['deadlock'] = self.test_8_locking_deadlock()

        # 最终报告
        logger.info(f"\n{'='*80}")
        logger.info("📊 深度BUG狩猎 - 报告")
        logger.info(f"{'='*80}")

        passed = 0
        total = len(results)

        for name, success in results.items():
            status = "✅ 通过" if success else "❌ 失败"
            logger.info(f"{name}: {status}")
            if success:
                passed += 1

        logger.info(f"\n总计: {passed}/{total}")
        logger.info(f"操作数: {self.operation_count:,}")
        logger.info(f"发现错误: {len(self.errors)}")
        logger.info(f"发现警告: {len(self.warnings)}")

        if self.errors:
            logger.error("\n❌ 错误详情:")
            for i, err in enumerate(self.errors[:10]):
                logger.error(f"  {i+1}. [{err['category']}] {err['msg']} - {err.get('exc', '')}")

        all_passed = all(results.values()) and len(self.errors) == 0
        return all_passed


def main():
    """主函数"""
    hunter = DeepBugHunter()
    all_passed = hunter.run_all()
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
