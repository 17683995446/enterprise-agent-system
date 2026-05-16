"""
Redis Cache Manager - Production Ready
使用开源Redis实现高性能缓存层
"""

import json
import hashlib
from typing import Any, Optional, Dict
from dataclasses import dataclass
import redis
from enterprise_agent_system.infrastructure.config_manager import get_config
from enterprise_agent_system.infrastructure.advanced_logging import get_logger

logger = get_logger("redis_cache")


@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    hit_rate: float = 0.0


class RedisCacheManager:
    """Redis缓存管理器"""
    
    def __init__(self):
        self.config = get_config()
        self._client: Optional[redis.Redis] = None
        self._stats = CacheStats()
    
    @property
    def client(self) -> redis.Redis:
        """获取Redis客户端，延迟初始化"""
        if self._client is None:
            try:
                redis_url = self.config.cache.redis_url
                self._client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                self._client.ping()
                logger.info("Redis connection established")
            except redis.ConnectionError:
                logger.warning("Redis connection failed, using fallback")
                self._client = None
        return self._client
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                self._stats.hits += 1
                self._update_hit_rate()
                return json.loads(value)
            else:
                self._stats.misses += 1
                self._update_hit_rate()
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self._stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not self.client:
            return False
        
        try:
            ttl = ttl or self.config.cache.default_ttl
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)
            self._stats.sets += 1
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            self._stats.deletes += 1
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.client:
            return False
        
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def clear(self, pattern: str = "*") -> int:
        """清空缓存"""
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            "hits": self._stats.hits,
            "misses": self._stats.misses,
            "sets": self._stats.sets,
            "deletes": self._stats.deletes,
            "hit_rate": self._stats.hit_rate,
            "total_requests": self._stats.hits + self._stats.misses,
        }
    
    def _update_hit_rate(self):
        """更新命中率"""
        total = self._stats.hits + self._stats.misses
        if total > 0:
            self._stats.hit_rate = self._stats.hits / total
    
    def generate_key(self, prefix: str, *args) -> str:
        """生成缓存键"""
        key_parts = [prefix] + [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


# 全局实例
_cache_manager: Optional[RedisCacheManager] = None


def get_cache_manager() -> RedisCacheManager:
    """获取缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = RedisCacheManager()
    return _cache_manager
