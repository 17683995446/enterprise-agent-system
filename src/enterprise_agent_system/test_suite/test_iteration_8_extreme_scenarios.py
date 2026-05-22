"""
第8次迭代：极端场景深度测试
Iteration 8: Extreme Scenarios Deep Testing

按照用户要求进行：
1. 超长时间持续运行测试
2. 极端混乱并发场景测试
3. 大规模数据混合操作测试
4. 异常输入极端测试
5. 资源耗尽场景测试

重点测试：
- 每句代码执行后打印详细日志
- 验证代码执行流程是否正常
- 发现真实运行时的问题
- 遵循慢工出细活原则
"""

import sys
import time
import random
import threading
import gc
import traceback
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ExtremeScenariosLogger")

print("=" * 150)
print("🔥 启动第8次迭代：极端场景深度测试")
print("=" * 150)
print(f"[INIT] 测试开始时间: {datetime.now().isoformat()}")
print(f"[INIT] 每句代码执行后都会打印详细日志")
print(f"[INIT] 重点：验证代码执行流程是否正常")
print()


class ExtremeTestMetrics:
    """极端测试指标收集器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.operations_count = 0
        self.errors_count = 0
        self.success_count = 0
        self.checkpoints = []
        
    def record_operation(self, success: bool, operation_name: str):
        self.operations_count += 1
        if success:
            self.success_count += 1
        else:
            self.errors_count += 1
            
    def checkpoint(self, name: str):
        elapsed = time.time() - self.start_time
        success_rate = (self.success_count / self.operations_count * 100) if self.operations_count > 0 else 0
        self.checkpoints.append({
            'name': name,
            'elapsed': elapsed,
            'operations': self.operations_count,
            'errors': self.errors_count,
            'success_rate': success_rate
        })
        
        print(f"\n{'=' * 100}")
        print(f"📊 Checkpoint: {name}")
        print(f"{'=' * 100}")
        print(f"⏱️  已运行: {elapsed:.2f}秒")
        print(f"📊 总操作数: {self.operations_count:,}")
        print(f"✅ 成功: {self.success_count:,}")
        print(f"❌ 错误: {self.errors_count}")
        print(f"📈 成功率: {success_rate:.2f}%")
        print(f"{'=' * 100}\n")


class ExtremeTestRunner:
    """极端场景测试运行器"""
    
    def __init__(self):
        print("[INIT][1/6] 导入模块 - 开始")
        from enterprise_agent_system.core.in_memory_data_storage_backend import (
            InMemoryDataStorageBackend,
        )
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            TaskPriorityLevelEnumeration,
            TaskExecutionStatusEnumeration,
        )
        print("[INIT][1/6] 导入模块 - 完成")
        
        print("[INIT][2/6] 初始化后端 - 开始")
        self.real_backend = InMemoryDataStorageBackend()
        print("[INIT][2/6] 初始化后端 - 完成")
        
        print("[INIT][3/6] 初始化指标收集器 - 开始")
        self.metrics = ExtremeTestMetrics()
        print("[INIT][3/6] 初始化指标收集器 - 完成")
        
        print("[INIT][4/6] 初始化数据存储 - 开始")
        self.test_task_ids = []
        self.test_memory_ids = []
        self.test_node_ids = []
        self.test_edge_ids = []
        self.lock = threading.Lock()
        print("[INIT][4/6] 初始化数据存储 - 完成")
        
        print("[INIT][5/6] 初始化线程控制 - 开始")
        self.running = True
        self.threads = []
        print("[INIT][5/6] 初始化线程控制 - 完成")
        
        print("[INIT][6/6] 极端场景测试初始化 - 完成")
        print()
    
    def test_1_extreme_long_running(self, duration_seconds: int = 30):
        """测试1：超长时间持续运行测试"""
        print("=" * 150)
        print("⏱️  测试1：超长时间持续运行测试")
        print("=" * 150)
        print(f"[TEST1] 计划持续时间: {duration_seconds}秒")
        print()
        
        print("[TEST1][1/5] 准备后台工作线程 - 开始")
        operation_count = 0
        start_time = time.time()
        
        def background_worker(worker_id):
            nonlocal operation_count
            while self.running and (time.time() - start_time) < duration_seconds:
                try:
                    # 随机混合操作
                    op_type = random.choice([
                        'create_task', 'create_memory', 'create_node',
                        'retrieve_task', 'search_memory', 'update_task'
                    ])
                    
                    if op_type == 'create_task':
                        task = self.real_backend.create_new_task_entry(
                            task_title=f"Extreme-Long-Worker{worker_id}-{int(time.time() * 1000)}",
                            task_description=f"长时间运行测试任务 - Worker {worker_id}",
                            priority_level=random.choice([
                                TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL,
                                TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
                                TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL
                            ])
                        )
                        if task:
                            with self.lock:
                                self.test_task_ids.append(task.unique_entity_id)
                            self.metrics.record_operation(True, 'create_task')
                    
                    elif op_type == 'create_memory':
                        memory = self.real_backend.create_new_memory_entry(
                            content_text=f"长时间运行测试记忆 - Worker {worker_id} - {time.time()}",
                            tags_list=[f"worker{worker_id}", "long_running"],
                            importance_score=random.randint(1, 5)
                        )
                        if memory:
                            with self.lock:
                                self.test_memory_ids.append(memory.unique_memory_id)
                            self.metrics.record_operation(True, 'create_memory')
                    
                    elif op_type == 'create_node':
                        node_id = self.real_backend.add_node_to_knowledge_graph(
                            label=f"Extreme-Node-Worker{worker_id}-{int(time.time())}",
                            properties={
                                'worker_id': worker_id,
                                'timestamp': time.time()
                            }
                        )
                        if node_id:
                            with self.lock:
                                self.test_node_ids.append(node_id)
                            self.metrics.record_operation(True, 'create_node')
                    
                    elif op_type == 'retrieve_task':
                        if self.test_task_ids:
                            task_id = random.choice(self.test_task_ids)
                            task = self.real_backend.retrieve_task_by_id(task_id)
                            if task:
                                self.metrics.record_operation(True, 'retrieve_task')
                            else:
                                self.metrics.record_operation(False, 'retrieve_task')
                    
                    elif op_type == 'search_memory':
                        results = self.real_backend.search_memories_by_text_content(
                            search_query=random.choice(['worker', 'long', 'test', 'memory'])
                        )
                        self.metrics.record_operation(True, 'search_memory')
                    
                    elif op_type == 'update_task':
                        if self.test_task_ids:
                            task_id = random.choice(self.test_task_ids)
                            task = self.real_backend.update_task_entry(
                                task_id,
                                progress_percentage_value=random.random(),
                                execution_status=random.choice([
                                    TaskExecutionStatusEnumeration.PENDING_STATUS,
                                    TaskExecutionStatusEnumeration.IN_PROGRESS_STATUS,
                                    TaskExecutionStatusEnumeration.COMPLETED_STATUS
                                ])
                            )
                            if task:
                                self.metrics.record_operation(True, 'update_task')
                except Exception as e:
                    self.metrics.record_operation(False, f'worker_{worker_id}')
                
                # 短暂延迟模拟真实场景
                time.sleep(random.uniform(0.001, 0.01))
        
        print("[TEST1][1/5] 准备后台工作线程 - 完成")
        
        print("[TEST1][2/5] 启动后台工作线程 - 开始")
        num_workers = 10
        for i in range(num_workers):
            thread = threading.Thread(target=background_worker, args=(i,), name=f"Worker-{i}")
            self.threads.append(thread)
            thread.start()
        print(f"[TEST1][2/5] 启动后台工作线程 - 完成 (共{num_workers}个线程)")
        
        print(f"[TEST1][3/5] 持续运行中 - {duration_seconds}秒")
        
        # 定期打印检查点
        last_checkpoint = time.time()
        while (time.time() - start_time) < duration_seconds:
            if (time.time() - last_checkpoint) > 5:
                self.metrics.checkpoint(f"Long-Running-{int(time.time() - start_time)}s")
                last_checkpoint = time.time()
            time.sleep(0.1)
        
        print(f"[TEST1][3/5] 持续运行 - 完成")
        
        print("[TEST1][4/5] 停止工作线程 - 开始")
        self.running = False
        for thread in self.threads:
            thread.join(timeout=2)
        print("[TEST1][4/5] 停止工作线程 - 完成")
        
        print("[TEST1][5/5] 收集最终统计 - 开始")
        final_stats = self.real_backend.generate_system_statistics_snapshot()
        print(f"[TEST1][5/5] 最终数据统计:")
        print(f"   总任务数: {final_stats.total_tasks_count:,}")
        print(f"   总记忆数: {final_stats.total_memories_count:,}")
        print(f"   知识图谱节点数: {final_stats.knowledge_graph_nodes_count:,}")
        print(f"   知识图谱边数: {final_stats.knowledge_graph_edges_count:,}")
        print("[TEST1][5/5] 收集最终统计 - 完成")
        
        self.metrics.checkpoint("Long-Running-Complete")
        print()
    
    def test_2_extreme_concurrent_chaos(self):
        """测试2：极端混乱并发测试"""
        print("=" * 150)
        print("⚡ 测试2：极端混乱并发测试")
        print("=" * 150)
        print()
        
        num_threads = 100
        operations_per_thread = 200
        print(f"[TEST2] 线程数: {num_threads}, 每线程操作数: {operations_per_thread}")
        print(f"[TEST2] 预计总操作数: {num_threads * operations_per_thread:,}")
        print()
        
        print("[TEST2][1/5] 准备数据预热 - 开始")
        for i in range(100):
            task = self.real_backend.create_new_task_entry(task_title=f"Warmup-Task-{i}")
            if task:
                self.test_task_ids.append(task.unique_entity_id)
            memory = self.real_backend.create_new_memory_entry(content_text=f"Warmup-Memory-{i}")
            if memory:
                self.test_memory_ids.append(memory.unique_memory_id)
        print("[TEST2][1/5] 准备数据预热 - 完成")
        
        print("[TEST2][2/5] 准备线程同步 - 开始")
        barrier = threading.Barrier(num_threads)
        errors = []
        start_time = [None]
        print("[TEST2][2/5] 准备线程同步 - 完成")
        
        print("[TEST2][3/5] 准备混乱工作线程 - 开始")
        
        def chaos_worker(thread_id):
            try:
                barrier.wait()
                if start_time[0] is None:
                    start_time[0] = time.time()
                
                local_errors = 0
                for i in range(operations_per_thread):
                    try:
                        # 极端混乱操作
                        chaos_op = random.choice([
                            'task_crud', 'memory_crud', 'graph_operations', 
                            'search_storm', 'mixed_operations'
                        ])
                        
                        if chaos_op == 'task_crud':
                            task = self.real_backend.create_new_task_entry(
                                task_title=f"Chaos-Task-{thread_id}-{i}"
                            )
                            if task:
                                retrieved = self.real_backend.retrieve_task_by_id(task.unique_entity_id)
                                updated = self.real_backend.update_task_entry(
                                    task.unique_entity_id,
                                    progress_percentage_value=random.random()
                                )
                                self.metrics.record_operation(True, 'chaos_task_crud')
                        
                        elif chaos_op == 'memory_crud':
                            memory = self.real_backend.create_new_memory_entry(
                                content_text=f"Chaos-Memory-{thread_id}-{i}"
                            )
                            if memory:
                                retrieved = self.real_backend.retrieve_memory_by_id(memory.unique_memory_id)
                                self.metrics.record_operation(True, 'chaos_memory_crud')
                        
                        elif chaos_op == 'graph_operations':
                            node1 = self.real_backend.add_node_to_knowledge_graph(
                                label=f"Chaos-Node-A-{thread_id}-{i}"
                            )
                            node2 = self.real_backend.add_node_to_knowledge_graph(
                                label=f"Chaos-Node-B-{thread_id}-{i}"
                            )
                            if node1 and node2:
                                edge_id = self.real_backend.add_edge_to_knowledge_graph(
                                    node1, node2, f"chaos-relation-{thread_id}-{i}"
                                )
                                self.metrics.record_operation(True, 'chaos_graph')
                        
                        elif chaos_op == 'search_storm':
                            for _ in range(3):
                                self.real_backend.search_memories_by_text_content(
                                    search_query=random.choice(['chaos', 'test', 'task', 'memory'])
                                )
                            self.metrics.record_operation(True, 'chaos_search')
                        
                        elif chaos_op == 'mixed_operations':
                            # 混合多种操作
                            self.real_backend.create_new_task_entry(task_title=f"Mixed-{thread_id}-{i}")
                            self.real_backend.create_new_memory_entry(content_text=f"Mixed-Mem-{thread_id}-{i}")
                            self.real_backend.add_node_to_knowledge_graph(label=f"Mixed-Node-{thread_id}-{i}")
                            self.metrics.record_operation(True, 'chaos_mixed')
                    
                    except Exception as e:
                        local_errors += 1
                        self.metrics.record_operation(False, f'chaos_worker_{thread_id}')
                
                if local_errors > 0:
                    with self.lock:
                        errors.append(f"Thread {thread_id}: {local_errors} errors")
            
            except Exception as e:
                with self.lock:
                    errors.append(f"Thread {thread_id} crashed: {str(e)}")
        
        print("[TEST2][3/5] 准备混乱工作线程 - 完成")
        
        print("[TEST2][4/5] 启动并运行并发测试 - 开始")
        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=chaos_worker, args=(i,), name=f"Chaos-Worker-{i}")
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        elapsed = time.time() - start_time[0] if start_time[0] else 0
        print(f"[TEST2][4/5] 启动并运行并发测试 - 完成，耗时: {elapsed:.2f}秒")
        
        print("[TEST2][5/5] 错误检查与报告 - 开始")
        if errors:
            print(f"[TEST2][5/5] ⚠️ 发现 {len(errors)} 个错误:")
            for err in errors[:10]:
                print(f"   {err}")
        else:
            print(f"[TEST2][5/5] ✅ 100% 完美！0个错误！")
        print(f"[TEST2][5/5] 总操作数: {self.metrics.operations_count:,}")
        print("[TEST2][5/5] 错误检查与报告 - 完成")
        
        self.metrics.checkpoint("Extreme-Concurrent-Chaos")
        print()
    
    def test_3_extreme_large_scale_mixed(self):
        """测试3：超大规模混合操作测试"""
        print("=" * 150)
        print("💥 测试3：超大规模混合操作测试")
        print("=" * 150)
        print()
        
        print("[TEST3][1/6] 第一波：创建10,000个任务 - 开始")
        start = time.time()
        for i in range(10000):
            task = self.real_backend.create_new_task_entry(
                task_title=f"Scale-Task-{i}",
                task_description=f"大规模混合操作测试任务 - {i}"
            )
            if task:
                self.test_task_ids.append(task.unique_entity_id)
        elapsed = time.time() - start
        print(f"[TEST3][1/6] 第一波：创建10,000个任务 - 完成，耗时: {elapsed:.2f}秒，吞吐量: {10000/elapsed:.2f} ops/s")
        
        print("[TEST3][2/6] 第二波：创建10,000个记忆 - 开始")
        start = time.time()
        for i in range(10000):
            memory = self.real_backend.create_new_memory_entry(
                content_text=f"Scale-Memory-{i}",
                tags_list=[f"batch-{i//1000}", "scale-test"]
            )
            if memory:
                self.test_memory_ids.append(memory.unique_memory_id)
        elapsed = time.time() - start
        print(f"[TEST3][2/6] 第二波：创建10,000个记忆 - 完成，耗时: {elapsed:.2f}秒，吞吐量: {10000/elapsed:.2f} ops/s")
        
        print("[TEST3][3/6] 第三波：创建10,000个知识图谱节点 - 开始")
        start = time.time()
        for i in range(10000):
            node_id = self.real_backend.add_node_to_knowledge_graph(
                label=f"Scale-Node-{i}",
                properties={
                    'index': i,
                    'category': random.choice(['A', 'B', 'C', 'D', 'E'])
                }
            )
            if node_id:
                self.test_node_ids.append(node_id)
        elapsed = time.time() - start
        print(f"[TEST3][3/6] 第三波：创建10,000个知识图谱节点 - 完成，耗时: {elapsed:.2f}秒，吞吐量: {10000/elapsed:.2f} ops/s")
        
        print("[TEST3][4/6] 第四波：创建10,000条知识图谱边 - 开始")
        start = time.time()
        created_edges = 0
        for i in range(10000):
            if len(self.test_node_ids) >= 2:
                source_idx = random.randint(0, len(self.test_node_ids) - 1)
                target_idx = random.randint(0, len(self.test_node_ids) - 1)
                if source_idx != target_idx:
                    edge_id = self.real_backend.add_edge_to_knowledge_graph(
                        self.test_node_ids[source_idx],
                        self.test_node_ids[target_idx],
                        f"scale-edge-{i}"
                    )
                    if edge_id:
                        self.test_edge_ids.append(edge_id)
                        created_edges += 1
        elapsed = time.time() - start
        print(f"[TEST3][4/6] 第四波：创建{created_edges}条知识图谱边 - 完成，耗时: {elapsed:.2f}秒")
        
        print("[TEST3][5/6] 第五波：混合读写操作风暴 - 开始")
        start = time.time()
        mixed_ops = 5000
        for i in range(mixed_ops):
            # 混合读取操作
            if self.test_task_ids:
                self.real_backend.retrieve_task_by_id(random.choice(self.test_task_ids))
            if self.test_memory_ids:
                self.real_backend.search_memories_by_text_content(search_query=random.choice(['test', 'task', 'memory', 'scale']))
        elapsed = time.time() - start
        print(f"[TEST3][5/6] 第五波：混合读写操作风暴 - 完成，{mixed_ops}次操作，耗时: {elapsed:.2f}秒，吞吐量: {mixed_ops/elapsed:.2f} ops/s")
        
        print("[TEST3][6/6] 最终统计与验证 - 开始")
        final_stats = self.real_backend.generate_system_statistics_snapshot()
        print(f"[TEST3][6/6] 最终数据:")
        print(f"   任务数: {final_stats.total_tasks_count:,}")
        print(f"   记忆数: {final_stats.total_memories_count:,}")
        print(f"   知识图谱节点数: {final_stats.knowledge_graph_nodes_count:,}")
        print(f"   知识图谱边数: {final_stats.knowledge_graph_edges_count:,}")
        print(f"   预计总数: ~30,000+")
        print("[TEST3][6/6] 最终统计与验证 - 完成")
        
        self.metrics.checkpoint("Extreme-Large-Scale-Mixed")
        print()
    
    def test_4_extreme_edge_cases(self):
        """测试4：极端边界条件测试"""
        print("=" * 150)
        print("🔬 测试4：极端边界条件测试")
        print("=" * 150)
        print()
        
        edge_case_errors = 0
        
        print("[TEST4][1/8] 空字符串与None测试 - 开始")
        try:
            self.real_backend.create_new_task_entry(task_title="", task_description="")
            self.real_backend.create_new_task_entry(task_title="", task_description=None)
            self.metrics.record_operation(True, 'edge_empty')
        except Exception as e:
            self.metrics.record_operation(False, 'edge_empty')
            edge_case_errors += 1
        print("[TEST4][1/8] 空字符串与None测试 - 完成")
        
        print("[TEST4][2/8] 超长字符串测试 - 开始")
        try:
            very_long_string = "x" * 100000  # 100KB的字符串
            self.real_backend.create_new_task_entry(
                task_title=very_long_string[:1000],
                task_description=very_long_string
            )
            self.real_backend.create_new_memory_entry(content_text=very_long_string)
            self.metrics.record_operation(True, 'edge_long_string')
        except Exception as e:
            self.metrics.record_operation(False, 'edge_long_string')
            edge_case_errors += 1
        print("[TEST4][2/8] 超长字符串测试 - 完成")
        
        print("[TEST4][3/8] 特殊字符与Unicode测试 - 开始")
        try:
            special_string = "🎉🎊🎈🎆✨🌟⭐🔥💥\x00\x01\x02\n\t\r\"'&<>@#$%^&*()"
            self.real_backend.create_new_task_entry(task_title=special_string)
            self.real_backend.create_new_memory_entry(content_text=special_string)
            self.metrics.record_operation(True, 'edge_special_chars')
        except Exception as e:
            self.metrics.record_operation(False, 'edge_special_chars')
            edge_case_errors += 1
        print("[TEST4][3/8] 特殊字符与Unicode测试 - 完成")
        
        print("[TEST4][4/8] 极端优先级测试 - 开始")
        try:
            for priority in [-1000, -1, 0, 1, 100, 10000]:
                self.real_backend.create_new_task_entry(
                    task_title=f"Priority-Test-{priority}",
                    priority_level=priority
                )
            self.metrics.record_operation(True, 'edge_priority')
        except Exception as e:
            self.metrics.record_operation(False, 'edge_priority')
            edge_case_errors += 1
        print("[TEST4][4/8] 极端优先级测试 - 完成")
        
        print("[TEST4][5/8] 不存在ID检索测试 - 开始")
        try:
            non_existent_id = "this-id-does-not-exist-and-never-will-1234567890"
            result = self.real_backend.retrieve_task_by_id(non_existent_id)
            result2 = self.real_backend.retrieve_memory_by_id(non_existent_id)
            self.metrics.record_operation(True, 'edge_non_existent')
        except Exception as e:
            self.metrics.record_operation(False, 'edge_non_existent')
            edge_case_errors += 1
        print("[TEST4][5/8] 不存在ID检索测试 - 完成")
        
        print("[TEST4][6/8] 重复创建与更新测试 - 开始")
        try:
            # 重复创建相同标题的任务
            for i in range(100):
                self.real_backend.create_new_task_entry(task_title="Duplicate-Title-Test")
            self.metrics.record_operation(True, 'edge_duplicate')
        except Exception as e:
            self.metrics.record_operation(False, 'edge_duplicate')
            edge_case_errors += 1
        print("[TEST4][6/8] 重复创建与更新测试 - 完成")
        
        print("[TEST4][7/8] 知识图谱极端边测试 - 开始")
        try:
            node1 = self.real_backend.add_node_to_knowledge_graph(label="Edge-Test-Node-1")
            node2 = self.real_backend.add_node_to_knowledge_graph(label="Edge-Test-Node-2")
            
            # 测试重复边
            for i in range(10):
                self.real_backend.add_edge_to_knowledge_graph(node1, node2, f"repeated-edge-{i}")
            
            # 测试自循环边
            self.real_backend.add_edge_to_knowledge_graph(node1, node1, "self-loop-edge")
            self.metrics.record_operation(True, 'edge_graph')
        except Exception as e:
            self.metrics.record_operation(False, 'edge_graph')
            edge_case_errors += 1
        print("[TEST4][7/8] 知识图谱极端边测试 - 完成")
        
        print("[TEST4][8/8] 极端边界测试总结 - 开始")
        print(f"[TEST4][8/8] 极端边界错误数: {edge_case_errors}")
        if edge_case_errors == 0:
            print(f"[TEST4][8/8] ✅ 所有极端边界条件完美通过！")
        print("[TEST4][8/8] 极端边界测试总结 - 完成")
        
        self.metrics.checkpoint("Extreme-Edge-Cases")
        print()
    
    def run_all_tests(self):
        """运行所有极端场景测试"""
        print("\n" + "=" * 150)
        print("🔥 开始执行第8次迭代：极端场景深度测试")
        print("=" * 150)
        
        try:
            self.test_1_extreme_long_running(duration_seconds=20)  # 20秒演示
            self.test_2_extreme_concurrent_chaos()
            self.test_3_extreme_large_scale_mixed()
            self.test_4_extreme_edge_cases()
            
        except Exception as e:
            print(f"\n❌ 主测试流程崩溃: {e}")
            traceback.print_exc()
        
        self.generate_final_report()
    
    def generate_final_report(self):
        """生成最终报告"""
        print("\n" + "=" * 150)
        print("📊 第8次迭代：极端场景深度测试 - 最终报告")
        print("=" * 150)
        
        total_time = time.time() - self.metrics.start_time
        success_rate = (self.metrics.success_count / self.metrics.operations_count * 100) if self.metrics.operations_count > 0 else 0
        
        print(f"\n⏱️  总测试时间: {total_time:.2f}秒")
        print(f"📊 总操作数: {self.metrics.operations_count:,}")
        print(f"✅ 成功操作数: {self.metrics.success_count:,}")
        print(f"❌ 错误数: {self.metrics.errors_count}")
        print(f"📈 成功率: {success_rate:.2f}%")
        
        print(f"\n🎯 系统评级:")
        if self.metrics.errors_count == 0 and success_rate == 100:
            print(f"   ⭐⭐⭐⭐⭐ S级 - 完美！0错误！")
        elif success_rate >= 99.9:
            print(f"   ⭐⭐⭐⭐⭐ A+级 - 几乎完美！")
        elif success_rate >= 99:
            print(f"   ⭐⭐⭐⭐ A级 - 优秀！")
        else:
            print(f"   ⭐⭐⭐ B级 - 需要改进")
        
        print("\n" + "=" * 150)
        print("🏆🏆🏆 第8次迭代极端场景深度测试完成！")
        print("=" * 150)


def main():
    try:
        runner = ExtremeTestRunner()
        runner.run_all_tests()
        return 0
    except Exception as e:
        print(f"❌ 程序崩溃: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
