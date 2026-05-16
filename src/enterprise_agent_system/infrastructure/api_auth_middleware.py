"""
API认证和限流中间件
提供安全认证和速率限制功能
"""

import time
from typing import Optional
from collections import defaultdict
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance(__name__)

# 速率限制存储
class RateLimiter:
    """简单的内存速率限制器"""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_rate_limited(self, client_id: str) -> bool:
        """检查是否超过速率限制"""
        now = time.time()
        # 清理1分钟前的记录
        self.requests[client_id] = [
            t for t in self.requests[client_id] 
            if now - t < 60
        ]
        
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return True
        
        self.requests[client_id].append(now)
        return False


# 简单的API Key认证
security = HTTPBearer(auto_error=False)

# 有效的API Keys（生产环境应从数据库或配置文件读取）
VALID_API_KEYS = {
    "test-key-1234": {
        "user": "test-user",
        "role": "admin",
        "rate_limit": 1000
    }
}

# 全局速率限制器（测试期间暂时设置较高的速率
rate_limiter = RateLimiter(requests_per_minute=1000)


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """获取当前用户（API Key认证）"""
    if not credentials:
        return {"user": "anonymous", "role": "guest", "rate_limit": 100}
    
    api_key = credentials.credentials
    if api_key in VALID_API_KEYS:
        return VALID_API_KEYS[api_key]
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def rate_limit_middleware(request: Request, call_next):
    """速率限制中间件"""
    client_id = request.client.host if request.client else "unknown"
    
    # 检查速率限制
    if rate_limiter.is_rate_limited(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    response = await call_next(request)
    return response


def validate_api_key(api_key: str) -> bool:
    """验证API Key"""
    return api_key in VALID_API_KEYS
