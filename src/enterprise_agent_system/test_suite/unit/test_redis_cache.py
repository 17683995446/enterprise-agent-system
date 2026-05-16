"""
Unit Tests for Redis Cache Manager
测试缓存层功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from enterprise_agent_system.infrastructure.redis_cache import (
    RedisCacheManager,
    CacheStats,
    get_cache_manager,
)


class TestCacheStats:
    """缓存统计测试"""
    
    def test_cache_stats_default(self):
        """测试默认统计"""
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.hit_rate == 0.0
    
    def test_cache_stats_update(self):
        """测试统计更新"""
        stats = CacheStats()
        stats.hits = 10
        stats.misses = 5
        stats.hit_rate = 10 / 15
        assert stats.hits == 10
        assert stats.misses == 5


class TestRedisCacheManager:
    """Redis缓存管理器测试"""
    
    def test_generate_key(self):
        """测试键生成"""
        with patch('redis.from_url'):
            manager = RedisCacheManager()
            key = manager.generate_key("test", "arg1", "arg2")
            assert len(key) == 32
            assert key == manager.generate_key("test", "arg1", "arg2")
    
    def test_get_stats(self):
        """测试获取统计"""
        with patch('redis.from_url'):
            manager = RedisCacheManager()
            stats = manager.get_stats()
            assert "hits" in stats
            assert "misses" in stats
            assert "hit_rate" in stats


class TestCacheIntegration:
    """缓存集成测试"""
    
    @pytest.mark.asyncio
    async def test_cache_workflow(self):
        """测试缓存工作流"""
        with patch('redis.from_url') as mock_redis:
            mock_client = MagicMock()
            mock_redis.return_value = mock_client
            mock_client.ping.return_value = True
            mock_client.get.return_value = '{"key": "value"}'
            
            manager = RedisCacheManager()
            value = manager.get("test_key")
            
            assert value == {"key": "value"}
            assert manager._stats.hits == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
