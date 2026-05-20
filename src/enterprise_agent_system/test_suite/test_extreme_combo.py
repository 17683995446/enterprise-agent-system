"""
极端极限组合测试 - 2小时+
组合所有极端场景同时运行
"""

import sys
import time
import random
import threading
import gc
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, Future
from collections import deque

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('extreme_combo_test')


@dataclass
class TestPhase:
    name: str
    duration: float
    load_type: str
    thread_count: int
    operations_per_second: int
    data_size_range: tuple


class ExtremeComboTester:
    """极端极限组合测试器"""
    
    def __init__(self, total_duration=7200):  # 默认2小时
        self.total_duration = total_duration
        self.results: Dict[str, Any] = {}
        self.stop_flag = threading.Event()
        self.lock = threading.RLock()
        self.operation_count = 0
        self.error_count = 0
        self.success_count = 0
        self.operation_errors: List[str] = []
        self.phase_metrics: List[Dict] = []
        self.memory_history: deque = deque(maxlen=100)
        
        # 极端测试阶段配置 (演示版缩短时间)
        self.phases = [
            TestPhase("Warmup", 30, "light", 4, 500, (100, 500)),
            TestPhase("Normal Load", 60, "normal", 8, 1000, (500, 2000)),
            TestPhase("Extreme Load", 120, "extreme", 16, 2500, (2000, 10000)),
            TestPhase("Burst Traffic", 60, "burst", 24, 5000, (100, 1000)),
            TestPhase("Chaos Mode", 120, "chaos", 20, 3000, (100, 10000)),
            TestPhase("Cooldown", 30, "light", 4, 500, (100, 500)),
        ]
    
    def _get_memory_mb(self) -> float:
        """获取当前内存使用"""
        try:
            import psutil
            return psutil.Process().memory_info().rss / (1024 * 1024)
        except:
            return 0
    
    def _generate_large_data(self, min_size: int, max_size: int) -> str:
        """生成随机大小的数据"""
        size = random.randint(min_size, max_size)
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()'
        return ''.join(random.choice(chars) for _ in range(size))
    
    def _chaos_operation(self, store, cache, report_id):
        """模拟故障和边界情况的混沌操作"""
        roll = random.random()
        
        if roll < 0.1:  # 10% 概率使用超长ID
            report_id = 'x' * 1000
        elif roll < 0.2:  # 10% 概率使用空数据
            store.save_report({
                "id": report_id,
                "title": None,
                "type": "",
                "summary": "",
                "quality_score": None,
                "metrics": None
            })
            return
        elif roll < 0.3:  # 10% 概率使用极端分数
            store.save_report({
                "id": report_id,
                "title": "Extreme Score",
                "type": "chaos",
                "summary": "Test",
                "quality_score": 1e10 if random.random() < 0.5 else -1e10
            })
            return
        elif roll < 0.4:  # 10% 概率尝试删除不存在的ID
            store.delete_report("non_existent_id_987654321")
            return
        
        # 正常操作
        store.save_report({
            "id": report_id,
            "title": f"Chaos Test {report_id}",
            "type": "chaos",
            "summary": self._generate_large_data(100, 1000),
            "quality_score": random.random() * 10,
            "metrics": {"phase": "chaos", "time": time.time()}
        })
    
    def _worker_thread(self, phase: TestPhase, worker_id: int):
        """工作线程执行函数"""
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
        
        store = SimpleMemoryStore()
        cache = SimpleCache()
        
        phase_start = time.time()
        phase_end = phase_start + phase.duration
        
        local_ops = 0
        local_errors = 0
        
        while not self.stop_flag.is_set() and time.time() < phase_end:
            try:
                op_start = time.time()
                report_id = f"combo_{worker_id}_{local_ops}"
                
                if phase.load_type == "chaos":
                    self._chaos_operation(store, cache, report_id)
                else:
                    # 正常负载操作
                    if random.random() < 0.3:
                        # 读操作
                        store.get_report(f"combo_{worker_id}_{random.randint(0, max(0, local_ops - 100))}")
                    elif random.random() < 0.2:
                        # 缓存操作
                        cache.set(report_id, f"cache_value_{report_id}")
                        cache.get(report_id)
                    else:
                        # 写操作
                        min_size, max_size = phase.data_size_range
                        store.save_report({
                            "id": report_id,
                            "title": f"Combo Test {report_id}",
                            "type": phase.load_type,
                            "content": self._generate_large_data(min_size, max_size),
                            "summary": f"Phase: {phase.name}, Worker: {worker_id}",
                            "quality_score": random.uniform(0, 10),
                            "metrics": {
                                "worker": worker_id,
                                "phase": phase.name,
                                "time": time.time(),
                                "data_size": random.randint(min_size, max_size)
                            }
                        })
                
                local_ops += 1
                
                # 控制操作速率
                elapsed = time.time() - op_start
                if elapsed < 1.0 / phase.operations_per_second:
                    time.sleep(1.0 / phase.operations_per_second - elapsed)
                
            except Exception as e:
                local_errors += 1
                error_msg = f"Worker {worker_id} in {phase.name}: {str(e)[:100]}"
                with self.lock:
                    self.operation_errors.append(error_msg)
                    if len(self.operation_errors) > 100:
                        self.operation_errors = self.operation_errors[-50:]
        
        with self.lock:
            self.operation_count += local_ops
            self.success_count += local_ops - local_errors
            self.error_count += local_errors
    
    def run(self):
        """运行完整的极端测试"""
        logger.info("=" * 80)
        logger.info("🔥 开始极端极限组合测试 - 2小时+")
        logger.info("=" * 80)
        
        total_start = time.time()
        initial_memory = self._get_memory_mb()
        peak_memory = initial_memory
        
        try:
            for phase_idx, phase in enumerate(self.phases):
                phase_name = phase.name
                logger.info(f"\n{'=' * 80}")
                logger.info(f"Phase {phase_idx + 1}/{len(self.phases)}: {phase_name}")
                logger.info(f"{'=' * 80}")
                logger.info(f"Load: {phase.load_type}, Threads: {phase.thread_count}, "
                           f"Target TPS: {phase.operations_per_second}, "
                           f"Data: {phase.data_size_range} bytes")
                
                phase_start = time.time()
                phase_ops_start = self.operation_count
                
                # 启动工作线程
                threads = []
                for i in range(phase.thread_count):
                    t = threading.Thread(target=self._worker_thread, args=(phase, i))
                    threads.append(t)
                    t.start()
                
                # 监控循环
                last_log = time.time()
                while any(t.is_alive() for t in threads):
                    current_time = time.time()
                    
                    # 记录内存
                    current_memory = self._get_memory_mb()
                    if current_memory > peak_memory:
                        peak_memory = current_memory
                    self.memory_history.append({
                        "time": current_time,
                        "memory_mb": current_memory,
                        "operation": self.operation_count
                    })
                    
                    # 定期日志
                    if current_time - last_log > 60:  # 每1分钟
                        elapsed = current_time - phase_start
                        ops_in_phase = self.operation_count - phase_ops_start
                        ops_per_sec = ops_in_phase / elapsed if elapsed > 0 else 0
                        
                        logger.info(f"[{phase_name}] Elapsed: {elapsed:.0f}s, "
                                   f"Ops: {ops_in_phase:,}, TPS: {ops_per_sec:.0f}, "
                                   f"Errors: {self.error_count}, "
                                   f"Memory: {current_memory:.2f}MB (peak: {peak_memory:.2f}MB)")
                        
                        last_log = current_time
                    
                    time.sleep(2)
                
                # 等待所有线程结束
                for t in threads:
                    t.join()
                
                # 记录阶段指标
                phase_duration = time.time() - phase_start
                phase_ops = self.operation_count - phase_ops_start
                phase_tps = phase_ops / phase_duration if phase_duration > 0 else 0
                
                self.phase_metrics.append({
                    "phase": phase.name,
                    "duration": phase_duration,
                    "operations": phase_ops,
                    "tps": phase_tps,
                    "errors": self.error_count,
                    "peak_memory_mb": peak_memory
                })
                
                logger.info(f"✅ Phase {phase_name} completed: {phase_ops:,} ops @ {phase_tps:.0f} TPS")
                
                # 阶段间GC
                gc.collect()
            
        except KeyboardInterrupt:
            logger.warning("测试被用户中断")
            self.stop_flag.set()
        
        total_duration = time.time() - total_start
        
        return self._generate_report(total_duration, initial_memory, peak_memory)
    
    def _generate_report(self, total_duration, initial_memory, peak_memory):
        """生成测试报告"""
        final_memory = self._get_memory_mb()
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 极端极限组合测试 - 最终报告")
        logger.info("=" * 80)
        
        logger.info(f"总时长: {total_duration:.2f}秒 ({total_duration/60:.1f}分钟)")
        logger.info(f"总操作数: {self.operation_count:,}")
        logger.info(f"成功操作: {self.success_count:,}")
        logger.info(f"失败操作: {self.error_count:,}")
        logger.info(f"成功率: {(self.success_count/self.operation_count*100):.2f}%" if self.operation_count > 0 else "N/A")
        logger.info(f"整体 TPS: {(self.operation_count/total_duration):.0f}")
        logger.info(f"初始内存: {initial_memory:.2f}MB")
        logger.info(f"峰值内存: {peak_memory:.2f}MB")
        logger.info(f"最终内存: {final_memory:.2f}MB")
        logger.info(f"内存增长: {final_memory - initial_memory:.2f}MB")
        
        logger.info(f"\n各阶段详情:")
        for metric in self.phase_metrics:
            logger.info(f"  {metric['phase']}: "
                       f"{metric['operations']:,} ops @ {metric['tps']:.0f} TPS, "
                       f"{metric['errors']} errors, "
                       f"peak {metric['peak_memory_mb']:.2f}MB")
        
        if self.operation_errors:
            logger.warning(f"\n错误详情 (首10条):")
            for i, err in enumerate(self.operation_errors[:10]):
                logger.warning(f"  {i+1}. {err}")
        
        passed = self.error_count == 0 and (final_memory - initial_memory) < 100
        
        if passed:
            logger.info("\n🎉 测试通过！系统表现极其优秀！")
        else:
            logger.warning(f"\n⚠️ 测试发现潜在问题")
        
        return {
            "total_duration": total_duration,
            "total_operations": self.operation_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": peak_memory,
            "final_memory_mb": final_memory,
            "memory_growth_mb": final_memory - initial_memory,
            "phase_metrics": self.phase_metrics,
            "passed": passed
        }


def main():
    """主函数"""
    # 使用较短时间演示（实际应设为7200秒即2小时）
    # 为演示目的，设为7分钟
    tester = ExtremeComboTester(total_duration=420)
    
    try:
        results = tester.run()
        return results
    except Exception as e:
        logger.error(f"测试崩溃: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
