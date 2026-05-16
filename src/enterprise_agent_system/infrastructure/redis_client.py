"""
Redis Client for Enterprise Agent System
Infrastructure Layer - Redis缓存和消息队列客户端
"""

import redis
import json
from typing import Any, Optional, List, Dict
from dataclasses import dataclass
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance


logger = get_logger_instance(__name__)


@dataclass
class RedisConnectionConfig:
    """Redis连接配置"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    max_connections: int = 50
    decode_responses: bool = True


class RedisClient:
    """Redis客户端封装类"""
    
    def __init__(self, config: Optional[RedisConnectionConfig] = None):
        self.config = config or RedisConnectionConfig()
        self._client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        logger.info(f"RedisClient initialized for {self.config.host}:{self.config.port}")
    
    @property
    def client(self) -> redis.Redis:
        """获取Redis客户端实例（懒加载）"""
        if self._client is None:
            self._client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                max_connections=self.config.max_connections,
                decode_responses=self.config.decode_responses,
            )
        return self._client
    
    def ping(self) -> bool:
        """检查Redis连接"""
        try:
            return self.client.ping()
        except redis.RedisError as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    def get(self, key: str) -> Optional[str]:
        """获取值"""
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None,
        json_encode: bool = True
    ) -> bool:
        """设置值"""
        try:
            if json_encode and not isinstance(value, str):
                value = json.dumps(value)
            result = self.client.set(key, value)
            if expire:
                self.client.expire(key, expire)
            return result
        except redis.RedisError as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除键"""
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(self.client.exists(key))
        except redis.RedisError as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        try:
            return bool(self.client.expire(key, seconds))
        except redis.RedisError as e:
            logger.error(f"Redis expire error: {e}")
            return False
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """递增"""
        try:
            return self.client.incr(key, amount)
        except redis.RedisError as e:
            logger.error(f"Redis incr error: {e}")
            return None
    
    def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """递减"""
        try:
            return self.client.decr(key, amount)
        except redis.RedisError as e:
            logger.error(f"Redis decr error: {e}")
            return None
    
    def hset(self, name: str, key: str, value: Any) -> bool:
        """设置哈希字段"""
        try:
            if not isinstance(value, str):
                value = json.dumps(value)
            return bool(self.client.hset(name, key, value))
        except redis.RedisError as e:
            logger.error(f"Redis hset error: {e}")
            return False
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """获取哈希字段"""
        try:
            return self.client.hget(name, key)
        except redis.RedisError as e:
            logger.error(f"Redis hget error: {e}")
            return None
    
    def hgetall(self, name: str) -> Dict[str, str]:
        """获取所有哈希字段"""
        try:
            return self.client.hgetall(name)
        except redis.RedisError as e:
            logger.error(f"Redis hgetall error: {e}")
            return {}
    
    def lpush(self, key: str, *values) -> int:
        """左推入列表"""
        try:
            return self.client.lpush(key, *values)
        except redis.RedisError as e:
            logger.error(f"Redis lpush error: {e}")
            return 0
    
    def rpush(self, key: str, *values) -> int:
        """右推入列表"""
        try:
            return self.client.rpush(key, *values)
        except redis.RedisError as e:
            logger.error(f"Redis rpush error: {e}")
            return 0
    
    def lpop(self, key: str) -> Optional[str]:
        """左弹出列表"""
        try:
            return self.client.lpop(key)
        except redis.RedisError as e:
            logger.error(f"Redis lpop error: {e}")
            return None
    
    def rpop(self, key: str) -> Optional[str]:
        """右弹出列表"""
        try:
            return self.client.rpop(key)
        except redis.RedisError as e:
            logger.error(f"Redis rpop error: {e}")
            return None
    
    def llen(self, key: str) -> int:
        """获取列表长度"""
        try:
            return self.client.llen(key)
        except redis.RedisError as e:
            logger.error(f"Redis llen error: {e}")
            return 0
    
    def publish(self, channel: str, message: Any) -> int:
        """发布消息"""
        try:
            if not isinstance(message, str):
                message = json.dumps(message)
            return self.client.publish(channel, message)
        except redis.RedisError as e:
            logger.error(f"Redis publish error: {e}")
            return 0
    
    def subscribe(self, *channels: str):
        """订阅频道"""
        try:
            self._pubsub = self.client.pubsub()
            self._pubsub.subscribe(*channels)
            return self._pubsub
        except redis.RedisError as e:
            logger.error(f"Redis subscribe error: {e}")
            return None
    
    def get_message(self, timeout: float = 0.1):
        """获取消息"""
        try:
            if self._pubsub:
                return self._pubsub.get_message(timeout=timeout)
            return None
        except redis.RedisError as e:
            logger.error(f"Redis get_message error: {e}")
            return None
    
    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配的键"""
        try:
            return self.client.keys(pattern)
        except redis.RedisError as e:
            logger.error(f"Redis keys error: {e}")
            return []
    
    def flushdb(self) -> bool:
        """清空当前数据库"""
        try:
            return self.client.flushdb()
        except redis.RedisError as e:
            logger.error(f"Redis flushdb error: {e}")
            return False
    
    def info(self) -> Dict[str, Any]:
        """获取Redis信息"""
        try:
            return dict(self.client.info())
        except redis.RedisError as e:
            logger.error(f"Redis info error: {e}")
            return {}
    
    def close(self):
        """关闭连接"""
        try:
            if self._pubsub:
                self._pubsub.close()
            if self._client:
                self._client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Redis close error: {e}")


# 全局Redis客户端实例
_redis_client: Optional[RedisClient] = None


def get_redis_client(config: Optional[RedisConnectionConfig] = None) -> RedisClient:
    """获取Redis客户端实例（单例）"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient(config)
    return _redis_client
