"""
Prometheus Metrics for Enterprise Agent System
Infrastructure Layer - Prometheus指标收集和暴露
"""

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    REGISTRY,
    multiprocess,
    REGISTRY as _REGISTRY,
)
from prometheus_client.core import (
    GaugeMetricFamily,
    CounterMetricFamily,
    HistogramMetricFamily,
    SummaryMetricFamily,
)
import time
from functools import wraps
from typing import Callable, Any
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance


logger = get_logger_instance(__name__)


# ==================== 自定义指标 ====================

# Agent相关指标
AGENT_TASKS_TOTAL = Counter(
    'agent_tasks_total',
    'Total number of tasks processed',
    ['task_type', 'status']
)

AGENT_TASK_DURATION = Histogram(
    'agent_task_duration_seconds',
    'Task processing duration in seconds',
    ['task_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

AGENT_ACTIVE_TASKS = Gauge(
    'agent_active_tasks',
    'Number of currently active tasks',
    ['priority']
)

AGENT_QUEUE_DEPTH = Gauge(
    'agent_queue_depth',
    'Number of tasks in queue',
    ['queue_name']
)

# API相关指标
API_REQUESTS_TOTAL = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code']
)

API_REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

API_IN_PROGRESS = Gauge(
    'api_requests_in_progress',
    'Number of API requests currently being processed',
    ['method', 'endpoint']
)

# 知识图谱指标
KNOWLEDGE_GRAPH_NODES = Gauge(
    'knowledge_graph_nodes_total',
    'Total number of nodes in knowledge graph'
)

KNOWLEDGE_GRAPH_EDGES = Gauge(
    'knowledge_graph_edges_total',
    'Total number of edges in knowledge graph'
)

KNOWLEDGE_GRAPH_QUERIES = Counter(
    'knowledge_graph_queries_total',
    'Total number of knowledge graph queries',
    ['status']
)

# 系统资源指标
SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

SYSTEM_DISK_USAGE = Gauge(
    'system_disk_usage_bytes',
    'System disk usage in bytes'
)

# 任务优先级分布
TASK_PRIORITY_DISTRIBUTION = Gauge(
    'task_priority_distribution',
    'Number of tasks by priority',
    ['priority']
)

# 任务成功率
TASK_SUCCESS_RATE = Gauge(
    'task_success_rate',
    'Task success rate',
    ['task_type']
)

# Celery相关指标
CELERY_WORKER_TASKS = Counter(
    'celery_worker_tasks_total',
    'Total number of Celery worker tasks',
    ['task_name', 'status']
)

CELERY_WORKER_DURATION = Histogram(
    'celery_worker_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

CELERY_QUEUE_LENGTH = Gauge(
    'celery_queue_length',
    'Number of tasks in Celery queue',
    ['queue_name']
)

# 缓存指标
CACHE_HITS = Counter(
    'cache_hits_total',
    'Total number of cache hits'
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total number of cache misses'
)

CACHE_SIZE = Gauge(
    'cache_size_bytes',
    'Size of cache in bytes'
)

# 系统信息
SYSTEM_INFO = Info(
    'system',
    'System information'
)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.registry = REGISTRY
        logger.info("MetricsCollector initialized")
    
    def record_task(self, task_type: str, status: str, duration: float):
        """记录任务指标"""
        AGENT_TASKS_TOTAL.labels(task_type=task_type, status=status).inc()
        AGENT_TASK_DURATION.labels(task_type=task_type).observe(duration)
        
        if status == 'success':
            self._update_success_rate(task_type)
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """记录API请求指标"""
        API_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).inc()
        
        API_REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_knowledge_graph_query(self, status: str):
        """记录知识图谱查询"""
        KNOWLEDGE_GRAPH_QUERIES.labels(status=status).inc()
    
    def update_queue_metrics(self, queue_name: str, depth: int, urgent: int, high: int, medium: int, low: int):
        """更新队列指标"""
        AGENT_QUEUE_DEPTH.labels(queue_name=queue_name).set(depth)
        TASK_PRIORITY_DISTRIBUTION.labels(priority='urgent').set(urgent)
        TASK_PRIORITY_DISTRIBUTION.labels(priority='high').set(high)
        TASK_PRIORITY_DISTRIBUTION.labels(priority='medium').set(medium)
        TASK_PRIORITY_DISTRIBUTION.labels(priority='low').set(low)
    
    def update_system_metrics(self, cpu: float, memory: int, disk: int):
        """更新系统资源指标"""
        SYSTEM_CPU_USAGE.set(cpu)
        SYSTEM_MEMORY_USAGE.set(memory)
        SYSTEM_DISK_USAGE.set(disk)
    
    def record_cache_operation(self, hit: bool):
        """记录缓存操作"""
        if hit:
            CACHE_HITS.inc()
        else:
            CACHE_MISSES.inc()
    
    def set_system_info(self, version: str, python_version: str, platform: str):
        """设置系统信息"""
        SYSTEM_INFO.info({
            'version': version,
            'python_version': python_version,
            'platform': platform,
        })
    
    def _update_success_rate(self, task_type: str):
        """更新成功率"""
        pass  # 实现逻辑需要访问历史数据
    
    def get_metrics(self) -> bytes:
        """获取所有指标"""
        return generate_latest(self.registry)
    
    def get_content_type(self) -> str:
        """获取内容类型"""
        return CONTENT_TYPE_LATEST


def track_task_duration(task_type: str) -> Callable:
    """任务持续时间装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                record_task(task_type, 'success', duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                record_task(task_type, 'failure', duration)
                raise
        return wrapper
    return decorator


def track_api_request(method: str, endpoint: str) -> Callable:
    """API请求持续时间装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            API_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                status_code = getattr(result, 'status_code', 200) if hasattr(result, 'status_code') else 200
                record_api_request(method, endpoint, status_code, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                record_api_request(method, endpoint, 500, duration)
                raise
            finally:
                API_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()
        return wrapper
    return decorator


def record_task(task_type: str, status: str, duration: float):
    """全局任务记录函数"""
    AGENT_TASKS_TOTAL.labels(task_type=task_type, status=status).inc()
    AGENT_TASK_DURATION.labels(task_type=task_type).observe(duration)


def record_api_request(method: str, endpoint: str, status_code: int, duration: float):
    """全局API请求记录函数"""
    API_REQUESTS_TOTAL.labels(
        method=method,
        endpoint=endpoint,
        status_code=str(status_code)
    ).inc()
    
    API_REQUEST_DURATION.labels(
        method=method,
        endpoint=endpoint
    ).observe(duration)


# 全局指标收集器实例
_metrics_collector: MetricsCollector = None


def get_metrics_collector() -> MetricsCollector:
    """获取指标收集器实例"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
