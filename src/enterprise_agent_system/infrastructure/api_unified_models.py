"""
统一API响应模型和基础设施
提供标准化的API响应、错误处理和认证机制
"""

from datetime import datetime
from enum import Enum
from typing import Generic, List, Optional, TypeVar, Dict, Any
from pydantic import BaseModel, Field

# 响应数据类型变量
T = TypeVar("T")


class ResponseStatus(str, Enum):
    """响应状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    PENDING = "pending"


class ErrorCode(str, Enum):
    """错误码枚举"""
    # 通用错误
    VALIDATION_ERROR = "validation_error"
    INTERNAL_ERROR = "internal_error"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    RATE_LIMITED = "rate_limited"
    BAD_REQUEST = "bad_request"
    
    # 业务错误
    LLM_ERROR = "llm_error"
    ANALYSIS_FAILED = "analysis_failed"
    STORAGE_ERROR = "storage_error"


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    status: ResponseStatus = Field(..., description="响应状态")
    data: Optional[T] = Field(None, description="响应数据")
    error_info: Optional[Dict[str, Any]] = Field(None, description="错误信息", alias="error")
    meta: Optional[Dict[str, Any]] = Field(None, description="元数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {"result": "ok"},
                "meta": {"total": 10, "page": 1},
                "timestamp": "2024-05-16T12:00:00Z"
            }
        }

    @classmethod
    def success(cls, data: T, meta: Optional[Dict] = None, request_id: Optional[str] = None) -> "ApiResponse[T]":
        """成功响应"""
        return cls(
            status=ResponseStatus.SUCCESS,
            data=data,
            meta=meta,
            request_id=request_id
        )

    @classmethod
    def error(cls, error_code: ErrorCode, message: str, details: Optional[Any] = None, request_id: Optional[str] = None) -> "ApiResponse[T]":
        """错误响应"""
        return cls(
            status=ResponseStatus.ERROR,
            error_info={
                "code": error_code.value,
                "message": message,
                "details": details,
                "traceback": None  # 生产环境不返回traceback
            },
            request_id=request_id
        )
    
    @classmethod
    def partial(cls, data: T, meta: Optional[Dict] = None) -> "ApiResponse[T]":
        """部分成功响应"""
        return cls(
            status=ResponseStatus.PARTIAL,
            data=data,
            meta=meta
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class HealthStatus(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    uptime: float
    services: Dict[str, bool]


class AnalysisReportSummary(BaseModel):
    """分析报告摘要"""
    id: str
    title: str
    type: str
    quality_score: float
    created_at: datetime
    processing_time: float
    findings_count: int


# 认证相关模型
class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# 统计模型
class ApiStats(BaseModel):
    """API统计"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    rate_limits_hits: int


class SystemInfo(BaseModel):
    """系统信息"""
    version: str
    model: str
    cache_size: int
    cache_hits: int
    cache_misses: int
    total_analysis: int
