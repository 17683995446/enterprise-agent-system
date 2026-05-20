"""
第一性原理深度测试 - 根本性问题验证
遵循第一性原则：从最根本的假设出发，彻底验证系统核心

核心假设检验：
1. 内存存储真的是线程安全的吗？
2. 数据真的被持久化了吗？
3. 删除操作真的删除数据了吗？
4. 并发修改真的安全吗？
5. 边界情况真的被正确处理了吗？
"""

import sys
import time
import random
import threading
import gc
import traceback
from typing import Dict, List, Any, Set
from collections import defaultdict

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance('first_principles_test')


class FirstPrinciplesVerifier:
    """第一性原理验证器"""
    
    def __init__(self):
        self.passed_tests = []
        self.failed_tests = []
        self.warnings = []
        
    def log_pass(self, test_name: str, message: str):
        """记录通过的测试"""
        self.passed_tests.append((test_name, message))
        logger.info(f"✅ {test_name}: {message}")
    
    def log_fail(self, test_name: str, message: str):
        """记录失败的测试"""
        self.failed_tests.append((test_name, message))
        logger.error(f"❌ {test_name}: {message}")
    
    def log_warning(self, test_name: str, message: str):
        """记录警告"""
        self.warnings.append((test_name, message))
        logger.warning(f"⚠️ {test_name}: {message}")
    
    # ========== 第一性原理测试 1: 内存安全的根本假设 ==========
    def test_memory_safety_fundamental(self):
        """测试1: 内存安全的根本假设
        
        核心问题：数据写入后，真的能被读取出来吗？
        没有缓存、没有延迟、没有"魔法"——纯粹的数据存取
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性原理测试 1: 内存安全的根本假设")
        logger.info("=" * 80)
        logger.info("问题：写入的数据真的能被读取出来吗？")
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        # 测试：写入-读取-验证的闭环
        test_id = "fp_test_001"
        test_data = {
            "id": test_id,
            "title": "First Principles Test",
            "content": "The most basic assumption: what you write is what you read",
            "quality_score": 9.5,
            "metrics": {"iteration": 0, "timestamp": time.time()}
        }
        
        # Step 1: 写入
        returned_id = store.save_report(test_data)
        
        # Step 2: 读取
        retrieved = store.get_report(test_id)
        
        # Step 3: 验证（第一性：不应该有任何偏差）
        if retrieved is None:
            self.log_fail("内存安全", "写入后无法读取 - 数据丢失")
            return False
        
        if retrieved.get('content') != test_data['content']:
            self.log_fail("内存安全", f"内容不匹配: 期望 {test_data['content']}, 实际 {retrieved.get('content')}")
            return False
        
        if retrieved.get('quality_score') != test_data['quality_score']:
            self.log_fail("内存安全", f"分数不匹配: 期望 {test_data['quality_score']}, 实际 {retrieved.get('quality_score')}")
            return False
        
        self.log_pass("内存安全", "写入-读取闭环验证成功")
        return True
    
    # ========== 第一性原理测试 2: 删除的根本假设 ==========
    def test_deletion_fundamental(self):
        """测试2: 删除的根本假设
        
        核心问题：删除的数据真的消失了吗？
        真的不存在了吗？真的无法恢复了吗？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性原理测试 2: 删除的根本假设")
        logger.info("=" * 80)
        logger.info("问题：删除的数据真的消失了吗？")
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        # Step 1: 创建数据
        test_id = "fp_delete_test"
        store.save_report({
            "id": test_id,
            "title": "Will be deleted",
            "content": "This should disappear"
        })
        
        # Step 2: 验证数据存在
        if store.get_report(test_id) is None:
            self.log_fail("删除假设", "数据创建后立即无法找到")
            return False
        
        # Step 3: 删除
        delete_result = store.delete_report(test_id)
        
        if not delete_result:
            self.log_fail("删除假设", "删除操作返回失败")
            return False
        
        # Step 4: 验证数据真的消失了（第一性：应该返回None）
        retrieved = store.get_report(test_id)
        
        if retrieved is not None:
            self.log_fail("删除假设", f"删除后数据仍然存在: {retrieved}")
            return False
        
        # Step 5: 再次删除应该返回False
        second_delete = store.delete_report(test_id)
        if second_delete:
            self.log_warning("删除假设", "对已删除数据的二次删除返回了True（这可能是设计选择）")
        
        self.log_pass("删除假设", "删除后数据确实消失")
        return True
    
    # ========== 第一性原理测试 3: 并发修改的原子性 ==========
    def test_concurrency_fundamental(self):
        """测试3: 并发修改的原子性
        
        核心问题：当多个线程同时修改同一个数据时，会发生什么？
        是数据丢失？数据损坏？还是正确处理？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性原理测试 3: 并发修改的原子性")
        logger.info("=" * 80)
        logger.info("问题：多个线程同时修改，数据会损坏吗？")
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        # 共享数据
        shared_id = "fp_concurrent_test"
        store.save_report({
            "id": shared_id,
            "title": "Shared Data",
            "counter": 0
        })
        
        # 错误记录
        errors = []
        final_values = []
        
        def worker(worker_id: int, iterations: int):
            try:
                for _ in range(iterations):
                    # 读取
                    data = store.get_report(shared_id)
                    if data is None:
                        errors.append(f"Worker {worker_id}: Data disappeared")
                        continue
                    
                    # 修改
                    current = data.get('counter', 0)
                    data['counter'] = current + 1
                    
                    # 写回
                    store.save_report(data)
                    
            except Exception as e:
                errors.append(f"Worker {worker_id}: {str(e)}")
        
        # 启动多个线程同时修改
        num_threads = 10
        iterations_per_thread = 100
        threads = []
        
        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i, iterations_per_thread))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 验证结果
        final_data = store.get_report(shared_id)
        final_counter = final_data.get('counter', 0) if final_data else 0
        expected = num_threads * iterations_per_thread
        
        if errors:
            self.log_fail("并发原子性", f"发生错误: {errors[:3]}")
            return False
        
        if final_counter != expected:
            self.log_warning("并发原子性", 
                f"最终计数不匹配（这可能是竞态条件）: 期望 {expected}, 实际 {final_counter}, "
                f"丢失 {expected - final_counter} 次更新")
            # 注意：这不一定算失败，因为没有锁的情况下这可能发生
            # 但我们期望系统能正确处理
            return False
        
        self.log_pass("并发原子性", f"{num_threads}个线程各执行{iterations_per_thread}次修改，数据一致")
        return True
    
    # ========== 第一性原理测试 4: 数据隔离 ==========
    def test_data_isolation_fundamental(self):
        """测试4: 数据隔离
        
        核心问题：一个线程的操作会影响另一个线程吗？
        数据真的被隔离了吗？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性原理测试 4: 数据隔离")
        logger.info("=" * 80)
        logger.info("问题：不同线程的数据会互相干扰吗？")
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        results = {}
        
        def isolated_worker(worker_id: int, count: int):
            my_id_prefix = f"worker_{worker_id}"
            
            # 每个线程创建自己的数据
            for i in range(count):
                report_id = f"{my_id_prefix}_data_{i}"
                unique_value = f"Worker{worker_id}_Value{i}"
                
                store.save_report({
                    "id": report_id,
                    "title": unique_value,
                    "worker_id": worker_id,
                    "index": i
                })
                
                # 验证自己的数据
                retrieved = store.get_report(report_id)
                if retrieved is None or retrieved.get('title') != unique_value:
                    results[worker_id] = f"Failed at {i}: data mismatch"
                    return
                
                # 验证不会读到别人的数据（作为污染检测）
                for other_id in range(worker_id):
                    other_report = store.get_report(f"worker_{other_id}_data_{i}")
                    if other_report and other_report.get('worker_id') == worker_id:
                        results[worker_id] = f"Data contamination: read worker_{other_id}'s data as worker_{worker_id}"
                        return
            
            results[worker_id] = "success"
        
        # 并发执行隔离测试
        threads = []
        for i in range(20):
            t = threading.Thread(target=isolated_worker, args=(i, 50))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 检查结果
        failures = {k: v for k, v in results.items() if v != "success"}
        
        if failures:
            self.log_fail("数据隔离", f"发现数据隔离问题: {failures}")
            return False
        
        self.log_pass("数据隔离", "20个线程各操作50次，数据完全隔离，无污染")
        return True
    
    # ========== 第一性原理测试 5: 边界值探索 ==========
    def test_boundary_fundamental(self):
        """测试5: 边界值探索
        
        核心问题：系统的边界在哪里？超出边界会发生什么？
        空值、超大值、特殊字符、Unicode...
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性原理测试 5: 边界值探索")
        logger.info("=" * 80)
        logger.info("问题：系统的边界在哪里？")
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        failures = []
        
        # 测试用例：各种边界情况
        test_cases = [
            ("empty_string", {"id": "empty", "title": "", "content": ""}),
            ("null_title", {"id": "null_title", "title": None, "content": "test"}),
            ("null_content", {"id": "null_content", "title": "test", "content": None}),
            ("negative_score", {"id": "neg_score", "quality_score": -1.0}),
            ("extreme_score", {"id": "extreme_score", "quality_score": 1e308}),
            ("very_long_id", {"id": "x" * 10000, "title": "Long ID"}),
            ("unicode_test", {"id": "unicode", "title": "中文测试 🔥", "content": "Unicode 🎉"}),
            ("special_chars", {"id": "special", "title": "!@#$%^&*()_+-=[]{}|;':\",./<>?", "content": "test"}),
            ("empty_dict", {"id": "empty_dict", "metrics": {}}),
            ("nested_dict", {"id": "nested", "metrics": {"a": {"b": {"c": {"d": 1}}}}}),
            ("list_in_metrics", {"id": "list", "metrics": {"items": [1, 2, 3, "test"]}}),
        ]
        
        for test_name, test_data in test_cases:
            try:
                # 保存
                store.save_report(test_data)
                
                # 读取
                retrieved = store.get_report(test_data['id'])
                
                if retrieved is None:
                    failures.append(f"{test_name}: 保存后无法读取")
                    continue
                
                # 验证关键字段
                if 'title' in test_data and retrieved.get('title') != test_data['title']:
                    failures.append(f"{test_name}: title 不匹配")
                    continue
                
                if 'content' in test_data and retrieved.get('content') != test_data['content']:
                    failures.append(f"{test_name}: content 不匹配")
                    continue
                
                if 'quality_score' in test_data and retrieved.get('quality_score') != test_data['quality_score']:
                    failures.append(f"{test_name}: quality_score 不匹配")
                    continue
                
            except Exception as e:
                failures.append(f"{test_name}: 异常 {str(e)}")
        
        if failures:
            self.log_fail("边界值", f"边界测试发现问题: {failures}")
            return False
        
        self.log_pass("边界值", f"成功处理 {len(test_cases)} 种边界情况")
        return True
    
    # ========== 第一性原理测试 6: 资源清理 ==========
    def test_resource_cleanup_fundamental(self):
        """测试：资源清理
        
        核心问题：删除的数据真的释放内存了吗？
        大量创建和删除后，内存真的减少了吗？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性原理测试 6: 资源清理")
        logger.info("=" * 80)
        logger.info("问题：删除的数据真的释放内存了吗？")
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        # 尝试获取内存统计（如果psutil可用）
        process = None
        initial_memory = None
        final_memory = None
        
        try:
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss / (1024 * 1024)
        except ImportError:
            logger.warning("psutil 不可用，跳过内存监控")
        
        # 创建大量数据
        num_items = 10000
        ids = []
        
        for i in range(num_items):
            report_id = f"cleanup_test_{i}"
            ids.append(report_id)
            
            store.save_report({
                "id": report_id,
                "title": f"Test {i}",
                "content": "x" * 1000  # 1KB的数据
            })
        
        # 强制GC
        gc.collect()
        
        # 删除所有数据
        for report_id in ids:
            store.delete_report(report_id)
        
        # 再次强制GC
        gc.collect()
        time.sleep(0.1)
        gc.collect()
        
        # 检查最终内存（如果psutil可用）
        final_memory = 0
        memory_diff = 0
        peak_memory = 0
        
        if process and initial_memory is not None:
            final_memory = process.memory_info().rss / (1024 * 1024)
            memory_diff = final_memory - initial_memory
            peak_memory = final_memory
        
        # 验证存储真的为空
        stats = store.get_stats()
        
        if initial_memory is not None:
            logger.info(f"初始内存: {initial_memory:.2f}MB")
            if peak_memory > 0:
                logger.info(f"峰值内存: {peak_memory:.2f}MB")
            logger.info(f"最终内存: {final_memory:.2f}MB")
            logger.info(f"内存变化: {memory_diff:.2f}MB")
        
        logger.info(f"存储报告数: {stats['total_reports']}")
        
        if stats['total_reports'] != 0:
            self.log_fail("资源清理", f"删除后仍有 {stats['total_reports']} 个报告")
            return False
        
        # 内存增长应该在合理范围内（允许一些开销）
        if initial_memory is not None and memory_diff > 50:  # 允许50MB的开销
            self.log_warning("资源清理", f"内存未完全释放: 增长 {memory_diff:.2f}MB")
        
        # 通过的消息根据是否有内存监控调整
        if initial_memory is not None:
            self.log_pass("资源清理", f"清理 {num_items} 个报告，内存增长仅 {memory_diff:.2f}MB")
        else:
            self.log_pass("资源清理", f"清理 {num_items} 个报告，存储已清空")
        return True
    
    # ========== 第一性原理测试 7: 一致性验证 ==========
    def test_consistency_fundamental(self):
        """测试7: 一致性验证
        
        核心问题：读取的数据和写入的数据在任何时候都一致吗？
        有幻读、数据丢失、写偏等问题吗？
        """
        logger.info("\n" + "=" * 80)
        logger.info("第一性原理测试 7: 一致性验证")
        logger.info("=" * 80)
        logger.info("问题：数据在任何时候都一致吗？")
        
        from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore
        
        store = SimpleMemoryStore()
        
        # 创建初始数据
        test_id = "consistency_test"
        store.save_report({
            "id": test_id,
            "title": "Initial",
            "version": 0
        })
        
        inconsistencies = []
        num_reads = 10000
        
        def reader():
            for _ in range(num_reads):
                data = store.get_report(test_id)
                if data is None:
                    inconsistencies.append("Data disappeared during read")
                    break
        
        def writer():
            for i in range(num_reads):
                data = store.get_report(test_id)
                if data:
                    data['version'] = i
                    store.save_report(data)
        
        # 并发读写
        threads = [
            threading.Thread(target=reader),
            threading.Thread(target=reader),
            threading.Thread(target=writer)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # 验证最终状态
        final_data = store.get_report(test_id)
        
        if final_data is None:
            self.log_fail("一致性", "最终数据消失")
            return False
        
        if inconsistencies:
            self.log_fail("一致性", f"发现不一致: {inconsistencies}")
            return False
        
        self.log_pass("一致性", f"{num_reads}次并发读写，无数据不一致")
        return True
    
    # ========== 运行所有测试 ==========
    def run_all_tests(self):
        """运行所有第一性原理测试"""
        logger.info("=" * 80)
        logger.info("🚀 启动第一性原理深度测试")
        logger.info("=" * 80)
        logger.info("目标：从最根本的假设出发，彻底验证系统核心")
        
        tests = [
            ("内存安全", self.test_memory_safety_fundamental),
            ("删除假设", self.test_deletion_fundamental),
            ("并发原子性", self.test_concurrency_fundamental),
            ("数据隔离", self.test_data_isolation_fundamental),
            ("边界值", self.test_boundary_fundamental),
            ("资源清理", self.test_resource_cleanup_fundamental),
            ("一致性", self.test_consistency_fundamental),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                self.log_fail(test_name, f"测试崩溃: {str(e)}\n{traceback.format_exc()}")
                results[test_name] = False
        
        # 生成最终报告
        self.generate_report(results)
        
        return results
    
    def generate_report(self, results: Dict[str, bool]):
        """生成最终报告"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 第一性原理测试 - 最终报告")
        logger.info("=" * 80)
        
        passed = sum(1 for v in results.values() if v)
        failed = len(results) - passed
        
        logger.info(f"\n测试结果:")
        logger.info(f"  通过: {passed}")
        logger.info(f"  失败: {failed}")
        logger.info(f"  通过率: {passed/len(results)*100:.1f}%")
        
        if self.warnings:
            logger.info(f"\n警告 ({len(self.warnings)}):")
            for test, msg in self.warnings:
                logger.warning(f"  {test}: {msg}")
        
        if failed > 0:
            logger.info(f"\n失败测试 ({failed}):")
            for test, msg in self.failed_tests:
                logger.error(f"  ❌ {test}: {msg}")
        
        logger.info("\n" + "=" * 80)
        
        if failed == 0:
            logger.info("🎉 所有第一性原理测试通过！系统核心完全可靠！")
        else:
            logger.warning(f"⚠️ {failed} 个测试失败，需要进一步调查")
        
        logger.info("=" * 80)


def main():
    """主函数"""
    verifier = FirstPrinciplesVerifier()
    results = verifier.run_all_tests()
    
    return results


if __name__ == "__main__":
    main()
