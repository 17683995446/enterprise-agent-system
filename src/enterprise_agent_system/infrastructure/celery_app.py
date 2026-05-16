"""
Celery Application for Enterprise Agent System
Infrastructure Layer - 分布式任务队列应用
"""

from celery import Celery
from celery.schedules import crontab
from typing import Dict, Any, Optional, Callable
import json
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance


logger = get_logger_instance(__name__)


# Celery配置
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

# 创建Celery应用
app = Celery(
    'enterprise_agent_system',
    broker=broker_url,
    backend=result_backend,
    include=[
        'enterprise_agent_system.infrastructure.celery_tasks',
    ]
)

# Celery配置
app.conf.update(
    # 任务序列化
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    
    # 时间zone
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # 任务结果过期时间
    result_expires=3600,
    
    # 任务路由
    task_routes={
        'enterprise_agent_system.infrastructure.celery_tasks.*': {
            'queue': 'default',
        },
        'enterprise_agent_system.infrastructure.celery_tasks.urgent.*': {
            'queue': 'urgent',
        },
    },
    
    # 任务默认设置
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
    
    # 任务追踪
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Worker设置
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Beat调度（定期任务）
    beat_scheduler='celery.beat:PersistentScheduler',
    beat_schedule_filename='/tmp/celerybeat-schedule',
)

# 定义队列
app.conf.task_queues = {
    'default': {
        'exchange': 'default',
        'exchange_type': 'direct',
        'routing_key': 'default',
    },
    'urgent': {
        'exchange': 'urgent',
        'exchange_type': 'direct',
        'routing_key': 'urgent',
    },
    'low': {
        'exchange': 'low',
        'exchange_type': 'direct',
        'routing_key': 'low',
    },
}


@app.task(name='enterprise_agent_system.ping')
def ping() -> str:
    """心跳检测任务"""
    return 'pong'


@app.task(name='enterprise_agent_system.echo', bind=True)
def echo(self, message: str) -> str:
    """回显任务"""
    logger.info(f"Echo task received: {message}")
    return f"Echo: {message}"


@app.task(
    name='enterprise_agent_system.process_task',
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def process_task(
    self,
    task_id: str,
    task_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理任务
    
    Args:
        task_id: 任务ID
        task_data: 任务数据
    
    Returns:
        处理结果
    """
    logger.info(f"Processing task {task_id}")
    
    try:
        # 模拟任务处理
        result = {
            'task_id': task_id,
            'status': 'completed',
            'data': task_data,
            'processed_by': 'celery_worker',
        }
        
        logger.info(f"Task {task_id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        raise


@app.task(
    name='enterprise_agent_system.analyze_project_task',
    bind=True,
    max_retries=2,
    default_retry_delay=120,
)
def analyze_project_task(
    self,
    project_path: str,
    analysis_type: str = 'auto'
) -> Dict[str, Any]:
    """
    分析项目任务
    
    Args:
        project_path: 项目路径
        analysis_type: 分析类型
    
    Returns:
        分析结果
    """
    logger.info(f"Analyzing project: {project_path}")
    
    try:
        # 导入分析器
        from enterprise_agent_system.infrastructure.typescript_vue_project_analyzer import (
            TypeScriptVueProjectAnalyzer
        )
        
        analyzer = TypeScriptVueProjectAnalyzer(project_path)
        result = analyzer.analyze_project()
        
        return {
            'project_path': project_path,
            'analysis_type': analysis_type,
            'status': 'completed',
            'project_name': result.project_name,
            'project_type': result.project_type,
        }
        
    except Exception as e:
        logger.error(f"Project analysis failed: {e}")
        raise


@app.task(
    name='enterprise_agent_system.heavy_computation_task',
    bind=True,
    max_retries=1,
    time_limit=3600,
    soft_time_limit=3000,
)
def heavy_computation_task(
    self,
    computation_type: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    重计算任务
    
    Args:
        computation_type: 计算类型
        params: 计算参数
    
    Returns:
        计算结果
    """
    logger.info(f"Heavy computation: {computation_type}")
    
    # 模拟计算
    result = {
        'type': computation_type,
        'params': params,
        'status': 'completed',
        'result': f"Computation result for {computation_type}",
    }
    
    return result


@app.task(name='enterprise_agent_system.cleanup_task')
def cleanup_task() -> Dict[str, str]:
    """
    清理任务
    
    定期清理过期数据和缓存
    """
    logger.info("Running cleanup task")
    
    from enterprise_agent_system.infrastructure.redis_client import get_redis_client
    
    redis_client = get_redis_client()
    
    # 清理过期键
    cleaned_keys = 0
    
    # 这里可以实现具体的清理逻辑
    logger.info(f"Cleanup completed, cleaned {cleaned_keys} keys")
    
    return {
        'status': 'completed',
        'cleaned_keys': cleaned_keys,
    }


# 定期任务调度
app.conf.beat_schedule = {
    'cleanup-every-hour': {
        'task': 'enterprise_agent_system.cleanup_task',
        'schedule': crontab(minute=0),  # 每小时
    },
    'health-check-every-5-minutes': {
        'task': 'enterprise_agent_system.ping',
        'schedule': crontab(minute='*/5'),  # 每5分钟
    },
}


if __name__ == '__main__':
    app.start()
