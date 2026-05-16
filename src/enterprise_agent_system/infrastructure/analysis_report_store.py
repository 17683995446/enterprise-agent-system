"""
分析报告持久化存储
提供分析报告的数据库存储和查询功能
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Text, Float, DateTime, Integer, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from enterprise_agent_system.infrastructure.database_session_manager import DatabaseSessionManager
from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance(__name__)
Base = declarative_base()


class AnalysisReportEntity(Base):
    """分析报告数据库实体"""
    __tablename__ = "analysis_reports"
    
    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    findings = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    quality_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    metrics = Column(JSON, nullable=True)
    language = Column(String(50), nullable=True)
    file_path = Column(String(500), nullable=True)
    llm_insights = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 索引
    __table_args__ = (
        Index('idx_report_type', 'report_type'),
        Index('idx_quality_score', 'quality_score'),
        Index('idx_created_at', 'created_at'),
    )


class AnalysisReportStore:
    """分析报告存储管理器"""
    
    def __init__(self, db_manager: Optional[DatabaseSessionManager] = None):
        self.db_manager = db_manager or DatabaseSessionManager()
    
    def save_report(self, report_data: Dict[str, Any]) -> str:
        """保存分析报告"""
        import uuid
        
        session = self.db_manager.get_session()
        try:
            report_id = str(uuid.uuid4())
            entity = AnalysisReportEntity(
                id=report_id,
                title=report_data.get('title', ''),
                report_type=report_data.get('type', 'code'),
                content=report_data.get('content', ''),
                summary=report_data.get('summary', ''),
                findings=json.dumps(report_data.get('findings', [])) if report_data.get('findings') else None,
                recommendations=json.dumps(report_data.get('recommendations', [])) if report_data.get('recommendations') else None,
                quality_score=report_data.get('quality_score'),
                confidence=report_data.get('confidence'),
                processing_time=report_data.get('processing_time'),
                metrics=json.dumps(report_data.get('metrics', {})) if report_data.get('metrics') else None,
                language=report_data.get('language'),
                file_path=report_data.get('file_path'),
                llm_insights=report_data.get('llm_insights'),
                metadata=json.dumps(report_data.get('metadata', {})) if report_data.get('metadata') else None
            )
            session.add(entity)
            session.commit()
            logger.info(f"Report saved: {report_id}")
            return report_id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save report: {e}")
            raise
        finally:
            session.close()
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """获取单个报告"""
        session = self.db_manager.get_session()
        try:
            entity = session.query(AnalysisReportEntity).filter(
                AnalysisReportEntity.id == report_id
            ).first()
            
            if not entity:
                return None
            
            return self._entity_to_dict(entity)
        finally:
            session.close()
    
    def list_reports(
        self, 
        report_type: Optional[str] = None, 
        min_score: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """列出报告"""
        session = self.db_manager.get_session()
        try:
            query = session.query(AnalysisReportEntity)
            
            if report_type:
                query = query.filter(AnalysisReportEntity.report_type == report_type)
            if min_score is not None:
                query = query.filter(AnalysisReportEntity.quality_score >= min_score)
            
            entities = query.order_by(
                AnalysisReportEntity.created_at.desc()
            ).limit(limit).offset(offset).all()
            
            return [self._entity_to_dict(e) for e in entities]
        finally:
            session.close()
    
    def delete_report(self, report_id: str) -> bool:
        """删除报告"""
        session = self.db_manager.get_session()
        try:
            result = session.query(AnalysisReportEntity).filter(
                AnalysisReportEntity.id == report_id
            ).delete()
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete report: {e}")
            return False
        finally:
            session.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        session = self.db_manager.get_session()
        try:
            from sqlalchemy import func
            
            total = session.query(func.count(AnalysisReportEntity.id)).scalar()
            avg_score = session.query(func.avg(AnalysisReportEntity.quality_score)).scalar()
            
            # 按类型统计
            type_stats = session.query(
                AnalysisReportEntity.report_type,
                func.count(AnalysisReportEntity.id)
            ).group_by(AnalysisReportEntity.report_type).all()
            
            return {
                "total_reports": total or 0,
                "average_score": float(avg_score) if avg_score else 0.0,
                "by_type": {t: c for t, c in type_stats}
            }
        finally:
            session.close()
    
    def _entity_to_dict(self, entity: AnalysisReportEntity) -> Dict[str, Any]:
        """转换实体为字典"""
        return {
            "id": entity.id,
            "title": entity.title,
            "type": entity.report_type,
            "content": entity.content,
            "summary": entity.summary,
            "findings": json.loads(entity.findings) if entity.findings else [],
            "recommendations": json.loads(entity.recommendations) if entity.recommendations else [],
            "quality_score": entity.quality_score,
            "confidence": entity.confidence,
            "processing_time": entity.processing_time,
            "metrics": json.loads(entity.metrics) if entity.metrics else {},
            "language": entity.language,
            "file_path": entity.file_path,
            "llm_insights": entity.llm_insights,
            "metadata": json.loads(entity.metadata) if entity.metadata else {},
            "created_at": entity.created_at.isoformat() if entity.created_at else None,
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else None
        }
