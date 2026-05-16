"""
Test Suite for LLM Integration
Unit and Integration Tests for LLM Analysis System
Test Suite Layer - LLM测试套件
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from enterprise_agent_system.infrastructure.llm_integration import (
    AdvancedLLMManager,
    SiliconFlowClient,
    LLMConfig,
    LLMProvider,
    AnalysisOptions,
    AnalysisDepth,
    LRUCache,
    Message,
    CompletionResult,
)


class TestLRUCache:
    """LRU缓存测试"""
    
    def test_cache_set_and_get(self):
        cache = LRUCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
    
    def test_cache_eviction(self):
        cache = LRUCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")
        
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"
    
    def test_cache_lru_order(self):
        cache = LRUCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        cache.get("key1")
        cache.set("key4", "value4")
        
        assert cache.get("key2") is None
        assert cache.get("key1") == "value1"


class TestLLMConfig:
    """LLM配置测试"""
    
    def test_default_config(self):
        config = LLMConfig()
        
        assert config.provider == LLMProvider.SILICON_FLOW
        assert config.model == "Qwen/Qwen2.5-7B-Instruct"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.enable_cache is True
    
    def test_custom_config(self):
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            temperature=0.5,
            max_tokens=8192,
        )
        
        assert config.provider == LLMProvider.OPENAI
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 8192


class TestAnalysisOptions:
    """分析选项测试"""
    
    def test_default_options(self):
        options = AnalysisOptions()
        
        assert options.depth == AnalysisDepth.STANDARD
        assert options.include_security is True
        assert options.include_performance is True
        assert options.include_best_practices is True
    
    def test_custom_options(self):
        options = AnalysisOptions(
            depth=AnalysisDepth.DEEP,
            include_security=False,
            generate_tests=True,
        )
        
        assert options.depth == AnalysisDepth.DEEP
        assert options.include_security is False
        assert options.generate_tests is True


class TestSiliconFlowClient:
    """硅基流动客户端测试"""
    
    @pytest.fixture
    def client(self):
        config = LLMConfig(
            api_key="test-key",
            model="Qwen/Qwen2.5-7B-Instruct",
        )
        return SiliconFlowClient(config)
    
    def test_client_initialization(self, client):
        assert client.config.api_key == "test-key"
        assert client.config.model == "Qwen/Qwen2.5-7B-Instruct"
        assert client.client is None


class TestAdvancedLLMManager:
    """高级LLM管理器测试"""
    
    @pytest.fixture
    def manager(self):
        with patch('httpx.AsyncClient'):
            return AdvancedLLMManager()
    
    def test_manager_initialization(self, manager):
        assert manager.config is not None
        assert isinstance(manager.cache, LRUCache)
        assert manager.request_stats["total_requests"] == 0
    
    def test_get_cache_key(self, manager):
        key1 = manager._get_cache_key("prompt1", "system1", "model1")
        key2 = manager._get_cache_key("prompt1", "system1", "model1")
        key3 = manager._get_cache_key("prompt2", "system1", "model1")
        
        assert key1 == key2
        assert key1 != key3
    
    def test_clear_history(self, manager):
        manager.conversation_history["test"] = [
            Message(role="user", content="test")
        ]
        
        manager.clear_history()
        assert len(manager.conversation_history) == 0
        
        manager.conversation_history["test"] = [
            Message(role="user", content="test")
        ]
        manager.clear_history("test")
        assert "test" not in manager.conversation_history
    
    def test_clear_cache(self, manager):
        manager.cache.set("key", "value")
        assert manager.cache.get("key") == "value"
        
        manager.clear_cache()
        assert manager.cache.get("key") is None
    
    def test_get_stats(self, manager):
        stats = manager.get_stats()
        
        assert "total_requests" in stats
        assert "cached_requests" in stats
        assert "avg_latency" in stats
        assert "cache_hit_rate" in stats
        assert "cache_size" in stats


class TestCompletionResult:
    """完成结果测试"""
    
    def test_result_creation(self):
        result = CompletionResult(
            content="Test response",
            model="Qwen/Qwen2.5-7B-Instruct",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop",
            latency=1.5,
        )
        
        assert result.content == "Test response"
        assert result.usage["total_tokens"] == 30
        assert result.cached is False
    
    def test_result_with_error(self):
        result = CompletionResult(
            content="",
            model="Qwen/Qwen2.5-7B-Instruct",
            usage={},
            finish_reason="error",
            latency=0.5,
            error="Test error",
        )
        
        assert result.error == "Test error"


class TestMessage:
    """消息测试"""
    
    def test_message_creation(self):
        msg = Message(role="user", content="Hello")
        
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None
    
    def test_message_with_name(self):
        msg = Message(role="system", content="You are helpful", name="assistant")
        
        assert msg.role == "system"
        assert msg.name == "assistant"


@pytest.mark.asyncio
class TestAsyncLLMManager:
    """异步LLM管理器测试"""
    
    async def test_complete_caching(self):
        manager = AdvancedLLMManager()
        
        with patch.object(manager.client, 'complete', new_callable=AsyncMock) as mock_complete:
            mock_complete.return_value = CompletionResult(
                content="Test response",
                model="Qwen/Qwen2.5-7B-Instruct",
                usage={"total_tokens": 30},
                finish_reason="stop",
                latency=1.0,
            )
            
            result1 = await manager.complete("test prompt")
            result2 = await manager.complete("test prompt")
            
            assert result1.content == result2.content
            assert manager.request_stats["cached_requests"] == 1
    
    async def test_conversation_history(self):
        manager = AdvancedLLMManager()
        
        with patch.object(manager.client, 'complete', new_callable=AsyncMock) as mock_complete:
            mock_complete.return_value = CompletionResult(
                content="Response 1",
                model="Qwen/Qwen2.5-7B-Instruct",
                usage={"total_tokens": 30},
                finish_reason="stop",
                latency=1.0,
            )
            
            await manager.complete("prompt1", conversation_id="conv1")
            await manager.complete("prompt2", conversation_id="conv1")
            
            assert len(manager.conversation_history["conv1"]) == 4
    
    async def test_batch_complete(self):
        manager = AdvancedLLMManager()
        
        with patch.object(manager.client, 'complete', new_callable=AsyncMock) as mock_complete:
            mock_complete.return_value = CompletionResult(
                content="Batch response",
                model="Qwen/Qwen2.5-7B-Instruct",
                usage={"total_tokens": 30},
                finish_reason="stop",
                latency=1.0,
            )
            
            prompts = ["prompt1", "prompt2", "prompt3"]
            results = await manager.batch_complete(prompts, max_concurrent=2)
            
            assert len(results) == 3


class TestAnalysisDepth:
    """分析深度枚举测试"""
    
    def test_depth_values(self):
        assert AnalysisDepth.QUICK.value == "quick"
        assert AnalysisDepth.STANDARD.value == "standard"
        assert AnalysisDepth.DEEP.value == "deep"
        assert AnalysisDepth.COMPREHENSIVE.value == "comprehensive"


class TestLLMProvider:
    """LLM提供商测试"""
    
    def test_provider_values(self):
        assert LLMProvider.SILICON_FLOW.value == "silicon_flow"
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.LOCAL.value == "local"


def run_tests():
    """运行所有测试"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
