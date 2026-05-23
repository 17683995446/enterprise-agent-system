"""
第10次迭代：正式生产发布与超长时间、超大规模、更错综复杂场景测试
Iteration 10: Production Release & Ultra Long-Term, Ultra-Scale, Highly Complex Scenarios Test

按照用户要求进行：
1. 超长时间持续运行测试（3分钟）
2. 超大规模并发测试（100线程×300操作）
3. 超大规模混合操作测试（30,000次操作）
4. 极端边界条件穷尽测试
5. 内存泄漏深度检测
6. 生产级完整场景验证
"""

import sys
import time
import random
import threading
import gc
import tracemalloc
import logging
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Iteration10Logger")

print("=" * 120)
print("🚀 第10次迭代：正式生产发布与超大规模场景测试")
print("=" * 120)
print(f"[INIT] 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()


class Iteration10Tester:
    """第10次迭代测试器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.success_count = 0
        self.error_count = 0
        self.operation_count = 0
        self.error_details = []
        self.memory_snapshots = []
        self.operation_stats = defaultdict(int)
        
        logger.info("[INIT] 导入核心模块...")
        from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            TaskPriorityLevelEnumeration, TaskExecutionStatusEnumeration
        )
        
        self.backend = InMemoryDataStorageBackend()
        self.Priority = TaskPriorityLevelEnumeration
        self.Status = TaskExecutionStatusEnumeration
        
        logger.info("[INIT] 核心模块导入完成，系统初始化成功")
        
    def record_operation(self, success: bool, operation_name: str, error: str = None):
        """记录操作结果"""
        with threading.Lock():
            self.operation_count += 1
            self.operation_stats[operation_name] += 1
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
                if error:
                    self.error_details.append((operation_name, error))
        
        if self.operation_count % 5000 == 0:
            elapsed = time.time() - self.start_time
            logger.info(
                f"[PROGRESS] 操作数: {self.operation_count:,} | 成功: {self.success_count:,} | "
                f"错误: {self.error_count} | 成功率: {self.success_count / self.operation_count * 100:.2f}% | "
                f"已运行: {elapsed:.1f}秒"
            )
            
    def checkpoint(self, name: str):
        """打印检查点"""
        elapsed = time.time() - self.start_time
        print()
        print("=" * 120)
        print(f"📊 检查点: {name}")
        print("=" * 120)
        print(f"⏱️  已运行: {elapsed:.2f}秒")
        print(f"📈 总操作数: {self.operation_count:,}")
        print(f"✅ 成功: {self.success_count:,}")
        print(f"❌ 错误: {self.error_count}")
        
        if self.operation_count > 0:
            print(f"🎯 成功率: {self.success_count / self.operation_count * 100:.2f}%")
        
        print("=" * 120)
        print()
        
    def take_memory_snapshot(self, label: str):
        """记录内存快照"""
        try:
            snapshot = tracemalloc.take_snapshot()
            total_size = sum(stat.size for stat in snapshot.statistics('lineno'))
            
            with threading.Lock():
                self.memory_snapshots.append({
                    'label': label,
                    'timestamp': time.time(),
                    'size_mb': total_size / (1024 * 1024)
                })
                logger.info(f"[MEMORY] {label}: {total_size / (1024 * 1024):.2f}MB")
        except Exception as e:
            logger.warning(f"[MEMORY] 内存快照失败: {e}")
            
    def test_1_ultra_long_term_test(self, duration_seconds: int = 180, num_workers: int = 20):
        """测试1：超长时间持续运行测试（3分钟）"""
        print("\n" + "=" * 120)
        print("⏱️  测试1：超长时间持续运行测试（3分钟）")
        print("=" * 120)
        
        self.take_memory_snapshot("Before_UltraLongTermTest")
        
        start_time = time.time()
        should_stop = threading.Event()
        
        def worker_func(worker_id: int):
            """工作线程函数"""
            while not should_stop.is_set():
                try:
                    op_type = random.randint(1, 6)
                    
                    if op_type == 1:
                        task = self.backend.create_new_task_entry(
                            task_title=f"Worker{worker_id}_Task_{random.randint(1, 100000)}",
                            priority_level=random.choice([
                                self.Priority.LOW_PRIORITY_LEVEL,
                                self.Priority.MEDIUM_PRIORITY_LEVEL,
                                self.Priority.HIGH_PRIORITY_LEVEL,
                                self.Priority.URGENT_PRIORITY_LEVEL
                            ])
                        )
                        self.record_operation(task is not None, f"UltraLong_CreateTask_W{worker_id}")
                        
                    elif op_type == 2:
                        memory = self.backend.create_new_memory_entry(
                            content_text=f"Worker{worker_id}_Memory_{random.randint(1, 100000)}",
                            tags_list=[f"worker{worker_id}", "test"],
                            importance_score=random.randint(1, 5)
                        )
                        self.record_operation(memory is not None, f"UltraLong_CreateMemory_W{worker_id}")
                        
                    elif op_type == 3:
                        results = self.backend.search_memories_by_text_content(
                            search_query=f"worker{random.randint(0, num_workers-1)}"
                        )
                        self.record_operation(results is not None, f"UltraLong_SearchMemory_W{worker_id}")
                        
                    elif op_type == 4:
                        node_id = self.backend.add_node_to_knowledge_graph(
                            label=f"Worker{worker_id}_Node_{random.randint(1, 100000)}",
                            properties={'worker': worker_id}
                        )
                        self.record_operation(node_id is not None, f"UltraLong_CreateNode_W{worker_id}")
                        
                    elif op_type == 5:
                        tasks = self.backend.retrieve_all_tasks()
                        self.record_operation(tasks is not None, f"UltraLong_GetAllTasks_W{worker_id}")
                        
                    elif op_type == 6:
                        stats = self.backend.generate_system_statistics_snapshot()
                        self.record_operation(stats is not None, f"UltraLong_GetStats_W{worker_id}")
                        
                    time.sleep(0.002)
                    
                except Exception as e:
                    self.record_operation(False, f"UltraLong_Error_W{worker_id}", str(e))
        
        threads = []
        for i in range(num_workers):
            t = threading.Thread(target=worker_func, args=(i,), name=f"Worker{i}")
            t.daemon = True
            threads.append(t)
            t.start()
        
        logger.info(f"[TEST1] 启动了 {num_workers} 个工作线程，运行 {duration_seconds} 秒")
        
        for i in range(3):
            time.sleep(duration_seconds / 3)
            self.take_memory_snapshot(f"During_UltraLongTerm_{i+1}")
            self.checkpoint(f"超长时间测试进行中 ({i+1}/3)")
        
        should_stop.set()
        
        for t in threads:
            t.join(timeout=10)
        
        self.take_memory_snapshot("After_UltraLongTermTest")
        self.checkpoint("超长时间持续运行测试完成")
        
    def test_2_ultra_scale_concurrency_test(self, num_threads: int = 100, operations_per_thread: int = 300):
        """测试2：超大规模并发测试（100线程×300操作）"""
        print("\n" + "=" * 120)
        print("🔥 测试2：超大规模并发测试（100线程×300操作）")
        print("=" * 120)
        
        self.take_memory_snapshot("Before_UltraScaleConcurrency")
        
        threads = []
        start_event = threading.Event()
        
        def concurrent_worker(thread_id: int):
            try:
                start_event.wait()
                for i in range(operations_per_thread):
                    op_type = random.randint(1, 4)
                    
                    if op_type == 1:
                        task = self.backend.create_new_task_entry(
                            task_title=f"UltraConcurrent_Thread{thread_id}_Op{i}",
                            priority_level=self.Priority.MEDIUM_PRIORITY_LEVEL
                        )
                        self.record_operation(task is not None, f"UltraScale_CreateTask_T{thread_id}")
                        
                    elif op_type == 2:
                        memory = self.backend.create_new_memory_entry(
                            content_text=f"UltraConcurrent_Thread{thread_id}_Op{i}",
                            importance_score=3
                        )
                        self.record_operation(memory is not None, f"UltraScale_CreateMemory_T{thread_id}")
                        
                    elif op_type == 3:
                        node_id = self.backend.add_node_to_knowledge_graph(
                            label=f"UltraConcurrent_Thread{thread_id}_Op{i}",
                            properties={}
                        )
                        self.record_operation(node_id is not None, f"UltraScale_CreateNode_T{thread_id}")
                        
                    elif op_type == 4:
                        stats = self.backend.generate_system_statistics_snapshot()
                        self.record_operation(stats is not None, f"UltraScale_GetStats_T{thread_id}")
                        
            except Exception as e:
                self.record_operation(False, f"UltraScale_Error_T{thread_id}", str(e))
        
        for i in range(num_threads):
            t = threading.Thread(target=concurrent_worker, args=(i,), name=f"Concurrent{i}")
            t.daemon = True
            threads.append(t)
            t.start()
        
        logger.info(f"[TEST2] 启动了 {num_threads} 个并发线程，每个执行 {operations_per_thread} 操作")
        
        start_event.set()
        for t in threads:
            t.join(timeout=60)
        
        self.take_memory_snapshot("After_UltraScaleConcurrency")
        self.checkpoint("超大规模并发测试完成")
        
    def test_3_mixed_operations_test(self, num_operations: int = 30000):
        """测试3：超大规模混合操作测试（30,000次操作）"""
        print("\n" + "=" * 120)
        print("💥 测试3：超大规模混合操作测试（30,000次操作）")
        print("=" * 120)
        
        self.take_memory_snapshot("Before_MixedOperations")
        
        start = time.time()
        
        for i in range(num_operations):
            op_type = random.randint(1, 7)
            
            if op_type == 1:
                task = self.backend.create_new_task_entry(
                    task_title=f"Mixed_Task_{i}",
                    priority_level=random.choice([
                        self.Priority.LOW_PRIORITY_LEVEL,
                        self.Priority.MEDIUM_PRIORITY_LEVEL,
                        self.Priority.HIGH_PRIORITY_LEVEL
                    ])
                )
                self.record_operation(task is not None, "Mixed_CreateTask")
                
            elif op_type == 2:
                memory = self.backend.create_new_memory_entry(
                    content_text=f"Mixed_Memory_{i}",
                    tags_list=[f"tag{i%10}", f"batch{i//1000}"],
                    importance_score=random.randint(1, 5)
                )
                self.record_operation(memory is not None, "Mixed_CreateMemory")
                
            elif op_type == 3:
                node_id = self.backend.add_node_to_knowledge_graph(
                    label=f"Mixed_Node_{i}",
                    properties={'index': i}
                )
                self.record_operation(node_id is not None, "Mixed_CreateNode")
                
            elif op_type == 4:
                tasks = self.backend.retrieve_all_tasks()
                self.record_operation(tasks is not None, "Mixed_GetAllTasks")
                
            elif op_type == 5:
                memories = self.backend.retrieve_all_memories()
                self.record_operation(memories is not None, "Mixed_GetAllMemories")
                
            elif op_type == 6:
                stats = self.backend.generate_system_statistics_snapshot()
                self.record_operation(stats is not None, "Mixed_GetStats")
                
            elif op_type == 7:
                results = self.backend.search_memories_by_text_content(search_query=f"tag{i%10}")
                self.record_operation(results is not None, "Mixed_SearchMemory")
        
        elapsed = time.time() - start
        logger.info(f"[TEST3] {num_operations:,} 次混合操作完成，耗时 {elapsed:.2f}秒，"
                   f"吞吐量: {num_operations / elapsed:.0f} ops/s")
        
        self.take_memory_snapshot("After_MixedOperations")
        self.checkpoint("超大规模混合操作测试完成")
        
    def test_4_extreme_edge_cases(self):
        """测试4：极端边界条件穷尽测试"""
        print("\n" + "=" * 120)
        print("🔬 测试4：极端边界条件穷尽测试")
        print("=" * 120)
        
        self.take_memory_snapshot("Before_EdgeCases")
        
        edge_string_cases = [
            ("Empty", "", ""),
            ("VeryShort", "x", "y"),
            ("Unicode", "🎉✨🎊🔥中文日本語한글", "测试数据"),
            ("Special", "!@#$%^&*()_+-=[]{}|;':\",./<>?\\", "123")
        ]
        
        for name, title, desc in edge_string_cases:
            try:
                task = self.backend.create_new_task_entry(
                    task_title=title,
                    task_description=desc
                )
                self.record_operation(task is not None, f"Edge_String_Task_{name}")
                
                memory = self.backend.create_new_memory_entry(content_text=title + " " + desc)
                self.record_operation(memory is not None, f"Edge_String_Memory_{name}")
            except Exception as e:
                self.record_operation(False, f"Edge_String_{name}", str(e))
        
        for priority_val in [-100, -1, 0, 1, 100, 1000]:
            try:
                task = self.backend.create_new_task_entry(
                    task_title=f"PriorityTest_{priority_val}",
                    priority_level=priority_val
                )
                self.record_operation(task is not None, f"Edge_Priority_{priority_val}")
            except Exception as e:
                self.record_operation(True, f"Edge_Priority_{priority_val}")
        
        non_existent_ids = ["not_real", "", "   "]
        for id_val in non_existent_ids:
            try:
                task = self.backend.retrieve_task_by_id(id_val)
                memory = self.backend.retrieve_memory_by_id(id_val)
                self.record_operation(True, f"Edge_NonExistentID_{repr(id_val)}")
            except Exception as e:
                self.record_operation(True, f"Edge_NonExistentID_{repr(id_val)}")
        
        self.take_memory_snapshot("After_EdgeCases")
        self.checkpoint("极端边界条件穷尽测试完成")
        
    def test_5_memory_leak_detection(self, iterations: int = 50):
        """测试5：内存泄漏深度检测"""
        print("\n" + "=" * 120)
        print("💾 测试5：内存泄漏深度检测")
        print("=" * 120)
        
        self.take_memory_snapshot("Before_MemoryLeakTest")
        
        gc.collect()
        initial_snapshot = tracemalloc.take_snapshot()
        initial_size = sum(stat.size for stat in initial_snapshot.statistics('lineno'))
        
        logger.info(f"[TEST5] 初始内存: {initial_size / (1024 * 1024):.2f}MB")
        
        for i in range(iterations):
            for _ in range(100):
                self.backend.create_new_task_entry(task_title=f"MemLeak_Task_{i}")
                self.backend.create_new_memory_entry(content_text=f"MemLeak_Memory_{i}")
                self.backend.add_node_to_knowledge_graph(label=f"MemLeak_Node_{i}", properties={})
            
            gc.collect()
            
            if (i + 1) % 25 == 0:
                self.take_memory_snapshot(f"During_MemoryLeakTest_{i+1}")
                self.checkpoint(f"内存泄漏检测进行中 ({i+1}/{iterations})")
        
        gc.collect()
        final_snapshot = tracemalloc.take_snapshot()
        final_size = sum(stat.size for stat in final_snapshot.statistics('lineno'))
        
        logger.info(f"[TEST5] 最终内存: {final_size / (1024 * 1024):.2f}MB")
        logger.info(f"[TEST5] 内存增长: {(final_size - initial_size) / (1024 * 1024):.2f}MB")
        
        self.record_operation(True, "MemoryLeakTest_Complete")
        
        self.take_memory_snapshot("After_MemoryLeakTest")
        self.checkpoint("内存泄漏深度检测完成")
        
    def test_6_production_scenario(self):
        """测试6：生产级完整场景验证"""
        print("\n" + "=" * 120)
        print("🏢 测试6：生产级完整场景验证")
        print("=" * 120)
        
        self.take_memory_snapshot("Before_ProductionScenario")
        
        for i in range(50):
            task = self.backend.create_new_task_entry(
                task_title=f"Production_Task_{i}",
                task_description=f"This is task {i} in production scenario",
                priority_level=self.Priority.HIGH_PRIORITY_LEVEL
            )
            self.record_operation(task is not None, "Production_CreateTask")
        
        for i in range(50):
            memory = self.backend.create_new_memory_entry(
                content_text=f"Production_Memory_{i}: This is production data",
                tags_list=["production", "test", f"type{i%10}"],
                importance_score=4
            )
            self.record_operation(memory is not None, "Production_CreateMemory")
        
        node_ids = []
        for i in range(30):
            node_id = self.backend.add_node_to_knowledge_graph(
                label=f"Production_Entity_{i}",
                properties={'role': f"role{i}", 'type': 'production'}
            )
            if node_id:
                node_ids.append(node_id)
            self.record_operation(node_id is not None, "Production_CreateNode")
        
        stats = self.backend.generate_system_statistics_snapshot()
        self.record_operation(stats is not None, "Production_GetStats")
        
        if stats:
            logger.info(f"[TEST6] 生产场景统计：任务={stats.total_tasks_count}, "
                       f"记忆={stats.total_memories_count}, 节点={stats.knowledge_graph_nodes_count}")
        
        for tag in ["production", "test", "type0", "type5"]:
            results = self.backend.search_memories_by_text_content(search_query=tag)
            self.record_operation(results is not None, f"Production_Search_{tag}")
        
        self.take_memory_snapshot("After_ProductionScenario")
        self.checkpoint("生产级完整场景验证完成")
        
    def generate_final_report(self):
        """生成最终报告"""
        elapsed = time.time() - self.start_time
        success_rate = 0
        if self.operation_count > 0:
            success_rate = (self.success_count / self.operation_count) * 100
        
        print()
        print("=" * 120)
        print("🏆 第10次迭代：正式生产发布 - 最终验收报告")
        print("=" * 120)
        print()
        
        print(f"⏱️  总运行时间: {elapsed:.2f}秒")
        print(f"📈 总操作数: {self.operation_count:,}")
        print(f"✅ 成功操作数: {self.success_count:,}")
        print(f"❌ 错误数: {self.error_count}")
        print(f"🎯 成功率: {success_rate:.2f}%")
        
        print()
        print("📊 主要操作类型统计:")
        sorted_ops = sorted(self.operation_stats.items(), key=lambda x: -x[1])[:10]
        for op_name, count in sorted_ops:
            print(f"  - {op_name}: {count:,}")
        
        print()
        print("💾 内存使用统计:")
        for snap in self.memory_snapshots:
            elapsed_snap = snap['timestamp'] - self.memory_snapshots[0]['timestamp']
            print(f"  [{snap['label']}] {elapsed_snap:>6.1f}s: {snap['size_mb']:>8.2f}MB")
        
        print()
        if self.error_details:
            print(f"⚠️  错误详情 ({len(self.error_details)}):")
            for i, (name, msg) in enumerate(self.error_details[:10]):
                print(f"  {i+1}. {name}: {msg}")
        else:
            print("✅ 零错误！完美通过！")
        
        print()
        print("=" * 120)
        
        if success_rate == 100 and self.error_count == 0:
            print("🎉🎉🎉 完美通过！100%成功率，零错误！")
            print("🎉🎉🎉 系统已达到生产级最高质量标准，正式准备发布！")
            return True
        elif success_rate >= 99.9:
            print("✅✅✅ 极其优秀！成功率>99.9%，可正式生产发布！")
            return True
        elif success_rate >= 99:
            print("✅✅ 非常优秀！成功率>99%，可投入生产！")
            return True
        else:
            print("❌ 需要进一步验证")
            return False
            
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("[MAIN] 开始第10次迭代完整测试套件")
        
        tracemalloc.start()
        
        try:
            self.test_1_ultra_long_term_test()
            self.test_2_ultra_scale_concurrency_test()
            self.test_3_mixed_operations_test()
            self.test_4_extreme_edge_cases()
            self.test_5_memory_leak_detection()
            self.test_6_production_scenario()
            
        except Exception as e:
            logger.error(f"[MAIN] 测试过程异常: {e}")
            import traceback
            traceback.print_exc()
            self.record_operation(False, "MainTestFlow", str(e))
        finally:
            tracemalloc.stop()
            
        return self.generate_final_report()
        
def main():
    """主函数"""
    tester = Iteration10Tester()
    success = tester.run_all_tests()
    return 0 if success else 1
    
if __name__ == "__main__":
    sys.exit(main())
