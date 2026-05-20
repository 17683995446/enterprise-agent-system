"""
Domain Layer - Core Data Models and Enumerations
领域层 - 核心数据模型和枚举定义

职责：
- 定义所有核心领域数据模型
- 定义任务状态、优先级等枚举
- 提供类型安全的数据结构
"""

from enum import Enum, IntEnum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TypeVar, Type
from datetime import datetime, timezone
from uuid import uuid4


# =============================================================
# 辅助函数
# =============================================================

def generate_unique_entity_identifier(prefix: str = "entity") -> str:
    """生成唯一实体标识符"""
    return f"{prefix}_{uuid4().hex[:12]}"


def get_current_utc_timestamp() -> datetime:
    """获取当前 UTC 时间戳"""
    return datetime.now(timezone.utc)


E = TypeVar('E', bound=Enum)


def validate_and_convert_enum(
    value: Any, 
    enum_type: Type[E], 
    default_value: E
) -> E:
    """
    验证并转换为枚举类型
    
    支持：
    - 枚举对象本身
    - 字符串（枚举名称或值）
    - 整数（对于 IntEnum）
    
    Args:
        value: 要验证的值
        enum_type: 目标枚举类型
        default_value: 转换失败时的默认值
        
    Returns:
        有效的枚举值
    """
    if isinstance(value, enum_type):
        return value
    
    if value is None:
        return default_value
    
    if isinstance(value, str):
        value_lower = value.lower()
        for enum_val in enum_type:
            if enum_val.name.lower() == value_lower or str(enum_val.value) == value_lower:
                return enum_val
            if str(enum_val.value) == value:
                return enum_val
        return default_value
    
    if isinstance(value, int) and hasattr(enum_type, '_value2member_map_'):
        if value in enum_type._value2member_map_:
            return enum_type(value)
    
    return default_value


# =============================================================
# 枚举类型定义
# =============================================================

class TaskExecutionStatusEnumeration(Enum):
    """任务执行状态枚举"""
    PENDING_STATUS = "pending"
    IN_PROGRESS_STATUS = "in_progress"
    COMPLETED_STATUS = "completed"
    FAILED_STATUS = "failed"
    CANCELLED_STATUS = "cancelled"


class TaskPriorityLevelEnumeration(IntEnum):
    """任务优先级等级枚举"""
    LOW_PRIORITY_LEVEL = 1
    MEDIUM_PRIORITY_LEVEL = 2
    HIGH_PRIORITY_LEVEL = 3
    URGENT_PRIORITY_LEVEL = 4


class MemoryCategoryTypeEnumeration(Enum):
    """记忆类别类型枚举"""
    GENERAL_MEMORY_CATEGORY = "general"
    TECHNICAL_MEMORY_CATEGORY = "technical"
    EXPERIENCE_MEMORY_CATEGORY = "experience"
    KNOWLEDGE_MEMORY_CATEGORY = "knowledge"
    CASE_STUDY_MEMORY_CATEGORY = "case_study"


class AgentOperatingModeEnumeration(Enum):
    """Agent 运行模式枚举"""
    TASK_EXECUTION_MODE = "task_execution"
    IDLE_IMPROVEMENT_MODE = "idle_improvement"
    PAUSED_MODE = "paused"


class SystemHealthStatusEnumeration(Enum):
    """系统健康状态枚举"""
    HEALTHY_STATUS = "healthy"
    DEGRADED_STATUS = "degraded"
    UNHEALTHY_STATUS = "unhealthy"


# =============================================================
# 数据模型定义
# =============================================================

@dataclass
class TaskExecutionDataModel:
    """
    任务执行数据模型 - 核心领域模型

    Attributes:
        unique_entity_id: 唯一实体标识符
        task_title: 任务标题
        task_description: 任务描述
        execution_status: 执行状态
        priority_level: 优先级等级
        created_timestamp: 创建时间戳
        started_timestamp: 开始执行时间戳
        completed_timestamp: 完成时间戳
        execution_result_message: 执行结果消息
        error_message: 错误消息
        progress_percentage_value: 进度百分比值
        execution_steps_list: 执行步骤列表
        metadata_dictionary: 元数据字典
    """
    unique_entity_id: str = field(
        default_factory=lambda: generate_unique_entity_identifier("task")
    )
    task_title: str = field(default_factory=str)
    task_description: str = field(default="")
    execution_status: TaskExecutionStatusEnumeration = field(
        default=TaskExecutionStatusEnumeration.PENDING_STATUS
    )
    priority_level: TaskPriorityLevelEnumeration = field(
        default=TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL
    )
    created_timestamp: datetime = field(
        default_factory=get_current_utc_timestamp
    )
    started_timestamp: Optional[datetime] = field(default=None)
    completed_timestamp: Optional[datetime] = field(default=None)
    execution_result_message: str = field(default="")
    error_message: str = field(default="")
    progress_percentage_value: float = field(default=0.0)
    execution_steps_list: List[str] = field(default_factory=list)
    metadata_dictionary: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后处理"""
        self.execution_status = validate_and_convert_enum(
            self.execution_status,
            TaskExecutionStatusEnumeration,
            TaskExecutionStatusEnumeration.PENDING_STATUS
        )
        self.priority_level = validate_and_convert_enum(
            self.priority_level,
            TaskPriorityLevelEnumeration,
            TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL
        )
        self.progress_percentage_value = max(
            0.0, min(1.0, self.progress_percentage_value)
        )


@dataclass
class MemoryStorageDataModel:
    """
    记忆存储数据模型 - 知识记忆

    Attributes:
        unique_memory_id: 唯一记忆标识符
        content_text_body: 内容文本主体
        summary_text: 摘要文本
        category_type: 类别类型
        tags_list: 标签列表
        importance_score: 重要性评分
        access_count_number: 访问次数
        last_accessed_timestamp: 最后访问时间戳
        created_timestamp: 创建时间戳
        updated_timestamp: 更新时间戳
        source_task_id: 来源任务标识符
    """
    unique_memory_id: str = field(
        default_factory=lambda: generate_unique_entity_identifier("memory")
    )
    content_text_body: str = field(default_factory=str)
    summary_text: Optional[str] = field(default=None)
    category_type: MemoryCategoryTypeEnumeration = field(
        default=MemoryCategoryTypeEnumeration.GENERAL_MEMORY_CATEGORY
    )
    tags_list: List[str] = field(default_factory=list)
    importance_score: int = field(default=3)
    access_count_number: int = field(default=0)
    last_accessed_timestamp: Optional[datetime] = field(default=None)
    created_timestamp: datetime = field(
        default_factory=get_current_utc_timestamp
    )
    updated_timestamp: datetime = field(
        default_factory=get_current_utc_timestamp
    )
    source_task_id: Optional[str] = field(default=None)
    
    def __post_init__(self):
        """初始化后处理"""
        self.category_type = validate_and_convert_enum(
            self.category_type,
            MemoryCategoryTypeEnumeration,
            MemoryCategoryTypeEnumeration.GENERAL_MEMORY_CATEGORY
        )
        # 确保重要性评分在合理范围
        self.importance_score = max(1, min(5, self.importance_score))


@dataclass
class ExperienceLearningDataModel:
    """
    经验学习数据模型 - 从任务中学习的经验

    Attributes:
        unique_experience_id: 唯一经验标识符
        task_reference_id: 任务引用标识符
        task_type_label: 任务类型标签
        was_successful_flag: 是否成功标志
        duration_seconds_value: 执行时长秒值
        lessons_learned_list: 学到的经验教训列表
        patterns_recognized_list: 识别的模式列表
        suggested_improvements_list: 建议的改进列表
        recorded_timestamp: 记录时间戳
    """
    unique_experience_id: str = field(
        default_factory=lambda: generate_unique_entity_identifier("experience")
    )
    task_reference_id: str = field(default_factory=str)
    task_type_label: str = field(default="general")
    was_successful_flag: bool = field(default=True)
    duration_seconds_value: float = field(default=0.0)
    lessons_learned_list: List[str] = field(default_factory=list)
    patterns_recognized_list: List[str] = field(default_factory=list)
    suggested_improvements_list: List[str] = field(default_factory=list)
    recorded_timestamp: datetime = field(
        default_factory=get_current_utc_timestamp
    )


@dataclass
class SystemStatisticsSnapshotModel:
    """
    系统统计快照数据模型 - 系统状态统计

    Attributes:
        total_tasks_count: 任务总数
        completed_tasks_count: 已完成任务数
        pending_tasks_count: 待处理任务数
        failed_tasks_count: 失败任务数
        success_rate_percentage: 成功率百分比
        average_execution_seconds: 平均执行秒数
        total_memories_count: 记忆总数
        total_experiences_count: 经验总数
        knowledge_graph_nodes_count: 知识图谱节点数
        knowledge_graph_edges_count: 知识图谱边数
        uptime_seconds_value: 运行时间秒值
        current_operating_mode: 当前运行模式
    """
    total_tasks_count: int = field(default=0)
    completed_tasks_count: int = field(default=0)
    pending_tasks_count: int = field(default=0)
    failed_tasks_count: int = field(default=0)
    success_rate_percentage: float = field(default=0.0)
    average_execution_seconds: float = field(default=0.0)
    total_memories_count: int = field(default=0)
    total_experiences_count: int = field(default=0)
    knowledge_graph_nodes_count: int = field(default=0)
    knowledge_graph_edges_count: int = field(default=0)
    uptime_seconds_value: float = field(default=0.0)
    current_operating_mode: AgentOperatingModeEnumeration = field(
        default=AgentOperatingModeEnumeration.PAUSED_MODE
    )


@dataclass
class HealthCheckResultModel:
    """
    健康检查结果数据模型 - 系统健康状态

    Attributes:
        health_status: 健康状态
        status_message: 状态消息
        details_dictionary: 详细信息字典
        checked_timestamp: 检查时间戳
    """
    health_status: SystemHealthStatusEnumeration
    status_message: str
    details_dictionary: Dict[str, Any] = field(default_factory=dict)
    checked_timestamp: datetime = field(
        default_factory=get_current_utc_timestamp
    )
