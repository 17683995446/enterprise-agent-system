"""
Unit Tests for Error Handling System
测试错误处理和熔断器
"""

import pytest
from enterprise_agent_system.infrastructure.error_handling import (
    EnterpriseAgentError,
    LLMError,
    ValidationError,
    RetryableError,
    ErrorHandler,
    CircuitBreaker,
    ErrorCategory,
)


class TestErrorClasses:
    """错误类测试"""
    
    def test_base_error(self):
        """测试基础错误"""
        error = EnterpriseAgentError(
            message="Test error",
            code="TEST_ERROR",
            details={"key": "value"}
        )
        assert error.message == "Test error"
        assert error.code == "TEST_ERROR"
        assert error.details["key"] == "value"
        assert error.recoverable is True
    
    def test_llm_error(self):
        """测试LLM错误"""
        error = LLMError("LLM failed", model="gpt-4")
        assert error.category == ErrorCategory.LLM
        assert error.model == "gpt-4"
    
    def test_validation_error(self):
        """测试验证错误"""
        error = ValidationError("Invalid input", field="email")
        assert error.category == ErrorCategory.VALIDATION
        assert error.field == "email"
        assert error.recoverable is False
    
    def test_retryable_error(self):
        """测试可重试错误"""
        error = RetryableError("Temporary failure", retry_count=1, max_retries=3)
        assert error.can_retry is True
        assert error.retry_count == 1
        
        error2 = RetryableError("Max retries", retry_count=3, max_retries=3)
        assert error2.can_retry is False


class TestErrorHandler:
    """错误处理器测试"""
    
    def test_handle_known_error(self):
        """测试处理已知错误"""
        error = LLMError("Test")
        result = ErrorHandler.handle(error)
        assert result["error"] == "LLM_ERROR"
    
    def test_handle_unknown_error(self):
        """测试处理未知错误"""
        error = ValueError("Test")
        result = ErrorHandler.handle(error)
        assert result["error"] == "INTERNAL_ERROR"
    
    def test_should_retry(self):
        """测试重试判断"""
        assert ErrorHandler.should_retry(RetryableError("Test", retry_count=0)) is True
        assert ErrorHandler.should_retry(EnterpriseAgentError("Test")) is True


class TestCircuitBreaker:
    """熔断器测试"""
    
    def test_initial_state(self):
        """测试初始状态"""
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.can_attempt() is True
        assert cb.is_open is False
    
    def test_failure_threshold(self):
        """测试失败阈值"""
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure()
        assert cb.can_attempt() is True
        cb.record_failure()
        assert cb.is_open is True
        assert cb.can_attempt() is False
    
    def test_success_reset(self):
        """测试成功重置"""
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.failures == 0
        assert cb.is_open is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
