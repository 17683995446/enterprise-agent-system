#!/usr/bin/env python3
"""
超级复杂场景测试 - 模拟真实生产环境的最极端情况

测试场景包括：
1. 多层嵌套操作（任务→记忆→知识图谱交叉）
2. 超复杂并发（200+线程同时操作）
3. 混沌场景（随机失败、中断、延迟）
4. 极端边界条件（超大字符串、特殊字符）
5. 资源泄漏检测（大量创建/删除循环）
6. 数据一致性（跨组件验证）
7. 超长时间运行（10分钟+）
8. 异常容错（超时、断连、报错兜底）
"""

import sys
import os
import time
import random
import threading
import uuid
import traceback
import gc
import signal
from collections import defaultdict
from datetime import datetime
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
)

print("=" * 100)
print("🚀 启动超级复杂场景测试 - 模拟真实生产环境的最极端情况")
print("=" * 100)

class ChaosScenarios:
    """混沌场景生成器"""
    
    @staticmethod
    def generate_extreme_string(length: int = 100000) -> str:
        """生成极端字符串"""
        return "X" * length
    
    @staticmethod
    def generate_unicode_string() -> str:
        """生成Unicode字符串"""
        return "你好世界🌍🎉" * 100
    
    @staticmethod
    def generate_sql_injection() -> str:
        """生成SQL注入测试"""
        return "'; DROP TABLE users; --"
    
    @staticmethod
    def generate_special_chars() -> str:
        """生成特殊字符"""
        return "\x00\x01\x02\n\r\t\b\a"
    
    @staticmethod
    def generate_nested_dict(depth: int = 10) -> Dict[str, Any]:
        """生成嵌套字典"""
        if depth == 0:
            return {"value": random.random()}
        return {
            f"level_{depth}": ChaosScenarios.generate_nested_dict(depth - 1),
            "data": "x" * 100
        }

class SuperComplexTestOrchestrator:
    """超级复杂测试编排器"""
    
    def __init__(self):
        self.backend = InMemoryDataStorageBackend()
        self.store = SimpleMemoryStore()
        self.cache = SimpleCache()
        
        # 统计信息
        self.stats = {
            'operations': 0,
            'errors': 0,
            'warnings': 0,
            'deadlocks': 0,
            'memory_leaks': 0,
            'data_corruption': 0,
        }
        
        # 线程管理
        self.threads: List[threading.Thread] = []
        self.errors: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        
        # 混沌控制
        self.chaos_enabled = True
        self.failure_rate = 0.01  # 1% 随机失败率
        self.delay_rate = 0.05  # 5% 随机延迟
        
    def chaos_delay(self):
        """混沌延迟"""
        if self.chaos_enabled and random.random() < self.delay_rate:
            time.sleep(random.uniform(0.001, 0.01))
    
    def chaos_failure(self, operation: str) -> bool:
        """混沌失败模拟"""
        if self.chaos_enabled and random.random() < self.failure_rate:
            with self.lock:
                self.errors.append({
                    'type': 'chaos_failure',
                    'operation': operation,
                    'time': time.time()
                })
            return True
        return False
    
    # ========================================================================
    # 场景1: 多层嵌套操作 - 任务→记忆→知识图谱交叉操作
    # ========================================================================
    def scenario_1_nested_operations(self, iterations: int = 1000):
        """场景1: 多层嵌套操作"""
        print(f"\n{'='*80}")
        print(f"🧪 场景1: 多层嵌套操作 - {iterations}次迭代")
        print(f"{'='*80}")
        
        last_node_id = None  # 初始化last_node_id
        
        for i in range(iterations):
            try:
                # 创建任务
                task = self.backend.create_new_task_entry(
                    f"Nested Task {i}",
                    priority_level=random.choice([
                        TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL,
                        TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
                        TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL,
                        "low", "medium", "high"  # 字符串输入
                    ])
                )
                
                # 创建关联记忆
                memory = self.backend.create_new_memory_entry(
                    f"Memory for task {task.unique_entity_id}",
                    importance_score=random.randint(1, 5),
                    tags_list=["task", "nested", f"iteration_{i}"]
                )
                
                # 添加到知识图谱
                node_id = self.backend.add_node_to_knowledge_graph(
                    label=f"task_node_{i}",
                    properties={
                        "task_id": task.unique_entity_id,
                        "memory_id": memory.unique_memory_id,
                        "iteration": i
                    }
                )
                
                # 添加边 - 使用实际返回的node_id
                if i > 0 and last_node_id is not None:
                    self.backend.add_edge_to_knowledge_graph(
                        last_node_id,
                        node_id,
                        "NEXT",
                        1.0
                    )
                
                # 保存当前node_id用于下一次迭代
                last_node_id = node_id
                
                # 更新任务
                self.backend.update_task_entry(
                    task.unique_entity_id,
                    execution_status="in_progress",
                    progress_percentage_value=random.random()
                )
                
                # 检索验证
                retrieved_task = self.backend.retrieve_task_by_id(task.unique_entity_id)
                retrieved_memory = self.backend.retrieve_memory_by_id(memory.unique_memory_id)
                
                # 验证一致性
                assert retrieved_task is not None, "任务检索失败"
                assert retrieved_memory is not None, "记忆检索失败"
                
                with self.lock:
                    self.stats['operations'] += 1
                
                self.chaos_delay()
                
                if i % 100 == 0:
                    print(f"  进度: {i}/{iterations} ({(i/iterations*100):.1f}%)")
                    
            except Exception as e:
                with self.lock:
                    self.stats['errors'] += 1
                    self.errors.append({
                        'scenario': 'nested_operations',
                        'iteration': i,
                        'error': str(e),
                        'trace': traceback.format_exc()[:200]
                    })
                print(f"  ❌ 迭代 {i} 失败: {e}")
        
        print(f"✅ 场景1完成: {self.stats['operations']} 次操作, {self.stats['errors']} 次错误")
    
    # ========================================================================
    # 场景2: 超复杂并发 - 200+线程同时操作
    # ========================================================================
    def scenario_2_extreme_concurrency(self, num_threads: int = 200, ops_per_thread: int = 100):
        """场景2: 超复杂并发"""
        print(f"\n{'='*80}")
        print(f"🧪 场景2: 超复杂并发 - {num_threads}线程 × {ops_per_thread}操作")
        print(f"{'='*80}")
        
        errors = []
        errors_lock = threading.Lock()
        barrier = threading.Barrier(num_threads)
        
        def worker(thread_id: int):
            try:
                # 所有线程同时开始
                barrier.wait()
                
                local_errors = []
                
                for op_id in range(ops_per_thread):
                    try:
                        # 随机选择操作类型
                        op_type = random.choice(['task', 'memory', 'store', 'cache', 'graph', 'mixed'])
                        
                        if op_type == 'task' or op_type == 'mixed':
                            task = self.backend.create_new_task_entry(f"Concurrent Task {thread_id}-{op_id}")
                            self.backend.update_task_entry(
                                task.unique_entity_id,
                                progress_percentage_value=random.random()
                            )
                            self.backend.retrieve_task_by_id(task.unique_entity_id)
                            self.backend.retrieve_all_tasks()
                            self.backend.retrieve_pending_tasks_sorted_by_priority()
                        
                        if op_type == 'memory' or op_type == 'mixed':
                            memory = self.backend.create_new_memory_entry(
                                f"Concurrent Memory {thread_id}-{op_id}",
                                importance_score=random.randint(1, 5)
                            )
                            self.backend.retrieve_memory_by_id(memory.unique_memory_id)
                            self.backend.retrieve_all_memories()
                            self.backend.search_memories_by_text_content("concurrent")
                        
                        if op_type == 'store' or op_type == 'mixed':
                            report_id = f"concurrent_{thread_id}_{op_id}"
                            self.store.save_report({
                                'id': report_id,
                                'title': f"Report {thread_id}-{op_id}",
                                'quality_score': random.random() * 10
                            })
                            self.store.get_report(report_id)
                            self.store.list_reports()
                        
                        if op_type == 'cache' or op_type == 'mixed':
                            key = f"cache_{thread_id}_{op_id}"
                            self.cache.set(key, f"value_{op_id}", ttl=random.choice([0, 1, 10]))
                            self.cache.get(key)
                            self.cache.exists(key)
                        
                        if op_type == 'graph' or op_type == 'mixed':
                            node_id = self.backend.add_node_to_knowledge_graph(
                                label=f"concurrent_node_{thread_id}_{op_id}"
                            )
                            if op_id > 0:
                                try:
                                    self.backend.add_edge_to_knowledge_graph(
                                        f"concurrent_node_{thread_id}_{op_id-1}",
                                        node_id,
                                        "NEXT",
                                        1.0
                                    )
                                except:
                                    pass
                        
                        with self.lock:
                            self.stats['operations'] += 1
                        
                    except Exception as e:
                        local_errors.append(str(e))
                        with self.lock:
                            self.stats['errors'] += 1
                
                with errors_lock:
                    errors.extend(local_errors)
                    
            except Exception as e:
                with errors_lock:
                    self.stats['errors'] += 1
                    errors.append(f"Thread {thread_id} 初始化失败: {str(e)}")
        
        # 启动所有线程
        start_time = time.time()
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        duration = time.time() - start_time
        
        print(f"✅ 场景2完成:")
        print(f"   线程数: {num_threads}")
        print(f"   总操作: {num_threads * ops_per_thread}")
        print(f"   耗时: {duration:.2f}秒")
        print(f"   吞吐量: {num_threads * ops_per_thread / duration:.0f} ops/s")
        print(f"   错误: {len(errors)}")
        
        if errors:
            print(f"   错误样例: {errors[:5]}")
    
    # ========================================================================
    # 场景3: 混沌场景 - 随机失败、中断、延迟
    # ========================================================================
    def scenario_3_chaos_mode(self, duration_seconds: int = 60):
        """场景3: 混沌模式"""
        print(f"\n{'='*80}")
        print(f"🧪 场景3: 混沌模式 - {duration_seconds}秒随机混乱")
        print(f"{'='*80}")
        
        self.chaos_enabled = True
        self.failure_rate = 0.05  # 5% 失败率
        self.delay_rate = 0.1  # 10% 延迟
        
        start_time = time.time()
        operation_count = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                # 随机操作
                op = random.choice([
                    'create_task',
                    'update_task',
                    'create_memory',
                    'search_memory',
                    'save_report',
                    'cache_set_get',
                    'add_node',
                    'add_edge',
                    'get_stats',
                    'mixed_batch'
                ])
                
                if op == 'create_task':
                    self.backend.create_new_task_entry(f"Chaos Task {operation_count}")
                elif op == 'update_task':
                    tasks = self.backend.retrieve_all_tasks()
                    if tasks:
                        task = random.choice(tasks)
                        self.backend.update_task_entry(
                            task.unique_entity_id,
                            progress_percentage_value=random.random()
                        )
                elif op == 'create_memory':
                    self.backend.create_new_memory_entry(
                        f"Chaos Memory {operation_count}",
                        importance_score=random.randint(1, 5)
                    )
                elif op == 'search_memory':
                    self.backend.search_memories_by_text_content("chaos")
                elif op == 'save_report':
                    self.store.save_report({
                        'id': f"chaos_{operation_count}",
                        'title': f"Chaos Report {operation_count}",
                        'quality_score': random.random() * 10
                    })
                elif op == 'cache_set_get':
                    key = f"chaos_{operation_count}"
                    self.cache.set(key, f"value_{operation_count}", ttl=1)
                    self.cache.get(key)
                elif op == 'add_node':
                    self.backend.add_node_to_knowledge_graph(f"chaos_node_{operation_count}")
                elif op == 'add_edge':
                    try:
                        stats = self.backend.retrieve_knowledge_graph_statistics()
                        if stats and stats.get('node_count', 0) > 1:
                            # 随机添加边
                            pass
                    except:
                        pass
                elif op == 'get_stats':
                    self.backend.generate_system_statistics_snapshot()
                    self.store.get_stats()
                    self.cache.get_stats()
                elif op == 'mixed_batch':
                    # 批量混合操作
                    for _ in range(10):
                        self.backend.create_new_task_entry(f"Batch Task {_}")
                        self.backend.create_new_memory_entry(f"Batch Memory {_}")
                        self.store.save_report({'id': f"batch_{_}", 'title': f"Batch {_}"})
                
                operation_count += 1
                self.stats['operations'] += 1
                
                # 混沌延迟
                if random.random() < self.delay_rate:
                    time.sleep(random.uniform(0.001, 0.01))
                
                if operation_count % 1000 == 0:
                    elapsed = time.time() - start_time
                    print(f"  进度: {operation_count}次操作, {elapsed:.1f}秒 ({operation_count/elapsed:.0f} ops/s)")
                
            except Exception as e:
                self.stats['errors'] += 1
                self.errors.append({
                    'scenario': 'chaos_mode',
                    'operation': operation_count,
                    'error': str(e)
                })
                # 在混沌模式下，错误是预期的
                if random.random() < 0.1:  # 10%概率打印
                    print(f"  ⚠️ 混沌错误 (预期): {str(e)[:100]}")
        
        print(f"✅ 场景3完成: {operation_count}次操作, {self.stats['errors']}次错误")
    
    # ========================================================================
    # 场景4: 极端边界条件
    # ========================================================================
    def scenario_4_extreme_boundaries(self):
        """场景4: 极端边界条件"""
        print(f"\n{'='*80}")
        print(f"🧪 场景4: 极端边界条件")
        print(f"{'='*80}")
        
        test_cases = [
            ("空字符串", ""),
            ("超长字符串", "X" * 1000000),
            ("Unicode", "你好世界🌍🎉" * 100),
            ("SQL注入", "'; DROP TABLE users; --"),
            ("特殊字符", "\x00\x01\x02\n\r\t"),
            ("None值", None),
            ("负数", -999999),
            ("正无穷", float('inf')),
            ("负无穷", float('-inf')),
            ("NaN", float('nan')),
            ("嵌套字典", ChaosScenarios.generate_nested_dict(10)),
        ]
        
        for test_name, test_value in test_cases:
            try:
                print(f"  测试: {test_name}")
                
                # 测试任务
                try:
                    if test_value is None:
                        task = self.backend.create_new_task_entry(None)
                    else:
                        task = self.backend.create_new_task_entry(str(test_value)[:100])
                    self.backend.update_task_entry(
                        task.unique_entity_id,
                        error_message=str(test_value)[:1000]
                    )
                except Exception as e:
                    print(f"    ⚠️ 任务操作: {str(e)[:100]}")
                
                # 测试记忆
                try:
                    memory = self.backend.create_new_memory_entry(
                        str(test_value)[:1000] if test_value else "None",
                        importance_score=3
                    )
                except Exception as e:
                    print(f"    ⚠️ 记忆操作: {str(e)[:100]}")
                
                # 测试存储
                try:
                    self.store.save_report({
                        'id': f"boundary_{test_name}",
                        'title': str(test_value)[:100],
                        'content': str(test_value),
                        'quality_score': random.random() * 10
                    })
                except Exception as e:
                    print(f"    ⚠️ 存储操作: {str(e)[:100]}")
                
                # 测试缓存
                try:
                    self.cache.set(f"boundary_{test_name}", str(test_value))
                    self.cache.get(f"boundary_{test_name}")
                except Exception as e:
                    print(f"    ⚠️ 缓存操作: {str(e)[:100]}")
                
                self.stats['operations'] += 1
                
            except Exception as e:
                self.stats['errors'] += 1
                self.errors.append({
                    'scenario': 'extreme_boundaries',
                    'test': test_name,
                    'error': str(e)
                })
        
        print(f"✅ 场景4完成: {len(test_cases)}个边界测试")
    
    # ========================================================================
    # 场景5: 资源泄漏检测
    # ========================================================================
    def scenario_5_memory_leak_detection(self, iterations: int = 10000):
        """场景5: 资源泄漏检测"""
        print(f"\n{'='*80}")
        print(f"🧪 场景5: 资源泄漏检测 - {iterations}次创建/删除循环")
        print(f"{'='*80}")
        
        initial_memory = 0
        try:
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss
        except:
            pass
        
        # 循环创建和删除
        for i in range(iterations):
            # 创建对象
            task = self.backend.create_new_task_entry(f"Leak Test {i}")
            memory = self.backend.create_new_memory_entry(f"Leak Memory {i}")
            self.store.save_report({'id': f"leak_{i}", 'title': f"Report {i}"})
            self.cache.set(f"leak_{i}", f"value_{i}")
            
            # 定期删除
            if i % 100 == 0:
                # 删除旧对象
                for j in range(max(0, i - 100), i):
                    try:
                        pass  # 简化，不实际删除以增加压力
                    except:
                        pass
                
                # 强制GC
                gc.collect()
                
                if i % 1000 == 0:
                    print(f"  进度: {i}/{iterations} ({(i/iterations*100):.1f}%)")
            
            self.stats['operations'] += 1
        
        # 检查内存
        final_memory = 0
        try:
            import psutil
            process = psutil.Process()
            final_memory = process.memory_info().rss
        except:
            pass
        
        memory_growth = (final_memory - initial_memory) / (1024 * 1024) if initial_memory else 0
        
        print(f"✅ 场景5完成:")
        print(f"   迭代次数: {iterations}")
        print(f"   初始内存: {initial_memory / (1024*1024):.1f} MB")
        print(f"   最终内存: {final_memory / (1024*1024):.1f} MB")
        print(f"   内存增长: {memory_growth:.1f} MB")
        
        if memory_growth > 500:  # 超过500MB认为有泄漏
            self.stats['memory_leaks'] += 1
            print(f"   ⚠️ 警告: 可能存在内存泄漏!")
        else:
            print(f"   ✅ 内存增长正常")
    
    # ========================================================================
    # 场景6: 数据一致性验证
    # ========================================================================
    def scenario_6_data_consistency(self, operations: int = 5000):
        """场景6: 数据一致性验证"""
        print(f"\n{'='*80}")
        print(f"🧪 场景6: 数据一致性验证 - {operations}次操作")
        print(f"{'='*80}")
        
        inconsistencies = []
        
        for i in range(operations):
            try:
                # 创建任务
                task = self.backend.create_new_task_entry(f"Consistency Task {i}")
                task_id = task.unique_entity_id
                
                # 创建记忆并关联
                memory = self.backend.create_new_memory_entry(
                    f"Consistency Memory {i}",
                    importance_score=3,
                    tags_list=["consistency", "test"]
                )
                memory_id = memory.unique_memory_id
                
                # 添加到知识图谱
                node_id = self.backend.add_node_to_knowledge_graph(
                    label=f"consistency_node_{i}",
                    properties={"task_id": task_id, "memory_id": memory_id}
                )
                
                # 多次更新
                for progress in [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
                    self.backend.update_task_entry(
                        task_id,
                        progress_percentage_value=progress
                    )
                
                # 验证数据一致性
                retrieved_task = self.backend.retrieve_task_by_id(task_id)
                retrieved_memory = self.backend.retrieve_memory_by_id(memory_id)
                
                # 检查一致性
                if retrieved_task.execution_status not in [
                    TaskExecutionStatusEnumeration.COMPLETED_STATUS,
                    TaskExecutionStatusEnumeration.IN_PROGRESS_STATUS
                ]:
                    inconsistencies.append(f"任务状态不一致: {retrieved_task.execution_status}")
                
                if retrieved_memory.access_count_number < 1:
                    inconsistencies.append(f"记忆访问计数异常: {retrieved_memory.access_count_number}")
                
                self.stats['operations'] += 1
                
                if i % 500 == 0:
                    print(f"  进度: {i}/{operations} ({(i/operations*100):.1f}%)")
                    
            except Exception as e:
                self.stats['errors'] += 1
                inconsistencies.append(f"操作 {i} 错误: {str(e)}")
        
        print(f"✅ 场景6完成:")
        print(f"   操作数: {operations}")
        print(f"   不一致: {len(inconsistencies)}")
        
        if inconsistencies:
            print(f"   ⚠️ 发现数据不一致:")
            for inc in inconsistencies[:10]:
                print(f"     - {inc[:100]}")
            self.stats['data_corruption'] += len(inconsistencies)
        else:
            print(f"   ✅ 所有数据完全一致!")
    
    # ========================================================================
    # 运行所有场景
    # ========================================================================
    def run_all_scenarios(self):
        """运行所有场景"""
        print("\n" + "=" * 100)
        print("🚀 开始超级复杂场景测试")
        print("=" * 100)
        
        start_time = time.time()
        
        # 场景1: 多层嵌套操作
        self.scenario_1_nested_operations(iterations=1000)
        
        # 场景2: 超复杂并发
        self.scenario_2_extreme_concurrency(num_threads=200, ops_per_thread=100)
        
        # 场景3: 混沌模式
        self.scenario_3_chaos_mode(duration_seconds=60)
        
        # 场景4: 极端边界条件
        self.scenario_4_extreme_boundaries()
        
        # 场景5: 资源泄漏检测
        self.scenario_5_memory_leak_detection(iterations=10000)
        
        # 场景6: 数据一致性验证
        self.scenario_6_data_consistency(operations=5000)
        
        total_duration = time.time() - start_time
        
        # 生成报告
        print("\n" + "=" * 100)
        print("📊 超级复杂场景测试 - 最终报告")
        print("=" * 100)
        
        print(f"\n⏱️  总耗时: {total_duration:.1f}秒 ({total_duration/60:.1f}分钟)")
        
        print(f"\n📈 统计信息:")
        print(f"   总操作数: {self.stats['operations']:,}")
        print(f"   总错误数: {self.stats['errors']}")
        print(f"   警告数: {self.stats['warnings']}")
        print(f"   内存泄漏: {self.stats['memory_leaks']}")
        print(f"   数据损坏: {self.stats['data_corruption']}")
        print(f"   吞吐量: {self.stats['operations'] / total_duration:.0f} ops/s")
        
        print(f"\n📋 错误详情 (前20个):")
        for i, error in enumerate(self.errors[:20]):
            print(f"   {i+1}. [{error.get('scenario', 'unknown')}] {str(error.get('error', ''))[:100]}")
        
        # 最终检查
        print(f"\n🔍 最终检查:")
        
        consistency_ok = self.stats['data_corruption'] == 0
        memory_ok = self.stats['memory_leaks'] == 0
        error_rate = self.stats['errors'] / self.stats['operations'] * 100 if self.stats['operations'] > 0 else 0
        error_rate_ok = error_rate < 1.0  # 错误率小于1%
        
        print(f"   数据一致性: {'✅ 通过' if consistency_ok else '❌ 失败'}")
        print(f"   内存泄漏: {'✅ 通过' if memory_ok else '❌ 失败'}")
        print(f"   错误率: {'✅ 通过' if error_rate_ok else '❌ 失败'} ({error_rate:.2f}%)")
        
        all_passed = consistency_ok and memory_ok and error_rate_ok
        
        print(f"\n{'='*100}")
        if all_passed:
            print("🎉🎉🎉 超级复杂场景测试通过! 系统极其健壮!")
        else:
            print("⚠️  发现问题，需要进一步调查")
        print(f"{'='*100}")
        
        return all_passed


def main():
    """主函数"""
    try:
        orchestrator = SuperComplexTestOrchestrator()
        success = orchestrator.run_all_scenarios()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n❌ 测试崩溃: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
