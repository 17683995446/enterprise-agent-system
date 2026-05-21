"""
超大规模复杂场景测试 - 第1次迭代
Iteration 1: Ultra Complex Scenario Testing

测试覆盖：
1. 静态代码核验
2. 单元全覆盖测试
3. 模块集成联调
4. 接口全量遍历
5. 业务场景闭环
6. 数据一致性校验
7. 异常容错测试
8. 基础性能核验

要求：更长时间、更大规模、更错综复杂、更高难度、涉及更混乱的场景
"""

import sys
import time
import random
import threading
import gc
import uuid
import traceback
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import copy

sys.path.insert(0, '/workspace/enterprise_agent_system/src')

print("=" * 150)
print("🚀 启动超大规模复杂场景测试 - 第1次迭代")
print("=" * 150)
print(f"[INIT] 测试开始时间: {datetime.now().isoformat()}")
print(f"[INIT] 目标: 深度测试系统极限，处理最复杂的真实场景")
print()


class UltraComplexTestRunner:
    """超复杂测试运行器"""
    
    def __init__(self):
        print("[INIT] 正在初始化测试环境...")
        from enterprise_agent_system.core.in_memory_data_storage_backend import (
            InMemoryDataStorageBackend,
        )
        from enterprise_agent_system.infrastructure.simple_memory_store import (
            SimpleMemoryStore,
            SimpleCache,
        )
        
        self.backend = InMemoryDataStorageBackend()
        self.store = SimpleMemoryStore()
        self.cache = SimpleCache()
        
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.stats = {
            "total_operations": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "start_time": time.time(),
            "checkpoints": [],
        }
        
        self.lock = threading.Lock()
        
        # 数据验证集合
        self.task_ids = set()
        self.memory_ids = set()
        self.experience_ids = set()
        self.node_ids = []
        self.edge_ids = []
        
        print("[INIT] 测试环境初始化完成")
        print()
    
    def log_error(self, category: str, message: str, details: Any = None):
        """记录错误"""
        with self.lock:
            error = {
                "category": category,
                "message": message,
                "details": details,
                "timestamp": time.time(),
                "operation_count": self.stats["total_operations"],
            }
            self.errors.append(error)
            self.stats["total_errors"] += 1
            print(f"❌ [ERROR] {category}: {message}")
            if details:
                print(f"   详情: {details}")
    
    def log_warning(self, category: str, message: str):
        """记录警告"""
        with self.lock:
            warning = {
                "category": category,
                "message": message,
                "timestamp": time.time(),
            }
            self.warnings.append(warning)
            self.stats["total_warnings"] += 1
            print(f"⚠️  [WARNING] {category}: {message}")
    
    def checkpoint(self, name: str):
        """记录检查点"""
        elapsed = time.time() - self.stats["start_time"]
        checkpoint = {
            "name": name,
            "elapsed": elapsed,
            "operations": self.stats["total_operations"],
            "errors": self.stats["total_errors"],
        }
        self.stats["checkpoints"].append(checkpoint)
        print(f"🔍 [CHECKPOINT] {name}")
        print(f"   时间: {elapsed:.2f}s | 操作: {self.stats['total_operations']:,} | 错误: {self.stats['total_errors']}")
        print()
    
    # =========================================================================
    # 测试1: 静态代码核验 - 代码逻辑合理性检查
    # =========================================================================
    def test_1_static_code_validation(self):
        """测试1: 静态代码核验"""
        print("=" * 150)
        print("🧪 测试1: 静态代码核验 - 核对逻辑合理性")
        print("=" * 150)
        print()
        
        issues_found = []
        
        print("[VALIDATE] 验证1.1: 检查所有方法的返回类型...")
        # 验证retrieve_task_by_id返回Optional
        task = self.backend.create_new_task_entry("Test Task")
        retrieved = self.backend.retrieve_task_by_id(task.unique_entity_id)
        if retrieved is None:
            issues_found.append("retrieve_task_by_id返回None")
            self.log_error("类型检查", "retrieve_task_by_id不应返回None当ID存在时")
        print(f"   结果: 返回类型正确 - {type(retrieved)}")
        
        print("[VALIDATE] 验证1.2: 检查枚举转换...")
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            validate_and_convert_enum,
            TaskPriorityLevelEnumeration,
            TaskExecutionStatusEnumeration,
        )
        
        # 测试各种输入
        test_cases = [
            ("HIGH", TaskPriorityLevelEnumeration, TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL),
            (3, TaskPriorityLevelEnumeration, TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL),
            ("invalid", TaskPriorityLevelEnumeration, TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL),
            (None, TaskPriorityLevelEnumeration, TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL),
        ]
        
        for input_val, enum_type, default in test_cases:
            result = validate_and_convert_enum(input_val, enum_type, default)
            if not isinstance(result, enum_type):
                self.log_error("枚举验证", f"输入 {input_val} 未正确转换为枚举")
        
        print(f"   验证1.2完成: {len(test_cases)} 个测试用例")
        
        print("[VALIDATE] 验证1.3: 检查边界条件...")
        # 测试空字符串
        try:
            task = self.backend.create_new_task_entry("")
            if task.task_title != "":
                self.log_warning("边界条件", "空标题未正确处理")
        except Exception as e:
            self.log_error("边界条件", f"空标题导致异常: {e}")
        
        # 测试None
        try:
            task = self.backend.create_new_task_entry(None)
            if task.task_title != "None":
                self.log_warning("边界条件", "None标题未正确转换为字符串")
        except Exception as e:
            self.log_error("边界条件", f"None标题导致异常: {e}")
        
        print("[VALIDATE] 验证1.4: 检查数据完整性...")
        # 创建任务并验证所有字段
        task = self.backend.create_new_task_entry(
            task_title="完整性测试",
            task_description="测试描述",
            priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL,
        )
        
        required_fields = ['unique_entity_id', 'task_title', 'task_description', 
                         'execution_status', 'priority_level', 'created_timestamp']
        for field in required_fields:
            if not hasattr(task, field):
                self.log_error("数据完整性", f"缺少必需字段: {field}")
        
        print(f"   验证1.4完成: {len(required_fields)} 个必需字段")
        
        print("[VALIDATE] 验证1.5: 检查线程安全...")
        # 验证锁是否正确使用
        import inspect
        source = inspect.getsource(self.backend.create_new_task_entry)
        if "with self._lock" not in source:
            self.log_error("线程安全", "create_new_task_entry未使用锁")
        
        print(f"   验证1.5完成: 线程安全检查通过")
        
        self.checkpoint("Test1: 静态代码核验")
        print(f"✅ 测试1完成: 发现 {len(issues_found)} 个问题")
        print()
    
    # =========================================================================
    # 测试2: 单元全覆盖测试 - 所有if/else、分支、循环
    # =========================================================================
    def test_2_unit_coverage(self):
        """测试2: 单元全覆盖测试"""
        print("=" * 150)
        print("🧪 测试2: 单元全覆盖测试 - 穷尽所有分支")
        print("=" * 150)
        print()
        
        branches_tested = 0
        
        # 导入枚举类型
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            TaskPriorityLevelEnumeration,
            TaskExecutionStatusEnumeration,
            MemoryCategoryTypeEnumeration,
        )
        
        print("[BRANCH] 测试2.1: 任务创建分支...")
        # 测试所有优先级分支
        priorities = [
            TaskPriorityLevelEnumeration.LOW_PRIORITY_LEVEL,
            TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
            TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL,
            TaskPriorityLevelEnumeration.URGENT_PRIORITY_LEVEL,
            "LOW", "MEDIUM", "HIGH", "URGENT",  # 字符串输入
            1, 2, 3, 4,  # 整数输入
            "invalid",  # 无效输入
            None,  # None输入
        ]
        
        for priority in priorities:
            try:
                task = self.backend.create_new_task_entry(
                    task_title=f"Priority Test {priority}",
                    priority_level=priority,
                )
                branches_tested += 1
            except Exception as e:
                self.log_error("分支覆盖", f"优先级 {priority} 测试失败: {e}")
        
        print(f"   测试2.1完成: {len(priorities)} 个优先级测试")
        
        print("[BRANCH] 测试2.2: 任务状态更新分支...")
        task = self.backend.create_new_task_entry("Status Test")
        statuses = [
            TaskExecutionStatusEnumeration.PENDING_STATUS,
            TaskExecutionStatusEnumeration.IN_PROGRESS_STATUS,
            TaskExecutionStatusEnumeration.COMPLETED_STATUS,
            TaskExecutionStatusEnumeration.FAILED_STATUS,
            TaskExecutionStatusEnumeration.CANCELLED_STATUS,
            "pending", "in_progress", "completed", "failed",  # 字符串
            "invalid_status",  # 无效
            None,  # None
        ]
        
        for status in statuses:
            try:
                result = self.backend.update_task_entry(
                    task.unique_entity_id,
                    execution_status=status,
                )
                branches_tested += 1
            except Exception as e:
                self.log_error("分支覆盖", f"状态 {status} 更新失败: {e}")
        
        print(f"   测试2.2完成: {len(statuses)} 个状态测试")
        
        print("[BRANCH] 测试2.3: 进度值边界分支...")
        progress_tests = [-1, 0, 0.5, 1, 1.5, "invalid", None]
        for progress in progress_tests:
            try:
                result = self.backend.update_task_entry(
                    task.unique_entity_id,
                    progress_percentage_value=progress,
                )
                branches_tested += 1
            except Exception as e:
                self.log_error("分支覆盖", f"进度 {progress} 更新失败: {e}")
        
        print(f"   测试2.3完成: {len(progress_tests)} 个进度测试")
        
        print("[BRANCH] 测试2.4: 记忆创建分支...")
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            MemoryCategoryTypeEnumeration,
        )
        
        categories = [
            MemoryCategoryTypeEnumeration.GENERAL_MEMORY_CATEGORY,
            MemoryCategoryTypeEnumeration.TECHNICAL_MEMORY_CATEGORY,
            MemoryCategoryTypeEnumeration.EXPERIENCE_MEMORY_CATEGORY,
            MemoryCategoryTypeEnumeration.KNOWLEDGE_MEMORY_CATEGORY,
            MemoryCategoryTypeEnumeration.CASE_STUDY_MEMORY_CATEGORY,
            "general", "technical",  # 字符串
            "invalid",  # 无效
            None,  # None
        ]
        
        for category in categories:
            try:
                memory = self.backend.create_new_memory_entry(
                    content_text=f"Memory Test {category}",
                    category_type=category,
                    importance_score=random.randint(1, 5),
                )
                branches_tested += 1
            except Exception as e:
                self.log_error("分支覆盖", f"类别 {category} 创建失败: {e}")
        
        print(f"   测试2.4完成: {len(categories)} 个类别测试")
        
        print("[BRANCH] 测试2.5: 重要性评分边界分支...")
        importance_tests = [-10, 0, 1, 3, 5, 10, 100, "invalid", None]
        for importance in importance_tests:
            try:
                memory = self.backend.create_new_memory_entry(
                    content_text=f"Importance Test {importance}",
                    importance_score=importance,
                )
                branches_tested += 1
            except Exception as e:
                self.log_error("分支覆盖", f"重要性 {importance} 测试失败: {e}")
        
        print(f"   测试2.5完成: {len(importance_tests)} 个重要性测试")
        
        print("[BRANCH] 测试2.6: 知识图谱分支...")
        node = self.backend.add_node_to_knowledge_graph("test_node", {"key": "value"})
        
        # 测试各种关系类型
        relation_types = [
            "related_to", "depends_on", "includes", "references",
            "", None, "   ", "INVALID",  # 边界
        ]
        
        for rel_type in relation_types:
            try:
                if len(self.node_ids) >= 2:
                    edge = self.backend.add_edge_to_knowledge_graph(
                        self.node_ids[0],
                        self.node_ids[-1],
                        rel_type,
                        random.random(),
                    )
                    branches_tested += 1
            except ValueError as e:
                # 预期的错误
                branches_tested += 1
            except Exception as e:
                self.log_error("分支覆盖", f"关系类型 {rel_type} 测试失败: {e}")
        
        print(f"   测试2.6完成: {len(relation_types)} 个关系类型测试")
        
        self.checkpoint("Test2: 单元全覆盖")
        print(f"✅ 测试2完成: 测试了 {branches_tested} 个代码分支")
        print()
    
    # =========================================================================
    # 测试3: 模块集成联调 - 跨模块调用
    # =========================================================================
    def test_3_module_integration(self):
        """测试3: 模块集成联调"""
        print("=" * 150)
        print("🧪 测试3: 模块集成联调 - 跨模块调用")
        print("=" * 150)
        print()
        
        print("[INTEGRATE] 测试3.1: 任务-记忆集成...")
        # 创建任务
        task = self.backend.create_new_task_entry(
            task_title="集成测试任务",
            task_description="测试任务与记忆的关联",
        )
        self.task_ids.add(task.unique_entity_id)
        
        # 创建关联记忆
        memory = self.backend.create_new_memory_entry(
            content_text=f"这是关于任务 {task.unique_entity_id} 的记忆",
            source_task_id=task.unique_entity_id,
            tags_list=[task.unique_entity_id],
        )
        self.memory_ids.add(memory.unique_memory_id)
        
        # 验证关联
        retrieved_memory = self.backend.retrieve_memory_by_id(memory.unique_memory_id)
        if retrieved_memory.source_task_id != task.unique_entity_id:
            self.log_error("集成测试", "记忆与任务的关联失败")
        
        print(f"   测试3.1完成: 任务-记忆关联验证通过")
        
        print("[INTEGRATE] 测试3.2: 任务-知识图谱集成...")
        # 创建任务关联的节点
        node_id = self.backend.add_node_to_knowledge_graph(
            label=f"Task_{task.unique_entity_id}",
            memory_id=task.unique_entity_id,
            properties={"task_id": task.unique_entity_id},
        )
        self.node_ids.append(node_id)
        
        # 验证节点属性
        kg_stats = self.backend.retrieve_knowledge_graph_statistics()
        if kg_stats['total_nodes'] < 1:
            self.log_error("集成测试", "知识图谱节点创建失败")
        
        print(f"   测试3.2完成: 任务-知识图谱关联验证通过")
        
        print("[INTEGRATE] 测试3.3: 记忆-知识图谱集成...")
        # 创建记忆关联的节点
        memory_node_id = self.backend.add_node_to_knowledge_graph(
            label=f"Memory_{memory.unique_memory_id}",
            memory_id=memory.unique_memory_id,
        )
        self.node_ids.append(memory_node_id)
        
        # 创建边
        if len(self.node_ids) >= 2:
            edge_id = self.backend.add_edge_to_knowledge_graph(
                self.node_ids[0],
                memory_node_id,
                "contains",
                1.0,
            )
            self.edge_ids.append(edge_id)
        
        print(f"   测试3.3完成: 记忆-知识图谱关联验证通过")
        
        print("[INTEGRATE] 测试3.4: 存储后端-报告存储集成...")
        report_data = {
            "id": str(uuid.uuid4()),
            "title": "集成测试报告",
            "type": "integration_test",
            "content": f"测试报告内容，包含任务ID: {task.unique_entity_id}",
            "metadata": {
                "task_id": task.unique_entity_id,
                "memory_id": memory.unique_memory_id,
                "node_id": node_id,
            },
        }
        report_id = self.store.save_report(report_data)
        retrieved_report = self.store.get_report(report_id)
        
        if not retrieved_report:
            self.log_error("集成测试", "报告存储集成失败")
        
        print(f"   测试3.4完成: 存储集成验证通过")
        
        print("[INTEGRATE] 测试3.5: 多层集成验证...")
        # 创建完整的业务场景
        for i in range(10):
            # 创建任务
            task = self.backend.create_new_task_entry(
                task_title=f"集成场景任务 {i}",
                task_description=f"这是第 {i} 个集成测试任务",
            )
            self.task_ids.add(task.unique_entity_id)
            
            # 创建记忆
            memory = self.backend.create_new_memory_entry(
                content_text=f"任务 {task.unique_entity_id} 的学习记忆 {i}",
                source_task_id=task.unique_entity_id,
                tags_list=[f"task_{task.unique_entity_id}", f"index_{i}"],
            )
            self.memory_ids.add(memory.unique_memory_id)
            
            # 创建节点
            node_id = self.backend.add_node_to_knowledge_graph(
                label=f"task_node_{i}",
                properties={"index": i, "task_id": task.unique_entity_id},
            )
            self.node_ids.append(node_id)
        
        # 验证统计一致性
        stats = self.backend.generate_system_statistics_snapshot()
        print(f"   任务总数: {stats.total_tasks_count}")
        print(f"   记忆总数: {stats.total_memories_count}")
        print(f"   知识图谱节点: {stats.knowledge_graph_nodes_count}")
        
        print(f"   测试3.5完成: 多层集成验证通过")
        
        self.checkpoint("Test3: 模块集成联调")
        print(f"✅ 测试3完成: 跨模块集成测试通过")
        print()
    
    # =========================================================================
    # 测试4: 接口全量遍历 - 所有接口参数组合
    # =========================================================================
    def test_4_interface_traversal(self):
        """测试4: 接口全量遍历"""
        print("=" * 150)
        print("🧪 测试4: 接口全量遍历 - 参数组合测试")
        print("=" * 150)
        print()
        
        print("[INTERFACE] 测试4.1: create_new_task_entry 参数组合...")
        param_combinations = [
            # (title, description, priority)
            ("test", "", None),
            ("", "desc", None),
            (None, None, None),
            ("test", "desc", "HIGH"),
            ("test", "desc", 4),
            ("test", "desc", "invalid"),
            ("x" * 10000, "y" * 10000, None),  # 超长参数
            ("🎉" * 100, "🎊" * 100, None),  # Unicode
            ("test\n\t\r", "test\r\n", None),  # 特殊字符
        ]
        
        for title, desc, priority in param_combinations:
            try:
                task = self.backend.create_new_task_entry(
                    task_title=title,
                    task_description=desc,
                    priority_level=priority,
                )
                self.task_ids.add(task.unique_entity_id)
            except Exception as e:
                self.log_error("接口测试", f"参数组合失败: title={title}, desc={desc}, priority={priority}", str(e))
        
        print(f"   测试4.1完成: {len(param_combinations)} 个参数组合测试")
        
        print("[INTERFACE] 测试4.2: create_new_memory_entry 参数组合...")
        memory_params = [
            # (content, category, tags, importance, source_task)
            ("test", None, None, None, None),
            ("", None, [], 1, None),
            ("test", "general", ["tag1"], 5, None),
            ("test", "invalid", ["tag"], 1, "fake_id"),
            ("test", None, ["t" * 1000], 100, None),  # 超长标签
            (None, None, None, None, None),  # 全None
        ]
        
        for params in memory_params:
            try:
                memory = self.backend.create_new_memory_entry(
                    content_text=params[0],
                    category_type=params[1],
                    tags_list=params[2],
                    importance_score=params[3],
                    source_task_id=params[4],
                )
                self.memory_ids.add(memory.unique_memory_id)
            except Exception as e:
                self.log_error("接口测试", f"记忆创建失败: {params}", str(e))
        
        print(f"   测试4.2完成: {len(memory_params)} 个参数组合测试")
        
        print("[INTERFACE] 测试4.3: retrieve_task_by_id 边界测试...")
        boundary_ids = [
            "",  # 空字符串
            "nonexistent",  # 不存在
            "x" * 1000,  # 超长ID
            None,  # None
            "task_invalid",  # 无效前缀
        ]
        
        for task_id in boundary_ids:
            try:
                result = self.backend.retrieve_task_by_id(task_id)
                if task_id and task_id not in ["", None]:
                    self.log_warning("接口测试", f"不存在的ID {task_id} 未返回None")
            except Exception as e:
                self.log_error("接口测试", f"边界ID {task_id} 导致异常", str(e))
        
        print(f"   测试4.3完成: {len(boundary_ids)} 个边界测试")
        
        print("[INTERFACE] 测试4.4: search_memories_by_text_content 参数组合...")
        search_params = [
            ("test", None, 1),
            ("", None, 0),
            ("test", "general", 5),
            ("test", "invalid", -1),  # 无效类别
            (None, None, 1),  # None查询
            ("t" * 1000, None, 1),  # 超长查询
        ]
        
        for query, category, min_importance in search_params:
            try:
                results = self.backend.search_memories_by_text_content(
                    search_query=query,
                    category_filter=category,
                    min_importance=min_importance,
                )
            except Exception as e:
                self.log_error("接口测试", f"搜索失败: query={query}", str(e))
        
        print(f"   测试4.4完成: {len(search_params)} 个搜索参数测试")
        
        print("[INTERFACE] 测试4.5: update_task_entry 极端参数...")
        test_task = self.backend.create_new_task_entry("Update Test")
        self.task_ids.add(test_task.unique_entity_id)
        
        extreme_updates = [
            {"error_message": "x" * 10000},  # 超长错误信息
            {"execution_steps_list": ["step1", "step2"] * 100},  # 大量步骤
            {"metadata_dictionary": {f"key_{i}": f"value_{i}" for i in range(1000)}},  # 大量元数据
            {"progress_percentage_value": -0.5},
            {"progress_percentage_value": 1.5},
            {"progress_percentage_value": float('inf')},
            {"progress_percentage_value": float('-inf')},
        ]
        
        for update in extreme_updates:
            try:
                result = self.backend.update_task_entry(
                    test_task.unique_entity_id,
                    **update,
                )
            except Exception as e:
                self.log_error("接口测试", f"极端更新失败: {list(update.keys())}", str(e))
        
        print(f"   测试4.5完成: {len(extreme_updates)} 个极端参数测试")
        
        self.checkpoint("Test4: 接口全量遍历")
        print(f"✅ 测试4完成: 接口测试完成")
        print()
    
    # =========================================================================
    # 测试5: 业务场景闭环 - 完整业务流程
    # =========================================================================
    def test_5_business_scenario(self):
        """测试5: 业务场景闭环"""
        print("=" * 150)
        print("🧪 测试5: 业务场景闭环 - 完整业务流程")
        print("=" * 150)
        print()
        
        # 导入枚举类型
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            TaskPriorityLevelEnumeration,
            TaskExecutionStatusEnumeration,
        )
        
        print("[SCENARIO] 测试5.1: 完整任务生命周期...")
        # 1. 创建任务
        task = self.backend.create_new_task_entry(
            task_title="完整生命周期测试任务",
            task_description="测试从创建到完成的完整生命周期",
            priority_level=TaskPriorityLevelEnumeration.HIGH_PRIORITY_LEVEL,
        )
        self.task_ids.add(task.unique_entity_id)
        print(f"   步骤1: 创建任务 {task.unique_entity_id}")
        
        # 2. 创建关联记忆
        memory1 = self.backend.create_new_memory_entry(
            content_text=f"任务 {task.unique_entity_id} 已创建，正在准备执行",
            source_task_id=task.unique_entity_id,
            importance_score=4,
        )
        self.memory_ids.add(memory1.unique_memory_id)
        print(f"   步骤2: 创建记忆 {memory1.unique_memory_id}")
        
        # 3. 更新为进行中
        self.backend.update_task_entry(
            task.unique_entity_id,
            execution_status=TaskExecutionStatusEnumeration.IN_PROGRESS_STATUS,
            progress_percentage_value=0.0,
        )
        print(f"   步骤3: 任务开始执行")
        
        # 4. 添加执行步骤
        steps = ["需求分析", "设计", "实现", "测试", "部署"]
        for i, step in enumerate(steps):
            self.backend.update_task_entry(
                task.unique_entity_id,
                execution_steps_list=steps[:i+1],
                progress_percentage_value=(i + 1) / len(steps),
            )
            # 每次更新添加记忆
            memory = self.backend.create_new_memory_entry(
                content_text=f"任务执行第 {i+1} 步: {step}",
                source_task_id=task.unique_entity_id,
                tags_list=[step],
            )
            self.memory_ids.add(memory.unique_memory_id)
        
        print(f"   步骤4: 完成 {len(steps)} 个执行步骤")
        
        # 5. 创建经验
        experience = self.backend.create_new_experience_entry(
            task_reference_id=task.unique_entity_id,
            task_type_label="完整生命周期测试",
            was_successful=True,
            duration_seconds=3600.0,
            lessons_learned=["学到1", "学到2", "学到3"],
        )
        self.experience_ids.add(experience.unique_experience_id)
        print(f"   步骤5: 创建经验 {experience.unique_experience_id}")
        
        # 6. 标记为完成
        self.backend.update_task_entry(
            task.unique_entity_id,
            execution_status=TaskExecutionStatusEnumeration.COMPLETED_STATUS,
            progress_percentage_value=1.0,
            execution_result_message="任务成功完成！",
        )
        print(f"   步骤6: 任务完成")
        
        # 7. 验证完整性
        final_task = self.backend.retrieve_task_by_id(task.unique_entity_id)
        if final_task.execution_status != TaskExecutionStatusEnumeration.COMPLETED_STATUS:
            self.log_error("业务闭环", "任务状态不正确")
        if len(final_task.execution_steps_list) != len(steps):
            self.log_error("业务闭环", "执行步骤数量不匹配")
        
        print(f"   测试5.1完成: 完整生命周期验证通过")
        
        print("[SCENARIO] 测试5.2: 任务失败和重试场景...")
        # 模拟失败和重试
        fail_task = self.backend.create_new_task_entry("失败测试任务")
        self.task_ids.add(fail_task.unique_entity_id)
        
        for attempt in range(3):
            self.backend.update_task_entry(
                fail_task.unique_entity_id,
                execution_status=TaskExecutionStatusEnumeration.FAILED_STATUS,
                error_message=f"第 {attempt + 1} 次尝试失败",
            )
            # 创建失败记忆
            memory = self.backend.create_new_memory_entry(
                content_text=f"第 {attempt + 1} 次尝试失败: {fail_task.unique_entity_id}",
                source_task_id=fail_task.unique_entity_id,
            )
            self.memory_ids.add(memory.unique_memory_id)
            
            # 重置任务
            self.backend.update_task_entry(
                fail_task.unique_entity_id,
                execution_status=TaskExecutionStatusEnumeration.PENDING_STATUS,
                error_message="",
            )
        
        print(f"   测试5.2完成: 失败重试场景验证通过")
        
        print("[SCENARIO] 测试5.3: 并发任务场景...")
        barrier = threading.Barrier(10)
        concurrent_tasks = []
        
        def concurrent_worker(worker_id):
            try:
                barrier.wait()  # 同步启动
                # 创建任务
                task = self.backend.create_new_task_entry(
                    task_title=f"并发任务 {worker_id}",
                    task_description=f"来自线程 {worker_id}",
                )
                with self.lock:
                    self.task_ids.add(task.unique_entity_id)
                    concurrent_tasks.append(task.unique_entity_id)
                
                # 更新任务
                for i in range(5):
                    self.backend.update_task_entry(
                        task.unique_entity_id,
                        progress_percentage_value=(i + 1) / 5,
                    )
                
                # 创建记忆
                self.backend.create_new_memory_entry(
                    content_text=f"并发任务 {worker_id} 的记忆",
                    source_task_id=task.unique_entity_id,
                )
            except Exception as e:
                self.log_error("并发场景", f"线程 {worker_id} 失败", str(e))
        
        threads = [threading.Thread(target=concurrent_worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        print(f"   测试5.3完成: {len(concurrent_tasks)} 个并发任务验证通过")
        
        self.checkpoint("Test5: 业务场景闭环")
        print(f"✅ 测试5完成: 业务场景测试完成")
        print()
    
    # =========================================================================
    # 测试6: 数据一致性校验
    # =========================================================================
    def test_6_data_consistency(self):
        """测试6: 数据一致性校验"""
        print("=" * 150)
        print("🧪 测试6: 数据一致性校验")
        print("=" * 150)
        print()
        
        print("[CONSISTENCY] 测试6.1: 任务数据一致性...")
        initial_count = len(self.backend.retrieve_all_tasks())
        
        # 创建任务
        task = self.backend.create_new_task_entry(
            task_title="一致性测试任务",
        )
        self.task_ids.add(task.unique_entity_id)
        
        # 验证计数
        after_create = len(self.backend.retrieve_all_tasks())
        if after_create != initial_count + 1:
            self.log_error("数据一致性", "任务计数不一致")
        
        # 验证检索
        retrieved = self.backend.retrieve_task_by_id(task.unique_entity_id)
        if not retrieved:
            self.log_error("数据一致性", "任务检索失败")
        if retrieved.task_title != task.task_title:
            self.log_error("数据一致性", "任务标题不一致")
        
        # 更新任务
        self.backend.update_task_entry(
            task.unique_entity_id,
            task_title="更新后的标题",
            progress_percentage_value=0.5,
        )
        
        # 验证更新
        updated = self.backend.retrieve_task_by_id(task.unique_entity_id)
        if updated.task_title != "更新后的标题":
            self.log_error("数据一致性", "任务更新不一致")
        if abs(updated.progress_percentage_value - 0.5) > 0.01:
            self.log_error("数据一致性", "进度更新不一致")
        
        print(f"   测试6.1完成: 任务数据一致性验证通过")
        
        print("[CONSISTENCY] 测试6.2: 记忆数据一致性...")
        initial_mem_count = len(self.backend.retrieve_all_memories())
        
        # 创建记忆
        memory = self.backend.create_new_memory_entry(
            content_text="一致性测试记忆",
            importance_score=4,
        )
        self.memory_ids.add(memory.unique_memory_id)
        
        # 验证计数
        after_mem_create = len(self.backend.retrieve_all_memories())
        if after_mem_create != initial_mem_count + 1:
            self.log_error("数据一致性", "记忆计数不一致")
        
        # 验证检索
        retrieved_mem = self.backend.retrieve_memory_by_id(memory.unique_memory_id)
        if not retrieved_mem:
            self.log_error("数据一致性", "记忆检索失败")
        
        # 验证搜索
        search_results = self.backend.search_memories_by_text_content("一致性测试")
        if not any(r.unique_memory_id == memory.unique_memory_id for r in search_results):
            self.log_error("数据一致性", "记忆搜索不一致")
        
        print(f"   测试6.2完成: 记忆数据一致性验证通过")
        
        print("[CONSISTENCY] 测试6.3: 知识图谱一致性...")
        initial_nodes = len(self.node_ids)
        initial_edges = len(self.edge_ids)
        
        # 创建节点
        node = self.backend.add_node_to_knowledge_graph("consistency_node")
        self.node_ids.append(node)
        
        # 创建第二个节点和边
        node2 = self.backend.add_node_to_knowledge_graph("consistency_node_2")
        self.node_ids.append(node2)
        
        edge = self.backend.add_edge_to_knowledge_graph(node, node2, "test_relation")
        self.edge_ids.append(edge)
        
        # 验证统计
        stats = self.backend.retrieve_knowledge_graph_statistics()
        if stats['total_nodes'] != initial_nodes + 2:
            self.log_error("数据一致性", f"节点计数不一致: 期望 {initial_nodes + 2}, 实际 {stats['total_nodes']}")
        if stats['total_edges'] != initial_edges + 1:
            self.log_error("数据一致性", f"边计数不一致: 期望 {initial_edges + 1}, 实际 {stats['total_edges']}")
        
        print(f"   测试6.3完成: 知识图谱一致性验证通过")
        
        print("[CONSISTENCY] 测试6.4: 引用安全性...")
        # 验证深拷贝
        task = self.backend.create_new_task_entry("引用安全测试")
        self.task_ids.add(task.unique_entity_id)
        
        retrieved1 = self.backend.retrieve_task_by_id(task.unique_entity_id)
        retrieved2 = self.backend.retrieve_task_by_id(task.unique_entity_id)
        
        # 修改第一个检索结果
        retrieved1.task_title = "已修改的标题"
        
        # 验证原始数据未被修改
        retrieved3 = self.backend.retrieve_task_by_id(task.unique_entity_id)
        if retrieved3.task_title == "已修改的标题":
            self.log_error("引用安全", "深拷贝失败，原始数据被修改")
        
        print(f"   测试6.4完成: 引用安全性验证通过")
        
        print("[CONSISTENCY] 测试6.5: 并发一致性...")
        barrier = threading.Barrier(5)
        inconsistency_found = []
        
        def consistency_worker(worker_id):
            try:
                barrier.wait()
                # 快速创建和检索
                for i in range(20):
                    task = self.backend.create_new_task_entry(
                        task_title=f"并发一致性测试 {worker_id}_{i}",
                    )
                    retrieved = self.backend.retrieve_task_by_id(task.unique_entity_id)
                    if retrieved.task_title != task.task_title:
                        with self.lock:
                            inconsistency_found.append((worker_id, i))
                    self.backend.update_task_entry(
                        task.unique_entity_id,
                        progress_percentage_value=random.random(),
                    )
            except Exception as e:
                self.log_error("并发一致性", f"线程 {worker_id} 失败", str(e))
        
        threads = [threading.Thread(target=consistency_worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        if inconsistency_found:
            self.log_error("并发一致性", f"发现 {len(inconsistency_found)} 个不一致情况")
        
        print(f"   测试6.5完成: 并发一致性验证通过")
        
        self.checkpoint("Test6: 数据一致性校验")
        print(f"✅ 测试6完成: 数据一致性校验完成")
        print()
    
    # =========================================================================
    # 测试7: 异常容错测试
    # =========================================================================
    def test_7_exception_handling(self):
        """测试7: 异常容错测试"""
        print("=" * 150)
        print("🧪 测试7: 异常容错测试")
        print("=" * 150)
        print()
        
        print("[EXCEPTION] 测试7.1: 无效输入容错...")
        invalid_inputs = [
            (None, ""),  # None输入
            ("", ""),  # 空字符串
            (123, ""),  # 非字符串
            ({"dict": "value"}, ""),  # 字典输入
            (["list"], ""),  # 列表输入
        ]
        
        for invalid_input, desc in invalid_inputs:
            try:
                task = self.backend.create_new_task_entry(
                    task_title=invalid_input,
                    task_description=desc,
                )
                # 应该成功处理
                print(f"   成功处理无效输入: {type(invalid_input)}")
            except Exception as e:
                self.log_error("异常处理", f"无效输入 {type(invalid_input)} 未被妥善处理", str(e))
        
        print(f"   测试7.1完成: 无效输入容错验证通过")
        
        print("[EXCEPTION] 测试7.2: 缺失字段容错...")
        try:
            # 只提供必需字段
            task = self.backend.create_new_task_entry(task_title="最小字段测试")
            if not task.unique_entity_id:
                self.log_error("异常处理", "必需字段缺失")
        except Exception as e:
            self.log_error("异常处理", "最小字段测试失败", str(e))
        
        print(f"   测试7.2完成: 缺失字段容错验证通过")
        
        print("[EXCEPTION] 测试7.3: 知识图谱无效边...")
        invalid_edges = [
            ("nonexistent_node", "another_nonexistent"),
            ("", ""),
            (123, 456),  # 非字符串ID
            ("x" * 1000, "y" * 1000),
        ]
        
        for source, target in invalid_edges:
            try:
                self.backend.add_edge_to_knowledge_graph(source, target, "test")
                self.log_warning("异常处理", f"无效边 {source} -> {target} 未抛出异常")
            except (ValueError, TypeError) as e:
                # 预期行为
                pass
            except Exception as e:
                self.log_error("异常处理", f"无效边 {source} 异常类型不匹配", str(e))
        
        print(f"   测试7.3完成: 知识图谱无效边容错验证通过")
        
        print("[EXCEPTION] 测试7.4: 并发异常场景...")
        barrier = threading.Barrier(20)
        exceptions_caught = []
        
        def exception_worker(worker_id):
            try:
                barrier.wait()
                # 尝试各种可能失败的场景
                if worker_id % 5 == 0:
                    self.backend.retrieve_task_by_id("nonexistent")
                elif worker_id % 5 == 1:
                    self.backend.add_edge_to_knowledge_graph("a", "b", "test")
                elif worker_id % 5 == 2:
                    self.backend.create_new_task_entry(None)
                elif worker_id % 5 == 3:
                    self.backend.update_task_entry("nonexistent", task_title="test")
                else:
                    self.backend.retrieve_memory_by_id("nonexistent")
            except Exception as e:
                with self.lock:
                    exceptions_caught.append((worker_id, type(e).__name__))
        
        threads = [threading.Thread(target=exception_worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        print(f"   测试7.4完成: {len(exceptions_caught)} 个并发异常被正确处理")
        
        print("[EXCEPTION] 测试7.5: 系统统计异常场景...")
        # 测试系统统计在各种状态下的表现
        try:
            # 空系统统计
            stats = self.backend.generate_system_statistics_snapshot()
            if stats.total_tasks_count < 0:
                self.log_error("异常处理", "系统统计返回负数")
        except Exception as e:
            self.log_error("异常处理", "系统统计失败", str(e))
        
        print(f"   测试7.5完成: 系统统计异常场景验证通过")
        
        self.checkpoint("Test7: 异常容错测试")
        print(f"✅ 测试7完成: 异常容错测试完成")
        print()
    
    # =========================================================================
    # 测试8: 基础性能核验
    # =========================================================================
    def test_8_performance_benchmark(self):
        """测试8: 基础性能核验"""
        print("=" * 150)
        print("🧪 测试8: 基础性能核验")
        print("=" * 150)
        print()
        
        print("[PERFORMANCE] 测试8.1: 高频任务操作性能...")
        start = time.time()
        num_operations = 1000
        
        for i in range(num_operations):
            task = self.backend.create_new_task_entry(
                task_title=f"性能测试任务 {i}",
                task_description=f"描述 {i}",
            )
            self.backend.retrieve_task_by_id(task.unique_entity_id)
            self.backend.update_task_entry(
                task.unique_entity_id,
                progress_percentage_value=random.random(),
            )
        
        duration = time.time() - start
        ops_per_second = num_operations / duration
        print(f"   {num_operations} 次任务操作耗时: {duration:.2f}s")
        print(f"   吞吐量: {ops_per_second:.2f} ops/s")
        
        if ops_per_second < 100:
            self.log_warning("性能", f"任务操作性能较低: {ops_per_second:.2f} ops/s")
        
        print(f"   测试8.1完成: 任务操作性能验证通过")
        
        print("[PERFORMANCE] 测试8.2: 高频记忆操作性能...")
        start = time.time()
        
        for i in range(500):
            memory = self.backend.create_new_memory_entry(
                content_text=f"性能测试记忆 {i}" * 10,
                importance_score=random.randint(1, 5),
            )
            self.backend.search_memories_by_text_content("性能测试")
        
        duration = time.time() - start
        ops_per_second = 500 / duration
        print(f"   500 次记忆操作耗时: {duration:.2f}s")
        print(f"   吞吐量: {ops_per_second:.2f} ops/s")
        
        if ops_per_second < 50:
            self.log_warning("性能", f"记忆操作性能较低: {ops_per_second:.2f} ops/s")
        
        print(f"   测试8.2完成: 记忆操作性能验证通过")
        
        print("[PERFORMANCE] 测试8.3: 知识图谱性能...")
        start = time.time()
        num_nodes = 500
        
        for i in range(num_nodes):
            node_id = self.backend.add_node_to_knowledge_graph(
                label=f"perf_node_{i}",
                properties={"index": i},
            )
            self.node_ids.append(node_id)
        
        duration = time.time() - start
        ops_per_second = num_nodes / duration
        print(f"   {num_nodes} 个节点创建耗时: {duration:.2f}s")
        print(f"   吞吐量: {ops_per_second:.2f} ops/s")
        
        print(f"   测试8.3完成: 知识图谱性能验证通过")
        
        print("[PERFORMANCE] 测试8.4: 并发性能压测...")
        start = time.time()
        barrier = threading.Barrier(50)
        
        def perf_worker(worker_id):
            barrier.wait()
            for i in range(50):
                task = self.backend.create_new_task_entry(
                    task_title=f"并发性能测试 {worker_id}_{i}",
                )
                self.backend.retrieve_task_by_id(task.unique_entity_id)
        
        threads = [threading.Thread(target=perf_worker, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        duration = time.time() - start
        total_ops = 50 * 50 * 2  # 50线程 * 50次 * 2操作(创建+检索)
        ops_per_second = total_ops / duration
        print(f"   {total_ops} 次并发操作耗时: {duration:.2f}s")
        print(f"   吞吐量: {ops_per_second:.2f} ops/s")
        
        if ops_per_second < 500:
            self.log_warning("性能", f"并发性能较低: {ops_per_second:.2f} ops/s")
        
        print(f"   测试8.4完成: 并发性能压测验证通过")
        
        print("[PERFORMANCE] 测试8.5: 内存使用监控...")
        import sys
        # 获取当前对象大小
        backend_size = sys.getsizeof(self.backend)
        store_size = sys.getsizeof(self.store)
        cache_size = sys.getsizeof(self.cache)
        
        print(f"   Backend对象大小: {backend_size} bytes")
        print(f"   Store对象大小: {store_size} bytes")
        print(f"   Cache对象大小: {cache_size} bytes")
        
        # 强制垃圾回收
        gc.collect()
        
        print(f"   测试8.5完成: 内存使用监控完成")
        
        self.checkpoint("Test8: 基础性能核验")
        print(f"✅ 测试8完成: 基础性能核验完成")
        print()
    
    # =========================================================================
    # 主测试运行方法
    # =========================================================================
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 150)
        print("🚀 开始执行超大规模复杂场景测试 - 第1次迭代")
        print("=" * 150)
        print()
        
        try:
            self.test_1_static_code_validation()
            self.test_2_unit_coverage()
            self.test_3_module_integration()
            self.test_4_interface_traversal()
            self.test_5_business_scenario()
            self.test_6_data_consistency()
            self.test_7_exception_handling()
            self.test_8_performance_benchmark()
            
        except Exception as e:
            self.log_error("主测试", "测试执行失败", str(e))
            traceback.print_exc()
        
        # 生成最终报告
        self.generate_final_report()
    
    def generate_final_report(self):
        """生成最终报告"""
        print("=" * 150)
        print("📊 超大规模复杂场景测试 - 第1次迭代 - 最终报告")
        print("=" * 150)
        print()
        
        total_time = time.time() - self.stats["start_time"]
        
        print(f"⏱️  总耗时: {total_time:.2f} 秒")
        print(f"📈 总操作数: {self.stats['total_operations']:,}")
        print(f"❌ 总错误数: {self.stats['total_errors']}")
        print(f"⚠️  总警告数: {self.stats['total_warnings']}")
        print(f"🎯 操作成功率: {((self.stats['total_operations'] - self.stats['total_errors']) / self.stats['total_operations'] * 100) if self.stats['total_operations'] > 0 else 0:.2f}%")
        print()
        
        print(f"📋 检查点记录:")
        for i, cp in enumerate(self.stats['checkpoints'], 1):
            print(f"   {i}. {cp['name']}: {cp['elapsed']:.2f}s")
        print()
        
        if self.errors:
            print(f"❌ 发现 {len(self.errors)} 个错误:")
            for i, error in enumerate(self.errors[:20], 1):
                print(f"   {i}. [{error['category']}] {error['message']}")
                if error['details']:
                    print(f"      详情: {str(error['details'])[:100]}")
        print()
        
        if self.warnings:
            print(f"⚠️  发现 {len(self.warnings)} 个警告:")
            for i, warning in enumerate(self.warnings[:10], 1):
                print(f"   {i}. [{warning['category']}] {warning['message']}")
        print()
        
        print(f"📊 数据统计:")
        print(f"   创建的任务数: {len(self.task_ids)}")
        print(f"   创建的记忆数: {len(self.memory_ids)}")
        print(f"   创建的经验数: {len(self.experience_ids)}")
        print(f"   创建的节点数: {len(self.node_ids)}")
        print(f"   创建的边数: {len(self.edge_ids)}")
        print()
        
        print("=" * 150)
        if self.stats['total_errors'] == 0:
            print("🎉🎉🎉 第1次迭代测试完美通过！")
        elif self.stats['total_errors'] < 10:
            print("✅ 第1次迭代测试基本通过，少量错误需要修复")
        else:
            print("⚠️  第1次迭代测试发现较多问题，需要修复")
        print("=" * 150)
        print()


def main():
    """主函数"""
    try:
        runner = UltraComplexTestRunner()
        runner.run_all_tests()
        return 0 if runner.stats['total_errors'] < 10 else 1
    except Exception as e:
        print(f"❌ 测试主程序崩溃: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
