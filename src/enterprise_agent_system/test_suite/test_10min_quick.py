"""
快速版本 - 10分钟超极端测试
"""

import sys
import time
import random
import threading
import gc
import uuid
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

logger = get_logger_instance('quick_10min_test')

class QuickExtremeTester:
    """快速极端测试器 - 10分钟"""

    def __init__(self):
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self.errors = []
        self.metrics = defaultdict(int)
        self.success_metrics = defaultdict(int)
        self.store = SimpleMemoryStore()
        self.cache = SimpleCache()
        self.backend = InMemoryDataStorageBackend()

    def _generate_extreme_value(self):
        """生成极端值"""
        choices = [
            None, '', 'x' * 10000,
            random.randint(-1000000, 1000000),
            float('inf'), float('nan'),
            [i for i in range(1000)],
            {f'k{i}': i for i in range(100)},
        ]
        return random.choice(choices)

    def _random_operation(self, thread_id: int):
        """随机操作"""
        try:
            op_type = random.randint(0, 5)

            if op_type == 0:  # 任务创建
                title = str(self._generate_extreme_value() or '')
                desc = str(self._generate_extreme_value() or '')
                task = self.backend.create_new_task_entry(
                    task_title=title,
                    task_description=desc,
                    priority_level=self._generate_extreme_value()
                )
                self.metrics['task_create'] += 1
                self.success_metrics['task_create'] += 1

                # 更新
                self.backend.update_task_entry(
                    task.unique_entity_id,
                    execution_status=self._generate_extreme_value(),
                    progress_percentage_value=random.random()
                )
                self.metrics['task_update'] += 1
                self.success_metrics['task_update'] += 1

            elif op_type == 1:  # 记忆
                content = str(self._generate_extreme_value() or '')
                memory = self.backend.create_new_memory_entry(
                    content_text=content,
                    category_type=self._generate_extreme_value()
                )
                self.metrics['memory_create'] += 1
                self.success_metrics['memory_create'] += 1

                self.backend.retrieve_memory_by_id(memory.unique_memory_id)
                self.metrics['memory_read'] += 1
                self.success_metrics['memory_read'] += 1

            elif op_type == 2:  # 缓存
                key = f'key_{thread_id}_{random.randint(0, 100)}'
                value = self._generate_extreme_value()

                if random.random() > 0.5:
                    self.cache.set(key, value)
                    self.metrics['cache_set'] += 1
                    self.success_metrics['cache_set'] += 1
                else:
                    self.cache.get(key)
                    self.metrics['cache_get'] += 1
                    self.success_metrics['cache_get'] += 1

            elif op_type == 3:  # 存储
                report_id = str(uuid.uuid4())
                data = {
                    'id': report_id,
                    'title': str(self._generate_extreme_value()),
                    'data': self._generate_extreme_value()
                }
                self.store.save_report(data)
                self.metrics['store_save'] += 1
                self.success_metrics['store_save'] += 1

            elif op_type == 4:  # 图
                label = str(self._generate_extreme_value() or 'temp')
                node_id = self.backend.add_node_to_knowledge_graph(label=label)
                self.metrics['graph_node'] += 1
                self.success_metrics['graph_node'] += 1

            else:  # 统计
                self.backend.generate_system_statistics_snapshot()
                self.metrics['stats'] += 1
                self.success_metrics['stats'] += 1

        except Exception as e:
            with self.lock:
                self.errors.append({
                    'type': op_type,
                    'error': str(e),
                    'trace': traceback.format_exc()[:200]
                })
            self.metrics[f'error_{op_type}'] += 1

    def _worker(self, thread_id: int, duration: int):
        """工作线程"""
        start = time.time()
        ops = 0
        while not self.stop_flag.is_set() and (time.time() - start) < duration:
            self._random_operation(thread_id)
            ops += 1
            if ops % 1000 == 0:
                elapsed = time.time() - start
                logger.info(f"Thread {thread_id}: {ops} ops, {elapsed:.0f}s")

    def _monitor(self, duration: int):
        """监控线程"""
        start = time.time()
        last_report = start
        while not self.stop_flag.is_set() and (time.time() - start) < duration:
            if time.time() - last_report >= 60:  # 每分钟报告
                elapsed = time.time() - start
                total_ops = sum(self.metrics.values())
                logger.info(f"\n[{elapsed:.0f}s] 总操作: {total_ops:,}, 错误: {len(self.errors)}\n")
                last_report = time.time()
            time.sleep(1)

    def run(self, duration: int = 600):
        """运行测试"""
        logger.info(f"{'='*60}")
        logger.info(f"🚀 10分钟超极端测试 - 开始")
        logger.info(f"{'='*60}")

        start_time = time.time()

        # 启动100个线程
        threads = []
        for i in range(100):
            t = threading.Thread(target=self._worker, args=(i, duration))
            threads.append(t)
            t.start()

        # 监控
        monitor = threading.Thread(target=self._monitor, args=(duration,))
        monitor.start()

        # 等待
        for t in threads:
            t.join()
        self.stop_flag.set()
        monitor.join()

        actual_duration = time.time() - start_time

        # 报告
        logger.info(f"\n{'='*60}")
        logger.info("📊 最终报告")
        logger.info(f"{'='*60}")

        total_ops = sum(self.metrics.values())
        total_success = sum(self.success_metrics.values())

        logger.info(f"时长: {actual_duration:.1f}s")
        logger.info(f"总操作: {total_ops:,}")
        logger.info(f"成功: {total_success:,}")
        logger.info(f"错误: {len(self.errors):,}")

        if self.errors:
            logger.error(f"\n❌ 错误详情:")
            error_counts = defaultdict(int)
            for err in self.errors:
                error_counts[err['error']] += 1

            for err_type, count in sorted(error_counts.items(), key=lambda x: -x[1])[:10]:
                logger.error(f"  {count}x: {err_type[:80]}")

            logger.error(f"\n第一个错误的完整trace:")
            logger.error(self.errors[0]['trace'])

        passed = len(self.errors) == 0

        if passed:
            logger.info(f"\n🎉 测试完美通过！")
        else:
            logger.error(f"\n❌ 发现 {len(self.errors)} 个错误！")

        return {
            'duration': actual_duration,
            'total_ops': total_ops,
            'errors': len(self.errors),
            'passed': passed
        }


if __name__ == '__main__':
    tester = QuickExtremeTester()
    result = tester.run(duration=600)  # 10分钟
    sys.exit(0 if result['passed'] else 1)
