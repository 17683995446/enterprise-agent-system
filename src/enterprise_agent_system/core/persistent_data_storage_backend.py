"""
Core Layer - Persistent Data Storage Backend with SQLAlchemy
核心层 - 基于 SQLAlchemy 的持久化数据存储后端

职责：
- 提供统一的数据存储接口（支持内存和持久化）
- 管理任务、记忆、经验等数据
- 提供知识图谱支持
- 实现 CRUD 操作
- 异步数据库操作支持
"""

import json
import time
from typing import Dict, List, Optional, Any, TypeVar, Generic
from collections import defaultdict

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from enterprise_agent_system.infrastructure.sqlalchemy_database_models import (
    Base,
    TaskEntity,
    MemoryEntity,
    ExperienceEntity,
    KnowledgeNodeEntity,
    KnowledgeEdgeEntity,
    SystemMetricsEntity,
    TaskStatusEnum,
    TaskPriorityEnum,
    MemoryCategoryEnum,
)
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionDataModel,
    MemoryStorageDataModel,
    ExperienceLearningDataModel,
    SystemStatisticsSnapshotModel,
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
    AgentOperatingModeEnumeration,
)
from enterprise_agent_system.infrastructure.database_session_manager import (
    DatabaseSessionManager,
)
from enterprise_agent_system.core.storage_backend_interface import (
    StorageBackendInterface,
)


class PersistentStorageBackend(StorageBackendInterface):
    """
    持久化数据存储后端类

    Features:
    - SQLAlchemy ORM 持久化存储
    - 异步数据库操作
    - 知识图谱支持
    - 生产级接口
    """

    def __init__(self, session: AsyncSession):
        """
        初始化持久化存储后端

        Args:
            session: SQLAlchemy 异步会话
        """
        self._session = session
        self._system_start_timestamp: float = time.time()

    def _convert_task_entity_to_model(self, entity: TaskEntity) -> TaskExecutionDataModel:
        """
        将任务实体转换为领域模型

        Args:
            entity: 任务实体

        Returns:
            任务数据模型
        """
        return TaskExecutionDataModel(
            unique_entity_id=entity.unique_entity_id,
            task_title=entity.task_title,
            task_description=entity.task_description,
            execution_status=TaskExecutionStatusEnumeration(entity.execution_status.value),
            priority_level=TaskPriorityLevelEnumeration(entity.priority_level.value),
            created_timestamp=entity.created_timestamp,
            started_timestamp=entity.started_timestamp,
            completed_timestamp=entity.completed_timestamp,
            execution_result_message=entity.execution_result_message,
            error_message=entity.error_message,
            progress_percentage_value=entity.progress_percentage,
            execution_steps_list=json.loads(entity.execution_steps_json or "[]"),
            metadata_dictionary=json.loads(entity.metadata_json or "{}"),
        )

    def _convert_memory_entity_to_model(self, entity: MemoryEntity) -> MemoryStorageDataModel:
        """
        将记忆实体转换为领域模型

        Args:
            entity: 记忆实体

        Returns:
            记忆数据模型
        """
        return MemoryStorageDataModel(
            unique_memory_id=entity.unique_memory_id,
            content_text_body=entity.content_text_body,
            summary_text=entity.summary_text,
            category_type=MemoryCategoryTypeEnumeration(entity.category_type.value),
            tags_list=json.loads(entity.tags_json or "[]"),
            importance_score=entity.importance_score,
            access_count_number=entity.access_count,
            last_accessed_timestamp=entity.last_accessed_timestamp,
            created_timestamp=entity.created_timestamp,
            updated_timestamp=entity.updated_timestamp,
            source_task_id=entity.source_task_id,
        )

    def _convert_experience_entity_to_model(self, entity: ExperienceEntity) -> ExperienceLearningDataModel:
        """
        将经验实体转换为领域模型

        Args:
            entity: 经验实体

        Returns:
            经验数据模型
        """
        return ExperienceLearningDataModel(
            unique_experience_id=entity.unique_experience_id,
            task_reference_id=entity.task_reference_id,
            task_type_label=entity.task_type_label,
            was_successful_flag=entity.was_successful,
            duration_seconds_value=entity.duration_seconds,
            lessons_learned_list=json.loads(entity.lessons_learned_json or "[]"),
            patterns_recognized_list=json.loads(entity.patterns_json or "[]"),
            suggested_improvements_list=json.loads(entity.improvements_json or "[]"),
            recorded_timestamp=entity.recorded_timestamp,
        )

    # =============================================================
    # 任务管理操作 (异步)
    # =============================================================

    async def create_new_task_entry(
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
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            generate_unique_entity_identifier,
        )

        task = TaskExecutionDataModel(
            task_title=task_title,
            task_description=task_description,
            priority_level=priority_level,
        )

        entity = TaskEntity(
            unique_entity_id=task.unique_entity_id,
            task_title=task.task_title,
            task_description=task.task_description,
            execution_status=TaskStatusEnum(task.execution_status.value),
            priority_level=TaskPriorityEnum(task.priority_level.value),
            created_timestamp=task.created_timestamp,
            execution_steps_json=json.dumps([]),
            metadata_json=json.dumps({}),
        )

        self._session.add(entity)
        await self._session.flush()

        return task

    async def retrieve_task_by_id(self, task_id: str) -> Optional[TaskExecutionDataModel]:
        """
        根据 ID 检索任务

        Args:
            task_id: 任务唯一标识符

        Returns:
            任务数据模型或 None
        """
        stmt = select(TaskEntity).where(TaskEntity.unique_entity_id == task_id)
        result = await self._session.execute(stmt)
        entity = result.scalar_one_or_none()

        if entity:
            return self._convert_task_entity_to_model(entity)
        return None

    async def retrieve_pending_tasks_sorted_by_priority(
        self,
    ) -> List[TaskExecutionDataModel]:
        """
        检索待处理任务并按优先级排序

        Returns:
            按优先级降序、创建时间升序排序的任务列表
        """
        stmt = (
            select(TaskEntity)
            .where(TaskEntity.execution_status == TaskStatusEnum.PENDING)
            .order_by(TaskEntity.priority_level.desc(), TaskEntity.created_timestamp.asc())
        )
        result = await self._session.execute(stmt)
        entities = result.scalars().all()

        return [self._convert_task_entity_to_model(e) for e in entities]

    async def update_task_entry(
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
        stmt = select(TaskEntity).where(TaskEntity.unique_entity_id == task_id)
        result = await self._session.execute(stmt)
        entity = result.scalar_one_or_none()

        if not entity:
            return None

        field_mapping = {
            "task_title": "task_title",
            "task_description": "task_description",
            "execution_status": ("execution_status", lambda v: TaskStatusEnum(v.value) if isinstance(v, TaskExecutionStatusEnumeration) else TaskStatusEnum(v)),
            "priority_level": ("priority_level", lambda v: TaskPriorityEnum(v.value) if isinstance(v, TaskPriorityLevelEnumeration) else TaskPriorityEnum(v)),
            "execution_result_message": "execution_result_message",
            "error_message": "error_message",
            "progress_percentage_value": "progress_percentage",
            "execution_steps_list": ("execution_steps_json", json.dumps),
            "metadata_dictionary": ("metadata_json", json.dumps),
        }

        for key, value in updates.items():
            if key in field_mapping:
                if isinstance(field_mapping[key], tuple):
                    attr, transform = field_mapping[key]
                    setattr(entity, attr, transform(value))
                else:
                    setattr(entity, field_mapping[key], value)

        await self._session.flush()
        return self._convert_task_entity_to_model(entity)

    async def retrieve_all_tasks(self) -> List[TaskExecutionDataModel]:
        """
        检索所有任务

        Returns:
            所有任务列表
        """
        stmt = select(TaskEntity).order_by(TaskEntity.created_timestamp.desc())
        result = await self._session.execute(stmt)
        entities = result.scalars().all()

        return [self._convert_task_entity_to_model(e) for e in entities]

    # =============================================================
    # 记忆管理操作 (异步)
    # =============================================================

    async def create_new_memory_entry(
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
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            generate_unique_entity_identifier,
        )

        memory = MemoryStorageDataModel(
            content_text_body=content_text,
            category_type=category_type,
            tags_list=tags_list or [],
            importance_score=importance_score,
            source_task_id=source_task_id,
        )

        entity = MemoryEntity(
            unique_memory_id=memory.unique_memory_id,
            content_text_body=memory.content_text_body,
            summary_text=memory.summary_text,
            category_type=MemoryCategoryEnum(memory.category_type.value),
            tags_json=json.dumps(memory.tags_list),
            importance_score=memory.importance_score,
            access_count=memory.access_count_number,
            last_accessed_timestamp=memory.last_accessed_timestamp,
            source_task_id=memory.source_task_id,
        )

        self._session.add(entity)
        await self._session.flush()

        return memory

    async def retrieve_memory_by_id(
        self, memory_id: str
    ) -> Optional[MemoryStorageDataModel]:
        """
        根据 ID 检索记忆

        Args:
            memory_id: 记忆唯一标识符

        Returns:
            记忆数据模型或 None
        """
        stmt = select(MemoryEntity).where(MemoryEntity.unique_memory_id == memory_id)
        result = await self._session.execute(stmt)
        entity = result.scalar_one_or_none()

        if entity:
            entity.access_count += 1
            entity.last_accessed_timestamp = time.time()
            await self._session.flush()
            return self._convert_memory_entity_to_model(entity)
        return None

    async def search_memories_by_text_content(
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
        conditions = [
            MemoryEntity.importance_score >= min_importance,
            or_(
                MemoryEntity.content_text_body.ilike(f"%{search_query}%"),
                MemoryEntity.tags_json.ilike(f"%{search_query}%"),
            ),
        ]

        if category_filter:
            conditions.append(
                MemoryEntity.category_type == MemoryCategoryEnum(category_filter.value)
            )

        stmt = select(MemoryEntity).where(and_(*conditions))
        result = await self._session.execute(stmt)
        entities = result.scalars().all()

        return [self._convert_memory_entity_to_model(e) for e in entities]

    async def retrieve_all_memories(self) -> List[MemoryStorageDataModel]:
        """
        检索所有记忆

        Returns:
            所有记忆列表
        """
        stmt = select(MemoryEntity).order_by(MemoryEntity.created_timestamp.desc())
        result = await self._session.execute(stmt)
        entities = result.scalars().all()

        return [self._convert_memory_entity_to_model(e) for e in entities]

    # =============================================================
    # 经验管理操作 (异步)
    # =============================================================

    async def create_new_experience_entry(
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
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            generate_unique_entity_identifier,
        )

        experience = ExperienceLearningDataModel(
            task_reference_id=task_reference_id,
            task_type_label=task_type_label,
            was_successful_flag=was_successful,
            duration_seconds_value=duration_seconds,
            lessons_learned_list=lessons_learned or [],
        )

        entity = ExperienceEntity(
            unique_experience_id=experience.unique_experience_id,
            task_reference_id=experience.task_reference_id,
            task_type_label=experience.task_type_label,
            was_successful=experience.was_successful_flag,
            duration_seconds=experience.duration_seconds_value,
            lessons_learned_json=json.dumps(experience.lessons_learned_list),
            patterns_json=json.dumps(experience.patterns_recognized_list),
            improvements_json=json.dumps(experience.suggested_improvements_list),
        )

        self._session.add(entity)
        await self._session.flush()

        return experience

    async def retrieve_all_experiences(self) -> List[ExperienceLearningDataModel]:
        """
        检索所有经验

        Returns:
            所有经验列表
        """
        stmt = select(ExperienceEntity).order_by(ExperienceEntity.recorded_timestamp.desc())
        result = await self._session.execute(stmt)
        entities = result.scalars().all()

        return [self._convert_experience_entity_to_model(e) for e in entities]

    # =============================================================
    # 知识图谱操作 (异步)
    # =============================================================

    async def add_node_to_knowledge_graph(
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
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            generate_unique_entity_identifier,
        )

        node_id = generate_unique_entity_identifier("kg_node")

        entity = KnowledgeNodeEntity(
            node_id=node_id,
            label=label.lower(),
            properties_json=json.dumps(properties or {}),
            memory_id=memory_id,
        )

        self._session.add(entity)
        await self._session.flush()

        return node_id

    async def add_edge_to_knowledge_graph(
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
        from enterprise_agent_system.domain.core_data_models_and_enumerations import (
            generate_unique_entity_identifier,
        )

        source_stmt = select(KnowledgeNodeEntity).where(
            KnowledgeNodeEntity.node_id == source_node_id
        )
        source_result = await self._session.execute(source_stmt)
        if not source_result.scalar_one_or_none():
            raise ValueError(f"源节点不存在: {source_node_id}")

        target_stmt = select(KnowledgeNodeEntity).where(
            KnowledgeNodeEntity.node_id == target_node_id
        )
        target_result = await self._session.execute(target_stmt)
        if not target_result.scalar_one_or_none():
            raise ValueError(f"目标节点不存在: {target_node_id}")

        edge_id = generate_unique_entity_identifier("kg_edge")

        entity = KnowledgeEdgeEntity(
            edge_id=edge_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relationship_type=relationship_type,
            weight=weight,
        )

        self._session.add(entity)
        await self._session.flush()

        return edge_id

    async def retrieve_knowledge_graph_statistics(self) -> Dict[str, int]:
        """
        检索知识图谱统计信息

        Returns:
            知识图谱统计字典
        """
        nodes_stmt = select(func.count()).select_from(KnowledgeNodeEntity)
        nodes_result = await self._session.execute(nodes_stmt)
        total_nodes = nodes_result.scalar() or 0

        edges_stmt = select(func.count()).select_from(KnowledgeEdgeEntity)
        edges_result = await self._session.execute(edges_stmt)
        total_edges = edges_result.scalar() or 0

        return {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
        }

    # =============================================================
    # 系统统计 (异步)
    # =============================================================

    async def generate_system_statistics_snapshot(
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
        total_stmt = select(func.count()).select_from(TaskEntity)
        total_result = await self._session.execute(total_stmt)
        total_tasks = total_result.scalar() or 0

        completed_stmt = select(func.count()).select_from(TaskEntity).where(
            TaskEntity.execution_status == TaskStatusEnum.COMPLETED
        )
        completed_result = await self._session.execute(completed_stmt)
        completed = completed_result.scalar() or 0

        pending_stmt = select(func.count()).select_from(TaskEntity).where(
            TaskEntity.execution_status == TaskStatusEnum.PENDING
        )
        pending_result = await self._session.execute(pending_stmt)
        pending = pending_result.scalar() or 0

        failed_stmt = select(func.count()).select_from(TaskEntity).where(
            TaskEntity.execution_status == TaskStatusEnum.FAILED
        )
        failed_result = await self._session.execute(failed_stmt)
        failed = failed_result.scalar() or 0

        success_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0.0

        memories_stmt = select(func.count()).select_from(MemoryEntity)
        memories_result = await self._session.execute(memories_stmt)
        total_memories = memories_result.scalar() or 0

        experiences_stmt = select(func.count()).select_from(ExperienceEntity)
        experiences_result = await self._session.execute(experiences_stmt)
        total_experiences = experiences_result.scalar() or 0

        kg_stats = await self.retrieve_knowledge_graph_statistics()

        return SystemStatisticsSnapshotModel(
            total_tasks_count=total_tasks,
            completed_tasks_count=completed,
            pending_tasks_count=pending,
            failed_tasks_count=failed,
            success_rate_percentage=success_rate,
            total_memories_count=total_memories,
            total_experiences_count=total_experiences,
            knowledge_graph_nodes_count=kg_stats["total_nodes"],
            knowledge_graph_edges_count=kg_stats["total_edges"],
            uptime_seconds_value=time.time() - self._system_start_timestamp,
            current_operating_mode=current_mode,
        )
