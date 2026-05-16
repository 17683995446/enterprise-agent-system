"""
High Difficulty Test 11 - Advanced Real-World Scenarios
特复杂高难度测试11 - 高级真实场景测试

测试：
1. LLM集成调用 - 使用真实硅基流动API密钥
2. 数据管道批量处理
3. 故障恢复和重试机制
4. 缓存失效和一致性检查
5. 长时间运行稳定性测试
"""

import asyncio
import sys
import time
import tempfile
import os
import random
import string
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance("high_difficulty_11")


@dataclass
class TestResult:
    test_name: str
    passed: bool
    issues: List[str]
    details: Dict[str, Any]
    execution_time: float


class AdvancedRealWorldTester:
    """高级真实世界测试器"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.temp_dirs: List[Path] = []
    
    def cleanup(self):
        """清理资源"""
        for dir_path in self.temp_dirs:
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path, ignore_errors=True)
    
    def test_llm_integration_smoke(self) -> TestResult:
        """测试LLM集成（不实际调用真实API）"""
        start_time = time.time()
        issues = []
        details = {}
        
        logger.info("🚀 测试LLM集成（不实际调用）")
        
        try:
            from enterprise_agent_system.infrastructure.llm_integration import (
                LLMConfig,
                LLMProvider,
                ModelType,
                CompletionResult,
                LRUCache,
                get_llm_manager,
            )
            
            # 1. 测试配置创建
            config = LLMConfig(
                provider=LLMProvider.MOCK,  # 使用MOCK
                api_key="test-key",
                model="Qwen/Qwen2.5-7B-Instruct",
                enable_cache=True
            )
            logger.info(f"LLM配置创建成功: {config}")
            details["config_created"] = True
            
            # 2. 测试LRU缓存
            logger.info("测试LRU缓存...")
            cache = LRUCache(max_size=100)
            
            for i in range(200):
                cache.set(f"key_{i}", f"value_{i}")
            
            # 检查淘汰是否正常
            cache_size = len(cache.cache)
            details["lru_cache_size"] = cache_size
            if cache_size > 100:
                issues.append("LRU缓存没有正确淘汰数据")
            logger.info(f"LRU缓存测试完成: 大小 {cache_size}")
            
            # 3. 测试获取LLM管理器
            logger.info("测试获取LLM管理器...")
            try:
                llm_manager = get_llm_manager()
                stats = llm_manager.get_stats()
                logger.info(f"LLM管理器获取成功: {stats}")
                details["llm_manager_working"] = True
            except Exception as e:
                issues.append(f"LLM管理器失败: {str(e)}")
            
        except Exception as e:
            issues.append(f"LLM集成测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return TestResult(
            test_name="LLM集成基础测试",
            passed=len(issues) == 0,
            issues=issues,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def test_data_pipeline_batch_processing(self) -> TestResult:
        """测试数据管道批量处理"""
        start_time = time.time()
        issues = []
        details = {}
        
        logger.info("🚀 测试数据管道批量处理")
        
        try:
            # 创建大量模拟代码文件进行处理
            temp_dir = Path(tempfile.mkdtemp(prefix="data_pipeline_test_"))
            self.temp_dirs.append(temp_dir)
            
            # 创建100个Python代码文件
            logger.info("创建100个测试代码文件...")
            for i in range(100):
                file_path = temp_dir / f"file_{i}.py"
                code_content = f"""
def function_{i}(x):
    return x * {i}

class Class{i}:
    def __init__(self):
        self.value = {i}
    
    def method(self):
        return self.value
"""
                file_path.write_text(code_content)
            
            details["files_created"] = 100
            logger.info(f"成功创建 {details['files_created']} 个文件")
            
            # 测试分析这些文件
            logger.info("测试数据管道分析流程...")
            
            # 尝试使用依赖分析器
            from enterprise_agent_system.test_suite.test_dependency_graph_fixed import EnhancedPythonDependencyAnalyzer
            
            analyzer = EnhancedPythonDependencyAnalyzer(str(temp_dir))
            modules = analyzer.scan_modules()
            
            details["modules_scanned"] = len(modules)
            logger.info(f"成功扫描 {len(modules)} 个模块")
            
            # 测试分析统计
            import_statements = 0
            class_definitions = 0
            function_definitions = 0
            
            for module in modules:
                with open(module, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    import_statements += content.count('import ')
                    class_definitions += content.count('class ')
                    function_definitions += content.count('def ')
            
            details["total_imports"] = import_statements
            details["total_classes"] = class_definitions
            details["total_functions"] = function_definitions
            
            logger.info(f"统计分析完成: {import_statements} imports, {class_definitions} classes, {function_definitions} functions")
            
        except Exception as e:
            issues.append(f"数据管道测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return TestResult(
            test_name="数据管道批量处理",
            passed=len(issues) == 0,
            issues=issues,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def test_fault_recovery_mechanism(self) -> TestResult:
        """测试故障恢复和重试机制"""
        start_time = time.time()
        issues = []
        details = {}
        
        logger.info("🚀 测试故障恢复和重试机制")
        
        try:
            # 测试 Circuit Breaker
            logger.info("测试Circuit Breaker...")
            from enterprise_agent_system.infrastructure.error_handling import CircuitBreaker
            
            breaker = CircuitBreaker(failure_threshold=3, timeout=10)
            
            # 模拟失败场景
            for i in range(5):
                try:
                    if i < 3:
                        breaker.record_failure()
                        logger.info(f"记录第 {i+1} 次失败")
                    else:
                        breaker.record_success()
                        logger.info(f"记录第 {i-2} 次成功")
                except Exception as e:
                    issues.append(f"Circuit Breaker失败 {i}: {str(e)}")
            
            details["breaker_tested"] = True
            logger.info(f"Circuit Breaker测试完成")
            
            # 测试 Error Handler
            logger.info("测试Error Handler...")
            from enterprise_agent_system.infrastructure.error_handling import ErrorHandler, EnterpriseAgentError, LLMError, CacheError
            
            handler = ErrorHandler()
            
            # 测试各类错误转换
            test_errors = [
                EnterpriseAgentError("Test error", code="TEST"),
                LLMError("Test LLM error", model="test-model"),
                CacheError("Test cache error", cache_key="test-key"),
            ]
            
            handled_results = []
            for err in test_errors:
                try:
                    result = handler.handle(err)
                    handled_results.append(result)
                except Exception as e:
                    issues.append(f"Handler failed for {err.__class__.__name__}: {str(e)}")
            
            details["errors_handled"] = len(handled_results)
            logger.info(f"成功处理 {len(handled_results)} 种错误类型")
            
            # 测试是否需要重试
            retry_count = 0
            for err in test_errors:
                try:
                    if handler.should_retry(err):
                        retry_count += 1
                except Exception as e:
                    issues.append(f"Should retry failed for {err.__class__.__name__}: {str(e)}")
            
            details["retry_checks"] = retry_count
            logger.info(f"重试检查完成: {retry_count} 个可重试错误")
            
        except Exception as e:
            issues.append(f"故障恢复测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return TestResult(
            test_name="故障恢复和重试机制",
            passed=len(issues) == 0,
            issues=issues,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def test_cache_consistency_invalidation(self) -> TestResult:
        """测试缓存一致性和失效机制"""
        start_time = time.time()
        issues = []
        details = {}
        
        logger.info("🚀 测试缓存一致性和失效")
        
        try:
            from enterprise_agent_system.infrastructure.redis_cache import RedisCacheManager
            
            cache = RedisCacheManager()
            
            # 写入测试数据
            test_key_1 = "test_key_1"
            test_value_1 = "test_value_1"
            
            test_key_2 = "test_key_2"
            test_value_2 = "test_value_2"
            
            cache.set(test_key_1, test_value_1)
            cache.set(test_key_2, test_value_2)
            
            logger.info("写入缓存测试数据")
            
            # 验证读取
            if cache.get(test_key_1) != test_value_1:
                issues.append("缓存读取值不匹配")
            
            # 验证统计
            stats = cache.get_stats()
            details["initial_stats"] = stats
            logger.info(f"缓存统计: {stats}")
            
            # 测试删除一个key
            cache.delete(test_key_1)
            if cache.get(test_key_1) is not None:
                issues.append("缓存删除后还能读取到值")
            
            # 验证缓存大小是否正确
            final_stats = cache.get_stats()
            details["final_stats"] = final_stats
            logger.info(f"删除后缓存统计: {final_stats}")
            
            # 测试缓存清除
            cache.clear()
            if cache.get(test_key_2) is not None:
                issues.append("缓存清除后还能读取到值")
            
            details["cache_tested"] = True
            
        except Exception as e:
            issues.append(f"缓存一致性测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return TestResult(
            test_name="缓存一致性和失效",
            passed=len(issues) == 0,
            issues=issues,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def test_analysis_report_storage(self) -> TestResult:
        """测试分析报告存储（数据库集成）"""
        start_time = time.time()
        issues = []
        details = {}
        
        logger.info("🚀 测试分析报告存储")
        
        try:
            from enterprise_agent_system.infrastructure.analysis_report_store import AnalysisReportStore
            from enterprise_agent_system.domain.core_data_models_and_enumerations import AnalysisReport
            
            store = AnalysisReportStore(db_path=":memory:")
            
            # 创建大量报告
            num_reports = 50
            reports = []
            
            logger.info(f"创建 {num_reports} 个分析报告...")
            for i in range(num_reports):
                report = AnalysisReport(
                    id=f"report_{i}",
                    title=f"Test Report {i}",
                    summary=f"This is the {i}th test report",
                    quality_score=random.uniform(0.0, 10.0),
                    created_at=time.time()
                )
                reports.append(report)
                store.save(report)
            
            details["reports_saved"] = num_reports
            
            # 测试获取
            logger.info("测试报告获取...")
            retrieved_success_count = 0
            for i in range(num_reports):
                report = store.get(f"report_{i}")
                if report is not None:
                    retrieved_success_count += 1
            
            details["reports_retrieved"] = retrieved_success_count
            
            if retrieved_success_count != num_reports:
                issues.append(f"报告获取不完整: 期望 {num_reports}, 实际 {retrieved_success_count}")
            
            logger.info(f"成功获取 {retrieved_success_count} 个报告")
            
            # 测试列出所有
            all_reports = store.list_all()
            details["reports_listed"] = len(all_reports)
            
            # 测试删除
            logger.info("测试报告删除...")
            delete_count = 0
            for i in range(10):
                try:
                    store.delete(f"report_{i}")
                    delete_count += 1
                except Exception as e:
                    issues.append(f"删除报告失败: {str(e)}")
            
            details["reports_deleted"] = delete_count
            logger.info(f"删除了 {delete_count} 个报告")
            
        except Exception as e:
            issues.append(f"报告存储测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return TestResult(
            test_name="分析报告存储",
            passed=len(issues) == 0,
            issues=issues,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def test_long_running_stability(self) -> TestResult:
        """测试长时间运行稳定性"""
        start_time = time.time()
        issues = []
        details = {}
        
        logger.info("🚀 测试长时间运行稳定性")
        
        try:
            from enterprise_agent_system.infrastructure.redis_cache import RedisCacheManager
            from enterprise_agent_system.infrastructure.analysis_report_store import AnalysisReportStore
            from enterprise_agent_system.domain.core_data_models_and_enumerations import AnalysisReport
            
            cache = RedisCacheManager()
            store = AnalysisReportStore(db_path=":memory:")
            
            operations = 1000
            success_count = 0
            
            logger.info(f"执行 {operations} 次混合操作...")
            
            for i in range(operations):
                try:
                    # 混合操作：写缓存、读缓存、写数据库、读数据库
                    cache_key = f"stress_key_{i % 100}"
                    cache.set(cache_key, f"stress_value_{i}")
                    cache.get(cache_key)
                    
                    report_id = f"stress_report_{i % 50}"
                    report = AnalysisReport(
                        id=report_id,
                        title=f"Stress Report {i}",
                        summary=f"Stress test report",
                        quality_score=random.uniform(0, 10)
                    )
                    store.save(report)
                    store.get(report_id)
                    
                    success_count += 1
                    
                    # 偶尔打印进度
                    if (i+1) % 100 == 0:
                        logger.info(f"进度: {i+1}/{operations}")
                        
                except Exception as e:
                    issues.append(f"第 {i} 次操作失败: {str(e)}")
            
            details["operations_attempted"] = operations
            details["operations_succeeded"] = success_count
            
            if success_count != operations:
                issues.append(f"部分操作失败: {success_count}/{operations}")
            
            logger.info(f"长时间稳定性测试完成: {success_count}/{operations}")
            
        except Exception as e:
            issues.append(f"稳定性测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return TestResult(
            test_name="长时间运行稳定性",
            passed=len(issues) == 0,
            issues=issues,
            details=details,
            execution_time=time.time() - start_time
        )
    
    def run_all_tests(self) -> List[TestResult]:
        """运行所有高级测试"""
        logger.info("=" * 80)
        logger.info("🔥 High Difficulty Test 11 - Advanced Real-World Scenarios")
        logger.info("=" * 80)
        
        all_tests = [
            self.test_llm_integration_smoke,
            self.test_data_pipeline_batch_processing,
            self.test_fault_recovery_mechanism,
            self.test_cache_consistency_invalidation,
            self.test_analysis_report_storage,
            self.test_long_running_stability,
        ]
        
        all_results = []
        
        for test_func in all_tests:
            logger.info("\n" + "-" * 80)
            result = test_func()
            all_results.append(result)
            
            status = "✅" if result.passed else "❌"
            logger.info(f"{status} {result.test_name} ({result.execution_time:.2f}秒)")
            
            if result.issues:
                for issue in result.issues:
                    logger.warning(f"  ⚠️  {issue}")
        
        return all_results


def print_final_summary(results: List[TestResult]):
    """打印最终总结报告"""
    print("\n" + "=" * 80)
    print("📊 High Difficulty Test 11 - Final Summary")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    total_time = sum(r.execution_time for r in results)
    total_issues = sum(len(r.issues) for r in results)
    
    print(f"\n📈 总体执行:")
    print(f"  总测试数: {total}")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  通过率: {(passed / total * 100):.1f}%" if total > 0 else "N/A")
    print(f"  发现问题: {total_issues} 个")
    print(f"  总执行时间: {total_time:.2f} 秒")
    
    print(f"\n📋 详细结果:")
    for result in results:
        status_icon = "✅" if result.passed else "❌"
        print(f"\n  {status_icon} {result.test_name}")
        print(f"    时间: {result.execution_time:.2f}秒")
        print(f"    问题: {len(result.issues)}个")
        if result.details:
            print(f"    详情: {result.details}")


async def main():
    """主函数"""
    tester = AdvancedRealWorldTester()
    
    try:
        results = tester.run_all_tests()
        print_final_summary(results)
        
        return results
        
    finally:
        tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
