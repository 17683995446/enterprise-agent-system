"""
分析报告持久化存储 - 带后备方案
提供分析报告的数据库存储和查询功能
在没有SQLAlchemy时自动使用内存存储
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# 尝试导入SQLAlchemy，如果没有则使用后备方案
try:
    from sqlalchemy import Column, String, Text, Float, DateTime, Integer, Index, create_engine, func
    from sqlalchemy.orm import sessionmaker, declarative_base
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logger = None

from enterprise_agent_system.infrastructure.enterprise_logging_system import get_logger_instance

logger = get_logger_instance(__name__)


class AnalysisReportEntity:
    """分析报告实体类（后备方案）"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# 如果有SQLAlchemy，定义真实的数据库模型
if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
    
    class AnalysisReportEntity(Base):
        """分析报告数据库实体"""
        __tablename__ = "analysis_reports"
        
        id = Column(String(36), primary_key=True)
        title = Column(String(255), nullable=False)
        report_type = Column(String(50), nullable=False)
        content = Column(Text, nullable=True)
        summary = Column(Text, nullable=True)
        findings = Column(Text, nullable=True)
        recommendations = Column(Text, nullable=True)
        quality_score = Column(Float, nullable=True)
        confidence = Column(Float, nullable=True)
        processing_time = Column(Float, nullable=True)
        metrics = Column(Text, nullable=True)
        language = Column(String(50), nullable=True)
        file_path = Column(String(500), nullable=True)
        llm_insights = Column(Text, nullable=True)
        extra_metadata = Column("metadata", Text, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
        
        __table_args__ = (
            Index('idx_report_type', 'report_type'),
            Index('idx_quality_score', 'quality_score'),
            Index('idx_created_at', 'created_at'),
        )
else:
    Base = None
    AnalysisReportEntity = AnalysisReportEntity


class SimpleReportStore:
    """简单的内存报告存储（后备方案）"""
    
    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._lock = __import__('threading').RLock()
        self._version: Dict[str, int] = {}
    
    def save_report(self, report_data: Dict[str, Any]) -> str:
        """保存报告"""
        import uuid
        with self._lock:
            report_id = report_data.get('id') or str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            report_dict = {
                "id": report_id,
                "title": report_data.get('title', ''),
                "type": report_data.get('type', 'analysis'),
                "content": report_data.get('content'),
                "summary": report_data.get('summary'),
                "findings": report_data.get('findings'),
                "recommendations": report_data.get('recommendations'),
                "quality_score": report_data.get('quality_score'),
                "confidence": report_data.get('confidence'),
                "processing_time": report_data.get('processing_time'),
                "metrics": report_data.get('metrics'),
                "language": report_data.get('language'),
                "file_path": report_data.get('file_path'),
                "llm_insights": report_data.get('llm_insights'),
                "metadata": report_data.get('metadata'),
                "created_at": now,
                "updated_at": now,
            }
            
            self._storage[report_id] = report_dict
            self._version[report_id] = self._version.get(report_id, 0) + 1
            return report_id
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """获取单个报告"""
        with self._lock:
            return self._storage.get(report_id)
    
    def list_reports(
        self, 
        report_type: Optional[str] = None, 
        min_score: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """列出报告"""
        with self._lock:
            reports = list(self._storage.values())
            
            if report_type:
                reports = [r for r in reports if r.get('type') == report_type]
            if min_score is not None:
                reports = [r for r in reports if (r.get('quality_score') or 0) >= min_score]
            
            reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return reports[offset:offset+limit]
    
    def delete_report(self, report_id: str) -> bool:
        """删除报告"""
        with self._lock:
            if report_id in self._storage:
                del self._storage[report_id]
                if report_id in self._version:
                    del self._version[report_id]
                return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            total = len(self._storage)
            scores = [r.get('quality_score', 0) for r in self._storage.values() if r.get('quality_score') is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            by_type = {}
            for report in self._storage.values():
                typ = report.get('type', 'unknown')
                by_type[typ] = by_type.get(typ, 0) + 1
            
            return {
                "total_reports": total,
                "average_score": avg_score,
                "by_type": by_type
            }


class AnalysisReportStore:
    """分析报告存储管理器 - 支持SQLAlchemy和后备方案"""
    
    def __init__(self, db_path: str = "data/enterprise_agent.db"):
        self.db_path = db_path
        
        if SQLALCHEMY_AVAILABLE:
            try:
                if not db_path.startswith(':memory:'):
                    dir_path = os.path.dirname(db_path)
                    if dir_path:
                        os.makedirs(dir_path, exist_ok=True)
                
                self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
                Base.metadata.create_all(self.engine)
                self.Session = sessionmaker(bind=self.engine)
                self._use_sqlalchemy = True
                logger.info("Using SQLAlchemy for report storage")
            except Exception as e:
                logger.warning(f"Failed to initialize SQLAlchemy, using fallback: {e}")
                self._use_sqlalchemy = False
                self._fallback = SimpleReportStore()
        else:
            logger.warning("SQLAlchemy not available, using in-memory fallback")
            self._use_sqlalchemy = False
            self._fallback = SimpleReportStore()
    
    def save_report(self, report_data: Dict[str, Any]) -> str:
        """保存分析报告"""
        if self._use_sqlalchemy:
            return self._save_report_sqlalchemy(report_data)
        else:
            return self._fallback.save_report(report_data)
    
    def _save_report_sqlalchemy(self, report_data: Dict[str, Any]) -> str:
        """使用SQLAlchemy保存报告"""
        import uuid
        
        session = self.Session()
        try:
            report_id = report_data.get('id') if report_data.get('id') else str(uuid.uuid4())
            
            # 检查是否已存在，先删除
            existing = session.query(AnalysisReportEntity).filter_by(id=report_id).first()
            if existing:
                session.delete(existing)
                session.commit()
            
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
                extra_metadata=json.dumps(report_data.get('metadata', {})) if report_data.get('metadata') else None
            )
            session.add(entity)
            session.commit()
            return report_id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save report: {e}")
            raise
        finally:
            session.close()
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """获取单个报告"""
        if self._use_sqlalchemy:
            return self._get_report_sqlalchemy(report_id)
        else:
            return self._fallback.get_report(report_id)
    
    def _get_report_sqlalchemy(self, report_id: str) -> Optional[Dict[str, Any]]:
        """使用SQLAlchemy获取报告"""
        session = self.Session()
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
        if self._use_sqlalchemy:
            return self._list_reports_sqlalchemy(report_type, min_score, limit, offset)
        else:
            return self._fallback.list_reports(report_type, min_score, limit, offset)
    
    def _list_reports_sqlalchemy(
        self,
        report_type: Optional[str],
        min_score: Optional[float],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """使用SQLAlchemy列出报告"""
        session = self.Session()
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
        if self._use_sqlalchemy:
            return self._delete_report_sqlalchemy(report_id)
        else:
            return self._fallback.delete_report(report_id)
    
    def _delete_report_sqlalchemy(self, report_id: str) -> bool:
        """使用SQLAlchemy删除报告"""
        session = self.Session()
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
        if self._use_sqlalchemy:
            return self._get_stats_sqlalchemy()
        else:
            return self._fallback.get_stats()
    
    def _get_stats_sqlalchemy(self) -> Dict[str, Any]:
        """使用SQLAlchemy获取统计"""
        session = self.Session()
        try:
            total = session.query(func.count(AnalysisReportEntity.id)).scalar()
            avg_score = session.query(func.avg(AnalysisReportEntity.quality_score)).scalar()
            
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
            "metadata": json.loads(entity.extra_metadata) if entity.extra_metadata else {},
            "created_at": entity.created_at.isoformat() if entity.created_at else None,
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else None
        }
