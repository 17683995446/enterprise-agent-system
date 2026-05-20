"""
超长时间（1小时+）、超大规模、超复杂混乱场景的极端压力测试
用于发现真实运行时的深层bug
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
import weakref
import resource

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance
from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration
)

logger = get_logger_instance('ultra_extreme_1hour_test')


@dataclass
class PhaseStats:
    """阶段统计"""
    name: str
    start_time: float
    operations: int = 0
    errors: int = 0
    warnings: int = 0


class UltraExtreme1HourTester:
    """超极端1小时+测试器"""

    def __init__(self):
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self.errors = []
        self.warnings = []
        self.metrics = defaultdict(int)
        self.success_metrics = defaultdict(int)
        self.phase_stats = []
        self.resource_samples = []

        # 组件实例
        self.store = SimpleMemoryStore()
        self.cache = SimpleCache()
        self.backend = InMemoryDataStorageBackend()

        # 控制变量
        self.current_phase = "初始化"
        self.operation_count = 0
        self.start_time = None

    def _log_error(self, msg: str, exc_info: Exception = None):
        """记录错误"""
        with self.lock:
            self.errors.append({
                'time': time.time(),
                'phase': self.current_phase,
                'msg': msg,
                'exc': str(exc_info) if exc_info else None,
                'trace': traceback.format_exc()[:500] if exc_info else None
            })
            if len(self.errors) % 100 == 0:
                logger.error(f"错误数达到 {len(self.errors)}: {msg}")

    def _log_warning(self, msg: str):
        """记录警告"""
        with self.lock:
            self.warnings.append({
                'time': time.time(),
                'phase': self.current_phase,
                'msg': msg
            })

    def _generate_extreme_value(self):
        """生成极端值"""
        choices = [
            # 极端数字
            random.randint(-2**31, 2**31-1),
            random.uniform(-1e308, 1e308),
            float('inf'),
            float('-inf'),
            float('nan'),
            None,
            # 极端字符串
            'x' * 100000,  # 100KB字符串
            '',  # 空字符串
            '\x00\x01\x02',  # 控制字符
            '中文' * 1000,
            # 极端数据结构
            [i for i in range(10000)],  # 大列表
            {f'key_{i}': i for i in range(1000)},  # 大字典
            (((1, 2), (3, 4)), ((5, 6), (7, 8))),  # 深层嵌套
        ]
        return random.choice(choices)

    def _chaos_operation_1(self, thread_id: int, iteration: int):
        """混乱操作1 - 任务极端操作"""
        try:
            # 创建任务，传入各种极端值
            title = self._generate_extreme_value()
            desc = self._generate_extreme_value()

            task = self.backend.create_new_task_entry(
                task_title=str(title) if title is not None else '',
                task_description=str(desc) if desc is not None else '',
                priority_level=self._generate_extreme_value()
            )

            self.metrics['task_create'] += 1
            self.success_metrics['task_create'] += 1

            # 极端更新
            if random.random() > 0.5:
                updates = {
                    'execution_status': self._generate_extreme_value(),
                    'progress_percentage_value': self._generate_extreme_value(),
                    'priority_level': self._generate_extreme_value(),
                    'error_message': self._generate_extreme_value()
                }
                self.backend.update_task_entry(task.unique_entity_id, **updates)
                self.metrics['task_update'] += 1
                self.success_metrics['task_update'] += 1

        except Exception as e:
            self.metrics['task_create'] += 1
            self._log_error(f"任务操作失败", e)

    def _chaos_operation_2(self, thread_id: int, iteration: int):
        """混乱操作2 - 记忆极端操作"""
        try:
            content = self._generate_extreme_value()
            category = self._generate_extreme_value()
            importance = self._generate_extreme_value()

            memory = self.backend.create_new_memory_entry(
                content_text=str(content) if content is not None else '',
                category_type=category,
                importance_score=importance if isinstance(importance, int) else 3
            )

            self.metrics['memory_create'] += 1
            self.success_metrics['memory_create'] += 1

            # 疯狂读取
            if random.random() > 0.3:
                for _ in range(random.randint(1, 10)):
                    self.backend.retrieve_memory_by_id(memory.unique_memory_id)
                    self.metrics['memory_read'] += 1
                    self.success_metrics['memory_read'] += 1

        except Exception as e:
            self.metrics['memory_create'] += 1
            self._log_error(f"记忆操作失败", e)

    def _chaos_operation_3(self, thread_id: int, iteration: int):
        """混乱操作3 - 缓存极端操作"""
        try:
            key = self._generate_extreme_value()
            value = self._generate_extreme_value()
            ttl = self._generate_extreme_value()

            # 转换为可哈希的类型
            if isinstance(key, (list, dict)):
                key = str(key)

            # 转换TTL
            if isinstance(ttl, (str, list, dict, float)):
                try:
                    ttl = float(ttl)
                except:
                    ttl = random.choice([0, 1, 10, None])

            op = random.choice(['set', 'get', 'delete'])

            if op == 'set':
                self.cache.set(str(key) if key else f'key_{thread_id}_{iteration}', value, ttl)
                self.metrics['cache_set'] += 1
                self.success_metrics['cache_set'] += 1
            elif op == 'get':
                self.cache.get(str(key) if key else f'key_{thread_id}_{iteration}')
                self.metrics['cache_get'] += 1
                self.success_metrics['cache_get'] += 1
            else:
                self.cache.delete(str(key) if key else f'key_{thread_id}_{iteration}')
                self.metrics['cache_delete'] += 1
                self.success_metrics['cache_delete'] += 1

        except Exception as e:
            self._log_error(f"缓存操作失败", e)

    def _chaos_operation_4(self, thread_id: int, iteration: int):
        """混乱操作4 - 存储报告极端操作"""
        try:
            report_id = str(uuid.uuid4())
            report_data = {
                'id': report_id,
                'title': str(self._generate_extreme_value()),
                'content': str(self._generate_extreme_value()),
                'metadata': self._generate_extreme_value(),
                'timestamp': time.time(),
                'nested': {
                    'data': self._generate_extreme_value(),
                    'list': [self._generate_extreme_value() for _ in range(10)]
                }
            }

            op = random.choice(['save', 'get', 'list', 'delete'])

            if op == 'save':
                self.store.save_report(report_data)
                self.metrics['store_save'] += 1
                self.success_metrics['store_save'] += 1
            elif op == 'get':
                self.store.get_report(report_id)
                self.metrics['store_get'] += 1
                self.success_metrics['store_get'] += 1
            elif op == 'list':
                self.store.list_reports(limit=random.randint(0, 1000))
                self.metrics['store_list'] += 1
                self.success_metrics['store_list'] += 1
            else:
                self.store.delete_report(report_id)
                self.metrics['store_delete'] += 1
                self.success_metrics['store_delete'] += 1

        except Exception as e:
            self._log_error(f"存储操作失败", e)

    def _chaos_operation_5(self, thread_id: int, iteration: int):
        """混乱操作5 - 知识图谱极端操作"""
        try:
            label = self._generate_extreme_value()
            props = self._generate_extreme_value() if random.random() > 0.5 else None

            node_id = self.backend.add_node_to_knowledge_graph(
                label=str(label) if label else 'temp',
                properties=props if isinstance(props, dict) else {'value': str(props)}
            )
            self.metrics['graph_node'] += 1
            self.success_metrics['graph_node'] += 1

            # 疯狂添加边
            if random.random() > 0.7:
                node2 = self.backend.add_node_to_knowledge_graph(label='temp2')
                weight = self._generate_extreme_value()
                try:
                    if isinstance(weight, (int, float)) and not (weight != weight):  # 排除NaN
                        weight = float(weight)
                    else:
                        weight = 1.0
                except:
                    weight = 1.0

                try:
                    self.backend.add_edge_to_knowledge_graph(
                        source_node_id=node_id,
                        target_node_id=node2,
                        relationship_type='rel',
                        weight=weight
                    )
                    self.metrics['graph_edge'] += 1
                    self.success_metrics['graph_edge'] += 1
                except:
                    pass

        except Exception as e:
            self._log_error(f"图操作失败", e)

    def _chaos_operation_6(self, thread_id: int, iteration: int):
        """混乱操作6 - 统计和查询"""
        try:
            ops = [
                lambda: self.backend.generate_system_statistics_snapshot(),
                lambda: self.backend.retrieve_all_tasks(),
                lambda: self.backend.retrieve_all_memories(),
                lambda: self.backend.retrieve_pending_tasks_sorted_by_priority(),
                lambda: self.backend.retrieve_knowledge_graph_statistics(),
                lambda: self.store.get_stats(),
                lambda: self.cache.get_stats(),
            ]

            op = random.choice(ops)
            op()

            self.metrics['analytics'] += 1
            self.success_metrics['analytics'] += 1

        except Exception as e:
            self.metrics['analytics'] += 1
            self._log_error(f"统计操作失败", e)

    def _worker_thread(self, thread_id: int, duration: int):
        """工作线程 - 运行指定时长"""
        operations = [
            self._chaos_operation_1,
            self._chaos_operation_2,
            self._chaos_operation_3,
            self._chaos_operation_4,
            self._chaos_operation_5,
            self._chaos_operation_6,
        ]

        start_time = time.time()
        iteration = 0

        while not self.stop_flag.is_set() and (time.time() - start_time) < duration:
            iteration += 1

            # 随机选择1-5个操作
            num_ops = random.randint(1, 5)
            for _ in range(num_ops):
                op = random.choice(operations)
                op(thread_id, iteration)

            # 随机休眠0-5ms
            time.sleep(random.uniform(0, 0.005))

    def _resource_monitor(self, duration: int):
        """资源监控线程"""
        start_time = time.time()

        while not self.stop_flag.is_set() and (time.time() - start_time) < duration:
            try:
                # 收集资源使用情况
                sample = {
                    'time': time.time(),
                    'thread_count': threading.active_count(),
                    'gc_objects': len(gc.get_objects()),
                }

                # 尝试获取内存信息
                try:
                    import psutil
                    process = psutil.Process()
                    sample['memory_mb'] = process.memory_info().rss / (1024 * 1024)
                    sample['cpu_percent'] = process.cpu_percent()
                except:
                    pass

                with self.lock:
                    self.resource_samples.append(sample)

                # 每5秒输出一次状态
                if len(self.resource_samples) % 100 == 0:
                    elapsed = time.time() - start_time
                    ops = sum(self.metrics.values())
                    logger.info(f"[{elapsed:.0f}s/{duration}s] "
                               f"操作: {ops:,}, 错误: {len(self.errors)}, "
                               f"内存: {sample.get('memory_mb', 0):.1f}MB")

                time.sleep(5)

            except Exception as e:
                logger.error(f"资源监控错误: {e}")

    def _gc_stress(self):
        """GC压力测试"""
        logger.info("执行GC压力测试...")
        for _ in range(10):
            # 创建大量临时对象
            data = [self._generate_extreme_value() for _ in range(10000)]
            del data
            gc.collect()

    def run(self, total_duration: int = 3600):
        """
        运行超长时间测试

        Args:
            total_duration: 总时长（秒），默认1小时
        """
        logger.info(f"{'='*80}")
        logger.info(f"🚀 启动超极端1小时+压力测试")
        logger.info(f"   目标时长: {total_duration}秒 ({total_duration/60:.1f}分钟)")
        logger.info(f"{'='*80}")

        self.start_time = time.time()

        # 阶段1: 预热 (10分钟)
        logger.info("\n📌 阶段1: 预热 (10分钟)")
        self.current_phase = "预热"
        threads = [threading.Thread(target=self._worker_thread, args=(i, 600)) for i in range(50)]
        monitor = threading.Thread(target=self._resource_monitor, args=(600,))

        for t in threads:
            t.start()
        monitor.start()

        for t in threads:
            t.join()
        monitor.join()

        logger.info(f"预热完成 - 操作: {sum(self.metrics.values()):,}, 错误: {len(self.errors)}")

        # 阶段2: 核心压力测试 (30分钟)
        logger.info("\n📌 阶段2: 核心压力测试 (30分钟)")
        self.current_phase = "核心压力"
        threads = [threading.Thread(target=self._worker_thread, args=(i, 1800)) for i in range(100)]
        monitor = threading.Thread(target=self._resource_monitor, args=(1800,))

        for t in threads:
            t.start()
        monitor.start()

        for t in threads:
            t.join()
        monitor.join()

        logger.info(f"核心压力完成 - 操作: {sum(self.metrics.values()):,}, 错误: {len(self.errors)}")

        # 阶段3: GC压力测试 (5分钟)
        logger.info("\n📌 阶段3: GC压力测试 (5分钟)")
        self.current_phase = "GC压力"
        self._gc_stress()

        # 阶段4: 高并发测试 (15分钟)
        logger.info("\n📌 阶段4: 高并发测试 (15分钟)")
        self.current_phase = "高并发"
        threads = [threading.Thread(target=self._worker_thread, args=(i, 900)) for i in range(200)]
        monitor = threading.Thread(target=self._resource_monitor, args=(900,))

        for t in threads:
            t.start()
        monitor.start()

        for t in threads:
            t.join()
        monitor.join()

        logger.info(f"高并发完成 - 操作: {sum(self.metrics.values()):,}, 错误: {len(self.errors)}")

        # 生成最终报告
        return self._generate_report(total_duration)

    def _generate_report(self, duration: int):
        """生成最终报告"""
        logger.info(f"\n{'='*80}")
        logger.info("📊 超极端1小时+测试 - 最终报告")
        logger.info(f"{'='*80}")

        actual_duration = time.time() - self.start_time

        logger.info(f"\n⏱️  时间统计:")
        logger.info(f"   目标时长: {duration}秒 ({duration/60:.1f}分钟)")
        logger.info(f"   实际时长: {actual_duration:.1f}秒 ({actual_duration/60:.1f}分钟)")

        logger.info(f"\n📈 操作统计:")
        total_ops = sum(self.metrics.values())
        total_success = sum(self.success_metrics.values())
        logger.info(f"   总操作: {total_ops:,}")
        logger.info(f"   成功操作: {total_success:,}")
        logger.info(f"   失败操作: {total_ops - total_success:,}")
        logger.info(f"   成功率: {total_success/total_ops*100:.2f}%")

        logger.info(f"\n📊 操作类型分布:")
        for op_type, count in sorted(self.metrics.items(), key=lambda x: -x[1])[:10]:
            success = self.success_metrics.get(op_type, 0)
            logger.info(f"   {op_type}: {count:,} (成功率: {success/count*100:.1f}%)")

        logger.info(f"\n❌ 错误统计:")
        logger.info(f"   总错误数: {len(self.errors)}")
        if self.errors:
            # 按类型统计错误
            error_types = defaultdict(int)
            for err in self.errors:
                error_types[err['exc'] or 'Unknown'] += 1

            logger.info(f"   错误类型:")
            for err_type, count in sorted(error_types.items(), key=lambda x: -x[1])[:10]:
                logger.info(f"     {err_type}: {count}")

            logger.info(f"\n   错误样例 (前5):")
            for i, err in enumerate(self.errors[:5]):
                logger.info(f"     [{i+1}] {err['phase']}: {err['msg']} - {err['exc']}")

        logger.info(f"\n⚠️  警告统计:")
        logger.info(f"   总警告数: {len(self.warnings)}")

        logger.info(f"\n💾 资源使用:")
        if self.resource_samples:
            first = self.resource_samples[0]
            last = self.resource_samples[-1]
            memory_growth = last.get('memory_mb', 0) - first.get('memory_mb', 0)

            logger.info(f"   内存变化: {memory_growth:+.1f}MB")
            logger.info(f"   峰值线程数: {max(s.get('thread_count', 0) for s in self.resource_samples)}")
            logger.info(f"   平均线程数: {sum(s.get('thread_count', 0) for s in self.resource_samples)/len(self.resource_samples):.1f}")

        passed = len(self.errors) == 0 and actual_duration >= duration * 0.95

        if passed:
            logger.info(f"\n🎉🎉🎉 测试完美通过！")
        else:
            logger.error(f"\n❌ 测试未能完全通过")

        return {
            'duration': actual_duration,
            'total_operations': total_ops,
            'total_success': total_success,
            'total_errors': len(self.errors),
            'passed': passed,
            'success_rate': total_success / total_ops if total_ops > 0 else 0
        }


def main():
    """主函数"""
    tester = UltraExtreme1HourTester()

    # 运行1小时的测试（可以调整为更长）
    # 注意：实际运行需要很长时间，请根据需要调整 duration 参数
    result = tester.run(total_duration=3600)  # 1小时

    if result['passed']:
        logger.info("\n✅ 超极端1小时+测试通过！")
        return 0
    else:
        logger.error(f"\n❌ 测试发现问题！错误数: {result['total_errors']}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
