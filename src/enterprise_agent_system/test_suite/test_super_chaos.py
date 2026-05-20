"""
超级混乱、超级极端、超级大规模的生产级压力测试
包含：大量并发、随机数据、边缘情况、资源压力、长时间运行
"""

import sys
import time
import random
import threading
import gc
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import traceback

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance
from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration
)

logger = get_logger_instance('super_chaos_test')


@dataclass
class TestPhase:
    """测试阶段"""
    name: str
    duration_seconds: int
    thread_count: int
    operations_per_second: int
    description: str


@dataclass
class ErrorLog:
    """错误记录"""
    timestamp: float
    thread_id: int
    phase: str
    operation: str
    error_type: str
    error_message: str
    stack_trace: str
    iteration: int


class SuperChaosTester:
    """超级混乱测试器"""

    TEST_PHASES = [
        TestPhase(
            name="疯狂初始化",
            duration_seconds=60,
            thread_count=50,
            operations_per_second=1000,
            description="创建大量任务、记忆、节点"
        ),
        TestPhase(
            name="混合读写风暴",
            duration_seconds=120,
            thread_count=150,
            operations_per_second=3000,
            description="疯狂混合读写，完全混乱的顺序"
        ),
        TestPhase(
            name="边界值雪崩",
            duration_seconds=90,
            thread_count=100,
            operations_per_second=2000,
            description="极端边缘情况，空字符串、超长数据、特殊字符"
        ),
        TestPhase(
            name="线程竞争赛",
            duration_seconds=150,
            thread_count=300,
            operations_per_second=5000,
            description="超级高并发，所有线程同时操作相同资源"
        ),
        TestPhase(
            name="清理与重建",
            duration_seconds=60,
            thread_count=80,
            operations_per_second=1500,
            description="大量删除再重建"
        ),
        TestPhase(
            name="最终验证风暴",
            duration_seconds=120,
            thread_count=200,
            operations_per_second=4000,
            description="疯狂验证操作，确保一切正常"
        )
    ]

    def __init__(self):
        self.store = SimpleMemoryStore()
        self.cache = SimpleCache()
        self.backend = InMemoryDataStorageBackend()
        self.errors = []
        self.warnings = []
        self.error_lock = threading.Lock()
        self.stop_flag = threading.Event()
        self.operation_counters = defaultdict(int)
        self.counter_lock = threading.Lock()
        self.success_counters = defaultdict(int)
        self.phase_results = []
        self.resource_snapshots = []

    def _generate_chaos_string(self, length: int = 100) -> str:
        """生成混乱字符串"""
        chars = (
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            '!@#$%^&*()_+-=[]{}|;:,.<>?`~ \t\n\r\x00\x01\x02\x03'
            '中文俄文العربية日本語'
        )
        return ''.join(random.choice(chars) for _ in range(length))

    def _generate_chaos_dict(self) -> Dict[str, Any]:
        """生成混乱字典"""
        return {
            'key_' + str(i): random.choice([
                random.randint(-1000000, 1000000),
                random.random(),
                self._generate_chaos_string(random.randint(1, 500)),
                random.choice([True, False, None]),
                [random.randint(0, 100) for _ in range(random.randint(0, 20))],
                {'nested': self._generate_chaos_string(20)}
            ])
            for i in range(random.randint(0, 10))
        }

    def _chaos_create_task(self, thread_id: int, i: int) -> None:
        """混乱的任务创建"""
        try:
            title = self._generate_chaos_string(random.randint(1, 200)) if random.random() > 0.1 else random.choice(['', '    ', None])
            desc = self._generate_chaos_string(random.randint(0, 1000)) if random.random() > 0.05 else ''
            
            # 随机选择优先级（可能是字符串或枚举）
            priority = random.choice([
                random.choice(list(TaskPriorityLevelEnumeration)),
                random.choice(['low', 'medium', 'high', 'urgent', 'LOW_PRIORITY_LEVEL', 'invalid']),
                None
            ])
            
            task = self.backend.create_new_task_entry(
                task_title=title if title is not None else '',
                task_description=desc,
                priority_level=priority
            )
            with self.counter_lock:
                self.operation_counters['task_create'] += 1
                self.success_counters['task_create'] += 1
                
            # 随机立即更新
            if random.random() > 0.7:
                new_status = random.choice([
                    random.choice(list(TaskExecutionStatusEnumeration)),
                    random.choice(['pending', 'in_progress', 'completed', 'failed', 'invalid']),
                    None
                ])
                self.backend.update_task_entry(
                    task.unique_entity_id,
                    execution_status=new_status,
                    progress_percentage_value=random.random()
                )
                with self.counter_lock:
                    self.operation_counters['task_update'] += 1
                    self.success_counters['task_update'] += 1
        except Exception as e:
            self._log_error(thread_id, 'task_create', e, i)

    def _chaos_create_memory(self, thread_id: int, i: int) -> None:
        """混乱的记忆创建"""
        try:
            content = self._generate_chaos_string(random.randint(0, 5000)) if random.random() > 0.1 else ''
            category = random.choice([
                random.choice(list(MemoryCategoryTypeEnumeration)),
                random.choice(['general', 'technical', 'experience', 'knowledge', 'invalid']),
                None
            ])
            tags = [self._generate_chaos_string(random.randint(1, 20)) for _ in range(random.randint(0, 20))] if random.random() > 0.2 else []
            importance = random.randint(-100, 100) if random.random() > 0.05 else random.choice([None, 0, 1, 5, 1000])
            
            memory = self.backend.create_new_memory_entry(
                content_text=content,
                category_type=category if category is not None else MemoryCategoryTypeEnumeration.GENERAL_MEMORY_CATEGORY,
                tags_list=tags,
                importance_score=importance if importance is not None else 3
            )
            with self.counter_lock:
                self.operation_counters['memory_create'] += 1
                self.success_counters['memory_create'] += 1
                
            # 随机立即查询
            if random.random() > 0.6:
                self.backend.retrieve_memory_by_id(memory.unique_memory_id)
                with self.counter_lock:
                    self.operation_counters['memory_read'] += 1
                    self.success_counters['memory_read'] += 1
        except Exception as e:
            self._log_error(thread_id, 'memory_create', e, i)

    def _chaos_cache_operations(self, thread_id: int, i: int) -> None:
        """混乱的缓存操作"""
        try:
            key = self._generate_chaos_string(random.randint(1, 200)) if random.random() > 0.05 else random.choice(['', '    ', None, 'very-long-key-' * 100])
            value = random.choice([
                self._generate_chaos_dict(),
                self._generate_chaos_string(random.randint(1, 10000)),
                [random.randint(0, 100) for _ in range(random.randint(0, 1000))],
                None,
                random.randint(-1000000000, 1000000000)
            ])
            ttl = random.choice([0, 1, 10, 60, 3600, None, -1, random.randint(-100, 100)])
            
            # 随机执行多个操作
            ops = random.randint(1, 4)
            for _ in range(ops):
                op = random.choice(['set', 'get', 'delete', 'exists', 'get_stats'])
                if op == 'set':
                    self.cache.set(key, value, ttl)
                    with self.counter_lock:
                        self.operation_counters['cache_set'] += 1
                        self.success_counters['cache_set'] += 1
                elif op == 'get':
                    self.cache.get(key)
                    with self.counter_lock:
                        self.operation_counters['cache_get'] += 1
                        self.success_counters['cache_get'] += 1
                elif op == 'delete':
                    self.cache.delete(key)
                    with self.counter_lock:
                        self.operation_counters['cache_delete'] += 1
                        self.success_counters['cache_delete'] += 1
                elif op == 'exists':
                    self.cache.exists(key)
                    with self.counter_lock:
                        self.operation_counters['cache_exists'] += 1
                        self.success_counters['cache_exists'] += 1
                elif op == 'get_stats':
                    self.cache.get_stats()
                    with self.counter_lock:
                        self.operation_counters['cache_stats'] += 1
                        self.success_counters['cache_stats'] += 1
        except Exception as e:
            self._log_error(thread_id, 'cache_ops', e, i)

    def _chaos_knowledge_graph(self, thread_id: int, i: int) -> None:
        """混乱的知识图谱操作"""
        try:
            # 随机混合各种操作
            for _ in range(random.randint(1, 5)):
                op = random.choice(['add_node', 'add_edge', 'get_stats'])
                
                if op == 'add_node':
                    label = self._generate_chaos_string(random.randint(1, 50)) if random.random() > 0.1 else ''
                    props = self._generate_chaos_dict() if random.random() > 0.2 else None
                    node_id = self.backend.add_node_to_knowledge_graph(
                        label=label,
                        properties=props
                    )
                    with self.counter_lock:
                        self.operation_counters['graph_node_add'] += 1
                        self.success_counters['graph_node_add'] += 1
                        
                elif op == 'add_edge':
                    # 创建一些临时节点
                    if random.random() > 0.3:
                        node1 = self.backend.add_node_to_knowledge_graph(label='temp1')
                        node2 = self.backend.add_node_to_knowledge_graph(label='temp2')
                        rel_type = self._generate_chaos_string(random.randint(1, 20)) if random.random() > 0.1 else 'rel'
                        weight = random.random() * 1000 if random.random() > 0.2 else random.choice([0, -1, 1000, None])
                        try:
                            self.backend.add_edge_to_knowledge_graph(
                                source_node_id=node1,
                                target_node_id=node2,
                                relationship_type=rel_type,
                                weight=weight if weight is not None else 1.0
                            )
                            with self.counter_lock:
                                self.operation_counters['graph_edge_add'] += 1
                                self.success_counters['graph_edge_add'] += 1
                        except Exception:
                            pass  # 图操作预期可能会有一些异常
                            
                elif op == 'get_stats':
                    self.backend.retrieve_knowledge_graph_statistics()
                    with self.counter_lock:
                        self.operation_counters['graph_stats'] += 1
                        self.success_counters['graph_stats'] += 1
        except Exception as e:
            self._log_error(thread_id, 'graph_ops', e, i)

    def _chaos_store_operations(self, thread_id: int, i: int) -> None:
        """混乱的存储报告操作"""
        try:
            report_id = str(uuid.uuid4()) if random.random() > 0.1 else random.choice(['', None])
            report_data = {
                'id': report_id if report_id is not None else str(uuid.uuid4()),
                'title': self._generate_chaos_string(random.randint(0, 100)),
                'type': self._generate_chaos_string(10),
                'content': self._generate_chaos_string(random.randint(0, 2000)),
                'summary': self._generate_chaos_string(random.randint(0, 500)) if random.random() > 0.3 else None,
                'quality_score': random.uniform(-100, 200),
                'confidence': random.uniform(0, 2),
                'findings': [self._generate_chaos_dict() for _ in range(random.randint(0, 5))] if random.random() > 0.4 else None,
                'extra': self._generate_chaos_dict()
            }
            
            op = random.choice(['save', 'get', 'list', 'delete'])
            if op == 'save':
                self.store.save_report(report_data)
                with self.counter_lock:
                    self.operation_counters['store_save'] += 1
                    self.success_counters['store_save'] += 1
            elif op == 'get':
                # 可能用不存在的ID
                target_id = report_id if random.random() > 0.3 else str(uuid.uuid4())
                self.store.get_report(target_id)
                with self.counter_lock:
                    self.operation_counters['store_get'] += 1
                    self.success_counters['store_get'] += 1
            elif op == 'list':
                limit = random.randint(0, 1000)
                offset = random.randint(0, 500)
                self.store.list_reports(limit=limit, offset=offset)
                with self.counter_lock:
                    self.operation_counters['store_list'] += 1
                    self.success_counters['store_list'] += 1
            elif op == 'delete':
                target_id = report_id if random.random() > 0.3 else str(uuid.uuid4())
                self.store.delete_report(target_id)
                with self.counter_lock:
                    self.operation_counters['store_delete'] += 1
                    self.success_counters['store_delete'] += 1
        except Exception as e:
            self._log_error(thread_id, 'store_ops', e, i)

    def _chaos_analytics(self, thread_id: int, i: int) -> None:
        """混乱的分析操作"""
        try:
            for _ in range(random.randint(1, 3)):
                op = random.choice(['stats', 'pending', 'all_tasks', 'all_memories'])
                if op == 'stats':
                    self.backend.generate_system_statistics_snapshot()
                elif op == 'pending':
                    self.backend.retrieve_pending_tasks_sorted_by_priority()
                elif op == 'all_tasks':
                    self.backend.retrieve_all_tasks()
                elif op == 'all_memories':
                    self.backend.retrieve_all_memories()
                
                with self.counter_lock:
                    self.operation_counters['analytics_' + op] += 1
                    self.success_counters['analytics_' + op] += 1
        except Exception as e:
            self._log_error(thread_id, 'analytics', e, i)

    def _log_error(self, thread_id: int, op_name: str, error: Exception, iteration: int) -> None:
        """记录错误"""
        with self.error_lock:
            error_log = ErrorLog(
                timestamp=time.time(),
                thread_id=thread_id,
                phase=getattr(self, 'current_phase', 'unknown'),
                operation=op_name,
                error_type=type(error).__name__,
                error_message=str(error)[:200],
                stack_trace=traceback.format_exc()[:1000],
                iteration=iteration
            )
            self.errors.append(error_log)
            
            with self.counter_lock:
                self.operation_counters[op_name] += 1  # 确保计数增加
                # 不增加成功计数

    def _worker_thread(self, thread_id: int, phase: TestPhase, phase_start: float) -> None:
        """工作线程"""
        i = 0
        while not self.stop_flag.is_set() and (time.time() - phase_start) < phase.duration_seconds:
            i += 1
            try:
                # 随机选择多种操作
                operations = [
                    self._chaos_create_task,
                    self._chaos_create_memory,
                    self._chaos_cache_operations,
                    self._chaos_knowledge_graph,
                    self._chaos_store_operations,
                    self._chaos_analytics
                ]
                
                # 随机执行1-3个操作
                for _ in range(random.randint(1, 3)):
                    op = random.choice(operations)
                    op(thread_id, i)
                
                # 控制速率
                sleep_time = 1.0 / phase.operations_per_second * random.uniform(0.5, 2.0)
                time.sleep(sleep_time)
                
            except Exception as e:
                self._log_error(thread_id, 'worker_loop', e, i)

    def _take_resource_snapshot(self, phase_name: str) -> None:
        """获取资源快照"""
        try:
            import psutil
            memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)
        except Exception:
            memory_mb = 0
        
        gc_stats = gc.get_stats()
        gc_collections = sum(s['collections'] for s in gc_stats)
        active_threads = threading.active_count()
        
        self.resource_snapshots.append({
            'phase': phase_name,
            'timestamp': time.time(),
            'memory_mb': memory_mb,
            'gc_collections': gc_collections,
            'active_threads': active_threads,
            'object_count': len(gc.get_objects())
        })

    def _run_single_phase(self, phase: TestPhase) -> Dict[str, Any]:
        """运行单个阶段"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 开始阶段: {phase.name}")
        logger.info(f"   描述: {phase.description}")
        logger.info(f"   线程: {phase.thread_count}")
        logger.info(f"   目标OPS: {phase.operations_per_second}")
        logger.info(f"{'='*80}")
        
        self.current_phase = phase.name
        start_time = time.time()
        errors_before = len(self.errors)
        
        # 启动工作线程
        threads = []
        phase_start = time.time()
        for i in range(phase.thread_count):
            t = threading.Thread(target=self._worker_thread, args=(i, phase, phase_start), daemon=True)
            t.start()
            threads.append(t)
        
        # 监控线程
        monitor_stop = threading.Event()
        def monitor_loop():
            last_report = time.time()
            while not monitor_stop.is_set() and not self.stop_flag.is_set():
                self._take_resource_snapshot(phase.name)
                
                if time.time() - last_report >= 10:
                    elapsed = time.time() - start_time
                    total_ops = sum(self.operation_counters.values())
                    logger.info(f"   [进度 {elapsed:.0f}s/{phase.duration_seconds}s] "
                               f"总操作: {total_ops:,}, 错误: {len(self.errors) - errors_before}")
                    last_report = time.time()
                
                time.sleep(2)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        # 等待阶段完成
        for t in threads:
            t.join()
        
        monitor_stop.set()
        monitor_thread.join(timeout=2)
        
        # 阶段统计
        duration = time.time() - start_time
        phase_errors = len(self.errors) - errors_before
        total_ops = sum(self.operation_counters.values())
        
        logger.info(f"\n✅ 阶段完成: {phase.name}")
        logger.info(f"   耗时: {duration:.1f}s, 总操作: {total_ops:,}, 错误: {phase_errors}")
        
        return {
            'name': phase.name,
            'duration': duration,
            'total_operations': total_ops,
            'errors': phase_errors
        }

    def _generate_final_report(self) -> Dict[str, Any]:
        """生成最终报告"""
        logger.info(f"\n{'='*80}")
        logger.info("📊 超级混乱测试 - 最终报告")
        logger.info(f"{'='*80}")
        
        total_ops = sum(self.operation_counters.values())
        total_success = sum(self.success_counters.values())
        
        logger.info(f"总操作: {total_ops:,}")
        logger.info(f"总成功: {total_success:,}")
        logger.info(f"总错误: {len(self.errors):,}")
        
        if self.errors:
            logger.warning(f"\n⚠️  错误类型统计:")
            error_types = defaultdict(int)
            for err in self.errors:
                error_types[err.error_type] += 1
            for err_type, count in sorted(error_types.items(), key=lambda x: -x[1])[:10]:
                logger.warning(f"  {err_type}: {count:,}")
            
            logger.error(f"\n❌ 错误样例 (前10):")
            for i, err in enumerate(self.errors[:10]):
                logger.error(f"  [{i+1}] {err.operation} - {err.error_type}: {err.error_message[:100]}")
        else:
            logger.info(f"\n🎉 无错误！完美！")
        
        # 资源分析
        if self.resource_snapshots:
            logger.info(f"\n📈 资源分析:")
            first = self.resource_snapshots[0]
            last = self.resource_snapshots[-1]
            memory_growth = last['memory_mb'] - first['memory_mb']
            logger.info(f"  内存变化: {memory_growth:+.1f}MB ({first['memory_mb']:.1f}MB → {last['memory_mb']:.1f}MB)")
            logger.info(f"  GC收集: {last['gc_collections'] - first['gc_collections']:,} 次")
        
        return {
            'total_operations': total_ops,
            'total_success': total_success,
            'error_count': len(self.errors),
            'passed': len(self.errors) == 0,
            'success_rate': total_success / total_ops if total_ops > 0 else 0
        }

    def run(self) -> Dict[str, Any]:
        """运行完整测试"""
        logger.info(f"{'='*80}")
        logger.info("🔥 超级混乱、超级极端、超级大规模压力测试启动！")
        logger.info(f"{'='*80}")
        
        try:
            for phase in self.TEST_PHASES:
                result = self._run_single_phase(phase)
                self.phase_results.append(result)
            
            return self._generate_final_report()
            
        except Exception as e:
            logger.error(f"FATAL ERROR: {e}")
            traceback.print_exc()
            self._log_error(-1, 'main', e, 0)
            return self._generate_final_report()


def main():
    """主函数"""
    tester = SuperChaosTester()
    result = tester.run()
    
    if result['passed']:
        logger.info("\n🎉🎉🎉 所有测试通过！超级混乱测试完美！")
        return 0
    else:
        logger.error("\n❌ 有错误！请检查并修复！")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
