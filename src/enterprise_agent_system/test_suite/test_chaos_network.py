"""
超极端混沌网络测试 - 模拟真实分布式系统的混乱场景
包含：网络分区、资源耗尽、异常中断、级联失败、TOCTOU竞态等
"""

import sys
import time
import random
import threading
import gc
import uuid
import traceback
from collections import defaultdict
from threading import Barrier, Semaphore, Event
from typing import Dict, Any, List, Optional
import signal

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance
from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration
)

logger = get_logger_instance('chaos_network_test')


class ChaosScenario:
    """混沌场景基类"""

    def __init__(self, name: str, severity: int = 5):
        self.name = name
        self.severity = severity
        self.errors = []
        self.warnings = []

    def execute(self, backend, store, cache) -> bool:
        """执行混沌场景"""
        raise NotImplementedError


class ResourceExhaustionScenario(ChaosScenario):
    """资源耗尽场景"""

    def __init__(self):
        super().__init__("资源耗尽", severity=10)

    def execute(self, backend, store, cache) -> bool:
        """尝试耗尽系统资源"""
        errors = []
        logger.info(f"🔥 执行: {self.name}")

        try:
            # 尝试创建海量对象
            task_ids = []
            for i in range(10000):
                try:
                    task = backend.create_new_task_entry(f"Exhaustion Task {i}")
                    task_ids.append(task.unique_entity_id)
                except Exception as e:
                    errors.append(str(e))

            logger.info(f"   创建了 {len(task_ids)} 个任务")

            # 尝试填充缓存
            for i in range(10000):
                try:
                    cache.set(f"exhaust_key_{i}", f"value_{i}" * 100)
                except Exception as e:
                    errors.append(str(e))

            # 尝试填充存储
            for i in range(5000):
                try:
                    store.save_report({
                        'id': str(uuid.uuid4()),
                        'title': f"Report {i}",
                        'content': 'x' * 10000
                    })
                except Exception as e:
                    errors.append(str(e))

            # 尝试并发填充
            threads = []
            for i in range(50):
                def worker():
                    for j in range(200):
                        try:
                            backend.create_new_memory_entry(f"Mem {i}-{j}")
                        except:
                            pass

                t = threading.Thread(target=worker)
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            logger.info(f"   错误数: {len(errors)}")
            return len(errors) == 0

        except Exception as e:
            logger.error(f"   资源耗尽测试异常: {e}")
            return False


class ConcurrentModificationScenario(ChaosScenario):
    """并发修改场景 - TOCTOU竞态"""

    def __init__(self):
        super().__init__("并发修改(TOCTOU)", severity=8)

    def execute(self, backend, store, cache) -> bool:
        """测试并发修改的竞态条件"""
        logger.info(f"🔥 执行: {self.name}")

        # 创建测试数据
        task = backend.create_new_task_entry("TOCTOU Test Task")
        task_id = task.unique_entity_id

        errors = []
        barrier = Barrier(20)

        def worker(worker_id):
            try:
                barrier.wait()
                for _ in range(50):
                    # TOCTOU: Check-Then-Act
                    current = backend.retrieve_task_by_id(task_id)
                    if current:
                        # 模拟处理时间
                        time.sleep(random.uniform(0, 0.001))

                        # Act: 更新
                        backend.update_task_entry(
                            task_id,
                            progress_percentage_value=random.random()
                        )
            except Exception as e:
                errors.append(f"Worker {worker_id}: {str(e)}")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        logger.info(f"   TOCTOU竞态测试完成，错误: {len(errors)}")
        return len(errors) == 0


class CascadeFailureScenario(ChaosScenario):
    """级联失败场景"""

    def __init__(self):
        super().__init__("级联失败", severity=9)

    def execute(self, backend, store, cache) -> bool:
        """模拟一个组件失败如何级联到其他组件"""
        logger.info(f"🔥 执行: {self.name}")

        errors = []
        lock = threading.Lock()

        # 创建依赖链
        tasks = []
        for i in range(100):
            try:
                task = backend.create_new_task_entry(f"Cascade Task {i}")
                tasks.append(task.unique_entity_id)
            except Exception as e:
                with lock:
                    errors.append(str(e))

        # 并发操作
        barrier = Barrier(30)

        def task_worker(i):
            try:
                barrier.wait()
                for _ in range(100):
                    task_id = random.choice(tasks) if tasks else "invalid"
                    backend.update_task_entry(task_id, progress_percentage_value=0.5)
            except Exception as e:
                with lock:
                    errors.append(f"TaskWorker {i}: {str(e)}")

        def memory_worker(i):
            try:
                barrier.wait()
                for _ in range(100):
                    backend.create_new_memory_entry(f"Cascade Memory {i}-{_}")
            except Exception as e:
                with lock:
                    errors.append(f"MemoryWorker {i}: {str(e)}")

        def cache_worker(i):
            try:
                barrier.wait()
                for _ in range(100):
                    cache.set(f"cache_{i}_{_}", f"value_{_}")
            except Exception as e:
                with lock:
                    errors.append(f"CacheWorker {i}: {str(e)}")

        threads = []
        threads.extend([threading.Thread(target=task_worker, args=(i,)) for i in range(10)])
        threads.extend([threading.Thread(target=memory_worker, args=(i,)) for i in range(10)])
        threads.extend([threading.Thread(target=cache_worker, args=(i,)) for i in range(10)])

        random.shuffle(threads)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        logger.info(f"   级联失败测试完成，错误: {len(errors)}")
        return len(errors) == 0


class SignalInterruptionScenario(ChaosScenario):
    """信号中断场景"""

    def __init__(self):
        super().__init__("信号中断", severity=7)

    def execute(self, backend, store, cache) -> bool:
        """模拟信号中断"""
        logger.info(f"🔥 执行: {self.name}")

        errors = []
        stop_flag = Event()
        interrupted_count = 0

        def worker():
            nonlocal interrupted_count
            try:
                for i in range(1000):
                    if stop_flag.is_set():
                        break
                    try:
                        backend.create_new_task_entry(f"Signal Task {i}")
                    except Exception as e:
                        errors.append(str(e))
            except KeyboardInterrupt:
                interrupted_count += 1
            except Exception as e:
                errors.append(str(e))

        # 启动工作线程
        thread = threading.Thread(target=worker)
        thread.start()

        # 模拟中断
        time.sleep(0.1)
        stop_flag.set()
        thread.join(timeout=1)

        if thread.is_alive():
            logger.warning(f"   线程未正常停止")

        logger.info(f"   信号中断测试完成，中断次数: {interrupted_count}, 错误: {len(errors)}")
        return len(errors) == 0


class TransactionRollbackScenario(ChaosScenario):
    """事务回滚场景"""

    def __init__(self):
        super().__init__("事务回滚", severity=6)

    def execute(self, backend, store, cache) -> bool:
        """测试操作失败时的回滚"""
        logger.info(f"🔥 执行: {self.name}")

        errors = []
        task_id = None

        try:
            # 创建一个任务
            task = backend.create_new_task_entry("Transaction Test")
            task_id = task.unique_entity_id
            initial_count = len(backend.retrieve_all_tasks())

            # 模拟失败的操作序列
            def failing_worker():
                try:
                    # 创建一些成功的任务
                    for i in range(10):
                        backend.create_new_task_entry(f"Success {i}")

                    # 尝试更新不存在的任务（会失败）
                    try:
                        backend.update_task_entry("nonexistent_id_12345", progress_percentage_value=0.5)
                    except:
                        pass  # 预期会失败

                    # 创建更多任务
                    for i in range(10):
                        backend.create_new_task_entry(f"More Success {i}")

                except Exception as e:
                    errors.append(str(e))

            # 并发执行多个工作
            threads = [threading.Thread(target=failing_worker) for _ in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # 验证数据一致性
            final_count = len(backend.retrieve_all_tasks())

            # 应该有更多的任务（成功创建了 20*5=100 个新任务）
            if final_count <= initial_count:
                errors.append("任务数量没有增加，数据可能丢失")

            logger.info(f"   事务回滚测试完成，最终任务数: {final_count}, 错误: {len(errors)}")
            return len(errors) == 0

        except Exception as e:
            logger.error(f"   事务回滚测试异常: {e}")
            return False


class DataCorruptionScenario(ChaosScenario):
    """数据损坏场景"""

    def __init__(self):
        super().__init__("数据损坏", severity=10)

    def execute(self, backend, store, cache) -> bool:
        """测试数据损坏检测和恢复"""
        logger.info(f"🔥 执行: {self.name}")

        errors = []

        # 创建一些正常数据
        tasks = []
        for i in range(50):
            try:
                task = backend.create_new_task_entry(f"Normal Task {i}")
                tasks.append(task)
            except Exception as e:
                errors.append(str(e))

        # 验证数据完整性
        for task in tasks:
            try:
                retrieved = backend.retrieve_task_by_id(task.unique_entity_id)
                if not retrieved:
                    errors.append(f"任务 {task.unique_entity_id} 无法检索")

                # 验证枚举值
                if not isinstance(retrieved.execution_status, TaskExecutionStatusEnumeration):
                    errors.append(f"任务状态类型错误: {type(retrieved.execution_status)}")

                if not isinstance(retrieved.priority_level, TaskPriorityLevelEnumeration):
                    errors.append(f"任务优先级类型错误: {type(retrieved.priority_level)}")

            except Exception as e:
                errors.append(str(e))

        # 验证边界数据
        try:
            # 创建带有极端值的任务
            extreme_task = backend.create_new_task_entry(
                task_title="Extreme" * 1000,  # 超长标题
                task_description="Description" * 1000,
                priority_level="high"  # 字符串，应该被转换
            )

            retrieved = backend.retrieve_task_by_id(extreme_task.unique_entity_id)
            if not retrieved:
                errors.append("极端任务无法检索")

            # 验证类型转换
            if not isinstance(retrieved.priority_level, TaskPriorityLevelEnumeration):
                errors.append("极端任务的优先级类型未正确转换")

        except Exception as e:
            errors.append(f"极端任务测试: {str(e)}")

        logger.info(f"   数据损坏测试完成，错误: {len(errors)}")
        return len(errors) == 0


class MemoryLeakScenario(ChaosScenario):
    """内存泄漏场景"""

    def __init__(self):
        super().__init__("内存泄漏", severity=8)

    def execute(self, backend, store, cache) -> bool:
        """测试内存泄漏"""
        logger.info(f"🔥 执行: {self.name}")

        try:
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss / (1024 * 1024)
        except:
            initial_memory = 0

        # 创建大量对象
        for i in range(10000):
            backend.create_new_task_entry(f"Memory Test {i}")

        # 强制GC
        gc.collect()

        # 再次检查内存
        try:
            import psutil
            process = psutil.Process()
            final_memory = process.memory_info().rss / (1024 * 1024)
            memory_growth = final_memory - initial_memory

            logger.info(f"   内存变化: {memory_growth:+.1f}MB")

            if memory_growth > 100:
                logger.warning(f"   可能存在内存泄漏！增长超过 100MB")
                return False

        except:
            pass

        return True


class DeepChaosOrchestrator:
    """深度混沌编排器"""

    def __init__(self):
        self.backend = InMemoryDataStorageBackend()
        self.store = SimpleMemoryStore()
        self.cache = SimpleCache()

        self.scenarios = [
            ResourceExhaustionScenario(),
            ConcurrentModificationScenario(),
            CascadeFailureScenario(),
            SignalInterruptionScenario(),
            TransactionRollbackScenario(),
            DataCorruptionScenario(),
            MemoryLeakScenario(),
        ]

        self.results = {}
        self.lock = threading.Lock()

    def run_scenario(self, scenario: ChaosScenario, iterations: int = 3):
        """运行单个场景多次"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🧪 场景: {scenario.name} (严重度: {scenario.severity})")
        logger.info(f"{'='*80}")

        successes = 0
        failures = 0

        for i in range(iterations):
            logger.info(f"   迭代 {i+1}/{iterations}...")

            try:
                result = scenario.execute(self.backend, self.store, self.cache)

                if result:
                    successes += 1
                    logger.info(f"   ✅ 迭代 {i+1} 通过")
                else:
                    failures += 1
                    logger.warning(f"   ⚠️  迭代 {i+1} 失败")

            except Exception as e:
                failures += 1
                logger.error(f"   ❌ 迭代 {i+1} 异常: {e}")
                logger.error(traceback.format_exc()[:300])

            # 清理
            time.sleep(0.1)

        with self.lock:
            self.results[scenario.name] = {
                'successes': successes,
                'failures': failures,
                'severity': scenario.severity
            }

        return failures == 0

    def run_all(self):
        """运行所有混沌场景"""
        logger.info(f"\n{'='*80}")
        logger.info("🚀 深度混沌网络测试 - 开始")
        logger.info(f"{'='*80}")

        start_time = time.time()

        # 按严重度排序（先运行最严重的）
        sorted_scenarios = sorted(self.scenarios, key=lambda s: -s.severity)

        for scenario in sorted_scenarios:
            self.run_scenario(scenario, iterations=3)
            time.sleep(0.5)

        # 生成报告
        duration = time.time() - start_time

        logger.info(f"\n{'='*80}")
        logger.info("📊 深度混沌测试 - 最终报告")
        logger.info(f"{'='*80}")

        logger.info(f"\n⏱️  总耗时: {duration:.1f}秒 ({duration/60:.1f}分钟)")

        logger.info(f"\n📈 场景结果:")
        total_success = 0
        total_failures = 0

        for name, result in sorted(self.results.items(), key=lambda x: -x[1]['severity']):
            success = result['successes']
            fail = result['failures']
            severity = result['severity']

            total_success += success
            total_failures += fail

            status = "✅" if fail == 0 else "⚠️" if fail < success else "❌"
            logger.info(f"  {status} {name} (严重度 {severity}): "
                       f"{success} 通过, {fail} 失败")

        logger.info(f"\n📊 总计:")
        logger.info(f"  总测试: {total_success + total_failures}")
        logger.info(f"  通过: {total_success}")
        logger.info(f"  失败: {total_failures}")

        all_passed = total_failures == 0

        if all_passed:
            logger.info(f"\n🎉🎉🎉 所有混沌场景通过！系统极其健壮！")
        else:
            logger.error(f"\n❌ 发现 {total_failures} 个失败，需要进一步调查")

        return all_passed


def main():
    """主函数"""
    orchestrator = DeepChaosOrchestrator()
    success = orchestrator.run_all()

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
