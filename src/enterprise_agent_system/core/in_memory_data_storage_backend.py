"""
Core Layer - In-Memory Data Storage Backend
核心层 - 内存数据存储后端

职责：
- 提供统一的数据存储接口
- 管理任务、记忆、经验等数据
- 提供知识图谱支持
- 实现 CRUD 操作
- 线程安全
"""

import time
import threading
from typing import Dict, List, Optional, Any
from collections import defaultdict

from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionDataModel,
    MemoryStorageDataModel,
    ExperienceLearningDataModel,
    SystemStatisticsSnapshotModel,
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
    AgentOperatingModeEnumeration,
    validate_and_convert_enum,
)
from enterprise_agent_system.core.storage_backend_interface import (
    StorageBackendInterface,
)


class InMemoryDataStorageBackend(StorageBackendInterface):
    """
    内存数据存储后端类

    Features:
    - 快速内存操作
    - 无外部依赖
    - 生产级接口
    - 知识图谱支持
    - 实现统一存储接口
    - 线程安全
    """

    def __init__(self):
        """初始化存储后端"""
        self._lock = threading.RLock()  # 可重入锁，支持嵌套调用
        self._task_storage: Dict[str, TaskExecutionDataModel] = {}
        self._memory_storage: Dict[str, MemoryStorageDataModel] = {}
        self._experience_storage: Dict[str, ExperienceLearningDataModel] = {}
        self._knowledge_graph_nodes: Dict[str, Dict] = {}
        self._knowledge_graph_edges: List[Dict] = []
        self._system_start_timestamp: float = time.time()

        self._node_counter: int = 0
        self._edge_counter: int = 0

        self._outgoing_edges: Dict[str, List[Dict]] = defaultdict(list)
        self._incoming_edges: Dict[str, List[Dict]] = defaultdict(list)

    # =============================================================
    # 任务管理操作
    # =============================================================

    def create_new_task_entry(
        self,
        task_title: str,
        task_description: str = "",
        priority_level: TaskPriorityLevelEnumeration = TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
    ) -> TaskExecutionDataModel:
        """
        创建新的任务条目

        Args:
            task_title: 任务标题
            task_description: 任务描述
            priority_level: 优先级等级

        Returns:
            新创建的任务数据模型
        """
        with self._lock:
            # 确保标题是字符串
            safe_title = str(task_title) if task_title is not None else ""
            safe_description = str(task_description) if task_description is not None else ""
            
            task = TaskExecutionDataModel(
                task_title=safe_title,
                task_description=safe_description,
                priority_level=priority_level,
            )
            self._task_storage[task.unique_entity_id] = task
            return task

    def retrieve_task_by_id(self, task_id: str) -> Optional[TaskExecutionDataModel]:
        """
        根据 ID 检索任务

        Args:
            task_id: 任务唯一标识符

        Returns:
            任务数据模型或 None
        """
        with self._lock:
            return self._task_storage.get(task_id)

    def retrieve_pending_tasks_sorted_by_priority(
        self,
    ) -> List[TaskExecutionDataModel]:
        """
        检索待处理任务并按优先级排序

        Returns:
            按优先级降序、创建时间升序排序的任务列表
        """
        with self._lock:
            pending = [
                task
                for task in self._task_storage.values()
                if task.execution_status == TaskExecutionStatusEnumeration.PENDING_STATUS
            ]
            pending.sort(
                key=lambda t: (-t.priority_level.value, t.created_timestamp)
            )
            return pending

    def update_task_entry(
        self, task_id: str, **updates: Any
    ) -> Optional[TaskExecutionDataModel]:
        """
        更新任务条目

        Args:
            task_id: 任务唯一标识符
            **updates: 要更新的属性

        Returns:
            更新后的任务或 None
        """
        with self._lock:
            task = self._task_storage.get(task_id)
            if task:
                for key, value in updates.items():
                    if hasattr(task, key):
                        # 安全处理各种类型的更新
                        if key == 'priority_level':
                            value = validate_and_convert_enum(
                                value,
                                TaskPriorityLevelEnumeration,
                                task.priority_level
                            )
                        elif key == 'execution_status':
                            value = validate_and_convert_enum(
                                value,
                                TaskExecutionStatusEnumeration,
                                task.execution_status
                            )
                        elif key == 'progress_percentage_value':
                            # 确保进度在 0-1 范围内
                            try:
                                value = float(value)
                                value = max(0.0, min(1.0, value))
                            except (ValueError, TypeError):
                                # 无效值，保持原样
                                continue
                        
                        setattr(task, key, value)
            return task

    def retrieve_all_tasks(self) -> List[TaskExecutionDataModel]:
        """
        检索所有任务

        Returns:
            所有任务列表
        """
        with self._lock:
            return list(self._task_storage.values())

    # =============================================================
    # 记忆管理操作
    # =============================================================

    def create_new_memory_entry(
        self,
        content_text: str,
        category_type: MemoryCategoryTypeEnumeration = MemoryCategoryTypeEnumeration.GENERAL_MEMORY_CATEGORY,
        tags_list: Optional[List[str]] = None,
        importance_score: int = 3,
        source_task_id: Optional[str] = None,
    ) -> MemoryStorageDataModel:
        """
        创建新的记忆条目

        Args:
            content_text: 记忆内容文本
            category_type: 记忆类别类型
            tags_list: 标签列表
            importance_score: 重要性评分
            source_task_id: 来源任务标识符

        Returns:
            新创建的记忆数据模型
        """
        with self._lock:
            # 安全处理输入
            safe_content = str(content_text) if content_text is not None else ""
            safe_tags = []
            if tags_list:
                safe_tags = [str(tag) for tag in tags_list if tag is not None]
            
            # 安全处理重要性分数
            try:
                safe_importance = int(importance_score)
                safe_importance = max(1, min(5, safe_importance))
            except (ValueError, TypeError):
                safe_importance = 3
            
            memory = MemoryStorageDataModel(
                content_text_body=safe_content,
                category_type=category_type,
                tags_list=safe_tags,
                importance_score=safe_importance,
                source_task_id=source_task_id,
            )
            self._memory_storage[memory.unique_memory_id] = memory
            return memory

    def retrieve_memory_by_id(
        self, memory_id: str
    ) -> Optional[MemoryStorageDataModel]:
        """
        根据 ID 检索记忆

        Args:
            memory_id: 记忆唯一标识符

        Returns:
            记忆数据模型或 None
        """
        with self._lock:
            memory = self._memory_storage.get(memory_id)
            if memory:
                memory.access_count_number += 1
                memory.last_accessed_timestamp = time.time()
            return memory

    def search_memories_by_text_content(
        self,
        search_query: str,
        category_filter: Optional[MemoryCategoryTypeEnumeration] = None,
        min_importance: int = 1,
    ) -> List[MemoryStorageDataModel]:
        """
        根据文本内容搜索记忆

        Args:
            search_query: 搜索查询
            category_filter: 类别过滤器
            min_importance: 最低重要性

        Returns:
            匹配的记忆列表
        """
        with self._lock:
            search_query_lower = search_query.lower()
            results: List[MemoryStorageDataModel] = []

            for memory in self._memory_storage.values():
                if memory.importance_score < min_importance:
                    continue
                if category_filter and memory.category_type != category_filter:
                    continue

                relevance_score = 0
                if search_query_lower in memory.content_text_body.lower():
                    relevance_score += 10

                for tag in memory.tags_list:
                    if search_query_lower in tag.lower():
                        relevance_score += 5

                if relevance_score > 0:
                    results.append(memory)

            results.sort(
                key=lambda m: (-m.importance_score, -m.access_count_number)
            )
            return results

    def retrieve_all_memories(self) -> List[MemoryStorageDataModel]:
        """
        检索所有记忆

        Returns:
            所有记忆列表
        """
        with self._lock:
            return list(self._memory_storage.values())

    # =============================================================
    # 经验管理操作
    # =============================================================

    def create_new_experience_entry(
        self,
        task_reference_id: str,
        task_type_label: str,
        was_successful: bool,
        duration_seconds: float,
        lessons_learned: Optional[List[str]] = None,
    ) -> ExperienceLearningDataModel:
        """
        创建新的经验条目

        Args:
            task_reference_id: 任务引用标识符
            task_type_label: 任务类型标签
            was_successful: 是否成功
            duration_seconds: 执行时长秒数
            lessons_learned: 学到的经验列表

        Returns:
            新创建的经验数据模型
        """
        with self._lock:
            experience = ExperienceLearningDataModel(
                task_reference_id=task_reference_id,
                task_type_label=task_type_label,
                was_successful_flag=was_successful,
                duration_seconds_value=duration_seconds,
                lessons_learned_list=lessons_learned or [],
            )
            self._experience_storage[experience.unique_experience_id] = experience
            return experience

    def retrieve_all_experiences(self) -> List[ExperienceLearningDataModel]:
        """
        检索所有经验

        Returns:
            所有经验列表
        """
        with self._lock:
            return list(self._experience_storage.values())

    # =============================================================
    # 知识图谱操作
    # =============================================================

    def add_node_to_knowledge_graph(
        self,
        label: str,
        properties: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None,
    ) -> str:
        """
        添加节点到知识图谱

        Args:
            label: 节点标签
            properties: 节点属性
            memory_id: 关联记忆标识符

        Returns:
            新创建的节点 ID
        """
        with self._lock:
            self._node_counter += 1
            node_id = f"kg_node_{self._node_counter:06d}"

            node = {
                "id": node_id,
                "label": label.lower(),
                "properties": properties or {},
                "memory_id": memory_id,
            }

            self._knowledge_graph_nodes[node_id] = node
            self._outgoing_edges[node_id] = []
            self._incoming_edges[node_id] = []

            return node_id

    def add_edge_to_knowledge_graph(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        weight: float = 1.0,
    ) -> str:
        """
        添加边到知识图谱

        Args:
            source_node_id: 源节点 ID
            target_node_id: 目标节点 ID
            relationship_type: 关系类型
            weight: 关系权重

        Returns:
            新创建的边 ID
        """
        with self._lock:
            if source_node_id not in self._knowledge_graph_nodes:
                raise ValueError(f"源节点不存在: {source_node_id}")
            if target_node_id not in self._knowledge_graph_nodes:
                raise ValueError(f"目标节点不存在: {target_node_id}")

            self._edge_counter += 1
            edge_id = f"kg_edge_{self._edge_counter:06d}"

            edge = {
                "id": edge_id,
                "source_node_id": source_node_id,
                "target_node_id": target_node_id,
                "relationship_type": relationship_type,
                "weight": weight,
            }

            self._knowledge_graph_edges.append(edge)
            self._outgoing_edges[source_node_id].append(edge)
            self._incoming_edges[target_node_id].append(edge)

            return edge_id

    def retrieve_knowledge_graph_statistics(self) -> Dict[str, int]:
        """
        检索知识图谱统计信息

        Returns:
            知识图谱统计字典
        """
        with self._lock:
            return {
                "total_nodes": len(self._knowledge_graph_nodes),
                "total_edges": len(self._knowledge_graph_edges),
            }

    # =============================================================
    # 系统统计
    # =============================================================

    def generate_system_statistics_snapshot(
        self,
        current_mode: AgentOperatingModeEnumeration = AgentOperatingModeEnumeration.PAUSED_MODE,
    ) -> SystemStatisticsSnapshotModel:
        """
        生成系统统计快照

        Args:
            current_mode: 当前运行模式

        Returns:
            系统统计快照模型
        """
        with self._lock:
            total_tasks = len(self._task_storage)
            completed = sum(
                1
                for t in self._task_storage.values()
                if t.execution_status == TaskExecutionStatusEnumeration.COMPLETED_STATUS
            )
            pending = sum(
                1
                for t in self._task_storage.values()
                if t.execution_status == TaskExecutionStatusEnumeration.PENDING_STATUS
            )
            failed = sum(
                1
                for t in self._task_storage.values()
                if t.execution_status == TaskExecutionStatusEnumeration.FAILED_STATUS
            )

            success_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0.0

            kg_stats = self.retrieve_knowledge_graph_statistics()

            return SystemStatisticsSnapshotModel(
                total_tasks_count=total_tasks,
                completed_tasks_count=completed,
                pending_tasks_count=pending,
                failed_tasks_count=failed,
                success_rate_percentage=success_rate,
                total_memories_count=len(self._memory_storage),
                total_experiences_count=len(self._experience_storage),
                knowledge_graph_nodes_count=kg_stats["total_nodes"],
                knowledge_graph_edges_count=kg_stats["total_edges"],
                uptime_seconds_value=time.time() - self._system_start_timestamp,
                current_operating_mode=current_mode,
            )


# 全局存储实例
_global_storage_instance: Optional[InMemoryDataStorageBackend] = None
_storage_lock = threading.RLock()


def get_storage_backend_instance() -> InMemoryDataStorageBackend:
    """
    获取存储后端实例 - 单例模式

    Returns:
        存储后端实例
    """
    global _global_storage_instance
    with _storage_lock:
        if _global_storage_instance is None:
            _global_storage_instance = InMemoryDataStorageBackend()
        return _global_storage_instance


def reset_storage_backend_instance() -> None:
    """重置存储后端实例"""
    global _global_storage_instance
    with _storage_lock:
        _global_storage_instance = None
