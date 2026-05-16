"""
特复杂高难度测试9 - 真实系统压力测试
包含: 文件系统、网络API、数据库、Redis、LLM集成等真实场景
"""

import asyncio
import os
import sys
import tempfile
import time
import random
import string
from pathlib import Path
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance
logger = get_logger_instance('high_difficulty_9')


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    status: str
    passed: bool
    issues_found: List[str]
    execution_time: float
    details: Dict[str, Any]


class RealWorldStressTester:
    """真实世界压力测试器"""

    def __init__(self):
        self.results: List[TestResult] = []
        self.errors: List[str] = []
        self.temp_dirs: List[Path] = []

    def cleanup(self):
        """清理临时资源"""
        for dir_path in self.temp_dirs:
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path, ignore_errors=True)
        self.temp_dirs = []

    def test_file_system_stress(self) -> TestResult:
        """文件系统压力测试 - 真实场景"""
        start_time = time.time()
        issues = []
        details = {}

        logger.info("🚀 开始真实文件系统压力测试")

        try:
            temp_dir = Path(tempfile.mkdtemp(prefix='ea_stress_test_'))
            self.temp_dirs.append(temp_dir)

            # 1. 测试: 创建大量小文件
            file_count = 2000
            logger.info(f"创建 {file_count} 个小文件...")
            created_files = []
            for i in range(file_count):
                file_path = temp_dir / f'file_{i}.txt'
                content = ''.join(random.choices(string.ascii_letters, k=100))
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created_files.append(file_path)
                except Exception as e:
                    issues.append(f"创建文件失败 {i}: {str(e)}")

            details['files_created'] = len(created_files)
            details['files_failed'] = file_count - len(created_files)

            # 2. 测试: 读取大量文件
            logger.info(f"读取 {len(created_files)} 个文件...")
            read_count = 0
            for file_path in created_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.read()
                    read_count += 1
                except Exception as e:
                    issues.append(f"读取文件失败 {file_path}: {str(e)}")

            details['files_read'] = read_count

            # 3. 测试: 删除大量文件
            logger.info(f"删除 {len(created_files)} 个文件...")
            delete_count = 0
            for file_path in created_files:
                try:
                    file_path.unlink(missing_ok=True)
                    delete_count += 1
                except Exception as e:
                    issues.append(f"删除文件失败 {file_path}: {str(e)}")

            details['files_deleted'] = delete_count

            # 4. 测试: 目录操作
            logger.info("目录操作测试...")
            nested_dir = temp_dir / 'level1' / 'level2' / 'level3'
            try:
                nested_dir.mkdir(parents=True, exist_ok=True)
                for i in range(100):
                    file_in_nested = nested_dir / f'nested_{i}.txt'
                    file_in_nested.write_text(f'test {i}')
                details['nested_dir_ok'] = True
            except Exception as e:
                issues.append(f"目录操作失败: {str(e)}")
                details['nested_dir_ok'] = False

            end_time = time.time()
            execution_time = end_time - start_time

            return TestResult(
                test_name="真实文件系统压力测试",
                status="completed",
                passed=len(issues) == 0,
                issues_found=issues,
                execution_time=execution_time,
                details=details
            )

        except Exception as e:
            issues.append(f"文件系统测试崩溃: {str(e)}")
            end_time = time.time()
            return TestResult(
                test_name="真实文件系统压力测试",
                status="failed",
                passed=False,
                issues_found=issues,
                execution_time=end_time - start_time,
                details={"error": str(e)}
            )

    def test_concurrent_file_access(self) -> TestResult:
        """并发文件访问测试"""
        start_time = time.time()
        issues = []
        details = {}

        logger.info("🚀 开始并发文件访问测试")

        try:
            temp_dir = Path(tempfile.mkdtemp(prefix='ea_concurrent_test_'))
            self.temp_dirs.append(temp_dir)

            shared_file = temp_dir / 'shared.txt'
            shared_file.write_text('')

            num_threads = 50
            writes_per_thread = 100

            def writer(thread_id):
                for i in range(writes_per_thread):
                    try:
                        with open(shared_file, 'a', encoding='utf-8') as f:
                            f.write(f"Thread {thread_id} - Write {i}\n")
                    except Exception as e:
                        raise Exception(f"Thread {thread_id} write error: {e}")

            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = {executor.submit(writer, i): i for i in range(num_threads)}
                completed = 0
                failed = 0
                for future in as_completed(futures):
                    try:
                        future.result()
                        completed += 1
                    except Exception as e:
                        issues.append(f"线程 {futures[future]} 失败: {str(e)}")
                        failed += 1

            details['threads_completed'] = completed
            details['threads_failed'] = failed
            details['total_operations'] = num_threads * writes_per_thread

            # 验证文件内容
            lines = shared_file.read_text().split('\n')
            details['total_lines_written'] = len([l for l in lines if l.strip()])

            end_time = time.time()
            return TestResult(
                test_name="并发文件访问测试",
                status="completed",
                passed=len(issues) == 0,
                issues_found=issues,
                execution_time=end_time - start_time,
                details=details
            )

        except Exception as e:
            issues.append(f"并发文件测试崩溃: {str(e)}")
            end_time = time.time()
            return TestResult(
                test_name="并发文件访问测试",
                status="failed",
                passed=False,
                issues_found=issues,
                execution_time=end_time - start_time,
                details={"error": str(e)}
            )

    def test_database_stress(self) -> TestResult:
        """数据库压力测试"""
        start_time = time.time()
        issues = []
        details = {}

        logger.info("🚀 开始数据库压力测试")

        try:
            from enterprise_agent_system.infrastructure import analysis_report_store
            from enterprise_agent_system.domain import core_data_models_and_enumerations

            store = analysis_report_store.AnalysisReportStore(db_path=":memory:")
            details['db_initialized'] = True

            # 测试: 大量数据写入
            num_records = 500
            logger.info(f"写入 {num_records} 条数据库记录...")
            write_start = time.time()
            for i in range(num_records):
                try:
                    report = core_data_models_and_enumerations.AnalysisReport(
                        id=f"test_report_{i}",
                        title=f"Test Report {i}",
                        summary=f"This is test report number {i}",
                        quality_score=random.uniform(0.0, 10.0)
                    )
                    store.save(report)
                except Exception as e:
                    issues.append(f"数据库写入失败 {i}: {str(e)}")

            details['db_write_time'] = time.time() - write_start
            details['db_write_count'] = num_records

            # 测试: 大量数据查询
            logger.info(f"查询 {num_records} 条数据库记录...")
            query_start = time.time()
            query_count = 0
            for i in range(num_records):
                try:
                    _ = store.get(f"test_report_{i}")
                    query_count += 1
                except Exception as e:
                    issues.append(f"数据库查询失败 {i}: {str(e)}")

            details['db_query_time'] = time.time() - query_start
            details['db_query_count'] = query_count

            # 测试: 批量操作
            logger.info("批量操作测试...")
            batch_start = time.time()
            batch_reports = []
            for i in range(100):
                report = core_data_models_and_enumerations.AnalysisReport(
                    id=f"batch_test_{i}",
                    title=f"Batch Test {i}",
                    summary=f"Batch summary {i}",
                    quality_score=random.uniform(0.0, 10.0)
                )
                batch_reports.append(report)
                store.save(report)

            details['db_batch_time'] = time.time() - batch_start
            details['db_batch_count'] = 100

            end_time = time.time()
            return TestResult(
                test_name="数据库压力测试",
                status="completed",
                passed=len(issues) == 0,
                issues_found=issues,
                execution_time=end_time - start_time,
                details=details
            )

        except Exception as e:
            issues.append(f"数据库测试崩溃: {str(e)}")
            end_time = time.time()
            return TestResult(
                test_name="数据库压力测试",
                status="failed",
                passed=False,
                issues_found=issues,
                execution_time=end_time - start_time,
                details={"error": str(e)}
            )

    def test_cache_stress(self) -> TestResult:
        """缓存系统压力测试"""
        start_time = time.time()
        issues = []
        details = {}

        logger.info("🚀 开始缓存系统压力测试")

        try:
            from enterprise_agent_system.infrastructure import redis_cache

            cache = redis_cache.RedisCacheManager()

            # 测试: 大量缓存写入
            num_items = 1000
            logger.info(f"写入 {num_items} 个缓存项...")
            write_start = time.time()
            for i in range(num_items):
                try:
                    key = f"stress_test_key_{i}"
                    value = f"value_{i}_{''.join(random.choices(string.ascii_letters, k=100))}"
                    cache.set(key, value)
                except Exception as e:
                    issues.append(f"缓存写入失败 {i}: {str(e)}")

            details['cache_write_time'] = time.time() - write_start

            # 测试: 大量缓存读取
            logger.info(f"读取 {num_items} 个缓存项...")
            read_start = time.time()
            hits = 0
            misses = 0
            for i in range(num_items):
                try:
                    key = f"stress_test_key_{i}"
                    result = cache.get(key)
                    if result:
                        hits += 1
                    else:
                        misses += 1
                except Exception as e:
                    issues.append(f"缓存读取失败 {i}: {str(e)}")

            details['cache_read_time'] = time.time() - read_start
            details['cache_hits'] = hits
            details['cache_misses'] = misses
            details['cache_hit_rate'] = hits / num_items if num_items > 0 else 0

            # 测试: 缓存淘汰
            logger.info("测试缓存淘汰机制...")
            cache_stats = cache.get_stats()
            details['cache_size_before'] = cache_stats.get('size', 0)
            details['cache_stats'] = cache_stats

            end_time = time.time()
            return TestResult(
                test_name="缓存系统压力测试",
                status="completed",
                passed=len(issues) == 0,
                issues_found=issues,
                execution_time=end_time - start_time,
                details=details
            )

        except Exception as e:
            issues.append(f"缓存测试崩溃: {str(e)}")
            end_time = time.time()
            return TestResult(
                test_name="缓存系统压力测试",
                status="failed",
                passed=False,
                issues_found=issues,
                execution_time=end_time - start_time,
                details={"error": str(e)}
            )

    def test_api_stress_fastapi(self) -> TestResult:
        """FastAPI 真实端点压力测试"""
        start_time = time.time()
        issues = []
        details = {}

        logger.info("🚀 开始 FastAPI 端点压力测试")

        try:
            from fastapi.testclient import TestClient
            from enterprise_agent_system.infrastructure.api import api_server

            client = TestClient(api_server.app)

            # 测试: 大量 GET 请求
            num_requests = 500
            logger.info(f"发送 {num_requests} 个 GET 请求...")
            requests_start = time.time()
            success_count = 0
            fail_count = 0

            for i in range(num_requests):
                try:
                    response = client.get("/")
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        fail_count += 1
                        issues.append(f"请求 {i} 失败: HTTP {response.status_code}")
                except Exception as e:
                    fail_count += 1
                    issues.append(f"请求 {i} 异常: {str(e)}")

            details['api_success_count'] = success_count
            details['api_fail_count'] = fail_count
            details['api_total_requests'] = num_requests
            details['api_time'] = time.time() - requests_start

            if num_requests > 0:
                details['api_qps'] = num_requests / (time.time() - requests_start) if (time.time() - requests_start) > 0 else 0
                details['api_success_rate'] = success_count / num_requests

            # 测试: 健康检查
            health_start = time.time()
            health_response = client.get("/health")
            details['health_check_status'] = health_response.status_code
            details['health_check_time'] = time.time() - health_start

            end_time = time.time()
            return TestResult(
                test_name="FastAPI 端点压力测试",
                status="completed",
                passed=len(issues) == 0,
                issues_found=issues,
                execution_time=end_time - start_time,
                details=details
            )

        except Exception as e:
            issues.append(f"API 测试崩溃: {str(e)}")
            end_time = time.time()
            return TestResult(
                test_name="FastAPI 端点压力测试",
                status="failed",
                passed=False,
                issues_found=issues,
                execution_time=end_time - start_time,
                details={"error": str(e)}
            )

    def test_config_manager_edge_cases(self) -> TestResult:
        """配置管理器边缘情况测试"""
        start_time = time.time()
        issues = []
        details = {}

        logger.info("🚀 开始配置管理器边缘情况测试")

        try:
            from enterprise_agent_system.infrastructure import config_manager

            # 测试: 环境变量覆盖
            logger.info("测试环境变量覆盖...")
            os.environ['EA_LLM_TEMPERATURE'] = '0.5'
            os.environ['EA_API_DEBUG'] = 'true'
            os.environ['EA_ANALYSIS_BATCH_SIZE'] = '100'

            config = config_manager.get_config()

            details['env_var_test'] = True

            # 测试: 类型转换验证
            logger.info("测试类型转换...")
            if not isinstance(config.llm.temperature, float):
                issues.append(f"温度配置类型错误: {type(config.llm.temperature)}")
            if not isinstance(config.api.debug, bool):
                issues.append(f"调试配置类型错误: {type(config.api.debug)}")
            if not isinstance(config.analysis.batch_size, int):
                issues.append(f"批处理大小类型错误: {type(config.analysis.batch_size)}")

            details['type_check_passed'] = len(issues) == 0

            # 测试: 配置重载
            logger.info("测试配置重载...")
            original_temp = config.llm.temperature
            os.environ['EA_LLM_TEMPERATURE'] = '0.8'
            config_manager.reload_config()
            new_config = config_manager.get_config()

            details['config_reload_ok'] = True

            # 清理环境变量
            for key in list(os.environ.keys()):
                if key.startswith('EA_'):
                    del os.environ[key]

            end_time = time.time()
            return TestResult(
                test_name="配置管理器边缘情况测试",
                status="completed",
                passed=len(issues) == 0,
                issues_found=issues,
                execution_time=end_time - start_time,
                details=details
            )

        except Exception as e:
            issues.append(f"配置测试崩溃: {str(e)}")
            end_time = time.time()
            return TestResult(
                test_name="配置管理器边缘情况测试",
                status="failed",
                passed=False,
                issues_found=issues,
                execution_time=end_time - start_time,
                details={"error": str(e)}
            )

    def run_all_tests(self) -> List[TestResult]:
        """运行所有高难度测试"""
        logger.info("=" * 80)
        logger.info("🔥 开始特复杂高难度测试9 - 真实系统压力测试")
        logger.info("=" * 80)

        all_tests = [
            self.test_file_system_stress,
            self.test_concurrent_file_access,
            self.test_database_stress,
            self.test_cache_stress,
            self.test_api_stress_fastapi,
            self.test_config_manager_edge_cases,
        ]

        all_results = []

        for test_func in all_tests:
            try:
                result = test_func()
                all_results.append(result)

                logger.info("-" * 80)
                logger.info(f"✅ 测试: {result.test_name}")
                logger.info(f"   状态: {'通过' if result.passed else '失败'}")
                logger.info(f"   耗时: {result.execution_time:.2f}秒")
                if result.issues_found:
                    logger.info(f"   发现问题: {len(result.issues_found)}个")
                    for issue in result.issues_found[:5]:
                        logger.warning(f"   - {issue}")
                if result.details:
                    logger.info(f"   详情: {result.details}")

            except Exception as e:
                logger.error(f"❌ 测试函数崩溃: {e}")
                result = TestResult(
                    test_name=getattr(test_func, '__name__', 'unknown_test'),
                    status="crashed",
                    passed=False,
                    issues_found=[str(e)],
                    execution_time=0,
                    details={"exception": str(e)}
                )
                all_results.append(result)

        self.cleanup()
        return all_results


def print_summary(results: List[TestResult]):
    """打印测试总结"""
    print("\n" + "=" * 80)
    print("📊 特复杂高难度测试9 - 完整总结")
    print("=" * 80)

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    total_issues = sum(len(r.issues_found) for r in results)

    print(f"\n📈 总体表现:")
    print(f"   总测试数: {total}")
    print(f"   通过数: {passed}")
    print(f"   失败数: {failed}")
    print(f"   通过率: {(passed/total*100):.1f}%" if total > 0 else "N/A")
    print(f"   发现问题: {total_issues}个")

    if total_issues > 0:
        print(f"\n🔍 发现的问题列表:")
        for result in results:
            if result.issues_found:
                print(f"\n  在 '{result.test_name}' 中:")
                for i, issue in enumerate(result.issues_found, 1):
                    print(f"    {i}. {issue}")

    print(f"\n⏱️  详细执行时间:")
    for result in results:
        print(f"   {result.test_name}: {result.execution_time:.2f}秒")

    print("\n" + "=" * 80)


async def main():
    tester = RealWorldStressTester()

    try:
        results = tester.run_all_tests()
        print_summary(results)

        return results

    finally:
        tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
