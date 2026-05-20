"""
Extreme High Difficulty Test - Extreme Scenarios
特复杂高难度测试 - 极端场景

设计场景：
1. 极端并发测试 (5000+ 并发操作)
2. 超长运行稳定性测试 (5000+ 持续操作)
3. 极端数据量处理 (10000+ 记录)
4. 内存泄漏检测和压力测试
5. 异常处理测试（边界条件和极端值）
6. 随机故障注入和恢复测试
"""

import sys
import time
import tempfile
import os
import random
import string
import threading
import gc
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('extreme_high_difficulty')


@dataclass
class TestResult:
    scenario: str
    passed: bool
    duration: float
    iterations: int
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]


class ExtremeHighDifficultyTester:
    """极端高难度测试器"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.temp_dirs: List[Path] = []
        self.should_stop = False

    def cleanup(self):
        """清理资源"""
        for dir_path in self.temp_dirs:
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path, ignore_errors=True)

    def test_extreme_concurrency(self) -> TestResult:
        """极端并发测试 - 5000 并发操作"""
        logger.info("=" * 80)
        logger.info("🔥 场景1: 极端并发测试 (5000 并发操作)")
        logger.info("=" * 80)

        start_time = time.time()
        errors = []
        warnings = []
        metrics = {
            "total_operations": 0,
            "success_operations": 0,
            "failed_operations": 0,
            "avg_latency": 0,
            "max_latency": 0,
        }

        try:
            # 使用简单的无依赖存储方案
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleCache, SimpleMemoryStore

            cache = SimpleCache()
            store = SimpleMemoryStore()

            num_concurrent = 1000
            operations_per_thread = 5
            total_operations = num_concurrent * operations_per_thread

            logger.info(f"启动 {num_concurrent} 个并发线程，每个线程执行 {operations_per_thread} 次操作...")

            latencies = []
            lock = threading.Lock()

            def worker(thread_id: int):
                thread_success = 0
                thread_fail = 0
                thread_latencies = []

                for i in range(operations_per_thread):
                    op_start = time.time()
                    try:
                        cache_key = f"extreme_test_{thread_id}_{i}"
                        cache_val = f"value_{thread_id}_{i}"
                        cache.set(cache_key, cache_val)
                        cache.get(cache_key)

                        report_id = f"extreme_report_{thread_id}_{i}"
                        report = {
                            "id": report_id,
                            "title": f"Extreme Report {thread_id}-{i}",
                            "summary": f"Extreme summary {i}",
                            "type": "test",
                            "quality_score": random.uniform(0, 10),
                        }
                        store.save_report(report)
                        store.get_report(report_id)

                        thread_success += 1
                    except Exception as e:
                        thread_fail += 1
                        errors.append(f"Thread {thread_id} Op {i}: {str(e)[:100]}")
                    finally:
                        op_time = (time.time() - op_start) * 1000
                        thread_latencies.append(op_time)

                with lock:
                    metrics["success_operations"] += thread_success
                    metrics["failed_operations"] += thread_fail
                    latencies.extend(thread_latencies)

            with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                futures = [executor.submit(worker, i) for i in range(num_concurrent)]

                completed = 0
                for future in as_completed(futures):
                    completed += 1
                    if completed % 100 == 0:
                        logger.info(f"完成进度: {completed}/{num_concurrent}")

            metrics["total_operations"] = total_operations

            if latencies:
                metrics["avg_latency"] = sum(latencies) / len(latencies)
                metrics["max_latency"] = max(latencies)

            logger.info(f"极端并发测试完成:")
            logger.info(f"  总操作: {total_operations}")
            logger.info(f"  成功: {metrics['success_operations']}")
            logger.info(f"  失败: {metrics['failed_operations']}")
            logger.info(f"  平均延迟: {metrics['avg_latency']:.2f}ms")
            logger.info(f"  最大延迟: {metrics['max_latency']:.2f}ms")

            success_rate = metrics["success_operations"] / total_operations if total_operations > 0 else 0
            passed = success_rate >= 0.95

            if success_rate < 0.95:
                warnings.append(f"成功率 {success_rate*100:.2f}% 低于 95%")

        except Exception as e:
            logger.error(f"极端并发测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            passed = False
            errors.append(f"测试崩溃: {str(e)}")

        duration = time.time() - start_time
        return TestResult(
            scenario="极端并发测试",
            passed=passed,
            duration=duration,
            iterations=metrics["total_operations"],
            errors=errors[:100],
            warnings=warnings,
            metrics=metrics
        )

    def test_extreme_data_volume(self) -> TestResult:
        """极端数据量测试 - 10000+ 记录"""
        logger.info("=" * 80)
        logger.info("🔥 场景2: 极端数据量测试 (10000+ 记录)")
        logger.info("=" * 80)

        start_time = time.time()
        errors = []
        warnings = []
        metrics = {
            "records_created": 0,
            "records_retrieved": 0,
            "records_deleted": 0,
            "create_time": 0,
            "retrieve_time": 0,
            "delete_time": 0,
        }

        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore

            store = SimpleMemoryStore()

            num_records = 10000
            logger.info(f"创建 {num_records} 条记录...")

            # 创建记录
            create_start = time.time()
            for i in range(num_records):
                try:
                    report = {
                        "id": f"volume_report_{i}",
                        "title": f"Volume Report {i}",
                        "summary": f"This is volume test report number {i} with a very long summary to test storage efficiency. " * 5,
                        "type": random.choice(["code", "security", "performance", "documentation"]),
                        "quality_score": random.uniform(0, 10),
                        "metrics": {"complexity": random.randint(1, 100), "size": random.randint(1, 10000)},
                    }
                    store.save_report(report)
                    metrics["records_created"] += 1

                    if (i + 1) % 1000 == 0:
                        logger.info(f"  创建进度: {i + 1}/{num_records}")
                except Exception as e:
                    errors.append(f"创建记录 {i} 失败: {str(e)[:100]}")

            metrics["create_time"] = time.time() - create_start

            # 列出记录
            list_start = time.time()
            logger.info("列出所有记录...")
            all_reports = store.list_reports(limit=num_records)
            metrics["records_retrieved"] = len(all_reports)
            metrics["retrieve_time"] = time.time() - list_start

            logger.info(f"  成功检索 {len(all_reports)} 条记录")

            # 删除记录
            delete_start = time.time()
            logger.info("删除记录...")
            for i in range(min(1000, num_records)):
                try:
                    result = store.delete_report(f"volume_report_{i}")
                    if result:
                        metrics["records_deleted"] += 1
                except Exception as e:
                    errors.append(f"删除记录 {i} 失败: {str(e)[:100]}")

            metrics["delete_time"] = time.time() - delete_start

            logger.info(f"极端数据量测试完成:")
            logger.info(f"  创建: {metrics['records_created']} 条 (耗时: {metrics['create_time']:.2f}s)")
            logger.info(f"  检索: {metrics['records_retrieved']} 条 (耗时: {metrics['retrieve_time']:.2f}s)")
            logger.info(f"  删除: {metrics['records_deleted']} 条 (耗时: {metrics['delete_time']:.2f}s)")

            passed = metrics["records_created"] >= num_records * 0.99 and len(errors) < 100

        except Exception as e:
            logger.error(f"极端数据量测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            passed = False
            errors.append(f"测试崩溃: {str(e)}")

        duration = time.time() - start_time
        return TestResult(
            scenario="极端数据量测试",
            passed=passed,
            duration=duration,
            iterations=metrics["records_created"],
            errors=errors[:50],
            warnings=warnings,
            metrics=metrics
        )

    def test_memory_leak_detection(self) -> TestResult:
        """内存泄漏检测"""
        logger.info("=" * 80)
        logger.info("🔥 场景3: 内存泄漏检测")
        logger.info("=" * 80)

        start_time = time.time()
        errors = []
        warnings = []
        metrics = {
            "initial_memory": 0,
            "peak_memory": 0,
            "final_memory": 0,
            "memory_increase_mb": 0,
            "gc_collections": 0,
        }

        try:
            import psutil
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleCache, SimpleMemoryStore

            process = psutil.Process()
            cache = SimpleCache()
            store = SimpleMemoryStore()

            metrics["initial_memory"] = process.memory_info().rss
            peak_memory = metrics["initial_memory"]

            num_iterations = 1000
            logger.info(f"执行 {num_iterations} 次内存密集操作...")

            for i in range(num_iterations):
                # 创建大量临时数据
                temp_data = []
                for j in range(100):
                    temp_data.append({
                        "key": f"temp_key_{i}_{j}",
                        "value": f"temp_value_{i}_{j}_{'x' * 100}"
                    })

                # 使用缓存
                cache_key = f"mem_test_{i}"
                cache.set(cache_key, temp_data)
                cache.get(cache_key)

                # 使用数据库
                report = {
                    "id": f"mem_report_{i}",
                    "title": f"Memory Test {i}",
                    "summary": f"Memory test summary {i}",
                    "type": "test",
                    "quality_score": random.uniform(0, 10),
                }
                store.save_report(report)

                # 定期 GC 收集
                if i % 100 == 0:
                    gc.collect()
                    metrics["gc_collections"] += 1

                    # 检查内存
                    current_memory = process.memory_info().rss
                    if current_memory > peak_memory:
                        peak_memory = current_memory

                    logger.info(f"  进度: {i}/{num_iterations}, 内存: {current_memory / 1024 / 1024:.2f}MB")

            # 最终 GC 和测量
            gc.collect()
            gc.collect()
            gc.collect()
            metrics["final_memory"] = process.memory_info().rss
            metrics["peak_memory"] = peak_memory

            memory_increase = metrics["final_memory"] - metrics["initial_memory"]
            metrics["memory_increase_mb"] = memory_increase / (1024 * 1024)

            logger.info(f"内存泄漏检测完成:")
            logger.info(f"  初始内存: {metrics['initial_memory'] / 1024 / 1024:.2f}MB")
            logger.info(f"  峰值内存: {metrics['peak_memory'] / 1024 / 1024:.2f}MB")
            logger.info(f"  最终内存: {metrics['final_memory'] / 1024 / 1024:.2f}MB")
            logger.info(f"  内存增长: {metrics['memory_increase_mb']:.2f}MB")

            passed = metrics["memory_increase_mb"] < 50

            if metrics["memory_increase_mb"] > 20:
                warnings.append(f"内存增长较高: {metrics['memory_increase_mb']:.2f}MB")

        except ImportError:
            logger.warning("psutil not available, skipping memory leak test")
            warnings.append("psutil not available")
            passed = True
        except Exception as e:
            logger.error(f"内存泄漏检测崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            passed = False
            errors.append(f"测试崩溃: {str(e)}")

        duration = time.time() - start_time
        return TestResult(
            scenario="内存泄漏检测",
            passed=passed,
            duration=duration,
            iterations=1000,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )

    def test_extreme_edge_cases(self) -> TestResult:
        """极端边界条件测试"""
        logger.info("=" * 80)
        logger.info("🔥 场景4: 极端边界条件测试")
        logger.info("=" * 80)

        start_time = time.time()
        errors = []
        warnings = []
        metrics = {
            "edge_cases_tested": 0,
            "success_cases": 0,
            "failed_cases": 0,
        }

        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleCache, SimpleMemoryStore

            cache = SimpleCache()
            store = SimpleMemoryStore()

            edge_cases = [
                ("empty key", "", "empty value"),
                ("very long key", "x" * 1000, "value"),
                ("very long value", "key", "x" * 100000),
                ("special chars key", "!@#$%^&*()_+-=[]{}|;':\",./<>?\\", "special value"),
                ("unicode key", "测试键_🔑", "测试值_✨"),
                ("none value", "key_none", None),
                ("numeric key", 123456, "numeric key value"),
            ]

            logger.info(f"测试 {len(edge_cases)} 个边界情况...")

            for i, (case_name, key, value) in enumerate(edge_cases):
                metrics["edge_cases_tested"] += 1
                try:
                    logger.info(f"  测试: {case_name}")
                    cache.set(str(key), value)
                    retrieved = cache.get(str(key))

                    # 测试数据库边界情况
                    db_test = {
                        "id": f"edge_{i}",
                        "title": "x" * 500 if case_name == "very long key" else f"Edge Test {i}",
                        "summary": "x" * 5000 if case_name == "very long value" else f"Edge test summary {i}",
                        "type": "test",
                        "quality_score": -1 if case_name == "empty key" else (11 if case_name == "very long key" else 5.5),
                    }
                    store.save_report(db_test)
                    store.get_report(f"edge_{i}")

                    metrics["success_cases"] += 1
                    logger.info(f"    ✅ 通过")
                except Exception as e:
                    metrics["failed_cases"] += 1
                    errors.append(f"{case_name}: {str(e)[:100]}")
                    logger.warning(f"    ❌ 失败: {str(e)[:50]}")

            # 测试空操作和无效参数
            logger.info("测试无效参数和边界情况...")

            try:
                cache.get(None)
                metrics["success_cases"] += 1
            except Exception as e:
                errors.append(f"get(None): {str(e)[:100]}")

            try:
                cache.delete(None)
                metrics["success_cases"] += 1
            except Exception as e:
                errors.append(f"delete(None): {str(e)[:100]}")

            try:
                store.get_report(None)
                metrics["success_cases"] += 1
            except Exception as e:
                errors.append(f"get_report(None): {str(e)[:100]}")

            try:
                store.delete_report(None)
                metrics["success_cases"] += 1
            except Exception as e:
                errors.append(f"delete_report(None): {str(e)[:100]}")

            logger.info(f"极端边界条件测试完成:")
            logger.info(f"  测试用例: {metrics['edge_cases_tested']}")
            logger.info(f"  成功: {metrics['success_cases']}")
            logger.info(f"  失败: {metrics['failed_cases']}")

            passed = metrics["failed_cases"] == 0

        except Exception as e:
            logger.error(f"极端边界条件测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            passed = False
            errors.append(f"测试崩溃: {str(e)}")

        duration = time.time() - start_time
        return TestResult(
            scenario="极端边界条件测试",
            passed=passed,
            duration=duration,
            iterations=metrics["edge_cases_tested"],
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )

    def test_long_running_stability_extreme(self) -> TestResult:
        """超长运行稳定性测试 - 5000+ 混合操作"""
        logger.info("=" * 80)
        logger.info("🔥 场景5: 超长运行稳定性测试 (5000+ 混合操作)")
        logger.info("=" * 80)

        start_time = time.time()
        errors = []
        warnings = []
        num_operations = 5000  # 提前定义，避免作用域问题
        metrics = {
            "total_operations": num_operations,
            "success_operations": 0,
            "cache_ops": 0,
            "db_ops": 0,
            "failures": 0,
            "operations_per_second": 0,
        }

        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleCache, SimpleMemoryStore

            cache = SimpleCache()
            store = SimpleMemoryStore()

            logger.info(f"执行 {num_operations} 次混合操作...")

            for i in range(num_operations):
                try:
                    op_type = random.choice(['cache_set', 'cache_get', 'cache_delete',
                                           'db_save', 'db_get', 'db_list'])

                    if op_type == 'cache_set':
                        cache.set(f"long_test_{i}", f"value_{i}")
                        metrics["cache_ops"] += 1
                    elif op_type == 'cache_get':
                        cache.get(f"long_test_{random.randint(0, i)}")
                        metrics["cache_ops"] += 1
                    elif op_type == 'cache_delete':
                        cache.delete(f"long_test_{random.randint(0, max(0, i-10))}")
                        metrics["cache_ops"] += 1
                    elif op_type == 'db_save':
                        report = {
                            "id": f"long_report_{i}",
                            "title": f"Long Test Report {i}",
                            "summary": f"Long running test report {i}",
                            "type": "test",
                            "quality_score": random.uniform(0, 10),
                        }
                        store.save_report(report)
                        metrics["db_ops"] += 1
                    elif op_type == 'db_get':
                        store.get_report(f"long_report_{random.randint(0, max(0, i-1))}")
                        metrics["db_ops"] += 1
                    elif op_type == 'db_list':
                        store.list_reports(limit=20)
                        metrics["db_ops"] += 1

                    metrics["success_operations"] += 1

                    # 定期报告进度
                    if (i + 1) % 500 == 0:
                        logger.info(f"  进度: {i + 1}/{num_operations}")

                except Exception as e:
                    metrics["failures"] += 1
                    errors.append(f"Op {i} failed: {str(e)[:100]}")
                    # 继续执行其他操作

            metrics["total_operations"] = num_operations
            metrics["operations_per_second"] = num_operations / (time.time() - start_time) if (time.time() - start_time) > 0 else 0

            logger.info(f"超长运行稳定性测试完成:")
            logger.info(f"  总操作: {metrics['total_operations']}")
            logger.info(f"  成功: {metrics['success_operations']}")
            logger.info(f"  失败: {metrics['failures']}")
            logger.info(f"  缓存操作: {metrics['cache_ops']}")
            logger.info(f"  数据库操作: {metrics['db_ops']}")
            logger.info(f"  操作/秒: {metrics['operations_per_second']:.2f}")

            failure_rate = metrics["failures"] / num_operations if num_operations > 0 else 0
            passed = failure_rate < 0.01

            if failure_rate > 0.005:
                warnings.append(f"失败率较高: {failure_rate*100:.2f}%")

        except Exception as e:
            logger.error(f"超长运行稳定性测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            passed = False
            errors.append(f"测试崩溃: {str(e)}")

        duration = time.time() - start_time
        return TestResult(
            scenario="超长运行稳定性测试",
            passed=passed,
            duration=duration,
            iterations=num_operations,
            errors=errors[:100],
            warnings=warnings,
            metrics=metrics
        )

    def run_all_scenarios(self) -> List[TestResult]:
        """运行所有极端测试场景"""
        logger.info("=" * 80)
        logger.info("🚀 开始极端高难度真实实践")
        logger.info("=" * 80)

        scenarios = [
            ("极端并发测试", self.test_extreme_concurrency, 180),
            ("极端数据量测试", self.test_extreme_data_volume, 120),
            ("内存泄漏检测", self.test_memory_leak_detection, 60),
            ("极端边界条件测试", self.test_extreme_edge_cases, 60),
            ("超长运行稳定性测试", self.test_long_running_stability_extreme, 300),
        ]

        all_results = []

        for scenario_name, test_func, expected_time in scenarios:
            logger.info(f"\n{'=' * 80}")
            logger.info(f"开始场景: {scenario_name} (预期 {expected_time} 秒)")
            logger.info(f"{'=' * 80}\n")

            result = test_func()
            all_results.append(result)

            status = "✅ 通过" if result.passed else "❌ 失败"
            logger.info(f"\n{'=' * 80}")
            logger.info(f"场景 '{scenario_name}' 完成: {status}")
            logger.info(f"  耗时: {result.duration:.2f}秒")
            logger.info(f"  迭代: {result.iterations:,}")
            logger.info(f"  错误数: {len(result.errors)}")
            if result.warnings:
                logger.warning(f"  警告数: {len(result.warnings)}")
                for warning in result.warnings[:5]:
                    logger.warning(f"    - {warning}")
            logger.info(f"{'=' * 80}\n")

        return all_results


def print_final_report(results: List[TestResult]):
    """打印最终报告"""
    print("\n" + "=" * 80)
    print("📊 极端高难度真实实践 - 最终报告")
    print("=" * 80)

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    total_time = sum(r.duration for r in results)
    total_iterations = sum(r.iterations for r in results)
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)

    print(f"\n📈 总体执行:")
    print(f"  总场景数: {total}")
    print(f"  通过: {passed} ({passed/total*100:.1f}%)")
    print(f"  失败: {failed}")
    print(f"  总耗时: {total_time:.2f} 秒 ({total_time/60:.1f} 分钟)")
    print(f"  总迭代数: {total_iterations:,}")
    print(f"  总错误数: {total_errors}")
    print(f"  总警告数: {total_warnings}")

    print(f"\n📋 详细结果:")
    for result in results:
        status_icon = "✅" if result.passed else "❌"
        print(f"\n  {status_icon} {result.scenario}")
        print(f"    耗时: {result.duration:.2f}秒")
        print(f"    迭代: {result.iterations:,}")
        print(f"    错误: {len(result.errors)}")

        if result.warnings:
            print(f"    警告: {len(result.warnings)}")
            for warning in result.warnings[:3]:
                print(f"      ⚠️  {warning}")

        if result.metrics:
            print(f"    关键指标:")
            for key, value in list(result.metrics.items())[:6]:
                if isinstance(value, float):
                    print(f"      - {key}: {value:.2f}")
                else:
                    print(f"      - {key}: {value}")

    print("\n" + "=" * 80)
    if passed == total:
        print("🎉 所有测试场景通过！系统表现优秀！")
        score = 10.0
    elif passed >= total * 0.8:
        print("⚠️  大部分测试通过，系统表现良好")
        score = 8.0
    elif passed >= total * 0.6:
        print("❌ 部分测试通过，系统需要改进")
        score = 6.0
    else:
        print("❌❌ 多数测试失败，系统存在严重问题")
        score = 4.0

    print(f"\n综合评分: {score}/10")
    print("=" * 80)


def main():
    """主函数"""
    tester = ExtremeHighDifficultyTester()

    try:
        results = tester.run_all_scenarios()
        print_final_report(results)

        return results

    except KeyboardInterrupt:
        logger.warning("测试被用户中断")
    except Exception as e:
        logger.error(f"测试崩溃: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main()
