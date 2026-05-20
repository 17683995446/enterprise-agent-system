"""
极端长期生产级测试 - 模拟真实环境连续运行
包含多模块协作、资源泄漏检测、压力测试等多种场景
"""

import sys
import time
import random
import threading
import gc
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('extreme_long_term_test')


@dataclass
class TestPhase:
    """测试阶段"""
    name: str
    duration_seconds: int
    description: str
    workload: Dict[str, float]  # 各操作类型的权重


@dataclass
class ResourceSnapshot:
    """资源快照"""
    timestamp: float
    memory_mb: float
    gc_collections: int
    active_threads: int
    object_count: int
    storage_size: int


class ExtremeLongTermTester:
    """极端长期生产级测试器"""

    TEST_PHASES = [
        TestPhase(
            name="初始化预热",
            duration_seconds=60,
            description="初始化所有组件，预热缓存",
            workload={"memory": 0.4, "task": 0.4, "cache": 0.2}
        ),
        TestPhase(
            name="基础负载",
            duration_seconds=120,
            description="基础稳定负载，模拟正常使用",
            workload={"memory": 0.3, "task": 0.3, "cache": 0.2, "graph": 0.2}
        ),
        TestPhase(
            name="高并发压力",
            duration_seconds=180,
            description="200+线程并发，极端压力",
            workload={"memory": 0.25, "task": 0.25, "cache": 0.25, "graph": 0.25}
        ),
        TestPhase(
            name="混合操作",
            duration_seconds=240,
            description="混合读写删除查询，真实场景",
            workload={"memory": 0.2, "task": 0.2, "cache": 0.2, "graph": 0.2, "analytics": 0.2}
        ),
        TestPhase(
            name="内存极限测试",
            duration_seconds=180,
            description="大量数据写入，测试内存管理",
            workload={"memory": 0.6, "task": 0.2, "cache": 0.2}
        ),
        TestPhase(
            name="稳定性验证",
            duration_seconds=120,
            description="低负载验证系统稳定性",
            workload={"memory": 0.3, "task": 0.3, "cache": 0.2, "graph": 0.2}
        )
    ]

    def __init__(self):
        self.phases = self.TEST_PHASES
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self.errors = []
        self.warnings = []
        self.phase_results = []
        self.resource_snapshots = []
        self.metrics = defaultdict(int)
        self.component_stats = defaultdict(lambda: {
            'operations': 0, 'success': 0, 'failures': 0
        })

        # 组件初始化
        self.store = None
        self.cache = None
        self.storage_backend = None

    def _init_components(self):
        """初始化所有组件"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
        from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend

        self.store = SimpleMemoryStore()
        self.cache = SimpleCache()
        self.storage_backend = InMemoryDataStorageBackend()
        logger.info("✅ 所有组件初始化完成")

    def _take_resource_snapshot(self, phase_name: str):
        """获取资源快照"""
        snapshot = ResourceSnapshot(
            timestamp=time.time(),
            memory_mb=0.0,
            gc_collections=0,
            active_threads=threading.active_count(),
            object_count=len(gc.get_objects()),
            storage_size=0
        )

        # 内存统计
        try:
            import psutil
            snapshot.memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)
        except:
            pass

        # GC统计
        gc_stats = gc.get_stats()
        snapshot.gc_collections = sum(s['collections'] for s in gc_stats)

        # 存储大小
        if self.store:
            stats = self.store.get_stats()
            snapshot.storage_size = stats.get('total_reports', 0)

        with self.lock:
            self.resource_snapshots.append((phase_name, snapshot))

        return snapshot

    def _memory_operation(self, thread_id: int, iteration: int):
        """执行记忆存储操作"""
        try:
            op_type = random.choice(['create', 'read', 'update', 'search'])

            if op_type == 'create':
                content = f"记忆内容 #{thread_id}-{iteration} - {random.randbytes(100).hex()}"
                memory = self.storage_backend.create_new_memory_entry(
                    content_text=content,
                    category_type=random.choice(list(MemoryCategoryTypeEnumeration)),
                    tags_list=[f"tag_{random.randint(1, 20)}" for _ in range(random.randint(1, 5))],
                    importance_score=random.randint(1, 5)
                )
                self.metrics['memory_created'] += 1

            elif op_type == 'read':
                memories = self.storage_backend.retrieve_all_memories()
                if memories:
                    mem = random.choice(memories)
                    self.storage_backend.retrieve_memory_by_id(mem.unique_memory_id)
                self.metrics['memory_read'] += 1

            elif op_type == 'update':
                memories = self.storage_backend.retrieve_all_memories()
                if memories:
                    mem = random.choice(memories)
                    # 通过任务创建API来模拟更新
                    self.store.save_report({
                        "id": mem.unique_memory_id,
                        "title": f"Updated Memory #{thread_id}",
                        "type": "memory",
                        "content": f"Updated content at {datetime.now()}",
                        "quality_score": random.uniform(0, 10)
                    })
                self.metrics['memory_updated'] += 1

            else:  # search
                results = self.storage_backend.search_memories_by_text_content(
                    search_query="记忆" if random.random() < 0.5 else "test",
                    min_importance=random.randint(1, 3)
                )
                self.metrics['memory_searched'] += 1

            self.component_stats['memory']['success'] += 1
        except Exception as e:
            self.component_stats['memory']['failures'] += 1
            with self.lock:
                self.errors.append(f"[Memory] Thread {thread_id}, Iter {iteration}: {str(e)[:150]}")

    def _task_operation(self, thread_id: int, iteration: int):
        """执行任务管理操作"""
        try:
            op_type = random.choice(['create', 'read', 'update', 'list_pending'])

            if op_type == 'create':
                task = self.storage_backend.create_new_task_entry(
                    task_title=f"任务 #{thread_id}-{iteration}",
                    task_description=f"任务描述: {random.randbytes(50).hex()}",
                    priority_level=random.choice(list(TaskPriorityLevelEnumeration))
                )
                self.metrics['task_created'] += 1

            elif op_type == 'read':
                tasks = self.storage_backend.retrieve_all_tasks()
                if tasks:
                    task = random.choice(tasks)
                    self.storage_backend.retrieve_task_by_id(task.unique_entity_id)
                self.metrics['task_read'] += 1

            elif op_type == 'update':
                tasks = self.storage_backend.retrieve_all_tasks()
                if tasks:
                    task = random.choice(tasks)
                    status = random.choice(list(TaskExecutionStatusEnumeration))
                    self.storage_backend.update_task_entry(
                        task.unique_entity_id,
                        execution_status=status,
                        progress_percentage_value=random.random()
                    )
                self.metrics['task_updated'] += 1

            else:  # list_pending
                self.storage_backend.retrieve_pending_tasks_sorted_by_priority()
                self.metrics['task_listed'] += 1

            self.component_stats['task']['success'] += 1
        except Exception as e:
            self.component_stats['task']['failures'] += 1
            with self.lock:
                self.errors.append(f"[Task] Thread {thread_id}, Iter {iteration}: {str(e)[:150]}")

    def _cache_operation(self, thread_id: int, iteration: int):
        """执行缓存操作"""
        try:
            op_type = random.choice(['set', 'get', 'delete', 'exists'])
            key = f"cache_{thread_id}_{random.randint(0, 1000)}"

            if op_type == 'set':
                value = {
                    'data': random.randbytes(200).hex(),
                    'timestamp': time.time(),
                    'thread_id': thread_id
                }
                ttl = random.choice([0, None, 1, 5, 10, 30])
                self.cache.set(key, value, ttl)
                self.metrics['cache_set'] += 1

            elif op_type == 'get':
                self.cache.get(key)
                self.metrics['cache_get'] += 1

            elif op_type == 'delete':
                self.cache.delete(key)
                self.metrics['cache_deleted'] += 1

            else:  # exists
                self.cache.exists(key)
                self.metrics['cache_exists'] += 1

            self.component_stats['cache']['success'] += 1
        except Exception as e:
            self.component_stats['cache']['failures'] += 1
            with self.lock:
                self.errors.append(f"[Cache] Thread {thread_id}, Iter {iteration}: {str(e)[:150]}")

    def _graph_operation(self, thread_id: int, iteration: int):
        """执行知识图谱操作"""
        try:
            op_type = random.choice(['add_node', 'add_edge', 'get_stats'])

            if op_type == 'add_node':
                node_id = self.storage_backend.add_node_to_knowledge_graph(
                    label=f"节点_{thread_id}_{iteration}",
                    properties={
                        'type': random.choice(['concept', 'entity', 'event']),
                        'value': random.randbytes(30).hex()
                    }
                )
                self.metrics['graph_node_added'] += 1

            elif op_type == 'add_edge':
                # 需要至少两个节点
                # 先创建两个节点
                node1 = self.storage_backend.add_node_to_knowledge_graph(
                    label=f"源节点_{thread_id}_{iteration}_1"
                )
                node2 = self.storage_backend.add_node_to_knowledge_graph(
                    label=f"目标节点_{thread_id}_{iteration}_2"
                )
                self.storage_backend.add_edge_to_knowledge_graph(
                    source_node_id=node1,
                    target_node_id=node2,
                    relationship_type=random.choice(['relates_to', 'depends_on', 'causes', 'includes']),
                    weight=random.uniform(0.1, 1.0)
                )
                self.metrics['graph_edge_added'] += 1

            else:  # get_stats
                self.storage_backend.retrieve_knowledge_graph_statistics()
                self.metrics['graph_stats'] += 1

            self.component_stats['graph']['success'] += 1
        except Exception as e:
            self.component_stats['graph']['failures'] += 1
            with self.lock:
                self.errors.append(f"[Graph] Thread {thread_id}, Iter {iteration}: {str(e)[:150]}")

    def _analytics_operation(self, thread_id: int, iteration: int):
        """执行分析操作"""
        try:
            op_type = random.choice(['get_system_stats', 'get_store_stats', 'get_cache_stats'])

            if op_type == 'get_system_stats':
                self.storage_backend.generate_system_statistics_snapshot()
                self.metrics['system_stats'] += 1

            elif op_type == 'get_store_stats':
                self.store.get_stats()
                self.metrics['store_stats'] += 1

            else:  # get_cache_stats
                self.cache.get_stats()
                self.metrics['cache_stats'] += 1

            self.component_stats['analytics']['success'] += 1
        except Exception as e:
            self.component_stats['analytics']['failures'] += 1
            with self.lock:
                self.errors.append(f"[Analytics] Thread {thread_id}, Iter {iteration}: {str(e)[:150]}")

    def _worker_thread(self, thread_id: int, phase: TestPhase):
        """工作线程"""
        operations = {
            'memory': self._memory_operation,
            'task': self._task_operation,
            'cache': self._cache_operation,
            'graph': self._graph_operation,
            'analytics': self._analytics_operation
        }

        iteration = 0
        phase_start = time.time()

        while not self.stop_flag.is_set() and (time.time() - phase_start) < phase.duration_seconds:
            iteration += 1
            # 根据权重选择操作
            op_types, weights = zip(*phase.workload.items())
            op_type = random.choices(op_types, weights=weights, k=1)[0]

            if op_type in operations:
                operations[op_type](thread_id, iteration)

            # 控制速率，避免CPU 100%
            time.sleep(0.0005)

    def _run_phase(self, phase: TestPhase, thread_count: int):
        """运行单个测试阶段"""
        logger.info("\n" + "=" * 80)
        logger.info(f"🚀 开始阶段: {phase.name}")
        logger.info(f"   描述: {phase.description}")
        logger.info(f"   时长: {phase.duration_seconds}秒")
        logger.info(f"   线程数: {thread_count}")
        logger.info(f"   负载权重: {phase.workload}")
        logger.info("=" * 80)

        phase_start = time.time()
        phase_errors_before = len(self.errors)

        # 启动工作线程
        threads = []
        for i in range(thread_count):
            t = threading.Thread(target=self._worker_thread, args=(i, phase), daemon=True)
            t.start()
            threads.append(t)

        # 监控线程 - 定期获取资源快照
        monitor_stop = threading.Event()

        def monitor_loop():
            while not monitor_stop.is_set() and not self.stop_flag.is_set():
                self._take_resource_snapshot(phase.name)
                time.sleep(5)

        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

        # 等待阶段结束
        for t in threads:
            t.join()

        monitor_stop.set()
        monitor_thread.join(timeout=1)

        # 阶段统计
        phase_duration = time.time() - phase_start
        phase_errors = len(self.errors) - phase_errors_before

        logger.info(f"\n✅ 阶段完成: {phase.name}")
        logger.info(f"   实际耗时: {phase_duration:.1f}秒")
        logger.info(f"   阶段错误: {phase_errors}")

        self.phase_results.append({
            'phase_name': phase.name,
            'duration': phase_duration,
            'errors': phase_errors,
            'thread_count': thread_count
        })

    def run(self):
        """运行完整测试"""
        logger.info("=" * 80)
        logger.info("🔥 开始极端长期生产级测试")
        logger.info("=" * 80)

        try:
            # 初始化
            self._init_components()

            # 运行各个阶段
            for i, phase in enumerate(self.phases):
                # 不同阶段使用不同数量的线程
                if "高并发" in phase.name:
                    thread_count = 200
                elif "内存极限" in phase.name:
                    thread_count = 100
                else:
                    thread_count = 50

                self._run_phase(phase, thread_count)

            # 生成最终报告
            return self._generate_final_report()

        except Exception as e:
            logger.error(f"测试崩溃: {str(e)}")
            import traceback
            traceback.print_exc()
            self.errors.append(f"Fatal: {str(e)}")
            return self._generate_final_report()

    def _analyze_resource_leaks(self):
        """分析资源泄漏"""
        if len(self.resource_snapshots) < 2:
            return []

        issues = []
        # 分析内存增长趋势
        first_snapshot = self.resource_snapshots[0][1]
        last_snapshot = self.resource_snapshots[-1][1]

        memory_growth = last_snapshot.memory_mb - first_snapshot.memory_mb
        if memory_growth > 100:  # 内存增长超过100MB
            issues.append(f"⚠️  内存泄漏可疑: 测试期间内存增长了 {memory_growth:.1f}MB")

        # 分析对象数量
        object_growth = last_snapshot.object_count - first_snapshot.object_count
        if object_growth > 10000:
            issues.append(f"⚠️  对象数量大幅增长: +{object_growth:,} 个对象")

        return issues

    def _generate_final_report(self) -> Dict[str, Any]:
        """生成最终报告"""
        total_duration = sum(phase.duration_seconds for phase in self.phases)
        resource_issues = self._analyze_resource_leaks()

        # 组件成功率统计
        component_success_rates = {}
        for comp, stats in self.component_stats.items():
            total = stats['success'] + stats['failures']
            success_rate = (stats['success'] / total * 100) if total > 0 else 100
            component_success_rates[comp] = {
                'total_ops': total,
                'success': stats['success'],
                'failures': stats['failures'],
                'success_rate': success_rate
            }

        logger.info("\n" + "=" * 80)
        logger.info("📊 极端长期生产级测试 - 最终报告")
        logger.info("=" * 80)
        logger.info(f"总测试时长: {total_duration}秒 ({total_duration/60:.1f}分钟)")
        logger.info(f"总阶段数: {len(self.phases)}")

        logger.info("\n🎯 各阶段结果:")
        for result in self.phase_results:
            status = "✅" if result['errors'] == 0 else "⚠️"
            logger.info(f"  {status} {result['phase_name']}: {result['errors']}个错误")

        logger.info("\n📈 操作统计:")
        for key, value in sorted(self.metrics.items()):
            logger.info(f"  {key}: {value:,}")

        logger.info("\n🏭 组件健康状况:")
        for comp, rates in sorted(component_success_rates.items()):
            status = "✅" if rates['success_rate'] >= 99.9 else "⚠️" if rates['success_rate'] >= 99 else "❌"
            logger.info(f"  {status} {comp}: {rates['success_rate']:.2f}%成功率 "
                       f"({rates['success']:,}/{rates['total_ops']:,})")

        if resource_issues:
            logger.warning("\n⚠️  资源问题警告:")
            for issue in resource_issues:
                logger.warning(f"  {issue}")

        if self.errors:
            logger.error(f"\n❌ 错误总数: {len(self.errors)}")
            logger.error("错误摘要 (前20个):")
            for i, err in enumerate(self.errors[:20]):
                logger.error(f"  {i+1}. {err}")
        else:
            logger.info("\n✅ 没有发现错误！")

        overall_success = len(self.errors) == 0 and \
                         all(rate['success_rate'] >= 99.9 for rate in component_success_rates.values())

        if overall_success:
            logger.info("\n🎉🎉🎉 所有测试通过！系统生产级稳定！")
        else:
            logger.error("\n❌ 测试未能完全通过，需要进一步检查")

        return {
            'total_duration': total_duration,
            'phase_results': self.phase_results,
            'metrics': dict(self.metrics),
            'component_health': component_success_rates,
            'resource_issues': resource_issues,
            'error_count': len(self.errors),
            'errors': self.errors[:50],  # 限制返回的错误数量
            'passed': overall_success
        }


def main():
    """主函数"""
    tester = ExtremeLongTermTester()

    try:
        result = tester.run()

        if result['passed']:
            logger.info("\n🎉 极端长期生产级测试通过！")
        else:
            logger.error("\n❌ 极端长期生产级测试发现问题！")

        return result

    except Exception as e:
        logger.error(f"测试崩溃: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
