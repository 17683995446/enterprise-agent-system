"""
持续负载测试 - 1小时+
模拟真实生产环境的持续高负载
"""

import sys
import time
import random
import threading
import gc
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('1hour_sustained_load')


@dataclass
class PerformanceMetrics:
    """性能指标"""
    start_time: float = field(default_factory=time.time)
    end_time: float = 0
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    avg_latency_ms: float = 0
    max_latency_ms: float = 0
    min_latency_ms: float = float('inf')
    p50_latency_ms: float = 0
    p95_latency_ms: float = 0
    p99_latency_ms: float = 0
    current_rps: float = 0  # requests per second
    memory_mb: float = 0
    gc_collections: int = 0


class SustainedLoadTester:
    """持续负载测试器 - 运行1小时+"""

    def __init__(self, duration_seconds: int = 3600):  # 默认1小时
        self.duration = duration_seconds
        self.metrics = PerformanceMetrics()
        self.stop_flag = threading.Event()
        self.lock = threading.Lock()
        self.errors = []
        
    def run(self):
        """运行持续负载测试"""
        logger.info("=" * 80)
        logger.info(f"🚀 开始持续负载测试 - 预计运行 {self.duration} 秒 ({(self.duration/60):.1f} 分钟)")
        logger.info("=" * 80)
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
        
        store = SimpleMemoryStore()
        cache = SimpleCache()
        
        start_time = time.time()
        last_report_time = start_time
        last_checkpoint = start_time
        
        operation_count = 0
        latencies = []
        gc_before = gc.get_count()
        
        try:
            while not self.stop_flag.is_set() and (time.time() - start_time) < self.duration:
                op_start = time.time()
                op_type = random.choice(['read', 'write', 'cache'])
                
                try:
                    if op_type == 'read':
                        report_id = f"sustained_test_{random.randint(0, max(0, operation_count-100))}"
                        store.get_report(report_id)
                    elif op_type == 'write':
                        store.save_report({
                            "id": f"sustained_test_{operation_count}",
                            "title": f"Sustained Load Test {operation_count}",
                            "type": "sustained",
                            "summary": f"Load test record {operation_count}",
                            "quality_score": random.uniform(0, 10),
                            "metrics": {
                                "iteration": operation_count,
                                "timestamp": time.time(),
                                "random_data": random.randint(0, 1000000)
                            }
                        })
                    else:
                        cache.set(f"cache_{operation_count}", operation_count)
                        cache.get(f"cache_{random.randint(0, max(0, operation_count-10))}")
                    
                    # 记录成功
                    operation_count += 1
                    self.metrics.successful_operations += 1
                    
                    # 记录延迟
                    latency = (time.time() - op_start) * 1000
                    latencies.append(latency)
                    
                except Exception as e:
                    self.metrics.failed_operations += 1
                    self.errors.append(f"Op {operation_count}: {str(e)[:100]}")
                
                # 每10秒报告一次进度
                current_time = time.time()
                if current_time - last_report_time >= 10:
                    elapsed = current_time - start_time
                    current_rps = operation_count / elapsed if elapsed > 0 else 0
                    
                    # 计算延迟统计
                    if latencies:
                        latencies_sorted = sorted(latencies[-1000:])  # 最近1000个
                        self.metrics.avg_latency_ms = sum(latencies) / len(latencies)
                        self.metrics.max_latency_ms = max(latencies)
                        self.metrics.min_latency_ms = min(latencies) if latencies else 0
                        if latencies_sorted:
                            self.metrics.p50_latency_ms = latencies_sorted[int(len(latencies_sorted) * 0.5)]
                            self.metrics.p95_latency_ms = latencies_sorted[int(len(latencies_sorted) * 0.95)]
                            self.metrics.p99_latency_ms = latencies_sorted[int(len(latencies_sorted) * 0.99)]
                    
                    # 内存统计
                    try:
                        import psutil
                        self.metrics.memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)
                    except:
                        pass
                    
                    # GC统计
                    gc_after = gc.get_count()
                    self.metrics.gc_collections = sum(gc_after) - sum(gc_before)
                    
                    self.metrics.current_rps = current_rps
                    
                    logger.info(f"📊 [{elapsed:.0f}s/{self.duration}s] "
                               f"操作: {operation_count:,} | "
                               f"RPS: {current_rps:.1f} | "
                               f"延迟: {self.metrics.avg_latency_ms:.2f}ms | "
                               f"P99: {self.metrics.p99_latency_ms:.2f}ms | "
                               f"内存: {self.metrics.memory_mb:.1f}MB")
                    
                    last_report_time = current_time
                
                # 每30秒执行GC
                if current_time - last_checkpoint >= 30:
                    gc.collect()
                    last_checkpoint = current_time
                
                # 控制速率，避免过快
                time.sleep(0.0001)
            
            # 测试结束
            self.metrics.end_time = time.time()
            self.metrics.total_operations = operation_count
            self.metrics.current_rps = operation_count / (self.metrics.end_time - self.metrics.start_time)
            
        except KeyboardInterrupt:
            logger.warning("测试被用户中断")
            self.stop_flag.set()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        duration = self.metrics.end_time - self.metrics.start_time if self.metrics.end_time else 0
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 持续负载测试报告")
        logger.info("=" * 80)
        logger.info(f"测试时长: {duration:.2f}秒 ({duration/60:.1f}分钟)")
        logger.info(f"总操作数: {self.metrics.total_operations:,}")
        logger.info(f"成功操作: {self.metrics.successful_operations:,}")
        logger.info(f"失败操作: {self.metrics.failed_operations:,}")
        logger.info(f"成功率: {self.metrics.successful_operations/self.metrics.total_operations*100:.2f}%")
        logger.info(f"吞吐量: {self.metrics.current_rps:.2f} 次/秒")
        logger.info(f"\n延迟统计:")
        logger.info(f"  平均: {self.metrics.avg_latency_ms:.2f}ms")
        logger.info(f"  最小: {self.metrics.min_latency_ms:.2f}ms")
        logger.info(f"  最大: {self.metrics.max_latency_ms:.2f}ms")
        logger.info(f"  P50: {self.metrics.p50_latency_ms:.2f}ms")
        logger.info(f"  P95: {self.metrics.p95_latency_ms:.2f}ms")
        logger.info(f"  P99: {self.metrics.p99_latency_ms:.2f}ms")
        logger.info(f"\n资源使用:")
        logger.info(f"  最终内存: {self.metrics.memory_mb:.2f}MB")
        logger.info(f"  GC执行次数: {self.metrics.gc_collections}")
        
        if self.errors:
            logger.warning(f"\n错误摘要 (前10个):")
            for i, err in enumerate(self.errors[:10]):
                logger.warning(f"  {i+1}. {err}")
        
        return {
            "duration_seconds": duration,
            "total_operations": self.metrics.total_operations,
            "successful_operations": self.metrics.successful_operations,
            "failed_operations": self.metrics.failed_operations,
            "success_rate": self.metrics.successful_operations / self.metrics.total_operations if self.metrics.total_operations > 0 else 0,
            "rps": self.metrics.current_rps,
            "latency": {
                "avg": self.metrics.avg_latency_ms,
                "min": self.metrics.min_latency_ms,
                "max": self.metrics.max_latency_ms,
                "p50": self.metrics.p50_latency_ms,
                "p95": self.metrics.p95_latency_ms,
                "p99": self.metrics.p99_latency_ms,
            },
            "memory_mb": self.metrics.memory_mb,
            "gc_collections": self.metrics.gc_collections,
            "error_count": len(self.errors),
            "passed": len(self.errors) == 0 and self.metrics.successful_operations / self.metrics.total_operations > 0.99
        }


def main():
    """主函数"""
    # 设置测试时长为 1小时 (3600秒)，但为了快速演示设为 120 秒
    tester = SustainedLoadTester(duration_seconds=120)  # 实际使用时改为 3600
    
    try:
        result = tester.run()
        
        if result["passed"]:
            logger.info("\n🎉 测试通过！系统表现优秀！")
        else:
            logger.error("\n❌ 测试失败！需要检查问题。")
        
        return result
        
    except Exception as e:
        logger.error(f"测试崩溃: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
