"""
Advanced Logging and Monitoring System
结构化日志、性能监控、指标采集
"""

import time
import json
import traceback
import logging
import re
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, Optional, Callable
from functools import wraps
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enterprise_agent_system.infrastructure.config_manager import get_config


@dataclass
class MetricsData:
    """指标数据"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_processing_time: float = 0.0
    request_times: list = field(default_factory=list)
    cache_hits: int = 0
    cache_misses: int = 0
    api_calls: Dict[str, int] = field(default_factory=dict)
    errors: Dict[str, int] = field(default_factory=dict)


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器 (JSON)"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
            "function": record.funcName,
        }
        
        # 异常信息
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # 额外字段
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


class SimpleFormatter(logging.Formatter):
    """简单文本格式化器"""
    
    def format(self, record):
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{record.levelname}] [{record.name}] {record.getMessage()}"


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.metrics = MetricsData()
        self._start_times = {}
    
    def record_request_start(self, request_id: str):
        """记录请求开始"""
        self._start_times[request_id] = time.time()
        self.metrics.total_requests += 1
    
    def record_request_end(self, request_id: str, success: bool = True):
        """记录请求结束"""
        if request_id in self._start_times:
            duration = time.time() - self._start_times.pop(request_id)
            self.metrics.total_processing_time += duration
            self.metrics.request_times.append(duration)
            
            if success:
                self.metrics.successful_requests += 1
            else:
                self.metrics.failed_requests += 1
    
    def record_cache_hit(self):
        """记录缓存命中"""
        self.metrics.cache_hits += 1
    
    def record_cache_miss(self):
        """记录缓存未命中"""
        self.metrics.cache_misses += 1
    
    def record_api_call(self, api_name: str):
        """记录 API 调用"""
        self.metrics.api_calls[api_name] = self.metrics.api_calls.get(api_name, 0) + 1
    
    def record_error(self, error_type: str):
        """记录错误"""
        self.metrics.errors[error_type] = self.metrics.errors.get(error_type, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        average_time = (
            self.metrics.total_processing_time / self.metrics.total_requests
            if self.metrics.total_requests > 0 else 0.0
        )
        
        cache_hit_rate = (
            self.metrics.cache_hits / (self.metrics.cache_hits + self.metrics.cache_misses)
            if (self.metrics.cache_hits + self.metrics.cache_misses) > 0 else 0.0
        )
        
        return {
            "total_requests": self.metrics.total_requests,
            "successful_requests": self.metrics.successful_requests,
            "failed_requests": self.metrics.failed_requests,
            "average_processing_time": average_time,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "api_calls": self.metrics.api_calls,
            "errors": self.metrics.errors,
        }
    
    def reset(self):
        """重置指标"""
        self.metrics = MetricsData()


class PerformanceMonitor:
    """性能监控装饰器"""
    
    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics
    
    def timed(self, name: Optional[str] = None):
        """计时装饰器"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    self.metrics.record_request_end(
                        getattr(func, '__name__', name), True
                    )
                    return result
                except Exception as e:
                    self.metrics.record_request_end(
                        getattr(func, '__name__', name), False
                    )
                    raise
                finally:
                    duration = time.time() - start_time
                    logger.info(f"Function {name or func.__name__} took {duration:.2f}s")
            return wrapper
        return decorator


# 全局实例
_metrics_collector: Optional[MetricsCollector] = None
_logger_instance: Optional[logging.Logger] = None


def get_metrics_collector() -> MetricsCollector:
    """获取指标收集器"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def setup_logging():
    """设置日志系统"""
    global _logger_instance
    
    config = get_config()
    logger = logging.getLogger("enterprise_agent")
    logger.setLevel(getattr(logging, config.logging.level))
    
    # 清除已有的 handler
    logger.handlers.clear()
    
    # 控制台 Handler
    console_handler = logging.StreamHandler()
    if config.logging.format == "json":
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(SimpleFormatter())
    logger.addHandler(console_handler)
    
    # 文件 Handler
    if config.logging.file:
        file_handler = RotatingFileHandler(
            config.logging.file,
            maxBytes=parse_size(config.logging.max_size),
            backupCount=config.logging.backup_count
        )
        if config.logging.format == "json":
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler.setFormatter(SimpleFormatter())
        logger.addHandler(file_handler)
    
    _logger_instance = logger
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取日志记录器"""
    if _logger_instance:
        if name:
            return _logger_instance.getChild(name)
        return _logger_instance
    return setup_logging()


def parse_size(size_str: str) -> int:
    """解析大小字符串，如 100MB -> 100*1024*1024"""
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024,
    }
    match = re.match(r'^(\d+(?:\.\d+)?)\s*(\w+)?$', size_str.strip())
    if match:
        number = float(match.group(1))
        unit = match.group(2) or 'B'
        return int(number * units.get(unit.upper(), 1))
    return int(size_str)


def log_structured(level: str, message: str, **extra):
    """记录结构化日志"""
    logger = get_logger()
    log_record = logging.LogRecord(
        name=logger.name,
        level=getattr(logging, level),
        pathname='',
        lineno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    log_record.extra_fields = extra
    logger.handle(log_record)
