"""
Core Layer - Agent Orchestrator and Executor
核心层 - Agent 编排器和执行器

职责：
- 管理 Agent 主循环
- 协调任务执行流程
- 实现双重模式运行
- 管理空闲改进和学习
"""

import asyncio
import time
import re
from typing import Optional, List
from datetime import datetime, timezone

from enterprise_agent_system.infrastructure.application_configuration_management import (
    get_application_configuration_instance,
)
from enterprise_agent_system.infrastructure.enterprise_logging_system import (
    get_logger_instance,
)
from enterprise_agent_system.domain.core_data_models_and_enumerations import (
    TaskExecutionDataModel,
    TaskExecutionStatusEnumeration,
    TaskPriorityLevelEnumeration,
    MemoryCategoryTypeEnumeration,
    AgentOperatingModeEnumeration,
    get_current_utc_timestamp,
)
from enterprise_agent_system.core.storage_backend_factory import (
    get_storage_backend_instance,
)
from enterprise_agent_system.core.storage_backend_interface import (
    StorageBackendInterface,
)


class AgentOrchestratorAndExecutor:
    """
    Agent 编排器和执行器类

    主要功能：
    1. 任务执行模式 - 处理用户提交的任务
    2. 空闲改进模式 - 自我优化和学习
    3. 知识图谱记忆 - 从任务中学习
    4. 完整统计和监控
    """

    def __init__(
        self,
        agent_name: str = "Enterprise Agent",
    ):
        """
        初始化 Agent 编排器和执行器

        Args:
            agent_name: Agent 名称
        """
        self.agent_name = agent_name
        self.configuration = get_application_configuration_instance()
        self.current_operating_mode = AgentOperatingModeEnumeration.PAUSED_MODE
        self.system_start_timestamp = time.time()

        self.logger = get_logger_instance(f"{__name__}.{agent_name}")
        self.storage_backend: StorageBackendInterface = (
            get_storage_backend_instance()
        )

        self._shutdown_request_flag = False
        self._currently_executing_task_id: Optional[str] = None

        self.logger.info(
            f"Agent '{self.agent_name}' initialized successfully",
            extra={"version": self.configuration.application_version_string},
        )

        self.current_operating_mode = AgentOperatingModeEnumeration.IDLE_IMPROVEMENT_MODE

    # =============================================================
    # 任务管理
    # =============================================================

    def create_and_queue_task(
        self,
        task_title: str,
        task_description: str = "",
        priority_level: TaskPriorityLevelEnumeration = TaskPriorityLevelEnumeration.MEDIUM_PRIORITY_LEVEL,
    ) -> str:
        """
        创建并排队任务

        Args:
            task_title: 任务标题
            task_description: 任务描述
            priority_level: 优先级等级

        Returns:
            创建的任务 ID
        """
        task = self.storage_backend.create_new_task_entry(
            task_title=task_title,
            task_description=task_description,
            priority_level=priority_level,
        )

        self.logger.info(
            f"Task created and queued: {task_title}",
        )

        return task.unique_entity_id

    async def execute_task_by_id(self, task_id: str) -> TaskExecutionDataModel:
        """
        根据 ID 执行任务

        Args:
            task_id: 任务 ID

        Returns:
            执行完成的任务
        """
        task = self.storage_backend.retrieve_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID '{task_id}' not found")

        self.current_operating_mode = AgentOperatingModeEnumeration.TASK_EXECUTION_MODE
        self._currently_executing_task_id = task_id

        try:
            self.logger.info(
                f"Starting task execution: {task.task_title}",
            )

            task.execution_status = TaskExecutionStatusEnumeration.IN_PROGRESS_STATUS
            task.started_timestamp = get_current_utc_timestamp()

            await self._simulate_task_execution_workflow(task)

            task.execution_status = TaskExecutionStatusEnumeration.COMPLETED_STATUS
            task.execution_result_message = (
                f"Task '{task.task_title}' completed successfully"
            )
            task.completed_timestamp = get_current_utc_timestamp()

            if task.completed_timestamp and task.started_timestamp:
                duration_seconds = (
                    task.completed_timestamp - task.started_timestamp
                ).total_seconds()

                self._extract_learning_from_completed_task(
                    task,
                    duration_seconds,
                )

            self.logger.info(
                f"Task completed successfully: {task.task_title}",
            )

        except Exception as error:
            task.execution_status = TaskExecutionStatusEnumeration.FAILED_STATUS
            task.error_message = str(error)
            task.completed_timestamp = get_current_utc_timestamp()

            self._record_failed_task_execution(task, str(error))

            self.logger.error(
                f"Task execution failed: {task.task_title}",
                extra={"error": str(error)},
            )

        finally:
            self._currently_executing_task_id = None

            pending_tasks = self.storage_backend.retrieve_pending_tasks_sorted_by_priority()
            if pending_tasks:
                self.current_operating_mode = (
                    AgentOperatingModeEnumeration.TASK_EXECUTION_MODE
                )
            else:
                self.current_operating_mode = (
                    AgentOperatingModeEnumeration.IDLE_IMPROVEMENT_MODE
                )

        return task

    async def _simulate_task_execution_workflow(self, task: TaskExecutionDataModel) -> None:
        """
        模拟任务执行工作流

        Args:
            task: 正在执行的任务
        """
        total_execution_steps = 5

        for step in range(1, total_execution_steps + 1):
            await asyncio.sleep(0.1)

            task.progress_percentage_value = step / total_execution_steps
            task.execution_steps_list.append(
                f"Step {step}/{total_execution_steps} completed"
            )

    def _extract_learning_from_completed_task(
        self,
        task: TaskExecutionDataModel,
        duration_seconds: float,
    ) -> None:
        """
        从完成的任务中提取学习内容

        Args:
            task: 完成的任务
            duration_seconds: 执行时长
        """
        if task.execution_status != TaskExecutionStatusEnumeration.COMPLETED_STATUS:
            return

        memory = self.storage_backend.create_new_memory_entry(
            content_text=f"Completed task: {task.task_title}\nResult: {task.execution_result_message[:200]}",
            category_type=MemoryCategoryTypeEnumeration.EXPERIENCE_MEMORY_CATEGORY,
            tags_list=["task", "completed"],
            importance_score=4,
            source_task_id=task.unique_entity_id,
        )

        self._build_knowledge_from_text_content(
            task.execution_result_message,
            memory.unique_memory_id,
        )

        self.storage_backend.create_new_experience_entry(
            task_reference_id=task.unique_entity_id,
            task_type_label="general",
            was_successful=True,
            duration_seconds=duration_seconds,
            lessons_learned=[f"Successfully executed: {task.task_title}"],
        )

    def _record_failed_task_execution(
        self,
        task: TaskExecutionDataModel,
        error_message: str,
    ) -> None:
        """记录失败的任务执行"""
        self.storage_backend.create_new_experience_entry(
            task_reference_id=task.unique_entity_id,
            task_type_label="general",
            was_successful=False,
            duration_seconds=0.0,
            lessons_learned=[f"Task failed: {error_message}"],
        )

    def _build_knowledge_from_text_content(
        self,
        content_text: str,
        memory_id: str,
    ) -> None:
        """
        从文本内容构建知识

        Args:
            content_text: 文本内容
            memory_id: 记忆 ID
        """
        words = re.findall(r"\b[a-zA-Z]{4,}\b", content_text.lower())

        for word in set(words):
            try:
                self.storage_backend.add_node_to_knowledge_graph(
                    label=word,
                    memory_id=memory_id,
                )
            except Exception:
                pass

    # =============================================================
    # 空闲改进
    # =============================================================

    async def perform_idle_improvement_cycle(self) -> None:
        """
        执行空闲改进周期

        在没有任务时，Agent 会：
        1. 组织记忆
        2. 从历史学习
        3. 更新知识图谱
        """
        self.current_operating_mode = (
            AgentOperatingModeEnumeration.IDLE_IMPROVEMENT_MODE
        )

        self.logger.debug("Starting idle improvement cycle")

        all_memories = self.storage_backend.retrieve_all_memories()
        for memory in all_memories[:5]:
            self._build_knowledge_from_text_content(
                memory.content_text_body,
                memory.unique_memory_id,
            )

        await asyncio.sleep(0.5)

        self.logger.debug("Idle improvement cycle completed")

    # =============================================================
    # 主循环
    # =============================================================

    async def run_main_execution_loop(
        self,
        max_iteration_count: Optional[int] = None,
    ) -> None:
        """
        运行主执行循环

        Args:
            max_iteration_count: 最大迭代次数
        """
        self.logger.info(
            f"Starting main execution loop",
            extra={"max_iterations": max_iteration_count or "unlimited"},
        )

        iteration_count = 0

        try:
            while not self._shutdown_request_flag:
                pending_tasks = (
                    self.storage_backend.retrieve_pending_tasks_sorted_by_priority()
                )

                if pending_tasks:
                    await self.execute_task_by_id(
                        pending_tasks[0].unique_entity_id
                    )
                else:
                    await self.perform_idle_improvement_cycle()

                iteration_count += 1

                if max_iteration_count and iteration_count >= max_iteration_count:
                    self.logger.info(
                        f"Reached max iteration count: {max_iteration_count}"
                    )
                    break

                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as error:
            self.logger.exception(
                f"Fatal error in main loop",
                extra={"error": str(error)},
            )
            raise
        finally:
            await self.shutdown_agent_gracefully()

    def request_shutdown(self) -> None:
        """请求关闭 Agent"""
        self._shutdown_request_flag = True
        self.logger.info("Shutdown requested")

    async def shutdown_agent_gracefully(self) -> None:
        """优雅关闭 Agent"""
        self.current_operating_mode = AgentOperatingModeEnumeration.PAUSED_MODE
        self._shutdown_request_flag = True

        self.logger.info(
            f"Agent shutdown complete",
            extra={
                "total_runtime_seconds": time.time()
                - self.system_start_timestamp,
            },
        )

    # =============================================================
    # 查询和统计
    # =============================================================

    @property
    def current_system_statistics(self):
        """获取当前系统统计"""
        return self.storage_backend.generate_system_statistics_snapshot(
            self.current_operating_mode
        )

    @property
    def system_uptime_seconds(self) -> float:
        """获取系统运行时间（秒）"""
        return time.time() - self.system_start_timestamp

    @property
    def pending_task_summary(self) -> dict:
        """获取待处理任务摘要"""
        pending = self.storage_backend.retrieve_pending_tasks_sorted_by_priority()

        summary = {
            "total": len(pending),
            "urgent": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for task in pending:
            summary[task.priority_level.name.lower().replace("_priority_level", "")] += 1

        return summary
