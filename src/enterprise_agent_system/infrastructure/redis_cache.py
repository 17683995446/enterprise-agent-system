"""
Redis Cache Manager with Fallback
Redis缓存管理器 - 带内存后备方案
"""

import json
import hashlib
from typing import Any, Optional, Dict
from dataclasses import dataclass
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance(__name__)


@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    hit_rate: float = 0.0


class FallbackCache:
    """内存后备缓存 - 当Redis不可用时使用"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._ttls: Dict[str, float] = {}
    
    def get(self, key: str) -> Optional[Any]:
        import time
        if key in self._cache:
            if key in self._ttls and time.time() > self._ttls[key]:
                del self._cache[key]
                del self._ttls[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        import time
        self._cache[key] = value
        if ttl:
            self._ttls[key] = time.time() + ttl
        elif key in self._ttls:
            del self._ttls[key]
        return True
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            if key in self._ttls:
                del self._ttls[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        return key in self._cache
    
    def clear(self, pattern: str = "*") -> int:
        import fnmatch
        keys = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
        for key in keys:
            del self._cache[key]
            if key in self._ttls:
                del self._ttls[key]
        return len(keys)


class RedisCacheManager:
    """Redis缓存管理器 - 带有后备方案"""
    
    def __init__(self):
        self._client = None
        self._fallback = FallbackCache()
        self._using_fallback = True
        self._stats = CacheStats()
        
        # 尝试连接Redis
        self._try_connect_redis()
    
    def _try_connect_redis(self):
        """尝试连接Redis"""
        try:
            import redis
            self._client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            self._client.ping()
            self._using_fallback = False
            logger.info("Redis connection established")
        except Exception:
            logger.warning("Redis not available, using in-memory fallback")
            self._using_fallback = True
            self._client = None
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if self._using_fallback:
            value = self._fallback.get(key)
        else:
            try:
                value_str = self._client.get(key)
                if value_str:
                    value = json.loads(value_str)
                else:
                    value = None
            except Exception as e:
                logger.error(f"Redis get error: {e}, switching to fallback")
                self._using_fallback = True
                value = self._fallback.get(key)
        
        if value:
            self._stats.hits += 1
        else:
            self._stats.misses += 1
        self._update_hit_rate()
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            if self._using_fallback:
                self._fallback.set(key, value, ttl)
            else:
                serialized = json.dumps(value)
                if ttl:
                    self._client.setex(key, ttl, serialized)
                else:
                    self._client.set(key, serialized)
            self._stats.sets += 1
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}, switching to fallback")
            self._using_fallback = True
            self._fallback.set(key, value, ttl)
            self._stats.sets += 1
            return True
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        if self._using_fallback:
            result = self._fallback.delete(key)
        else:
            try:
                result = bool(self._client.delete(key))
            except Exception as e:
                logger.error(f"Cache delete error: {e}")
                result = self._fallback.delete(key)
        
        if result:
            self._stats.deletes += 1
        return result
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if self._using_fallback:
            return self._fallback.exists(key)
        try:
            return bool(self._client.exists(key))
        except Exception:
            return self._fallback.exists(key)
    
    def clear(self, pattern: str = "*") -> int:
        """清空缓存"""
        if self._using_fallback:
            return self._fallback.clear(pattern)
        try:
            keys = self._client.keys(pattern)
            if keys:
                count = self._client.delete(*keys)
                return count
            return 0
        except Exception:
            return self._fallback.clear(pattern)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            "hits": self._stats.hits,
            "misses": self._stats.misses,
            "sets": self._stats.sets,
            "deletes": self._stats.deletes,
            "hit_rate": self._stats.hit_rate,
            "total_requests": self._stats.hits + self._stats.misses,
            "using_fallback": self._using_fallback,
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
