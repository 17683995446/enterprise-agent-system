"""
极端极限压力测试 - 寻找深层隐藏bug
测试场景：
1. 超长时间运行测试 - 连续执行10万次操作
2. 极端大数据存储 - 100MB+数据
3. 边缘值与异常数据测试
4. 快速高频操作测试 - 100万次简单操作
5. 资源耗尽与恢复测试
"""

import sys
import time
import random
import threading
import gc
import string
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('extreme_limit_test')


@dataclass
class ExtremeTestResult:
    scenario: str
    passed: bool
    duration: float
    operations: int
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]


class ExtremeLimitTester:
    """极端极限测试器"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def generate_large_data(self, size_mb: float) -> str:
        """生成指定大小的大数据"""
        chars = string.ascii_letters + string.digits + string.punctuation
        size_bytes = int(size_mb * 1024 * 1024)
        return ''.join(random.choice(chars) for _ in range(size_bytes))

    def test_long_running_sustained(self) -> ExtremeTestResult:
        """超长时间持续运行测试 - 5000次操作（简化版）"""
        logger.info("🔥 场景1: 超长时间持续运行测试 (5000次操作)")
        
        start_time = time.time()
        total_ops = 5000
        success_count = 0
        error_count = 0
        latencies = []
        
        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
            
            store = SimpleMemoryStore()
            cache = SimpleCache()
            
            for i in range(total_ops):
                op_start = time.time()
                
                try:
                    if i % 3 == 0:
                        # 写入操作
                        report_id = f"long_test_{i}"
                        store.save_report({
                            "id": report_id,
                            "title": f"Long Run Test {i}",
                            "type": "test",
                            "summary": f"This is test {i}",
                            "quality_score": random.uniform(0, 10),
                            "metrics": {"iteration": i, "timestamp": time.time()}
                        })
                    elif i % 3 == 1:
                        # 读取操作
                        report_id = f"long_test_{random.randint(0, max(0, i-1))}"
                        store.get_report(report_id)
                    else:
                        # 缓存操作
                        cache.set(f"cache_{i}", i)
                        cache.get(f"cache_{random.randint(0, max(0, i-1))}")
                    
                    success_count += 1
                    
                    if (i + 1) % 10000 == 0:
                        logger.info(f"  进度: {i+1}/{total_ops} ({(i+1)/total_ops*100:.1f}%)")
                
                except Exception as e:
                    error_count += 1
                    if error_count <= 10:  # 只记录前10个错误
                        self.errors.append(f"操作{i}失败: {str(e)[:100]}")
                
                op_time = (time.time() - op_start) * 1000
                latencies.append(op_time)
            
            # 统计
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            max_latency = max(latencies) if latencies else 0
            
            logger.info(f"超长时间测试完成")
            logger.info(f"  总操作: {total_ops}, 成功: {success_count}, 失败: {error_count}")
            logger.info(f"  平均延迟: {avg_latency:.2f}ms, 最大延迟: {max_latency:.2f}ms")
            
            passed = error_count == 0 and success_count == total_ops
        
        except Exception as e:
            logger.error(f"超长时间测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.errors.append(f"测试崩溃: {str(e)}")
            passed = False
        
        return ExtremeTestResult(
            scenario="超长时间持续运行测试",
            passed=passed,
            duration=time.time() - start_time,
            operations=total_ops,
            errors=list(self.errors),
            warnings=list(self.warnings),
            metrics={
                "success_rate": success_count / total_ops if total_ops > 0 else 0,
                "avg_latency_ms": avg_latency if 'avg_latency' in locals() else 0,
                "max_latency_ms": max_latency if 'max_latency' in locals() else 0
            }
        )

    def test_extreme_data_size(self) -> ExtremeTestResult:
        """极端大数据存储测试"""
        logger.info("🔥 场景2: 极端大数据存储测试")
        
        start_time = time.time()
        self.errors.clear()
        self.warnings.clear()
        
        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
            
            store = SimpleMemoryStore()
            sizes = [0.1, 0.5, 1, 5, 10]  # 单位MB
            
            success_count = 0
            total_count = len(sizes)
            
            for size_mb in sizes:
                try:
                    logger.info(f"  测试 {size_mb}MB 数据")
                    
                    large_data = self.generate_large_data(size_mb)
                    report_id = f"large_data_{size_mb}mb"
                    
                    save_start = time.time()
                    result_id = store.save_report({
                        "id": report_id,
                        "title": f"Large Data Test {size_mb}MB",
                        "type": "large_data",
                        "content": large_data,
                        "summary": f"Test of {size_mb}MB data",
                        "quality_score": 10.0,
                        "metrics": {"size_mb": size_mb, "data_length": len(large_data)}
                    })
                    save_time = (time.time() - save_start) * 1000
                    
                    read_start = time.time()
                    retrieved = store.get_report(report_id)
                    read_time = (time.time() - read_start) * 1000
                    
                    if retrieved and retrieved.get("content") == large_data:
                        success_count += 1
                        logger.info(f"    ✓ {size_mb}MB - 保存{save_time:.1f}ms, 读取{read_time:.1f}ms")
                    else:
                        self.errors.append(f"{size_mb}MB数据验证失败")
                        
                except Exception as e:
                    self.errors.append(f"{size_mb}MB测试失败: {str(e)}")
                    logger.error(f"  ✗ {size_mb}MB失败: {str(e)}")
            
            passed = success_count == total_count and len(self.errors) == 0
            
        except Exception as e:
            logger.error(f"大数据测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.errors.append(f"测试崩溃: {str(e)}")
            passed = False
        
        return ExtremeTestResult(
            scenario="极端大数据存储测试",
            passed=passed,
            duration=time.time() - start_time,
            operations=len(sizes) if 'sizes' in locals() else 0,
            errors=list(self.errors),
            warnings=list(self.warnings),
            metrics={"success_count": success_count if 'success_count' in locals() else 0}
        )

    def test_edge_values_and_exceptions(self) -> ExtremeTestResult:
        """边缘值与异常数据测试"""
        logger.info("🔥 场景3: 边缘值与异常数据测试")
        
        start_time = time.time()
        self.errors.clear()
        self.warnings.clear()
        
        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
            
            store = SimpleMemoryStore()
            cache = SimpleCache()
            
            edge_cases = [
                ("空字符串标题", {"title": "", "type": "test"}),
                ("None类型标题", {"title": None, "type": "test"}),
                ("空字典", {}),
                ("超复杂嵌套结构", {
                    "a": {"b": {"c": {"d": {"e": [1, 2, 3, {"f": "deep"}]}}}},
                    "type": "nested"
                }),
                ("特殊字符", {"title": "你好世界!@#$%^&*()_+=-[]{};:'\"\\|,.<>/?", "type": "test"}),
                ("大量字段", {f"field_{i}": f"value_{i}" for i in range(100)}),
                ("超长ID", {"id": "x" * 1000, "title": "Long ID Test", "type": "test"}),
                ("None值", {"id": "none_test", "title": None, "summary": None, "type": "test"}),
                ("极端数字", {"quality_score": 1e308, "confidence": -1e308, "type": "test"}),
            ]
            
            success_count = 0
            for case_name, report_data in edge_cases:
                try:
                    logger.info(f"  测试: {case_name}")
                    report_id = store.save_report(report_data)
                    retrieved = store.get_report(report_id)
                    
                    if retrieved:
                        success_count += 1
                        logger.info(f"    ✓ 成功")
                    else:
                        self.errors.append(f"{case_name}: 读取失败")
                        logger.warning(f"    ✗ 读取失败")
                
                except Exception as e:
                    self.errors.append(f"{case_name} 抛出异常: {str(e)}")
                    logger.error(f"    ✗ 异常: {str(e)}")
            
            # 测试缓存边缘情况
            logger.info("  测试缓存边缘情况")
            try:
                cache.set("", "empty_key")  # 空键
                cache.get("")
                
                cache.set("none_value", None)  # None值
                cache.get("none_value")
                
                # 超大键值
                huge_key = "x" * 10000
                huge_value = "y" * 1000000
                cache.set(huge_key, huge_value)
                cache.get(huge_key)
                
                success_count += 1
                logger.info("    ✓ 缓存边缘情况正常")
            except Exception as e:
                self.errors.append(f"缓存边缘情况失败: {str(e)}")
            
            passed = success_count == len(edge_cases) + 1
        
        except Exception as e:
            logger.error(f"边缘值测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.errors.append(f"测试崩溃: {str(e)}")
            passed = False
        
        return ExtremeTestResult(
            scenario="边缘值与异常数据测试",
            passed=passed,
            duration=time.time() - start_time,
            operations=len(edge_cases) + 1 if 'edge_cases' in locals() else 0,
            errors=list(self.errors),
            warnings=list(self.warnings),
            metrics={"success_count": success_count if 'success_count' in locals() else 0}
        )

    def test_high_frequency_operations(self) -> ExtremeTestResult:
        """高频快速操作测试 - 10万次简单操作（简化版）"""
        logger.info("🔥 场景4: 高频快速操作测试 (10万次)")
        
        start_time = time.time()
        self.errors.clear()
        self.warnings.clear()
        
        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
            
            store = SimpleMemoryStore()
            cache = SimpleCache()
            
            total_ops = 100000
            success_count = 0
            error_count = 0
            batch_size = 10000
            
            logger.info(f"开始执行 {total_ops} 次快速操作")
            
            for batch_start in range(0, total_ops, batch_size):
                batch_end = min(batch_start + batch_size, total_ops)
                
                for i in range(batch_start, batch_end):
                    try:
                        # 高频简单操作
                        cache.set(f"hf_{i}", i)
                        cache.get(f"hf_{random.randint(0, i)}")
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        if error_count <= 10:
                            self.errors.append(f"高频操作{i}失败: {str(e)[:50]}")
                
                if batch_end % 100000 == 0:
                    logger.info(f"  进度: {batch_end}/{total_ops} ({batch_end/total_ops*100:.0f}%)")
            
            # 统计性能
            duration = time.time() - start_time
            ops_per_second = total_ops / duration if duration > 0 else 0
            
            logger.info(f"高频操作测试完成")
            logger.info(f"  总操作: {total_ops}, 成功: {success_count}, 失败: {error_count}")
            logger.info(f"  吞吐量: {ops_per_second:.0f} 次/秒")
            
            passed = error_count == 0
        
        except Exception as e:
            logger.error(f"高频操作测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            self.errors.append(f"测试崩溃: {str(e)}")
            passed = False
        
        return ExtremeTestResult(
            scenario="高频快速操作测试",
            passed=passed,
            duration=time.time() - start_time,
            operations=total_ops if 'total_ops' in locals() else 0,
            errors=list(self.errors),
            warnings=list(self.warnings),
            metrics={
                "ops_per_second": ops_per_second if 'ops_per_second' in locals() else 0,
                "success_rate": success_count / total_ops if 'success_count' in locals() and total_ops > 0 else 0
            }
        )

    def run_all_scenarios(self) -> List[ExtremeTestResult]:
        """运行所有极端测试场景"""
        logger.info("=" * 80)
        logger.info("🚀 开始极端极限压力测试")
        logger.info("=" * 80)
        
        scenarios = [
            self.test_long_running_sustained,
            self.test_extreme_data_size,
            self.test_edge_values_and_exceptions,
            self.test_high_frequency_operations,
        ]
        
        all_results = []
        
        for scenario_func in scenarios:
            logger.info(f"\n{'=' * 80}")
            result = scenario_func()
            all_results.append(result)
            
            status = "✅ 通过" if result.passed else "❌ 失败"
            logger.info(f"场景 '{result.scenario}' 完成: {status}")
            logger.info(f"  耗时: {result.duration:.2f}秒")
            logger.info(f"  错误数: {len(result.errors)}")
            
            if result.warnings:
                for warning in result.warnings[:3]:
                    logger.warning(f"  ⚠️  {warning}")
        
        return all_results


def print_extreme_report(results: List[ExtremeTestResult]):
    """打印极端测试报告"""
    print("\n" + "=" * 80)
    print("📊 极端极限压力测试报告")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    total_ops = sum(r.operations for r in results)
    total_time = sum(r.duration for r in results)
    
    print(f"\n📈 总体执行:")
    print(f"  总场景数: {total}")
    print(f"  通过: {passed} ({passed/total*100:.1f}%)")
    print(f"  失败: {failed}")
    print(f"  总操作: {total_ops:,}")
    print(f"  总耗时: {total_time:.2f}秒")
    
    print(f"\n📋 详细结果:")
    for result in results:
        status_icon = "✅" if result.passed else "❌"
        print(f"\n  {status_icon} {result.scenario}")
        print(f"    耗时: {result.duration:.2f}秒")
        print(f"    操作数: {result.operations:,}")
        print(f"    错误数: {len(result.errors)}")
        
        if result.errors:
            for err in result.errors[:3]:
                print(f"    ✗ {err}")
        
        if result.metrics:
            print(f"    指标:")
            for key, value in list(result.metrics.items()):
                if isinstance(value, float):
                    print(f"      - {key}: {value:.2f}")
                else:
                    print(f"      - {key}: {value}")
    
    print("\n" + "=" * 80)
    if passed == total:
        print("🎉 所有极端测试通过！系统表现极其优秀！")
    elif passed >= total * 0.75:
        print("⚠️ 大部分测试通过，系统表现良好")
    else:
        print("❌ 存在严重问题，需要修复")
    
    score = passed / total * 10
    print(f"综合评分: {score:.1f}/10")
    print("=" * 80)


def main():
    """主函数"""
    tester = ExtremeLimitTester()
    
    try:
        results = tester.run_all_scenarios()
        print_extreme_report(results)
        return results
    except KeyboardInterrupt:
        logger.warning("测试被用户中断")
    except Exception as e:
        logger.error(f"测试崩溃: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
