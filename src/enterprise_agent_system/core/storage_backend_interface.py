"""
Core Layer - Storage Interface Abstraction
核心层 - 存储接口抽象层

职责：
- 定义统一的存储后端接口
- 支持多种存储后端（内存、SQLAlchemy、Redis缓存等）
- 提供可插拔的存储策略
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionDataModel,
    MemoryStorageDataModel,
    ExperienceLearningDataModel,
    SystemStatisticsSnapshotModel,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
    AgentOperatingModeEnumeration,
)


@dataclass
class StorageBackendConfig:
    """存储后端配置"""
    backend_type: str = "in_memory"
    database_url: Optional[str] = None
    cache_enabled: bool = False
    redis_url: Optional[str] = None


class StorageBackendInterface(ABC):
    """存储后端抽象基类"""

    @abstractmethod
    def create_new_task_entry(
        self,
        task_title: str,
        task_description: str = "",
        priority_level: TaskPriorityLevelEnumeration = TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
    ) -> TaskExecutionDataModel:
        """创建新的任务条目"""
        pass

    @abstractmethod
    def retrieve_task_by_id(self, task_id: str) -> Optional[TaskExecutionDataModel]:
        """根据ID检索任务"""
        pass

    @abstractmethod
    def retrieve_pending_tasks_sorted_by_priority(
        self,
    ) -> List[TaskExecutionDataModel]:
        """检索待处理任务并按优先级排序"""
        pass

    @abstractmethod
    def update_task_entry(
        self, task_id: str, **updates: Any
    ) -> Optional[TaskExecutionDataModel]:
        """更新任务条目"""
        pass

    @abstractmethod
    def retrieve_all_tasks(self) -> List[TaskExecutionDataModel]:
        """检索所有任务"""
        pass

    @abstractmethod
    def create_new_memory_entry(
        self,
        content_text: str,
        category_type: MemoryCategoryTypeEnumeration = MemoryCategoryTypeEnumeration.GENERAL_MEMORY_CATEGORY,
        tags_list: Optional[List[str]] = None,
        importance_score: int = 3,
        source_task_id: Optional[str] = None,
    ) -> MemoryStorageDataModel:
        """创建新的记忆条目"""
        pass

    @abstractmethod
    def retrieve_memory_by_id(
        self, memory_id: str
    ) -> Optional[MemoryStorageDataModel]:
        """根据ID检索记忆"""
        pass

    @abstractmethod
    def search_memories_by_text_content(
        self,
        search_query: str,
        category_filter: Optional[MemoryCategoryTypeEnumeration] = None,
        min_importance: int = 1,
    ) -> List[MemoryStorageDataModel]:
        """根据文本内容搜索记忆"""
        pass

    @abstractmethod
    def retrieve_all_memories(self) -> List[MemoryStorageDataModel]:
        """检索所有记忆"""
        pass

    @abstractmethod
    def create_new_experience_entry(
        self,
        task_reference_id: str,
        task_type_label: str,
        was_successful: bool,
        duration_seconds: float,
        lessons_learned: Optional[List[str]] = None,
    ) -> ExperienceLearningDataModel:
        """创建新的经验条目"""
        pass

    @abstractmethod
    def retrieve_all_experiences(self) -> List[ExperienceLearningDataModel]:
        """检索所有经验"""
        pass

    @abstractmethod
    def add_node_to_knowledge_graph(
        self,
        label: str,
        properties: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None,
    ) -> str:
        """添加节点到知识图谱"""
        pass

    @abstractmethod
    def add_edge_to_knowledge_graph(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        weight: float = 1.0,
    ) -> str:
        """添加边到知识图谱"""
        pass

    @abstractmethod
    def retrieve_knowledge_graph_statistics(self) -> Dict[str, int]:
        """检索知识图谱统计信息"""
        pass

    @abstractmethod
    def generate_system_statistics_snapshot(
        self,
        current_mode: AgentOperatingModeEnumeration = AgentOperatingModeEnumeration.PAUSED_MODE,
    ) -> SystemStatisticsSnapshotModel:
        """生成系统统计快照"""
        pass


class AsyncStorageBackendInterface(ABC):
    """异步存储后端抽象基类"""

    @abstractmethod
    async def create_new_task_entry(
        self,
        task_title: str,
        task_description: str = "",
        priority_level: TaskPriorityLevelEnumeration = TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
    ) -> TaskExecutionDataModel:
        """创建新的任务条目（异步）"""
        pass

    @abstractmethod
    async def retrieve_task_by_id(self, task_id: str) -> Optional[TaskExecutionDataModel]:
        """根据ID检索任务（异步）"""
        pass

    @abstractmethod
    async def retrieve_pending_tasks_sorted_by_priority(
        self,
    ) -> List[TaskExecutionDataModel]:
        """检索待处理任务并按优先级排序（异步）"""
        pass

    @abstractmethod
    async def update_task_entry(
        self, task_id: str, **updates: Any
    ) -> Optional[TaskExecutionDataModel]:
        """更新任务条目（异步）"""
        pass

    @abstractmethod
    async def retrieve_all_tasks(self) -> List[TaskExecutionDataModel]:
        """检索所有任务（异步）"""
        pass

    @abstractmethod
    async def create_new_memory_entry(
        self,
        content_text: str,
        category_type: MemoryCategoryTypeEnumeration = MemoryCategoryTypeEnumeration.GENERAL_MEMORY_CATEGORY,
        tags_list: Optional[List[str]] = None,
        importance_score: int = 3,
        source_task_id: Optional[str] = None,
    ) -> MemoryStorageDataModel:
        """创建新的记忆条目（异步）"""
        pass

    @abstractmethod
    async def retrieve_memory_by_id(
        self, memory_id: str
    ) -> Optional[MemoryStorageDataModel]:
        """根据ID检索记忆（异步）"""
        pass

    @abstractmethod
    async def search_memories_by_text_content(
        self,
        search_query: str,
        category_filter: Optional[MemoryCategoryTypeEnumeration] = None,
        min_importance: int = 1,
    ) -> List[MemoryStorageDataModel]:
        """根据文本内容搜索记忆（异步）"""
        pass

    @abstractmethod
    async def retrieve_all_memories(self) -> List[MemoryStorageDataModel]:
        """检索所有记忆（异步）"""
        pass

    @abstractmethod
    async def create_new_experience_entry(
        self,
        task_reference_id: str,
        task_type_label: str,
        was_successful: bool,
        duration_seconds: float,
        lessons_learned: Optional[List[str]] = None,
    ) -> ExperienceLearningDataModel:
        """创建新的经验条目（异步）"""
        pass

    @abstractmethod
    async def retrieve_all_experiences(self) -> List[ExperienceLearningDataModel]:
        """检索所有经验（异步）"""
        pass

    @abstractmethod
    async def add_node_to_knowledge_graph(
        self,
        label: str,
        properties: Optional[Dict[str, Any]] = None,
        memory_id: Optional[str] = None,
    ) -> str:
        """添加节点到知识图谱（异步）"""
        pass

    @abstractmethod
    async def add_edge_to_knowledge_graph(
        self,
        source_node_id: str,
        target_node_id: str,
        relationship_type: str,
        weight: float = 1.0,
    ) -> str:
        """添加边到知识图谱（异步）"""
        pass

    @abstractmethod
    async def retrieve_knowledge_graph_statistics(self) -> Dict[str, int]:
        """检索知识图谱统计信息（异步）"""
        pass

    @abstractmethod
    async def generate_system_statistics_snapshot(
        self,
        current_mode: AgentOperatingModeEnumeration = AgentOperatingModeEnumeration.PAUSED_MODE,
    ) -> SystemStatisticsSnapshotModel:
        """生成系统统计快照（异步）"""
        pass
