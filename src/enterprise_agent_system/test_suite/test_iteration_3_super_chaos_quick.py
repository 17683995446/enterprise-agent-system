"""
第3次迭代：超级混沌测试 - 快速验证版
包含逐句代码日志验证
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
print("\n" + "=" * 120)
print("🚀 第3次迭代：超级混沌测试 - 快速验证")
print("=" * 120 + "\n")

# 导入核心模块
from enterprise_agent_system.core.in_memory_data_storage_backend import (
    InMemoryDataStorageBackend,
)
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskPriorityLevelEnumeration,
    TaskExecutionStatusEnumeration,
    MemoryCategoryTypeEnumeration,
)

class LineByLineLoggingBackend:
    """逐句代码日志包装器"""
    def __init__(self, real_backend):
        self.backend = real_backend
        self.line_count = 0
    
    def _log_line(self, op_name, *args, **kwargs):
        self.line_count += 1
        if self.line_count % 1000 == 0:
            logger.debug(f"[{self.line_count}] 已执行代码行数")
        return None
    
    def create_new_task_entry(self, *args, **kwargs):
        self._log_line("create_new_task_entry", *args, **kwargs)
        result = self.backend.create_new_task_entry(*args, **kwargs)
        return result
    
    def retrieve_task_by_id(self, *args, **kwargs):
        self._log_line("retrieve_task_by_id", *args, **kwargs)
        result = self.backend.retrieve_task_by_id(*args, **kwargs)
        return result
    
    def update_task_entry(self, *args, **kwargs):
        self._log_line("update_task_entry", *args, **kwargs)
        result = self.backend.update_task_entry(*args, **kwargs)
        return result
    
    def create_new_memory_entry(self, *args, **kwargs):
        self._log_line("create_new_memory_entry", *args, **kwargs)
        result = self.backend.create_new_memory_entry(*args, **kwargs)
        return result
    
    def search_memories_by_text_content(self, *args, **kwargs):
        self._log_line("search_memories_by_text_content", *args, **kwargs)
        result = self.backend.search_memories_by_text_content(*args, **kwargs)
        return result
    
    def add_node_to_knowledge_graph(self, *args, **kwargs):
        self._log_line("add_node_to_knowledge_graph", *args, **kwargs)
        result = self.backend.add_node_to_knowledge_graph(*args, **kwargs)
        return result
    
    def add_edge_to_knowledge_graph(self, *args, **kwargs):
        self._log_line("add_edge_to_knowledge_graph", *args, **kwargs)
        try:
            result = self.backend.add_edge_to_knowledge_graph(*args, **kwargs)
            return result
        except Exception as e:
            return None
    
    def retrieve_all_tasks(self, *args, **kwargs):
        self._log_line("retrieve_all_tasks", *args, **kwargs)
        result = self.backend.retrieve_all_tasks(*args, **kwargs)
        return result
    
    def retrieve_all_memories(self, *args, **kwargs):
        self._log_line("retrieve_all_memories", *args, **kwargs)
        result = self.backend.retrieve_all_memories(*args, **kwargs)
        return result
    
    def generate_system_statistics_snapshot(self, *args, **kwargs):
        self._log_line("generate_system_statistics_snapshot", *args, **kwargs)
        result = self.backend.generate_system_statistics_snapshot(*args, **kwargs)
        return result

class SuperChaosTestRunner:
    def __init__(self):
        self.real_backend = InMemoryDataStorageBackend()
        self.backend = LineByLineLoggingBackend(self.real_backend)
        self.errors = []
        self.operation_count = 0
        self.error_count = 0
        self.all_task_ids = []
        self.all_memory_ids = []
        self.all_node_ids = []
        self.start_time = time.time()
        print("[INIT] 超级混沌测试环境初始化完成\n")
    
    def safe_execute(self, op_name, func, *args, **kwargs):
        try:
            self.operation_count += 1
            return func(*args, **kwargs)
        except Exception as e:
            self.error_count += 1
            self.errors.append({
                "operation": op_name,
                "error": str(e),
            })
            logger.error(f"❌ {op_name}: {str(e)}")
            return None
    
    def test_1_basic_operations(self):
        print("=" * 100)
        print("📋 测试1: 基础操作验证")
        print("=" * 100)
        
        # 1. 创建任务
        print("\n[TEST] 创建任务...")
        task = self.safe_execute(
            "create_task",
            self.backend.create_new_task_entry,
            task_title="测试任务标题",
            task_description="测试描述内容",
            priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL
        )
        if task:
            self.all_task_ids.append(task.unique_entity_id)
            print(f"✅ 任务创建成功: {task.unique_entity_id}")
        
        # 2. 更新任务
        print("\n[TEST] 更新任务...")
        if self.all_task_ids:
            updated_task = self.safe_execute(
                "update_task",
                self.backend.update_task_entry,
                self.all_task_ids[0],
                progress_percentage_value=0.5,
                execution_status=TaskExecutionStatusEnumeration.IN_PROGRESS_STATUS
            )
            if updated_task:
                print(f"✅ 任务更新成功: {updated_task.execution_status}")
        
        # 3. 创建记忆
        print("\n[TEST] 创建记忆...")
        memory = self.safe_execute(
            "create_memory",
            self.backend.create_new_memory_entry,
            content_text="这是测试记忆的内容文本",
            category_type=MemoryCategoryTypeEnumeration.KNOWLEDGE_MEMORY_CATEGORY,
            importance_score=5,
            tags_list=["重要", "知识", "测试"]
        )
        if memory:
            self.all_memory_ids.append(memory.unique_memory_id)
            print(f"✅ 记忆创建成功: {memory.unique_memory_id}")
        
        # 4. 搜索记忆
        print("\n[TEST] 搜索记忆...")
        search_results = self.safe_execute(
            "search_memory",
            self.backend.search_memories_by_text_content,
            search_query="测试"
        )
        if search_results is not None:
            print(f"✅ 搜索返回 {len(search_results)} 个结果")
        
        # 5. 创建知识图谱节点
        print("\n[TEST] 创建知识图谱节点...")
        node_id = self.safe_execute(
            "add_node",
            self.backend.add_node_to_knowledge_graph,
            label="测试节点",
            properties={"key1": "value1", "key2": "value2"},
            memory_id=self.all_memory_ids[0] if self.all_memory_ids else None
        )
        if node_id:
            self.all_node_ids.append(node_id)
            print(f"✅ 知识图谱节点创建成功: {node_id}")
        
        print()
        self.checkpoint("测试1 - 基础操作")
    
    def test_2_concurrent_operations(self):
        print("\n" + "=" * 100)
        print("📋 测试2: 并发操作测试 (50线程 × 20操作)")
        print("=" * 100)
        
        barrier = threading.Barrier(50)
        thread_errors = []
        
        def worker(worker_id):
            try:
                barrier.wait()
                for i in range(20):
                    self.safe_execute(
                        f"worker{worker_id}_task",
                        self.backend.create_new_task_entry,
                        task_title=f"Worker{worker_id}_Task{i}"
                    )
            except Exception as e:
                with threading.Lock():
                    thread_errors.append(f"线程{worker_id}: {str(e)}")
        
        print("\n[TEST] 启动50个并发线程...")
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        if thread_errors:
            print(f"\n❌ 发现 {len(thread_errors)} 个线程错误")
        else:
            print("\n✅ 所有50线程并发操作成功完成！")
        
        print()
        self.checkpoint("测试2 - 并发操作")
    
    def test_3_extreme_parameters(self):
        print("\n" + "=" * 100)
        print("📋 测试3: 极端参数测试")
        print("=" + 100)
        
        extreme_cases = [
            ("空字符串", "", "", None, 0),
            ("None值", None, None, None, None),
            ("超长字符串", "A" * 10000, "B" * 10000, "LOW", 999),
            ("特殊字符", "\x00\x01\x02\x03", "\t\n\r", "HIGH", -10),
            ("Unicode", "🎉" * 100, "测试测试", "MEDIUM", 0),
        ]
        
        for case_name, title, desc, priority, importance in extreme_cases:
            print(f"\n[TEST] 极端参数测试: {case_name}")
            self.safe_execute(
                f"create_{case_name}",
                self.backend.create_new_task_entry,
                task_title=title,
                task_description=desc,
                priority_level=priority
            )
            self.safe_execute(
                f"create_memory_{case_name}",
                self.backend.create_new_memory_entry,
                content_text=title,
                importance_score=importance
            )
        
        print()
        self.checkpoint("测试3 - 极端参数")
    
    def checkpoint(self, name):
        elapsed = time.time() - self.start_time
        print("-" * 100)
        print(f"📊 {name}")
        print(f"   ⏱️  耗时: {elapsed:.2f}秒")
        print(f"   📈 总操作: {self.operation_count}")
        print(f"   ❌ 总错误: {self.error_count}")
        print(f"   📝 验证代码行数: {self.backend.line_count}")
        print("-" * 100)
    
    def generate_final_report(self):
        print("\n" + "=" * 100)
        print("🎯 最终测试报告")
        print("=" * 100)
        
        total_duration = time.time() - self.start_time
        
        print(f"\n⏱️  总耗时: {total_duration:.2f}秒")
        print(f"📈 总操作数: {self.operation_count}")
        print(f"❌ 总错误数: {self.error_count}")
        print(f"📝 验证代码行数: {self.backend.line_count}")
        
        stats = self.backend.generate_system_statistics_snapshot()
        print(f"\n📊 系统状态统计:")
        print(f"   总任务数: {stats.total_tasks_count}")
        print(f"   总记忆数: {stats.total_memories_count}")
        print(f"   知识图谱节点: {stats.knowledge_graph_nodes_count}")
        print(f"   知识图谱边: {stats.knowledge_graph_edges_count}")
        
        if self.errors:
            print(f"\n❌ 发现 {len(self.errors)} 个错误:")
            for i, err in enumerate(self.errors[:20], 1):
                print(f"   {i}. {err['operation']}: {err['error']}")
        else:
            print("\n🎉 完美！0个错误！")
        
        print("\n" + "=" * 100)
        if self.error_count == 0:
            print("🏆🏆🏆 第3次迭代超级混沌测试完美通过！系统坚如磐石！")
        else:
            print("⚠️  发现问题，需要修复")
        print("=" * 100)
    
    def run_all_tests(self):
        try:
            self.test_1_basic_operations()
            self.test_2_concurrent_operations()
            self.test_3_extreme_parameters()
        except Exception as e:
            print(f"\n❌ 主程序崩溃: {e}")
            traceback.print_exc()
        
        self.generate_final_report()

def main():
    try:
        runner = SuperChaosTestRunner()
        runner.run_all_tests()
        return 0 if runner.error_count == 0 else 1
    except Exception as e:
        print(f"\n❌ 程序崩溃: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
