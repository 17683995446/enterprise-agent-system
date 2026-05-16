"""
Phase 7 Test Suite
Tests for API, RAG, Persistence, and CLI
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from enterprise_agent_system.infrastructure.api_unified_models import ApiResponse, ResponseStatus
from enterprise_agent_system.infrastructure.api_auth_middleware import RateLimiter
from enterprise_agent_system.application.rag_system import RAGSystem, DocumentProcessor
from enterprise_agent_system.infrastructure.llm_integration import LRUCache


class TestUnifiedResponse:
    """测试统一响应模型"""
    
    def test_success_response(self):
        """测试成功响应"""
        response = ApiResponse.success(data={"key": "value"})
        assert response.status == ResponseStatus.SUCCESS
        assert response.data == {"key": "value"}
        assert response.error is None
    
    def test_error_response(self):
        """测试错误响应"""
        from enterprise_agent_system.infrastructure.api_unified_models import ErrorCode
        
        response = ApiResponse.error(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="Test error"
        )
        assert response.status == ResponseStatus.ERROR
        assert response.error["message"] == "Test error"


class TestRateLimiter:
    """测试速率限制器"""
    
    def test_rate_limit_not_exceeded(self):
        """测试未超过限制"""
        limiter = RateLimiter(requests_per_minute=100)
        assert limiter.is_rate_limited("client1") is False
    
    def test_rate_limit_exceeded(self):
        """测试超过限制"""
        limiter = RateLimiter(requests_per_minute=2)
        limiter.is_rate_limited("client2")
        limiter.is_rate_limited("client2")
        assert limiter.is_rate_limited("client2") is True


class TestLRUCache:
    """测试LRU缓存"""
    
    def test_cache_get_set(self):
        """测试缓存设置和获取"""
        cache = LRUCache(max_size=5)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_cache_eviction(self):
        """测试缓存淘汰"""
        cache = LRUCache(max_size=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # 淘汰a
        assert cache.get("a") is None
        assert cache.get("d") == 4


class TestDocumentProcessor:
    """测试文档处理器"""
    
    def test_split_text(self):
        """测试文本分割"""
        processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)
        text = "This is a test. " * 10
        chunks = processor.split_text(text)
        assert len(chunks) > 0
        assert all(len(chunk) <= 60 for chunk in chunks)


class TestRAGSystem:
    """测试RAG系统"""
    
    def test_add_document(self):
        """测试添加文档"""
        rag = RAGSystem()
        rag.add_document(
            content="This is a test document about Python programming.",
            source="test.txt"
        )
        stats = rag.get_knowledge_base_stats()
        assert stats["total_documents"] == 1
    
    def test_search(self):
        """测试搜索"""
        rag = RAGSystem()
        rag.add_document(
            content="Python is a programming language.",
            source="test.txt"
        )
        results = rag.search("Python")
        assert len(results) > 0


@pytest.mark.asyncio
class TestLLMIntegration:
    """测试LLM集成（模拟）"""
    
    async def test_llm_manager_initialization(self):
        """测试LLM管理器初始化"""
        from enterprise_agent_system.infrastructure.llm_integration import AdvancedLLMManager
        with patch('httpx.AsyncClient') as mock_client:
            manager = AdvancedLLMManager()
            assert manager is not None
            assert manager.config is not None


def run_tests():
    """运行测试"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
