"""
Simple In-Memory Storage - No Dependencies
完全不依赖外部库的内存存储，用于极端测试
"""
import json
import uuid
import threading
import copy
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class AnalysisReport:
    id: str
    title: str
    type: str
    content: Optional[str] = None
    summary: Optional[str] = None
    findings: Optional[List[Any]] = None
    recommendations: Optional[List[Any]] = None
    quality_score: Optional[float] = None
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    metrics: Optional[Dict[Any, Any]] = None
    language: Optional[str] = None
    file_path: Optional[str] = None
    llm_insights: Optional[str] = None
    metadata: Optional[Dict[Any, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SimpleMemoryStore:
    """简单的线程安全内存存储 - 完全不依赖外部库"""
    
    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._version: Dict[str, int] = {}  # 版本号用于乐观锁
        
    def save_report(self, report_data: Dict[str, Any]) -> str:
        """保存报告"""
        with self._lock:
            report_id = report_data.get('id') or str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            
            # 检查是否已存在，如果存在则更新现有字段
            existing = self._storage.get(report_id)
            
            if existing:
                # 更新现有报告，保留created_at
                existing.update(report_data)
                existing['id'] = report_id
                existing['updated_at'] = now
                # 保留created_at
                existing['created_at'] = existing.get('created_at', now)
                self._storage[report_id] = existing
            else:
                # 创建新报告
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
                # 合并额外字段
                for key, value in report_data.items():
                    if key not in report_dict:
                        report_dict[key] = value
                
                self._storage[report_id] = report_dict
            
            # 更新版本号
            self._version[report_id] = self._version.get(report_id, 0) + 1
            return report_id
            
    def save_report_with_version(self, report_data: Dict[str, Any], expected_version: Optional[int] = None) -> bool:
        """带版本检查的保存 - 用于乐观锁"""
        with self._lock:
            report_id = report_data.get('id')
            
            if report_id:
                current_version = self._version.get(report_id, 0)
                if expected_version is not None and current_version != expected_version:
                    return False  # 版本不匹配，保存失败
            
            self.save_report(report_data)
            return True
            
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """获取单个报告"""
        with self._lock:
            report = self._storage.get(report_id)
            if report:
                # 返回深拷贝以防止外部修改影响内部存储
                return copy.deepcopy(report)
            return None
            
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
            
            # 过滤
            if report_type:
                reports = [r for r in reports if r.get('type') == report_type]
            if min_score is not None:
                reports = [r for r in reports if (r.get('quality_score') or 0) >= min_score]
                
            # 排序（最新优先）
            reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # 分页
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
            
    def atomic_increment(self, report_id: str, field_path: str, increment: int = 1) -> int:
        """原子增量操作 - 用于并发安全的计数器更新"""
        with self._lock:
            if report_id not in self._storage:
                return 0
            
            # 解析字段路径，支持嵌套，如 "metrics.counter"
            fields = field_path.split('.')
            data = self._storage[report_id]
            
            # 遍历到目标字段
            for field in fields[:-1]:
                if isinstance(data, dict) and field in data:
                    data = data[field]
                else:
                    return 0
            
            target_field = fields[-1]
            if isinstance(data, dict) and target_field in data:
                current_value = int(data[target_field])
                new_value = current_value + increment
                data[target_field] = new_value
                
                # 更新版本号
                self._version[report_id] = self._version.get(report_id, 0) + 1
                return new_value
            return 0
            
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            total = len(self._storage)
            
            avg_score = 0
            if total > 0:
                scores = [r.get('quality_score', 0) for r in self._storage.values() if r.get('quality_score') is not None]
                avg_score = sum(scores) / len(scores) if scores else 0
                
            # 按类型统计
            by_type = {}
            for report in self._storage.values():
                typ = report.get('type', 'unknown')
                by_type[typ] = by_type.get(typ, 0) + 1
                
            return {
                "total_reports": total,
                "average_score": avg_score,
                "by_type": by_type
            }
            
    # 兼容测试的别名方法
    save = save_report
    get = get_report
    list_all = lambda self: self.list_reports()
    delete = delete_report


class SimpleCache:
    """简单的线程安全缓存"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._ttls: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        with self._lock:
            self._cache[key] = value
            # TTL=0 或 None 表示永不过期
            if ttl is not None and ttl > 0:
                self._ttls[key] = time.time() + ttl
            elif ttl == 0:
                # TTL=0 明确表示永不过期，移除任何现有的TTL
                if key in self._ttls:
                    del self._ttls[key]
            self._stats['sets'] += 1
            return True
            
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self._lock:
            if key in self._cache:
                # 检查TTL
                if key in self._ttls and time.time() > self._ttls[key]:
                    del self._cache[key]
                    del self._ttls[key]
                    self._stats['misses'] += 1
                    return None
                
                self._stats['hits'] += 1
                return self._cache[key]
            else:
                self._stats['misses'] += 1
                return None
                
    def delete(self, key: str) -> bool:
        """删除缓存"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._ttls:
                    del self._ttls[key]
                self._stats['deletes'] += 1
                return True
            return False
            
    def exists(self, key: str) -> bool:
        """检查是否存在"""
        with self._lock:
            return key in self._cache
            
    def clear(self, pattern: str = "*") -> int:
        """清空缓存"""
        with self._lock:
            if pattern == "*":
                count = len(self._cache)
                self._cache = {}
                self._ttls = {}
                return count
            else:
                import fnmatch
                keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
                for key in keys_to_delete:
                    del self._cache[key]
                    if key in self._ttls:
                        del self._ttls[key]
                return len(keys_to_delete)
                
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            stats = dict(self._stats)
            total = stats['hits'] + stats['misses']
            stats['total_requests'] = total
            stats['hit_rate'] = stats['hits'] / total if total > 0 else 0
            stats['using_fallback'] = True
            return stats
            
    def generate_key(self, prefix: str, *args) -> str:
        """生成缓存键"""
        import hashlib
        key_str = ":".join([prefix] + [str(a) for a in args])
        return hashlib.md5(key_str.encode()).hexdigest()
