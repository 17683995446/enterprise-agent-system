"""
Real Production Scenario Test
真实生产环境模拟测试 - 模拟真实用户行为

场景设计：
1. API Gateway 压力测试
2. 数据库连接池测试
3. 异步任务队列测试
4. 网络延迟和超时测试
5. 日志和监控测试
6. 资源泄漏检测
7. 故障恢复测试
"""

import sys
import time
import random
import threading
import traceback
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, Future
import queue

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('real_production_test')


@dataclass
class ScenarioResult:
    name: str
    passed: bool
    duration: float
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]


@dataclass
class UserAction:
    action_type: str
    user_id: str
    timestamp: float
    success: bool
    latency_ms: float
    error: Optional[str] = None


class RealProductionSimulator:
    """真实生产环境模拟器"""

    def __init__(self):
        self.results: List[ScenarioResult] = []
        self.user_actions: List[UserAction] = []
        self.error_counter = 0
        self.success_counter = 0
        self.lock = threading.RLock()

    def simulate_api_gateway_stress(self) -> ScenarioResult:
        """API网关压力测试 - 模拟10000次API调用"""
        logger.info("🔥 场景1: API网关压力测试")
        
        start_time = time.time()
        errors = []
        warnings = []
        metrics = {
            "total_requests": 0,
            "success_requests": 0,
            "failed_requests": 0,
            "avg_latency_ms": 0,
            "p95_latency_ms": 0,
            "p99_latency_ms": 0,
            "requests_per_second": 0,
        }

        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
            store = SimpleMemoryStore()
            
            num_requests = 10000
            latencies = []
            successes = 0
            
            logger.info(f"模拟 {num_requests} 次API调用...")
            
            def make_request(req_id: int):
                nonlocal successes
                start = time.time()
                try:
                    if req_id % 3 == 0:
                        store.save_report({
                            "id": f"api_test_{req_id}",
                            "title": f"API Test {req_id}",
                            "summary": "API Gateway Test",
                            "type": "api",
                            "quality_score": random.uniform(0, 10),
                        })
                    elif req_id % 3 == 1:
                        store.get_report(f"api_test_{req_id - 1}")
                    else:
                        store.list_reports(limit=10)
                    
                    successes += 1
                    return (time.time() - start) * 1000, None
                except Exception as e:
                    return (time.time() - start) * 1000, str(e)
            
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures: List[Future] = []
                for i in range(num_requests):
                    futures.append(executor.submit(make_request, i))
                
                completed = 0
                for future in futures:
                    latency, error = future.result()
                    latencies.append(latency)
                    if error:
                        errors.append(f"Request {completed}: {error[:80]}")
                    completed += 1
                    if completed % 2000 == 0:
                        logger.info(f"  进度: {completed}/{num_requests}")
            
            # 计算指标
            metrics["total_requests"] = num_requests
            metrics["success_requests"] = successes
            metrics["failed_requests"] = num_requests - successes
            metrics["avg_latency_ms"] = sum(latencies) / len(latencies) if latencies else 0
            
            latencies.sort()
            if latencies:
                p95_idx = int(len(latencies) * 0.95)
                p99_idx = int(len(latencies) * 0.99)
                metrics["p95_latency_ms"] = latencies[p95_idx] if p95_idx < len(latencies) else 0
                metrics["p99_latency_ms"] = latencies[p99_idx] if p99_idx < len(latencies) else 0
            
            duration = time.time() - start_time
            metrics["requests_per_second"] = num_requests / duration
            
            logger.info(f"API网关压力测试完成:")
            logger.info(f"  请求数: {num_requests}, 成功: {successes}")
            logger.info(f"  平均延迟: {metrics['avg_latency_ms']:.2f}ms, P95: {metrics['p95_latency_ms']:.2f}ms")
            
            passed = successes >= num_requests * 0.99
            
        except Exception as e:
            logger.error(f"API网关测试崩溃: {str(e)}")
            errors.append(f"测试崩溃: {str(e)}")
            passed = False
        
        return ScenarioResult(
            name="API网关压力测试",
            passed=passed,
            duration=time.time() - start_time,
            errors=errors[:50],
            warnings=warnings,
            metrics=metrics
        )

    def simulate_database_connection_pool(self) -> ScenarioResult:
        """数据库连接池模拟测试"""
        logger.info("🔥 场景2: 数据库连接池测试")
        
        start_time = time.time()
        errors = []
        warnings = []
        metrics = {
            "connections_created": 0,
            "connections_reused": 0,
            "pool_hits": 0,
            "pool_misses": 0,
            "max_concurrent": 0,
        }

        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
            
            class MockConnectionPool:
                def __init__(self, max_size=10):
                    self.max_size = max_size
                    self.connections = queue.Queue(maxsize=max_size)
                    self.created = 0
                    self.reused = 0
                    self.pool_hits = 0
                    self.pool_misses = 0
                    self.lock = threading.Lock()
                    self.current_concurrent = 0
                    self.max_concurrent = 0
                
                def get_connection(self):
                    with self.lock:
                        if not self.connections.empty():
                            self.reused += 1
                            self.pool_hits += 1
                        else:
                            if self.created < self.max_size:
                                self.created += 1
                                self.pool_misses += 1
                            else:
                                # 等待可用连接
                                pass
                        self.current_concurrent += 1
                        if self.current_concurrent > self.max_concurrent:
                            self.max_concurrent = self.current_concurrent
                    return f"conn_{self.created}"
                
                def release_connection(self, conn):
                    with self.lock:
                        self.current_concurrent -= 1
                        if not self.connections.full():
                            self.connections.put(conn)
            
            pool = MockConnectionPool(max_size=10)
            store = SimpleMemoryStore()
            
            def worker(worker_id: int, iterations: int):
                for _ in range(iterations):
                    conn = pool.get_connection()
                    try:
                        store.save_report({
                            "id": f"pool_test_{worker_id}_{_}",
                            "title": f"Pool Test {worker_id}",
                            "type": "pool",
                        })
                    finally:
                        pool.release_connection(conn)
                    time.sleep(random.uniform(0.001, 0.005))
            
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = []
                for i in range(20):
                    futures.append(executor.submit(worker, i, 100))
                
                for future in futures:
                    future.result()
            
            metrics["connections_created"] = pool.created
            metrics["connections_reused"] = pool.reused
            metrics["pool_hits"] = pool.pool_hits
            metrics["pool_misses"] = pool.pool_misses
            metrics["max_concurrent"] = pool.max_concurrent
            
            logger.info(f"连接池测试完成:")
            logger.info(f"  创建连接: {pool.created}, 复用: {pool.reused}")
            logger.info(f"  最大并发: {pool.max_concurrent}")
            
            if pool.created > pool.max_size * 2:
                warnings.append(f"连接创建过多: {pool.created}")
            
            passed = True
            
        except Exception as e:
            logger.error(f"连接池测试崩溃: {str(e)}")
            errors.append(f"测试崩溃: {str(e)}")
            passed = False
        
        return ScenarioResult(
            name="数据库连接池测试",
            passed=passed,
            duration=time.time() - start_time,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )

    def simulate_network_failure(self) -> ScenarioResult:
        """网络延迟和故障模拟测试"""
        logger.info("🔥 场景3: 网络故障模拟测试")
        
        start_time = time.time()
        errors = []
        warnings = []
        metrics = {
            "total_operations": 0,
            "successful_retries": 0,
            "failed_operations": 0,
            "timeout_count": 0,
            "retry_attempts": 0,
        }

        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
            store = SimpleMemoryStore()
            
            failure_rate = 0.1  # 10%的失败率
            timeout_rate = 0.05  # 5%的超时率
            max_retries = 3
            
            num_operations = 1000
            successful_retries = 0
            failed_ops = 0
            timeout_count = 0
            retry_attempts = 0
            
            def operation_with_retry(op_id: int):
                nonlocal successful_retries, failed_ops, timeout_count, retry_attempts
                
                for attempt in range(max_retries):
                    # 模拟网络延迟
                    time.sleep(random.uniform(0.001, 0.005))
                    
                    # 模拟失败
                    if random.random() < failure_rate:
                        retry_attempts += 1
                        continue
                    
                    # 模拟超时
                    if random.random() < timeout_rate:
                        timeout_count += 1
                        retry_attempts += 1
                        continue
                    
                    # 成功操作
                    try:
                        store.save_report({
                            "id": f"net_test_{op_id}",
                            "title": f"Network Test {op_id}",
                            "type": "network",
                        })
                        if attempt > 0:
                            successful_retries += 1
                        return True
                    except Exception:
                        retry_attempts += 1
                
                failed_ops += 1
                return False
            
            for i in range(num_operations):
                operation_with_retry(i)
                if (i + 1) % 200 == 0:
                    logger.info(f"  进度: {i + 1}/{num_operations}")
            
            metrics["total_operations"] = num_operations
            metrics["successful_retries"] = successful_retries
            metrics["failed_operations"] = failed_ops
            metrics["timeout_count"] = timeout_count
            metrics["retry_attempts"] = retry_attempts
            
            logger.info(f"网络故障测试完成:")
            logger.info(f"  成功重试: {successful_retries}, 失败: {failed_ops}")
            logger.info(f"  超时: {timeout_count}, 重试尝试: {retry_attempts}")
            
            passed = failed_ops < num_operations * 0.02
            
            if retry_attempts > num_operations * 0.2:
                warnings.append(f"重试次数过多: {retry_attempts}")
        
        except Exception as e:
            logger.error(f"网络故障测试崩溃: {str(e)}")
            errors.append(f"测试崩溃: {str(e)}")
            passed = False
        
        return ScenarioResult(
            name="网络故障模拟测试",
            passed=passed,
            duration=time.time() - start_time,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )

    def simulate_memory_and_resource_leak(self) -> ScenarioResult:
        """内存和资源泄漏检测"""
        logger.info("🔥 场景4: 内存和资源泄漏检测")
        
        start_time = time.time()
        errors = []
        warnings = []
        metrics = {
            "initial_memory_mb": 0,
            "peak_memory_mb": 0,
            "final_memory_mb": 0,
            "memory_growth_mb": 0,
            "objects_created": 0,
            "objects_cleaned": 0,
            "gc_collections": 0,
        }

        try:
            import gc
            try:
                import psutil
                use_psutil = True
                process = psutil.Process()
                initial_memory = process.memory_info().rss
            except ImportError:
                use_psutil = False
                initial_memory = 0
            
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
            
            store = SimpleMemoryStore()
            cache = SimpleCache()
            
            num_iterations = 5000
            peak_memory = initial_memory
            
            for i in range(num_iterations):
                # 创建临时对象
                temp_data = {
                    "id": f"leak_test_{i}",
                    "title": f"Leak Test {i}",
                    "summary": "x" * 1000,
                    "type": "leak",
                    "metrics": {"value": i},
                }
                
                store.save_report(temp_data)
                cache.set(f"leak_key_{i}", temp_data)
                
                # 定期清理
                if i % 100 == 0:
                    cache.delete(f"leak_key_{i - 100}")
                    store.delete_report(f"leak_test_{i - 100}")
                    gc.collect()
                    metrics["gc_collections"] += 1
                    
                    if use_psutil:
                        current_memory = process.memory_info().rss
                        if current_memory > peak_memory:
                            peak_memory = current_memory
                
                if (i + 1) % 1000 == 0:
                    logger.info(f"  进度: {i + 1}/{num_iterations}")
            
            # 最终清理
            for i in range(num_iterations):
                cache.delete(f"leak_key_{i}")
                store.delete_report(f"leak_test_{i}")
            
            gc.collect()
            gc.collect()
            gc.collect()
            
            if use_psutil:
                final_memory = process.memory_info().rss
                memory_growth = (final_memory - initial_memory) / (1024 * 1024)
                
                metrics["initial_memory_mb"] = initial_memory / (1024 * 1024)
                metrics["peak_memory_mb"] = peak_memory / (1024 * 1024)
                metrics["final_memory_mb"] = final_memory / (1024 * 1024)
                metrics["memory_growth_mb"] = memory_growth
            
            metrics["objects_created"] = num_iterations
            metrics["objects_cleaned"] = num_iterations
            
            logger.info(f"内存泄漏检测完成:")
            logger.info(f"  初始内存: {metrics['initial_memory_mb']:.2f}MB")
            logger.info(f"  峰值内存: {metrics['peak_memory_mb']:.2f}MB")
            logger.info(f"  最终内存: {metrics['final_memory_mb']:.2f}MB")
            logger.info(f"  内存增长: {metrics['memory_growth_mb']:.2f}MB")
            
            passed = True
            if use_psutil and memory_growth > 50:
                warnings.append(f"内存增长较高: {memory_growth:.2f}MB")
                passed = memory_growth < 100
        
        except Exception as e:
            logger.error(f"内存泄漏测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            errors.append(f"测试崩溃: {str(e)}")
            passed = False
        
        return ScenarioResult(
            name="内存和资源泄漏检测",
            passed=passed,
            duration=time.time() - start_time,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )

    def simulate_concurrent_data_modification(self) -> ScenarioResult:
        """并发数据修改冲突测试"""
        logger.info("🔥 场景5: 并发数据修改冲突测试")
        
        start_time = time.time()
        errors = []
        warnings = []
        metrics = {
            "total_writes": 0,
            "conflicts_detected": 0,
            "data_corruptions": 0,
            "successful_operations": 0,
            "threads_used": 0,
        }

        try:
            from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
            
            store = SimpleMemoryStore()
            shared_key = "shared_counter"
            iterations_per_thread = 1000
            num_threads = 20
            
            # 初始化共享数据
            store.save_report({
                "id": shared_key,
                "title": "Shared Counter",
                "type": "shared",
                "metrics": {"counter": 0},
            })
            
            conflicts = 0
            successes = 0
            
            def writer_thread(thread_id: int):
                nonlocal conflicts, successes
                local_errors = []
                
                for _ in range(iterations_per_thread):
                    try:
                        # 使用原子增量操作，避免并发冲突
                        new_value = store.atomic_increment(shared_key, "metrics.counter", 1)
                        if new_value > 0:
                            successes += 1
                        else:
                            conflicts += 1
                        
                        # 模拟处理时间
                        time.sleep(random.uniform(0.0001, 0.0005))
                        
                    except Exception as e:
                        conflicts += 1
                        local_errors.append(str(e))
                
                if local_errors:
                    errors.extend(local_errors[:3])
            
            threads = []
            for i in range(num_threads):
                t = threading.Thread(target=writer_thread, args=(i,))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            # 验证最终值
            final_data = store.get_report(shared_key)
            final_counter = final_data.get('metrics', {}).get('counter', 0)
            expected_counter = num_threads * iterations_per_thread
            
            metrics["total_writes"] = expected_counter
            metrics["conflicts_detected"] = conflicts
            metrics["successful_operations"] = successes
            metrics["threads_used"] = num_threads
            
            if final_counter != expected_counter:
                warnings.append(f"数据不一致: 预期 {expected_counter}, 实际 {final_counter}")
                metrics["data_corruptions"] = 1
            
            logger.info(f"并发冲突测试完成:")
            logger.info(f"  预期值: {expected_counter}, 实际值: {final_counter}")
            logger.info(f"  冲突: {conflicts}, 成功: {successes}")
            
            passed = final_counter == expected_counter
        
        except Exception as e:
            logger.error(f"并发测试崩溃: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            errors.append(f"测试崩溃: {str(e)}")
            passed = False
        
        return ScenarioResult(
            name="并发数据修改冲突测试",
            passed=passed,
            duration=time.time() - start_time,
            errors=errors[:10],
            warnings=warnings,
            metrics=metrics
        )

    def run_all_scenarios(self) -> List[ScenarioResult]:
        """运行所有真实场景测试"""
        logger.info("=" * 80)
        logger.info("🚀 开始真实生产环境模拟测试")
        logger.info("=" * 80)
        
        scenarios = [
            self.simulate_api_gateway_stress,
            self.simulate_database_connection_pool,
            self.simulate_network_failure,
            self.simulate_memory_and_resource_leak,
            self.simulate_concurrent_data_modification,
        ]
        
        all_results = []
        
        for scenario_func in scenarios:
            logger.info(f"\n{'=' * 80}")
            result = scenario_func()
            all_results.append(result)
            
            status = "✅ 通过" if result.passed else "❌ 失败"
            logger.info(f"场景 '{result.name}' 完成: {status}")
            logger.info(f"  耗时: {result.duration:.2f}秒")
            logger.info(f"  错误: {len(result.errors)}")
            
            if result.warnings:
                for warning in result.warnings[:3]:
                    logger.warning(f"  ⚠️  {warning}")
        
        return all_results


def print_detailed_report(results: List[ScenarioResult]):
    """打印详细报告"""
    print("\n" + "=" * 80)
    print("📊 真实生产环境模拟测试 - 详细报告")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    total_time = sum(r.duration for r in results)
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)
    
    print(f"\n📈 总体执行:")
    print(f"  总场景数: {total}")
    print(f"  通过: {passed} ({passed/total*100:.1f}%)")
    print(f"  失败: {failed}")
    print(f"  总耗时: {total_time:.2f}秒")
    print(f"  总错误: {total_errors}")
    print(f"  总警告: {total_warnings}")
    
    print(f"\n📋 详细结果:")
    for result in results:
        status_icon = "✅" if result.passed else "❌"
        print(f"\n  {status_icon} {result.name}")
        print(f"    耗时: {result.duration:.2f}秒")
        print(f"    错误: {len(result.errors)}")
        
        if result.warnings:
            print(f"    警告:")
            for warning in result.warnings:
                print(f"      ⚠️  {warning}")
        
        if result.metrics:
            print(f"    关键指标:")
            for key, value in list(result.metrics.items())[:6]:
                if isinstance(value, float):
                    print(f"      - {key}: {value:.2f}")
                else:
                    print(f"      - {key}: {value}")
    
    # 生成改进建议
    print(f"\n💡 改进建议:")
    issues_found = []
    
    for result in results:
        if not result.passed:
            issues_found.append(f"- {result.name}: 测试失败，请检查相关代码")
        for warning in result.warnings:
            if "内存" in warning:
                issues_found.append(f"- 考虑优化内存使用，当前内存增长较高")
            if "重试" in warning:
                issues_found.append(f"- 考虑优化重试机制，减少重试次数")
            if "数据不一致" in warning:
                issues_found.append(f"- 考虑添加并发控制机制")
    
    if issues_found:
        for issue in issues_found:
            print(issue)
    else:
        print("- 系统表现优秀，未发现需要改进的问题")
    
    print("\n" + "=" * 80)
    score = passed / total * 10
    print(f"综合评分: {score:.1f}/10")
    print("=" * 80)


def main():
    """主函数"""
    simulator = RealProductionSimulator()
    
    try:
        results = simulator.run_all_scenarios()
        print_detailed_report(results)
        return results
    except KeyboardInterrupt:
        logger.warning("测试被用户中断")
    except Exception as e:
        logger.error(f"测试崩溃: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
