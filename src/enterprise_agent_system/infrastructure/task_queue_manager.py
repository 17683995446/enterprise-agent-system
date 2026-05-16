"""
Task Queue Manager for Enterprise Agent System
Infrastructure Layer - 分布式任务队列管理器
"""

from typing import Dict, Any, Optional, List
from celery.result import AsyncResult
from celery import group, chain, chord
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
from enterprise_agent_system.infrastructure.celery_app import app
from enterprise_agent_system.infrastructure.redis_client import get_redis_client
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance


logger = get_logger_instance(__name__)


class TaskPriority(Enum):
    """任务优先级"""
    URGENT = 'urgent'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    
    def to_queue(self) -> str:
        """转换为队列名称"""
        mapping = {
            'urgent': 'urgent',
            'high': 'default',
            'medium': 'default',
            'low': 'low',
        }
        return mapping.get(self.value, 'default')


class TaskStatus(Enum):
    """任务状态"""
    PENDING = 'pending'
    STARTED = 'started'
    PROGRESS = 'progress'
    SUCCESS = 'success'
    FAILURE = 'failure'
    REVOKED = 'revoked'


@dataclass
class TaskInfo:
    """任务信息"""
    task_id: str
    task_name: str
    status: str
    result: Optional[Any] = None
    progress: float = 0.0
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class TaskQueueManager:
    """任务队列管理器"""
    
    def __init__(self):
        self.app = app
        self.redis_client = get_redis_client()
        self.task_prefix = 'celery_task:'
        self.task_meta_prefix = 'celery_task_meta:'
        logger.info("TaskQueueManager initialized")
    
    def submit_task(
        self,
        task_name: str,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        countdown: Optional[float] = None,
        expires: Optional[float] = None,
    ) -> str:
        """
        提交任务
        
        Args:
            task_name: 任务名称
            args: 位置参数
            kwargs: 关键字参数
            priority: 优先级
            countdown: 延迟执行秒数
            expires: 任务过期时间
        
        Returns:
            任务ID
        """
        kwargs = kwargs or {}
        
        logger.info(f"Submitting task: {task_name} with priority {priority.value}")
        
        # 选择任务
        task = self.app.task(task_name)
        
        # 提交任务
        if countdown:
            result = task.apply_async(
                args=args,
                kwargs=kwargs,
                queue=priority.to_queue(),
                countdown=countdown,
                expires=expires,
            )
        else:
            result = task.apply_async(
                args=args,
                kwargs=kwargs,
                queue=priority.to_queue(),
                expires=expires,
            )
        
        task_id = result.id
        
        # 存储任务元数据
        self._store_task_meta(task_id, {
            'task_name': task_name,
            'priority': priority.value,
            'created_at': datetime.now().isoformat(),
            'args': args,
            'kwargs': kwargs,
        })
        
        logger.info(f"Task submitted: {task_id}")
        return task_id
    
    def submit_batch(
        self,
        task_configs: List[Dict[str, Any]],
        parallel: bool = True
    ) -> List[str]:
        """
        批量提交任务
        
        Args:
            task_configs: 任务配置列表
            parallel: 是否并行执行
        
        Returns:
            任务ID列表
        """
        task_ids = []
        
        for config in task_configs:
            task_name = config.get('task_name')
            args = config.get('args', ())
            kwargs = config.get('kwargs', {})
            priority = TaskPriority(config.get('priority', 'medium'))
            
            task_id = self.submit_task(task_name, args, kwargs, priority)
            task_ids.append(task_id)
        
        logger.info(f"Batch submitted {len(task_ids)} tasks")
        return task_ids
    
    def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """
        获取任务结果
        
        Args:
            task_id: 任务ID
            timeout: 超时时间
        
        Returns:
            任务结果
        """
        result = AsyncResult(task_id, app=self.app)
        
        if timeout:
            return result.get(timeout=timeout)
        else:
            return result.get()
    
    def get_task_status(self, task_id: str) -> TaskInfo:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务信息
        """
        result = AsyncResult(task_id, app=self.app)
        
        status = result.state.lower()
        progress = 0.0
        result_data = None
        error = None
        
        if status == 'progress':
            progress = result.info.get('progress', 0.0) if isinstance(result.info, dict) else 0.0
            status = 'progress'
        elif status == 'success':
            result_data = result.result
            progress = 1.0
        elif status == 'failure':
            error = str(result.info)
        
        meta = self._get_task_meta(task_id)
        
        return TaskInfo(
            task_id=task_id,
            task_name=meta.get('task_name', 'unknown') if meta else 'unknown',
            status=status,
            result=result_data,
            progress=progress,
            error=error,
            created_at=meta.get('created_at') if meta else None,
        )
    
    def revoke_task(self, task_id: str, terminate: bool = False) -> bool:
        """
        撤销任务
        
        Args:
            task_id: 任务ID
            terminate: 是否强制终止
        
        Returns:
            是否成功
        """
        try:
            self.app.control.revoke(task_id, terminate=terminate)
            logger.info(f"Task revoked: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to revoke task {task_id}: {e}")
            return False
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        获取队列统计
        
        Returns:
            队列统计信息
        """
        try:
            inspect = self.app.control.inspect()
            
            active_tasks = inspect.active()
            scheduled_tasks = inspect.scheduled()
            registered_tasks = inspect.registered()
            stats = inspect.stats()
            
            return {
                'active_tasks': active_tasks,
                'scheduled_tasks': scheduled_tasks,
                'registered_tasks': registered_tasks,
                'worker_stats': stats,
            }
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {}
    
    def get_worker_info(self) -> List[Dict[str, Any]]:
        """
        获取Worker信息
        
        Returns:
            Worker信息列表
        """
        try:
            inspect = self.app.control.inspect()
            stats = inspect.stats()
            
            workers = []
            if stats:
                for worker_name, worker_stats in stats.items():
                    workers.append({
                        'name': worker_name,
                        'status': 'online',
                        'statistics': worker_stats,
                    })
            
            return workers
        except Exception as e:
            logger.error(f"Failed to get worker info: {e}")
            return []
    
    def cancel_all_tasks(self) -> int:
        """
        取消所有任务
        
        Returns:
            取消的任务数量
        """
        try:
            inspect = self.app.control.inspect()
            active = inspect.active()
            
            count = 0
            if active:
                for worker, tasks in active.items():
                    for task in tasks:
                        self.revoke_task(task['id'], terminate=True)
                        count += 1
            
            logger.info(f"Cancelled {count} tasks")
            return count
        except Exception as e:
            logger.error(f"Failed to cancel all tasks: {e}")
            return 0
    
    def _store_task_meta(self, task_id: str, meta: Dict[str, Any]):
        """存储任务元数据"""
        key = f"{self.task_meta_prefix}{task_id}"
        self.redis_client.set(key, json.dumps(meta), expire=86400)  # 24小时过期
    
    def _get_task_meta(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务元数据"""
        key = f"{self.task_meta_prefix}{task_id}"
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    
    def create_task_group(self, task_ids: List[str]) -> group:
        """
        创建任务组
        
        Args:
            task_ids: 任务ID列表
        
        Returns:
            任务组
        """
        tasks = [AsyncResult(tid, app=self.app) for tid in task_ids]
        return group(tasks)
    
    def create_task_chain(self, *task_ids: str) -> chain:
        """
        创建任务链
        
        Args:
            *task_ids: 任务ID列表
        
        Returns:
            任务链
        """
        tasks = [AsyncResult(tid, app=self.app) for tid in task_ids]
        return chain(*tasks)


# 全局任务队列管理器实例
_task_queue_manager: Optional[TaskQueueManager] = None


def get_task_queue_manager() -> TaskQueueManager:
    """获取任务队列管理器实例"""
    global _task_queue_manager
    if _task_queue_manager is None:
        _task_queue_manager = TaskQueueManager()
    return _task_queue_manager
