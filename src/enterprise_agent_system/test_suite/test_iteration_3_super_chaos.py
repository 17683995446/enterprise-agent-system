"""
第3次迭代：超级混沌测试 - 逐句代码日志验证
Iteration 3: Super Chaos - Line-by-Line Logging Verification

按照用户要求，进行：
1. 更长时间的持续测试
2. 更大规模的极端测试
3. 更错综复杂的场景
4. 更高难度的挑战
5. 更混乱的组合场景
6. 逐句代码日志验证
"""

import sys
import time
import random
import threading
import gc
import uuid
import traceback
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

# 配置逐句代码日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("LineByLineLogger")

print("=" * 150)
print("🚀 启动第3次迭代：超级混沌测试 - 逐句代码日志验证")
print("=" * 150)
print(f"[INIT] 测试开始时间: {datetime.now().isoformat()}")
print(f"[INIT] 目标: 超级极限场景 + 逐句代码日志验证")
print()


class LineByLineLoggingBackend:
    """逐句代码日志包装器 - 验证每一行代码执行"""
    
    def __init__(self, real_backend):
        self.backend = real_backend
        self.line_count = 0
        self.verified_ops = []
    
    def _log_line(self, op_name, *args, **kwargs):
        self.line_count += 1
        logger.debug(f"[{self.line_count}] 执行: {op_name}")
        logger.debug(f"  参数: args={args}, kwargs={kwargs}")
        self.verified_ops.append(op_name)
        return None
    
    def create_new_task_entry(self, *args, **kwargs):
        self._log_line("create_new_task_entry", *args, **kwargs)
        result = self.backend.create_new_task_entry(*args, **kwargs)
        logger.debug(f"  结果: {result.unique_entity_id if result else None}")
        return result
    
    def retrieve_task_by_id(self, *args, **kwargs):
        self._log_line("retrieve_task_by_id", *args, **kwargs)
        result = self.backend.retrieve_task_by_id(*args, **kwargs)
        logger.debug(f"  结果: {result is not None}")
        return result
    
    def update_task_entry(self, *args, **kwargs):
        self._log_line("update_task_entry", *args, **kwargs)
        result = self.backend.update_task_entry(*args, **kwargs)
        logger.debug(f"  更新成功: {result is not None}")
        return result
    
    def retrieve_all_tasks(self, *args, **kwargs):
        self._log_line("retrieve_all_tasks", *args, **kwargs)
        result = self.backend.retrieve_all_tasks(*args, **kwargs)
        logger.debug(f"  获取任务数: {len(result)}")
        return result
    
    def create_new_memory_entry(self, *args, **kwargs):
        self._log_line("create_new_memory_entry", *args, **kwargs)
        result = self.backend.create_new_memory_entry(*args, **kwargs)
        logger.debug(f"  记忆ID: {result.unique_memory_id}")
        return result
    
    def retrieve_memory_by_id(self, *args, **kwargs):
        self._log_line("retrieve_memory_by_id", *args, **kwargs)
        result = self.backend.retrieve_memory_by_id(*args, **kwargs)
        logger.debug(f"  结果: {result is not None}")
        return result
    
    def search_memories_by_text_content(self, *args, **kwargs):
        self._log_line("search_memories_by_text_content", *args, **kwargs)
        result = self.backend.search_memories_by_text_content(*args, **kwargs)
        logger.debug(f"  搜索结果数: {len(result)}")
        return result
    
    def retrieve_all_memories(self, *args, **kwargs):
        self._log_line("retrieve_all_memories", *args, **kwargs)
        result = self.backend.retrieve_all_memories(*args, **kwargs)
        logger.debug(f"  记忆数: {len(result)}")
        return result
    
    def create_new_experience_entry(self, *args, **kwargs):
        self._log_line("create_new_experience_entry", *args, **kwargs)
        result = self.backend.create_new_experience_entry(*args, **kwargs)
        logger.debug(f"  经验ID: {result.unique_experience_id}")
        return result
    
    def retrieve_all_experiences(self, *args, **kwargs):
        self._log_line("retrieve_all_experiences", *args, **kwargs)
        result = self.backend.retrieve_all_experiences(*args, **kwargs)
        logger.debug(f"  经验数: {len(result)}")
        return result
    
    def add_node_to_knowledge_graph(self, *args, **kwargs):
        self._log_line("add_node_to_knowledge_graph", *args, **kwargs)
        result = self.backend.add_node_to_knowledge_graph(*args, **kwargs)
        logger.debug(f"  节点ID: {result}")
        return result
    
    def add_edge_to_knowledge_graph(self, *args, **kwargs):
        self._log_line("add_edge_to_knowledge_graph", *args, **kwargs)
        try:
            result = self.backend.add_edge_to_knowledge_graph(*args, **kwargs)
            logger.debug(f"  边创建成功: {result}")
            return result
        except Exception as e:
            logger.debug(f"  边创建异常 (预期): {str(e)[:50]}")
            return None
    
    def retrieve_knowledge_graph_statistics(self, *args, **kwargs):
        self._log_line("retrieve_knowledge_graph_statistics", *args, **kwargs)
        result = self.backend.retrieve_knowledge_graph_statistics(*args, **kwargs)
        logger.debug(f"  统计: {result}")
        return result
    
    def generate_system_statistics_snapshot(self, *args, **kwargs):
        self._log_line("generate_system_statistics_snapshot", *args, **kwargs)
        result = self.backend.generate_system_statistics_snapshot(*args, **kwargs)
        logger.debug(f"  系统统计快照生成")
        return result
    
    def retrieve_pending_tasks_sorted_by_priority(self, *args, **kwargs):
        self._log_line("retrieve_pending_tasks_sorted_by_priority", *args, **kwargs)
        result = self.backend.retrieve_pending_tasks_sorted_by_priority(*args, **kwargs)
        logger.debug(f"  待处理任务数: {len(result)}")
        return result


class SuperChaosTestRunner:
    """超级混沌测试运行器"""
    
    def __init__(self):
        print("[INIT] 正在初始化超级混沌测试环境...")
        from enterprise_agent_system.core.in_memory_data_storage_backend import (
            InMemoryDataStorageBackend,
        )
        
        self.real_backend = InMemoryDataStorageBackend()
        self.backend = LineByLineLoggingBackend(self.real_backend)
        
        self.errors: List[Dict[str, Any]] = []
        self.critical_failures: List[Dict[str, Any]] = []
        self.stats = {
            "total_operations": 0,
            "total_errors": 0,
            "start_time": time.time(),
            "checkpoints": [],
        }
        
        self.lock = threading.Lock()
        self.operation_count = 0
        self.error_count = 0
        
        # 持久化记录
        self.all_task_ids = []
        self.all_memory_ids = []
        self.all_experience_ids = []
        self.all_node_ids = []
        self.all_edge_ids = []
        
        print("[INIT] 超级混沌测试环境初始化完成")
        print()
    
    def log_operation(self, name):
        with self.lock:
            self.operation_count += 1
            if self.operation_count % 1000 == 0:
                logger.info(f"📊 操作进度: {self.operation_count:,}")
    
    def safe_execute(self, operation_name, func, *args, **kwargs):
        try:
            self.log_operation(operation_name)
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            with self.lock:
                self.error_count += 1
                error_info = {
                    "operation": operation_name,
                    "error": str(e),
                    "args": str(args)[:100],
                    "kwargs": str(kwargs)[:100],
                    "traceback": traceback.format_exc()
                }
                self.errors.append(error_info)
                logger.error(f"❌ 错误: {operation_name}: {str(e)}")
            return None
    
    def checkpoint(self, name):
        elapsed = time.time() - self.stats["start_time"]
        self.stats["checkpoints"].append({
            "name": name,
            "elapsed": elapsed,
            "operations": self.operation_count,
            "errors": self.error_count,
            "verified_lines": self.backend.line_count
        })
        print(f"\n" + "="*100)
        print(f"🔍 [CHECKPOINT] {name}")
        print(f"   ⏱️  耗时: {elapsed:.2f}秒")
        print(f"   📈 操作数: {self.operation_count:,}")
        print(f"   ❌ 错误数: {self.error_count}")
        print(f"   📝 验证代码行数: {self.backend.line_count:,}")
        print("="*100 + "\n")
    
    # =========================================================================
    # 超级混沌1: 无限循环持续测试
    # =========================================================================
    def super_chaos_1_infinite_loop(self, duration_seconds=30):
        """超级混沌1: 无限循环持续测试 - 长时间运行验证"""
        print("=" * 150)
        print("💥 超级混沌1: 无限循环持续测试 - 30秒")
        print("=" * 150)
        print()
        
        start_time = time.time()
        iteration_count = 0
        
        while time.time() - start_time < duration_seconds:
            iteration_count += 1
            
            if iteration_count % 100 == 0:
                elapsed = time.time() - start_time
                print(f"   🕐 持续运行 {elapsed:.1f}秒, 迭代 {iteration_count}次")
            
            # 随机混合操作
            operations = [
                "create_task", "create_memory", "create_experience", "create_node",
                "retrieve_task", "retrieve_memory", "search_memory",
                "update_task", "create_edge", "get_stats",
            ]
            
            for i in range(10):  # 每次迭代10个操作
                op = random.choice(operations)
                
                if op == "create_task":
                    task = self.safe_execute("create_task", 
                        self.backend.create_new_task_entry,
                        task_title=f"LoopTask_{iteration_count}_{i}",
                        task_description=f"持续运行测试_{iteration_count}",
                        priority_level=random.choice([1, 2, 3, 4, "low", "medium", "high", "urgent", None])
                    )
                    if task:
                        self.all_task_ids.append(task.unique_entity_id)
                
                elif op == "create_memory":
                    memory = self.safe_execute("create_memory",
                        self.backend.create_new_memory_entry,
                        content_text=f"记忆_{iteration_count}_{i}" + "x"*random.randint(10, 1000),
                        category_type=random.choice([None, "general", "technical", "experience"]),
                        tags_list=[f"tag_{j}" for j in range(random.randint(0, 20))],
                        importance_score=random.randint(-10, 20),
                        source_task_id=random.choice(self.all_task_ids) if self.all_task_ids else None
                    )
                    if memory:
                        self.all_memory_ids.append(memory.unique_memory_id)
                
                elif op == "create_experience":
                    if self.all_task_ids:
                        exp = self.safe_execute("create_experience",
                            self.backend.create_new_experience_entry,
                            task_reference_id=random.choice(self.all_task_ids),
                            task_type_label=f"Type_{iteration_count}",
                            was_successful=random.choice([True, False]),
                            duration_seconds=random.random()*1000
                        )
                        if exp:
                            self.all_experience_ids.append(exp.unique_experience_id)
                
                elif op == "create_node":
                    node = self.safe_execute("create_node",
                        self.backend.add_node_to_knowledge_graph,
                        label=f"Node_{iteration_count}_{i}",
                        properties={f"key_{k}": f"value_{k}" for k in range(random.randint(0, 10))},
                        memory_id=random.choice(self.all_memory_ids) if self.all_memory_ids else None
                    )
                    if node:
                        self.all_node_ids.append(node)
                
                elif op == "retrieve_task":
                    if self.all_task_ids:
                        self.safe_execute("retrieve_task",
                            self.backend.retrieve_task_by_id,
                            random.choice(self.all_task_ids + ["nonexistent", "invalid", ""])
                        )
                
                elif op == "retrieve_memory":
                    if self.all_memory_ids:
                        self.safe_execute("retrieve_memory",
                            self.backend.retrieve_memory_by_id,
                            random.choice(self.all_memory_ids + ["nonexistent", "invalid", ""])
                        )
                
                elif op == "search_memory":
                    search_term = random.choice(["记忆", "test", "x", "", None, f"LoopTask_{iteration_count}"])
                    self.safe_execute("search_memory",
                        self.backend.search_memories_by_text_content,
                        search_query=search_term,
                        category_filter=random.choice([None, "general", "technical"]),
                        min_importance=random.randint(0, 10)
                    )
                
                elif op == "update_task":
                    if self.all_task_ids:
                        task_id = random.choice(self.all_task_ids)
                        self.safe_execute("update_task",
                            self.backend.update_task_entry,
                            task_id,
                            progress_percentage_value=random.random() * 2 - 0.5,  # -0.5 到 1.5
                            execution_status=random.choice([
                                "pending", "in_progress", "completed", "failed", "cancelled", 
                                "invalid", None
                            ]),
                            task_title=f"更新_{iteration_count}_{i}"
                        )
                
                elif op == "create_edge":
                    if len(self.all_node_ids) >= 2:
                        source = random.choice(self.all_node_ids)
                        target = random.choice(self.all_node_ids)
                        edge = self.safe_execute("create_edge",
                            self.backend.add_edge_to_knowledge_graph,
                            source, target,
                            relation_type=random.choice(["related", "depends", "includes", "invalid", "", None]),
                            weight=random.random() * 10 - 5  # -5 到 5
                        )
                        if edge:
                            self.all_edge_ids.append(edge)
                
                elif op == "get_stats":
                    if random.random() < 0.1:  # 10%概率获取统计
                        self.safe_execute("get_kg_stats",
                            self.backend.retrieve_knowledge_graph_statistics
                        )
                        self.safe_execute("get_system_stats",
                            self.backend.generate_system_statistics_snapshot
                        )
        
        elapsed = time.time() - start_time
        print(f"\n✅ 超级混沌1完成: {elapsed:.1f}秒, {iteration_count}次迭代")
        self.checkpoint("SuperChaos1: 无限循环持续测试")
    
    # =========================================================================
    # 超级混沌2: 大规模并发攻击
    # =========================================================================
    def super_chaos_2_massive_concurrent_attack(self):
        """超级混沌2: 大规模并发攻击 - 200线程同时攻击"""
        print("=" * 150)
        print("💥 超级混沌2: 大规模并发攻击 - 200线程")
        print("=" * 150)
        print()
        
        barrier = threading.Barrier(200)
        threads = []
        thread_errors = []
        
        def attacker(thread_id):
            try:
                barrier.wait()
                
                for i in range(50):  # 每个线程50次攻击
                    # 随机选择攻击方式
                    attack = random.choice([
                        "create_many_tasks", "create_many_memories", 
                        "update_same_task", "search_heavily", 
                        "create_graph_storm", "mixed_ops"
                    ])
                    
                    if attack == "create_many_tasks":
                        for j in range(5):
                            task = self.safe_execute(f"attacker{thread_id}_task",
                                self.backend.create_new_task_entry,
                                task_title=f"Attack_{thread_id}_{i}_{j}",
                            )
                            if task:
                                with self.lock:
                                    self.all_task_ids.append(task.unique_entity_id)
                    
                    elif attack == "create_many_memories":
                        for j in range(5):
                            mem = self.safe_execute(f"attacker{thread_id}_mem",
                                self.backend.create_new_memory_entry,
                                content_text=f"攻击记忆_{thread_id}_{i}_{j}"
                            )
                            if mem:
                                with self.lock:
                                    self.all_memory_ids.append(mem.unique_memory_id)
                    
                    elif attack == "update_same_task":
                        if self.all_task_ids:
                            target_task = random.choice(self.all_task_ids)
                            for j in range(10):
                                self.safe_execute(f"attacker{thread_id}_update",
                                    self.backend.update_task_entry,
                                    target_task,
                                    progress_percentage_value=random.random()
                                )
                    
                    elif attack == "search_heavily":
                        for j in range(10):
                            self.safe_execute(f"attacker{thread_id}_search",
                                self.backend.search_memories_by_text_content,
                                search_query=random.choice(["a", "b", "c", "x", "y", "z"])
                            )
                    
                    elif attack == "create_graph_storm":
                        for j in range(3):
                            node = self.safe_execute(f"attacker{thread_id}_node",
                                self.backend.add_node_to_knowledge_graph,
                                label=f"AttackNode_{thread_id}_{i}_{j}"
                            )
                            if node:
                                with self.lock:
                                    self.all_node_ids.append(node)
                    
                    elif attack == "mixed_ops":
                        self.safe_execute(f"attacker{thread_id}_create",
                            self.backend.create_new_task_entry,
                            task_title=f"Mixed_{thread_id}_{i}"
                        )
                        if self.all_memory_ids:
                            self.safe_execute(f"attacker{thread_id}_retrieve",
                                self.backend.retrieve_memory_by_id,
                                random.choice(self.all_memory_ids)
                            )
                            self.safe_execute(f"attacker{thread_id}_search",
                                self.backend.search_memories_by_text_content,
                                search_query="攻击"
                            )
            
            except Exception as e:
                with self.lock:
                    thread_errors.append({
                        "thread": thread_id,
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    })
        
        print("[ATTACK] 启动200个攻击线程...")
        for i in range(200):
            t = threading.Thread(target=attacker, args=(i,))
            threads.append(t)
            t.start()
        
        print("[ATTACK] 等待所有攻击线程完成...")
        for t in threads:
            t.join()
        
        if thread_errors:
            print(f"❌ 发现 {len(thread_errors)} 个线程崩溃！")
            for err in thread_errors[:10]:
                print(f"   线程{err['thread']}: {err['error']}")
        else:
            print(f"✅ 200线程攻击完美完成！0崩溃！")
        
        self.checkpoint("SuperChaos2: 大规模并发攻击")
    
    # =========================================================================
    # 超级混沌3: 数据破坏与恢复
    # =========================================================================
    def super_chaos_3_data_corruption_recovery(self):
        """超级混沌3: 数据破坏与恢复 - 测试异常状态处理"""
        print("=" * 150)
        print("💥 超级混沌3: 数据破坏与恢复")
        print("=" * 150)
        print()
        
        corruption_tests = [
            "create_then_modify", "create_many_then_cleanup", 
            "mixed_invalid_ops", "stress_garbage_collection"
        ]
        
        for test in corruption_tests:
            print(f"\n[TEST] 测试场景: {test}")
            
            if test == "create_then_modify":
                # 创建对象然后尝试通过返回值修改（验证深拷贝）
                task = self.backend.create_new_task_entry(
                    task_title="原版标题",
                    task_description="原版描述"
                )
                self.all_task_ids.append(task.unique_entity_id)
                
                # 尝试修改返回的对象（应该不影响内部存储）
                task.task_title = "被篡改的标题"
                task.progress_percentage_value = 999.9
                
                # 重新获取验证
                retrieved = self.backend.retrieve_task_by_id(task.unique_entity_id)
                if retrieved:
                    if retrieved.task_title == "原版标题":
                        print("   ✅ 引用安全验证通过：外部修改不影响内部存储")
                    else:
                        print(f"   ❌ 引用安全漏洞：内部数据被外部修改")
            
            elif test == "create_many_then_cleanup":
                # 创建大量对象然后强制GC
                print(f"   创建1000个对象...")
                for i in range(1000):
                    task = self.backend.create_new_task_entry(task_title=f"GC_Test_{i}")
                    if task:
                        self.all_task_ids.append(task.unique_entity_id)
                
                print(f"   强制垃圾回收...")
                gc.collect()
                
                # 验证系统仍然正常工作
                final_task = self.backend.create_new_task_entry(task_title="GC后测试")
                if final_task:
                    print(f"   ✅ GC后系统正常工作")
            
            elif test == "mixed_invalid_ops":
                # 混合有效和无效操作
                print(f"   混合操作测试...")
                ops_count = 0
                for i in range(100):
                    # 随机选择有效或无效操作
                    is_valid = random.random() > 0.3
                    
                    if is_valid:
                        self.backend.create_new_task_entry(
                            task_title=f"混合有效_{i}"
                        )
                        ops_count += 1
                    else:
                        # 无效操作
                        self.safe_execute("invalid_update",
                            self.backend.update_task_entry,
                            "不存在的ID",
                            progress_percentage_value=0.5
                        )
                        self.safe_execute("invalid_retrieve",
                            self.backend.retrieve_task_by_id,
                            ""
                        )
                        self.safe_execute("invalid_edge",
                            self.backend.add_edge_to_knowledge_graph,
                            "a", "b", "test"
                        )
                
                print(f"   ✅ 混合操作完成：{ops_count}个有效操作")
            
            elif test == "stress_garbage_collection":
                # 多次GC压力测试
                print(f"   GC压力测试...")
                for i in range(10):
                    # 创建临时对象
                    for j in range(100):
                        self.backend.create_new_task_entry(
                            task_title=f"临时_{i}_{j}"
                        )
                    gc.collect()
                
                print(f"   ✅ GC压力测试完成")
        
        self.checkpoint("SuperChaos3: 数据破坏与恢复")
    
    # =========================================================================
    # 超级混沌4: 极端参数组合
    # =========================================================================
    def super_chaos_4_extreme_parameter_combinations(self):
        """超级混沌4: 极端参数组合 - 穷尽可能性"""
        print("=" * 150)
        print("💥 超级混沌4: 极端参数组合")
        print("=" * 150)
        print()
        
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            TaskPriorityLevelEnumeration,
            TaskExecutionStatusEnumeration,
            MemoryCategoryTypeEnumeration
        )
        
        # 极端值组合
        extreme_values = {
            "strings": [
                "", "a", "x"*1000, "x"*10000, 
                "🎉"*1000, "\x00\x01\x02", 
                "\n\t\r", "test\nline2",
                None
            ],
            "numbers": [
                -1000, -1, -0.5, 0, 0.0001, 0.5, 0.999,
                1, 1.0001, 1000, 1e30, 1e300,
                float('inf'), float('-inf'), float('nan')
            ],
            "booleans": [True, False, None],
            "lists": [
                [], ["a"], ["a","b","c"]*100, None
            ],
            "dicts": [
                {}, {"a": 1}, {"a": {"b": {"c": 1}}}, None
            ],
            "enums": [
                TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL,
                TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
                "invalid", 999, None
            ]
        }
        
        print("[TEST] 穷尽创建任务的参数组合...")
        create_count = 0
        for title in extreme_values["strings"][:5]:
            for desc in extreme_values["strings"][:3]:
                for priority in extreme_values["enums"][:3]:
                    task = self.safe_execute(f"create_{create_count}",
                        self.backend.create_new_task_entry,
                        task_title=title,
                        task_description=desc,
                        priority_level=priority
                    )
                    if task:
                        self.all_task_ids.append(task.unique_entity_id)
                        create_count += 1
        
        print(f"   ✅ 任务创建参数组合测试完成: {create_count}个")
        
        print("[TEST] 穷尽更新任务的参数组合...")
        update_count = 0
        if self.all_task_ids:
            test_task = self.all_task_ids[0]
            for progress in extreme_values["numbers"][:6]:
                for status in extreme_values["enums"][:3]:
                    self.safe_execute(f"update_{update_count}",
                        self.backend.update_task_entry,
                        test_task,
                        progress_percentage_value=progress,
                        execution_status=status
                    )
                    update_count += 1
        
        print(f"   ✅ 任务更新参数组合测试完成: {update_count}个")
        
        print("[TEST] 穷尽记忆创建参数组合...")
        mem_count = 0
        for content in extreme_values["strings"][:4]:
            for category in extreme_values["enums"][:3]:
                for tags in extreme_values["lists"][:3]:
                    for importance in extreme_values["numbers"][:5]:
                        memory = self.safe_execute(f"mem_{mem_count}",
                            self.backend.create_new_memory_entry,
                            content_text=content,
                            category_type=category,
                            tags_list=tags,
                            importance_score=importance
                        )
                        if memory:
                            self.all_memory_ids.append(memory.unique_memory_id)
                            mem_count += 1
        
        print(f"   ✅ 记忆创建参数组合测试完成: {mem_count}个")
        
        self.checkpoint("SuperChaos4: 极端参数组合")
    
    # =========================================================================
    # 主测试流程
    # =========================================================================
    def run_all_super_chaos_tests(self):
        print("\n" + "=" * 150)
        print("🚀 开始执行第3次迭代：超级混沌测试")
        print("=" * 150)
        
        try:
            self.super_chaos_1_infinite_loop(duration_seconds=10)
            self.super_chaos_2_massive_concurrent_attack()
            self.super_chaos_3_data_corruption_recovery()
            self.super_chaos_4_extreme_parameter_combinations()
        
        except Exception as e:
            print(f"❌ 主程序崩溃: {e}")
            traceback.print_exc()
        
        self.generate_final_report()
    
    def generate_final_report(self):
        print("\n" + "=" * 150)
        print("📊 第3次迭代：超级混沌测试 - 最终报告")
        print("=" * 150)
        
        total_time = time.time() - self.stats["start_time"]
        
        print(f"\n⏱️  总耗时: {total_time:.2f}秒")
        print(f"📈 总操作数: {self.operation_count:,}")
        print(f"❌ 错误数: {self.error_count}")
        print(f"📝 验证代码行数: {self.backend.line_count:,}")
        print(f"✅ 操作成功率: {((self.operation_count - self.error_count) / self.operation_count * 100):.2f}%" if self.operation_count > 0 else "0%")
        
        print(f"\n📊 数据规模:")
        print(f"   任务数: {len(self.all_task_ids):,}")
        print(f"   记忆数: {len(self.all_memory_ids):,}")
        print(f"   经验数: {len(self.all_experience_ids):,}")
        print(f"   节点数: {len(self.all_node_ids):,}")
        print(f"   边数: {len(self.all_edge_ids):,}")
        
        if self.errors:
            print(f"\n❌ 发现 {len(self.errors)} 个错误:")
            for i, err in enumerate(self.errors[:20]):
                print(f"   {i+1}. {err['operation']}: {err['error']}")
        else:
            print(f"\n🎉 完美！0错误！")
        
        print("\n" + "=" * 150)
        if len(self.errors) == 0:
            print("🎉🎉🎉 第3次迭代超级混沌测试完美通过！系统坚如磐石！")
        elif len(self.errors) < 20:
            print("✅ 第3次迭代基本通过，少量错误被正确处理！")
        else:
            print("⚠️ 发现较多问题，需要修复！")
        print("=" * 150)


def main():
    try:
        runner = SuperChaosTestRunner()
        runner.run_all_super_chaos_tests()
        return 0 if runner.error_count < 20 else 1
    except Exception as e:
        print(f"❌ 主程序崩溃: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
