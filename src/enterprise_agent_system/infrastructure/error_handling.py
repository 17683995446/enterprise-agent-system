"""
Productization Error Handling System
完整的异常类体系和错误处理
"""

from typing import Optional, Dict, Any
from enum import Enum


class ErrorCategory(str, Enum):
    """错误类别"""
    VALIDATION = "validation"
    LLM = "llm"
    DATABASE = "database"
    CACHE = "cache"
    NETWORK = "network"
    SECURITY = "security"
    SYSTEM = "system"


class EnterpriseAgentError(Exception):
    """基础异常类"""
    
    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        category: ErrorCategory = ErrorCategory.SYSTEM,
        details: Optional[Dict[str, Any]] = None,
        recoverable: bool = True,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.category = category
        self.details = details or {}
        self.recoverable = recoverable
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code,
            "message": self.message,
            "category": self.category.value,
            "details": self.details,
            "recoverable": self.recoverable,
        }


class LLMError(EnterpriseAgentError):
    """LLM相关错误"""
    
    def __init__(self, message: str, model: str = "", **kwargs):
        super().__init__(
            message=message,
            code="LLM_ERROR",
            category=ErrorCategory.LLM,
            **kwargs
        )
        self.model = model


class ConfigurationError(EnterpriseAgentError):
    """配置错误"""
    
    def __init__(self, message: str, config_key: str = "", **kwargs):
        super().__init__(
            message=message,
            code="CONFIG_ERROR",
            category=ErrorCategory.SYSTEM,
            recoverable=False,
            **kwargs
        )
        self.config_key = config_key


class CacheError(EnterpriseAgentError):
    """缓存错误"""
    
    def __init__(self, message: str, cache_key: str = "", **kwargs):
        super().__init__(
            message=message,
            code="CACHE_ERROR",
            category=ErrorCategory.CACHE,
            **kwargs
        )
        self.cache_key = cache_key


class ValidationError(EnterpriseAgentError):
    """验证错误"""
    
    def __init__(self, message: str, field: str = "", **kwargs):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            recoverable=False,
            **kwargs
        )
        self.field = field


class RetryableError(EnterpriseAgentError):
    """可重试错误"""
    
    def __init__(
        self,
        message: str,
        retry_count: int = 0,
        max_retries: int = 3,
        **kwargs
    ):
        super().__init__(
            message=message,
            code="RETRYABLE_ERROR",
            recoverable=True,
            **kwargs
        )
        self.retry_count = retry_count
        self.max_retries = max_retries
        self.can_retry = retry_count < max_retries


class ErrorHandler:
    """错误处理器"""
    
    @staticmethod
    def handle(error: Exception) -> Dict[str, Any]:
        """处理错误"""
        if isinstance(error, EnterpriseAgentError):
            return error.to_dict()
        
        return {
            "code": "INTERNAL_ERROR",
            "message": str(error),
            "category": ErrorCategory.SYSTEM.value,
            "recoverable": False,
        }
    
    @staticmethod
    def should_retry(error: Exception) -> bool:
        """判断是否应该重试"""
        if isinstance(error, RetryableError):
            return error.can_retry
        if isinstance(error, EnterpriseAgentError):
            return error.recoverable
        return False


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.is_open = False
    
    def record_success(self):
        """记录成功"""
        self.failures = 0
        self.is_open = False
    
    def record_failure(self):
        """记录失败"""
        import time
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.is_open = True
    
    def can_attempt(self) -> bool:
        """是否可以尝试"""
        import time
        if not self.is_open:
            return True
        
        if self.last_failure_time:
            if time.time() - self.last_failure_time > self.timeout:
                self.is_open = False
                return True
        
        return False
