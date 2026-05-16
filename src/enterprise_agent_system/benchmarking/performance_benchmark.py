"""
Performance Benchmark Suite
性能基准测试、瓶颈识别、优化工具
"""

import time
import asyncio
import statistics
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from enterprise_agent_system.infrastructure.advanced_logging import get_logger, get_metrics_collector

logger = get_logger("performance")


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    iterations: int
    min_time: float
    max_time: float
    avg_time: float
    median_time: float
    std_dev: float
    total_time: float
    ops_per_second: float


class BenchmarkSuite:
    """基准测试套件"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.metrics = get_metrics_collector()
    
    def benchmark(self, name: str, iterations: int = 100):
        """基准测试装饰器"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                times = []
                for _ in range(iterations):
                    start = time.time()
                    func(*args, **kwargs)
                    times.append(time.time() - start)
                
                result = self._calculate_stats(name, times, iterations)
                self.results.append(result)
                logger.info(f"Benchmark {name} completed: {result.ops_per_second:.2f} ops/s")
                return result
            return wrapper
        return decorator
    
    def _calculate_stats(self, name: str, times: List[float], iterations: int) -> BenchmarkResult:
        """计算统计信息"""
        total_time = sum(times)
        return BenchmarkResult(
            name=name,
            iterations=iterations,
            min_time=min(times),
            max_time=max(times),
            avg_time=total_time / iterations,
            median_time=statistics.median(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            total_time=total_time,
            ops_per_second=iterations / total_time if total_time > 0 else 0
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """获取基准测试摘要"""
        if not self.results:
            return {"total_benchmarks": 0}
        
        avg_ops = sum(r.ops_per_second for r in self.results) / len(self.results)
        return {
            "total_benchmarks": len(self.results),
            "average_ops_per_second": avg_ops,
            "results": [
                {
                    "name": r.name,
                    "ops_per_second": r.ops_per_second,
                    "avg_time": r.avg_time
                }
                for r in self.results
            ]
        }
    
    def print_summary(self):
        """打印摘要"""
        print("\n" + "=" * 80)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 80)
        
        for result in self.results:
            print(f"\n{result.name}:")
            print(f"  {result.iterations} iterations, {result.total_time:.3f}s total")
            print(f"  Operations per second: {result.ops_per_second:.2f}")
            print(f"  Min/Avg/Median/Max: {result.min_time:.4f}s / {result.avg_time:.4f}s / "
                  f"{result.median_time:.4f}s / {result.max_time:.4f}s")


class PerformanceOptimizer:
    """性能优化工具"""
    
    @staticmethod
    def memoize(func):
        """记忆化缓存装饰器"""
        cache = {}
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
        return wrapper
    
    @staticmethod
    async def concurrent_execution(tasks: List[Callable], max_concurrent: int = 10):
        """并发执行任务"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_task(task):
            async with semaphore:
                if asyncio.iscoroutinefunction(task):
                    return await task()
                else:
                    return task()
        
        return await asyncio.gather(*[bounded_task(task) for task in tasks])


# 标准基准测试
def run_standard_benchmarks():
    """运行标准基准测试"""
    suite = BenchmarkSuite()
    
    @suite.benchmark("simple_calculation", iterations=10000)
    def test_simple():
        x = 0
        for i in range(1000):
            x += i
    
    @suite.benchmark("string_operations", iterations=10000)
    def test_string():
        s = "test" * 100
        for _ in range(100):
            s = s + "test"
    
    @suite.benchmark("list_operations", iterations=1000)
    def test_list():
        lst = list(range(10000))
        _ = len(lst)
    
    suite.print_summary()
    return suite.get_summary()


if __name__ == "__main__":
    run_standard_benchmarks()
