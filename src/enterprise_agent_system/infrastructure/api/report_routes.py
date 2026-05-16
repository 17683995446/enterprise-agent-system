"""
Report Management API Routes
Provides endpoints for managing analysis reports
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from enterprise_agent_system.infrastructure.api_unified_models import ApiResponse, PaginatedResponse
from enterprise_agent_system.infrastructure.api_auth_middleware import get_current_user
from enterprise_agent_system.infrastructure.analysis_report_store import AnalysisReportStore
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance(__name__)
router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])

# 初始化存储
report_store = AnalysisReportStore()


class ReportQueryRequest(BaseModel):
    """报告查询请求"""
    report_type: Optional[str] = None
    min_score: Optional[float] = None
    limit: int = 50
    offset: int = 0


@router.get("/", response_model=ApiResponse[PaginatedResponse[Dict[str, Any]]])
async def list_reports(
    report_type: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user)
):
    """列出分析报告"""
    try:
        reports = report_store.list_reports(
            report_type=report_type,
            min_score=min_score,
            limit=limit,
            offset=offset
        )
        
        total = len(reports)
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        
        paginated = PaginatedResponse(
            items=reports,
            total=total,
            page=offset // limit + 1,
            page_size=limit,
            total_pages=total_pages,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )
        
        return ApiResponse.success(paginated)
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to list reports")


@router.get("/{report_id}", response_model=ApiResponse[Dict[str, Any]])
async def get_report(
    report_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """获取单个报告"""
    try:
        report = report_store.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return ApiResponse.success(report)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get report")


@router.delete("/{report_id}", response_model=ApiResponse[bool])
async def delete_report(
    report_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """删除报告"""
    try:
        success = report_store.delete_report(report_id)
        if not success:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return ApiResponse.success(True)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete report: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete report")


@router.get("/stats/summary", response_model=ApiResponse[Dict[str, Any]])
async def get_report_stats(
    current_user: Dict = Depends(get_current_user)
):
    """获取报告统计信息"""
    try:
        stats = report_store.get_stats()
        return ApiResponse.success(stats)
    except Exception as e:
        logger.error(f"Failed to get report stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get report stats")
