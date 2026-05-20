"""
Simple In-Memory Storage - With Extremely Detailed Logging
完全不依赖外部库的内存存储，用于极端测试 + 详细日志
"""
import json
import uuid
import threading
import copy
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


print("[LOG] simple_memory_store_with_logging.py is importing modules")
print("[LOG] import json - done")
print("[LOG] import uuid - done")
print("[LOG] import threading - done")
print("[LOG] import copy - done")
print("[LOG] import time - done")
print("[LOG] from datetime import datetime - done")
print("[LOG] from typing import ... - done")
print("[LOG] from dataclasses import ... - done")


@dataclass
class AnalysisReport:
    print("[LOG] AnalysisReport class is defined")
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
    print("[LOG] SimpleMemoryStore class definition start")
    """简单的线程安全内存存储 - 完全不依赖外部库 + 详细日志"""
    
    def __init__(self):
        print("[LOG] SimpleMemoryStore.__init__() called")
        self._storage: Dict[str, Dict[str, Any]] = {}
        print("[LOG] SimpleMemoryStore._storage initialized")
        self._lock = threading.RLock()
        print("[LOG] SimpleMemoryStore._lock initialized")
        self._version: Dict[str, int] = {}
        print("[LOG] SimpleMemoryStore._version initialized")
        
    def save_report(self, report_data: Dict[str, Any]) -> str:
        print(f"[LOG] SimpleMemoryStore.save_report(report_data={report_data}) called")
        """保存报告"""
        with self._lock:
            print("[LOG] SimpleMemoryStore.save_report() got lock")
            report_id = report_data.get('id') or str(uuid.uuid4())
            print(f"[LOG] SimpleMemoryStore.save_report() report_id={report_id}")
            now = datetime.utcnow().isoformat()
            print(f"[LOG] SimpleMemoryStore.save_report() now={now}")
            
            existing = self._storage.get(report_id)
            print(f"[LOG] SimpleMemoryStore.save_report() existing={existing}")
            
            if existing:
                print("[LOG] SimpleMemoryStore.save_report() existing report found")
                existing.update(report_data)
                print(f"[LOG] SimpleMemoryStore.save_report() existing updated")
                existing['id'] = report_id
                print(f"[LOG] SimpleMemoryStore.save_report() existing['id'] set to {report_id}")
                existing['updated_at'] = now
                print(f"[LOG] SimpleMemoryStore.save_report() existing['updated_at'] set to {now}")
                existing['created_at'] = existing.get('created_at', now)
                print(f"[LOG] SimpleMemoryStore.save_report() existing['created_at']={existing['created_at']}")
                self._storage[report_id] = existing
                print(f"[LOG] SimpleMemoryStore.save_report() self._storage[{report_id}] set to existing")
            else:
                print("[LOG] SimpleMemoryStore.save_report() creating new report")
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
                print(f"[LOG] SimpleMemoryStore.save_report() report_dict created")
                for key, value in report_data.items():
                    print(f"[LOG] SimpleMemoryStore.save_report() checking key {key}")
                    if key not in report_dict:
                        report_dict[key] = value
                        print(f"[LOG] SimpleMemoryStore.save_report() added key {key} to report_dict")
                
                self._storage[report_id] = report_dict
                print(f"[LOG] SimpleMemoryStore.save_report() self._storage[{report_id}] = report_dict")
            
            self._version[report_id] = self._version.get(report_id, 0) + 1
            print(f"[LOG] SimpleMemoryStore.save_report() self._version[{report_id}] updated to {self._version[report_id]}")
            return report_id
            
    def save_report_with_version(self, report_data: Dict[str, Any], expected_version: Optional[int] = None) -> bool:
        print(f"[LOG] SimpleMemoryStore.save_report_with_version(report_data={report_data}, expected_version={expected_version}) called")
        """带版本检查的保存 - 用于乐观锁"""
        with self._lock:
            print("[LOG] SimpleMemoryStore.save_report_with_version() got lock")
            report_id = report_data.get('id')
            print(f"[LOG] SimpleMemoryStore.save_report_with_version() report_id={report_id}")
            
            if report_id:
                current_version = self._version.get(report_id, 0)
                print(f"[LOG] SimpleMemoryStore.save_report_with_version() current_version={current_version}")
                if expected_version is not None and current_version != expected_version:
                    print(f"[LOG] SimpleMemoryStore.save_report_with_version() version mismatch, returning False")
                    return False
            
            self.save_report(report_data)
            print("[LOG] SimpleMemoryStore.save_report_with_version() called save_report()")
            return True
            
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        print(f"[LOG] SimpleMemoryStore.get_report(report_id={report_id}) called")
        """获取单个报告"""
        with self._lock:
            print("[LOG] SimpleMemoryStore.get_report() got lock")
            report = self._storage.get(report_id)
            print(f"[LOG] SimpleMemoryStore.get_report() report found={report is not None}")
            if report:
                deepcopied = copy.deepcopy(report)
                print(f"[LOG] SimpleMemoryStore.get_report() returning deepcopy")
                return deepcopied
            print(f"[LOG] SimpleMemoryStore.get_report() returning None")
            return None
            
    def list_reports(
        self, 
        report_type: Optional[str] = None, 
        min_score: Optional[float] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        print(f"[LOG] SimpleMemoryStore.list_reports(type={report_type}, min_score={min_score}, limit={limit}, offset={offset}) called")
        """列出报告"""
        with self._lock:
            print("[LOG] SimpleMemoryStore.list_reports() got lock")
            reports = list(self._storage.values())
            print(f"[LOG] SimpleMemoryStore.list_reports() got {len(reports)} reports")
            
            if report_type:
                reports = [r for r in reports if r.get('type') == report_type]
                print(f"[LOG] SimpleMemoryStore.list_reports() filtered by type={report_type}, {len(reports)} left")
            if min_score is not None:
                reports = [r for r in reports if (r.get('quality_score') or 0) >= min_score]
                print(f"[LOG] SimpleMemoryStore.list_reports() filtered by score>={min_score}, {len(reports)} left")
                
            reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            print(f"[LOG] SimpleMemoryStore.list_reports() sorted reports")
            
            return reports[offset:offset+limit]
            
    def delete_report(self, report_id: str) -> bool:
        print(f"[LOG] SimpleMemoryStore.delete_report(report_id={report_id}) called")
        """删除报告"""
        with self._lock:
            print("[LOG] SimpleMemoryStore.delete_report() got lock")
            if report_id in self._storage:
                print(f"[LOG] SimpleMemoryStore.delete_report() deleting {report_id}")
                del self._storage[report_id]
                if report_id in self._version:
                    del self._version[report_id]
                    print(f"[LOG] SimpleMemoryStore.delete_report() deleted version")
                return True
            print(f"[LOG] SimpleMemoryStore.delete_report() {report_id} not found")
            return False
            
    def atomic_increment(self, report_id: str, field_path: str, increment: int = 1) -> int:
        print(f"[LOG] SimpleMemoryStore.atomic_increment(report_id={report_id}, field_path={field_path}, increment={increment}) called")
        """原子增量操作"""
        with self._lock:
            print("[LOG] SimpleMemoryStore.atomic_increment() got lock")
            if report_id not in self._storage:
                print(f"[LOG] SimpleMemoryStore.atomic_increment() {report_id} not found, return 0")
                return 0
            
            fields = field_path.split('.')
            print(f"[LOG] SimpleMemoryStore.atomic_increment() fields={fields}")
            data = self._storage[report_id]
            
            for field in fields[:-1]:
                print(f"[LOG] SimpleMemoryStore.atomic_increment() checking field {field}")
                if isinstance(data, dict) and field in data:
                    data = data[field]
                    print(f"[LOG] SimpleMemoryStore.atomic_increment() moved to {field}")
                else:
                    print(f"[LOG] SimpleMemoryStore.atomic_increment() path not found, return 0")
                    return 0
            
            target_field = fields[-1]
            print(f"[LOG] SimpleMemoryStore.atomic_increment() target_field={target_field}")
            if isinstance(data, dict) and target_field in data:
                current_value = int(data[target_field])
                print(f"[LOG] SimpleMemoryStore.atomic_increment() current_value={current_value}")
                new_value = current_value + increment
                data[target_field] = new_value
                print(f"[LOG] SimpleMemoryStore.atomic_increment() new_value={new_value}")
                
                self._version[report_id] = self._version.get(report_id, 0) + 1
                print(f"[LOG] SimpleMemoryStore.atomic_increment() version updated")
                return new_value
            print(f"[LOG] SimpleMemoryStore.atomic_increment() target field not found, return 0")
            return 0
            
    def get_stats(self) -> Dict[str, Any]:
        print(f"[LOG] SimpleMemoryStore.get_stats() called")
        """获取统计信息"""
        with self._lock:
            print("[LOG] SimpleMemoryStore.get_stats() got lock")
            total = len(self._storage)
            print(f"[LOG] SimpleMemoryStore.get_stats() total={total}")
            
            avg_score = 0
            if total > 0:
                scores = [r.get('quality_score', 0) for r in self._storage.values() if r.get('quality_score') is not None]
                avg_score = sum(scores) / len(scores) if scores else 0
                print(f"[LOG] SimpleMemoryStore.get_stats() avg_score={avg_score}")
                
            by_type = {}
            for report in self._storage.values():
                typ = report.get('type', 'unknown')
                by_type[typ] = by_type.get(typ, 0) + 1
                print(f"[LOG] SimpleMemoryStore.get_stats() by_type[{typ}] = {by_type[typ]}")
                
            return {
                "total_reports": total,
                "average_score": avg_score,
                "by_type": by_type
            }
            
    save = save_report
    get = get_report
    list_all = lambda self: self.list_reports()
    delete = delete_report


class SimpleCache:
    print("[LOG] SimpleCache class definition start")
    """简单的线程安全缓存 + 详细日志"""
    
    def __init__(self):
        print("[LOG] SimpleCache.__init__() called")
        self._cache: Dict[str, Any] = {}
        print("[LOG] SimpleCache._cache initialized")
        self._ttls: Dict[str, float] = {}
        print("[LOG] SimpleCache._ttls initialized")
        self._lock = threading.RLock()
        print("[LOG] SimpleCache._lock initialized")
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        print(f"[LOG] SimpleCache._stats initialized = {self._stats}")
        
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        print(f"[LOG] SimpleCache.set(key={key}, value={value}, ttl={ttl}) called")
        """设置缓存"""
        with self._lock:
            print("[LOG] SimpleCache.set() got lock")
            self._cache[key] = value
            print(f"[LOG] SimpleCache.set() self._cache[{key}] = {value}")
            if ttl is not None and ttl > 0:
                print(f"[LOG] SimpleCache.set() setting TTL for {key}")
                self._ttls[key] = time.time() + ttl
                print(f"[LOG] SimpleCache.set() TTL for {key} = {self._ttls[key]}")
            elif ttl == 0:
                print(f"[LOG] SimpleCache.set() TTL=0, removing TTL if exists")
                if key in self._ttls:
                    del self._ttls[key]
                    print(f"[LOG] SimpleCache.set() TTL for {key} deleted")
            self._stats['sets'] += 1
            print(f"[LOG] SimpleCache.set() self._stats['sets'] = {self._stats['sets']}")
            return True
            
    def get(self, key: str) -> Optional[Any]:
        print(f"[LOG] SimpleCache.get(key={key}) called")
        """获取缓存"""
        with self._lock:
            print("[LOG] SimpleCache.get() got lock")
            if key in self._cache:
                print(f"[LOG] SimpleCache.get() key {key} exists in cache")
                if key in self._ttls and time.time() > self._ttls[key]:
                    print(f"[LOG] SimpleCache.get() TTL expired for {key}")
                    del self._cache[key]
                    print(f"[LOG] SimpleCache.get() deleted from cache")
                    del self._ttls[key]
                    print(f"[LOG] SimpleCache.get() deleted from ttl")
                    self._stats['misses'] += 1
                    print(f"[LOG] SimpleCache.get() misses incremented to {self._stats['misses']}")
                    return None
                
                self._stats['hits'] += 1
                print(f"[LOG] SimpleCache.get() hits incremented to {self._stats['hits']}")
                return self._cache[key]
            else:
                self._stats['misses'] += 1
                print(f"[LOG] SimpleCache.get() misses incremented to {self._stats['misses']}")
                return None
                
    def delete(self, key: str) -> bool:
        print(f"[LOG] SimpleCache.delete(key={key}) called")
        """删除缓存"""
        with self._lock:
            print("[LOG] SimpleCache.delete() got lock")
            if key in self._cache:
                print(f"[LOG] SimpleCache.delete() key {key} exists")
                del self._cache[key]
                print(f"[LOG] SimpleCache.delete() deleted from cache")
                if key in self._ttls:
                    del self._ttls[key]
                    print(f"[LOG] SimpleCache.delete() deleted from ttl")
                self._stats['deletes'] += 1
                print(f"[LOG] SimpleCache.delete() deletes incremented to {self._stats['deletes']}")
                return True
            print(f"[LOG] SimpleCache.delete() key {key} not found")
            return False
            
    def exists(self, key: str) -> bool:
        print(f"[LOG] SimpleCache.exists(key={key}) called")
        """检查是否存在"""
        with self._lock:
            print("[LOG] SimpleCache.exists() got lock")
            exists = key in self._cache
            print(f"[LOG] SimpleCache.exists() returning {exists}")
            return exists
            
    def clear(self, pattern: str = "*") -> int:
        print(f"[LOG] SimpleCache.clear(pattern={pattern}) called")
        """清空缓存"""
        with self._lock:
            print("[LOG] SimpleCache.clear() got lock")
            if pattern == "*":
                count = len(self._cache)
                print(f"[LOG] SimpleCache.clear() clearing all {count} items")
                self._cache = {}
                self._ttls = {}
                return count
            else:
                import fnmatch
                keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
                print(f"[LOG] SimpleCache.clear() will delete {len(keys_to_delete)} items")
                for key in keys_to_delete:
                    del self._cache[key]
                    if key in self._ttls:
                        del self._ttls[key]
                return len(keys_to_delete)
                
    def get_stats(self) -> Dict[str, Any]:
        print(f"[LOG] SimpleCache.get_stats() called")
        """获取统计信息"""
        with self._lock:
            print("[LOG] SimpleCache.get_stats() got lock")
            stats = dict(self._stats)
            total = stats['hits'] + stats['misses']
            stats['total_requests'] = total
            stats['hit_rate'] = stats['hits'] / total if total > 0 else 0
            stats['using_fallback'] = True
            print(f"[LOG] SimpleCache.get_stats() returning {stats}")
            return stats
            
    def generate_key(self, prefix: str, *args) -> str:
        print(f"[LOG] SimpleCache.generate_key(prefix={prefix}, args={args}) called")
        """生成缓存键"""
        import hashlib
        key_str = ":".join([prefix] + [str(a) for a in args])
        result = hashlib.md5(key_str.encode()).hexdigest()
        print(f"[LOG] SimpleCache.generate_key() returning {result}")
        return result


print("[LOG] simple_memory_store_with_logging.py end of file")
