"""
Core Layer - SQLAlchemy Database Models
核心层 - SQLAlchemy 数据库模型

This module defines SQLAlchemy ORM models for persistent storage.
Uses SQLAlchemy 2.0 style with type hints for better IDE support.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import enum


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class"""
    pass


class TaskStatusEnum(str, enum.Enum):
    """Task status enumeration for database"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriorityEnum(int, enum.Enum):
    """Task priority enumeration for database"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class MemoryCategoryEnum(str, enum.Enum):
    """Memory category enumeration for database"""
    GENERAL = "general"
    TECHNICAL = "technical"
    EXPERIENCE = "experience"
    KNOWLEDGE = "knowledge"
    CASE_STUDY = "case_study"


class AgentModeEnum(str, enum.Enum):
    """Agent operating mode enumeration for database"""
    TASK_EXECUTION = "task_execution"
    IDLE_IMPROVEMENT = "idle_improvement"
    PAUSED = "paused"


class TaskEntity(Base):
    """
    SQLAlchemy ORM model for tasks
    Represents a task in the system with full audit trail
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    unique_entity_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    task_title: Mapped[str] = mapped_column(String(255), nullable=False)
    task_description: Mapped[str] = mapped_column(Text, default="")

    execution_status: Mapped[str] = mapped_column(
        SQLEnum(TaskStatusEnum), default=TaskStatusEnum.PENDING
    )
    priority_level: Mapped[int] = mapped_column(
        SQLEnum(TaskPriorityEnum), default=TaskPriorityEnum.MEDIUM
    )

    created_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    started_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    execution_result_message: Mapped[str] = mapped_column(Text, default="")
    error_message: Mapped[str] = mapped_column(Text, default="")
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    execution_steps_json: Mapped[str] = mapped_column(Text, default="[]")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    memories: Mapped[List["MemoryEntity"]] = relationship(
        "MemoryEntity", back_populates="source_task", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<TaskEntity(id={self.id}, title='{self.task_title}', status={self.execution_status})>"


class MemoryEntity(Base):
    """
    SQLAlchemy ORM model for memories
    Stores agent memories and learned knowledge
    """
    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    unique_memory_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    content_text_body: Mapped[str] = mapped_column(Text, nullable=False)
    summary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    category_type: Mapped[str] = mapped_column(
        SQLEnum(MemoryCategoryEnum), default=MemoryCategoryEnum.GENERAL
    )
    tags_json: Mapped[str] = mapped_column(Text, default="[]")

    importance_score: Mapped[int] = mapped_column(Integer, default=3)
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source_task_id: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("tasks.unique_entity_id"), nullable=True
    )

    source_task: Mapped[Optional["TaskEntity"]] = relationship(
        "TaskEntity", back_populates="memories"
    )

    def __repr__(self) -> str:
        return f"<MemoryEntity(id={self.id}, category={self.category_type})>"


class ExperienceEntity(Base):
    """
    SQLAlchemy ORM model for experiences
    Records learned experiences from task execution
    """
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    unique_experience_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    task_reference_id: Mapped[str] = mapped_column(String(50), nullable=False)
    task_type_label: Mapped[str] = mapped_column(String(100), default="general")

    was_successful: Mapped[bool] = mapped_column(Boolean, default=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)

    lessons_learned_json: Mapped[str] = mapped_column(Text, default="[]")
    patterns_json: Mapped[str] = mapped_column(Text, default="[]")
    improvements_json: Mapped[str] = mapped_column(Text, default="[]")

    recorded_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<ExperienceEntity(id={self.id}, task_ref='{self.task_reference_id}')>"


class KnowledgeNodeEntity(Base):
    """
    SQLAlchemy ORM model for knowledge graph nodes
    Represents concepts in the knowledge graph
    """
    __tablename__ = "knowledge_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    label: Mapped[str] = mapped_column(String(255), nullable=False)
    properties_json: Mapped[str] = mapped_column(Text, default="{}")
    memory_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    created_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    outgoing_edges: Mapped[List["KnowledgeEdgeEntity"]] = relationship(
        "KnowledgeEdgeEntity",
        foreign_keys="KnowledgeEdgeEntity.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan"
    )
    incoming_edges: Mapped[List["KnowledgeEdgeEntity"]] = relationship(
        "KnowledgeEdgeEntity",
        foreign_keys="KnowledgeEdgeEntity.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<KnowledgeNodeEntity(id={self.id}, label='{self.label}')>"


class KnowledgeEdgeEntity(Base):
    """
    SQLAlchemy ORM model for knowledge graph edges
    Represents relationships between concepts
    """
    __tablename__ = "knowledge_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    edge_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )

    source_node_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("knowledge_nodes.node_id"), nullable=False
    )
    target_node_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("knowledge_nodes.node_id"), nullable=False
    )

    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    created_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    source_node: Mapped["KnowledgeNodeEntity"] = relationship(
        "KnowledgeNodeEntity",
        foreign_keys=[source_node_id],
        back_populates="outgoing_edges"
    )
    target_node: Mapped["KnowledgeNodeEntity"] = relationship(
        "KnowledgeNodeEntity",
        foreign_keys=[target_node_id],
        back_populates="incoming_edges"
    )

    def __repr__(self) -> str:
        return f"<KnowledgeEdgeEntity(id={self.id}, type='{self.relationship_type}')>"


class SystemMetricsEntity(Base):
    """
    SQLAlchemy ORM model for system metrics
    Stores historical system performance metrics
    """
    __tablename__ = "system_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    total_tasks: Mapped[int] = mapped_column(Integer, default=0)
    completed_tasks: Mapped[int] = mapped_column(Integer, default=0)
    pending_tasks: Mapped[int] = mapped_column(Integer, default=0)
    failed_tasks: Mapped[int] = mapped_column(Integer, default=0)

    success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_execution_time: Mapped[float] = mapped_column(Float, default=0.0)

    memory_usage_mb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cpu_usage_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    current_mode: Mapped[str] = mapped_column(
        SQLEnum(AgentModeEnum), default=AgentModeEnum.PAUSED
    )
    uptime_seconds: Mapped[float] = mapped_column(Float, default=0.0)

    def __repr__(self) -> str:
        return f"<SystemMetricsEntity(timestamp={self.timestamp})>"
