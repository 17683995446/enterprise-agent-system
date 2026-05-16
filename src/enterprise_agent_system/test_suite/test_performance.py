"""
Performance Tests for Enterprise Agent System
Test Suite Layer - 性能测试
"""

import pytest
import time
from typing import Callable, List, Dict, Any
from dataclasses import dataclass
from test_coverage_optimization import (
    TaskFactory,
    AgentFactory,
    MemoryFactory,
    PerformanceMonitor,
    Assertions,
)


@dataclass
class PerformanceBenchmark:
    """性能基准"""
    name: str
    target_duration: float
    actual_duration: float
    passed: bool
    metadata: Dict[str, Any]


class PerformanceBenchmarkSuite:
    """性能基准测试套件"""
    
    def __init__(self):
        self.benchmarks: List[PerformanceBenchmark] = []
        self.monitor = PerformanceMonitor()
    
    def run_benchmark(
        self,
        name: str,
        func: Callable,
        target_duration: float = 1.0,
        iterations: int = 1,
        **kwargs
    ) -> PerformanceBenchmark:
        """运行性能基准"""
        durations = []
        
        for _ in range(iterations):
            result, duration = self.monitor.measure(func, **kwargs)
            durations.append(duration)
        
        actual_duration = sum(durations) / len(durations) if iterations > 1 else durations[0]
        
        benchmark = PerformanceBenchmark(
            name=name,
            target_duration=target_duration,
            actual_duration=actual_duration,
            passed=actual_duration < target_duration,
            metadata={
                "iterations": iterations,
                "min_duration": min(durations),
                "max_duration": max(durations),
            }
        )
        
        self.benchmarks.append(benchmark)
        return benchmark
    
    def get_summary(self) -> Dict[str, Any]:
        """获取总结"""
        total = len(self.benchmarks)
        passed = sum(1 for b in self.benchmarks if b.passed)
        failed = total - passed
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            "benchmarks": [
                {
                    "name": b.name,
                    "target": b.target_duration,
                    "actual": b.actual_duration,
                    "passed": b.passed,
                }
                for b in self.benchmarks
            ],
        }


@pytest.mark.performance
class TestTaskPerformance:
    """任务性能测试"""
    
    @pytest.mark.asyncio
    async def test_task_creation_speed(self):
        """测试任务创建速度"""
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Task Creation",
            func=lambda: TaskFactory.create_task(),
            target_duration=0.01,  # 10ms
            iterations=100,
        )
        
        assert benchmark.passed, f"Task creation too slow: {benchmark.actual_duration}s"
    
    @pytest.mark.asyncio
    async def test_task_batch_creation_speed(self):
        """测试批量任务创建速度"""
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Batch Task Creation (100 tasks)",
            func=lambda: TaskFactory.create_batch(100),
            target_duration=0.1,  # 100ms
            iterations=10,
        )
        
        assert benchmark.passed, f"Batch creation too slow: {benchmark.actual_duration}s"
    
    @pytest.mark.asyncio
    async def test_task_validation_speed(self):
        """测试任务验证速度"""
        task = TaskFactory.create_task()
        
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Task Validation",
            func=lambda: Assertions.assert_task_valid(task),
            target_duration=0.001,  # 1ms
            iterations=1000,
        )
        
        assert benchmark.passed


@pytest.mark.performance
class TestAgentPerformance:
    """Agent性能测试"""
    
    @pytest.mark.asyncio
    async def test_agent_creation_speed(self):
        """测试Agent创建速度"""
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Agent Creation",
            func=lambda: AgentFactory.create_agent(),
            target_duration=0.01,  # 10ms
            iterations=100,
        )
        
        assert benchmark.passed
    
    @pytest.mark.asyncio
    async def test_agent_batch_creation_speed(self):
        """测试批量Agent创建速度"""
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Batch Agent Creation (50 agents)",
            func=lambda: AgentFactory.create_batch(50),
            target_duration=0.1,  # 100ms
            iterations=10,
        )
        
        assert benchmark.passed


@pytest.mark.performance
class TestMemoryPerformance:
    """记忆性能测试"""
    
    @pytest.mark.asyncio
    async def test_memory_creation_speed(self):
        """测试记忆创建速度"""
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Memory Creation",
            func=lambda: MemoryFactory.create_memory(),
            target_duration=0.01,  # 10ms
            iterations=100,
        )
        
        assert benchmark.passed
    
    @pytest.mark.asyncio
    async def test_memory_batch_creation_speed(self):
        """测试批量记忆创建速度"""
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Batch Memory Creation (100 memories)",
            func=lambda: MemoryFactory.create_batch(100),
            target_duration=0.1,  # 100ms
            iterations=10,
        )
        
        assert benchmark.passed


@pytest.mark.performance
class TestDataGeneratorPerformance:
    """数据生成器性能测试"""
    
    @pytest.mark.asyncio
    async def test_unique_id_generation_speed(self):
        """测试唯一ID生成速度"""
        from test_coverage_optimization import TestDataGenerator
        
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Unique ID Generation (1000 IDs)",
            func=lambda: [TestDataGenerator.generate_unique_id() for _ in range(1000)],
            target_duration=0.5,  # 500ms
            iterations=10,
        )
        
        assert benchmark.passed
    
    @pytest.mark.asyncio
    async def test_text_generation_speed(self):
        """测试文本生成速度"""
        from test_coverage_optimization import TestDataGenerator
        
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Text Generation (1000 texts, 100 chars each)",
            func=lambda: [TestDataGenerator.generate_text(100) for _ in range(1000)],
            target_duration=0.1,  # 100ms
            iterations=10,
        )
        
        assert benchmark.passed


@pytest.mark.performance
class TestMockPerformance:
    """Mock性能测试"""
    
    @pytest.mark.asyncio
    async def test_mock_redis_operations(self):
        """测试Mock Redis操作性能"""
        from test_coverage_optimization import MockRedisClient
        
        redis_client = MockRedisClient()
        
        # 准备数据
        for i in range(1000):
            redis_client.set(f"key{i}", f"value{i}")
        
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Mock Redis Read (1000 operations)",
            func=lambda: [redis_client.get(f"key{i}") for i in range(1000)],
            target_duration=0.1,  # 100ms
            iterations=5,
        )
        
        assert benchmark.passed
    
    @pytest.mark.asyncio
    async def test_mock_celery_task_submission(self):
        """测试Mock Celery任务提交性能"""
        from test_coverage_optimization import MockCeleryTask
        
        celery = MockCeleryTask()
        
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Mock Celery Task Submission (100 tasks)",
            func=lambda: [celery.apply_async(kwargs={"id": i}) for i in range(100)],
            target_duration=0.1,  # 100ms
            iterations=5,
        )
        
        assert benchmark.passed


@pytest.mark.performance
class TestAssertionPerformance:
    """断言性能测试"""
    
    @pytest.mark.asyncio
    async def test_task_assertion_performance(self):
        """测试任务断言性能"""
        task = TaskFactory.create_task()
        
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Task Assertion (10000 times)",
            func=lambda: Assertions.assert_task_valid(task),
            target_duration=0.5,  # 500ms
            iterations=1,
        )
        
        assert benchmark.passed
    
    @pytest.mark.asyncio
    async def test_agent_assertion_performance(self):
        """测试Agent断言性能"""
        agent = AgentFactory.create_agent()
        
        benchmark_suite = PerformanceBenchmarkSuite()
        
        benchmark = benchmark_suite.run_benchmark(
            name="Agent Assertion (10000 times)",
            func=lambda: Assertions.assert_agent_valid(agent),
            target_duration=0.5,  # 500ms
            iterations=1,
        )
        
        assert benchmark.passed


# ==================== 导出 ====================

__all__ = [
    "PerformanceBenchmark",
    "PerformanceBenchmarkSuite",
    "TestTaskPerformance",
    "TestAgentPerformance",
    "TestMemoryPerformance",
    "TestDataGeneratorPerformance",
    "TestMockPerformance",
    "TestAssertionPerformance",
]
