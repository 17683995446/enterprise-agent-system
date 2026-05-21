"""
极端压力测试 - 100万次操作深度验证
测试系统在极限压力下的表现
"""

import sys
import time
import random
import threading
import gc
import uuid
import traceback
from typing import Dict, Any, List, Optional
from collections import defaultdict

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

from enterprise_agent_system.infrastructure.simple_memory_store import SimpleMemoryStore, SimpleCache
from enterprise_agent_system.core.in_memory_data_storage_backend import InMemoryDataStorageBackend
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
)


class ExtremeStressTester:
    """极端压力测试器"""
    
    def __init__(self):
        self.backend = InMemoryDataStorageBackend()
        self.store = SimpleMemoryStore()
        self.cache = SimpleCache()
        
        self.stats = {
            "operations": 0,
            "errors": 0,
            "critical_errors": 0,
            "start_time": None,
            "checkpoints": []
        }
        
        self.lock = threading.Lock()
        
        # 记录发现的问题
        self.issues = []
        
        # 用于验证数据一致性的标记
        self.validation_tasks = set()
        self.validation_memories = set()
    
    def record_issue(self, category: str, description: str, severity: str = "warning"):
        """记录发现的问题"""
        issue = {
            "category": category,
            "description": description,
            "severity": severity,
            "timestamp": time.time()
        }
        self.issues.append(issue)
        print(f"⚠️  [{severity.upper()}] {category}: {description}")
    
    def checkpoint(self, name: str):
        """记录检查点"""
        elapsed = time.time() - self.stats["start_time"]
        self.stats["checkpoints"].append({
            "name": name,
            "time": elapsed,
            "operations": self.stats["operations"],
            "errors": self.stats["errors"]
        })
        print(f"🔍  检查点: {name} @ {elapsed:.1f}s ({self.stats['operations']} ops)")
    
    def test_1_extreme_task_stress(self, num_tasks: int = 100000):
        """测试1: 极端任务创建压力 - 10万任务"""
        print(f"\n{'='*80}")
        print(f"🧪 测试1: 极端任务创建压力 - {num_tasks} 个任务")
        print(f"{'='*80}")
        
        self.stats["start_time"] = time.time()
        errors = 0
        
        for i in range(num_tasks):
            try:
                # 随机生成极端参数
                title = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(random.randint(1, 1000)))
                priority = random.choice([
                    TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL,
                    TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
                    TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL,
                    TaskPriorityLevelEnumeration.URGENT_PRIORITY_LEVEL,
                    "LOW", "MEDIUM", "HIGH", "URGENT",
                    1, 2, 3, 4, -1, 999
                ])
                
                task = self.backend.create_new_task_entry(
                    task_title=title,
                    priority_level=priority
                )
                self.validation_tasks.add(task.unique_entity_id)
                
                # 随机更新任务
                if random.random() < 0.3:
                    self.backend.update_task_entry(
                        task.unique_entity_id,
                        progress_percentage_value=random.random(),
                        execution_status=random.choice([
                            "pending", "in_progress", "completed", "failed",
                            TaskExecutionStatusEnumeration.PENDING_STATUS,
                            "invalid_status"
                        ])
                    )
                
                self.stats["operations"] += 1
                
                if (i + 1) % 10000 == 0:
                    self.checkpoint(f"Test1: {i+1} tasks")
                    
            except Exception as e:
                errors += 1
                self.stats["errors"] += 1
        
        print(f"✅ 测试1完成: 任务创建 {num_tasks}, 错误 {errors}")
        
        # 验证任务数据一致性
        print(f"   验证数据一致性...")
        all_tasks = self.backend.retrieve_all_tasks()
        print(f"   实际任务数: {len(all_tasks)}, 预期: {num_tasks}")
        
        if len(all_tasks) != num_tasks:
            self.record_issue("数据一致性", f"任务数不一致: 预期 {num_tasks}, 实际 {len(all_tasks)}", "critical")
        
        return errors
    
    def test_2_concurrent_memory_storm(self, num_threads: int = 500, ops_per_thread: int = 200):
        """测试2: 并发记忆风暴 - 500线程 × 200操作"""
        print(f"\n{'='*80}")
        print(f"🧪 测试2: 并发记忆风暴 - {num_threads} 线程 × {ops_per_thread} 操作")
        print(f"{'='*80}")
        
        errors = 0
        barrier = threading.Barrier(num_threads)
        lock = threading.Lock()
        
        def memory_worker(worker_id):
            nonlocal errors
            try:
                barrier.wait()  # 所有线程同时开始
                local_error_count = 0
                
                for i in range(ops_per_thread):
                    try:
                        # 创建极端记忆
                        content = "".join(chr(random.randint(32, 126)) for _ in range(random.randint(1, 10000)))
                        tags = [f"tag_{j}" for j in range(random.randint(0, 50))]
                        
                        memory = self.backend.create_new_memory_entry(
                            content_text=content,
                            importance_score=random.randint(-10, 20),
                            tags_list=tags
                        )
                        
                        self.validation_memories.add(memory.unique_memory_id)
                        
                        # 随机搜索
                        search_query = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(5))
                        self.backend.search_memories_by_text_content(search_query)
                        
                        # 随机检索
                        if random.random() < 0.1:
                            mem_id = random.choice(list(self.validation_memories)) if self.validation_memories else None
                            if mem_id:
                                self.backend.retrieve_memory_by_id(mem_id)
                        
                        with self.lock:
                            self.stats["operations"] += 1
                    
                    except Exception as e:
                        local_error_count += 1
                        with self.lock:
                            self.stats["errors"] += 1
                
                if local_error_count > 0:
                    print(f"   线程 {worker_id}: {local_error_count} errors")
            
            except Exception as e:
                with self.lock:
                    self.record_issue("线程崩溃", f"线程 {worker_id} 崩溃", "critical")
        
        threads = [threading.Thread(target=memory_worker, args=(i,)) for i in range(num_threads)]
        start_time = time.time()
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        duration = time.time() - start_time
        print(f"✅ 测试2完成: 耗时 {duration:.1f}s, 吞吐量 {num_threads*ops_per_thread/duration:.1f} ops/s")
        
        self.checkpoint("Test2: Memory Storm")
        return errors
    
    def test_3_knowledge_graph_explosion(self, num_nodes: int = 50000, num_edges: int = 150000):
        """测试3: 知识图谱爆炸 - 5万节点，15万边"""
        print(f"\n{'='*80}")
        print(f"🧪 测试3: 知识图谱爆炸 - {num_nodes} 节点, {num_edges} 边")
        print(f"{'='*80}")
        
        node_ids = []
        errors = 0
        
        # 创建节点
        for i in range(num_nodes):
            try:
                label = f"NODE_{i}_{uuid.uuid4()}"
                props = {
                    "index": i,
                    "random": random.random(),
                    "nested": {
                        "level1": {
                            "level2": {
                                "level3": "deep data"
                            }
                        }
                    }
                }
                
                node_id = self.backend.add_node_to_knowledge_graph(label, props)
                node_ids.append(node_id)
                
                self.stats["operations"] += 1
                
                if (i + 1) % 10000 == 0:
                    self.checkpoint(f"Test3: {i+1} nodes")
            
            except Exception as e:
                errors += 1
                self.stats["errors"] += 1
        
        # 创建边 - 极端的边创建
        edges_created = 0
        for i in range(num_edges):
            try:
                if len(node_ids) >= 2:
                    source_idx = random.randint(0, len(node_ids)-1)
                    target_idx = random.randint(0, len(node_ids)-1)
                    
                    # 尝试创建边（包括故意无效的节点）
                    source = node_ids[source_idx] if random.random() > 0.01 else "invalid_node_id"
                    target = node_ids[target_idx] if random.random() > 0.01 else "invalid_node_id"
                    
                    rel_type = random.choice([
                        "related_to", "depends_on", "includes", "references",
                        "", None, "   ", "INVALID-RELATION-123"
                    ])
                    
                    self.backend.add_edge_to_knowledge_graph(
                        source, target, rel_type, random.random()*10
                    )
                    edges_created += 1
                    self.stats["operations"] += 1
            
            except ValueError:
                # 预期的无效节点异常
                pass
            except Exception as e:
                self.record_issue("知识图谱异常", f"边创建异常: {str(e)}", "warning")
        
        # 验证统计
        kg_stats = self.backend.retrieve_knowledge_graph_statistics()
        print(f"✅ 测试3完成: 节点 {kg_stats['total_nodes']}, 边 {kg_stats['total_edges']}")
        print(f"   预期节点: ~{num_nodes}, 预期边: ~{num_edges}")
        
        self.checkpoint("Test3: Knowledge Graph Explosion")
        return errors
    
    def test_4_cache_ttl_torture(self, duration_seconds: int = 60):
        """测试4: 缓存TTL酷刑 - 60秒极端TTL操作"""
        print(f"\n{'='*80}")
        print(f"🧪 测试4: 缓存TTL酷刑 - {duration_seconds} 秒")
        print(f"{'='*80}")
        
        start_time = time.time()
        errors = 0
        ops_per_second = 0
        
        while time.time() - start_time < duration_seconds:
            for i in range(1000):
                try:
                    # 随机TTL值 - 包括负数、0、很大的数
                    ttl = random.choice([
                        0, 1, 2, 5, 10, 100, 1000, 999999,
                        -1, -10, -100, None
                    ])
                    
                    key = f"cache_test_{uuid.uuid4()}"
                    value = "x" * random.randint(1, 10000)
                    
                    self.cache.set(key, value, ttl)
                    self.cache.get(key)
                    
                    self.stats["operations"] += 1
                    ops_per_second += 1
                
                except Exception as e:
                    errors += 1
                    self.stats["errors"] += 1
            
            # 强制清理
            if random.random() < 0.1:
                self.cache.clear()
        
        cache_stats = self.cache.get_stats()
        print(f"✅ 测试4完成: {ops_per_second/duration_seconds:.1f} ops/s")
        print(f"   缓存统计: {cache_stats}")
        
        self.checkpoint("Test4: TTL Torture")
        return errors
    
    def test_5_reference_escape_validation(self):
        """测试5: 引用逃逸验证 - 检查引用问题"""
        print(f"\n{'='*80}")
        print(f"🧪 测试5: 引用逃逸验证")
        print(f"{'='*80}")
        
        # 验证retrieve_task_by_id返回的引用
        task = self.backend.create_new_task_entry("Reference Test", "Original description")
        original_title = task.task_title
        
        # 获取引用并修改
        retrieved = self.backend.retrieve_task_by_id(task.unique_entity_id)
        if retrieved:
            retrieved.task_title = "MODIFIED EXTERNALLY!"
        
        # 重新获取验证
        retrieved2 = self.backend.retrieve_task_by_id(task.unique_entity_id)
        if retrieved2 and retrieved2.task_title != original_title:
            self.record_issue("引用问题", "retrieve_task_by_id 返回的引用可以修改内部存储", "warning")
        
        # 验证retrieve_all_tasks
        tasks_list = self.backend.retrieve_all_tasks()
        original_len = len(tasks_list)
        tasks_list.clear()  # 尝试清空返回的列表
        
        # 检查是否影响内部
        final_tasks = self.backend.retrieve_all_tasks()
        if len(final_tasks) != original_len:
            self.record_issue("引用问题", "retrieve_all_tasks 返回的列表引用影响内部存储", "warning")
        
        print(f"✅ 测试5完成: 引用验证完成")
        self.checkpoint("Test5: Reference Validation")
        return 0
    
    def test_6_fuzzing_chaos(self, num_iterations: int = 100000):
        """测试6: Fuzzing混沌测试 - 10万次完全随机操作"""
        print(f"\n{'='*80}")
        print(f"🧪 测试6: Fuzzing混沌测试 - {num_iterations} 次随机操作")
        print(f"{'='*80}")
        
        errors = 0
        
        for iteration in range(num_iterations):
            try:
                # 随机选择操作
                op_type = random.randint(0, 50)
                
                if op_type < 15:
                    # 任务操作
                    if op_type < 10:
                        self.backend.create_new_task_entry(
                            task_title=str(uuid.uuid4()) * random.randint(1, 5)
                        )
                    else:
                        if self.validation_tasks:
                            task_id = random.choice(list(self.validation_tasks))
                            self.backend.update_task_entry(
                                task_id,
                                **{
                                    "progress_percentage_value": random.random(),
                                    "error_message": str(uuid.uuid4()) * 10,
                                    "some_nonexistent_field": "should be ignored"
                                }
                            )
                
                elif op_type < 30:
                    # 记忆操作
                    if op_type < 20:
                        self.backend.create_new_memory_entry(
                            content_text=str(uuid.uuid4()) * 100,
                            importance_score=random.randint(-100, 100),
                            tags_list=[str(uuid.uuid4()) for _ in range(random.randint(0, 10))]
                        )
                    else:
                        self.backend.search_memories_by_text_content(str(uuid.uuid4()))
                
                elif op_type < 40:
                    # 存储操作
                    self.store.save_report({
                        "id": str(uuid.uuid4()),
                        "title": str(uuid.uuid4()),
                        "some_random_field": str(uuid.uuid4())
                    })
                
                elif op_type < 50:
                    # 知识图谱
                    self.backend.add_node_to_knowledge_graph(
                        label=str(uuid.uuid4()),
                        properties={"random": random.random()}
                    )
                
                else:
                    # 系统统计
                    self.backend.generate_system_statistics_snapshot()
                
                self.stats["operations"] += 1
                
                if (iteration + 1) % 10000 == 0:
                    self.checkpoint(f"Test6: {iteration+1} iterations")
            
            except Exception as e:
                errors += 1
                self.stats["errors"] += 1
                if errors <= 10:  # 只记录前10个
                    self.record_issue("Fuzzing异常", f"迭代 {iteration}: {str(e)}", "warning")
        
        print(f"✅ 测试6完成: Fuzzing {num_iterations} 次, 错误 {errors}")
        self.checkpoint("Test6: Fuzzing Chaos")
        return errors
    
    def run_all_tests(self):
        """运行所有极端测试"""
        print("\n" + "="*100)
        print("🚀 开始极端压力测试")
        print("="*100)
        
        # 运行测试
        self.test_1_extreme_task_stress(num_tasks=10000)  # 简化为1万以便快速测试
        self.test_2_concurrent_memory_storm(num_threads=100, ops_per_thread=100)
        self.test_3_knowledge_graph_explosion(num_nodes=5000, num_edges=15000)
        self.test_4_cache_ttl_torture(duration_seconds=10)
        self.test_5_reference_escape_validation()
        self.test_6_fuzzing_chaos(num_iterations=50000)
        
        # 最终报告
        print("\n" + "="*100)
        print("📊 极端压力测试 - 最终报告")
        print("="*100)
        
        total_time = time.time() - self.stats["start_time"]
        print(f"\n⏱️  总耗时: {total_time:.1f}s")
        print(f"📈 总操作: {self.stats['operations']:,}")
        print(f"❌ 总错误: {self.stats['errors']}")
        print(f"⚡ 吞吐量: {self.stats['operations']/total_time:.1f} ops/s")
        
        if self.issues:
            print(f"\n🔍 发现的问题 ({len(self.issues)}):")
            for i, issue in enumerate(self.issues[:20], 1):
                print(f"   {i}. [{issue['severity']}] {issue['category']}: {issue['description']}")
        
        print(f"\n{'='*100}")
        if self.stats["errors"] == 0 and len(self.issues) == 0:
            print("🎉🎉🎉 极端压力测试完美通过！")
        else:
            print("⚠️  发现问题，需要修复！")
        print("="*100)
        
        return self.stats["errors"] == 0 and len(self.issues) == 0


def main():
    """主函数"""
    try:
        tester = ExtremeStressTester()
        result = tester.run_all_tests()
        return 0 if result else 1
    except Exception as e:
        print(f"❌ 测试主程序崩溃: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
